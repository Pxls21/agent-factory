"""F2 discriminator: which row excerpts start or end inside an entry (the hook's own ENTRY_START_RX). Exit 1 while any do."""
import importlib.util, re, sys
sys.path.insert(0, ".")
import h
spec = importlib.util.spec_from_file_location("s1", str(h.R / ".claude/hooks/system1-context.py"))
s1 = importlib.util.module_from_spec(spec); spec.loader.exec_module(s1)
bad = []
for row in h.TABLE["rows"]:
    L, secs = s1.parse_skill(h.skill_text(row["skill"]))
    idx = s1.resolve(row, L, secs)
    (s, e), = h.sections_of(row["skill"])[1][row["heading"]]
    runs, cur = [], [idx[0]]
    for i in idx[1:]:
        (cur.append(i) if i == cur[-1] + 1 else (runs.append(cur), cur := [i]))
    runs.append(cur)
    for run in runs:
        a, b = run[0], run[-1]
        if not (s1.ENTRY_START_RX.match(L[a]) or not L[a - 1].strip() or re.match(r"#{1,6}\s", L[a - 1])):
            bad.append((row["id"], "starts mid-entry at", a + 1))
        if not (b + 1 >= e or not L[b + 1].strip() or s1.ENTRY_START_RX.match(L[b + 1])):
            bad.append((row["id"], "ends mid-entry at", b + 1))
for x in bad: print(*x)
print(len(bad), "row runs start or end inside an entry")
sys.exit(1 if bad else 0)
