#!/usr/bin/env python3
"""S0-05: no-direct-model-egress conformance checker.

Reads the evidence bundles that `run_canaries.sh` writes for each contained unit and decides,
deterministically and without any LLM, whether the seed's two assertions hold
(`seeds/seed-stage0-v1.yaml:423-441`):

  * mechanism — a veth/iptables namespace lets the unit reach the OmniRoute endpoint while a
    model endpoint fails with the exact denial reason;
  * full proof — every non-OmniRoute unit's canaries FAIL, and each unit first proves its
    positive control (it CAN reach its allowed target).

Order is part of the contract, and it runs in this order for a reason:

  1. GATE STATE, for every unit, before a single canary is read. The seed's negative control is
     "switch the egress gate off -> the suite goes RED with `egress-permitted: gate-disabled`";
     if that check came after the canaries, a bundle collected with the gate flushed could pass
     by luck whenever nothing happened to be reachable. Exit 1, reason `egress-permitted:
     gate-disabled`.
  2. POSITIVE CONTROL (C0). A unit that could not reach its allowed target proves nothing about
     containment — that is what bare `unshare --net` looks like (AF-AP-1,
     row AF-AP-1 in docs/INCIDENT-LOG.md). Exit 1, `positive-control-failed: <unit>`.
  3. DENIAL CANARIES (C1 DNS, C2 TCP, C3 TLS, C5 UDP/53, C6 routable-but-not-allow-listed).
     Each must have failed with an rc in {6, 7, 28}, a diagnostic drawn from this mechanism's
     own vocabulary, AND — where the diagnostic names an endpoint — that endpoint must be the
     canary's own target. Both halves are load-bearing: in this sandbox an ambient
     `HTTPS_PROXY=http://127.0.0.1:40173` makes curl fail with rc 7 and the same generic
     `Couldn't connect to server` text a real gate denial produces, and only the address it
     names separates the two. Any success is `egress-permitted: <unit> <canary> <target>`.
  4. C4 (a non-model internet target) is RECORDED, never asserted:
     docs/02_COMPONENT_AUDIT.md:56 — "OmniRoute is sole model API egress, not automatically sole
     web/tool egress". The checker prints what happened so the report can state it.
  5. THE GATE ACTUALLY FIRED: the namespace's OUTPUT policy DROP counter advanced during the
     run. A suite whose canaries all failed for reasons other than the gate leaves it at zero.
  6. THE RULES ARE PINNED: the recorded rule list hashes to the digest in gate.json, and that
     digest equals the digest of the rule set this checker derives from the declared allow-list.
     The mechanism cannot be silently widened and still pass.
  7. UNIT SET: at least one run unit, and every unit in `--units` present. Units declared absent
     in `units.json` are NOT counted and can never pass — `NOT run: unit does not exist` is a
     recorded gap, not a green.

Deferral (exit 2), never a pass: the evidence root does not exist (the live units run on the
PC), or a canary is recorded `status: not-run` — a discriminator that could not run is a DEFER
(row AF-AP-24 in docs/INCIDENT-LOG.md).

Usage:
  check_egress.py <evidence-root> [--units curl,hermes-acp]

Exit 0 + PASS; 1 + reason; 2 + `deferred: ...`.
"""
import argparse
import hashlib
import json
import re
import stat
import sys
from pathlib import Path

REQUIRED_DENIALS = ("C1", "C2", "C3", "C5", "C6")
RECORDED = ("C4",)
POSITIVE = "C0"
DENIAL_RCS = (6, 7, 28)

# The denial vocabulary of THIS mechanism, keyed by the exit code that must accompany it. An
# allow-list, never a blacklist (AF-AP-47): a diagnostic from any other mechanism is rejected.
DENIAL_DETAILS = {
    6: ("Could not resolve host", "Could not resolve", "Name or service not known",
        "Temporary failure in name resolution"),
    # curl 8.5 renders EVERY connect errno as the generic "Couldn't connect to server", so the
    # fragment alone cannot say WHICH endpoint refused. That is why every curl-shaped detail is
    # additionally bound to the canary's own target below.
    7: ("Network is unreachable", "Host is unreachable", "No route to host",
        "Connection refused", "Operation not permitted", "Network is down",
        "Couldn't connect to server"),
    28: ("Timeout was reached", "timed out", "Connection timed out"),
}

GATE_KEYS = ("gate", "mechanism", "netns", "unit", "allowed", "rules_sha256")
RUNTIME_KEYS = ("venue", "unit", "kernel", "iptables_version", "rules",
                "drop_counter_before", "drop_counter_after")
RECORD_KEYS = ("canary", "unit", "target", "kind", "rc", "status", "detail")
IPV4_PORT = re.compile(r"^(\d{1,3})\.(\d{1,3})\.(\d{1,3})\.(\d{1,3}):(\d{1,5})$")
# The two places a curl diagnostic names the endpoint it failed on.
CURL_CONNECT = re.compile(r"Failed to connect to (\S+) port (\d+)")
CURL_RESOLVE = re.compile(r"Could not resolve host: (\S+?)\.?$")


class Failure(Exception):
    """A real S0-05 violation: exit 1 with this reason."""


class Deferred(Exception):
    """The venue could not produce this evidence: exit 2, never a pass."""


def _is_int(value):
    """True iff value is an int and NOT a bool (AF-AP-26: isinstance(True, int) is True)."""
    return isinstance(value, int) and not isinstance(value, bool)


def _foreign_endpoint_in_detail(record):
    """A denial only counts when the diagnostic names the canary's OWN target. THE discriminator
    against a denial produced by something else: with this sandbox's ambient
    HTTPS_PROXY=http://127.0.0.1:40173, curl inside the namespace reports
    `Failed to connect to 127.0.0.1 port 40173 ... Couldn't connect to server` — the same rc and
    the same generic fragment as a real gate denial, distinguishable only by the address. A
    detail that names no endpoint (the python probes print an errno) passes this check."""
    host = record["target"].rsplit(":", 1)[0]
    names = {host, record["target"]}
    # The record's own `ip` is an accepted alias ONLY when it is a real remote address. Without
    # this floor a forged record carrying `"ip": "127.0.0.1"` would whitelist exactly the
    # proxy-shaped denial this rule exists to catch (found by the 18-class sweep, class 18).
    candidate = record.get("ip")
    if isinstance(candidate, str) and not candidate.startswith("127."):
        names.add(candidate)
    for pattern in (CURL_CONNECT, CURL_RESOLVE):
        match = pattern.search(record["detail"])
        if match and match.group(1) not in names:
            return match.group(1)
    return None


def _require_regular(path, name):
    """Reject a missing or non-regular file (FIFO, directory, socket, device) BEFORE any read —
    existence alone is not enough, and a FIFO would hang the checker."""
    if not path.exists():
        raise Failure(f"evidence-missing: {name} absent at {path}")
    if not stat.S_ISREG(path.lstat().st_mode):
        raise Failure(f"evidence-missing: {name} is not a regular file")
    return path


def _load_json(path, name):
    _require_regular(path, name)

    def _reject(constant):
        raise Failure(f"evidence-invalid: {name} contains {constant}")

    try:
        return json.loads(path.read_text(), parse_constant=_reject)
    except Failure:
        raise
    except Exception as error:
        raise Failure(f"evidence-invalid: {name} {error}") from error


def _split_ip_port(entry):
    match = IPV4_PORT.match(entry or "")
    if not match:
        raise Failure(f"gate-manifest-invalid: allow entry {entry!r} is not <ipv4>:<port>")
    *octets, port = match.groups()
    if any(int(o) > 255 for o in octets) or not 1 <= int(port) <= 65535:
        raise Failure(f"gate-manifest-invalid: allow entry {entry!r} is out of range")
    return ".".join(octets), port


def expected_rules(allowed):
    """The rule set this mechanism is pinned to, derived from the declared allow-list alone.
    Sorted: every rule is an ACCEPT under a DROP policy, so order carries no semantics, but
    membership does — adding, widening or dropping any rule changes the digest."""
    lines = ["-P INPUT DROP", "-P FORWARD DROP", "-P OUTPUT DROP",
             "-A INPUT -i lo -j ACCEPT", "-A OUTPUT -o lo -j ACCEPT"]
    for entry in allowed:
        ip, port = _split_ip_port(entry)
        lines.append(f"-A INPUT -s {ip}/32 -p tcp -m tcp --sport {port} -j ACCEPT")
        lines.append(f"-A OUTPUT -d {ip}/32 -p tcp -m tcp --dport {port} -j ACCEPT")
    return sorted(lines)


def rules_digest(lines):
    return hashlib.sha256(("\n".join(lines) + "\n").encode()).hexdigest()


def read_gate(unit_dir, unit):
    gate = _load_json(unit_dir / "gate.json", f"{unit} gate.json")
    if not isinstance(gate, dict):
        raise Failure(f"evidence-invalid: {unit} gate.json is not an object")
    for key in GATE_KEYS:
        if key not in gate:
            raise Failure(f"gate-manifest-invalid: {unit} gate.json lacks {key}")
    if not isinstance(gate["allowed"], list) or not gate["allowed"]:
        raise Failure(f"gate-manifest-invalid: {unit} allowed must be a non-empty list")
    if gate["gate"] not in ("enabled", "disabled"):
        raise Failure(f"gate-manifest-invalid: {unit} gate={gate['gate']!r}")
    return gate


def read_records(unit_dir, unit):
    path = _require_regular(unit_dir / "canaries.jsonl", f"{unit} canaries.jsonl")
    records = {}
    for number, line in enumerate(path.read_text().splitlines(), start=1):
        if not line.strip():
            continue

        def _reject(constant, _n=number):
            raise Failure(f"evidence-invalid: {unit} canaries.jsonl line {_n} contains {constant}")

        try:
            record = json.loads(line, parse_constant=_reject)
        except Failure:
            raise
        except Exception as error:
            raise Failure(f"evidence-invalid: {unit} canaries.jsonl line {number} {error}") from error
        if not isinstance(record, dict) or any(key not in record for key in RECORD_KEYS):
            raise Failure(f"evidence-invalid: {unit} canaries.jsonl line {number} is not a canary record")
        if record["status"] not in ("run", "not-run"):
            raise Failure(f"evidence-invalid: {unit} canary {record['canary']} status={record['status']!r}")
        if record["unit"] != unit:
            raise Failure(f"evidence-invalid: {unit} canaries.jsonl line {number} names unit {record['unit']!r}")
        records.setdefault(record["canary"], []).append(record)
    return records


def check_positive_control(records, unit):
    """Returns 1 for a unit whose positive control is proven. The PASS line's
    `positive controls N/M` is then units-proven over units-checked — two distinct populations,
    not one count printed twice."""
    entries = records.get(POSITIVE, [])
    if not entries:
        raise Failure(f"positive-control-failed: {unit}")
    for record in entries:
        status = record.get("http_status")
        if (record["status"] != "run" or record["rc"] != 0 or not _is_int(status)
                or not 200 <= status < 300):
            raise Failure(f"positive-control-failed: {unit}")
    return 1


def check_denials(records, unit):
    failed = 0
    for canary in REQUIRED_DENIALS:
        entries = records.get(canary, [])
        if not entries:
            raise Failure(f"canary-missing: {unit} {canary}")
        for record in entries:
            if record["status"] == "not-run":
                raise Deferred(f"deferred: {unit} {canary} not-run: {record['detail']}")
            rc = record["rc"]
            if rc == 0:
                raise Failure(f"egress-permitted: {unit} {canary} {record['target']}")
            if not _is_int(rc) or rc not in DENIAL_RCS:
                raise Failure(f"denial-rc-unrecognized: {unit} {canary} rc={rc}")
            allowed_details = DENIAL_DETAILS[rc]
            if not any(fragment in record["detail"] for fragment in allowed_details):
                raise Failure(f"denial-detail-unrecognized: {unit} {canary} {record['detail']}")
            foreign = _foreign_endpoint_in_detail(record)
            if foreign:
                raise Failure(f"denial-detail-foreign-target: {unit} {canary} denial names "
                              f"{foreign}, not {record['target']}")
            failed += 1
    return failed


def check_recorded(records, unit):
    lines = []
    for canary in RECORDED:
        entries = records.get(canary, [])
        if not entries:
            raise Failure(f"canary-missing: {unit} {canary}")
        for record in entries:
            outcome = "reachable" if record["rc"] == 0 else f"denied rc={record['rc']}"
            lines.append(f"recorded: {unit} {canary} {record['target']} {outcome} — {record['detail']}")
    return lines


def check_runtime_and_rules(unit_dir, unit, gate):
    runtime = _load_json(unit_dir / "runtime.json", f"{unit} runtime.json")
    if not isinstance(runtime, dict):
        raise Failure(f"evidence-invalid: {unit} runtime.json is not an object")
    for key in RUNTIME_KEYS:
        if key not in runtime:
            raise Failure(f"runtime-manifest-invalid: {unit} runtime.json lacks {key}")
    before, after = runtime["drop_counter_before"], runtime["drop_counter_after"]
    if not (_is_int(before) and _is_int(after)) or before < 0 or after < 0:
        raise Failure(f"runtime-manifest-invalid: {unit} drop counters must be non-negative integers")
    if after <= before:
        raise Failure(f"gate-inert: {unit} OUTPUT DROP counter did not advance ({before} -> {after})")
    rules = runtime["rules"]
    if not isinstance(rules, list) or not all(isinstance(line, str) for line in rules):
        raise Failure(f"runtime-manifest-invalid: {unit} rules must be a list of strings")
    if rules_digest(rules) != gate["rules_sha256"]:
        raise Failure(f"egress-rules-unpinned: {unit} recorded rules do not hash to the gate digest")
    if rules_digest(expected_rules(gate["allowed"])) != gate["rules_sha256"]:
        raise Failure(f"egress-rules-unpinned: {unit} rules are not the pinned allow-list for {gate['allowed']}")
    return f"gate-fired: {unit} OUTPUT policy DROP {before} -> {after} packets"


def read_units_manifest(root):
    """units.json declares the unit set, including units that DO NOT EXIST yet. A declared-absent
    unit is never counted as passed — the gap is recorded, not greened."""
    path = root / "units.json"
    if not path.exists():
        return {}, []
    manifest = _load_json(path, "units.json")
    if not isinstance(manifest, dict) or not isinstance(manifest.get("units"), list):
        raise Failure("units-manifest-invalid: units.json must be {\"units\": [...]}")
    declared, absent = {}, []
    for entry in manifest["units"]:
        if not isinstance(entry, dict) or "unit" not in entry or "status" not in entry:
            raise Failure("units-manifest-invalid: each entry needs unit and status")
        if entry["status"] not in ("run", "not-run"):
            raise Failure(f"units-manifest-invalid: {entry['unit']} status={entry['status']!r}")
        if entry["status"] == "not-run" and not entry.get("reason"):
            raise Failure(f"units-manifest-invalid: {entry['unit']} declared not-run without a reason")
        declared[entry["unit"]] = entry["status"]
        if entry["status"] == "not-run":
            absent.append(f"NOT run: {entry['unit']} — {entry['reason']}")
    return declared, absent


def check(root, required_units):
    if not root.is_dir():
        raise Deferred(f"deferred: evidence-root-absent: {root}")
    declared, absent_lines = read_units_manifest(root)
    present = sorted(child.name for child in root.iterdir() if child.is_dir())
    for unit, status in sorted(declared.items()):
        if status == "not-run" and unit in present:
            raise Failure(f"unit-declared-absent-but-present: {unit}")
        if status == "run" and unit not in present:
            raise Failure(f"unit-missing: {unit}")
    units = [unit for unit in present if declared.get(unit, "run") == "run"]

    # PHASE 1 — the gate state of EVERY unit, before a single canary is read.
    gates = {}
    for unit in units:
        gates[unit] = read_gate(root / unit, unit)
        if gates[unit]["gate"] != "enabled":
            raise Failure("egress-permitted: gate-disabled")

    # PHASE 2 — the evidence itself.
    lines, denied, positives = list(absent_lines), 0, 0
    for unit in units:
        records = read_records(root / unit, unit)
        positives += check_positive_control(records, unit)
        denied += check_denials(records, unit)
        lines.extend(check_recorded(records, unit))
        lines.append(check_runtime_and_rules(root / unit, unit, gates[unit]))

    if not units:
        raise Failure(f"no-units: no run unit in {root}")
    for unit in required_units:
        if unit not in units:
            raise Failure(f"unit-missing: {unit}")
    lines.append(f"PASS: S0-05 no-direct-egress - {len(units)} units, {denied} canaries failed "
                 f"as required, positive controls {positives}/{len(units)}")
    return lines


def main(argv):
    parser = argparse.ArgumentParser(description="S0-05 no-direct-model-egress checker")
    parser.add_argument("evidence_root")
    parser.add_argument("--units", default="curl",
                        help="comma-separated units that MUST be present (default: curl)")
    args = parser.parse_args(argv)
    required = [unit for unit in args.units.split(",") if unit]
    try:
        for line in check(Path(args.evidence_root), required):
            print(line)
    except Deferred as deferred:
        print(deferred)
        return 2
    except Failure as failure:
        print(failure)
        print("exit 1 per contract")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
