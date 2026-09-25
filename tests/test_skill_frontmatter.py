"""Every skill carries a label the harness can read (D-092, owner 2026-09-25: "keep the skills, just label them properly").

Claude Code lists a skill with its description only when the SKILL.md frontmatter parses as YAML and names a description.
On 2026-09-25 two of the project's own skills, anti-hollow-green and deep-work, had an unquoted ": " in their description
("any project: the full ..."), a YAML error, so the harness listed them without a description; quoting the value
(text unchanged) brought them back the same minute. This test holds every SKILL.md in the three skill trees to that rule:
frontmatter present, valid YAML, a non-empty `name` and `description`. The negative control feeds the check the exact shape
that broke.
"""
import re
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[1]
TREES = (".claude/skills", ".agents/skills", ".agents/lane-skills")
FRONT = re.compile(r"\A---\n(.*?)\n---\n", re.S)


def label_problem(text):
    """None when the frontmatter parses and names a non-empty name and description, else the reason."""
    m = FRONT.match(text)
    if not m:
        return "no frontmatter block"
    try:
        fm = yaml.safe_load(m.group(1))
    except yaml.YAMLError as e:
        return "frontmatter is not valid YAML (%s)" % type(e).__name__
    if not isinstance(fm, dict):
        return "frontmatter is not a mapping"
    for key in ("name", "description"):
        if not isinstance(fm.get(key), str) or not fm[key].strip():
            return "no %s" % key
    return None


def skill_files():
    files = []
    for tree in TREES:
        files += sorted((ROOT / tree).glob("*/SKILL.md"))
    return files


def test_the_trees_hold_skills():
    counts = {t: len(list((ROOT / t).glob("*/SKILL.md"))) for t in TREES}
    assert counts[".claude/skills"] > 300 and counts[".agents/skills"] > 300 and counts[".agents/lane-skills"] > 10, counts


def test_every_skill_has_a_readable_label():
    bad = [(str(p.relative_to(ROOT)), why) for p in skill_files()
           if (why := label_problem(p.read_text(encoding="utf-8", errors="replace")))]
    assert bad == []


@pytest.mark.parametrize("front, reason", [
    ("name: x\ndescription: The tactics — any project: the full checklist.", "frontmatter is not valid YAML (ScannerError)"),
    ("name: x", "no description"),
    ("name: x\ndescription: ''", "no description"),
    ("- a\n- b", "frontmatter is not a mapping"),
])
def test_negative_control_the_broken_shapes_are_caught(front, reason):
    assert label_problem("---\n%s\n---\nbody\n" % front) == reason
    # positive control: the same description quoted, as the fix wrote it, passes
    if "any project:" in front:
        fixed = front.replace("description: The tactics — any project: the full checklist.",
                              "description: 'The tactics — any project: the full checklist.'")
        assert label_problem("---\n%s\n---\nbody\n" % fixed) is None


def test_no_frontmatter_is_caught():
    assert label_problem("# a skill with no frontmatter\n") == "no frontmatter block"
