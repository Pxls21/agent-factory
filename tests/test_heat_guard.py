"""deploy/heat_guard.sh (D-136, AF-AP-263): the PC's CPU heat guard stops the qwen unit after three readings of Tctl
at or above the limit, or unreadable, and leaves it alone otherwise. The script runs for real under bash with fake
`sensors`, `systemctl` and `sleep` first on PATH: the fake sensors replays a list of readings, the fake systemctl
records every call and keeps the unit's state in a file, and the fake sleep ends the guard after the last reading."""
import os
import pathlib
import subprocess

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]
GUARD = ROOT / "deploy" / "heat_guard.sh"

SENSORS = """#!/bin/bash
D=$(dirname "$0")/..
i=$(cat "$D/idx" 2>/dev/null || echo 0)
n=$(wc -l < "$D/readings")
k=$(( i < n ? i + 1 : n ))
echo $((i + 1)) > "$D/idx"
v=$(sed -n "${k}p" "$D/readings")
echo "k10temp-pci-00c3"
[ "$v" = none ] || printf 'Tctl:         +%s\\xc2\\xb0C  \\n' "$v"
"""

SYSTEMCTL = """#!/bin/bash
D=$(dirname "$0")/..
echo "$*" >> "$D/calls"
case " $* " in
  *" is-active "*) cat "$D/state" ;;
  *" stop "*) echo inactive > "$D/state" ;;
esac
"""

SLEEP = """#!/bin/bash
D=$(dirname "$0")/..
c=$(( $(cat "$D/sleeps" 2>/dev/null || echo 0) + 1 ))
echo "$c" > "$D/sleeps"
[ "$c" -ge "$(wc -l < "$D/readings")" ] && kill -TERM "$PPID"
exit 0
"""


def run_guard(tmp_path, readings, state="active", args=("qwen",)):
    fake = tmp_path / "bin"
    fake.mkdir()
    for name, body in (("sensors", SENSORS), ("systemctl", SYSTEMCTL), ("sleep", SLEEP)):
        (fake / name).write_text(body)
        (fake / name).chmod(0o755)
    (tmp_path / "readings").write_text("".join(f"{r}\n" for r in readings))
    (tmp_path / "state").write_text(state + "\n")
    env = {"PATH": f"{fake}:/usr/bin:/bin", "HOME": str(tmp_path)}
    r = subprocess.run(["bash", str(GUARD), *args], capture_output=True, text=True, env=env, timeout=30)
    calls = (tmp_path / "calls").read_text().splitlines() if (tmp_path / "calls").exists() else []
    return r, calls


@pytest.mark.parametrize("readings", [
    ["92.5", "92.5", "92.5"],
    ["90", "90.0", "90"],             # at the limit counts
    ["none", "none", "none"],         # an unreadable sensor fails closed
    ["63.1", "none", "91", "95.2"],   # three in a row, after a cool one
], ids=["hot", "at-limit", "unreadable", "hot-after-cool"])
def test_three_hot_or_unreadable_readings_stop_the_unit(tmp_path, readings):
    r, calls = run_guard(tmp_path, readings)
    assert calls.count("--user stop qwen") == 1, (calls, r.stdout, r.stderr)
    assert (tmp_path / "state").read_text() == "inactive\n"
    assert "heat_guard: STOPPED qwen after 3 readings at or above 90 C" in r.stdout


@pytest.mark.parametrize("readings", [
    ["63.1"] * 5,
    ["89.9"] * 4,                                   # under the limit
    ["95", "95", "70", "95", "95", "70"],           # never three in a row
    ["none", "none", "62", "none", "none", "62"],
], ids=["cool", "just-under", "two-then-cool", "unreadable-twice"])
def test_readings_short_of_three_in_a_row_leave_the_unit_alone(tmp_path, readings):
    r, calls = run_guard(tmp_path, readings)
    assert [c for c in calls if "stop" in c] == [], (calls, r.stdout, r.stderr)
    assert (tmp_path / "state").read_text() == "active\n"
    assert "STOPPED" not in r.stdout


def test_a_unit_that_is_not_running_is_not_stopped(tmp_path):
    r, calls = run_guard(tmp_path, ["92.5"] * 3, state="inactive")
    assert calls == ["--user is-active qwen"], (calls, r.stdout)
    assert "heat_guard: hot with qwen not running (tctl=92.5); nothing to stop" in r.stdout


def test_the_limit_and_the_count_are_arguments(tmp_path):
    r, calls = run_guard(tmp_path, ["85", "85"], args=("qwen", "80", "1", "2"))
    assert calls.count("--user stop qwen") == 1, (calls, r.stdout, r.stderr)
    assert "heat_guard: STOPPED qwen after 2 readings at or above 80 C or unreadable (last tctl=85)" in r.stdout


@pytest.mark.parametrize("args", [
    ("qwen", "0"), ("qwen", "90", "0"), ("qwen", "90", "5", "00"), ("qwen", "x"), ("qwen", "90", "1.5"),
    ("qwen", "90", "5", "-3"),
], ids=["limit-0", "every-0", "readings-00", "limit-x", "every-fraction", "readings-negative"])
def test_bad_arguments_exit_64_before_any_reading(tmp_path, args):
    r, calls = run_guard(tmp_path, ["92.5"] * 3, args=args)
    assert r.returncode == 64, (r.returncode, r.stderr)
    assert "must be whole numbers above 0" in r.stderr
    assert calls == [] and not (tmp_path / "idx").exists()


def test_no_unit_is_a_usage_error(tmp_path):
    r, calls = run_guard(tmp_path, ["92.5"] * 3, args=())
    assert r.returncode != 0 and "usage: heat_guard.sh <unit>" in r.stderr
    assert calls == []


def test_the_service_runs_the_deployed_script_on_the_qwen_unit():
    unit = (ROOT / "deploy" / "heat-guard.service").read_text()
    lines = [ln for ln in unit.splitlines() if ln and not ln.startswith("#")]
    assert "ExecStart=/bin/bash %h/.config/qwen-serving/heat_guard.sh qwen" in lines
    assert "Restart=always" in lines and "WantedBy=default.target" in lines
    # a guard that dies must not restart the model server it guards: the qwen units require this unit (D-136)
    assert "RestartMode=direct" in lines
    assert os.access(GUARD, os.R_OK)
