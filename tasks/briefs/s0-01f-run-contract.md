# BRIEF — run every increment-#1 contract item and report DATA (role: contract-runner, route agentfactory-sweep)
PIN: (set at dispatch — scripts/pc_lane.sh refuses to run without a full SHA here)

Mechanical lane. You execute; you do not judge. First action: `pwd && git rev-parse HEAD` equals
the PIN and the tree is clean. Interpreter: `$HOME/venv-agent-factory/bin/python` (call it `$V`).
No edits, no commits, no pushes, no subagents. Append each finished item to `$LANE_REPORT_DRAFT`.

## Items (run each literally; paste invocation + decisive output lines; PASS/FAIL by the stated criterion)
C1  `$V scripts/validate-ledger integrity` → exit 0; twelve `S0-xx ABSENT` lines; the four
    denominator lines read `numerator=0` with denominators 7 (execution_proof), 3
    (conformance_checked_decision), 1 (blocked_credential), 1 (blocked_host).
C2  `$V scripts/validate-ledger stage1-gate` → exit 2; twelve `missing:` lines.
C3  Run C1 and C2 twice each; `sha256sum` of each stdout identical across the pair.
C4  `$V -m pytest tests/test_validate_ledger.py -q -k "forged_digest or valid_result"` → all pass
    (forged digest ⇒ `digest-mismatch`; the unforged twin PRESENT).
C5  `-k "ledger_claim"` → pass (`ledger-drift:`).
C6  `-k "missing_classification or unknown_class"` → pass.
C7  `-k "matches_seed"` → pass (classes = seed's four sets).
C8  `-k "undeclared or borrow or committed_pc_bridge or allowed_transitions"` → pass.
C9  `git diff c39b64f -- spikes/pc-bridge/result.json | grep -E '^[+-] ' ` → exactly one added
    `"outcome"` line and one changed `"schema"` pair (`-`/`+`), nothing else.
C10 `-k "extra_top_level or noncanonical_digest"` → pass; `$V -c "import json,jsonschema,glob; [jsonschema.Draft202012Validator.check_schema(json.load(open(f))) for f in glob.glob('proofs/schemas/*.json')]; print('SCHEMAS OK')"` → `SCHEMAS OK`.
C11 `$V -m pytest tests/ -q` twice → both `44 passed` (state the exact counts).
C12 `git log --oneline c39b64f..HEAD -- scripts/validate-ledger proofs tests spikes/pc-bridge` →
    list the commits; `git status --short` → empty.
C13 `-k "rfc3339 or date_time_checker or canonical or allowed_transitions"` → pass.
C14 `printf 'import builtins\nr=builtins.__import__\ndef g(n,*a,**k):\n    if n=="rfc3339_validator": raise ModuleNotFoundError(n)\n    return r(n,*a,**k)\nbuiltins.__import__=g\n' > /tmp/blk-$$/sitecustomize.py` (mkdir first) then
    `PYTHONPATH=/tmp/blk-$$ $V scripts/validate-ledger integrity` → exit 3, empty stdout, stderr
    `validate-ledger: date-time format checker unavailable (pip install rfc3339-validator==0.1.4)`.
C15 `-k "alias_and_branch"` → 3 passed.
C16 `grep -n "map-\|S0-0\|S0-1" scripts/validate-ledger` → only the proof-id regex line(s), the
    `S0-01 through S0-12` finding text, and the S0-03 credential-rejection clause; no other
    literal rule or proof id.
C17 `$V -m pytest tests/red -q` → `5 passed` (the verifier's findings, repaired in round 3).
C18 `$V -m pyflakes scripts/validate-ledger tests/test_validate_ledger.py tests/red/test_s0_01_adversarial.py` → no output.

Report: `item | PASS/FAIL/NOT-RUNNABLE | command | decisive output`, then `NOT-done`. No prose.
