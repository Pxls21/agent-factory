"""copyable.py: counts only, no text printed. For each tool call in this session's transcripts, how many of its
variable slot values (quoted strings, paths, hex ids, numbers in a Bash command; the file path of Read, Edit and
Write) already appear in the stream before the call: in the last 1, 10 or 50 events (substring), or anywhere earlier
in the same transcript (exact token). The stream is what the S1 view renders: prompts, texts, tool inputs and tool
results; never a thinking block. Each event's text is capped at CAP characters for the window checks."""
import collections, glob, json, re

SID = "bdab799a-dc80-5933-9c9e-c80f206f9a17"
paths = glob.glob(f"/root/.claude/projects/*/{SID}.jsonl") + glob.glob(f"/root/.claude/projects/*/{SID}/subagents/*.jsonl")
CAP = 20000
RX_Q = re.compile(r"'([^']*)'|\"([^\"]*)\"")
RX_P = re.compile(r"(?<![\w-])(?:/|\./|\$\w+/)[\w./@+-]*|\b[\w-]+/[\w./@+-]+")
RX_H = re.compile(r"\b[0-9a-f]{7,64}\b")
RX_N = re.compile(r"\b\d+(?:\.\d+)?\b")
RX_TOK = re.compile(r"[\w./@+$-]+")


def shape(cmd):
    c = re.sub(r"^\s*(cd /home/user/agent-factory\s*&&\s*)", "", cmd)
    c = re.sub(r"\b[A-Z_][A-Z0-9_]*=\S*\s+", "", c)
    c = re.sub(r"'[^']*'|\"[^\"]*\"", "<s>", c)
    c = re.sub(r"(?<![\w-])(/|\./|\$\w+/)[\w./@+-]*", "<p>", c)
    c = re.sub(r"\b[\w-]+/[\w./@+-]+", "<p>", c)
    c = re.sub(r"\b[0-9a-f]{7,64}\b", "<h>", c)
    c = re.sub(r"\b\d+(\.\d+)?\b", "<n>", c)
    c = re.sub(r"\s+", " ", c).strip()
    return c[:200]


def slots(cmd):
    out = []
    c = re.sub(r"^\s*(cd /home/user/agent-factory\s*&&\s*)", "", cmd)
    for m in RX_Q.finditer(c):
        v = m.group(1) if m.group(1) is not None else m.group(2)
        if v:
            out.append(("quoted", v))
    c = RX_Q.sub(" ", c)
    for m in RX_P.finditer(c):
        out.append(("path", m.group(0)))
    c = RX_P.sub(" ", c)
    for m in RX_H.finditer(c):
        out.append(("hex", m.group(0)))
    c = RX_H.sub(" ", c)
    for m in RX_N.finditer(c):
        out.append(("number", m.group(0)))
    return out


def texts_of(r):
    """The stream texts one record adds, in order, and the tool calls it holds."""
    msg = r.get("message") or {}
    content = msg.get("content")
    out, calls = [], []
    if isinstance(content, str):
        out.append(content)
        return out, calls
    for b in content or []:
        if not isinstance(b, dict):
            continue
        t = b.get("type")
        if t == "text":
            out.append(b.get("text") or "")
        elif t == "tool_use":
            calls.append(b)
            inp = b.get("input") or {}
            out.append(inp.get("command") if b.get("name") == "Bash" and isinstance(inp.get("command"), str)
                       else json.dumps(inp, ensure_ascii=False))
        elif t == "tool_result":
            c = b.get("content")
            if isinstance(c, str):
                out.append(c)
            elif isinstance(c, list):
                out.append("\n".join(x.get("text") or "" for x in c if isinstance(x, dict) and x.get("type") == "text"))
    return out, calls


stat = collections.Counter()           # (class, scope) -> count
cmd_full = collections.Counter()      # per Bash command: every slot found in w50 (or no slots)
value_freq = collections.Counter()    # number values across all commands, for constant-like numbers
recs = []                             # per Bash command: (shape, all slots copyable, [(class, len) of new values])
seen = set()
n_bash = n_bash_noslot = n_file = n_bad = 0
for p in paths:
    win = collections.deque(maxlen=50)
    toks = set()
    with open(p, errors="replace") as f:
        for ln in f:
            if '"type":"user"' not in ln and '"type":"assistant"' not in ln:
                continue
            try:
                r = json.loads(ln)
            except Exception:
                n_bad += 1
                continue
            if r.get("type") not in ("user", "assistant"):
                continue
            txts, calls = texts_of(r)
            for b in calls:
                if b.get("id") in seen:
                    continue
                seen.add(b.get("id"))
                name, inp = b.get("name"), b.get("input") or {}
                w1 = win[-1] if win else ""
                w10 = "\n".join(list(win)[-10:])
                w50 = "\n".join(win)
                if name == "Bash" and isinstance(inp.get("command"), str):
                    n_bash += 1
                    ss = slots(inp["command"])
                    if not ss:
                        n_bash_noslot += 1
                    allfound = True
                    newv = []
                    allv = []
                    for cls, v in ss:
                        stat[(cls, "slots")] += 1
                        in50 = v in w50
                        if in50:
                            stat[(cls, "w50")] += 1
                            if v in w10:
                                stat[(cls, "w10")] += 1
                                if v in w1:
                                    stat[(cls, "w1")] += 1
                        if v in toks:
                            stat[(cls, "prefix_token")] += 1
                        allv.append((cls, v, in50 or v in toks))
                        if in50 or v in toks:
                            stat[(cls, "w50_or_prefix")] += 1
                        else:
                            allfound = False
                            newv.append((cls, len(v)))
                        if cls == "number":
                            value_freq[v] += 1
                    cmd_full["all slots in w50 or prefix" if allfound else "some slot new"] += 1
                    recs.append((shape(inp["command"]), allfound, newv, allv))
                elif name in ("Read", "Edit", "Write") and isinstance(inp.get("file_path"), str):
                    n_file += 1
                    v = inp["file_path"]
                    stat[(name, "slots")] += 1
                    if v in w50:
                        stat[(name, "w50")] += 1
                    if v in toks:
                        stat[(name, "prefix_token")] += 1
                    if v in w50 or v in toks:
                        stat[(name, "w50_or_prefix")] += 1
            for t in txts:
                t = t or ""
                win.append(t[:CAP])
                toks.update(RX_TOK.findall(t))

print(f"transcripts={len(paths)} unparsed_lines={n_bad} bash={n_bash} (no slot {n_bash_noslot}) read_edit_write={n_file} cap={CAP}")
for cls in ("quoted", "path", "hex", "number", "Read", "Edit", "Write"):
    n = stat[(cls, "slots")]
    if not n:
        continue
    row = " ".join(f"{s}={100*stat[(cls, s)]/n:5.1f}%" for s in ("w1", "w10", "w50", "prefix_token", "w50_or_prefix"))
    print(f"  {cls:7s} n={n:7d}  {row}")
tot = sum(cmd_full.values())
for k, v in cmd_full.most_common():
    print(f"  bash commands: {k}: {v} ({100*v/max(tot,1):.1f}%)")
common = sum(v for k, v in value_freq.items() if v >= 50)
print(f"  number slot values that recur >=50 times (constant-like): {common} of {sum(value_freq.values())}"
      f" ({100*common/max(sum(value_freq.values()),1):.1f}%)")

shp = collections.Counter(r[0] for r in recs)
for lo, label in ((1, "all commands"), (2, "shape repeats >=2"), (10, "shape repeats >=10"), (50, "shape repeats >=50")):
    sel = [r for r in recs if shp[r[0]] >= lo]
    full = sum(1 for r in sel if r[1])
    onenew = sum(1 for r in sel if len(r[2]) == 1)
    print(f"  {label}: {len(sel)} commands; all slots copyable {full} ({100*full/max(len(sel),1):.1f}%); exactly one new slot {onenew} ({100*onenew/max(len(sel),1):.1f}%)")
for cls in ("quoted", "path"):
    ls = sorted(n for r in recs for c, n in r[2] if c == cls)
    if ls:
        q = lambda f: ls[min(len(ls) - 1, int(f * len(ls)))]
        short = sum(1 for n in ls if n <= 12)
        print(f"  new {cls} values: n={len(ls)} median={q(0.5)} p75={q(0.75)} p90={q(0.9)} chars; <=12 chars {short} ({100*short/len(ls):.1f}%)")

# per shape and slot position: a value seen >= 3 times in that slot is a closed-set value of the form
slotval = collections.Counter()
for r in recs:
    idx = collections.Counter()
    for cls, v, cp in r[3]:
        slotval[(r[0], cls, idx[cls], v)] += 1
        idx[cls] += 1
for lo in (2, 10, 50):
    sel = [r for r in recs if shp[r[0]] >= lo]
    zero = one = 0
    free = []
    for r in sel:
        idx = collections.Counter()
        nfree = 0
        for cls, v, cp in r[3]:
            closed = slotval[(r[0], cls, idx[cls], v)] >= 3
            idx[cls] += 1
            if not cp and not closed:
                nfree += 1
                free.append((cls, len(v)))
        zero += nfree == 0
        one += nfree == 1
    ls = sorted(n for c, n in free)
    q = lambda f: ls[min(len(ls) - 1, int(f * len(ls)))] if ls else 0
    print(f"  form view, shape repeats >={lo}: {len(sel)} commands; no free slot {zero} ({100*zero/max(len(sel),1):.1f}%); "
          f"one free slot {one} ({100*one/max(len(sel),1):.1f}%); free values n={len(ls)} median={q(0.5)} p75={q(0.75)} "
          f"p90={q(0.9)} chars; by class " + ", ".join(f"{k} {v}" for k, v in collections.Counter(c for c, n in free).most_common()))
