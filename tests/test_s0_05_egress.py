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
import hashlib
import importlib.util
import json
import os
import re
import shutil
import signal
import stat
import subprocess
import sys
import tempfile
import time
import uuid
from pathlib import Path
from urllib.parse import urlsplit

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
def test_runner_live_leg(e3dir):
    """Runner-level live test: run_s0_05_units.sh <root> hermes-acp with a local listener on the
    unit's veth host address. E3: the unit is replaced by a stand-in ONLY through the runner's
    RECORDED override (A1) — the E2 form (an S0_01_TOOLS pc_launch.py stand-in) is retired with the
    S0-01 tool rows it stood in for.
    F14: the stand-in records its pid and argv; the test asserts the record exists, that the
    argv is the unit row as given (A1: the pinned realpath run directly, so argv[0] is that path
    under the kernel's shebang; kills M16), and that the stand-in is dead after its unit's leg
    (kills M17).
    Also asserts: no stand-in process remains, no namespace remains, units.json carries the
    F10 row, hermes-acp row is 'run', and a concurrent invocation is refused.
    E3, each asserted on this ONE real run: the override recorded on the unit row and refused by the
    checker as a live claim (A1); no row names an S0-01 tool, .markers or .secrets (A1); the unit's
    scratch tree and the census record (A2); stdin and stdout are pipes and the unit stopped on
    stdin EOF (A3); it ran as uid 65534 (A4); its environment is exactly the declared set, with no
    planted secret (A5); unit-identity.json names what ran, and the checker grades that REAL record
    against the real pins (A7); the allow entry was derived and the planted address ignored (A8)."""
    ns = "s0-05-hermes-acp"
    port = 18080
    listener = None
    evidence = e3dir / "evidence"
    env = _runner_env(e3dir, port)
    override = json.loads((e3dir / "override.json").read_text())
    standin = override["PINNED_AGENT_REALPATH"]
    try:
        listener = _listener(e3dir, port)
        # Before the leg: a concurrent create of the same name is refused while its owner lives.
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
            capture_output=True, text=True, timeout=240, env=env)
        # The runner body is top-level code: a bash error line (e.g. `local` outside a
        # function, coordinator touch at the E2 landing) must never reach its stderr.
        assert "can only be used in a function" not in runner.stderr, runner.stderr
        # No file of ours may sit in /etc/netns/<ns>/: `ip netns exec` bind-mounts every file there
        # over /etc inside the namespace (coordinator touch at the E2 landing: the F23 owner file).
        assert "Bind /etc/netns/" not in runner.stderr, runner.stderr
        # A1: the override is announced, and the retired inputs are named as ignored.
        assert "PIN OVERRIDE ACTIVE" in runner.stderr, runner.stderr
        assert "ALLOWED_HERMES, ALLOWED_BUZZACP and S0_01_TOOLS are retired" in runner.stderr
        # F14: assert the stand-in actually ran (kills M16: a bash-wrapped launch never runs it).
        records = _standin_records(e3dir)
        assert len(records) == 1, "stand-in record not found: the stand-in never ran"
        record = records[0]
        assert "pid" in record, record
        assert "argv" in record, record
        # F14 + A1 (a changed expectation: the E2 row was `python3 <S0-01 tool>`; the A1 row is the
        # pinned realpath itself): argv is exactly the unit row as launched.
        assert record["argv"] == [standin], record["argv"]
        assert not any(f in a for a in record["argv"] for f in ("proofs/S0-01/tools", ".markers", ".secrets"))
        # F14: assert the stand-in is dead after its leg (kills M17: kill-only leaves it alive).
        standin_pid = record["pid"]
        assert not _pid_alive(standin_pid), f"stand-in pid {standin_pid} still alive after its unit's leg"
        # verify no stand-in process remains with the stand-in's path
        standin_procs = subprocess.run(["pgrep", "-f", standin], capture_output=True, text=True)
        assert standin_procs.returncode != 0, \
            f"stand-in still running: {standin_procs.stdout.strip()}"
        # verify no namespace remains (and nothing else of the leg: E3 census)
        assert ns not in _netns_names()
        assert _census(ns) == CLEAN, _census(ns)
        # verify units.json carries the F10 row and the hermes-acp row is 'run'
        units_list = json.loads((evidence / "units.json").read_text())["units"]
        backend_row = [u for u in units_list if u["unit"] == "s0-01-backend"]
        assert len(backend_row) == 1, units_list
        assert backend_row[0]["status"] == "not-run"
        assert "not a docs/05" in backend_row[0]["reason"]
        assert "override" not in backend_row[0], backend_row      # absent units launch nothing
        hermes_row = [u for u in units_list if u["unit"] == "hermes-acp"]
        assert len(hermes_row) == 1, units_list
        assert hermes_row[0]["status"] == "run", hermes_row[0]
        # A1: the override is RECORDED on the unit row, naming exactly what was replaced ...
        assert hermes_row[0]["override"] == override, hermes_row[0]
        # ... and the checker refuses this REAL runner output as a live claim.
        checker_out = runner.stdout.split("=== checker ===\n", 1)[1]
        assert checker_out.splitlines()[0] == "units-manifest-invalid: hermes-acp override present", checker_out
        assert runner.returncode == 1, runner.returncode
        # A3: stdin and stdout were pipes, and the unit stopped on stdin EOF — before the backstop.
        assert (record["stdin"], record["stdout"], record["stop"]) == ("fifo", "fifo", "eof"), record
        assert "=== hermes-acp: exited 0 on stdin EOF ===" in runner.stdout, runner.stdout
        log = evidence / "hermes-acp.launch.log"
        assert stat.S_ISREG(log.lstat().st_mode) and "stand-in: serving" in log.read_text()
        # A4: the unit ran as the unit user, never root.
        assert (record["uid"], record["gid"]) == UNIT_USER, record
        # A5: the unit's environment is exactly the declared set — nothing inherited, no secret.
        scratch = evidence / "hermes-acp" / "scratch"
        assert record["env_keys"] == UNIT_ENV_KEYS, record["env_keys"]
        assert record["env"] == {"PATH": PINS.PINNED_PATH, "HOME": str(scratch / "home"),
                                 "HERMES_HOME": str(scratch / "hermes-home"), "LANG": "C.UTF-8",
                                 "PYTHONDONTWRITEBYTECODE": "1"}, record["env"]
        assert not [k for k in record["env_keys"] if REDACTED.search(k)], record["env_keys"]
        assert record["key_sha256"] is None and record["cwd"] == str(scratch / "home")
        # A2: the unit's own scratch tree, owned by the unit user; the S0-01 census recorded.
        for sub in ("home", "hermes-home"):
            st = (scratch / sub).stat()
            assert (st.st_uid, st.st_gid, stat.S_IMODE(st.st_mode)) == (*UNIT_USER, 0o700), sub
        census = json.loads((evidence / "s0-01-census.json").read_text())
        assert census["base"] == os.path.dirname(PINS.PINNED_HERMES_HOME), census
        assert census["changed"] == [] and census["tree"].startswith("absent on this venue"), census
        # A7: unit-identity.json names the process that ran ...
        identity = json.loads((evidence / "hermes-acp" / "unit-identity.json").read_text())
        assert identity == {"unit": "hermes-acp", "pid": standin_pid, "exe_realpath": _agent_interpreter(),
                            "entrypoint_realpath": standin, "entrypoint_sha256": _sha256(standin),
                            "uid": [UNIT_USER[0]] * 4, "argv": [_agent_interpreter(), standin]}, identity
        # ... and the checker grades that REAL record against the REAL pins once the override row is
        # gone: the stand-in is not the pinned unit.
        graded = e3dir / "graded"
        shutil.copytree(evidence, graded, ignore=shutil.ignore_patterns("scratch"))
        units = json.loads((graded / "units.json").read_text())
        for row in units["units"]:
            row.pop("override", None)
        (graded / "units.json").write_text(json.dumps(units))
        verdict = run_checker(graded, "--units", "hermes-acp")
        assert verdict.stdout.splitlines()[0] == \
            f"unit-identity-invalid: hermes-acp entrypoint_realpath {standin} is not the pin", verdict.stdout
        # A8: the allow entry was formed from the namespace's host address and the port input; the
        # planted operator-typed ALLOWED_HERMES (port 1) was ignored.
        gate = json.loads((evidence / "hermes-acp" / "gate.json").read_text())
        assert gate["allowed"] == [f"10.201.107.1:{port}"], gate
        assert f"=== hermes-acp: namespace {ns}, allowed 10.201.107.1:{port} ===" in runner.stdout
        seen = (e3dir / "listener.log").read_text().split()
        assert "10.201.107.2" in seen, seen          # the preflight and C0 came from inside the namespace
    finally:
        _stop(listener)
        _lib(f'egress_ns_destroy {ns}')
    assert ns not in subprocess.run(
        ["ip", "netns", "list"], capture_output=True, text=True).stdout


def test_shebang_matches_launch_interpreter():
    """F8: every unit row's interpreter agrees with its target's shebang, so a bash script can never
    again be handed to python3. Re-targeted by E3 A1, and STRICTER (a changed expectation: the E2
    rows were `/usr/bin/python3 $S0_01_TOOLS/pc_launch.py`, which A1 retires): a unit row now NAMES
    the pin of its executable and nothing else — no interpreter token exists to disagree with the
    shebang, because the kernel reads the unit's OWN shebang (the dynamic half: the live leg's A7
    record shows the pinned interpreter as /proc/<pid>/exe). A1: no row names proofs/S0-01/tools,
    .markers or .secrets, and no S0-01 tool is named anywhere in the runner. That the pinned file
    exists and carries its digest is checked at run time (A1's sha check, test_a1_*)."""
    runner_text = RUNNER.read_text()
    rows = re.findall(r"^UNIT_EXE\[([\w-]+)\]=(\S+)", runner_text, re.M)
    assert sorted(unit for unit, _ in rows) == ["buzz-acp", "hermes-acp"], "no unit rows found"
    for unit, pin in rows:
        assert re.fullmatch(r"PINNED_[A-Z_]+", pin), f"row {unit} names {pin!r}, not a pin"
        value = getattr(PINS, pin)
        assert os.path.isabs(value) and value == os.path.normpath(value), (unit, value)
        for forbidden in ("proofs/S0-01/tools", ".markers", ".secrets"):
            assert forbidden not in value, (unit, value)
    for forbidden in ("LAUNCH[", "pc_launch.py", "proofs/S0-01/tools", "tools/pc/pc_"):
        assert forbidden not in runner_text, forbidden


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
def test_units_json_quotes_in_reason(e3dir):
    """F4: a reason carrying double quote, backslash and newline is encoded correctly in
    units.json. check_egress.py parses units.json and the reason equals the input exactly.
    E3 A8 (a changed expectation): the operator no longer types an address, so the special
    characters ride the OmniRoute PORT input; the runner forms `<host ip>:<port>` whole (never
    word-split) and egress_ns_create refuses it by name, carrying the input into the reason."""
    evidence = e3dir / "evidence"
    reason_value = 'test "quote\\ and\nnewline'
    env = _runner_env(e3dir, reason_value)
    subprocess.run(
        ["bash", str(RUNNER), str(evidence), "hermes-acp"],
        capture_output=True, text=True, timeout=60, env=env)
    units_data = json.loads((evidence / "units.json").read_text())
    hermes_row = [u for u in units_data["units"] if u["unit"] == "hermes-acp"]
    assert len(hermes_row) == 1, units_data
    assert hermes_row[0]["status"] == "not-run"
    # The reason must contain the original value (the validation error includes the input) — the
    # exact contract line, E3: the whole formed entry.
    assert reason_value in hermes_row[0]["reason"], hermes_row[0]["reason"]
    assert hermes_row[0]["reason"] == \
        f"egress: allow entry must be <ip>:<port>, got '10.201.107.1:{reason_value}'", hermes_row[0]


@NEEDS_NETNS
def test_runner_refusal_does_not_destroy_sibling(e3dir):
    """F3/M20: when runner B's create is refused (runner A holds the namespace via a LIVE pid),
    B must not destroy A's namespace. The runner path: B's create returns 65 (namespace-live),
    B records not-run and continues. A's namespace, canary and owner record survive.
    E3: B's inputs are the recorded-override form (A1); STRICTER: A's veth, /etc/netns entry and
    owner record are asserted intact too (with X2's early reap entry this test also kills M14)."""
    ns = "s0-05-hermes-acp"
    port = 18081
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
        before = _census(ns)
        # Runner B: the real runner, which will fail to create the namespace.
        env = _runner_env(e3dir, port)
        evidence_b = e3dir / "evidence_b"
        subprocess.run(
            ["bash", str(RUNNER), str(evidence_b), "hermes-acp"],
            capture_output=True, text=True, timeout=60, env=env)
        # B's units.json should say "not-run" for hermes-acp.
        units_b = json.loads((evidence_b / "units.json").read_text())
        hermes_row = [u for u in units_b["units"] if u["unit"] == "hermes-acp"]
        assert len(hermes_row) == 1, units_b
        assert hermes_row[0]["status"] == "not-run", hermes_row[0]
        # A's namespace must still exist.
        census = subprocess.run(
            ["ip", "netns", "list"], capture_output=True, text=True).stdout
        assert ns in census, f"A's namespace destroyed by B: {census}"
        assert _census(ns) == before, (_census(ns), before)
        # holder is still alive (its PID is in the owner file).
        assert holder.poll() is None, "holder died unexpectedly"
        assert (OWNER_DIR / f"{ns}.owner").read_text().strip() == str(holder.pid)
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


# ===================================================================== E3 — Part X
# tasks/briefs/s0-05-support/E3-brief.md Part X: VERIFY-E2-R1 F1 (X1), the partial-state class
# (X2), F4 (X3) and F8 (X4). Faults are injected from the TEST side only: a bash function defined
# after sourcing the library, a PATH shim that refuses one exact argv and runs the real binary
# otherwise, or a paused child. The library and the runner carry no test hook.

OWNER_DIR = Path("/run/s0-05-egress")   # netns_lib.sh's default EGRESS_OWNER_DIR
CLEAN = {"netns": False, "veth": False, "etc_netns": False, "owner_dir": []}
IP_REAL = shutil.which("ip") or "/usr/sbin/ip"


def _netns_names():
    out = subprocess.run(["ip", "netns", "list"], capture_output=True, text=True).stdout
    return {line.split()[0] for line in out.splitlines() if line.strip()}


def _census(ns):
    """Everything a create of <ns> can leave on the host, read from the host itself: the namespace,
    either end of its veth pair still in the host, /etc/netns/<ns>, and every owner-dir entry that
    names <ns> (the owner record, the E2-R1 claim dir, any claim temp or tombstone)."""
    names = _lib(f'egress_ns_host_if {ns}', f'egress_ns_if {ns}').stdout.split()
    veth = subprocess.run(["ip", "-o", "link", "show", "type", "veth"],
                          capture_output=True, text=True).stdout
    owner = sorted(p.name for p in OWNER_DIR.iterdir() if ns in p.name) if OWNER_DIR.is_dir() else []
    return {"netns": ns in _netns_names(),
            "veth": any(f" {name}@" in veth or f" {name}:" in veth for name in names),
            "etc_netns": os.path.exists(f"/etc/netns/{ns}"), "owner_dir": owner}


@pytest.fixture
def e3dir():
    """A world-traversable scratch dir OF OUR OWN under /tmp (pytest's tmp_path is 0700, and from
    A4 on the unit runs as a non-root user that must reach its stand-in and its scratch tree).
    Removed at teardown; /tmp itself is never touched."""
    path = Path(tempfile.mkdtemp(prefix="e3-", dir="/tmp"))
    path.chmod(0o755)
    try:
        yield path
    finally:
        shutil.rmtree(path, ignore_errors=True)


def _listener(workdir, port, host="0.0.0.0", name="listener"):
    """A host HTTP stand-in answering 200 on every GET and logging each client address (one line
    per request) to <workdir>/<name>.log. Returns the Popen; the caller kills it BY PID."""
    script = workdir / f"{name}.py"
    log = workdir / f"{name}.log"
    script.write_text(
        "import http.server, socketserver, sys\n"
        "LOG = sys.argv[3]\n"
        "class H(http.server.BaseHTTPRequestHandler):\n"
        "    def do_GET(self):\n"
        "        with open(LOG, 'a') as fh:\n"
        "            fh.write(self.client_address[0] + ' ' + self.path + '\\n')\n"
        "        self.send_response(200); self.end_headers(); self.wfile.write(b'{}')\n"
        "    def log_message(self, *a): pass\n"
        "socketserver.TCPServer.allow_reuse_address = True\n"
        "socketserver.TCPServer((sys.argv[1], int(sys.argv[2])), H).serve_forever()\n")
    process = subprocess.Popen([sys.executable, str(script), host, str(port), str(log)],
                               stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    probe_host = "127.0.0.1" if host in ("0.0.0.0", "127.0.0.1") else host
    deadline = time.monotonic() + 5
    while time.monotonic() < deadline:
        if subprocess.run(["curl", "-fsS", "--noproxy", "*", "--max-time", "1", "-o", "/dev/null",
                           f"http://{probe_host}:{port}/ready"], capture_output=True).returncode == 0:
            log.write_text("")          # readiness probes are not evidence
            return process
        time.sleep(0.1)
    process.kill()
    process.wait(timeout=5)
    raise AssertionError(f"{name} on {host}:{port} did not become ready")


def _stop(process):
    if process is not None and process.poll() is None:
        process.kill()
        process.wait(timeout=10)


def _secret_free_environ():
    """os.environ without any key the pins' redaction rule names (the sandbox exports real tokens):
    a runner under test never needs them, and a leak into a unit must be proven with PLANTED fakes."""
    rx = re.compile(r"(?i)(KEY|TOKEN|SECRET|PASSWORD|NSEC|PRIV)")
    return {k: v for k, v in os.environ.items() if not rx.search(k)}


# The pinned values the runner and the checker read, loaded the way the checker loads them (by path).
_pins_spec = importlib.util.spec_from_file_location("s0_01_pins_for_tests", REPO / "proofs" / "S0-01" / "pins.py")
PINS = importlib.util.module_from_spec(_pins_spec)
_pins_spec.loader.exec_module(PINS)
REDACTED = re.compile(PINS.REDACTED_ENV_KEY_RE)
UNIT_USER = (65534, 65534)                  # the sandbox's `nobody`: the non-root unit user (A4)
UNIT_ENV_KEYS = ["HERMES_HOME", "HOME", "LANG", "PATH", "PYTHONDONTWRITEBYTECODE"]
PLANTED = {"E3_PLANTED_SECRET_TOKEN": "planted", "OMNIROUTE_API_KEY": "planted",
           "BUZZ_PRIVATE_KEY": "planted-in-the-runner-env", "ALLOWED_HERMES": "10.201.107.1:1"}


def _agent_interpreter():
    """The stand-in's shebang: the PINNED agent interpreter when this venue has it — then the A7
    exe check runs against the real pin — else this venue's python, recorded as an override."""
    pinned = PINS.PINNED_AGENT_INTERPRETER_REALPATH
    return pinned if os.access(pinned, os.X_OK) else os.path.realpath(sys.executable)


# The hermes-acp stand-in (A1: installed ONLY through the runner's recorded override). It records
# what it was given — env KEY NAMES only (values for the closed non-secret set, a digest for the
# pair's key), never a value that could be a credential — then does what the real adapter does at
# startup: registers its stdio with epoll, which fails with EPERM on /dev/null or a regular file
# (CD1 probe 2), and serves until stdin reaches EOF (CD1 probe 3).
AGENT_STANDIN = """#!@@INTERP@@
import hashlib, json, os, selectors, stat, sys
REC = "@@REC@@"
SHOWN = ("PATH", "HOME", "HERMES_HOME", "LANG", "PYTHONDONTWRITEBYTECODE")
def fd_kind(fd):
    mode = os.fstat(fd).st_mode
    for name, test in (("fifo", stat.S_ISFIFO), ("chr", stat.S_ISCHR), ("reg", stat.S_ISREG), ("sock", stat.S_ISSOCK)):
        if test(mode):
            return name
    return "other"
key = os.environ.get("BUZZ_PRIVATE_KEY")
record = {"pid": os.getpid(), "ppid": os.getppid(), "argv": sys.argv, "uid": os.getuid(), "gid": os.getgid(),
          "net_ino": os.stat("/proc/self/ns/net").st_ino, "cwd": os.getcwd(), "env_keys": sorted(os.environ),
          "env": {k: os.environ[k] for k in SHOWN if k in os.environ},
          "key_sha256": hashlib.sha256(key.encode()).hexdigest() if key is not None else None,
          "stdin": fd_kind(0), "stdout": fd_kind(1), "stop": None}
path = os.path.join(REC, "agent-%d.json" % os.getpid())
def dump():
    with open(path + ".tmp", "w") as fh:
        json.dump(record, fh)
    os.replace(path + ".tmp", path)
dump()
selector = selectors.EpollSelector()
try:
    selector.register(0, selectors.EVENT_READ)
    selector.register(1, selectors.EVENT_WRITE)
except PermissionError as exc:
    record["stop"] = "crash: %r" % (exc,)
    dump()
    print("PermissionError: %s" % (exc,), file=sys.stderr)
    sys.exit(1)
@@EXTRA@@
print("stand-in: serving", flush=True)
while os.read(0, 65536):
    pass
record["stop"] = "eof"
dump()
"""


def _sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def _rec_dir(workdir):
    rec = workdir / "rec"
    rec.mkdir(exist_ok=True)
    os.chown(rec, *UNIT_USER)          # the unit (uid 65534) writes its record here
    return rec


def _agent_standin(workdir, extra="", name="hermes-acp-standin"):
    path = workdir / name
    path.write_text(AGENT_STANDIN.replace("@@INTERP@@", _agent_interpreter())
                    .replace("@@REC@@", str(_rec_dir(workdir))).replace("@@EXTRA@@", extra))
    path.chmod(0o755)
    return path


def _runner_env(workdir, port, path_prefix=None, override=None, unit_user="65534:65534", extra=""):
    """The runner's inputs for one sandbox leg (E3). The pinned hermes-acp is replaced by the
    stand-in ONLY through the runner's recorded override (A1); the OmniRoute port is an input (A8);
    the unit user is 65534 (A4). PLANTED secret-shaped variables and a planted operator-typed
    address sit in the runner's own environment: none may reach a unit (A5), and the address must
    be ignored (A8). The sandbox's real tokens are removed first (never exposed to the runner)."""
    standin = _agent_standin(workdir, extra)
    pin_override = {"PINNED_AGENT_REALPATH": str(standin),
                    "PINNED_AGENT_ENTRYPOINT_SHA256": _sha256(standin)}
    if _agent_interpreter() != PINS.PINNED_AGENT_INTERPRETER_REALPATH:
        pin_override["PINNED_AGENT_INTERPRETER_REALPATH"] = _agent_interpreter()
    pin_override.update(override or {})
    (workdir / "override.json").write_text(json.dumps(pin_override))
    env = {**_secret_free_environ(), **PLANTED, "S0_05_PIN_OVERRIDE": str(workdir / "override.json"),
           "S0_05_OMNIROUTE_PORT": str(port)}
    if unit_user is not None:
        env["S0_05_UNIT_USER"] = unit_user
    if path_prefix is not None:
        env["PATH"] = f"{path_prefix}:{env['PATH']}"
    return env


def _standin_records(workdir, prefix="agent"):
    rec = workdir / "rec"
    return [json.loads(p.read_text()) for p in sorted(rec.glob(f"{prefix}-*.json"))] if rec.is_dir() else []


def _wait_for(predicate, timeout, what):
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if predicate():
            return
        time.sleep(0.1)
    raise AssertionError(f"timed out waiting for {what}")


def _pid_alive(pid):
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    return True


def _dead_pid():
    """A pid that WAS a real process and is now reaped: the stale owner of a planted claim."""
    process = subprocess.Popen(["true"])
    process.wait(timeout=10)
    assert not _pid_alive(process.pid)
    return process.pid


@pytest.mark.parametrize("entry", [
    "10.9.9.9:99999999999999999999", "10.9.9.9:9223372036854775808", "10.9.9.9:65536",
    "10.9.9.9:0", "10.9.9.9:00080",
], ids=["overflow-20-digits", "overflow-2^63", "port-65536", "port-zero", "port-leading-zeros"])
def test_x1_port_is_digit_bounded_before_any_arithmetic(entry):
    """X1 (VERIFY-E2-R1 F1, AF-AP-129): the port is `^[1-9][0-9]{0,4}$` and at most 65535, bounded
    by DIGIT COUNT before any arithmetic, so a digit string past bash's intmax can no longer make a
    `[ -gt ]` exit 2 and slip through as 'false'. Each entry returns 64 with the exact contract line
    and nothing else on stderr; on a root venue it also creates NOTHING (census)."""
    ns = f"s0-05-e3-{uuid.uuid4().hex[:8]}"
    try:
        result = _lib(f'egress_ns_create {ns} "{entry}"')
        assert result.returncode == 64, (result.returncode, result.stderr)
        assert result.stderr == f"egress: allow entry must be <ip>:<port>, got '{entry}'\n", result.stderr
        if netns_capable():
            assert _census(ns) == CLEAN, _census(ns)
    finally:
        if netns_capable():
            _lib(f'egress_ns_destroy {ns}')


# One exact step refused per fault; `command ip` runs the real binary for every other call. Before
# refusing, the fault writes what already exists, so the test proves the rollback had work to do.
_X2_FAULTS = {
    "veth": ('[ "$1" = link ] && [ "$2" = add ]', "E3-injected: veth add refused", 2),
    "gate-rule": ('[ "$1 $2" = "netns exec" ] && [ "$4 $5 $6 $7" = "iptables -A OUTPUT -d" ]',
                  "E3-injected: gate rule refused", 4),
}


@NEEDS_NETNS
@pytest.mark.parametrize("step", ["veth", "gate-rule"])
def test_x2_create_rolls_back_a_failed_step(tmp_path, step):
    """X2 (the partial-state class VERIFY-E2-R1 F1 exposed): a create that fails at a step AFTER
    its first mutation rolls back everything it made — namespace, veth, /etc/netns/<ns>, the claim
    and the owner record — and returns its failure code with the failing step's message on stderr.
    Two fault points: one early (the veth add) and one late (the first allow-entry gate rule, after
    the policies, the addresses, the links and /etc/netns exist)."""
    ns = f"s0-05-e3-{uuid.uuid4().hex[:8]}"
    condition, message, rc = _X2_FAULTS[step]
    snapshot = tmp_path / "at-fault.txt"
    fault = (f'ip() {{ if {condition}; then '
             f'{{ echo "netns=$(command ip netns list | grep -c "^{ns}\\b")"; '
             f'echo "etc=$([ -d /etc/netns/{ns} ] && echo yes || echo no)"; '
             f'echo "owner=$(cat /run/s0-05-egress/{ns}.owner 2>/dev/null)"; }} > {snapshot}; '
             f'echo "{message}" >&2; return {rc}; fi; command ip "$@"; }}')
    try:
        result = subprocess.run(
            ["bash", "-c", f'. {LIB}\n{fault}\negress_ns_create {ns} 10.201.1.1:1\necho "rc=$?"'],
            capture_output=True, text=True, timeout=60)
        assert result.stdout.splitlines()[-1] == "rc=1", (result.stdout, result.stderr)
        assert message in result.stderr, result.stderr
        at_fault = snapshot.read_text().split()
        assert "netns=1" in at_fault and not any(v == "owner=" for v in at_fault), at_fault
        if step == "gate-rule":
            assert "etc=yes" in at_fault, at_fault
        assert _census(ns) == CLEAN, _census(ns)
    finally:
        _lib(f'egress_ns_destroy {ns}')


@NEEDS_NETNS
def test_x2_runner_reaps_a_create_killed_midway(e3dir):
    """X2 + E3: the runner puts the name into its reap set BEFORE it calls create, so a leftover
    create could NOT roll back (its shell killed mid-way) is reaped by `cleanup` at exit under the
    ownership check (the owner record names the runner). The fault: a PATH `ip` shim that, on the
    veth add, records what exists and SIGKILLs its parent — the subshell running egress_ns_create
    inside the runner's command substitution."""
    ns = "s0-05-hermes-acp"
    shim = e3dir / "shim"
    shim.mkdir()
    marker = e3dir / "killed-at.txt"
    (shim / "ip").write_text(
        "#!/bin/bash\n"
        'if [ "$1" = link ] && [ "$2" = add ]; then\n'
        f'  {{ echo "netns=$({IP_REAL} netns list | grep -c "^{ns}\\b")"; '
        f'echo "owner=$(cat /run/s0-05-egress/{ns}.owner 2>/dev/null)"; }} > {marker}\n'
        '  kill -KILL "$PPID"; exit 1\n'
        "fi\n"
        f'exec {IP_REAL} "$@"\n')
    (shim / "ip").chmod(0o755)
    env = _runner_env(e3dir, 18091, path_prefix=shim)
    evidence = e3dir / "evidence"
    try:
        runner = subprocess.Popen(["bash", str(RUNNER), str(evidence), "hermes-acp"],
                                  stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, env=env)
        out, err = runner.communicate(timeout=180)
        # the instrument fired, and the state it left was REAL and owned by the runner
        at_kill = marker.read_text().split()
        assert at_kill == ["netns=1", f"owner={runner.pid}"], (at_kill, err)
        assert _census(ns) == CLEAN, (_census(ns), out, err)
        rows = json.loads((evidence / "units.json").read_text())["units"]
        assert [r["status"] for r in rows if r["unit"] == "hermes-acp"] == ["not-run"], rows
    finally:
        _lib(f'egress_ns_destroy {ns}')


@NEEDS_NETNS
def test_x3_stale_takeover_is_atomic(tmp_path):
    """X3 (VERIFY-E2-R1 F4): two creators find the SAME stale claim (its owner pid is dead).
    Deterministic: the loser is paused (SIGSTOP, from a `cat` function defined after sourcing the
    library) right after it READ the stale owner and before its takeover; the winner then takes
    the claim and builds its namespace; the loser resumes. Exactly one proceeds: the loser refuses
    `namespace-live: <ns> owned by pid <winner>` (65) and creates nothing — the winner's namespace
    is the same inode before and after — and the owner record names the winner."""
    ns = f"s0-05-e3-{uuid.uuid4().hex[:8]}"
    owner_file = OWNER_DIR / f"{ns}.owner"
    signal_file = tmp_path / "loser-paused"
    stale = _dead_pid()
    OWNER_DIR.mkdir(parents=True, exist_ok=True)
    (OWNER_DIR / f"{ns}.claim").mkdir()          # the E2-R1 claim shape, left by a dead creator
    owner_file.write_text(f"{stale}\n")
    pause = (f'cat() {{ command cat "$@"; local rc=$?; '
             f'if [ "$1" = "{owner_file}" ] && [ ! -e {signal_file} ]; then '
             f'echo $BASHPID > {signal_file}.tmp; mv {signal_file}.tmp {signal_file}; '
             f'kill -STOP $BASHPID; fi; return $rc; }}')
    loser = winner = None
    try:
        loser = subprocess.Popen(
            ["bash", "-c", f'. {LIB}\n{pause}\negress_ns_create {ns} 10.201.1.1:1\necho "loser_rc=$?"'],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        _wait_for(signal_file.exists, 20, "the loser to pause after its stale read")
        paused = int(signal_file.read_text())
        winner = subprocess.Popen(
            ["bash", "-c", f'. {LIB}\negress_ns_create {ns} 10.201.1.1:1\necho "winner_rc=$?"\n'
                           'echo READY\nsleep 300'],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        first = winner.stdout.readline().strip()
        assert first == "winner_rc=0", (first, winner.stderr.read() if winner.poll() is not None else "")
        assert winner.stdout.readline().strip() == "READY"
        inode_before = os.stat(f"/run/netns/{ns}").st_ino
        os.kill(paused, signal.SIGCONT)
        out, err = loser.communicate(timeout=60)
        assert out.splitlines()[-1] == "loser_rc=65", (out, err)
        assert f"namespace-live: {ns} owned by pid {winner.pid}\n" in err, err
        assert owner_file.read_text().strip() == str(winner.pid)
        assert os.stat(f"/run/netns/{ns}").st_ino == inode_before, "the loser recreated the namespace"
        assert _lib(f'egress_ns_mechanism {ns}').stdout.strip() == "veth-iptables"
    finally:
        for process in (loser, winner):
            _stop(process)
        _lib(f'egress_ns_destroy {ns}')
    assert _census(ns) == CLEAN, _census(ns)


@NEEDS_NETNS
def test_x4_runner_cleanup_reaps_its_own_namespace_at_exit(e3dir):
    """X4 (VERIFY-E2-R1 F8), case 1, through the runner's REAL `cleanup` (its EXIT/INT/TERM trap,
    never a copy of its logic): the runner is interrupted with SIGTERM while its unit is live in the
    namespace it owns; after the runner exits, that namespace, its veth, /etc/netns/<ns> and the
    owner record are gone and the stand-in unit is dead."""
    ns = "s0-05-hermes-acp"
    port = 18092
    env = _runner_env(e3dir, port)
    evidence = e3dir / "evidence"
    listener = runner = None
    try:
        listener = _listener(e3dir, port)
        runner = subprocess.Popen(["bash", str(RUNNER), str(evidence), "hermes-acp"],
                                  stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, env=env)
        _wait_for(lambda: _standin_records(e3dir), 60, "the unit to start inside the namespace")
        standin = _standin_records(e3dir)[0]["pid"]
        assert ns in _netns_names()
        assert (OWNER_DIR / f"{ns}.owner").read_text().strip() == str(runner.pid)
        runner.send_signal(signal.SIGTERM)
        out, err = runner.communicate(timeout=180)
        assert _census(ns) == CLEAN, (_census(ns), out, err)
        assert not _pid_alive(standin), f"stand-in {standin} outlived its runner"
    finally:
        _stop(runner)
        _stop(listener)
        _lib(f'egress_ns_destroy {ns}')


@NEEDS_NETNS
def test_x4_runner_cleanup_leaves_a_live_owners_namespace(e3dir):
    """X4 (VERIFY-E2-R1 F8), case 2 — kills M14 (the owner check in `cleanup` dropped). A holder
    process owns `s0-05-hermes-acp`; the REAL runner for hermes-acp puts the name in its reap set
    (X2's early entry), its create is refused `namespace-live`, and at exit its `cleanup` must leave
    the holder's namespace, veth, /etc/netns entry and owner record untouched."""
    ns = "s0-05-hermes-acp"
    port = 18093
    holder = None
    try:
        holder = subprocess.Popen(
            ["bash", "-c", f'. {LIB}\negress_ns_create {ns} 10.201.107.1:{port} || exit 10\n'
                           'echo READY\nsleep 300'],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        assert holder.stdout.readline().strip() == "READY", holder.stderr.read()
        before = _census(ns)
        assert before["netns"] and before["veth"] and before["etc_netns"], before
        evidence = e3dir / "evidence"
        runner = subprocess.run(["bash", str(RUNNER), str(evidence), "hermes-acp"],
                                capture_output=True, text=True, timeout=180,
                                env=_runner_env(e3dir, port))
        rows = json.loads((evidence / "units.json").read_text())["units"]
        hermes = [r for r in rows if r["unit"] == "hermes-acp"]
        override = json.loads((e3dir / "override.json").read_text())   # A1: recorded on the row
        assert hermes == [{"unit": "hermes-acp", "status": "not-run", "override": override,
                           "reason": f"namespace-live: {ns} owned by pid {holder.pid}"}], hermes
        assert _census(ns) == before, (_census(ns), runner.stderr)
        assert (OWNER_DIR / f"{ns}.owner").read_text().strip() == str(holder.pid)
        assert holder.poll() is None
    finally:
        _stop(holder)
        _lib(f'egress_ns_destroy {ns}')


# ===================================================================== E3 — Part A (CD1 A1-A8)
# The contract text is tasks/briefs/s0-05-support/CD1-AMENDMENT.md; E3's brief adds the refusal
# texts. In the sandbox the pinned binaries are absent, so every leg below replaces a unit ONLY
# through the runner's recorded override (A1), and asserts what the override cannot hide.

UID0 = FIXTURES / "evidence-synthetic-uid0"
PAIR_KEY = "e3-test-identity-not-a-real-key-0123456789"


def _run_runner(env, evidence, *units, timeout=120):
    return subprocess.run(["bash", str(RUNNER), str(evidence), *units],
                          capture_output=True, text=True, timeout=timeout, env=env)


def _unit_row(evidence, unit):
    rows = [r for r in json.loads((evidence / "units.json").read_text())["units"] if r["unit"] == unit]
    assert len(rows) == 1, rows
    return rows[0]


def _pair_override(workdir):
    """A regular file standing in for the pinned buzz-acp binary (its bytes never run in the refusal
    legs below; the launching leg in Part D uses a compiled stand-in)."""
    buzz = workdir / "buzz-acp-standin"
    buzz.write_bytes(b"\x7fELF e3 stand-in bytes\n")
    buzz.chmod(0o755)
    return {"PINNED_BUZZ_ACP_EXE_REALPATH": str(buzz), "PINNED_BUZZ_ACP_SHA256": _sha256(buzz)}


def _identity_file(path, mode=0o600, owner=UNIT_USER, body=f"BUZZ_PRIVATE_KEY={PAIR_KEY}\n"):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(body)
    os.chown(path, *owner)
    path.chmod(mode)
    return path


@NEEDS_NETNS
@pytest.mark.parametrize("case", ["wrong-sha", "symlinked-path", "absent", "real-pins", "pair-wrong-sha"])
def test_a1_unit_identity_mismatch_is_refused(e3dir, case):
    """A1: before anything is created, the runner checks that the file at the pinned path IS its own
    realpath and carries the pinned sha256 (for the pair: buzz-acp, then the agent it launches);
    otherwise `not-run|unit identity mismatch: <path>`. `real-pins` is the sandbox run with NO
    override: the pinned paths from proofs/S0-01/pins.py do not exist here — refused by name, and
    no override is recorded because none was used."""
    evidence = e3dir / "evidence"
    unit = "buzz-acp" if case.startswith("pair") else "hermes-acp"
    env = _runner_env(e3dir, 18094, override=_pair_override(e3dir))
    override = json.loads((e3dir / "override.json").read_text())
    if case == "wrong-sha":
        override["PINNED_AGENT_ENTRYPOINT_SHA256"] = "0" * 64
        expected = override["PINNED_AGENT_REALPATH"]
    elif case == "symlinked-path":
        link = e3dir / "linked-standin"
        link.symlink_to(override["PINNED_AGENT_REALPATH"])
        override["PINNED_AGENT_REALPATH"] = expected = str(link)
    elif case == "absent":
        override["PINNED_AGENT_REALPATH"] = expected = str(e3dir / "no-such-unit")
    elif case == "pair-wrong-sha":
        override["PINNED_BUZZ_ACP_SHA256"] = "f" * 64
        expected = override["PINNED_BUZZ_ACP_EXE_REALPATH"]
    if case == "real-pins":
        del env["S0_05_PIN_OVERRIDE"]
        expected, override = PINS.PINNED_AGENT_REALPATH, None
    else:
        (e3dir / "override.json").write_text(json.dumps(override))
    runner = _run_runner(env, evidence, unit)
    row = _unit_row(evidence, unit)
    assert row.pop("override", None) == override, row
    assert row == {"unit": unit, "status": "not-run", "reason": f"unit identity mismatch: {expected}"}, runner.stderr
    assert _census(f"s0-05-{unit}") == CLEAN


def test_a1_checker_refuses_an_override_on_a_live_claim(tmp_path):
    """A1, the checker half: a units.json row that records a pin override, for a run unit whose
    bundle says venue pc, is `units-manifest-invalid: <unit> override present` — before its identity
    is graded (a stand-in run can never pass as the live leg). The same override on a non-pc bundle
    (the synthetic curl unit) is not a live claim and is not refused."""
    bundle = copy_bundle(tmp_path, SYNTHETIC)
    units = json.loads((bundle / "units.json").read_text())
    for row in units["units"]:
        if row["unit"] == "curl":
            row["override"] = {"PINNED_AGENT_REALPATH": "/tmp/stand-in"}
    (bundle / "units.json").write_text(json.dumps(units))
    result = run_checker(bundle, "--units", "curl,hermes-acp")
    assert result.returncode == 0, result.stdout                  # curl's venue is not pc
    for row in units["units"]:
        if row["unit"] == "hermes-acp":
            row["override"] = {"PINNED_AGENT_REALPATH": "/tmp/stand-in"}
    (bundle / "units.json").write_text(json.dumps(units))
    patch_json(bundle / "hermes-acp" / "unit-identity.json", uid=[0, 0, 0, 0])   # a second defect
    result = run_checker(bundle, "--units", "curl,hermes-acp")
    assert result.returncode == 1
    assert result.stdout.splitlines()[0] == "units-manifest-invalid: hermes-acp override present"


@NEEDS_NETNS
def test_a2_s0_01_tree_change_fails_the_leg(e3dir):
    """A2: the runner takes a stat census of <pinned base>/.markers and every v2-* directory before
    the first unit and after the last; anything changed fails the leg with `s0-01-tree-changed:
    <path>` and a non-zero exit, and the checker is not run. The base comes from pins.py (the
    directory of PINNED_HERMES_HOME), here moved through the recorded override to a scratch tree the
    stand-in unit changes (one chmod of v2-run-1). Also A4's DEFAULT user: no S0_05_UNIT_USER, so the
    unit runs as the owner of the (overridden) agent realpath — uid 65534."""
    base = e3dir / "s0-01-pinned"
    v2 = base / ".markers" / "v2-run-1"
    v2.mkdir(parents=True)
    os.chown(v2, *UNIT_USER)
    (base / ".markers" / "v2-negative").mkdir()          # present and untouched: must not be named
    port = 18095
    env = _runner_env(e3dir, port, unit_user=None, override={"PINNED_HERMES_HOME": str(base / ".hermes-home")},
                      extra=f"os.chmod({str(v2)!r}, 0o700)")
    override = json.loads((e3dir / "override.json").read_text())
    os.chown(override["PINNED_AGENT_REALPATH"], *UNIT_USER)
    evidence = e3dir / "evidence"
    listener = None
    try:
        listener = _listener(e3dir, port)
        runner = _run_runner(env, evidence, "hermes-acp", timeout=240)
        assert runner.returncode == 1, (runner.returncode, runner.stderr)
        changed = [l for l in runner.stderr.splitlines() if l.startswith("s0-01-tree-changed:")]
        assert changed == [f"s0-01-tree-changed: {v2}"], runner.stderr
        assert "=== checker ===" not in runner.stdout, runner.stdout
        census = json.loads((evidence / "s0-01-census.json").read_text())
        assert census["changed"] == [str(v2)] and census["tree"] == "present", census
        assert str(base / ".markers" / "v2-negative") in census["after"], census
        assert _unit_row(evidence, "hermes-acp")["status"] == "run"
        record = _standin_records(e3dir)[0]
        assert (record["uid"], record["gid"]) == UNIT_USER, record          # the A4 default
    finally:
        _stop(listener)
        _lib('egress_ns_destroy s0-05-hermes-acp')
    assert _census("s0-05-hermes-acp") == CLEAN


@NEEDS_NETNS
@pytest.mark.parametrize("how", ["explicit", "default-owner"])
def test_a4_a_root_unit_user_is_refused(e3dir, how):
    """A4: the unit user is resolved once — the operator input, or the owner of the pinned agent
    realpath — and a resolved uid 0 is `not-run|unit would run as root`, before anything is made.
    `default-owner`: the (overridden) agent realpath is owned by root and no input is given."""
    evidence = e3dir / "evidence"
    env = _runner_env(e3dir, 18096, unit_user="0:0" if how == "explicit" else None)
    _run_runner(env, evidence, "hermes-acp")
    row = _unit_row(evidence, "hermes-acp")
    assert (row["status"], row["reason"]) == ("not-run", "unit would run as root"), row
    assert _census("s0-05-hermes-acp") == CLEAN


@NEEDS_NETNS
def test_a4_a_malformed_unit_user_is_a_usage_error(e3dir):
    """A4: a unit user that is not <uid>:<gid> in plain decimal (`00:0` would be root) is a usage
    error before anything is written."""
    evidence = e3dir / "evidence"
    runner = _run_runner(_runner_env(e3dir, 18096, unit_user="00:0"), evidence, "hermes-acp")
    assert runner.returncode == 64
    assert "run_s0_05_units: S0_05_UNIT_USER must be <uid>:<gid>, got '00:0'" in runner.stderr
    assert not evidence.exists()


@NEEDS_NETNS
@pytest.mark.parametrize("case", ["unset", "absent", "mode", "owner", "shape", "s0-01-path", "s0-01-real-path"])
def test_a6_identity_file_refusals(e3dir, case):
    """A6: the pair's S0-05 identity is an operator input (a file path) the runner reads without
    printing: absent -> `absent`; group/other bits -> `mode <octal>`; not owned by the unit user ->
    `owner uid <n>`; no `BUZZ_PRIVATE_KEY=` line -> `shape`; and NEVER S0-01's .secrets, refused by
    PATH before the file is opened — both under an overridden base and at the REAL pinned base by
    name (/home/rocco/s0-01-pinned/.secrets/agent.env). Each is `not-run|identity file refused:
    <detail>`, nothing is created, and the key's value is printed nowhere."""
    evidence = e3dir / "evidence"
    base = e3dir / "s0-01-pinned"
    extra = {**_pair_override(e3dir)}
    if case == "s0-01-path":
        extra["PINNED_HERMES_HOME"] = str(base / ".hermes-home")
    env = _runner_env(e3dir, 18097, override=extra)
    identity, detail = None, None
    if case == "absent":
        identity, detail = e3dir / "no-identity", "absent"
    elif case == "unset":
        detail = "absent"
    elif case == "mode":
        identity, detail = _identity_file(e3dir / "id" / "pair.env", mode=0o644), "mode 644"
    elif case == "owner":
        identity, detail = _identity_file(e3dir / "id" / "pair.env", owner=(0, 0)), "owner uid 0"
    elif case == "shape":
        identity, detail = _identity_file(e3dir / "id" / "pair.env", body="NOT_THE_KEY=x\n"), "shape"
    elif case == "s0-01-path":
        identity = _identity_file(base / ".secrets" / "agent.env")
        detail = f"S0-01 path {identity}"
    elif case == "s0-01-real-path":
        identity = Path(os.path.dirname(PINS.PINNED_HERMES_HOME)) / ".secrets" / "agent.env"
        detail = f"S0-01 path {identity}"
    if identity is not None:
        env["S0_05_PAIR_IDENTITY"] = str(identity)
    runner = _run_runner(env, evidence, "buzz-acp")
    row = _unit_row(evidence, "buzz-acp")
    assert (row["status"], row["reason"]) == ("not-run", f"identity file refused: {detail}"), row
    assert _census("s0-05-buzz-acp") == CLEAN
    for text in (runner.stdout, runner.stderr, (evidence / "units.json").read_text()):
        assert PAIR_KEY not in text


@NEEDS_NETNS
def test_a7_a_unit_not_matching_the_pins_is_not_observed(e3dir):
    """A7, the runner half: at canary time the runner records which process runs in the namespace
    (<unit>/unit-identity.json: pid, /proc/<pid>/exe realpath, entrypoint realpath and sha256, the
    Uid line, argv) and runs the canaries ONLY if it matches the pins — else `not-run|unit identity
    not observed: <detail>`, every mismatch named. Two faults from the test side: the interpreter pin
    is overridden to another path (exe mismatch), and a PATH `setpriv` shim runs the unit WITHOUT
    dropping privileges (uid 0 — the runner-side uid check, E6)."""
    port = 18098
    shim = e3dir / "shim"
    shim.mkdir()
    (shim / "setpriv").write_text(
        "#!/bin/bash\n# E3 test fault: a setpriv that does NOT drop privileges\n"
        'while [ $# -gt 0 ]; do case $1 in --) shift; break;; --*) shift;; *) break;; esac; done\n'
        'exec "$@"\n')
    (shim / "setpriv").chmod(0o755)
    wrong_exe = "/usr/bin/e3-not-the-interpreter"
    env = _runner_env(e3dir, port, path_prefix=shim, override={"PINNED_AGENT_INTERPRETER_REALPATH": wrong_exe})
    evidence = e3dir / "evidence"
    listener = None
    try:
        listener = _listener(e3dir, port)
        runner = _run_runner(env, evidence, "hermes-acp", timeout=240)
        row = _unit_row(evidence, "hermes-acp")
        assert (row["status"], row["reason"]) == (
            "not-run", f"unit identity not observed: exe {_agent_interpreter()} is not {wrong_exe}; uid 0"), row
        identity = json.loads((evidence / "hermes-acp" / "unit-identity.json").read_text())
        assert identity["uid"] == [0, 0, 0, 0] and identity["exe_realpath"] == _agent_interpreter(), identity
        assert not (evidence / "hermes-acp" / "canaries.jsonl").exists(), "the canaries ran for an unobserved unit"
        standin = _standin_records(e3dir)[0]["pid"]
        assert not _pid_alive(standin)
    finally:
        _stop(listener)
        _lib('egress_ns_destroy s0-05-hermes-acp')
    assert _census("s0-05-hermes-acp") == CLEAN, runner.stderr


def test_a7_the_synthetic_pass_fixture_grades_its_identity():
    """A7, the checker half, positive: the synthetic-pass fixture's hermes-acp bundle says venue pc
    and carries the unit-identity record that matches proofs/S0-01/pins.py; the checker GRADES it
    (the line below is printed only by that check) and passes."""
    result = run_checker(SYNTHETIC, "--units", "curl,hermes-acp")
    assert result.returncode == 0, result.stdout
    assert (f"unit-identity: hermes-acp pid 424242 runs {PINS.PINNED_AGENT_REALPATH} "
            f"(sha256 {PINS.PINNED_AGENT_ENTRYPOINT_SHA256[:12]}) as uid 1000") in result.stdout.splitlines()


def test_a7_the_uid0_fixture_is_refused():
    """A7: the committed negative fixture differs from synthetic-pass in ONE field — the record's
    Uid line is root — and is refused by exactly that."""
    pos = json.loads((SYNTHETIC / "hermes-acp" / "unit-identity.json").read_text())
    neg = json.loads((UID0 / "hermes-acp" / "unit-identity.json").read_text())
    assert {k for k in pos if pos[k] != neg[k]} == {"uid"} and neg["uid"] == [0, 0, 0, 0]
    result = run_checker(UID0, "--units", "curl,hermes-acp")
    assert result.returncode == 1
    assert result.stdout.splitlines()[0] == "unit-identity-invalid: hermes-acp uid 0"


@pytest.mark.parametrize("mutate, detail", [
    ("delete", "unit-identity.json absent"),
    ({"entrypoint_sha256": "0" * 64}, f"entrypoint_sha256 {'0' * 64} is not the pin"),
    ({"exe_realpath": "/usr/bin/python3.12"}, "exe_realpath /usr/bin/python3.12 is not the pin"),
    ({"entrypoint_realpath": "/tmp/stand-in"}, "entrypoint_realpath /tmp/stand-in is not the pin"),
    ({"uid": [1000, 0, 1000, 1000]}, "uid 0"),
    ({"uid": 1000}, "uid 1000 is not the four uids of the Uid line"),
    ({"uid": [True, 1000, 1000, 1000]}, "uid [True, 1000, 1000, 1000] is not the four uids of the Uid line"),
    ("not-json", "unit-identity.json is not JSON"),
    ("drop-key", "unit-identity.json lacks one of unit, pid, exe_realpath, entrypoint_realpath, "
                 "entrypoint_sha256, uid, argv"),
], ids=["missing", "digest", "exe-path", "entrypoint-path", "effective-uid-0", "uid-not-a-list",
        "uid-bool", "not-json", "missing-key"])
def test_a7_the_checker_refuses_an_identity_that_is_not_the_pin(tmp_path, mutate, detail):
    """A7: for a run unit whose bundle says venue pc, `unit-identity-invalid: <unit> <detail>` on a
    missing record, a digest or path that is not the pin, or any uid 0 (the record carries all four
    Uid-line uids: a setuid-root unit is root too)."""
    bundle = copy_bundle(tmp_path, SYNTHETIC)
    record = bundle / "hermes-acp" / "unit-identity.json"
    if mutate == "delete":
        record.unlink()
    elif mutate == "not-json":
        record.write_text("{not json")
    elif mutate == "drop-key":
        payload = json.loads(record.read_text())
        del payload["argv"]
        record.write_text(json.dumps(payload))
    else:
        patch_json(record, **mutate)
    result = run_checker(bundle, "--units", "curl,hermes-acp")
    assert result.returncode == 1
    assert result.stdout.splitlines()[0] == f"unit-identity-invalid: hermes-acp {detail}"


def test_a7_the_identity_is_graded_only_for_a_live_claim(tmp_path):
    """A7 scope: the record is required for a run unit whose bundle says venue pc. A curl bundle
    relabelled pc has no pinned identity and is refused; the sandbox mechanism bundle (venue sandbox)
    needs none and passes."""
    assert run_checker(MECHANISM).returncode == 0
    bundle = copy_bundle(tmp_path)
    patch_json(bundle / "curl" / "runtime.json", venue="pc")
    assert run_checker(bundle).stdout.splitlines()[0] == "unit-identity-invalid: curl unit-identity.json absent"
    shutil.copy(SYNTHETIC / "hermes-acp" / "unit-identity.json", bundle / "curl" / "unit-identity.json")
    assert run_checker(bundle).stdout.splitlines()[0] == "unit-identity-invalid: curl no pinned identity for this unit"


@NEEDS_NETNS
def test_a8_every_allow_entry_is_formed_by_the_runner(e3dir):
    """A8: the allow entry is `$(egress_ns_host_ip <ns>):<port input>`, formed by the runner; the
    planted operator-typed ALLOWED_HERMES (port 1) is ignored. With nothing listening on the port,
    the preflight names exactly that derived entry: `not-run|positive control unreachable:
    10.201.107.1:<port> not reachable from s0-05-hermes-acp`, and the namespace is gone after."""
    port = 18099
    evidence = e3dir / "evidence"
    runner = _run_runner(_runner_env(e3dir, port), evidence, "hermes-acp")
    row = _unit_row(evidence, "hermes-acp")
    assert row["reason"] == f"positive control unreachable: 10.201.107.1:{port} not reachable from s0-05-hermes-acp", row
    assert f"positive-control-unreachable: hermes-acp 10.201.107.1:{port}" in runner.stderr
    assert _census("s0-05-hermes-acp") == CLEAN


# ===================================================================== E3 — Part D (D-051)
# The pair (buzz-acp + the hermes-acp it spawns) reaches the pinned relay on the host's 127.0.0.1
# through ONE leg-scoped DNAT on its veth host end. The sandbox proof: a relay stand-in bound to
# 127.0.0.1 ONLY — unreachable from a namespace by any other path — reached through <host ip>:<port>.

RELAY_PORT = urlsplit(PINS.PINNED_RELAY_URL).port
IPTABLES_REAL = shutil.which("iptables") or "/usr/sbin/iptables"

# The buzz-acp stand-in: a compiled binary, because A7 grades /proc/<pid>/exe and the real unit is
# an ELF. THIS process is the unit; its worker records what the unit was given, opens the unit's
# own socket to its relay URL, spawns the agent command as its child (as buzz-acp does, CD1 probe
# 2), and serves until stdin reaches EOF.
PAIR_WRAPPER_C = r"""
#include <stdlib.h>
#include <sys/wait.h>
#include <unistd.h>
int main(int argc, char **argv) {
    char **wargv = calloc((size_t)argc + 3, sizeof *wargv);
    if (wargv == NULL) return 1;
    wargv[0] = INTERP; wargv[1] = WORKER;
    for (int i = 0; i < argc; i++) wargv[i + 2] = argv[i];
    pid_t child = fork();
    if (child == 0) { execv(INTERP, wargv); _exit(127); }
    int status = 0;
    if (child < 0 || waitpid(child, &status, 0) < 0) return 1;
    return WIFEXITED(status) ? WEXITSTATUS(status) : 1;
}
"""
PAIR_WORKER = """
import hashlib, json, os, selectors, socket, stat, subprocess, sys
from urllib.parse import urlsplit
REC = "@@REC@@"
SHOWN = ("PATH", "HOME", "HERMES_HOME", "LANG", "PYTHONDONTWRITEBYTECODE")
def fd_kind(fd):
    mode = os.fstat(fd).st_mode
    for name, test in (("fifo", stat.S_ISFIFO), ("chr", stat.S_ISCHR), ("reg", stat.S_ISREG), ("sock", stat.S_ISSOCK)):
        if test(mode):
            return name
    return "other"
argv = sys.argv[1:]
key = os.environ.get("BUZZ_PRIVATE_KEY")
record = {"pid": os.getpid(), "unit_pid": os.getppid(), "pair_argv": argv, "uid": os.getuid(), "gid": os.getgid(),
          "net_ino": os.stat("/proc/self/ns/net").st_ino, "env_keys": sorted(os.environ),
          "env": {k: os.environ[k] for k in SHOWN if k in os.environ},
          "key_sha256": hashlib.sha256(key.encode()).hexdigest() if key is not None else None,
          "stdin": fd_kind(0), "stdout": fd_kind(1), "stop": None}
path = os.path.join(REC, "pair-%d.json" % os.getpid())
def dump():
    with open(path + ".tmp", "w") as fh:
        json.dump(record, fh)
    os.replace(path + ".tmp", path)
selector = selectors.EpollSelector()
try:
    selector.register(0, selectors.EVENT_READ)
    selector.register(1, selectors.EVENT_WRITE)
except PermissionError as exc:
    record["stop"] = "crash: %r" % (exc,)
    dump()
    sys.exit(1)
relay = urlsplit(argv[argv.index("--relay-url") + 1])
try:
    with socket.create_connection((relay.hostname, relay.port), timeout=5) as conn:
        conn.sendall(b"GET /pair-own-socket HTTP/1.0\\r\\n\\r\\n")
        record["relay_reply"] = conn.recv(12).decode(errors="replace")
except OSError as exc:
    record["relay_reply"] = "error: %r" % (exc,)
agent = subprocess.Popen([argv[argv.index("--agent-command") + 1]], stdin=subprocess.PIPE, stdout=subprocess.PIPE)
record["agent_pid"] = agent.pid
dump()
print("pair stand-in: serving", flush=True)
while os.read(0, 65536):
    pass
agent.stdin.close()
agent.wait(timeout=20)
record["stop"] = "eof"
dump()
"""


def _pair_standin(workdir):
    worker = workdir / "pair_worker.py"
    worker.write_text(PAIR_WORKER.replace("@@REC@@", str(_rec_dir(workdir))))
    source = workdir / "pair_standin.c"
    source.write_text(PAIR_WRAPPER_C)
    binary = workdir / "buzz-acp-standin"
    subprocess.run(["gcc", "-O0", f'-DINTERP="{_agent_interpreter()}"', f'-DWORKER="{worker}"',
                    "-o", str(binary), str(source)], check=True, capture_output=True, text=True)
    binary.chmod(0o755)
    return binary


def _nat_rules_naming(host_if):
    rules = subprocess.run(["iptables", "-t", "nat", "-S", "PREROUTING"], capture_output=True, text=True).stdout
    return [line for line in rules.splitlines() if f" -i {host_if} " in line]


def _route_localnet(host_if):
    path = Path(f"/proc/sys/net/ipv4/conf/{host_if}/route_localnet")
    return path.read_text().strip() if path.exists() else None


def _iptables_shim(workdir, action):
    """A PATH `iptables` that intercepts ONE exact argv — the relay reach's nat add — and runs the real
    binary for everything else (the namespace gates run through it too)."""
    shim = workdir / "shim"
    shim.mkdir()
    (shim / "iptables").write_text(
        "#!/bin/bash\n"
        f'if [ "$1 $2 $3 $4" = "-t nat -A PREROUTING" ]; then {action}; fi\n'
        f'exec {IPTABLES_REAL} "$@"\n')
    (shim / "iptables").chmod(0o755)
    return shim


def _curl_from(ns, url):
    return _lib(f'egress_ns_run {ns} curl -sS --noproxy "*" --connect-timeout 3 -o /dev/null -w "%{{http_code}}" {url}')


@NEEDS_NETNS
def test_d_relay_reach_add_and_del(e3dir):
    """D-051, the library: a relay stand-in bound to the host's 127.0.0.1:<relay port> ONLY is
    unreachable from the namespace until egress_relay_reach_add installs the one DNAT on the pair's
    veth host end; then it is reached through <host ip>:<port>, and the stand-in sees the
    namespace's own address (a loopback listener receiving a non-loopback source: only the DNAT
    path produces that). route_localnet is load-bearing (off -> unreachable again). egress_relay_
    reach_del removes the rule and puts route_localnet back to 0 while the interface still lives;
    destroy leaves nothing (census)."""
    ns = f"s0-05-e3-{uuid.uuid4().hex[:8]}"
    host_ip = _lib(f'egress_ns_host_ip {ns}').stdout.strip()
    host_if = _lib(f'egress_ns_host_if {ns}').stdout.strip()
    ns_ip = _lib(f'egress_ns_ip {ns}').stdout.strip()
    url = f"http://{host_ip}:{RELAY_PORT}"
    relay = None
    try:
        assert _lib(f'egress_ns_create {ns} {host_ip}:{RELAY_PORT}').returncode == 0
        relay = _listener(e3dir, RELAY_PORT, host="127.0.0.1", name="relay")
        assert _curl_from(ns, f"{url}/before").stdout == "000"                 # no path without the rule
        added = _lib(f'egress_relay_reach_add {ns} {RELAY_PORT} 127.0.0.1:{RELAY_PORT}')
        assert added.returncode == 0, added.stderr
        assert _nat_rules_naming(host_if) == [
            f"-A PREROUTING -d {host_ip}/32 -i {host_if} -p tcp -m tcp --dport {RELAY_PORT} "
            f"-j DNAT --to-destination 127.0.0.1:{RELAY_PORT}"]
        assert _route_localnet(host_if) == "1"
        assert _curl_from(ns, f"{url}/through-dnat").stdout == "200"
        assert (e3dir / "relay.log").read_text().splitlines() == [f"{ns_ip} /through-dnat"]
        subprocess.run(["sysctl", "-q", "-w", f"net.ipv4.conf.{host_if}.route_localnet=0"], check=True)
        assert _curl_from(ns, f"{url}/no-localnet").stdout == "000"            # the sysctl is load-bearing
        subprocess.run(["sysctl", "-q", "-w", f"net.ipv4.conf.{host_if}.route_localnet=1"], check=True)
        deleted = _lib(f'egress_relay_reach_del {ns}')
        assert deleted.returncode == 0, deleted.stderr
        assert _nat_rules_naming(host_if) == [] and _route_localnet(host_if) == "0"
        assert _curl_from(ns, f"{url}/after").stdout == "000"
    finally:
        _stop(relay)
        _lib(f'egress_ns_destroy {ns}')
    assert _census(ns) == CLEAN and _nat_rules_naming(host_if) == [] and _route_localnet(host_if) is None


@NEEDS_NETNS
@pytest.mark.skipif(shutil.which("gcc") is None,
                    reason="the buzz-acp stand-in is compiled (A7 grades /proc/<pid>/exe); no C compiler — NOT run here")
def test_d_pair_leg_reaches_the_relay_through_the_dnat(e3dir):
    """D-051 + A5/A6/A7 for the pair, one real run of the runner for buzz-acp: the relay stand-in is
    bound to the host's 127.0.0.1:<relay port> ONLY; the runner adds the leg's DNAT, preflights BOTH
    allowed destinations (relay, OmniRoute), launches the pair from the pinned argv shape with three
    substitutions (A6), and the pair's OWN socket reaches the relay through the DNAT. The pair's
    identity reaches its environment (and its agent child's) from the identity file, never an argv
    or the runner's environment (A5/A6). unit-identity.json names the compiled stand-in (A7). After
    the runner exits, no PREROUTING rule names the pair's interface and the interface is gone."""
    ns = "s0-05-buzz-acp"
    host_ip = _lib(f'egress_ns_host_ip {ns}').stdout.strip()
    host_if = _lib(f'egress_ns_host_if {ns}').stdout.strip()
    ns_ip = _lib(f'egress_ns_ip {ns}').stdout.strip()
    omni_port = 18100
    base = e3dir / "s0-01-pinned"
    (base / ".markers" / "v2-run-1").mkdir(parents=True)       # A2: present and untouched
    buzz = _pair_standin(e3dir)
    env = _runner_env(e3dir, omni_port, override={
        "PINNED_BUZZ_ACP_EXE_REALPATH": str(buzz), "PINNED_BUZZ_ACP_SHA256": _sha256(buzz),
        "PINNED_HERMES_HOME": str(base / ".hermes-home")})
    override = json.loads((e3dir / "override.json").read_text())
    agent = override["PINNED_AGENT_REALPATH"]
    env["S0_05_PAIR_IDENTITY"] = str(_identity_file(e3dir / "id" / "pair.env"))
    evidence = e3dir / "evidence"
    relay = omni = None
    try:
        relay = _listener(e3dir, RELAY_PORT, host="127.0.0.1", name="relay")
        omni = _listener(e3dir, omni_port, name="omniroute")
        runner = _run_runner(env, evidence, "buzz-acp", timeout=300)
        assert PAIR_KEY not in runner.stdout + runner.stderr + (evidence / "units.json").read_text()
        row = _unit_row(evidence, "buzz-acp")
        assert (row["status"], row["override"]) == ("run", override), (row, runner.stderr[-2000:])
        pair = _standin_records(e3dir, "pair")
        assert len(pair) == 1, pair
        pair = pair[0]
        # A6: the pinned shape (pins.py PINNED_LAUNCH_ARGV) with three substitutions only.
        assert pair["pair_argv"] == [str(buzz), "--relay-url", f"ws://{host_ip}:{RELAY_PORT}",
                                     "--agent-command", agent, "--agent-args", "",
                                     "--idle-timeout", PINS.PINNED_IDLE_TIMEOUT_ARG,
                                     "--max-turn-duration", PINS.PINNED_MAX_TURN_DURATION_ARG], pair["pair_argv"]
        assert not any(f in a for a in pair["pair_argv"] for f in ("proofs/S0-01/tools", ".markers", ".secrets"))
        # D-051: the pair's OWN socket reached the loopback-only relay through the DNAT, and so did the
        # preflight; the relay saw the namespace's address.
        assert pair["relay_reply"].startswith("HTTP/1.0 200"), pair["relay_reply"]
        seen = (e3dir / "relay.log").read_text().splitlines()
        assert f"{ns_ip} /v1/models" in seen and f"{ns_ip} /pair-own-socket" in seen, seen
        # A5 + A6: the environment is the declared set plus the pair's identity key — its value from
        # the identity file, not the planted runner variable — and nothing else secret-shaped.
        assert pair["env_keys"] == sorted(UNIT_ENV_KEYS + ["BUZZ_PRIVATE_KEY"]), pair["env_keys"]
        assert pair["key_sha256"] == hashlib.sha256(PAIR_KEY.encode()).hexdigest()
        assert [k for k in pair["env_keys"] if REDACTED.search(k)] == ["BUZZ_PRIVATE_KEY"]
        assert (pair["uid"], pair["gid"], pair["stdin"], pair["stop"]) == (*UNIT_USER, "fifo", "eof"), pair
        # the agent is the pair's child, in the pair's namespace, with the pair's environment
        child = [r for r in _standin_records(e3dir) if r["pid"] == pair["agent_pid"]]
        assert len(child) == 1, _standin_records(e3dir)
        assert (child[0]["ppid"], child[0]["net_ino"], child[0]["key_sha256"], child[0]["stop"]) == \
            (pair["pid"], pair["net_ino"], pair["key_sha256"], "eof"), child
        # A7: the record names the compiled unit that ran.
        identity = json.loads((evidence / "buzz-acp" / "unit-identity.json").read_text())
        assert (identity["pid"], identity["exe_realpath"], identity["entrypoint_realpath"],
                identity["entrypoint_sha256"], identity["uid"]) == \
            (pair["unit_pid"], str(buzz), str(buzz), _sha256(buzz), [UNIT_USER[0]] * 4), identity
        # D-051: the pair's namespace allowed exactly {relay, OmniRoute} (observed rules).
        rules = json.loads((evidence / "buzz-acp" / "runtime.json").read_text())["rules"]
        assert sorted(r for r in rules if " -j ACCEPT" in r and "-i lo" not in r and "-o lo" not in r) == sorted([
            f"-A INPUT -s {host_ip}/32 -p tcp -m tcp --sport {RELAY_PORT} -j ACCEPT",
            f"-A INPUT -s {host_ip}/32 -p tcp -m tcp --sport {omni_port} -j ACCEPT",
            f"-A OUTPUT -d {host_ip}/32 -p tcp -m tcp --dport {RELAY_PORT} -j ACCEPT",
            f"-A OUTPUT -d {host_ip}/32 -p tcp -m tcp --dport {omni_port} -j ACCEPT"]), rules
        assert "=== buzz-acp: exited 0 on stdin EOF ===" in runner.stdout
        checker_out = runner.stdout.split("=== checker ===\n", 1)[1]
        assert checker_out.splitlines()[0] == "units-manifest-invalid: buzz-acp override present"
        census = json.loads((evidence / "s0-01-census.json").read_text())
        assert census["tree"] == "present" and census["changed"] == [], census
    finally:
        _stop(relay)
        _stop(omni)
        _lib(f'egress_ns_destroy {ns}')
    assert _nat_rules_naming(host_if) == [] and _route_localnet(host_if) is None
    assert _census(ns) == CLEAN


@NEEDS_NETNS
@pytest.mark.parametrize("fault", ["rule-absent", "rule-refused"])
def test_d_without_the_relay_reach_the_pair_is_not_run(e3dir, fault):
    """D-051, the negative controls, through the REAL runner with the relay stand-in UP on the host's
    127.0.0.1: `rule-absent` — a PATH iptables swallows the nat add (exit 0, nothing added), so the
    preflight's C0 to the relay fails with the existing reason `positive control unreachable`;
    `rule-refused` — the nat add fails, `not-run|relay reach not established: <detail>`. Either way
    the relay saw nothing, and nothing is left (no nat rule, no interface, census)."""
    ns = "s0-05-buzz-acp"
    host_ip = _lib(f'egress_ns_host_ip {ns}').stdout.strip()
    host_if = _lib(f'egress_ns_host_if {ns}').stdout.strip()
    action = "exit 0" if fault == "rule-absent" else 'echo "E3-injected: nat rule refused" >&2; exit 1'
    shim = _iptables_shim(e3dir, action)
    env = _runner_env(e3dir, 18101, path_prefix=shim, override=_pair_override(e3dir))
    env["S0_05_PAIR_IDENTITY"] = str(_identity_file(e3dir / "id" / "pair.env"))
    evidence = e3dir / "evidence"
    relay = None
    try:
        relay = _listener(e3dir, RELAY_PORT, host="127.0.0.1", name="relay")
        _run_runner(env, evidence, "buzz-acp")
        reason = _unit_row(evidence, "buzz-acp")["reason"]
        if fault == "rule-absent":
            assert reason == f"positive control unreachable: {host_ip}:{RELAY_PORT} not reachable from {ns}"
        else:
            assert reason == "relay reach not established: E3-injected: nat rule refused"
        assert (e3dir / "relay.log").read_text() == ""
    finally:
        _stop(relay)
        _lib(f'egress_ns_destroy {ns}')
    assert _nat_rules_naming(host_if) == [] and _route_localnet(host_if) is None
    assert _census(ns) == CLEAN
