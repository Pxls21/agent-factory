"""scripts/task_sync.py: the harness task list as a synced view of the ledger (LS-B7, task #339, D-102).

Isolation: every run goes through a COPY of scripts/task_sync.py inside a temp repo, so its log, backups and off switch
live under the copy's own `.jev/`; CLAUDE_CONFIG_DIR and HOME point at temp dirs, so the hook form's tasks root is a temp
dir too. Nothing here writes the main tree's `.jev/` or `/root/.claude/tasks/`. The unit-level grammar checks import the
real module and call only its pure functions (extract, build_view).

Fixtures: GRAMMAR holds real headlines of todo/BUILD-TASKLIST.md (line numbers as of 2026-09-28), bodies trimmed to the
registration text they carry; the em dash is built with chr(0x2014). The harness's key order and bytes are the ones its
own task files carry (measured 2026-09-28: `JSON.stringify({id, ...task}, null, 2)`, no trailing newline).
"""
import fcntl
import importlib.util
import json
import os
import shutil
import subprocess
import sys
import tarfile
import time
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "scripts" / "task_sync.py"
REAL_LEDGER = ROOT / "todo" / "BUILD-TASKLIST.md"
EM = chr(0x2014)
KEYS = ["id", "subject", "description", "activeForm", "status", "blocks", "blockedBy"]
HEADER = ("# BUILD TASK LIST\n\n## 1. Tasks\n\n| slug | increment |\n|---|---|\n| s0-00 | #0 spike |\n\n"
          "## 2. LIVE ledger (append-only sync blocks; newest first)\n\n")


@pytest.fixture(autouse=True)
def _temp_config(tmp_path, monkeypatch):
    monkeypatch.setenv("CLAUDE_CONFIG_DIR", str(tmp_path / "config"))
    monkeypatch.setenv("HOME", str(tmp_path / "home"))


@pytest.fixture
def repo(tmp_path):
    r = tmp_path / "repo"
    (r / "scripts").mkdir(parents=True)
    (r / "todo").mkdir()
    shutil.copyfile(SRC, r / "scripts" / "task_sync.py")
    return r


def module():
    spec = importlib.util.spec_from_file_location("task_sync_under_test", SRC)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    assert Path(mod.__file__) == SRC
    return mod


def entry(head, stamp, body="", tail="."):
    return f"**{head} {EM} {stamp}{tail}** {body}".rstrip()


def ledger_text(*entries, overrides=None):
    text = HEADER + "\n\n".join(entries) + "\n"
    if overrides is not None:
        table = "## 1b. Task overrides\n\n| id | status | note |\n|---|---|---|\n" + "".join(f"| {r} |\n" for r in overrides)
        text = text.replace("## 2. LIVE", table + "\n## 2. LIVE")
    return text


def write_ledger(repo, *entries, overrides=None):
    path = repo / "todo" / "BUILD-TASKLIST.md"
    path.write_text(ledger_text(*entries, overrides=overrides), encoding="utf-8")
    return path


def cli(repo, *args):
    return subprocess.run([sys.executable, str(repo / "scripts" / "task_sync.py"), *map(str, args)],
                          capture_output=True, text=True, timeout=60, cwd="/")


def sync(repo, d, *extra):
    return cli(repo, "--ledger", repo / "todo" / "BUILD-TASKLIST.md", "--tasks-dir", d, *extra)


def hook(repo, event, payload):
    data = json.dumps(payload) if isinstance(payload, dict) else payload
    return subprocess.run([sys.executable, str(repo / "scripts" / "task_sync.py"), "--hook", event], input=data,
                          capture_output=True, text=True, timeout=60, cwd="/")


def harness_file(d, n, subject, status="pending"):
    """A task file in the harness's own shape and bytes."""
    d.mkdir(parents=True, exist_ok=True)
    obj = {"id": str(n), "subject": subject, "description": "seeded", "activeForm": "Seeding", "status": status,
           "blocks": [], "blockedBy": []}
    (d / f"{n}.json").write_bytes(json.dumps(obj, indent=2).encode())


def holds_open(proc, path):
    """True when the live process has `path` open (a structural sign that it is inside the lock wait)."""
    want = os.path.realpath(path)
    try:
        return any(os.path.realpath(f"/proc/{proc.pid}/fd/{n}") == want for n in os.listdir(f"/proc/{proc.pid}/fd"))
    except FileNotFoundError:
        return False


def snapshot(d):
    return {p.name: (p.read_bytes(), p.stat().st_mtime_ns) for p in sorted(d.iterdir())} if d.exists() else None


def view_files(d):
    """The task files, `<digits>.json` only (what the harness lists as tasks)."""
    return {int(p.stem): json.loads(p.read_bytes()) for p in d.glob("*.json") if p.stem.isdigit()}


def log_kinds(repo):
    path = repo / ".jev" / "task-sync" / "sync.log"
    return [line.split(" ", 2)[1] for line in path.read_text().splitlines()] if path.exists() else []


def words(*entries):
    """{id: the newest placed event's word, or None when every mention is unknown} for a built ledger."""
    ex = module().extract(ledger_text(*entries))
    return {tid: (sorted(t["events"])[-1][3] if t["events"] else None) for tid, t in ex["tasks"].items()}


# ---- the grammar, on real ledger headlines (the brief's evidence demand 2) ----

B = "REGISTERED (backlog)"
GRAMMAR = [
    ("1651-closed-and-by", entry("SYNTH1 OPTION 1 FAILS; TASK #308 CLOSED (SUPERSEDED BY #339); AF-AP-235 REGISTERED; "
                                 "TASK #341 REGISTERED", "2026-09-28 14:0xZ",
                                 "#341 (backlog): those readers refuse, with a named reason, a state folder that holds no "
                                 "`injections.jsonl`, instead of reporting zero joins."),
     {308: "CLOSED", 339: None, 341: B}),
    ("1420-issues-qualifier", entry("ISSUES #11 AND #17 CLOSED (completed)", "2026-09-24 03:3xZ"), {}),
    ("1369-run-qualifier", entry("CI RUN #988 PASSED; D-058 RECORDED (THE OWNER'S DREAM-PHASE JEV IDEA)",
                                 "2026-09-23 14:3xZ", tail=" (task #195 created, pending)."), {195: None}),
    ("1620-negation", entry("AF-AP-229 REGISTERED; TASK #318 WIDENED; SCRUB2-R1 BRIEFED (TASK #321, NOT DISPATCHED)",
                            "2026-09-26 06:4xZ"), {318: None, 321: "BRIEFED"}),
    ("1448-possessive", entry("VERIFY-COORD-0924 HOME: ALL THREE LANDINGS MERGE-READY-WITH-FOLLOWUPS (rule 0f; #214's "
                              "hooks, AF-AP-181, D-071)", "2026-09-24 12:2xZ"), {214: None}),
    ("1424-status-paren", entry("J0-b HOME: THE PC PROBE RAN; J0 DONE (task #123 closed; J1-4, task #121, unblocked)",
                                "2026-09-24 04:4xZ"), {123: "CLOSED", 121: None}),
    ("1439-tail-reference", entry("K170 DISPATCHED", "2026-09-24 08:0xZ", tail=" (task #170 in progress)."),
     {170: "DISPATCHED"}),
    ("1371-tail-last-clause", entry("THE SEVEN-LEG S0-02 CAPTURE CAME HOME; THE COMMITTED CHECKER CAUGHT A CONTAMINATED "
                                    "BAD-SIGNATURE LEG; B12 QUEUED (AF-AP-156)", "2026-09-23 14:5xZ",
                                    tail=" (task #196 created, pending, blocked on B11)."), {196: None}),
    ("1607-range", entry("THE ISSUE #59 BATCH PLANNED; TASKS #312-#315 REGISTERED", "2026-09-26 03:5xZ"),
     {312: "REGISTERED", 313: "REGISTERED", 314: "REGISTERED", 315: "REGISTERED"}),
    ("1565-event-before-list", entry("CI RED ON C0D01E7 FIXED (RUN #1087; TASK #286); D-091 REGISTERED AS TASKS #287-#289",
                                     "2026-09-25 19:4xZ"),
     {286: None, 287: "REGISTERED", 288: "REGISTERED", 289: "REGISTERED"}),
    ("1391-hyphen-compound", entry("C2 LANDED (task #148, the lane done-gate; GATED-PENDING-VERIFY, switched OFF)",
                                   "2026-09-23 21:0xZ"), {148: "LANDED"}),
    ("1552-re-prefix", entry("THE CONTAINER RESTARTED (ABOUT 16:4xZ): INSTALL1, VERIFY-S1-L1 AND L5 RE-DISPATCHED AS "
                             "CONTINUATIONS (TASKS #274, #275, #276)", "2026-09-25 16:4xZ"),
     {274: "DISPATCHED", 275: "DISPATCHED", 276: "DISPATCHED"}),
    ("1382-done", entry(f"VERIFY-S198A HOME: MERGE-READY-WITH-FOLLOWUPS {EM} S198A VERIFIED (task #203 closed; task #198 "
                        "increment A done)", "2026-09-23 18:2xZ"), {203: "CLOSED", 198: "DONE"}),
    ("1652-home", entry("#339: LS-AUDIT HOME, THE DESIGN WRITTEN, THE PREMORTEM DISPATCHED", "2026-09-28 14:1xZ"),
     {339: "HOME"}),
    ("1653-briefed", entry("D-102: THE TASK LIST BECOMES A SYNCED VIEW OF THE LEDGER (LS-B7 BRIEFED, TASK #339); THE MAIN "
                           "TREE RESET WITH THE OWNER'S AUTHORIZATION", "2026-09-28 14:2xZ"), {339: "BRIEFED"}),
    ("1598-landed", entry("S1-RATE LANDED ON THE OWNER'S RULING (TASK #295, D-095: THE FLAG WAS A FALSE POSITIVE; "
                          "GATED-PENDING-VERIFY)", "2026-09-26 02:3xZ"), {295: "LANDED"}),
    ("1647-backlog", entry("TURN RETRO: AF-AP-234 REGISTERED; TASK #331 WIDENED; TASKS #336 AND #337 REGISTERED",
                           "2026-09-28 13:0xZ",
                           "#336 (backlog): three PC-venue reds in the doc gate of 2026-09-28 (15 files set=c74d91a784ed, "
                           "each green in the sandbox). #337 (backlog): `scripts/extract_handback.py <agentId> <out.md>` "
                           "writes a subagent's SubagentHandback text with the coordinator note."),
     {331: None, 336: B, 337: B}),
    ("1655-backlog-registered", entry("D-103: LABELS NAME TOOL STACKS; THE LS PREMORTEM SAYS REDESIGN THE TRANSPORT; "
                                      "I59-F BUILT, ITS ROUND 2 RUNS; TASK #343 REGISTERED; LS-B7 AMENDED",
                                      "2026-09-28 15:0xZ",
                                      "(4) TASK #343 REGISTERED (backlog): `scripts/test_summary.sh` runs pytest with "
                                      "`-rs`, so a gate log names no FAILED line (I59-F A-5); CI moves to `-rfEs` with "
                                      "I59-F."), {343: B}),
    ("1648-body-run-number", entry("TASK #338 REGISTERED (the CI gate read an older run twice)", "2026-09-28 13:1xZ",
                                   "#295 (cee0c8a) inside a `--wait` loop, and #1100 (de2da78) at the landing push. #338 "
                                   "(backlog): before a WAIT that names a run older than the listing's newest "
                                   "run_number."), {338: B}),
    ("1463-date-only", entry(f"RETRO 14:4xZ {EM} TASK #238 OPENED; AF-AP-189; SKILL BAKES; PRODUCERS COMMITTED",
                             "2026-09-24"), {238: None}),
    ("1502-seconds-stamp", entry("PUSHED 00:3xZ (origin 9d94a9f, then the transcripts commit; CI run #1050 on d6a2142 "
                                 "passed first); THE QJ2 LANE LAUNCHED", "2026-09-25 00:35:59Z"), {}),
    ("1417-code-span", entry("MOJEV FINDINGS WRITTEN; AF-AP-172: THE PROJECT HOOKS DO NOT FIRE IN A `/home/user`-ROOTED "
                             "SESSION", "2026-09-24 03:2xZ",
                             tail=" (task #210 now waits on the owner; task #214 NEW, pending the owner's choice)."),
     {210: None, 214: None}),
    ("1383-dashes-in-headline", entry(f"T94 LANDED {EM} GATED-PENDING-VERIFY (tasks #200 + #167) {EM} with a COORDINATOR "
                                      "AMENDMENT to the poll probe", "2026-09-23 18:4xZ"),
     {200: "LANDED", 167: "LANDED"}),
]


@pytest.mark.parametrize("line,want", [(line, want) for _, line, want in GRAMMAR], ids=[g[0] for g in GRAMMAR])
def test_the_grammar_on_real_ledger_headlines(line, want):
    assert words(line) == want


WORD_STATUS = {"REGISTERED": "pending", "DISPATCHED": "in_progress", "RUNS": "in_progress", "RUNNING": "in_progress",
               "RESUMED": "in_progress", "BRIEFED": "in_progress", "HOME": "in_progress", "LANDED": "in_progress",
               "BUILT": "in_progress", "CLOSED": "closed", "DONE": "closed", "SUPERSEDED": "closed",
               "ACCEPTED": "closed"}          # the brief's item 1, written here, not read from the module


@pytest.mark.parametrize("word", sorted(WORD_STATUS))
def test_every_grammar_word_maps_to_its_status(word):
    """Built: on the 2026-09-28 ledger RUNS, RUNNING, RESUMED, BUILT, SUPERSEDED and ACCEPTED never sit beside a task id."""
    mod = module()
    for text in (f"TASK #5 {word}", f"TASK #5 {word.lower()}"):
        assert mod.build_view(mod.extract(ledger_text(entry(text, "2026-09-28 10:0xZ"))))["status"] == {5: WORD_STATUS[word]}


def test_the_stamp_is_the_last_dated_dash_outside_parens():
    """Built: no real headline carries a dated dash inside its tail parenthetical yet."""
    lines = (entry("TASK #7 DISPATCHED", "2026-09-28 10:0xZ", tail=f" (after the note {EM} 2026-09-20 09:0xZ)."),
             entry("TASK #7 CLOSED", "2026-09-25 10:0xZ"))
    mod = module()
    assert mod.build_view(mod.extract(ledger_text(*lines)))["status"] == {7: "in_progress"}


def test_backticks_and_a_date_only_stamp_place_nothing():
    """No real headline carries an event word only inside backticks, or a grammar word on a date-only line: built."""
    assert words(entry("X `DONE` FOR TASK #5", "2026-09-28 10:0xZ")) == {5: None}
    assert words(entry("X DONE FOR TASK #5", "2026-09-28 10:0xZ")) == {5: "DONE"}          # the control: it is the span
    assert words(entry("TASK #6 DISPATCHED", "2026-09-28")) == {6: None}
    assert words(entry("TASK #6 DISPATCHED", "2026-09-28 10:0xZ")) == {6: "DISPATCHED"}   # the control: it is the time


# ---- the sync: create, update, delete, idempotence, the dry run ----

def test_create_writes_one_file_per_view_task_in_the_harness_bytes(repo, tmp_path):
    write_ledger(repo, entry("TASK #10 REGISTERED", "2026-09-28 10:0xZ", "#10 (the sync hook): write the view."),
                 entry("TASK #11 DISPATCHED", "2026-09-28 10:1xZ"), entry("TASK #12 CLOSED", "2026-09-28 10:2xZ"))
    d = tmp_path / "dir"
    r = sync(repo, d, "--apply", "--allow-dir")
    assert r.returncode == 0, r.stderr
    assert sorted(p.name for p in d.glob("*.json")) == ["10.json", "11.json"]
    raw = (d / "10.json").read_bytes()
    obj = json.loads(raw)
    assert raw == json.dumps(obj, indent=2, ensure_ascii=False).encode() and not raw.endswith(b"\n")
    assert list(obj) == KEYS
    assert obj["id"] == "10" and obj["subject"] == "t10-sync-hook-write-the-view" and obj["status"] == "pending"
    assert obj["activeForm"] == "Working on task #10" and obj["blocks"] == [] and obj["blockedBy"] == []
    assert obj["description"].startswith("Ledger task #10: pending from REGISTERED on 2026-09-28 10:0xZ")
    assert json.loads((d / "11.json").read_bytes())["status"] == "in_progress"


def test_update_rewrites_a_stale_file_and_delete_removes_one_that_left_the_view(repo, tmp_path):
    write_ledger(repo, entry("TASK #10 REGISTERED", "2026-09-28 10:0xZ"))
    d = tmp_path / "dir"
    harness_file(d, 10, "t10-old-title", status="in_progress")
    harness_file(d, 7, "t7-hand-made")
    (d / "notes.json").write_text("{}")
    (d / ".highwatermark").write_text("7")
    r = sync(repo, d, "--apply", "--allow-dir")
    assert r.returncode == 0, r.stderr
    files = view_files(d)
    assert sorted(files) == [10] and files[10]["status"] == "pending" and files[10]["subject"].startswith("t10-")
    assert (d / "notes.json").read_text() == "{}"                     # not a <digits>.json: never touched
    assert (d / ".highwatermark").read_text() == "10"


def test_the_first_apply_migrates_harness_numbered_files(repo, tmp_path):
    """The live shape of 2026-09-28: harness 308 holds ledger task 318, harness 310 holds ledger task 321."""
    write_ledger(repo, entry("THE REPAIR S1-RATE-R1 (TASK #318) AND THE SCRUB GAP (TASK #319) REGISTERED",
                             "2026-09-26 04:3xZ"),
                 entry("SCRUB2-R1 ROUND 2 DISPATCHED (TASK #321)", "2026-09-28 12:5xZ"))
    d = tmp_path / "dir"
    harness_file(d, 308, "t318-s1-rate-r1-recorded-scores")
    harness_file(d, 310, "t321-scrub2-r1-repair", status="in_progress")
    (d / ".highwatermark").write_text("314")
    r = sync(repo, d, "--apply", "--allow-dir")
    assert r.returncode == 0, r.stderr
    files = view_files(d)
    assert sorted(files) == [318, 319, 321]
    assert {n: f["status"] for n, f in files.items()} == {318: "pending", 319: "pending", 321: "in_progress"}
    assert (d / ".highwatermark").read_text() == "321"


def test_a_second_run_plans_nothing(repo, tmp_path):
    write_ledger(repo, entry("TASKS #10 AND #11 REGISTERED", "2026-09-28 10:0xZ"))
    d = tmp_path / "dir"
    assert sync(repo, d, "--apply", "--allow-dir").returncode == 0
    before = snapshot(d)
    r = sync(repo, d, "--apply", "--allow-dir", "--quiet")
    assert (r.returncode, r.stdout) == (0, "") and snapshot(d) == before
    dry = sync(repo, d)
    assert "create=0 update=0 delete=0 hwm=11 " in dry.stdout
    assert len(list((repo / ".jev" / "task-sync").glob("backup-*.tar"))) == 1


def test_the_dry_run_writes_nothing(repo, tmp_path):
    write_ledger(repo, entry("TASK #10 REGISTERED", "2026-09-28 10:0xZ"))
    d = tmp_path / "dir"
    harness_file(d, 7, "t7-hand-made")
    before = snapshot(d)
    r = sync(repo, d)
    assert r.returncode == 0 and snapshot(d) == before
    assert r.stdout.splitlines()[0] == "task_sync: dry run, nothing written"
    assert "  create 10.json t10-" in r.stdout and "  delete 7.json (was t7-hand-made)" in r.stdout
    assert not list((repo / ".jev" / "task-sync").glob("backup-*.tar"))
    assert log_kinds(repo) == ["ok"]


# ---- fail closed ----

@pytest.mark.parametrize("case", ["missing", "not-utf8"])
def test_an_unreadable_ledger_writes_nothing_and_exits_3(repo, tmp_path, case):
    d = tmp_path / "dir"
    harness_file(d, 7, "t7-kept")
    before = snapshot(d)
    if case == "not-utf8":
        (repo / "todo" / "BUILD-TASKLIST.md").write_bytes(ledger_text(entry("TASK #1 REGISTERED", "2026-09-28 10:0xZ"))
                                                          .encode() + b"\xff\xfe")
    r = sync(repo, d, "--apply", "--allow-dir")
    assert r.returncode == 3 and "unreadable ledger" in r.stderr and snapshot(d) == before
    assert log_kinds(repo) == ["error"]


@pytest.mark.parametrize("text,reason", [
    ("# BUILD TASK LIST\n\n## 1. Tasks\n", "no '## 2.' LIVE section"),
    (HEADER + "a note with no dated line\n", "the LIVE section holds no dated line"),
    (ledger_text(f"**TASK #1 REGISTERED {EM} 2026-09-28 14:2x.** no Z", entry("TASK #2 REGISTERED", "2026-09-28 10:0xZ")),
     "line 11: malformed time"),
    (ledger_text(f"**TASK #1 REGISTERED {EM} 2026-13-40 14:2xZ.**", entry("TASK #2 REGISTERED", "2026-09-28 10:0xZ")),
     "line 11: bad date"),
    (ledger_text(entry("TASK #1 REGISTERED", "2026-09-28 10:0xZ"), overrides=["1 | done | not a status"]),
     "an override row must be"),
], ids=["no-live-section", "no-dated-line", "malformed-time", "bad-date", "bad-override"])
def test_a_parse_failure_writes_nothing_and_exits_3(repo, tmp_path, text, reason):
    (repo / "todo" / "BUILD-TASKLIST.md").write_text(text, encoding="utf-8")
    d = tmp_path / "dir"
    harness_file(d, 7, "t7-kept")
    before = snapshot(d)
    r = sync(repo, d, "--apply", "--allow-dir")
    assert r.returncode == 3 and "parse failure" in r.stderr and reason in r.stderr, r.stderr
    assert snapshot(d) == before


def test_an_empty_view_writes_nothing_and_exits_3(repo, tmp_path):
    write_ledger(repo, entry("TASK #10 REGISTERED", "2026-09-28 10:0xZ"), entry("TASK #10 CLOSED", "2026-09-28 11:0xZ"))
    d = tmp_path / "dir"
    harness_file(d, 7, "t7-kept")
    before = snapshot(d)
    r = sync(repo, d, "--apply", "--allow-dir")
    assert r.returncode == 3 and "empty view" in r.stderr and snapshot(d) == before


def test_apply_refuses_a_dir_outside_the_tasks_root(repo, tmp_path):
    write_ledger(repo, entry("TASK #10 REGISTERED", "2026-09-28 10:0xZ"))
    root = tmp_path / "config" / "tasks"
    for d in (tmp_path / "elsewhere", root / "a" / "b", root):
        r = sync(repo, d, "--apply")
        assert r.returncode == 3 and "is not a task dir under" in r.stderr, (d, r.stderr)
        assert not (d / "10.json").exists()
    assert sync(repo, tmp_path / "elsewhere", "--apply", "--allow-dir").returncode == 0
    r = sync(repo, root / "sess-1", "--apply")                          # a session dir under the root needs no flag
    assert r.returncode == 0 and (root / "sess-1" / "10.json").exists(), r.stderr


def test_a_held_lock_is_waited_for_and_never_written_under(repo, tmp_path):
    write_ledger(repo, entry("TASK #10 REGISTERED", "2026-09-28 10:0xZ"))
    d = tmp_path / "dir"
    d.mkdir()
    fd = os.open(d / ".lock", os.O_RDWR | os.O_CREAT, 0o644)
    fcntl.flock(fd, fcntl.LOCK_EX)
    try:
        r = sync(repo, d, "--apply", "--allow-dir", "--lock-wait", "0.3")        # refuses once the wait runs out
        assert r.returncode == 3 and "lock busy" in r.stderr and not (d / "10.json").exists()
        p = subprocess.Popen([sys.executable, str(repo / "scripts" / "task_sync.py"), "--ledger",
                              str(repo / "todo" / "BUILD-TASKLIST.md"), "--tasks-dir", str(d), "--apply", "--allow-dir",
                              "--lock-wait", "30", "--quiet"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        deadline = time.monotonic() + 30          # wait until the run holds the lock file open: it is inside the wait
        while not holds_open(p, d / ".lock"):
            assert p.poll() is None and time.monotonic() < deadline, "the run never reached the lock"
            time.sleep(0.01)
        time.sleep(0.5)
        assert p.poll() is None and not (d / "10.json").exists()
    finally:
        fcntl.flock(fd, fcntl.LOCK_UN)
        os.close(fd)
    assert p.wait(timeout=30) == 0 and (d / "10.json").exists()


# ---- the status rules ----

def test_lines_are_ordered_by_stamp_not_position():
    closed_first = ledger_text(entry("TASK #10 CLOSED", "2026-09-28 12:0xZ"), entry("TASK #10 DISPATCHED",
                                                                                    "2026-09-28 11:0xZ"))
    later_first = ledger_text(entry("TASK #10 DISPATCHED", "2026-09-28 12:0xZ"), entry("TASK #10 CLOSED",
                                                                                       "2026-09-27 23:5xZ"))
    mod = module()
    assert mod.build_view(mod.extract(closed_first))["status"] == {10: "closed"}
    assert mod.build_view(mod.extract(later_first))["status"] == {10: "in_progress"}


def test_the_override_table_wins(repo, tmp_path):
    write_ledger(repo, entry("TASK #10 REGISTERED", "2026-09-28 10:0xZ"), entry("TASK #11 CLOSED", "2026-09-28 10:1xZ"),
                 overrides=["10 | closed | done by hand", "#11 | in_progress | reopened", "12 | pending | the table alone"])
    d = tmp_path / "dir"
    r = sync(repo, d, "--apply", "--allow-dir")
    assert r.returncode == 0, r.stderr
    files = view_files(d)
    assert {n: f["status"] for n, f in files.items()} == {11: "in_progress", 12: "pending"}
    assert files[12]["subject"] == "t12-table-alone" and "by the override table" in files[11]["description"]


def test_unknown_mentions_never_change_a_status(repo, tmp_path):
    write_ledger(repo, entry("TASK #10 REGISTERED", "2026-09-28 10:0xZ"),
                 entry("TASK #20 DISPATCHED", "2026-09-28 10:1xZ"),
                 entry("TASK #10 WIDENED; TASK #20 WIDENED", "2026-09-28 11:0xZ"),
                 entry("SYNTH1 FAILS; TASK #30 CLOSED (SUPERSEDED BY #20)", "2026-09-28 12:0xZ"),
                 entry("#10'S FIRST FORM NAMED", "2026-09-28 13:0xZ"))
    d = tmp_path / "dir"
    r = sync(repo, d)
    assert r.returncode == 0, r.stderr
    assert "  #10 pending " in r.stdout and "  #20 in_progress " in r.stdout
    for line in ("#10 line 15 2026-09-28 11:0xZ: TASK #10 WIDENED", "#20 line 15 2026-09-28 11:0xZ:",
                 "#20 line 17 2026-09-28 12:0xZ:", "#10 line 19 2026-09-28 13:0xZ:"):
        assert f"  {line}" in r.stdout, line
    assert sync(repo, d, "--apply", "--allow-dir").returncode == 0
    files = view_files(d)
    assert {n: f["status"] for n, f in files.items()} == {10: "pending", 20: "in_progress"}
    assert "newest ledger line 2026-09-28 13:0xZ" in files[10]["description"]


def test_the_harness_keys_exactly(repo, tmp_path):
    long_text = "the " + " ".join(f"word{i}" for i in range(200))
    write_ledger(repo, entry("TASKS #10 AND #11 REGISTERED", "2026-09-28 10:0xZ", f"#10 ({long_text})."),
                 entry("TASK #11 HOME", "2026-09-28 11:0xZ"))
    d = tmp_path / "dir"
    assert sync(repo, d, "--apply", "--allow-dir").returncode == 0
    for p in sorted(d.glob("*.json")):
        raw = p.read_bytes()
        obj = json.loads(raw)
        assert list(obj) == KEYS and obj["id"] == p.stem
        assert all(type(obj[k]) is str for k in KEYS[:5]) and obj["blocks"] == [] and obj["blockedBy"] == []
        assert obj["status"] in ("pending", "in_progress")
        assert len(obj["description"]) <= 400 and obj["subject"].startswith(f"t{p.stem}-")
        assert 0 < len(obj["subject"]) - len(f"t{p.stem}-") <= 40
        assert raw == json.dumps(obj, indent=2, ensure_ascii=False).encode()
    ten = json.loads((d / "10.json").read_bytes())
    assert ten["subject"] == "t10-word0-word1-word2-word3-word4-word5"          # word6 would make the slug 41
    assert 390 < len(ten["description"]) <= 400 and ten["description"].endswith("...")


def test_the_same_ledger_gives_the_same_bytes(repo, tmp_path):
    write_ledger(repo, entry("TASKS #10 AND #11 REGISTERED", "2026-09-28 10:0xZ", "#10 (one): x. #11 (two): y."))
    a, b = tmp_path / "a", tmp_path / "b"
    assert sync(repo, a, "--apply", "--allow-dir").returncode == 0
    assert sync(repo, b, "--apply", "--allow-dir").returncode == 0
    assert {p.name: p.read_bytes() for p in a.glob("*.json")} == {p.name: p.read_bytes() for p in b.glob("*.json")}


def test_the_highwatermark_is_raised_never_lowered(repo, tmp_path):
    write_ledger(repo, entry("TASK #10 REGISTERED", "2026-09-28 10:0xZ"), entry("TASK #40 CLOSED", "2026-09-28 10:1xZ"))
    low, high = tmp_path / "low", tmp_path / "high"
    for d, hwm in ((low, "7"), (high, "999")):
        d.mkdir()
        (d / ".highwatermark").write_text(hwm)
        assert sync(repo, d, "--apply", "--allow-dir").returncode == 0
    assert (low / ".highwatermark").read_text() == "40" and (high / ".highwatermark").read_text() == "999"


def test_the_backup_holds_the_pre_state(repo, tmp_path):
    write_ledger(repo, entry("TASK #10 REGISTERED", "2026-09-28 10:0xZ"))
    d = tmp_path / "sess-9"
    harness_file(d, 7, "t7-before")
    before = (d / "7.json").read_bytes()
    assert sync(repo, d, "--apply", "--allow-dir").returncode == 0
    tars = list((repo / ".jev" / "task-sync").glob("backup-*.tar"))
    assert len(tars) == 1
    with tarfile.open(tars[0]) as tar:
        assert tar.getnames() == ["sess-9/7.json"] and tar.extractfile("sess-9/7.json").read() == before


# ---- the hooks (the brief's evidence demand 5) ----

def test_the_stop_hook_writes_the_view_and_prints_nothing(repo, tmp_path):
    write_ledger(repo, entry("TASK #10 REGISTERED", "2026-09-28 10:0xZ"))
    harness_file(tmp_path / "config" / "tasks" / "sess-1", 3, "t3-hand-made")
    before = {p: p.read_bytes() for p in tmp_path.rglob("*") if p.is_file()}
    r = hook(repo, "stop", {"session_id": "sess/1", "hook_event_name": "Stop"})
    assert (r.returncode, r.stdout, r.stderr) == (0, "", "")
    d = tmp_path / "config" / "tasks" / "sess-1"                         # the harness's own list-id spelling
    assert sorted(view_files(d)) == [10] and log_kinds(repo) == ["ok"]
    after = {p: p.read_bytes() for p in tmp_path.rglob("*") if p.is_file()}
    changed = {p for p in set(before) | set(after) if before.get(p) != after.get(p)}
    # it writes only the task dir and .jev/task-sync/ (git ignores .jev/), so it races no parallel Stop hook's reads
    assert changed and all(d in p.parents or repo / ".jev" / "task-sync" in p.parents for p in changed), changed


def test_the_hook_state_paths_are_git_ignored(tmp_path):
    """The repo's own .gitignore, checked in a fresh repo (a `git archive` gate copy has no .git of its own)."""
    g = tmp_path / "g"
    subprocess.run(["git", "init", "-q", str(g)], check=True, capture_output=True, timeout=60)
    shutil.copyfile(ROOT / ".gitignore", g / ".gitignore")
    for rel in (".jev/task-sync/sync.log", ".jev/task-sync/backup-20260928T000000.000000Z.tar", ".jev/task-sync-off"):
        r = subprocess.run(["git", "-C", str(g), "check-ignore", "-q", "--no-index", rel], capture_output=True, timeout=60)
        assert r.returncode == 0, rel
    r = subprocess.run(["git", "-C", str(g), "check-ignore", "-q", "--no-index", "scripts/task_sync.py"], timeout=60)
    assert r.returncode == 1                                                  # the control: a tracked path is not ignored


def test_a_stop_error_is_shown_once_per_new_error_and_never_blocks(repo):
    path = repo / "todo" / "BUILD-TASKLIST.md"
    path.write_text("# no live section\n")
    runs = [hook(repo, "stop", {"session_id": "s1"}), hook(repo, "stop", {"session_id": "s1"})]
    path.unlink()
    runs.append(hook(repo, "stop", {"session_id": "s1"}))
    runs.append(hook(repo, "stop", "not json"))
    assert [r.returncode for r in runs] == [1, 0, 1, 1] and all(r.stdout == "" for r in runs)
    assert [len(r.stderr.splitlines()) for r in runs] == [1, 0, 1, 1]
    assert "no '## 2.' LIVE section" in runs[0].stderr and "unreadable ledger" in runs[2].stderr
    assert "no usable session_id" in runs[3].stderr
    assert log_kinds(repo) == ["error"] * 4
    write_ledger(repo, entry("TASK #10 REGISTERED", "2026-09-28 10:0xZ"))
    ok = hook(repo, "stop", {"session_id": "s1"})
    again = hook(repo, "stop", "not json")    # the brief's rule compares with the previous ERROR line, not the last line:
    assert (ok.returncode, ok.stderr) == (0, "")                  # the same error after a success stays silent (report)
    assert (again.returncode, again.stdout, again.stderr) == (0, "", "")
    assert log_kinds(repo) == ["error"] * 4 + ["ok", "error"]


def test_session_start_prints_the_view_in_at_most_12_lines_then_the_newest_error(repo):
    write_ledger(repo, entry("TASKS #1-#15 REGISTERED", "2026-09-28 10:0xZ"), entry("TASK #9 HOME", "2026-09-28 11:0xZ"))
    r = hook(repo, "session-start", {"session_id": "s1", "source": "startup"})
    lines = r.stdout.splitlines()
    assert r.returncode == 0 and r.stderr == "" and len(lines) == 12
    assert lines[0].startswith("Task list = the ledger's view") and "15 open (1 in_progress, 14 pending)" in lines[0]
    assert lines[1].startswith("#9 in_progress t9-") and lines[-1].startswith("+5 more:")
    (repo / "todo" / "BUILD-TASKLIST.md").write_text("# no live section\n")
    r = hook(repo, "session-start", {"session_id": "s1"})
    assert r.returncode == 0 and r.stdout.startswith("task_sync error (newest log line): ")
    assert "no '## 2.' LIVE section" in r.stdout


def test_the_off_switch_makes_both_hooks_inert_and_refuses_apply(repo, tmp_path):
    write_ledger(repo, entry("TASK #10 REGISTERED", "2026-09-28 10:0xZ"))
    (repo / ".jev").mkdir()
    (repo / ".jev" / "task-sync-off").write_text("off until the verify round\n")
    for event, sid in (("stop", "s1"), ("session-start", "s1"), ("stop", "s1"), ("stop", "s2")):
        r = hook(repo, event, {"session_id": sid})
        assert (r.returncode, r.stdout, r.stderr) == (0, "", ""), (event, sid)
    assert not (tmp_path / "config").exists()
    log = (repo / ".jev" / "task-sync" / "sync.log").read_text().splitlines()
    assert [line.split(" ", 3)[1:3] for line in log] == [["off", "session=s1"], ["off", "session=s2"]]
    d = tmp_path / "dir"
    r = sync(repo, d, "--apply", "--allow-dir")
    assert r.returncode == 3 and "off switch set" in r.stderr and not d.exists()
    r = sync(repo, d)
    assert r.returncode == 0 and "  create 10.json t10-" in r.stdout and "off switch" in r.stdout


def test_the_stop_hook_wall_time_on_the_real_ledger(repo, tmp_path):
    shutil.copyfile(REAL_LEDGER, repo / "todo" / "BUILD-TASKLIST.md")
    d = tmp_path / "config" / "tasks" / "timed"
    for n in (289, 295, 297, 308, 310, 313, 315, 316, 317, 318, 319):           # the live dir's shape on 2026-09-28
        harness_file(d, n, f"t{n}-seeded")
    (d / ".highwatermark").write_text("314")
    t0 = time.monotonic()
    r = hook(repo, "stop", {"session_id": "timed"})
    elapsed = time.monotonic() - t0
    assert (r.returncode, r.stdout, r.stderr) == (0, "", ""), r.stderr
    assert elapsed < 10, f"the Stop hook took {elapsed:.2f} s on the real ledger (timeout 30 s)"
    files = view_files(d)
    assert files and all(list(f) == KEYS and f["subject"].startswith(f"t{n}-") for n, f in files.items())
