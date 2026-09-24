# PC lane VERIFY-J1-45 (task #217): the independent verify of J1-4 (the Laya pin) and J1-5 (the no-model closure)

PIN: 780f25a (the post-push origin head). J1-4 landed as 20da862; J1-5 as 342a5fe, hardened by 227bd82 (the blocker reaches every
process and counts attempts, AF-AP-179) and by 0574ac1 (the coordinator's pre-verify mutation audit: every check got a killing
negative control). All four commits are ancestors of the PIN; the premise block shows the boundary blobs.

Role: adversarial-verifier. Route: the LOCAL verify route (`agentfactory-verify-local`, xhigh; D-061: local Hermes only while the owner's
cloud subscription is out). Claim nothing about which model you are; the harvest measures the provider mix. Venue:
`tasks/briefs/pc/VENUE-MAP.md`, read it FIRST. Honey full: line-bounded findings, evidence anchors, SOLID/UNSURE. Keep your context
small: `| tail -n 40` on long output, `sed -n` ranges instead of whole-file reads. Do NOT spawn subagents.

AUTHORIZATION: read-only verification of the owner's own pin record and tests on the owner's own PC. Network: read-only public GETs to
`pypi.org` and `huggingface.co` metadata endpoints and one `pip download` of the pinned wheel into your scratch directory, nothing else.
No model inference, no server touch: the `laya-systemone` unit, vLLM, OmniRoute and every other running service stay as they are. Never
install anything into an existing venv; `/home/rocco/laya-venv` is the Laya endpoint's venv and is READ-ONLY to you.

## WHY (read first)

J1-4 and J1-5 are GATED-PENDING-VERIFY (rule 0f): the only gates so far are the coordinator's own tests, its own mutation audit and its
own full-suite run. This lane is the independent check. J1-4 records the Laya checkpoint J0 measured as an ADVISORY pin in
`upstream.lock.yaml` (`advisory_models.laya-typed-decisions`); J1-5 proves the decision ledger (J1-0..J1-3) has no model dependency.

CONTRACT SOURCES (read whole before you attack): `seeds/seed-laya-j1-v1.yaml` (the ACs that name `PINNED`, the no-model rule and the full
suite) · `tasks/laya-j1-breakdown.md` rows J1-4 and J1-5 (their gates and mutants m1) · `docs/research/findings/LAYA-PROBE-1.md` and its
two JSONs (the measured values) · D-044 and D-045 in `docs/08_DECISION_LOG.md` · AF-AP-179 in `docs/INCIDENT-LOG.md` (the closure's
design). The coordinator's ledger entries (`todo/BUILD-TASKLIST.md`, the J1-4, J1-5 and hardening notes of 2026-09-24) are CLAIMS to
attack, not truths.

## Items (report EVERY observation; no severity filter; rank downstream)

1. **Premise.** Re-measure the block below at the PIN in your tree. A mismatch in the boundary stops the lane CONTRACT-INVALID; say what
   differs.
2. **The pinned values, from primary sources, independently of the probe JSONs.** For each, paste the command and its output:
   (a) the revision: the snapshot directory in `/home/rocco/j0b/hf-cache` and the Hub's own answer
   (`https://huggingface.co/api/models/convaiinnovations/laya/revision/<rev>`); note every OTHER snapshot the cache holds and what it is;
   (b) the weights digest: `sha256sum` of the pinned snapshot's `typed-decisions/model.safetensors` (resolve the symlink to its blob) AND
   the Hub's LFS `oid` for that file at that revision (the tree API); (c) the wheel digest: `pip download laya==0.3.5 --no-deps` into
   your scratch and `sha256sum` it, AND PyPI's published digest (`https://pypi.org/pypi/laya/0.3.5/json`); (d) the package version:
   `importlib.metadata.version("laya")` in `/home/rocco/laya-venv` (read-only) and in the J0 PC probe JSON; (e) the lock's
   `runtime_measured` and `verdicts` strings against the two probe JSONs and the report. Every disagreement is a finding.
3. **The pin test, attacked with your own shapes** (never only the coordinator's table below). Ideas, not a limit: a row whose
   `revision` YAML-loads as an int; `advisory_models` as a list; a probe JSON missing `versions`; an uppercase-hex digest; a digest with
   trailing whitespace; a report that names the value only inside a longer token; a second `laya-typed-decisions` key (YAML duplicate
   keys); a lock row with an extra unknown key. For each: red by name, a crash, or a silent pass? A silent pass on a shape that a
   reviewer would call a drifted pin is a finding.
4. **The lock's other consumers.** The new block must not change any other reader of `upstream.lock.yaml`: `python3
   scripts/vendored_manifest.py --check` (its `parse_lock` reads `repository`/`commit`/`*_sha256` keys; the block avoids them on
   purpose: is that enough?), and every test that loads the lock (find them: `grep -rln "upstream.lock" tests/ proofs/ scripts/`).
   Paste each run with the PC venue exports.
5. **The closure (`tests/test_decisions_no_model.py`).** (a) Reproduce its four tests twice. (b) The static scan: list import forms it
   misses (for example `from importlib import import_module as im; im("laya")`, `getattr(importlib, "import_module")("laya")`,
   `runpy.run_module("laya")`, `exec("import laya")`, a module name built from a variable); for each, does the RUNTIME blocker catch it
   when the code runs? (c) The runtime blocker's reach: enumerate every process the four J1 test files start (`subprocess`, `os.exec*`,
   shell scripts) and say whether each inherits `PYTHONPATH` and runs `site` (a `-I`, `-S` or `-E` flag, an `env=` without
   `PYTHONPATH`, or a non-Python child each escape it). (d) The design against the breakdown's words ("a venv without `laya`/`torch` — a
   subprocess with an isolated site"): is the `sitecustomize` + attempt-log design equivalent or stronger, and is there any load path it
   cannot see (a `.pth` import before `sitecustomize`, a pre-seeded `sys.modules`, a C-extension import)? (e) THE REAL-WORLD RUN: run the
   four J1 test files under the closure's blocker with the model packages actually INSTALLED on the path (for example
   `PYTHONPATH=<blocker dir>:<tree>/src:/home/rocco/laya-venv/lib/python3.11/site-packages`, read-only, the agent-factory venv's python).
   With the packages importable, zero logged attempts is the real proof; any attempt is a finding. Say exactly how you built it.
6. **The coordinator's mutant table** (below, measured at authoring): rebuild at least eight rows on a scratch copy and confirm each is
   killed for the stated reason; then add at least five mutants of your own (on the pin test, the scan and the blocker) and say which
   test kills each, or that none does.
7. **The full suite.** `python -m pytest -n 8 -q -p no:cacheprovider --basetemp ../scratch/bt tests/ proofs/ spikes/` once at the PIN with
   the venue exports (one foreground call; it took 261 s at 942ad5e). Compare with the coordinator's 942ad5e run (`3937 passed, 81
   skipped, 8 xfailed`) and explain every difference by file.
8. **Gates.** `tests/test_laya_pin.py` and `tests/test_decisions_no_model.py` twice with identical counts; pyflakes on both;
   `python3 scripts/no_laya_in_gates.py` (exit 0).

## The coordinator's mutant table (driver `/tmp/j145m/mutate.py`, sandbox-only; each row removes one check or narrows one branch)

| id | file | change |
|---|---|---|
| P-missing | test_laya_pin.py | the missing-row return → `return []` |
| P-rev-malformed / P-weights-malformed / P-wheel-malformed | test_laya_pin.py | the named `…-malformed` append → `pass` |
| P-rev-drift / P-subfolder-drift / P-weights-drift / P-version-drift | test_laya_pin.py | the named per-probe drift append → `pass` |
| P-report-rev / P-report-weights / P-report-source | test_laya_pin.py | the named report-drift append → `pass` |
| N-import / N-importfrom / N-call | test_decisions_no_model.py | the branch's `names = …` → `names = []` (N-call: the condition → `if False:`) |
| N-level | test_decisions_no_model.py | `node.level == 0 and` dropped from the ImportFrom test |
| N-dunder | test_decisions_no_model.py | `("import_module", "__import__")` → `("import_module",)` |
| N-toplevel | test_decisions_no_model.py | `name.split(".")[0] in MODEL_PACKAGES` → `name in MODEL_PACKAGES` |

## Blocking predicate and verdict

A finding blocks only if it is contract-mapped (a seed AC, a breakdown gate, or AF-AP-179's design), reproduced on the PIN through the
real test or the real lock, materially effective (a drifted or false pin passes, or a model dependency escapes the closure), carries a
concrete discriminator, and is in-boundary. End with a GATE RECOMMENDATION: MERGE-READY / MERGE-READY-WITH-FOLLOWUPS / NOT-READY /
CONTRACT-INVALID.

## Boundary and standing do-nots

Write ONLY `tasks/briefs/laya/VERIFY-J1-45-report.md` in your tree (incrementally, from the start) and scratch files under your lane's
`../scratch/`. Every mutation runs on a scratch copy. Never edit any tracked file; never `git add`, `commit`, `stash`, `checkout`,
`restore`, `reset` or `clean`. No server touch, no sudo, no install into an existing venv, no model inference, no bridge tools. Paste every
count and timestamp from command output (timestamps from `date -u`). Every terminal call stays under the 420 s cap. Report lint:
`python3 scripts/report_lint.py --min-refs 15 tasks/briefs/laya/VERIFY-J1-45-report.md` (at most three fix rounds, then paste and
finish).

## PREMISE — MEASURED at authoring (2026-09-24 05:3xZ, /home/user/agent-factory@780f25a == origin; generated by `scripts/premise_block.sh`, every command echoed exactly as it ran)

The mutant driver `/tmp/j145m/mutate.py` exists in the sandbox only; the table above gives each row's change, rebuild it from there. `proofs/S0-12/check_pin_diff.py` reads the lock at run time; the minted S0-12 result names the lock only in its negative-control text, and `python3 scripts/validate-ledger integrity --root .` read all twelve proofs PRESENT at the PIN (rc 0).

```
$ git rev-parse --short '780f25a^{commit}'
780f25a
$ git merge-base --is-ancestor 780f25a origin/claude/soundbox-kit-migration-iz1jwf && echo pin-is-on-origin
pin-is-on-origin
$ for c in 20da862 342a5fe 227bd82 0574ac1; do git merge-base --is-ancestor $c 780f25a && echo "$c is an ancestor of the PIN"; done
20da862 is an ancestor of the PIN
342a5fe is an ancestor of the PIN
227bd82 is an ancestor of the PIN
0574ac1 is an ancestor of the PIN
$ git log --format='%h %s' -4 780f25a -- upstream.lock.yaml tests/test_laya_pin.py tests/test_decisions_no_model.py | cut -c1-110
0574ac1 J1-4/J1-5 tests: every check gets a killing negative control (pre-verify mutation audit, 8 of 15 survi
227bd82 J1-5 hardened before the push: the model block reaches every process and counts attempts (AF-AP-179)
342a5fe J1-5: the no-model closure test for the decision ledger (task #122)
20da862 J1-4: the Laya pin in upstream.lock.yaml, held equal to both J0 probes (task #121)
$ git ls-tree 780f25a -- upstream.lock.yaml tests/test_laya_pin.py tests/test_decisions_no_model.py docs/research/findings/LAYA-PROBE-1.md docs/research/findings/laya-probe-1-sandbox.json docs/research/findings/laya-probe-1-pc.json | awk '{print substr($3,1,12), $4}'
7411abff3efd docs/research/findings/LAYA-PROBE-1.md
9fa3c79e8f86 docs/research/findings/laya-probe-1-pc.json
c375e03fbbd6 docs/research/findings/laya-probe-1-sandbox.json
0f6cb8b937a4 tests/test_decisions_no_model.py
c923d856c4cc tests/test_laya_pin.py
514b0f96f8a2 upstream.lock.yaml
$ git show 780f25a:upstream.lock.yaml | /root/venv-agent-factory/bin/python -c "import sys, yaml; r = yaml.safe_load(sys.stdin)['advisory_models']['laya-typed-decisions']; [print(k, '=', repr(r[k])) for k in r]"
checkpoint_source = 'https://huggingface.co/convaiinnovations/laya'
revision = '1c5edc17a7acd8701df6fc341c0d179f1c62c982'
subfolder = 'typed-decisions'
weights_digest = 'sha256:4fa56de72383a9d3efa9cfa78955733c81b9fc8067a587ca4beb82c78107a24e'
package = 'laya'
package_version = '0.3.5'
package_wheel = 'laya-0.3.5-py3-none-any.whl'
package_wheel_digest = 'sha256:4c57f64cbaf893bb5c7b4affddc2bf21a819f55df51941689f11868583be2903'
runtime_measured = 'torch 2.14.0 (+cpu in the sandbox, +cu130 on the PC), transformers 5.17.0, safetensors 0.8.0; FP32 on 4 pinned CPU threads'
probe = 'docs/research/findings/LAYA-PROBE-1.md'
verdicts = 'PC (reference) ASYNC-ONLY + DETERMINISTIC; sandbox SYNC-OK + DETERMINISTIC for its own instance'
role = 'advisory_typed_decision_scorer_never_a_gate'
adopted = '2026-09-24 (J1-4; D-044, D-045; the PC endpoint is PCJ1, task #124)'
$ /root/venv-agent-factory/bin/python -m pytest tests/test_laya_pin.py tests/test_decisions_no_model.py -q -p no:cacheprovider 2>&1 | tail -1 | sed -E 's/ in [0-9.]+s.*$//'
14 passed
$ bash scripts/pc_suite.sh set-id -- tests/test_laya_pin.py tests/test_decisions_no_model.py
2 files set=bcc33b8bcdaf
$ python3 scripts/vendored_manifest.py --check 2>&1 | tail -1
PASS: sandbox-kit/VENDORED-MANIFEST.md matches 9 vendored roots
$ grep -n -E '^def |^[A-Z_0-9]+ = ' tests/test_laya_pin.py tests/test_decisions_no_model.py | cut -c1-110
tests/test_laya_pin.py:16:ROOT = pathlib.Path(__file__).resolve().parents[1]
tests/test_laya_pin.py:17:LOCK = ROOT / "upstream.lock.yaml"
tests/test_laya_pin.py:18:FINDINGS = ROOT / "docs" / "research" / "findings"
tests/test_laya_pin.py:19:PROBES = [FINDINGS / "laya-probe-1-sandbox.json", FINDINGS / "laya-probe-1-pc.json"]
tests/test_laya_pin.py:20:REPORT = FINDINGS / "LAYA-PROBE-1.md"
tests/test_laya_pin.py:21:ROW = ("advisory_models", "laya-typed-decisions")
tests/test_laya_pin.py:22:HF = "https://huggingface.co/"
tests/test_laya_pin.py:23:HEX40 = re.compile(r"[0-9a-f]{40}")
tests/test_laya_pin.py:24:DIGEST = re.compile(r"sha256:([0-9a-f]{64})")
tests/test_laya_pin.py:27:def pin_mismatches(lock: dict, probes: list[dict], report: str) -> list[str]:
tests/test_laya_pin.py:63:def _probes() -> list[dict]:
tests/test_laya_pin.py:72:def test_lock_pin_equals_both_probes_and_the_report():
tests/test_laya_pin.py:77:BOTH = ("laya-probe-1-sandbox", "laya-probe-1-pc")
tests/test_laya_pin.py:101:def test_each_pinned_field_is_red_by_name(field, value, expected):
tests/test_laya_pin.py:110:def test_missing_row_is_red_by_name():
tests/test_decisions_no_model.py:18:ROOT = pathlib.Path(__file__).resolve().parents[1]
tests/test_decisions_no_model.py:19:MODEL_PACKAGES = ("laya", "torch", "transformers", "safetensors", "hugging
tests/test_decisions_no_model.py:20:J1_MODULES = [
tests/test_decisions_no_model.py:25:J1_TESTS = [
tests/test_decisions_no_model.py:31:BLOCKER = textwrap.dedent(
tests/test_decisions_no_model.py:55:def model_imports(path: pathlib.Path) -> list[str]:
tests/test_decisions_no_model.py:76:def _run_blocked(work: pathlib.Path, *argv: str) -> tuple[subprocess.Compl
tests/test_decisions_no_model.py:96:def test_no_j1_module_imports_a_model_package():
tests/test_decisions_no_model.py:102:def test_scan_reds_an_added_laya_import(tmp_path):
tests/test_decisions_no_model.py:121:def test_j1_suite_passes_with_model_packages_blocked(tmp_path):
tests/test_decisions_no_model.py:130:def test_blocker_reds_an_import_logs_a_caught_one_and_reaches_a_child(tmp
$ rm -rf /tmp/j145m/pin && mkdir -p /tmp/j145m/pin && git archive 780f25a tests/test_laya_pin.py tests/test_decisions_no_model.py | tar -x -C /tmp/j145m/pin && python3 /tmp/j145m/mutate.py /tmp/j145m/pin | awk '{print $1, $2}'
P-missing KILLED
P-rev-malformed KILLED
P-weights-malformed KILLED
P-wheel-malformed KILLED
P-rev-drift KILLED
P-weights-drift KILLED
P-version-drift KILLED
P-report-rev KILLED
P-report-weights KILLED
P-subfolder-drift KILLED
P-report-source KILLED
N-import KILLED
N-importfrom KILLED
N-level KILLED
N-call KILLED
N-dunder KILLED
N-toplevel KILLED
$ grep -rln "upstream.lock" tests/ proofs/ scripts/ | sort
proofs/S0-01/GROUNDING.md
proofs/S0-01/vendor/buzz-acp/VENDORED-FROM.md
proofs/S0-06/__pycache__/check_four_scope.cpython-311.pyc
proofs/S0-06/check_four_scope.py
proofs/S0-06/fixtures/build_synthetic_bundles.py
proofs/S0-06/fixtures/evidence-leak/PROVENANCE.md
proofs/S0-06/fixtures/evidence-wrong-scope-write/PROVENANCE.md
proofs/S0-06/tools/pc/start_ai_memory.sh
proofs/S0-08/CONTAINMENT-SPEC.md
proofs/S0-08/check_containment.py
proofs/S0-10/fixtures/neg-missing-credential-stmt.md
proofs/S0-12/check_pin_diff.py
proofs/S0-12/result.json
proofs/S0-12/spec.json
scripts/__pycache__/vendored_manifest.cpython-311.pyc
scripts/fubuki_pin_sync.sh
scripts/pc_suite.sh
scripts/ripwire_review.sh
scripts/sentrux_review.sh
scripts/setup.sh
scripts/vendored_manifest.py
scripts/verify-planning-repo.sh
tests/__pycache__/test_fubuki_pin_sync.cpython-311-pytest-9.1.1.pyc
tests/__pycache__/test_governance_bounds.cpython-311-pytest-9.1.1.pyc
tests/__pycache__/test_governance_bounds.cpython-311.pyc
tests/__pycache__/test_governance_packet.cpython-311-pytest-9.1.1.pyc
tests/__pycache__/test_governance_packet.cpython-311.pyc
tests/__pycache__/test_governance_pin.cpython-311-pytest-9.1.1.pyc
tests/__pycache__/test_governance_pin.cpython-311.pyc
tests/__pycache__/test_governance_pin_enforcement.cpython-311-pytest-9.1.1.pyc
tests/__pycache__/test_governance_review.cpython-311-pytest-9.1.1.pyc
tests/__pycache__/test_laya_pin.cpython-311-pytest-9.1.1.pyc
tests/__pycache__/test_s0_02_buzz_authz.cpython-311-pytest-9.1.1.pyc
tests/__pycache__/test_s0_02_buzz_authz.cpython-311.pyc
tests/__pycache__/test_s0_06_four_scope.cpython-311-pytest-9.1.1.pyc
tests/__pycache__/test_s0_06_four_scope.cpython-311.pyc
tests/__pycache__/test_s0_12_license_sbom.cpython-311-pytest-9.1.1.pyc
tests/__pycache__/test_upstream_lock_lane_runtime.cpython-311-pytest-9.1.1.pyc
tests/__pycache__/test_vendored_manifest.cpython-311-pytest-9.1.1.pyc
tests/test_fubuki_pin_sync.py
tests/test_governance_bounds.py
tests/test_governance_packet.py
tests/test_governance_pin.py
tests/test_governance_pin_enforcement.py
tests/test_governance_review.py
tests/test_laya_pin.py
tests/test_s0_02_buzz_authz.py
tests/test_s0_06_four_scope.py
tests/test_s0_12_license_sbom.py
tests/test_upstream_lock_lane_runtime.py
tests/test_vendored_manifest.py
```
