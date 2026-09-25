#!/usr/bin/env python3
"""What the harness injections cost in re-sent context (counts only): the task-list reminders at their rendered size, the
instruction files and nested memory at their content length, skill bodies, and the tool, agent, skill and MCP listings at
their record size (an upper bound). Residency = characters / 4.06 x the requests until the next compaction (the P1
seed's formula).

  inject_cost.py TRANSCRIPT.jsonl [...]
"""
import collections, json, os, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[4] / "scripts"))
from jev_pipes import accounting, transcript
resid = collections.Counter(); cnt = collections.Counter(); chars = collections.Counter(); total = 0
for path in sys.argv[1:]:
    limit = os.path.getsize(path); idx = transcript.scan(path, limit, set(), 10 ** 12, lambda s: frozenset())
    total += sum(r.context_tokens for r in idx.requests)
    stats = collections.Counter()
    for off, rec in transcript.iter_records(path, limit, stats):
        a = rec.get("attachment")
        if rec.get("type") != "attachment" or not isinstance(a, dict): continue
        t = a.get("type"); n = 0
        if t == "instructions":
            n = sum(len(f.get("content") or "") for f in a.get("files") or [] if isinstance(f, dict))
        elif t == "nested_memory":
            c = a.get("content"); n = len(c.get("content") or "") if isinstance(c, dict) else 0
        elif t == "invoked_skills":
            n = sum(len(s.get("content") or "") for s in a.get("skills") or [] if isinstance(s, dict))
        elif t == "task_reminder":
            items = a.get("content") or []
            n = 420 + sum(len("#%s. [%s] %s\n" % (i.get("id"), i.get("status"), i.get("subject"))) for i in items if isinstance(i, dict))
        elif t in ("skill_listing", "agent_listing_delta", "deferred_tools_delta", "mcp_instructions_delta", "deferred_tools_record"):
            n = len(json.dumps(a, ensure_ascii=False))   # upper bound: the record
        else:
            continue
        f, _ = idx.following(off)
        cnt[t] += 1; chars[t] += n; resid[t] += accounting.tokens_saved(n, f)
print("re-sent total %d tokens" % total)
for t, v in sorted(resid.items(), key=lambda kv: -kv[1]):
    print("  %-24s n=%6d rendered chars=%11d  residency %13.0f  %5.1f%% of re-sent" % (t, cnt[t], chars[t], v, 100.0 * v / total))
