# Security policy

This repository is a design artifact and is not yet safe to deploy.

## Reporting

Do not open a public issue containing credentials, exploitable deployment details, or private user data. Report sensitive findings privately to the repository owner after the GitHub security contact is configured.

## Secret rules

- Never commit `.env`, API keys, Buzz private keys, OmniRoute bootstrap secrets, memory root tokens, or signing material.
- Hermes receives only an internal OmniRoute credential, never provider credentials.
- Dream workers, JIT/Foundry jobs, generated candidates, and evaluators receive no production credentials, data, or mutation authority.
- Use secret files or a secrets manager in deployment; environment examples are names only.

## Current security blockers

- The policy hook and decision service do not exist yet.
- The gVisor deployment has not been proven on the target host.
- The ai-memory delete and promotion surfaces have not been restricted.
- The four-scope composite adapter and cross-scope isolation tests do not exist yet.
- Buzz membership revocation and independent freshness checks have not been implemented.
- GBrain/JIT proposal and candidate sandboxes have not been implemented.
- AlphaEval's stock runner is not approved because it uses host networking, broad write permissions, and passes credentials directly into agent containers.

See `docs/05_SECURITY.md` for the full threat model and acceptance gates.
