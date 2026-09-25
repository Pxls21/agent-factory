"""Every row through the REAL registered PreToolUse command (on the copy): my own fixtures (not the builder's), a fresh
window per row, up to 5 calls until the row is complete; every delivered block checked by the independent oracle."""
import importlib.util, json, sys, uuid
sys.path.insert(0, ".")
import h
spec = importlib.util.spec_from_file_location("s1", str(h.R / ".claude/hooks/system1-context.py"))
s1 = importlib.util.module_from_spec(spec); spec.loader.exec_module(s1)
R = str(h.R)
FIX = {
 "pc-sqlite": h.bash(f"cd {R} && bash {R}/scripts/pc.sh \"echo QUJD | base64 -d > /tmp/q.sql && sqlite3 ~/x.db < /tmp/q.sql\""),
 "pc-podman": h.bash("bash scripts/pc.sh 'podman images --format {{.Repository}}'"),
 "pc-call": h.bash("PC_TIMEOUT=30 bash scripts/pc.sh 'nvidia-smi --query-gpu=memory.used --format=csv'"),
 "pc-lane": h.bash("cd /home/user/agent-factory && bash scripts/pc_lane.sh tasks/briefs/x/Y-brief.md hermes adversarial-verifier"),
 "pc-suite": h.bash("bash scripts/pc_suite.sh launch -n 8 -- tests/test_a.py"),
 "ouroboros": h.bash("IS_SANDBOX=1 timeout 600 python3 scripts/ooo_mcp.py ouroboros_generate_seed '{}'"),
 "push": h.bash("git -C /home/user/agent-factory push origin 1a2b3c4:claude/x"),
 "push-delegate-work": h.bash("git log origin/claude/x..HEAD --oneline && PUSH_BRANCH=claude/x bash scripts/push_clean.sh --lanes-live"),
 "stamp": h.edit("todo/BUILD-TASKLIST.md", "- ledger 17:0xZ: closed"),
 "commit": h.bash("git add -A && git commit -q -m 'x' && git log -1"),
 "commit-increment": h.bash("bash scripts/safe_commit.sh -m 'S1: x' scripts/a.py tests/test_a.py"),
 "proof-regen": h.bash("python3 scripts/proof-runner run --proof S0-03 --venue pc"),
 "vendored-manifest-write": h.bash("mv .claude/plugins /tmp/p && python3 scripts/vendored_manifest.py --write; mv /tmp/p .claude/plugins"),
 "test-vendored-manifest": h.bash("bash scripts/test_summary.sh tests/test_vendored_manifest.py --basetemp /tmp/vm"),
 "test-proof-status": h.bash("bash scripts/test_summary.sh tests/test_proof_status.py"),
 "test-gate": h.bash("python3 -m pytest -q tests/test_x.py -x"),
 "pasted-count": h.write("docs/notes/gate.md", "pytest-summary: 124 passed in 12.69s\n"),
 "anchor-edit": h.bash("python3 scripts/anchor_edit.py todo/BUILD-TASKLIST.md --insert-after '## LIVE' 'x'"),
 "ops-script": h.bash("bash scripts/orient.sh | head -40"),
 "background": h.bash("python3 long.py > /tmp/long.log 2>&1 &\necho started"),
 "pgrep": h.bash("while pgrep -f '[l]ane_gate' >/dev/null; do sleep 5; done"),
 "gitnexus": h.bash("npx gitnexus analyze --skip-agents-md"),
 "codebase-memory": h.bash("/root/.local/bin/codebase-memory-mcp cli trace_path '{}'"),
 "code-review-graph": h.bash("/root/venv-crg/bin/code-review-graph impact scripts/a.py"),
 "graft": h.bash("cd /home/user/agent-factory && graft ask 'who calls plan_tool' --source"),
 "lane-context": h.bash("bash scripts/lane_context.sh -q 'where is the seam' scripts/x.py"),
 "brief": h.write("tasks/briefs/pc/K300-brief.md", "# K300\n"),
 "brief-contract": h.edit("tasks/briefs/system1/L2-brief.md", "## CONTRACT"),
 "research-prompt": h.write("docs/research/prompts/RP-S1.md", "# prompt\n"),
 "live-state": h.edit("wiki/topics/live-state.md", "**2026-09-25 17:0xZ**"),
 "claude-md-gitnexus-block": h.edit("CLAUDE.md", "# GitNexus — Code Intelligence\n> x"),
 "dormant-claim": h.write("docs/research/findings/x/F.md", "The seam is DORMANT: no caller.\n"),
 "test-edit": h.write("tests/test_s1_new.py", "def test_x():\n    assert 1\n"),
 "test-edit-increment": h.edit("harness-ports/tests/test_port.sh", "echo ok"),
 "gate-edit": h.edit("src/agent_factory/policy.py", "return False"),
 "gate-edit-tactics": h.write("scripts/push_when_green.sh", "#!/bin/bash\n"),
 "code-edit": h.edit("harness-ports/bin/qwen-server.sh", "exit 0"),
 "code-edit-guidelines": h.write("proofs/s0_09/check.py", "x = 1\n"),
}
assert set(FIX) == set(h.ROWS), set(h.ROWS) ^ set(FIX)
problems, summary = [], []
for rid, payload in FIX.items():
    sid = "vs1-" + uuid.uuid4().hex[:8]
    payload = dict(payload, session_id=sid)
    row = h.ROWS[rid]
    lines, secs = s1.parse_skill(h.skill_text(row["skill"]))
    want = s1.resolve(row, lines, secs)
    got_by_row, calls, matched = {}, 0, None
    for n in range(6):
        r = h.run(h.PRE, payload); calls += 1
        c = h.ctx(r)
        rec = h.telemetry()[-1]
        if matched is None:
            matched = rec["matched"]
        if rid not in rec["matched"]:
            problems.append((rid, "row did not match its fixture", rec["matched"])); break
        nb = len(c.encode()) if c else 0
        if nb > 2048 or rec["bytes"] != nb:
            problems.append((rid, "bytes", nb, rec["bytes"]))
        try:
            blocks = h.check(c) if c else []
        except AssertionError as e:
            problems.append((rid, "oracle", str(e)[:200])); break
        for brid, skill, heading, idx in blocks:
            if heading != h.ROWS[brid]["heading"] or skill != h.ROWS[brid]["skill"]:
                problems.append((rid, "pointer names the wrong section", brid))
            got_by_row.setdefault(brid, []).extend(idx)
        if not c:
            break
    for brid in matched:
        brow = h.ROWS[brid]
        bl, bs = s1.parse_skill(h.skill_text(brow["skill"]))
        bwant = [i for i in s1.resolve(brow, bl, bs) if bl[i].strip()]
        got = got_by_row.get(brid, [])
        # lines shared with an earlier row of the same skill are delivered once, under that row
        shared = {i for other, idxs in got_by_row.items() if other != brid and h.ROWS[other]["skill"] == brow["skill"] for i in idxs}
        if len(got) != len(set(got)):
            problems.append((rid, brid, "a line delivered twice in one window"))
        missing = [i for i in bwant if i not in got and i not in shared]
        if missing:
            problems.append((rid, brid, "lines never delivered in 6 calls", len(missing)))
        if got != sorted(got):
            problems.append((rid, brid, "out of order"))
    summary.append((rid, len(matched), calls))
    h.wipe_state()
print("rows checked:", len(summary), "| total calls:", sum(c for *_, c in summary))
print("fixtures matching >1 row:", [(r, m) for r, m, c in summary if m > 1])
print("problems:", len(problems))
for p in problems: print("  ", p)
