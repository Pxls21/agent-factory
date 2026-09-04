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
`probe uid != parent uid`. A wrapper that fails to create the user namespace
(e.g. a pass-through `unshare`) leaves the UID unchanged and is rejected.

### 2.2 Network isolation (no host networking)

The new network namespace contains only an unconfigured loopback, so no
outbound connection is possible. The checker does NOT rely on "cannot reach an
external address" (that is a tautology inside an already-egress-filtered
sandbox). Instead it holds a loopback listener in its OWN netns and asserts the
rubric probe **cannot reach it** — a signal only real namespace isolation can
produce — while an un-wrapped probe reaches it. Namespace identity is confirmed
separately: `/proc/self/ns/net` inode of the probe differs from the parent's.

### 2.3 Credential isolation — allow-list, not blacklist (no credential passing)

The runner builds the rubric environment from an **allow-list**: only
`PATH, HOME, LANG, LC_ALL, LC_CTYPE, TMPDIR` and runner-specific `RUBRIC_*`
variables are passed. Every other variable — every present or future
credential, whatever it is named — is stripped by construction. A name
blacklist is explicitly rejected: it missed production credentials such as
`OMNIROUTE_INTERNAL_API_KEY`, `BUZZ_PRIVATE_KEY`, and `STORAGE_ENCRYPTION_KEY`.
The checker injects those exact decoys into the parent environment and asserts
they are absent from the wrapped probe and present in the un-wrapped one.

### 2.4 Permission hardening (no recursive chmod 777)

The runner never applies recursive or world-writable permission changes. The
S0-11 grep sweep enforces this across the proof's executable/config surface
(all files except Markdown docs and the checker itself): it rejects
world-writable `chmod`, octal (`777`, `0777`, `666`, ...) or symbolic
(`o+w`, `a+w`, `go+rwx`, ...), and any host-networking directive
(`--network host`, `network_mode: host`, `hostNetwork: true`, ...).

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
