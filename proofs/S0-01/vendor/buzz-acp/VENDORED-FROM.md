# Vendored: `acp.rs` from buzz at the pinned commit (verbatim, never edited)

| field | value |
|---|---|
| source repository | https://github.com/block/buzz.git (`upstream.lock.yaml` entry `buzz`, license Apache-2.0) |
| commit | `1c8321cd08feb597f8bcff5195c21148fb3e98ed` (the S0-01 pinned buzz-acp; `proofs/S0-01/pins.py`) |
| path in the source tree | `crates/buzz-acp/src/acp.rs` |
| sha256 | `44e82861763694d2b82d02b15ee100ffd6c78874a2b2282865e6656c539c38f1` (5030 lines, 217 424 bytes) |
| how it got here | `git show <commit>:<path>` on the owner's pinned clone `/home/rocco/s0-01-pinned/buzz` (HEAD = the commit), brought home through `scripts/pc_fetch.sh` (size-verified chunks), 2026-09-07 |
| independent confirmation | VERIFY-B5f (2026-09-07) fetched the same path from `raw.githubusercontent.com` at the same commit and recorded the same sha256 |
| purpose | the mechanical ORACLE for the tee's shutdown-bound prose (`tests/test_s0_01_frame_tee.py`): buzz-acp `killpg(SIGKILL)`s the agent's process group FIRST (`kill_process_group`, `:2323-2328`) and then waits up to 5 s for the child (`shutdown`, `:422-444`); the file contains no `SIGTERM`. A docstring that says otherwise is contradicted by this artifact, not by a word list (VERIFY-B5g F-B5g-1) |
| rule | never edit; regenerate only by re-fetching the pinned commit and updating the sha256 here and in the test's premise assertion |
