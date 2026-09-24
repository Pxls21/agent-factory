"""J1-4 (task #121): the Laya pin in upstream.lock.yaml equals what J0 measured.

The lock row `advisory_models.laya-typed-decisions` must carry the checkpoint revision, the subfolder, the
weights digest and the laya package version that both probe JSONs (sandbox and PC) recorded, and the probe
report must name the same checkpoint source, revision and weights digest, each as a backticked value.
Negative controls: every pinned field, changed to a drifted or a malformed value, is red by name (the
breakdown's mutant m1 is the placeholder revision).
"""
import json
import pathlib
import re

import pytest
import yaml

ROOT = pathlib.Path(__file__).resolve().parents[1]
LOCK = ROOT / "upstream.lock.yaml"
FINDINGS = ROOT / "docs" / "research" / "findings"
PROBES = [FINDINGS / "laya-probe-1-sandbox.json", FINDINGS / "laya-probe-1-pc.json"]
REPORT = FINDINGS / "LAYA-PROBE-1.md"
ROW = ("advisory_models", "laya-typed-decisions")
HF = "https://huggingface.co/"
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
        if probe.get("checkpoint") != row.get("subfolder"):
            out.append(f"laya-pin-subfolder-drift: {venue} probe {probe.get('checkpoint')!r}")
        if weights and probe.get("safetensors_sha256") != weights.group(1):
            out.append(f"laya-pin-weights-drift: {venue} probe {probe.get('safetensors_sha256')!r}")
        if probe.get("versions", {}).get("laya") != str(row.get("package_version")):
            out.append(f"laya-pin-version-drift: {venue} probe {probe.get('versions', {}).get('laya')!r}")
    source = str(row.get("checkpoint_source", ""))
    repo = source[len(HF):] if source.startswith(HF) else ""
    if not repo or f"`{repo}`" not in report:
        out.append("laya-pin-report-drift: the probe report does not name the lock checkpoint source")
    if isinstance(revision, str) and f"`{revision}`" not in report:
        out.append("laya-pin-report-drift: the probe report does not name the lock revision")
    if weights and f"`{weights.group(1)}`" not in report:
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


BOTH = ("laya-probe-1-sandbox", "laya-probe-1-pc")


@pytest.mark.parametrize(
    ("field", "value", "expected"),
    [
        # m1: a placeholder revision, well-formed but measured nowhere.
        ("revision", "0" * 40, [f"laya-pin-revision-drift: {v} probe " for v in BOTH]
         + ["laya-pin-report-drift: the probe report does not name the lock revision"]),
        ("revision", "1c5edc17a7acd8701df6fc341c0d179f1c62c98g", ["laya-pin-revision-malformed: "]
         + [f"laya-pin-revision-drift: {v} probe " for v in BOTH]
         + ["laya-pin-report-drift: the probe report does not name the lock revision"]),
        ("subfolder", "typed-decision", [f"laya-pin-subfolder-drift: {v} probe " for v in BOTH]),
        ("weights_digest", "sha256:" + "0" * 64, [f"laya-pin-weights-drift: {v} probe " for v in BOTH]
         + ["laya-pin-report-drift: the probe report does not name the lock weights digest"]),
        ("weights_digest", "sha256:TODO", ["laya-pin-weights-digest-malformed: 'sha256:TODO'"]),
        ("package_wheel_digest", "sha256:TODO", ["laya-pin-wheel-digest-malformed: 'sha256:TODO'"]),
        ("package_version", "0.3.4", [f"laya-pin-version-drift: {v} probe " for v in BOTH]),
        ("checkpoint_source", HF + "convaiinnovations/lay",
         ["laya-pin-report-drift: the probe report does not name the lock checkpoint source"]),
    ],
    ids=["m1-placeholder-revision", "malformed-revision", "subfolder", "weights-drift", "weights-malformed",
         "wheel-malformed", "version", "truncated-source"],
)
def test_each_pinned_field_is_red_by_name(field, value, expected):
    lock = yaml.safe_load(LOCK.read_text(encoding="utf-8"))
    lock[ROW[0]][ROW[1]][field] = value
    found = pin_mismatches(lock, _probes(), REPORT.read_text(encoding="utf-8"))
    assert len(found) == len(expected), found
    for prefix in expected:
        assert sum(item.startswith(prefix) for item in found) == 1, (prefix, found)


def test_missing_row_is_red_by_name():
    assert pin_mismatches({}, _probes(), REPORT.read_text(encoding="utf-8")) == [
        "laya-pin-missing: no advisory_models.laya-typed-decisions row"
    ]
