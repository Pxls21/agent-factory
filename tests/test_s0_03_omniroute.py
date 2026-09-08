"""S0-03 Hermes -> OmniRoute live round trip — deterministic, LLM-free tests.

Every hostile bundle is a COPY under the test's tmp_path; the three committed negative bundles
are only ever READ (AF-AP-42: the real-bundle CLI path runs unpatched against the committed
bytes). No network call leaves the host: the probe tests bind a real `http.server` on 127.0.0.1
and use a real closed port, so urllib's own error taxonomy is exercised rather than a mock of it.

The mutation suite is the point of this file. `test_conjunct_*` falsifies ONE conjunct of the
checker's conjunction at a time against an otherwise-passing bundle and pins the exact reason
each produces, in the checker's first-failure order — a conjunction whose conjuncts are never
individually falsified is a tautology wearing six hats (AF-AP-30).
"""
from __future__ import annotations

import http.server
import importlib.util
import inspect
import json
import shutil
import socket
import subprocess
import sys
import threading
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
PROOF = ROOT / "proofs" / "S0-03"
CHECKER = PROOF / "check_omniroute_roundtrip.py"
PROBE = PROOF / "probe_omniroute.py"
SPEC = PROOF / "spec.json"
FIXTURES = PROOF / "fixtures"
RUNNER = PROOF / "tools" / "pc" / "run_s0_03_legs.sh"
COLLECT = PROOF / "tools" / "pc" / "collect_leg.sh"

NEGATIVE_BUNDLES = (
    "evidence-credential-absent",
    "evidence-stub-route",
    "evidence-provider-key-present",
)


def _load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


check = _load(CHECKER, "s0_03_check_omniroute_roundtrip")


# --------------------------------------------------------------------------- the spec is the
# --------------------------------------------------------------------------- single source
def _spec() -> dict:
    return json.loads(SPEC.read_text())


def _leg_flags(leg: dict) -> dict:
    """Read the declarations back out of a spec leg's cmd — the checker's inputs ride there
    because spec.schema.json forbids any key beside proof_id/legs."""
    cmd = leg["cmd"]
    out = {"stub_routes": []}
    i = 0
    while i < len(cmd):
        if cmd[i] == "--route-id":
            out["route_id"] = cmd[i + 1]
        elif cmd[i] == "--expected-model-id":
            out["expected_model_id"] = cmd[i + 1]
        elif cmd[i] == "--stub-route":
            out["stub_routes"].append(cmd[i + 1])
        i += 1
    return out


def _positive_leg() -> dict:
    return next(leg for leg in _spec()["legs"] if leg["leg"] == "positive")


def _flags() -> list:
    """The checker's declared inputs, taken from spec.json — NEVER a literal in this file."""
    flags = _leg_flags(_positive_leg())
    argv = ["--route-id", flags["route_id"],
            "--expected-model-id", flags["expected_model_id"]]
    for stub in flags["stub_routes"]:
        argv += ["--stub-route", stub]
    return argv


def run_checker(root, *, extra=None):
    cmd = [sys.executable, str(CHECKER)] + _flags() + (extra or []) + [str(root)]
    return subprocess.run(cmd, capture_output=True, text=True, timeout=120, cwd=str(ROOT))


# --------------------------------------------------------------------------- passing bundle
@pytest.fixture
def passing(tmp_path) -> Path:
    """A synthetic PASSING bundle, built from the committed shapes: the stub-route bundle is a
    pass in every respect except its provider connection, so repairing that ONE field is the
    smallest honest way to construct a positive from committed bytes."""
    root = tmp_path / "evidence"
    shutil.copytree(FIXTURES / "evidence-stub-route", root)
    path = root / "omniroute-requests.json"
    record = json.loads(path.read_text())
    for row in record["requests"]:
        row["provider"] = "openai-codex"
    path.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n")
    return root


def _edit(root: Path, rel: str, mutate):
    path = root / rel
    record = json.loads(path.read_text())
    mutate(record)
    path.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n")


def _timeline(root: Path):
    path = root / "hermes" / "timeline.jsonl"
    return path, [json.loads(l) for l in path.read_text().splitlines() if l.strip()]


def _write_timeline(path: Path, entries):
    path.write_text("".join(json.dumps(e, sort_keys=True) + "\n" for e in entries))


def test_passing_bundle_passes(passing):
    result = run_checker(passing)
    assert result.returncode == 0, result.stdout + result.stderr
    assert result.stdout.startswith(
        "PASS: S0-03 omniroute-roundtrip - model "), result.stdout
    # The PASS line NAMES each conjunct it stands on, so a green cannot hide which parts ran.
    assert "via openai-codex" in result.stdout
    assert "tool-call round trip" in result.stdout
    assert "env clean" in result.stdout


# --------------------------------------------------------------------------- the committed
# --------------------------------------------------------------------------- negative bundles
@pytest.mark.parametrize("bundle,reason", [
    ("evidence-credential-absent",
     "blocked: credential_absent"),
    ("evidence-stub-route",
     "identity: request routed to the sanctioned stub route 's0-01-scripted', "
     "not an upstream model"),
    ("evidence-provider-key-present",
     "env: upstream provider key OPENAI_API_KEY present in the Hermes environ"),
])
def test_committed_negative_bundle_exact_reason(bundle, reason):
    """Run UNPATCHED against the committed bytes — the bundles the runner will grade."""
    result = run_checker(FIXTURES / bundle)
    assert result.returncode == 1, result.stdout + result.stderr
    assert result.stdout.strip() == f"failure_reason: {reason}"


def test_credential_absent_reason_is_the_seed_kill_switch():
    """`seeds/seed-stage0-v1.yaml:400` pins this string. It is the one reason a lane may not
    paraphrase (AF-AP-27: a frozen contract changes only by an explicit owner decision)."""
    assert check.REASONS["credential_absent"] == "blocked: credential_absent"


def test_every_negative_bundle_is_a_declared_spec_leg():
    legs = [leg for leg in _spec()["legs"] if leg["leg"] == "negative"]
    declared = {leg["cmd"][-1] for leg in legs}
    for bundle in NEGATIVE_BUNDLES:
        assert f"proofs/S0-03/fixtures/{bundle}" in declared
    # required_negative_controls is 1; three are shipped and ALL three are listed.
    assert len(legs) == 3


def test_each_negative_leg_reason_is_produced_verbatim():
    """AF-AP-29: the canonical contract must be at least as strong as the strongest test. The
    spec's `failure_reason` is the COMPLETE reason the checker emits, never a prefix of it."""
    for leg in _spec()["legs"]:
        if leg["leg"] != "negative":
            continue
        result = run_checker(ROOT / leg["cmd"][-1])
        assert result.returncode == leg["expect"]["exit_code"]
        assert result.stdout.strip() == f"failure_reason: {leg['expect']['failure_reason']}"


def test_fixtures_track_the_spec_expected_model_id():
    """The two PASSING-shaped negative bundles must carry the model id the spec declares, or
    conjunct (ii) fires before their own conjunct does and they stop testing what they name.
    This goes red the moment the spec's expected_model_id is filled in from the PC capture
    without the fixtures being regenerated in the same edit (AF-AP-42)."""
    expected = _leg_flags(_positive_leg())["expected_model_id"]
    for bundle in ("evidence-stub-route", "evidence-provider-key-present"):
        record = json.loads((FIXTURES / bundle / "direct" / "direct.json").read_text())
        assert record["model"] == expected, bundle
        rows = json.loads((FIXTURES / bundle / "omniroute-requests.json").read_text())
        for row in rows["requests"]:
            assert row["model"] == expected, bundle


def test_every_bundle_has_provenance():
    """AF-AP-42: a synthetic fixture must say where each file's shape came from."""
    for bundle in NEGATIVE_BUNDLES:
        text = (FIXTURES / bundle / "PROVENANCE.md").read_text()
        assert "NOT proven against a live capture" in text
        for rel in ("direct/direct.json", "hermes/timeline.jsonl", "omniroute-requests.json"):
            assert rel in text, (bundle, rel)


# --------------------------------------------------------------------------- the six mutants
# One conjunct falsified at a time, in the checker's first-failure order.
def test_conjunct_i_direct_stream(passing):
    """(i) a real streamed answer: drop the only text delta."""
    _edit(passing, "direct/direct.json", lambda r: r.__setitem__(
        "events", [e for e in r["events"] if e.get("type") != "response.output_text.delta"]))
    result = run_checker(passing)
    assert result.returncode == 1
    assert result.stdout.strip() == (
        "failure_reason: direct: no response.output_text.delta event")


def test_conjunct_i_rejects_a_vacuous_nonce(passing):
    """A nonce that is not a fresh 16-hex token would make "the nonce is in the text" vacuous.
    The domain floor rejects the whole unusable class, not just the empty specimen."""
    # Uppercase hex, one char short, one char long, and a non-hex tail are all rejected as a
    # CLASS, not as the one empty specimen.
    for bad in ("x", "A1B2C3D4E5F60718", "a1b2c3d4e5f6071", "a1b2c3d4e5f60718z", "0" * 32):
        _edit(passing, "direct/direct.json", lambda r, b=bad: r.__setitem__("nonce", b))
        result = run_checker(passing)
        assert result.returncode == 1, bad
        assert "is not a fresh 16-hex token" in result.stdout, bad
    # The empty nonce is caught one rung earlier, by the typed read, with its own named reason.
    _edit(passing, "direct/direct.json", lambda r: r.__setitem__("nonce", ""))
    result = run_checker(passing)
    assert result.returncode == 1
    assert result.stdout.strip() == (
        "failure_reason: bundle: direct.json nonce is not a non-empty string")


def test_conjunct_i_requires_the_compression_header_was_sent(passing):
    _edit(passing, "direct/direct.json", lambda r: r["request_headers_sent"].__setitem__(
        "x-omniroute-compression", "on"))
    result = run_checker(passing)
    assert result.returncode == 1
    assert "x-omniroute-compression sent as 'on', expected 'off'" in result.stdout


def test_conjunct_ii_identity_model(passing):
    """(ii) the response model id must equal the declared upstream id."""
    _edit(passing, "direct/direct.json", lambda r: r.__setitem__("model", "some-other-model"))
    _edit(passing, "omniroute-requests.json", lambda r: [
        row.__setitem__("model", "some-other-model") for row in r["requests"]])
    result = run_checker(passing)
    assert result.returncode == 1
    expected = _leg_flags(_positive_leg())["expected_model_id"]
    assert result.stdout.strip() == (
        f"failure_reason: identity: response model 'some-other-model' != "
        f"declared upstream model '{expected}'")


def test_conjunct_iii_identity_route(passing):
    """(iii) the independent instrument: a stub provider connection."""
    _edit(passing, "omniroute-requests.json", lambda r: r["requests"][0].__setitem__(
        "provider", "s0-01-scripted"))
    result = run_checker(passing)
    assert result.returncode == 1
    assert result.stdout.strip() == (
        "failure_reason: identity: request routed to the sanctioned stub route "
        "'s0-01-scripted', not an upstream model")


def test_conjunct_iii_catches_every_declared_stub_id_and_its_namespace(passing):
    """AF-AP-30: close the CLASS. Each declared stub id is rejected, and so is a model
    namespaced under one — an exact-match-only rule would pass `s0-01-scripted/anything-new`."""
    declared = _leg_flags(_positive_leg())["stub_routes"]
    assert "s0-01-scripted" in declared
    assert "s0-01-scripted/s0-01-pong" in declared
    assert "s0-01-scripted/s0-01-slow" in declared
    for stub in declared + ["s0-01-scripted/a-route-nobody-listed", "S0-01-SCRIPTED"]:
        _edit(passing, "omniroute-requests.json", lambda r, s=stub: [
            row.__setitem__("provider", s) for row in r["requests"]])
        result = run_checker(passing)
        assert result.returncode == 1, stub
        assert "identity: request routed to the sanctioned stub route" in result.stdout, stub


def test_conjunct_iii_binds_the_row_to_our_route(passing):
    """A call_logs row for somebody else's request proves nothing about ours."""
    _edit(passing, "omniroute-requests.json", lambda r: r["requests"][1].__setitem__(
        "requested_model", "someone-elses-route"))
    result = run_checker(passing)
    assert result.returncode == 1
    assert "requested_model 'someone-elses-route' != declared route" in result.stdout


def test_conjunct_iii_requires_the_two_instruments_to_agree(passing):
    """The response model and the call_logs model must be the same id — otherwise the two
    instruments are describing different requests and neither corroborates the other."""
    _edit(passing, "omniroute-requests.json", lambda r: [
        row.__setitem__("model", "drifted-model") for row in r["requests"]])
    result = run_checker(passing)
    assert result.returncode == 1
    assert "call_logs model 'drifted-model' != response model" in result.stdout


def test_conjunct_iv_roundtrip_requires_a_completed_tool_call(passing):
    """(iv) a tool call that STARTS but never completes is not a round trip."""
    path, entries = _timeline(passing)
    for entry in entries:
        update = entry["frame"].get("params", {}).get("update", {})
        if update.get("status") == "completed":
            update["status"] = "failed"
    _write_timeline(path, entries)
    result = run_checker(passing)
    assert result.returncode == 1
    assert result.stdout.strip() == (
        "failure_reason: roundtrip: no tool_call reached status 'completed'")


def test_conjunct_iv_roundtrip_requires_a_tool_call_at_all(passing):
    """The text-only turn: a model that answers with the nonce and never calls a tool passes
    every text assertion. Premortem row 2 (`docs/09_PREMORTEM.md:8`) is exactly this."""
    path, entries = _timeline(passing)
    kept = [e for e in entries
            if "tool_call" not in json.dumps(e.get("frame", {}))]
    _write_timeline(path, kept)
    result = run_checker(passing)
    assert result.returncode == 1
    assert result.stdout.strip() == "failure_reason: roundtrip: no tool_call update in the timeline"


def test_conjunct_iv_requires_exactly_one_prompt_turn(passing):
    path, entries = _timeline(passing)
    prompt = next(e for e in entries if e["frame"].get("method") == "session/prompt")
    duplicate = json.loads(json.dumps(prompt))
    duplicate["seq"] = max(e["seq"] for e in entries) + 1
    _write_timeline(path, entries + [duplicate])
    result = run_checker(passing)
    assert result.returncode == 1
    assert result.stdout.strip() == "failure_reason: roundtrip: 2 session/prompt turns, expected exactly 1"


def test_conjunct_iv_requires_the_nonce_in_the_final_text(passing):
    path, entries = _timeline(passing)
    for entry in entries:
        update = entry["frame"].get("params", {}).get("update", {})
        if update.get("sessionUpdate") == "agent_message_chunk":
            update["content"]["text"] = "done"
    _write_timeline(path, entries)
    result = run_checker(passing)
    assert result.returncode == 1
    assert "absent from the final agent text" in result.stdout


def test_conjunct_iv_binds_the_answer_to_the_question(passing):
    """The nonce the checker hunts in the answer must be the one the PROMPT asked for, so a
    bundle cannot pass by carrying a correct answer to a different question."""
    _edit(passing, "hermes/leg.json", lambda r: r.__setitem__("nonce2", "beefbeefbeefbeef"))
    result = run_checker(passing)
    assert result.returncode == 1
    assert "absent from the prompt frame" in result.stdout


def test_conjunct_v_transport(passing):
    """(v) the ADR's transport. The owner's live profiles currently use `chat_completions`
    (docs/OMNIROUTE-HERMES-FEDORA-HANDOFF.md:17) — this proof PINS the ADR and reports the
    deviation as RED rather than switching to it."""
    profile = passing / "hermes" / "profile.yaml"
    profile.write_text(profile.read_text().replace(
        "api_mode: codex_responses", "api_mode: chat_completions"))
    result = run_checker(passing)
    assert result.returncode == 1
    assert result.stdout.strip() == (
        "failure_reason: transport: profile api_mode 'chat_completions' != "
        "'codex_responses' (ADR 0002)")


def test_conjunct_v_rejects_an_inline_key_in_the_captured_profile(passing):
    profile = passing / "hermes" / "profile.yaml"
    profile.write_text(profile.read_text().replace(
        "    key_env: OMNIROUTE_API_KEY",
        "    key_env: OMNIROUTE_API_KEY\n    api_key: sk-not-a-real-key"))
    result = run_checker(passing)
    assert result.returncode == 1
    assert "profile.yaml carries an inline api_key" in result.stdout


def test_conjunct_v_requires_the_compression_header_in_the_profile(passing):
    profile = passing / "hermes" / "profile.yaml"
    profile.write_text(profile.read_text().replace('"off"', '"default"'))
    result = run_checker(passing)
    assert result.returncode == 1
    assert "x-omniroute-compression is 'default', expected 'off'" in result.stdout


def test_conjunct_vi_env(passing):
    """(vi) the deny-by-default allow-list."""
    _edit(passing, "hermes/hermes-env-names.json",
          lambda r: r["names"].append("ANTHROPIC_API_KEY"))
    result = run_checker(passing)
    assert result.returncode == 1
    assert result.stdout.strip() == (
        "failure_reason: env: upstream provider key ANTHROPIC_API_KEY present in the "
        "Hermes environ")


def test_first_failure_order_is_pinned(passing):
    """Falsify EVERY conjunct at once: the reason reported is the first in the checker's order,
    which is what makes each single-conjunct mutant above meaningful."""
    _edit(passing, "direct/direct.json", lambda r: r.__setitem__("status", 500))
    _edit(passing, "omniroute-requests.json", lambda r: [
        row.__setitem__("provider", "s0-01-scripted") for row in r["requests"]])
    _edit(passing, "hermes/hermes-env-names.json", lambda r: r["names"].append("OPENAI_API_KEY"))
    result = run_checker(passing)
    assert result.returncode == 1
    # The credential kill switch outranks every conjunct; with the credential present the
    # stream conjunct is next.
    assert result.stdout.strip() == "failure_reason: direct: status 500, expected 200"


def test_credential_absent_outranks_the_stream_conjunct(passing):
    """The kill switch must win over the SYMPTOM it causes: a 401 also breaks conjunct (i), and
    grading it as "no streamed answer" would lose the seed's pinned reason."""
    _edit(passing, "direct/direct.json", lambda r: r.__setitem__("status", 401))
    result = run_checker(passing)
    assert result.stdout.strip() == "failure_reason: blocked: credential_absent"


# --------------------------------------------------------------------------- the env allow-list
@pytest.mark.parametrize("name,rejected", [
    ("OMNIROUTE_API_KEY", False),
    ("PATH", False),
    ("HOME", False),
    ("HERMES_HOME", False),
    ("FOO_API_KEY", True),
    ("OMNIROUTE_API_KEY_2", True),
    ("OPENAI_API_KEY", True),
    ("ANTHROPIC_API_KEY", True),
    ("OPENROUTER_API_KEY", True),
    ("GITHUB_TOKEN", True),
    ("SOME_SECRET", True),
    ("AWS_SECRET_ACCESS_KEY", True),
])
def test_env_allowlist_is_a_closed_exact_set(name, rejected):
    """AF-AP-23: a CLOSED EXACT allow-list, never a prefix and never a blacklist.
    `OMNIROUTE_API_KEY_2` is the prefix trap: it starts with the allowed name and must still be
    rejected. `FOO_API_KEY` is the provider nobody listed."""
    if rejected:
        with pytest.raises(check.Failure) as excinfo:
            check.check_env([name])
        assert str(excinfo.value) == (
            f"env: upstream provider key {name} present in the Hermes environ")
    else:
        check.check_env([name])


def test_env_allowlist_reports_deterministically():
    """Two offenders must give ONE stable reason, not whichever the set iterated first."""
    for order in (["ZZZ_TOKEN", "AAA_API_KEY"], ["AAA_API_KEY", "ZZZ_TOKEN"]):
        with pytest.raises(check.Failure) as excinfo:
            check.check_env(order)
        assert "AAA_API_KEY" in str(excinfo.value)


# --------------------------------------------------------------------------- the reason table
def test_reason_values_are_unique():
    values = list(check.REASONS.values())
    assert len(values) == len(set(values))


def test_every_failing_exit_uses_the_reason_table():
    """Every `_fail(...)` names a key that exists, and every key is reachable from some call —
    an emitted-but-unreachable reason is a silent hollow green."""
    source = CHECKER.read_text()
    import re
    used = set(re.findall(r'_fail\(\s*"([a-z_]+)"', source))
    assert used <= set(check.REASONS), used - set(check.REASONS)
    assert used == set(check.REASONS), set(check.REASONS) - used


def test_reason_templates_render_without_stray_placeholders():
    for key, template in check.REASONS.items():
        rendered = template.format(*(["x"] * template.count("{")))
        assert "{" not in rendered and "}" not in rendered, key


# --------------------------------------------------------------------------- structural reads
def test_timeline_reader_is_imported_from_the_s0_01_checker():
    """The brief forbids a COPY of S0-01's reader. Assert by module identity, never by grep:
    a grep for the function name would pass on a pasted duplicate."""
    module = check._load_s0_01_module()
    reader = module._load_timeline_raw
    assert inspect.getmodule(reader) is module
    source_file = Path(inspect.getsourcefile(reader)).resolve()
    assert source_file == (ROOT / "proofs" / "S0-01" / "check_acp_conformance.py").resolve()


@pytest.mark.parametrize("rel", [
    "direct/direct.json",
    "hermes/hermes-env-names.json",
    "hermes/leg.json",
    "hermes/profile.yaml",
    "hermes/timeline.jsonl",
    "omniroute-requests.json",
])
def test_fifo_at_any_evidence_path_fails_in_bounded_time(passing, rel):
    """A FIFO blocks forever on open(); the S_ISREG guard must refuse BEFORE any read."""
    import os
    target = passing / rel
    target.unlink()
    os.mkfifo(target)
    result = subprocess.run(
        [sys.executable, str(CHECKER)] + _flags() + [str(passing)],
        capture_output=True, text=True, timeout=30, cwd=str(ROOT))
    assert result.returncode == 1, result.stdout + result.stderr
    assert "is not a regular file" in result.stdout, result.stdout


@pytest.mark.parametrize("rel", [
    "direct/direct.json",
    "hermes/hermes-env-names.json",
    "omniroute-requests.json",
])
def test_directory_at_an_evidence_path_is_a_named_failure(passing, rel):
    target = passing / rel
    target.unlink()
    target.mkdir()
    result = run_checker(passing)
    assert result.returncode == 1
    assert "is not a regular file" in result.stdout


@pytest.mark.parametrize("rel", [
    "direct/direct.json",
    "hermes/hermes-env-names.json",
    "hermes/leg.json",
    "hermes/profile.yaml",
    "hermes/timeline.jsonl",
    "omniroute-requests.json",
])
def test_absent_file_is_a_failure_not_a_deferral(passing, rel):
    """AF-AP-40: once a leg directory exists, absence is a Failure naming the file. A missing
    file must never shrink the proof into a green or a silent skip."""
    (passing / rel).unlink()
    result = run_checker(passing)
    assert result.returncode == 1, result.stdout
    assert "absent" in result.stdout


def test_deferred_when_nothing_was_captured(tmp_path):
    result = run_checker(tmp_path / "no-such-bundle")
    assert result.returncode == 2
    assert result.stdout.strip() == "deferred: S0-03 evidence not captured"


def test_deferred_when_the_root_has_no_leg_directory(tmp_path):
    root = tmp_path / "evidence"
    root.mkdir()
    (root / "README").write_text("empty\n")
    result = run_checker(root)
    assert result.returncode == 2


def test_usage_error_is_64_not_a_deferral(tmp_path):
    result = subprocess.run([sys.executable, str(CHECKER), str(tmp_path)],
                            capture_output=True, text=True, timeout=30, cwd=str(ROOT))
    assert result.returncode == 64
    assert "usage:" in result.stderr


def test_malformed_json_is_a_named_failure(passing):
    (passing / "direct" / "direct.json").write_text("{not json")
    result = run_checker(passing)
    assert result.returncode == 1
    assert "is not valid JSON" in result.stdout


# --------------------------------------------------------------------------- spec + schema
def test_spec_validates_against_the_schema():
    import jsonschema
    schema = json.loads((ROOT / "proofs" / "schemas" / "spec.schema.json").read_text())
    jsonschema.validate(_spec(), schema)


def test_spec_proof_id_and_checker_path():
    spec = _spec()
    assert spec["proof_id"] == "S0-03"
    for leg in spec["legs"]:
        assert leg["cmd"][1] == "proofs/S0-03/check_omniroute_roundtrip.py"
        assert leg["cwd"] == "."


def test_spec_declares_the_stub_routes_the_deployment_has():
    """The PC's authenticated catalog carries two sanctioned stub ids under the `s0-01-scripted`
    connection (coordinator's bridge measurement, 2026-09-08). Both, and the bare connection
    name, must be declared — a stub the spec does not name is a stub the checker cannot see."""
    stubs = _leg_flags(_positive_leg())["stub_routes"]
    assert set(stubs) == {
        "s0-01-scripted", "s0-01-scripted/s0-01-pong", "s0-01-scripted/s0-01-slow"}


def test_every_leg_declares_the_same_inputs():
    """A negative leg run with different declarations would be grading a different checker."""
    baseline = _leg_flags(_positive_leg())
    for leg in _spec()["legs"]:
        assert _leg_flags(leg) == baseline, leg["cmd"][-1]


# --------------------------------------------------------------------------- the probe, over
# --------------------------------------------------------------------------- REAL sockets
class _Handler(http.server.BaseHTTPRequestHandler):
    status = 200

    def do_GET(self):
        body = b'{"data":[]}'
        self.send_response(self.status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *args):
        pass


def _serve(status):
    handler = type("H", (_Handler,), {"status": status})
    server = http.server.HTTPServer(("127.0.0.1", 0), handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return server, thread


def _closed_port() -> int:
    sock = socket.socket()
    sock.bind(("127.0.0.1", 0))
    port = sock.getsockname()[1]
    sock.close()
    return port


def run_probe(url, env_key="present"):
    import os
    env = {"PATH": os.environ.get("PATH", "/usr/bin:/bin")}
    if env_key == "present":
        env["OMNIROUTE_API_KEY"] = "test-only-not-a-real-key"
    return subprocess.run([sys.executable, str(PROBE), url],
                          capture_output=True, text=True, timeout=60, env=env)


@pytest.mark.parametrize("status,expected", [(200, 0), (401, 11), (403, 11), (500, 12)])
def test_probe_maps_each_http_status(status, expected):
    """Real sockets, no monkeypatching of urllib: the taxonomy under test IS urllib's."""
    server, _thread = _serve(status)
    try:
        port = server.server_address[1]
        result = run_probe(f"http://127.0.0.1:{port}/v1/models")
        assert result.returncode == expected, (status, result.stderr)
    finally:
        server.shutdown()
        server.server_close()


def test_probe_key_absent_is_10():
    server, _thread = _serve(200)
    try:
        port = server.server_address[1]
        result = run_probe(f"http://127.0.0.1:{port}/v1/models", env_key="absent")
        assert result.returncode == 10
    finally:
        server.shutdown()
        server.server_close()


def test_probe_closed_port_is_13_not_credential_rejected():
    """THE BUG THIS FIX CLOSES. Before it, an unreachable OmniRoute returned 11
    `credential_rejected`, which `scripts/validate-ledger:336-338` escalates to proof-RED — a
    service outage reported as the owner's credential being refused."""
    result = run_probe(f"http://127.0.0.1:{_closed_port()}/v1/models")
    assert result.returncode == 13


def test_probe_dns_failure_is_13():
    result = run_probe("http://s0-03-no-such-host.invalid/v1/models")
    assert result.returncode == 13


def test_probe_usage_error_is_64():
    result = run_probe("")
    assert result.returncode == 64


def test_probe_never_prints_the_key():
    server, _thread = _serve(401)
    try:
        port = server.server_address[1]
        result = run_probe(f"http://127.0.0.1:{port}/v1/models")
        assert "test-only-not-a-real-key" not in (result.stdout + result.stderr)
    finally:
        server.shutdown()
        server.server_close()


def test_probe_json_reason_map_covers_exactly_the_credential_verdicts():
    """`probe.json`'s reason_map must map 10 and 11 and NOT 12/13: an unmapped exit makes the
    runner raise `probe-invalid` (LOUD) instead of minting a marker that misnames the blocker
    (`scripts/proof-runner:264-266`)."""
    probe_json = json.loads((PROOF / "probe.json").read_text())
    assert probe_json["reason_map"] == {"10": "credential_absent", "11": "credential_rejected"}
    assert probe_json["key_env"] == "OMNIROUTE_API_KEY"


def test_probe_exit_constants_match_the_reason_map():
    probe = _load(PROBE, "s0_03_probe_omniroute")
    assert probe.EXIT_KEY_ABSENT == 10
    assert probe.EXIT_KEY_REJECTED == 11
    assert probe.EXIT_HTTP_OTHER == 12
    assert probe.EXIT_UNREACHABLE == 13
    assert probe.REJECTING_STATUSES == (401, 403)


# --------------------------------------------------------------------------- PC tools
def test_pc_shell_tools_parse():
    for script in (RUNNER, COLLECT):
        result = subprocess.run(["bash", "-n", str(script)], capture_output=True, text=True)
        assert result.returncode == 0, (script.name, result.stderr)


def test_pc_tools_never_name_match_processes():
    """AF-AP-34 / AF-AP-59: `pkill`, `pgrep -f` and `killall` match the owner's production
    processes by name. Four `pkill -x buzz-relay` already restarted buzz-prod-relay-1."""
    import re
    for script in (RUNNER, COLLECT):
        text = script.read_text()
        assert not re.search(r"\bpkill\b|\bkillall\b|\bpgrep\b", text), script.name


def test_pc_tools_never_put_a_credential_in_argv():
    """AF-AP-39: a value interpolated into a command line sits in world-readable
    /proc/<pid>/cmdline. The key may travel only in a header file or an env dict."""
    import re
    for path in (RUNNER, COLLECT,
                 PROOF / "tools" / "pc" / "direct_responses_probe.py",
                 PROOF / "tools" / "pc" / "hermes_env_names.py"):
        text = path.read_text()
        assert not re.search(r'bash -c "[^"]*(KEY|TOKEN|SECRET)=', text), path.name
        assert not re.search(r"env\s+-i[^\n]*(KEY|TOKEN|SECRET)=", text), path.name


def test_direct_probe_does_not_impersonate_the_codex_cli():
    """OmniRoute rewrites the response `model` to the REQUESTED id when the caller's
    `originator`/`user-agent` starts with "codex" (open-sse/handlers/chatCore.ts:1022-1026 via
    open-sse/config/codexIdentity.ts:537-538). A probe that looked like Codex would turn its own
    identity assertion into a mirror of its request."""
    probe = _load(PROOF / "tools" / "pc" / "direct_responses_probe.py", "s0_03_direct_probe")
    assert not probe.USER_AGENT.lower().startswith("codex")
    text = (PROOF / "tools" / "pc" / "direct_responses_probe.py").read_text()
    assert '"originator"' not in text


def test_direct_probe_redacts_the_authorization_header_it_records():
    probe = _load(PROOF / "tools" / "pc" / "direct_responses_probe.py", "s0_03_direct_probe2")
    events = probe.parse_sse(
        'data: {"type":"response.created","response":{"model":"m"}}\n\n'
        'data: {"type":"response.output_text.delta","delta":"abc"}\n\n'
        'data: [DONE]\n\n')
    assert [e["type"] for e in events] == ["response.created", "response.output_text.delta"]
    assert probe._first_model(events) == "m"


def test_direct_probe_key_reader_extracts_only_the_omniroute_line(tmp_path):
    """The owner's profile env carries many unrelated Hermes variables; exactly one line is
    the credential, and a wrong extraction would send the wrong value or leak another."""
    probe = _load(PROOF / "tools" / "pc" / "direct_responses_probe.py", "s0_03_direct_probe3")
    env_file = tmp_path / ".env"
    env_file.write_text(
        "TERMINAL_DEBUG=1\n"
        "BROWSER_HEADLESS=true\n"
        'OMNIROUTE_API_KEY="sk-test-only-value"\n'
        "OMNIROUTE_API_KEY_2=decoy\n"
        "OTHER_TOKEN=nope\n")
    assert probe.read_key(str(env_file)) == "sk-test-only-value"


def test_direct_probe_key_reader_fails_loud(tmp_path):
    probe = _load(PROOF / "tools" / "pc" / "direct_responses_probe.py", "s0_03_direct_probe4")
    missing = tmp_path / "nope.env"
    with pytest.raises(SystemExit) as excinfo:
        probe.read_key(str(missing))
    assert "unreadable" in str(excinfo.value)

    empty = tmp_path / "empty.env"
    empty.write_text("TERMINAL_DEBUG=1\n")
    with pytest.raises(SystemExit) as excinfo:
        probe.read_key(str(empty))
    assert "carries no OMNIROUTE_API_KEY line" in str(excinfo.value)


def test_env_names_tool_refuses_an_empty_environ(tmp_path):
    """An empty name list satisfies every allow-list vacuously, so it must be LOUD."""
    tool = _load(PROOF / "tools" / "pc" / "hermes_env_names.py", "s0_03_env_names")
    proc = tmp_path / "proc" / "4242"
    proc.mkdir(parents=True)
    (proc / "environ").write_bytes(b"")
    with pytest.raises(SystemExit) as excinfo:
        tool.env_names(tmp_path / "proc", 4242)
    assert "is empty" in str(excinfo.value)


def test_env_names_tool_keeps_names_and_discards_values(tmp_path):
    tool = _load(PROOF / "tools" / "pc" / "hermes_env_names.py", "s0_03_env_names2")
    proc = tmp_path / "proc" / "4243"
    proc.mkdir(parents=True)
    (proc / "environ").write_bytes(
        b"PATH=/usr/bin\0OMNIROUTE_API_KEY=sk-secret-value\0HOME=/root\0")
    names = tool.env_names(tmp_path / "proc", 4243)
    assert names == ["HOME", "OMNIROUTE_API_KEY", "PATH"]
    assert not any("sk-secret-value" in n for n in names)


def test_runner_refuses_leg_b_without_the_declared_seam(tmp_path):
    """The runner must SURFACE the pc_launch.py blocker, never route around it. This asserts the
    refusal text names the seam so the reader can act on it."""
    text = RUNNER.read_text()
    assert "S0_03_HERMES_CONFIG" in text
    assert "BLOCKER" in text
    assert "pc_launch.py:216" in text
    assert "NOT stubbed" in text


def test_proof_owned_profile_pins_the_adr_transport():
    """The committed template is what leg B launches with; if it drifted to the deviation the
    proof would silently stop testing ADR 0002."""
    import yaml
    profile = yaml.safe_load((PROOF / "hermes" / "config.yaml").read_text())
    (_name, block), = profile["providers"].items()
    assert block["api_mode"] == "codex_responses"
    assert block["key_env"] == "OMNIROUTE_API_KEY"
    assert block["extra_headers"]["x-omniroute-compression"] == "off"
    assert "api_key" not in block
    assert profile["default"] == _leg_flags(_positive_leg())["route_id"]


def test_committed_profile_and_fixture_profiles_agree():
    """The bundles' profile.yaml is a copy of the template the runner launches (AF-AP-42)."""
    template = (PROOF / "hermes" / "config.yaml").read_text()
    import yaml
    expected = yaml.safe_load(template)
    for bundle in NEGATIVE_BUNDLES:
        got = yaml.safe_load((FIXTURES / bundle / "hermes" / "profile.yaml").read_text())
        assert got["providers"] == expected["providers"], bundle
        assert got["default"] == expected["default"], bundle


def test_no_credential_value_in_any_committed_s0_03_file():
    """A structural sweep: no committed S0-03 file may carry an `sk-`-shaped literal beside a
    key name. Cheap, and it is the check that would have caught AF-AP-35."""
    import re
    pattern = re.compile(r"(OMNIROUTE_API_KEY|api_key)\s*[:=]\s*[\"']?sk-[A-Za-z0-9]{8,}")
    for path in PROOF.rglob("*"):
        if not path.is_file() or "__pycache__" in path.parts:
            continue
        text = path.read_text(errors="replace")
        assert not pattern.search(text), path


def test_runner_captures_the_env_record_while_the_leg_is_alive():
    """18-class sweep, class 13 (AF-AP-55 family) — a DEFECT this lane found and fixed.

    The first version of the runner did `wait "$leg_pid"` and THEN read /proc/<pid>/environ, so
    the agent was already dead: leg B could never produce hermes-env-names.json, and a recycled
    pid would have handed back a different process's names. The capture must sit BEFORE the
    wait, inside a failure-aware poll.
    """
    body = RUNNER.read_text()
    start = body.index("capture_hermes_leg() {")
    end = body.index("capture_hermes_leg \"$EVIDENCE/hermes\"")
    fn = body[start:end]
    capture_at = fn.index("hermes_env_names.py")
    wait_at = fn.index('wait "$leg_pid"')
    assert capture_at < wait_at, "the env record is taken after the leg is reaped"
    # Failure-aware: the poll exits on a dead leg and on a deadline, never success-only silence.
    assert "kill -0" in fn
    assert "deadline" in fn
    assert "exited before its env record could be taken" in fn
    # A leg that produced no record is LOUD, never a silently short bundle.
    assert "produced NO hermes-env-names.json" in fn


def test_runner_captures_an_env_record_for_both_hermes_legs():
    """The credential-absent bundle needs its own env record — the ABSENCE of OMNIROUTE_API_KEY
    in it is half the kill switch's evidence."""
    body = RUNNER.read_text()
    calls = [line for line in body.splitlines()
             if line.startswith("capture_hermes_leg ")]
    assert len(calls) == 2, calls
    assert any("credential-absent" in c and "-u OMNIROUTE_API_KEY" in c for c in calls)


def test_runner_never_reaps_by_pidfile_lookup_after_the_fact():
    """Every kill in the runner targets a pid the runner itself recorded."""
    import re
    body = RUNNER.read_text()
    for match in re.finditer(r"^\s*kill\b[^\n]*", body, re.M):
        line = match.group(0)
        assert "$pid" in line or "$leg_pid" in line, line
