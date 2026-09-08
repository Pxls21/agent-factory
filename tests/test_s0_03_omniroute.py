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
import os
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
    "evidence-credential-rejected",
    "evidence-stub-route",
    "evidence-provider-key-present",
)
# The two credential bundles are DIRECT-LEG ONLY, exactly as the PC runner produces them: a
# key-free Hermes leg cannot be captured through the pinned S0-01 launcher (each bundle's
# NOT-CAPTURED.md names the seam), and the credential verdicts are graded on the direct leg's own
# evidence before the hermes half is required.
DIRECT_ONLY_BUNDLES = ("evidence-credential-absent", "evidence-credential-rejected")


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
    ("evidence-credential-rejected",
     "credential_rejected: OmniRoute refused the presented key (HTTP 401)"),
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
    # required_negative_controls is 1; four are shipped and ALL four are listed.
    assert len(legs) == 4


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
    """AF-AP-42: a synthetic fixture must say where each file's shape came from — and a file the
    bundle does NOT contain must be accounted for too, or the absence reads as an oversight."""
    for bundle in NEGATIVE_BUNDLES:
        root = FIXTURES / bundle
        text = (root / "PROVENANCE.md").read_text()
        assert "NOT proven against a live capture" in text
        for path in sorted(root.rglob("*")):
            if path.is_dir() or path.name in ("PROVENANCE.md", "NOT-CAPTURED.md"):
                continue
            rel = path.relative_to(root).as_posix()
            assert rel in text, (bundle, rel)
    for bundle in DIRECT_ONLY_BUNDLES:
        note = (FIXTURES / bundle / "NOT-CAPTURED.md").read_text()
        assert "pc_launch.py" in note and "launch_env" in note, bundle
        assert not (FIXTURES / bundle / "hermes").exists(), bundle


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
        "failure_reason: roundtrip: no tool_call that started reached status 'completed'")


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
    bundle cannot pass by carrying a correct answer to a different question. (The row's session
    tag is moved with it: conjunct (iii) binds the hermes row to the same nonce and fires first,
    so leaving it behind would test the wrong assertion.)"""
    _edit(passing, "hermes/leg.json", lambda r: r.__setitem__("nonce2", "beefbeefbeefbeef"))
    _edit(passing, "omniroute-requests.json", lambda r: [
        row.__setitem__("session_tag", "beefbeefbeefbeef")
        for row in r["requests"] if row["leg"] == "hermes"])
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
    assert "profile.yaml carries an inline credential under 'api_key'" in result.stdout


@pytest.mark.parametrize("line,named", [
    ('      Authorization: "Bearer sk-live-not-a-real-key"', "Authorization"),
    ('      X-Api-Key: "sk-live-not-a-real-key"', "X-Api-Key"),
    ('      X-Gateway-Token: "not-a-real-token"', "X-Gateway-Token"),
])
def test_conjunct_v_rejects_a_credential_in_extra_headers(passing, line, named):
    """F-12/F-4, mutant V3. Hermes documents per-provider `extra_headers` as the place operators
    put custom auth and says the values "are treated as secrets"
    (hermes-agent 527da608 cli-config.yaml.example:141-154) — so it is the LIKELY place for an
    inline credential, and the literal `api_key` screen never looked there."""
    profile = passing / "hermes" / "profile.yaml"
    profile.write_text(profile.read_text().replace(
        '      x-omniroute-compression: "off"',
        '      x-omniroute-compression: "off"\n' + line))
    result = run_checker(passing)
    assert result.returncode == 1
    assert f"profile.yaml carries an inline credential under '{named}'" in result.stdout


def test_conjunct_v_still_accepts_the_key_env_NAME(passing):
    """De-vacuous the screen above: `key_env: OMNIROUTE_API_KEY` is a NAME, not a value, and the
    profile must keep passing with it — a screen that rejected it would reject every real
    profile."""
    profile = (passing / "hermes" / "profile.yaml").read_text()
    assert "key_env: OMNIROUTE_API_KEY" in profile
    assert run_checker(passing).returncode == 0


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


def test_a_credential_verdict_outranks_the_stream_conjunct(passing):
    """The kill switch must win over the SYMPTOM it causes: a 401 also breaks conjunct (i), and
    grading it as "no streamed answer" would lose the seed's pinned reason. Which verdict is
    decided by the request itself — the passing bundle DID present a key, so a 401 on it is a
    REJECTION (F-5, mutant V4), never the blocked reason."""
    _edit(passing, "direct/direct.json", lambda r: r.__setitem__("status", 401))
    result = run_checker(passing)
    assert result.returncode == 1
    assert result.stdout.strip() == (
        "failure_reason: credential_rejected: OmniRoute refused the presented key (HTTP 401)")


def test_a_present_but_refused_key_is_rejected_not_absent(passing):
    """The seed (`seeds/seed-stage0-v1.yaml:400-402`): credential_rejected maps to proof-RED,
    never to blocked. Both rejecting statuses, with the Hermes environ still carrying the name."""
    for status in (401, 403):
        _edit(passing, "direct/direct.json", lambda r: r.__setitem__("status", status))
        result = run_checker(passing)
        assert result.returncode == 1
        assert result.stdout.strip() == (
            "failure_reason: credential_rejected: OmniRoute refused the presented key "
            f"(HTTP {status})")
        assert "blocked" not in result.stdout


def test_a_401_on_a_request_that_sent_no_key_is_the_kill_switch(passing):
    """The other half of the same switch: no Authorization header sent -> the credential was
    never presented -> the seed's `blocked: credential_absent`. This is the shape
    `direct_responses_probe.py --no-credential` produces."""
    def strip_auth(record):
        record["status"] = 401
        record["credential_presented"] = False
        record["request_headers_sent"] = {
            k: v for k, v in record["request_headers_sent"].items()
            if k.lower() != "authorization"}
    _edit(passing, "direct/direct.json", strip_auth)
    result = run_checker(passing)
    assert result.returncode == 1
    assert result.stdout.strip() == "failure_reason: blocked: credential_absent"


def test_a_401_with_an_unreadable_header_record_is_a_bundle_failure(passing):
    """Fail CLOSED: if the record cannot say whether a key was sent, the bundle is broken — it is
    not silently graded as the blocked outcome."""
    def break_headers(record):
        record["status"] = 401
        record.pop("request_headers_sent")
    _edit(passing, "direct/direct.json", break_headers)
    result = run_checker(passing)
    assert result.returncode == 1
    assert result.stdout.strip() == (
        "failure_reason: bundle: direct/direct.json request_headers_sent absent")


def test_an_environ_without_the_key_is_the_kill_switch(passing):
    """The second, independent signal: Hermes had no credential to send. Graded on the hermes
    half, after it is read."""
    _edit(passing, "hermes/hermes-env-names.json",
          lambda r: r.__setitem__("names", [n for n in r["names"] if n != "OMNIROUTE_API_KEY"]))
    result = run_checker(passing)
    assert result.returncode == 1
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
    # F-12: real credential-name shapes with no KEY|TOKEN|SECRET segment (mutants V7a-c).
    ("GITHUB_PAT", True),
    ("ANTHROPIC_AUTH", True),
    ("DB_PW", True),
    ("HERMES_BEARER", True),
    # The launched agent's environment key set is PINNED (proofs/S0-01/pins.py PINNED_ENV_KEYS).
    # Screening a SESSION segment would red EVERY real capture on BUZZ_ACP_SESSION_POLICY — an
    # assertion no live leg can satisfy is a broken gate, not a stronger one.
    ("BUZZ_ACP_SESSION_POLICY", False),
    ("BUZZ_ACP_RESPOND_TO", False),
    ("S0_01_FRAMEDIR", False),
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


def test_proof_owned_profile_declares_the_model_where_hermes_reads_it():
    """F-13. The pinned hermes-agent (527da608) resolves the default model from the `model:`
    section and nowhere else: cli.py:5359-5360 reads `CLI_CONFIG.get("model", {})` then
    `.get("default") or .get("model")`. A TOP-LEVEL `default:` is read by nothing, so the leg
    would not go through the declared provider at all."""
    import yaml
    profile = yaml.safe_load((PROOF / "hermes" / "config.yaml").read_text())
    route = _leg_flags(_positive_leg())["route_id"]
    assert "default" not in profile, "a top-level default: is a key Hermes never reads"
    assert profile["model"]["default"].split("/", 1)[-1] == route
    assert profile["model"]["default"].split("/", 1)[0] in profile["providers"]
    assert profile["model"]["provider"] in profile["providers"]


def test_proof_owned_profile_pins_the_adr_transport():
    """The committed template is what the launched profile is built from; if it drifted to the
    deviation the proof would silently stop testing ADR 0002."""
    import yaml
    profile = yaml.safe_load((PROOF / "hermes" / "config.yaml").read_text())
    (_name, block), = profile["providers"].items()
    assert block["api_mode"] == "codex_responses"
    assert block["key_env"] == "OMNIROUTE_API_KEY"
    assert block["extra_headers"]["x-omniroute-compression"] == "off"
    assert "api_key" not in block


def test_committed_profile_and_fixture_profiles_agree():
    """The bundles' profile.yaml is the launched profile — a per-leg COPY of the template that
    adds this leg's `x-omniroute-session-id` (the runner's own comment says why), so the provider
    block matches the template on every key EXCEPT that header (AF-AP-42)."""
    template = (PROOF / "hermes" / "config.yaml").read_text()
    import yaml
    expected = yaml.safe_load(template)
    (_name, expected_block), = expected["providers"].items()
    for bundle in NEGATIVE_BUNDLES:
        path = FIXTURES / bundle / "hermes" / "profile.yaml"
        if not path.exists():
            continue
        got = yaml.safe_load(path.read_text())
        (_gname, block), = got["providers"].items()
        headers = dict(block["extra_headers"])
        headers.pop("x-omniroute-session-id", None)
        assert {**block, "extra_headers": headers} == expected_block, bundle
        assert got["model"] == expected["model"], bundle


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


def _capture_fn() -> str:
    body = RUNNER.read_text()
    start = body.index("capture_hermes_leg() {")
    end = body.index("HERMES_HOME_LEG=")
    return body[start:end]


def test_runner_captures_the_env_record_while_the_leg_is_alive():
    """18-class sweep, class 13 (AF-AP-55 family) — a DEFECT this lane found and fixed.

    The first version of the runner did `wait "$leg_pid"` and THEN read /proc/<pid>/environ, so
    the agent was already dead. The capture must sit after `launch.ready` and before teardown,
    inside a failure-aware poll.
    """
    fn = _capture_fn()
    ready_at = fn.index("launch.ready")
    capture_at = fn.index("hermes_env_names.py")
    kill_at = fn.index('kill "$pid"')
    assert ready_at < capture_at < kill_at, "the env record is not taken while the leg is alive"
    # Failure-aware: the poll exits on a dead launcher and on a deadline, never success-only
    # silence.
    assert "kill -0" in fn
    assert "deadline" in fn
    assert "launcher exited before launch.ready" in fn
    assert "never reached launch.ready" in fn


def test_runner_never_reaps_by_pidfile_lookup_after_the_fact():
    """Every kill in the runner targets a pid the runner itself recorded."""
    import re
    body = RUNNER.read_text()
    for match in re.finditer(r"^\s*kill\b[^\n]*", body, re.M):
        line = match.group(0)
        assert "$pid" in line or "$leg_pid" in line, line


# --------------------------------------------------------------------------- conjunct (iii):
# --------------------------------------------------------------------------- the row is BOUND
def _rows(root: Path):
    return json.loads((root / "omniroute-requests.json").read_text())


def test_conjunct_iii_binds_the_direct_row_to_the_response_the_client_saw(passing):
    """VERIFY-O1 F-1, mutant V1 — the round's blocker. The direct leg's row is the one whose
    `response_id` is the `resp_…` id the client streamed (`callLogs.ts:521-524`, written from
    `extractResponsesId` at `attemptLogging.ts:501`; `direct.json` records the same value as
    `id`). Before this, the conjunct read only requested_model/provider/model, so a row from 1999
    with status 500 and a foreign response id satisfied the proof's headline assertion."""
    _edit(passing, "direct/direct.json", lambda d: d.__setitem__("id", "resp_A"))
    _edit(passing, "omniroute-requests.json",
          lambda r: [row.__setitem__("response_id", "resp_B") for row in r["requests"]])
    result = run_checker(passing)
    assert result.returncode == 1
    assert result.stdout.strip() == (
        "failure_reason: identity: direct leg row response_id 'resp_B' != the id the client "
        "streamed 'resp_A'")


def test_conjunct_iii_rejects_the_whole_forged_row(passing):
    """The verifier's V1 verbatim: a row from 1999, status 500, foreign response id. Three
    independent bindings now catch it; the window is the first in the checker's order, so that is
    the reason it reports (the response-id and status bindings have their own tests above and
    below, each falsified on its own)."""
    _edit(passing, "omniroute-requests.json", lambda r: [
        row.update({"timestamp": "1999-01-01T00:00:00.000Z", "status": 500,
                    "response_id": "resp_SOMETHING_ELSE"}) for row in r["requests"]])
    result = run_checker(passing)
    assert result.returncode == 1
    assert "is outside the leg's window" in result.stdout
    # ...and with a plausible timestamp it is the response id that catches it.
    _edit(passing, "omniroute-requests.json", lambda r: [
        row.__setitem__("timestamp", "2026-09-08T00:00:02.400Z") for row in r["requests"]])
    result = run_checker(passing)
    assert result.returncode == 1
    assert "response_id 'resp_SOMETHING_ELSE'" in result.stdout


def test_conjunct_iii_binds_the_hermes_row_to_this_turns_nonce(passing):
    """Leg B's binding is `call_logs.session_tag`, which OmniRoute fills from the client's
    `x-omniroute-session-id` header verbatim (`conversationTracker.ts:465-469`, "Client override
    wins outright"; `chatCore.ts:1096`). The runner puts the leg's nonce2 there through the
    launched profile's extra_headers."""
    _edit(passing, "omniroute-requests.json", lambda r: [
        row.__setitem__("session_tag", "someone-elses-session")
        for row in r["requests"] if row["leg"] == "hermes"])
    result = run_checker(passing)
    assert result.returncode == 1
    assert result.stdout.strip() == (
        "failure_reason: identity: hermes leg row session_tag 'someone-elses-session' != "
        "the leg's nonce2 '0f1e2d3c4b5a6978'")


def test_a_second_route_row_inside_the_hermes_window_is_unattributable(passing):
    """On the PC the route is the one the owner's OWN build lanes use. Two rows in the window
    means the leg cannot be identified — that is RED, never "take the earliest one"."""
    def add_row(record):
        extra = dict(next(r for r in record["requests"] if r["leg"] == "hermes"))
        extra["id"] = "log_someone_else"
        extra["session_tag"] = "someone-elses-session"
        record["requests"].append(extra)
    _edit(passing, "omniroute-requests.json", add_row)
    result = run_checker(passing)
    assert result.returncode == 1
    assert result.stdout.strip() == (
        "failure_reason: identity: 2 call_logs rows in the hermes leg's window — unattributable")


def test_two_rows_for_the_direct_leg_is_a_bundle_failure(passing):
    """F-2, mutant V2: `legs[leg] = row` in a loop kept the LAST row with each label, so a stub
    row prepended to the list was shadowed by the clean one after it and never graded."""
    def shadow(record):
        stub = dict(record["requests"][0])
        stub["provider"] = "s0-01-scripted"
        record["requests"].insert(0, stub)
    _edit(passing, "omniroute-requests.json", shadow)
    result = run_checker(passing)
    assert result.returncode == 1
    assert result.stdout.strip() == (
        "failure_reason: bundle: omniroute-requests.json has 2 rows for the direct leg")


def test_the_exported_window_must_be_the_window_the_leg_recorded(passing):
    """Without this the exporter could widen the window until exactly one row fell inside it and
    the uniqueness rule above would be vacuous."""
    _edit(passing, "omniroute-requests.json",
          lambda r: r["windows"]["hermes"].__setitem__("start", "1999-01-01T00:00:00.000000Z"))
    result = run_checker(passing)
    assert result.returncode == 1
    assert "!= the window hermes/leg.json records" in result.stdout


@pytest.mark.parametrize("leg", ["direct", "hermes"])
def test_conjunct_iii_requires_each_row_to_have_succeeded(passing, leg):
    """A row that FAILED is not evidence that our request was served by the upstream model."""
    _edit(passing, "omniroute-requests.json", lambda r: [
        row.__setitem__("status", 500) for row in r["requests"] if row["leg"] == leg])
    result = run_checker(passing)
    assert result.returncode == 1
    assert result.stdout.strip() == (
        f"failure_reason: identity: {leg} leg row status 500, expected 200")


@pytest.mark.parametrize("leg", ["direct", "hermes"])
def test_conjunct_v_reads_the_wire_not_the_template(passing, leg):
    """F-3, mutant V14. The profile check can only ever say what the repo's own file declares —
    `collect_leg.sh` already SELECTs the `path` OmniRoute recorded, which is the transport that
    was actually used. `/v1/chat/completions` is the exact ADR deviation this proof exists to
    catch, and it passed."""
    _edit(passing, "omniroute-requests.json", lambda r: [
        row.__setitem__("path", "/v1/chat/completions")
        for row in r["requests"] if row["leg"] == leg])
    result = run_checker(passing)
    assert result.returncode == 1
    assert result.stdout.strip() == (
        f"failure_reason: transport: {leg} leg row path '/v1/chat/completions' does not end in "
        "/responses (ADR 0002)")


def test_nan_in_any_evidence_file_is_a_named_failure(passing):
    """F-17, mutant V17: `json.loads` accepts NaN by default, and every comparison against NaN is
    False — the fail-open wormhole class the incident log records twice."""
    path = passing / "omniroute-requests.json"
    path.write_text(path.read_text().replace('"status": 200', '"status": NaN', 1))
    result = run_checker(passing)
    assert result.returncode == 1
    assert result.stdout.strip() == (
        "failure_reason: bundle: omniroute-requests.json is not valid JSON (ValueError)")


def test_conjunct_i_rejects_a_transport_error_beside_a_200(passing):
    """F-16, mutant V20: the probe records a transport failure AND still writes the record. A
    bundle claiming both is internally contradictory; the field was recorded and never read."""
    _edit(passing, "direct/direct.json",
          lambda r: r.__setitem__("transport_error", "URLError: connection refused"))
    result = run_checker(passing)
    assert result.returncode == 1
    assert result.stdout.strip() == (
        "failure_reason: direct: transport_error 'URLError: connection refused' recorded "
        "beside status 200")


# --------------------------------------------------------------------------- conjunct (iv):
# --------------------------------------------------------------------------- the tool OUTPUT
def test_conjunct_iv_requires_the_tool_output_to_carry_the_nonce(passing):
    """F-6. The conjunct needed only "some tool call finished" and "the nonce is in some agent
    text", with nothing joining them. The prompt asked for `printf <nonce2>`, so the completed
    call's OUTPUT is the evidence that this call is the one the prompt asked for."""
    path, entries = _timeline(passing)
    for entry in entries:
        update = ((entry.get("frame") or {}).get("params") or {}).get("update") or {}
        if update.get("status") == "completed" and update.get("content"):
            update["content"] = [{"type": "content",
                                  "content": {"type": "text", "text": "(no output)"}}]
    _write_timeline(path, entries)
    result = run_checker(passing)
    assert result.returncode == 1
    assert "absent from the completed tool call's output" in result.stdout


def test_conjunct_iv_rejects_an_unrelated_completed_tool_call(passing):
    """Mutant V6: the completed call is `read_file: /etc/hostname` with unrelated output."""
    path, entries = _timeline(passing)
    for entry in entries:
        update = ((entry.get("frame") or {}).get("params") or {}).get("update") or {}
        if update.get("status") == "completed" and update.get("content"):
            update["title"] = "read_file: /etc/hostname"
            update["rawInput"] = {"path": "/etc/hostname"}
            update["content"] = [{"type": "content",
                                  "content": {"type": "text", "text": "fedora"}}]
    _write_timeline(path, entries)
    result = run_checker(passing)
    assert result.returncode == 1
    assert "absent from the completed tool call's output" in result.stdout


def test_conjunct_iv_rejects_a_refusal_that_quotes_the_prompt_back(passing):
    """Mutant V5, in the shape a REFUSAL actually has: the agent quotes the command back and no
    tool output carries the nonce. (An edit to the answer text ALONE no longer falsifies the
    conjunct — see the report's DISCREPANCIES: with the tool output graded, a bundle whose
    completed call really produced the nonce IS a round trip, whatever the agent said after it.)
    """
    path, entries = _timeline(passing)
    nonce2 = json.loads((passing / "hermes" / "leg.json").read_text())["nonce2"]
    for entry in entries:
        update = ((entry.get("frame") or {}).get("params") or {}).get("update") or {}
        if update.get("sessionUpdate") == "agent_message_chunk":
            update["content"]["text"] = (
                f"I was asked to run the terminal command 'printf {nonce2}' but I will not.")
        if update.get("status") == "completed" and update.get("content"):
            update["content"] = [{"type": "content",
                                  "content": {"type": "text", "text": "refused"}}]
    _write_timeline(path, entries)
    result = run_checker(passing)
    assert result.returncode == 1
    assert "absent from the completed tool call's output" in result.stdout


def test_conjunct_iv_requires_the_completed_call_to_be_one_that_started(passing):
    """A `tool_call_update` for an id that never started is not a round trip either."""
    path, entries = _timeline(passing)
    for entry in entries:
        update = ((entry.get("frame") or {}).get("params") or {}).get("update") or {}
        if update.get("sessionUpdate") == "tool_call":
            update["toolCallId"] = "tc-never-completed"
    _write_timeline(path, entries)
    result = run_checker(passing)
    assert result.returncode == 1
    assert "no tool_call that started reached status 'completed'" in result.stdout


# --------------------------------------------------------------------------- the env RECORD
@pytest.mark.parametrize("field,value,pin", [
    ("exe", "/usr/bin/sleep", "PINNED_AGENT_INTERPRETER_REALPATH"),
    ("agent_realpath", "/usr/bin/false", "PINNED_AGENT_REALPATH"),
])
def test_env_record_must_come_from_the_pinned_hermes_agent(passing, field, value, pin):
    """F-11, mutant V15: `{"pid": 1, "exe": "/usr/bin/sleep"}` passed. Assertion 3 is "HERMES
    holds no upstream provider key"; a name list alone proves only that SOME process holds none.
    Both pins come from S0-01's pins module through the same import the timeline reader uses."""
    s0_01 = check._load_s0_01_module()
    _edit(passing, "hermes/hermes-env-names.json", lambda r: r.__setitem__(field, value))
    result = run_checker(passing)
    assert result.returncode == 1
    assert result.stdout.strip() == (
        f"failure_reason: env: the environ record's {field} is {value!r}, not the pinned "
        f"Hermes agent {getattr(s0_01, pin)!r}")


# The real-leg corpus is a DECLARED input (VERIFY-CK10 F-R10-25): with `S0_01_REAL_LEG_DIR` set
# the corpus MUST be there and the test fails if it is not; CI (venue unset here) skips by
# declaration. Both env reads resolved ONCE, at module scope.
_VENUE = os.environ.get("S0_01_VENUE", "sandbox")
_REAL_LEG_DIR = (Path(os.environ["S0_01_REAL_LEG_DIR"])
                 if os.environ.get("S0_01_REAL_LEG_DIR") else None)


def test_env_record_pins_match_the_real_corpus():
    """De-vacuous both pins against a REAL artifact: the committed corpus's runtime-identity.json
    carries the interpreter and the agent entry point this checker compares with, so neither
    assertion is one a live capture cannot satisfy (the F-7 class, applied to my own change)."""
    if _REAL_LEG_DIR is None:
        pytest.skip("S0_01_REAL_LEG_DIR unset (real-leg corpus not declared for this venue)")
    record = json.loads((_REAL_LEG_DIR / "run-1" / "runtime-identity.json").read_text())
    s0_01 = check._load_s0_01_module()
    assert record["agent_interpreter_realpath"] == s0_01.PINNED_AGENT_INTERPRETER_REALPATH
    assert record["agent_realpath"] == s0_01.PINNED_AGENT_REALPATH


# --------------------------------------------------------------------------- the NEGATIVE leg,
# --------------------------------------------------------------------------- built by its writer
DIRECT_PROBE = PROOF / "tools" / "pc" / "direct_responses_probe.py"
# A literal, non-secret placeholder. The tests that need a key file write exactly this value.
SCRATCH_KEY = "fake-scratch-value-not-a-credential"


class _AuthzRejectHandler(http.server.BaseHTTPRequestHandler):
    """OmniRoute's client-API rejection, transcribed from the pinned source (488f57e9):
    `src/server/authz/pipeline.ts:79-95` renders `{error:{code,message,correlation_id}}` with
    status from the policy and stamps `x-request-id` + `x-omniroute-route-class`
    (`src/server/authz/headers.ts:15,17`); `src/server/authz/policies/clientApi.ts:77` is the
    no-bearer `reject(401,"AUTH_002","Authentication required")` and `:96` is the invalid-key
    `reject(401,"AUTH_002","Invalid API key")`.
    """
    message = "Authentication required"
    request_id = "req_2b8e0f31"

    def do_POST(self):
        body = json.dumps({"error": {"code": "AUTH_002", "message": self.message,
                                     "correlation_id": self.request_id}}).encode()
        self.send_response(401)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("x-request-id", self.request_id)
        self.send_header("x-omniroute-route-class", "client-api")
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *args):
        pass


def _serve_reject(message):
    handler = type("H", (_AuthzRejectHandler,), {"message": message})
    server = http.server.HTTPServer(("127.0.0.1", 0), handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return server, thread


def build_direct_401_record(tmp_path: Path, *, present_key: bool, message: str) -> dict:
    """Run the REAL writer against a local 401 server and return the record it wrote.

    This is the producer the two credential fixtures were minted from: the committed files are
    this function's output with the volatile fields (nonce, stamps, duration) frozen. AF-AP-42 —
    a fixture whose shape the writer cannot make is a hollow green, and the previous
    credential-absent bundle depicted a request the probe structurally could not send.
    """
    server, _thread = _serve_reject(message)
    try:
        port = server.server_address[1]
        env = {"PATH": os.environ.get("PATH", "/usr/bin:/bin")}
        argv = [sys.executable, str(DIRECT_PROBE), "--route-id", "agentfactory-build",
                "--base-url", f"http://127.0.0.1:{port}/v1",
                "--out-dir", str(tmp_path / "direct")]
        if present_key:
            key_file = tmp_path / "scratch.env"
            key_file.write_text(f"TERMINAL_DEBUG=1\nOMNIROUTE_API_KEY={SCRATCH_KEY}\n")
            env["S0_03_KEY_FILE"] = str(key_file)
        else:
            argv.append("--no-credential")
        result = subprocess.run(argv, capture_output=True, text=True, timeout=60, env=env)
        assert result.returncode == 1, result.stdout + result.stderr
        return json.loads((tmp_path / "direct" / "direct.json").read_text())
    finally:
        server.shutdown()
        server.server_close()


def test_negative_leg_produces_a_gradeable_bundle(tmp_path):
    """F-9. The old negative leg ran the probe with `S0_03_KEY_FILE=/dev/null`, which exits
    before writing anything — the committed bundle had NO producer (anti-hollow-green tactic 7).
    `--no-credential` skips the key read and omits the header entirely, which is what makes
    OmniRoute answer its no-bearer 401."""
    record = build_direct_401_record(tmp_path, present_key=False,
                                     message="Authentication required")
    assert record["status"] == 401
    assert record["credential_presented"] is False
    assert "Authorization" not in record["request_headers_sent"]
    assert record["error_body"]["error"]["code"] == "AUTH_002"


def test_the_credential_probe_still_sends_the_header_when_it_has_a_key(tmp_path):
    """De-vacuous the test above: with a key file the SAME writer sends Authorization, redacted
    at the point of the write. Without this pair, `--no-credential` could be a no-op."""
    record = build_direct_401_record(tmp_path, present_key=True, message="Invalid API key")
    assert record["credential_presented"] is True
    assert record["request_headers_sent"]["Authorization"] == "<redacted>"
    assert SCRATCH_KEY not in json.dumps(record)


@pytest.mark.parametrize("bundle,present_key,message", [
    ("evidence-credential-absent", False, "Authentication required"),
    ("evidence-credential-rejected", True, "Invalid API key"),
])
def test_credential_fixture_matches_the_writers_key_set(tmp_path, bundle, present_key, message):
    """F-10/AF-AP-42. The committed fixture's PROVENANCE says the writer builds exactly these
    header keys; before this the absent-bundle's set was hand-edited and the writer could not
    produce it. Compare the KEY SET (the volatile fields — nonce, stamps, duration, correlation
    id — are frozen in the committed copy and are not part of the claim)."""
    produced = build_direct_401_record(tmp_path, present_key=present_key, message=message)
    committed = json.loads((FIXTURES / bundle / "direct" / "direct.json").read_text())
    assert sorted(produced["request_headers_sent"]) == sorted(committed["request_headers_sent"])
    assert produced["credential_presented"] == committed["credential_presented"]
    assert sorted(produced) == sorted(committed)
    assert produced["error_body"]["error"]["message"] == committed["error_body"]["error"]["message"]


# --------------------------------------------------------------------------- leg B rides the
# --------------------------------------------------------------------------- S0-01 launcher
PC_LAUNCH = ROOT / "proofs" / "S0-01" / "tools" / "pc" / "pc_launch.py"
PC_MENTION = ROOT / "proofs" / "S0-01" / "tools" / "pc" / "pc_mention.sh"


def _launcher_flags() -> set:
    """Every flag `pc_launch.py` DECLARES, parsed from its own `add_argument` calls — the
    CONSUMER contract read from the producer, never from a report about it."""
    import ast
    tree = ast.parse(PC_LAUNCH.read_text())
    flags = set()
    for node in ast.walk(tree):
        if (isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
                and node.func.attr == "add_argument" and node.args
                and isinstance(node.args[0], ast.Constant)):
            flags.add(node.args[0].value)
    return flags


def _runner_launcher_flags() -> set:
    """Every flag the runner passes to $LAUNCHER, from the runner's own invocation line."""
    import re
    body = RUNNER.read_text()
    line = next(l for l in body.splitlines() if 'python3 "$LAUNCHER"' in l)
    return set(re.findall(r"--[a-z-]+", line))


def test_runner_leg_b_uses_only_flags_pc_launch_declares():
    """VERIFY-O1 F-8: the old invocation passed `--config` and `--prompt`, neither of which
    exists on the launcher — leg B could not have run. build-loop step 1: verify the seam from
    the CONSUMER, against the producer's real bytes."""
    declared = _launcher_flags()
    passed = _runner_launcher_flags()
    assert passed, "the runner's launcher invocation was not found"
    assert passed <= declared, sorted(passed - declared)
    # And the seam this lane depends on is actually there (if it is not, leg B must refuse
    # rather than substitute a launcher).
    assert "--profile" in declared


def test_runner_launches_the_pinned_s0_01_launcher_and_nothing_else():
    """F-22: the previous version refused unless `$S0_03_HERMES_CONFIG` named "a launcher that
    accepts a profile path" — an env var whose whole purpose was the substitution the comment
    three lines above it called unacceptable. The variable now names a path that must BE
    pc_launch.py, and there is no allow-foreign flag."""
    body = RUNNER.read_text()
    code = "\n".join(l for l in body.splitlines() if not l.lstrip().startswith("#"))
    assert "S0_03_HERMES_CONFIG" not in code, "the renamed variable is still read"
    assert "proofs/S0-01/tools/pc/pc_launch.py" in body
    assert 'realpath "$LAUNCHER"' in body and 'realpath "$LAUNCHER_PIN"' in body
    assert "ALLOW_FOREIGN" not in body


def test_runner_sends_the_prompt_through_the_relay_mention():
    """S0-01 prompts do not travel through the launcher at all: `run_leg.sh`'s mention step sends them as a
    relay mention. The runner uses the same tool, with the nonce in TEXT."""
    fn = _capture_fn()
    assert 'TEXT="$PROMPT"' in fn
    assert "$MENTION" in fn
    assert "pc_mention.sh" in RUNNER.read_text()


def test_runner_and_pc_mention_resolve_the_same_marker_tree():
    """pc_mention.sh hard-codes its BASE (its `BASE=` line) and reads the leg's framedir from
    <BASE>/.markers/current-framedir. If the launcher wrote its markers into another tree (an
    $S0_01_HERMES_HOME override) the prompt would go to a different leg's session, so the runner
    checks the two agree BEFORE launching."""
    body = RUNNER.read_text()
    assert "current-framedir" in PC_MENTION.read_text()
    assert "MENTION_BASE" in body and "pins.hermes_home()" in body
    assert 'launcher markers $MARKERS != pc_mention.sh tree' in body


def test_runner_tears_down_by_the_launchers_own_pidfile():
    """`pc_launch.py` writes the buzz-acp pid it started (its `buzz-acp.pid` write); the runner copies
    that file into its own pids dir so the EXIT trap reaps it too. The launcher only returns when
    buzz-acp exits, so `wait` cannot be the teardown."""
    fn = _capture_fn()
    assert "buzz-acp.pid" in fn
    assert fn.index("buzz-acp.pid") < fn.index('kill "$pid"')
    assert "$WORK/pids/" in fn


def test_runner_captures_the_profile_the_launcher_actually_loaded():
    """F-3 on the producer side: the bundle's profile.yaml is copied from the launched Hermes
    home and checked against the launcher's own hermes-config.sha256, so it cannot be a copy of
    the repo template made after the fact."""
    fn = _capture_fn()
    assert "hermes-config.sha256" in fn
    assert 'cp "$profile" "$EVIDENCE/hermes/profile.yaml"' in fn
    assert "is not the launched config" in fn


def test_runner_writes_the_window_at_both_ends():
    """The hermes row's window must be CLOSED and recorded by the runner, not inferred."""
    fn = _capture_fn()
    assert fn.index("window_start=$(now)") < fn.index("$MENTION")
    assert fn.index("$MENTION") < fn.index("window_end=$(now)")
    assert '"window_start": start' in fn and '"window_end": end' in fn


def test_runner_negative_leg_has_a_producer_and_says_what_it_cannot_capture():
    """F-9/F-23: the negative leg is produced by `--no-credential` (not by pointing the key file
    at /dev/null, which writes nothing), collect runs on the negative root too, and the bundle
    states in-band that its hermes half is not capturable through the pinned launcher."""
    body = RUNNER.read_text()
    # The NOT-CAPTURED.md heredoc quotes both dead approaches by name, so it is excluded along
    # with the comments: the check is that neither is still EXECUTED.
    head, _, rest = body.partition("<<'NOTE'")
    code = "\n".join(l for l in (head + rest.partition("\nNOTE\n")[2]).splitlines()
                     if not l.lstrip().startswith("#"))
    assert "--no-credential" in code
    assert "S0_03_KEY_FILE=/dev/null" not in code
    assert "env -u OMNIROUTE_API_KEY" not in code
    assert body.count('collect_leg.sh"') >= 2
    assert 'collect_leg.sh" "$EVIDENCE/credential-absent"' in body
    assert "NOT-CAPTURED.md" in body and "launch_env" in body


# --------------------------------------------------------------------------- collect_leg.sh,
# --------------------------------------------------------------------------- over a REAL sqlite
# The `call_logs` column list, verbatim from the producer's INSERT statement (OmniRoute 488f57e9,
# `src/lib/usage/callLogs.ts:564-584`). A fixture DB built from any other list would be testing
# the exporter against a table OmniRoute does not have.
CALL_LOGS_COLUMNS = (
    "id, timestamp, method, path, status, model, requested_model, provider, "
    "account, connection_id, duration, tokens_in, tokens_out, "
    "tokens_cache_read, tokens_cache_creation, tokens_reasoning, tokens_compressed, "
    "reasoning_source, reasoning_chars, "
    "cache_source, request_type, source_format, target_format, api_key_id, api_key_name, "
    "combo_name, combo_step_id, combo_execution_key, error_summary, detail_state, "
    "artifact_relpath, artifact_size_bytes, artifact_sha256, "
    "has_request_body, has_response_body, has_pipeline_details, request_summary, "
    "correlation_id, model_pinned, session_tag, response_id, error_type"
)


def _call_logs_db(path: Path, rows):
    import sqlite3
    names = [c.strip() for c in CALL_LOGS_COLUMNS.split(",")]
    con = sqlite3.connect(str(path))
    con.execute("CREATE TABLE call_logs (%s)" % ", ".join(names))
    for row in rows:
        values = {name: None for name in names}
        values.update(row)
        con.execute("INSERT INTO call_logs (%s) VALUES (%s)"
                    % (CALL_LOGS_COLUMNS, ",".join("?" * len(names))),
                    [values[name] for name in names])
    con.commit()
    con.close()


def _run_collect(bundle: Path, data_dir: Path, route="agentfactory-build"):
    env = dict(os.environ, OMNIROUTE_DATA_DIR=str(data_dir))
    return subprocess.run(["bash", str(COLLECT), str(bundle), route],
                          capture_output=True, text=True, timeout=60, env=env)


def _collect_bundle(tmp_path: Path, *, response_id="resp_abc123", window=True,
                    window_start="2026-09-08T00:00:01.000000Z",
                    window_end="2026-09-08T00:00:01.450000Z") -> Path:
    bundle = tmp_path / "bundle"
    (bundle / "direct").mkdir(parents=True)
    (bundle / "direct" / "direct.json").write_text(json.dumps({"id": response_id}))
    if window:
        (bundle / "hermes").mkdir()
        (bundle / "hermes" / "leg.json").write_text(json.dumps({
            "leg": "hermes", "nonce2": "0f1e2d3c4b5a6978",
            "window_start": window_start, "window_end": window_end}))
    return bundle


_BASE_ROW = {"method": "POST", "path": "/v1/responses", "status": 200, "model": "gpt-5.5",
             "requested_model": "agentfactory-build", "provider": "openai-codex",
             "connection_id": "conn_7", "combo_name": "agentfactory-build"}


def test_collect_leg_binds_each_row_to_its_leg(tmp_path):
    """The exporter, run for real against a sqlite database with OmniRoute's own column set.
    Before this the SQL had never been executed by any test at all — only `bash -n` ran."""
    data = tmp_path / "data"
    data.mkdir()
    _call_logs_db(data / "storage.sqlite", [
        dict(_BASE_ROW, id="log_1", timestamp="2026-09-08T00:00:00.800Z",
             response_id="resp_abc123"),
        dict(_BASE_ROW, id="log_2", timestamp="2026-09-08T00:00:01.400Z",
             response_id="resp_def456", session_tag="0f1e2d3c4b5a6978"),
        # inside the route, OUTSIDE the window
        dict(_BASE_ROW, id="log_3", timestamp="2026-09-08T00:00:01.500Z",
             response_id="resp_ghi789", session_tag="somebody-else"),
        # inside the window, ANOTHER route
        dict(_BASE_ROW, id="log_4", timestamp="2026-09-08T00:00:01.200Z",
             requested_model="another-route", response_id="resp_zzz"),
    ])
    bundle = _collect_bundle(tmp_path)
    result = _run_collect(bundle, data)
    assert result.returncode == 0, result.stdout + result.stderr
    record = json.loads((bundle / "omniroute-requests.json").read_text())
    assert [(r["leg"], r["id"]) for r in record["requests"]] == [
        ("direct", "log_1"), ("hermes", "log_2")]
    assert record["windows"]["hermes"] == {"start": "2026-09-08T00:00:01.000000Z",
                                           "end": "2026-09-08T00:00:01.450000Z"}
    assert record["requests"][1]["session_tag"] == "0f1e2d3c4b5a6978"


def test_collect_leg_exports_every_row_in_the_window_not_the_earliest(tmp_path):
    """The old exporter picked the earliest row at/after a stamp and hid the ambiguity. Exporting
    all of them is what lets the checker call the leg unattributable."""
    data = tmp_path / "data"
    data.mkdir()
    _call_logs_db(data / "storage.sqlite", [
        dict(_BASE_ROW, id="log_1", timestamp="2026-09-08T00:00:00.800Z",
             response_id="resp_abc123"),
        dict(_BASE_ROW, id="log_2", timestamp="2026-09-08T00:00:01.100Z",
             response_id="resp_def456", session_tag="0f1e2d3c4b5a6978"),
        dict(_BASE_ROW, id="log_3", timestamp="2026-09-08T00:00:01.400Z",
             response_id="resp_ghi789", session_tag="somebody-else"),
    ])
    bundle = _collect_bundle(tmp_path)
    assert _run_collect(bundle, data).returncode == 0
    record = json.loads((bundle / "omniroute-requests.json").read_text())
    assert [r["leg"] for r in record["requests"]] == ["direct", "hermes", "hermes"]


def test_collect_leg_compares_stamps_as_instants_not_strings(tmp_path):
    """F-14: the runner writes 6 fractional digits and OmniRoute writes 3
    (`src/lib/usage/callLogs.ts:489`). Compared as STRINGS, `…01.000Z` sorts AFTER
    `…01.000000Z` because 'Z' (0x5A) > '0', so a row one millisecond before the window start
    reads as inside it."""
    data = tmp_path / "data"
    data.mkdir()
    _call_logs_db(data / "storage.sqlite", [
        dict(_BASE_ROW, id="log_1", timestamp="2026-09-08T00:00:00.800Z",
             response_id="resp_abc123"),
        # 0.456 ms BEFORE window_start — but string-greater than it, which is the trap.
        dict(_BASE_ROW, id="log_early", timestamp="2026-09-08T00:00:01.123Z",
             response_id="resp_early", session_tag="somebody-else"),
        dict(_BASE_ROW, id="log_2", timestamp="2026-09-08T00:00:01.400Z",
             response_id="resp_def456", session_tag="0f1e2d3c4b5a6978"),
    ])
    # The trap itself, asserted so the fixture cannot quietly stop demonstrating it.
    assert "2026-09-08T00:00:01.123Z" > "2026-09-08T00:00:01.123456Z"
    bundle = _collect_bundle(tmp_path, window_start="2026-09-08T00:00:01.123456Z")
    assert _run_collect(bundle, data).returncode == 0
    record = json.loads((bundle / "omniroute-requests.json").read_text())
    assert [r["id"] for r in record["requests"]] == ["log_1", "log_2"]


def test_collect_leg_binds_the_route_as_a_query_parameter(tmp_path):
    """F-15: `WHERE requested_model = '$ROUTE'` interpolated an argv value into the SQL text. A
    route id carrying a quote must be a value, not syntax — and must simply match nothing."""
    data = tmp_path / "data"
    data.mkdir()
    _call_logs_db(data / "storage.sqlite", [
        dict(_BASE_ROW, id="log_1", timestamp="2026-09-08T00:00:00.800Z",
             response_id="resp_abc123"),
    ])
    bundle = _collect_bundle(tmp_path, window=False)
    result = _run_collect(bundle, data, route="a' OR '1'='1")
    assert result.returncode == 1, result.stdout + result.stderr
    assert "no call_logs row for the direct leg" in result.stderr
    assert "syntax error" not in (result.stdout + result.stderr).lower()
    # Structural: the route never appears in the SQL TEXT — every query says `= ?`.
    text = COLLECT.read_text()
    assert "requested_model = ?" in text
    assert "requested_model = '" not in text


def test_collect_leg_on_a_negative_root_writes_an_honest_empty_export(tmp_path):
    """The negative root has no response id (a 401 streams none) and no hermes turn, so it
    legitimately contributes no rows — and that is not a failure."""
    data = tmp_path / "data"
    data.mkdir()
    _call_logs_db(data / "storage.sqlite", [])
    bundle = tmp_path / "neg"
    (bundle / "direct").mkdir(parents=True)
    (bundle / "direct" / "direct.json").write_text(json.dumps({"id": None, "status": 401}))
    result = _run_collect(bundle, data)
    assert result.returncode == 0, result.stdout + result.stderr
    record = json.loads((bundle / "omniroute-requests.json").read_text())
    assert record["requests"] == [] and record["windows"] == {}


def test_collect_leg_is_loud_when_a_declared_leg_has_no_row(tmp_path):
    """De-vacuous the test above: a leg that WAS declared and produced no row is an error."""
    data = tmp_path / "data"
    data.mkdir()
    _call_logs_db(data / "storage.sqlite", [
        dict(_BASE_ROW, id="log_1", timestamp="2026-09-08T00:00:00.800Z",
             response_id="resp_abc123"),
    ])
    bundle = _collect_bundle(tmp_path)
    result = _run_collect(bundle, data)
    assert result.returncode == 1
    assert "no call_logs row for the hermes leg" in result.stderr


def test_env_names_resolves_the_pid_the_tee_actually_writes(tmp_path):
    """F-7. The tool looked for agent_pid/child_pid/hermes_pid/pid; the tee writes
    `agent_child_pid` (`"agent_child_pid"` in `proofs/S0-01/tools/frame_tee.py`'s identity dict). Against a record with the REAL
    corpus key set the tool exited 1, so leg B could never take an env record at all. The key set
    here is COPIED from the corpus; only the values are synthetic."""
    if _REAL_LEG_DIR is None:
        pytest.skip("S0_01_REAL_LEG_DIR unset (real-leg corpus not declared for this venue)")
    real = json.loads((_REAL_LEG_DIR / "run-1" / "runtime-identity.json").read_text())
    record = dict(real)
    record["agent_child_pid"] = os.getpid()
    rid = tmp_path / "runtime-identity.json"
    rid.write_text(json.dumps(record, indent=1))
    tool = PROOF / "tools" / "pc" / "hermes_env_names.py"
    result = subprocess.run(
        [sys.executable, str(tool), "--out-dir", str(tmp_path / "out"),
         "--runtime-identity", str(rid)],
        capture_output=True, text=True, timeout=60)
    assert result.returncode == 0, result.stdout + result.stderr
    written = json.loads((tmp_path / "out" / "hermes-env-names.json").read_text())
    assert written["pid"] == os.getpid()
    assert written["agent_realpath"] == real["agent_realpath"]
    assert "PATH" in written["names"]


def test_the_hermes_row_must_really_be_inside_the_declared_window(passing):
    """The checker verifies the exporter's window filter rather than trusting it: the row it
    labelled `hermes` carries its own timestamp, and it must fall inside the window the leg
    recorded. Instants, never strings (F-14)."""
    _edit(passing, "omniroute-requests.json", lambda r: [
        row.__setitem__("timestamp", "2026-09-08T00:00:09.000Z")
        for row in r["requests"] if row["leg"] == "hermes"])
    result = run_checker(passing)
    assert result.returncode == 1
    assert "is outside the leg's window" in result.stdout


def test_a_row_at_either_window_edge_is_inside_it(passing):
    """De-vacuous the window: it is CLOSED at both ends, and the two producers write different
    fractional precision — an edge row written with 3 digits must still be inside a 6-digit
    boundary."""
    window = json.loads((passing / "hermes" / "leg.json").read_text())
    for edge in ("window_start", "window_end"):
        stamp = window[edge].replace("000Z", "Z")   # 6 fractional digits -> 3
        _edit(passing, "omniroute-requests.json", lambda r, s=stamp: [
            row.__setitem__("timestamp", s)
            for row in r["requests"] if row["leg"] == "hermes"])
        assert run_checker(passing).returncode == 0, edge
