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
    shutil.copy2(SCRIPT, root / "scripts" / SCRIPT.name)
    for relative in (module.PROVENANCE_PATH, module.LOCK_PATH, module.SBOM_PATH, module.MANIFEST_PATH):
        source = REPO / relative
        if source.exists():
            destination = root / relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, destination)
    for item in module.VENDORED_ROOTS:
        shutil.copytree(REPO / item.path, root / item.path, symlinks=True)
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
    assert result.stdout == "PASS: sandbox-kit/VENDORED-MANIFEST.md matches 8 vendored roots\n"


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
    assert result.stdout == "PASS: sandbox-kit/VENDORED-MANIFEST.md matches 8 vendored roots\n"


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
    assert result.stdout == "PASS: sandbox-kit/VENDORED-MANIFEST.md matches 8 vendored roots\n"

    changed_root = root / module.VENDORED_ROOTS[0].path
    changed_file = next(path for path in sorted(changed_root.rglob("*")) if path.is_file())
    changed_file.write_bytes(changed_file.read_bytes() + b"changed-byte\n")

    control = run_tool(root)

    assert control.returncode == 1
    assert "vendored manifest drift" in control.stderr
    assert "line 4" not in control.stderr
    assert "Generated from commit" not in control.stderr
    assert module.VENDORED_ROOTS[0].path in control.stderr


def test_changed_vendored_byte_names_root_and_returns_one(tmp_path: Path) -> None:
    module = load_module()
    root = copy_fixture(tmp_path, module)
    changed_root = root / module.VENDORED_ROOTS[0].path
    changed_file = next(path for path in sorted(changed_root.rglob("*")) if path.is_file())
    changed_file.write_bytes(changed_file.read_bytes() + b"changed-byte\n")

    result = run_tool(root)

    assert result.returncode == 1
    assert "vendored manifest drift" in result.stderr
    assert module.VENDORED_ROOTS[0].path in result.stderr


def test_provenance_root_missing_from_declared_list_is_named(tmp_path: Path) -> None:
    module = load_module()
    root = copy_fixture(tmp_path, module)
    missing = "sandbox-kit/output-styles/"
    setattr(
        module,
        "VENDORED_ROOTS",
        tuple(item for item in module.VENDORED_ROOTS if item.path != missing),
    )
    # Materialize the in-memory tuple change into a fixture-local script.
    text = SCRIPT.read_text(encoding="utf-8")
    start = text.index("VENDORED_ROOTS = (")
    end = text.index("\n\n\nclass ManifestError", start)
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
    first_row = manifest_row(first, ".claude/")

    link.unlink()
    link.symlink_to("../.agents/skills/../skills/anti-hollow-green")
    second = module.render(root)
    second_row = manifest_row(second, ".claude/")

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

    assert [path for path, _ in records] == ["aaa/c.txt", "b.txt", "zzz/d.txt"]
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
    assert [path for path, _ in baseline] == ["kept.txt"]


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
)


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
    mutant = load_module(mutant_script)

    # A mutant is killed only when its named assertion fails for the exact mutant
    # name; an unrelated exception is not accepted as a kill.
    with pytest.raises(AssertionError, match=mutant_name):
        if killer == "test_walk_is_sorted_before_digest":
            tree = tmp_path / "tree"
            (tree / "aaa").mkdir(parents=True)
            (tree / "zzz").mkdir(parents=True)
            (tree / "b.txt").write_text("b", encoding="utf-8")
            (tree / "aaa/c.txt").write_text("c", encoding="utf-8")
            (tree / "zzz/d.txt").write_text("d", encoding="utf-8")
            assert [path for path, _ in mutant.walk_tree(tree, tmp_path)] == [
                "aaa/c.txt",
                "b.txt",
                "zzz/d.txt",
            ], mutant_name
        elif killer == "test_exclusions_do_not_affect_tree_record":
            tree = tmp_path / "tree"
            tree.mkdir()
            (tree / "kept.txt").write_text("kept", encoding="utf-8")
            baseline = mutant.walk_tree(tree, tmp_path)
            excluded = tree / "node_modules/module.js"
            excluded.parent.mkdir()
            excluded.write_text("must stay excluded", encoding="utf-8")
            assert mutant.walk_tree(tree, tmp_path) == baseline, mutant_name
        elif killer == "test_sbom_pin_disagreement_is_named":
            root = copy_fixture(tmp_path, mutant)
            (root / mutant.LOCK_PATH).write_text(
                "selected_core:\n  example:\n    repository: https://github.com/example/component.git\n"
                "    commit: aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa\n",
                encoding="utf-8",
            )
            (root / mutant.SBOM_PATH).write_text(
                "components:\n  - name: example\n    repository: https://github.com/example/component.git\n"
                "    commit: bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb\n",
                encoding="utf-8",
            )
            detected = False
            try:
                # Exercise the production entry that the mutant disconnects;
                # calling validate_pin_agreement() directly would survive the
                # mutation and produce a hollow green.
                mutant.render(root)
            except mutant.ManifestError:
                detected = True
            assert detected, mutant_name
        elif killer == "test_escaping_symlink_is_refused_by_name":
            repo = tmp_path / "repo"
            tree = repo / "vendored"
            tree.mkdir(parents=True)
            subprocess.run(["git", "init", "-q"], cwd=repo, check=True)
            link = tree / "escape-link"
            link.symlink_to("/etc/hostname")
            detected = False
            try:
                mutant.walk_tree(tree, mutant.repo_root_of(repo))
            except mutant.ManifestError:
                detected = True
            assert detected, mutant_name
        else:
            pytest.fail(f"no killer implementation for {killer}")
