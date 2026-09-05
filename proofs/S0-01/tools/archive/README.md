# S0-01 tools/archive

Archived instrument versions whose outputs are committed under `proofs/S0-01/evidence/`.

## frame_tee_v1.py

The tee instrument that produced the v1 milestone captures:
- `evidence/initialize-20260905T062959Z/`
- `evidence/turn-20260905T070807Z/`
- `evidence/turn-20260905T071639Z/`
- `evidence/golden/` (v1 directional frames, before timeline.jsonl)

Byte-exact copy from `git show 2e5ccf5:proofs/S0-01/tools/frame_tee.py`.
sha256: `a7a0c367e5251b2cca2aca145ff6b4308ce5b9a40d4a184c73d79b27d32d1f38`.

The live `tools/frame_tee.py` is the v2 instrument (timestamps inside lock,
os.read stdin pump, bounded stdout join, signal exit codes, raw_b64 for
non-JSON frames, tee_pid in identity). The v1 captures bind to the archived
sha256; new v2 captures will bind to the live sha256.
