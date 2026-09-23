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


# curl 8.10 and later (the PC's 8.11.1) spell curl 8.5's generic connect failure "Could not connect to
# server". The first live bundle (2026-09-23 23:43Z) carried it on every C1 of both units, and the
# checker, which knew only the older spelling, failed it `denial-detail-unrecognized` (fail closed).
NEW_SPELLING_PROXY_DETAIL = ("curl: (7) Failed to connect to 127.0.0.1 port 40173 after 0 ms: "
                             "Could not connect to server")


def test_the_newer_curl_spelling_is_a_denial_when_it_names_its_own_target(tmp_path):
    """Every C1 record rewritten to the live PC text: rc 7 and curl 8.11.1's "Could not connect to
    server", naming the record's own target. The bundle passes, exactly as with 8.5's spelling."""
    bundle = copy_bundle(tmp_path)
    rows = records(bundle / "curl")
    rewritten = 0
    for row in rows:
        if row["canary"] == "C1":
            row.update(rc=7, detail=f"curl: (7) Failed to connect to {row['target']} port 443 after 3 ms: "
                                    "Could not connect to server")
            rewritten += 1
    assert rewritten >= 1
    write_records(bundle / "curl", rows)
    result = run_checker(bundle)
    assert result.returncode == 0, result.stdout
    assert result.stdout.splitlines()[-1].startswith("PASS: S0-05 no-direct-egress"), result.stdout


def test_the_newer_curl_spelling_behind_a_proxy_is_still_rejected(tmp_path):
    """The widening keeps the discriminator: the proxy-shaped denial in the NEW spelling names
    127.0.0.1, not the canary's target, and is rejected by the foreign-target rule."""
    bundle = copy_bundle(tmp_path)
    rows = [{**r, "rc": 7, "detail": NEW_SPELLING_PROXY_DETAIL} if r["canary"] == "C6" else r
            for r in records(bundle / "curl")]
    write_records(bundle / "curl", rows)
    result = run_checker(bundle)
    assert result.returncode == 1
    assert result.stdout.splitlines()[0].startswith("denial-detail-foreign-target: curl C6"), result.stdout
    assert "127.0.0.1" in result.stdout.splitlines()[0]


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
    """Declaring a second allowed destination without the rules to match is caught.
    E3-b item C (the fixture, not the expectation, changed): the positive control is per allowed entry
    now, so the widened entry also gets its passing C0 record — otherwise the positive control would
    refuse the bundle first, and this test is about the rule pin."""
    bundle = copy_bundle(tmp_path)
    gate = json.loads((bundle / "curl" / "gate.json").read_text())
    patch_json(bundle / "curl" / "gate.json", allowed=gate["allowed"] + ["1.2.3.4:443"])
    rows = records(bundle / "curl")
    c0 = next(r for r in rows if r["canary"] == "C0")
    rows.insert(rows.index(c0) + 1, {**c0, "target": "1.2.3.4:443"})
    write_records(bundle / "curl", rows)
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
    1/1 (one unit proven of one checked), not 2/2.
    E3-b item C (the fixture, not the expectation, changed): the old fixture duplicated the ONE C0
    record, which is now a refusal shape (two C0 records for one target); the unit here really has
    two allowed targets, each with its own C0 record (`_two_entry_bundle`)."""
    bundle = _two_entry_bundle(tmp_path)
    assert len([r for r in records(bundle / "curl") if r["canary"] == "C0"]) == 2
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
        # E3-b R1/R2 (a stricter fixture): the OmniRoute stand-in is shaped like the real service on the
        # PC (2026-09-23 06:57Z: 200 on /api/health, 401 on /v1/models).
        listener = _listener(e3dir, port, status={"/v1/models": 401})
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
        # E3-b R1 + R2 + P: the preflight and C0 each asked OmniRoute's health path — never /v1/models,
        # which this stand-in answers 401 like the real service — and C0 recorded the path it asked.
        asked = (e3dir / "listener.log").read_text().splitlines()
        assert asked == ["10.201.107.2 /api/health"] * 2, asked
        c0 = [row for row in (json.loads(line) for line in
                               (evidence / "hermes-acp" / "canaries.jsonl").read_text().splitlines() if line.strip())
              if row["canary"] == "C0"]
        assert [(r["target"], r.get("path"), r["rc"], r["http_status"]) for r in c0] == \
            [(f"10.201.107.1:{port}", "/api/health", 0, 200)], c0
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


def _listener(workdir, port, host="0.0.0.0", name="listener", status=None):
    """A host HTTP stand-in answering 200 on every GET and logging each client address and path (one
    line per request) to <workdir>/<name>.log. E3-b: `status` maps an exact path to the status that
    path answers (default 200), so one stand-in can be shaped like a real service — 200 on its health
    path, 401 or 404 on /v1/models. Returns the Popen; the caller kills it BY PID."""
    script = workdir / f"{name}.py"
    log = workdir / f"{name}.log"
    script.write_text(
        "import http.server, json, socketserver, sys\n"
        "LOG = sys.argv[3]\n"
        "STATUS = json.loads(sys.argv[4])\n"
        "class H(http.server.BaseHTTPRequestHandler):\n"
        "    def do_GET(self):\n"
        "        with open(LOG, 'a') as fh:\n"
        "            fh.write(self.client_address[0] + ' ' + self.path + '\\n')\n"
        "        self.send_response(STATUS.get(self.path, 200)); self.end_headers(); self.wfile.write(b'{}')\n"
        "    def log_message(self, *a): pass\n"
        "socketserver.TCPServer.allow_reuse_address = True\n"
        "socketserver.TCPServer((sys.argv[1], int(sys.argv[2])), H).serve_forever()\n")
    process = subprocess.Popen([sys.executable, str(script), host, str(port), str(log), json.dumps(status or {})],
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
    owner record are gone and the stand-in unit is dead.
    E3-b R4 (stricter): a stop stops — the runner exits 143 (`trap 'exit 143' TERM`, `cleanup` on EXIT
    only), writes no units.json, runs neither the census comparison (no s0-01-census.json) nor the
    checker. On the PIN (`trap cleanup EXIT INT TERM`) it ran cleanup and CONTINUED to its checker."""
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
        # E3-b R4: exit 143, and nothing after the stop.
        assert runner.returncode == 143, (runner.returncode, out, err)
        assert "=== checker ===" not in out, out
        assert not (evidence / "units.json").exists() and not (evidence / "s0-01-census.json").exists()
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
    v2_mode = "%04o" % stat.S_IMODE(v2.stat().st_mode)
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
        # A2' (E3-R1, a changed expectation): the census file names an entry by its path RELATIVE to
        # .markers and holds each side's entry count and digest plus the CHANGED entries' records, never
        # the whole list (at the PIN, `after` held every snapped entry by its absolute path). The count
        # still proves v2-negative was censused: ".", v2-run-1 and v2-negative.
        assert census["changed"] == ["v2-run-1"] and census["tree"] == "present", census
        assert census["before"]["entries"] == census["after"]["entries"] == 3, census
        assert "v2-negative" not in json.dumps(census), census
        assert [census["changed_records"]["v2-run-1"][side]["mode"] for side in ("before", "after")] == \
            [v2_mode, "0700"], census
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


def _iptables_shim(workdir, action, match="-t nat -A PREROUTING"):
    """A PATH `iptables` that intercepts ONE exact argv — the relay reach's nat add, or the argv `match`
    names (E3-R1: the teardown's `-t nat -D PREROUTING`) — and runs the real binary for everything else
    (the namespace gates run through it too)."""
    shim = workdir / "shim"
    shim.mkdir()
    (shim / "iptables").write_text(
        "#!/bin/bash\n"
        f'if [ "$1 $2 $3 $4" = "{match}" ]; then {action}; fi\n'
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
    the runner exits, no PREROUTING rule names the pair's interface and the interface is gone.
    E3-b (R1-R3, A, P, C): both stand-ins are shaped like the real services on the PC (2026-09-23
    06:57Z: the relay 200 on /health and 404 on /v1/models, OmniRoute 200 on /api/health and 401 on
    /v1/models); the preflight and C0 ask each service's health path; the collector records the WHOLE
    allow-set [relay, OmniRoute] and one C0 per entry, in order, with its path; and the checker's
    positive control and rule pin both pass on this real bundle (E3 section 9 measured
    `egress-rules-unpinned` here: the PIN collector recorded one entry)."""
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
        relay = _listener(e3dir, RELAY_PORT, host="127.0.0.1", name="relay", status={"/v1/models": 404})
        omni = _listener(e3dir, omni_port, name="omniroute", status={"/v1/models": 401})
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
        # E3-b R1 (a changed expectation: the PIN's preflight asked /v1/models, which the real relay
        # answers 404): the preflight and C0 each asked the relay's health path, the pair its own path.
        assert sorted(seen) == sorted([f"{ns_ip} /health"] * 2 + [f"{ns_ip} /pair-own-socket"]), seen
        assert (e3dir / "omniroute.log").read_text().splitlines() == [f"{ns_ip} /api/health"] * 2
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
        # E3-b A + P + C: the collector recorded the WHOLE allow-set, in the runner's order (R3: relay,
        # then OmniRoute), one C0 per entry with its health path, each 2xx; the checker's positive
        # control and its rule pin both pass on this real bundle.
        unit_dir = evidence / "buzz-acp"
        gate = json.loads((unit_dir / "gate.json").read_text())
        allowed = [f"{host_ip}:{RELAY_PORT}", f"{host_ip}:{omni_port}"]
        assert gate["allowed"] == allowed, gate
        c0 = [r for r in records(unit_dir) if r["canary"] == "C0"]
        assert [(r["target"], r.get("path"), r["rc"], r["http_status"]) for r in c0] == \
            [(allowed[0], "/health", 0, 200), (allowed[1], "/api/health", 0, 200)], c0
        assert chk.check_positive_control(chk.read_records(unit_dir, "buzz-acp"), "buzz-acp", gate["allowed"]) == 1
        assert chk.check_runtime_and_rules(unit_dir, "buzz-acp", gate).startswith("gate-fired: buzz-acp "), gate
        checker_out = runner.stdout.split("=== checker ===\n", 1)[1]
        print("the full checker's first line on the pair bundle:", checker_out.splitlines()[0])
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


# ===================================================================== E3-b — G, A, P, C, R
# tasks/briefs/s0-05-support/E3-b-brief.md: G one allow-entry rule in three places; A the collector
# records the unit's whole allow-set; P the probe path rides the C0 record; C the checker's positive
# control is per allowed entry; R the runner (R1 per-service health paths, R2 the preflight grades
# what the checker grades, R3 the whole entry list reaches the collector, R4 a stop stops).

COLLECTOR = PROOF / "run_canaries.sh"
NO_NS = "s0-05-e3b-nonexistent-ns"      # never created: an argument list that got past validation reads exit 3
LOCALES = ("C", "C.UTF-8")               # the locales this sandbox has (`locale -a`); the rule is ASCII in each
ARABIC_INDIC = str.maketrans("0123456789", "".join(chr(0x0660 + digit) for digit in range(10)))

# G: one table, the rule as the brief states it (never read from either implementation): a dotted quad
# of four decimal octets 0-255 with no leading zero (a lone 0 allowed); a port 1-65535 with no leading
# zero and at most five digits; ASCII only.
_G_ROWS = [
    ("valid", "10.201.7.1:20128", True),
    ("zeros-port-1", "0.0.0.0:1", True),
    ("all-max", "255.255.255.255:65535", True),
    ("leading-zero-octet", "010.201.7.1:20128", False),
    ("leading-zero-port", "10.201.7.1:080", False),
    ("octet-256", "256.201.7.1:20128", False),
    ("port-0", "10.201.7.1:0", False),
    ("port-65536", "10.201.7.1:65536", False),
    ("port-6-digits", "10.201.7.1:100000", False),
    ("port-20-digits", "10.201.7.1:99999999999999999999", False),
    ("arabic-indic-port", "10.201.7.1:" + "20128".translate(ARABIC_INDIC), False),
    ("arabic-indic-octet", "10".translate(ARABIC_INDIC) + ".201.7.1:20128", False),
    *[(f"{name}-{where}", entry, False)
      for name, ws in (("space", " "), ("tab", "\t"), ("vt", "\v"), ("ff", "\f"), ("nl", "\n"))
      for where, entry in (("inside", f"10.201.7.1:201{ws}28"), ("end", f"10.201.7.1:20128{ws}"))],
    ("empty", "", False),
    ("missing-port", "10.201.7.1", False),
    ("trailing-colon", "10.201.7.1:", False),
    ("ipv6", "[::1]:20128", False),
    ("hostname", "localhost:20128", False),
]


def _checker_accepts(entry):
    """`_split_ip_port`'s verdict. A refusal must carry one of its two texts, exactly."""
    try:
        chk._split_ip_port(entry)
    except chk.Failure as error:
        texts = (f"gate-manifest-invalid: allow entry {entry!r} is not <ipv4>:<port>",
                 f"gate-manifest-invalid: allow entry {entry!r} is out of range")
        return False if str(error) in texts else f"refused with another text: {error}"
    return True


def _library_accepts(entry, locale):
    """egress_allow_entry_ok's verdict under one locale: a SILENT predicate, status 0 or 1 and no output;
    anything else comes back as the raw result, so a failure names what the library did."""
    result = subprocess.run(["bash", "-c", '. "$0" && egress_allow_entry_ok "$1"', str(LIB), entry],
                            capture_output=True, text=True, timeout=30, env={**os.environ, "LC_ALL": locale})
    if result.returncode in (0, 1) and not result.stdout and not result.stderr:
        return result.returncode == 0
    return f"rc={result.returncode} out={result.stdout!r} err={result.stderr.strip()!r}"


@pytest.mark.parametrize("entry, accepted", [row[1:] for row in _G_ROWS], ids=[row[0] for row in _G_ROWS])
def test_e3b_g_one_allow_entry_rule_in_the_library_and_the_checker(entry, accepted):
    """G: ONE allow-entry rule, held by the library's silent predicate `egress_allow_entry_ok` (status 0
    valid, 1 not, no output) under every locale this venue has, and by the checker's `_split_ip_port`
    (its two refusal texts kept): the same accept/refuse on every row of one table, argv built here.
    On the PIN the checker read `\\d` (every Unicode digit) and `$` (which also matches before a trailing
    newline), and the library had no predicate to share."""
    verdicts = {"checker": _checker_accepts(entry),
                **{f"library[{locale}]": _library_accepts(entry, locale) for locale in LOCALES}}
    assert verdicts == dict.fromkeys(verdicts, accepted), (entry, verdicts)


@pytest.mark.parametrize("bad", ["10.201.1.1:" + "80".translate(ARABIC_INDIC), "10.201.1.1:080",
                                 "010.201.1.1:80", "10.201.1.1:80\n"],
                         ids=["arabic-indic-port", "leading-zero-port", "leading-zero-octet", "trailing-nl"])
def test_e3b_g_egress_ns_create_checks_every_entry_by_the_one_rule(bad):
    """G: egress_ns_create calls the shared predicate for EVERY entry — here a valid FIRST entry and an
    invalid SECOND one — and keeps its text, status and ordering byte-for-byte: 64 and the exact contract
    line, before any namespace, veth, rule or record work (census on a root venue). Green on the PIN by
    design (its inline rule checked every entry): this guards the move into one function (B14)."""
    ns = f"s0-05-e3b-{uuid.uuid4().hex[:8]}"
    try:
        result = subprocess.run(["bash", "-c", '. "$0" && egress_ns_create "$@"', str(LIB), ns, "10.201.1.1:1", bad],
                                capture_output=True, text=True, timeout=60)
        assert (result.returncode, result.stderr) == \
            (64, f"egress: allow entry must be <ip>:<port>, got '{bad}'\n"), result
        if netns_capable():
            assert _census(ns) == CLEAN, _census(ns)
    finally:
        if netns_capable():
            _lib(f'egress_ns_destroy {ns}')


def _collect(tmp_path, allowed, blocked="", venue="sandbox", ns=NO_NS):
    """The REAL collector against a namespace that does not exist: an argument list that got past
    validation reaches the namespace and reads the exit-3 unreadable-counter refusal, so an exit 64 with
    no evidence directory proves the refusal came first."""
    evidence = tmp_path / "ev"
    result = subprocess.run(["bash", str(COLLECTOR), "curl", ns, allowed, str(evidence), blocked, venue],
                            capture_output=True, text=True, timeout=120)
    return result, evidence


_NOT_ENTRY = "run_canaries: allowed entry '{}' is not <ip>:<port>[/<path>]"
_A_REFUSALS = [   # (id, allowed, blocked, venue, the exact stderr line); {H} = the host address of NO_NS
    ("empty-argument", "", "", "sandbox", _NOT_ENTRY.format("")),
    ("leading-comma", ",10.201.1.1:80", "", "sandbox", _NOT_ENTRY.format("")),
    ("trailing-comma", "10.201.1.1:80,", "", "sandbox", _NOT_ENTRY.format("")),
    ("doubled-comma", "10.201.1.1:80,,10.201.1.2:80", "", "sandbox", _NOT_ENTRY.format("")),
    ("leading-zero-port", "10.201.1.1:080", "", "sandbox", _NOT_ENTRY.format("10.201.1.1:080")),
    ("overflow", "10.201.1.1:9223372036854775807", "", "sandbox",
     _NOT_ENTRY.format("10.201.1.1:9223372036854775807")),
    ("bad-second-entry", "10.201.1.1:80,10.201.1.1:0/health", "", "sandbox",
     _NOT_ENTRY.format("10.201.1.1:0/health")),
    ("path-with-space", "10.201.1.1:80/bad path", "", "sandbox", _NOT_ENTRY.format("10.201.1.1:80/bad path")),
    ("path-64-chars", "10.201.1.1:80/" + "a" * 64, "", "sandbox", _NOT_ENTRY.format("10.201.1.1:80/" + "a" * 64)),
    ("path-non-ascii", "10.201.1.1:80/héalth", "", "sandbox", _NOT_ENTRY.format("10.201.1.1:80/héalth")),
    ("path-query", "10.201.1.1:80/health?probe=1", "", "sandbox", _NOT_ENTRY.format("10.201.1.1:80/health?probe=1")),
    ("path-only", "/health", "", "sandbox", _NOT_ENTRY.format("/health")),
    ("listed-twice", "10.201.1.1:80,10.201.1.1:80", "", "sandbox",
     "run_canaries: allowed entry '10.201.1.1:80' is listed twice"),
    ("listed-twice-other-path", "10.201.1.1:80/a,10.201.1.1:80/b", "", "sandbox",
     "run_canaries: allowed entry '10.201.1.1:80' is listed twice"),
    ("blocked-with-a-path", "10.201.1.1:80", "10.201.1.1:81/health", "sandbox",
     "run_canaries: blocked entry '10.201.1.1:81/health' is not <ip>:<port>"),
    ("blocked-leading-zero", "10.201.1.1:80", "10.201.1.1:081", "sandbox",
     "run_canaries: blocked entry '10.201.1.1:081' is not <ip>:<port>"),
    ("blocked-explicit-in-set", "10.201.1.1:80,10.201.1.1:81", "10.201.1.1:81", "sandbox",
     "run_canaries: blocked entry '10.201.1.1:81' is in the allowed set"),
    ("blocked-default-in-set", "{H}:3999,{H}:4000", "", "sandbox",
     "run_canaries: blocked entry '{H}:4000' is in the allowed set"),
    ("default-blocked-65536", "10.201.1.1:65535", "", "sandbox",
     "run_canaries: default blocked port 65536 is out of range; pass a blocked entry"),
    ("order-3-before-5-and-6", "10.201.1.1:0", "10.201.1.1:0", "x", _NOT_ENTRY.format("10.201.1.1:0")),
    ("order-5-before-6", "10.201.1.1:80", "10.201.1.1:0", "x",
     "run_canaries: blocked entry '10.201.1.1:0' is not <ip>:<port>"),
    ("order-default-5-before-6", "10.201.1.1:65535", "", "x",
     "run_canaries: default blocked port 65536 is out of range; pass a blocked entry"),
    ("order-6-last", "10.201.1.1:80", "", "x", "run_canaries: venue must be sandbox or pc, got 'x'"),
]


@pytest.mark.parametrize("allowed, blocked, venue, line", [row[1:] for row in _A_REFUSALS],
                         ids=[row[0] for row in _A_REFUSALS])
def test_e3b_a_a_bad_argument_is_refused_before_anything(tmp_path, allowed, blocked, venue, line):
    """A: `<allowed>` is a comma-separated list of `<ip>:<port>[<path>]` entries. Arguments are validated
    in the order 3, 5, 6; the first failure exits 64 with its exact text (the whole stderr) BEFORE any
    arithmetic on an input, any namespace access (a namespace access would read the exit-3 refusal
    instead), any directory or file and any canary — no evidence directory. The venue refusal keeps its
    text. On the PIN the collector did arithmetic on the raw port first (octal, overflow) and took the
    whole list as one entry."""
    host = _lib(f"egress_ns_host_ip {NO_NS}").stdout.strip()
    allowed, line = allowed.replace("{H}", host), line.replace("{H}", host)
    result, evidence = _collect(tmp_path, allowed, blocked, venue)
    assert (result.returncode, result.stderr) == (64, line + "\n"), result
    assert not evidence.exists()


def test_e3b_a_an_injected_port_never_runs(tmp_path):
    """A (the premise, measured on the PIN): a port of the form `NS[$(touch <file>)]` made the collector's
    `$((ALLOWED_PORT + 1))` RUN the command substitution (NS names a set variable, so its subscript is
    expanded). The argv is built here, never through a shell: now the one rule refuses the entry, exit 64,
    and the file never appears."""
    marker = tmp_path / "the-injected-command-ran"
    entry = f"10.201.1.1:NS[$(touch {marker})]"
    result, evidence = _collect(tmp_path, entry)
    assert (result.returncode, result.stderr) == (64, _NOT_ENTRY.format(entry) + "\n"), result
    assert not marker.exists(), "the injected command ran"
    assert not evidence.exists()


@pytest.mark.skipif(shutil.which("ip") is None, reason="iproute2 absent; NOT run here")
@pytest.mark.parametrize("allowed, blocked", [
    ("10.201.1.1:12800", ""),
    ("10.201.1.1:12800,10.201.1.1:3999/health", ""),
    ("10.201.1.1:12800/api/health,10.201.1.1:3999/", "10.201.1.1:4000"),
    ("10.201.1.1:1/" + "~._-/aZ09" * 7, ""),
], ids=["one-entry", "two-entries-a-path", "paths-explicit-blocked", "path-of-63-chars"])
def test_e3b_a_a_valid_argument_list_reaches_the_namespace(tmp_path, allowed, blocked):
    """The other side of every refusal above: the same collector, a valid list (one entry, two entries,
    paths, an explicit blocked entry, a path of the full 63 characters after its slash) gets past
    validation and reaches the namespace — the exit-3 unreadable-counter refusal, nothing else on stderr,
    no evidence directory."""
    result, evidence = _collect(tmp_path, allowed, blocked)
    assert (result.returncode, result.stderr) == \
        (3, f"run_canaries: cannot read the OUTPUT DROP counter of {NO_NS}\n"), result
    assert not evidence.exists()


@NEEDS_NETNS
def test_e3b_a_a_two_entry_run_records_the_whole_allow_set(e3dir):
    """A + P on a REAL namespace with two allowed entries: the first carries a probe path, the second
    none (it probes /v1/models, passed explicitly). gate.json `allowed` = both ip:port parts in order; C0
    runs once per entry, in order, with the entry's ip:port as target and its path recorded, and each
    listener's own log shows the path asked from the namespace's address; the recorded rules are the
    checker's own derivation from that allow-set (check_runtime_and_rules passes). On the PIN the
    collector took the whole list as ONE entry: `"allowed": [<the list>]` (E3 section 9)."""
    ns = f"s0-05-e3b-{uuid.uuid4().hex[:8]}"
    host_ip = _lib(f"egress_ns_host_ip {ns}").stdout.strip()
    ns_ip = _lib(f"egress_ns_ip {ns}").stdout.strip()
    first, second = f"{host_ip}:18120", f"{host_ip}:18130"   # not adjacent: the default blocked is first + 1
    root = e3dir / "evidence"
    listeners = []
    try:
        created = _lib(f"egress_ns_create {ns} {first} {second}")
        assert created.returncode == 0, created.stderr
        listeners = [_listener(e3dir, 18120, name="first"), _listener(e3dir, 18130, name="second")]
        run = subprocess.run(["bash", str(COLLECTOR), "curl", ns, f"{first}/health,{second}", str(root), "", "sandbox"],
                             capture_output=True, text=True, timeout=180)
        assert run.returncode == 0, run.stderr
        gate = json.loads((root / "curl" / "gate.json").read_text())
        assert gate["allowed"] == [first, second], gate
        c0 = [r for r in records(root / "curl") if r["canary"] == "C0"]
        assert [(r["target"], r.get("path"), r["rc"], r["http_status"]) for r in c0] == \
            [(first, "/health", 0, 200), (second, "/v1/models", 0, 200)], c0
        assert (e3dir / "first.log").read_text().splitlines() == [f"{ns_ip} /health"]
        assert (e3dir / "second.log").read_text().splitlines() == [f"{ns_ip} /v1/models"]
        c6 = [r for r in records(root / "curl") if r["canary"] == "C6"]
        assert [r["target"] for r in c6] == [f"{host_ip}:18121"], c6          # the default blocked entry
        runtime = json.loads((root / "curl" / "runtime.json").read_text())
        assert runtime["rules"] == chk.expected_rules([first, second]), runtime["rules"]
        assert chk.check_positive_control(chk.read_records(root / "curl", "curl"), "curl", gate["allowed"]) == 1
        assert chk.check_runtime_and_rules(root / "curl", "curl", gate).startswith("gate-fired: curl "), runtime
    finally:
        for listener in listeners:
            _stop(listener)
        _lib(f"egress_ns_destroy {ns}")
    assert _census(ns) == CLEAN, _census(ns)


def test_e3b_p_the_c0_record_carries_the_path_it_asked(tmp_path):
    """P: `c0_allowed_target.sh` adds `path=<path>` to its record (emit_canary keeps a non-integer value
    as a string) — the target alone no longer says what was asked. The stand-in's own log shows that
    path was the one requested. No namespace needed: the canary itself, against a loopback stand-in."""
    port = 18122
    listener = _listener(tmp_path, port, host="127.0.0.1", name="c0-standin")
    try:
        result = subprocess.run(["bash", str(PROOF / "canaries" / "c0_allowed_target.sh"), "curl",
                                 f"127.0.0.1:{port}", "/api/health"], capture_output=True, text=True, timeout=60)
    finally:
        _stop(listener)
    record = json.loads(result.stdout)
    assert (record["target"], record.get("path"), record["rc"], record["http_status"]) == \
        (f"127.0.0.1:{port}", "/api/health", 0, 200), record
    assert (tmp_path / "c0-standin.log").read_text().splitlines() == ["127.0.0.1 /api/health"]


def _two_entry_bundle(tmp_path, second="10.201.136.1:3999"):
    """The committed mechanism bundle declared with a SECOND allowed entry: gate.json `allowed` [first,
    second] with the recorded rules and the digest re-derived for both (the checker's own derivation: the
    rule pin is not what this fixture tests), and a passing C0 record for the second entry right after
    the first one's."""
    bundle = copy_bundle(tmp_path)
    unit = bundle / "curl"
    gate = json.loads((unit / "gate.json").read_text())
    runtime = json.loads((unit / "runtime.json").read_text())
    assert runtime["rules"] == chk.expected_rules(gate["allowed"]), "the committed rules are the one-entry set"
    allowed = gate["allowed"] + [second]
    rules = chk.expected_rules(allowed)
    patch_json(unit / "runtime.json", rules=rules)
    patch_json(unit / "gate.json", allowed=allowed, rules_sha256=chk.rules_digest(rules))
    rows = records(unit)
    c0 = next(r for r in rows if r["canary"] == "C0")
    rows.insert(rows.index(c0) + 1, {**c0, "target": second})
    write_records(unit, rows)
    return bundle


@pytest.mark.parametrize("shape", ["allowed-entry-without-c0", "c0-target-outside-the-allow-set",
                                   "two-c0-for-one-target", "second-c0-not-2xx"])
def test_e3b_c_the_positive_control_is_per_allowed_entry(tmp_path, shape):
    """C: a unit proves its positive control only if its C0 targets are every allowed entry exactly once
    and nothing else, and every C0 record meets today's predicate. Every failure is the one line
    `positive-control-failed: <unit>`. Each shape breaks ONE half: an allowed entry with no C0 record and
    two C0 records for one target break "every allowed entry exactly once"; a C0 target outside the
    allow-set breaks "nothing else"; a second C0 answering 401 breaks the per-record predicate. On the
    PIN only the per-record predicate was graded: the first three shapes PASSED."""
    two = shape in ("allowed-entry-without-c0", "second-c0-not-2xx")
    bundle = _two_entry_bundle(tmp_path) if two else copy_bundle(tmp_path)
    rows = records(bundle / "curl")
    c0 = [r for r in rows if r["canary"] == "C0"]
    if shape == "allowed-entry-without-c0":
        rows.remove(c0[1])
    elif shape == "c0-target-outside-the-allow-set":
        rows.insert(rows.index(c0[0]) + 1, {**c0[0], "target": "10.201.136.1:4000"})
    elif shape == "two-c0-for-one-target":
        rows.insert(rows.index(c0[0]) + 1, dict(c0[0]))
    else:
        rows[rows.index(c0[1])] = {**c0[1], "http_status": 401}
    write_records(bundle / "curl", rows)
    result = run_checker(bundle)
    assert result.returncode == 1, result.stdout
    assert result.stdout.splitlines()[0] == "positive-control-failed: curl"


@NEEDS_NETNS
def test_e3b_r2_a_health_path_answering_401_launches_nothing(e3dir):
    """R2: the preflight grades what the checker grades — the collector's own C0 request (the same path,
    the proxy variables scrubbed, the canaries' timeouts) must get rc 0 AND a 2xx. A stand-in whose health
    path answers 401 is an HTTP answer outside 2xx: stderr `positive-control-not-2xx: <unit>
    <ip:port><path> HTTP <code>`, the row `not-run|positive control not 2xx: <ip:port><path> answered HTTP
    <code> from <ns>`, the namespace destroyed (census) and NO unit launched (no stand-in record; the
    stand-in saw the one preflight request). The stand-in answers 401 on /v1/models too: on the PIN the
    preflight asked /v1/models and passed ANY HTTP answer (curl without -f), so the unit launched and
    only the checker would have failed it later."""
    port = 18123
    env = _runner_env(e3dir, port)
    override = json.loads((e3dir / "override.json").read_text())
    evidence = e3dir / "evidence"
    listener = None
    probe = f"10.201.107.1:{port}/api/health"
    try:
        listener = _listener(e3dir, port, status={"/api/health": 401, "/v1/models": 401})
        runner = _run_runner(env, evidence, "hermes-acp", timeout=240)
        assert _unit_row(evidence, "hermes-acp") == {
            "unit": "hermes-acp", "status": "not-run", "override": override,
            "reason": f"positive control not 2xx: {probe} answered HTTP 401 from s0-05-hermes-acp"}, runner.stderr
        assert f"positive-control-not-2xx: hermes-acp {probe} HTTP 401" in runner.stderr.splitlines(), runner.stderr
        assert _standin_records(e3dir) == [], "a unit launched past a not-2xx preflight"
        assert (e3dir / "listener.log").read_text().splitlines() == ["10.201.107.2 /api/health"]
    finally:
        _stop(listener)
        _lib('egress_ns_destroy s0-05-hermes-acp')
    assert _census("s0-05-hermes-acp") == CLEAN


@NEEDS_NETNS
def test_e3b_r4_sigint_stops_the_runner_with_130(e3dir):
    """R4: `trap 'exit 130' INT` with `cleanup` on EXIT only — SIGINT mid-leg ends the runner with 130:
    the namespace it owns is gone with its veth, /etc/netns entry and owner record, the unit is dead,
    and nothing runs after the stop (no units.json, no census comparison, no checker). On the PIN
    (`trap cleanup EXIT INT TERM`) the runner ran cleanup and CONTINUED to its checker."""
    ns = "s0-05-hermes-acp"
    env = _runner_env(e3dir, 18124)
    evidence = e3dir / "evidence"
    listener = runner = None
    try:
        listener = _listener(e3dir, 18124)
        runner = subprocess.Popen(["bash", str(RUNNER), str(evidence), "hermes-acp"],
                                  stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, env=env)
        _wait_for(lambda: _standin_records(e3dir), 60, "the unit to start inside the namespace")
        standin = _standin_records(e3dir)[0]["pid"]
        runner.send_signal(signal.SIGINT)
        out, err = runner.communicate(timeout=180)
        assert runner.returncode == 130, (runner.returncode, out, err)
        assert "=== checker ===" not in out, out
        assert not (evidence / "units.json").exists() and not (evidence / "s0-01-census.json").exists()
        assert _census(ns) == CLEAN, (_census(ns), out, err)
        assert not _pid_alive(standin), f"stand-in {standin} outlived its runner"
    finally:
        _stop(runner)
        _stop(listener)
        _lib(f'egress_ns_destroy {ns}')


@NEEDS_NETNS
def test_e3b_r4_a_stop_in_the_first_leg_starts_no_second_leg(e3dir):
    """R4: a two-unit run (hermes-acp, then buzz-acp, with every precondition of the pair's leg met: its
    pins through the override and its identity file) stopped with SIGTERM during its FIRST leg exits 143,
    runs `cleanup` ONCE and never creates the second unit's namespace. The instrument: a PATH `ip` shim
    logs every `ip` call the runner makes; the test writes a STOP line into that log just before the
    signal. After it: exactly one `netns del s0-05-hermes-acp` (the one cleanup), and no call anywhere
    names s0-05-buzz-acp. On the PIN the TERM trap ran cleanup, the loop went on, the leg teardown
    destroyed the name a second time and the pair's namespace was built."""
    shim = e3dir / "shim"
    shim.mkdir()
    ip_log = e3dir / "ip-calls.log"
    (shim / "ip").write_text(f'#!/bin/bash\nprintf "%s\\n" "$*" >> {ip_log}\nexec {IP_REAL} "$@"\n')
    (shim / "ip").chmod(0o755)
    port = 18125
    env = _runner_env(e3dir, port, path_prefix=shim, override=_pair_override(e3dir))
    env["S0_05_PAIR_IDENTITY"] = str(_identity_file(e3dir / "id" / "pair.env"))
    evidence = e3dir / "evidence"
    listener = runner = None
    try:
        listener = _listener(e3dir, port)
        runner = subprocess.Popen(["bash", str(RUNNER), str(evidence), "hermes-acp", "buzz-acp"],
                                  stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, env=env)
        _wait_for(lambda: _standin_records(e3dir), 60, "the first unit to start inside its namespace")
        with open(ip_log, "a") as handle:
            handle.write("=== STOP ===\n")
        runner.send_signal(signal.SIGTERM)
        out, err = runner.communicate(timeout=240)
        assert runner.returncode == 143, (runner.returncode, out, err)
        calls = ip_log.read_text().splitlines()
        assert "netns add s0-05-hermes-acp" in calls, calls           # the instrument saw the first leg
        after = calls[calls.index("=== STOP ===") + 1:]
        assert after.count("netns del s0-05-hermes-acp") == 1, after   # cleanup ran once
        assert not [call for call in calls if "s0-05-buzz-acp" in call], calls
        assert "=== buzz-acp:" not in out and "=== checker ===" not in out, out
        assert not (evidence / "units.json").exists()
    finally:
        _stop(runner)
        _stop(listener)
        _lib('egress_ns_destroy s0-05-hermes-acp')
        _lib('egress_ns_destroy s0-05-buzz-acp')
    assert _census("s0-05-hermes-acp") == CLEAN and _census("s0-05-buzz-acp") == CLEAN
    assert _nat_rules_naming(_lib('egress_ns_host_if s0-05-buzz-acp').stdout.strip()) == []


# ===================================================================== E3-R1 — R1 (VERIFY-E3 F3) + R2 (A2')
# tasks/briefs/s0-05-support/E3-R1-brief.md. R1: `cleanup` cannot be aborted by a second INT or TERM,
# PID-directed or group-directed, and every command it starts inherits that protection. Each runner
# below runs in its OWN session (pgid = its pid), so a group-directed signal reaches the runner, its
# units and whatever `cleanup` started, and nothing of pytest's. R2: A2 as the coordinator amended it
# (A2'): the census covers every entry under <base>/.markers, recursively, never following a symbolic
# link; its file holds counts, digests and the CHANGED entries only.

STOP_RC = {"INT": 130, "TERM": 143}

# The hermes-acp stand-in's SIGTERM handler takes 3 s (a unit slow to shut down), and first writes a
# marker the test waits for: the proof that `cleanup`'s own SIGTERM reached the unit.
SLOW_STOP = """
import signal, time
def _slow_stop(signum, frame):
    with open(os.path.join(REC, "term-%d" % os.getpid()), "a") as fh:
        fh.write("TERM\\n")
    time.sleep(3)
    os._exit(0)
signal.signal(signal.SIGTERM, _slow_stop)
"""


def _runner_session(env, evidence, *units):
    """The REAL runner in its own session: its pgid is its pid, the group a group-directed signal names."""
    return subprocess.Popen(["bash", str(RUNNER), str(evidence), *units], stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE, text=True, env=env, start_new_session=True)


def _send(runner, name, target):
    sig = {"INT": signal.SIGINT, "TERM": signal.SIGTERM}[name]
    if target == "group":
        os.killpg(runner.pid, sig)
    else:
        runner.send_signal(sig)


def _route_localnet_state(host_if):
    """route_localnet of all, default and <host_if> (None while that interface does not exist)."""
    return {name: _route_localnet(name) for name in ("all", "default", host_if)}


@NEEDS_NETNS
@pytest.mark.parametrize("first,second,target", [
    ("TERM", "TERM", "pid"), ("TERM", "INT", "pid"), ("INT", "TERM", "group")],
    ids=["term-then-term-to-the-pid", "term-then-int-to-the-pid", "int-then-term-to-the-group"])
def test_e3r1_r1_b_a_second_signal_while_cleanup_waits_for_a_slow_unit(e3dir, first, second, target):
    """R1, VERIFY-E3's shape (b): a unit whose SIGTERM handler takes 3 s. The first signal goes to the
    runner's pid in the launch window; the second fires once the unit has received `cleanup`'s SIGTERM
    (its marker), i.e. while `cleanup` waits for the unit. Afterwards nothing of the leg is left — no
    namespace, veth, /etc/netns/<ns>, owner record or relay-reach rule, route_localnet as before the run —
    and the exit status is the FIRST signal's. On the PIN the second signal's `exit` abandoned the EXIT
    trap: the namespace outlived the run (VERIFY-E3 section 10), and a second INT turned 143 into 130."""
    ns = "s0-05-hermes-acp"
    host_if = _lib(f'egress_ns_host_if {ns}').stdout.strip()
    port = 18144
    env = _runner_env(e3dir, port, extra=SLOW_STOP)
    evidence = e3dir / "evidence"
    before = _route_localnet_state(host_if)
    listener = runner = None
    try:
        listener = _listener(e3dir, port)
        runner = _runner_session(env, evidence, "hermes-acp")
        _wait_for(lambda: _standin_records(e3dir), 60, "the unit to start inside the namespace")
        unit = _standin_records(e3dir)[0]["pid"]
        _send(runner, first, "pid")
        _wait_for(lambda: list((e3dir / "rec").glob("term-*")), 60, "cleanup's SIGTERM to reach the unit")
        assert runner.poll() is None, "the runner ended before the second signal"
        _send(runner, second, target)
        out, err = runner.communicate(timeout=120)
        assert _census(ns) == CLEAN, (_census(ns), runner.returncode, out, err)
        assert _nat_rules_naming(host_if) == [] and _route_localnet_state(host_if) == before
        assert runner.returncode == STOP_RC[first], (runner.returncode, out, err)
        assert not _pid_alive(unit), f"unit {unit} outlived its runner"
        assert "=== checker ===" not in out, out
        assert not (evidence / "units.json").exists() and not (evidence / "s0-01-census.json").exists()
    finally:
        _stop(runner)
        _stop(listener)
        _lib(f'egress_ns_destroy {ns}')
    assert _census(ns) == CLEAN


@NEEDS_NETNS
@pytest.mark.skipif(shutil.which("gcc") is None,
                    reason="the buzz-acp stand-in is compiled (A7 grades /proc/<pid>/exe); no C compiler — NOT run here")
@pytest.mark.parametrize("second,target", [("TERM", "pid"), ("TERM", "group"), ("INT", "group")],
                         ids=["term-to-the-pid", "term-to-the-group", "int-to-the-group"])
def test_e3r1_r1_c_a_second_signal_inside_the_relay_reach_removal(e3dir, second, target):
    """R1, VERIFY-E3's shape (c): the pair's leg with a PATH `iptables` that holds the teardown's `-t nat -D`
    for 2 s (timing only; then it runs the real binary with the same argv). SIGTERM goes to the runner's pid
    while the pair runs; the second signal fires inside that hold. Afterwards: exit 143 (the first signal's),
    no nat rule names the pair's interface, route_localnet is as before the run, nothing of the namespace is
    left. A signal to the whole group also reaches the held `iptables`, a command `cleanup` started, which
    must inherit the protection. On the PIN: route_localnet=1 outlived the run (pid), and so did D-051's
    DNAT itself (group: the held removal was killed)."""
    ns = "s0-05-buzz-acp"
    host_if = _lib(f'egress_ns_host_if {ns}').stdout.strip()
    omni_port = 18145
    held = e3dir / "nat-del-held"
    shim = _iptables_shim(e3dir, f"echo held >> {held}; sleep 2", match="-t nat -D PREROUTING")
    buzz = _pair_standin(e3dir)
    env = _runner_env(e3dir, omni_port, path_prefix=shim, override={
        "PINNED_BUZZ_ACP_EXE_REALPATH": str(buzz), "PINNED_BUZZ_ACP_SHA256": _sha256(buzz)})
    env["S0_05_PAIR_IDENTITY"] = str(_identity_file(e3dir / "id" / "pair.env"))
    evidence = e3dir / "evidence"
    before = _route_localnet_state(host_if)
    relay = omni = runner = None
    try:
        relay = _listener(e3dir, RELAY_PORT, host="127.0.0.1", name="relay")
        omni = _listener(e3dir, omni_port, name="omniroute")
        runner = _runner_session(env, evidence, "buzz-acp")
        _wait_for(lambda: _standin_records(e3dir, "pair"), 60, "the pair to start inside its namespace")
        assert len(_nat_rules_naming(host_if)) == 1 and _route_localnet(host_if) == "1"   # the reach is live
        _send(runner, "TERM", "pid")
        _wait_for(held.exists, 60, "cleanup to enter the relay reach's nat removal")
        assert runner.poll() is None, "the runner ended before the second signal"
        _send(runner, second, target)
        out, err = runner.communicate(timeout=120)
        assert _nat_rules_naming(host_if) == [], (_nat_rules_naming(host_if), runner.returncode, err)
        assert _route_localnet_state(host_if) == before, (_route_localnet_state(host_if), before, err)
        assert _census(ns) == CLEAN, (_census(ns), runner.returncode, out, err)
        assert runner.returncode == 143, (runner.returncode, out, err)
        assert held.read_text() == "held\n"                      # one removal, held once
        assert "=== checker ===" not in out and not (evidence / "units.json").exists()
    finally:
        _stop(runner)
        _stop(relay)
        _stop(omni)
        _lib(f'egress_ns_destroy {ns}')
    assert _nat_rules_naming(host_if) == [] and _route_localnet(host_if) is None
    assert _census(ns) == CLEAN


@NEEDS_NETNS
@pytest.mark.parametrize("target", ["pid", "group"])
def test_e3r1_r1_a_signal_while_cleanup_reaps_at_the_runs_own_end_changes_nothing(e3dir, target):
    """R1 on the path where the run ENDS ON ITS OWN, so no stop handler ran and only `cleanup`'s own ignore
    protects it. X2's fault (a PATH `ip` that SIGKILLs create's subshell at the veth add) leaves a namespace
    this runner owns; the run goes on to its end (a not-run row, units.json, the census, the checker), and
    `cleanup` then reaps that leftover; the same `ip` holds the reap's `netns del` for 2 s (timing only). A
    SIGTERM fired inside that hold changes nothing: the status is the run's own (the checker's `exit 1 per
    contract`) and nothing of the leftover remains. On the PIN the TERM's `exit 143` cut the reap short."""
    ns = "s0-05-hermes-acp"
    shim = e3dir / "shim"
    shim.mkdir()
    killed, held = e3dir / "killed-at-link-add", e3dir / "netns-del-held"
    (shim / "ip").write_text(
        "#!/bin/bash\n"
        f'if [ "$1 $2" = "link add" ]; then touch {killed}; kill -KILL "$PPID"; exit 1; fi\n'
        f'if [ "$1 $2 $3" = "netns del {ns}" ] && [ -e {killed} ]; then echo held >> {held}; sleep 2; fi\n'
        f'exec {IP_REAL} "$@"\n')
    (shim / "ip").chmod(0o755)
    env = _runner_env(e3dir, 18146, path_prefix=shim)
    evidence = e3dir / "evidence"
    runner = None
    try:
        runner = _runner_session(env, evidence, "hermes-acp")
        _wait_for(held.exists, 120, "cleanup to reap the leftover at the run's own end")
        assert runner.poll() is None, "the runner ended before the signal"
        _send(runner, "TERM", target)
        out, err = runner.communicate(timeout=120)
        assert _census(ns) == CLEAN, (_census(ns), runner.returncode, out, err)
        assert out.rstrip().endswith("exit 1 per contract"), out     # the run reached its own end first
        assert runner.returncode == 1, (runner.returncode, out, err)
        assert held.read_text() == "held\n"
    finally:
        _stop(runner)
        _lib(f'egress_ns_destroy {ns}')
    assert _census(ns) == CLEAN


def _s0_01_tree(e3dir, files, links=None, dirs=()):
    """<e3dir>/s0-01-pinned/.markers holding <dirs>, <files> ({relative path: bytes}, mode 0644) and <links>
    ({relative path: target}). Every entry is owned by the unit user: on the PC rocco owns S0-01's tree and
    is the default unit user, so the stand-in unit can write where a real unit could. Returns .markers."""
    markers = e3dir / "s0-01-pinned" / ".markers"
    markers.mkdir(parents=True)
    for rel in dirs:
        (markers / rel).mkdir()
    for rel, data in files.items():
        (markers / rel).write_bytes(data)
        (markers / rel).chmod(0o644)
    for rel, target in (links or {}).items():
        (markers / rel).symlink_to(target)
    os.lchown(markers, *UNIT_USER)
    for root, dirnames, filenames in os.walk(markers):
        for name in dirnames + filenames:
            os.lchown(os.path.join(root, name), *UNIT_USER)
    return markers


def _entries_under(markers):
    """The census's entry count, measured independently: .markers itself and everything below it, never
    descending through a symbolic link (os.walk's default)."""
    return 1 + sum(len(dirnames) + len(filenames) for _, dirnames, filenames in os.walk(markers))


def _changed_lines(stderr):
    prefix = "s0-01-tree-changed: "
    return [line[len(prefix):] for line in stderr.splitlines() if line.startswith(prefix)]


def _sha_of(data):
    return hashlib.sha256(data).hexdigest()


def _census_leg(e3dir, port, unit_code, serve=None):
    """ONE real runner leg for A2': the pinned base moved (the recorded override) to <e3dir>/s0-01-pinned;
    the hermes-acp stand-in runs <unit_code> as the unit user inside its namespace and then exits, so its
    row reads `launch exited within the settle window` while the census after the last unit still runs.
    <serve>(e3dir, port) starts the service on the leg's one allowed port (default: _listener).
    Returns the finished runner, the census file's content (None when absent) and its path."""
    env = _runner_env(e3dir, port, override={"PINNED_HERMES_HOME": str(e3dir / "s0-01-pinned" / ".hermes-home")},
                      extra=unit_code + "sys.exit(0)\n")
    evidence = e3dir / "evidence"
    listener = None
    try:
        listener = (serve or _listener)(e3dir, port)
        runner = _run_runner(env, evidence, "hermes-acp", timeout=240)
    finally:
        _stop(listener)
        _lib('egress_ns_destroy s0-05-hermes-acp')
    assert _census("s0-05-hermes-acp") == CLEAN
    reason = _unit_row(evidence, "hermes-acp")["reason"]
    assert reason.startswith("launch exited within the settle window"), (reason, runner.stderr)
    census_file = evidence / "s0-01-census.json"
    return runner, json.loads(census_file.read_text()) if census_file.exists() else None, census_file


# VERIFY-E3 F2's four writes (section 3), each blind to the PIN's directory-stat census.
UNIT_WRITES = """
M = @@M@@
with open(os.path.join(M, "buzz-acp.pid"), "r+") as fh:          # in place, the same size: only a digest sees it
    fh.write("9999\\n")
os.truncate(os.path.join(M, "current-framedir"), 0)
with open(os.path.join(M, "v2-run-1", "frames.jsonl"), "a") as fh:
    fh.write('{"frame": 2}\\n')
with open(os.path.join(M, "logs", "s0-05-new-file"), "w") as fh:  # one directory down, not a v2-* directory
    fh.write("S0-05 new file one directory down\\n")
"""


@NEEDS_NETNS
def test_e3r1_r2_each_in_place_write_fails_the_leg_by_name(e3dir):
    """R2 (A2'): VERIFY-E3 F2's four writes — an in-place rewrite of .markers/buzz-acp.pid (the SAME size, so
    only the sha256 sees it), a truncation of .markers/current-framedir, an append to a frames file, a new
    file one directory down (in `logs`, a directory the PIN never looked inside) — are each named
    (`s0-01-tree-changed: <path on disk>`), and the leg fails before the checker. The census file names them
    relative to .markers with their full before and after records; forty untouched entries are counted on
    both sides and never listed (the file never holds the whole entry list)."""
    markers = _s0_01_tree(e3dir, dirs=["v2-run-1", "logs"], files={
        "buzz-acp.pid": b"4242\n", "current-framedir": b"v2-run-1\n", "v2-run-1/frames.jsonl": b'{"frame": 1}\n',
        "logs/leg.log": b"S0-01 leg\n", **{f"v2-run-1/untouched-{n:02d}.jsonl": b"frame %d\n" % n for n in range(40)}})
    count = _entries_under(markers)
    runner, census, census_file = _census_leg(e3dir, 18140, UNIT_WRITES.replace("@@M@@", repr(str(markers))))
    named = {str(Path(p).relative_to(markers)) for p in _changed_lines(runner.stderr)}
    writes = {"buzz-acp.pid", "current-framedir", "v2-run-1/frames.jsonl", "logs/s0-05-new-file"}
    # `logs` may be named as well: a directory's size can count its entries (btrfs on the PC; ext4 here keeps 4096)
    assert writes <= named and named - writes <= {"logs"}, runner.stderr
    assert runner.returncode == 1 and "=== checker ===" not in runner.stdout, (runner.returncode, runner.stdout)
    assert f"=== S0-01's tree changed during the leg: the leg FAILS (census: {census_file}) ===" in runner.stderr
    assert census["changed"] == sorted(named) and sorted(census["changed_records"]) == census["changed"], census
    # A2'' added `appended` (none here: no file of this tree has a holder) and `writers`
    assert sorted(census) == ["after", "appended", "base", "before", "changed", "changed_records", "tree",
                              "writers"], census
    assert census["appended"] == {} and census["writers"] == {"before": {}, "after": {}}, census
    assert (census["before"]["entries"], census["after"]["entries"]) == (count, count + 1), census
    assert census["before"]["sha256"] != census["after"]["sha256"], census
    records = census["changed_records"]
    file_record = {"type": "file", "mode": "0644", "uid": UNIT_USER[0], "gid": UNIT_USER[1]}
    assert records["buzz-acp.pid"] == {"before": {**file_record, "size": 5, "sha256": _sha_of(b"4242\n")},
                                       "after": {**file_record, "size": 5, "sha256": _sha_of(b"9999\n")}}, records
    assert records["current-framedir"]["after"] == {**file_record, "size": 0, "sha256": _sha_of(b"")}, records
    assert records["v2-run-1/frames.jsonl"]["after"]["sha256"] == _sha_of(b'{"frame": 1}\n{"frame": 2}\n'), records
    new = records["logs/s0-05-new-file"]
    assert new["before"] is None and new["after"]["sha256"] == _sha_of(b"S0-05 new file one directory down\n"), new
    assert "untouched" not in census_file.read_text()                 # counted on both sides, never listed


UNIT_LINKS = """
M, OUT = @@M@@, @@OUT@@
os.remove(os.path.join(M, "link-retargeted"))
os.symlink("v2-run-1/frames.jsonl", os.path.join(M, "link-retargeted"))
with open(os.path.join(OUT, "target.txt"), "w") as fh:            # the bytes BEHIND a link are not the tree's
    fh.write("rewritten behind the link, and longer than before\\n")
with open(os.path.join(OUT, "dir", "new-file"), "w") as fh:        # nor is a directory behind a link
    fh.write("new behind the link\\n")
"""


@NEEDS_NETNS
def test_e3r1_r2_a_symbolic_link_is_recorded_by_its_target_never_followed(e3dir):
    """R2 (A2'): a symbolic link inside the tree is an entry recorded by its TARGET, never followed. The unit
    retargets one link (named, with its old and new target), rewrites the bytes of an outside file a second
    link points to, and adds a file inside an outside directory a third link points to: neither of those is
    named, and nothing behind a link is ever counted."""
    outside = e3dir / "outside"
    (outside / "dir").mkdir(parents=True)
    (outside / "target.txt").write_text("outside bytes\n")
    for path in (outside, outside / "dir", outside / "target.txt"):
        os.chown(path, *UNIT_USER)
    markers = _s0_01_tree(
        e3dir, dirs=["v2-run-1"], files={"buzz-acp.pid": b"4242\n", "v2-run-1/frames.jsonl": b"{}\n"},
        links={"link-retargeted": "buzz-acp.pid", "link-to-outside-file": str(outside / "target.txt"),
               "link-to-outside-dir": str(outside / "dir")})
    count = _entries_under(markers)
    runner, census, _ = _census_leg(e3dir, 18141, UNIT_LINKS.replace("@@M@@", repr(str(markers)))
                                    .replace("@@OUT@@", repr(str(outside))))
    assert (outside / "dir" / "new-file").exists() and "longer" in (outside / "target.txt").read_text()  # it ran
    named = [str(Path(p).relative_to(markers)) for p in _changed_lines(runner.stderr)]
    assert named == ["link-retargeted"], runner.stderr
    assert runner.returncode == 1 and "=== checker ===" not in runner.stdout, (runner.returncode, runner.stdout)
    link = {"type": "link", "mode": "0777", "uid": UNIT_USER[0], "gid": UNIT_USER[1]}
    assert census["changed_records"] == {"link-retargeted": {
        "before": {**link, "size": len("buzz-acp.pid"), "target": "buzz-acp.pid"},
        "after": {**link, "size": len("v2-run-1/frames.jsonl"), "target": "v2-run-1/frames.jsonl"}}}, census
    assert census["before"]["entries"] == census["after"]["entries"] == count, census


UNIT_NO_CHANGE = """
M = @@M@@
os.utime(os.path.join(M, "touched"), (1, 1))                       # new times: not compared
tmp = os.path.join(M, ".replaced.tmp")                              # the same bytes under a new inode: not compared
with open(tmp, "wb") as fh:
    fh.write(b"same bytes\\n")
os.chmod(tmp, 0o644)
os.replace(tmp, os.path.join(M, "replaced"))
"""


@NEEDS_NETNS
def test_e3r1_r2_an_unchanged_tree_passes(e3dir):
    """R2 (A2'): a tree whose compared attributes do not change passes the census, and the leg goes on to its
    checker. The unit does only what A2' does NOT compare: new times on one file, and a byte-identical
    replacement of another (a new inode; the same type, mode, owner and bytes). Both sides carry the same
    entry count and digest, and the census file names no entry. (The PIN compared times: it named .markers.)"""
    markers = _s0_01_tree(e3dir, dirs=["v2-run-1"], links={"link": "buzz-acp.pid"}, files={
        "buzz-acp.pid": b"4242\n", "touched": b"same bytes\n", "replaced": b"same bytes\n",
        "v2-run-1/frames.jsonl": b"{}\n"})
    count = _entries_under(markers)
    inode = os.lstat(markers / "replaced").st_ino
    runner, census, _ = _census_leg(e3dir, 18142, UNIT_NO_CHANGE.replace("@@M@@", repr(str(markers))))
    assert os.lstat(markers / "replaced").st_ino != inode and os.lstat(markers / "touched").st_mtime == 1  # it ran
    assert _changed_lines(runner.stderr) == [], runner.stderr
    assert "=== checker ===" in runner.stdout, runner.stdout            # the census let the leg go on
    assert census["changed"] == [] and census["changed_records"] == {} and census["tree"] == "present", census
    assert census["before"] == census["after"] and census["before"]["entries"] == count, census


@NEEDS_NETNS
def test_e3r1_r2_a_census_that_cannot_be_taken_fails_the_leg(e3dir):
    """R2, fail closed (this lane's addition to A2', flagged in its report): a census that cannot be taken
    certifies nothing. The pinned base is a regular FILE, so <base>/.markers cannot be read (ENOTDIR, which is
    not "absent"): the leg fails before the checker with the census failure named, and no census file is
    written. At the PIN a crashed census left `census_changed` empty and the run went on to its checker."""
    (e3dir / "s0-01-pinned").write_text("not a directory\n")
    runner, census, _ = _census_leg(e3dir, 18143, "")
    assert "=== S0-01's tree census failed (exit 1): the leg FAILS ===" in runner.stderr.splitlines(), runner.stderr
    assert runner.returncode == 1 and "=== checker ===" not in runner.stdout, (runner.returncode, runner.stdout)
    assert census is None


# A2'' (the first live pair leg, 2026-09-23 22:47Z): the pinned test relay, running since before the
# leg, holds .markers/relay.log open for write as its stdout (fdinfo flags 0100001: O_WRONLY, no
# O_APPEND) and appended to it while it served the pair, which failed the leg. These stand-ins take that
# shape: each opens its files ONCE at start and writes through the descriptor it holds.
RELAY_LOG_SERVER = """
import http.server, os, socketserver, sys
fd = os.open(sys.argv[3], os.O_WRONLY)
os.lseek(fd, 0, os.SEEK_END)
class H(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        os.write(fd, ("relay: %s %s\\n" % (self.client_address[0], self.path)).encode())
        self.send_response(200); self.end_headers(); self.wfile.write(b"{}")
    def log_message(self, *a): pass
socketserver.TCPServer.allow_reuse_address = True
socketserver.TCPServer((sys.argv[1], int(sys.argv[2])), H).serve_forever()
"""

# mode hold: hold each w:<path> for write and r:<path> for read from the start, append to the w: files on
# SIGUSR1. mode leave: the same, then exit. mode late: hold nothing until SIGUSR1, then open the w: files,
# append and keep holding them. mode stream: hold the w: files and append to them every half millisecond
# until killed. <ready> is created once the files are held.
HOLDER = """
import os, signal, sys, time
mode, ready, *specs = sys.argv[1:]
held = []
def hold():
    for spec in specs:
        how, path = spec.split(":", 1)
        fd = os.open(path, os.O_WRONLY | os.O_CREAT if how == "w" else os.O_RDONLY)
        os.lseek(fd, 0, os.SEEK_END)
        held.append((how, fd))
def on_signal(*_):
    if mode == "late":
        hold()
    for how, fd in held:
        if how == "w":
            os.write(fd, ("%s %d: appended\\n" % (mode, os.getpid())).encode())
    if mode == "leave":
        os._exit(0)
signal.signal(signal.SIGUSR1, on_signal)
if mode != "late":
    hold()
open(ready, "w").close()
while mode == "stream":
    for how, fd in held:
        os.write(fd, b"stream: one more line\\n")
    time.sleep(0.0005)
while True:
    signal.pause()
"""


def _proc_identity(pid):
    """[pid, start time, comm] from /proc, read independently of the runner: the census's holder key."""
    stat_line = Path(f"/proc/{pid}/stat").read_text()
    return [pid, int(stat_line[stat_line.rindex(")") + 2:].split()[19]), stat_line[stat_line.index("(") + 1:stat_line.rindex(")")]]


def _wait_ready(path, process, what):
    _wait_for(lambda: path.exists() or process.poll() is not None, 10, what)
    assert path.exists(), f"{what} exited with {process.poll()} before it was ready"


def _relay_log_server(workdir, port, log):
    """The relay's shape on the leg's allowed port, as the unit user (on the PC the relay and the units
    are both uid 1000). Returns the Popen; the caller kills it BY PID."""
    script = workdir / "relay_log_server.py"
    script.write_text(RELAY_LOG_SERVER)
    process = subprocess.Popen([_agent_interpreter(), str(script), "0.0.0.0", str(port), str(log)],
                               user=UNIT_USER[0], group=UNIT_USER[1], extra_groups=[],
                               stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    deadline = time.monotonic() + 5
    while time.monotonic() < deadline:
        if subprocess.run(["curl", "-fsS", "--noproxy", "*", "--max-time", "1", "-o", "/dev/null",
                           f"http://127.0.0.1:{port}/ready"], capture_output=True).returncode == 0:
            return process
        time.sleep(0.1)
    _stop(process)
    raise AssertionError(f"the relay-log server on port {port} did not become ready")


def _holder(workdir, mode, *specs, ns_over=None):
    """A HOLDER process (as the unit user, so the unit can signal it). With <ns_over> it runs as root in
    its OWN mount namespace with a tmpfs over <ns_over>: its descriptors then read as paths of the tree
    while naming other inodes."""
    script = workdir / "holder.py"
    script.write_text(HOLDER)
    ready = _rec_dir(workdir) / f"ready-{mode}-{uuid.uuid4().hex[:6]}"
    argv = [_agent_interpreter(), str(script), mode, str(ready), *specs]
    if ns_over is None:
        process = subprocess.Popen(argv, user=UNIT_USER[0], group=UNIT_USER[1], extra_groups=[],
                                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    else:
        process = subprocess.Popen(
            ["unshare", "--mount", "--propagation", "private", "sh", "-c",
             'mount -t tmpfs none "$0" && exec "$@"', str(ns_over), *argv],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    _wait_ready(ready, process, f"holder {mode}")
    return process


UNIT_RELAY = """
import socket
M, HOST, PORT = @@M@@, @@HOST@@, @@PORT@@
with socket.create_connection((HOST, PORT), timeout=5) as conn:
    conn.sendall(b"GET /unit-was-here HTTP/1.0\\r\\n\\r\\n")
    conn.recv(64)
with open(os.path.join(M, "relay.log"), "a") as fh:     # declared limit 8: the unit's own append
    fh.write("unit: appended itself\\n")
"""


@NEEDS_NETNS
def test_a2pp_a_log_its_holder_appends_during_the_leg_passes(e3dir):
    """A2'' (the relay's shape): relay.log, held open for write since before the leg by the service on
    the leg's allowed port, grows during the leg — the runner's own preflight request and the unit's
    request are both logged through the held descriptor — while every byte it held before stays. The
    census lists it under `appended` with both records and its holder, says so on stderr, names nothing,
    and the leg goes on to its checker. The unit's own append to the same file passes too: declared
    limit 8, pinned here so the prose cannot drift from the behaviour."""
    markers = _s0_01_tree(e3dir, dirs=["v2-run-1"], files={
        "relay.log": b"relay: listening\n", "buzz-acp.pid": b"4242\n", "v2-run-1/frames.jsonl": b"{}\n"})
    port, host = 18144, _lib("egress_ns_host_ip s0-05-hermes-acp").stdout.strip()
    relay = {}
    def serve(workdir, port):
        relay["process"] = _relay_log_server(workdir, port, markers / "relay.log")
        relay["identity"] = _proc_identity(relay["process"].pid)
        return relay["process"]
    unit = UNIT_RELAY.replace("@@M@@", repr(str(markers))).replace("@@HOST@@", repr(host)) \
        .replace("@@PORT@@", str(port))
    runner, census, census_file = _census_leg(e3dir, port, unit, serve=serve)
    data = (markers / "relay.log").read_bytes()        # the holder is stopped: these are the final bytes
    assert _changed_lines(runner.stderr) == [], runner.stderr
    assert "=== checker ===" in runner.stdout, runner.stdout            # the census let the leg go on
    pid, _, comm = relay["identity"]
    assert f"s0-01-tree-appended: {markers / 'relay.log'} (held for write by pid {pid} ({comm}); not a change)" \
        in runner.stderr.splitlines(), runner.stderr
    assert census["changed"] == [] and census["changed_records"] == {} and census["tree"] == "present", census
    assert census["before"]["sha256"] != census["after"]["sha256"], census   # the sides differ: A2'' decided
    assert census["writers"] == {"before": {"relay.log": [relay["identity"]]},
                                 "after": {"relay.log": [relay["identity"]]}}, census
    assert sorted(census["appended"]) == ["relay.log"], census
    was, now = census["appended"]["relay.log"]["before"], census["appended"]["relay.log"]["after"]
    file_record = {"type": "file", "mode": "0644", "uid": UNIT_USER[0], "gid": UNIT_USER[1]}
    assert now == {**file_record, "size": len(data), "sha256": _sha_of(data)}, (now, data)
    assert was["size"] < now["size"] and was == {**file_record, "size": was["size"],
                                                  "sha256": _sha_of(data[:was["size"]])}, (was, data)
    grown = data[was["size"]:].decode()
    assert f"relay: {_lib('egress_ns_ip s0-05-hermes-acp').stdout.strip()} /api/health\n" in grown, grown
    assert "/unit-was-here\n" in grown and "unit: appended itself\n" in grown, grown


UNIT_NOT_APPENDS = """
import signal, socket, time
M, HOST, PORT, HOLD, LEAVE, LATE = @@ARGS@@
def size(rel):
    return os.path.getsize(os.path.join(M, rel))
def grow(rels, act):
    was = [size(rel) for rel in rels]
    act()
    deadline = time.monotonic() + 20
    while any(size(rel) <= before for rel, before in zip(rels, was)):
        assert time.monotonic() < deadline, "no growth in %r" % (rels,)
        time.sleep(0.05)
def get():
    with socket.create_connection((HOST, PORT), timeout=5) as conn:
        conn.sendall(b"GET /unit-was-here HTTP/1.0\\r\\n\\r\\n")
        conn.recv(64)
grow(["relay.log"], get)                                                        # appended by its holder
grow(["chmod.log", "prefix.log", "late.log"], lambda: os.kill(HOLD, signal.SIGUSR1))
os.chmod(os.path.join(M, "chmod.log"), 0o600)                                   # then a new mode
with open(os.path.join(M, "prefix.log"), "r+b") as fh:                           # then a rewritten byte
    fh.write(b"X")
grow(["late.log"], lambda: os.kill(LATE, signal.SIGUSR1))                       # a holder added
grow(["exit.log"], lambda: os.kill(LEAVE, signal.SIGUSR1))                      # its holder then exits
for rel in ("v2-run-1/frames.jsonl", "watched.log", "ghost.log"):               # no holder for write
    with open(os.path.join(M, rel), "a") as fh:
        fh.write("unit: appended\\n")
"""


@NEEDS_NETNS
def test_a2pp_every_other_change_to_a_grown_file_still_fails_the_leg_by_name(e3dir):
    """A2'' fails closed: one file per condition, each grown with every earlier byte kept, so only that
    condition can name it — chmod.log (its holder appended, then a new mode), prefix.log (its holder
    appended, then byte 0 rewritten), late.log (a second holder opened it for write during the leg),
    exit.log (its holder appended and exited: no holder after), v2-run-1/frames.jsonl (no holder at
    all), watched.log (held for READ only), ghost.log (held for write by a process whose own mount
    namespace puts a tmpfs over .markers: the same path, another inode). Each is named and the leg
    fails before the checker, while relay.log, appended by its holder in the same leg, is still listed
    under `appended`: the allowance is per file."""
    body = {rel: f"{rel}: before\n".encode() for rel in (
        "relay.log", "chmod.log", "prefix.log", "late.log", "exit.log", "watched.log", "ghost.log")}
    markers = _s0_01_tree(e3dir, dirs=["v2-run-1"], files={**body, "v2-run-1/frames.jsonl": b"{}\n"})
    port, host = 18145, _lib("egress_ns_host_ip s0-05-hermes-acp").stdout.strip()
    at = {rel: markers / rel for rel in body}
    processes = []
    try:
        hold = _holder(e3dir, "hold", f"w:{at['chmod.log']}", f"w:{at['prefix.log']}", f"w:{at['late.log']}",
                       f"r:{at['watched.log']}")
        leave = _holder(e3dir, "leave", f"w:{at['exit.log']}")
        late = _holder(e3dir, "late", f"w:{at['late.log']}")
        processes += [hold, leave, late]
        processes.append(_holder(e3dir, "hold", f"w:{at['ghost.log']}", ns_over=markers))
        identity = {name: _proc_identity(p.pid) for name, p in (("hold", hold), ("leave", leave), ("late", late))}
        relay = {}
        def serve(workdir, port):
            relay["process"] = _relay_log_server(workdir, port, at["relay.log"])
            relay["identity"] = _proc_identity(relay["process"].pid)
            return relay["process"]
        args = repr((str(markers), host, port, hold.pid, leave.pid, late.pid))
        runner, census, census_file = _census_leg(e3dir, port, UNIT_NOT_APPENDS.replace("@@ARGS@@", args),
                                                  serve=serve)
    finally:
        for process in processes:
            _stop(process)
    launch_log = (e3dir / "evidence" / "hermes-acp.launch.log").read_text()
    assert (markers / "exit.log").read_text().endswith(f"leave {identity['leave'][0]}: appended\n"), launch_log
    for rel in ("v2-run-1/frames.jsonl", "watched.log", "ghost.log"):
        assert (markers / rel).read_text().endswith("unit: appended\n"), (rel, launch_log)   # the unit ran to its end
    named = sorted(str(Path(p).relative_to(markers)) for p in _changed_lines(runner.stderr))
    expected = ["chmod.log", "exit.log", "ghost.log", "late.log", "prefix.log", "v2-run-1/frames.jsonl",
                "watched.log"]
    assert named == expected, (runner.stderr, launch_log)
    assert runner.returncode == 1 and "=== checker ===" not in runner.stdout, (runner.returncode, runner.stdout)
    assert f"=== S0-01's tree changed during the leg: the leg FAILS (census: {census_file}) ===" in runner.stderr
    assert census["changed"] == expected and sorted(census["changed_records"]) == expected, census
    assert sorted(census["appended"]) == ["relay.log"], census
    # the holders as the census saw them: no read-only holder, no holder from another mount namespace
    assert census["writers"]["before"] == {
        "relay.log": [relay["identity"]], "chmod.log": [identity["hold"]], "prefix.log": [identity["hold"]],
        "late.log": [identity["hold"]], "exit.log": [identity["leave"]]}, census
    assert census["writers"]["after"] == {
        "relay.log": [relay["identity"]], "chmod.log": [identity["hold"]], "prefix.log": [identity["hold"]],
        "late.log": sorted([identity["hold"], identity["late"]])}, census
    records = census["changed_records"]
    assert (records["chmod.log"]["before"]["mode"], records["chmod.log"]["after"]["mode"]) == ("0644", "0600"), records
    assert records["prefix.log"]["after"]["size"] > records["prefix.log"]["before"]["size"], records
    assert (markers / "prefix.log").read_bytes().startswith(b"Xrefix.log: before\n"), records


@NEEDS_NETNS
def test_a2pp_a_file_that_grows_while_the_census_reads_it_gets_one_consistent_record(e3dir):
    """A2'': a file's size is the count of the bytes its digest covers. stream.log (32 MiB) is held open
    for write since before the leg by a holder that appends a line every half millisecond the whole time,
    so it grows WHILE each census reads it. Each record still describes one byte string: the leg goes on,
    stream.log is listed under `appended`, and its records match the file's final bytes. (A size taken
    from lstat before the read describes fewer bytes than the digest covers; the file would then be named,
    its earlier bytes "changed", and the leg failed on a pure append.)"""
    markers = _s0_01_tree(e3dir, files={"stream.log": b"s" * (32 << 20), "buzz-acp.pid": b"4242\n"})
    stream = _holder(e3dir, "stream", f"w:{markers / 'stream.log'}")
    try:
        runner, census, _ = _census_leg(e3dir, 18146, "")
    finally:
        _stop(stream)
    data = (markers / "stream.log").read_bytes()
    assert _changed_lines(runner.stderr) == [] and "=== checker ===" in runner.stdout, runner.stderr
    assert census["changed"] == [] and sorted(census["appended"]) == ["stream.log"], census
    was, now = census["appended"]["stream.log"]["before"], census["appended"]["stream.log"]["after"]
    assert (32 << 20) < was["size"] < now["size"] <= len(data), (was, now, len(data))
    assert was["sha256"] == _sha_of(data[:was["size"]]) and now["sha256"] == _sha_of(data[:now["size"]]), census
