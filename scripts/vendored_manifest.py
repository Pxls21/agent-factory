#!/usr/bin/env python3
"""Generate and check the repository's vendored-tree manifest.

`.claude/` classification compares each file's git blob sha1 with the committed
kit index. Mode differences such as 100644 vs 100755 are ignored for class;
mode 120000 is used only to identify kit symlink paths.

K1-h (task #137) widens the `.claude/` split. Classification order per path:
(a) in the kit index -> `kit-verbatim` / `kit-adapted`; (b) under a declared
set prefix (CLAUDE_DECLARED_SETS) -> `vendored:<set>`; (c) a regular file whose
git blob sha1 equals a committed file under a declared `sandbox-kit/<name>/`
root (match by blob identity only, never by name; a blob under two roots is
refused by name) -> `copy:sandbox-kit/<name>/`; (d) everything else, including
every symlink, stays `first-party` under today's rule.
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import os
from pathlib import Path, PurePosixPath
import re
import subprocess
import sys
from typing import Iterable, NamedTuple

import yaml

MANIFEST_PATH = Path("sandbox-kit/VENDORED-MANIFEST.md")
PROVENANCE_PATH = Path("sandbox-kit/VENDORED-FROM.md")
LOCK_PATH = Path("upstream.lock.yaml")
SBOM_PATH = Path("SBOM.yaml")
CLASSES_PATH = Path("sandbox-kit/VENDORED-CLAUDE-CLASSES.tsv")
KIT_INDEX_PATH = Path("sandbox-kit/dot-claude.aeb3082.index.tsv")
KIT_INDEX_SHA256 = "5d266a2bbd7c84d1cf59ffde52eb0c596bb96ab930982dd74778541425ddf02c"
EXCLUDED_DIRS = frozenset({".git", "__pycache__", "node_modules"})
EXCLUDED_SUFFIXES = (".pyc",)
GENERATED_AT_PREFIX = "Generated at (UTC): "


class VendoredRoot(NamedTuple):
    path: str
    source: str
    provenance_line: int
    pin: str
    pin_source: str
    component: str | None = None


# Frozen from sandbox-kit/VENDORED-FROM.md. Broad table destinations are
# expanded only into the vendored trees named by their provenance lines.
VENDORED_ROOTS = (
    VendoredRoot(
        ".claude/",
        "pxls21/sandbox-kit:dot-claude/",
        11,
        "aeb3082",
        "sandbox-kit/VENDORED-FROM.md:3-5",
    ),
    VendoredRoot(
        "sandbox-kit/aleph/",
        "https://github.com/Hmbown/aleph",
        17,
        "aeb3082",
        "sandbox-kit/VENDORED-FROM.md:3-5 (kit snapshot)",
    ),
    VendoredRoot(
        "sandbox-kit/codebase-memory-mcp/",
        "github.com/bosun-ai/codebase-memory-mcp",
        17,
        "aeb3082",
        "sandbox-kit/VENDORED-FROM.md:3-5 (kit snapshot)",
    ),
    VendoredRoot(
        "sandbox-kit/council-of-high-intelligence/",
        "https://github.com/0xNyk/council-of-high-intelligence",
        17,
        "aeb3082",
        "sandbox-kit/VENDORED-FROM.md:3-5 (kit snapshot)",
    ),
    VendoredRoot(
        "sandbox-kit/llm-wiki-compiler/",
        "https://github.com/ussumant/llm-wiki-compiler",
        17,
        "0f734fd3fba7dbc6a3b58efb4fb5fbaf7ce7565d",
        "sandbox-kit/llm-wiki-compiler/README.md:3-5",
    ),
    VendoredRoot(
        "sandbox-kit/output-styles/",
        "https://github.com/alexgreensh/attention-span",
        17,
        "unpinned (vendored copy)",
        "sandbox-kit/output-styles/PROVENANCE.md:3-5",
    ),
    VendoredRoot(
        "sandbox-kit/reference-scripts/",
        "pxls21/sandbox-kit:scripts/",
        15,
        "aeb3082",
        "sandbox-kit/VENDORED-FROM.md:3-5",
    ),
    VendoredRoot(
        "sandbox-kit/honey-for-devs/",
        "https://github.com/Green-PT/honey-for-devs",
        21,
        "unpinned (vendored copy)",
        "sandbox-kit/VENDORED-FROM.md:21-23",
    ),
    VendoredRoot(
        "sandbox-kit/docs/",
        "pxls21/sandbox-kit:docs/",
        18,
        "aeb3082",
        "sandbox-kit/VENDORED-FROM.md:18",
    ),
    VendoredRoot(
        "vendor/jev-pruner/",
        "https://github.com/tamaratran/jev-pruner",
        57,
        "47d017c34eab7690b95f075ce6f4839247c5dc0a",
        "upstream.lock.yaml:advisory_tooling.jev-pruner",
    ),
)

# CLOSED classification of every top-level entry under `sandbox-kit/`
# (K1-g / VERIFY-K1 F1). Classes: `vendored-root` (a VENDORED_ROOTS tree),
# `kit-portable-files` (regular files taken from the kit snapshot, carried by
# ONE digest row), `first-party` (this repository's own files; no digest for
# the manifest itself, the kit index is verified by its own sha256).
# `--check` and `--write` refuse, before any digest work, an entry under
# `sandbox-kit/` that is not here and any entry here that is missing from the
# tree.
SANDBOX_KIT_ENTRIES: dict[str, str] = {
    "aleph": "vendored-root",
    "codebase-memory-mcp": "vendored-root",
    "council-of-high-intelligence": "vendored-root",
    "docs": "vendored-root",
    "honey-for-devs": "vendored-root",
    "llm-wiki-compiler": "vendored-root",
    "output-styles": "vendored-root",
    "reference-scripts": "vendored-root",
    "BEHAVIORAL-GUIDELINES.md": "kit-portable-files",
    "CLAUDE.template.md": "kit-portable-files",
    "EXAMPLE-RESEARCH-PROMPT-EXPLORATORY.md": "kit-portable-files",
    "EXAMPLE-RESEARCH-PROMPT-SETTLED-SPEC.md": "kit-portable-files",
    "GITNEXUS-CLI.md": "kit-portable-files",
    "OPERATING-GUIDE.md": "kit-portable-files",
    "OUROBOROS-SETUP.md": "kit-portable-files",
    "README.md": "kit-portable-files",
    "REFERENCE-setup-agent-distiller.sh": "kit-portable-files",
    "RESEARCH-PROMPT-GUIDE.md": "kit-portable-files",
    "TELEMETRY-REFERENCE.md": "kit-portable-files",
    "example.mcp.json": "kit-portable-files",
    "VENDORED-FROM.md": "first-party",
    "VENDORED-MANIFEST.md": "first-party",
    "VENDORED-CLAUDE-CLASSES.tsv": "first-party",
    "dot-claude.aeb3082.index.tsv": "first-party",
}
KIT_PORTABLE_ROW = "sandbox-kit/ (kit-portable files)"


class DeclaredSet(NamedTuple):
    """A vendored set installed under `.claude/` (K1-h, task #137).

    `prefix` is relative to `.claude/`. Every field is verified against the
    provenance file at generation: the file must exist and contain both the
    `owner/repo` source and the pin string, else `manifest: provenance
    mismatch: <set> <field>` (non-zero exit, nothing written). The row's pin
    source cell names `<provenance file>:<line>` of the line carrying the pin
    (computed, never typed). The license SHA-256 cell is the file's sha256
    when `license_file` is present and `none found` otherwise (never inferred
    from another source).
    """

    name: str
    prefix: str
    provenance: str
    source: str
    pin: str
    license: str
    license_file: str | None = None


# CLOSED table (one entry per set, K1-h). honey is NOT a set: its `.claude/`
# files are byte-identical copies of `sandbox-kit/honey-for-devs/`, which
# already has its own row; they are classified by the copy rule. The three
# `PROVENANCE-*.md` files document the sets but are not set members: they
# stay `first-party` (measured at the PIN: no set-prefixed path is a kit-index
# path and no set-prefixed path is a blob-copy of a kit root).
CLAUDE_DECLARED_SETS = (
    DeclaredSet(
        name="aegis",
        prefix="skills/aegis-",
        provenance="skills/PROVENANCE-AEGIS.md",
        source="https://github.com/GanyuanRan/Aegis",
        pin="60321ed",
        license="MIT (declared)",
        license_file=None,
    ),
    DeclaredSet(
        name="prism",
        prefix="skills/prism-",
        provenance="skills/PROVENANCE-PRISM.md",
        source="https://github.com/Cranot/super-hermes",
        pin="ffe2d10042041dcc23325f013e8b7e607e069952",
        license="MIT (declared)",
        license_file=None,
    ),
    DeclaredSet(
        name="typesafe",
        prefix="skills/typesafe-ai/",
        provenance="skills/PROVENANCE-TYPESAFE.md",
        source="https://github.com/typesafe-ai/skills",
        pin="65a39f3",
        license="MIT (LICENSE)",
        license_file="skills/typesafe-ai/LICENSE",
    ),
)

# Path prefixes under `.claude/`, in classification order (first match wins).
CLAUDE_SET_PREFIXES: tuple[tuple[str, str], ...] = tuple(
    (set_.prefix, f"vendored:{set_.name}") for set_ in CLAUDE_DECLARED_SETS
)


class ManifestError(RuntimeError):
    """A named, fail-closed manifest validation error."""


class TreeRecord(NamedTuple):
    path: str
    source: str
    pin: str
    pin_source: str
    license: str
    license_file: str | None
    license_sha256: str | None
    regular_file_count: int
    symlink_count: int
    tree_sha256: str


class ManifestData(NamedTuple):
    records: list[TreeRecord]
    claude_classes: dict[str, str]
    kit_only_count: int


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def normalize_repo(value: str) -> str:
    value = value.strip().removesuffix(".git").rstrip("/")
    value = re.sub(r"^(?:https?://)?(?:www\.)?github\.com/", "github.com/", value)
    return value.lower()


# K170 (D-1/D-2): the lock and SBOM are parsed with PyYAML's safe loader, through a
# per-call loader subclass that refuses a duplicate mapping key at any depth, instead
# of the old line regex that silently skipped every line it did not recognise (AF-AP-25).
#
# R1: characters both YAML and `str.splitlines()` treat as a line break (U+0085,
# U+2028, U+2029, carriage return). Built with chr() so none is ever typed in source;
# a file holding one is refused before any line is numbered, because any later line
# number would disagree with an editor's and with git's (AF-AP-132). The read is RAW
# bytes (`read_bytes().decode`), never `Path.read_text`: universal-newline translation
# in `read_text` silently strips a carriage return, so a CRLF file would slip past the
# R1 scan and reach the YAML parser as a different document than an editor or git sees.
_LINE_SEPARATORS = (chr(0x0085), chr(0x2028), chr(0x2029), chr(0x000D))


def _refuse_line_separators(text: str, path: Path) -> None:
    """R1: refuse a file holding U+0085 / U+2028 / U+2029 / a carriage return, naming the
    file first, then the 1-based line (counted by newline characters, never
    `str.splitlines()`, AF-AP-132), then the character itself by `repr`. Shared by the
    YAML and provenance loaders so one scan answers "which line holds a break both YAML
    and `splitlines` would split"."""
    for separator in _LINE_SEPARATORS:
        index = text.find(separator)
        if index >= 0:
            line = text.count("\n", 0, index) + 1
            raise ManifestError(f"{path.as_posix()}: line {line} holds {separator!r}")


def load_manifest_yaml(path: Path, label: str) -> object:
    """Read one manifest input and parse it with the fail-closed loader (D-1/D-2).

    A missing file, a separator character (R1), a YAML syntax error and a duplicate key
    (R2) all become a `ManifestError` naming the file and the line, never a raw
    `yaml.YAMLError` or a traceback. The separator line is counted by newline characters
    so it agrees with an editor's and git's (R1, AF-AP-132); a YAML syntax error carries
    the line from the YAML mark (R2); a duplicate key carries the second key's line by
    YAML's own mark. The read is raw bytes so a carriage return is seen, not translated
    away by universal-newline mode.
    """
    if not path.is_file():
        raise ManifestError(f"{label} missing: {path.as_posix()}")
    text = path.read_bytes().decode("utf-8")
    _refuse_line_separators(text, path)
    loader = type("K170 manifest loader", (yaml.SafeLoader,), {})

    def mapping(loader_, node, deep=False):
        loader_.flatten_mapping(node)
        seen = set()
        for key_node, _value_node in node.value:
            key = loader_.construct_object(key_node, deep=deep)
            if key in seen:
                raise ManifestError(
                    f"{label} duplicate key {key!r} at line {key_node.start_mark.line + 1} ({path.as_posix()})"
                )
            seen.add(key)
        return yaml.SafeLoader.construct_mapping(loader_, node, deep)

    loader.add_constructor(yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, mapping)
    try:
        return yaml.load(text, Loader=loader)
    except ManifestError:
        raise
    except yaml.YAMLError as error:
        mark = error.problem_mark
        line = mark.line + 1 if mark is not None else None
        if line is None:
            raise ManifestError(f"{label} parse failure in {path.as_posix()}") from None
        raise ManifestError(f"{label} parse failure at line {line} ({path.as_posix()})") from None


def _clean_str(value: object, where: str) -> str:
    """R5: a repository or pin must be a non-empty string carrying no whitespace
    (YAML reads a long run of digits as an int, an empty value as None; a stray space
    would glue into the value). Anything else is refused by `where`."""
    if not isinstance(value, str) or not value or any(char.isspace() for char in value):
        raise ManifestError(f"{where}: the value {value!r} is not a non-empty whitespace-free string")
    return value


def excluded(relative: PurePosixPath) -> bool:
    return any(part in EXCLUDED_DIRS for part in relative.parts) or relative.name.endswith(
        EXCLUDED_SUFFIXES
    )


def walk_tree(root: Path, repo_root: Path | None) -> list[tuple[str, bytes]]:
    if root.is_symlink():
        raise ManifestError(
            f"declared root is a symlink: {root.as_posix()} -> {os.readlink(root)}"
        )
    if not root.is_dir():
        raise ManifestError(f"vendored root missing or not a directory: {root.as_posix()}")

    # The declared root's own type is part of the digest domain. Child records
    # retain the existing regular-file / `symlink:<target>` encoding.
    records: list[tuple[str, bytes]] = [("", b"dir")]
    for directory, dirnames, filenames in os.walk(root, topdown=True, followlinks=False):
        directory_path = Path(directory)
        kept_dirs: list[str] = []
        for name in sorted(dirnames):
            path = directory_path / name
            relative = PurePosixPath(path.relative_to(root).as_posix())
            if excluded(relative):
                continue
            if path.is_symlink():
                records.append(symlink_record(root, path, repo_root))
            else:
                kept_dirs.append(name)
        dirnames[:] = kept_dirs

        for name in sorted(filenames):
            path = directory_path / name
            relative = PurePosixPath(path.relative_to(root).as_posix())
            if excluded(relative):
                continue
            if path.is_symlink():
                records.append(symlink_record(root, path, repo_root))
            elif path.is_file():
                records.append((relative.as_posix(), sha256_bytes(path.read_bytes()).encode()))

    return sorted(records, key=lambda record: record[0].encode("utf-8"))


def repo_root_of(root: Path) -> Path | None:
    """The repository root (`git rev-parse --show-toplevel`), resolved once per run."""
    try:
        out = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            cwd=root,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            text=True,
        ).stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        return None
    return Path(out).resolve() if out else None


def symlink_record(root: Path, path: Path, repo_root: Path | None) -> tuple[str, bytes]:
    relative = path.relative_to(root).as_posix()
    target = os.readlink(path)
    # A link is digested by its TARGET STRING only. It is allowed when its resolved
    # target lies inside the repository root (AMENDMENT 1); outside it, or dangling,
    # it is refused with the link and its target named.
    if repo_root is None:
        raise ManifestError(
            f"symlink refused in {root.as_posix()}: {relative} -> {target}: "
            "repository root unknown (git rev-parse --show-toplevel failed)"
        )
    resolved = (path.parent / target).resolve(strict=False)
    try:
        resolved.relative_to(repo_root)
    except ValueError:
        raise ManifestError(
            f"escaping symlink refused in {root.as_posix()}: {relative} -> {target} "
            f"(resolved target {resolved.as_posix()} lies outside the repository root "
            f"{repo_root.as_posix()})"
        ) from None
    if not resolved.exists():
        raise ManifestError(
            f"dangling symlink refused in {root.as_posix()}: {relative} -> {target} "
            f"(resolved target {resolved.as_posix()} does not exist)"
        )
    return relative, f"symlink:{target}".encode("utf-8")


def digest_records(records: Iterable[tuple[str, bytes]]) -> str:
    digest = hashlib.sha256()
    for relative, payload in records:
        digest.update(relative.encode("utf-8"))
        digest.update(b"\0")
        digest.update(payload)
        digest.update(b"\n")
    return digest.hexdigest()


def record_counts(records: list[tuple[str, bytes]]) -> tuple[int, int]:
    payloads = [(path, payload) for path, payload in records if path]
    symlink_count = sum(payload.startswith(b"symlink:") for _, payload in payloads)
    return len(payloads) - symlink_count, symlink_count


def validate_sandbox_kit_entries(root: Path) -> None:
    kit_root = root / "sandbox-kit"
    if not kit_root.is_dir():
        raise ManifestError("sandbox-kit/ missing")
    present = {path.name for path in kit_root.iterdir()}
    missing = sorted(set(SANDBOX_KIT_ENTRIES) - present)
    if missing:
        raise ManifestError(f"declared sandbox-kit entry missing: {missing[0]}")
    for name, klass in sorted(SANDBOX_KIT_ENTRIES.items()):
        path = kit_root / name
        if klass == "vendored-root" and path.is_symlink():
            raise ManifestError(
                f"declared root is a symlink: {path.as_posix()} -> {os.readlink(path)}"
            )
    unknown = sorted(present - set(SANDBOX_KIT_ENTRIES))
    if unknown:
        raise ManifestError(f"undeclared entry under sandbox-kit/: {unknown[0]}")


def kit_portable_records(root: Path, repo_root: Path | None) -> list[tuple[str, bytes]]:
    kit_root = root / "sandbox-kit"
    records: list[tuple[str, bytes]] = [("", b"dir")]
    for name, klass in sorted(SANDBOX_KIT_ENTRIES.items()):
        if klass != "kit-portable-files":
            continue
        path = kit_root / name
        if path.is_symlink():
            records.append(symlink_record(kit_root, path, repo_root))
        elif path.is_file():
            records.append((name, sha256_bytes(path.read_bytes()).encode()))
        else:
            raise ManifestError(f"kit-portable entry is not a file: sandbox-kit/{name}")
    return records


def git_blob_sha1(data: bytes) -> str:
    return hashlib.sha1(b"blob %d\0" % len(data) + data).hexdigest()


def load_kit_index(root: Path) -> dict[str, tuple[str, str]]:
    index_path = root / KIT_INDEX_PATH
    if not index_path.is_file():
        raise ManifestError("kit index missing")
    data = index_path.read_bytes()

    entries: dict[str, tuple[str, str]] = {}
    lines = data.decode("utf-8").splitlines()
    for line_number, line in enumerate(lines[1:], start=2):
        cells = line.split("\t")
        if len(cells) != 3 or not cells[0] or not re.fullmatch(r"[0-9a-f]{40}", cells[2]):
            raise ManifestError(
                f"kit index parse failure at line {line_number}: expected path<TAB>mode<TAB>git-blob-sha1"
            )
        path, mode, sha1 = cells
        if path in entries:
            raise ManifestError(f"kit index parse failure at line {line_number}: duplicate path {path}")
        entries[path] = (mode, sha1)
    if sha256_bytes(data) != KIT_INDEX_SHA256:
        raise ManifestError("kit index sha256 mismatch")
    return entries


def build_kit_blob_index(root: Path) -> dict[str, list[str]]:
    """The committed git blob sha1 -> paths map over every declared
    `sandbox-kit/<name>/` root (the `copy:` rule's source side; the root
    digest rows already hold each root's files, but the copy rule needs the
    blob identity, not the digest)."""
    index: dict[str, list[str]] = {}
    for item in VENDORED_ROOTS:
        if not item.path.startswith("sandbox-kit/"):
            continue
        item_root = root / item.path
        for _directory, _dirnames, filenames in os.walk(
            item_root, topdown=True, followlinks=False
        ):
            for name in sorted(filenames):
                path = Path(_directory) / name
                if not path.is_file() or path.is_symlink():
                    continue
                blob = git_blob_sha1(path.read_bytes())
                index.setdefault(blob, []).append(
                    item.path + path.relative_to(item_root).as_posix()
                )
    return index


def set_class_for(relative: str) -> str | None:
    for prefix, klass in CLAUDE_SET_PREFIXES:
        if relative.startswith(prefix):
            return klass
    return None


def set_row_license(root: Path, item: DeclaredSet) -> tuple[str, str | None, str | None]:
    if item.license_file is None:
        return item.license, None, None
    path = root / ".claude" / item.license_file
    data = path.read_bytes()
    return item.license, item.license_file, sha256_bytes(data)


def verify_declared_sets(root: Path) -> dict[str, int]:
    """K1-h: verify every declared set against its provenance file, BEFORE any
    digest work (the fail-closed order: nothing is written on a mismatch).
    The file must exist and contain the `owner/repo` source and the pin
    string; the returned map carries each set's pin line number (computed,
    never typed) for the pin-source cell."""
    line_numbers: dict[str, int] = {}
    for item in CLAUDE_DECLARED_SETS:
        path = root / ".claude" / item.provenance
        if not path.is_file():
            raise ManifestError(f"manifest: provenance mismatch: {item.name} provenance file")
        text = path.read_text(encoding="utf-8")
        # The source's `owner/repo` (the URL's last two path segments).
        segments = item.source.rstrip("/").rsplit("/")
        if len(segments) < 2:
            raise ManifestError(f"manifest: provenance mismatch: {item.name} source")
        owner_repo = "/".join(segments[-2:])
        if owner_repo not in text:
            raise ManifestError(f"manifest: provenance mismatch: {item.name} source")
        pin_line = None
        for line_number, line in enumerate(text.splitlines(), start=1):
            if item.pin in line:
                pin_line = line_number
                break
        if pin_line is None:
            raise ManifestError(f"manifest: provenance mismatch: {item.name} pin")
        line_numbers[item.name] = pin_line
    return line_numbers


def claude_records(
    root: Path, repo_root: Path | None, index: dict[str, tuple[str, str]]
) -> tuple[dict[str, list[tuple[str, bytes]]], dict[str, str], int]:
    claude_root = root / ".claude"
    if claude_root.is_symlink():
        raise ManifestError(
            f"declared root is a symlink: {claude_root.as_posix()} -> {os.readlink(claude_root)}"
        )
    if not claude_root.is_dir():
        raise ManifestError(f"vendored root missing or not a directory: {claude_root.as_posix()}")

    # The copy rule runs before the per-file walk: one blob index over the
    # declared roots answers every (c) classification in the pass.
    kit_blobs = build_kit_blob_index(root)
    by_class: dict[str, list[tuple[str, bytes]]] = {
        "kit-verbatim": [],
        "kit-adapted": [],
        "first-party": [],
    }
    classes: dict[str, str] = {}
    for directory, dirnames, filenames in os.walk(claude_root, topdown=True, followlinks=False):
        directory_path = Path(directory)
        kept_dirs: list[str] = []
        for name in sorted(dirnames):
            path = directory_path / name
            relative = PurePosixPath(path.relative_to(claude_root).as_posix())
            if excluded(relative):
                continue
            if path.is_symlink():
                rel = relative.as_posix()
                record = symlink_record(claude_root, path, repo_root)
                klass = "kit-verbatim" if index.get(rel, ("", ""))[0] == "120000" else "first-party"
                classes[rel] = klass
                by_class.setdefault(klass, []).append(record)
            else:
                kept_dirs.append(name)
        dirnames[:] = kept_dirs

        for name in sorted(filenames):
            path = directory_path / name
            relative = PurePosixPath(path.relative_to(claude_root).as_posix())
            if excluded(relative):
                continue
            rel = relative.as_posix()
            if path.is_symlink():
                record = symlink_record(claude_root, path, repo_root)
                klass = "kit-verbatim" if index.get(rel, ("", ""))[0] == "120000" else "first-party"
            else:
                data = path.read_bytes()
                record = (rel, sha256_bytes(data).encode())
                if rel in index:
                    klass = "kit-verbatim" if index[rel][1] == git_blob_sha1(data) else "kit-adapted"
                elif (set_class := set_class_for(rel)) is not None:
                    klass = set_class
                else:
                    # (c) copy rule: blob identity only, never by name. A blob
                    # found under two declared roots is refused by name. The
                    # kit path is `sandbox-kit/<name>/<file…>`: the root is its
                    # first two segments.
                    matched = [
                        "/".join(kit_path.split("/")[:2]) + "/"
                        for kit_path in kit_blobs.get(git_blob_sha1(data), [])
                    ]
                    matched = sorted(set(matched))
                    if len(matched) > 1:
                        raise ManifestError(
                            f"manifest: .claude copy ambiguous: {rel} matches "
                            + ", ".join(matched)
                        )
                    klass = (
                        f"copy:{matched[0]}" if matched else "first-party"
                    )
            classes[rel] = klass
            by_class.setdefault(klass, []).append(record)

    for klass in by_class:
        by_class[klass] = sorted(by_class[klass], key=lambda record: record[0].encode("utf-8"))
    kit_only_count = len(set(index) - set(classes))
    return by_class, classes, kit_only_count


def render_classes(classes: dict[str, str]) -> str:
    rows = ["path\tclass"]
    rows.extend(f"{path}\t{classes[path]}" for path in sorted(classes))
    return "\n".join(rows) + "\n"


def parse_classes(text: str) -> dict[str, str]:
    lines = text.splitlines()
    if not lines or lines[0] != "path\tclass":
        raise ManifestError(".claude class file parse failure at line 1")
    classes: dict[str, str] = {}
    for line_number, line in enumerate(lines[1:], start=2):
        cells = line.split("\t")
        klass = cells[1] if len(cells) == 2 else ""
        if klass not in {"kit-verbatim", "kit-adapted", "first-party"} and not (
            klass.startswith("copy:") or klass.startswith("vendored:")
        ):
            raise ManifestError(f".claude class file parse failure at line {line_number}")
        classes[cells[0]] = klass
    return classes


def class_difference(committed: str, generated: str) -> str:
    committed_classes = parse_classes(committed)
    generated_classes = parse_classes(generated)
    for path in sorted(set(committed_classes) | set(generated_classes)):
        committed_class = committed_classes.get(path, "<missing>")
        generated_class = generated_classes.get(path, "<missing>")
        if committed_class != generated_class:
            return f"{path}: committed={committed_class} generated={generated_class}"
    return "byte length differs"


def detect_spdx(text: str) -> str:
    normalized = " ".join(text.lower().split())
    if re.search(r"spdx-license-identifier\s*:\s*mit\b", normalized):
        return "MIT"
    if re.search(r"spdx-license-identifier\s*:\s*apache-2\.0\b", normalized):
        return "Apache-2.0"
    if re.search(r"spdx-license-identifier\s*:\s*agpl-3\.0(?:-only)?\b", normalized):
        return "AGPL-3.0"
    if "creative commons zero v1.0 universal" in normalized:
        return "CC0-1.0"
    if "gnu affero general public license" in normalized:
        return "AGPL-3.0"
    if "apache license" in normalized and "version 2.0" in normalized:
        return "Apache-2.0"
    if "mit license" in normalized and "permission is hereby granted" in normalized:
        return "MIT"
    return "unknown"


def license_for(root: Path, records: list[tuple[str, bytes]]) -> tuple[str, str | None, str | None]:
    candidates = [
        relative
        for relative, _ in records
        if len(PurePosixPath(relative).parts) == 1
        and re.fullmatch(r"(?i)(?:license|copying|notice)(?:[._-].*)?", relative)
    ]
    if not candidates:
        return "none found", None, None

    for relative in sorted(candidates, key=lambda value: (not value.lower().startswith("license"), value)):
        path = root / relative
        data = path.read_bytes()
        identifier = detect_spdx(data.decode("utf-8", errors="replace"))
        if identifier != "unknown":
            return identifier, relative, sha256_bytes(data)

    relative = sorted(candidates)[0]
    data = (root / relative).read_bytes()
    return "unknown", relative, sha256_bytes(data)


def markdown_cells(line: str) -> list[str]:
    return [cell.strip() for cell in line.strip().strip("|").split("|")]


def clean_code(cell: str) -> str:
    return cell.strip().strip("`").strip()


def parse_provenance(path: Path) -> tuple[set[str], dict[str, int]]:
    if not path.is_file():
        raise ManifestError(f"provenance file missing: {path.as_posix()}")
    text = path.read_bytes().decode("utf-8")
    _refuse_line_separators(text, path)
    lines = text.split("\n")
    header = next(
        (index for index, line in enumerate(lines) if markdown_cells(line)[:2] == ["Source (pxls21/sandbox-kit)", "Here"]),
        None,
    )
    if header is None:
        raise ManifestError("provenance table parse failure: Source/Here header not found")
    if header + 1 >= len(lines) or not re.fullmatch(r"\|?[ :|-]+\|[ :|-]+\|[ :|-]+\|?", lines[header + 1]):
        raise ManifestError("provenance table parse failure: malformed separator row")

    destinations: set[str] = set()
    roots: dict[str, int] = {}
    row_count = 0
    for offset, line in enumerate(lines[header + 2 :], start=header + 3):
        if not line.startswith("|"):
            if line.strip() == "":
                break  # R8: the table ends at the first blank line
            raise ManifestError(f"provenance table parse failure at line {offset}: expected a row")
        cells = markdown_cells(line)
        if len(cells) != 3 or not all(cells[:2]):
            raise ManifestError(f"provenance table parse failure at line {offset}: expected 3 cells")
        source, here, notes = cells
        here = clean_code(here)
        destinations.add(here)
        row_count += 1

        if here == ".claude/":
            roots[here] = offset
        elif here == "sandbox-kit/reference-scripts/setup-trading-system.sh":
            roots["sandbox-kit/reference-scripts/"] = offset
        elif here == "sandbox-kit/reference-scripts/":
            roots[here] = offset
        elif here == "sandbox-kit/":
            source_notes = f"{source} {notes}"
            named = set(
                re.findall(
                    r"`((?:aleph|codebase-memory-mcp|council-of-high-intelligence|llm-wiki-compiler)/)`",
                    source_notes,
                )
            )
            expected = {
                "aleph/",
                "codebase-memory-mcp/",
                "council-of-high-intelligence/",
                "llm-wiki-compiler/",
            }
            if named != expected or "output-styles" not in source_notes:
                found = sorted(
                    (*named, *(["output-styles/"] if "output-styles" in source_notes else []))
                )
                expected_all = sorted((*expected, "output-styles/"))
                raise ManifestError(
                    "provenance table parse failure at line "
                    f"{offset}: sandbox-kit vendored roots were {found}, expected {expected_all}"
                )
            named.add("output-styles/")
            roots.update({f"sandbox-kit/{name}": offset for name in named})
        elif here == "sandbox-kit/docs/":
            roots[here] = offset
        elif here == KIT_PORTABLE_ROW:
            pass
        elif here not in {".mcp.json", "scripts/"} and not here.startswith("sandbox-kit/"):
            raise ManifestError(f"provenance table parse failure at line {offset}: unknown Here value {here}")

    if row_count == 0:
        raise ManifestError("provenance table parse failure: no rows")

    honey_line = next(
        (
            index
            for index, line in enumerate(lines, start=1)
            if line.startswith("**Added ") and "`sandbox-kit/honey-for-devs/`" in line
        ),
        None,
    )
    if honey_line is None:
        raise ManifestError("provenance parse failure: sandbox-kit/honey-for-devs/ declaration missing")
    roots["sandbox-kit/honey-for-devs/"] = honey_line
    # A tree vendored outside the kit snapshot, under `vendor/`, is declared the honey way:
    # its own `**Added ...` line names the backticked `vendor/<name>/` root (P1, task #231).
    for index, line in enumerate(lines, start=1):
        if line.startswith("**Added "):
            for name in re.findall(r"`(vendor/[A-Za-z0-9._-]+/)`", line):
                if name in roots:
                    raise ManifestError(f"provenance parse failure: {name} declared twice")
                roots[name] = index
    return destinations, roots


def validate_declared_roots(root: Path) -> None:
    _, provenance_roots = parse_provenance(root / PROVENANCE_PATH)
    declared = {item.path: item.provenance_line for item in VENDORED_ROOTS}
    missing = sorted(set(provenance_roots) - set(declared))
    extra = sorted(set(declared) - set(provenance_roots))
    wrong_lines = sorted(
        path
        for path in set(declared) & set(provenance_roots)
        if declared[path] != provenance_roots[path]
    )
    if missing or extra or wrong_lines:
        parts = []
        if missing:
            parts.append(f"roots missing from declared list: {', '.join(missing)}")
        if extra:
            parts.append(f"declared roots absent from provenance: {', '.join(extra)}")
        if wrong_lines:
            parts.append(f"declared provenance lines drifted: {', '.join(wrong_lines)}")
        raise ManifestError("vendored-root declaration mismatch: " + "; ".join(parts))


def parse_lock(path: Path) -> dict[str, tuple[str, str]]:
    """R3-R6. Parse the lock with the fail-closed loader (D-1) and extract the
    `result[normalize_repo(repository)] = (pin, section.component)` agreement map.

    A top-level scalar carries no pin and is ignored (R3); a section must be a mapping
    and a component inside it must be a mapping (R3); a component with a `repository`
    must carry a pin (R4); a repository and its chosen pin must be non-empty
    whitespace-free strings (R5); two components whose repositories normalise to one
    key are refused by both `section.component` keys (R6). A component without a
    `repository` stays outside the agreement check, as before. Pin precedence:
    `commit`, `binary_sha256`, `asset_sha256`.
    """
    doc = load_manifest_yaml(path, "upstream lock")
    if not isinstance(doc, dict):
        raise ManifestError("upstream lock: the top level is not a mapping")
    result: dict[str, tuple[str, str]] = {}
    for section, body in doc.items():
        if not isinstance(body, dict):
            if body is None or isinstance(body, (str, int, float, bool)):
                continue  # R3: a top-level scalar carries no pin
            if isinstance(body, (list, tuple)):
                raise ManifestError(f"upstream lock: section {section!r} is a list, not a mapping")
            raise ManifestError(f"upstream lock: section {section!r} is not a mapping")
        for component, values in body.items():
            where = f"{section}.{component}"
            if not isinstance(values, dict):
                raise ManifestError(f"upstream lock: {where} is not a mapping")
            if "repository" not in values:
                continue  # R4: no repository -> outside the agreement check
            key = normalize_repo(_clean_str(values["repository"], where))
            if key in result:
                raise ManifestError(f"upstream lock: repository {key} is pinned by both {result[key][1]} and {where}")
            pins = [pin for pin in ("commit", "binary_sha256", "asset_sha256") if pin in values]
            if not pins:
                raise ManifestError(
                    f"upstream lock: {where} has a repository but no pin (commit, binary_sha256, asset_sha256)"
                )
            result[key] = (_clean_str(values[pins[0]], where), where)
    return result


def parse_sbom(path: Path) -> dict[str, tuple[str, str]]:
    """R7. Parse the SBOM with the fail-closed loader (D-1) and extract the
    `result[normalize_repo(repository)] = (pin, name)` agreement map.

    The top level must be a mapping whose `components` value is a list; each item must
    be a mapping with a non-empty string `name` and `repository`, and a pin (`commit` or
    `digest`) that is a non-empty whitespace-free string (R5). A non-mapping item, a
    missing name, a missing repository, a missing pin, or two items whose repositories
    normalise to one key are refused, naming the item's `name` (or its 1-based position
    when it has none) (R7). Pin precedence: `commit`, `digest`.
    """
    doc = load_manifest_yaml(path, "SBOM")
    if not isinstance(doc, dict):
        raise ManifestError("SBOM: the top level is not a mapping")
    components = doc.get("components")
    if not isinstance(components, list):
        raise ManifestError("SBOM: the 'components' value is not a list")
    result: dict[str, tuple[str, str]] = {}
    for position, item in enumerate(components, start=1):
        if not isinstance(item, dict):
            raise ManifestError(f"SBOM: component #{position} is not a mapping")
        name = item.get("name")
        label = name if isinstance(name, str) and name else f"#{position}"
        if not (isinstance(name, str) and name):
            raise ManifestError(f"SBOM: component {label} is missing its name")
        if "repository" not in item:
            raise ManifestError(f"SBOM: component {label} is missing its repository")
        key = normalize_repo(_clean_str(item["repository"], f"SBOM: component {label}"))
        if key in result:
            raise ManifestError(f"SBOM: repository {key} is named by both {result[key][1]} and {label}")
        pins = [pin for pin in ("commit", "digest") if pin in item]
        if not pins:
            raise ManifestError(f"SBOM: component {label} has a repository but no pin (commit, digest)")
        result[key] = (_clean_str(item[pins[0]], f"SBOM: component {label}"), label)
    return result


def validate_pin_agreement(root: Path) -> None:
    locked = parse_lock(root / LOCK_PATH)
    sbom = parse_sbom(root / SBOM_PATH)
    for repository in sorted(set(locked) & set(sbom)):
        lock_pin, lock_key = locked[repository]
        sbom_pin, sbom_name = sbom[repository]
        if lock_pin != sbom_pin:
            raise ManifestError(
                f"pin disagreement for {repository}: upstream.lock.yaml {lock_key}={lock_pin}, "
                f"SBOM.yaml {sbom_name}={sbom_pin}"
            )

    for item in VENDORED_ROOTS:
        repository = normalize_repo(item.source)
        if repository not in locked:
            continue
        lock_pin, lock_key = locked[repository]
        if item.pin != lock_pin or item.pin_source != f"upstream.lock.yaml:{lock_key}":
            raise ManifestError(
                f"manifest pin disagreement for {item.path}: declared {item.pin} ({item.pin_source}), "
                f"lock has {lock_pin} (upstream.lock.yaml:{lock_key})"
            )
        if repository in sbom and sbom[repository][0] != item.pin:
            raise ManifestError(
                f"manifest/SBOM pin disagreement for {item.path}: {item.pin} != {sbom[repository][0]}"
            )


def git_revision(root: Path) -> str:
    try:
        return subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=root,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            text=True,
        ).stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        return "unknown"


def git_tree(root: Path, revision: str) -> str:
    """The tree of the generating commit, or `unknown`. The header records the tree, not the commit (task #246): a
    regen before a push recorded a local commit id that push_clean's rewrite replaced, so origin's manifest named a
    commit that does not exist there; the rewrite keeps every tree, so the tree id holds on origin."""
    try:
        return subprocess.run(
            ["git", "rev-parse", "--verify", "--quiet", f"{revision}^{{tree}}"],
            cwd=root,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            text=True,
        ).stdout.strip() or "unknown"
    except (OSError, subprocess.CalledProcessError):
        return "unknown"


def build_manifest_data(root: Path, repo_root: Path | None) -> ManifestData:
    # Fail-closed before any digest work (K1-h): a set that cannot be verified
    # against its provenance file writes nothing (neither --check nor --write).
    set_pin_lines = verify_declared_sets(root)
    index = load_kit_index(root)
    validate_sandbox_kit_entries(root)
    claude_by_class, claude_classes, kit_only_count = claude_records(root, repo_root, index)

    records: list[TreeRecord] = []
    for item in VENDORED_ROOTS:
        if item.path == ".claude/":
            claude_rows = (
                (
                    ".claude/ (kit-verbatim)",
                    "pxls21/sandbox-kit:dot-claude/",
                    "aeb3082",
                    KIT_INDEX_PATH.as_posix(),
                    claude_by_class["kit-verbatim"],
                ),
                (
                    ".claude/ (kit-adapted)",
                    "pxls21/sandbox-kit:dot-claude/",
                    "aeb3082 (adapted here)",
                    KIT_INDEX_PATH.as_posix(),
                    claude_by_class["kit-adapted"],
                ),
                (
                    ".claude/ (first-party)",
                    "first-party (this repository)",
                    "n/a",
                    "n/a",
                    claude_by_class["first-party"],
                ),
            )
            for path, source, pin, pin_source, files in claude_rows:
                regular_count, symlink_count = record_counts(files)
                records.append(
                    TreeRecord(
                        path=path,
                        source=source,
                        pin=pin,
                        pin_source=pin_source,
                        license="none found",
                        license_file=None,
                        license_sha256=None,
                        regular_file_count=regular_count,
                        symlink_count=symlink_count,
                        tree_sha256=digest_records(files),
                    )
                )

            # K1-h: one row per NON-EMPTY copy root, then per NON-EMPTY
            # declared set. Copy rows copy their source cells from the kit
            # root's own row (the digest stays over the .claude/ copies
            # themselves); set rows carry the verified set's own cells.
            copy_rows: list[tuple[str, str, str, str, str, str | None, str | None, list[tuple[str, bytes]]]] = []
            for item in VENDORED_ROOTS:
                if not item.path.startswith("sandbox-kit/"):
                    continue
                row_files = claude_by_class.get(f"copy:{item.path}", [])
                if not row_files:
                    continue
                # The license cells come from the root's own files (the same
                # `license_for` call the root's row makes), per the K1-h
                # contract.
                root_files = walk_tree(root / item.path, repo_root)
                license_id, license_file, license_sha = license_for(
                    root / item.path, root_files
                )
                copy_rows.append(
                    (
                        f".claude/ (copy of {item.path})",
                        item.source,
                        item.pin,
                        item.pin_source,
                        license_id,
                        license_file,
                        license_sha,
                        row_files,
                    )
                )
            for (
                path,
                source,
                pin,
                pin_source,
                license_id,
                license_file,
                license_sha,
                files,
            ) in copy_rows:
                regular_count, symlink_count = record_counts(files)
                records.append(
                    TreeRecord(
                        path=path,
                        source=source,
                        pin=pin,
                        pin_source=pin_source,
                        license=license_id,
                        license_file=license_file,
                        license_sha256=license_sha,
                        regular_file_count=regular_count,
                        symlink_count=symlink_count,
                        tree_sha256=digest_records(files),
                    )
                )

            set_rows: list[tuple[str, str, str, str, str, str | None, str | None, list[tuple[str, bytes]]]] = []
            for item in CLAUDE_DECLARED_SETS:
                row_files = claude_by_class.get(f"vendored:{item.name}", [])
                if not row_files:
                    continue
                license_id, license_file, license_sha = set_row_license(root, item)
                set_rows.append(
                    (
                        f".claude/ (vendored: {item.name})",
                        item.source,
                        item.pin,
                        f".claude/{item.provenance}:{set_pin_lines[item.name]}",
                        license_id,
                        license_file,
                        license_sha,
                        row_files,
                    )
                )
            for (
                path,
                source,
                pin,
                pin_source,
                license_id,
                license_file,
                license_sha,
                files,
            ) in set_rows:
                regular_count, symlink_count = record_counts(files)
                records.append(
                    TreeRecord(
                        path=path,
                        source=source,
                        pin=pin,
                        pin_source=pin_source,
                        license=license_id,
                        license_file=license_file,
                        license_sha256=license_sha,
                        regular_file_count=regular_count,
                        symlink_count=symlink_count,
                        tree_sha256=digest_records(files),
                    )
                )
            continue

        tree_root = root / item.path
        files = walk_tree(tree_root, repo_root)
        license_id, license_file, license_sha = license_for(tree_root, files)
        regular_count, symlink_count = record_counts(files)
        records.append(
            TreeRecord(
                path=item.path,
                source=item.source,
                pin=item.pin,
                pin_source=item.pin_source,
                license=license_id,
                license_file=license_file,
                license_sha256=license_sha,
                regular_file_count=regular_count,
                symlink_count=symlink_count,
                tree_sha256=digest_records(files),
            )
        )

    portable = kit_portable_records(root, repo_root)
    portable_license, portable_license_file, portable_license_sha = license_for(
        root / "sandbox-kit", portable
    )
    portable_regular_count, portable_symlink_count = record_counts(portable)
    records.append(
        TreeRecord(
            path=KIT_PORTABLE_ROW,
            source="pxls21/sandbox-kit:portable top-level files",
            pin="aeb3082",
            pin_source="sandbox-kit/VENDORED-FROM.md:19",
            license=portable_license,
            license_file=portable_license_file,
            license_sha256=portable_license_sha,
            regular_file_count=portable_regular_count,
            symlink_count=portable_symlink_count,
            tree_sha256=digest_records(portable),
        )
    )
    return ManifestData(records, claude_classes, kit_only_count)


def build_records(root: Path, repo_root: Path | None) -> list[TreeRecord]:
    return build_manifest_data(root, repo_root).records


def escape_cell(value: str) -> str:
    return value.replace("|", "\\|")


def generated_at_utc() -> str:
    source_date_epoch = os.environ.get("SOURCE_DATE_EPOCH")
    if source_date_epoch is not None:
        try:
            timestamp = int(source_date_epoch)
            return dt.datetime.fromtimestamp(timestamp, dt.timezone.utc).isoformat().replace("+00:00", "Z")
        except (OSError, OverflowError, ValueError):
            raise ManifestError(
                f"invalid SOURCE_DATE_EPOCH: {source_date_epoch!r} (expected Unix seconds)"
            ) from None
    return dt.datetime.now(dt.timezone.utc).isoformat().replace("+00:00", "Z")


def render(root: Path, revision: str | None = None) -> str:
    repo_root = repo_root_of(root)
    validate_declared_roots(root)
    validate_pin_agreement(root)
    revision = revision or git_revision(root)
    manifest_data = build_manifest_data(root, repo_root)
    rows = manifest_data.records
    output = [
        "# Vendored-tree manifest",
        "",
        "Generated by: `scripts/vendored_manifest.py`",
        f"Generated from tree: `{git_tree(root, revision) if revision != 'unknown' else 'unknown'}`",
        f"{GENERATED_AT_PREFIX}{generated_at_utc()}",
        "Excluded from every tree walk: `.git`, `__pycache__`, `*.pyc`, `node_modules`.",
        "Regenerate with `python3 scripts/vendored_manifest.py --write`; `--check` is the drift gate.",
        "Symlinks under a vendored root are digested by their target string; a link is allowed when its resolved target lies inside the repository root (AMENDMENT 1) and is refused by name when it dangles or resolves outside it.",
        "Declared roots are refused when the root itself is a symlink; the root type `dir` is included in each tree digest.",
        "Mode differences in `.claude/` are ignored for class; git blob sha1 bytes decide `kit-verbatim` vs `kit-adapted`.",
        f"Kit index: {KIT_INDEX_PATH.as_posix()} sha256 {KIT_INDEX_SHA256}; kit-only paths in index absent here: {manifest_data.kit_only_count}.",
        "First-party sandbox-kit entries: `VENDORED-FROM.md`, `VENDORED-MANIFEST.md`, `VENDORED-CLAUDE-CLASSES.tsv`, `dot-claude.aeb3082.index.tsv`.",
        "",
        "A pin source names the evidence for the pin. `unpinned (vendored copy)` is explicit where no immutable upstream pin is recorded.",
        "License SHA-256 is over the tree-local license file bytes; `none found` is never inferred from another source.",
        "",
        "| Path | Upstream source | Pin | Pin source | License | License file SHA-256 | Regular files | Symlinks | Tree SHA-256 |",
        "|---|---|---|---|---|---|---:|---:|---|",
    ]
    for record in rows:
        license_cell = record.license
        license_sha_cell = "none found"
        if record.license_file and record.license_sha256:
            license_cell = f"{record.license} (`{record.license_file}`)"
            license_sha_cell = f"`{record.license_sha256}`"
        output.append(
            "| "
            + " | ".join(
                [
                    f"`{record.path}`",
                    escape_cell(record.source),
                    f"`{record.pin}`",
                    escape_cell(record.pin_source),
                    license_cell,
                    license_sha_cell,
                    str(record.regular_file_count),
                    str(record.symlink_count),
                    f"`{record.tree_sha256}`",
                ]
            )
            + " |"
        )
    output.append("")
    return "\n".join(output)


def normalize_generated_time(text: str) -> str:
    """Blank the two lines that describe the GENERATION, not the vendored trees, before
    the drift comparison: the timestamp and the generating commit. A manifest committed
    at commit C necessarily names C's parent, so a strict commit line could never pass
    `--check` on a clean committed tree (found at the K1-d landing, 2026-09-22); drift of
    the vendored roots is carried exactly by the per-root digest rows below the header."""
    text = re.sub(
        rf"(?m)^{re.escape(GENERATED_AT_PREFIX)}.*$",
        GENERATED_AT_PREFIX + "<ignored by drift comparison>",
        text,
    )
    return re.sub(   # `commit` is the header before task #246; both forms compare equal
        r"(?m)^Generated from (?:commit|tree): .*$",
        "Generated from: <ignored by drift comparison>",
        text,
    )


def first_difference(expected: str, actual: str) -> str:
    expected_lines = expected.splitlines()
    actual_lines = actual.splitlines()
    limit = max(len(expected_lines), len(actual_lines))
    for index in range(limit):
        left = expected_lines[index] if index < len(expected_lines) else "<missing>"
        right = actual_lines[index] if index < len(actual_lines) else "<missing>"
        if left != right:
            return f"line {index + 1}: committed={left!r}; generated={right!r}"
    return "byte length differs"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path("."))
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true")
    mode.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    root = args.root.resolve()

    if args.write:
        try:
            generated = render(root)
            generated_classes = render_classes(
                build_manifest_data(root, repo_root_of(root)).claude_classes
            )
            manifest = root / MANIFEST_PATH
            manifest.write_text(generated, encoding="utf-8")
            classes = root / CLASSES_PATH
            classes.write_text(generated_classes, encoding="utf-8")
            print(f"WROTE {MANIFEST_PATH.as_posix()} ({len(VENDORED_ROOTS)} roots)")
            print(f"WROTE {CLASSES_PATH.as_posix()} ({len(parse_classes(generated_classes))} paths)")
            return 0
        except (ManifestError, OSError, UnicodeError) as error:
            print(f"FAIL: {error}", file=sys.stderr)
            return 1

    if not (root / MANIFEST_PATH).is_file():
        print(f"FAIL: committed manifest missing: {MANIFEST_PATH.as_posix()}", file=sys.stderr)
        return 1

    for attempt in range(2):
        try:
            start_revision = git_revision(root)
            manifest = root / MANIFEST_PATH
            committed = manifest.read_text(encoding="utf-8")
            generated = render(root, revision=start_revision)
            classes = root / CLASSES_PATH
            committed_classes = classes.read_text(encoding="utf-8")
            generated_classes = render_classes(
                build_manifest_data(root, repo_root_of(root)).claude_classes
            )
            end_revision = git_revision(root)
            if start_revision != end_revision:
                if attempt == 0:
                    continue
                raise ManifestError(
                    f"repository revision changed during --check: {start_revision} -> {end_revision}"
                )
            expected = normalize_generated_time(committed)
            actual = normalize_generated_time(generated)
            problems = []
            if expected != actual:
                problems.append(f"vendored manifest drift: {first_difference(expected, actual)}")
            if committed_classes != generated_classes:
                problems.append(
                    f".claude class drift: {class_difference(committed_classes, generated_classes)}"
                )
            if problems:
                raise ManifestError("; ".join(problems))
            print(f"PASS: {MANIFEST_PATH.as_posix()} matches {len(VENDORED_ROOTS)} vendored roots")
            return 0
        except (ManifestError, OSError, UnicodeError) as error:
            print(f"FAIL: {error}", file=sys.stderr)
            return 1
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
