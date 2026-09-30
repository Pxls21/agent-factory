"""scripts/skill_bake_finish.sh: the refusals that happen before it touches anything (usage, a bad or unknown skill name,
a hand-ported skill whose port is missing, task #393), the ready path for a skill that is not hand-ported (task #369), and
for a hand-ported one with its port or with BAKE_UNPORTED_OK (task #393), each run in a detached worktree of HEAD.

The ride-along refusal (another skill's edit present) was proven live on 2026-09-24 against the shared tree (the commit that
adds the script pastes it); it is not repeated here. Each refusal case asserts the exit code and the message, and that no
tracked file changed.
"""
import hashlib
import os
import pathlib
import subprocess

ROOT = pathlib.Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "skill_bake_finish.sh"


def _status():
    return subprocess.run(["git", "-C", str(ROOT), "status", "--porcelain", "--untracked-files=no"],
                          capture_output=True, text=True, check=True).stdout


def _run(*args):
    return subprocess.run(["bash", str(SCRIPT), *args], capture_output=True, text=True, cwd=ROOT, timeout=60)


def test_no_skill_is_a_usage_error():
    before = _status()
    r = _run()
    assert r.returncode == 64 and "usage: skill_bake_finish.sh" in r.stderr
    assert _status() == before


def test_a_path_like_name_is_refused():
    before = _status()
    for bad in ("../x", "a/b", ".hidden"):
        r = _run(bad)
        assert r.returncode == 64 and "bad skill name: %s" % bad in r.stderr, (bad, r.stderr)
    assert _status() == before


def test_an_unknown_skill_is_refused():
    before = _status()
    r = _run("no-such-skill-qz8")
    assert r.returncode == 64 and "no .claude/skills/no-such-skill-qz8/SKILL.md" in r.stderr
    assert _status() == before


def test_a_plain_skill_edit_reaches_its_agents_and_lane_copies(tmp_path):
    # Task #369: the bake mirrored only the hand-ported lane copies, so an edit to a skill that is not hand-ported left
    # .agents/skills/<skill> stale and the pre-commit hook blocked (2026-09-29, env-tool-quirks). vendor-first is not
    # hand-ported and is a lane skill: .agents/lane-skills is filled from .agents/skills, so its copy is right only when
    # the .agents/skills copy is made first.
    wt = tmp_path / "wt"
    subprocess.run(["git", "-C", str(ROOT), "-c", "core.hooksPath=/dev/null", "worktree", "add", "-q", "--detach",
                    str(wt), "HEAD"], check=True, capture_output=True)
    try:
        skill = "vendor-first"
        src = wt / ".claude" / "skills" / skill / "SKILL.md"
        with open(src, "a", encoding="utf-8") as f:
            f.write("\nA line the bake test adds (task #369).\n")
        env = dict(os.environ, TMPDIR=str(tmp_path))
        r = subprocess.run(["bash", str(SCRIPT), skill], capture_output=True, text=True, cwd=wt, env=env, timeout=600)
        assert r.returncode == 0, r.stderr
        want = src.read_bytes()
        for copy in (".agents/skills", ".agents/lane-skills"):
            assert (wt / copy / skill / "SKILL.md").read_bytes() == want, copy
        listed = r.stdout.splitlines()
        for rel in (".claude/skills/%s/SKILL.md" % skill, ".agents/skills/%s/SKILL.md" % skill,
                    ".agents/lane-skills/%s/SKILL.md" % skill, "sandbox-kit/VENDORED-MANIFEST.md"):
            assert rel in listed, (rel, r.stdout)
    finally:
        subprocess.run(["git", "-C", str(ROOT), "worktree", "remove", "--force", str(wt)], capture_output=True)


def test_a_bake_that_rewords_a_line_ctx1_moved_is_refused(tmp_path):
    # CI run #1143 (2026-09-29): an env-tool-quirks edit reworded two lines CTX1 had moved from CLAUDE.md, and
    # tests/test_claude_md_lossless.py went red in CI only (it finds the skills by pattern, so no path-based gate ran it).
    wt = tmp_path / "wt"
    subprocess.run(["git", "-C", str(ROOT), "-c", "core.hooksPath=/dev/null", "worktree", "add", "-q", "--detach",
                    str(wt), "HEAD"], check=True, capture_output=True)
    try:
        src = wt / ".claude" / "skills" / "env-tool-quirks" / "SKILL.md"
        text = src.read_text(encoding="utf-8")
        moved = "liveness/wait loop MUST exclude its own command line"      # a line of CLAUDE.md at the CTX1 PIN
        assert text.count(moved) == 1
        src.write_text(text.replace(moved, "liveness loop MUST exclude its own command line"), encoding="utf-8")
        env = dict(os.environ, TMPDIR=str(tmp_path))
        r = subprocess.run(["bash", str(SCRIPT), "env-tool-quirks"], capture_output=True, text=True, cwd=wt, env=env,
                           timeout=600)
        assert r.returncode == 65, (r.returncode, r.stderr)
        assert "MISSING" in r.stderr and "moved from CLAUDE.md is gone" in r.stderr
        assert "sandbox-kit/VENDORED-MANIFEST.md" not in r.stdout          # it stopped before the manifest
    finally:
        subprocess.run(["git", "-C", str(ROOT), "worktree", "remove", "--force", str(wt)], capture_output=True)


def test_a_bake_that_grows_a_system1_entry_past_its_budget_is_refused(tmp_path):
    # The same hour as run #1143: a sentence added to the entry System-1's pc-suite row quotes took it past the hook's
    # 2048-byte TOOL_BUDGET, so the entry would never arrive; tests/test_system1_context.py finds the skills by pattern too.
    wt = tmp_path / "wt"
    subprocess.run(["git", "-C", str(ROOT), "-c", "core.hooksPath=/dev/null", "worktree", "add", "-q", "--detach",
                    str(wt), "HEAD"], check=True, capture_output=True)
    try:
        src = wt / ".claude" / "skills" / "env-tool-quirks" / "SKILL.md"
        text = src.read_text(encoding="utf-8")
        end = "(a worktree's `.git` is a file — bit 2026-09-06)."   # the last line of the pc-suite row's window
        assert text.count(end) == 1
        src.write_text(text.replace(end, end + " A sentence the bake test adds." * 20), encoding="utf-8")
        env = dict(os.environ, TMPDIR=str(tmp_path))
        r = subprocess.run(["bash", str(SCRIPT), "env-tool-quirks"], capture_output=True, text=True, cwd=wt, env=env,
                           timeout=600)
        assert r.returncode == 65, (r.returncode, r.stderr)
        assert "test_every_row_resolves_and_each_entry_fits_a_call_alone" in r.stderr and "skill reader is red" in r.stderr
        assert "MISSING" not in r.stderr                                    # the lossless check passed: the budget refused
        assert "sandbox-kit/VENDORED-MANIFEST.md" not in r.stdout
    finally:
        subprocess.run(["git", "-C", str(ROOT), "worktree", "remove", "--force", str(wt)], capture_output=True)


def _worktree(tmp_path):
    wt = tmp_path / "wt"
    subprocess.run(["git", "-C", str(ROOT), "-c", "core.hooksPath=/dev/null", "worktree", "add", "-q", "--detach",
                    str(wt), "HEAD"], check=True, capture_output=True)
    return wt


def _wt_status(wt):
    return subprocess.run(["git", "-C", str(wt), "status", "--porcelain", "--untracked-files=no"],
                          capture_output=True, text=True, check=True).stdout


# Task #393: D-115's bake (2026-09-30) edited the .claude copies of contract-gate and orchestration, both hand-ported;
# sync-skills never writes a hand-ported .agents copy, and the bake's --record then took the new base hash, so the
# lane copies lacked the edit while `sync-skills.sh --check` read in sync. The line goes in a section of its own at the
# end, so no System-1 entry grows.
HP_SKILL = "contract-gate"
HP_LINE = "\n## Bake test\n\nA line the bake test adds (task #393).\n"


def _hp_base(wt):
    for line in (wt / "harness-ports" / "hand-ported.sha256").read_text(encoding="utf-8").splitlines():
        parts = line.split()
        if len(parts) == 2 and parts[1] == HP_SKILL:
            return parts[0]
    raise AssertionError("no base hash for " + HP_SKILL)


def test_a_hand_ported_skill_whose_port_is_missing_is_refused(tmp_path):
    wt = _worktree(tmp_path)
    try:
        src = wt / ".claude" / "skills" / HP_SKILL / "SKILL.md"
        with open(src, "a", encoding="utf-8") as f:
            f.write(HP_LINE)
        base = _hp_base(wt)
        env = dict(os.environ, TMPDIR=str(tmp_path))
        env.pop("BAKE_UNPORTED_OK", None)
        r = subprocess.run(["bash", str(SCRIPT), HP_SKILL], capture_output=True, text=True, cwd=wt, env=env, timeout=600)
        assert r.returncode == 65, (r.returncode, r.stderr)
        assert ("%s is hand-ported, and .claude/skills/%s/SKILL.md changed while .agents/skills/%s/SKILL.md did not"
                % (HP_SKILL, HP_SKILL, HP_SKILL)) in r.stderr, r.stderr
        assert "MISSING" not in r.stderr and "skill reader is red" not in r.stderr    # this refusal, not a reader's
        assert _wt_status(wt) == " M .claude/skills/%s/SKILL.md\n" % HP_SKILL          # before any sync or --record
        assert _hp_base(wt) == base
        assert r.stdout == ""
    finally:
        subprocess.run(["git", "-C", str(ROOT), "worktree", "remove", "--force", str(wt)], capture_output=True)


def test_a_hand_ported_skill_with_its_port_bakes_and_records_its_base(tmp_path):
    wt = _worktree(tmp_path)
    try:
        for copy in (".claude/skills", ".agents/skills"):
            with open(wt / copy / HP_SKILL / "SKILL.md", "a", encoding="utf-8") as f:
                f.write(HP_LINE)
        env = dict(os.environ, TMPDIR=str(tmp_path))
        env.pop("BAKE_UNPORTED_OK", None)
        r = subprocess.run(["bash", str(SCRIPT), HP_SKILL], capture_output=True, text=True, cwd=wt, env=env, timeout=600)
        assert r.returncode == 0, (r.returncode, r.stderr)
        want = hashlib.sha256((wt / ".claude" / "skills" / HP_SKILL / "SKILL.md").read_bytes()).hexdigest()
        assert _hp_base(wt) == want
        listed = r.stdout.splitlines()
        for rel in (".claude/skills/%s/SKILL.md" % HP_SKILL, ".agents/skills/%s/SKILL.md" % HP_SKILL,
                    "harness-ports/hand-ported.sha256", "sandbox-kit/VENDORED-MANIFEST.md"):
            assert rel in listed, (rel, r.stdout)
    finally:
        subprocess.run(["git", "-C", str(ROOT), "worktree", "remove", "--force", str(wt)], capture_output=True)


def test_bake_unported_ok_passes_a_change_that_needs_no_port_and_says_so(tmp_path):
    wt = _worktree(tmp_path)
    try:
        agents = wt / ".agents" / "skills" / HP_SKILL / "SKILL.md"
        agents_before = agents.read_bytes()
        with open(wt / ".claude" / "skills" / HP_SKILL / "SKILL.md", "a", encoding="utf-8") as f:
            f.write(HP_LINE)
        env = dict(os.environ, TMPDIR=str(tmp_path), BAKE_UNPORTED_OK="orchestration %s" % HP_SKILL)
        r = subprocess.run(["bash", str(SCRIPT), HP_SKILL], capture_output=True, text=True, cwd=wt, env=env, timeout=600)
        assert r.returncode == 0, (r.returncode, r.stderr)
        assert "BAKE_UNPORTED_OK names %s: its .agents copy stays as it is" % HP_SKILL in r.stderr
        assert agents.read_bytes() == agents_before
        want = hashlib.sha256((wt / ".claude" / "skills" / HP_SKILL / "SKILL.md").read_bytes()).hexdigest()
        assert _hp_base(wt) == want
    finally:
        subprocess.run(["git", "-C", str(ROOT), "worktree", "remove", "--force", str(wt)], capture_output=True)
