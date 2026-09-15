# VERIFY-QM0 report — qwen-server matrix knobs and pre-write lane guard

> **COORDINATOR DISPOSITION (2026-09-15 16:0xZ).** Finding 1 is FALSE on the real sink: `curl_key()` builds its header from
> `$(cat "$QWEN_KEY_FILE")` (`harness-ports/bin/qwen-server.sh:204`), and a read-only live probe read `/props` no-key 401, wrong-key 401,
> the launcher's header 200 (`/v1/models` is public: 200 for all three); the verifier's strict fake, not the server, rejected the request.
> Its kernel is TRUE and registered as AF-AP-83: `health` certifies readiness through the public `/v1/models` and the test's fake curl
> accepts any header — QM0-c (after QM0-b lands) moves `health` to a keyed endpoint with the 401 negative control and makes the fake
> validate the Bearer value. Finding 2 (the stale H identity row) was recorded at the QM0 landing. No verdict was expected (single-model rule).

NO VERDICT (single-model rule): findings only

Map: S=harness-ports/bin/qwen-server.sh; T=harness-ports/tests/test_qwen_server.sh; H=docs/HARNESS-PORTS.md; P=PC-BRIDGE.md. PIN `efde78d`. This verification used scratch-only copies and fake lifecycle seams. No real `qwen-builder` lifecycle command ran.

## Findings

1. [BLOCKING] `curl_key()` does not pass the API-key file's contents. S:204 passes the literal filename text as an incorrectly quoted, redacted-looking header argument. A strict fake curl that accepts only a Bearer header built from its configured test-key file makes `health` fail: `auth_shim_rc=1`, `qwen-server: /health not ok: <no answer>`. The stock T fake at T:322–326 returns models without validating the request, so T reports `qwen-server: 79 passed, 0 failed` while the real authenticated `/v1/models` request cannot work. Fix: read the key in a local variable without logging it, construct exactly one authorization header from it, and add a fake curl assertion that rejects an incorrect header and accepts the configured non-secret test key.

2. [SHOULD-FIX] The builder report’s H file-identity assertion is stale and objectively false. Its H proposal SHA is `cb88ec…`, but the PIN and landed H bytes are `60433df0…`; `git diff efde78d -- docs/HARNESS-PORTS.md` is empty. The documentation’s behavioural content did match the code in the reviewed lines (H:397–409; P:170–177). Fix the report identity row before using that report as evidence.

## V1 — guard against D-030

SOLID. S:159–185 implements D-030’s live-PID policy: `kill -0` selects live processes; unreadable or absent `HERMES_MODEL` maps to LOCAL; `*-local` maps LOCAL; other model strings map CLOUD; dead or malformed pidfiles print `stale`. Scratch real-child probes returned:

- local: rc 7, `lane.pid <pid> LOCAL`
- cloud: rc 0, `lane.pid <pid> CLOUD`
- absent route: rc 7, `lane.pid <pid> LOCAL`
- dead `99999999`: rc 0, `lane.pid 99999999 stale`
- empty: rc 0, `lane.pid <empty> stale`
- garbage: rc 0, `lane.pid bad-pid stale`
- unreadable synthetic proc root: rc 7, `lane.pid <pid> LOCAL`
- own cloud-route shell: rc 0, `lane.pid <pid> CLOUD`

A child zombie has `kill -0=0`; S classifies it LOCAL (rc 7). That is a conservative false refusal and agrees with D-030’s “any live PID” wording. The live read-only real-lane probe printed VERIFY-GOV1 as LOCAL and returned rc 7, alongside four CLOUD lanes and one stale lane.

## V2 — guard before effects

SOLID. In fake lifecycle seams, a live LOCAL child made all five commands return rc 7 with the exact refusal `qwen-server: a local-route lane is alive — service change refused 7`; every unit SHA stayed identical; fake systemctl calls=0; key=0; logs=0. This covers changed `install` (S:223–250) and the `change_service` `start`, `stop`, `restart`, `uninstall` command paths (S:276–286).

SOLID. `install` first runs `validate_knobs` and renders/compares candidate bytes (S:226–229), then runs `guard_or_die` before its first effect: active-state query at S:237, `mkdir` at S:238, `keygen` at S:239, unit write at S:240, and `systemd-analyze` / systemctl at S:241–246. An invalid knob can thus fail before a guard, but neither path has a persistent/service effect.

## V3 — identical unit no-op

SOLID. `install` compares rendered candidate bytes with the on-disk unit using `cmp -s` (S:227–232). A local live lane plus explicit `QWEN_SPEC_TYPE=draft-mtp` rendered identical bytes and returned rc 0, no systemctl calls. Adding one newline changed bytes; the fake run made five service calls and restored rendered bytes. Therefore no-op equality is rendered-byte equality, not input hashing, and hand-edited whitespace is treated as changed.

## V4 — knob domains

SOLID. `validate_knobs` starts at S:66; its p-min condition is `if [ -n "$QWEN_SPEC_P_MIN" ]` at S:72 and its heredoc ends at S:81. It rejects zero, negative, decimal, scientific, hex, plus-prefixed values for all positive integer knobs with rc 3; unset/empty optional values remain absent. It accepts p-min 0, 1 and `-0.0`, rejects `nan`, `inf`, `1.0000001`, and `-0.1` with rc 3 and the finite-range message. It rejects `draft-mtp ` and `DRAFT-MTP` with rc 3. `ngram-mod`/`none` omit MTP depth when `QWEN_MTP_N` is unset and reject explicit `QWEN_MTP_N` with rc 3. This covers the non-finite class, not only NaN.

## V5 — argv

SOLID. The freshly run T suite reports `qwen-server: 79 passed, 0 failed`; the `PIN_ARGV` pinned-fixture block starts at T:77 and `cmp -s "$PIN_ARGV" "$NEW_WITHOUT_CACHE_RAM"` is at T:119. It strips only `--cache-ram 8192`. S:91 starts `argv`; its `case` emits `draft-mtp` as `--spec-type draft-mtp --spec-draft-n-max 3`; `none` emits neither speculation token; `ngram-mod` emits `--spec-type ngram-mod` without MTP depth; unset optional scalar flags are absent (S:91–114).

## V6 — test oracle and key-before-guard mutant

UNSURE. T:322’s comment says `Fake health/probe traffic`; the fake `curl` sink’s `case "$*"` starts at T:326. The AF-AP-79 unit `UNIT_PATH` oracle starts at T:304. The fake uses no claimed server value outside the test shape. The negative lifecycle oracle observes unit bytes, call log, log directory, and key absence, not just the unit file. But it does not authenticate fake curl requests, yielding Finding 1.

SOLID. My scratch-only `keygen`-before-guard mutant was killed by a new independent byte/state probe: landed S yielded `key=0`, mutant yielded `key=1`, both rc 7. The existing T test would also fail this mutant at its AF-AP-79 assertion.

## V7 — docs

SOLID. H:397 begins with the literal `harness-ports/bin/qwen-server.sh argv|unit|keygen|guard|install|start|stop|restart|status|health|probe|uninstall`; P:170 begins its `Operate:` command. H:397–409 and P:170–177 accurately state the command surface, default cell, six knobs, accepted speculation types, rc 3 invalid-domain rule, D-030 stale/route behaviour, rendered-unit no-op, and guard-before-effect paths. The only documentation discrepancy found is evidentiary: the builder report’s H SHA is stale (Finding 2), not the documentation itself.

## V8 — mutation audit

SOLID. Scratch copies compiled with `bash -n`; each ran T after mutation. All six mutants were killed, so there were no survivors:

| mutant | failing assertion(s) |
| --- | --- |
| fixed cache RAM | `all five scalar matrix knobs render their flag/value pairs` (78/1) |
| LOCAL → CLOUD | `guard rc 7…`, AF-AP-79, refusal reason, and all four lifecycle refusal checks (72/7) |
| absent route → CLOUD | absent and empty fail-closed checks (77/2) |
| changed-install guard removed | AF-AP-79 and refusal-reason checks (77/2) |
| stale pid blocks | `guard reports and ignores a stale pidfile` (78/1) |
| uninstall guard removed | `uninstall refuses before disk or systemd change…` (78/1) |

## V9 — builder-report evidence audit

SOLID. Actual landed hashes: S `3a663e4f…`; T `2b3e51cc…`; H `60433df0…`; P `6bb45bd…`. S/T/P match the builder report. H does not: see Finding 2. The builder’s reported `46 refs — OK 20, NEAR 12, MISS 14` does not reproduce against the current report copy: `48 refs — OK 13, NEAR 17, MISS 18`; its `--min-refs 15` floor fails. This is a report-quality issue, not a code-semantic claim.

## Reproduced gates and static review

- `PATH=/home/rocco/venv-agent-factory/bin:$PATH bash harness-ports/tests/test_qwen_server.sh`: `qwen-server: 79 passed, 0 failed`.
- AP screen: S had 0 hits. T had one AF-AP-33 fake-curl hit at T:326; it is explicitly labelled as a sink fake but is insufficiently strict per Finding 1.
- ShellCheck is unavailable on this host; it was not installed.
- Graft had no index for these shell files; GitNexus returned target not found/risk UNKNOWN for shell `guard`; ripwire observed `guard_or_die` as the direct caller of `guard`. These are advisory-only and do not support a reachability verdict.

## Not done

- No real `install`, `start`, `stop`, `restart`, or `uninstall`; no service, GPU, or owner lane was touched.
- No live authenticated model-server call was made. Finding 1 is established against a strict fake request sink.
- `harness-ports/tests/run-all.sh` was not rerun. The brief records its prior sandbox success and unrelated dispatcher instability; this review’s affected suite was rerun fresh.
- No patch was applied to landed files. The coordinator must route the findings to a builder and a sandbox-side independent verifier.

## Discrepancies

- `graft` lacks indexed definitions/scopes for the reviewed shell files despite `graft/INDEX.md`; used ripwire plus direct primary-source reads instead.
- First V1 scratch script had an argument-order defect and produced `env: ‘local’: Permission denied`; corrected once before recording any V1 evidence. No source bytes changed.
- `report_lint` final bounded round (round 3) is recorded in this report as `report_lint: 30 refs — OK 22, NEAR 5, MISS 2, UNCHECKABLE 1, UNRESOLVED 0`; the 15-reference floor passes. The misses are S:81’s heredoc terminator and this lint-summary line’s self-reference; the UNCHECKABLE is the AP-screen line. All are reported, not chased (AF-AP-76).
- `curl_key` redacts a pseudo-key in process argv but fails to read the configured file; the report never prints the real key.

## Hygiene

No worktree production files changed beyond the two staged lane-brief files supplied at launch. All mutation copies and fakes were under `../scratch`; children were killed and waited by PID. Retro: new defect class is “auth sink fake accepts unauthenticated traffic”; send to bug-echo/incident registry with Finding 1 before any repair closes.
