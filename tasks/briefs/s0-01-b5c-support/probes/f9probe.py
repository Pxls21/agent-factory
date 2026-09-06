import json, os, pathlib, subprocess, sys, textwrap
# PROBE_WORK: the work dir holding base/ (a copy or symlink of the tree under test) — sandbox default below.
_VB6 = os.environ.get("PROBE_WORK", "/tmp/claude-0/-home-user/bdab799a-dc80-5933-9c9e-c80f206f9a17/scratchpad/vb6")

TEE = os.environ.get("PROBE_TEE", _VB6 + "/base/proofs/S0-01/tools/frame_tee.py")
W = pathlib.Path(_VB6 + "/f9work")
AG = """
    import os, sys, json
    line = sys.stdin.readline()
    sys.stdout.write(json.dumps({"jsonrpc":"2.0","id":1,"result":{}}, separators=(",",":")) + chr(10))
    sys.stdout.flush()
    os._exit(0)
"""
def one(i, n):
    d = W / str(i)
    subprocess.run(["rm","-rf",str(d)]); d.mkdir(parents=True)
    fd = d/"frames"; fd.mkdir()
    a = d/"agent.py"; a.write_text("#!%s\n"%sys.executable+textwrap.dedent(AG)); a.chmod(0o755)
    e = os.environ.copy(); e["S0_01_FRAMEDIR"]=str(fd); e["S0_01_AGENT"]=str(a); e["PYTHONDONTWRITEBYTECODE"]="1"
    payload = b"".join((json.dumps({"jsonrpc":"2.0","id":k,"method":"m","params":{}},separators=(",",":"))+"\n").encode() for k in range(n))
    r = subprocess.run([sys.executable,TEE], input=payload, capture_output=True, env=e, timeout=60)
    st = json.loads((fd/"tee-status.json").read_text())
    return r.returncode, st["recorded_c2a"], st["forwarded_c2a"], st["drained"], len(st["write_errors"])
if __name__ == "__main__":
    n = int(sys.argv[1]); trials = int(sys.argv[2])
    rcs = {}
    for i in range(trials):
        rc, rec, fwd, dr, ne = one(i, n)
        rcs[rc] = rcs.get(rc,0)+1
        if i < 4: print("  trial %d rc=%d rec_c2a=%d fwd_c2a=%d drained=%s errs=%d" % (i, rc, rec, fwd, dr, ne))
    print("n=%d trials=%d rc distribution: %s  (the suite's F9 test asserts rc==70)" % (n, trials, rcs))
