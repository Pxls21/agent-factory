"""S0-05: no-direct-model-egress — checker, canary suite and netns library.

The oracle is `proofs/S0-05/check_egress.py`; these tests attack it. Three bundles are committed
evidence collected in this sandbox on a REAL network namespace (`proofs/S0-05/fixtures/`):
`evidence-mechanism-sandbox` (gate on -> PASS), `evidence-gate-off` (the seed's mutation ->
`egress-permitted: gate-disabled`), `evidence-bare-unshare` (total isolation ->
`positive-control-failed: curl`, the AF-AP-1 class). Every mutation below is applied to a COPY
under the test's tmp_path; the committed bundles are never edited.

Venue facts these tests pin, both measured on 2026-09-08 in this sandbox:
  * `HTTPS_PROXY=http://127.0.0.1:40173` is exported here, and curl inside the namespace then
    fails with rc 7 and the SAME generic "Couldn't connect to server" text a real gate denial
    produces. Only the address named in the diagnostic separates them, so a proxy-shaped denial
    must be rejected (`test_proxy_shaped_denial_is_rejected`).
  * `/etc/hosts` maps api.anthropic.com to the provider address, so C1 for that host resolves
    locally and fails at connect instead of at resolution. That record must still be accepted —
    it names its own target (`test_hosts_file_shortcircuit_is_accepted`).

Namespace tests need root (`ip netns`); on a venue without it they SKIP with a declared reason,
never fail silently.
"""
import importlib.util
import json
import os
import re
import shutil
import subprocess
import sys
import uuid
from pathlib import Path

import jsonschema
import pytest

REPO = Path(__file__).resolve().parents[1]
PROOF = REPO / "proofs" / "S0-05"
CHECKER = PROOF / "check_egress.py"
LIB = PROOF / "netns_lib.sh"
SPEC = PROOF / "spec.json"
SPEC_SCHEMA = REPO / "proofs" / "schemas" / "spec.schema.json"
FIXTURES = PROOF / "fixtures"
MECHANISM = FIXTURES / "evidence-mechanism-sandbox"
GATE_OFF = FIXTURES / "evidence-gate-off"
BARE = FIXTURES / "evidence-bare-unshare"
SYNTHETIC = FIXTURES / "evidence-synthetic-pass"
SHELL_FILES = sorted(
    [LIB, PROOF / "run_canaries.sh", PROOF / "tools" / "pc" / "run_s0_05_units.sh"]
    + sorted((PROOF / "canaries").glob("*.sh")))

# The exact proxy diagnostic this sandbox produces inside the namespace (measured, not invented).
PROXY_DETAIL = ("curl: (7) Failed to connect to 127.0.0.1 port 40173 after 0 ms: "
                "Couldn't connect to server")

_spec = importlib.util.spec_from_file_location("check_egress", CHECKER)
chk = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(chk)


def run_checker(*args, timeout=60):
    return subprocess.run([sys.executable, str(CHECKER), *map(str, args)],
                          capture_output=True, text=True, timeout=timeout, cwd=REPO)


def copy_bundle(tmp_path, source=MECHANISM, name="bundle"):
    destination = tmp_path / name
    shutil.copytree(source, destination)
    return destination


def records(unit_dir):
    return [json.loads(line) for line in (unit_dir / "canaries.jsonl").read_text().splitlines()
            if line.strip()]


def write_records(unit_dir, rows):
    (unit_dir / "canaries.jsonl").write_text(
        "".join(json.dumps(row, sort_keys=True) + "\n" for row in rows))


def patch_json(path, **fields):
    payload = json.loads(path.read_text())
    payload.update(fields)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    return payload


def netns_capable():
    if os.getuid() != 0:
        return False
    return shutil.which("ip") is not None and shutil.which("iptables") is not None


NEEDS_NETNS = pytest.mark.skipif(
    not netns_capable(),
    reason="network-namespace legs need root + iproute2 + iptables; NOT run here — they run on "
           "a capable venue (this sandbox has them; CI does not)")


# ---------------------------------------------------------------- the three committed bundles


def test_sandbox_mechanism_bundle_passes():
    """The real gate-on bundle collected in this sandbox. The PASS line is pinned whole."""
    result = run_checker(MECHANISM)
    assert result.returncode == 0, result.stdout + result.stderr
    assert ("PASS: S0-05 no-direct-egress - 1 units, 11 canaries failed as required, "
            "positive controls 1/1") in result.stdout
    assert "gate-fired: curl OUTPUT policy DROP 0 -> 10 packets" in result.stdout


def test_synthetic_bundle_passes_with_two_units():
    result = run_checker(SYNTHETIC, "--units", "curl,hermes-acp")
    assert result.returncode == 0, result.stdout + result.stderr
    assert "2 units, 22 canaries failed as required, positive controls 2/2" in result.stdout
    assert "NOT run: memory-adapter — unit does not exist" in result.stdout


def test_gate_off_bundle_is_red_with_the_seed_reason():
    """GATE-OFF-ACCEPTED. seeds/seed-stage0-v1.yaml:423-441 pins this exact reason."""
    result = run_checker(GATE_OFF)
    assert result.returncode == 1
    assert result.stdout.splitlines()[0] == "egress-permitted: gate-disabled"


def test_gate_off_bundle_really_did_flip_a_canary():
    """De-vacuity of the negative control: with the gate flushed, the routable non-allow-listed
    endpoint C6 became REACHABLE (rc 0, HTTP 200) where the gate-on bundle timed out. Without
    this the gate-off bundle would only differ by a JSON field."""
    on = {row["canary"]: row for row in records(MECHANISM / "curl")}
    off = {row["canary"]: row for row in records(GATE_OFF / "curl")}
    assert on["C6"]["rc"] == 28 and off["C6"]["rc"] == 0
    assert off["C6"]["http_status"] == 200
    assert json.loads((MECHANISM / "curl" / "gate.json").read_text())["rules_sha256"] != \
        json.loads((GATE_OFF / "curl" / "gate.json").read_text())["rules_sha256"]


def test_bare_unshare_bundle_is_red_on_the_positive_control():
    """BARE-UNSHARE-ACCEPTED / AF-AP-1: total isolation blocks the positive control too, so the
    bundle can never be S0-05 evidence."""
    result = run_checker(BARE)
    assert result.returncode == 1
    assert result.stdout.splitlines()[0] == "positive-control-failed: curl"
    c0 = [r for r in records(BARE / "curl") if r["canary"] == "C0"]
    assert len(c0) == 1 and c0[0]["rc"] == 7


def test_committed_bundles_carry_the_real_venue_shape():
    """The mechanism bundle must be a veth namespace with the gate on — not a relabelled copy."""
    gate = json.loads((MECHANISM / "curl" / "gate.json").read_text())
    runtime = json.loads((MECHANISM / "curl" / "runtime.json").read_text())
    assert gate["mechanism"] == "veth-iptables" and gate["gate"] == "enabled"
    assert runtime["venue"] == "sandbox"
    assert runtime["drop_counter_after"] > runtime["drop_counter_before"]
    assert "-P OUTPUT DROP" in runtime["rules"]


# --------------------------------------------------------------------------- ordering mutants


def test_gate_check_runs_before_any_canary(tmp_path):
    """GATE-CHECK-AFTER-CANARIES. A disabled gate is fatal even when every canary failed — the
    checker never gets to read them, so a flushed gate can never pass by luck."""
    bundle = copy_bundle(tmp_path, GATE_OFF)
    rows = records(bundle / "curl")
    for row in rows:  # make every canary a denial, including the one that flipped
        if row["canary"] == "C6":
            host, port = row["target"].rsplit(":", 1)
            row.update(rc=28, http_status=0,
                       detail=f"curl: (28) Failed to connect to {host} port {port} "
                              "after 5002 ms: Timeout was reached")
    write_records(bundle / "curl", rows)
    result = run_checker(bundle)
    assert result.returncode == 1
    assert result.stdout.splitlines()[0] == "egress-permitted: gate-disabled"


def test_gate_check_precedes_a_canary_success_in_another_unit(tmp_path):
    """Two units, one with the gate off: the gate verdict wins over any later canary reading."""
    bundle = copy_bundle(tmp_path, SYNTHETIC)
    patch_json(bundle / "hermes-acp" / "gate.json", gate="disabled")
    rows = records(bundle / "curl")
    for row in rows:
        if row["canary"] == "C2":
            row["rc"] = 0
    write_records(bundle / "curl", rows)
    result = run_checker(bundle, "--units", "curl,hermes-acp")
    assert result.returncode == 1
    assert result.stdout.splitlines()[0] == "egress-permitted: gate-disabled"


# ------------------------------------------------------------------- positive-control mutants


@pytest.mark.parametrize("mutate, ids", [
    (lambda rows: [r for r in rows if r["canary"] != "C0"], "c0-deleted"),
    (lambda rows: [{**r, "rc": 7} if r["canary"] == "C0" else r for r in rows], "c0-failed"),
    (lambda rows: [{**r, "http_status": 500} if r["canary"] == "C0" else r for r in rows], "c0-500"),
    (lambda rows: [{k: v for k, v in r.items() if k != "http_status"} if r["canary"] == "C0" else r
                   for r in rows], "c0-no-status"),
    (lambda rows: [{**r, "http_status": True} if r["canary"] == "C0" else r for r in rows], "c0-bool-status"),
    (lambda rows: [{**r, "status": "not-run", "rc": None} if r["canary"] == "C0" else r
                   for r in rows], "c0-not-run"),
], ids=["c0-deleted", "c0-failed", "c0-500", "c0-no-status", "c0-bool-status", "c0-not-run"])
def test_positive_control_is_mandatory(tmp_path, mutate, ids):
    """POSITIVE-CONTROL-OPTIONAL. Every way of losing the positive control is the same verdict —
    including a boolean 500 dressed as an int (AF-AP-26: isinstance(True, int) is True)."""
    bundle = copy_bundle(tmp_path)
    write_records(bundle / "curl", mutate(records(bundle / "curl")))
    result = run_checker(bundle)
    assert result.returncode == 1
    assert result.stdout.splitlines()[0] == "positive-control-failed: curl"


# ---------------------------------------------------------------------- denial-canary mutants


@pytest.mark.parametrize("canary", ["C1", "C2", "C3", "C5", "C6"])
def test_a_canary_that_succeeded_is_caught(tmp_path, canary):
    """CANARY-SUCCESS-ACCEPTED: a reachable model endpoint is the violation S0-05 exists for."""
    bundle = copy_bundle(tmp_path)
    rows = records(bundle / "curl")
    target = None
    for row in rows:
        if row["canary"] == canary:
            row.update(rc=0, detail="connected")
            target = row["target"]
            break
    write_records(bundle / "curl", rows)
    result = run_checker(bundle)
    assert result.returncode == 1
    assert result.stdout.splitlines()[0] == f"egress-permitted: curl {canary} {target}"


@pytest.mark.parametrize("canary", ["C1", "C2", "C3", "C4", "C5", "C6"])
def test_a_deleted_canary_is_caught(tmp_path, canary):
    """DNS-CANARY-DROPPED, generalised: dropping ANY required canary (C4 included, which is
    recorded rather than asserted) is a missing observation, not a pass."""
    bundle = copy_bundle(tmp_path)
    write_records(bundle / "curl", [r for r in records(bundle / "curl") if r["canary"] != canary])
    result = run_checker(bundle)
    assert result.returncode == 1
    assert result.stdout.splitlines()[0] == f"canary-missing: curl {canary}"


@pytest.mark.parametrize("rc", [0, 1, 35, 52, -1])
def test_a_denial_rc_outside_the_set_is_caught(tmp_path, rc):
    bundle = copy_bundle(tmp_path)
    rows = [{**r, "rc": rc} if r["canary"] == "C2" else r for r in records(bundle / "curl")]
    write_records(bundle / "curl", rows)
    result = run_checker(bundle)
    assert result.returncode == 1
    first = result.stdout.splitlines()[0]
    assert first.startswith("egress-permitted: curl C2" if rc == 0 else "denial-rc-unrecognized: curl C2")


def test_proxy_shaped_denial_is_rejected(tmp_path):
    """DETAIL-UNCHECKED, the real specimen. The ambient HTTPS_PROXY in this venue makes curl fail
    with rc 7 and curl 8.5's generic "Couldn't connect to server" — indistinguishable from a gate
    denial except by the address it names. Accepting it would count the proxy as containment."""
    bundle = copy_bundle(tmp_path)
    rows = [{**r, "rc": 7, "detail": PROXY_DETAIL} if r["canary"] == "C6" else r
            for r in records(bundle / "curl")]
    write_records(bundle / "curl", rows)
    result = run_checker(bundle)
    assert result.returncode == 1
    assert result.stdout.splitlines()[0].startswith("denial-detail-foreign-target: curl C6")
    assert "127.0.0.1" in result.stdout.splitlines()[0]


def test_a_forged_loopback_ip_cannot_whitelist_a_proxy_denial(tmp_path):
    """18-class sweep, class 18: the record's own `ip` field is an accepted alias for the address
    a diagnostic may name. Without a floor, a record carrying `"ip": "127.0.0.1"` would whitelist
    the exact proxy-shaped denial the foreign-target rule exists to reject."""
    bundle = copy_bundle(tmp_path)
    rows = [{**r, "rc": 7, "detail": PROXY_DETAIL, "ip": "127.0.0.1"} if r["canary"] == "C2" else r
            for r in records(bundle / "curl")]
    write_records(bundle / "curl", rows)
    result = run_checker(bundle)
    assert result.returncode == 1
    assert result.stdout.splitlines()[0].startswith("denial-detail-foreign-target: curl C2")


def test_a_real_remote_ip_alias_is_still_accepted(tmp_path):
    """The other side of that floor: a genuine resolved address still counts as the target's own
    name, so a real C2/C3 denial naming the IP is not spuriously rejected."""
    bundle = copy_bundle(tmp_path)
    rows = records(bundle / "curl")
    for row in rows:
        if row["canary"] == "C2":
            row.update(rc=7, ip="162.159.140.245",
                       detail="curl: (7) Failed to connect to 162.159.140.245 port 443 after "
                              "0 ms: Couldn't connect to server")
            break
    write_records(bundle / "curl", rows)
    assert run_checker(bundle).returncode == 0


def test_resolve_denial_naming_another_host_is_rejected(tmp_path):
    bundle = copy_bundle(tmp_path)
    rows = [{**r, "rc": 6, "detail": "curl: (6) Could not resolve host: example.invalid"}
            if r["canary"] == "C1" else r for r in records(bundle / "curl")]
    write_records(bundle / "curl", rows)
    result = run_checker(bundle)
    assert result.returncode == 1
    assert result.stdout.splitlines()[0].startswith("denial-detail-foreign-target: curl C1")


@pytest.mark.parametrize("detail", [
    "curl: (7) SSL certificate problem: self signed certificate",
    "OSError [Errno 13] Permission denied",
    "",
    "denied",
], ids=["tls-error", "wrong-errno", "empty", "vague"])
def test_a_denial_detail_from_another_mechanism_is_rejected(tmp_path, detail):
    """DETAIL-UNCHECKED, the class: an rc in the denial set with a diagnostic this mechanism
    cannot produce is not evidence of containment."""
    bundle = copy_bundle(tmp_path)
    rows = [{**r, "rc": 7, "detail": detail} if r["canary"] == "C2" else r
            for r in records(bundle / "curl")]
    write_records(bundle / "curl", rows)
    result = run_checker(bundle)
    assert result.returncode == 1
    assert result.stdout.splitlines()[0].startswith("denial-detail-unrecognized: curl C2")


def test_hosts_file_shortcircuit_is_accepted():
    """The other half of the detail rule: this venue's /etc/hosts resolves api.anthropic.com, so
    C1 for that host fails at CONNECT with the generic curl text. It names its own target, so it
    is a real denial and the committed bundle passes with it."""
    row = [r for r in records(MECHANISM / "curl")
           if r["canary"] == "C1" and r["target"] == "api.anthropic.com"][0]
    assert row["rc"] == 7 and row["resolved"] == "160.79.104.10"
    assert "Failed to connect to api.anthropic.com" in row["detail"]
    assert run_checker(MECHANISM).returncode == 0


# ----------------------------------------------------------------------- rule-digest mutants


def test_rules_that_do_not_hash_to_the_digest_are_caught(tmp_path):
    """RULES-DIGEST-UNPINNED (a): the recorded rule list was edited and the digest left alone."""
    bundle = copy_bundle(tmp_path)
    runtime = json.loads((bundle / "curl" / "runtime.json").read_text())
    runtime["rules"].append("-A OUTPUT -j ACCEPT")
    (bundle / "curl" / "runtime.json").write_text(json.dumps(runtime, indent=2, sort_keys=True) + "\n")
    result = run_checker(bundle)
    assert result.returncode == 1
    assert result.stdout.splitlines()[0] == \
        "egress-rules-unpinned: curl recorded rules do not hash to the gate digest"


def test_a_widened_rule_set_with_a_matching_digest_is_caught(tmp_path):
    """RULES-DIGEST-UNPINNED (b), the one that matters: the collector adds a blanket ACCEPT and
    recomputes its own digest honestly. The checker derives the rules from the DECLARED allow-list
    and rejects the widening anyway — the mechanism cannot be silently weakened."""
    bundle = copy_bundle(tmp_path)
    runtime = json.loads((bundle / "curl" / "runtime.json").read_text())
    runtime["rules"] = sorted(runtime["rules"] + ["-A OUTPUT -j ACCEPT"])
    (bundle / "curl" / "runtime.json").write_text(json.dumps(runtime, indent=2, sort_keys=True) + "\n")
    patch_json(bundle / "curl" / "gate.json", rules_sha256=chk.rules_digest(runtime["rules"]))
    result = run_checker(bundle)
    assert result.returncode == 1
    assert result.stdout.splitlines()[0].startswith("egress-rules-unpinned: curl rules are not the pinned allow-list")


def test_a_dropped_policy_line_is_caught(tmp_path):
    bundle = copy_bundle(tmp_path)
    runtime = json.loads((bundle / "curl" / "runtime.json").read_text())
    runtime["rules"] = [r for r in runtime["rules"] if r != "-P OUTPUT DROP"]
    (bundle / "curl" / "runtime.json").write_text(json.dumps(runtime, indent=2, sort_keys=True) + "\n")
    patch_json(bundle / "curl" / "gate.json", rules_sha256=chk.rules_digest(runtime["rules"]))
    result = run_checker(bundle)
    assert result.returncode == 1
    assert result.stdout.splitlines()[0].startswith("egress-rules-unpinned: curl rules are not the pinned allow-list")


def test_a_widened_allow_list_changes_the_expected_digest(tmp_path):
    """Declaring a second allowed destination without the rules to match is caught."""
    bundle = copy_bundle(tmp_path)
    gate = json.loads((bundle / "curl" / "gate.json").read_text())
    patch_json(bundle / "curl" / "gate.json", allowed=gate["allowed"] + ["1.2.3.4:443"])
    result = run_checker(bundle)
    assert result.returncode == 1
    assert result.stdout.splitlines()[0].startswith("egress-rules-unpinned: curl rules are not the pinned allow-list")


def test_expected_rules_is_the_allow_list_and_nothing_more():
    rules = chk.expected_rules(["10.0.0.1:20128"])
    assert rules == sorted([
        "-P INPUT DROP", "-P FORWARD DROP", "-P OUTPUT DROP",
        "-A INPUT -i lo -j ACCEPT", "-A OUTPUT -o lo -j ACCEPT",
        "-A INPUT -s 10.0.0.1/32 -p tcp -m tcp --sport 20128 -j ACCEPT",
        "-A OUTPUT -d 10.0.0.1/32 -p tcp -m tcp --dport 20128 -j ACCEPT"])
    assert chk.rules_digest(rules) != chk.rules_digest(chk.expected_rules(["10.0.0.1:20129"]))


@pytest.mark.parametrize("entry", ["10.0.0.1", "10.0.0.1:0", "10.0.0.1:70000", "999.1.1.1:80",
                                   "host.example:443", "10.0.0.1:44 3"])
def test_a_malformed_allow_entry_is_rejected(entry):
    with pytest.raises(chk.Failure) as error:
        chk.expected_rules([entry])
    assert "gate-manifest-invalid" in str(error.value)


# ---------------------------------------------------------------------- gate-fired / inertness


@pytest.mark.parametrize("before, after", [(0, 0), (5, 5), (7, 3)])
def test_a_gate_that_never_fired_is_caught(tmp_path, before, after):
    """The gate must have actually dropped a packet during the run. A suite whose canaries all
    failed for reasons other than the gate leaves the OUTPUT policy counter where it started."""
    bundle = copy_bundle(tmp_path)
    patch_json(bundle / "curl" / "runtime.json",
               drop_counter_before=before, drop_counter_after=after)
    result = run_checker(bundle)
    assert result.returncode == 1
    assert result.stdout.splitlines()[0].startswith("gate-inert: curl OUTPUT DROP counter did not advance")


@pytest.mark.parametrize("value", [True, -1, "9", 1.5, None])
def test_a_non_integer_drop_counter_is_rejected(tmp_path, value):
    bundle = copy_bundle(tmp_path)
    patch_json(bundle / "curl" / "runtime.json", drop_counter_after=value)
    result = run_checker(bundle)
    assert result.returncode == 1
    assert result.stdout.splitlines()[0].startswith(
        ("runtime-manifest-invalid: curl", "gate-inert: curl"))


# ------------------------------------------------------------------------------- the unit set


def test_an_empty_evidence_root_is_red(tmp_path):
    """UNIT-SET-EMPTY-PASSES: no units is a failure, never a vacuous pass."""
    empty = tmp_path / "empty"
    empty.mkdir()
    result = run_checker(empty)
    assert result.returncode == 1
    assert result.stdout.splitlines()[0].startswith("no-units:")


def test_a_declared_absent_unit_cannot_also_be_present(tmp_path):
    bundle = copy_bundle(tmp_path)
    shutil.copytree(bundle / "curl", bundle / "hermes-acp")
    result = run_checker(bundle)
    assert result.returncode == 1
    assert result.stdout.splitlines()[0] == "unit-declared-absent-but-present: hermes-acp"


def test_a_declared_run_unit_that_is_missing_is_red(tmp_path):
    bundle = copy_bundle(tmp_path, SYNTHETIC)
    shutil.rmtree(bundle / "hermes-acp")
    result = run_checker(bundle, "--units", "curl")
    assert result.returncode == 1
    assert result.stdout.splitlines()[0] == "unit-missing: hermes-acp"


def test_a_required_unit_that_was_never_collected_is_red():
    result = run_checker(MECHANISM, "--units", "curl,hermes-acp")
    assert result.returncode == 1
    assert result.stdout.splitlines()[0] == "unit-missing: hermes-acp"


@pytest.mark.parametrize("manifest, fragment", [
    ({"units": "curl"}, "units-manifest-invalid"),
    ({"units": [{"unit": "curl"}]}, "units-manifest-invalid"),
    ({"units": [{"unit": "curl", "status": "maybe"}]}, "units-manifest-invalid"),
    ({"units": [{"unit": "x", "status": "not-run"}]}, "declared not-run without a reason"),
], ids=["not-a-list", "no-status", "bad-status", "no-reason"])
def test_a_malformed_units_manifest_is_rejected(tmp_path, manifest, fragment):
    bundle = copy_bundle(tmp_path)
    (bundle / "units.json").write_text(json.dumps(manifest))
    result = run_checker(bundle)
    assert result.returncode == 1
    assert fragment in result.stdout


# --------------------------------------------------------------------------- defer, never pass


def test_an_absent_evidence_root_defers(tmp_path):
    """DEFERRED-AS-PASS: the live-unit evidence is collected on the PC. Absent here means DEFER
    (exit 2, the runner preserves the artifact), never a pass and never a silent skip."""
    result = run_checker(tmp_path / "nope")
    assert result.returncode == 2
    assert result.stdout.splitlines()[0].startswith("deferred: evidence-root-absent:")


def test_the_committed_spec_positive_leg_defers_here():
    result = run_checker(PROOF / "evidence")
    assert result.returncode == 2


def test_a_canary_that_could_not_run_defers(tmp_path):
    """AF-AP-24: a discriminator that could not run is a DEFER, not a pass."""
    bundle = copy_bundle(tmp_path)
    rows = [{**r, "status": "not-run", "rc": None,
             "detail": "resolve-failed: api.openai.com has no A record from this venue"}
            if r["canary"] == "C2" else r for r in records(bundle / "curl")]
    write_records(bundle / "curl", rows)
    result = run_checker(bundle)
    assert result.returncode == 2
    assert result.stdout.splitlines()[0].startswith("deferred: curl C2 not-run: resolve-failed")


# ------------------------------------------------------------------- malformed / hostile input


@pytest.mark.parametrize("name", ["curl/canaries.jsonl", "curl/gate.json", "curl/runtime.json",
                                  "units.json"])
def test_a_fifo_in_place_of_evidence_is_rejected_without_hanging(tmp_path, name):
    """FIFO-HANG: a named pipe passes `exists()` and blocks forever on read. S_ISREG first —
    on every file the checker reads, units.json included."""
    bundle = copy_bundle(tmp_path)
    target = bundle / name
    target.unlink()
    os.mkfifo(target)
    result = run_checker(bundle, timeout=30)
    assert result.returncode == 1
    assert "is not a regular file" in result.stdout


@pytest.mark.parametrize("name", ["canaries.jsonl", "gate.json", "runtime.json"])
def test_missing_evidence_files_are_named(tmp_path, name):
    bundle = copy_bundle(tmp_path)
    (bundle / "curl" / name).unlink()
    result = run_checker(bundle)
    assert result.returncode == 1
    assert "evidence-missing" in result.stdout and name in result.stdout


@pytest.mark.parametrize("payload", ["NaN", "Infinity", "-Infinity"])
def test_nan_in_the_canary_log_is_rejected(tmp_path, payload):
    bundle = copy_bundle(tmp_path)
    with open(bundle / "curl" / "canaries.jsonl", "a") as handle:
        handle.write('{"canary": "C7", "unit": "curl", "target": "x", "kind": "k", '
                     f'"rc": {payload}, "status": "run", "detail": "d"}}\n')
    result = run_checker(bundle)
    assert result.returncode == 1
    assert "evidence-invalid" in result.stdout


def test_a_record_claiming_another_unit_is_rejected(tmp_path):
    bundle = copy_bundle(tmp_path)
    rows = [{**r, "unit": "somebody-else"} if r["canary"] == "C5" else r
            for r in records(bundle / "curl")]
    write_records(bundle / "curl", rows)
    result = run_checker(bundle)
    assert result.returncode == 1
    assert "names unit 'somebody-else'" in result.stdout


@pytest.mark.parametrize("key", ["gate", "mechanism", "netns", "unit", "allowed", "rules_sha256"])
def test_a_gate_file_missing_a_key_is_rejected(tmp_path, key):
    bundle = copy_bundle(tmp_path)
    gate = json.loads((bundle / "curl" / "gate.json").read_text())
    del gate[key]
    (bundle / "curl" / "gate.json").write_text(json.dumps(gate, indent=2, sort_keys=True) + "\n")
    result = run_checker(bundle)
    assert result.returncode == 1
    assert f"gate-manifest-invalid: curl gate.json lacks {key}" in result.stdout


def test_the_pass_line_counts_units_not_records(tmp_path):
    """18-class sweep, class 15: the PASS line's `positive controls N/M` must be two DIFFERENT
    populations. A unit with two allowed targets has two C0 records; the line must still read
    1/1 (one unit proven of one checked), not 2/2."""
    bundle = copy_bundle(tmp_path)
    rows = records(bundle / "curl")
    extra = dict([r for r in rows if r["canary"] == "C0"][0])
    rows.insert(1, extra)
    write_records(bundle / "curl", rows)
    result = run_checker(bundle)
    assert result.returncode == 0, result.stdout
    assert "1 units," in result.stdout and "positive controls 1/1" in result.stdout


@pytest.mark.skipif(shutil.which("ip") is None, reason="iproute2 absent; NOT run here")
def test_the_collector_refuses_an_unreadable_drop_counter(tmp_path):
    """18-class sweep, class 6: an unreadable OUTPUT DROP counter used to default to 0, which
    inflates the recorded delta and fail-OPENs the checker's gate-inert rule. It now exits 3 with
    a named reason. Driven against a namespace that does not exist."""
    result = subprocess.run(
        ["bash", str(PROOF / "run_canaries.sh"), "curl", "s0-05-e1-does-not-exist",
         "10.201.1.1:12800", str(tmp_path / "ev")],
        capture_output=True, text=True, timeout=120)
    assert result.returncode == 3, (result.returncode, result.stdout, result.stderr)
    assert "cannot read the OUTPUT DROP counter" in result.stderr


def test_the_checker_is_deterministic():
    first, second = run_checker(MECHANISM), run_checker(MECHANISM)
    assert first.stdout == second.stdout and first.returncode == second.returncode == 0


# -------------------------------------------------------------------------- the canonical spec


def test_spec_validates_against_the_schema():
    spec = json.loads(SPEC.read_text())
    jsonschema.Draft202012Validator(json.loads(SPEC_SCHEMA.read_text())).validate(spec)
    assert spec["proof_id"] == "S0-05"


def test_every_spec_leg_behaves_exactly_as_declared():
    """AF-AP-29: the canonical contract is at least as strong as the strongest test. Each
    negative leg's declared failure_reason must be the checker's COMPLETE first output line, not
    a prefix of it."""
    for leg in json.loads(SPEC.read_text())["legs"]:
        result = subprocess.run(leg["cmd"], capture_output=True, text=True, cwd=REPO,
                                timeout=leg["timeout_s"])
        expected = leg["expect"]["exit_code"]
        if leg["leg"] == "positive" and leg["cmd"][-1].endswith("S0-05/evidence"):
            assert result.returncode in (expected, 2), result.stdout  # defers until the PC leg runs
            continue
        assert result.returncode == expected, (leg["cmd"], result.stdout, result.stderr)
        if "failure_reason" in leg["expect"]:
            assert result.stdout.splitlines()[0] == leg["expect"]["failure_reason"]


# ------------------------------------------------------------------------ shell + library legs


def test_every_new_shell_file_parses():
    for path in SHELL_FILES:
        assert path.is_file(), path
        result = subprocess.run(["bash", "-n", str(path)], capture_output=True, text=True)
        assert result.returncode == 0, f"{path}: {result.stderr}"


def test_bash_n_would_have_caught_a_broken_script(tmp_path):
    broken = tmp_path / "broken.sh"
    broken.write_text("#!/bin/bash\nif true; then\n")
    assert subprocess.run(["bash", "-n", str(broken)], capture_output=True).returncode != 0


def _lib(*script_lines):
    body = "\n".join([". " + str(LIB), *script_lines])
    return subprocess.run(["bash", "-c", body], capture_output=True, text=True, timeout=120)


def test_library_derivations_are_deterministic_and_fit_ifnamsiz():
    result = _lib('egress_ns_host_if s0-05-e1-test', 'egress_ns_if s0-05-e1-test',
                  'egress_ns_host_ip s0-05-e1-test', 'egress_ns_resolver s0-05-e1-test')
    host_if, ns_if, host_ip, resolver = result.stdout.split()
    assert len(host_if) <= 15 and len(ns_if) <= 15
    assert re.fullmatch(r"10\.201\.\d{1,3}\.1", host_ip)
    assert resolver.rsplit(".", 1)[1] == "53" and resolver.rsplit(".", 2)[0] == host_ip.rsplit(".", 2)[0]
    assert _lib('egress_ns_host_if s0-05-e1-test').stdout == host_if + "\n"


@NEEDS_NETNS
def test_library_round_trip_leaves_no_namespace_behind():
    """NETNS-LEAK: create -> run -> destroy, and the census must not name the namespace after.
    The library's rules must also be EXACTLY the set check_egress.py derives from the allow-list
    — the two halves of the pinned contract, compared against a real kernel."""
    ns = f"s0-05-e1-{uuid.uuid4().hex[:8]}"
    allowed = None
    try:
        result = _lib(f'egress_ns_create {ns} "$(egress_ns_host_ip {ns}):20128" || exit 1',
                      f'egress_ns_host_ip {ns}',
                      f'egress_ns_gate_state {ns}',
                      f'egress_ns_mechanism {ns}',
                      f'egress_ns_run {ns} true && echo run-ok',
                      f'egress_ns_rules {ns}')
        assert result.returncode == 0, result.stderr
        lines = result.stdout.splitlines()
        allowed, gate_state, mechanism, run_ok = lines[0], lines[1], lines[2], lines[3]
        assert gate_state == "enabled" and mechanism == "veth-iptables" and run_ok == "run-ok"
        assert lines[4:] == chk.expected_rules([f"{allowed}:20128"])
        off = _lib(f'egress_gate_off {ns}', f'egress_ns_gate_state {ns}')
        assert off.stdout.splitlines()[-1] == "disabled"
    finally:
        _lib(f'egress_ns_destroy {ns}')
    census = subprocess.run(["ip", "netns", "list"], capture_output=True, text=True).stdout
    assert ns not in census, census


@NEEDS_NETNS
def test_the_drop_counter_reads_both_policies():
    """Regression, bit while collecting the gate-off bundle on 2026-09-08: the counter reader
    only understood a DROP policy, so with the gate switched OFF it returned the empty string,
    the collector's fail-loud guard fired, and the negative-control bundle was written EMPTY.
    A DROP policy reports its count, an ACCEPT policy reports 0, an unreadable chain reports
    nothing at all."""
    ns = f"s0-05-e1-{uuid.uuid4().hex[:8]}"
    try:
        result = _lib(f'ip netns add {ns} && ip netns exec {ns} ip link set lo up',
                      f'ip netns exec {ns} iptables -P OUTPUT DROP',
                      f'echo "drop=[$(egress_ns_drop_counter {ns})]"',
                      f'ip netns exec {ns} iptables -P OUTPUT ACCEPT',
                      f'echo "accept=[$(egress_ns_drop_counter {ns})]"',
                      'echo "missing=[$(egress_ns_drop_counter s0-05-e1-no-such-ns)]"')
        assert result.returncode == 0, result.stderr
        assert "drop=[0]" in result.stdout and "accept=[0]" in result.stdout
        assert "missing=[]" in result.stdout
    finally:
        _lib(f'egress_ns_destroy {ns}')
    assert ns not in subprocess.run(["ip", "netns", "list"], capture_output=True, text=True).stdout


@NEEDS_NETNS
def test_the_isolated_control_has_no_veth_and_fails_its_positive_control():
    """The committed bare-unshare bundle's shape, re-derived live: same gate, no veth, so the
    allowed target is unreachable — the AF-AP-1 class."""
    ns = f"s0-05-e1-{uuid.uuid4().hex[:8]}"
    try:
        result = _lib(f'egress_ns_create_isolated {ns} "$(egress_ns_host_ip {ns}):20128" || exit 1',
                      f'egress_ns_mechanism {ns}',
                      f'egress_ns_gate_state {ns}',
                      f'egress_ns_run {ns} curl -sS --connect-timeout 3 -o /dev/null '
                      f'"http://$(egress_ns_host_ip {ns}):20128/" ; echo "c0-rc=$?"')
        assert result.returncode == 0, result.stderr
        assert result.stdout.splitlines()[0] == "netns-no-veth"
        assert result.stdout.splitlines()[1] == "enabled"
        assert result.stdout.splitlines()[-1] == "c0-rc=7"
    finally:
        _lib(f'egress_ns_destroy {ns}')
    assert ns not in subprocess.run(["ip", "netns", "list"], capture_output=True, text=True).stdout


@NEEDS_NETNS
def test_the_canary_emitter_scrubs_the_proxy_environment():
    """The scrub is the first defence against the venue's ambient proxy. Proven by running a
    canary script's own preamble with the proxy set and reading the environment back."""
    body = ('export HTTPS_PROXY=http://127.0.0.1:40173 https_proxy=http://127.0.0.1:40173\n'
            f'. {PROOF}/canaries/_emit.sh\n'
            'echo "HTTPS_PROXY=[${HTTPS_PROXY:-unset}] https_proxy=[${https_proxy:-unset}]"')
    result = subprocess.run(["bash", "-c", body], capture_output=True, text=True, timeout=30)
    assert result.stdout.strip() == "HTTPS_PROXY=[unset] https_proxy=[unset]", result.stdout
