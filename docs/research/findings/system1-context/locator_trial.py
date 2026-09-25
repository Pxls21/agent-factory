#!/usr/bin/env python3
"""locator_trial.py — S1A evidence demand 5: what each existing tool answers about "where did this first appear",
shown by running it on five registry rows whose first appearance first_seen.py fixed from the records.

Tools and how each is run (read-only toward the tree; every transcript-derived output goes to the scratch folder, is
measured, and is deleted before the script ends; only counts, positions and timestamps are printed):
  hiccup_scan.py   one page over every transcript but this lane's (--out in scratch, never docs/HICCUPS.md)
  chat_tail.py     --export of the transcript that holds the first appearance (user + assistant text), then searched
  jev_locate.py    "<bug text>" in its default lexical order (no Jev call, nothing sent to the Laya server)
  why.sh           on the file the row names (none for AF-AP-154)
  replay_transcript_edits.py  REPLAY_TARGETS=<that file> over every transcript, inside a private mount namespace in
                   which the target path is bind-mounted to a scratch copy, so the replayed writes never reach the tree

Usage: locator_trial.py --scratch DIR [--exclude BASENAME]
"""
import argparse
import collections
import glob
import hashlib
import os
import re
import shutil
import subprocess
import sys
import time

REPO = "/home/user/agent-factory"
ROOT = "/root/.claude/projects"
MAIN = ROOT + "/-home-user/bdab799a-dc80-5933-9c9e-c80f206f9a17.jsonl"
SUB = ROOT + "/-home-user/bdab799a-dc80-5933-9c9e-c80f206f9a17/subagents/"
REPO_MAIN = ROOT + "/-home-user-agent-factory/bdab799a-dc80-5933-9c9e-c80f206f9a17.jsonl"

# row -> (first appearance from first_seen.py, transcript holding it, tokens, bug text for jev_locate, file for why/replay)
ROWS = {
    "AF-AP-154": ("2026-09-23T04:11:20Z subagent a9150cf9f42b052b6 line 131 (first in any transcript: main 2026-09-02T22:30:03Z)",
                  SUB + "agent-a9150cf9f42b052b6.jsonl", ["refusal", "opus-4-8"],
                  "a subagent lane's served model changed from claude-opus-5-5 to claude-opus-4-8 after a refusal stop, mid-run, with no notice",
                  None),
    "AF-AP-181": ("2026-09-24T10:49:55Z main line 113774", MAIN, ["'gone' == 'Z'"],
                  "AssertionError assert 'gone' == 'Z' in a zombie liveness test that reads /proc/<pid>/stat after os.path.exists",
                  "tests/test_s0_01_frame_tee.py"),
    "AF-AP-183": ("2026-09-22T16:45:55Z main (repo-rooted transcript) line 219", REPO_MAIN, ["10,000", "preview"],
                  "the SessionStart hook printed 42298 characters and the model received only a 2 KB preview of it",
                  ".claude/hooks/session-start.sh"),
    "AF-AP-201": ("2026-09-24T23:45:38Z main line 126517", MAIN, ["EngineDeadError"],
                  "EngineDeadError: the shared vLLM model server died after one request option made it allocate outside its memory budget",
                  "docs/research/findings/j2b-variants/qwen27b/transport_probe.py"),
    "AF-AP-209": ("2026-09-25T06:03:40Z subagent a7c113e7a3e1d35cb line 708", SUB + "agent-a7c113e7a3e1d35cb.jsonl",
                  ["ERR_OUT_OF_RANGE", "AbortSignal"],
                  "RangeError ERR_OUT_OF_RANGE from AbortSignal.timeout when the bridge passed a fractional remaining budget in ms",
                  "scripts/jev_pipes/bridge.mjs"),
}


def run(argv, env=None, stdin=None, timeout=600):
    t0 = time.perf_counter()
    p = subprocess.run(argv, cwd=REPO, capture_output=True, env=env, input=stdin, timeout=timeout)
    return p, (time.perf_counter() - t0) * 1000


def sha(path):
    return hashlib.sha256(open(path, "rb").read()).hexdigest()[:12] if os.path.exists(path) else "absent"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--scratch", required=True)
    ap.add_argument("--exclude", action="append", default=[])
    a = ap.parse_args()
    s = a.scratch
    os.makedirs(s, exist_ok=True)
    transcripts = sorted(p for p in glob.glob(ROOT + "/**/*.jsonl", recursive=True)
                         if os.path.basename(p) not in a.exclude and not p.endswith("journal.jsonl"))
    out = collections.defaultdict(dict)

    # 1. hiccup_scan: one page, then what it holds for each row
    page = os.path.join(s, "hiccups.md")
    argv = ["python3", "scripts/hiccup_scan.py", "--out", page]
    for t in transcripts:
        argv += ["--transcript", t]
    p, ms = run(argv)
    text = open(page, errors="replace").read() if os.path.exists(page) else ""
    agents = {}
    sec = None
    for line in text.splitlines():
        if line.startswith("## "):
            sec = line
        elif sec and sec.startswith("## Agents") and line.startswith("|") and not line.startswith("|---"):
            cols = [c.strip() for c in line.split("|")[1:-1]]
            if len(cols) >= 8:
                agents[cols[0]] = cols
    print(f"hiccup_scan: rc {p.returncode}, {ms:.0f} ms, {len(transcripts)} transcripts, page {len(text.encode())} bytes")
    for row, (truth, tr, toks, bug, f) in ROWS.items():
        agent = os.path.basename(tr)[6:-6] if "/subagents/" in tr else None
        a_cols = agents.get(agent)
        hits = {t: text.count(t) for t in toks}
        out[row]["hiccup"] = ("agent row: models [%s], refusal stops %s, first %s, last %s" % (a_cols[2], a_cols[5], a_cols[6], a_cols[7])
                              if a_cols else "no agent row") + "; token hits " + ", ".join(f"{k} {v}" for k, v in hits.items())
    os.remove(page)

    # 2. chat_tail --export of the transcript holding the first appearance, searched for the tokens
    for row, (truth, tr, toks, bug, f) in ROWS.items():
        d = os.path.join(s, "export-" + row)
        os.makedirs(d, exist_ok=True)
        p, ms = run(["python3", "scripts/chat_tail.py", tr, "--export", d])
        res = []
        for tok in toks:
            first, n = None, 0
            for fn in sorted(os.listdir(d)):
                head = None
                for line in open(os.path.join(d, fn), errors="replace"):
                    if line.startswith("## "):
                        m = re.match(r"## (\S+) @ (\S+)", line)
                        head = f"{m.group(1)} {m.group(2)[:19]}Z" if m else "?"
                        continue
                    if tok in line:
                        n += 1
                        first = first or head
            res.append(f"{tok}: {n} hits" + (f", first under {first}" if first else ""))
        size = sum(os.path.getsize(os.path.join(d, x)) for x in os.listdir(d))
        out[row]["chat_tail"] = f"rc {p.returncode}, {ms:.0f} ms, {len(os.listdir(d))} day file(s), {size} bytes; " + "; ".join(res)
        shutil.rmtree(d)

    # 2b. chat_tail on the MAIN transcript for every row: the day view of the first-appearance day, and the export
    d = os.path.join(s, "export-main")
    os.makedirs(d, exist_ok=True)
    run(["python3", "scripts/chat_tail.py", MAIN, "--export", d])
    for row, (truth, tr, toks, bug, f) in ROWS.items():
        day = truth[:10]
        p, ms = run(["python3", "scripts/chat_tail.py", MAIN, "--day", day, "--turns", "10"])
        view = p.stdout.decode("utf-8", "replace")
        res = []
        for tok in toks:
            first, n = None, 0
            for fn in sorted(os.listdir(d)):
                head = None
                for line in open(os.path.join(d, fn), errors="replace"):
                    if line.startswith("## "):
                        m = re.match(r"## (\S+) @ (\S+)", line)
                        head = f"{m.group(1)} {m.group(2)[:19]}Z" if m else "?"
                        continue
                    if tok in line:
                        n += 1
                        first = first or head
            res.append(f"{tok}: {n} hits" + (f", first under {first}" if first else ""))
        out[row]["chat_tail_main"] = (f"day view of {day}: {len(view.splitlines())} lines, token hits "
                                      + ", ".join(f"{t} {view.count(t)}" for t in toks)
                                      + "; main export: " + "; ".join(res))
    shutil.rmtree(d)

    # 3. jev_locate (lexical, no Jev)
    for row, (truth, tr, toks, bug, f) in ROWS.items():
        p, ms = run(["python3", "scripts/jev_locate.py", bug])
        pack = p.stdout.decode("utf-8", "replace")
        ids = sorted(set(re.findall(r"AF-AP-\d+", pack)))
        shas = re.findall(r"\(git log -S", pack)
        out[row]["jev_locate"] = (f"rc {p.returncode}, {ms:.0f} ms, {len(pack.encode())} bytes; names {row}: "
                                  f"{'yes' if row in ids else 'no'}; registry ids named {len(ids)}; "
                                  f"names the row's file: {'yes' if f and f in pack else ('-' if not f else 'no')}; "
                                  f"git-log hits {len(shas)}; transcript positions named: "
                                  f"{len(re.findall(r'[.]jsonl', pack))}")

    # 4. why.sh on the row's file
    for row, (truth, tr, toks, bug, f) in ROWS.items():
        if not f:
            out[row]["why"] = "not run: the row names no file (why.sh needs one)"
            continue
        p, ms = run(["bash", "scripts/why.sh", f])
        w = p.stdout.decode("utf-8", "replace")
        dates = sorted(set(re.findall(r"\b(2026-\d\d-\d\d)\b", w)))
        out[row]["why"] = (f"rc {p.returncode}, {ms:.0f} ms, {len(w.encode())} bytes; dates named {dates[0] if dates else '-'}"
                           f"..{dates[-1] if dates else '-'}; names {row}: {'yes' if row in w else 'no'}; "
                           f"transcript positions named: {len(re.findall(r'[.]jsonl', w))}")

    # 5. replay_transcript_edits.py inside a private mount namespace, target bind-mounted to a scratch copy
    for row, (truth, tr, toks, bug, f) in ROWS.items():
        if not f:
            out[row]["replay"] = "not run: the row names no file (REPLAY_TARGETS needs one)"
            continue
        target = os.path.join(REPO, f)
        before = sha(target)
        copy = os.path.join(s, "replay-copy-" + os.path.basename(f))
        shutil.copyfile(target, copy)
        script = ('mount --bind "$COPY" "$TARGET" && REPLAY_TARGETS="$TARGET" python3 scripts/replay_transcript_edits.py "$@"')
        env = dict(os.environ, COPY=copy, TARGET=target)
        p, ms = run(["unshare", "-m", "--propagation", "private", "bash", "-c", script, "replay"] + transcripts, env=env)
        r = p.stdout.decode("utf-8", "replace").splitlines()
        calls = [re.match(r"^([WEX=]) (\d\d:\d\d:\d\d) ", line) for line in r]
        calls = [m for m in calls if m]
        kinds = collections.Counter(m.group(1) for m in calls)
        done = next((line for line in r if line.startswith("done:")), "(no done line)")
        after = sha(target)
        out[row]["replay"] = (f"rc {p.returncode}, {ms:.0f} ms; {r[0] if r else '(no output)'}; call lines by status "
                              + (", ".join(f"{k} {v}" for k, v in sorted(kinds.items())) or "none")
                              + (f"; first {calls[0].group(1)} at {calls[0].group(2)}, last at {calls[-1].group(2)} (time of day"
                                 f" only, no date)" if calls else "")
                              + f"; `{done}`; real file sha before/after {before}/{after}")
        os.remove(copy)

    print("| row | first appearance (first_seen.py) | hiccup_scan.py | chat_tail.py --export of the transcript holding it | "
          "chat_tail.py on the main transcript (--day view; --export) | jev_locate.py (lexical) | why.sh | "
          "replay_transcript_edits.py |")
    print("|---|---|---|---|---|---|---|---|")
    for row, (truth, *_rest) in ROWS.items():
        o = out[row]
        print(f"| {row} | {truth} | {o['hiccup']} | {o['chat_tail']} | {o['chat_tail_main']} | {o['jev_locate']} | "
              f"{o['why']} | {o['replay']} |")
    return 0


if __name__ == "__main__":
    sys.exit(main())
