#!/usr/bin/env python3
"""slopo_run.py: slopo's own CLI with its whole-tree scan replaced by a walker that skips excluded directories (SLOPO2).

slopo's scanner walks every entry under source_dir (`Path.rglob("*")`) and only then drops the excluded files. The PC
clone holds 18.1 million files under .lanes/ and 1.7 million under .suite/, all excluded by slopo.conf.yaml, so its
first sync took 1,389 s for the 116 files the index needs (tasks/briefs/system1/SLOPO2-brief.md).

  ~/venv-slopo/bin/python scripts/slopo_run.py <slopo args>              e.g. `index`; scripts/slopo_review.sh runs this
  ~/venv-slopo/bin/python scripts/slopo_run.py --compare [--config PATH]  slopo's own scan against the walker (below)

slopo (rafal-qa/slopo, AGPL-3.0-or-later) stays pinned in its own venv and is never copied, vendored or edited. This
runs slopo's own entry point (`slopo.cli:main`, what the venv's bin/slopo runs) in this process and replaces ONE name:
`scan_directory` in `slopo.indexing.sync`, the name `sync_index` calls. The walker is written from the SLOPO2 contract,
not from slopo's code. It yields what slopo's scanner yields, in the same order (the order moves bytes in slopo's
cluster reports: tasks/briefs/system1/SLOPO2-report.md, section 3):
  - the entries `Path.rglob("*")` yields, in the running interpreter's order. Both interpreters list a directory's
    entries when its parent is visited and never enter a symlinked directory; hidden entries are included. 3.12 then
    visits the first child directory first (its `walk()`); 3.13 visits the last first (a stack). Measured against
    CPython's own rglob on both (the SLOPO2 report, section 1);
  - slopo's file decision, made with slopo's own parts: `path.is_file()`, the lower-cased suffix in slopo's
    `supported_extensions()`, and no match in a pathspec built the way slopo's scanner builds it (the "gitignore"
    factory over the config's exclude lines), for the path relative to source_dir, yielded with forward slashes;
  - the one new thing, pruning: a directory is skipped only when every path beneath it is excluded whatever its name.
    pathspec tests a path against each pattern's regex (`regex.search`) and the last pattern that matches decides.
    So directory D is pruned when (1) an excluding pattern covers D: its regex finds a match in "D/" and has no end
    anchor, lookaround or flag, so it matches every longer path too; and (2) no re-including ("!") pattern after the
    last covering one can match below D: its regex is anchored at the start, and its literal prefix neither starts
    with "D/" nor is a prefix of "D/". A pattern this rule cannot read (an unanchored negation such as "!keep.py", a
    flag, an unknown construct) counts as a possible match, so the walker descends. Before a directory is pruned,
    pathspec itself must exclude a witness file of every supported extension beneath it (D/x.py, D/x/x.py, ...). A
    disagreement means the rule misreads this pathspec: the walker then drops all pruning, returns slopo's own scan
    and prints one line to stderr. The walk is collected in full before its first path is returned, so a fallback
    never follows a partial walk.
Seam checks, made before anything is replaced; a failed one runs slopo unchanged and prints one stderr line naming it:
  version      the installed slopo is the version upstream.lock.yaml pins (advisory_tooling.slopo.version);
  scanner      slopo.indexing.sync.scan_directory is slopo.indexing.scanner.scan_directory, sync_index still calls it
               by that name, and its code still names the parts the walker mirrors (SCANNER_NAMES, SCANNER_CONSTS);
               slopo.indexing.scanner still exposes supported_extensions and PathSpec;
  interpreter  Python 3.12 or 3.13, the two whose rglob order was measured.
The launcher's exit code is slopo's own.

--compare runs the walker (first, so it does not ride slopo's warm cache) and then slopo's own scanner over the
config's source_dir and excludes, and prints one line each: the counts, the paths only in slopo's scan and only in the
walker's (count, then at most 20), the order, the wall times, and what the walker read and pruned. Exit 0 only when
both give the same paths in the same order; 1 when they differ or pathspec disagreed with the pruning rule; 2 usage
or a config slopo refuses; 3 a seam check failed (the launcher would not use the walker).
"""
import os
import re
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LOCK = ROOT / "upstream.lock.yaml"
# rglob("*")'s visiting order per interpreter: True = the last child directory first (3.13), False = the first (3.12).
LIFO_BY_INTERPRETER = {(3, 12): False, (3, 13): True}
# The names slopo 0.6.0's scan_directory uses (measured from its code object on 3.12 and 3.13; the SLOPO2 report).
SCANNER_NAMES = {"rglob", "is_file", "suffix", "lower", "relative_to", "match_file", "as_posix", "supported_extensions",
                 "PathSpec", "from_lines"}
SCANNER_CONSTS = {"*", "gitignore"}
LIST_MAX = 20


def seam_problem(version_info=None):
    """None when the walker may replace slopo's scan; otherwise one line naming the check that failed."""
    interp = tuple((version_info or sys.version_info)[:2])
    try:
        import yaml
        from importlib.metadata import version
        pinned = yaml.safe_load(LOCK.read_text(encoding="utf-8"))["advisory_tooling"]["slopo"]["version"]
        installed = version("slopo")
    except Exception as e:
        return "seam check 'version' failed (%s: %s)" % (type(e).__name__, e)
    if installed != pinned:
        return "seam check 'version' failed (installed slopo %s, upstream.lock.yaml pins %s)" % (installed, pinned)
    try:
        import slopo.indexing.scanner as scanner
        import slopo.indexing.sync as sync
    except Exception as e:
        return "seam check 'scanner' failed (%s: %s)" % (type(e).__name__, e)
    fn = getattr(sync, "scan_directory", None)
    code = getattr(fn, "__code__", None)
    sync_code = getattr(getattr(sync, "sync_index", None), "__code__", None)
    consts = {c for c in getattr(code, "co_consts", ()) if isinstance(c, str)}
    failures = [
        (fn is not None and fn is getattr(scanner, "scan_directory", None),
         "slopo.indexing.sync.scan_directory is %r, not slopo.indexing.scanner.scan_directory" % (fn,)),
        (code is not None and getattr(fn, "__module__", None) == "slopo.indexing.scanner"
         and getattr(fn, "__name__", None) == "scan_directory",
         "slopo.indexing.sync.scan_directory is not a function defined in slopo.indexing.scanner"),
        (sync_code is not None and "scan_directory" in sync_code.co_names,
         "slopo.indexing.sync.sync_index no longer calls scan_directory by name"),
        (code is not None and SCANNER_NAMES <= set(code.co_names) and SCANNER_CONSTS <= consts,
         "scan_directory's code no longer names %s" % sorted((SCANNER_NAMES - set(getattr(code, "co_names", ())))
                                                             | (SCANNER_CONSTS - consts))),
        (callable(getattr(scanner, "supported_extensions", None))
         and callable(getattr(getattr(scanner, "PathSpec", None), "from_lines", None)),
         "slopo.indexing.scanner no longer exposes supported_extensions and PathSpec"),
    ]
    for ok, detail in failures:
        if not ok:
            return "seam check 'scanner' failed (%s)" % detail
    if interp not in LIFO_BY_INTERPRETER:
        return ("seam check 'interpreter' failed (Python %d.%d; the walker knows rglob's order on 3.12 and 3.13)"
                % interp)
    return None


# ---------- the walk: Path.rglob("*")'s entries and order, minus pruned directories ----------

def _listing(path, stats):
    """Every entry name of path in scandir order, or None when it cannot be listed (rglob skips such a directory)."""
    if stats is not None:
        stats["listed"] += 1
    try:
        with os.scandir(path) as it:
            return [e.name for e in it]
    except OSError:
        return None


def _child_dirs(path):
    """path's subdirectories in scandir order; a symlink is not one (rglob yields it but never enters it)."""
    out = []
    try:
        with os.scandir(path) as it:
            for e in it:
                try:
                    if e.is_dir(follow_symlinks=False):
                        out.append(e.name)
                except OSError:
                    pass
    except OSError:
        pass
    return out


def rglob_entries(root, prune, lifo, stats=None):
    """The paths `root.rglob("*")` yields, in its order, minus every entry below a directory `prune(rel)` accepts.

    `rel` is the directory's path relative to root with forward slashes. Each directory is listed twice, as rglob
    lists it: once for the entries it yields, once for the subdirectories it visits. lifo: see LIFO_BY_INTERPRETER."""
    names = _listing(root, stats)
    if names is None:
        return
    yield from (root / n for n in names)
    stack = [(root, "")]
    while stack:
        path, rel = stack.pop()
        kids = []
        for name in _child_dirs(path):
            krel = rel + "/" + name if rel else name
            if prune(krel):
                if stats is not None:
                    stats["pruned"].append(krel)
                continue
            kpath = path / name
            yield from (kpath / n for n in _listing(kpath, stats) or ())
            kids.append((kpath, krel))
        stack.extend(kids if lifo else reversed(kids))


# ---------- the pruning rule (see the module docstring) ----------

def _tree(rx):
    """(the regex's parse tree, re's opcode constants), or None when it cannot be read: a flag besides re.UNICODE, or
    a parse this interpreter's re module refuses (re._parser is CPython's own parser; any doubt means no analysis)."""
    if not isinstance(rx, re.Pattern) or not isinstance(rx.pattern, str) or rx.flags != re.UNICODE:
        return None
    try:
        from re import _constants, _parser
        return _parser.parse(rx.pattern, rx.flags), _constants
    except Exception:
        return None


def _monotone(items, c):
    """True when a match found in a string stays a match in every longer string with that prefix: no end anchor, no
    word boundary, no lookaround, no conditional, no scoped flag. Unknown nodes answer False."""
    for op, av in items:
        if op is c.AT:
            if av not in (c.AT_BEGINNING, c.AT_BEGINNING_STRING):
                return False
        elif op in (c.LITERAL, c.NOT_LITERAL, c.ANY, c.IN):
            continue
        elif op in (c.MAX_REPEAT, c.MIN_REPEAT, c.POSSESSIVE_REPEAT):
            if not _monotone(av[2], c):
                return False
        elif op is c.SUBPATTERN:
            if av[1] or av[2] or not _monotone(av[3], c):
                return False
        elif op is c.BRANCH:
            if not all(_monotone(b, c) for b in av[1]):
                return False
        elif op is c.ATOMIC_GROUP:
            if not _monotone(av, c):
                return False
        else:
            return False
    return True


def _anchored_prefix(items, c):
    """The literal text every match must start with, when the regex is anchored at the start (under `search`, an
    unanchored regex can match anywhere); None when it is not."""
    items = list(items)
    i = 0
    while i < len(items) and items[i][0] is c.AT and items[i][1] in (c.AT_BEGINNING, c.AT_BEGINNING_STRING):
        i += 1
    if i == 0:
        return None
    prefix = []
    while i < len(items) and items[i][0] is c.LITERAL:
        prefix.append(chr(items[i][1]))
        i += 1
    return "".join(prefix)


class ModelDisagrees(Exception):
    """pathspec did not exclude a witness below a directory the pruning rule would skip."""


class Pruner:
    """prune(rel) for rglob_entries: True only when every path below rel/ is excluded by `spec`, whatever its name."""

    def __init__(self, spec, extensions):
        self.spec = spec
        self.witnesses = [w for e in sorted(extensions) for w in ("x" + e, "x/x" + e)]
        # per pattern in order: (include, its regex's search when it can cover a directory, else None; for a "!"
        # pattern, the literal prefix every match starts with, else None = it may match anything)
        self.rules = []
        for p in getattr(spec, "patterns", None) or ():
            include = getattr(p, "include", None)
            if include is None:
                continue
            rx = getattr(p, "regex", None)
            parsed = _tree(rx)
            covers = may = None
            if parsed is not None:
                tree, c = parsed
                if include and _monotone(tree, c):
                    covers = rx.search
                if not include:
                    may = _anchored_prefix(tree, c)
            self.rules.append((include, covers, may))

    def __call__(self, rel):
        stem = rel + "/"
        last = None
        for i, (include, covers, _) in enumerate(self.rules):
            if include and covers is not None and covers(stem) is not None:
                last = i
        if last is None:
            return False
        for include, _, prefix in self.rules[last + 1:]:
            if not include and (prefix is None or stem.startswith(prefix) or prefix.startswith(stem)):
                return False
        for w in self.witnesses:
            if not self.spec.match_file(stem + w):
                raise ModelDisagrees(stem + w)
        return True


def walk_paths(root, exclude, stats=None, prune_factory=Pruner):
    """The list slopo's scanner would yield for (root, exclude), from the walker. Raises ModelDisagrees (see Pruner)."""
    import slopo.indexing.scanner as scanner
    extensions = scanner.supported_extensions()
    spec = scanner.PathSpec.from_lines("gitignore", exclude)
    lifo = LIFO_BY_INTERPRETER[sys.version_info[:2]]
    out = []
    for path in rglob_entries(root, prune_factory(spec, extensions), lifo, stats):
        if path.is_file() and path.suffix.lower() in extensions:
            relative = path.relative_to(root)
            if not spec.match_file(relative):
                out.append(relative.as_posix())
    return out


def install():
    """Replace the scan sync_index calls with the walker; slopo's own scan stays the fallback."""
    import slopo.indexing.sync as sync
    original = sync.scan_directory

    def scan_directory(root, exclude):
        try:
            return iter(walk_paths(root, exclude))
        except ModelDisagrees as e:
            print("slopo_run: pathspec keeps %s, which the pruning rule would skip; this walk is slopo's own scan"
                  % e, file=sys.stderr)
            return original(root, exclude)

    sync.scan_directory = scan_directory


# ---------- --compare ----------

def compare(args):
    config = Path("slopo.conf.yaml")
    if args[:1] == ["--config"] and len(args) == 2:
        config = Path(args[1])
    elif args:
        print("usage: slopo_run.py --compare [--config PATH]", file=sys.stderr)
        return 2
    problem = seam_problem()
    if problem:
        print("slopo_run compare: %s" % problem)
        return 3
    import slopo.indexing.scanner as scanner
    from slopo.config import ConfigError, load_config
    try:
        cfg = load_config(config)
    except ConfigError as e:
        print("slopo_run compare: %s" % e, file=sys.stderr)
        return 2
    stats = {"listed": 0, "pruned": []}
    t0 = time.monotonic()
    try:
        walker = walk_paths(cfg.source_dir, cfg.source_dir_exclude, stats)
    except ModelDisagrees as e:
        print("slopo_run compare: pathspec keeps %s, which the pruning rule would skip" % e)
        return 1
    t1 = time.monotonic()
    slopo = list(scanner.scan_directory(cfg.source_dir, cfg.source_dir_exclude))
    t2 = time.monotonic()
    only_slopo = sorted(set(slopo) - set(walker))
    only_walker = sorted(set(walker) - set(slopo))
    common = set(slopo) & set(walker)
    if walker == slopo:
        order = "same"
    elif not only_slopo and not only_walker:
        at = next(i for i, (a, b) in enumerate(zip(slopo, walker)) if a != b)
        order = "differs (first at index %d: slopo %s, walker %s)" % (at, slopo[at], walker[at])
    else:
        same = [p for p in slopo if p in common] == [p for p in walker if p in common]
        order = "of the common paths: %s" % ("same" if same else "differs")
    print("slopo_run compare: count slopo %d walker %d" % (len(slopo), len(walker)))
    print("slopo_run compare: only in slopo %d %s" % (len(only_slopo), only_slopo[:LIST_MAX]))
    print("slopo_run compare: only in walker %d %s" % (len(only_walker), only_walker[:LIST_MAX]))
    print("slopo_run compare: order %s" % order)
    print("slopo_run compare: wall slopo %.2f s walker %.2f s" % (t2 - t1, t1 - t0))
    print("slopo_run compare: walker read %d directories, pruned %d %s" % (
        stats["listed"], len(stats["pruned"]), stats["pruned"][:LIST_MAX]))
    return 0 if walker == slopo else 1


def main(argv):
    if argv[:1] == ["--compare"]:
        return compare(argv[1:])
    problem = seam_problem()
    if problem:
        print("slopo_run: %s; running slopo unchanged" % problem, file=sys.stderr)
    else:
        install()
    from slopo.cli import main as slopo_main
    sys.argv = ["slopo", *argv]
    return slopo_main()


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
