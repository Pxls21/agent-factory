"""scripts/gpu_window.sh: the guarded GPU window (task #242; D-078, D-081).

The script runs on the PC and drives systemd, nvidia-smi and the vLLM /v1/models endpoint. Here those are replaced at the
system boundary only: PATH shims for `systemctl` (a state file stands in for the unit) and `nvidia-smi` (a number), and a
loopback HTTP server that answers /v1/models 200 only while the unit is "active" AND the request carries the right bearer
key. `curl` is the REAL curl behind a shim that logs its argv, so the key path (a header file descriptor) is exercised for
real. Every refusal asserts its exit code, its message, and that the service was never stopped; every window asserts the
service was started again. The key is a FAKE string.
"""
import http.server
import json
import os
import pathlib
import random
import re
import shutil
import signal
import subprocess
import threading
import time

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "gpu_window.sh"
KEY = "QZJ8-fake-window-key-7c1e"
REAL_CURL = shutil.which("curl")

SYSTEMCTL = r"""#!/usr/bin/env bash
echo "systemctl $*" >> "$SHIM_DIR/calls.log"
case "$*" in
  "--user is-active --quiet qwen") [ -e "$SHIM_DIR/active" ];;
  "--user stop qwen") rc="${SHIM_STOP_RC:-0}"; [ "$rc" = 0 ] && rm -f "$SHIM_DIR/active"; exit "$rc";;
  "--user start qwen")
    if [ -f "$SHIM_DIR/job.pid" ]; then          # a zombie holds nothing: `kill -0` alone would call it alive
      st=$(awk '{print $3}' "/proc/$(cat "$SHIM_DIR/job.pid")/stat" 2>/dev/null)
      if [ -n "$st" ] && [ "$st" != Z ]; then echo job-alive-at-start; else echo job-dead-at-start; fi \
        >> "$SHIM_DIR/calls.log"
    fi
    if [ -e "$SHIM_DIR/never-back" ]; then :
    elif [ -e "$SHIM_DIR/slow-start" ]; then (sleep 3; touch "$SHIM_DIR/active") > /dev/null 2>&1 &
    else touch "$SHIM_DIR/active"; fi
    exit 0;;
  *) exit 99;;
esac
"""
NVIDIA_SMI = r"""#!/usr/bin/env bash
echo "nvidia-smi $*" >> "$SHIM_DIR/calls.log"
if [ ! -e "$SHIM_DIR/active" ]; then                 # the service is stopped: the window's free wait
  [ -e "$SHIM_DIR/nvsmi-hang" ] && exec sleep 60
  [ -e "$SHIM_DIR/nvsmi-hang-noterm" ] && { trap '' TERM; exec sleep 60; }
  [ -e "$SHIM_DIR/nvsmi-error-after-stop" ] && { echo "Unable to determine the device handle for GPU0000:01:00.0: Unknown Error"; exit 0; }
fi
[ -e "$SHIM_DIR/nvsmi-hang-always" ] && exec sleep 60
[ -e "$SHIM_DIR/nvsmi-broken" ] && { echo "Failed to initialize NVML: Driver/library version mismatch"; exit 18; }
cat "$SHIM_DIR/gpu_used" 2>/dev/null || echo 100
"""
CURL = r"""#!/usr/bin/env bash
printf '%s\n' "$*" >> "$SHIM_DIR/curl-argv.log"
exec REAL_CURL "$@"
"""


class _Models(http.server.BaseHTTPRequestHandler):
    def do_GET(self):  # noqa: N802 (the stdlib's name)
        auth = self.headers.get("Authorization", "")
        self.server.seen.append(auth)
        ok_key = auth == "Bearer " + KEY
        code = 200 if (ok_key and (self.server.shim / "active").exists()) else (401 if not ok_key else 503)
        self.send_response(code)
        self.end_headers()
        self.wfile.write(b'{"data":[]}')

    def log_message(self, *a):
        pass


@pytest.fixture
def win(tmp_path):
    shim = tmp_path / "shim"
    shim.mkdir()
    for name, body in (("systemctl", SYSTEMCTL), ("nvidia-smi", NVIDIA_SMI), ("curl", CURL.replace("REAL_CURL", REAL_CURL))):
        (shim / name).write_text(body)
        (shim / name).chmod(0o755)
    (shim / "active").touch()
    key = tmp_path / "api-key"
    key.write_text(KEY + "\n")
    key.chmod(0o600)
    repo = tmp_path / "repo"
    (repo / ".lanes").mkdir(parents=True)
    srv = http.server.ThreadingHTTPServer(("127.0.0.1", 0), _Models)
    srv.seen, srv.shim = [], shim
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    env = dict(os.environ, PATH="%s:%s" % (shim, os.environ["PATH"]), HOME=str(tmp_path), SHIM_DIR=str(shim),
               AF_REPO=str(repo), QWEN_KEY_FILE=str(key), GPU_WINDOW_DIR=str(tmp_path / "state"),
               QWEN_MODELS_URL="http://127.0.0.1:%d/v1/models" % srv.server_address[1],
               XDG_RUNTIME_DIR=str(tmp_path))
    for k in ("GPU_WINDOW_MAX_SECONDS", "GPU_FREE_WAIT_SECONDS", "GPU_JOB_KILL_AFTER", "QWEN_BACK_SECONDS",
              "SHIM_STOP_RC", "GPU_FREE_MIB", "QWEN_UNIT"):
        env.pop(k, None)
    w = type("W", (), {})()
    w.tmp, w.shim, w.repo, w.env, w.srv, w.key = tmp_path, shim, repo, env, srv, key
    yield w
    srv.shutdown()
    srv.server_close()


def _jobs(w, *lines):
    p = w.tmp / "jobs.txt"
    p.write_text("# a comment line\n\n" + "\n".join(lines) + "\n")
    return str(p)


def _run(w, *args, timeout=60, **extra):
    env = dict(w.env, **extra)
    return subprocess.run(["bash", str(SCRIPT), *args], capture_output=True, text=True, env=env, timeout=timeout)


def _calls(w):
    p = w.shim / "calls.log"
    return p.read_text().splitlines() if p.exists() else []


def _events(w):
    p = w.tmp / "state" / "record.jsonl"
    return [json.loads(line) for line in p.read_text().splitlines()] if p.exists() else []


def _never_stopped(w):
    assert not any(c.startswith("systemctl --user stop") or c.startswith("systemctl --user start") for c in _calls(w))
    assert (w.shim / "active").exists()


def _key_never_in_argv(w):
    argv = (w.shim / "curl-argv.log").read_text() if (w.shim / "curl-argv.log").exists() else ""
    assert KEY not in argv
    for p in w.tmp.rglob("*"):
        if p.is_file() and p != w.key and p.suffix in (".log", ".jsonl", ".txt"):
            assert KEY not in p.read_text(errors="replace"), p


def _dead_pid():
    p = subprocess.Popen(["true"])
    p.wait()
    return p.pid


def test_usage_errors_touch_nothing(win):
    jobs = _jobs(win, "true")
    empty = win.tmp / "empty.txt"
    empty.write_text("# only a comment\n\n")
    cases = [((), "usage: gpu_window.sh"), (("--max-minutes",), "usage: gpu_window.sh"),
             (("--max-minutes", "0", jobs), "must be 1-240"), (("--max-minutes", "241", jobs), "must be 1-240"),
             (("--max-minutes", "x", jobs), "needs a whole number"), ((str(win.tmp / "missing.txt"),), "usage:"),
             ((jobs, jobs), "usage:"), (("--bogus", jobs), "usage:"), ((str(empty),), "no jobs in")]
    for args, msg in cases:
        r = _run(win, *args, timeout=15)
        assert r.returncode == 64 and msg in r.stderr, (args, r.returncode, r.stderr)
    assert _calls(win) == []
    _never_stopped(win)


def test_a_live_lane_refuses_and_never_stops(win):
    (win.repo / ".lanes" / "L1").mkdir()
    (win.repo / ".lanes" / "L1" / "lane.pid").write_text("%d\n" % os.getpid())
    r = _run(win, _jobs(win, "touch %s/ran" % win.tmp))
    assert r.returncode == 3 and "refusing, 1 lane(s) live" in r.stderr, r.stderr
    _never_stopped(win)
    assert not (win.tmp / "ran").exists()
    assert [e["event"] for e in _events(win)] == ["refused"] and _events(win)[0]["reason"] == "lane live"


def test_a_pid_file_without_a_pid_counts_as_live(win):
    (win.repo / ".lanes" / "L2").mkdir()
    (win.repo / ".lanes" / "L2" / "lane.pid").write_text("12abc\n")
    r = _run(win, _jobs(win, "true"))
    assert r.returncode == 3 and "(no pid in it)" in r.stderr, r.stderr
    _never_stopped(win)


def test_an_inactive_service_refuses(win):
    (win.shim / "active").unlink()
    r = _run(win, _jobs(win, "true"))
    assert r.returncode == 4 and "qwen is not active" in r.stderr, r.stderr
    assert not any("stop" in c or "start" in c for c in _calls(win))
    assert _events(win)[-1]["reason"] == "service not active"


def test_a_service_that_rejects_the_key_refuses_before_stopping(win):
    win.key.write_text("X4Z9-not-the-served-key\n")
    r = _run(win, _jobs(win, "true"))
    assert r.returncode == 4 and "does not answer 200 before the window" in r.stderr, r.stderr
    _never_stopped(win)
    assert win.srv.seen == ["Bearer X4Z9-not-the-served-key"]


def test_a_held_lock_refuses(win):
    import fcntl
    (win.tmp / "state").mkdir()
    with open(win.tmp / "state" / "lock", "w") as fh:
        fcntl.flock(fh, fcntl.LOCK_EX | fcntl.LOCK_NB)
        r = _run(win, _jobs(win, "true"))
    assert r.returncode == 5 and "another window holds" in r.stderr, r.stderr
    _never_stopped(win)


def test_dry_run_prints_the_plan_and_stops_nothing(win):
    r = _run(win, "--dry-run", "--max-minutes", "7", _jobs(win, "echo one", "echo two"))
    assert r.returncode == 0, r.stderr
    assert "would stop qwen, run 2 job(s) within 7 min" in r.stdout and "  job: echo two" in r.stdout
    _never_stopped(win)


def test_a_window_stops_runs_and_restores_in_order(win):
    (win.repo / ".lanes" / "DEAD").mkdir()
    (win.repo / ".lanes" / "DEAD" / "lane.pid").write_text("%d\n" % _dead_pid())
    job1 = 'test ! -e "$SHIM_DIR/active" && echo job1-ran-while-stopped >> "$SHIM_DIR/calls.log"'
    job2 = 'echo job2-ran >> "$SHIM_DIR/calls.log"; echo to-the-log'
    r = _run(win, _jobs(win, job1, job2))
    assert r.returncode == 0, r.stderr
    calls = _calls(win)
    order = [calls.index(c) for c in ("systemctl --user is-active --quiet qwen", "systemctl --user stop qwen",
                                      "job1-ran-while-stopped", "job2-ran", "systemctl --user start qwen")]
    assert order == sorted(order), calls
    assert any(c.startswith("nvidia-smi") for c in calls[order[1]:order[2]])
    ev = _events(win)
    assert [e["event"] for e in ev] == ["open", "stop", "gpu_free", "job", "job", "start", "back", "close"], ev
    assert [e.get("rc") for e in ev if e["event"] == "job"] == [0, 0] and ev[-2]["ok"] is True and ev[-1]["rc"] == 0
    assert pathlib.Path(ev[4]["log"]).read_text() == "to-the-log\n"
    assert (win.shim / "active").exists()
    assert win.srv.seen and set(win.srv.seen) == {"Bearer " + KEY}
    assert "@/dev/fd/" in (win.shim / "curl-argv.log").read_text()
    _key_never_in_argv(win)


def test_a_failing_job_does_not_stop_the_next_and_the_service_returns(win):
    r = _run(win, _jobs(win, "exit 7", 'echo job2-ran >> "$SHIM_DIR/calls.log"'))
    assert r.returncode == 1, r.stderr
    assert [e.get("rc") for e in _events(win) if e["event"] == "job"] == [7, 0]
    assert "job2-ran" in _calls(win) and (win.shim / "active").exists()
    assert _events(win)[-1] == dict(_events(win)[-1], event="close", rc=1)


def test_the_budget_kills_a_long_job_and_skips_the_rest(win):
    t0 = time.monotonic()
    r = _run(win, _jobs(win, "exec sleep 30", 'echo late >> "$SHIM_DIR/calls.log"'), GPU_WINDOW_MAX_SECONDS="2")
    assert r.returncode == 1, r.stderr
    assert time.monotonic() - t0 < 20
    jobs = [e for e in _events(win) if e["event"] == "job"]
    assert jobs[0]["rc"] == 124 and jobs[1] == dict(jobs[1], skipped="no time left")
    assert "late" not in _calls(win) and (win.shim / "active").exists()


def test_a_gpu_that_never_frees_runs_no_job_and_restores(win):
    (win.shim / "gpu_used").write_text("20000\n")
    r = _run(win, _jobs(win, 'echo ran >> "$SHIM_DIR/calls.log"'), GPU_FREE_WAIT_SECONDS="0")
    assert r.returncode == 1 and "the GPU did not free (used 20000 MiB)" in r.stderr, r.stderr
    assert "ran" not in _calls(win)
    assert [e["event"] for e in _events(win)] == ["open", "stop", "gpu_busy", "start", "back"]
    assert (win.shim / "active").exists()


def test_a_failed_stop_runs_no_job_and_restores(win):
    r = _run(win, _jobs(win, 'echo ran >> "$SHIM_DIR/calls.log"'), SHIM_STOP_RC="5")
    assert r.returncode == 1 and "stopping qwen failed (rc 5)" in r.stderr, r.stderr
    assert "ran" not in _calls(win) and "systemctl --user start qwen" in _calls(win)
    assert [e["event"] for e in _events(win)] == ["open", "stop", "start", "back"] and _events(win)[1]["rc"] == 5


def test_a_service_that_never_returns_exits_6(win):
    (win.shim / "never-back").touch()
    r = _run(win, _jobs(win, 'echo ran >> "$SHIM_DIR/calls.log"'), QWEN_BACK_SECONDS="0")
    assert r.returncode == 6 and "did not answer" in r.stderr, r.stderr
    assert "ran" in _calls(win)
    ev = _events(win)
    assert [e["event"] for e in ev][-2:] == ["start", "back"] and ev[-1]["ok"] is False
    assert not any(e["event"] == "close" for e in ev)


def test_term_stops_the_running_job_at_once_and_restores(win):
    job = 'echo job-start >> "$SHIM_DIR/calls.log"; echo $$ > "$SHIM_DIR/job.pid"; exec sleep 60'
    proc = subprocess.Popen(["bash", str(SCRIPT), _jobs(win, job, 'echo second >> "$SHIM_DIR/calls.log"')],
                            env=win.env, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    try:
        deadline = time.monotonic() + 15
        while not (win.shim / "job.pid").exists() or not (win.shim / "job.pid").read_text().strip():
            assert time.monotonic() < deadline and proc.poll() is None, proc.poll()
            time.sleep(0.05)
        job_pid = int((win.shim / "job.pid").read_text())
        t0 = time.monotonic()
        proc.send_signal(signal.SIGTERM)
        rc = proc.wait(timeout=40)
        assert rc == 130 and time.monotonic() - t0 < 10, (rc, proc.stderr.read())
    finally:
        if proc.poll() is None:
            proc.kill()
    deadline = time.monotonic() + 5
    while True:
        try:
            os.kill(job_pid, 0)
        except ProcessLookupError:
            break
        assert time.monotonic() < deadline, "the job outlived the abort"
        time.sleep(0.05)
    calls = _calls(win)
    assert "second" not in calls and calls.index("job-start") < calls.index("systemctl --user start qwen")
    ev = [e["event"] for e in _events(win)]
    assert ev[-3:] == ["abort", "start", "back"] and _events(win)[-3]["signal"] == "TERM"
    assert (win.shim / "active").exists()


def _start(w, jobs, **extra):
    return subprocess.Popen(["bash", str(SCRIPT), jobs], env=dict(w.env, **extra), stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE, text=True)


def _wait_for(pred, seconds=15):
    deadline = time.monotonic() + seconds
    while not pred():
        assert time.monotonic() < deadline, "timed out waiting"
        time.sleep(0.05)


def _job_pid(w):
    _wait_for(lambda: (w.shim / "job.pid").exists() and (w.shim / "job.pid").read_text().strip())
    return int((w.shim / "job.pid").read_text())


def _dead(pid, seconds=10):
    deadline = time.monotonic() + seconds
    while True:
        try:
            os.kill(pid, 0)
        except ProcessLookupError:
            return True
        if time.monotonic() > deadline:
            return False
        time.sleep(0.05)


def test_a_signal_during_the_restore_is_ignored_so_a_service_that_never_returns_still_exits_6(win):
    """VERIFY-GW1 F-1: a TERM or INT during `restore` ended the script with rc 130 ("the service back") while the
    service had not come back, and a TERM between `restored=1` and the start skipped the start."""
    (win.shim / "never-back").touch()
    proc = _start(win, _jobs(win, "true"), QWEN_BACK_SECONDS="4")
    try:
        _wait_for(lambda: any(e["event"] == "start" for e in _events(win)))
        proc.send_signal(signal.SIGTERM)
        time.sleep(0.2)
        proc.send_signal(signal.SIGINT)
        rc = proc.wait(timeout=30)
    finally:
        if proc.poll() is None:
            proc.kill()
    assert rc == 6 and "did not answer" in proc.stderr.read()
    ev = [e["event"] for e in _events(win)]
    assert ev[-2:] == ["start", "back"] and _events(win)[-1]["ok"] is False and "abort" not in ev


def test_a_second_term_during_the_aborts_restore_is_ignored_and_the_service_returns(win):
    (win.shim / "slow-start").touch()
    job = 'echo $$ > "$SHIM_DIR/job.pid"; exec sleep 60'
    proc = _start(win, _jobs(win, job))
    try:
        pid = _job_pid(win)
        proc.send_signal(signal.SIGTERM)
        _wait_for(lambda: any(e["event"] == "start" for e in _events(win)))
        proc.send_signal(signal.SIGTERM)
        rc = proc.wait(timeout=40)
    finally:
        if proc.poll() is None:
            proc.kill()
    assert rc == 130 and _dead(pid)
    ev = _events(win)
    assert [e["event"] for e in ev][-3:] == ["abort", "start", "back"] and ev[-1]["ok"] is True
    assert "job-dead-at-start" in _calls(win) and (win.shim / "active").exists()


def test_int_during_a_job_stops_it_and_restores_after_it_is_dead(win):
    job = 'echo $$ > "$SHIM_DIR/job.pid"; exec sleep 60'
    proc = _start(win, _jobs(win, job, 'echo second >> "$SHIM_DIR/calls.log"'))
    try:
        pid = _job_pid(win)
        t0 = time.monotonic()
        proc.send_signal(signal.SIGINT)
        rc = proc.wait(timeout=40)
    finally:
        if proc.poll() is None:
            proc.kill()
    assert rc == 130 and time.monotonic() - t0 < 10 and _dead(pid)
    assert "job-dead-at-start" in _calls(win) and "second" not in _calls(win)
    assert _events(win)[-3]["signal"] == "INT" and (win.shim / "active").exists()


def test_a_hung_nvidia_smi_is_bounded_and_the_service_returns(win):
    """VERIFY-GW1 F-2: a probe with no time limit kept the service stopped for as long as it hung."""
    (win.shim / "nvsmi-hang").touch()
    t0 = time.monotonic()
    r = _run(win, _jobs(win, 'echo ran >> "$SHIM_DIR/calls.log"'), GPU_FREE_WAIT_SECONDS="0")
    assert r.returncode == 1 and "the GPU did not free" in r.stderr, r.stderr
    assert time.monotonic() - t0 < 30 and "ran" not in _calls(win) and (win.shim / "active").exists()


def test_a_job_that_ignores_term_is_killed_after_the_grace_on_the_budget_and_on_abort(win):
    stubborn = 'trap "" TERM; echo $$ > "$SHIM_DIR/job.pid"; while :; do sleep 1; done'
    t0 = time.monotonic()
    r = _run(win, _jobs(win, stubborn), GPU_WINDOW_MAX_SECONDS="2", GPU_JOB_KILL_AFTER="2")
    assert r.returncode == 1 and time.monotonic() - t0 < 20, r.stderr
    assert [e.get("rc") for e in _events(win) if e["event"] == "job"] == [137]
    (win.shim / "job.pid").unlink()
    proc = _start(win, _jobs(win, stubborn), GPU_JOB_KILL_AFTER="2")
    try:
        pid = _job_pid(win)
        proc.send_signal(signal.SIGTERM)
        rc = proc.wait(timeout=30)
    finally:
        if proc.poll() is None:
            proc.kill()
    starts = [c for c in _calls(win) if c.startswith("job-")]   # the LAST start: the first half left its own line
    assert rc == 130 and _dead(pid) and starts[-1] == "job-dead-at-start", starts


def test_a_job_cannot_read_the_callers_stdin(win):
    r = subprocess.run(["bash", str(SCRIPT), _jobs(win, 'read -r x; echo "read=[$x]" >> "$SHIM_DIR/calls.log"')],
                       input="LEAK\n", capture_output=True, text=True, env=win.env, timeout=60)
    assert r.returncode == 0 and "read=[]" in _calls(win), (r.stderr, _calls(win))


def test_a_proxy_in_the_environment_is_never_used_for_the_loopback_check(win):
    dead = "http://127.0.0.1:9"
    r = _run(win, _jobs(win, "true"), http_proxy=dead, HTTP_PROXY=dead, no_proxy="", NO_PROXY="")
    assert r.returncode == 0, r.stderr


def test_numbers_are_decimal_and_the_seams_are_checked_before_anything_stops(win):
    """VERIFY-GW1 F-7 (a leading zero read as octal) and F-8 (garbage seams reached a wait)."""
    jobs = _jobs(win, "true")
    for arg, minutes in (("010", 10), ("08", 8)):
        r = _run(win, "--dry-run", "--max-minutes", arg, jobs)
        assert r.returncode == 0 and "within %d min" % minutes in r.stdout, (arg, r.stdout, r.stderr)
    for seam, value, msg in (("GPU_FREE_WAIT_SECONDS", "abc", "must be a whole number"),
                             ("GPU_JOB_KILL_AFTER", "-1", "must be a whole number"),
                             ("GPU_WINDOW_MAX_SECONDS", "999999", "is too large"),
                             ("GPU_WINDOW_MAX_SECONDS", "20000", "at most 14400"),
                             ("QWEN_BACK_SECONDS", "20m", "must be a whole number"),
                             ("GPU_FREE_MIB", "1.5k", "must be a whole number"),
                             ("GPU_JOB_KILL_AFTER", "0", "must be 1-300"),
                             ("GPU_JOB_KILL_AFTER", "301", "must be 1-300"),
                             ("GPU_FREE_WAIT_SECONDS", "3601", "at most 3600"),
                             ("QWEN_BACK_SECONDS", "3601", "at most 3600")):
        r = _run(win, jobs, **{seam: value})
        assert r.returncode == 64 and msg in r.stderr, (seam, value, r.stderr)
    _never_stopped(win)


def test_leading_zero_seams_are_decimal(win):
    """VERIFY-GW1-R1 R1-F-5: `10#` on the seams had no test (its mutants survived). A leading 0 before an 8 or a 9 is an
    octal error in bash arithmetic, so without `10#` the script dies before the lock."""
    r = _run(win, _jobs(win, "true"), GPU_WINDOW_MAX_SECONDS="09", GPU_FREE_WAIT_SECONDS="09", GPU_JOB_KILL_AFTER="09",
             QWEN_BACK_SECONDS="09", GPU_FREE_MIB="0900")
    assert r.returncode == 0, r.stderr
    assert [e["event"] for e in _events(win)][-3:] == ["start", "back", "close"]


def test_no_gpu_reading_before_the_window_refuses_and_stops_nothing(win):
    """VERIFY-GW1-R1 R1-F-6: a driver that cannot start a new GPU process (a driver update without a reboot) keeps the
    running service alive but would keep it from starting again; nvidia-smi must give a number before the stop."""
    (win.shim / "nvsmi-broken").touch()
    r = _run(win, _jobs(win, 'echo ran >> "$SHIM_DIR/calls.log"'))
    assert r.returncode == 4 and "nvidia-smi gives no reading" in r.stderr, r.stderr
    assert _events(win)[-1]["reason"] == "no GPU reading" and "ran" not in _calls(win)
    _never_stopped(win)


def test_a_hung_nvidia_smi_before_the_window_is_bounded_and_refuses(win):
    (win.shim / "nvsmi-hang-always").touch()
    t0 = time.monotonic()
    r = _run(win, _jobs(win, "true"))
    assert r.returncode == 4 and time.monotonic() - t0 < 30, r.stderr
    _never_stopped(win)


def test_an_error_line_after_the_stop_is_no_reading_so_no_job_runs(win):
    """VERIFY-GW1 F-10: `tr -dc 0-9` turned an error line into 1000 MiB ("free") and the jobs ran on a GPU nobody read."""
    (win.shim / "nvsmi-error-after-stop").touch()
    r = _run(win, _jobs(win, 'echo ran >> "$SHIM_DIR/calls.log"'), GPU_FREE_WAIT_SECONDS="0")
    assert r.returncode == 1 and "the GPU did not free (used ? MiB)" in r.stderr, r.stderr
    assert "ran" not in _calls(win) and (win.shim / "active").exists()


def test_a_hung_probe_that_ignores_term_is_killed_after_two_seconds(win):
    """VERIFY-GW1-R1 R1-F-5: `timeout 10` without `-k 2` survived; a probe that ignores TERM then held the window 60 s."""
    (win.shim / "nvsmi-hang-noterm").touch()
    t0 = time.monotonic()
    r = _run(win, _jobs(win, "true"), GPU_FREE_WAIT_SECONDS="0", timeout=90)
    assert r.returncode == 1 and time.monotonic() - t0 < 30, (r.stderr, time.monotonic() - t0)
    assert (win.shim / "active").exists()


def test_a_burst_of_signals_across_the_abort_never_skips_the_restore(win):
    """AF-AP-145, met by VERIFY-GW1-R1 (R-1): a second signal between abort's exit and restore's first line re-ran abort
    inside the EXIT trap, and its exit ended the shell before the service was started."""
    job = 'echo $$ > "$SHIM_DIR/job.pid"; while :; do sleep 1; done'
    for trial in range(8):
        (win.shim / "job.pid").unlink(missing_ok=True)
        proc = _start(win, _jobs(win, job), GPU_JOB_KILL_AFTER="3")
        try:
            _job_pid(win)
            end = time.monotonic() + 0.05
            while time.monotonic() < end and proc.poll() is None:
                os.kill(proc.pid, signal.SIGTERM)
                time.sleep(0.00005)
            rc = proc.wait(timeout=40)
        finally:
            if proc.poll() is None:
                proc.kill()
        ev = [e["event"] for e in _events(win)]
        assert rc == 130 and ev[-2:] == ["start", "back"] and (win.shim / "active").exists(), (trial, rc, ev[-5:])


@pytest.mark.parametrize("shape", ["gpu_busy", "failed stop"])
def test_one_term_right_after_a_plain_exit_never_skips_the_restore(win, shape):
    """VERIFY-GW1-R1 R-2 and R-3: ONE TERM 0-300 us after the busy-GPU or the failed-stop exit ran abort inside the EXIT
    trap (25 of 150 and 13 of 150 lost the start on the first repair). A watcher sends it as the record line appears."""
    random.seed(7)
    marker = b'"gpu_busy"' if shape == "gpu_busy" else b'"rc":5'
    extra = {"GPU_FREE_WAIT_SECONDS": "0"} if shape == "gpu_busy" else {"SHIM_STOP_RC": "5"}
    if shape == "gpu_busy":
        (win.shim / "gpu_used").write_text("20000\n")
    rec = win.tmp / "state" / "record.jsonl"
    for trial in range(20):
        (win.shim / "active").touch()
        seen = rec.read_bytes().count(marker) if rec.exists() else 0
        starts = _calls(win).count("systemctl --user start qwen")
        proc = _start(win, _jobs(win, "true"), **extra)
        try:
            deadline = time.monotonic() + 20
            while not (rec.exists() and rec.read_bytes().count(marker) > seen):   # a busy watch: the gap is ~130 us
                if proc.poll() is not None or time.monotonic() > deadline:
                    assert rec.exists() and rec.read_bytes().count(marker) > seen, (trial, "the marker never appeared")
                    break
            t1, jitter = time.perf_counter(), random.uniform(0, 300e-6)
            while time.perf_counter() - t1 < jitter:
                pass
            proc.send_signal(signal.SIGTERM)
            rc = proc.wait(timeout=60)
        finally:
            if proc.poll() is None:
                proc.kill()
        assert rc in (1, 130), (trial, rc)
        assert _calls(win).count("systemctl --user start qwen") == starts + 1, (trial, rc, _events(win)[-4:])
        assert _events(win)[-1]["event"] == "back" and (win.shim / "active").exists(), (trial, _events(win)[-4:])


def test_every_exit_once_the_traps_are_armed_ignores_int_and_term_first():
    """AF-AP-145 / R1-F-1, the deterministic form: the handlers open with the ignore, abort leaves through `leave`, and no
    bare `exit` follows abort's definition (restore, defined earlier, opens with the ignore itself)."""
    lines = SCRIPT.read_text().splitlines()
    code = [re.sub(r"\s+#\s.*$", "", line) for line in lines]
    assert "leave() { trap '' INT TERM; exit \"$1\"; }" in code
    assert "trap 'trap \"\" INT TERM; abort INT' INT" in code
    assert "trap 'trap \"\" INT TERM; abort TERM' TERM" in code
    r = code.index("restore() {")
    assert code[r + 1].strip() == "trap '' INT TERM"
    a = code.index("abort() {")
    bare = [(i + 1, line) for i, line in enumerate(code) if i > a and re.search(r"(?<![\w-])exit(?![\w-])", line)]
    assert bare == [], bare
