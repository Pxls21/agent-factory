"""Fixtures shared by more than one test file in this directory.

`synthetic_leg` is here because a hand-written leg is a SECOND copy of `pins.PINNED_LEG_FILES`. VERIFY-P5a F1:
`tests/test_s0_01_scripted_backend.py`'s round-trip test built its own seven-file leg, and the day
`build_capture_record.py` started requiring the whole list that test went red — for a reason it could not
state, since it asserts nothing about leg shape. The repair that re-creates the drift is to paste the 21
missing names into it; the repair that ends it is ONE fixture that reads the ONE list, used by both files.

Deliberately inert for the other ~30 test files in this directory: nothing is imported and `sys.path` is not
touched at collection time — the S0-01 pin module is imported inside the fixture body, only for a test that
actually asks for the fixture.
"""
import gzip
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture
def synthetic_leg():
    """Factory `synthetic_leg(dst) -> Path`: a COMPLETE positive leg.

    Every `required` name in `pins.PINNED_LEG_FILES` and every `required` dir in `pins.PINNED_LEG_DIRS`, with
    real parseable content for the six files `build_capture_record.py` actually reads and a one-byte
    placeholder for the rest. The name list is never typed here: a change to the ONE list moves every caller's
    leg at once, which is the whole point.
    """
    s0_01 = str(ROOT / "proofs" / "S0-01")
    if s0_01 not in sys.path:
        sys.path.insert(0, s0_01)
    import pins

    def _make(dst):
        dst = Path(dst)
        dst.mkdir(parents=True, exist_ok=True)
        (dst / "timeline.jsonl").write_text(
            json.dumps({"seq": 1, "dir": "c2a", "frame": {"id": 0, "method": "initialize"}}) + "\n")
        (dst / "runtime-identity.json").write_text(json.dumps({"tee_pid": 1}) + "\n")
        (dst / "env.json").write_text(json.dumps({"PATH": "/usr/bin"}) + "\n")
        (dst / "startup-line.txt").write_text("buzz-acp starting: idle_timeout=900s max_turn=3600s\n")
        (dst / "hermes-model.txt").write_text("  default: s0-01-scripted/s0-01-pong\n")
        # a leg that is internally CONSISTENT: its scan header names the contract version whose required set
        # this leg carries, so pins.corpus_version() reads v2.4 here and really does demand tee-status.json
        (dst / "process-scan-after.txt").write_text(
            "# process-scan v2.4 mode=after rows=0 buzz_acp_pid=1 buzz_present=0 owned=1 owned_present=0 "
            "pinned_present=0 owned_zombies=0 table_rows=1 utc=2026-09-08T00:00:00Z\n")
        body = b"## hermes-agent\n" + b"0" * 64 + b" f 0644  ./x\n"
        for phase in ("pre", "post"):
            (dst / f"manifest-{phase}.txt.gz").write_bytes(gzip.compress(body))
        for name in pins.required_files(pins.PINNED_SCAN_VERSIONS[-1]):
            if not (dst / name).exists():
                (dst / name).write_text("0\n")
        for name in pins.PINNED_LEG_DIRS:
            (dst / name).mkdir(exist_ok=True)
        return dst

    return _make
