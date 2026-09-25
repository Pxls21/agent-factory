"""F1 discriminator: the pgrep row must fire on a `while pgrep` wait loop. Exit 1 while it does not."""
import sys, uuid
sys.path.insert(0, ".")
import h
h.wipe_state()
c = h.ctx(h.run(h.PRE, h.bash("while pgrep -f '[l]ane_gate' >/dev/null; do sleep 5; done", sid="f1-" + uuid.uuid4().hex[:6])))
ok = "[system1 · pgrep]" in c
print("pgrep row on `while pgrep …`:", "injected" if ok else "NOT injected", "| matched:", h.telemetry()[-1]["matched"])
h.wipe_state(); sys.exit(0 if ok else 1)
