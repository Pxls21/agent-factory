"""S0-01 — the raw initialize exchange captured 2026-09-05 (pinned buzz-acp -> pinned hermes-acp).

Deterministic, LLM-free, network-free. Proves, from the committed RAW JSON-RPC frames and their
provenance record: the client offered protocol 2; the agent returned protocol 1; both frames conform
to the pinned v1 schema; the capability VALUES are the pinned contract; the record binds the frames to
the pinned binaries/trees (digests recomputed here); no OmniRoute credential was in the environment
and no prompt was issued. It does NOT claim any other S0-01 assertion.

Negative control: the seed fixture `fixtures/neg-malformed-initialize.json` (the captured pinned
request minus its one required field) classifies as exactly
`protocol-violation: missing required initialize field`, and is de-vacuoused both ways.
"""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
P = ROOT / "proofs" / "S0-01"
EV = P / "evidence" / "initialize-20260905T062959Z"
CHECKER = P / "check_initialize.py"
sys.path.insert(0, str(P))
import check_initialize as ci  # noqa: E402

PINNED_AGENT_CAPABILITIES = {
    "loadSession": True,
    "promptCapabilities": {"image": True},
    "sessionCapabilities": {"fork": {}, "list": {}, "resume": {}},
}
PINNED_AGENT_INFO = {"name": "hermes-agent", "version": "0.21.0"}


def _sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def _frame(name: str) -> dict:
    lines = (EV / name).read_text().splitlines()
    assert len(lines) == 1, f"{name}: expected exactly one raw frame, got {len(lines)}"
    return json.loads(lines[0])


def _record() -> dict:
    return json.loads((EV / "capture.json").read_text())


def test_request_frame_conforms_to_pinned_v1_and_offers_protocol_2():
    req = _frame("frames-client-to-agent.jsonl")
    assert req["jsonrpc"] == "2.0" and req["method"] == "initialize"
    assert ci.classify_request(req["params"]) == "ok"
    assert req["params"]["protocolVersion"] == 2
    assert req["params"]["clientInfo"] == {"name": "buzz-acp", "version": "0.1.0"}


def test_response_frame_conforms_to_pinned_v1_and_returns_protocol_1_with_pinned_capabilities():
    req = _frame("frames-client-to-agent.jsonl")
    res = _frame("frames-agent-to-client.jsonl")
    assert res["jsonrpc"] == "2.0" and res["id"] == req["id"] and "error" not in res
    assert ci.classify_response(res["result"]) == "ok"
    assert res["result"]["protocolVersion"] == 1
    assert res["result"]["agentCapabilities"] == PINNED_AGENT_CAPABILITIES
    assert res["result"]["agentInfo"] == PINNED_AGENT_INFO
    # v1 requires only protocolVersion; the pinned schema says so, and the frame carried it.
    schema = ci.load_schema()
    assert schema["$defs"]["InitializeResponse"]["required"] == ["protocolVersion"]
    assert schema["$defs"]["InitializeRequest"]["required"] == ["protocolVersion"]


def test_record_binds_frames_instrument_schema_and_pinned_trees():
    rec = _record()
    assert rec["protocol"]["client_offered_protocolVersion"] == 2
    assert rec["protocol"]["agent_returned_protocolVersion"] == 1
    for key in ("client_to_agent", "agent_to_client", "argv", "env_names"):
        f = rec["frames"][key]
        assert _sha(EV / f["file"]) == f["sha256"], key
    # The v1 captures were produced by the v1 tee; pin against the archived copy (V-d F1).
    assert _sha(P / "tools" / "archive" / "frame_tee_v1.py") == rec["components"]["frame_tee"]["sha256"]
    assert _sha(P / "fixtures" / "acp-schema-v1.json") == rec["components"]["acp-schema-v1"]["sha256"]
    m = rec["manifests"]
    assert m["baseline"] == m["pre_capture"] == m["post_capture"] and m["identical"] is True
    assert set(m["baseline"]) == {"hermes-agent", "buzz", "acp"}
    argv = (EV / "argv.txt").read_text().split("\n")[:-1]
    assert argv == rec["process"]["argv"]
    assert argv[0] == rec["components"]["buzz-acp"]["path"]
    assert argv[argv.index("--agent-command") + 1] == rec["components"]["frame_tee"]["path"]
    assert argv[argv.index("--idle-timeout") + 1] == "900"
    env_names = (EV / "env-names.txt").read_text().split()
    assert env_names == rec["process"]["env_names"]
    assert not any(n.startswith("OMNIROUTE") for n in env_names)
    assert rec["process"]["omniroute_credential_in_env"] is False
    assert rec["process"]["prompt_issued"] is False
    assert "PYTHONDONTWRITEBYTECODE" in env_names


def test_negative_control_fixture_classifies_exactly_and_is_not_vacuous():
    fixture = json.loads((P / "fixtures" / "neg-malformed-initialize.json").read_text())
    assert "protocolVersion" not in fixture
    assert ci.classify_request(fixture) == "protocol-violation: missing required initialize field"
    # de-vacuous (1): restoring the field makes the same document conformant
    assert ci.classify_request({**fixture, "protocolVersion": 2}) == "ok"
    # de-vacuous (2): a DIFFERENT violation is reported as a different reason, not folded into ours
    other = ci.classify_request({**fixture, "protocolVersion": "two"})
    assert other.startswith("protocol-violation: ") and other != "protocol-violation: missing required initialize field"
    # the fixture is the pinned captured request minus its one required field (authored from the pin, frozen)
    req = _frame("frames-client-to-agent.jsonl")
    assert {k: v for k, v in req["params"].items() if k != "protocolVersion"} == fixture


def test_checker_cli_exit_codes_and_messages(tmp_path):
    def run(kind, path):
        return subprocess.run([sys.executable, str(CHECKER), kind, str(path)], capture_output=True, text=True, timeout=60)
    ok = run("request", EV / "frames-client-to-agent.jsonl")
    assert (ok.returncode, ok.stdout.strip(), ok.stderr) == (0, "ok", "")
    ok2 = run("response", EV / "frames-agent-to-client.jsonl")
    assert (ok2.returncode, ok2.stdout.strip()) == (0, "ok")
    neg = run("request", P / "fixtures" / "neg-malformed-initialize.json")
    assert (neg.returncode, neg.stdout.strip()) == (1, "protocol-violation: missing required initialize field")
    bad = tmp_path / "not-initialize.jsonl"
    bad.write_text(json.dumps({"jsonrpc": "2.0", "id": 1, "method": "session/new", "params": {}}) + "\n")
    usage = run("request", bad)
    assert usage.returncode == 2 and "not 'initialize'" in usage.stderr
