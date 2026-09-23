#!/usr/bin/env python3
"""Advisory-exclusion screen: no Laya/Jev vocabulary in gate-defining files.

KC-J1 mechanism -- an absorbing barrier with no bypass.  Exit codes:
  0   clean
  3   violation (one line per hit: <path>:<line>:<token>)
  4   completeness control (gate-file-unlisted, gate-file-missing, gate-file-not-regular,
      gate-file-unreadable, gate-file-sources, gate-file-unparseable,
      gate-file-import-unlisted, gate-file-import-unresolved or gate-file-import-ambiguous)
  64  usage error

Include edges (AMENDMENT 2, J1-0-R3, AF-AP-120): the screen reads the TEXT of listed files, so
it also closes the edges through which a listed file pulls other code INTO ITS OWN PROCESS.
A `source` or `.` command in a non-Python gate file is refused unless its exact (file, target)
pair is in the closed ALLOWED_SOURCES set (two today, neither loads repo code). Every
import of a Python gate file must resolve to the standard library, the closed EXTERNAL_MODULES
set, or a LISTED repo file (which is then screened like any other listed file). Declared limit,
not followed: EXEC edges, where a gate file runs another repo script in a separate process
(`bash harness-ports/bin/x.sh`, `python3 "$AF_REPO/scripts/y.py"`). Many are built from
variables no lexical rule can resolve, and a fail-closed rule would block every commit. Measured
at this amendment (2026-09-23): 26 literal exec edges from listed shell gate files reach 12
unlisted scripts. Dynamic imports (importlib, __import__, exec of a file) are the same limit.
"""

import argparse
import ast
import os
import posixpath
import re
import stat
import subprocess
import sys
from pathlib import Path

# A listed gate file must be a REGULAR file (contract AMENDMENT 1, VERIFY-J1-0-R1 R3):
# `git show :<path>` returns a symlink's LINK TEXT, so a listed path replaced by a symlink
# to an unlisted file screened clean. Only these index modes are accepted in --staged.
REGULAR_INDEX_MODES = frozenset(["100644", "100755"])

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

# ---------- Include edges (AMENDMENT 2) ----------

# Third-party modules a Python gate may import. Closed: a new one is a reviewed change here.
# fubuki_os and lint come from S0-07's pinned fubuki-os checkout, outside this repo.
EXTERNAL_MODULES = frozenset(["fubuki_os", "jsonschema", "lint", "pyflakes", "yaml"])

# Where a first-party import is looked for, besides the importing file's own directory
# and its subdirectories (to this depth).
IMPORT_SEARCH_DEPTH = 2
IMPORT_SEARCH_ROOTS = ("scripts", "src")

# The source edges a gate file may keep: (gate file, the exact target text). Closed: a new
# one is a reviewed change here. Both load no repo code: the first is the untracked bridge
# link file the owner pastes (KEY=VALUE lines), the second the dispatcher tests' fake-bridge seam.
ALLOWED_SOURCES = frozenset([
    ("scripts/pc_lane.sh", '"$ROOT/.pc-bridge.env"'),
    ("scripts/pc_lane.sh", '"$PC_LANE_BRIDGE_FN"'),
])

# A command segment that sources a file, read on the MASKED segment (quoted text replaced).
_SOURCE_RE = re.compile(r"^(?:source|\.)[ \t]+(\S.*)$")
_LEADING_KEYWORD_RE = re.compile(r"^(?:then|do|else|elif|if|while|until|!)[ \t]+")
_HEREDOC_RE = re.compile(r"<<(-?)[ \t]*(['\"]?)([A-Za-z_][A-Za-z0-9_]*)\2")
# In YAML a command follows a list dash and a key: `- run: . x` sources x.
_YAML_KEY_RE = re.compile(r"^(?:-[ \t]+)?(?:[A-Za-z_][A-Za-z0-9_-]*:[ \t]*)?")


def _is_python_gate(entry, content):
    """A listed file is Python when it ends in .py or its first line is a python shebang."""
    if entry.endswith(".py"):
        return True
    first = content.split("\n", 1)[0]
    return first.startswith("#!") and "python" in first


def _command_segments(content, yaml):
    """Yield (lineno, raw, masked) for each command segment of a shell (or YAML) text.

    Quoted text is masked with 'Q' so a word inside a string never starts a command; comments
    and heredoc bodies are skipped. Segments split at newlines, `;`, `&`, `|` and, for shell,
    at `(`, `)`, `{`, `}` (YAML prose uses parentheses freely, so they do not split there)."""
    separators = ";&|\n" if yaml else ";&|(){}\n"
    lines = content.split("\n")
    heredocs = []
    raw, masked = [], []
    quote = None
    seg_line = 1
    lineno = 0
    while lineno < len(lines):
        line = lines[lineno]
        lineno += 1
        if heredocs and quote is None:
            strip_tabs, delim = heredocs[0]
            if (line.lstrip("\t") if strip_tabs else line) == delim:
                heredocs.pop(0)
            continue
        if quote is None and not raw:
            seg_line = lineno
        i = 0
        while i < len(line):
            c = line[i]
            if quote:
                if c == "\\" and quote == '"' and i + 1 < len(line):
                    raw.append(line[i:i + 2])
                    masked.append("QQ")
                    i += 2
                    continue
                raw.append(c)
                masked.append("Q")
                if c == quote:
                    quote = None
                i += 1
                continue
            if c in "'\"":
                quote = c
                raw.append(c)
                masked.append("Q")
                i += 1
                continue
            if c == "\\" and i + 1 < len(line):
                raw.append(line[i:i + 2])
                masked.append("QQ")
                i += 2
                continue
            if c == "$" and line.startswith("${", i):
                depth, j = 0, i + 1
                while j < len(line):
                    if line[j] == "{":
                        depth += 1
                    elif line[j] == "}":
                        depth -= 1
                        if depth == 0:
                            break
                    j += 1
                token = line[i:j + 1]
                raw.append(token)
                masked.append("Q" * len(token))
                i = j + 1
                continue
            if c == "#" and (not masked or masked[-1][-1:] in (" ", "\t")):
                break
            if c == "<" and line.startswith("<<", i) and not line.startswith("<<<", i):
                m = _HEREDOC_RE.match(line, i)
                if m:
                    heredocs.append((m.group(1) == "-", m.group(3)))
            if c in separators:
                yield seg_line, "".join(raw).strip(), "".join(masked).strip()
                raw, masked = [], []
                seg_line = lineno
                i += 1
                continue
            raw.append(c)
            masked.append(c)
            i += 1
        if quote is None:
            yield seg_line, "".join(raw).strip(), "".join(masked).strip()
            raw, masked = [], []
            seg_line = lineno + 1
        else:
            raw.append("\n")
            masked.append("Q")
    if raw:
        yield seg_line, "".join(raw).strip(), "".join(masked).strip()


def _source_errors(entry, content):
    """`gate-file-sources` lines for every command segment that sources a file, unless the
    exact (file, target) pair is in ALLOWED_SOURCES."""
    errors = []
    yaml = entry.endswith((".yml", ".yaml"))
    for lineno, raw, masked in _command_segments(content, yaml):
        cut = _YAML_KEY_RE.match(masked).end() if yaml else 0
        while True:
            m = _LEADING_KEYWORD_RE.match(masked[cut:])
            if not m:
                break
            cut += m.end()
        m = _SOURCE_RE.match(masked[cut:])
        if not m:
            continue
        target = raw[cut + m.start(1):].strip()
        if (entry, target) in ALLOWED_SOURCES:
            continue
        errors.append("gate-file-sources: %s:%d: %s" % (entry, lineno, target))
    return errors


class _Tree:
    """The files an import can resolve to: the git index (--staged) or the filesystem."""

    def __init__(self, root, staged):
        self.root = root
        self.staged = staged
        self.index = None
        self.dirs = None
        self._subdirs = {}
        if staged:
            r = subprocess.run(["git", "ls-files", "-z", "--cached"],
                               capture_output=True, check=True)
            self.index = set(p.decode("utf-8", "replace") for p in r.stdout.split(b"\0") if p)
            self.dirs = set()
            for path in self.index:
                parent = posixpath.dirname(path)
                while parent and parent not in self.dirs:
                    self.dirs.add(parent)
                    parent = posixpath.dirname(parent)

    def isfile(self, rel):
        if self.staged:
            return rel in self.index
        return (self.root / rel).is_file()

    def subdirs(self, rel_dir, depth):
        """Directories below rel_dir, at most `depth` levels down, hidden ones skipped; sorted."""
        key = (rel_dir, depth)
        if key not in self._subdirs:
            self._subdirs[key] = self._scan_subdirs(rel_dir, depth)
        return self._subdirs[key]

    def _scan_subdirs(self, rel_dir, depth):
        prefix = rel_dir + "/" if rel_dir else ""
        found = set()
        if self.staged:
            for d in self.dirs:
                if not d.startswith(prefix) or d == rel_dir:
                    continue
                parts = d[len(prefix):].split("/")
                if len(parts) <= depth and not any(p.startswith(".") for p in parts):
                    found.add(d)
        else:
            def walk(abs_dir, rel, level):
                if level > depth:
                    return
                try:
                    children = sorted(os.scandir(abs_dir), key=lambda e: e.name)
                except OSError:
                    return
                for child in children:
                    if child.name.startswith(".") or not child.is_dir(follow_symlinks=False):
                        continue
                    child_rel = rel + "/" + child.name if rel else child.name
                    found.add(child_rel)
                    walk(child.path, child_rel, level + 1)
            walk(self.root / rel_dir if rel_dir else self.root, rel_dir, 1)
        return sorted(found)


def _package_files(tree, base, parts, names):
    """Files a dotted import reaches from package dir `base`: each package __init__.py, then the
    module file, then any imported name that is itself a submodule. None when the first part is
    not found."""
    files = []
    cur = base
    for i, part in enumerate(parts):
        pkg_init = posixpath.join(cur, part, "__init__.py")
        mod = posixpath.join(cur, part + ".py")
        if tree.isfile(pkg_init):
            cur = posixpath.join(cur, part)
            files.append(pkg_init)
        elif tree.isfile(mod):
            files.append(mod)
            return files
        else:
            return files if i else None
    for name in names:
        sub_mod = posixpath.join(cur, name + ".py")
        sub_pkg = posixpath.join(cur, name, "__init__.py")
        if tree.isfile(sub_mod):
            files.append(sub_mod)
        elif tree.isfile(sub_pkg):
            files.append(sub_pkg)
    return files


def _flagged_by_vocabulary(entry, module, names):
    """Imports the vocabulary scan already reports (exit 3) are not also resolved here."""
    if not entry.endswith(".py"):
        return False
    return (module == "agent_factory.decisions"
            or module.startswith("agent_factory.decisions.")
            or (module == "agent_factory" and "decisions" in names))


def _import_errors(entry, content, tree, listed_set):
    """Completeness lines for the imports of one Python gate file."""
    try:
        parsed = ast.parse(content)
    except SyntaxError:
        return ["gate-file-unparseable: %s" % entry]
    imports = []
    for node in ast.walk(parsed):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.append((node.lineno, 0, alias.name, ()))
        elif isinstance(node, ast.ImportFrom):
            imports.append((node.lineno, node.level, node.module or "",
                            tuple(a.name for a in node.names)))
    importer_dir = posixpath.dirname(entry)
    errors = []
    for lineno, level, module, names in sorted(imports):
        if _flagged_by_vocabulary(entry, module, names):
            continue
        label = ("." * level) + (module or ",".join(names))
        if level:
            base = importer_dir
            for _ in range(level - 1):
                base = posixpath.dirname(base)
            parts = module.split(".") if module else []
            files = _package_files(tree, base, parts, names)
            if not files and not parts and tree.isfile(posixpath.join(base, "__init__.py")):
                files = [posixpath.join(base, "__init__.py")]
            if not files:
                errors.append("gate-file-import-unresolved: %s:%d imports %s" % (entry, lineno, label))
                continue
        else:
            parts = module.split(".")
            search = [importer_dir] + tree.subdirs(importer_dir, IMPORT_SEARCH_DEPTH)
            search += [d for d in IMPORT_SEARCH_ROOTS if d not in search]
            candidates = []
            for d in search:
                reached = _package_files(tree, d, parts[:1], ())
                if reached:
                    candidates.append(d)
            if not candidates:
                top = parts[0]
                if top in sys.stdlib_module_names or top == "__future__" or top in EXTERNAL_MODULES:
                    continue
                errors.append("gate-file-import-unresolved: %s:%d imports %s" % (entry, lineno, module))
                continue
            if len(candidates) > 1:
                where = ",".join(_package_files(tree, d, parts[:1], ())[0] for d in candidates)
                errors.append("gate-file-import-ambiguous: %s:%d imports %s -> %s" % (entry, lineno, module, where))
                continue
            files = _package_files(tree, candidates[0], parts, names)
        for path in files:
            if path not in listed_set:
                errors.append("gate-file-import-unlisted: %s:%d imports %s -> %s" % (entry, lineno, label, path))
    return errors

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

def _parse_allowlist(text):
    """Parse allowlist text, stripping comments and blanks."""
    entries = []
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        entries.append(line)
    return entries


def _load_allowlist(list_path):
    """Load the gate-file allowlist from a file path."""
    return _parse_allowlist(list_path.read_text())


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


def _glob_structural_staged():
    """Walk the three structural patterns from the git index."""
    found = set()
    try:
        r = subprocess.run(
            ["git", "ls-files", "--cached", "--",
             "scripts/hooks/*",
             ".github/workflows/*.yml",
             "proofs/*/check_*.py"],
            capture_output=True, text=True, check=True,
        )
        for line in r.stdout.splitlines():
            line = line.strip()
            if line:
                found.add(line)
    except subprocess.CalledProcessError:
        pass
    return found


def _exists_staged(path):
    """Check whether a path exists in the git index."""
    r = subprocess.run(
        ["git", "cat-file", "-e", ":%s" % path],
        capture_output=True,
    )
    return r.returncode == 0


def _index_mode(path):
    """The index mode of a path (`git ls-files --stage`), or None when it is not staged."""
    r = subprocess.run(
        ["git", "ls-files", "--stage", "--", path],
        capture_output=True, text=True,
    )
    parts = r.stdout.split()
    return parts[0] if r.returncode == 0 and parts else None


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

    # Determine allowlist path and load entries
    if args.list is not None:
        list_path = Path(args.list)
        if not list_path.exists():
            print("gate-file-missing: %s" % list_path, file=sys.stderr)
            return 64
        entries = _load_allowlist(list_path)
    elif args.staged:
        allowlist_content = _read_staged("scripts/gate_files.txt")
        if allowlist_content is None:
            print("gate-file-missing: scripts/gate_files.txt", file=sys.stderr)
            return 64
        entries = _parse_allowlist(allowlist_content)
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
    if args.staged:
        structural_matches = _glob_structural_staged()
    else:
        structural_matches = _glob_structural(root)
    listed_set = set(entries)
    for path in sorted(structural_matches):
        if path not in listed_set:
            completeness_errors.append("gate-file-unlisted: %s" % path)

    # Check listed paths exist AND are regular files (index-backed in staged,
    # lstat-backed otherwise). A symlink is refused by name: reading it would
    # screen its link text (staged) or its target (worktree), not the gate file.
    for entry in entries:
        if args.staged:
            if not _exists_staged(entry):
                completeness_errors.append("gate-file-missing: %s" % entry)
                continue
            mode = _index_mode(entry)
            if mode not in REGULAR_INDEX_MODES:
                completeness_errors.append("gate-file-not-regular: %s mode=%s" % (entry, mode))
        else:
            fp = root / entry
            if fp.is_symlink():
                completeness_errors.append("gate-file-not-regular: %s symlink" % entry)
            elif not fp.exists():
                completeness_errors.append("gate-file-missing: %s" % entry)
            elif not stat.S_ISREG(os.lstat(fp).st_mode):
                completeness_errors.append("gate-file-not-regular: %s not-a-regular-file" % entry)

    if completeness_errors:
        for err in completeness_errors:
            print(err, file=sys.stderr)
        return 4

    contents = {}
    for entry in entries:
        content = _read_staged(entry) if args.staged else _read_file(root, entry)
        if content is None:
            print("gate-file-unreadable: %s" % entry, file=sys.stderr)
            return 4
        contents[entry] = content

    # --- Include edges (AMENDMENT 2): no sourcing; Python imports closed over the list ---
    tree = _Tree(root, args.staged)
    include_errors = []
    for entry in entries:
        if _is_python_gate(entry, contents[entry]):
            include_errors.extend(_import_errors(entry, contents[entry], tree, listed_set))
        else:
            include_errors.extend(_source_errors(entry, contents[entry]))
    if include_errors:
        for err in include_errors:
            print(err, file=sys.stderr)
        return 4

    # --- Scan ---
    violations = []
    scanned = 0
    for entry in entries:
        is_py = entry.endswith(".py")
        content = contents[entry]
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
