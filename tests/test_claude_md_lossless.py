"""CTX1 (D-089): CLAUDE.md was shortened LOSSLESSLY into skills. This is the mechanical check.

The owner: shorten CLAUDE.md "losslessly, and anything you take out, you turn into a skill that you then reference in
the Claude.md". The check: every non-empty line of CLAUDE.md at the PIN (715caaf), whitespace-normalized, is found in
the current CLAUDE.md or in a skill file the current CLAUDE.md names (`.claude/skills/<name>/SKILL.md` for each
backticked `<name>` in it that is a skill directory), except the lines DROPPED names with its reason. Contract 1 allows
only an exact duplicate there; none was dropped. "Found" is a substring match against a file's whitespace-collapsed
text, so a moved line may be re-wrapped. A stricter count, "in context", also asks that the line sit next to one of its
PIN neighbors in the same file; a line found only bare is either a split point or a short line matching by
coincidence, and the script lists every one for review.

A later deliberate removal of moved text names the line in DROPPED with the owner's ruling, or this check goes red.

    python3 tests/test_claude_md_lossless.py [--new PATH] [--base REV]     # the summary line, and the bare-only list

Deterministic and LLM-free. The negative controls remove one moved line from an in-memory copy of its skill, and plant
a short line that matches only by coincidence.
"""
import argparse
import re
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
PIN = "715caaf"
DROPPED = {}          # normalized PIN line -> why it may be absent (contract 1: an exact duplicate only). None dropped.


def norm(s):
    return " ".join(s.split())


def named_skills(claude_text, root=ROOT):
    """The skills the text names: each backticked `<name>` with a .claude/skills/<name>/SKILL.md."""
    names = sorted(set(re.findall(r"`([a-z0-9][a-z0-9-]*)`", claude_text)))
    return [n for n in names if (root / ".claude" / "skills" / n / "SKILL.md").is_file()]


def corpus(claude_text, root=ROOT):
    """[(label, whitespace-collapsed text)]: the current CLAUDE.md first, then each skill it names."""
    docs = [("CLAUDE.md", norm(claude_text))]
    for n in named_skills(claude_text, root):
        docs.append((n, norm((root / ".claude" / "skills" / n / "SKILL.md").read_text(encoding="utf-8"))))
    return docs


def check(old_text, docs, dropped=None):
    """Every non-empty line of old_text against docs -> {checked, found{label: n}, missing, dropped, bare}."""
    dropped = DROPPED if dropped is None else dropped
    lines = [norm(x) for x in old_text.split("\n")]
    r = {"checked": 0, "found": {}, "missing": [], "dropped": [], "bare": []}
    for i, ln in enumerate(lines):
        if not ln:
            continue
        r["checked"] += 1
        if ln in dropped:
            r["dropped"].append((i + 1, ln))
            continue
        where = next((label for label, text in docs if ln in text), None)
        if where is None:
            r["missing"].append((i + 1, ln))
            continue
        r["found"][where] = r["found"].get(where, 0) + 1
        prev = lines[i - 1] if i > 0 else ""
        nxt = lines[i + 1] if i + 1 < len(lines) else ""
        pairs = [p for p in ((prev + " " + ln) if prev else "", (ln + " " + nxt) if nxt else "") if p]
        if pairs and not any(p in text for p in pairs for _, text in docs):
            r["bare"].append((i + 1, ln))
    return r


def summary(r):
    where = ", ".join("%s %d" % kv for kv in sorted(r["found"].items(), key=lambda kv: (-kv[1], kv[0])))
    return ("lossless: %d non-empty PIN lines checked, %d found (%s), %d missing, %d dropped as duplicates%s; "
            "%d in context, %d found only bare" % (
                r["checked"], sum(r["found"].values()), where, len(r["missing"]), len(r["dropped"]),
                " (%s)" % "; ".join("%d: %s" % d for d in r["dropped"]) if r["dropped"] else " (none)",
                sum(r["found"].values()) - len(r["bare"]), len(r["bare"])))


def pin_text(rev=PIN):
    p = subprocess.run(["git", "-C", str(ROOT), "show", "%s:CLAUDE.md" % rev], capture_output=True, text=True)
    return p.stdout if p.returncode == 0 else None


# ---------- the real check ----------

def test_every_pin_line_is_in_claude_md_or_a_skill_it_names():
    old = pin_text()
    if old is None:
        pytest.skip("the PIN %s is not in this clone's history (CI fetches the whole history)" % PIN)
    r = check(old, corpus((ROOT / "CLAUDE.md").read_text(encoding="utf-8")))
    assert r["missing"] == [] and r["dropped"] == [], summary(r)
    assert r["checked"] == 727 and len(r["found"]) > 1, summary(r)     # the PIN's 727 non-empty lines; text did move


def test_negative_control_a_line_removed_from_its_skill_is_reported():
    old = pin_text()
    if old is None:
        pytest.skip("the PIN %s is not in this clone's history" % PIN)
    line = next(x for x in old.split("\n") if x.startswith("**A `pgrep -f <pattern>` liveness/wait loop"))
    docs = corpus((ROOT / "CLAUDE.md").read_text(encoding="utf-8"))
    assert [label for label, text in docs if norm(line) in text] == ["env-tool-quirks"]   # it lives in one place only
    cut = [(label, text.replace(norm(line), "") if label == "env-tool-quirks" else text) for label, text in docs]
    assert check(old, cut)["missing"] == [(old.split("\n").index(line) + 1, norm(line))]


def test_negative_control_synthetic_missing_dropped_and_bare():
    old = "a1 long line\na2 long line\nit.\na4 long line\na5 long line\n\nremoved line here\n"
    docs = [("CLAUDE.md", norm("a1 long line a2 long line")), ("s", norm("a4 long line a5 long line")),
            ("t", norm("some other text it. and more"))]
    r = check(old, docs, dropped={})
    assert r["checked"] == 6 and r["missing"] == [(7, "removed line here")]
    assert r["found"] == {"CLAUDE.md": 2, "s": 2, "t": 1}
    assert r["bare"] == [(3, "it.")]                    # "it." is in `t`, but next to neither of its neighbors
    r = check(old, docs, dropped={"removed line here": "a planted duplicate"})
    assert r["dropped"] == [(7, "removed line here")] and r["missing"] == []


def test_named_skills_are_backticked_names_with_a_skill_dir():
    names = named_skills("see skill `build-loop`, `env-tool-quirks`, `not-a-skill-xyz` and `CLAUDE.md`")
    assert names == ["build-loop", "env-tool-quirks"]


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--new", default=str(ROOT / "CLAUDE.md"), help="the shortened CLAUDE.md (default: the repo's)")
    ap.add_argument("--base", default=PIN, help="the revision whose CLAUDE.md must survive (default: the PIN)")
    a = ap.parse_args(argv)
    old = pin_text(a.base)
    if old is None:
        print("lossless: %s:CLAUDE.md not readable" % a.base, file=sys.stderr)
        return 2
    new = Path(a.new).read_text(encoding="utf-8")
    r = check(old, corpus(new))
    print(summary(r))
    for no, ln in r["missing"]:
        print("MISSING %d: %s" % (no, ln[:150]))
    for no, ln in r["bare"]:
        print("bare %d: %s" % (no, ln[:150]))
    counts = {}
    for x in old.split("\n"):
        if norm(x):
            counts[norm(x)] = counts.get(norm(x), 0) + 1
    dups = sorted(x for x, n in counts.items() if n > 1)
    print("PIN exact-duplicate lines: %d%s" % (len(dups), "".join("\n  dup: %s" % d[:150] for d in dups)))
    return 0 if not r["missing"] else 1


if __name__ == "__main__":
    sys.exit(main())
