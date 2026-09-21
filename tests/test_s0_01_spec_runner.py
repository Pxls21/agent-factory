"""S0-01 through the CANONICAL proof-runner.

The committed evidence (since the 2026-09-21 recapture, the REAL v2.4 bundle:
five legs + the negative leg) is a real capture. The deferral tests exercise
the DEFERRED path on a controlled input instead: _strip_v2_evidence puts a COPY
of the tree into the v1 shape (no leg carries a timeline; negative/ absent) so
the deferral path still runs.

The two "committed" tests pin the COMMITTED tree's real behaviour after owner
decision (a), 2026-09-21 (AF-AP-107): the order-free golden lets the canonical
runner finish with rc 0 and mint result.json on its copy, while the negative leg
cmd still prints the two-line protocol-violation classification and exits 1.

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


def _strip_v2_evidence(root):
    """Put a copy of the tree into the DEFERRED state on purpose: no leg carries a timeline (the checker's
    `v2 evidence not captured` predicate) and negative/ is absent. Until 2026-09-21 the committed tree WAS in
    this state (the withdrawn 2026-09-05 v1 bundle); since the v2.4 recapture it is a real bundle, so the
    deferral path is exercised on a controlled input instead of on whatever the tree happens to hold."""
    golden = root / "proofs" / "S0-01" / "evidence" / "golden"
    for tl in golden.glob("*/timeline.jsonl"):
        tl.unlink()
    shutil.rmtree(golden / "negative", ignore_errors=True)
    # The committed tree carries proofs/S0-01/result.json since the 2026-09-21 mint; the DEFERRED state never
    # had one and the runner PRESERVES an existing artifact on deferral, so strip the copy's too — the deferral
    # tests prove NON-CREATION (the PC 13-file gate on e458801 caught the inherited artifact: 2 failed).
    (root / "proofs" / "S0-01" / "result.json").unlink(missing_ok=True)
    return root


def test_positive_leg_defers_on_v1_evidence(tmp_path):
    """The positive leg defers (exit 2) when no leg carries a timeline (the v1 shape of the withdrawn
    2026-09-05 bundle, reconstructed on the copy). The runner must NOT create a result.json."""
    root = _strip_v2_evidence(_copy(tmp_path))
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
    for real on a copy stripped to the v1 shape → exact deferral stderr and exit 2. The positive leg defers first."""
    root = _strip_v2_evidence(_copy(tmp_path))
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
    """The negative leg cmd defers (negative/ absent on the stripped copy) with the exact text."""
    root = _strip_v2_evidence(_copy(tmp_path))
    spec = json.loads((root / "proofs" / "S0-01" / "spec.json").read_text())
    neg = next(leg for leg in spec["legs"] if leg["leg"] == "negative")
    r = subprocess.run(
        [sys.executable, *neg["cmd"][1:]],
        cwd=root, capture_output=True, text=True, timeout=60,
    )
    assert r.returncode == 2, f"expected exit 2 (deferred), got {r.returncode}: {r.stdout}"
    assert r.stdout.strip() == "deferred: negative probe not captured"


def test_committed_bundle_runner_mints_a_result(tmp_path):
    """The committed v2.4 bundle through the REAL runner succeeds after owner decision
    (a) made asynchronous session metadata order-free. The runner is silent on success
    and writes result.json in the copied tree; it never mutates the source checkout."""
    root = _copy(tmp_path)
    result = root / "proofs" / "S0-01" / "result.json"
    result.unlink(missing_ok=True)   # the copy carries the committed mint: prove the runner WRITES one
    r = subprocess.run(
        [sys.executable, str(RUNNER), "run", "--proof", "S0-01",
         "--venue", "sandbox", "--root", str(root)],
        capture_output=True, text=True, timeout=120,
    )
    assert r.returncode == 0, (
        f"expected exit 0, got {r.returncode}: "
        f"stdout={r.stdout!r} stderr={r.stderr!r}"
    )
    assert r.stdout == ""
    assert r.stderr == ""
    assert result.is_file()


def test_committed_negative_leg_cmd_reports_the_protocol_violation(tmp_path):
    """The committed v2.4 negative leg remains unchanged by the golden decision: its
    malformed initialize is classified on line 1, the observed error is on line 2,
    and the command exits 1."""
    root = _copy(tmp_path)
    spec = json.loads((root / "proofs" / "S0-01" / "spec.json").read_text())
    neg = next(leg for leg in spec["legs"] if leg["leg"] == "negative")
    r = subprocess.run(
        [sys.executable, *neg["cmd"][1:]],
        cwd=root, capture_output=True, text=True, timeout=60,
    )
    assert r.returncode == 1, (
        f"expected exit 1, got {r.returncode}: {r.stdout!r}"
    )
    assert r.stdout.splitlines() == [
        "protocol-violation: missing required initialize field",
        "observed: error code=-32602 message=Invalid params",
    ]


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


def test_runner_per_line_rule_holds_for_a_multiline_expected_reason(tmp_path):
    """The schema forbids a multiline reason in production
    (see test_spec_failure_reason_rejects_edge_whitespace_and_newlines);
    this pins the matcher itself, with the pattern lifted from the schema
    copy so the reason can reach the loop.  SR-03 mutant killer
    (expected in whole_text matches across the newline boundary)."""
    root = _copy(tmp_path)

    spec_schema_path = root / "proofs" / "schemas" / "spec.schema.json"
    spec_schema = json.loads(spec_schema_path.read_text())
    spec_schema["properties"]["proof_id"]["pattern"] = r"^S0-\d+$"
    # Remove the failure_reason pattern so the multiline reason passes schema validation
    fr_props = spec_schema["$defs"]["leg"]["properties"]["expect"]["properties"]["failure_reason"]
    fr_props.pop("pattern", None)
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


def _register_runner_proof(root, proof_id, title, reason, checker_src):
    """Register a synthetic proof (schema pattern + registry + S0-N dir) running
    the given checker as its negative leg; return the proof dir."""
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
        "proof_id": proof_id,
        "title": title,
        "classification": "execution_proof",
        "wave": 0,
        "spike_dependencies": [],
        "required_negative_controls": 1,
    })
    reg_path.write_text(json.dumps(reg, indent=2))

    sdir = root / "proofs" / proof_id
    sdir.mkdir(parents=True)
    (sdir / "pass.py").write_text("import sys; sys.exit(0)\n")
    (sdir / "checker.py").write_text(checker_src)
    spec = {
        "proof_id": proof_id,
        "legs": [
            {"leg": "positive", "cmd": [sys.executable, f"proofs/{proof_id}/pass.py"],
             "cwd": ".", "timeout_s": 30, "expect": {"exit_code": 0}},
            {"leg": "negative", "cmd": [sys.executable, f"proofs/{proof_id}/checker.py"],
             "cwd": ".", "timeout_s": 30, "expect": {
                 "exit_code": 1,
                 "failure_reason": reason,
             }},
        ],
    }
    (sdir / "spec.json").write_text(json.dumps(spec, indent=2))
    return sdir


def test_runner_reason_match_is_case_sensitive(tmp_path):
    """N5e-F7/SR-07: the checker prints the expected reason UPPER-CASED while
    the spec expects it lower-case.  A case-insensitive match would forge a
    pass; the runner's per-line 'expected in line' is case-SENSITIVE, so this
    must report negative-control-unmet."""
    root = _copy(tmp_path)
    reason = "protocol-violation: missing required initialize field"
    checker_src = (
        "import sys\n"
        f"print({reason.upper()!r})\n"
        "sys.exit(1)\n"
    )
    _register_runner_proof(root, "S0-96", "case-sensitive reason match",
                           reason, checker_src)
    r = subprocess.run(
        [sys.executable, str(RUNNER), "run", "--proof", "S0-96",
         "--venue", "sandbox", "--root", str(root)],
        capture_output=True, text=True, timeout=60,
    )
    assert r.returncode != 0, (
        f"runner should fail (case-insensitive match would forge a pass), "
        f"got rc=0: stdout={r.stdout!r} stderr={r.stderr!r}"
    )
    assert r.stderr.strip() == "negative-control-unmet: S0-96"


def test_runner_records_the_first_matching_line(tmp_path):
    """N5e-F7/SR-08: TWO lines both contain the expected reason.  The
    runner's next(...) generator must record the FIRST occurrence, not the
    last."""
    root = _copy(tmp_path)
    reason = "protocol-violation: missing required initialize field"
    first_line = f"failure_reason: negative: {reason} (first occurrence)"
    second_line = f"failure_reason: negative: {reason} (second occurrence)"
    checker_src = (
        "import sys\n"
        f"print({first_line!r})\n"
        f"print({second_line!r})\n"
        "sys.exit(1)\n"
    )
    sdir = _register_runner_proof(root, "S0-94", "first matching line recorded",
                                  reason, checker_src)
    r = subprocess.run(
        [sys.executable, str(RUNNER), "run", "--proof", "S0-94",
         "--venue", "sandbox", "--root", str(root)],
        capture_output=True, text=True, timeout=60,
    )
    assert r.returncode == 0, (
        f"runner should succeed (reason present), got rc={r.returncode}: "
        f"stdout={r.stdout!r} stderr={r.stderr!r}"
    )
    result = json.loads((sdir / "result.json").read_text())
    assert result["negative_control"]["observed_failure_reason"] == first_line, (
        f"observed_failure_reason should be the FIRST matching line, got "
        f"{result['negative_control']['observed_failure_reason']!r}"
    )


def test_runner_records_the_raw_line_not_the_stripped_line(tmp_path):
    """N5f-F9/SR-09: the checker prints a padded line.  The runner must record
    the RAW observed line (with padding), not the stripped version.
    Kills SR-09 (line.strip() recorded)."""
    root = _copy(tmp_path)
    reason = "protocol-violation: whitespace test"
    padded_line = f"   failure_reason: negative: {reason}   "
    checker_src = (
        "import sys\n"
        f"print({padded_line!r})\n"
        "sys.exit(1)\n"
    )
    sdir = _register_runner_proof(root, "S0-93", "raw line not stripped",
                                  reason, checker_src)
    r = subprocess.run(
        [sys.executable, str(RUNNER), "run", "--proof", "S0-93",
         "--venue", "sandbox", "--root", str(root)],
        capture_output=True, text=True, timeout=60,
    )
    assert r.returncode == 0, (
        f"runner should succeed (reason present in padded line), got rc={r.returncode}: "
        f"stdout={r.stdout!r} stderr={r.stderr!r}"
    )
    result = json.loads((sdir / "result.json").read_text())
    assert result["negative_control"]["observed_failure_reason"] == padded_line, (
        f"observed_failure_reason should be the RAW padded line, got "
        f"{result['negative_control']['observed_failure_reason']!r}"
    )
