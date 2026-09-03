"""Round-4 verifier RED tests for S0-01. Do not relax without an adversarial finding."""
import json
import pathlib
import shutil
import subprocess
import sys


ROOT = pathlib.Path(__file__).resolve().parents[2]
CLI = ROOT / "scripts" / "validate-ledger"


def _copy_contract(tmp_path):
    root = tmp_path / "repo"
    shutil.copytree(ROOT / "proofs", root / "proofs")
    return root


def _registry(root):
    path = root / "proofs" / "registry.yaml"
    text = "\n".join(line for line in path.read_text().splitlines() if not line.lstrip().startswith("#"))
    return path, json.loads(text)


def _run(root):
    return subprocess.run(
        [sys.executable, str(CLI), "integrity", "--root", str(root)],
        capture_output=True,
        text=True,
        timeout=5,
    )


def test_registry_reports_all_missing_required_proof_fields(tmp_path):
    root = _copy_contract(tmp_path)
    path, registry = _registry(root)
    registry["proofs"][0].pop("classification")
    registry["proofs"][0].pop("title")
    path.write_text(json.dumps(registry))

    completed = _run(root)

    assert completed.returncode == 1
    assert "registry-schema: S0-01 missing classification" in completed.stdout
    assert "registry-schema: S0-01 missing classification,title" in completed.stdout
    assert completed.stderr == ""
