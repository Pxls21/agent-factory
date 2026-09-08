"""S0-04 compression contract — deterministic, LLM-free tests for the checker, the fixtures and
the PC-side capture tool.

Every hostile bundle is a COPY under the test's tmp_path; the tracked fixtures are only ever
read (AF-AP-42: the real-bundle CLI test runs unpatched against the committed bundle).
`test_record_shape_is_the_current_producer_shape` pins the checker's reading of the S0-01
scripted backend to a record produced by RUNNING that backend, so a change to the instrument's
record shape breaks here instead of silently at capture time on the PC.
"""
from __future__ import annotations

import base64
import http.client
import json
import os
import shutil
import socket
import subprocess
import sys
import time
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
CHECKER = ROOT / "proofs" / "S0-04" / "check_compression.py"
CAPTURE = ROOT / "proofs" / "S0-04" / "tools" / "pc" / "capture_leg.py"
RUNNER = ROOT / "proofs" / "S0-04" / "tools" / "pc" / "run_s0_04_legs.sh"
SPEC = ROOT / "proofs" / "S0-04" / "spec.json"
FIXTURES = ROOT / "proofs" / "S0-04" / "fixtures"
PASS_BUNDLE = FIXTURES / "evidence-pass"
BACKEND = ROOT / "proofs" / "S0-01" / "tools" / "scripted_backend.py"

PASS_LINE = "PASS: S0-04 compression-contract - 3 assertions over 3 legs"
TOKEN = "s0-04-test-upstream-token-0123456789"

# The record keys the checker reads. Pinned from a RUN of the real producer; a change to
# scripted_backend.State.record breaks this test, not the PC capture.
RECORD_KEYS = {"authorization_fingerprint", "body", "headers", "method", "path",
               "received_at", "remote_addr", "seq", "t_mono_ns"}


# --------------------------------------------------------------------------- helpers
def run_checker(root, fixtures_dir=None):
    argv = [sys.executable, str(CHECKER)]
    if fixtures_dir is not None:
        argv += ["--fixtures-dir", str(fixtures_dir)]
    argv.append(str(root))
    proc = subprocess.run(argv, capture_output=True, text=True, timeout=180, cwd=str(ROOT))
    return proc.returncode, proc.stdout + proc.stderr


def bundle(tmp_path, name="b"):
    """A fresh writable copy of the committed passing bundle."""
    dst = tmp_path / name
    shutil.copytree(PASS_BUNDLE, dst)
    return dst


def load(path):
    return json.loads(Path(path).read_text())


def store(path, obj):
    Path(path).write_text(json.dumps(obj, indent=2, sort_keys=True) + "\n")


def free_port():
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        return sock.getsockname()[1]


# --------------------------------------------------------------------------- positive
def test_committed_bundle_passes_unpatched():
    """The real CLI over the tracked bundle and the tracked fixtures — no flags, no patching."""
    code, out = run_checker(PASS_BUNDLE)
    assert code == 0, out
    assert PASS_LINE in out, out


def test_pass_line_is_exact():
    code, out = run_checker(PASS_BUNDLE)
    assert code == 0
    assert out.strip().splitlines()[-1] == PASS_LINE


def test_observations_are_recorded_not_asserted():
    code, out = run_checker(PASS_BUNDLE)
    assert code == 0
    assert "observation: config api_mode = chat_completions" in out
    assert out.count("observation:") == 3


def test_bundle_is_deterministic_run_twice():
    first = run_checker(PASS_BUNDLE)
    second = run_checker(PASS_BUNDLE)
    assert first == second


# --------------------------------------------------------------------------- mutants
def test_mutant_header_absent_accepted(tmp_path):
    """HEADER-ABSENT-ACCEPTED — the pinned negative control, exact reason."""
    code, out = run_checker(FIXTURES / "evidence-header-missing")
    assert code == 1, out
    assert "failure_reason: off: compression-header-missing" in out, out


def test_mutant_header_value_on_accepted(tmp_path):
    """HEADER-VALUE-ON-ACCEPTED — presence is not a value (AF-AP-38)."""
    b = bundle(tmp_path)
    path = b / "off" / "response.json"
    obj = load(path)
    obj["headers"] = [["X-OmniRoute-Compression", "on"] if h[0].lower() == "x-omniroute-compression"
                      else h for h in obj["headers"]]
    store(path, obj)
    code, out = run_checker(b)
    assert code == 1, out
    assert "failure_reason: off: compression-header-value: on" in out, out


def test_mutant_body_diff_accepted():
    """BODY-DIFF-ACCEPTED — the committed one-byte bundle, exact reason."""
    code, out = run_checker(FIXTURES / "evidence-body-diff")
    assert code == 1, out
    assert "failure_reason: off: request-not-preserved: first diff at byte 56" in out, out


def test_mutant_offset_wrong():
    """OFFSET-WRONG — the reported offset IS the first differing byte, computed independently."""
    fixture = load(FIXTURES / "request-baseline.json")
    want = base64.b64decode(fixture["body_b64"])
    record = load(FIXTURES / "evidence-body-diff" / "off" / "upstream-record.json")
    got = json.dumps(record["body"], sort_keys=True, separators=(",", ":"),
                     ensure_ascii=True).encode()
    expected = next(i for i in range(min(len(want), len(got))) if want[i] != got[i])
    code, out = run_checker(FIXTURES / "evidence-body-diff")
    assert code == 1
    assert f"first diff at byte {expected}" in out, (expected, out)


@pytest.mark.parametrize("position", [0, 20, 40, 65])
def test_offset_tracks_the_mutation_position(tmp_path, position):
    """The reported offset must FOLLOW the mutation, not be a constant that matched once.

    The mutation is made inside the user-message content (where one character maps to exactly one
    canonical byte) and the expected offset is computed independently of the checker, as the
    content's own start offset in the committed body plus the mutated position.
    """
    fixture = load(FIXTURES / "request-baseline.json")
    body = base64.b64decode(fixture["body_b64"])
    content = json.loads(body)["messages"][0]["content"]
    # the test's own premise: the mutated position must lie OUTSIDE the nonce, or the nonce
    # guard fires first and this test would be measuring the wrong check.
    assert position < content.index(fixture["nonce"]), "position collides with the nonce"
    expected = body.index(content.encode()) + position
    mutated = content[:position] + ("Q" if content[position] != "Q" else "Z") + content[position + 1:]
    assert len(mutated) == len(content)

    b = bundle(tmp_path, f"pos{position}")
    path = b / "off" / "upstream-record.json"
    record = load(path)
    record["body"]["messages"][0]["content"] = mutated
    store(path, record)
    code, out = run_checker(b)
    assert code == 1, out
    assert f"first diff at byte {expected}" in out, (expected, out)


def test_mutant_nonce_mismatch_accepted(tmp_path):
    """NONCE-MISMATCH-ACCEPTED — a record from another leg must not satisfy this one."""
    b = bundle(tmp_path)
    shutil.copyfile(b / "off-large" / "upstream-record.json", b / "off" / "upstream-record.json")
    code, out = run_checker(b)
    assert code == 1, out
    assert "failure_reason: off: nonce-mismatch: fixture nonce absent from upstream record" in out, out


def test_mutant_bearer_in_evidence_accepted(tmp_path):
    """BEARER-IN-EVIDENCE-ACCEPTED — a bundle carrying a credential is rejected, not graded."""
    b = bundle(tmp_path)
    path = b / "off" / "response.json"
    obj = load(path)
    obj["headers"].append(["x-debug-upstream-auth", "Bearer sk-abc123def456ghi789"])
    store(path, obj)
    code, out = run_checker(b)
    assert code == 1, out
    assert "credential-in-evidence" in out, out
    assert "sk-abc123def456ghi789" not in out, "the checker echoed the credential it rejected"


def test_credential_screen_covers_every_leg_and_file(tmp_path):
    for leg, name in (("off", "request.json"), ("off-large", "upstream-record.json"),
                      ("config", "hermes-provider.json")):
        b = bundle(tmp_path, f"b-{leg}-{name}")
        path = b / leg / name
        obj = load(path)
        obj["stray_note"] = "authorization: Bearer sk-000111222333444"
        store(path, obj)
        code, out = run_checker(b)
        assert code == 1, (leg, name, out)
        assert "credential-in-evidence" in out, (leg, name, out)


def test_fingerprint_field_may_not_carry_a_bearer(tmp_path):
    """The one 64-hex carve-out is validated for digest shape, so it is not a smuggling lane."""
    b = bundle(tmp_path)
    path = b / "off" / "upstream-record.json"
    obj = load(path)
    obj["authorization_fingerprint"] = "Bearer sk-smuggled-through-the-carveout"
    store(path, obj)
    code, out = run_checker(b)
    assert code == 1, out
    assert "credential-in-evidence" in out, out


def test_a_second_hex64_still_fails(tmp_path):
    """Masking the fingerprint must not blind the screen to another 64-hex value."""
    b = bundle(tmp_path)
    path = b / "off" / "upstream-record.json"
    obj = load(path)
    obj["headers"]["x-note"] = "d" * 64
    store(path, obj)
    code, out = run_checker(b)
    assert code == 1, out
    assert "credential-in-evidence" in out and "hex64" in out, out


def test_mutant_config_header_missing_accepted(tmp_path):
    """CONFIG-HEADER-MISSING-ACCEPTED — assertion A1's configuration half."""
    b = bundle(tmp_path)
    path = b / "config" / "hermes-provider.json"
    obj = load(path)
    obj["extra_headers"] = {}
    store(path, obj)
    code, out = run_checker(b)
    assert code == 1, out
    assert "failure_reason: config: config-header-absent" in out, out


def test_config_reason_does_not_satisfy_the_response_negative_control(tmp_path):
    """The spec's negative leg binds on the substring `compression-header-missing`; no config
    failure may contain it, or the wrong check could satisfy the control."""
    b = bundle(tmp_path)
    obj = load(b / "config" / "hermes-provider.json")
    obj["extra_headers"] = {}
    store(b / "config" / "hermes-provider.json", obj)
    code, out = run_checker(b)
    assert code == 1
    negative = json.loads(SPEC.read_text())["legs"][1]["expect"]["failure_reason"]
    assert negative not in out, out


def test_mutant_fifo_hang(tmp_path):
    """FIFO-HANG — a FIFO in the bundle is named and refused, never read."""
    b = bundle(tmp_path)
    path = b / "off" / "response.json"
    path.unlink()
    os.mkfifo(path)
    code, out = run_checker(b)
    assert code == 1, out
    assert "evidence-not-regular-file" in out, out


def test_symlink_in_bundle_is_refused(tmp_path):
    b = bundle(tmp_path)
    path = b / "off" / "response.json"
    target = tmp_path / "elsewhere.json"
    target.write_text("{}\n")
    path.unlink()
    path.symlink_to(target)
    code, out = run_checker(b)
    assert code == 1, out
    assert "evidence-not-regular-file" in out, out


def test_mutant_deferred_as_pass(tmp_path):
    """DEFERRED-AS-PASS — an absent root defers (exit 2), it never passes."""
    code, out = run_checker(tmp_path / "nothing-here")
    assert code == 2, out
    assert out.strip() == "deferred: S0-04 evidence not captured"


def test_empty_root_defers(tmp_path):
    (tmp_path / "evidence").mkdir()
    code, out = run_checker(tmp_path / "evidence")
    assert code == 2, out
    assert "deferred: S0-04 evidence not captured" in out


def test_partial_capture_fails_it_does_not_defer(tmp_path):
    """Once anything is captured every required leg is REQUIRED (AF-AP-40)."""
    b = bundle(tmp_path)
    shutil.rmtree(b / "off-large")
    code, out = run_checker(b)
    assert code == 1, out
    assert "failure_reason: off-large: leg directory absent" in out, out


def test_extra_leg_is_refused(tmp_path):
    b = bundle(tmp_path)
    (b / "smuggled").mkdir()
    (b / "smuggled" / "x.json").write_text("{}\n")
    code, out = run_checker(b)
    assert code == 1, out
    assert "failure_reason: unexpected-leg: smuggled" in out, out


def test_missing_required_file_fails_named(tmp_path):
    for leg, name in (("off", "request.json"), ("off", "response.json"),
                      ("off", "upstream-record.json"), ("off-large", "upstream-record.json"),
                      ("config", "hermes-provider.json")):
        b = bundle(tmp_path, f"m-{leg}-{name}")
        (b / leg / name).unlink()
        code, out = run_checker(b)
        assert code == 1, (leg, name, out)
        assert f"{leg}: {name} absent" in out, (leg, name, out)


def test_mutant_case_sensitive_header(tmp_path):
    """CASE-SENSITIVE-HEADER — any spelling of the header NAME is accepted; the VALUE is exact."""
    for spelling in ("X-OmniRoute-Compression", "x-omniroute-compression",
                     "X-OMNIROUTE-COMPRESSION", "x-OmNiRoUtE-cOmPrEsSiOn"):
        b = bundle(tmp_path, f"c-{spelling}")
        path = b / "off" / "response.json"
        obj = load(path)
        obj["headers"] = [[spelling, h[1]] if h[0].lower() == "x-omniroute-compression" else h
                          for h in obj["headers"]]
        store(path, obj)
        code, out = run_checker(b)
        assert code == 0, (spelling, out)
        assert PASS_LINE in out


def test_config_header_key_case_is_also_insensitive(tmp_path):
    b = bundle(tmp_path)
    path = b / "config" / "hermes-provider.json"
    obj = load(path)
    obj["extra_headers"] = {"X-OmniRoute-Compression": "off"}
    store(path, obj)
    code, out = run_checker(b)
    assert code == 0, out


def test_duplicated_response_header_is_refused(tmp_path):
    """AF-AP-41 — a duplicated header must not collapse to a last-wins pass."""
    b = bundle(tmp_path)
    path = b / "off" / "response.json"
    obj = load(path)
    obj["headers"] = [["x-omniroute-compression", "on"]] + obj["headers"]
    store(path, obj)
    code, out = run_checker(b)
    assert code == 1, out
    assert "compression-header-duplicated: 2 occurrences" in out, out


def test_content_length_mutation_is_caught(tmp_path):
    b = bundle(tmp_path)
    path = b / "off" / "upstream-record.json"
    obj = load(path)
    obj["headers"]["content-length"] = "188"
    store(path, obj)
    code, out = run_checker(b)
    assert code == 1, out
    assert "request-not-preserved: content-length 188 != 189" in out, out


def test_tail_truncation_of_the_body_is_caught(tmp_path):
    """The large fixture carries its nonce at the START, so a tail truncation reaches A3's byte
    comparison rather than the nonce guard. The expected offset is computed independently."""
    fixture = load(FIXTURES / "request-large.json")
    body = base64.b64decode(fixture["body_b64"])
    content = json.loads(body)["messages"][0]["content"]
    expected = body.index(content.encode()) + 2048
    b = bundle(tmp_path)
    path = b / "off-large" / "upstream-record.json"
    obj = load(path)
    obj["body"]["messages"][0]["content"] = content[:2048]
    store(path, obj)
    code, out = run_checker(b)
    assert code == 1, out
    assert f"off-large: request-not-preserved: first diff at byte {expected}" in out, (expected, out)


def test_a_real_truncation_trips_the_length_half_of_a3(tmp_path):
    """A proxy that actually truncates changes the wire content-length too; that half of A3 is a
    separate record field and is checked before the body bytes."""
    b = bundle(tmp_path)
    path = b / "off-large" / "upstream-record.json"
    obj = load(path)
    obj["body"]["messages"][0]["content"] = obj["body"]["messages"][0]["content"][:2048]
    obj["headers"]["content-length"] = str(len(json.dumps(
        obj["body"], sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode()))
    store(path, obj)
    code, out = run_checker(b)
    assert code == 1, out
    assert "off-large: request-not-preserved: content-length" in out, out
    assert "!= 65536" in out, out


def test_truncation_that_removes_the_nonce_is_caught_as_a_wrong_record(tmp_path):
    """Ordering is deliberate: identity ("is this the right record") before preservation."""
    b = bundle(tmp_path)
    path = b / "off" / "upstream-record.json"
    obj = load(path)
    obj["body"]["messages"][0]["content"] = obj["body"]["messages"][0]["content"][:20]
    store(path, obj)
    code, out = run_checker(b)
    assert code == 1, out
    assert "off: nonce-mismatch" in out, out


def test_request_json_must_equal_the_committed_fixture(tmp_path):
    """The capture cannot send something other than the fixture and still pass."""
    for field, value in (("path", "/v1/responses"), ("method", "PUT"),
                         ("headers", {"content-type": "application/json"}),
                         ("body_b64", base64.b64encode(b"{}").decode())):
        b = bundle(tmp_path, f"r-{field}")
        path = b / "off" / "request.json"
        obj = load(path)
        obj[field] = value
        store(path, obj)
        code, out = run_checker(b)
        assert code == 1, (field, out)
        assert f"request-fixture-mismatch: {field}" in out, (field, out)


@pytest.mark.parametrize("url", [
    "http://127.0.0.1:20201/v1/chat/completions",   # straight at the scripted backend
    "http://127.0.0.1:20128/v1/responses",          # a different endpoint
    "https://example.invalid:20128/v1/chat/completions",
])
def test_request_url_must_be_the_omniroute_endpoint(tmp_path, url):
    """A leg captured against the backend directly would preserve the request perfectly and
    prove nothing about the gateway; a tail anchor on the path would have accepted it."""
    b = bundle(tmp_path, "url" + str(abs(hash(url))))
    path = b / "off" / "request.json"
    obj = load(path)
    obj["url"] = url
    store(path, obj)
    code, out = run_checker(b)
    assert code == 1, out
    assert "request-url-unexpected" in out, out


def test_capture_leg_refuses_a_fifo_fixture(tmp_path):
    module = _import(CAPTURE, "capture_leg")
    path = tmp_path / "fifo.json"
    os.mkfifo(path)
    with pytest.raises(module.CaptureError, match="not a regular file"):
        module.read_regular(path, "fixture")


def test_capture_leg_never_writes_through_a_symlink(tmp_path):
    module = _import(CAPTURE, "capture_leg")
    target = tmp_path / "outside.json"
    target.write_text("ORIGINAL\n")
    link = tmp_path / "out" / "request.json"
    link.parent.mkdir()
    link.symlink_to(target)
    module._write(link, {"leg": "off"})
    assert target.read_text() == "ORIGINAL\n"
    assert not link.is_symlink()


def test_config_field_mutations(tmp_path):
    cases = [
        ({"base_url": "http://127.0.0.1:8010/v1"}, "base-url-unexpected"),
        ({"key_env": "not a variable name"}, "key-env-not-a-name"),
        ({"key_env": None}, "key-env-not-a-name"),
        ({"api_mode": ""}, "api-mode-absent"),
        ({"extra_headers": {"x-omniroute-compression": "on"}}, "config-header-value: on"),
    ]
    for index, (patch, expected) in enumerate(cases):
        b = bundle(tmp_path, f"cfg-{index}")
        path = b / "config" / "hermes-provider.json"
        obj = load(path)
        obj.update(patch)
        store(path, obj)
        code, out = run_checker(b)
        assert code == 1, (patch, out)
        assert expected in out, (patch, out)


def test_unexpected_provider_field_is_refused(tmp_path):
    """Reachability: a field that is NOT credential-shaped still has to be refused, else the
    unexpected-fields check would only ever be reached through the screen (unreachable code)."""
    b = bundle(tmp_path)
    path = b / "config" / "hermes-provider.json"
    obj = load(path)
    obj["note"] = "harmless"
    store(path, obj)
    code, out = run_checker(b)
    assert code == 1, out
    assert "unexpected-provider-fields: note" in out, out


def test_inline_api_key_in_the_config_leg_is_a_credential_finding(tmp_path):
    """An `api_key` field carries a value shape the screen rejects before any grading."""
    b = bundle(tmp_path)
    path = b / "config" / "hermes-provider.json"
    obj = load(path)
    obj["api_key"] = "placeholder"
    store(path, obj)
    code, out = run_checker(b)
    assert code == 1, out
    assert "credential-in-evidence" in out and "key-assignment" in out, out


def test_non_canonical_fixture_is_refused(tmp_path):
    """De-vacuous the compare: a fixture whose bytes are not canonical cannot grade anything."""
    fixtures = tmp_path / "fx"
    shutil.copytree(FIXTURES, fixtures)
    path = fixtures / "request-baseline.json"
    obj = load(path)
    body = json.loads(base64.b64decode(obj["body_b64"]))
    obj["body_b64"] = base64.b64encode(json.dumps(body, indent=2).encode()).decode()
    store(path, obj)
    code, out = run_checker(PASS_BUNDLE, fixtures_dir=fixtures)
    assert code == 1, out
    assert "fixture-not-canonical" in out, out


def test_nan_in_evidence_is_refused(tmp_path):
    b = bundle(tmp_path)
    path = b / "off" / "upstream-record.json"
    path.write_text(path.read_text().replace('"seq": 1', '"seq": NaN'))
    code, out = run_checker(b)
    assert code == 1, out
    assert "NaN or Infinity" in out, out


def test_oversized_evidence_file_is_refused(tmp_path):
    b = bundle(tmp_path)
    (b / "off" / "filler.json").write_bytes(b"0" * (8 * 1024 * 1024 + 1))
    code, out = run_checker(b)
    assert code == 1, out
    assert "evidence-file-too-large" in out, out


def test_evidence_root_that_is_a_file_fails(tmp_path):
    path = tmp_path / "notadir"
    path.write_text("{}\n")
    code, out = run_checker(path)
    assert code == 1, out
    assert "evidence-root-not-a-directory" in out, out


# --------------------------------------------------------------------------- fixtures
def test_fixture_bytes_round_trip():
    for name in ("request-baseline.json", "request-large.json"):
        obj = load(FIXTURES / name)
        raw = base64.b64decode(obj["body_b64"], validate=True)
        assert base64.b64encode(raw).decode() == obj["body_b64"], name
        assert json.dumps(json.loads(raw), sort_keys=True, separators=(",", ":"),
                          ensure_ascii=True).encode() == raw, f"{name} is not canonical"
        assert obj["nonce"].encode() in raw, name
        assert obj["headers"]["x-omniroute-compression"] == "off", name
        assert json.loads(raw)["model"] == "s0-01-pong", name


def test_large_fixture_is_64_kib():
    obj = load(FIXTURES / "request-large.json")
    assert len(base64.b64decode(obj["body_b64"])) == 65536


def test_fixture_nonces_are_distinct():
    a = load(FIXTURES / "request-baseline.json")["nonce"]
    b = load(FIXTURES / "request-large.json")["nonce"]
    assert a != b and a not in b and b not in a


def test_required_legs_match_the_committed_bundle():
    import importlib.util
    spec = importlib.util.spec_from_file_location("check_compression", CHECKER)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    assert sorted(p.name for p in PASS_BUNDLE.iterdir()) == sorted(module.REQUIRED_LEGS)
    assert set(module.LEG_FIXTURE) == set(module.REQUIRED_LEGS) - {module.CONFIG_LEG}
    for name in module.LEG_FIXTURE.values():
        assert (FIXTURES / name).is_file(), name


def test_committed_fixtures_carry_no_credential_shape():
    import importlib.util
    spec = importlib.util.spec_from_file_location("check_compression", CHECKER)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    for path in sorted(FIXTURES.rglob("*.json")):
        text = path.read_text()
        for value in module._fingerprints(text, path):
            text = text.replace(value, "<authorization_fingerprint>")
        assert module._leak_hit(text) is None, path


# --------------------------------------------------------------------------- spec
def test_spec_matches_the_schema():
    """No silent skip (class 10): without jsonschema the structural half still runs."""
    spec = json.loads(SPEC.read_text())
    assert spec["proof_id"] == "S0-04"
    assert [leg["leg"] for leg in spec["legs"]] == ["positive", "negative"]
    assert all(leg["cwd"] == "." and 1 <= leg["timeout_s"] <= 3600 for leg in spec["legs"])
    assert "failure_reason" in spec["legs"][1]["expect"]
    try:
        import jsonschema
    except ImportError:
        pytest.fail("jsonschema absent: only the structural half of this check ran")
    jsonschema.validate(spec, json.loads(
        (ROOT / "proofs" / "schemas" / "spec.schema.json").read_text()))


def test_checker_reads_no_environment():
    """The verdict must not depend on the environment (`os.environ` is not a config channel).
    The checker reads none at all, so no exported value can flip a leg."""
    text = CHECKER.read_text()
    for token in ("os.environ", "getenv", "environb"):
        assert token not in text, token


def test_capture_leg_resolves_the_key_file_at_exactly_one_site():
    text = CAPTURE.read_text()
    sites = [i + 1 for i, line in enumerate(text.splitlines())
             if "os.environ" in line and not line.lstrip().startswith(("#", '"""'))]
    assert len(sites) == 1, sites


def test_spec_negative_reason_is_produced_by_the_real_checker():
    """AF-AP-27/AF-AP-29 — the seed's frozen reason must be the one the checker actually prints."""
    spec = json.loads(SPEC.read_text())
    negative = [leg for leg in spec["legs"] if leg["leg"] == "negative"]
    assert len(negative) == 1
    assert negative[0]["expect"]["failure_reason"] == "compression-header-missing"
    proc = subprocess.run([sys.executable] + negative[0]["cmd"][1:], cwd=str(ROOT),
                          capture_output=True, text=True, timeout=180)
    assert proc.returncode == negative[0]["expect"]["exit_code"]
    assert any(negative[0]["expect"]["failure_reason"] in line
               for line in (proc.stdout + proc.stderr).splitlines())


def test_spec_positive_leg_defers_today():
    """The evidence root is not captured yet: the positive leg must DEFER, never pass."""
    spec = json.loads(SPEC.read_text())
    positive = [leg for leg in spec["legs"] if leg["leg"] == "positive"][0]
    assert not (ROOT / "proofs" / "S0-04" / "evidence").exists()
    proc = subprocess.run([sys.executable] + positive["cmd"][1:], cwd=str(ROOT),
                          capture_output=True, text=True, timeout=180)
    assert proc.returncode == 2, proc.stdout + proc.stderr
    assert "deferred: S0-04 evidence not captured" in proc.stdout


# --------------------------------------------------------------------------- capture tool
def test_capture_leg_redacts_credential_headers():
    module = _import(CAPTURE, "capture_leg")
    out = module.redact_headers([("Content-Type", "application/json"),
                                 ("Authorization", "Bearer sk-secret-value-here"),
                                 ("Set-Cookie", "session=abc")])
    assert out == [["Content-Type", "application/json"],
                   ["Authorization", "<redacted>"],
                   ["Set-Cookie", "<redacted>"]]


def test_capture_leg_provider_block_drops_inline_key():
    module = _import(CAPTURE, "capture_leg")
    block = module.provider_block({"providers": {"factory-router": {
        "base_url": "http://127.0.0.1:20128/v1", "api_mode": "chat_completions",
        "api_key": "sk-inline-secret-value", "key_env": "OMNIROUTE_API_KEY",
        "extra_headers": {"x-omniroute-compression": "off"}}}}, "factory-router")
    assert set(block) == {"provider", "base_url", "api_mode", "key_env", "extra_headers"}
    assert "sk-inline-secret-value" not in json.dumps(block)
    assert block["key_env"] == "OMNIROUTE_API_KEY"


def test_capture_leg_provider_block_without_key_env_is_null_not_a_value():
    module = _import(CAPTURE, "capture_leg")
    block = module.provider_block({"providers": {"p": {
        "base_url": "http://127.0.0.1:20128/v1", "api_mode": "chat_completions",
        "api_key": "sk-inline-secret-value"}}}, "p")
    assert block["key_env"] is None
    assert "sk-inline-secret-value" not in json.dumps(block)


def test_capture_leg_find_record_requires_exactly_one(tmp_path):
    module = _import(CAPTURE, "capture_leg")
    records = tmp_path / "rec"
    records.mkdir()
    (records / "000001.json").write_text('{"body": {"c": "nonce-A"}}\n')
    (records / "000002.json").write_text('{"body": {"c": "nonce-B"}}\n')
    assert module.find_record(records, "nonce-A").name == "000001.json"
    with pytest.raises(module.CaptureError, match="no record"):
        module.find_record(records, "nonce-C")
    (records / "000003.json").write_text('{"body": {"c": "nonce-A"}}\n')
    with pytest.raises(module.CaptureError, match="2 records carry the nonce"):
        module.find_record(records, "nonce-A")


def test_capture_leg_key_file_mode_is_enforced(tmp_path):
    module = _import(CAPTURE, "capture_leg")
    key = tmp_path / "key.env"
    key.write_text("OMNIROUTE_API_KEY=sk-not-a-real-key\n")
    key.chmod(0o644)
    with pytest.raises(module.CaptureError, match="group/other readable"):
        module.read_key(str(key))
    key.chmod(0o600)
    assert module.read_key(str(key)) == "sk-not-a-real-key"
    key.write_text("NOTHING=1\n")
    with pytest.raises(module.CaptureError, match="no OMNIROUTE_API_KEY"):
        module.read_key(str(key))


def test_capture_leg_error_messages_never_echo_a_credential():
    module = _import(CAPTURE, "capture_leg")
    assert module.safe("boom Bearer sk-abcdefghij") == "<message withheld: credential-shaped>"
    assert module.safe("record dir not found: /tmp/x") == "record dir not found: /tmp/x"


def test_runner_is_syntactically_valid():
    proc = subprocess.run(["bash", "-n", str(RUNNER)], capture_output=True, text=True)
    assert proc.returncode == 0, proc.stderr


def test_runner_never_kills_by_name():
    """AF-AP-34 — no name-based kill on the owner's shared host. Comments may NAME the banned
    calls (the runner documents the rule); executable lines may not contain them."""
    code = [line for line in RUNNER.read_text().splitlines()
            if line.strip() and not line.lstrip().startswith("#")]
    for banned in ("pkill", "killall", "pgrep -f"):
        assert not any(banned in line for line in code), banned
    assert any("/proc/$pid/exe" in line for line in code)


def _import(path, name):
    import importlib.util
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


# --------------------------------------------------------------------------- real producer
@pytest.fixture(scope="module")
def live_backend(tmp_path_factory):
    """The REAL S0-01 scripted backend on a free port; terminated by pid, never by name."""
    tmp = tmp_path_factory.mktemp("s0_04_backend")
    token_file = tmp / "upstream.env"
    token_file.write_text(f"UPSTREAM_TOKEN={TOKEN}\n")
    token_file.chmod(0o600)
    port = free_port()
    records = tmp / "rec"
    proc = subprocess.Popen(
        [sys.executable, str(BACKEND), "--port", str(port), "--token-file", str(token_file),
         "--record-dir", str(records), "--pidfile", str(tmp / "pid")],
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    deadline = time.time() + 20
    ready = False
    while time.time() < deadline and proc.poll() is None:
        try:
            conn = http.client.HTTPConnection("127.0.0.1", port, timeout=1)
            conn.request("GET", "/healthz")
            resp = conn.getresponse()
            resp.read()
            conn.close()
            if resp.status == 200:
                ready = True
                break
        except OSError:
            time.sleep(0.05)
    if not ready:
        proc.terminate()
        proc.wait(timeout=10)
        pytest.fail("scripted backend did not become ready")
    yield {"port": port, "records": records}
    proc.terminate()
    proc.wait(timeout=10)


def _post_fixture(port, fixture):
    raw = base64.b64decode(fixture["body_b64"])
    headers = dict(fixture["headers"])
    headers["Authorization"] = f"Bearer {TOKEN}"
    conn = http.client.HTTPConnection("127.0.0.1", port, timeout=30)
    conn.request(fixture["method"], fixture["path"], body=raw, headers=headers)
    resp = conn.getresponse()
    resp.read()
    conn.close()
    return resp.status


def test_record_shape_is_the_current_producer_shape(live_backend, tmp_path):
    """AF-AP-42 — the checker's reading of the instrument is pinned to a RUN of the instrument.

    A real record for the committed fixture is dropped into a bundle and the checker must accept
    it; the record's key set is pinned; and the DOCUMENTED LIMIT (no raw request bytes in the
    record) is asserted, so a future backend that starts persisting them shows up here.
    """
    fixture = load(FIXTURES / "request-baseline.json")
    before = {p.name for p in live_backend["records"].glob("*.json")} \
        if live_backend["records"].is_dir() else set()
    assert _post_fixture(live_backend["port"], fixture) == 200
    new = sorted({p.name for p in live_backend["records"].glob("*.json")} - before)
    assert len(new) == 1, new
    record = load(live_backend["records"] / new[0])

    assert set(record) == RECORD_KEYS, set(record) ^ RECORD_KEYS
    assert "raw_body" not in record, (
        "the instrument now persists raw bytes — the checker's canonical comparison can be "
        "upgraded to a literal wire-byte compare")
    assert record["headers"]["content-length"] == str(len(base64.b64decode(fixture["body_b64"])))

    b = bundle(tmp_path)
    shutil.copyfile(live_backend["records"] / new[0], b / "off" / "upstream-record.json")
    code, out = run_checker(b)
    assert code == 0, out
    assert PASS_LINE in out, out


def test_real_record_of_a_mutated_body_is_rejected(live_backend, tmp_path):
    """The paired negative through the REAL producer: send a one-byte-different body and the
    checker must reject the record the backend actually wrote."""
    fixture = load(FIXTURES / "request-baseline.json")
    raw = base64.b64decode(fixture["body_b64"])
    mutated = dict(fixture)
    mutated["body_b64"] = base64.b64encode(raw.replace(b"probe", b"prXbe", 1)).decode()
    before = {p.name for p in live_backend["records"].glob("*.json")}
    assert _post_fixture(live_backend["port"], mutated) == 200
    new = sorted({p.name for p in live_backend["records"].glob("*.json")} - before)
    assert len(new) == 1, new

    b = bundle(tmp_path, "neg-real")
    shutil.copyfile(live_backend["records"] / new[0], b / "off" / "upstream-record.json")
    code, out = run_checker(b)
    assert code == 1, out
    assert "request-not-preserved: first diff at byte" in out, out


def test_real_large_record_round_trips(live_backend, tmp_path):
    """The 64 KiB leg through the real producer — the size where a compressing proxy would act."""
    fixture = load(FIXTURES / "request-large.json")
    before = {p.name for p in live_backend["records"].glob("*.json")}
    assert _post_fixture(live_backend["port"], fixture) == 200
    new = sorted({p.name for p in live_backend["records"].glob("*.json")} - before)
    assert len(new) == 1, new
    b = bundle(tmp_path, "large-real")
    shutil.copyfile(live_backend["records"] / new[0], b / "off-large" / "upstream-record.json")
    code, out = run_checker(b)
    assert code == 0, out
