#!/usr/bin/env python
"""AP-67 pre-commit guard: a staged edit to a file that a mutation manifest anchors
into re-checks EVERY anchor of that manifest against the staged tree.

The drift shape (2026-09-02, I3h): a later commit in the stack deleted the code a
mutant's `old` anchor spanned; the manifest was untouched, the anchor matched 0 times,
and only the gate of record's stage 4 (after two ~26-min passes) would have said
ANCHOR_FAIL. This runs mutation_run.py --check-anchors (seconds, no pytest) on
`git write-tree` of the index, so the commit that breaks an anchor is the commit
that gets blocked. Manifests whose anchored files are not staged are skipped.
"""
from __future__ import annotations

import importlib.util
import subprocess
import sys
import tempfile
from pathlib import Path

# The runner sits next to this file; the repo is whatever git says the cwd belongs to
# (mutation_run.py resolves REPO the same way), so the test can point both at a temp repo.
MUTATION_RUN = Path(__file__).resolve().parent / "mutation_run.py"


def _repo() -> Path:
    return Path(subprocess.check_output(["git", "rev-parse", "--show-toplevel"], text=True).strip())


def anchored_paths(manifest: Path) -> set[str]:
    spec = importlib.util.spec_from_file_location("mutants_precommit", manifest)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return {path for _name, hunks, *_ in mod.MUTANTS for path, _old, _new in hunks}


def manifests_to_check(staged: set[str], manifests: list[Path], repo: Path) -> list[Path]:
    """A manifest is checked when it is staged itself or any file it anchors into is."""
    out = []
    for m in manifests:
        rel = str(m.relative_to(repo))
        if rel in staged or anchored_paths(m) & staged:
            out.append(m)
    return out


def main() -> int:
    repo = _repo()
    manifest_dir = repo / "scripts" / "mutants"
    staged = set(
        subprocess.check_output(["git", "diff", "--cached", "--name-only"], cwd=repo, text=True).split()
    )
    manifests = sorted(manifest_dir.glob("*.py")) if manifest_dir.is_dir() else []
    todo = manifests_to_check(staged, manifests, repo)
    if not todo:
        return 0
    tree = subprocess.check_output(["git", "write-tree"], cwd=repo, text=True).strip()
    rc = 0
    with tempfile.TemporaryDirectory(prefix="anchor_precommit_") as work:
        for m in todo:
            r = subprocess.run(
                [sys.executable, str(MUTATION_RUN), "--manifest", str(m),
                 "--workdir", work, "--rev", tree, "--check-anchors"],
                cwd=repo, text=True, capture_output=True,
            )
            if r.returncode != 0:
                rc = 1
                print(f"AP-67: manifest {m.relative_to(repo)} has anchors the staged tree no longer "
                      f"matches — re-pin them in the SAME commit:\n{r.stdout}{r.stderr}", file=sys.stderr)
    return rc


if __name__ == "__main__":
    sys.exit(main())
