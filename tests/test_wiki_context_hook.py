"""`.claude/hooks/wiki-context.py`: what it injects per prompt (2026-09-24, the context-cost fix after task #214).

The hook runs on every UserPromptSubmit. Once the hooks fired in the /home/user session it injected the first 40 lines of
live-state (6.5 KB) on every person's prompt and 11.5 KB on every harness event (task notifications, agent hand-backs),
which are not a person's prompt. Now: harness events get nothing, and live-state contributes only its newest dated block.
The fixture runs a copy of the hook inside a temp tree, because the hook finds the wiki from its own path.
"""
import json
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HOOK = ROOT / ".claude" / "hooks" / "wiki-context.py"

LIVE_STATE = """---
topic: live-state
---

# Live State

## Clocks

- stale clock line from an old day

## Active lanes

**2026-09-24 12:0xZ — WHAT IS LIVE NOW (newest).**
- **LIVE:** the newest lane NEWESTMARK.

**2026-09-24 11:0xZ — WHAT IS LIVE NOW (older).**
- **LIVE:** an older lane OLDERMARK.

## Last updated
"""


def _tree(tmp_path, live_state):
    hook = tmp_path / ".claude" / "hooks" / "wiki-context.py"
    hook.parent.mkdir(parents=True)
    shutil.copy(HOOK, hook)
    page = tmp_path / "wiki" / "topics" / "live-state.md"
    page.parent.mkdir(parents=True)
    page.write_text(live_state)
    return hook


def _run(hook, prompt):
    r = subprocess.run([sys.executable, str(hook)], input=json.dumps({"prompt": prompt}),
                       capture_output=True, text=True, timeout=60)
    assert r.returncode == 0, r.stderr
    return r.stdout


def test_harness_events_inject_nothing(tmp_path):
    hook = _tree(tmp_path, LIVE_STATE)
    for prompt in ("[SYSTEM NOTIFICATION - NOT USER INPUT]\nThis is an automated background-task event",
                   "Another Claude session sent a message while you were working:\n<agent-message from=\"x\">",
                   "Stop hook feedback:\n[retro]", "<task-notification>\n<task-id>b1</task-id>",
                   "   [SYSTEM NOTIFICATION - NOT USER INPUT] leading spaces",
                   "<agent-message from=\"a1\">\n[Subagent hand-back] The text below is the final report"):
        assert _run(hook, prompt) == "", prompt


def test_a_person_gets_only_the_newest_live_block(tmp_path):
    hook = _tree(tmp_path, LIVE_STATE)
    out = _run(hook, "what lane is live now")
    assert "NEWESTMARK" in out
    assert "OLDERMARK" not in out and "stale clock line" not in out
    assert out.splitlines()[0] == "[wiki live-state — the newest block; the page holds the rest]"


def test_a_page_without_dated_blocks_falls_back_to_its_first_40_lines(tmp_path):
    lines = ["# Live State", "## Clocks"] + [f"- line {i}" for i in range(60)]
    hook = _tree(tmp_path, "\n".join(lines) + "\n")
    out = _run(hook, "what lane is live now").splitlines()
    assert "- line 37" in out and "- line 38" not in out


def test_the_newest_block_is_capped(tmp_path):
    body = "\n".join(f"- row {i}" for i in range(80))
    hook = _tree(tmp_path, "## Active lanes\n\n**2026-09-24 12:0xZ — WHAT IS LIVE NOW.**\n" + body + "\n")
    out = _run(hook, "what lane is live now").splitlines()
    assert "- row 28" in out and "- row 29" not in out


def test_the_real_wiki_stays_small_for_a_person_and_silent_for_an_event():
    person = subprocess.run([sys.executable, str(HOOK)], input=json.dumps({"prompt": "push the commits"}),
                            capture_output=True, text=True, timeout=60)
    event = subprocess.run([sys.executable, str(HOOK)],
                           input=json.dumps({"prompt": "[SYSTEM NOTIFICATION - NOT USER INPUT] done"}),
                           capture_output=True, text=True, timeout=60)
    assert person.returncode == 0 and event.returncode == 0
    assert 0 < len(person.stdout.encode()) < 8000, len(person.stdout.encode())
    assert event.stdout == ""


def test_long_incident_lines_are_cut_and_the_total_stays_under_the_harness_limit(tmp_path):
    hook = _tree(tmp_path, LIVE_STATE)
    log = tmp_path / "docs" / "INCIDENT-LOG.md"
    log.parent.mkdir(parents=True)
    entry = "**2026-09-24 — redaction leak in the ledger replay** " + "the redaction ledger replay leaked a value " * 70
    log.write_text("# redaction ledger replay incidents\n" + "\n".join([entry] * 12) + "\n")
    for i in range(3):
        page = tmp_path / "wiki" / "topics" / f"redaction-ledger-replay-{i}.md"
        page.write_text("# redaction ledger replay\n" + "\n".join(["redaction ledger replay " * 60] * 12) + "\n")
    out = _run(hook, "redaction ledger replay leak")
    assert len(out) < 8200, len(out)
    assert all(len(line) <= 300 + len(" [...]") for line in out.splitlines() if not line.startswith("**2026"))
    assert "[incident match: docs/INCIDENT-LOG.md]" in out or "[wiki match:" in out


def test_live_block_mode_prints_only_the_newest_block(tmp_path):
    hook = _tree(tmp_path, LIVE_STATE)
    r = subprocess.run([sys.executable, str(hook), "--live-block"], capture_output=True, text=True, timeout=60)
    assert r.returncode == 0 and "NEWESTMARK" in r.stdout and "OLDERMARK" not in r.stdout


def test_the_final_cap_holds_in_the_worst_case(tmp_path):
    # A live block at its 4,500-character cap plus three full matches under 200-character page names: only the final
    # 8,000-character cap keeps the text under the harness's 10,000-character preview threshold with margin.
    rows = "\n".join(f"- **LIVE:** row {i:02d} " + "x" * 132 for i in range(40))  # 30 lines, about 4,470 characters
    hook = _tree(tmp_path, "## Active lanes\n\n**2026-09-24 12:0xZ — WHAT IS LIVE NOW.**\n" + rows + "\n")
    for i in range(3):
        page = tmp_path / "wiki" / "topics" / (("redaction-ledger-replay-" * 10) + f"{i}.md")  # 245-character names
        page.write_text("# redaction ledger replay\n" + "\n".join(["redaction ledger replay " * 60] * 12) + "\n")
    out = _run(hook, "redaction ledger replay leak")
    body = out.split("\n[wiki-context:")[0]
    assert len(body) <= 8000, len(body)
    assert "row 00" in body and "[wiki match:" in body
