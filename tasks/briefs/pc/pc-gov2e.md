# GOV2e — the ONE focused repair of VERIFY-GOV2d's Finding 1 on the review binding (D-031)

PIN: c4d12d1 (the post-push SHA of the VERIFY-GOV2d harvest commit; `src/agent_factory/governance/review.py` sha256[:16] 06da43e1024e548b and `tests/test_governance_review.py` 1ec52c579c7b4558 — both byte-identical to the GOV2d PIN d116cbc)
LANE: pc-gov2e
ROLE: code-implementer (build) — the STRICT local route: `HERMES_MODEL=qwen-local/qwen3.8-27b-local` (D-039(a) + D-042(2): a raw id routes without a combo, so no universal handoff on this lane)
COMPONENT: `src/agent_factory/governance/review.py` (RV) + `tests/test_governance_review.py` (TR) — NOTHING ELSE. `docs/governance/reviews/README.md` and `packet.py` are OUT of boundary (README wording = issue #21 F2, not this lane's).
CONTRACT REVISION: the VERIFY-GOV2d report `tasks/briefs/stage3-governance-support/VERIFY-GOV2d-report.md` (frozen: Finding 1 is the blocker; F2/F3/F4 = issue #21, NOT this lane's). The GOV2d contract item 2(d): an explicit `gpg=` that is an absolute SYMLINK to a regular file must be refused as `fubuki-review-gpg-unavailable` BEFORE any process runs.
BUDGET: one repair round; nothing outside Finding 1.
ENVIRONMENT (the governance tests are declared inputs): export `FUBUKI_OS_ROOT` and `FUBUKI_OTHER_ROOT` from `bash scripts/fubuki_pin_sync.sh` before pytest; a short `--basetemp` (gpg-agent's socket path limit: `mkdir -p /home/rocco/tmp-gov2e/bt && pytest --basetemp=/home/rocco/tmp-gov2e/bt …` — NEVER the PC's tmpfs `/tmp` for trees).

## What VERIFY-GOV2d proved (Finding 1, SOLID; reproduced by the coordinator in the sandbox 2026-09-22 15:4xZ)

`review.py:135-139` (verbatim at the PIN):
```
        # An explicit gpg is a deliberate code decision (tests); it must name an absolute regular file.
        gpg_path = Path(gpg)
        if not gpg_path.is_absolute() or not gpg_path.is_file():
            raise GovernanceError("fubuki-review-gpg-unavailable", f"gpg must be an absolute regular file: {gpg}")
        gpg = str(gpg_path)
```
`Path.is_file()` FOLLOWS symlinks, so an absolute symlink to a regular executable passes and its TARGET RUNS. Coordinator reproduction (scratch dir; a sentinel script `touch SENTINEL-RAN; exit 2` behind an absolute symlink passed as `gpg=`; a reviews dir with a record + a fake signature; a fake owner key):
```
link is_symlink: True | Path.is_file() on the symlink: True | lstat regular: False
raised: GovernanceError fubuki-owner-key-invalid
SENTINEL EXECUTED via the symlink gpg= : True
```
The production default path (`load_packet` at `packet.py:155`, no `gpg=`) is unaffected; the explicit test-only interface is the defect.

## The repair (exactly this)

1. In the explicit-`gpg=` branch, refuse a symlink BEFORE `is_file()`: `os.lstat(gpg_path)` must exist and `stat.S_ISREG(st.st_mode)` must be true on the PATHNAME ITSELF (no following) — or equivalently `gpg_path.is_symlink()` → refuse; then keep `is_absolute()` + `is_file()`. The reason stays `fubuki-review-gpg-unavailable`; the detail names the pathname and says it must be an absolute regular file, not a symlink. Nothing else in `review.py` changes (the `_GPG_PATHS` default branch, the FD proof, the child env are untouched — they HELD under VERIFY-GOV2d).
2. The committed FAILING regression (RED at the PIN, GREEN after): `test_explicit_gpg_symlink_is_refused_before_any_process_runs` — creates an absolute symlink to a sentinel executable (a shell script that writes a marker file), calls `verify_review(..., gpg=<symlink>)` with a valid reviews dir shape, asserts `GovernanceError` with reason `fubuki-review-gpg-unavailable`, asserts the MARKER DOES NOT EXIST (zero invocation), and asserts the detail mentions the pathname. Also the positive control: the same sentinel passed by its REAL absolute regular path still reaches the subprocess (the marker exists) — proving the refusal is about the symlink, not the sentinel.
3. A second negative shape: a symlink whose TARGET is missing (dangling) — refused with the same reason, no invocation.

## Gates (paste verbatim)
- `python -m pytest tests/test_governance_review.py -q -p no:cacheprovider --basetemp=/home/rocco/tmp-gov2e/bt` TWICE (counts bitwise-identical; the current file collects 24 tests — paste the new count); `python -m pyflakes src/agent_factory/governance/review.py tests/test_governance_review.py` if pyflakes is present, else say NOT run (the lane environment lacked it 2026-09-22).
- Mutants (each in a scratch copy, the killing test named): (m1) drop the symlink refusal (restore the PIN's two-clause check) → the new regression red; (m2) refuse symlinks but AFTER the subprocess spawn → the zero-invocation assertion red; (m3) change the reason string → the reason assertion red; (m4) `is_symlink()` replaced by `os.path.islink(str(gpg_path).rstrip('/'))`-style equivalence — state EQUIVALENT if no test discriminates, do not invent a kill.
- Coordinator gates at landing (not yours): `harness-ports/tests/run-all.sh`, `python3 scripts/ap_screen.py src/agent_factory/governance/review.py --tests tests/test_governance_review.py`, `report_lint --min-refs 10`.

## Report (`tasks/briefs/stage3-governance-support/GOV2e-report.md`)
DATA: files:lines changed; the RED→GREEN pair pasted; the mutant rows; the two pytest runs with counts; DISCREPANCIES / NOT-done (F2/F3/F4 are issue #21 — say so). Never touch the ledger, the wiki, any brief, `packet.py`, or the README.

## PREMISE — MEASURED at authoring (2026-09-22 15:4xZ, sandbox clone @ c4d12d1; re-verify at the PIN before editing)
```
$ git diff --stat d116cbc c4d12d1 -- src/agent_factory/governance/review.py tests/test_governance_review.py docs/governance/reviews/README.md
(prints nothing — the three files are byte-identical to the GOV2d PIN)
$ sed -n '137p' src/agent_factory/governance/review.py
        if not gpg_path.is_absolute() or not gpg_path.is_file():
$ grep -n 'is_symlink\|lstat' src/agent_factory/governance/review.py
(no output — no symlink refusal exists at the PIN)
$ grep -c 'def test_' tests/test_governance_review.py
24
$ wc -l src/agent_factory/governance/review.py tests/test_governance_review.py
  211 src/agent_factory/governance/review.py
  476 tests/test_governance_review.py
$ sha256sum src/agent_factory/governance/review.py tests/test_governance_review.py | cut -c1-16
06da43e1024e548b
1ec52c579c7b4558
```
