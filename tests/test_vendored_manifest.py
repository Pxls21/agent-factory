from __future__ import annotations

import hashlib
import importlib.util
import re
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
SCRIPT = REPO / "scripts" / "vendored_manifest.py"
MANIFEST_PATH = Path("sandbox-kit/VENDORED-MANIFEST.md")
EXPECTED_PASS = "PASS: sandbox-kit/VENDORED-MANIFEST.md matches 9 vendored roots\n"


ADAPTED_PATHS = [
    "agents/adversarial-verifier.md",
    "agents/code-implementer.md",
    "agents/evidence-gatherer.md",
    "hooks/edit-snapshot.py",
    "hooks/graft-first-nag.py",
    "hooks/session-start.sh",
    "hooks/turn-retro-gate.sh",
    "settings.json",
    "skills/adversarial-review/SKILL.md",
    "skills/anti-hollow-green/SKILL.md",
    "skills/build-loop/SKILL.md",
    "skills/code-intel-trio/SKILL.md",
    "skills/contract-gate/SKILL.md",
    "skills/deep-work/SKILL.md",
    "skills/orchestration/SKILL.md",
    "skills/session-continuity/SKILL.md",
]


def load_module(path: Path = SCRIPT):
    spec = importlib.util.spec_from_file_location("vendored_manifest_under_test", path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def copy_fixture(tmp_path: Path, module=None) -> Path:
    """Copy only the generator's declared inputs, then create a real git
    toplevel. The bare repo has no commit, so git_revision() exercises the
    documented `unknown` fallback while repo_root_of() has an exact boundary."""
    module = module or load_module()
    root = tmp_path / "repo"
    (root / "scripts").mkdir(parents=True)
    shutil.copy2(Path(module.__file__), root / "scripts" / SCRIPT.name)
    for relative in (
        module.PROVENANCE_PATH,
        module.LOCK_PATH,
        module.SBOM_PATH,
        module.MANIFEST_PATH,
        module.CLASSES_PATH,
        module.KIT_INDEX_PATH,
    ):
        source = REPO / relative
        if source.exists():
            destination = root / relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, destination)
    for item in module.VENDORED_ROOTS:
        shutil.copytree(REPO / item.path, root / item.path, symlinks=True)
    for name, klass in module.SANDBOX_KIT_ENTRIES.items():
        source = REPO / "sandbox-kit" / name
        destination = root / "sandbox-kit" / name
        if destination.exists() or destination.is_symlink():
            continue
        if klass == "kit-portable-files":
            shutil.copy2(source, destination)
        elif klass == "first-party":
            if source.exists():
                shutil.copy2(source, destination)
    # AMENDMENT 2(d)'s cross-root fixture source. It is not a vendored root and
    # does not affect any row until a link under .claude points at it.
    agent_skill = Path(".agents/skills/anti-hollow-green")
    shutil.copytree(REPO / agent_skill, root / agent_skill)
    subprocess.run(["git", "init", "-q"], cwd=root, check=True)
    # Give the fixture a 40-hex HEAD without creating a commit object (rev-parse only
    # reads this ref), so git_revision() returns a real-shaped revision and
    # repo_root_of() still gets a real toplevel. The generating commit line is
    # informational — the drift comparison ignores it (see
    # test_committed_manifest_passes_check_at_a_later_head).
    commit_match = re.search(
        r"^Generated from commit: `([0-9a-f]{40})`$",
        (root / module.MANIFEST_PATH).read_text(encoding="utf-8"),
        re.M,
    )
    if not commit_match:
        raise AssertionError("committed manifest must carry a 40-hex generating commit")
    (root / ".git/refs/heads/master").write_text(commit_match.group(1) + "\n", encoding="ascii")
    return root


def write_module_source(root: Path, module) -> None:
    source = Path(module.__file__)
    assert source.is_file()
    shutil.copy2(source, root / "scripts" / SCRIPT.name)


def run_tool(root: Path, mode: str = "--check") -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(root / "scripts" / SCRIPT.name), "--root", str(root), mode],
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        timeout=180,
    )


def manifest_row(text: str, path: str) -> str:
    match = re.search(rf"^\| `{re.escape(path)}`.*$", text, re.M)
    assert match, f"manifest row missing: {path}"
    return match.group(0)


def manifest_row_sha(row: str) -> str:
    return row.rsplit("`", 2)[1]


def class_rows(path: Path) -> dict[str, str]:
    lines = path.read_text(encoding="utf-8").splitlines()
    assert lines[0] == "path\tclass"
    return dict(line.split("\t") for line in lines[1:])


def replace_manifest_hash(root: Path, path: str, sha: str = "0" * 64) -> None:
    manifest = root / MANIFEST_PATH
    lines = manifest.read_text(encoding="utf-8").splitlines()
    for index, line in enumerate(lines):
        if line.startswith(f"| `{path}`"):
            lines[index] = re.sub(r"`[0-9a-f]{64}`(?= \|$)", f"`{sha}`", line)
            manifest.write_text("\n".join(lines) + "\n", encoding="utf-8")
            return
    raise AssertionError(f"manifest row missing: {path}")


def classify_fixture(root: Path, module) -> None:
    classes = module.render_classes(
        module.build_manifest_data(root, module.repo_root_of(root)).claude_classes
    )
    (root / module.CLASSES_PATH).write_text(classes, encoding="utf-8")


def rewrite_manifest_and_classes(root: Path, module) -> None:
    (root / module.MANIFEST_PATH).write_text(module.render(root), encoding="utf-8")
    classify_fixture(root, module)


def test_real_link_passes_and_changes_digest_when_target_string_changes(tmp_path: Path) -> None:
    # AMENDMENT 2(a): the ONE real link passes. Its target STRING (not target
    # contents) is digest input, proved by changing only that string to another
    # in-repo path and observing the codebase-memory row's tree digest change.
    module = load_module()
    root = copy_fixture(tmp_path, module)
    link = root / "sandbox-kit/codebase-memory-mcp/Formula"
    assert link.is_symlink()
    assert link.readlink().as_posix() == "pkg/homebrew/Formula"
    first = module.render(root)
    first_record = next(
        record
        for record in module.build_records(root, module.repo_root_of(root))
        if record.path == "sandbox-kit/codebase-memory-mcp/"
    )
    first_row = manifest_row(first, "sandbox-kit/codebase-memory-mcp/")
    assert first_record.symlink_count == 1
    assert first_record.regular_file_count == 513

    link.unlink()
    link.symlink_to("pkg/homebrew")
    second = module.render(root)
    second_record = next(
        record
        for record in module.build_records(root, module.repo_root_of(root))
        if record.path == "sandbox-kit/codebase-memory-mcp/"
    )
    second_row = manifest_row(second, "sandbox-kit/codebase-memory-mcp/")

    assert second_record.symlink_count == 1
    assert second_record.regular_file_count == 513
    assert first_row != second_row


def test_committed_manifest_matches_fresh_generation(tmp_path: Path) -> None:
    root = copy_fixture(tmp_path)
    result = run_tool(root)
    assert result.returncode == 0, result.stderr
    assert result.stdout == EXPECTED_PASS


def test_two_write_runs_are_byte_identical(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    root = copy_fixture(tmp_path)
    monkeypatch.setenv("SOURCE_DATE_EPOCH", "0")

    first = run_tool(root, "--write")
    first_bytes = (root / MANIFEST_PATH).read_bytes()
    second = run_tool(root, "--write")
    second_bytes = (root / MANIFEST_PATH).read_bytes()

    assert first.returncode == 0, first.stderr
    assert second.returncode == 0, second.stderr
    assert first_bytes == second_bytes
    assert "Generated at (UTC): 1970-01-01T00:00:00Z" in first_bytes.decode("utf-8")


def test_generation_time_is_only_normalized_drift_line(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    root = copy_fixture(tmp_path)
    monkeypatch.setenv("SOURCE_DATE_EPOCH", "0")
    written = run_tool(root, "--write")
    assert written.returncode == 0, written.stderr
    manifest = root / MANIFEST_PATH
    text = manifest.read_text(encoding="utf-8")
    assert text.count("Generated at (UTC): ") == 1
    manifest.write_text(
        text.replace(
            "Generated at (UTC): 1970-01-01T00:00:00Z",
            "Generated at (UTC): 2030-12-31T23:59:59Z",
            1,
        ),
        encoding="utf-8",
    )

    result = run_tool(root)

    assert result.returncode == 0, result.stderr
    assert result.stdout == EXPECTED_PASS


def test_invalid_source_date_epoch_is_named(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    root = copy_fixture(tmp_path)
    monkeypatch.setenv("SOURCE_DATE_EPOCH", "not-unix-seconds")

    result = run_tool(root, "--write")

    assert result.returncode == 1
    assert "invalid SOURCE_DATE_EPOCH: 'not-unix-seconds'" in result.stderr


def test_committed_manifest_passes_check_at_a_later_head(tmp_path: Path) -> None:
    """The outermost boundary (K1-d landing, 2026-09-22): a manifest committed at commit
    C names C's parent in its header, so `--check` on any later HEAD must still PASS while
    the vendored trees are unchanged — the generating commit is information, never a
    drift input. The paired control: at that later HEAD one changed vendored byte is still
    named as drift on its ROW, never on the header line."""
    module = load_module()
    root = copy_fixture(tmp_path, module)
    (root / ".git/refs/heads/master").write_text(
        "1111111111111111111111111111111111111111\n", encoding="ascii"
    )

    result = run_tool(root)

    assert result.returncode == 0, result.stderr
    assert result.stdout == EXPECTED_PASS

    changed_root = root / "sandbox-kit/docs"
    changed_file = changed_root / "THIRD-PARTY-AGENT-TOOLS.md"
    changed_file.write_bytes(changed_file.read_bytes() + b"changed-byte\n")

    control = run_tool(root)

    assert control.returncode == 1
    assert "vendored manifest drift" in control.stderr
    assert "line 4" not in control.stderr
    assert "Generated from commit" not in control.stderr
    assert "sandbox-kit/docs/" in control.stderr


def test_changed_vendored_byte_names_root_and_returns_one(tmp_path: Path) -> None:
    module = load_module()
    root = copy_fixture(tmp_path, module)
    changed_root = root / "sandbox-kit/docs"
    changed_file = changed_root / "THIRD-PARTY-AGENT-TOOLS.md"
    changed_file.write_bytes(changed_file.read_bytes() + b"changed-byte\n")

    result = run_tool(root)

    assert result.returncode == 1
    assert "vendored manifest drift" in result.stderr
    assert "sandbox-kit/docs/" in result.stderr


def test_undeclared_sandbox_kit_entry_is_named(tmp_path: Path) -> None:
    root = copy_fixture(tmp_path)
    undeclared = root / "sandbox-kit/newtool"
    undeclared.mkdir()
    (undeclared / "file.txt").write_text("new vendored-looking tool\n", encoding="utf-8")

    result = run_tool(root)

    assert result.returncode == 1
    assert "FAIL: undeclared entry under sandbox-kit/: newtool" in result.stderr


def test_docs_byte_change_names_docs_row(tmp_path: Path) -> None:
    module = load_module()
    root = copy_fixture(tmp_path, module)
    changed = root / "sandbox-kit/docs/THIRD-PARTY-AGENT-TOOLS.md"
    changed.write_bytes(changed.read_bytes() + b"changed-byte\n")

    result = run_tool(root)

    assert result.returncode == 1
    assert "vendored manifest drift" in result.stderr
    assert "sandbox-kit/docs/" in result.stderr


def test_docs_table_entry_is_required_for_docs_drift(tmp_path: Path) -> None:
    module = load_module()
    root = copy_fixture(tmp_path, module)
    before = module.render(root)
    changed = root / "sandbox-kit/docs/THIRD-PARTY-AGENT-TOOLS.md"
    changed.write_bytes(changed.read_bytes() + b"changed-byte\n")
    after = module.render(root)

    assert manifest_row(before, "sandbox-kit/docs/") != manifest_row(after, "sandbox-kit/docs/")


def test_declared_sandbox_kit_entry_missing_is_named(tmp_path: Path) -> None:
    root = copy_fixture(tmp_path)
    (root / "sandbox-kit/README.md").unlink()

    result = run_tool(root)

    assert result.returncode == 1
    assert "FAIL: declared sandbox-kit entry missing: README.md" in result.stderr


def test_vendored_root_table_entry_missing_is_named(tmp_path: Path) -> None:
    root = copy_fixture(tmp_path)
    shutil.rmtree(root / "sandbox-kit/docs")

    result = run_tool(root)

    assert result.returncode == 1
    assert "FAIL: declared sandbox-kit entry missing: docs" in result.stderr


def test_kit_portable_row_changes_when_portable_file_changes(tmp_path: Path) -> None:
    module = load_module()
    root = copy_fixture(tmp_path, module)
    before = manifest_row(module.render(root), module.KIT_PORTABLE_ROW)
    portable = root / "sandbox-kit/README.md"
    portable.write_bytes(portable.read_bytes() + b"portable change\n")
    after = manifest_row(module.render(root), module.KIT_PORTABLE_ROW)

    assert before != after
    assert manifest_row_sha(before) != manifest_row_sha(after)


def test_real_claude_split_counts_and_class_file(tmp_path: Path) -> None:
    module = load_module()
    root = copy_fixture(tmp_path, module)
    rewrite_manifest_and_classes(root, module)
    manifest = (root / module.MANIFEST_PATH).read_text(encoding="utf-8")
    classes = class_rows(root / module.CLASSES_PATH)

    assert "Kit index: sandbox-kit/dot-claude.aeb3082.index.tsv sha256" in manifest
    assert "kit-only paths in index absent here: 19" in manifest
    assert "| `.claude/ (kit-verbatim)`" in manifest
    assert "| `.claude/ (kit-adapted)`" in manifest
    assert "| `.claude/ (first-party)`" in manifest
    # 2958/14 -> 2957/15 on 2026-09-23 (D-054, 6914400): agents/code-implementer.md pins its model id,
    # so it differs from the kit index and moves from kit-verbatim to kit-adapted.
    # 2957/15 -> 2956/16 on 2026-09-24 (D-065): agents/evidence-gatherer.md pins its model id the same way.
    assert manifest_row(manifest, ".claude/ (kit-verbatim)").split(" | ")[6:8] == ["2956", "0"]
    assert manifest_row(manifest, ".claude/ (kit-adapted)").split(" | ")[6:8] == ["16", "0"]
    # K1-h (task #137): the 129 first-party row of 6ec33ed split into 56 byte-identical
    # copies of kit roots (20 council-of-high-intelligence + 19 honey-for-devs + 13
    # llm-wiki-compiler + 4 output-styles), 61 declared-set members (47 aegis + 12 prism
    # + 2 typesafe), and a 12-file remainder. The 129 pin is replaced by K1-h counts.
    assert manifest_row(manifest, ".claude/ (first-party)").split(" | ")[6:8] == ["12", "0"]
    assert [path for path, klass in classes.items() if klass == "kit-adapted"] == ADAPTED_PATHS
    assert sum(klass == "kit-verbatim" for klass in classes.values()) == 2956
    assert sum(klass == "kit-adapted" for klass in classes.values()) == 16
    assert sum(klass == "first-party" for klass in classes.values()) == 12


# K1-h: the 12-file remainder of `.claude/ (first-party)` at the PIN. The three
# PROVENANCE-*.md files document the declared sets but are not set members;
# they stay first-party.
K1H_FIRST_PARTY_REMAINDER = [
    "agents/codebase-memory-auditor.md",
    "agents/codebase-memory-scout.md",
    "agents/codebase-memory.md",
    "commands/fetch-bookmarks.md",
    "commands/wiki-ingest.md",
    "commands/wiki-visualize.md",
    "skills/PROVENANCE-AEGIS.md",
    "skills/PROVENANCE-PRISM.md",
    "skills/PROVENANCE-TYPESAFE.md",
    "skills/codebase-memory/SKILL.md",
    "skills/session-start-hook/SKILL.md",
    "skills/wiki-compiler/SKILL.md",
]

# The three PROVENANCE-*.md files are the only first-party files OUTSIDE a
# declared set prefix and outside the copy rule; everything else under the
# set prefixes is a set member, everything byte-identical to a kit root is a
# copy, and the 12 above are the remainder.
K1H_SET_REMAINDER_PATHS = {
    "skills/PROVENANCE-AEGIS.md",
    "skills/PROVENANCE-PRISM.md",
    "skills/PROVENANCE-TYPESAFE.md",
}

# A .claude/ file whose blob matches EXACTLY ONE file under EXACTLY ONE
# declared kit root, so a one-byte edit flips it copy -> first-party without
# triggering the copy-ambiguous refusal.
K1H_HONEY_COPY_FILE = ".claude/agents/hive-builder.md"

# A source file whose blob is unique to ONE kit root (llm-wiki-compiler) and
# has NO committed .claude/ copy, so planting a byte-identical copy under
# .claude/ plus a second root's file makes the walk name THAT .claude/ path in
# the copy-ambiguous refusal. (The output-styles files are NOT usable: they
# already have byte-identical .claude/ copies, which the walk hits first and
# names in the refusal instead.)
K1H_AMBIGUOUS_SOURCE = "sandbox-kit/llm-wiki-compiler/README.md"


def k1h_class_counts(classes: dict[str, str]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for klass in classes.values():
        counts[klass] = counts.get(klass, 0) + 1
    return counts


def test_k1h_claude_classification_and_remainder(tmp_path: Path) -> None:
    """The K1-h class table: 12 first-party (the named remainder), 61 set
    members (47 aegis + 12 prism + 2 typesafe), 56 copies (20 + 19 + 13 + 4),
    and kit-verbatim 2956 / kit-adapted 16 (D-054, D-065). The 129-pin test
    above carries the manifest row; this test carries the per-class split."""
    module = load_module()
    root = copy_fixture(tmp_path, module)
    rewrite_manifest_and_classes(root, module)
    classes = class_rows(root / module.CLASSES_PATH)
    counts = k1h_class_counts(classes)

    assert counts.get("first-party", 0) == 12
    assert counts.get("vendored:aegis", 0) == 47
    assert counts.get("vendored:prism", 0) == 12
    assert counts.get("vendored:typesafe", 0) == 2
    assert counts.get("copy:sandbox-kit/council-of-high-intelligence/", 0) == 20
    assert counts.get("copy:sandbox-kit/honey-for-devs/", 0) == 19
    assert counts.get("copy:sandbox-kit/llm-wiki-compiler/", 0) == 13
    assert counts.get("copy:sandbox-kit/output-styles/", 0) == 4
    assert counts.get("kit-verbatim", 0) == 2956
    assert counts.get("kit-adapted", 0) == 16
    assert [
        path
        for path, klass in sorted(classes.items())
        if klass == "first-party"
    ] == K1H_FIRST_PARTY_REMAINDER
    assert [
        path
        for path, klass in sorted(classes.items())
        if klass == "vendored:aegis"
    ] == sorted(
        path for path in classes if path.startswith("skills/aegis-")
    )
    assert [
        path
        for path, klass in sorted(classes.items())
        if klass == "vendored:prism"
    ] == sorted(
        path for path in classes if path.startswith("skills/prism-")
    )
    assert [
        path
        for path, klass in sorted(classes.items())
        if klass == "vendored:typesafe"
    ] == sorted(
        path for path in classes if path.startswith("skills/typesafe-ai/")
    )
    # The 9 non-PROVENANCE remainder paths stay first-party and must NOT be
    # copies: the copy set is disjoint from them (their blobs are not under
    # any declared kit root — measured at the PIN, the brief's premise).
    copy_paths = {
        path for path, klass in classes.items() if klass.startswith("copy:")
    }
    assert not (
        copy_paths & (set(K1H_FIRST_PARTY_REMAINDER) - K1H_SET_REMAINDER_PATHS)
    )


def test_k1h_new_aegis_file_is_vendored_set_member(tmp_path: Path) -> None:
    """Control (b) first half: a NEW file under a declared set prefix is
    classified by the set rule, not the copy rule (the aegis tree is not
    byte-identical to any kit root, so the copy rule would not catch it)."""
    module = load_module()
    root = copy_fixture(tmp_path, module)
    new_dir = root / ".claude/skills/aegis-new"
    new_dir.mkdir(parents=True)
    (new_dir / "SKILL.md").write_text("new aegis skill\n", encoding="utf-8")

    classes = module.render_classes(
        module.build_manifest_data(root, module.repo_root_of(root)).claude_classes
    )
    parsed = module.parse_classes(classes)

    assert parsed["skills/aegis-new/SKILL.md"] == "vendored:aegis"


def test_k1h_aegis_provenance_pin_removed_is_refused(tmp_path: Path) -> None:
    """Control (b) second half: the aegis pin string removed from
    PROVENANCE-AEGIS.md refuses the WHOLE generation with the exact
    provenance-mismatch message and writes nothing (neither manifest nor
    class file is touched). The pin and the source share line 3, so the pin
    token is removed in place (the source line is kept) to isolate the
    `aegis pin` field: deleting the line would break the source first and
    mis-name the error."""
    module = load_module()
    root = copy_fixture(tmp_path, module)
    rewrite_manifest_and_classes(root, module)
    before = (root / module.MANIFEST_PATH).read_bytes()
    before_classes = (root / module.CLASSES_PATH).read_bytes()
    provenance = root / ".claude/skills/PROVENANCE-AEGIS.md"
    original = provenance.read_text(encoding="utf-8")
    assert original.count("60321ed") == 1  # the pin appears exactly once
    mutated = original.replace("60321ed", "0000000")
    assert "GanyuanRan/Aegis" in mutated and "60321ed" not in mutated
    provenance.write_text(mutated, encoding="utf-8")

    result = run_tool(root)

    assert result.returncode == 1
    assert "manifest: provenance mismatch: aegis pin" in result.stderr
    assert (root / module.MANIFEST_PATH).read_bytes() == before
    assert (root / module.CLASSES_PATH).read_bytes() == before_classes


def test_k1h_honey_copy_byte_change_falls_back_to_first_party(tmp_path: Path) -> None:
    """Control (a): one byte changed in a hive file that is a byte-identical
    copy of `sandbox-kit/honey-for-devs/` (the honey set is NOT a declared
    set: it is carried by the copy rule) flips the path copy ->
    first-party (the copy rule matches by blob identity only; a name match
    would not produce this fallback, which is what m2 kills)."""
    module = load_module()
    root = copy_fixture(tmp_path, module)
    rewrite_manifest_and_classes(root, module)
    target = root / K1H_HONEY_COPY_FILE
    target.write_bytes(target.read_bytes() + b"one byte changed\n")

    data = module.build_manifest_data(root, module.repo_root_of(root))
    classes = module.parse_classes(
        module.render_classes(data.claude_classes)
    )

    assert classes["agents/hive-builder.md"] == "first-party"
    counts = k1h_class_counts(classes)
    assert counts.get("copy:sandbox-kit/honey-for-devs/", 0) == 18
    assert counts.get("first-party", 0) == 13


def test_k1h_ambiguous_copy_blob_is_refused_by_name(tmp_path: Path) -> None:
    """Control (c): a `.claude/` file whose blob matches files under TWO
    different declared kit roots is refused by name (the ambiguity
    refusal); no classification is produced. The source file is
    `llm-wiki-compiler/README.md`: its blob is unique to that root and has no
    committed `.claude/` copy, so the ONLY `.claude/` file holding it is the
    one planted here. Planting the same blob into `output-styles/` makes the
    planted `.claude/` copy match two roots, so the refusal names THAT path
    (a pre-existing `.claude/` copy would be named instead)."""
    module = load_module()
    root = copy_fixture(tmp_path, module)
    source = root / K1H_AMBIGUOUS_SOURCE
    blob = source.read_bytes()
    (root / "sandbox-kit/output-styles/AMBIGUOUS-PLANT.md").write_bytes(blob)
    (root / ".claude/skills/dup-copy.md").write_bytes(blob)

    detected = False
    message = ""
    try:
        module.render(root)
    except module.ManifestError as error:
        detected = "manifest: .claude copy ambiguous: skills/dup-copy.md matches" in str(error)
        message = str(error)
    assert detected
    # both roots named (the refusal names every matching root, sorted)
    assert "sandbox-kit/llm-wiki-compiler/" in message
    assert "sandbox-kit/output-styles/" in message


def test_k1h_check_passes_then_honey_copy_flip_names_class_drift(
    tmp_path: Path,
) -> None:
    """Control (d) first half: --check PASSES on the (rewritten) committed
    tree; then a single byte in a honey copy flips its class and --check
    fails with the existing class-drift message naming the path."""
    module = load_module()
    root = copy_fixture(tmp_path, module)
    rewrite_manifest_and_classes(root, module)

    good = run_tool(root)
    assert good.returncode == 0, good.stderr
    assert good.stdout == EXPECTED_PASS

    target = root / K1H_HONEY_COPY_FILE
    target.write_bytes(target.read_bytes() + b"one byte changed\n")

    result = run_tool(root)

    assert result.returncode == 1
    assert (
        ".claude class drift: agents/hive-builder.md: "
        "committed=copy:sandbox-kit/honey-for-devs/ generated=first-party"
    ) in result.stderr


def test_claude_class_drift_names_changed_path(tmp_path: Path) -> None:
    module = load_module()
    root = copy_fixture(tmp_path, module)
    rewrite_manifest_and_classes(root, module)
    # The target must be kit-verbatim in the committed class file; code-implementer.md is kit-adapted since D-054,
    # evidence-gatherer.md since D-065. A vendored template is the stable choice.
    target = root / ".claude/skills/0-autoresearch-skill/templates/findings.md"
    target.write_bytes(target.read_bytes() + b"adapted now\n")
    replace_manifest_hash(root, ".claude/ (kit-verbatim)", module.build_manifest_data(root, module.repo_root_of(root)).records[0].tree_sha256)
    replace_manifest_hash(root, ".claude/ (kit-adapted)", module.build_manifest_data(root, module.repo_root_of(root)).records[1].tree_sha256)

    result = run_tool(root)

    assert result.returncode == 1
    assert ".claude class drift: skills/0-autoresearch-skill/templates/findings.md: committed=kit-verbatim generated=kit-adapted" in result.stderr


def test_new_first_party_claude_file_names_manifest_and_class_drift(tmp_path: Path) -> None:
    module = load_module()
    root = copy_fixture(tmp_path, module)
    rewrite_manifest_and_classes(root, module)
    added = root / ".claude/first-party-new.md"
    added.write_text("new first-party content\n", encoding="utf-8")

    result = run_tool(root)

    assert result.returncode == 1
    assert "vendored manifest drift" in result.stderr
    assert ".claude/ (first-party)" in result.stderr
    assert ".claude class drift: first-party-new.md: committed=<missing> generated=first-party" in result.stderr


@pytest.mark.parametrize(
    ("shape", "malform"),
    (
        # the class cell of line 2 replaced with an unknown value (VERIFY-K1-h's probe)
        ("unknown-class", lambda lines: (2, [lines[0], lines[1].split("\t")[0] + "\tBROKEN-CLASS", *lines[2:]])),
        # a row with no tab appended (the K150 brief's premise probe)
        ("no-tab", lambda lines: (len(lines) + 1, [*lines, "this row has no tab"])),
    ),
)
def test_malformed_claude_class_row_is_refused_by_line(tmp_path: Path, shape: str, malform) -> None:
    """Issue #60 finding 1 (VERIFY-K1-h): `parse_classes` refuses a malformed class row by line number, but no test
    reached the refusal, and mutants v-D (the refusal swallowed into first-party) and v4 (`parse_classes` a no-op)
    passed the whole file. `--check` parses the committed class file (`class_difference`) once it differs from the
    generated one, so a malformed row fails with the named refusal, never as a class drift."""
    module = load_module()
    root = copy_fixture(tmp_path, module)
    rewrite_manifest_and_classes(root, module)
    good = run_tool(root)
    assert good.returncode == 0, good.stderr
    assert good.stdout == EXPECTED_PASS

    classes = root / module.CLASSES_PATH
    line, lines = malform(classes.read_text(encoding="utf-8").splitlines())
    classes.write_text("\n".join(lines) + "\n", encoding="utf-8")

    result = run_tool(root)

    assert result.returncode == 1, shape
    assert f"FAIL: .claude class file parse failure at line {line}\n" in result.stderr, (shape, result.stderr)


def test_kit_index_sha256_mismatch_is_named(tmp_path: Path) -> None:
    module = load_module()
    root = copy_fixture(tmp_path, module)
    index = root / module.KIT_INDEX_PATH
    lines = index.read_text(encoding="utf-8").splitlines()
    lines[0] += " tampered"
    index.write_text("\n".join(lines) + "\n", encoding="utf-8")

    result = run_tool(root)

    assert result.returncode == 1
    assert "FAIL: kit index sha256 mismatch" in result.stderr


def test_malformed_kit_index_row_names_line(tmp_path: Path) -> None:
    module = load_module()
    root = copy_fixture(tmp_path, module)
    index = root / module.KIT_INDEX_PATH
    lines = index.read_text(encoding="utf-8").splitlines()
    lines[3] = "malformed"
    index.write_text("\n".join(lines) + "\n", encoding="utf-8")

    result = run_tool(root)

    assert result.returncode == 1
    assert "kit index parse failure at line 4" in result.stderr


def test_missing_kit_index_is_named(tmp_path: Path) -> None:
    module = load_module()
    root = copy_fixture(tmp_path, module)
    (root / module.KIT_INDEX_PATH).unlink()

    result = run_tool(root)

    assert result.returncode == 1
    assert "FAIL: kit index missing" in result.stderr


def test_real_tree_write_then_check_regenerates_claude_rows(tmp_path: Path) -> None:
    root = copy_fixture(tmp_path)
    written = run_tool(root, "--write")
    checked = run_tool(root)
    manifest = (root / MANIFEST_PATH).read_text(encoding="utf-8")

    assert written.returncode == 0, written.stderr
    assert checked.returncode == 0, checked.stderr
    assert checked.stdout == EXPECTED_PASS
    assert "| `.claude/ (kit-verbatim)`" in manifest
    assert "| `.claude/ (kit-adapted)`" in manifest
    assert "| `.claude/ (first-party)`" in manifest


def test_provenance_root_missing_from_declared_list_is_named(tmp_path: Path) -> None:
    module = load_module()
    root = copy_fixture(tmp_path, module)
    missing = "sandbox-kit/output-styles/"
    setattr(
        module,
        "VENDORED_ROOTS",
        tuple(item for item in module.VENDORED_ROOTS if item.path != missing),
    )
    # Materialize the in-memory tuple change into a fixture-local script while
    # keeping the rest of the module-scope constants intact.
    text = SCRIPT.read_text(encoding="utf-8")
    start = text.index("VENDORED_ROOTS = (")
    end = text.index(")\n\n# CLOSED classification", start) + 1
    declared = repr(tuple(module.VENDORED_ROOTS))
    mutated = text[:start] + f"VENDORED_ROOTS = {declared}" + text[end:]
    (root / "scripts" / SCRIPT.name).write_text(mutated, encoding="utf-8")

    result = run_tool(root)

    assert result.returncode == 1
    assert "roots missing from declared list" in result.stderr
    assert missing in result.stderr


def test_escaping_symlink_is_refused_by_name(tmp_path: Path) -> None:
    # AMENDMENT 2(b): an absolute link to /etc/hostname is outside the fixture
    # repository root and is refused with the link and target named.
    module = load_module()
    root = copy_fixture(tmp_path, module)
    link = root / module.VENDORED_ROOTS[1].path / "escape-link"
    link.symlink_to("/etc/hostname")

    result = run_tool(root)

    assert result.returncode == 1
    assert "escaping symlink refused" in result.stderr
    assert "escape-link -> /etc/hostname" in result.stderr
    assert str(root) in result.stderr


def test_dangling_symlink_is_refused_by_name(tmp_path: Path) -> None:
    # AMENDMENT 2(c): a dangling link inside a vendored root is refused by name.
    module = load_module()
    root = copy_fixture(tmp_path, module)
    link = root / module.VENDORED_ROOTS[1].path / "dangling-link"
    link.symlink_to("definitely-not-a-real-target")

    result = run_tool(root)

    assert result.returncode == 1
    assert "dangling symlink refused" in result.stderr
    assert "dangling-link -> definitely-not-a-real-target" in result.stderr


def test_cross_root_link_inside_repository_is_allowed_and_digested(tmp_path: Path) -> None:
    # AMENDMENT 2(d): .claude/x crosses roots into .agents/skills but stays
    # inside the repository. It is allowed; changing only its TARGET STRING to a
    # second path that resolves to the same directory changes .claude's digest.
    module = load_module()
    root = copy_fixture(tmp_path, module)
    link = root / ".claude/x"
    link.symlink_to("../.agents/skills/anti-hollow-green")
    first = module.render(root)
    first_row = manifest_row(first, ".claude/ (first-party)")

    link.unlink()
    link.symlink_to("../.agents/skills/../skills/anti-hollow-green")
    second = module.render(root)
    second_row = manifest_row(second, ".claude/ (first-party)")

    assert first_row != second_row


def test_missing_repository_root_refuses_symlink(tmp_path: Path) -> None:
    module = load_module()
    tree = tmp_path / "vendored"
    tree.mkdir()
    (tree / "in-repo-link").symlink_to("target")
    (tree / "target").write_text("exists but has no repository boundary\n", encoding="utf-8")

    with pytest.raises(module.ManifestError, match="repository root unknown"):
        module.walk_tree(tree, None)


def test_moving_real_link_target_outside_repo_flips_to_refused(tmp_path: Path) -> None:
    # AMENDMENT 2(e): moving the real Formula link target outside the repository
    # flips its disposition from allowed to refused. The outside target exists,
    # so this proves containment, not the dangling guard.
    module = load_module()
    root = copy_fixture(tmp_path, module)
    outside = tmp_path / "outside-target"
    outside.write_text("outside the repository root\n", encoding="utf-8")
    link = root / "sandbox-kit/codebase-memory-mcp/Formula"
    assert link.is_symlink()
    link.unlink()
    link.symlink_to("../../../outside-target")

    result = run_tool(root)

    assert result.returncode == 1
    assert "escaping symlink refused" in result.stderr
    assert "Formula -> ../../../outside-target" in result.stderr
    assert str(outside) in result.stderr


def test_declared_root_symlink_is_refused_by_name(tmp_path: Path) -> None:
    module = load_module()
    root = copy_fixture(tmp_path, module)
    plain_control = run_tool(root)
    assert plain_control.returncode == 0, plain_control.stderr

    declared = root / "sandbox-kit/aleph"
    real = root / "sandbox-kit/aleph-real"
    declared.rename(real)
    declared.symlink_to("aleph-real")

    result = run_tool(root)

    assert result.returncode == 1
    assert f"declared root is a symlink: {(root / 'sandbox-kit/aleph').as_posix()} -> aleph-real" in result.stderr


def test_declared_root_symlink_target_outside_sandbox_kit_is_refused_by_name(tmp_path: Path) -> None:
    root = copy_fixture(tmp_path)
    declared = root / "sandbox-kit/aleph"
    real = root / "aleph-real"
    declared.rename(real)
    declared.symlink_to("../aleph-real")

    result = run_tool(root)

    assert result.returncode == 1
    assert f"declared root is a symlink: {declared.as_posix()} -> ../aleph-real" in result.stderr


def test_declared_root_dangling_symlink_is_refused_by_type(tmp_path: Path) -> None:
    root = copy_fixture(tmp_path)
    declared = root / "sandbox-kit/aleph"
    shutil.rmtree(declared)
    declared.symlink_to("aleph-missing")

    result = run_tool(root)

    assert result.returncode == 1
    assert f"declared root is a symlink: {declared.as_posix()} -> aleph-missing" in result.stderr


def test_license_detection_reports_spdx_and_sha_or_none(tmp_path: Path) -> None:
    module = load_module()
    licensed = tmp_path / "licensed"
    licensed.mkdir()
    license_bytes = b"MIT License\n\nPermission is hereby granted, free of charge\n"
    (licensed / "LICENSE").write_bytes(license_bytes)
    files = module.walk_tree(licensed, tmp_path)

    assert module.license_for(licensed, files) == (
        "MIT",
        "LICENSE",
        hashlib.sha256(license_bytes).hexdigest(),
    )

    unlicensed = tmp_path / "unlicensed"
    unlicensed.mkdir()
    (unlicensed / "README.md").write_text("no license here\n", encoding="utf-8")
    assert module.license_for(unlicensed, module.walk_tree(unlicensed, tmp_path)) == (
        "none found",
        None,
        None,
    )



def test_walk_is_sorted_before_digest(tmp_path: Path) -> None:
    module = load_module()
    tree = tmp_path / "tree"
    # Nested paths make the final sort load-bearing: without it, os.walk yields
    # b.txt before aaa/c.txt even though the required byte order is the reverse.
    (tree / "aaa").mkdir(parents=True)
    (tree / "zzz").mkdir(parents=True)
    (tree / "b.txt").write_text("b", encoding="utf-8")
    (tree / "aaa/c.txt").write_text("c", encoding="utf-8")
    (tree / "zzz/d.txt").write_text("d", encoding="utf-8")
    records = module.walk_tree(tree, tmp_path)

    assert [path for path, _ in records] == ["", "aaa/c.txt", "b.txt", "zzz/d.txt"]
    assert records[0] == ("", b"dir")
    assert module.digest_records(records) != module.digest_records(list(reversed(records)))


def test_exclusions_do_not_affect_tree_record(tmp_path: Path) -> None:
    module = load_module()
    tree = tmp_path / "tree"
    tree.mkdir()
    (tree / "kept.txt").write_text("kept", encoding="utf-8")
    baseline = module.walk_tree(tree, tmp_path)
    excluded_files = (
        tree / ".git/config",
        tree / "__pycache__/cached.py",
        tree / "cached.pyc",
        tree / "node_modules/module.js",
    )
    for path in excluded_files:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("excluded mutation", encoding="utf-8")

    assert module.walk_tree(tree, tmp_path) == baseline
    assert [path for path, _ in baseline] == ["", "kept.txt"]
    assert baseline[0] == ("", b"dir")


def test_sbom_pin_disagreement_is_named(tmp_path: Path) -> None:
    module = load_module()
    root = copy_fixture(tmp_path, module)
    (root / module.LOCK_PATH).write_text(
        "selected_core:\n"
        "  example:\n"
        "    repository: https://github.com/example/component.git\n"
        "    commit: aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa\n",
        encoding="utf-8",
    )
    (root / module.SBOM_PATH).write_text(
        "components:\n"
        "  - name: example\n"
        "    repository: https://github.com/example/component.git\n"
        "    commit: bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb\n",
        encoding="utf-8",
    )

    result = run_tool(root)

    assert result.returncode == 1
    assert "pin disagreement for github.com/example/component" in result.stderr
    assert "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa" in result.stderr
    assert "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb" in result.stderr


def test_manifest_root_matching_lock_must_use_lock_pin(tmp_path: Path) -> None:
    module = load_module()
    root = copy_fixture(tmp_path, module)
    first = module.VENDORED_ROOTS[0]
    repository = "https://github.com/example/vendored.git"
    text = SCRIPT.read_text(encoding="utf-8")
    old = (
        '        "pxls21/sandbox-kit:dot-claude/",\n'
        "        11,\n"
        '        "aeb3082",\n'
        '        "sandbox-kit/VENDORED-FROM.md:3-5",\n'
    )
    new = (
        f'        "{repository}",\n'
        "        11,\n"
        '        "wrong",\n'
        '        "invented",\n'
    )
    assert text.count(old) == 1
    (root / "scripts" / SCRIPT.name).write_text(text.replace(old, new, 1), encoding="utf-8")
    (root / module.LOCK_PATH).write_text(
        "selected_core:\n"
        "  vendored:\n"
        f"    repository: {repository}\n"
        "    commit: aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa\n",
        encoding="utf-8",
    )
    (root / module.SBOM_PATH).write_text(
        "components:\n"
        "  - name: vendored\n"
        f"    repository: {repository}\n"
        "    commit: aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa\n",
        encoding="utf-8",
    )

    result = run_tool(root)

    assert result.returncode == 1
    assert f"manifest pin disagreement for {first.path}" in result.stderr
    assert "upstream.lock.yaml:selected_core.vendored" in result.stderr


MUTANTS = (
    (
        "unsorted-tree-digest",
        lambda text: text.replace(
            'return sorted(records, key=lambda record: record[0].encode("utf-8"))',
            "return records",
        ),
        "test_walk_is_sorted_before_digest",
    ),
    (
        "empty-exclusions",
        lambda text: text.replace(
            'EXCLUDED_DIRS = frozenset({".git", "__pycache__", "node_modules"})',
            "EXCLUDED_DIRS = frozenset()",
        ).replace('EXCLUDED_SUFFIXES = (".pyc",)', "EXCLUDED_SUFFIXES = ()"),
        "test_exclusions_do_not_affect_tree_record",
    ),
    (
        "remove-sbom-agreement",
        lambda text: text.replace("    validate_pin_agreement(root)\n", "    pass\n"),
        "test_sbom_pin_disagreement_is_named",
    ),
    (
        "remove-symlink-refusal",
        lambda text: text.replace(
            "        raise ManifestError(\n"
            "            f\"escaping symlink refused in {root.as_posix()}: {relative} -> {target} \"\n"
            "            f\"(resolved target {resolved.as_posix()} lies outside the repository root \"\n"
            "            f\"{repo_root.as_posix()})\"\n"
            "        ) from None",
            "        pass",
        ),
        "test_escaping_symlink_is_refused_by_name",
    ),
    (
        "remove-declared-root-symlink-refusal",
        lambda text: text.replace(
            "    if root.is_symlink():\n"
            "        raise ManifestError(\n"
            "            f\"declared root is a symlink: {root.as_posix()} -> {os.readlink(root)}\"\n"
            "        )\n",
            "    if root.is_symlink():\n        pass\n",
            1,
        ).replace(
            "        if klass == \"vendored-root\" and path.is_symlink():\n"
            "            raise ManifestError(\n"
            "                f\"declared root is a symlink: {path.as_posix()} -> {os.readlink(path)}\"\n"
            "            )\n",
            "        if klass == \"vendored-root\" and path.is_symlink():\n            pass\n",
        ),
        "test_declared_root_symlink_target_outside_sandbox_kit_is_refused_by_name",
    ),
    (
        "remove-undeclared-entry-refusal",
        lambda text: text.replace(
            '    if unknown:\n        raise ManifestError(f"undeclared entry under sandbox-kit/: {unknown[0]}")\n',
            '    if unknown:\n        pass\n',
        ),
        "test_undeclared_sandbox_kit_entry_is_named",
    ),
    (
        "remove-missing-entry-refusal",
        lambda text: text.replace(
            '    if not root.is_dir():\n'
            '        raise ManifestError(f"vendored root missing or not a directory: {root.as_posix()}")\n',
            '    if not root.is_dir():\n'
            '        pass\n',
        ).replace(
            '    missing = sorted(set(SANDBOX_KIT_ENTRIES) - present)\n'
            '    if missing:\n'
            '        raise ManifestError(f"declared sandbox-kit entry missing: {missing[0]}")\n',
            '    missing = []\n'
            '    if missing:\n'
            '        pass\n',
        ),
        "test_vendored_root_table_entry_missing_is_named",
    ),
    (
        "blob-sha-without-git-header",
        lambda text: text.replace(
            'return hashlib.sha1(b"blob %d\\0" % len(data) + data).hexdigest()',
            "return hashlib.sha1(data).hexdigest()",
        ),
        "test_real_claude_split_counts_and_class_file",
    ),
    (
        "remove-kit-index-sha256-check",
        lambda text: text.replace(
            '    if sha256_bytes(data) != KIT_INDEX_SHA256:\n        raise ManifestError("kit index sha256 mismatch")\n',
            '    if sha256_bytes(data) != KIT_INDEX_SHA256:\n        pass\n',
        ),
        "test_kit_index_sha256_mismatch_is_named",
    ),
    (
        "remove-claude-class-comparison",
        lambda text: text.replace(
            "            if committed_classes != generated_classes:\n"
            "                problems.append(\n"
            "                    f\".claude class drift: {class_difference(committed_classes, generated_classes)}\"\n"
            "                )\n",
            "            if False:\n                pass\n",
        ),
        "test_claude_class_drift_names_changed_path",
    ),
    (
        "drop-docs-root-from-manifest-table",
        lambda text: text.replace(
            '    for item in VENDORED_ROOTS:\n        if item.path == ".claude/":\n',
            '    for item in VENDORED_ROOTS:\n        if item.path == "sandbox-kit/docs/":\n            continue\n        if item.path == ".claude/":\n',
        ),
        "test_docs_byte_change_names_docs_row",
    ),
)


def run_killer(killer: str, module, work: Path, label: str) -> None:
    """One killer's check against `module`, inside its own directory `work`. Each assertion carries `label`,
    so a kill is that named assertion failing, never an unrelated exception."""
    if killer == "test_walk_is_sorted_before_digest":
        tree = work / "tree"
        (tree / "aaa").mkdir(parents=True)
        (tree / "zzz").mkdir(parents=True)
        (tree / "b.txt").write_text("b", encoding="utf-8")
        (tree / "aaa/c.txt").write_text("c", encoding="utf-8")
        (tree / "zzz/d.txt").write_text("d", encoding="utf-8")
        # the root's own record ("", b"dir") comes first since fe2284d, as the direct test pins; this copy of the
        # list lacked it, so the row failed on the UNMUTATED module too (AF-AP-138, caught by the baseline control)
        assert [path for path, _ in module.walk_tree(tree, work)] == [
            "",
            "aaa/c.txt",
            "b.txt",
            "zzz/d.txt",
        ], label
    elif killer == "test_exclusions_do_not_affect_tree_record":
        tree = work / "tree"
        tree.mkdir()
        (tree / "kept.txt").write_text("kept", encoding="utf-8")
        baseline = module.walk_tree(tree, work)
        excluded = tree / "node_modules/module.js"
        excluded.parent.mkdir()
        excluded.write_text("must stay excluded", encoding="utf-8")
        assert module.walk_tree(tree, work) == baseline, label
    elif killer == "test_sbom_pin_disagreement_is_named":
        root = copy_fixture(work, module)
        (root / module.LOCK_PATH).write_text(
            "selected_core:\n  example:\n    repository: https://github.com/example/component.git\n"
            "    commit: aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa\n",
            encoding="utf-8",
        )
        (root / module.SBOM_PATH).write_text(
            "components:\n  - name: example\n    repository: https://github.com/example/component.git\n"
            "    commit: bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb\n",
            encoding="utf-8",
        )
        detected = False
        try:
            # Exercise the production entry that the mutant disconnects;
            # calling validate_pin_agreement() directly would survive the
            # mutation and produce a hollow green.
            module.render(root)
        except module.ManifestError:
            detected = True
        assert detected, label
    elif killer == "test_escaping_symlink_is_refused_by_name":
        repo = work / "repo"
        tree = repo / "vendored"
        tree.mkdir(parents=True)
        subprocess.run(["git", "init", "-q"], cwd=repo, check=True)
        link = tree / "escape-link"
        link.symlink_to("/etc/hostname")
        detected = False
        try:
            module.walk_tree(tree, module.repo_root_of(repo))
        except module.ManifestError:
            detected = True
        assert detected, label
    elif killer == "test_declared_root_symlink_target_outside_sandbox_kit_is_refused_by_name":
        root = copy_fixture(work, module)
        declared = root / "sandbox-kit/aleph"
        real = root / "aleph-real"
        declared.rename(real)
        declared.symlink_to("../aleph-real")
        detected = False
        try:
            module.render(root)
        except module.ManifestError:
            detected = True
        assert detected, label
    elif killer == "test_undeclared_sandbox_kit_entry_is_named":
        root = copy_fixture(work, module)
        undeclared = root / "sandbox-kit/newtool"
        undeclared.mkdir()
        (undeclared / "file.txt").write_text("new\n", encoding="utf-8")
        detected = False
        try:
            module.render(root)
        except module.ManifestError:
            detected = True
        assert detected, label
    elif killer == "test_vendored_root_table_entry_missing_is_named":
        root = copy_fixture(work, module)
        shutil.rmtree(root / "sandbox-kit/docs")
        detected = False
        try:
            module.render(root)
        except module.ManifestError:
            detected = True
        assert detected, label
    elif killer == "test_real_claude_split_counts_and_class_file":
        root = copy_fixture(work, module)
        data = module.build_manifest_data(root, module.repo_root_of(root))
        counts = {record.path: record.regular_file_count for record in data.records}
        assert counts[".claude/ (kit-verbatim)"] == 2956, label
        assert counts[".claude/ (kit-adapted)"] == 16, label
    elif killer == "test_kit_index_sha256_mismatch_is_named":
        root = copy_fixture(work, module)
        index = root / module.KIT_INDEX_PATH
        lines = index.read_text(encoding="utf-8").splitlines()
        lines[0] += " tampered"
        index.write_text("\n".join(lines) + "\n", encoding="utf-8")
        detected = False
        try:
            module.render(root)
        except module.ManifestError:
            detected = True
        assert detected, label
    elif killer == "test_claude_class_drift_names_changed_path":
        root = copy_fixture(work, module)
        rewrite_manifest_and_classes(root, module)
        target = root / ".claude/skills/0-autoresearch-skill/templates/findings.md"
        target.write_bytes(target.read_bytes() + b"adapted now\n")
        result = subprocess.run(
            [sys.executable, str(root / "scripts" / SCRIPT.name), "--root", str(root), "--check"],
            check=False,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=180,
        )
        assert ".claude class drift" in result.stderr, label
    elif killer == "test_docs_byte_change_names_docs_row":
        root = copy_fixture(work, module)
        before = module.render(root)
        before_match = re.search(r"^\| `sandbox-kit/docs/`.*$", before, re.M)
        assert before_match, label
        changed = root / "sandbox-kit/docs/THIRD-PARTY-AGENT-TOOLS.md"
        changed.write_bytes(changed.read_bytes() + b"changed-byte\n")
        after = module.render(root)
        after_match = re.search(r"^\| `sandbox-kit/docs/`.*$", after, re.M)
        assert after_match, label
        assert before_match.group(0) != after_match.group(0), label
    else:
        pytest.fail(f"no killer implementation for {killer}")


@pytest.mark.parametrize(("mutant_name", "mutate", "killer"), MUTANTS)
def test_required_mutants_are_killed(
    tmp_path: Path,
    mutant_name: str,
    mutate,
    killer: str,
) -> None:
    text = SCRIPT.read_text(encoding="utf-8")
    mutated = mutate(text)
    assert mutated != text, f"{mutant_name} mutation did not apply"
    mutant_script = tmp_path / f"vendored_manifest_{mutant_name}.py"
    mutant_script.write_text(mutated, encoding="utf-8")

    # AF-AP-138 baseline control: the killer runs on the UNMUTATED module first and must pass there. A killer that
    # fails on the real module (a stale pin, a broken fixture) would "kill" every mutant, and the kill would say
    # nothing about the mutation.
    baseline = tmp_path / "baseline"
    baseline.mkdir()
    try:
        run_killer(killer, load_module(), baseline, mutant_name)
    except AssertionError as error:
        pytest.fail(f"AF-AP-138: {killer} fails on the UNMUTATED module, so a kill of {mutant_name} "
                    f"is not attributable to the mutation: {error!r}")

    mutant = load_module(mutant_script)
    mutated_work = tmp_path / "mutant"
    mutated_work.mkdir()
    # A mutant is killed only when its named assertion fails for the exact mutant
    # name; an unrelated exception is not accepted as a kill.
    with pytest.raises(AssertionError, match=mutant_name):
        run_killer(killer, mutant, mutated_work, mutant_name)
