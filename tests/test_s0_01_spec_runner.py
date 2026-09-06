"""S0-01 through the CANONICAL proof-runner: with the committed evidence still v1
(no timeline.jsonl), the runner's positive leg must DEFER (exit 2, no result.json).
The negative leg also defers today (the negative/ directory does not exist yet).

V3: this test invokes scripts/proof-runner run --proof <id> --venue sandbox --root <root>
for real (not just the leg cmd directly). The runner matches failure_reason with:
    next((line for line in (stdout + "\\n" + stderr).splitlines() if expected_reason in line), None)
This is a per-line substring match. check_initialize's two-line output
(classification on line 1, observed on line 2) is compatible because the expected
failure_reason "protocol-violation: missing required initialize field" is the
exact text of line 1.
"""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RUNNER = ROOT / "scripts" / "proof-runner"


def _copy(tmp_path):
    root = tmp_path / "repo"
    shutil.copytree(ROOT / "proofs", root / "proofs")
    # The runner also needs scripts/ for the validator
    shutil.copytree(ROOT / "scripts", root / "scripts")
    return root


def test_positive_leg_defers_on_v1_evidence(tmp_path):
    """The positive leg defers (exit 2) because the committed evidence is v1
    (no timeline.jsonl). The runner must NOT create a result.json."""
    root = _copy(tmp_path)
    spec = json.loads((root / "proofs" / "S0-01" / "spec.json").read_text())
    pos = next(leg for leg in spec["legs"] if leg["leg"] == "positive")
    r = subprocess.run(
        [sys.executable, *pos["cmd"][1:]],
        cwd=root, capture_output=True, text=True, timeout=120,
    )
    assert r.returncode == 2, f"expected exit 2 (deferred), got {r.returncode}: {r.stdout}"
    assert r.stdout.strip() == "deferred: v2 evidence not captured"
    assert not (root / "proofs" / "S0-01" / "result.json").exists()


def test_runner_defers_s0_01_via_real_runner(tmp_path):
    """V3(a): invoke proof-runner run --proof S0-01 --venue sandbox --root <root>
    for real → exact deferral stderr and exit 2. The positive leg defers first."""
    root = _copy(tmp_path)
    r = subprocess.run(
        [sys.executable, str(RUNNER), "run", "--proof", "S0-01",
         "--venue", "sandbox", "--root", str(root)],
        capture_output=True, text=True, timeout=120,
    )
    assert r.returncode == 2, (
        f"expected exit 2 (deferred), got {r.returncode}: "
        f"stdout={r.stdout!r} stderr={r.stderr!r}"
    )
    assert r.stderr.strip() == (
        "deferred: S0-01 positive capability-unavailable (exit 2); "
        "artifact preserved — run on a capable venue"
    )
    assert not (root / "proofs" / "S0-01" / "result.json").exists()


def test_negative_leg_defers_directly(tmp_path):
    """The negative leg cmd defers today (directory absent) with the exact text."""
    root = _copy(tmp_path)
    spec = json.loads((root / "proofs" / "S0-01" / "spec.json").read_text())
    neg = next(leg for leg in spec["legs"] if leg["leg"] == "negative")
    r = subprocess.run(
        [sys.executable, *neg["cmd"][1:]],
        cwd=root, capture_output=True, text=True, timeout=60,
    )
    assert r.returncode == 2, f"expected exit 2 (deferred), got {r.returncode}: {r.stdout}"
    assert r.stdout.strip() == "deferred: negative probe not captured"


def test_spec_structure_matches_brief(tmp_path):
    """The spec's negative leg now points at the golden/negative directory,
    and the positive leg still runs check_acp_conformance.py."""
    root = _copy(tmp_path)
    spec = json.loads((root / "proofs" / "S0-01" / "spec.json").read_text())
    pos = next(leg for leg in spec["legs"] if leg["leg"] == "positive")
    neg = next(leg for leg in spec["legs"] if leg["leg"] == "negative")
    assert pos["cmd"][1].endswith("check_acp_conformance.py")
    assert neg["cmd"] == ["python3", "proofs/S0-01/check_initialize.py", "request",
                          "proofs/S0-01/evidence/golden/negative"]
    assert neg["expect"]["exit_code"] == 1
    assert neg["expect"]["failure_reason"] == "protocol-violation: missing required initialize field"


def test_runner_records_negative_leg_met_s0_99(tmp_path):
    """V3(b): a synthetic proof S0-99 with one negative leg running a tiny script
    that prints 'protocol-violation: missing required initialize field' then
    'observed: ...' and exits 1. The runner records the leg as met (exit 0,
    result.json created with negative_control populated), proving the per-line
    substring match rule against the REAL runner, not a re-implementation.

    The spec schema restricts proof_id to S0-01..S0-12 and requires both positive
    and negative legs, so the tmp copy's schemas are widened to accept S0-99."""
    root = _copy(tmp_path)

    # Widen spec schema to accept S0-99
    spec_schema_path = root / "proofs" / "schemas" / "spec.schema.json"
    spec_schema = json.loads(spec_schema_path.read_text())
    spec_schema["properties"]["proof_id"]["pattern"] = r"^S0-\d+$"
    spec_schema_path.write_text(json.dumps(spec_schema, indent=2))

    # Widen result schema to accept S0-99
    result_schema_path = root / "proofs" / "schemas" / "result.schema.json"
    result_schema = json.loads(result_schema_path.read_text())
    result_schema["properties"]["proof_id"]["pattern"] = r"^S0-\d+$"
    result_schema_path.write_text(json.dumps(result_schema, indent=2))

    # Add S0-99 to registry (strip comment lines first, same as the runner)
    reg_path = root / "proofs" / "registry.yaml"
    reg_text = "\n".join(
        line for line in reg_path.read_text().splitlines()
        if not line.lstrip().startswith("#")
    )
    reg = json.loads(reg_text)
    reg["proofs"].append({
        "proof_id": "S0-99",
        "title": "synthetic runner-match test",
        "classification": "execution_proof",
        "wave": 0,
        "spike_dependencies": [],
        "required_negative_controls": 1,
        "assertion_count": 1,
    })
    reg_path.write_text(json.dumps(reg, indent=2))

    # Create synthetic proof dir
    s99 = root / "proofs" / "S0-99"
    s99.mkdir(parents=True)

    # Positive leg: exits 0 (passes)
    pos_script = s99 / "pass.py"
    pos_script.write_text("import sys; sys.exit(0)\n")

    # Negative leg: prints the expected two-line output and exits 1
    neg_script = s99 / "checker.py"
    neg_script.write_text(
        "import sys\n"
        'print("protocol-violation: missing required initialize field")\n'
        'print("observed: error code=-32602 message=Invalid params")\n'
        "sys.exit(1)\n"
    )

    spec = {
        "proof_id": "S0-99",
        "legs": [
            {
                "leg": "positive",
                "cmd": [sys.executable, "proofs/S0-99/pass.py"],
                "cwd": ".",
                "timeout_s": 30,
                "expect": {"exit_code": 0},
            },
            {
                "leg": "negative",
                "cmd": [sys.executable, "proofs/S0-99/checker.py"],
                "cwd": ".",
                "timeout_s": 30,
                "expect": {
                    "exit_code": 1,
                    "failure_reason": "protocol-violation: missing required initialize field",
                },
            },
        ],
    }
    (s99 / "spec.json").write_text(json.dumps(spec, indent=2))

    r = subprocess.run(
        [sys.executable, str(RUNNER), "run", "--proof", "S0-99",
         "--venue", "sandbox", "--root", str(root)],
        capture_output=True, text=True, timeout=60,
    )
    assert r.returncode == 0, (
        f"runner failed: rc={r.returncode} stdout={r.stdout!r} stderr={r.stderr!r}"
    )

    # The runner creates result.json
    result_path = s99 / "result.json"
    assert result_path.exists(), "result.json not created"
    result = json.loads(result_path.read_text())
    assert result["proof_id"] == "S0-99"
    # The negative_control block must be populated with the observed failure_reason
    assert result["negative_control"] is not None
    assert result["negative_control"]["observed_failure_reason"] == \
        "protocol-violation: missing required initialize field"
    # The run for the negative leg must carry the failure_reason
    neg_run = next(run for run in result["runs"] if run["leg"] == "negative")
    assert neg_run["exit_code"] == 1
    assert neg_run["failure_reason"] == \
        "protocol-violation: missing required initialize field"


def test_runner_records_unmet_when_reason_absent(tmp_path):
    """4-F16/6-F22: a negative leg whose output LACKS the expected failure_reason
    causes the runner to exit non-zero (negative-control-unmet).
    Kills the R07 mutant (negative-control-unmet never raised)."""
    root = _copy(tmp_path)

    # Widen spec schema to accept S0-98
    spec_schema_path = root / "proofs" / "schemas" / "spec.schema.json"
    spec_schema = json.loads(spec_schema_path.read_text())
    spec_schema["properties"]["proof_id"]["pattern"] = r"^S0-\d+$"
    spec_schema_path.write_text(json.dumps(spec_schema, indent=2))

    # Widen result schema
    result_schema_path = root / "proofs" / "schemas" / "result.schema.json"
    result_schema = json.loads(result_schema_path.read_text())
    result_schema["properties"]["proof_id"]["pattern"] = r"^S0-\d+$"
    result_schema_path.write_text(json.dumps(result_schema, indent=2))

    # Add S0-98 to registry
    reg_path = root / "proofs" / "registry.yaml"
    reg_text = "\n".join(
        line for line in reg_path.read_text().splitlines()
        if not line.lstrip().startswith("#")
    )
    reg = json.loads(reg_text)
    reg["proofs"].append({
        "proof_id": "S0-98",
        "title": "synthetic unmet test",
        "classification": "execution_proof",
        "wave": 0,
        "spike_dependencies": [],
        "required_negative_controls": 1,
        "assertion_count": 1,
    })
    reg_path.write_text(json.dumps(reg, indent=2))

    # Create synthetic proof dir
    s98 = root / "proofs" / "S0-98"
    s98.mkdir(parents=True)

    # Positive leg: exits 0
    pos_script = s98 / "pass.py"
    pos_script.write_text("import sys; sys.exit(0)\n")

    # Negative leg: prints something that does NOT contain the expected reason
    neg_script = s98 / "checker.py"
    neg_script.write_text(
        "import sys\n"
        'print("some unrelated output")\n'
        "sys.exit(1)\n"
    )

    spec = {
        "proof_id": "S0-98",
        "legs": [
            {
                "leg": "positive",
                "cmd": [sys.executable, "proofs/S0-98/pass.py"],
                "cwd": ".",
                "timeout_s": 30,
                "expect": {"exit_code": 0},
            },
            {
                "leg": "negative",
                "cmd": [sys.executable, "proofs/S0-98/checker.py"],
                "cwd": ".",
                "timeout_s": 30,
                "expect": {
                    "exit_code": 1,
                    "failure_reason": "protocol-violation: missing required initialize field",
                },
            },
        ],
    }
    (s98 / "spec.json").write_text(json.dumps(spec, indent=2))

    r = subprocess.run(
        [sys.executable, str(RUNNER), "run", "--proof", "S0-98",
         "--venue", "sandbox", "--root", str(root)],
        capture_output=True, text=True, timeout=60,
    )
    assert r.returncode != 0, (
        f"runner should fail (unmet negative), got rc=0: "
        f"stdout={r.stdout!r} stderr={r.stderr!r}"
    )
    assert r.stderr.strip() == "negative-control-unmet: S0-98", (
        f"expected exact unmet line, got: {r.stderr!r}"
    )


def test_runner_matches_reason_on_non_first_line(tmp_path):
    """R5-N5-F14/SR-02: the expected failure_reason on a non-first line is MET.
    Kills the 'first-line exact' mutant."""
    root = _copy(tmp_path)

    spec_schema_path = root / "proofs" / "schemas" / "spec.schema.json"
    spec_schema = json.loads(spec_schema_path.read_text())
    spec_schema["properties"]["proof_id"]["pattern"] = r"^S0-\d+$"
    spec_schema_path.write_text(json.dumps(spec_schema, indent=2))

    result_schema_path = root / "proofs" / "schemas" / "result.schema.json"
    result_schema = json.loads(result_schema_path.read_text())
    result_schema["properties"]["proof_id"]["pattern"] = r"^S0-\d+$"
    result_schema_path.write_text(json.dumps(result_schema, indent=2))

    reg_path = root / "proofs" / "registry.yaml"
    reg_text = "\n".join(
        line for line in reg_path.read_text().splitlines()
        if not line.lstrip().startswith("#")
    )
    reg = json.loads(reg_text)
    reg["proofs"].append({
        "proof_id": "S0-97",
        "title": "reason on non-first line",
        "classification": "execution_proof",
        "wave": 0,
        "spike_dependencies": [],
        "required_negative_controls": 1,
        "assertion_count": 1,
    })
    reg_path.write_text(json.dumps(reg, indent=2))

    s97 = root / "proofs" / "S0-97"
    s97.mkdir(parents=True)
    (s97 / "pass.py").write_text("import sys; sys.exit(0)\n")
    # The reason appears on the SECOND line, not the first
    (s97 / "checker.py").write_text(
        "import sys\n"
        'print("preamble line")\n'
        'print("protocol-violation: missing required initialize field")\n'
        'print("observed: error code=-32602 message=Invalid params")\n'
        "sys.exit(1)\n"
    )
    spec = {
        "proof_id": "S0-97",
        "legs": [
            {"leg": "positive", "cmd": [sys.executable, "proofs/S0-97/pass.py"],
             "cwd": ".", "timeout_s": 30, "expect": {"exit_code": 0}},
            {"leg": "negative", "cmd": [sys.executable, "proofs/S0-97/checker.py"],
             "cwd": ".", "timeout_s": 30, "expect": {
                 "exit_code": 1,
                 "failure_reason": "protocol-violation: missing required initialize field",
             }},
        ],
    }
    (s97 / "spec.json").write_text(json.dumps(spec, indent=2))

    r = subprocess.run(
        [sys.executable, str(RUNNER), "run", "--proof", "S0-97",
         "--venue", "sandbox", "--root", str(root)],
        capture_output=True, text=True, timeout=60,
    )
    assert r.returncode == 0, (
        f"runner should succeed (reason on non-first line), got rc={r.returncode}: "
        f"stdout={r.stdout!r} stderr={r.stderr!r}"
    )
    result = json.loads((s97 / "result.json").read_text())
    assert result["negative_control"]["observed_failure_reason"] == \
        "protocol-violation: missing required initialize field"


def test_runner_records_the_observed_line_not_the_expected_reason(tmp_path):
    """N5d-F2/SR-03 CASE B: the checker prints a line that is a superset of the
    expected reason. The runner must record the OBSERVED line as
    observed_failure_reason, not the expected reason string. Reds on the
    SR-03 mutant (expected in whole_text returns the expected reason verbatim)."""
    root = _copy(tmp_path)

    spec_schema_path = root / "proofs" / "schemas" / "spec.schema.json"
    spec_schema = json.loads(spec_schema_path.read_text())
    spec_schema["properties"]["proof_id"]["pattern"] = r"^S0-\d+$"
    spec_schema_path.write_text(json.dumps(spec_schema, indent=2))

    result_schema_path = root / "proofs" / "schemas" / "result.schema.json"
    result_schema = json.loads(result_schema_path.read_text())
    result_schema["properties"]["proof_id"]["pattern"] = r"^S0-\d+$"
    result_schema_path.write_text(json.dumps(result_schema, indent=2))

    reg_path = root / "proofs" / "registry.yaml"
    reg_text = "\n".join(
        line for line in reg_path.read_text().splitlines()
        if not line.lstrip().startswith("#")
    )
    reg = json.loads(reg_text)
    reg["proofs"].append({
        "proof_id": "S0-96",
        "title": "observed line is a superset",
        "classification": "execution_proof",
        "wave": 0,
        "spike_dependencies": [],
        "required_negative_controls": 1,
        "assertion_count": 1,
    })
    reg_path.write_text(json.dumps(reg, indent=2))

    expected_reason = "protocol-violation: missing required initialize field"
    observed_line = f"failure_reason: negative: {expected_reason} (seq 2, id 0)"
    s96 = root / "proofs" / "S0-96"
    s96.mkdir(parents=True)
    (s96 / "pass.py").write_text("import sys; sys.exit(0)\n")
    (s96 / "checker.py").write_text(
        "import sys\n"
        f'print({observed_line!r})\n'
        "sys.exit(1)\n"
    )
    spec = {
        "proof_id": "S0-96",
        "legs": [
            {"leg": "positive", "cmd": [sys.executable, "proofs/S0-96/pass.py"],
             "cwd": ".", "timeout_s": 30, "expect": {"exit_code": 0}},
            {"leg": "negative", "cmd": [sys.executable, "proofs/S0-96/checker.py"],
             "cwd": ".", "timeout_s": 30, "expect": {
                 "exit_code": 1,
                 "failure_reason": expected_reason,
             }},
        ],
    }
    (s96 / "spec.json").write_text(json.dumps(spec, indent=2))

    r = subprocess.run(
        [sys.executable, str(RUNNER), "run", "--proof", "S0-96",
         "--venue", "sandbox", "--root", str(root)],
        capture_output=True, text=True, timeout=60,
    )
    assert r.returncode == 0, (
        f"runner should succeed (observed line contains expected reason), "
        f"got rc={r.returncode}: stdout={r.stdout!r} stderr={r.stderr!r}"
    )
    result = json.loads((s96 / "result.json").read_text())
    assert result["negative_control"]["observed_failure_reason"] == observed_line, (
        f"observed_failure_reason should be the full observed line, not the expected reason; "
        f"got {result['negative_control']['observed_failure_reason']!r}"
    )


def test_runner_unmet_when_expected_reason_is_multiline(tmp_path):
    """N5d-F2/SR-03 CASE A: a newline in the expected failure_reason makes the
    match impossible under the per-line rule, so the runner must report
    negative-control-unmet. Reds on the SR-03 mutant (expected in whole_text
    matches across the newline boundary)."""
    root = _copy(tmp_path)

    spec_schema_path = root / "proofs" / "schemas" / "spec.schema.json"
    spec_schema = json.loads(spec_schema_path.read_text())
    spec_schema["properties"]["proof_id"]["pattern"] = r"^S0-\d+$"
    spec_schema_path.write_text(json.dumps(spec_schema, indent=2))

    result_schema_path = root / "proofs" / "schemas" / "result.schema.json"
    result_schema = json.loads(result_schema_path.read_text())
    result_schema["properties"]["proof_id"]["pattern"] = r"^S0-\d+$"
    result_schema_path.write_text(json.dumps(result_schema, indent=2))

    reg_path = root / "proofs" / "registry.yaml"
    reg_text = "\n".join(
        line for line in reg_path.read_text().splitlines()
        if not line.lstrip().startswith("#")
    )
    reg = json.loads(reg_text)
    reg["proofs"].append({
        "proof_id": "S0-95",
        "title": "multiline expected reason",
        "classification": "execution_proof",
        "wave": 0,
        "spike_dependencies": [],
        "required_negative_controls": 1,
        "assertion_count": 1,
    })
    reg_path.write_text(json.dumps(reg, indent=2))

    s95 = root / "proofs" / "S0-95"
    s95.mkdir(parents=True)
    (s95 / "pass.py").write_text("import sys; sys.exit(0)\n")
    # Checker prints the two halves as two lines
    (s95 / "checker.py").write_text(
        "import sys\n"
        'print("alpha-violation: part-one")\n'
        'print("part-two tail")\n'
        "sys.exit(1)\n"
    )
    spec = {
        "proof_id": "S0-95",
        "legs": [
            {"leg": "positive", "cmd": [sys.executable, "proofs/S0-95/pass.py"],
             "cwd": ".", "timeout_s": 30, "expect": {"exit_code": 0}},
            {"leg": "negative", "cmd": [sys.executable, "proofs/S0-95/checker.py"],
             "cwd": ".", "timeout_s": 30, "expect": {
                 "exit_code": 1,
                 "failure_reason": "alpha-violation: part-one\npart-two tail",
             }},
        ],
    }
    (s95 / "spec.json").write_text(json.dumps(spec, indent=2))

    r = subprocess.run(
        [sys.executable, str(RUNNER), "run", "--proof", "S0-95",
         "--venue", "sandbox", "--root", str(root)],
        capture_output=True, text=True, timeout=60,
    )
    assert r.returncode != 0, (
        f"runner should fail (multiline expected reason is unmatchable per-line), "
        f"got rc=0: stdout={r.stdout!r} stderr={r.stderr!r}"
    )
    assert r.stderr.strip() == "negative-control-unmet: S0-95"


def test_runner_unmet_when_reason_split_across_streams(tmp_path):
    """R6-N5b-F7/SR-04: the reason's first half on stdout (no trailing newline)
    and the rest on stderr. The runner joins with '\\n' so neither line contains
    the full reason → UNMET. Kills SR-04 (no-separator mutant: stdout+stderr
    concatenation would forge a matching line)."""
    root = _copy(tmp_path)

    spec_schema_path = root / "proofs" / "schemas" / "spec.schema.json"
    spec_schema = json.loads(spec_schema_path.read_text())
    spec_schema["properties"]["proof_id"]["pattern"] = r"^S0-\d+$"
    spec_schema_path.write_text(json.dumps(spec_schema, indent=2))

    result_schema_path = root / "proofs" / "schemas" / "result.schema.json"
    result_schema = json.loads(result_schema_path.read_text())
    result_schema["properties"]["proof_id"]["pattern"] = r"^S0-\d+$"
    result_schema_path.write_text(json.dumps(result_schema, indent=2))

    reg_path = root / "proofs" / "registry.yaml"
    reg_text = "\n".join(
        line for line in reg_path.read_text().splitlines()
        if not line.lstrip().startswith("#")
    )
    reg = json.loads(reg_text)
    reg["proofs"].append({
        "proof_id": "S0-95",
        "title": "reason split across streams",
        "classification": "execution_proof",
        "wave": 0,
        "spike_dependencies": [],
        "required_negative_controls": 1,
        "assertion_count": 1,
    })
    reg_path.write_text(json.dumps(reg, indent=2))

    s95 = root / "proofs" / "S0-95"
    s95.mkdir(parents=True)
    (s95 / "pass.py").write_text("import sys; sys.exit(0)\n")
    # Reason first half on stdout (no trailing newline), rest on stderr
    (s95 / "checker.py").write_text(
        "import sys\n"
        'sys.stdout.write("protocol-violation: missing")\n'
        'sys.stderr.write(" required initialize field\\n")\n'
        "sys.exit(1)\n"
    )
    spec = {
        "proof_id": "S0-95",
        "legs": [
            {"leg": "positive", "cmd": [sys.executable, "proofs/S0-95/pass.py"],
             "cwd": ".", "timeout_s": 30, "expect": {"exit_code": 0}},
            {"leg": "negative", "cmd": [sys.executable, "proofs/S0-95/checker.py"],
             "cwd": ".", "timeout_s": 30, "expect": {
                 "exit_code": 1,
                 "failure_reason": "protocol-violation: missing required initialize field",
             }},
        ],
    }
    (s95 / "spec.json").write_text(json.dumps(spec, indent=2))

    r = subprocess.run(
        [sys.executable, str(RUNNER), "run", "--proof", "S0-95",
         "--venue", "sandbox", "--root", str(root)],
        capture_output=True, text=True, timeout=60,
    )
    assert r.returncode != 0, (
        f"runner should fail (reason split across streams), got rc=0: "
        f"stdout={r.stdout!r} stderr={r.stderr!r}"
    )
    assert r.stderr.strip() == "negative-control-unmet: S0-95"
