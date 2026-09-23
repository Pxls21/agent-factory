# PC continuation — lane J1-3 (task #120): `scripts/decide-harvest`, the strict grammars, the committed-source rule and the harvest line (the KC-J7 measurement)

PIN: feb26d7 (the post-push origin head; the decisions package and the J1 suites are byte-identical at the original brief's PIN 38a9832 and here; the boundary is still absent — premise below)

Role: code-implementer. Route: the CLOUD build route (`HERMES_MODEL=agentfactory-build`, reasoning ultra). The local route is at its KV
ceiling with two verify lanes (AF-AP-146). Claim nothing about which model wrote the code; the harvest measures the provider mix. Venue:
`tasks/briefs/pc/VENUE-MAP.md`, read it FIRST. Honey ultra, Lever-2: the report is DATA. Keep your context small: `| tail -n 40` on long
output, `sed -n` ranges instead of whole-file reads; the corpus files are large, so read them through your own scripts, never whole.

AUTHORIZATION: a read-only harvester over the owner's own committed reports and logs. It writes only the ledger file you name under your
scratch directory; no credential, server or network is touched.

## CONTINUATION (read second)

This lane CONTINUES sandbox lane J1-3. The sandbox model's weekly quota stopped it at about 16:4xZ on 2026-09-23, after its premise
re-measure and one DISCREPANCY; it wrote NO code. Its report draft `tasks/briefs/laya/J1-3-report.md` (§1 premise, DISCREPANCY D-1) is
APPLIED on your worktree as the lane patch. Continue that file: keep D-1 with its measurement, add the resolution below, write the rest.

**The original brief governs:** `tasks/briefs/laya/J1-3-brief.md`. READ IT WHOLE. Its contract, grammars, exit codes, stdout lines,
tests (a)-(h), mutants m1-m8 and report rules apply unchanged, except AMENDMENT A1 and the venue mapping below.

## AMENDMENT A1 (coordinator, 2026-09-23 16:5xZ; resolves the predecessor's D-1; decided, do not re-litigate)

D-1 is correct: `_strip_pin_suffix` (`src/agent_factory/decisions/volatile.py:142-148`) strips `--<7..40 hex>` only at the END of the
value, so the brief's §4.2 value `pc-verify-<x>.md--<pin>.md` keeps its PIN in state (premise below). The rule for `v1.finding_class`
state `lane` from a `report-pc-verify-<x>.md--<pin>.md` file is now: the file name without the leading `report-` AND without the final
`.md` (`pc-verify-<x>.md--<pin>`); J1-1's normalizer then strips the pin (`pc-verify-<x>.md`). The harvester never parses or strips a PIN
itself: J1-1's normalizer stays the only PIN stripper. The `VERIFY-<x>-report.md` → `VERIFY-<x>` rule is unchanged. Tests (added to your
(a)-(h) set): a harvested row's `decision_state(...)['lane']` equals `pc-verify-<x>.md` and holds no hex run of 7 or more characters; two
report files of the same lane at two different pins give the same state `lane` and different `source_ref` paths. Mutant m9: drop the
`.md` removal; it must red the first test.

## VENUE NOTES (this lane only)

- Every `/tmp/j13/…` path in the original brief maps to `../scratch/j13/…` (beside your tree). `/root/venv-agent-factory/bin/python` maps
  to `/home/rocco/venv-agent-factory/bin/python`.
- THE REAL RUN (original brief, the real-run section): do NOT use `git worktree add` on this host (your tree is itself a worktree of the
  main clone; another worktree would change the main clone's worktree list). Use a private clone instead:
  `git clone -q --no-checkout --shared /home/rocco/agent-factory ../scratch/j13/wt && git -C ../scratch/j13/wt checkout -q --detach feb26d7`,
  paste `git -C ../scratch/j13/wt rev-parse HEAD`, run `scripts/decide-harvest --root ../scratch/j13/wt --out ../scratch/j13/real.jsonl`
  from your tree twice (the second into `real2.jsonl`), paste `cmp`, then `rm -rf ../scratch/j13/wt`. The corpus at feb26d7 is larger
  than the brief's premise measured at c6dcd61 (new reports and incident rows): paste the counts you measure, never the brief's.
- Gates on this host: `python -m pytest -n 8 -q -p no:cacheprovider --basetemp ../scratch/j13/bt <files>` directly (twice for the new
  test file, counts equal); the J1 suites `tests/test_decisions_canonical.py tests/test_decisions_ledger.py tests/test_no_laya_in_gates.py`
  once; each call under the 420 s terminal cap. Paste every set id (`bash scripts/pc_suite.sh set-id -- <files>` works offline).
- Other lanes on this host: `pc-verify-k1-h.md--5276976` and `pc-verify-j1-0-r6.md--c6dcd61` (verify lanes), and the continuation lanes
  T94 and J1-1-R3. J1-1-R3 edits `src/agent_factory/decisions/volatile.py` in ITS tree; your tree holds the PIN's bytes, and your
  harvester must work with them.

## PREMISE — MEASURED at authoring (2026-09-23 16:57Z, /home/user/agent-factory@feb26d7, the lane patch built from the dead lane's tree)
```
$ date -u +%Y-%m-%dT%H:%MZ; git rev-parse --short origin/claude/soundbox-kit-migration-iz1jwf
2026-09-23T16:57Z
feb26d7
$ for f in <decisions package + J1 suites>; do echo "$(git rev-parse feb26d7:$f | cut -c1-12) $(git show feb26d7:$f | wc -l) $f"; done
377ccd53da0c 24 src/agent_factory/decisions/__init__.py
607b65b613e2 78 src/agent_factory/decisions/canonical.py
bf04415d72c1 395 src/agent_factory/decisions/volatile.py
71fc398a5340 616 src/agent_factory/decisions/ledger.py
440ac2426d8f 1060 tests/test_decisions_canonical.py
6648679bd40a 1612 tests/test_decisions_ledger.py
$ git ls-tree feb26d7 -- scripts/decide-harvest tests/test_decide_harvest.py tests/fixtures/decisions/sources | wc -l   (0 = the boundary is still absent)
0
$ git diff --stat 38a9832 feb26d7 -- src/agent_factory/decisions tests/test_decisions_canonical.py tests/test_decisions_ledger.py | wc -l   (0 = the J1-3 brief's PIN and feb26d7 carry identical decisions bytes)
0
$ python - <<EOF   (D-1 and AMENDMENT A1, measured with the real module at feb26d7)
'pc-verify-m3.md--e776dd0.md' -> 'pc-verify-m3.md--e776dd0.md'
'pc-verify-m3.md--e776dd0' -> 'pc-verify-m3.md'
'pc-verify-k1-h.md--5276976.md' -> 'pc-verify-k1-h.md--5276976.md'
'pc-verify-k1-h.md--5276976' -> 'pc-verify-k1-h.md'
$ git ls-tree -r --name-only feb26d7 -- tasks/briefs | grep -c "/report-pc-verify-.*\.md--[0-9a-f]*\.md$"
20
$ sha256sum <lane patch> | cut -c1-12; grep "^diff --git" <lane patch>
4a0cdb3befda
diff --git a/tasks/briefs/laya/J1-3-report.md b/tasks/briefs/laya/J1-3-report.md
```
