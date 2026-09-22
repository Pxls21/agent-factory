# PC lane — VERIFY-GOV2d (the independent targeted adversarial verify of GOV2d: the review binding's fixed gpg trust root, the fixed child PATH, and the regular-file proof on the FD — new shapes, never the builder's cases)

PIN: d116cbc

Role: adversarial-verifier. Route: the LOCAL verify route (`agentfactory-verify-local`, the vLLM server default effort; the
route is HYBRID in practice — the cloud step serves a turn when the local step refuses with the chat-template 400 — say so in
the report header, claim nothing about which model produced this report). Venue: `tasks/briefs/pc/VENUE-MAP.md` — read it
first. Honey mode: full (line-bounded findings, evidence anchors, SOLID/UNSURE). Keep your context small: bounded terminal
output (`| tail -n 40`), the report drafted after each item, never a whole-file read where `sed -n` of a range answers.

AUTHORIZATION: defensive verification of the owner's own governance binding on the owner's PC. Every gpg run uses a scratch
GNUPGHOME under the lane's own directory with throwaway keys; the committed owner public key is read, never any private
material of the owner's; no production service, no host secret file, no commit, no push, no repair. The `gpg=` kwarg of
`verify_review` is used ONLY to point at scratch doubles under the lane directory.

## THE CONTRACT — the frozen contract is the GOV2d brief `tasks/briefs/pc/pc-gov2d.md` (VERIFY-GOV2c-B F1/F2 under D-031: B/F1
the gpg executable never resolved from the caller's PATH; B/F2 the is_file()-then-open window closed by a regular-file proof on
the FD, a planted FIFO refused by name never a hang) graded against the landed bytes at the PIN; the lane's own report
`tasks/briefs/stage3-governance-support/GOV2d-report.md` is the CLAIM under test, never the oracle. Verify EVERY claim through
the real production path (`agent_factory.governance.review.verify_review` imported from the PIN tree, the real `/usr/bin/gpg`),
report every observation (no severity filter), then apply the blocking predicate (contract-mapped · canonically reproduced ·
materially effective · a concrete discriminator · in-boundary) and return a GATE RECOMMENDATION (`MERGE-READY` /
`MERGE-READY-WITH-FOLLOWUPS` / `NOT-READY` / `CONTRACT-INVALID`) — the coordinator owns the gate.

Files (read-only for you; write ONLY the report): RV `src/agent_factory/governance/review.py`, TR
`tests/test_governance_review.py`, RM `docs/governance/reviews/README.md`, PK `src/agent_factory/governance/packet.py` (the sole production caller),
GR `tasks/briefs/stage3-governance-support/GOV2d-report.md`. Report: `tasks/briefs/stage3-governance-support/VERIFY-GOV2d-report.md`.
Declared test inputs (exported by `scripts/fubuki_pin_sync.sh`, present on the PC): `FUBUKI_OS_ROOT`, `FUBUKI_OTHER_ROOT`.

## PREMISE — MEASURED at authoring (2026-09-22T14:04:53Z, the sandbox clone at the PIN = origin head after the GOV2d harvest; the PC clone ff-synced to the same head); re-measure as item 1

```
PIN d116cbc (the GOV2d harvest on origin); date 2026-09-22T14:04:53Z
src/agent_factory/governance/review.py sha256[:16]=06da43e1024e548b lines=211 last-commit=d116cbc
tests/test_governance_review.py sha256[:16]=1ec52c579c7b4558 lines=476 last-commit=d116cbc
docs/governance/reviews/README.md sha256[:16]=20be44677047f037 lines=74 last-commit=d116cbc
src/agent_factory/governance/packet.py sha256[:16]=5d8cf21468adb55e lines=156 last-commit=756d516
--- RV anchors (grep -n)
46:_MAX_RECORD_BYTES = 1 << 20  # a review record is a few hundred bytes; refuse anything absurd
51:_GPG_PATHS: tuple[str, ...] = ("/usr/bin/gpg", "/usr/bin/gpg2")
58:def _read_regular_file(path: Path) -> bytes:
63:    fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK | os.O_CLOEXEC)
65:        st = os.fstat(fd)
66:        if not stat.S_ISREG(st.st_mode):
67:            raise OSError("review record is not a regular file")
75:            if total > _MAX_RECORD_BYTES:
101:def verify_review(
106:    gpg: str | Path | None = None,
117:    fubuki-review-gpg-unavailable before anything runs.
137:        if not gpg_path.is_absolute() or not gpg_path.is_file():
138:            raise GovernanceError("fubuki-review-gpg-unavailable", f"gpg must be an absolute regular file: {gpg}")
143:        gpg = next((p for p in _GPG_PATHS if Path(p).is_file()), None)
145:            raise GovernanceError("fubuki-review-gpg-unavailable", "no gpg at " + ", ".join(_GPG_PATHS))
152:        record_bytes = _read_regular_file(record_path)
153:        sig_bytes = _read_regular_file(sig_path)
154:        owner_key_bytes = _read_regular_file(owner_key)
156:        raise GovernanceError("fubuki-review-record-invalid", str(exc)) from exc
168:        env = {"GNUPGHOME": home, "PATH": "/usr/bin:/bin", "LC_ALL": "C"}
183:            raise GovernanceError("fubuki-review-gpg-unavailable", str(exc)) from exc
202:        raise GovernanceError("fubuki-review-record-invalid", str(exc)) from exc
204:        raise GovernanceError("fubuki-review-record-invalid", "record is not a JSON object")
--- RV: shutil / environ / which occurrences
0
--- PK: the production call(s) of verify_review
155:    verify_review(packet_hash, reviews_dir=reviews_dir, owner_key=owner_key)
--- TR anchors (grep -n)
40:    """FUBUKI_OS_ROOT (a declared input) reaches the tests only through the production pin (AF-AP-81)."""
41:    value = os.environ.get("FUBUKI_OS_ROOT")
43:        pytest.fail("FUBUKI_OS_ROOT is a declared GOV1 test input")
114:def test_valid_owner_signed_review_passes(tmp_path: Path, keys) -> None:
120:def test_absent_review_refuses(tmp_path: Path, keys) -> None:
127:def test_review_signed_by_non_owner_is_refused(tmp_path: Path, keys) -> None:
134:def test_review_naming_a_different_hash_does_not_authorize(tmp_path: Path, keys) -> None:
141:def test_tampered_record_is_refused(tmp_path: Path, keys) -> None:
148:def test_reviewed_false_refuses(tmp_path: Path, keys) -> None:
155:def test_a_review_for_one_hash_does_not_authorize_another(tmp_path: Path, keys) -> None:
162:def test_a_non_hex_hash_is_refused(tmp_path: Path, keys) -> None:
171:def test_load_packet_with_a_valid_review_returns_reviewed(tmp_path: Path, keys) -> None:
181:def test_load_packet_without_a_record_refuses(tmp_path: Path, keys) -> None:
192:def test_toctou_a_flip_after_verify_does_not_grant_review(tmp_path: Path, keys, monkeypatch) -> None:
213:def test_a_revoked_key_with_a_goodsig_notation_is_refused(tmp_path: Path, keys) -> None:
242:def test_two_keys_in_the_owner_file_are_refused(tmp_path: Path, keys) -> None:
252:def test_a_non_object_record_raises_a_governance_error(tmp_path: Path, keys) -> None:
264:def test_gpg_absent_raises_a_governance_error(tmp_path: Path, keys, monkeypatch) -> None:
274:def test_a_symlinked_record_is_refused(tmp_path: Path, keys) -> None:
316:    signal.signal(signal.SIGALRM, on_alarm)
322:    signal.signal(signal.SIGALRM, signal.SIG_DFL)
332:def test_gpg_is_never_resolved_from_the_callers_path(tmp_path: Path, keys, monkeypatch) -> None:
346:def test_a_hostile_path_does_not_break_the_real_gpg(tmp_path: Path, keys, monkeypatch) -> None:
356:def test_the_child_path_is_fixed(tmp_path: Path, keys, monkeypatch) -> None:
377:def test_an_explicit_gpg_must_be_an_absolute_regular_file(tmp_path: Path, keys, monkeypatch) -> None:
397:def test_a_fifo_swapped_in_after_the_precheck_is_refused_not_hung(tmp_path: Path, keys, monkeypatch) -> None:
427:def test_a_fifo_swapped_in_for_the_signature_is_refused_not_hung(tmp_path: Path, keys, monkeypatch) -> None:
457:def test_a_fifo_at_the_record_path_is_unreviewed(tmp_path: Path, keys) -> None:
470:def test_the_read_primitive_proves_the_fd_not_the_path() -> None:
472:    os.fstat(fd) and the read cannot be forced by these tests, so the source shape is pinned: the
473:    regular-file proof must be on the FD (os.fstat(fd)), never on the path (os.stat)."""
475:    assert "os.fstat(fd)" in src
--- GR: mutant table rows
149:| m1 restore `shutil.which("gpg")` | `4 failed, 6 passed, 14 deselected in 0.65s` | `1 failed, 23 deselected in 0.10
150:| m2 forward caller PATH | `1 failed, 9 passed, 14 deselected in 0.65s` | `1 failed, 23 deselected in 0.13s` | hosti
151:| m3 drop `O_NONBLOCK` | `2 failed, 8 passed, 14 deselected in 20.65s` | `2 failed, 22 deselected in 20.16s` | detai
152:| m4 drop `S_ISREG` check | `2 failed, 8 passed, 14 deselected in 0.67s` | `2 failed, 22 deselected in 0.16s` | reas
153:| m5 `_GPG_PATHS = ("gpg",)` | `5 failed, 5 passed, 14 deselected in 0.63s` | `1 failed, 23 deselected in 0.09s` | `
154:| m6 drop `is_absolute()` | `1 failed, 9 passed, 14 deselected in 0.65s` | `1 failed, 23 deselected in 0.10s` | exis
155:| m7 drop `O_NOFOLLOW` | `1 failed, 9 passed, 14 deselected in 0.66s` | `1 failed, 23 deselected in 0.11s` | symlink
156:| m8 `os.fstat(fd)` → `os.stat(path)` | `1 failed, 9 passed, 14 deselected in 0.65s` | `1 failed, 23 deselected in
--- gpg versions: sandbox gpg (GnuPG) 2.4.4; PC = the lane measures
--- sandbox census (coordinator, 14:04Z): gpg-agent processes 0 before, 25 [gpg-agent] <defunct> after ONE review-suite run (24 passed in 2.05s), gpg 2.4.4; the lane's PC census 0 -> 0 (GR PC GATES (d))
--- coordinator mutant re-runs (sandbox, in place, restored bitwise): m1 2 failed/22 passed; m2 1 failed/23 passed; m4 2 failed/22 passed; m7 1 failed/23 passed; m8 1 failed/23 passed; clean 24 passed in 2.08s
```

## ITEMS (in order; the report drafted after each; every run pasted)

1. **Re-measure the premise** at the PIN in your worktree (the same commands; paste). Export the declared inputs. Any sha
   or anchor that differs → STOP, first section = the discrepancy.

2. **The trust root** through the real `verify_review` with a scratch owner key + a scratch signed record (build them once
   under the lane dir with the real gpg; the committed owner key is not needed for these shapes): (a) production never
   passes `gpg=` — paste PK's call; (b) with an EMPTY caller `PATH` (`env -i` or `PATH=`) the real `/usr/bin/gpg` still
   verifies (the fixed path is the root, not a lookup); (c) a hostile PATH whose first `gpg` is a scratch script that prints
   a shaped `[GNUPG:] GOODSIG …` line for an UNSIGNED record → the record is REFUSED (the B item-5 attack, on the PIN bytes);
   (d) an explicit `gpg=` that is a bare name, a relative path to an EXISTING file (after chdir), a directory, a missing path,
   a symlink to a regular file → each refused as `fubuki-review-gpg-unavailable` before any process runs (prove nothing ran:
   the scratch target logs its invocation); (e) `_GPG_PATHS` when `/usr/bin/gpg` is absent is not testable on the PC without
   touching the host — SAY SO; grade the fail-closed branch by reading it and by the m5 mutant only.

3. **The regular-file proof on the FD** through the real `verify_review` (the record path, then the signature path, then the
   owner-key path — all three go through `_read_regular_file`): a FIFO with a LIVE WRITER attached (a writer process holding
   the write end; the open must not block and the writer's bytes must never be read), a FIFO with no writer, a directory, a
   character device (`/dev/zero` — prove the refusal is the S_ISREG check by its exact detail text, not the `_MAX_RECORD_BYTES`
   cap), a symlink to a regular file (O_NOFOLLOW), a symlink to a FIFO, a socket file, a hard link (a regular file — allowed;
   state it). Each: the exact reason + detail; wall time bounded (a 10 s alarm guard of your own). The pre-check order: a
   FIFO present at the pre-check refuses as `fubuki-packet-unreviewed` (RV's pre-check) while a FIFO planted AFTER the
   pre-check refuses on the FD as `fubuki-review-record-invalid` — force the second with a swap between the two calls (a
   scratch subclass/monkeypatch of `Path.is_file` inside the TEST only is acceptable to force the window; the production
   bytes stay untouched) and paste both texts.

4. **The child environment**: with the fixed `PATH=/usr/bin:/bin`, does the real gpg 2.4.7 verification (import + verify)
   need anything outside it (`gpg-agent`, `dirmngr`, `pinentry`)? Run a positive verification under `strace -f -e execve`
   (if available; else `gpg --debug-level` output) and list every executable the child tree executes with its path; a
   binary outside `/usr/bin:/bin` would be a finding.

5. **The alarm-guard tests** (TR's SIGALRM guard, the AF-AP-58 screen hits): run TR under `-n 4` twice and serially once on
   the PC (paste); confirm `signal.signal` runs on the main thread in both shapes (a non-main thread raises `ValueError` —
   grep xdist's worker model or observe by run). If a shape is green only by timing, say so.

6. **The AF-AP-110 census, both venues** (the GOV2d brief folded the cleanup in only if F3 reproduced on 2.4.4 — the
   coordinator measured 0 → 25 `[gpg-agent] <defunct>` in the sandbox after ONE suite run on gpg 2.4.4; the lane measured
   0 → 0 on the PC): reproduce on the PC — count live AND defunct `gpg-agent` processes before/after one TR run and after
   ten `verify_review` calls in a loop; explain the venue difference (a reaping init vs a live orphan; the agent exits when
   its socket dir vanishes); then, READ-ONLY and outside the tree, test whether `--no-autostart` on RV's two gpg invocations
   (`--import` of a PUBLIC key, `--verify`) succeeds on 2.4.7 without starting an agent (a scratch copy of RV under the lane
   dir, never the worktree file). The outcome is a FINDING for the follow-up (issue / GOV2e), never an edit.

7. **Mutants**: re-run the report's m1-m8 from your OWN scratch copies (never the worktree RV; each compiles and collects
   first, AF-AP-78; the killing test named), then add v1 `_GPG_PATHS` order swapped (gpg2 first — equivalent on a host
   without gpg2? state the venue fact), v2 the explicit-gpg `is_file()` check removed (a directory passes), v3 `O_CLOEXEC`
   dropped (equivalent under the suite? a declared limit or a finding — prove it by a leaked-fd census across the gpg
   subprocess if you can), v4 the S_ISREG refusal's detail text changed (which test pins the text?). A survivor is a row.

8. **The report's evidence**: reproduce GR's lint at 2da04bf and at the PIN (`scripts/report_lint.py`); the RED-first table
   (GR:50-83) — re-run two of its seven REDs against the PIN's PARENT bytes (`git show 2da04bf:src/agent_factory/governance/review.py`
   into a scratch module) to confirm they were red for the stated reason (AF-AP-114: the first failing assertion pasted).

9. **Screens**: `python3 scripts/ap_screen.py` on RV + TR + RM at the PIN (paste); every hit explained or a finding.

10. **GATE RECOMMENDATION** with the blocking predicate applied per finding; followups listed for D-034's verify-followup issue.

## RULES THAT SURVIVE EVERYTHING

- CODE INTEL FIRST: `scripts/lane_context.sh` / `graft ask` before reading whole files; the pack is attached to your prompt.
- Every count and timestamp is PASTED; every shape is NEW (never the builder's fixture reused as-is); the production bytes are
  never edited (scratch copies only; `git status --porcelain` clean except the report).
- No commit, no push, no outward action; the coordinator harvests and owns the gate.
