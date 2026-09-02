#!/usr/bin/env python
"""Run a mutation manifest against a git-archive copy of HEAD.

The manifest is a .py file exposing MUTANTS = [(name, hunks[, tests]), ...] with
hunks = [(path, old, new), ...] (the RP-30b I3g catalogue shape). Each mutant is applied
to a FRESH archive of HEAD in --workdir (the shared checkout is never touched, so a
verifier can run this while the tree is live), the gate suite is run once, and the
mutant is KILLED when pytest exits non-zero. A mutant's optional `tests` narrows the run
to its expected killers (a 43-file gate set x 9 mutants is a day of sandbox CPU); every
such target must be a FILE of the --tests gate set, else SCOPE_FAIL — a kill by a test
outside the gate proves nothing about the gate. Every `old` anchor must occur exactly once — an anchor that drifted
is reported as ANCHOR_FAIL, never silently skipped (a skipped mutant looks killed).

Exit 1 when any mutant SURVIVED or any anchor failed. Output is one line per mutant
plus a totals line, meant to be pasted verbatim into the lane report.
"""
from __future__ import annotations

import argparse
import importlib.util
import os
import shutil
import subprocess
import sys
from pathlib import Path

REPO = Path(subprocess.check_output(["git", "rev-parse", "--show-toplevel"], text=True).strip())
PY = sys.executable


def _load(manifest: Path):
    spec = importlib.util.spec_from_file_location("mutants", manifest)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return list(mod.MUTANTS)


def _fresh_tree(dest: Path, rev: str) -> None:
    if dest.exists():
        shutil.rmtree(dest)
    dest.mkdir(parents=True)
    archive = subprocess.Popen(["git", "archive", rev], cwd=REPO, stdout=subprocess.PIPE)
    subprocess.check_call(["tar", "-x", "-C", str(dest)], stdin=archive.stdout)
    archive.wait()
    if archive.returncode != 0:
        raise SystemExit(f"git archive {rev} failed")
    # Same fix as lane_gate.sh::archive_tree — the editable vbt install resolves
    # to <repo>/vectorbtpro-new, so an archived copy at another path makes
    # verify_vbt_install() red every vbt-touching test as a "shadow". Without
    # this, a killer file like test_seal_certification.py fails whatever the
    # mutation did and every KILLED line narrowed to it is hollow (V7-F1).
    vbt = REPO / "vectorbtpro-new"
    if vbt.is_dir():
        shutil.rmtree(dest / "vectorbtpro-new", ignore_errors=True)
        (dest / "vectorbtpro-new").symlink_to(vbt)


def _apply(tree: Path, hunks) -> str | None:
    for path, old, new in hunks:
        p = tree / path
        if not p.exists():
            return f"missing file {path}"
        s = p.read_text()
        c = s.count(old)
        if c != 1:
            return f"anchor count {c} in {path}"
        p.write_text(s.replace(old, new))
    return None


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--manifest", required=True)
    ap.add_argument(
        "--tests",
        help="space-separated pytest targets (the gate set). Required to run; optional "
             "with --check-anchors, where omitting it skips the scope check and SAYS so "
             "(the pre-commit anchor hook has no gate set -- a fake one made every "
             "narrowed mutant SCOPE_FAIL, 2026-09-02)",
    )
    ap.add_argument("--workdir", required=True)
    ap.add_argument("--rev", default="HEAD")
    ap.add_argument("--only", help="comma-separated mutant names")
    ap.add_argument(
        "--check-anchors", action="store_true",
        help="apply every anchor to one archive of --rev and exit; no pytest. Seconds, "
             "not an hour — run it BEFORE the gate so a drifted anchor is caught up front "
             "(2026-09-02: a commit that removed a local import left a manifest anchor "
             "stale and the 50-minute gate of record would have been the first to say so)",
    )
    args = ap.parse_args()

    mutants = _load(Path(args.manifest))
    if args.only:
        keep = set(args.only.split(","))
        mutants = [m for m in mutants if m[0] in keep]
    if not args.tests and not args.check_anchors:
        ap.error("--tests is required to run mutants")
    tests = args.tests.split() if args.tests else []
    work = Path(args.workdir)
    logs = work / "logs"
    logs.mkdir(parents=True, exist_ok=True)
    tree = work / "tree"

    gate_files = {t.split("::")[0] for t in tests}
    killed, survived, anchor_fail = [], [], []
    if args.check_anchors:
        # One archive, every mutant applied to its own fresh copy of the touched
        # files only (cheap): anchors are checked against pristine bytes each time.
        _fresh_tree(tree, args.rev)
        pristine = {}
        if not tests:
            print("scope: UNCHECKED (no --tests given)")
        for name, hunks, *rest in mutants:
            # Scope is checked here too, or a killer file outside the gate set
            # passes the seconds-long pre-flight and fails an hour later (V7-F6).
            run_tests = list(rest[0]) if rest and rest[0] else tests
            out_of_scope = sorted({t.split("::")[0] for t in run_tests} - gate_files) if tests else []
            if out_of_scope:
                anchor_fail.append(name)
                print(f"SCOPE_FAIL {name}: not in gate set: {' '.join(out_of_scope)}")
                continue
            for path, _old, _new in hunks:
                p = tree / path
                pristine.setdefault(path, p.read_text() if p.exists() else None)
            err = _apply(tree, hunks)
            for path, text in pristine.items():
                if text is not None:
                    (tree / path).write_text(text)
            if err:
                anchor_fail.append(name)
                print(f"ANCHOR_FAIL {name}: {err}")
            else:
                print(f"ANCHOR_OK   {name}")
        print(f"mutation_run --check-anchors ({args.rev}): {len(mutants)} checked / "
              f"{len(anchor_fail)} anchor-fail")
        return 1 if anchor_fail else 0
    for entry in mutants:
        name, hunks = entry[0], entry[1]
        run_tests = list(entry[2]) if len(entry) > 2 and entry[2] else tests
        out_of_scope = sorted({t.split("::")[0] for t in run_tests} - gate_files)
        if out_of_scope:
            anchor_fail.append(name)
            print(f"SCOPE_FAIL {name}: not in gate set: {' '.join(out_of_scope)}")
            continue
        _fresh_tree(tree, args.rev)
        err = _apply(tree, hunks)
        if err:
            anchor_fail.append(name)
            print(f"ANCHOR_FAIL {name}: {err}")
            continue
        env = dict(os.environ, PYTHONPATH=".", PYTHONDONTWRITEBYTECODE="1")
        log = logs / f"{name}.log"
        with open(log, "w") as fh:
            rc = subprocess.call(
                [PY, "-m", "pytest", "-p", "no:randomly", "-q", "--tb=no", "-rfE", *run_tests],
                cwd=tree, env=env, stdout=fh, stderr=subprocess.STDOUT,
            )
        tail = ""
        for line in reversed(log.read_text().splitlines()):
            if " passed" in line or " failed" in line or " error" in line or "no tests ran" in line:
                tail = line.strip()
                break
        if rc == 0:
            survived.append(name)
            print(f"SURVIVED {name}: {tail}")
        else:
            killed.append(name)
            print(f"KILLED   {name}: {tail} [{len(run_tests)} target(s)]")

    print(f"mutation_run ({args.rev}): {len(mutants)} run / {len(killed)} killed / "
          f"{len(survived)} survived / {len(anchor_fail)} anchor-fail")
    if survived:
        print("  survivors: " + ", ".join(survived))
    return 1 if (survived or anchor_fail) else 0


if __name__ == "__main__":
    sys.exit(main())
