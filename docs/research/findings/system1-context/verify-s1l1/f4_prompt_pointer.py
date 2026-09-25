"""F4 discriminator: the best-scoring section's pointer must reach the model. Exit 1 while it does not."""
import sys, uuid
sys.path.insert(0, ".")
import h
h.wipe_state()
c = h.ctx(h.run(h.PROMPT, h.prompt("launch the pc lane with pc_lane.sh and re-attach it later", sid="f4-" + uuid.uuid4().hex[:6])))
rec = h.telemetry()[-1]
best = rec["matched"][0].rsplit(" (", 1)[0]
ok = f"full details: .claude/skills/{best.split(' § ')[0]}/SKILL.md § {best.split(' § ', 1)[1]}" in c
print("best:", best, "| its pointer in additionalContext:", ok, "| skipped:", [(s["key"], s["why"]) for s in rec["skipped"]])
h.wipe_state(); sys.exit(0 if ok else 1)
