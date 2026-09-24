"""J1-5 (task #122): the decision ledger has no model dependency (seed-laya-j1-v1 AC 5 and AC 10).

Two checks. (1) A static scan: no J1 module imports a model package, statically or through
`importlib.import_module` / `__import__` with a constant name. (2) A run: the J1 test files pass in a
subprocess where every model package is blocked at import time, so the result does not depend on what
the venv happens to have installed. Negative controls: the scan reds an added `import laya` (the
breakdown's mutant m1, on a copy of ledger.py); the blocker reds a real import of a blocked package.
"""
import ast
import os
import pathlib
import subprocess
import sys
import textwrap

ROOT = pathlib.Path(__file__).resolve().parents[1]
MODEL_PACKAGES = ("laya", "torch", "transformers", "safetensors", "huggingface_hub")
J1_MODULES = [
    *sorted((ROOT / "src" / "agent_factory" / "decisions").glob("*.py")),
    ROOT / "scripts" / "decide-harvest",
    ROOT / "scripts" / "no_laya_in_gates.py",
]
J1_TESTS = [
    "tests/test_decisions_canonical.py",
    "tests/test_decisions_ledger.py",
    "tests/test_decide_harvest.py",
    "tests/test_no_laya_in_gates.py",
]
BLOCKER = textwrap.dedent(
    """
    import importlib.abc
    import sys

    BLOCKED = {blocked!r}

    class _Block(importlib.abc.MetaPathFinder):
        def find_spec(self, name, path, target=None):
            if name.split(".")[0] in BLOCKED:
                raise ImportError("model-import-blocked: " + name)
            return None

    sys.meta_path.insert(0, _Block())
    for loaded in list(sys.modules):
        if loaded.split(".")[0] in BLOCKED:
            del sys.modules[loaded]
    {body}
    """
)


def model_imports(path: pathlib.Path) -> list[str]:
    """Every import of a model package in one source file, as `name:line: module`."""
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    found = []
    for node in ast.walk(tree):
        names = []
        if isinstance(node, ast.Import):
            names = [alias.name for alias in node.names]
        elif isinstance(node, ast.ImportFrom) and node.level == 0 and node.module:
            names = [node.module]
        elif isinstance(node, ast.Call) and node.args and isinstance(node.args[0], ast.Constant):
            func = node.func
            called = func.attr if isinstance(func, ast.Attribute) else getattr(func, "id", "")
            if called in ("import_module", "__import__") and isinstance(node.args[0].value, str):
                names = [node.args[0].value]
        for name in names:
            if name.split(".")[0] in MODEL_PACKAGES:
                found.append(f"{path.name}:{node.lineno}: {name}")
    return found


def _run_blocked(body: str, *args: str, tmp_path: pathlib.Path) -> subprocess.CompletedProcess:
    code = BLOCKER.format(blocked=set(MODEL_PACKAGES), body=body)
    # The venv's editable install may point at another checkout: import this tree's src first.
    env = dict(os.environ, PYTHONPATH=os.pathsep.join(filter(None, [str(ROOT / "src"), os.environ.get("PYTHONPATH")])))
    return subprocess.run(
        [sys.executable, "-c", code, *args],
        cwd=ROOT,
        env=env,
        capture_output=True,
        text=True,
        timeout=600,
    )


def test_no_j1_module_imports_a_model_package():
    assert all(path.is_file() for path in J1_MODULES), [str(p) for p in J1_MODULES if not p.is_file()]
    hits = [hit for path in J1_MODULES for hit in model_imports(path)]
    assert hits == [], "decisions-imports-model: " + "; ".join(hits)


def test_scan_reds_an_added_laya_import(tmp_path):
    ledger = (ROOT / "src" / "agent_factory" / "decisions" / "ledger.py").read_text(encoding="utf-8")
    mutant = tmp_path / "ledger.py"
    mutant.write_text(ledger + "\nimport laya\n", encoding="utf-8")
    line = len(mutant.read_text(encoding="utf-8").splitlines())
    assert model_imports(mutant) == [f"ledger.py:{line}: laya"]
    dynamic = tmp_path / "dynamic.py"
    dynamic.write_text("import importlib\nimportlib.import_module('torch.nn')\n", encoding="utf-8")
    assert model_imports(dynamic) == ["dynamic.py:2: torch.nn"]


def test_j1_suite_passes_with_model_packages_blocked(tmp_path):
    body = "import pytest\nsys.exit(pytest.main(sys.argv[1:]))"
    result = _run_blocked(body, *J1_TESTS, "-q", "-p", "no:cacheprovider", f"--basetemp={tmp_path / 'bt'}", tmp_path=tmp_path)
    tail = (result.stdout + result.stderr)[-3000:]
    assert result.returncode == 0, tail
    assert "model-import-blocked" not in result.stdout + result.stderr, tail
    assert " passed" in result.stdout.splitlines()[-1], tail


def test_blocker_reds_a_blocked_import(tmp_path):
    result = _run_blocked("import laya", tmp_path=tmp_path)
    assert result.returncode != 0
    assert "ImportError: model-import-blocked: laya" in result.stderr
