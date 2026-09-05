"""proofs/S0-01/check_acp_conformance.py — the S0-01 positive leg, exercised on bundles BUILT FROM REAL
FRAMES (the committed 2026-09-05 captures). The passing bundle reuses run-1 as run-2 (identical
structure) and synthesizes the cancel / shutdown / two-users legs from those real frames; every
negative control below is one structural mutation the owner named as a real failure (missing,
duplicated, reordered, cross-session events) or one seed assertion violated, and must FAIL with the
exact reason. Absent evidence must DEFER (exit 2), never pass.
"""
from __future__ import annotations

import copy
import json
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
P = ROOT / "proofs" / "S0-01"
CHECKER = P / "check_acp_conformance.py"
REAL = P / "evidence" / "turn-20260905T070807Z"
sys.path.insert(0, str(P))
import check_acp_conformance as cc  # noqa: E402


def _frames(d: Path):
    return ([json.loads(l) for l in (d / "frames-client-to-agent.jsonl").read_text().splitlines()],
            [json.loads(l) for l in (d / "frames-agent-to-client.jsonl").read_text().splitlines()])


def _write(d: Path, c2a, a2c, record):
    d.mkdir(parents=True, exist_ok=True)
    (d / "frames-client-to-agent.jsonl").write_text("".join(json.dumps(o) + "\n" for o in c2a))
    (d / "frames-agent-to-client.jsonl").write_text("".join(json.dumps(o) + "\n" for o in a2c))
    (d / "capture.json").write_text(json.dumps(record, indent=1))


def _real():
    c2a, a2c = _frames(REAL)
    rec = json.loads((REAL / "capture.json").read_text())
    return c2a, a2c, rec


def _cancel_leg():
    c2a, a2c, rec = _real()
    sid = next(o for o in a2c if o.get("id") == 1)["result"]["sessionId"]
    c2a = c2a + [{"jsonrpc": "2.0", "method": "session/cancel", "params": {"sessionId": sid}}]
    a2c = copy.deepcopy(a2c)
    term = next(o for o in a2c if o.get("id") == 2)
    term["result"]["stopReason"] = "cancelled"
    rec = copy.deepcopy(rec)
    rec["orphan_check"] = {"checked": True, "orphan_processes_after": 0, "agent_children_alive": 1, "all_children_parented_by_buzz_acp": True}
    return c2a, a2c, rec


def _shutdown_leg():
    c2a, a2c, rec = _real()
    rec = copy.deepcopy(rec)
    rec["shutdown"] = {"buzz_acp_exit_code": 0, "agent_process_alive_after": False, "session_completed_before_shutdown": True}
    return c2a, a2c, rec


def _two_users_leg():
    c2a, a2c, rec = _real()
    sid2 = "11111111-2222-3333-4444-555555555555"
    init_req = c2a[0]
    new_req = copy.deepcopy(c2a[1]); prompt_req = copy.deepcopy(c2a[2])
    new2 = copy.deepcopy(new_req); new2["id"] = 3
    prompt2 = copy.deepcopy(prompt_req); prompt2["id"] = 4; prompt2["params"]["sessionId"] = sid2
    c2a2 = [init_req, new_req, prompt_req, new2, prompt2]
    init_resp = next(o for o in a2c if o.get("id") == 0)
    new_resp = next(o for o in a2c if o.get("id") == 1)
    new_resp2 = copy.deepcopy(new_resp); new_resp2["id"] = 3; new_resp2["result"]["sessionId"] = sid2
    notifs = [o for o in a2c if "method" in o]
    notifs2 = copy.deepcopy(notifs)
    for o in notifs2:
        o["params"]["sessionId"] = sid2
    term = next(o for o in a2c if o.get("id") == 2)
    term2 = copy.deepcopy(term); term2["id"] = 4
    a2c2 = [init_resp, new_resp, new_resp2] + notifs + [term] + notifs2 + [term2]
    return c2a2, a2c2, copy.deepcopy(rec)


@pytest.fixture
def bundle(tmp_path):
    """A passing evidence bundle under tmp_path/evidence/golden."""
    g = tmp_path / "evidence" / "golden"
    c2a, a2c, rec = _real()
    _write(g / "run-1", c2a, a2c, rec)
    _write(g / "run-2", c2a, a2c, rec)
    _write(g / "cancel", *_cancel_leg())
    _write(g / "shutdown", *_shutdown_leg())
    _write(g / "two-users", *_two_users_leg())
    (g / "golden.jsonl").write_text("\n".join(cc.normalize_run(c2a, a2c)) + "\n")
    return tmp_path / "evidence"


def _run(root: Path):
    return subprocess.run([sys.executable, str(CHECKER), str(root)], capture_output=True, text=True, timeout=60)


def _mutate_run2(root: Path, fn):
    d = root / "golden" / "run-2"
    c2a, a2c = _frames(d)
    rec = json.loads((d / "capture.json").read_text())
    c2a, a2c, rec = fn(c2a, a2c, rec)
    _write(d, c2a, a2c, rec)


def test_passing_bundle_passes_and_cli_exit_0(bundle):
    assert cc.check_bundle(bundle).startswith("PASS: 6 assertions + golden x2 identical")
    r = _run(bundle)
    assert r.returncode == 0 and r.stdout.startswith("PASS")


def test_normalization_keeps_structure_and_drops_values():
    c2a, a2c, _ = _real()
    lines = cc.normalize_run(c2a, a2c)
    text = "\n".join(lines)
    sid = next(o for o in a2c if o.get("id") == 1)["result"]["sessionId"]
    assert sid not in text and "pong" not in text and "/home/rocco" not in text
    assert text.count('"sessionUpdate":"agent_message_chunk"') == 27 and text.count('"sessionUpdate":"agent_thought_chunk"') == 49
    assert '"stopReason":"end_turn"' in text and '"protocolVersion":2' in text and '"protocolVersion":1' in text
    # id pairing survives: the prompt request and its terminal response share the same placeholder
    prompt = next(json.loads(l) for l in lines if l.startswith('{"dir":"c2a"') and '"session/prompt"' in l)
    terminal = next(json.loads(l) for l in lines if '"stopReason":"end_turn"' in l)
    assert prompt["id"] == terminal["id"] == "<ID3>"
    # deterministic
    assert lines == cc.normalize_run(c2a, a2c)


# NOTE: two ADJACENT chunks of the same kind are interchangeable once text is stripped — swapping them is not a
# structural reorder; the reorder control therefore swaps two events of DIFFERENT kinds (indices 2 and 3).
@pytest.mark.parametrize("name,mutation,reason", [
    ("missing event", lambda c, a, r: (c, [o for i, o in enumerate(a) if i != 10], r), "golden mismatch between run-1 and run-2"),
    ("duplicated event", lambda c, a, r: (c, a[:10] + [a[10]] + a[10:], r), "golden mismatch between run-1 and run-2"),
    ("reordered events", lambda c, a, r: (c, a[:2] + [a[3], a[2]] + a[4:], r), "golden mismatch between run-1 and run-2"),
])
def test_structural_mutations_of_run2_fail_the_golden(bundle, name, mutation, reason):
    # de-vacuous the mutation itself: it must change the STRUCTURE, i.e. the normalized text
    c2a, a2c, rec = _real()
    before = cc.normalize_run(c2a, a2c)
    mc, ma, _ = mutation(copy.deepcopy(c2a), copy.deepcopy(a2c), rec)
    assert cc.normalize_run(mc, ma) != before, f"{name}: mutation is structurally invisible"
    _mutate_run2(bundle, mutation)
    r = _run(bundle)
    assert r.returncode == 1 and reason in r.stdout, (name, r.stdout)


def test_cross_session_event_fails_before_the_golden(bundle):
    def cross(c, a, r):
        a = copy.deepcopy(a)
        n = next(o for o in a if "method" in o)
        n["params"]["sessionId"] = "deadbeef-0000-0000-0000-000000000000"
        return c, a, r
    _mutate_run2(bundle, cross)
    r = _run(bundle)
    assert r.returncode == 1 and "run-2: notifications carry a foreign session id" in r.stdout


def test_cancel_leg_requires_cancel_notification_and_cancelled_terminal(bundle):
    d = bundle / "golden" / "cancel"
    c2a, a2c = _frames(d); rec = json.loads((d / "capture.json").read_text())
    _write(d, [o for o in c2a if o.get("method") != "session/cancel"], a2c, rec)
    assert "cancel: no session/cancel notification was sent" in _run(bundle).stdout
    _write(d, c2a, a2c, rec)  # restore
    a2 = copy.deepcopy(a2c); next(o for o in a2 if o.get("id") == 2)["result"]["stopReason"] = "end_turn"
    _write(d, c2a, a2, rec)
    assert "cancel: terminal stopReason is 'end_turn', expected 'cancelled'" in _run(bundle).stdout
    rec2 = copy.deepcopy(rec); rec2["orphan_check"] = {"checked": True, "orphan_processes_after": 1}
    _write(d, c2a, a2c, rec2)
    assert "cancel: capture record does not prove zero orphan processes after cancel" in _run(bundle).stdout


def test_shutdown_and_two_users_and_config_echo_negatives(bundle):
    d = bundle / "golden" / "shutdown"
    c2a, a2c = _frames(d); rec = json.loads((d / "capture.json").read_text())
    bad = copy.deepcopy(rec); bad["shutdown"]["buzz_acp_exit_code"] = 143
    _write(d, c2a, a2c, bad)
    assert "shutdown: buzz-acp exit code is 143, expected 0" in _run(bundle).stdout
    _write(d, c2a, a2c, rec)
    d = bundle / "golden" / "two-users"
    c2a, a2c = _frames(d); rec = json.loads((d / "capture.json").read_text())
    collide = copy.deepcopy(a2c)
    sid1 = next(o for o in collide if o.get("id") == 1)["result"]["sessionId"]
    next(o for o in collide if o.get("id") == 3)["result"]["sessionId"] = sid1
    _write(d, c2a, collide, rec)
    assert "two-users: session ids collide" in _run(bundle).stdout
    _write(d, c2a, a2c, rec)
    d = bundle / "golden" / "run-1"
    c2a, a2c = _frames(d); rec = json.loads((d / "capture.json").read_text())
    slow = copy.deepcopy(rec); slow["config_echo"]["idle_timeout"] = "1500s"
    _write(d, c2a, a2c, slow)
    assert "run-1: idle timeout echo is not 900s" in _run(bundle).stdout
    _write(d, c2a, a2c, rec)
    dirty = copy.deepcopy(rec); dirty["manifests"]["post_capture"] = {"buzz": "changed"}
    _write(d, c2a, a2c, dirty)
    assert "run-1: source-tree manifests are not identical" in _run(bundle).stdout


def test_absent_or_incomplete_evidence_defers_with_exit_2(tmp_path, bundle):
    empty = tmp_path / "empty-evidence"; empty.mkdir()
    r = _run(empty)
    assert r.returncode == 2 and r.stdout.startswith("deferred: golden evidence bundle absent")
    shutil.rmtree(bundle / "golden" / "two-users")
    r = _run(bundle)
    assert r.returncode == 2 and "deferred: golden/two-users absent" in r.stdout


def test_frozen_golden_is_binding(bundle):
    frozen = bundle / "golden" / "golden.jsonl"
    frozen.unlink()
    r = _run(bundle)
    assert r.returncode == 2 and "golden.jsonl not frozen yet" in r.stdout
    frozen.write_text("{}\n")
    r = _run(bundle)
    assert r.returncode == 1 and "differ from the frozen golden.jsonl" in r.stdout


def test_real_committed_evidence_root_passes_with_the_frozen_golden():
    """The repo's own evidence bundle (captured 2026-09-05 on the PC venue) passes; the frozen golden is binding."""
    r = _run(P / "evidence")
    assert r.returncode == 0 and r.stdout.startswith("PASS: 6 assertions + golden x2 identical"), r.stdout
    frozen = (P / "evidence" / "golden" / "golden.jsonl").read_text().splitlines()
    c2a, a2c = _frames(P / "evidence" / "golden" / "run-1")
    assert cc.normalize_run(c2a, a2c) == frozen
    c2a2, a2c2 = _frames(P / "evidence" / "golden" / "run-2")
    assert cc.normalize_run(c2a2, a2c2) == frozen
    for leg in ("cancel", "shutdown", "two-users"):
        rec = json.loads((P / "evidence" / "golden" / leg / "capture.json").read_text())
        assert rec["manifests"]["identical"] is True and rec["config_echo"]["idle_timeout"] == "900s", leg
