#!/usr/bin/env python3
"""Idempotent Ouroboros patches — run with the ooo interpreter, not the project venv.

Two patches (see OUROBOROS-SETUP.md for the full rationale):
  P1 (W2) — ledger self-conflict tie-break: resolve assumption-class ties deterministically
             so bounded auto can close instead of blocking on its own same-key collisions.
  P2 (W4) — interview context cap: raise MAX_PROMPT_SAFE_INITIAL_CONTEXT_CHARS 3500 -> 10000
             so research-grounded initial_context isn't force-compressed.

Usage:
  OOO_PY=/root/.local/share/uv/tools/ouroboros-ai/bin/python
  "$OOO_PY" scripts/patch_ouroboros.py
"""
import importlib.util
import pathlib
import sys


def patch_ledger():
    spec = importlib.util.find_spec("ouroboros.auto.ledger")
    if spec is None or spec.origin is None:
        print("SKIP P1: ouroboros.auto.ledger not found (not installed?)")
        return False
    p = pathlib.Path(spec.origin)
    src = p.read_text()
    OLD = (
        "    if existing.confidence > incoming.confidence:\n"
        "        return ConflictResolution.EXISTING_WINS\n"
        "    return ConflictResolution.CONFLICTING\n"
    )
    if OLD not in src:
        print(f"already patched: {p}")
        return True
    NEW = (
        "    if existing.confidence > incoming.confidence:\n"
        "        return ConflictResolution.EXISTING_WINS\n"
        "    _tb = {LedgerSource.CONSERVATIVE_DEFAULT, LedgerSource.ASSUMPTION,\n"
        "           LedgerSource.INFERENCE, LedgerSource.AUTO_FILL_INFERENCE}\n"
        "    if existing.source in _tb and incoming.source in _tb:\n"
        "        return ConflictResolution.EXISTING_WINS\n"
        "    return ConflictResolution.CONFLICTING\n"
    )
    p.write_text(src.replace(OLD, NEW, 1))
    print(f"patched: {p}")
    return True


def patch_interview_cap():
    spec = importlib.util.find_spec("ouroboros.bigbang.interview")
    if spec is None or spec.origin is None:
        print("SKIP P2: ouroboros.bigbang.interview not found (not installed?)")
        return False
    p = pathlib.Path(spec.origin)
    src = p.read_text()
    _CAP_OLD = "MAX_PROMPT_SAFE_INITIAL_CONTEXT_CHARS = 3500"
    _CAP_NEW = "MAX_PROMPT_SAFE_INITIAL_CONTEXT_CHARS = 10000"
    if _CAP_NEW in src:
        print(f"interview cap already raised: {p}")
        return True
    if _CAP_OLD not in src:
        print(f"ERROR P2: anchor not found in {p} (ooo version changed?)")
        return False
    p.write_text(src.replace(_CAP_OLD, _CAP_NEW, 1))
    print(f"interview cap raised: {p}")
    return True


if __name__ == "__main__":
    ok1 = patch_ledger()
    ok2 = patch_interview_cap()
    sys.exit(0 if (ok1 and ok2) else 1)
