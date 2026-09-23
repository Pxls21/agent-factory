# VERIFY-J1-3 Report

## 1. PREMISE
MEASUREMENT:
```
e8db82c2 transcripts: scrubbed sandbox chat digests (2026-09-23)
3a455682 C2: the lane done-gate (lane-done-gate.py + the LANE_DONE_GATE profile switch, OFF), GATED-PENDING-VERIFY
8cc03c15 lane_gate.sh: make the archive directory absolute before the cd (AF-AP-163; J1-3 D-2)
```
The tree commits (`e8db82c2`, `3a455682`, `8cc03c15`) differ from the brief's premise (`b6f4b77`, `da79e93`, `41154a1`).
Also, `grep -n -E '^def |make_row|\.append\(|cat-file|ls-tree|show HEAD' scripts/decide-harvest | head -40` returned lines (like 187, 208, 211, 214) not present in the premise output block.

Because of these mismatches, following the standing rule "A mismatch is CONTRACT-INVALID: stop and report it", I am stopping.

## DISCREPANCIES
- Commits differ from premise block.
- `grep` output for seam lines differs (matches `\.append\(` which was omitted in the brief's snapshot).

## GATE RECOMMENDATION
GATE RECOMMENDATION: CONTRACT-INVALID
Contract-mapped: Premise check failed against frozen contract.
