"""J1-4 (task #121): the Laya pin in upstream.lock.yaml equals what J0 measured.

The lock row `advisory_models.laya-typed-decisions` must carry the checkpoint revision, the weights digest
and the laya package version that both probe JSONs (sandbox and PC) recorded, and the probe report must
name the same revision and digest. Negative control: a lock copy with a placeholder revision (the
breakdown's mutant m1) is red by name.
"""
import json
import pathlib
import re

import yaml

ROOT = pathlib.Path(__file__).resolve().parents[1]
LOCK = ROOT / "upstream.lock.yaml"
FINDINGS = ROOT / "docs" / "research" / "findings"
PROBES = [FINDINGS / "laya-probe-1-sandbox.json", FINDINGS / "laya-probe-1-pc.json"]
REPORT = FINDINGS / "LAYA-PROBE-1.md"
ROW = ("advisory_models", "laya-typed-decisions")
HEX40 = re.compile(r"[0-9a-f]{40}")
DIGEST = re.compile(r"sha256:([0-9a-f]{64})")


def pin_mismatches(lock: dict, probes: list[dict], report: str) -> list[str]:
    """Every way the lock row disagrees with the probe evidence; [] when they agree."""
    row = lock.get(ROW[0], {}).get(ROW[1])
    if not isinstance(row, dict):
        return ["laya-pin-missing: no advisory_models.laya-typed-decisions row"]
    out = []
    revision = row.get("revision")
    if not isinstance(revision, str) or not HEX40.fullmatch(revision):
        out.append(f"laya-pin-revision-malformed: {revision!r}")
    weights = DIGEST.fullmatch(str(row.get("weights_digest", "")))
    wheel = DIGEST.fullmatch(str(row.get("package_wheel_digest", "")))
    if not weights:
        out.append(f"laya-pin-weights-digest-malformed: {row.get('weights_digest')!r}")
    if not wheel:
        out.append(f"laya-pin-wheel-digest-malformed: {row.get('package_wheel_digest')!r}")
    for probe in probes:
        venue = probe.get("_venue", "?")
        if probe.get("revision") != revision:
            out.append(f"laya-pin-revision-drift: {venue} probe {probe.get('revision')!r} != lock {revision!r}")
        if weights and probe.get("safetensors_sha256") != weights.group(1):
            out.append(f"laya-pin-weights-drift: {venue} probe {probe.get('safetensors_sha256')!r}")
        if probe.get("versions", {}).get("laya") != str(row.get("package_version")):
            out.append(f"laya-pin-version-drift: {venue} probe {probe.get('versions', {}).get('laya')!r}")
    if isinstance(revision, str) and revision not in report:
        out.append("laya-pin-report-drift: the probe report does not name the lock revision")
    if weights and weights.group(1) not in report:
        out.append("laya-pin-report-drift: the probe report does not name the lock weights digest")
    return out


def _probes() -> list[dict]:
    loaded = []
    for path in PROBES:
        probe = json.loads(path.read_text(encoding="utf-8"))
        probe["_venue"] = path.stem
        loaded.append(probe)
    return loaded


def test_lock_pin_equals_both_probes_and_the_report():
    lock = yaml.safe_load(LOCK.read_text(encoding="utf-8"))
    assert pin_mismatches(lock, _probes(), REPORT.read_text(encoding="utf-8")) == []


def test_placeholder_revision_is_red_by_name():
    lock = yaml.safe_load(LOCK.read_text(encoding="utf-8"))
    lock[ROW[0]][ROW[1]]["revision"] = "0" * 40
    found = pin_mismatches(lock, _probes(), REPORT.read_text(encoding="utf-8"))
    assert "laya-pin-revision-drift: laya-probe-1-pc probe " in "\n".join(found)
    assert any(item.startswith("laya-pin-report-drift: the probe report does not name the lock revision") for item in found)


def test_missing_row_and_malformed_digest_are_red_by_name():
    report = REPORT.read_text(encoding="utf-8")
    assert pin_mismatches({}, _probes(), report) == ["laya-pin-missing: no advisory_models.laya-typed-decisions row"]
    lock = yaml.safe_load(LOCK.read_text(encoding="utf-8"))
    lock[ROW[0]][ROW[1]]["weights_digest"] = "sha256:TODO"
    assert "laya-pin-weights-digest-malformed: 'sha256:TODO'" in pin_mismatches(lock, _probes(), report)
