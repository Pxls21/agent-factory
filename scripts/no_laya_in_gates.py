#!/usr/bin/env python3
"""Advisory-exclusion screen: no Laya/Jev vocabulary in gate-defining files.

KC-J1 mechanism -- an absorbing barrier with no bypass.  Exit codes:
  0   clean
  3   violation (one line per hit: <path>:<line>:<token>)
  4   completeness control (gate-file-unlisted or gate-file-missing)
  64  usage error
"""

import argparse
import re
import subprocess
import sys
from pathlib import Path

# ---------- Closed vocabulary ----------

# Simple tokens: matched as whole maximal runs of [A-Za-z0-9_-], case-insensitive.
# A maximal run is the longest contiguous sequence of identifier characters.
# "laya_probe" is ONE run and is NOT in the list, so it does not fire.
# "receives" is ONE run and is NOT in the list, so it does not fire.
# "Laya" matches "laya" case-insensitively and fires.
SIMPLE_TOKENS = frozenset([
    "laya", "systemone", "system_one", "system-one",
    "jev", "jevcache", "sieve", "sieve-run",
    "decide-harvest", "decide_harvest", "laya-decide",
])

# Dotted tokens: matched as literal substrings at identifier boundaries.
DOTTED_TOKENS = (
    "agent_factory.decisions",
    "decisions.ledger",
    "decisions.canonical",
    "decisions.jsonl",
)

# The screen's own path -- refuses to be listed (it contains the vocabulary).
SELF_PATH = "scripts/no_laya_in_gates.py"

# ---------- Matching ----------

_TOKEN_RE = re.compile(r"[A-Za-z0-9_-]+")
_ID_CHARS = frozenset("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_-")

# Structural import patterns for .py files.
_IMPORT_RE = re.compile(
    r"^\s*(?:"
    r"import\s+agent_factory\.decisions\b"
    r"|from\s+agent_factory\.decisions(?:\.\w+)*\s+import\b"
    r"|from\s+agent_factory\s+import\s+decisions\b"
    r")",
)


def _check_line(line, is_py):
    """Return a list of matched vocabulary tokens from a single line."""
    hits = []
    seen = set()

    # 1. Simple tokens via maximal-run boundary matching
    for m in _TOKEN_RE.finditer(line):
        canon = m.group().lower()
        if canon in SIMPLE_TOKENS and canon not in seen:
            hits.append(canon)
            seen.add(canon)

    # 2. Dotted tokens via literal substring with boundary checks
    lower = line.lower()
    for tok in DOTTED_TOKENS:
        if tok in seen:
            continue
        idx = 0
        while True:
            pos = lower.find(tok, idx)
            if pos == -1:
                break
            before_ok = pos == 0 or lower[pos - 1] not in _ID_CHARS
            end = pos + len(tok)
            after_ok = end >= len(lower) or lower[end] not in _ID_CHARS
            if before_ok and after_ok:
                hits.append(tok)
                seen.add(tok)
                break
            idx = pos + 1

    # 3. Structural import check (.py files only)
    if is_py and "agent_factory.decisions" not in seen:
        if _IMPORT_RE.match(line):
            hits.append("agent_factory.decisions")

    return hits


# ---------- File reading ----------

def _read_staged(path):
    """Read the staged (index) version of a file via git show."""
    try:
        r = subprocess.run(
            ["git", "show", ":%s" % path],
            capture_output=True, text=True, check=True,
        )
        return r.stdout
    except subprocess.CalledProcessError:
        return None


def _read_file(root, path):
    """Read a file from a filesystem root."""
    fp = root / path
    try:
        return fp.read_text(errors="replace")
    except (OSError, UnicodeDecodeError):
        return None


# ---------- Allowlist and completeness ----------

def _load_allowlist(list_path):
    """Load the gate-file allowlist, stripping comments and blanks."""
    entries = []
    for line in list_path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        entries.append(line)
    return entries


def _glob_structural(root):
    """Walk the three structural patterns and return repo-relative paths."""
    found = set()
    # scripts/hooks/*
    hooks_dir = root / "scripts" / "hooks"
    if hooks_dir.is_dir():
        for p in hooks_dir.iterdir():
            if p.is_file():
                found.add(str(p.relative_to(root)))
    # .github/workflows/*.yml
    wf_dir = root / ".github" / "workflows"
    if wf_dir.is_dir():
        for p in wf_dir.glob("*.yml"):
            if p.is_file():
                found.add(str(p.relative_to(root)))
    # proofs/*/check_*.py
    proofs_dir = root / "proofs"
    if proofs_dir.is_dir():
        for sub in proofs_dir.iterdir():
            if sub.is_dir():
                for p in sub.glob("check_*.py"):
                    if p.is_file():
                        found.add(str(p.relative_to(root)))
    return found


# ---------- Main ----------

def main():
    parser = argparse.ArgumentParser(
        description="Advisory-exclusion screen: no Laya/Jev vocabulary in gate files.",
    )
    parser.add_argument(
        "--root", type=str, default=None,
        help="Scan this tree instead of the repo (for fixture trees).",
    )
    parser.add_argument(
        "--list", type=str, default=None,
        help="Path to the allowlist (default: <root>/scripts/gate_files.txt).",
    )
    parser.add_argument(
        "--staged", action="store_true",
        help="Scan staged (index) content via git show instead of files on disk.",
    )
    args = parser.parse_args()

    # Determine root
    if args.root is not None:
        root = Path(args.root).resolve()
    else:
        root = Path.cwd()

    # Determine allowlist path
    if args.list is not None:
        list_path = Path(args.list)
    else:
        list_path = root / "scripts" / "gate_files.txt"

    if not list_path.exists():
        print("gate-file-missing: %s" % list_path, file=sys.stderr)
        return 64

    entries = _load_allowlist(list_path)

    # Self-listing check
    for e in entries:
        if e == SELF_PATH:
            print("gate-file-self: %s" % SELF_PATH, file=sys.stderr)
            return 64

    # --- Completeness control ---
    completeness_errors = []
    structural_matches = _glob_structural(root)
    listed_set = set(entries)
    for path in sorted(structural_matches):
        if path not in listed_set:
            completeness_errors.append("gate-file-unlisted: %s" % path)

    # Check listed paths exist (skip in staged mode: files may not be on disk)
    if not args.staged:
        for entry in entries:
            fp = root / entry
            if not fp.exists():
                completeness_errors.append("gate-file-missing: %s" % entry)

    if completeness_errors:
        for err in completeness_errors:
            print(err, file=sys.stderr)
        return 4

    # --- Scan ---
    violations = []
    scanned = 0
    for entry in entries:
        is_py = entry.endswith(".py")
        if args.staged:
            content = _read_staged(entry)
        else:
            content = _read_file(root, entry)
        if content is None:
            continue
        scanned += 1
        for lineno, line in enumerate(content.splitlines(), 1):
            for token in _check_line(line, is_py):
                violations.append("%s:%d:%s" % (entry, lineno, token))

    if violations:
        for v in violations:
            print(v)
        return 3

    print("no_laya_in_gates: %d files scanned, clean" % scanned, file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
