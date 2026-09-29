# K1 authoring probe (D-106, design §10.2 R-B): no-judge quality signals per 100k of context fill in one main-session
# transcript. Segments start at the transcript's own compact_boundary records. Prints counts only, never content.
# Usage: python3 tasks/briefs/jev-trim/k1_authoring_probe.py <session.jsonl>
import json, sys, collections
p = sys.argv[1]
B = collections.defaultdict(collections.Counter)
pending, seen_req, reads = {}, set(), {}
seg, seg_max = 0, collections.Counter()
with open(p) as fh:
    for line in fh:
        if '"compact_boundary"' not in line and '"assistant"' not in line and '"tool_result"' not in line:
            continue
        try:
            r = json.loads(line)
        except Exception:
            continue
        if r.get('type') == 'system' and r.get('subtype') == 'compact_boundary':
            seg += 1
            reads = {}
            continue
        if r.get('isSidechain'):
            continue
        m = r.get('message') or {}
        if r.get('type') == 'assistant':
            u = m.get('usage') or {}
            fill = (u.get('input_tokens') or 0) + (u.get('cache_read_input_tokens') or 0) + (u.get('cache_creation_input_tokens') or 0)
            if not fill:
                continue
            seg_max[seg] = max(seg_max[seg], fill)
            b = min(fill // 100000, 9)
            mid = m.get('id')
            if mid not in seen_req:
                seen_req.add(mid)
                B[b]['requests'] += 1
            for c in m.get('content') or []:
                if not (isinstance(c, dict) and c.get('type') == 'tool_use'):
                    continue
                name, inp = c.get('name'), c.get('input') or {}
                pending[c.get('id')] = (name, b)
                B[b]['calls'] += 1
                if name == 'Read':
                    key = (inp.get('file_path'), inp.get('offset'), inp.get('limit'))
                    B[b]['reads'] += 1
                    if reads.get(key) == 'clean':
                        B[b]['reread_nochange'] += 1
                    reads[key] = 'clean'
                elif name in ('Edit', 'Write'):
                    fp = inp.get('file_path')
                    for k in list(reads):
                        if k[0] == fp:
                            reads[k] = 'changed'
                    B[b]['edits'] += 1
                elif name == 'Bash':
                    B[b]['bash'] += 1
        elif r.get('type') == 'user' and isinstance(m.get('content'), list):
            for x in m['content']:
                if isinstance(x, dict) and x.get('type') == 'tool_result':
                    k = pending.pop(x.get('tool_use_id'), None)
                    if k and x.get('is_error'):
                        name, b = k
                        B[b]['errors'] += 1
                        B[b]['edit_errors' if name in ('Edit', 'Write') else 'bash_errors' if name == 'Bash' else 'other_errors'] += 1
print('segments', seg + 1, 'with requests', len(seg_max), 'segment max fill (k) median', sorted(v // 1000 for v in seg_max.values())[len(seg_max) // 2])
print('bin(k)  requests calls err%  bash_err%  edits edit_err%  reads reread_nochange%')
for b in sorted(B):
    c = B[b]
    pct = lambda a, d: f"{100.0 * c[a] / c[d]:5.1f}" if c[d] else '  n/a'
    print(f"{b*100:4d}-{b*100+100:<4d} {c['requests']:7d} {c['calls']:6d} {pct('errors','calls')}  {pct('bash_errors','bash')}     {c['edits']:5d} {pct('edit_errors','edits')}     {c['reads']:5d} {pct('reread_nochange','reads')}")
