"""S0-05: no-direct-model-egress — checker, canary suite and netns library.

The oracle is `proofs/S0-05/check_egress.py`; these tests attack it. Three bundles are committed
evidence collected in this sandbox on a REAL network namespace (`proofs/S0-05/fixtures/`):
`evidence-mechanism-sandbox` (gate on -> PASS), `evidence-gate-off` (the seed's mutation ->
`egress-permitted: gate-disabled`), `evidence-bare-unshare` (total isolation ->
`total-isolation: curl mechanism=netns-no-veth`, the AF-AP-1 class). Every mutation below is
applied to a COPY under the test's tmp_path; the committed bundles are never edited.

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
import time
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


def test_bare_unshare_bundle_is_red_as_total_isolation():
    """BARE-UNSHARE-ACCEPTED / AF-AP-1: a namespace with no selective-egress veth is the
    total-isolation class the seed declares inadmissible. The guard rejects it by CLASS in
    PHASE 1 — the class-naming reason, not the positive control's downstream symptom."""
    result = run_checker(BARE)
    assert result.returncode == 1
    assert result.stdout.splitlines()[0] == "total-isolation: curl mechanism=netns-no-veth"
    c0 = [r for r in records(BARE / "curl") if r["canary"] == "C0"]
    assert len(c0) == 1 and c0[0]["rc"] == 7


@pytest.mark.parametrize("value, expected", [
    ("netns-no-veth", "total-isolation: curl mechanism=netns-no-veth"),
    ("", "total-isolation: curl mechanism="),
    (["veth-iptables"], "total-isolation: curl mechanism=['veth-iptables']"),
    ("veth-iptables ", "total-isolation: curl mechanism=veth-iptables "),
    ("VETH-IPTABLES", "total-isolation: curl mechanism=VETH-IPTABLES"),
], ids=["wrong-mechanism", "empty-mechanism", "list-mechanism", "trailing-space-mechanism",
        "case-variant-mechanism"])
def test_a_mechanism_mutation_is_rejected_by_class(tmp_path, value, expected):
    """MUTANT (the hollow green): the veth-iptables bundle's gate.json relabelled to ANY other
    mechanism is refused in PHASE 1 by class. An exact-equality allow-list of ONE value (never a
    blacklist), so a wrong value, an empty value, a non-string value and a whitespace-padded
    value are each named in the reason's `mechanism=` tail in its own str form — no
    normalisation."""
    bundle = copy_bundle(tmp_path)
    patch_json(bundle / "curl" / "gate.json", mechanism=value)
    result = run_checker(bundle)
    assert result.returncode == 1
    assert result.stdout.splitlines()[0] == expected


def test_total_isolation_precedes_a_disabled_gate(tmp_path):
    """ORDER: the mechanism guard runs in PHASE 1 BEFORE the gate-state check — a bundle that is
    BOTH total-isolation and gate-disabled is refused for the mechanism, not the gate, so the
    class verdict cannot be masked by the gate verdict's later position."""
    bundle = copy_bundle(tmp_path)
    patch_json(bundle / "curl" / "gate.json", mechanism="netns-no-veth", gate="disabled")
    result = run_checker(bundle)
    assert result.returncode == 1
    assert result.stdout.splitlines()[0] == "total-isolation: curl mechanism=netns-no-veth"


def test_a_non_first_unit_mechanism_is_rejected_by_class(tmp_path):
    """EVERY run unit (the seed's clause): the two-unit synthetic bundle with only its SECOND unit
    relabelled total-isolation is refused for THAT unit — a guard applied to `units[0]` alone
    (VERIFY-E1-R1 M11) survives every single-unit test above and dies here."""
    bundle = copy_bundle(tmp_path, SYNTHETIC)
    patch_json(bundle / "hermes-acp" / "gate.json", mechanism="netns-no-veth")
    result = run_checker(bundle, "--units", "curl,hermes-acp")
    assert result.returncode == 1
    assert result.stdout.splitlines()[0] == "total-isolation: hermes-acp mechanism=netns-no-veth"


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
         "10.201.1.1:12800", str(tmp_path / "ev"), "", "sandbox"],
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


def _in_ns_listener(ns, port, tmp_path):
    """Start a loopback-only HTTP stand-in INSIDE the namespace and return its Popen handle.
    The readiness probe also runs inside the namespace; the caller owns PID-scoped cleanup."""
    script = tmp_path / "loopback_standin.py"
    script.write_text("""\
import http.server
import socketserver
import sys

class Handler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(b'{"ok":true}')

    def log_message(self, *args):
        pass

socketserver.TCPServer(("127.0.0.1", int(sys.argv[1])), Handler).serve_forever()
""")
    process = subprocess.Popen(
        ["ip", "netns", "exec", ns, sys.executable, str(script), str(port)],
        stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, text=True)
    deadline = time.monotonic() + 5
    while time.monotonic() < deadline:
        if process.poll() is not None:
            stderr = process.stderr.read() if process.stderr is not None else ""
            raise AssertionError(f"loopback stand-in exited: {stderr}")
        probe = subprocess.run(
            ["ip", "netns", "exec", ns, "curl", "-fsS", "--max-time", "1",
             f"http://127.0.0.1:{port}/v1/models"],
            capture_output=True, text=True, timeout=3)
        if probe.returncode == 0:
            return process
        time.sleep(0.1)
    process.terminate()
    process.wait(timeout=5)
    raise AssertionError("loopback stand-in did not become ready inside the namespace")


@NEEDS_NETNS
def test_the_motivating_instance_is_a_total_isolation_class(tmp_path):
    """The motivating instance (anti-hollow-green tactic 11): the verifier's exact topology,
    re-derived live through the REAL collector (`run_canaries.sh`) and the REAL checker.

    An isolated namespace (same DROP gate, no selective-egress veth) with ONE internal veth pair
    (both ends inside the namespace; not the derived name, so the detector still reads
    netns-no-veth) and a loopback stand-in on the allowed port INSIDE the namespace: the positive
    control CAN pass (the listener is reachable over the namespace's own loopback), so the old
    downstream symptom (the positive-control failure) never fires — yet the bundle is
    total-isolation and must be refused by its class. That is exactly the hollow green F1: a
    mechanism the checker emits and records but never asserts. On the PIN's checker this bundle
    PASSES (rc 0); after the guard it fails with the class reason, first line."""
    ns = f"s0-05-e1-{uuid.uuid4().hex[:8]}"
    port = 12800
    root = tmp_path / "evidence"
    listener = None
    try:
        # The internal veth pair lives entirely inside the namespace: both ends have their own
        # on-link address in the same netns, creating the traffic that advances the DROP counter.
        # Neither end has the derived `en…` name the detector probes for, so egress_ns_mechanism
        # still reads netns-no-veth (total isolation) even though a veth exists.
        result = _lib(
            f'egress_ns_create_isolated {ns} 127.0.0.1:{port} || exit 1',
            f'ip -n {ns} link add ve1a type veth peer name ve1b || exit 1',
            f'ip -n {ns} address add 192.0.2.1/31 dev ve1a || exit 1',
            f'ip -n {ns} address add 192.0.2.0/31 dev ve1b || exit 1',
            f'ip -n {ns} link set ve1a up && ip -n {ns} link set ve1b up',
            # A routed, NON-local /24 behind ve1a: C6's target must lie outside the namespace's
            # own addresses, or its packets go over loopback (`-o lo -j ACCEPT`) and the DROP
            # counter never advances — VERIFY-E1-R1 F1 measured `0 -> 0` on the first shape of
            # this test and `0 -> 5` with this route (the counter VERIFY-E1 F1 reported).
            f'ip -n {ns} route add 198.51.100.0/24 dev ve1a || exit 1',
            f'ip -n {ns} link show',
            f'egress_ns_mechanism {ns}',
            f'egress_ns_gate_state {ns}')
        assert result.returncode == 0, result.stderr
        assert result.stdout.splitlines()[-2] == "netns-no-veth", result.stdout
        assert result.stdout.splitlines()[-1] == "enabled", result.stdout
        # The loopback stand-in runs INSIDE the namespace on its own loopback (reachable by the
        # canaries, which also run in the ns, under the gate's lo-ACCEPT rules). It makes C0 pass
        # even though the namespace has no route out — the downstream symptom never fires.
        listener = _in_ns_listener(ns, port, tmp_path)
        assert listener.poll() is None, "loopback stand-in did not stay live in the namespace"
        # The REAL collector, unmodified: it records the mechanism it OBSERVES (netns-no-veth),
        # the gate state (enabled), and the canaries. The stand-in lets C0 pass; C6 targets a
        # routed address behind ve1a (never a local one), so its packets reach the DROP policy and
        # the counter advances despite total isolation. The other canaries fail or are recorded —
        # all of it irrelevant to the PHASE 1 guard.
        run = subprocess.run(
            ["bash", str(PROOF / "run_canaries.sh"), "curl", ns, f"127.0.0.1:{port}",
             str(root), "198.51.100.7:12801", "sandbox"],
            capture_output=True, text=True, timeout=120)
        assert run.returncode == 0, run.stderr
        gate = json.loads((root / "curl" / "gate.json").read_text())
        rows = records(root / "curl")
        c0 = [row for row in rows if row["canary"] == "C0"]
        c6 = [row for row in rows if row["canary"] == "C6"]
        assert gate["mechanism"] == "netns-no-veth" and gate["gate"] == "enabled"
        assert len(c0) == 1 and c0[0]["rc"] == 0 and 200 <= c0[0]["http_status"] < 300
        # The gate must have FIRED on this bundle (a timed-out C6, the counter advanced): only then
        # is the pre-repair checker's verdict the rc-0 PASS the docstring names, and not the
        # `gate-inert` refusal VERIFY-E1-R1 F1 found behind the first shape of this test.
        runtime = json.loads((root / "curl" / "runtime.json").read_text())
        assert runtime["drop_counter_after"] > runtime["drop_counter_before"], runtime
        assert len(c6) == 1 and c6[0]["rc"] == 28, c6
        # The REAL checker, unmodified, on the bundle the collector wrote.
        result = run_checker(root)
        assert result.returncode == 1, result.stdout
        assert result.stdout.splitlines()[0] == "total-isolation: curl mechanism=netns-no-veth", \
            result.stdout
    finally:
        if listener is not None:
            listener.terminate()
            try:
                listener.wait(timeout=5)
            except subprocess.TimeoutExpired:
                listener.kill()
                listener.wait(timeout=5)
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


# ===================================================================== E2 — new tests


RUNNER = PROOF / "tools" / "pc" / "run_s0_05_units.sh"


@NEEDS_NETNS
def test_address_plan_collision_is_refused(tmp_path):
    """F6: two namespaces whose names derive one /24 octet (107) cannot both exist. The second
    create returns 65 with the exact message and leaves nothing behind; the first still passes
    its positive control."""
    ns1 = "s0-05-hermes-acp"
    ns2 = "s0-05-u7"
    port = 18080
    # server script in a file for reliability
    server = tmp_path / "server.py"
    server.write_text(
        "import http.server, socketserver, sys\n"
        "class H(http.server.BaseHTTPRequestHandler):\n"
        "    def do_GET(self):\n"
        "        self.send_response(200)\n"
        "        self.end_headers()\n"
        "        self.wfile.write(b'ok')\n"
        "    def log_message(self, *a): pass\n"
        "socketserver.TCPServer.allow_reuse_address = True\n"
        "socketserver.TCPServer(('0.0.0.0', int(sys.argv[1])), H).serve_forever()\n")
    listener = None
    try:
        # verify both hash to the same octet
        r = _lib(f'_egress_octet {ns1}', f'_egress_octet {ns2}')
        o1, o2 = r.stdout.strip().split()
        assert o1 == o2 == "107"
        # create the first
        r = _lib(f'egress_ns_create {ns1} 10.201.107.1:{port}')
        assert r.returncode == 0, r.stderr
        # start a listener on the host side for the positive control
        listener = subprocess.Popen(
            [sys.executable, str(server), str(port)],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        # wait for the listener to become ready
        deadline = time.monotonic() + 5
        while time.monotonic() < deadline:
            probe = subprocess.run(
                ["curl", "-fsS", "--max-time", "1", f"http://127.0.0.1:{port}/"],
                capture_output=True, text=True, timeout=3)
            if probe.returncode == 0:
                break
            time.sleep(0.1)
        else:
            raise AssertionError("listener did not become ready")
        # the second create must fail
        r = _lib(f'egress_ns_create {ns2} 10.201.107.1:{port}')
        assert r.returncode == 65, (r.returncode, r.stderr, r.stdout)
        assert f"address-plan-collision: {ns2} 10.201.107.0/24" in r.stderr
        # nothing of ns2 was created
        census = subprocess.run(["ip", "netns", "list"], capture_output=True, text=True).stdout
        assert ns2 not in census
        # the first namespace's positive control still works
        r = _lib(f'egress_ns_run {ns1} curl -sS --connect-timeout 3 -o /dev/null '
                 f'-w "%{{http_code}}" http://10.201.107.1:{port}/')
        assert r.stdout.strip() == "200", r.stdout
    finally:
        if listener is not None:
            listener.terminate()
            try:
                listener.wait(timeout=5)
            except subprocess.TimeoutExpired:
                listener.kill()
                listener.wait(timeout=5)
        _lib(f'egress_ns_destroy {ns1}')
        _lib(f'egress_ns_destroy {ns2}')
    census = subprocess.run(["ip", "netns", "list"], capture_output=True, text=True).stdout
    assert ns1 not in census and ns2 not in census


@NEEDS_NETNS
def test_live_sibling_namespace_is_refused():
    """F23: a create of a name whose owner is a live process returns 65; the sibling's veth is
    still present. A stale owner (dead pid) allows the create to succeed."""
    ns = f"s0-05-e2-{uuid.uuid4().hex[:8]}"
    try:
        # In a single bash process: create the namespace (records $$), then from a child bash
        # (different $$, while parent is alive) try to re-create.
        result = subprocess.run(
            ["bash", "-c",
             f'. {LIB}\n'
             f'egress_ns_create {ns} 10.201.1.1:1 || exit 10\n'
             f'echo "owner=$(cat /run/s0-05-egress/{ns}.owner)"\n'
             f'echo "self=$$"\n'
             f'bash -c \'. {LIB}; egress_ns_create {ns} 10.201.1.1:1; echo inner_rc=$?\''
             f' 2>/tmp/e2_sibling.err\n'
             f'cat /tmp/e2_sibling.err\n'
             f'egress_ns_mechanism {ns}\n'
             f'ip netns exec {ns} ip -o link show | grep -c en\n'],
            capture_output=True, text=True, timeout=30)
        assert result.returncode == 0, result.stderr
        lines = result.stdout.strip().split('\n')
        # owner was recorded
        assert lines[0].startswith("owner=")
        owner_pid = lines[0].split("=")[1]
        assert lines[1] == f"self={owner_pid}"
        # inner create was refused
        assert "inner_rc=65" in result.stdout, lines
        assert f"namespace-live: {ns}" in result.stdout, lines
        # veth still present (mechanism is veth-iptables)
        assert "veth-iptables" in result.stdout, lines
        # at least one en* link inside the namespace
        assert int(lines[-1]) >= 1, lines
    finally:
        _lib(f'egress_ns_destroy {ns}')
    # stale owner: after the first bash exits, the owner pid is dead; re-create succeeds
    result2 = _lib(f'egress_ns_create {ns} 10.201.1.1:1')
    assert result2.returncode == 0, result2.stderr
    _lib(f'egress_ns_destroy {ns}')
    assert ns not in subprocess.run(
        ["ip", "netns", "list"], capture_output=True, text=True).stdout


@NEEDS_NETNS
def test_destroy_kills_all_namespace_processes():
    """F7+F9: a process started inside a namespace (as the runner starts a unit:
    egress_ns_run <ns> setsid ...) is gone after egress_ns_destroy, and no process's
    net-namespace inode equals the deleted namespace's."""
    ns = f"s0-05-e2-{uuid.uuid4().hex[:8]}"
    proc = None
    try:
        _lib(f'egress_ns_create {ns} 10.201.1.1:1')
        # start a process inside the namespace the way the runner does
        proc = subprocess.Popen(
            ["ip", "netns", "exec", ns, "setsid", "/usr/bin/python3", "-c",
             "import time; time.sleep(300)"],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        time.sleep(1)
        assert proc.poll() is None, "process exited early"
        # get pids inside the namespace and their net inode
        pids_out = subprocess.run(
            ["ip", "netns", "pids", ns], capture_output=True, text=True).stdout.strip()
        unit_pids = [p for p in pids_out.split() if p]
        assert unit_pids, "no pids in namespace"
        ino = os.stat(f"/proc/{unit_pids[0]}/ns/net").st_ino
        # destroy
        _lib(f'egress_ns_destroy {ns}')
        time.sleep(0.5)
        # every recorded pid is dead or has a different net namespace
        for pid in unit_pids:
            try:
                new_ino = os.stat(f"/proc/{pid}/ns/net").st_ino
                assert new_ino != ino, f"pid {pid} still in the destroyed namespace"
            except FileNotFoundError:
                pass  # dead — good
    finally:
        if proc is not None and proc.poll() is None:
            proc.terminate()
            try:
                proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                proc.kill()
                proc.wait(timeout=5)
        _lib(f'egress_ns_destroy {ns}')
    assert ns not in subprocess.run(
        ["ip", "netns", "list"], capture_output=True, text=True).stdout


@NEEDS_NETNS
def test_runner_live_leg(tmp_path):
    """Runner-level live test: run_s0_05_units.sh <tmp> hermes-acp with a test-local stand-in
    launcher and a local listener on the unit's veth host address.
    F14: the stand-in records its pid and argv; the test asserts the record exists, that the
    argv equals the LAUNCH row as given (kills M16), and that the stand-in is dead after its
    unit's leg and before the next unit's leg (kills M17).
    Also asserts: no stand-in process remains, no namespace remains, units.json carries the
    F10 row, hermes-acp row is 'run', and a concurrent invocation is refused."""
    ns = "s0-05-hermes-acp"
    port = 18080
    # F14: the stand-in records its pid, argv and net namespace inode to a file.
    record_file = tmp_path / "standin_record.json"
    tools_dir = tmp_path / "tools" / "pc"
    tools_dir.mkdir(parents=True)
    (tools_dir / "pc_launch.py").write_text(
        "#!/usr/bin/env python3\n"
        "import json, os, sys, time\n"
        f"record = {{'pid': os.getpid(), 'argv': sys.argv, "
        f"'net_ino': os.stat('/proc/self/ns/net').st_ino}}\n"
        f"with open({str(record_file)!r}, 'w') as f:\n"
        f"    json.dump(record, f)\n"
        "time.sleep(300)\n")
    (tools_dir / "pc_launch.py").chmod(0o755)
    # start a listener on all interfaces for the preflight check
    listener_script = tmp_path / "listener.py"
    listener_script.write_text(
        "import http.server,socketserver as s,sys\n"
        "class H(http.server.BaseHTTPRequestHandler):\n"
        "  def do_GET(self):\n"
        "    self.send_response(200);self.end_headers();self.wfile.write(b'{}')\n"
        "  def log_message(self,*a):pass\n"
        "s.TCPServer.allow_reuse_address = True\n"
        "s.TCPServer(('0.0.0.0',int(sys.argv[1])),H).serve_forever()\n")
    listener = subprocess.Popen(
        [sys.executable, str(listener_script), str(port)],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    evidence = tmp_path / "evidence"
    try:
        time.sleep(0.5)
        env = {**os.environ, "S0_01_TOOLS": str(tools_dir),
               "ALLOWED_HERMES": f"10.201.107.1:{port}"}
        # Run the runner in a subprocess; it will create the namespace, launch the stand-in,
        # run canaries, and destroy. We also test F23 concurrency by checking the owner file
        # during the run.
        # First: run a quick concurrent test. Create the namespace, hold it, try a second runner.
        r = subprocess.run(
            ["bash", "-c",
             f'. {LIB}\n'
             f'egress_ns_create {ns} 10.201.107.1:{port}\n'
             f'echo "created, owner=$(cat /run/s0-05-egress/{ns}.owner)"\n'
             f'bash -c \'. {LIB}; egress_ns_create {ns} 10.201.107.1:{port}; echo rc=$?\''
             f' 2>/tmp/e2_runner_sibling.err\n'
             f'cat /tmp/e2_runner_sibling.err\n'
             f'egress_ns_destroy {ns}'],
            capture_output=True, text=True, timeout=30)
        assert r.returncode == 0, r.stderr
        assert "namespace-live:" in r.stdout or "namespace-live:" in r.stderr, r.stdout
        assert "rc=65" in r.stdout, r.stdout
        # Now run the actual runner
        runner = subprocess.run(
            ["bash", str(RUNNER), str(evidence), "hermes-acp"],
            capture_output=True, text=True, timeout=120, env=env)
        # The runner body is top-level code: a bash error line (e.g. `local` outside a
        # function, coordinator touch at the E2 landing) must never reach its stderr.
        assert "can only be used in a function" not in runner.stderr, runner.stderr
        # No file of ours may sit in /etc/netns/<ns>/: `ip netns exec` bind-mounts every file there
        # over /etc inside the namespace (coordinator touch at the E2 landing: the F23 owner file).
        assert "Bind /etc/netns/" not in runner.stderr, runner.stderr
        # F14: assert the stand-in actually ran (kills M16: a bash-wrapped launch never runs it).
        assert record_file.exists(), "stand-in record not found: the stand-in never ran"
        record = json.loads(record_file.read_text())
        assert "pid" in record, record
        assert "argv" in record, record
        # F14: assert argv matches the LAUNCH row as given — the stand-in was run directly,
        # not wrapped in bash.
        expected_script = str(tools_dir / "pc_launch.py")
        assert record["argv"][0] == expected_script, \
            f"argv[0] should be the script path, got {record['argv']}"
        # F14: assert the stand-in is dead after its leg (kills M17: kill-only leaves it alive).
        standin_pid = record["pid"]
        try:
            os.kill(standin_pid, 0)
            raise AssertionError(
                f"stand-in pid {standin_pid} still alive after its unit's leg")
        except OSError:
            pass  # dead — good
        # verify no stand-in process remains with the stand-in's path
        standin_procs = subprocess.run(
            ["pgrep", "-f", str(tools_dir / "pc_launch.py")],
            capture_output=True, text=True)
        assert standin_procs.returncode != 0, \
            f"stand-in still running: {standin_procs.stdout.strip()}"
        # verify no namespace remains
        census = subprocess.run(
            ["ip", "netns", "list"], capture_output=True, text=True).stdout
        assert ns not in census, census
        # verify units.json carries the F10 row and the hermes-acp row is 'run'
        units_json = json.loads((evidence / "units.json").read_text())
        units_list = units_json["units"]
        backend_row = [u for u in units_list if u["unit"] == "s0-01-backend"]
        assert len(backend_row) == 1, units_list
        assert backend_row[0]["status"] == "not-run"
        assert "not a docs/05" in backend_row[0]["reason"]
        # F14: assert hermes-acp row is 'run' (not 'not-run')
        hermes_row = [u for u in units_list if u["unit"] == "hermes-acp"]
        assert len(hermes_row) == 1, units_list
        assert hermes_row[0]["status"] == "run", hermes_row[0]
    finally:
        listener.terminate()
        try:
            listener.wait(timeout=5)
        except subprocess.TimeoutExpired:
            listener.kill()
            listener.wait(timeout=5)
        _lib(f'egress_ns_destroy {ns}')
    assert ns not in subprocess.run(
        ["ip", "netns", "list"], capture_output=True, text=True).stdout


def test_shebang_matches_launch_interpreter():
    """F8: every LAUNCH row's interpreter agrees with its target script's shebang. A bash
    script can never again be handed to python3."""
    # Parse the LAUNCH rows from the runner
    runner_text = RUNNER.read_text()
    launch_lines = re.findall(r'LAUNCH\[[\w-]+\]="([^"]+)"', runner_text)
    assert launch_lines, "no LAUNCH rows found"
    for row in launch_lines:
        parts = row.split()
        interpreter = parts[0]  # e.g. /usr/bin/python3
        # find the target script in the row (the first non-flag argument after the interpreter)
        target = None
        for part in parts[1:]:
            if not part.startswith("-"):
                # resolve $S0_01_TOOLS
                target = part.replace("$S0_01_TOOLS", str(PROOF.parent / "S0-01" / "tools" / "pc"))
                break
        assert target is not None, f"no target script in LAUNCH row: {row}"
        target_path = Path(target)
        assert target_path.is_file(), f"target script not found: {target_path}"
        shebang = target_path.read_text().split('\n')[0]
        # interpreter /usr/bin/python3 requires a python shebang
        if "python" in interpreter:
            assert "python" in shebang, \
                f"LAUNCH row uses {interpreter} but shebang is {shebang!r}: {target_path}"
        elif "bash" in interpreter:
            assert "bash" in shebang or "sh" in shebang, \
                f"LAUNCH row uses {interpreter} but shebang is {shebang!r}: {target_path}"


@pytest.mark.skipif(shutil.which("ip") is None, reason="iproute2 absent; NOT run here")
def test_unreadable_counter_creates_no_canaries_file(tmp_path):
    """F3+F17: an exit-3 collection (unreadable DROP counter) leaves no canaries.jsonl behind.
    This discriminates: with the DROP_BEFORE guard removed (mutant m4) the canaries run and
    write records before the DROP_AFTER guard exits 3."""
    ev = tmp_path / "ev"
    result = subprocess.run(
        ["bash", str(PROOF / "run_canaries.sh"), "curl", "s0-05-e2-nonexistent-ns",
         "10.201.1.1:12800", str(ev), "", "sandbox"],
        capture_output=True, text=True, timeout=120)
    assert result.returncode == 3, (result.returncode, result.stdout, result.stderr)
    assert "cannot read the OUTPUT DROP counter" in result.stderr
    assert not (ev / "curl" / "canaries.jsonl").exists(), \
        "canaries.jsonl should not exist after an exit-3 collection"


@pytest.mark.parametrize("venue,expected_rc", [
    ("", 64), ("synthetic", 64), ("pc", None), ("sandbox", None),
], ids=["missing", "invalid", "pc-valid", "sandbox-valid"])
def test_venue_required_and_validated(tmp_path, venue, expected_rc):
    """F11: venue must be sandbox or pc; anything else or nothing exits 64."""
    args = ["bash", str(PROOF / "run_canaries.sh"), "curl", "s0-05-e2-nonexistent-ns",
            "10.201.1.1:12800", str(tmp_path / "ev"), ""]
    if venue:
        args.append(venue)
    result = subprocess.run(args, capture_output=True, text=True, timeout=30)
    if expected_rc is not None:
        assert result.returncode == expected_rc, (result.returncode, result.stderr)
        assert "venue must be sandbox or pc" in result.stderr
    else:
        # valid venue: should NOT fail on venue (may fail on something else like DROP counter)
        assert "venue must be sandbox or pc" not in result.stderr


@pytest.mark.parametrize("units,label", [
    ("", "empty-string"), (",", "bare-comma"), ("a,,b", "interior-empty"),
], ids=["empty-string", "bare-comma", "interior-empty"])
def test_empty_unit_name_rejected(tmp_path, units, label):
    """F18: --units refuses an empty unit name in any of three spellings."""
    result = run_checker(MECHANISM, "--units", units)
    assert result.returncode == 64, (result.returncode, result.stdout)
    assert "usage: --units carries an empty unit name" in result.stdout


@NEEDS_NETNS
def test_destroy_kills_sigterm_ignoring_process():
    """F1: a process that ignores SIGTERM (trap '' TERM) is killed by the SIGKILL escalation
    in egress_ns_destroy and is dead at return."""
    ns = f"s0-05-e2-{uuid.uuid4().hex[:8]}"
    try:
        _lib(f'egress_ns_create {ns} 10.201.1.1:1')
        # start a SIGTERM-ignoring process inside the namespace
        proc = subprocess.Popen(
            ["ip", "netns", "exec", ns, "setsid", "bash", "-c",
             "trap '' TERM; sleep 300"],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        time.sleep(0.5)
        assert proc.poll() is None, "SIGTERM-ignoring process exited early"
        pids_out = subprocess.run(
            ["ip", "netns", "pids", ns], capture_output=True, text=True).stdout.strip()
        unit_pids = [p for p in pids_out.split() if p]
        assert unit_pids, "no pids in namespace"
        ino = os.stat(f"/proc/{unit_pids[0]}/ns/net").st_ino
        _lib(f'egress_ns_destroy {ns}')
        # every recorded pid is dead or in a different namespace AT RETURN
        for pid in unit_pids:
            try:
                new_ino = os.stat(f"/proc/{pid}/ns/net").st_ino
                assert new_ino != ino, f"pid {pid} still in the destroyed namespace"
            except FileNotFoundError:
                pass  # dead — good
    finally:
        if proc.poll() is None:
            proc.kill()
            proc.wait(timeout=5)
        _lib(f'egress_ns_destroy {ns}')


@NEEDS_NETNS
def test_create_race_one_wins():
    """F2: two concurrent creates on the same name — exactly one returns 0, the other returns 65
    with the named refusal. The winner's namespace, processes and owner record are intact."""
    ns = f"s0-05-e2-{uuid.uuid4().hex[:8]}"
    try:
        result = subprocess.run(
            ["bash", "-c",
             f'. {LIB}\n'
             # First create claims the name.
             f'egress_ns_create {ns} 10.201.1.1:1\n'
             f'rc1=$?\n'
             f'echo "rc1=$rc1"\n'
             # From a child bash (different $$), try to create the same name.
             f'bash -c \'. {LIB}; egress_ns_create {ns} 10.201.1.1:1; echo rc2=$?\' 2>&1\n'
             # Check that the winner's namespace and owner record are intact.
             f'echo "owner=$(cat /run/s0-05-egress/{ns}.owner 2>/dev/null)"\n'
             f'echo "self=$$"\n'
             f'ip netns list | grep -c {ns}\n'],
            capture_output=True, text=True, timeout=30)
        lines = result.stdout.strip().split('\n')
        # first create succeeded
        assert "rc1=0" in result.stdout, lines
        # second create refused
        assert "rc2=65" in result.stdout, lines
        assert f"namespace-live: {ns}" in result.stdout, lines
        # owner record is our pid (the winner)
        owner_line = [l for l in lines if l.startswith("owner=")][0]
        self_line = [l for l in lines if l.startswith("self=")][0]
        assert owner_line.split("=")[1] == self_line.split("=")[1], lines
        # namespace still exists (exactly 1)
        assert lines[-1] == "1", lines
    finally:
        _lib(f'egress_ns_destroy {ns}')


@NEEDS_NETNS
def test_same_shell_recreate_succeeds():
    """M22: the same bash process can call egress_ns_create twice on the same name (idempotent
    re-create). The create's destroy-first step cleans up the previous namespace, and the !=$$
    clause lets the same owner through. Dropping that clause makes the second call fail rc 65."""
    ns = f"s0-05-e2-{uuid.uuid4().hex[:8]}"
    try:
        result = subprocess.run(
            ["bash", "-c",
             f'. {LIB}\n'
             f'egress_ns_create {ns} 10.201.1.1:1\n'
             f'echo "first_rc=$?"\n'
             # Call create AGAIN from the same shell, without explicit destroy.
             # The create is idempotent: its internal destroy-first cleans up.
             f'egress_ns_create {ns} 10.201.1.1:1\n'
             f'echo "second_rc=$?"\n'],
            capture_output=True, text=True, timeout=30)
        assert "first_rc=0" in result.stdout, result.stdout
        assert "second_rc=0" in result.stdout, (result.stdout, result.stderr)
    finally:
        _lib(f'egress_ns_destroy {ns}')


@NEEDS_NETNS
def test_cleanup_does_not_destroy_sibling_namespace():
    """F3: runner A exits while runner B holds a namespace for the same unit name. A's cleanup
    must not destroy B's namespace. B's canary process and owner record survive."""
    ns = f"s0-05-e2-{uuid.uuid4().hex[:8]}"
    try:
        # Runner A creates, then destroys (simulating a completed leg).
        # Runner B (child bash, different $$) re-creates the same name.
        # A's ownership-checking cleanup (NS_LIVE still has the name) must skip it.
        result = subprocess.run(
            ["bash", "-c",
             f'. {LIB}\n'
             f'egress_ns_create {ns} 10.201.1.1:1 || exit 10\n'
             f'A_PID=$$\n'
             f'echo "A_self=$A_PID"\n'
             # A destroys its leg (simulates in-loop destroy that prunes NS_LIVE).
             f'egress_ns_destroy {ns}\n'
             # Runner B (child bash, different $$) re-creates.
             f'bash -c \'. {LIB}; egress_ns_create {ns} 10.201.1.1:1 || exit 10;'
             f' echo "B_self=$$";'
             f' echo "B_owner=$(cat /run/s0-05-egress/{ns}.owner 2>/dev/null)"\'\n'
             # A's cleanup: ownership check prevents destroying B's namespace.
             f'owner_pid=$(cat "$(egress_ns_owner_file {ns})" 2>/dev/null)\n'
             f'if [ "$owner_pid" = "$A_PID" ]; then\n'
             f'  egress_ns_destroy {ns}\n'
             f'  echo "A_destroyed={ns}"\n'
             f'else\n'
             f'  echo "A_skipped={ns} owner=$owner_pid"\n'
             f'fi\n'
             f'echo "ns_exists=$(ip netns list | grep -c {ns})"\n'
             f'echo "owner_after=$(cat /run/s0-05-egress/{ns}.owner 2>/dev/null)"\n'],
            capture_output=True, text=True, timeout=30)
        assert result.returncode == 0, result.stderr
        # A skipped the destroy (not its own)
        assert f"A_skipped={ns}" in result.stdout, result.stdout
        assert "A_destroyed=" not in result.stdout, result.stdout
        # namespace still exists
        assert "ns_exists=1" in result.stdout, result.stdout
        # B's owner record still present and equals B's pid
        b_self = [l for l in result.stdout.split('\n') if l.startswith("B_self=")]
        owner_after = [l for l in result.stdout.split('\n') if l.startswith("owner_after=")]
        assert b_self and owner_after, result.stdout
        assert b_self[0].split("=")[1] == owner_after[0].split("=")[1], result.stdout
    finally:
        _lib(f'egress_ns_destroy {ns}')


@NEEDS_NETNS
def test_units_json_quotes_in_reason(tmp_path):
    """F4: a reason carrying double quote, backslash and newline is encoded correctly in
    units.json. check_egress.py parses units.json and the reason equals the input exactly."""
    evidence = tmp_path / "evidence"
    tools_dir = tmp_path / "tools" / "pc"
    tools_dir.mkdir(parents=True)
    (tools_dir / "pc_launch.py").write_text("#!/usr/bin/env python3\nimport time\ntime.sleep(300)\n")
    reason_value = 'test "quote\\ and\nnewline'
    # Use a ALLOWED_HERMES that will be rejected by validation (triggers the reason path).
    env = {**os.environ, "S0_01_TOOLS": str(tools_dir),
           "ALLOWED_HERMES": reason_value}
    subprocess.run(
        ["bash", str(RUNNER), str(evidence), "hermes-acp"],
        capture_output=True, text=True, timeout=30, env=env)
    units_data = json.loads((evidence / "units.json").read_text())
    hermes_row = [u for u in units_data["units"] if u["unit"] == "hermes-acp"]
    assert len(hermes_row) == 1, units_data
    assert hermes_row[0]["status"] == "not-run"
    # The reason must contain the original value (the validation error includes the input).
    assert reason_value in hermes_row[0]["reason"], hermes_row[0]["reason"]


@NEEDS_NETNS
def test_runner_refusal_does_not_destroy_sibling(tmp_path):
    """F3/M20: when runner B's create is refused (runner A holds the namespace via a LIVE pid),
    B must not destroy A's namespace. The runner path: B's create returns 65 (namespace-live),
    B records not-run and continues. A's namespace, canary and owner record survive."""
    ns = "s0-05-hermes-acp"
    port = 18081
    tools_dir = tmp_path / "tools" / "pc"
    tools_dir.mkdir(parents=True)
    (tools_dir / "pc_launch.py").write_text(
        "#!/usr/bin/env python3\nimport time\ntime.sleep(300)\n")
    (tools_dir / "pc_launch.py").chmod(0o755)
    # Runner A: a bash that creates the namespace and sleeps (keeping its PID alive).
    holder = subprocess.Popen(
        ["bash", "-c",
         f'. {LIB}\n'
         f'egress_ns_create {ns} 10.201.107.1:{port} || exit 10\n'
         f'ip netns exec {ns} sleep 300 &\n'
         f'echo READY\n'
         f'sleep 300\n'],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    try:
        # Wait for the holder to print READY.
        import select
        ready = b""
        for _ in range(100):
            r, _, _ = select.select([holder.stdout], [], [], 0.1)
            if r:
                ready += holder.stdout.read1(1024)
                if b"READY" in ready:
                    break
        assert b"READY" in ready, f"holder did not become ready: {ready}"
        # Runner B: the real runner, which will fail to create the namespace.
        env = {**os.environ, "S0_01_TOOLS": str(tools_dir),
               "ALLOWED_HERMES": f"10.201.107.1:{port}"}
        evidence_b = tmp_path / "evidence_b"
        subprocess.run(
            ["bash", str(RUNNER), str(evidence_b), "hermes-acp"],
            capture_output=True, text=True, timeout=30, env=env)
        # B's units.json should say "not-run" for hermes-acp.
        units_b = json.loads((evidence_b / "units.json").read_text())
        hermes_row = [u for u in units_b["units"] if u["unit"] == "hermes-acp"]
        assert len(hermes_row) == 1, units_b
        assert hermes_row[0]["status"] == "not-run", hermes_row[0]
        # A's namespace must still exist.
        census = subprocess.run(
            ["ip", "netns", "list"], capture_output=True, text=True).stdout
        assert ns in census, f"A's namespace destroyed by B: {census}"
        # holder is still alive (its PID is in the owner file).
        assert holder.poll() is None, "holder died unexpectedly"
    finally:
        holder.terminate()
        try:
            holder.wait(timeout=5)
        except subprocess.TimeoutExpired:
            holder.kill()
            holder.wait(timeout=5)
        _lib(f'egress_ns_destroy {ns}')


@pytest.mark.parametrize("entry", [
    "10.0.0.1/8:443", "host.example:443", ":8080",
    "1..2:80", "....:80", "999.1.1.1:80", "1.2.3.4.5:80",
    "1.2.3:80", "010.0.0.1:80", "1.2.3.4:0", "1.2.3.4:65536", "1.2.3.4:080",
], ids=["cidr", "hostname", "empty-host",
        "double-dot", "all-dots", "octet-999", "five-octets",
        "three-octets", "leading-zero", "port-zero", "port-65536", "port-leading-zero"])
def test_allow_entry_must_be_ipv4_literal(entry):
    """F19/F11/F12: egress_ns_create refuses an entry whose host part is not a strict dotted-quad
    IPv4 literal (four decimal octets 0-255, no leading zeros) or whose port is outside 1-65535.
    The validation runs up front before any namespace/veth/rule/record work, so it needs no
    root and leaves nothing behind."""
    ns = f"s0-05-e2-{uuid.uuid4().hex[:8]}"
    result = _lib(f'egress_ns_create {ns} "{entry}"')
    assert result.returncode == 64, (result.returncode, result.stderr, result.stdout)
    assert "allow entry must be <ip>:<port>" in result.stderr
    # F11(iii): no namespace, no veth, no owner record left behind after a refusal.
    if netns_capable():
        census = subprocess.run(["ip", "netns", "list"], capture_output=True, text=True).stdout
        assert ns not in census, f"namespace leaked after refusal: {census}"
        veth = subprocess.run(["ip", "-o", "link", "show", "type", "veth"],
                              capture_output=True, text=True).stdout
        host_if = _lib(f'egress_ns_host_if {ns}').stdout.strip()
        assert host_if not in veth, f"veth leaked after refusal: {veth}"
        owner_file = f"/run/s0-05-egress/{ns}.owner"
        assert not os.path.exists(owner_file), f"owner record leaked: {owner_file}"
