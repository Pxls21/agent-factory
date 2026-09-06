Done. The credential screen closure fix is applied and verified. Here's the summary:

**Reproduction confirmed** before any code change: `HTTP/1.1 200 OK` with the `%20`-split token recorded verbatim in `headers["x-trace"]`, recoverable by `re.sub(r"\s+", "", unquote(text))`.

**Three files touched** (as named in the boundary):
- `proofs/S0-01/tools/scripted_backend.py` — `_normal_forms` closure over `{unquote, unquote_plus, strip_ws}` (depth-5 bounded, fail-closed at bound), `_carries_secret` rewritten, `_iter_json_strings` iterative, `RecursionError` → `_BAD_CL`, `allow_nan=False` with non-finite coercion, docstring updated.
- `tests/test_s0_01_scripted_backend.py` — F13 `Handler.timeout` positive-number assert; F16 five new framing domain rows.
- `tests/red/test_s0_01_backend_credential_screen.py` — fixed broken `_post` f-string; F2 wide oracle (`{unquote, strip_ws, lower, unquote_plus}` depth-4); F3 obs-fold extended to LF; six new red tests covering F1, F4, F5, F6, F10, F11.

**Deviation flagged loud**: the brief specified `{unquote, strip_ws}` but the required 15/15 battery needs `unquote_plus` in the backend for `+` to be caught in all three sinks. The oracle remains strictly wider.

**Gate results**:
- pyflakes: rc=0 on all three files
- Full suite twice (xdist): 385 passed / 385 passed
- Red file standalone: 47 passed
- 15/15 battery: 15 passed

**Mutation testing**: 8/8 non-equivalent mutants killed. M57 survived (equivalent — quad-encoded token reached at depth 4, before the bound). M18 survived (equivalent — `read(0)` returns `b""` without consuming bytes). M29 not run — its definition is in the round-8 lane report, which is a 429 error page.

Report draft: `/home/rocco/agent-factory/.lanes/s0-01-d5e-credential-screen-closure.md--1e679825/report-draft.md`
