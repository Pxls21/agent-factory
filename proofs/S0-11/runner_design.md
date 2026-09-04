# Hermes Evaluation Runner Design

## 1. Problem statement

The stock AlphaEval runner exposes three documented hazards (component audit §3):

1. **Host networking** — rubric subprocesses share the host network namespace,
   enabling data exfiltration or lateral movement.
2. **Recursive chmod 777** — workspace permissions are opened recursively,
   allowing rubric code to read or modify any file in the evaluation workspace.
3. **Production credential passing** — environment variables containing API keys
   are inherited by rubric processes.

## 2. Design: isolated rubric execution

Each rubric process is launched through `unshare --user --net`, which places it
in a fresh **user namespace** (privilege drop) and a fresh **network namespace**
(no host networking) in one unprivileged step. The runner asserts the isolation
actually took effect on four axes; the S0-11 checker
(`check_eval_hardening.py`) enforces each axis and, crucially, re-runs the same
predicate against an UN-wrapped probe to prove no axis is a tautology.

### 2.1 UID drop (least privilege)

The rubric process runs under a new user namespace, so its effective UID is not
the runner's UID (it maps to an unprivileged id, not root). The checker asserts
`probe uid != parent uid` AND `probe uid != 0` — a report claiming root is
rejected even when the parent is non-root, and a report missing the UID (or any
other mandatory field) is rejected, never defaulted to a pass. A wrapper that
fails to create the user namespace (e.g. a pass-through `unshare`) leaves the
UID unchanged and is rejected. The checker first runs a capability preflight
(`--selftest`): where the host cannot create or read the namespaces the check
consumes, it exits 2 (capability unavailable — not a pass, not a breach) so the
proof is deferred to the PC/gVisor host rather than reporting a false result.

### 2.2 Network isolation (no host networking)

The new network namespace contains only an unconfigured loopback, so no
outbound connection is possible. The checker does NOT rely on "cannot reach an
external address" (that is a tautology inside an already-egress-filtered
sandbox). Instead it holds a loopback listener in its OWN netns and asserts the
rubric probe **cannot reach it** — a signal only real namespace isolation can
produce — while an un-wrapped probe reaches it. Namespace identity is confirmed
separately: `/proc/self/ns/net` inode of the probe differs from the parent's.

### 2.3 Credential isolation — allow-list, not blacklist (no credential passing)

The runner builds the rubric environment from a **closed allow-list**: an EXACT
set of names — `PATH, HOME, LANG, LC_ALL, LC_CTYPE, TMPDIR` plus the three
runner variables `RUBRIC_TASK_ID, RUBRIC_CWD, RUBRIC_PROBE_PORT`. It is NOT a
`RUBRIC_*` prefix wildcard (a prefix is itself an open-ended allow-list — a
credential named `RUBRIC_PRODUCTION_API_KEY` would slip through it) and NOT a
name blacklist (a blacklist missed production credentials such as
`OMNIROUTE_INTERNAL_API_KEY`, `BUZZ_PRIVATE_KEY`, and `STORAGE_ENCRYPTION_KEY`).
Every other variable, whatever it is named, is stripped by construction. The
checker injects those exact decoys into the parent environment and asserts they
are absent from the wrapped probe and present in the un-wrapped one.

### 2.4 Permission hardening (no recursive chmod 777)

The runner never applies recursive or world-writable permission changes. The
S0-11 forbidden-op sweep enforces this across every non-Markdown file in the
proof (the checker included — see below) using STRUCTURED checks, not a regex
list: Python is parsed as an AST so real `os.chmod(…, 0o777)` calls and
shell-command string arguments are caught while the checker's own pattern
literals are not; YAML is parsed so `network_mode: host` and `hostNetwork: true`
(including the bool `True`) are caught; shell and other text use regex. Because
the Python check is call-based, the checker file needs no self-exclusion — a
real forbidden call hidden inside it would still be caught. Rejected forms:
world-writable `chmod`, octal (`777`, `0777`, `666`, ...) or symbolic
(`o+w`, `a+w`, `go+rwx`, ...), and any host-networking directive.

The design doc itself is checked for the inverse defect: a doc that asserts any
hazard is enabled/required (or isolation disabled) fails, so the coverage gate
cannot be satisfied by prose that documents the hazards as permitted.

### 2.5 Working directory

Each rubric invocation receives a fresh temporary directory as its working
directory, cleaned up after the rubric completes. This is a convenience for
output collection — it is **not** a filesystem containment boundary (see §4).

## 3. Judge call routing

Any rubric requiring LLM calls uses the OmniRoute endpoint exclusively
(standing rule 3). The runner injects the OmniRoute base URL as
`RUBRIC_LLM_ENDPOINT`; no direct-provider credentials are passed.

## 4. NOT verified in the sandbox (delivered at the PC/production boundary)

- **Filesystem containment.** A separate cwd is not a jail, and the sandbox
  user namespace does not enforce host file ownership against an unmapped UID.
  Real FS containment is delivered by **gVisor + a mapped user namespace** at
  the PC/production boundary (standing rule 11: least privilege, non-root
  service users, gVisor containment). It is proven by the S0-08 gVisor proof,
  not here.
- **UDP/ICMP egress and DNS** inside the netns (only TCP loopback reachability
  is exercised as the network discriminator).
- **Live rubric workloads.** The probe reports process state; it does not run a
  real AlphaEval rubric. That integration is Wave-2 work.
