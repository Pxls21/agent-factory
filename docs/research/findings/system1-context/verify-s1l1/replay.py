"""VERIFY-S1-L1 replay, independent of the builder's replay.py: the main transcript's Write/Edit/Bash tool_use inputs and its
human/task-notification prompts, in file order, through plan_tool / plan_prompt of the COPY of the hook (the functions
main() calls). Prints counts only; never prints or stores transcript text.

Variants (tool path): V0 = the hook as is; V1 = CMD_POS plus while/until/if/elif/!/{ (F1); V2 = heredoc bodies masked
unless a shell reads them (D11, part 1); V3 = V2 plus quoted spans masked unless owned by pc.sh/ssh/eval/`sh -c` (D11)."""
import importlib.util
import json
import re
import statistics
import sys
import time
from collections import Counter, defaultdict
from pathlib import Path

S = Path(__file__).resolve().parent
HOOK = S / "repo" / ".claude" / "hooks" / "system1-context.py"
T = "/root/.claude/projects/-home-user/bdab799a-dc80-5933-9c9e-c80f206f9a17.jsonl"
CUTOFF = sys.argv[1] if len(sys.argv) > 1 else None          # ISO timestamp: stop after the last call at or before it


def load(name):
    spec = importlib.util.spec_from_file_location(name, str(HOOK))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


V = {k: load("s1_" + k) for k in ("V0", "V1", "V2", "V3")}
for _m in V.values():
    _m.ROOT = "/home/user/agent-factory"      # rel_path() reads the module ROOT; the skills and table stay the copy's
V["V1"].CMD_POS = V["V1"].CMD_POS.replace(r"timeout\s+\S+)\s)", r"timeout\s+\S+|while|until|if|elif)\s|!\s|\{\s)")
assert V["V1"].CMD_POS != V["V0"].CMD_POS

HEREDOC = re.compile(r"<<-?\s*(['\"]?)([A-Za-z_][A-Za-z0-9_]*)\1")
SHELL_OWNER = re.compile(r"(?:^|[\s/])(?:bash|sh|zsh|ssh|pc\.sh)\b")
QUOTE_OWNER = re.compile(r"(?:pc\.sh|\bssh\s+\S+|\beval|\b(?:bash|sh|zsh)\s+-\w*c\w*)\s*$")


def mask_heredocs(cmd):
    out = list(cmd)
    for m in HEREDOC.finditer(cmd):
        seg_start = max(cmd.rfind(c, 0, m.start()) for c in ";&|\n(") + 1
        if SHELL_OWNER.search(cmd[seg_start:m.start()]):
            continue
        nl = cmd.find("\n", m.end())
        if nl < 0:
            continue
        pos, delim = nl + 1, m.group(2)
        while pos < len(cmd):
            end = cmd.find("\n", pos)
            end = len(cmd) if end < 0 else end
            if cmd[pos:end].strip("\t") == delim:
                break
            for k in range(pos, end + 1 if end < len(cmd) else end):
                out[k] = "x"                                     # the newline too: a body line is not a command
            pos = end + 1
    return "".join(out)


def mask_quotes(cmd):
    out, i, n = list(cmd), 0, len(cmd)
    while i < n:
        c = cmd[i]
        if c == "\\":
            i += 2
            continue
        if c in "'\"":
            j = i + 1
            while j < n and cmd[j] != c:
                j += 2 if (c == '"' and cmd[j] == "\\") else 1
            seg_start = max(cmd.rfind(s, 0, i) for s in ";&|\n(") + 1
            if not QUOTE_OWNER.search(cmd[seg_start:i]):
                for k in range(i + 1, min(j, n)):
                    out[k] = "x"
            i = j + 1
            continue
        i += 1
    return "".join(out)


orig_positions = V["V0"].command_positions
V["V2"].command_positions = lambda cmd: orig_positions(mask_heredocs(cmd))
V["V3"].command_positions = lambda cmd: orig_positions(mask_quotes(mask_heredocs(cmd)))

TABLES = {k: m.load_table() for k, m in V.items()}
ROWLINES = {}
for row in TABLES["V0"]["rows"]:
    m = V["V0"]
    lines, secs = m.parse_skill(open(m.skill_file(row["skill"]), encoding="utf-8").read())
    ROWLINES[row["id"]] = {m.line_key(row["skill"], lines[i]) for i in m.resolve(row, lines, secs) if lines[i].strip()}

HP = V["V0"].HARNESS_EVENT_PREFIXES
CACHE = str(S / "replay-cache.json")

win = 0
seen = {k: set() for k in V}                 # per variant, the current window's keys (variant A: compact resets)
seenB = set()                                # V0 with resume resets too (variant B)
calls = Counter()
inj_calls = {k: Counter() for k in V}
bytes_tot = Counter()
bytesB = 0
per_call_bytes = []
win_bytes = defaultdict(int)
win_calls = defaultdict(int)
rows = defaultdict(lambda: Counter())
rows_v = {k: Counter() for k in ("V0", "V1", "V2", "V3")}
times = []
diff_calls = {k: 0 for k in ("V1", "V2", "V3")}        # calls whose injected TEXT differs from V0's
rows_touched = defaultdict(set)              # window -> rows injected at least once (V0)
incomplete = Counter()
first_t = last_t = None
resume_runs = 0
prompts = Counter()
pstats = defaultdict(list)
bad = 0


def close_window(w):
    for rid in rows_touched.pop(w, set()):
        if not ROWLINES[rid] <= seen["V0"]:
            incomplete[rid] += 1


def tool_payload(name, inp, cwd):
    return {"hook_event_name": "PreToolUse", "tool_name": name, "tool_input": inp, "cwd": cwd}


with open(T, encoding="utf-8") as fh:
    for line in fh:
        try:
            r = json.loads(line)
        except ValueError:
            bad += 1
            continue
        t = r.get("type")
        ts = r.get("timestamp")
        if CUTOFF and ts and ts > CUTOFF:
            break
        if t == "system" and r.get("subtype") == "compact_boundary":
            close_window(win)
            win += 1
            for k in seen:
                seen[k] = set()
            seenB = set()
            continue
        if t == "attachment":
            a = r.get("attachment") or {}
            if a.get("hookName") == "SessionStart:resume":
                resume_runs += 1
                seenB = set()
            continue
        if t == "user" and r.get("origin") and not r.get("isMeta"):
            c = (r.get("message") or {}).get("content")
            text = c if isinstance(c, str) else "".join(x.get("text", "") for x in c or [] if isinstance(x, dict) and x.get("type") == "text")
            kind = (r.get("origin") or {}).get("kind") if isinstance(r.get("origin"), dict) else "other"
            if CUTOFF is None:
                m = V["V0"]
                ptext, prec, pnew = m.plan_prompt({"prompt": text}, TABLES["V0"], seen["V0"], CACHE)
                prompts[(kind, prec.get("why") or ("injected" if ptext else "nothing"))] += 1
                if ptext:
                    for k in seen:
                        seen[k] |= set(pnew)
                    seenB |= set(pnew)
                    q = m.tokens(text[:m.PROMPT_SCAN_CHARS])
                    best = prec["matched"][0].rsplit(" (", 1)[0]
                    skill, hd = best.split(" § ", 1)
                    lead = (q & m.tokens(hd)) | (q & m.tokens(skill.replace("-", " ")))
                    pstats["lead_size"].append(len(lead))
                    pstats["n_excerpts"].append(len([i for i in prec["injected"]]))
                    pstats["bytes"].append(prec["bytes"])
                    pstats["score"].append(float(prec["matched"][0].rsplit("(", 1)[1].rstrip(")")))
                    pstats["cover"].append(len(q & m.tokens(ptext)) / max(1, len(q)))
                    pstats["budget_skip"].append(any(s["why"] == "budget" for s in prec["skipped"]))
                    pstats["best_injected"].append(any(i["key"] == best for i in prec["injected"]))
                else:
                    if any(s["why"] == "budget" for s in prec.get("skipped", [])):
                        pstats["budget_skip_nothing"].append(1)
            continue
        if t != "assistant":
            continue
        for c in (r.get("message") or {}).get("content") or []:
            if not (isinstance(c, dict) and c.get("type") == "tool_use" and c.get("name") in ("Write", "Edit", "Bash")):
                continue
            name, inp = c["name"], c.get("input")
            if not isinstance(inp, dict):
                continue
            first_t = first_t or ts
            last_t = ts
            calls[name] += 1
            win_calls[win] += 1
            p = tool_payload(name, inp, r.get("cwd"))
            texts = {}
            for k, m in V.items():
                t0 = time.perf_counter()
                text, rec, new = m.plan_tool(p, TABLES[k], seen[k])
                if k == "V0":
                    times.append(time.perf_counter() - t0)
                seen[k] |= set(new)
                texts[k] = text
                for _i in rec["injected"]:
                    rows_v[k][_i["row"]] += 1
                if text:
                    inj_calls[k][name] += 1
                    bytes_tot[k] += rec["bytes"]
                if k == "V0":
                    if text:
                        per_call_bytes.append(rec["bytes"])
                        win_bytes[win] += rec["bytes"]
                    for rid in rec["matched"]:
                        rows[rid]["matched"] += 1
                    for i in rec["injected"]:
                        rows[i["row"]]["injected"] += 1
                        rows_touched[win].add(i["row"])
                        if i.get("cut"):
                            rows[i["row"]]["cut"] += 1
                    for s in rec["skipped"]:
                        rows[s["row"]]["skip_" + s["why"]] += 1
            tB, recB, newB = V["V0"].plan_tool(p, TABLES["V0"], seenB)
            seenB |= set(newB)
            bytesB += recB["bytes"]
            for k in ("V1", "V2", "V3"):
                diff_calls[k] += texts[k] != texts["V0"]
close_window(win)

nwin = win + 1
wb = [win_bytes.get(w, 0) for w in range(nwin)]
wc = [win_calls.get(w, 0) for w in range(nwin)]
q = lambda xs, p: sorted(xs)[int(p * (len(xs) - 1))]
print("cutoff:", CUTOFF, "| bad json lines skipped:", bad)
print("transcript span (first..last Write/Edit/Bash call):", first_t, "..", last_t)
print(f"windows: {nwin} (compact_boundary records: {win}); recorded SessionStart:resume runs: {resume_runs}")
print("calls:", dict(calls), "| total", sum(calls.values()))
for k in V:
    print(f"{k}: calls that received an injection: {dict(inj_calls[k])} total {sum(inj_calls[k].values())} | injected bytes {bytes_tot[k]}")
print("V0 variant B (+ resume resets) bytes:", bytesB)
print("bytes per injected call: median", statistics.median(per_call_bytes), "max", max(per_call_bytes))
print(f"bytes per window (A, {nwin} windows): median {statistics.median(wb)}, p90(index) {q(wb, .9)}, max {max(wb)}, windows with none {sum(1 for x in wb if not x)}")
print("Write/Edit/Bash calls per window: median", statistics.median(wc), "max", max(wc))
print("calls whose injected text differs from V0:", diff_calls)
ms = sorted(x * 1000 for x in times)
print(f"V0 plan_tool in-process ms: median {statistics.median(ms):.2f} p99 {q(ms, .99):.2f} max {ms[-1]:.1f} | over 50 ms {sum(1 for x in ms if x > 50)} over 100 ms {sum(1 for x in ms if x > 100)} over 500 ms {sum(1 for x in ms if x > 500)}")
print("per situation row (matched / injected / cut / skipped duplicate / skipped budget / skipped unresolved):")
for row in TABLES["V0"]["rows"]:
    c = rows[row["id"]]
    print(f"  {row['id']:28s} {c['matched']:6d} {c['injected']:6d} {c['cut']:5d} {c['skip_duplicate']:6d} {c['skip_budget']:6d} {c['skip_unresolved']:4d}")
print("windows where a row was injected but some of its lines never arrived before the window closed:", sum(incomplete.values()),
      "| by row:", dict(incomplete.most_common()))
if CUTOFF is None:
    print("prompts (origin kind, outcome):", dict(prompts))
    if pstats["lead_size"]:
        ls = Counter(pstats["lead_size"])
        print("injected prompts:", len(pstats["lead_size"]), "| lead tokens per best section:", dict(sorted(ls.items())),
              "| excerpts per prompt:", dict(Counter(pstats["n_excerpts"])),
              "| bytes median", statistics.median(pstats["bytes"]), "max", max(pstats["bytes"]))
        print("  share of the prompt's tokens found in the injected text: median %.2f, prompts under 0.10: %d, under 0.20: %d" % (
            statistics.median(pstats["cover"]), sum(1 for x in pstats["cover"] if x < .10), sum(1 for x in pstats["cover"] if x < .20)))
        print("  best score: median %.1f; scores under 15: %d" % (statistics.median(pstats["score"]), sum(1 for x in pstats["score"] if x < 15)))
        print("  prompts whose best section was NOT injected:", sum(1 for x in pstats["best_injected"] if not x),
              "| of them a budget skip:", sum(1 for x, y in zip(pstats["best_injected"], pstats["budget_skip"]) if not x and y),
              "| prompts injecting nothing because of a budget skip:", len(pstats["budget_skip_nothing"]))

print("per-row injections V0 -> V1 (keywords) / V2 (heredocs masked) / V3 (heredocs+quotes masked), rows that differ:")
for row in TABLES["V0"]["rows"]:
    rid = row["id"]; a = rows_v["V0"][rid]
    if any(rows_v[k][rid] != a for k in ("V1", "V2", "V3")):
        print(f"  {rid:26s} {a:5d} -> {rows_v['V1'][rid]:5d} / {rows_v['V2'][rid]:5d} / {rows_v['V3'][rid]:5d}")
