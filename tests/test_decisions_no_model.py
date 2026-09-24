"""J1-5 (task #122): the decision ledger has no model dependency (seed-laya-j1-v1 AC 5 and AC 10).

Two checks. (1) A static scan: no J1 module imports a model package, statically or through
`importlib.import_module` / `__import__` with a constant name. (2) A run: the J1 test files pass while every
model package is blocked at import time in every Python process of the run, the scripts the tests start
included (a `sitecustomize` on `PYTHONPATH` installs the blocker at interpreter start), and the blocker's log
holds zero ATTEMPTS: an import the code catches, or a test that skips on ImportError, still counts. Negative
controls: the scan reds an added `import laya` (the breakdown's mutant m1, on a copy of ledger.py); the blocker
reds an import, logs a caught one, and reaches a child process.
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
    LOG = {log!r}

    class _Block(importlib.abc.MetaPathFinder):
        def find_spec(self, name, path, target=None):
            if name.split(".")[0] in BLOCKED:
                with open(LOG, "a", encoding="utf-8") as handle:
                    handle.write(name + "\\n")
                raise ImportError("model-import-blocked: " + name)
            return None

    sys.meta_path.insert(0, _Block())
    for loaded in list(sys.modules):
        if loaded.split(".")[0] in BLOCKED:
            del sys.modules[loaded]
    """
)


def model_imports(path: pathlib.Path) -> list[str]:
    """Every import of a model package in one source file, as `name:line: module`, in line order."""
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
                found.append((node.lineno, f"{path.name}:{node.lineno}: {name}"))
    return [text for _, text in sorted(found)]


def _run_blocked(work: pathlib.Path, *argv: str) -> tuple[subprocess.CompletedProcess, list[str]]:
    """Run `python ARGV` with the model packages blocked in it and in every Python process it starts.

    Returns the result and the blocked import attempts, in order."""
    site_dir = work / "model-blocker"
    site_dir.mkdir(parents=True)
    log = work / "blocked-imports.log"
    (site_dir / "sitecustomize.py").write_text(
        BLOCKER.format(blocked=MODEL_PACKAGES, log=str(log)), encoding="utf-8"
    )
    # The venv's editable install may point at another checkout: import this tree's src first.
    path = [str(site_dir), str(ROOT / "src"), os.environ.get("PYTHONPATH")]
    env = dict(os.environ, PYTHONPATH=os.pathsep.join(filter(None, path)))
    result = subprocess.run(
        [sys.executable, *argv], cwd=ROOT, env=env, capture_output=True, text=True, timeout=600
    )
    attempts = log.read_text(encoding="utf-8").splitlines() if log.exists() else []
    return result, attempts


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
    forms = tmp_path / "forms.py"
    forms.write_text(
        "import importlib\n"
        "importlib.import_module('torch.nn')\n"
        "from transformers import AutoModel\n"
        "__import__('safetensors')\n"
        "from .torch import helpers\n",
        encoding="utf-8",
    )
    # The relative import (line 5) names a local module, not the package: it must not be flagged.
    assert model_imports(forms) == ["forms.py:2: torch.nn", "forms.py:3: transformers", "forms.py:4: safetensors"]


def test_j1_suite_passes_with_model_packages_blocked(tmp_path):
    argv = ["-m", "pytest", *J1_TESTS, "-q", "-p", "no:cacheprovider", f"--basetemp={tmp_path / 'bt'}"]
    result, attempts = _run_blocked(tmp_path, *argv)
    tail = (result.stdout + result.stderr)[-3000:]
    assert result.returncode == 0, tail
    assert attempts == [], "decisions-attempted-model-import: " + ", ".join(attempts)
    assert " passed" in result.stdout.splitlines()[-1], tail


def test_blocker_reds_an_import_logs_a_caught_one_and_reaches_a_child(tmp_path):
    result, attempts = _run_blocked(tmp_path / "direct", "-c", "import laya")
    assert result.returncode != 0
    assert "ImportError: model-import-blocked: laya" in result.stderr
    assert attempts == ["laya"]
    result, attempts = _run_blocked(tmp_path / "caught", "-c", "try:\n    import torch.nn\nexcept ImportError:\n    pass")
    assert (result.returncode, attempts) == (0, ["torch"])
    child = "import subprocess, sys; raise SystemExit(subprocess.run([sys.executable, '-c', 'import transformers']).returncode)"
    result, attempts = _run_blocked(tmp_path / "child", "-c", child)
    assert result.returncode != 0
    assert "ImportError: model-import-blocked: transformers" in result.stderr
    assert attempts == ["transformers"]
