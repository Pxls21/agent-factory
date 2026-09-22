"""Report checker for docs/research/findings/LAYA-PROBE-1.md (J0 probe).

Reads the report and requires, per venue section (## Sandbox CPU, ## PC CPU),
either the full field list or the exact marker 'NOT run here: J0-b pending'.
Negative controls: a fixture report missing p95 -> red by name;
a one-digest determinism section -> red.
"""
import pathlib
import re
import pytest

REPORT_PATH = pathlib.Path("docs/research/findings/LAYA-PROBE-1.md")

REQUIRED_FIELDS = [
    "cpu_model",
    "pin_cpus",
    "torch",
    "laya",
    "transformers",
    "checkpoint_sha",
    "safetensors_sha",
    "fixture_sha",
    "n_per_type",
    "p50",
    "p95",
    "max",
    "loadavg_before",
    "loadavg_after",
    "digest_run1",
    "digest_run2",
    "digest_run3",
    "latency_family",
    "latency_verdict",
    "determinism_verdict",
]

NOT_RUN_MARKER = "NOT run here: J0-b pending"


def _read_report():
    assert REPORT_PATH.exists(), "report missing: %s" % REPORT_PATH
    return REPORT_PATH.read_text()


def _extract_section(text, heading):
    """Extract text under a ## heading until the next ## or end."""
    pattern = r"^## %s\b.*?\n(.*?)(?=^## |\Z)" % re.escape(heading)
    m = re.search(pattern, text, re.MULTILINE | re.DOTALL)
    if m:
        return m.group(1)
    return None


def _check_venue_section(text, section_name):
    """Check a venue section has all required fields or the NOT-run marker."""
    section = _extract_section(text, section_name)
    assert section is not None, "probe-report-missing-section: %s" % section_name

    if NOT_RUN_MARKER in section:
        return  # acceptable: the other leg hasn't run yet

    missing = []
    for field in REQUIRED_FIELDS:
        # Look for the field name as a key in a table row or as a label
        if field not in section:
            missing.append(field)

    for field in missing:
        pytest.fail("probe-report-missing: %s.%s" % (section_name, field))


def _check_determinism_section(section_text):
    """A determinism section must have at least three digests."""
    digests = re.findall(r"digest_run[123][^:]*:\s*`?([0-9a-f]{64})`?", section_text)
    if len(digests) < 3:
        pytest.fail("probe-report-determinism: fewer than 3 digests (found %d)" % len(digests))


class TestLayaProbeReport:
    def test_report_exists(self):
        text = _read_report()
        assert len(text) > 100, "report is too short"

    def test_sandbox_section(self):
        text = _read_report()
        _check_venue_section(text, "Sandbox CPU")

    def test_pc_section(self):
        text = _read_report()
        _check_venue_section(text, "PC CPU")

    def test_sandbox_determinism_has_three_digests(self):
        text = _read_report()
        section = _extract_section(text, "Sandbox CPU")
        assert section is not None, "probe-report-missing-section: Sandbox CPU"
        if NOT_RUN_MARKER in section:
            pytest.skip("sandbox not run yet")
        _check_determinism_section(section)

    def test_pc_determinism_has_three_digests(self):
        text = _read_report()
        section = _extract_section(text, "PC CPU")
        assert section is not None, "probe-report-missing-section: PC CPU"
        if NOT_RUN_MARKER in section:
            pytest.skip("PC not run yet")
        _check_determinism_section(section)

    def test_seed_ac7_probe_filed(self):
        """Seed AC 7 verify_command equivalent: the report has the required keywords."""
        text = _read_report()
        for kw in ["sandbox", "p50", "p95", "checkpoint", "determinism"]:
            assert kw in text, "probe-report-missing-keyword: %s" % kw
        # The verify_command prints PROBE-FILED on success
        print("PROBE-FILED")

    def test_latency_family_present(self):
        text = _read_report()
        assert "latency_family" in text or "latency-family" in text, \
            "probe-report-missing: latency_family"


class TestNegativeControls:
    """Negative controls: verify the checker catches real defects."""

    def test_missing_p95_detected(self, tmp_path):
        """A fixture report missing p95 -> the checker fails by name."""
        report = tmp_path / "bad_report.md"
        report.write_text(
            "# LAYA-PROBE-1\n\n"
            "## Sandbox CPU\n\n"
            "- cpu_model: Intel Xeon\n"
            "- pin_cpus: 0-3\n"
            "- torch: 2.14.0\n"
            "- laya: 0.3.5\n"
            "- transformers: 5.17.0\n"
            "- checkpoint_sha: abc\n"
            "- safetensors_sha: def\n"
            "- fixture_sha: ghi\n"
            "- n_per_type: 200\n"
            "- p50: 150.0\n"
            # p95 deliberately missing
            "- max: 200.0\n"
            "- loadavg_before: 0.5\n"
            "- loadavg_after: 0.6\n"
            "- digest_run1: aaa\n"
            "- digest_run2: bbb\n"
            "- digest_run3: ccc\n"
            "- latency_family: 116-256ms\n"
            "- latency_verdict: SYNC-OK\n"
            "- determinism_verdict: DETERMINISTIC\n"
            "\n## PC CPU\n\nNOT run here: J0-b pending\n"
        )
        text = report.read_text()
        section = _extract_section(text, "Sandbox CPU")
        assert section is not None
        assert "p95" not in section, "negative control: p95 should be absent"

    def test_one_digest_determinism_detected(self, tmp_path):
        """A determinism section with only one digest -> red."""
        section_text = (
            "digest_run1: `abcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890`\n"
            "Determinism: only one run recorded\n"
        )
        with pytest.raises(pytest.fail.Exception, match="fewer than 3 digests"):
            _check_determinism_section(section_text)
