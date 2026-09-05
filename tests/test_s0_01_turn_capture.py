"""S0-01 — the relay-driven prompt turn captured 2026-09-05 (exploratory run 1, NOT the golden run).

From the committed RAW frames: the owner mention drove buzz-acp to `session/new` + `session/prompt`
on the pinned hermes-acp; every frame of the turn conforms to the pinned v1 schema; notifications all
carry the session id from `session/new`; the turn reached the terminal `stopReason: end_turn`; the
config echo shows idle_timeout=900s. It does NOT claim the golden (two-run byte-identical) result,
cancellation, shutdown, two-user separation, the negative control in a live run, or validated egress.
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
P = ROOT / "proofs" / "S0-01"
EV = P / "evidence" / "turn-20260905T070807Z"
sys.path.insert(0, str(P))
import check_initialize as ci  # noqa: E402

SCHEMA = ci.load_schema()


def _frames(name):
    return [json.loads(l) for l in (EV / name).read_text().splitlines()]


def _valid(defn, obj):
    errors = sorted(ci.validator_for(SCHEMA, defn).iter_errors(obj), key=lambda e: (list(e.path), e.message))
    return [f"{'/'.join(map(str, e.path)) or '<root>'}: {e.message[:120]}" for e in errors]


def test_client_sequence_is_initialize_new_prompt_with_paired_ids():
    c2a = _frames("frames-client-to-agent.jsonl")
    assert [(o["id"], o["method"]) for o in c2a] == [(0, "initialize"), (1, "session/new"), (2, "session/prompt")]
    a2c = _frames("frames-agent-to-client.jsonl")
    responses = {o["id"]: o for o in a2c if "id" in o}
    assert set(responses) == {0, 1, 2} and all("error" not in r for r in responses.values())
    notifications = [o for o in a2c if "method" in o]
    assert notifications and all(o["method"] == "session/update" and "id" not in o for o in notifications)


def test_every_frame_of_the_turn_conforms_to_pinned_v1():
    c2a = _frames("frames-client-to-agent.jsonl")
    a2c = _frames("frames-agent-to-client.jsonl")
    by_id = {o["id"]: o for o in a2c if "id" in o}
    assert ci.classify_request(c2a[0]["params"]) == "ok"
    assert ci.classify_response(by_id[0]["result"]) == "ok"
    assert _valid("NewSessionRequest", c2a[1]["params"]) == []
    assert _valid("NewSessionResponse", by_id[1]["result"]) == []
    assert _valid("PromptRequest", c2a[2]["params"]) == []
    assert _valid("PromptResponse", by_id[2]["result"]) == []
    bad = [(i, errs) for i, o in enumerate(a2c) if "method" in o for errs in [_valid("SessionNotification", o["params"])] if errs]
    assert bad == [], bad[:3]


def test_session_identity_and_terminal_state():
    c2a = _frames("frames-client-to-agent.jsonl")
    a2c = _frames("frames-agent-to-client.jsonl")
    sid = next(o for o in a2c if o.get("id") == 1)["result"]["sessionId"]
    assert c2a[2]["params"]["sessionId"] == sid
    notifications = [o for o in a2c if "method" in o]
    assert {o["params"]["sessionId"] for o in notifications} == {sid}
    kinds = [o["params"]["update"]["sessionUpdate"] for o in notifications]
    assert "agent_message_chunk" in kinds  # a prompt turn streamed content updates
    terminal = next(o for o in a2c if o.get("id") == 2)["result"]
    assert terminal["stopReason"] == "end_turn"
    stop_reason_def = SCHEMA["$defs"]["StopReason"]
    allowed = stop_reason_def.get("enum") or [alt["const"] for alt in stop_reason_def.get("oneOf", []) if "const" in alt]
    assert allowed and terminal["stopReason"] in allowed
    # the terminal response follows every content update; only session_info_update trails it
    idx = a2c.index(next(o for o in a2c if o.get("id") == 2))
    trailing = [o["params"]["update"]["sessionUpdate"] for o in a2c[idx + 1:]]
    assert set(trailing) <= {"session_info_update"}, trailing


def test_config_echo_idle_timeout_900_and_record_binding():
    rec = json.loads((EV / "capture.json").read_text())
    line = (EV / "startup-line.txt").read_text()
    assert "idle_timeout=900s" in line and "max_turn=7200s" in line and "session_policy=thread" in line
    argv = (EV / "argv.txt").read_text().split("\n")[:-1]
    assert argv[argv.index("--idle-timeout") + 1] == "900" and rec["config_echo"]["idle_timeout"] == "900s"
    for key in ("client_to_agent", "agent_to_client", "argv", "env_names", "startup_line"):
        f = rec["frames"][key]
        assert hashlib.sha256((EV / f["file"]).read_bytes()).hexdigest() == f["sha256"], key
    m = rec["manifests"]
    assert m["baseline"] == m["pre_capture"] == m["post_capture"] and m["identical"] is True
    assert rec["process"]["omniroute_credential_in_env"] is True and "OMNIROUTE_API_KEY" in (EV / "env-names.txt").read_text().split()
    assert rec["acp_sequence"]["terminal_stop_reason"] == "end_turn"
    assert any("NOT validated" in c for c in rec["caveats"])  # the record states the credential caveat first-class


def test_second_run_same_path_but_the_live_route_structure_differs():
    """Determinism evidence (2026-09-05): identical inputs, two runs, same client sequence and terminal
    state, DIFFERENT session/update structure — the reason the golden needs the deterministic backend."""
    ev2 = P / "evidence" / "turn-20260905T071639Z"
    c2a = [json.loads(l) for l in (ev2 / "frames-client-to-agent.jsonl").read_text().splitlines()]
    a2c = [json.loads(l) for l in (ev2 / "frames-agent-to-client.jsonl").read_text().splitlines()]
    assert [(o["id"], o["method"]) for o in c2a] == [(0, "initialize"), (1, "session/new"), (2, "session/prompt")]
    by_id = {o["id"]: o for o in a2c if "id" in o}
    assert by_id[2]["result"]["stopReason"] == "end_turn"
    assert _valid("NewSessionResponse", by_id[1]["result"]) == [] and _valid("PromptRequest", c2a[2]["params"]) == []
    assert all(_valid("SessionNotification", o["params"]) == [] for o in a2c if "method" in o)
    sid = by_id[1]["result"]["sessionId"]
    assert {o["params"]["sessionId"] for o in a2c if "method" in o} == {sid}
    det = json.loads((P / "evidence" / "determinism-live-route.json").read_text())
    rec1 = json.loads((EV / "capture.json").read_text())
    rec2 = json.loads((ev2 / "capture.json").read_text())
    assert det["run1"]["kind_counts"] == rec1["acp_sequence"]["session_update_kind_counts"]
    assert det["run2"]["kind_counts"] == rec2["acp_sequence"]["session_update_kind_counts"]
    assert det["run1"]["kind_counts"] != det["run2"]["kind_counts"] and det["structure_identical"] is False
    assert all(det["invariant_across_runs"].values())
    for key in ("client_to_agent", "agent_to_client", "argv", "env_names", "startup_line"):
        f = rec2["frames"][key]
        assert hashlib.sha256((ev2 / f["file"]).read_bytes()).hexdigest() == f["sha256"], key
