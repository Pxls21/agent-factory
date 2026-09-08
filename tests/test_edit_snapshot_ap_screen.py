"""Tests for .claude/hooks/edit-snapshot.py AP_SCREEN and TEST_SCREEN rows.

8-verify F17: asserts fire/no-fire pairs for AF-AP-33..45 so the screen rows
have a test gate and cannot be silently weakened.
"""
import importlib.util
from pathlib import Path

# Import the hook module from its non-package location
_HOOK = Path(__file__).resolve().parents[1] / ".claude" / "hooks" / "edit-snapshot.py"
spec = importlib.util.spec_from_file_location("edit_snapshot", _HOOK)
_mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(_mod)

AP_SCREEN = _mod.AP_SCREEN
TEST_SCREEN = _mod.TEST_SCREEN

# Gather all screen rows into a dict by id for lookup
_AP_BY_ID = {row[0]: row[1] for row in AP_SCREEN}
_TEST_BY_ID = {row[0]: row[1] for row in TEST_SCREEN}


# ---- AF-AP-33 (TEST_SCREEN): health-endpoint-only liveness ----

class TestAFAP33:
    rx = _TEST_BY_ID["AF-AP-33"]

    def test_fires_on_health_endpoint(self):
        assert self.rx.search('conn.request("GET", "/api/health")')

    def test_fires_on_bare_health(self):
        assert self.rx.search('requests.get(url + "/health")')

    def test_no_fire_on_healthz(self):
        # /healthz does not match the pattern (no /api/health or /health")
        assert not self.rx.search('requests.get(url + "/healthz")')

    def test_no_fire_on_unrelated(self):
        assert not self.rx.search('result = check_system_status()')


# ---- AF-AP-34 (TEST_SCREEN): name-based process kill ----

class TestAFAP34:
    rx = _TEST_BY_ID["AF-AP-34"]

    def test_fires_on_pkill(self):
        assert self.rx.search('subprocess.run(["pkill", "-x", "buzz-relay"])')

    def test_fires_on_killall(self):
        assert self.rx.search('os.system("killall myproc")')

    def test_fires_on_kill_pgrep(self):
        assert self.rx.search('kill $(pgrep myproc)')

    def test_no_fire_on_kill_pid(self):
        assert not self.rx.search('os.kill(pid, signal.SIGTERM)')


# ---- AF-AP-35 (TEST_SCREEN): redaction keyed on a secret's VALUE ----

class TestAFAP35:
    rx = _TEST_BY_ID["AF-AP-35"]

    def test_fires_on_replace_token(self):
        assert self.rx.search('line.replace(api_token, "***")')

    def test_fires_on_re_sub_secret(self):
        assert self.rx.search('re.sub(re.escape(secret_key), "REDACTED", text)')

    def test_no_fire_on_replace_literal(self):
        assert not self.rx.search('text.replace("debug", "info")')


# ---- AF-AP-36 (AP_SCREEN): PASS line with literal check count ----

class TestAFAP36:
    rx = _AP_BY_ID["AF-AP-36"]

    def test_fires_on_literal_pass_checks(self):
        assert self.rx.search('PASS: 16 checks executed')

    def test_fires_on_pass_n_checks(self):
        assert self.rx.search('print("PASS: 5 checks done")')

    def test_no_fire_on_derived_pass(self):
        # The derived form uses f-string with a variable
        assert not self.rx.search('f"PASS: S0-01 acp-conformance -- {n} checks executed"')


# ---- AF-AP-37 (AP_SCREEN): hand-typed test counts ----

class TestAFAP37:
    rx = _AP_BY_ID["AF-AP-37"]

    def test_fires_on_tests_green(self):
        assert self.rx.search('217 tests green')

    def test_fires_on_passed_green(self):
        assert self.rx.search('435 passed green')

    def test_fires_on_test_green(self):
        assert self.rx.search('1 test green')

    def test_no_fire_on_summary_line(self):
        # The pasted format from test_summary.sh does not contain "green"
        assert not self.rx.search('pytest-summary: 26 passed in 1.15s')


# ---- AF-AP-38 (AP_SCREEN): presence instead of exact value on a pin ----

class TestAFAP38:
    rx = _AP_BY_ID["AF-AP-38"]

    def test_fires_on_get_adjacent_to_pin(self):
        # The pin-adjacent form: if x.get(...): on a line containing PINNED_
        assert self.rx.search('if rec.get("authorization_fingerprint"): check(PINNED_FP)')

    def test_fires_on_assert_get(self):
        assert self.rx.search('assert config.get("model")')

    def test_no_fire_on_get_without_pin(self):
        # if x.get() without PINNED_ on the same line -> no fire
        assert not self.rx.search('if body.get("stream"):')

    def test_no_fire_on_exact_comparison(self):
        # == comparison using direct dict access is the correct form
        assert not self.rx.search('if rec["model"] == PINNED_MODEL:')

    def test_fires_on_assert_get_even_with_eq(self):
        # assert x.get() fires even with == because .get() returns None silently
        # when the key is missing, masking a missing-key bug (AP-38 tell)
        assert self.rx.search('assert rec.get("model") == PINNED_MODEL')


# ---- AF-AP-39 (AP_SCREEN): secret interpolated into a command line ----

class TestAFAP39:
    rx = _AP_BY_ID["AF-AP-39"]

    def test_fires_on_shell_single_quoted_value(self):
        assert self.rx.search("""bash -c "env -i OMNIROUTE_API_KEY='$OMNIROUTE_API_KEY' buzz-acp" """)

    def test_fires_on_brace_expansion(self):
        assert self.rx.search('cmd = f"BUZZ_PRIVATE_KEY=${BUZZ_PRIVATE_KEY} hermes"')

    def test_fires_on_fstring_interpolation(self):
        assert self.rx.search('argv = ["bash", "-c", f"env -i API_TOKEN={token} run"]')

    def test_no_fire_on_env_dict_assignment(self):
        # The correct form: the value goes into the env mapping, never argv
        assert not self.rx.search('env["OMNIROUTE_API_KEY"] = read_secret(path)')

    def test_no_fire_on_pin_tuple(self):
        assert not self.rx.search('PINNED_ENV_KEYS = ("HERMES_HOME", "OMNIROUTE_API_KEY")')

    def test_no_fire_on_secret_file_write(self):
        # Writing KEY=value into a 0600 secret FILE is the sanctioned form (the launcher reads it)
        assert not self.rx.search('token_file.write_text(f"UPSTREAM_TOKEN={TOKEN}\\n")')

    def test_fires_on_argv_line_next_to_a_file_write(self):
        # The line filter is per line: a file write on one line does not launder an argv line below it
        assert self.rx.search('tf.write_text("x")\nargv = ["bash", "-c", f"env -i API_TOKEN={token} run"]')


# ---- AF-AP-40 (AP_SCREEN): presence-gated check ----

class TestAFAP40:
    rx = _AP_BY_ID["AF-AP-40"]

    def test_fires_on_bare_exists_guard(self):
        assert self.rx.search("if env_path.exists():\n    check_env(env_path)")

    def test_fires_on_joined_path_is_file(self):
        assert self.rx.search('if (leg_dir / "env.json").is_file():')

    def test_fires_on_exists_and_conjunct(self):
        assert self.rx.search("if scan.exists() and scan.stat().st_size:")

    def test_fires_on_the_ternary_form(self):
        # VERIFY-P5a F7: the same defect with no colon and no `and` — build_capture_record.py recorded an
        # absent relay receipt as `"accepted": null` through exactly this shape
        assert self.rx.search('receipt = json.loads(rp.read_text()) if rp.exists() else {}')

    def test_no_fire_on_an_unrelated_ternary(self):
        # the `else` alternative must not widen the row to every conditional expression — only to one whose
        # condition is a presence probe
        assert not self.rx.search('mode = "after" if phase == "post" else "teardown"')

    def test_no_fire_on_negated_guard(self):
        # `if not x.exists(): raise Failure` is the REQUIRED-artifact form
        assert not self.rx.search('if not env_path.exists():\n    raise Failure(f"{leg}: env.json missing")')

    def test_no_fire_on_negated_joined_path(self):
        assert not self.rx.search('if not (leg_dir / "env.json").is_file():')


# ---- AF-AP-41 (AP_SCREEN): last-wins parse of an echo line ----

class TestAFAP41:
    rx = _AP_BY_ID["AF-AP-41"]

    def test_fires_on_dict_re_findall(self):
        assert self.rx.search('kv = dict(re.findall(r"(\\w+)=(\\S+)", line))')

    def test_fires_on_compiled_pattern(self):
        assert self.rx.search("kv = dict(_KV.findall(line))")

    def test_no_fire_on_findall_alone(self):
        assert not self.rx.search('pairs = re.findall(r"(\\w+)=(\\S+)", line)')

    def test_no_fire_on_dict_zip(self):
        assert not self.rx.search("kv = dict(zip(keys, values))")


# ---- AF-AP-43 (AP_SCREEN): ordering field sampled outside the ordering lock ----

class TestAFAP43:
    rx = _AP_BY_ID["AF-AP-43"]

    def test_fires_on_timestamp_before_lock(self):
        assert self.rx.search("t_mono = time.monotonic_ns()\nwith self._lock:\n    self.seq += 1")

    def test_fires_on_wallclock_before_lock(self):
        assert self.rx.search("t_utc = time.time()\nrec = {}\nwith lock:\n    seq += 1")

    def test_no_fire_on_timestamp_inside_lock(self):
        assert not self.rx.search("with self._lock:\n    t_mono = time.monotonic_ns()\n    self.seq += 1\n")

    def test_no_fire_on_lock_named_otherwise(self):
        assert not self.rx.search("t = time.monotonic_ns()\nwith self._writer_guard:\n    pass")



# ---- AF-AP-44 (TEST_SCREEN): module-scope venue probe that can raise ----

class TestAFAP44:
    rx = _TEST_BY_ID["AF-AP-44"]

    def test_fires_on_skipif_exists(self):
        assert self.rx.search('@pytest.mark.skipif(not BIN.exists(), reason="pinned binary not installed")')

    def test_fires_on_skipif_is_file(self):
        assert self.rx.search("@pytest.mark.skipif(not Path(HOME).is_file(), reason=\"x\")")

    def test_no_fire_on_wrapped_probe(self):
        assert not self.rx.search('@pytest.mark.skipif(not _binary_available(), reason="not visible in this venue")')


# ---- AF-AP-45 (AP_SCREEN): liveness without the process state column ----

class TestAFAP45:
    rx = _AP_BY_ID["AF-AP-45"]

    def test_fires_on_ps_without_stat(self):
        assert self.rx.search('subprocess.run(["ps", "-eo", "pid,ppid,etimes,args", "--no-headers"])')

    def test_fires_on_proc_existence_liveness(self):
        assert self.rx.search('while os.path.exists(f"/proc/{pid}"):')

    def test_no_fire_on_ps_with_stat(self):
        assert not self.rx.search('subprocess.run(["ps", "-eo", "pid,ppid,etimes,stat,args", "--no-headers"])')

    def test_no_fire_on_proc_stat_read(self):
        assert not self.rx.search('Path(f"/proc/{pid}/stat").read_text()')

    def test_no_fire_on_proc_stat_existence_probe(self):
        # VERIFY-B5e F15: the state-aware form (exists on /proc/<pid>/stat, field 3 read next) must not fire
        assert not self.rx.search('if os.path.exists("/proc/%d/stat" % child_pid):')

    def test_no_fire_on_proc_stat_existence_probe_fstring(self):
        assert not self.rx.search('if not os.path.exists(f"/proc/{agent_pid}/stat"):')

    def test_fires_on_bare_proc_pid_existence(self):
        assert self.rx.search('if os.path.exists("/proc/%d" % child_pid):')


# ---- AF-AP-55 (AP_SCREEN): identity sampled from /proc/<pid>/exe at spawn time ----

class TestAFAP55:
    rx = _AP_BY_ID["AF-AP-55"]

    def test_fires_on_percent_format_pid(self):
        assert self.rx.search('candidate = os.readlink("/proc/%d/exe" % proc.pid)')

    def test_fires_on_fstring_pid(self):
        assert self.rx.search('interp = os.readlink(f"/proc/{proc.pid}/exe")')

    def test_no_fire_on_cwd_link(self):
        assert not self.rx.search('cwd = os.readlink("/proc/%d/cwd" % pid)')

    def test_no_fire_on_realpath_of_executable(self):
        assert not self.rx.search('expected = os.path.realpath(sys.executable)')


# ---- AF-AP-57 (TEST_SCREEN): ordinal gate in a test fake ----

class TestAFAP57:
    rx = _TEST_BY_ID["AF-AP-57"]

    def test_fires_on_rl_calls_ordinal(self):
        assert self.rx.search("                if _rl_calls[0] == 1:                    # the early loop's single attempt")

    def test_fires_on_call_count_lt(self):
        assert self.rx.search("    if call_count < 2:\n        raise OSError()")

    def test_fires_on_attempts_ge(self):
        assert self.rx.search("        if attempts[0] >= 3: return path")

    def test_fires_on_a_bracketed_call_count(self):
        # VERIFY-N5h F11: `[0]` was offered to `calls`/`attempts` but not to `call_count`, so the commonest
        # spelling of the ordinal gate was invisible to the screen
        assert self.rx.search("                if _call_count[0] == 1:")

    def test_no_fire_on_call_count_assertion(self):
        assert not self.rx.search("    assert spy.call_count == 1")

    def test_no_fire_on_counter_increment(self):
        assert not self.rx.search("                _rl_calls[0] += 1")

    def test_no_fire_on_phase_gate(self):
        assert not self.rx.search("                if threading.active_count() == 1:")


# ---- AF-AP-58 (AP_SCREEN): raising signal handler installed before its catching scope ----

class TestAFAP58:
    rx = _AP_BY_ID["AF-AP-58"]

    def test_fires_on_sigterm_install(self):
        assert self.rx.search("    signal.signal(signal.SIGTERM, _sigterm_handler)")

    def test_fires_on_sigalrm_install_with_alias(self):
        assert self.rx.search("    old = signal.signal(signal.SIGALRM, _raise_timeout)")

    def test_no_fire_on_alarm(self):
        assert not self.rx.search("    signal.alarm(timeout_s)")

    def test_no_fire_on_send_signal(self):
        assert not self.rx.search("    proc.send_signal(signal.SIGTERM)")


# ---- AF-AP-59 (TEST_SCREEN): world-scoped process sweep in a test ----

class TestAFAP59:
    rx = _TEST_BY_ID["AF-AP-59"]

    def test_fires_on_pgrep_f_pattern(self):
        assert self.rx.search('out = subprocess.run(["pgrep", "-f", "import time; time.sleep"], capture_output=True)')

    def test_fires_on_shell_pgrep_f(self):
        assert self.rx.search('subprocess.run("pgrep -f time.sleep", shell=True)')

    def test_fires_on_bare_ps_census(self):
        assert self.rx.search('rows = subprocess.run(["ps", "-eo", "pid,ppid,stat,args"], capture_output=True)')

    def test_no_fire_on_pgrep_own_child(self):
        assert not self.rx.search('kids = subprocess.run(["pgrep", "-P", str(tee_proc.pid)], capture_output=True)')

    def test_no_fire_on_own_proc_stat(self):
        assert not self.rx.search('stat = Path(f"/proc/{gc_pid}/stat").read_text()')
