# Hermes Evaluation Runner Design

## 1. Problem statement

The stock AlphaEval runner exposes three documented hazards (component audit §3):

1. **Host networking** — rubric subprocesses share the host network namespace,
   enabling data exfiltration or lateral movement.
2. **Recursive chmod 777** — workspace permissions are opened recursively,
   allowing rubric code to read or modify any file in the evaluation workspace.
3. **Production credential passing** — environment variables containing API keys
   (OPENAI_API_KEY, ANTHROPIC_API_KEY, OMNIROUTE_API_KEY) are inherited by
   rubric processes.

## 2. Design: isolated rubric execution

### 2.1 Network isolation (no host networking)

Every rubric process runs inside a separate network namespace created with
`unshare --net`. The namespace contains only the loopback interface
(unconfigured), preventing any outbound connection.

### 2.2 Permission hardening (no recursive chmod 777)

The runner never applies recursive permission changes. Task inputs are copied
into the rubric working directory with mode 0o644 (files) and 0o755
(directories). The rubric process has read access to inputs and write access
only to its own temporary output directory.

### 2.3 Credential isolation (no production credential passing)

The runner constructs a clean environment for rubric processes by stripping
all credential-bearing environment variables. The stripped set includes:

- OPENAI_API_KEY, ANTHROPIC_API_KEY, OMNIROUTE_API_KEY, HERMES_API_KEY
- Any variable matching *_SECRET, *_TOKEN, *_CREDENTIAL

The rubric process receives only: PATH, HOME, TMPDIR, LANG, and
runner-specific variables (RUBRIC_TASK_ID, RUBRIC_CWD).

### 2.4 Separate working directory

Each rubric invocation receives a fresh temporary directory as its working
directory. This directory is isolated from the production workspace and
cleaned up after the rubric completes.

## 3. Judge call routing

Any rubric requiring LLM calls uses the OmniRoute endpoint exclusively
(standing rule 3). The runner injects the OmniRoute base URL as
RUBRIC_LLM_ENDPOINT; no direct-provider credentials are passed.
