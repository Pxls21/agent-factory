#!/usr/bin/env python3
"""Direct behavioural probes against the SHIPPED frame_tee.py (read-only on the shared tree;
all writes go to this scratch dir)."""
import json, os, pathlib, subprocess, sys, textwrap, time

# PROBE_WORK: the work dir holding base/ (a copy or symlink of the tree under test) — sandbox default below.
_VB6 = os.environ.get("PROBE_WORK", "/tmp/claude-0/-home-user/bdab799a-dc80-5933-9c9e-c80f206f9a17/scratchpad/vb6")

TEE = os.environ.get("PROBE_TEE", _VB6 + "/base/proofs/S0-01/tools/frame_tee.py")
WORK = pathlib.Path(_VB6 + "/probework")
WORK.mkdir(parents=True, exist_ok=True)


def newdir(name):
    d = WORK / name
    if d.exists():
        subprocess.run(["rm", "-rf", str(d)])
    d.mkdir(parents=True)
    return d


def agent(d, code):
    p = d / "agent.py"
    p.write_text("#!%s\n" % sys.executable + textwrap.dedent(code))
    p.chmod(0o755)
    return p


def env_for(framedir, agent_path, **extra):
    e = os.environ.copy()
    e["S0_01_FRAMEDIR"] = str(framedir)
    e["S0_01_AGENT"] = str(agent_path)
    e["PYTHONDONTWRITEBYTECODE"] = "1"
    e.update(extra)
    return e


def p1_dangling_symlink():
    d = newdir("p1")
    fd = d / "frames"
    os.symlink(str(d / "nonexistent-target"), str(fd))
    a = agent(d, "import sys\nsys.exit(0)\n")
    r = subprocess.run([sys.executable, TEE], input=b"", capture_output=True,
                       env=env_for(fd, a), timeout=30)
    print("P1 dangling-symlink FRAMEDIR: rc=%d" % r.returncode)
    print("   stderr: %r" % r.stderr.decode()[-400:])


def p1b_symlink_to_file():
    d = newdir("p1b")
    tgt = d / "afile"
    tgt.write_text("x")
    fd = d / "frames"
    os.symlink(str(tgt), str(fd))
    a = agent(d, "import sys\nsys.exit(0)\n")
    r = subprocess.run([sys.executable, TEE], input=b"", capture_output=True,
                       env=env_for(fd, a), timeout=30)
    print("P1b symlink->file FRAMEDIR: rc=%d stderr=%r" % (r.returncode, r.stderr.decode().strip()[:200]))


def p1c_unwritable_parent():
    d = newdir("p1c")
    par = d / "ro"
    par.mkdir()
    os.chmod(str(par), 0o500)
    fd = par / "frames"
    a = agent(d, "import sys\nsys.exit(0)\n")
    try:
        r = subprocess.run([sys.executable, TEE], input=b"", capture_output=True,
                           env=env_for(fd, a), timeout=30)
        print("P1c unwritable parent: rc=%d" % r.returncode)
        print("   stderr tail: %r" % r.stderr.decode()[-300:])
    finally:
        os.chmod(str(par), 0o700)


def p2_c2a_inflight_race(trials=5):
    """Agent exits but a grandchild keeps proc.stdin's read end open, so c2a writes
    still succeed. Client keeps streaming. Does the tee report drained=false / exit 70
    on a run where nothing was actually lost by a write failure?"""
    results = []
    for i in range(trials):
        d = newdir("p2_%d" % i)
        fd = d / "frames"
        fd.mkdir()
        a = agent(d, """
            import subprocess, sys, os, time
            # grandchild inherits fd 0 (read end of the tee->agent pipe) and holds it open
            subprocess.Popen([sys.executable, "-c", "import time; time.sleep(20)"])
            sys.stdout.write('{"jsonrpc":"2.0","id":1,"result":{}}\\n')
            sys.stdout.flush()
            time.sleep(0.15)
            os._exit(0)
        """)
        line = json.dumps({"jsonrpc": "2.0", "id": 1, "method": "m", "params": {"p": "y" * 200}},
                          separators=(",", ":")) + "\n"
        payload = (line * 4000).encode()
        r = subprocess.run([sys.executable, TEE], input=payload, capture_output=True,
                           env=env_for(fd, a), timeout=60)
        st = json.loads((fd / "tee-status.json").read_text())
        results.append((r.returncode, st["drained"], st["forwarded_c2a"], st["recorded_c2a"],
                        len(st["write_errors"]), st["write_errors"][:1]))
    for i, row in enumerate(results):
        print("P2 trial %2d rc=%3d drained=%-5s fwd_c2a=%-6d rec_c2a=%-6d n_err=%-3d %s"
              % (i, row[0], row[1], row[2], row[3], row[4], row[5]))
    n70 = sum(1 for r in results if r[0] == 70)
    noerr70 = sum(1 for r in results if r[0] == 70 and r[4] == 0)
    print("P2 SUMMARY: exit70=%d/%d ; exit70-with-EMPTY-write_errors=%d/%d"
          % (n70, trials, noerr70, trials))


def p4_stdout_enospc():
    """Forward-path OSError that is NOT BrokenPipeError: tee stdout -> /dev/full."""
    d = newdir("p4")
    fd = d / "frames"
    fd.mkdir()
    a = agent(d, """
        import sys, json
        sys.stdin.readline()
        sys.stdout.write('{"jsonrpc":"2.0","id":1,"result":{}}\\n')
        sys.stdout.flush()
        sys.exit(0)
    """)
    with open("/dev/full", "wb") as devfull:
        r = subprocess.run([sys.executable, TEE],
                           input=json.dumps({"jsonrpc": "2.0", "id": 1, "method": "initialize",
                                             "params": {}}, separators=(",", ":")).encode() + b"\n",
                           stdout=devfull, stderr=subprocess.PIPE,
                           env=env_for(fd, a), timeout=30)
    st = json.loads((fd / "tee-status.json").read_text())
    print("P4 stdout=/dev/full: rc=%d status=%s" % (r.returncode, json.dumps(st)))
    print("   stderr tail: %r" % r.stderr.decode()[-300:])


def p5_recorded_vs_timeline():
    """A21: recorded counts must equal the timeline's per-direction counts.
    Probe with an empty line, a partial last line and a CRLF line."""
    d = newdir("p5")
    fd = d / "frames"
    fd.mkdir()
    a = agent(d, """
        import sys
        data = sys.stdin.read()
        sys.stdout.write('{"a":1}\\n')
        sys.stdout.write('\\n')
        sys.stdout.write('{"b":2}')   # partial last line, no terminator
        sys.stdout.flush()
        sys.exit(0)
    """)
    payload = b'{"c":1}\n\n{"d":2}\r\n{"e":3}'
    r = subprocess.run([sys.executable, TEE], input=payload, capture_output=True,
                       env=env_for(fd, a), timeout=30)
    tl = [json.loads(l) for l in (fd / "timeline.jsonl").read_bytes().split(b"\n") if l.strip()]
    st = json.loads((fd / "tee-status.json").read_text())
    per = {}
    for e in tl:
        per[e["dir"]] = per.get(e["dir"], 0) + 1
    print("P5 rc=%d timeline per-dir=%s status recorded c2a=%d a2c=%d  drained=%s errs=%s"
          % (r.returncode, per, st["recorded_c2a"], st["recorded_a2c"], st["drained"], st["write_errors"]))
    print("   MATCH c2a=%s a2c=%s" % (per.get("c2a", 0) == st["recorded_c2a"],
                                      per.get("a2c", 0) == st["recorded_a2c"]))
    print("   raw timeline entries: %s" % json.dumps([{k: e[k] for k in ("seq", "dir") if k in e} | ({"raw": e["raw"]} if "raw" in e else {"frame": e["frame"]}) for e in tl]))


def p6_signal_leg_contract():
    """A21 says exit_code == agent_returncode. Probe a SIGTERM'd agent."""
    d = newdir("p6")
    fd = d / "frames"
    fd.mkdir()
    a = agent(d, """
        import os, signal, sys
        sys.stdin.readline()
        sys.stdout.write('{"jsonrpc":"2.0","id":1,"result":{}}\\n')
        sys.stdout.flush()
        os.kill(os.getpid(), signal.SIGTERM)
    """)
    r = subprocess.run([sys.executable, TEE],
                       input=b'{"jsonrpc":"2.0","id":1,"method":"initialize","params":{}}\n',
                       capture_output=True, env=env_for(fd, a), timeout=30)
    st = json.loads((fd / "tee-status.json").read_text())
    print("P6 SIGTERM leg: tee rc=%d  agent_returncode=%s exit_code=%s  A21(exit_code==agent_returncode)=%s"
          % (r.returncode, st["agent_returncode"], st["exit_code"],
             st["exit_code"] == st["agent_returncode"]))



def p7_client_never_closes_clean():
    """Production shape: client holds stdin open, sends nothing more; agent exits 0.
    Contract expectation: rc == agent rc, drained true, write_errors []."""
    for i in range(5):
        d = newdir("p7_%d" % i)
        fd = d / "frames"; fd.mkdir()
        a = agent(d, """
            import sys, json
            sys.stdin.readline()
            sys.stdout.write('{"jsonrpc":"2.0","id":1,"result":{}}\\n')
            sys.stdout.flush()
            sys.exit(0)
        """)
        holder = d / "holder.py"
        holder.write_text("import sys,time\nsys.stdout.write('{\"jsonrpc\":\"2.0\",\"id\":1,\"method\":\"m\",\"params\":{}}\\n')\nsys.stdout.flush()\ntime.sleep(20)\n")
        hp = subprocess.Popen([sys.executable, str(holder)], stdout=subprocess.PIPE)
        tp = subprocess.Popen([sys.executable, TEE], stdin=hp.stdout, stdout=subprocess.PIPE,
                              stderr=subprocess.PIPE, env=env_for(fd, a))
        hp.stdout.close()
        tp.wait(timeout=30)
        tp.stdout.read(); tp.stderr.read()
        tp.stdout.close(); tp.stderr.close()
        hp.kill(); hp.wait(timeout=5)
        st = json.loads((fd / "tee-status.json").read_text())
        print("P7 trial %d rc=%d drained=%s stdin_done=%s c2a %d/%d a2c %d/%d errs=%s"
              % (i, tp.returncode, st["drained"], st["stdin_reader_done"],
                 st["forwarded_c2a"], st["recorded_c2a"], st["forwarded_a2c"], st["recorded_a2c"],
                 st["write_errors"]))


def p8_client_streams_while_agent_exits(trials=8):
    """Agent consumes c2a frames then exits normally while the client is still streaming."""
    for i in range(trials):
        d = newdir("p8_%d" % i)
        fd = d / "frames"; fd.mkdir()
        a = agent(d, """
            import sys, os
            n = 0
            for line in sys.stdin:
                n += 1
                if n >= 50:
                    break
            sys.stdout.write('{"jsonrpc":"2.0","id":1,"result":{}}\\n')
            sys.stdout.flush()
            os._exit(0)
        """)
        line = json.dumps({"jsonrpc": "2.0", "id": 1, "method": "m", "params": {}},
                          separators=(",", ":")) + "\n"
        payload = (line * 5000).encode()
        r = subprocess.run([sys.executable, TEE], input=payload, capture_output=True,
                           env=env_for(fd, a), timeout=60)
        st = json.loads((fd / "tee-status.json").read_text())
        print("P8 trial %d rc=%3d drained=%-5s c2a %d/%d n_err=%d first=%s"
              % (i, r.returncode, st["drained"], st["forwarded_c2a"], st["recorded_c2a"],
                 len(st["write_errors"]), st["write_errors"][:1]))




def p9_late_client_frame(trials=3, delay=1.0):
    """R5-B5-F1 shape (and the shape of the DELETED round-5 test
    TestAgentExitsWhileStdinOpen::test_tee_exits_cleanly_with_agent_code):
    client writes frame 1, sleeps `delay`, writes frame 2; the agent reads frame 1,
    replies and exits.  Frame 2 MUST be recorded in frames-client-to-agent.jsonl
    or the tee must exit 70."""
    for i in range(trials):
        d = newdir("p9_%d" % i)
        fd = d / "frames"; fd.mkdir()
        a = agent(d, """
            import sys, json
            line = sys.stdin.readline()
            sys.stdout.write('{"jsonrpc":"2.0","id":1,"result":{}}\\n')
            sys.stdout.flush()
            sys.exit(0)
        """)
        helper = d / "helper.py"
        helper.write_text(
            "import sys, time, json\n"
            "f1 = json.dumps({'jsonrpc':'2.0','id':1,'method':'initialize','params':{}})\n"
            "sys.stdout.buffer.write(f1.encode() + b'\\n'); sys.stdout.buffer.flush()\n"
            "time.sleep(%r)\n"
            "f2 = json.dumps({'jsonrpc':'2.0','id':2,'method':'late','params':{}})\n"
            "try:\n"
            "    sys.stdout.buffer.write(f2.encode() + b'\\n'); sys.stdout.buffer.flush()\n"
            "except BrokenPipeError:\n"
            "    sys.stderr.write('frame2 EPIPE\\n')\n"
            "time.sleep(20)\n" % delay)
        t0 = time.monotonic()
        hp = subprocess.Popen([sys.executable, str(helper)], stdout=subprocess.PIPE,
                              stderr=subprocess.PIPE)
        tp = subprocess.Popen([sys.executable, TEE], stdin=hp.stdout, stdout=subprocess.PIPE,
                              stderr=subprocess.PIPE, env=env_for(fd, a))
        hp.stdout.close()
        tp.wait(timeout=60)
        elapsed = time.monotonic() - t0
        tp.stdout.close(); tp.stderr.close()
        hp.kill(); hp.wait(timeout=5)
        c2a = (fd / "frames-client-to-agent.jsonl").read_bytes()
        sent = 2
        got = sum(1 for l in c2a.split(b"\n") if l.strip())
        stp = fd / "tee-status.json"
        st = json.loads(stp.read_text()) if stp.exists() else {}
        ok = (got == sent) or tp.returncode == 70
        print("P9 trial %d rc=%-3d elapsed=%4.1fs client sent %d c2a frames, evidence has %d | "
              "drained=%s stdin_done=%s errs=%s rec_c2a=%s fwd_c2a=%s | CONTRACT_OK=%s"
              % (i, tp.returncode, elapsed, sent, got, st.get("drained"),
                 st.get("stdin_reader_done"), st.get("write_errors"),
                 st.get("recorded_c2a"), st.get("forwarded_c2a"), ok))


def p10_torn_status(trials=3):
    """A21d invariant: every timeline seq increment is paired, under the SAME lock,
    with a recorded_<dir> increment, so any consistent status must satisfy
    updated_seq == recorded_c2a + recorded_a2c.  _write_status() does NOT take that
    lock, so a concurrent reader (= the real checker reading a SIGKILLed leg's last
    running status) can observe a torn snapshot."""
    for i in range(trials):
        d = newdir("p10_%d" % i)
        fd = d / "frames"; fd.mkdir()
        a = agent(d, """
            import sys, json
            n = 0
            for line in sys.stdin:
                n += 1
                sys.stdout.write('{"jsonrpc":"2.0","id":%d,"result":{}}\\n' % n)
                sys.stdout.flush()
                if n >= 4000:
                    break
            sys.exit(0)
        """)
        line = json.dumps({"jsonrpc": "2.0", "id": 1, "method": "m", "params": {}},
                          separators=(",", ":")) + "\n"
        payload = (line * 4000).encode()
        tp = subprocess.Popen([sys.executable, TEE], stdin=subprocess.PIPE,
                              stdout=subprocess.DEVNULL, stderr=subprocess.PIPE,
                              env=env_for(fd, a))
        import threading
        torn = [0]; reads = [0]; worst = [None]
        stop = threading.Event()
        stp = fd / "tee-status.json"

        def reader():
            while not stop.is_set():
                try:
                    s = json.loads(stp.read_text())
                except Exception:
                    continue
                reads[0] += 1
                if s["updated_seq"] != s["recorded_c2a"] + s["recorded_a2c"]:
                    torn[0] += 1
                    if worst[0] is None:
                        worst[0] = {k: s[k] for k in ("updated_seq", "recorded_c2a",
                                                      "recorded_a2c", "forwarded_c2a",
                                                      "forwarded_a2c")}
        th = threading.Thread(target=reader, daemon=True); th.start()
        tp.stdin.write(payload); tp.stdin.close()
        tp.wait(timeout=120)
        stop.set(); th.join(timeout=5)
        tp.stderr.close()
        print("P10 trial %d rc=%d reads=%d TORN(updated_seq != recorded_c2a+recorded_a2c)=%d first=%s"
              % (i, tp.returncode, reads[0], torn[0], worst[0]))


def p11_sigterm_a21b():
    """A21d: 'when final, A21b' (exit_code == agent_returncode, or 128+sig).
    The F4 SIGTERM handler writes final=true with exit_code 70 and whatever
    proc.poll() returns."""
    d = newdir("p11")
    fd = d / "frames"; fd.mkdir()
    a = agent(d, """
        import sys, json
        for line in sys.stdin:
            sys.stdout.write('{"jsonrpc":"2.0","id":1,"result":{}}\\n')
            sys.stdout.flush()
        sys.exit(0)
    """)
    tp = subprocess.Popen([sys.executable, TEE], stdin=subprocess.PIPE,
                          stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=env_for(fd, a))
    tp.stdin.write(b'{"jsonrpc":"2.0","id":1,"method":"m","params":{}}\n'); tp.stdin.flush()
    stp = fd / "tee-status.json"
    deadline = time.monotonic() + 15
    while time.monotonic() < deadline:
        if stp.exists():
            try:
                if json.loads(stp.read_text()).get("updated_seq", 0) >= 1:
                    break
            except Exception:
                pass
        time.sleep(0.05)
    tp.terminate()
    tp.wait(timeout=15)
    tp.stdin.close(); tp.stdout.close(); tp.stderr.close()
    st = json.loads(stp.read_text())
    a21b_ok = (st["exit_code"] == st["agent_returncode"]) if (st["agent_returncode"] is not None and st["agent_returncode"] >= 0) \
        else (st["agent_returncode"] is not None and st["exit_code"] == 128 + (-st["agent_returncode"]))
    print("P11 SIGTERM'd tee: rc=%d final=%s agent_returncode=%s exit_code=%s -> A21b_HOLDS=%s"
          % (tp.returncode, st["final"], st["agent_returncode"], st["exit_code"], a21b_ok))
    print("   full status: %s" % json.dumps(st))


def p12_no_status_before_first_frame():
    """A21d makes tee-status.json a RUNNING status because the real client SIGKILLs
    the process group.  Is the file present before the first frame is forwarded?"""
    d = newdir("p12")
    fd = d / "frames"; fd.mkdir()
    a = agent(d, "import sys, time\ntime.sleep(30)\n")
    tp = subprocess.Popen([sys.executable, TEE], stdin=subprocess.PIPE,
                          stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=env_for(fd, a))
    t0 = time.monotonic()
    ident = fd / "runtime-identity.json"
    while time.monotonic() - t0 < 10 and not ident.exists():
        time.sleep(0.02)
    time.sleep(1.0)
    present = (fd / "tee-status.json").exists()
    listing = sorted(p.name for p in fd.iterdir())
    tp.kill(); tp.wait(timeout=10)
    tp.stdin.close(); tp.stdout.close(); tp.stderr.close()
    print("P12 after identity written + 1s, tee-status.json present=%s ; framedir=%s"
          % (present, listing))


def p13_unbounded_write_errors():
    """R5-B5-F6: is write_errors bounded?  The forward arms now latch on
    forward_broken, but the DIRECTIONAL and TIMELINE arms append per frame."""
    d = newdir("p13")
    fd = d / "frames"; fd.mkdir()
    os.symlink("/dev/full", str(fd / "frames-client-to-agent.jsonl"))
    a = agent(d, """
        import sys
        sys.stdin.read()
        sys.exit(0)
    """)
    line = json.dumps({"jsonrpc": "2.0", "id": 1, "method": "m", "params": {}},
                      separators=(",", ":")) + "\n"
    n = 2000
    r = subprocess.run([sys.executable, TEE], input=(line * n).encode(), capture_output=True,
                       env=env_for(fd, a), timeout=120)
    st = json.loads((fd / "tee-status.json").read_text())
    size = (fd / "tee-status.json").stat().st_size
    uniq = len(set(st["write_errors"]))
    print("P13 %d frames onto a failing directional file: rc=%d len(write_errors)=%d unique=%d "
          "tee-status.json=%d bytes" % (n, r.returncode, len(st["write_errors"]), uniq, size))



def p13b_write_errors_scaling():
    """R5-B5-F6 residue: the DIRECTIONAL arm appends one write_error per frame with
    no latch, and _write_status re-serialises the whole list after every frame ->
    O(n^2).  Measure wall time and list length vs frame count."""
    for n in (100, 200, 400, 800):
        d = newdir("p13b_%d" % n)
        fd = d / "frames"; fd.mkdir()
        os.symlink("/dev/full", str(fd / "frames-client-to-agent.jsonl"))
        a = agent(d, "import sys\nsys.stdin.read()\nsys.exit(0)\n")
        line = json.dumps({"jsonrpc": "2.0", "id": 1, "method": "m", "params": {}},
                          separators=(",", ":")) + "\n"
        t0 = time.monotonic()
        try:
            r = subprocess.run([sys.executable, TEE], input=(line * n).encode(),
                               capture_output=True, env=env_for(fd, a), timeout=300)
            rc = r.returncode
        except subprocess.TimeoutExpired:
            rc = "TIMEOUT"
        el = time.monotonic() - t0
        stp = fd / "tee-status.json"
        st = json.loads(stp.read_text()) if stp.exists() else {"write_errors": []}
        print("P13b n=%4d rc=%-7s wall=%7.2fs len(write_errors)=%5d status_bytes=%8d"
              % (n, rc, el, len(st["write_errors"]), stp.stat().st_size if stp.exists() else -1))


def p14_status_cost_11_frames(trials=5):
    """Cost of the per-frame atomic rewrite on the 11-frame real-leg shape:
    with the rewrite vs with the rewrite disabled (a scratch-copy mutant is used
    by the caller; here we just time the shipped tee)."""
    for i in range(trials):
        d = newdir("p14_%d" % i)
        fd = d / "frames"; fd.mkdir()
        a = agent(d, """
            import sys, json
            n = 0
            for line in sys.stdin:
                n += 1
                sys.stdout.write('{"jsonrpc":"2.0","id":%d,"result":{}}\\n' % n)
                sys.stdout.flush()
            sys.exit(0)
        """)
        line = json.dumps({"jsonrpc": "2.0", "id": 1, "method": "session/prompt",
                           "params": {"p": "x" * 100}}, separators=(",", ":")) + "\n"
        payload = (line * 6).encode()   # 6 c2a + 6 a2c = 12 frames ~ the 11-frame leg
        t0 = time.monotonic()
        r = subprocess.run([sys.executable, TEE], input=payload, capture_output=True,
                           env=env_for(fd, a), timeout=60)
        el = time.monotonic() - t0
        st = json.loads((fd / "tee-status.json").read_text())
        print("P14 trial %d rc=%d wall=%6.3fs frames=%d status_writes>=%d"
              % (i, r.returncode, el, st["recorded_c2a"] + st["recorded_a2c"],
                 st["recorded_c2a"] + st["recorded_a2c"]))

if __name__ == "__main__":
    for n in sys.argv[1:]:
        globals()[n]()
