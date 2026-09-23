# PC continuation — lane J1-1-R3 (task #202; D-059): the three regressions the second repair introduced close, R-3 closes, and the surviving mutants die

PIN: feb26d7 (the post-push origin head; the original brief's PIN 0e60603 and this PIN carry byte-identical boundary files — premise below; gate with `-r feb26d7`)

Role: code-implementer. Route: the CLOUD build route (`HERMES_MODEL=agentfactory-build`, reasoning ultra). The local route is at its KV
ceiling with two verify lanes (AF-AP-146). Claim nothing about which model wrote the code; the harvest measures the provider mix. Venue:
`tasks/briefs/pc/VENUE-MAP.md`, read it FIRST. Honey ultra, Lever-2: the report is DATA. Keep your context small: `| tail -n 40` on long
output, `sed -n` ranges instead of whole-file reads.

AUTHORIZATION: defensive redaction code on the owner's own repository. Every secret-shaped value in a test, a mutant or a probe is a FAKE
string (`QZJ8…`, `X4Z9…` style); no credential, server or network is touched.

## CONTINUATION (read second)

This lane CONTINUES sandbox lane J1-1-R3. The sandbox model's weekly quota stopped it at about 16:4xZ on 2026-09-23 while it was reading
the brief; it wrote NOTHING. Start from the original brief's first step. The lane patch carries ONLY the verifier's read-only tools (see
below); it holds no predecessor code and no report.

**The original brief governs:** `tasks/briefs/laya/J1-1-R3-brief.md`. READ IT WHOLE. Its contract (AMENDMENT 3 to J1-1 under D-059: FIX-A
and FIX-B, C1-C6, the declared residue), the scratch-copy-then-write-once rule, the tests, the mutation audit (m1-m7 plus the builder's
30-mutant table), the gates, the boundary and the report rules apply unchanged, with the venue mapping below. This is the THIRD focused
repair; no fourth round is pre-authorized, so a contract line you cannot meet is a DISCREPANCY with its measurement, never a silent change.

## VENUE NOTES (this lane only)

- The verifier's tools: the original brief's `/tmp/vj11r2/` is shipped in your lane patch as
  `tasks/briefs/laya/j1-1-r3-support/vj11r2/` (`repro.py`, `fixa/volatile.py`, `fixb/volatile.py`, `tools/*.py`; 30 files, byte copies —
  sha prefixes below). READ-ONLY: never edit them and never count them as your diff. Several `tools/*.py` hardcode `/tmp/vj11r2`; to run
  one, copy the directory there first (`cp -a tasks/briefs/laya/j1-1-r3-support/vj11r2 /tmp/vj11r2`, refuse if `/tmp/vj11r2` already
  exists) and remove that copy at the end. `repro.py` needs no copy: `python tasks/briefs/laya/j1-1-r3-support/vj11r2/repro.py src`.
  `tools/b4_worker.py` hardcodes the sandbox repo path; do not use it.
- Every `/tmp/j113/…` path maps to `../scratch/j113/…`; the brief's "shared tree" is your lane tree; `/root/venv-agent-factory/bin/python`
  maps to `/home/rocco/venv-agent-factory/bin/python`; `/home/user/agent-factory/src` maps to your tree's `src`.
- Gates on this host: `python -m pytest -n 8 -q -p no:cacheprovider --basetemp ../scratch/j113/bt/r<n> tests/test_decisions_canonical.py
  tests/test_decisions_ledger.py` directly (set 16a7b628685e; twice, counts equal), each call under the 420 s terminal cap; the repro
  after the write; pyflakes on the three boundary files.
- Other lanes on this host: `pc-verify-k1-h.md--5276976`, `pc-verify-j1-0-r6.md--c6dcd61`, and the continuation lanes T94 and J1-3.
  J1-3 builds a harvester that imports `volatile.py` from ITS tree at the PIN; your edits stay in your tree.

## PREMISE — MEASURED at authoring (2026-09-23 16:57Z, /home/user/agent-factory@feb26d7)
```
$ date -u +%Y-%m-%dT%H:%MZ; git rev-parse --short origin/claude/soundbox-kit-migration-iz1jwf
2026-09-23T16:57Z
feb26d7
$ git diff --stat 0e60603 feb26d7 -- src/agent_factory/decisions tests/test_decisions_canonical.py tests/test_decisions_ledger.py | wc -l   (0 = the original brief's PIN 0e60603 and feb26d7 carry identical boundary bytes)
0
$ for f in <boundary>; do echo "$(git rev-parse feb26d7:$f | cut -c1-12) $(git show feb26d7:$f | wc -l) $f"; done
bf04415d72c1 395 src/agent_factory/decisions/volatile.py
440ac2426d8f 1060 tests/test_decisions_canonical.py
6648679bd40a 1612 tests/test_decisions_ledger.py
$ git ls-tree feb26d7 -- tasks/briefs/laya/J1-1-R3-report.md | wc -l   (0 = no report yet)
0
$ python tasks/briefs/laya/j1-1-r3-support/vj11r2/repro.py src   (the verifier repro on feb26d7's src; run here from /tmp/vj11r2, the byte-identical source of the lane-patch copy)
volatile: /home/user/agent-factory/src/agent_factory/decisions/volatile.py
R-1 body-in-ledger-line=True  state.msg='Authorization: Bearer QZJ8QZJ8ıQZJ8QZJ8QZJ8QZJ8QZJ8'
R-2 body-in-ledger-line=True  state.msg='<redacted:sk>token <redacted:token>: X4Z9X4Z9X4Z9'
R-4 body-in-ledger-line=True  state.msg='ta<redacted:sk>password:<redacted:envval> X4Z9X4Z9X4'
R-3 body-in-ledger-line=True  state.msg='ta<redacted:sk>= QZJ8QZJ8QZJ8QZJ8QZJ8'
replayed rows: 4
$ python -m pytest tests/test_decisions_canonical.py tests/test_decisions_ledger.py -q -p no:cacheprovider --basetemp=/tmp/j113p/bt | tail -1   (set 16a7b628685e)
121 passed in 3.54s
$ bash scripts/pc_suite.sh set-id -- tests/test_decisions_canonical.py tests/test_decisions_ledger.py
2 files set=16a7b628685e
$ sha256sum <lane patch> | cut -c1-12; grep -c "^diff --git" <lane patch>; (cd /tmp/vj11r2 && sha256sum repro.py fixa/volatile.py fixb/volatile.py | cut -c1-12)
7c453312fdfa
30
a97a7add8084
cba34afa49ae
5da6e5ead1cb
```
