#!/usr/bin/env python3
"""Generate and check the repository's vendored-tree manifest."""

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

MANIFEST_PATH = Path("sandbox-kit/VENDORED-MANIFEST.md")
PROVENANCE_PATH = Path("sandbox-kit/VENDORED-FROM.md")
LOCK_PATH = Path("upstream.lock.yaml")
SBOM_PATH = Path("SBOM.yaml")
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
        19,
        "unpinned (vendored copy)",
        "sandbox-kit/VENDORED-FROM.md:19-21",
    ),
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


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def normalize_repo(value: str) -> str:
    value = value.strip().removesuffix(".git").rstrip("/")
    value = re.sub(r"^(?:https?://)?(?:www\.)?github\.com/", "github.com/", value)
    return value.lower()


def excluded(relative: PurePosixPath) -> bool:
    return any(part in EXCLUDED_DIRS for part in relative.parts) or relative.name.endswith(
        EXCLUDED_SUFFIXES
    )


def walk_tree(root: Path, repo_root: Path | None) -> list[tuple[str, bytes]]:
    if not root.is_dir():
        raise ManifestError(f"vendored root missing or not a directory: {root.as_posix()}")

    records: list[tuple[str, bytes]] = []
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
    lines = path.read_text(encoding="utf-8").splitlines()
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
            break
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
    if not path.is_file():
        raise ManifestError(f"upstream lock missing: {path.as_posix()}")
    section = ""
    component = ""
    entries: dict[str, dict[str, str]] = {}
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if not line.startswith(" ") and line.endswith(":"):
            section = line[:-1]
            component = ""
            continue
        match = re.fullmatch(r"  ([a-z0-9][a-z0-9-]*):", line)
        if match:
            component = match.group(1)
            entries.setdefault(component, {})["key"] = f"{section}.{component}"
            continue
        match = re.fullmatch(r"    (repository|commit|binary_sha256|asset_sha256):\s*(.+)", line)
        if match and component:
            entries[component][match.group(1)] = match.group(2).strip().strip('"')
        elif line.startswith("    ") and ":" not in line:
            raise ManifestError(f"upstream lock parse failure at line {line_number}")

    parsed: dict[str, tuple[str, str]] = {}
    for name, values in entries.items():
        pin = values.get("commit") or values.get("binary_sha256") or values.get("asset_sha256")
        repository = values.get("repository")
        if repository and pin:
            parsed[normalize_repo(repository)] = (pin, values["key"])
    return parsed


def parse_sbom(path: Path) -> dict[str, tuple[str, str]]:
    if not path.is_file():
        raise ManifestError(f"SBOM missing: {path.as_posix()}")
    current: dict[str, str] = {}
    entries: dict[str, tuple[str, str]] = {}

    def finish() -> None:
        repository = current.get("repository")
        pin = current.get("commit") or current.get("digest")
        if repository and pin:
            entries[normalize_repo(repository)] = (pin, current.get("name", "unnamed"))

    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        match = re.fullmatch(r"\s*- name:\s*(\S+)\s*", line)
        if match:
            finish()
            current = {"name": match.group(1)}
            continue
        match = re.fullmatch(r"\s+(repository|commit|digest):\s*(\S+)\s*", line)
        if match and current:
            current[match.group(1)] = match.group(2).strip('"')
        elif line.lstrip().startswith("-") and current and "name:" not in line:
            raise ManifestError(f"SBOM parse failure at line {line_number}")
    finish()
    return entries


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


def build_records(root: Path, repo_root: Path | None) -> list[TreeRecord]:
    records: list[TreeRecord] = []
    for item in VENDORED_ROOTS:
        tree_root = root / item.path
        files = walk_tree(tree_root, repo_root)
        license_id, license_file, license_sha = license_for(tree_root, files)
        symlink_count = sum(payload.startswith(b"symlink:") for _, payload in files)
        records.append(
            TreeRecord(
                path=item.path,
                source=item.source,
                pin=item.pin,
                pin_source=item.pin_source,
                license=license_id,
                license_file=license_file,
                license_sha256=license_sha,
                regular_file_count=len(files) - symlink_count,
                symlink_count=symlink_count,
                tree_sha256=digest_records(files),
            )
        )
    return records


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
    rows = build_records(root, repo_root)
    output = [
        "# Vendored-tree manifest",
        "",
        "Generated by: `scripts/vendored_manifest.py`",
        f"Generated from commit: `{revision}`",
        f"{GENERATED_AT_PREFIX}{generated_at_utc()}",
        "Excluded from every tree walk: `.git`, `__pycache__`, `*.pyc`, `node_modules`.",
        "Regenerate with `python3 scripts/vendored_manifest.py --write`; `--check` is the drift gate.",
        "Symlinks under a vendored root are digested by their target string; a link is allowed when its resolved target lies inside the repository root (AMENDMENT 1) and is refused by name when it dangles or resolves outside it.",
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
    return re.sub(
        r"(?m)^Generated from commit: .*$",
        "Generated from commit: <ignored by drift comparison>",
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
            manifest = root / MANIFEST_PATH
            manifest.write_text(generated, encoding="utf-8")
            print(f"WROTE {MANIFEST_PATH.as_posix()} ({len(VENDORED_ROOTS)} roots)")
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
            end_revision = git_revision(root)
            if start_revision != end_revision:
                if attempt == 0:
                    continue
                raise ManifestError(
                    f"repository revision changed during --check: {start_revision} -> {end_revision}"
                )
            expected = normalize_generated_time(committed)
            actual = normalize_generated_time(generated)
            if expected != actual:
                raise ManifestError(
                    f"vendored manifest drift: {first_difference(expected, actual)}"
                )
            print(f"PASS: {MANIFEST_PATH.as_posix()} matches {len(VENDORED_ROOTS)} vendored roots")
            return 0
        except (ManifestError, OSError, UnicodeError) as error:
            print(f"FAIL: {error}", file=sys.stderr)
            return 1
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
