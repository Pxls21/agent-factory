#!/usr/bin/env python3
"""Cost probe for the scripted backend credential screen.

Counts: connect + full send + full read of the response, min of 5 iterations.
Runs its own subprocess backend on an ephemeral port.
Prints /proc/loadavg before and after.

Four columns at 1 / 10 / 100 / 1000 KB:
  ordinary           — a valid chat body
  invalid-UTF-8 hdr  — header with 0x80 0xC0 (fails closed)
  bound-exceeded hdr — header with %25252541 (bound exceeded)
  bound-exceeded body— body content = padding + "-%25252541"
"""
import http.client
import json
import os
import socket
import subprocess
import sys
import tempfile
import time

SERVER = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))))),
    "proofs", "S0-01", "tools", "scripted_backend.py")
TOKEN = "s0-01-upstream-token-0123456789abcdef"
ITERS = 5


def _free_port():
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def _loadavg():
    return open("/proc/loadavg").read().strip()


def _time_request(port, method, path, body_bytes, extra_headers=None):
    """Time connect + send + read. Returns (elapsed_s, status)."""
    t0 = time.monotonic()
    conn = http.client.HTTPConnection("127.0.0.1", port, timeout=60)
    headers = {"Content-Type": "application/json"}
    headers["Authorization"] = f"Bearer {TOKEN}"
    if extra_headers:
        headers.update(extra_headers)
    conn.request(method, path, body=body_bytes, headers=headers)
    resp = conn.getresponse()
    _ = resp.read()
    status = resp.status
    conn.close()
    elapsed = time.monotonic() - t0
    return elapsed, status


def _min_time(port, method, path, body_bytes, extra_headers=None, n=ITERS):
    times = []
    status = None
    for _ in range(n):
        t, s = _time_request(port, method, path, body_bytes, extra_headers)
        times.append(t)
        status = s
    return min(times), status


def main():
    td = tempfile.mkdtemp()
    tf = os.path.join(td, "token.env")
    with open(tf, "w") as f:
        f.write(f"UPSTREAM_TOKEN={TOKEN}\n")
    os.chmod(tf, 0o600)
    rec = os.path.join(td, "rec")
    port = _free_port()
    proc = subprocess.Popen(
        [sys.executable, SERVER, "--port", str(port), "--token-file", tf,
         "--record-dir", rec, "--slow-delay", "0.05",
         "--allow-existing-records"],
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    deadline = time.time() + 10
    while time.time() < deadline:
        try:
            c = http.client.HTTPConnection("127.0.0.1", port, timeout=1)
            c.request("GET", "/healthz")
            r = c.getresponse(); r.read(); c.close()
            if r.status == 200:
                break
        except Exception:
            time.sleep(0.1)

    print(f"load before: {_loadavg()}")
    print(f"{'KB':>6} | {'ordinary':>10} | {'inv-utf8-hdr':>12} | {'bound-hdr':>10} | {'bound-body':>10}")
    print("-" * 65)

    for kb in (1, 10, 100, 1000):
        size = kb * 1024
        # 1. Ordinary: valid chat body with padding INSIDE a JSON string value
        #    (U+0020 is Zs and in _INVIS_PINNED; trailing spaces get stripped
        #    by strip_invis, so padding must be inside a string — D5j-F5).
        pad = "x" * max(0, size - 80)
        body_ord = json.dumps({"model": "s0-01-pong", "messages": [
            {"role": "user", "content": pad}]}).encode()
        t1, s1 = _min_time(port, "POST", "/v1/chat/completions", body_ord)

        # 2. Invalid UTF-8 in header (fail closed, body = ordinary)
        t2, s2 = _min_time(port, "POST", "/v1/chat/completions", body_ord,
                           extra_headers={"X-Trace": "ua-\x80\xc0-probe"})

        # 3. Bound-exceeded in header (body = ordinary)
        t3, s3 = _min_time(port, "POST", "/v1/chat/completions", body_ord,
                           extra_headers={"X-Trace": "%25252541"})

        # 4. Bound-exceeded IN BODY: padding + "-%25252541"
        tail = b'-%25252541"}'
        inner_pad = b"x" * max(0, size - len(tail) - 80)
        body_be = (b'{"model":"s0-01-pong","messages":[],"note":"'
                   + inner_pad + tail)
        t4, s4 = _min_time(port, "POST", "/v1/chat/completions", body_be)

        print(f"{kb:>6} | {t1:>8.3f} {s1} | {t2:>8.3f}  {s2} | {t3:>8.3f} {s3} | {t4:>8.3f} {s4}")

    print(f"load after:  {_loadavg()}")
    proc.terminate()
    proc.wait(timeout=5)


if __name__ == "__main__":
    main()
