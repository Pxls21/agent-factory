# Hermes Evaluation Runner Design

## 1. Problem statement

The stock AlphaEval runner exposes three documented hazards (component audit §3):

1. **Host networking** — rubric subprocesses share the host network namespace,
   enabling data exfiltration or lateral movement.
2. **Recursive chmod 777** — workspace permissions are opened recursively,
   allowing rubric code to read or modify any file in the evaluation workspace.
3. **Production credential passing** — environment variables containing API keys
   are inherited by rubric processes.

## 2. Policy (machine-readable)

The S0-11 design gate parses this block; each hazard must be declared forbidden.
Prose elsewhere in this document is explanatory only and is NOT the contract —
the checker reads this block, so no wording can satisfy the gate while a hazard
is enabled.

```yaml
policy:
  host_networking: forbidden
  recursive_chmod_777: forbidden
  production_credential_passing: forbidden
```

## 3. Design: isolated rubric execution, verified by parent observation

Each rubric process is launched under isolation and then observed FROM THE
PARENT via `/proc/<pid>` — the checker never trusts a report the child writes
about itself, because a child under a fake or pass-through wrapper can fabricate
a clean self-report. Wrapper binaries are invoked by ABSOLUTE path
(`/usr/bin/unshare`, `/usr/bin/setpriv`, `/usr/bin/nsenter`) so a `PATH` entry
cannot substitute a fake. A non-vacuity gate re-runs the same parent observation
against an UN-wrapped child and requires every axis to breach.

A capability preflight (`--selftest`) runs first: where the host cannot create or
observe the namespaces the check consumes, the checker exits 2 (capability
unavailable — not a pass, not a breach) so the proof is deferred to the
PC/gVisor host. Every proof leg that reads a child's namespaces is gated by this
same preflight.

### 3.1 UID drop (least privilege), parent-observed

The rubric runs as a non-root uid, and the parent reads the child's real host
uid from `/proc/<pid>/status` — asserting `!= 0` (never root). It is deliberately
NOT `!= parent uid`: a non-root runner cannot change its child's host uid (that
needs root), so the rubric legitimately INHERITS the runner's own non-root uid,
and `uid != parent` would wrongly fail there. The launch differs by venue: as
root, `unshare --net` creates the netns and `setpriv --reuid=65534
--regid=65534 --clear-groups --no-new-privs --bounding-set -all` performs a REAL
privilege drop (root→nobody) that ALSO sets `no_new_privs` and CLEARS the
capability bounding set; as a non-root service user (production, CI),
`unshare --user --net` keeps the runner's own non-root host uid, which already
satisfies `uid != 0`. The child's own `getuid()` is never used: under a bare
user namespace it reports an unprivileged id while the host uid is unchanged, so
it is not evidence. The uid-drop DISCRIMINATION (that the check would catch a
root rubric) is exercised by the non-vacuity gate only on a root venue, where an
un-wrapped child is actually root; the netns and env axes discriminate on every
venue.

**Privilege boundary (parent-observed, root venue).** A uid drop alone is not a
complete privilege boundary: without `no_new_privs`, a later `execve` of a
setuid or file-capability binary can regain privilege. The root launch therefore
sets `no_new_privs` and empties the capability bounding set, and the parent reads
`/proc/<pid>/status` and asserts `NoNewPrivs: 1` and `CapBnd: 0000000000000000`
on the wrapped child. This axis is venue-dependent (only the root `setpriv` drop
sets it); a non-root user-namespace venue defers via the capability preflight
before the check runs.

### 3.2 Network isolation (no host networking), parent-observed

The netns contains only an unconfigured loopback, so it has no connectivity. The
parent reads `/proc/<pid>/ns/net` and asserts the inode differs from its own (a
fresh netns). When the parent has the privilege, it also actively confirms
isolation: it holds a loopback listener in its own netns and `nsenter`s the
child's netns to prove that listener is UNREACHABLE from inside — a signal only
real namespace isolation can produce. The un-wrapped child shares the parent
netns and reaches it.

### 3.3 Credential isolation — closed allow-list, parent-observed

The runner builds the rubric environment from a **closed EXACT allow-list**:
`PATH, HOME, LANG, LC_ALL, LC_CTYPE, TMPDIR` plus the three runner variables
`RUBRIC_TASK_ID, RUBRIC_CWD, RUBRIC_PROBE_PORT`. It is NOT a `RUBRIC_*` prefix
wildcard (a prefix is itself open-ended — a credential named
`RUBRIC_PRODUCTION_API_KEY` would slip through) and NOT a name blacklist (which
missed `OMNIROUTE_INTERNAL_API_KEY`, `BUZZ_PRIVATE_KEY`, `STORAGE_ENCRYPTION_KEY`).
The parent reads the child's actual environment from `/proc/<pid>/environ` and
asserts every key is in the allow-list; production-named decoys the checker
injects into the parent environment must be absent from the child and present in
the un-wrapped control.

### 3.4 Permission hardening (no recursive chmod 777)

The runner never applies recursive or world-writable permission changes. S0-11
enforces this with a **best-effort lint** over every non-Markdown file in the
proof (Python via AST with import-alias resolution and constant folding, YAML via
a parsed walk, shell/other via regex). The lint catches obvious and accidental
hazards; it is deliberately NOT presented as a complete static-analysis boundary
— a determined author can express `chmod 777` or `network_mode: host` in forms no
static scan enumerates. The real guarantees are the runtime isolation above
(network) and gVisor + a non-root service user at the PC boundary
(filesystem/privilege — §5).

### 3.5 Working directory, parent-observed

Each rubric invocation runs in a fresh per-rubric temporary directory, passed to
the process as its actual working directory (not merely advertised in an
environment variable). The directory is chowned to the drop uid so the
post-privilege-drop rubric can actually WRITE it — a real AlphaEval rubric writes
results and logs to its workspace. The rubric writes an output file there; the
parent COLLECTS that output (reads it back) BEFORE the directory is cleaned up,
proving the workspace is securely-owned AND usable, not merely a different
directory the dropped uid cannot write. The parent also reads `/proc/<pid>/cwd`
and requires the child's real cwd to differ from the parent's cwd (the
production workspace); the un-wrapped control, which inherits the parent's cwd,
breaches this axis while still receiving its own throwaway workspace so its write
never lands in the proof tree. The fresh cwd is a usable output directory and a
first separation from the workspace — it is **not** a filesystem containment
boundary (§5); real FS containment is delivered by gVisor at the PC boundary.

## 4. Judge call routing

Any rubric requiring LLM calls uses the OmniRoute endpoint exclusively (standing
rule 3): in production the runner injects the OmniRoute base URL as
`RUBRIC_LLM_ENDPOINT` for a rubric that makes model calls, and passes no
direct-provider credentials. This S0-11 proof's rubric stand-in makes NO model
call, so `RUBRIC_LLM_ENDPOINT` is not injected here and is deliberately absent
from this proof's closed environment allow-list (§3.3) — the allow-list carries
only what the stand-in actually needs. A rubric that calls the model would add
`RUBRIC_LLM_ENDPOINT` to the allow-list at that point.

## 5. NOT verified in the sandbox (delivered at the PC/production boundary)

- **Filesystem containment.** A separate cwd is not a jail, and the sandbox user
  namespace does not enforce host file ownership against an unmapped uid. Real FS
  containment is delivered by **gVisor + a mapped user namespace** at the PC
  boundary (standing rule 11) and proven by the S0-08 gVisor proof, not here.
- **Complete static hazard coverage.** The forbidden-op lint is best-effort, not
  exhaustive; the runtime isolation and gVisor boundary are the guarantees.
- **UDP/ICMP egress and DNS** inside the netns (TCP loopback reachability is the
  network discriminator).
- **Live rubric workloads.** The stand-in blocks for observation; it does not run
  a real AlphaEval rubric. That integration is Wave-2 work.

## 6. Artifact bound to its inputs (attestation)

The recorded `result.json` is bound to the exact code, spec and fixtures that
produced it. On a capable venue the canonical runner (`scripts/proof-runner`)
records an `attestation` — the sha256 of every input file under this proof
directory (checker, spec, fixtures, this design doc). `scripts/validate-ledger`
re-derives those digests from the tree and fails on any mismatch. A neutered
checker (e.g. `_iso_launch` replaced with a pass-through) therefore no longer
validates against a stale green artifact: the schema and digest checks pass over
such an artifact, but the source binding does not. On an incapable venue the
runner DEFERS (exit 2) and PRESERVES the capable-venue artifact rather than
deleting it; the isolation proof is regenerated only where the namespaces and
the `nsenter` discriminator can actually run (the root sandbox, or gVisor at the
PC boundary).
