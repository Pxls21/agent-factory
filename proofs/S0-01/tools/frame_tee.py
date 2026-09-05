#!/usr/bin/python3
"""stdio proxy: preserve raw ACP JSON-RPC frames between buzz-acp (client) and hermes-acp (agent)."""
import os, sys, subprocess, threading
D = os.environ["S0_01_FRAMEDIR"]; A = os.environ["S0_01_AGENT"]
os.makedirs(D, exist_ok=True)
p = subprocess.Popen([A], stdin=subprocess.PIPE, stdout=subprocess.PIPE)
def pump(src, dst, path, close_dst):
    with open(path, "ab") as f:
        while True:
            line = src.readline()
            if not line:
                break
            f.write(line); f.flush()
            try:
                dst.write(line); dst.flush()
            except BrokenPipeError:
                break
    if close_dst:
        try: dst.close()
        except Exception: pass
ti = threading.Thread(target=pump, args=(sys.stdin.buffer, p.stdin, D + "/frames-client-to-agent.jsonl", True), daemon=True)
to = threading.Thread(target=pump, args=(p.stdout, sys.stdout.buffer, D + "/frames-agent-to-client.jsonl", False), daemon=True)
ti.start(); to.start(); to.join(); p.wait(); sys.exit(p.returncode)
