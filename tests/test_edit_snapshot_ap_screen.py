"""Tests for .claude/hooks/edit-snapshot.py: the AP_SCREEN and TEST_SCREEN rows, and pyflakes_delta's fail-soft contract.

8-verify F17: asserts fire/no-fire pairs for AF-AP-33..45 so the screen rows
have a test gate and cannot be silently weakened.
"""
import errno
import importlib.util
import io
import json
import subprocess
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


# ---- AF-AP-70 (AP_SCREEN): classify-then-open by pathname ----

class TestAFAP70:
    rx = _AP_BY_ID["AF-AP-70"]

    def test_fires_on_refuse_then_write_text(self):
        src = 'if _refuse_non_regular(slot):\n    raise _RecordSlotError(slot)\nslot.write_text(json.dumps(rec))'
        assert self.rx.search(src)

    def test_fires_on_isreg_then_open(self):
        src = 'if not stat.S_ISREG(os.stat(p).st_mode):\n    return 2\nwith open(p, "w") as fh:\n    fh.write(x)'
        assert self.rx.search(src)

    def test_no_fire_on_atomic_open_after_classification(self):
        src = 'st = os.lstat(p)\nfd = os.open(p, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW | os.O_NONBLOCK, 0o600)'
        assert not self.rx.search(src)

    def test_no_fire_on_write_without_classification(self):
        assert not self.rx.search('out.write_text(json.dumps(record) + "\\n")')


# ---- AF-AP-71 (AP_SCREEN): a bounded query upstream of a completeness gate ----

class TestAFAP71:
    rx = _AP_BY_ID["AF-AP-71"]

    def test_fires_on_parameterised_limit(self):
        assert self.rx.search('"WHERE requested_model = ? ORDER BY timestamp ASC LIMIT ?"')

    def test_fires_on_literal_limit(self):
        assert self.rx.search("SELECT id FROM call_logs ORDER BY timestamp LIMIT 50")

    def test_no_fire_on_a_constant_named_limit(self):
        assert not self.rx.search("RATE_LIMIT = 5")

    def test_no_fire_on_python_keyword_argument(self):
        assert not self.rx.search("rows = fetch(route, limit=limit)")


# ---- AF-AP-72 (AP_SCREEN): a typed upstream field coerced ----

class TestAFAP72:
    rx = _AP_BY_ID["AF-AP-72"]

    def test_fires_on_bool_of_subscript(self):
        assert self.rx.search('receipt["accepted"] = bool(blob["accepted"])')

    def test_fires_on_int_of_get(self):
        assert self.rx.search('uid = int(record.get("uid"))')

    def test_no_fire_on_bool_of_a_local(self):
        assert not self.rx.search("ready = bool(flag)")

    def test_no_fire_on_isinstance(self):
        assert not self.rx.search('if not isinstance(blob["accepted"], bool):')


# ---- AF-AP-80 (TEST_SCREEN): a source-text pin as the only guard of a behavioral property ----
def test_af_ap_80_flags_source_text_pins_and_spares_behavioral_asserts():
    rx = _TEST_BY_ID["AF-AP-80"]
    # the three shapes seen on 2026-09-15: a read_text() substring, an ast.unparse() presence check, an `in source` inventory
    assert rx.search('    assert "close_fds=True" in Path("acp_probe.py").read_text()')
    assert rx.search('    assert "pins.is_pinned_argv" in ast.unparse(classifier)')
    assert rx.search('    assert "os.O_NOFOLLOW" in source')
    # behavioral asserts are not pins: an exception's text, an observed stderr, an fd delta, a received line
    assert not rx.search('    assert "ELOOP" in str(exc.value)')
    assert not rx.search('    assert observed["stderr"] in expected')
    assert not rx.search('    assert fd_delta == 0')
    assert not rx.search('    assert "x" in received_lines')


# ---- AF-AP-115 (AP_SCREEN): a trust-boundary executable resolved from the caller's PATH ----

class TestAFAP115:
    rx = _AP_BY_ID["AF-AP-115"]

    def test_fires_on_shutil_which(self):
        assert self.rx.search('    gpg = shutil.which("gpg")')

    def test_fires_on_environ_get_path_forwarded(self):
        assert self.rx.search('env = {"GNUPGHOME": home, "PATH": os.environ.get("PATH", "/usr/bin:/bin")}')

    def test_fires_on_environ_subscript_path(self):
        assert self.rx.search("child_env['PATH'] = os.environ['PATH']")

    def test_no_fire_on_fixed_path(self):
        assert not self.rx.search('gpg = "/usr/bin/gpg"')

    def test_no_fire_on_other_environ_key(self):
        assert not self.rx.search('home = os.environ.get("HOME")')


# ---- AF-AP-127 (AP_SCREEN): a pattern redaction applied to an already-capped slice ----

class TestAFAP127:
    rx = _AP_BY_ID["AF-AP-127"]

    def test_fires_on_scrub_of_a_capped_slice(self):
        assert self.rx.search('days.append(f"{scrub(txt[:cap])}")')

    def test_fires_on_redact_of_a_capped_attribute_slice(self):
        assert self.rx.search("out = redact(self.body[: limit])")

    def test_no_fire_on_scrub_then_cap(self):
        assert not self.rx.search('days.append(f"{scrub(txt)[:cap]}")')

    def test_no_fire_on_a_suffix_slice(self):
        assert not self.rx.search("rest = scrub(txt[1:])")


# ---- AF-AP-159 (AP_SCREEN): a line number computed from a YAML node's start mark ----

class TestAFAP159:
    rx = _AP_BY_ID["AF-AP-159"]

    def test_fires_on_the_j1_0_r5_line_map(self):
        assert self.rx.search('runs.append((value.start_mark.line + (2 if value.style in ("|", ">") else 1), value.value,')

    def test_fires_without_spaces(self):
        assert self.rx.search("first = node.start_mark.line+1")

    def test_no_fire_on_the_token_line_lookup(self):
        assert not self.rx.search("line = token_line.get(value.end_mark.index, value.start_mark.line)")

    def test_no_fire_on_the_token_map(self):
        assert not self.rx.search("token_line = {t.end_mark.index: t.start_mark.line for t in yaml.scan(content)")

    def test_fires_on_the_right_operand_form(self):
        # issue #57 F-2: the start line as the RIGHT operand of the sum is the same line map
        assert self.rx.search("first = 2 + node.start_mark.line")

    def test_no_fire_on_a_right_operand_column(self):
        # a column offset is not a line map
        assert not self.rx.search("col = 2 + node.start_mark.column")


# ---- AF-AP-139 (AP_SCREEN and TEST_SCREEN): an HTTP stand-in more permissive than the service ----

# tests/test_s0_05_egress.py before E3-b (76f439f^:1579-1583): the embedded server logs the path, never branches on it
PRE_FIX_S0_05_LISTENER = r'''
        "class H(http.server.BaseHTTPRequestHandler):\n"
        "    def do_GET(self):\n"
        "        with open(LOG, 'a') as fh:\n"
        "            fh.write(self.client_address[0] + ' ' + self.path + '\\n')\n"
        "        self.send_response(200); self.end_headers(); self.wfile.write(b'{}')\n"
'''


class TestAFAP139:
    rx = _AP_BY_ID["AF-AP-139"]

    def test_the_same_row_screens_tests(self):
        # the registry's instance was a test stand-in, and the hook screens /tests/ paths with TEST_SCREEN only
        assert _TEST_BY_ID["AF-AP-139"] is self.rx

    def test_fires_on_the_pre_fix_s0_05_listener(self):
        assert self.rx.search(PRE_FIX_S0_05_LISTENER)

    def test_fires_on_a_class_handler_that_always_answers_200(self):
        assert self.rx.search("    def do_POST(self):\n        body = self.rfile.read(n)\n        self.send_response(200)\n")

    def test_no_fire_on_a_status_keyed_on_the_path(self):
        # the E3-b fix: the stand-in's status comes from a per-path map
        assert not self.rx.search("    def do_GET(self):\n        self.send_response(STATUS.get(self.path, 200)); self.end_headers()\n")

    def test_no_fire_when_the_handler_branches_on_the_path(self):
        src = ('    def do_GET(self):\n        if self.path == "/health":\n            self.send_response(200)\n'
               "        else:\n            self.send_response(404)\n")
        assert not self.rx.search(src)

    def test_no_fire_on_a_literal_200_outside_a_handler(self):
        assert not self.rx.search("    def _stream(self, model):\n        self.send_response(200)\n")

    def test_fires_on_a_handler_annotated_to_return_none(self):
        # VERIFY-K150 F-06 (its near miss A1): the return annotation does not change the class
        assert self.rx.search("    def do_GET(self) -> None:\n        self.send_response(200)\n        self.end_headers()\n")

    def test_fires_on_an_http_status_member(self):
        # VERIFY-K150 F-06 (A2): HTTPStatus.OK is the same 2xx as the literal
        assert self.rx.search("    def do_GET(self):\n        self.send_response(HTTPStatus.OK)\n        self.end_headers()\n")

    def test_no_fire_on_a_handler_that_always_refuses(self):
        # VERIFY-K150 F-06 (its mutant K3, any status): an always-401 stand-in refuses every request, so it is not more
        # permissive than the service it stands in for
        assert not self.rx.search("    def do_GET(self):\n        self.send_response(401)\n        self.end_headers()\n")


# ---- AF-AP-25 (AP_SCREEN): a regex line parser that skips a line it does not recognise ----

class TestAFAP25:
    rx = _AP_BY_ID["AF-AP-25"]

    def test_fires_on_the_parse_sbom_loop(self):
        # scripts/vendored_manifest.py parse_sbom (VERIFY-REPIN-a F11's sibling)
        src = ('    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):\n'
               '        match = re.fullmatch(r"\\s*- name:\\s*(\\S+)\\s*", line)\n')
        assert self.rx.search(src)

    def test_fires_past_the_skip_prefix_of_parse_lock(self):
        src = ('    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):\n'
               '        if not line.strip() or line.lstrip().startswith("#"):\n'
               "            continue\n"
               '        if not line.startswith(" ") and line.endswith(":"):\n'
               "            section = line[:-1]\n"
               '            component = ""\n'
               "            continue\n"
               '        match = re.fullmatch(r"  ([a-z0-9][a-z0-9-]*):", line)\n')
        assert self.rx.search(src)

    def test_no_fire_on_a_jsonl_loop(self):
        # json.loads raises on a malformed line: the loop cannot skip one silently
        assert not self.rx.search("    for line in path.read_text().splitlines():\n        rows.append(json.loads(line))\n")

    def test_no_fire_on_a_single_value_match(self):
        assert not self.rx.search('    if not re.fullmatch(r"[0-9a-f]{40}", sha):\n        raise ManifestError(sha)\n')


# ---- AF-AP-89 (AP_SCREEN): a doubled escape inside a double-quoted bridge argument (AF-AP-162) ----

class TestAFAP89:
    rx = _AP_BY_ID["AF-AP-89"]

    def test_fires_on_the_t94_doubled_command_substitution(self):
        # T94's poll probe (scripts/pc_lane.sh, 2026-09-23): the lookup ran in the sandbox
        assert self.rx.search(r'probe="$(bridge "! kill -0 \\$(cat $PC_AF_REPO/.lanes/$LANE_ID/lane.pid 2>/dev/null) 2>/dev/null && echo READY")"')

    def test_fires_on_a_doubled_escaped_quote_through_pc_sh(self):
        assert self.rx.search(r'bash scripts/pc.sh "test ! -f $D/lane.pid && [ -n \\\"$X\\\" ] && echo RUNNING"')

    def test_no_fire_on_the_single_escape(self):
        # the correct form: the substitution is escaped once and resolves on the PC
        assert not self.rx.search(r'probe="$(bridge "kill -0 \$(cat $PC_AF_REPO/.lanes/$LANE_ID/lane.pid) 2>/dev/null && echo RUNNING")"')

    def test_no_fire_outside_a_bridge_argument(self):
        assert not self.rx.search(r'echo "a literal \\$(date) for the log"')

    def test_no_fire_after_the_argument_closes(self):
        assert not self.rx.search(r'bridge "uptime"; echo "\\$(date)"')


# ---- AF-AP-132 (AP_SCREEN): a line number computed with str.splitlines() ----

class TestAFAP132:
    rx = _AP_BY_ID["AF-AP-132"]

    def test_fires_on_the_no_laya_screen_loop(self):
        # scripts/no_laya_in_gates.py:1443 at the K215 PIN, an open site the registry names
        assert self.rx.search("        for lineno, line in enumerate(content.splitlines(), 1):\n")

    def test_fires_on_the_parse_lock_loop(self):
        # scripts/vendored_manifest.py:759 at the K215 PIN (parse_lock), the other open site
        assert self.rx.search('    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):\n')

    def test_fires_on_a_list_from_splitlines_enumerated_with_a_start(self):
        # scripts/vendored_manifest.py:575-577 (parse_classes): the same line map spelled over two statements
        src = ('    lines = text.splitlines()\n'
               '    if not lines or lines[0] != "path\\tclass":\n'
               '        raise ManifestError(".claude class file parse failure at line 1")\n'
               '    classes: dict[str, str] = {}\n'
               '    for line_number, line in enumerate(lines[1:], start=2):\n')
        assert self.rx.search(src)

    def test_fires_on_a_literal_separator(self):
        # J1-2-R1's ledger held two literal separators in a set of bad characters: invisible, and a line break to splitlines
        assert self.rx.search("_BAD = frozenset('" + chr(0x2028) + chr(0x2029) + "')\n")

    def test_no_fire_on_the_newline_split(self):
        # the fix the registry names: number lines on "\n" only
        assert not self.rx.search('        for lineno, line in enumerate(content.split("\\n"), 1):\n')

    def test_no_fire_on_a_line_that_did_not_decode(self):
        # a binary file read with errors="replace" (a .gz evidence file named to ap_screen.py) holds U+FFFD beside the
        # byte pairs that decode as U+0085: that line is not source (275 such hits in 11 files at the K215 PIN)
        assert not self.rx.search("r" + chr(0xFFFD) + "C[" + chr(0x85) + "I\n")

    def test_no_fire_on_the_separator_written_as_its_escape(self):
        assert not self.rx.search("_BAD = frozenset('" + "\\" + "u2028" + "\\" + "u2029')\n")

    def test_no_fire_on_a_list_used_as_an_index(self):
        # an index into the list, never a line number
        src = ('    lines = text.splitlines()\n'
               '    header = next((i for i, line in enumerate(lines) if line.startswith("|")), None)\n')
        assert not self.rx.search(src)


# ---- AF-AP-141 (AP_SCREEN): a git history-walk exit code read as a yes/no ----

class TestAFAP141:
    rx = _AP_BY_ID["AF-AP-141"]

    def test_fires_on_the_check_proof_status_ancestry_check(self):
        # scripts/check-proof-status.py:164, the registry's WATCH site
        assert self.rx.search('    if _git(repo_root, "merge-base", "--is-ancestor", commit, "HEAD").returncode != 0:\n')

    def test_fires_on_a_cat_file_existence_check(self):
        # scripts/ci_gate.py:213, the OPEN sibling (issue #40)
        assert self.rx.search('    if _git(root, "cat-file", "-e", f"{sha}^{{commit}}")[0] != 0:\n')

    def test_fires_on_a_shell_existence_check(self):
        # scripts/pc_suite.sh:67 spells it in shell: stderr discarded, the exit code decides
        assert self.rx.search('  bridge "cd $PC_AF_REPO && { git cat-file -e $BASE^{commit} 2>/dev/null && echo HAVE; }"\n')

    def test_no_fire_when_the_error_text_is_bound(self):
        # scripts/ci_gate.py:207, the fix: rc, out and err come back together and err is read
        assert not self.rx.search('    rc, _, err = _git(root, "merge-base", "--is-ancestor", sha, origin_sha)\n')

    def test_no_fire_on_other_git_calls(self):
        assert not self.rx.search('    base = _git(root, "merge-base", sha, origin_sha).stdout.strip()\n')
        assert not self.rx.search('    tagged = _git(repo_root, "cat-file", "-p", f"{commit}:{rel}", binary=True)\n')


# ---- AF-AP-144 (AP_SCREEN, path-scoped by the hook's main): a raw parse call in a proof checker ----

class TestAFAP144:
    row = _AP_BY_ID["AF-AP-144"]

    def test_fires_in_a_proof_checker(self):
        # proofs/S0-12/check_pin_diff.py:33, a WATCH site: yaml.safe_load of a committed file, no handler in main
        assert self.row.for_path("/repo/proofs/S0-12/check_pin_diff.py").search("    sbom = yaml.safe_load(sbom_text)\n")

    def test_fires_on_a_default_encoding_read_and_a_decode(self):
        rx = self.row.for_path("proofs/S0-07/check_fubuki_corrections.py")
        assert rx.search('    review_text = (fixture_dir / "01-review-only.txt").read_text()\n')
        assert rx.search("    text = raw.decode()\n")

    def test_no_fire_outside_the_checker_paths(self):
        hunk = "    sbom = yaml.safe_load(sbom_text)\n"
        assert not self.row.for_path("/repo/proofs/S0-12/tools/check_helper.py").search(hunk)
        assert not self.row.for_path("/repo/scripts/check-proof-status.py").search(hunk)

    def test_no_fire_on_a_read_that_names_its_encoding(self):
        # the signature is the DEFAULT-encoding read; an explicit encoding is a different line
        assert not self.row.for_path("proofs/S0-07/check_x.py").search('    text = path.read_text(encoding="utf-8")\n')

    def test_the_path_less_callers_see_nothing(self):
        # scripts/ap_screen.py and scripts/lint_delta.py pass text alone, so the scope cannot apply there
        assert self.row.search("json.loads(x)\n") is None
        assert list(self.row.finditer("json.loads(x)\n")) == []


def _snapshot(monkeypatch, capsys, path, hunk):
    """The hook's real main on an Edit payload; the slow probes (git history, pyflakes) answer nothing."""
    monkeypatch.setattr(_mod, "file_chronology", lambda fp, n=3: [])
    monkeypatch.setattr(_mod, "pyflakes_delta", lambda fp, src: [])
    payload = {"tool_name": "Edit", "tool_input": {"file_path": str(path), "new_string": hunk}}
    monkeypatch.setattr(_mod.sys, "stdin", io.StringIO(json.dumps(payload)))
    assert _mod.main() == 0
    return capsys.readouterr().out


def test_af_ap_144_the_hook_applies_the_path_scope(monkeypatch, capsys, tmp_path):
    hunk = "sbom = yaml.safe_load(open(p).read())\n"
    checker = tmp_path / "proofs" / "S0-99" / "check_pins.py"
    helper = tmp_path / "proofs" / "S0-99" / "tools" / "pins.py"
    for path in (checker, helper):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(hunk, encoding="utf-8")
    assert "/tests/" not in str(tmp_path)  # a /tests/ path takes the TEST_SCREEN branch instead
    assert "AF-AP-144" in _snapshot(monkeypatch, capsys, checker, hunk)
    assert "AF-AP-144" not in _snapshot(monkeypatch, capsys, helper, hunk)


# ---- AF-AP-145 (AP_SCREEN, shell): an EXIT-trap cleanup that a second signal can abort ----

# proofs/S0-05/tools/pc/run_s0_05_units.sh before E3-R1 (97b589a^:322-336), shortened
PRE_FIX_S0_05_CLEANUP = (
    "cleanup() {\n"
    "  local ns owner_pid pid dir\n"
    "  for ns in $NS_LIVE; do\n"
    '    ip netns del "$ns"\n'
    "  done\n"
    "}\n"
    "trap cleanup EXIT\n"
)
FIXED_S0_05_CLEANUP = (
    "cleanup() {\n"
    "  trap '' INT TERM\n"
    "  local ns owner_pid pid dir\n"
    "}\n"
    "trap cleanup EXIT\n"
    "trap 'trap \"\" INT TERM; exit 130' INT\n"
    "trap 'trap \"\" INT TERM; exit 143' TERM\n"
)


class TestAFAP145:
    rx = _AP_BY_ID["AF-AP-145"]

    def test_fires_on_the_pre_fix_s0_05_cleanup(self):
        assert self.rx.search(PRE_FIX_S0_05_CLEANUP)

    def test_fires_when_the_trap_line_comes_first(self):
        # bash resolves the name when the trap runs, so a trap above its function is the same cleanup
        assert self.rx.search("trap cleanup EXIT\n\ncleanup() {\n  ip netns del \"$NS\"\n}\n")

    def test_fires_on_a_handler_without_the_ignore(self):
        # the pre-fix handlers (97b589a^:335-336): E3-R1 measured the cleanup ignore alone still aborting
        assert self.rx.search("trap 'exit 143' TERM\n")

    def test_no_fire_on_the_fixed_s0_05_runner(self):
        assert not self.rx.search(FIXED_S0_05_CLEANUP)

    def test_no_fire_when_a_status_capture_comes_first(self):
        # harness-ports/bin/qwen-matrix.sh:94-96 after task #176: `$?` must be read before any other command
        src = "cleanup() {\n  local rc=$?\n  trap '' INT TERM\n  trap - EXIT\n}\ntrap cleanup EXIT\n"
        assert not self.rx.search(src)

    def test_no_fire_on_a_function_no_exit_trap_names(self):
        assert not self.rx.search("stop_all() {\n  kill $pid\n}\ntrap stop_all RETURN\n")

    def test_fires_on_a_bare_exit_after_the_handler_traps(self):
        # VERIFY-GW1-R1 R-2: ONE TERM right after this `exit 1` ran the handler's exit inside the EXIT trap
        assert self.rx.search(FIXED_S0_05_CLEANUP + "if [ -n \"$failed\" ]; then\n  exit 1\nfi\n")

    def test_no_fire_on_exits_that_ignore_first_or_come_before_the_handlers(self):
        src = ("usage() { echo usage >&2; exit 64; }\n" + FIXED_S0_05_CLEANUP.replace("trap cleanup EXIT\n", "")
               + "leave() { trap '' INT TERM; exit \"$1\"; }\ntrap cleanup EXIT\n"
               + "[ -n \"$x\" ] || leave 1\n  trap '' INT TERM; exit 2\nexit_code=3\n")
        assert not self.rx.search(src)

    def test_no_fire_on_an_exit_when_no_exit_trap_runs_a_cleanup(self):
        assert not self.rx.search("trap 'trap \"\" INT TERM; exit 143' TERM\nexit 1\n")

    def test_no_fire_on_exits_after_an_ignore_that_is_not_a_handler(self):
        # scripts/push_clean.sh (task #243): its EXIT-trap cleanup opens with `trap '' INT TERM`; it arms no handler
        src = "back() {\n  trap '' INT TERM\n  rm -f x\n}\ntrap back EXIT\n[ -n \"$a\" ] || { echo no >&2; exit 2; }\n"
        assert not self.rx.search(src)


# ---- AF-AP-149 (AP_SCREEN): a private-key block rule written for one label spelling ----

class TestAFAP149:
    rx = _AP_BY_ID["AF-AP-149"]

    def test_fires_on_the_first_decisions_redactor(self):
        # the J1-1 redactor (01ca7d5, _PRIVKEY): one label spelling and no end-of-text alternative
        assert self.rx.search('    r"-----BEGIN [A-Z ]*PRIVATE KEY-----.*?-----END [A-Z ]*PRIVATE KEY-----",\n')

    def test_fires_on_the_pre_fix_transcript_exporter(self):
        # scripts/transcript_export.py before 9932f34 (:27): the END is optional, the label still one spelling
        assert self.rx.search(r'''    (re.compile(r"-----BEGIN [A-Z0-9 ]*PRIVATE KEY-----.*?(?:-----END [A-Z0-9 ]*PRIVATE KEY-----|\Z)", re.S),''')

    def test_fires_on_a_rule_that_needs_the_end_line(self):
        src = r'''    re.compile(r"-----BEGIN [A-Z ]*(?:PRIVATE|SECRET) KEY(?: BLOCK)?-----.*?-----END [A-Z ]*(?:PRIVATE|SECRET) KEY(?: BLOCK)?-----", re.S)'''
        assert self.rx.search(src)

    def test_no_fire_on_the_fixed_transcript_exporter(self):
        # 9932f34 and after: both label families on the BEGIN line; the END line ends in |\Z on the next line
        assert not self.rx.search('    (re.compile(r"-----BEGIN [A-Z0-9 ]*(?:PRIVATE|SECRET) KEY(?: BLOCK)?-----.*?"\n')

    def test_no_fire_on_a_literal_key_fixture(self):
        # a test's fake key block is text, not a rule
        assert not self.rx.search('    pem = "-----BEGIN RSA PRIVATE KEY-----\\n" + KEY_BODY + "\\n-----END RSA PRIVATE KEY-----"\n')


# ---- AF-AP-152 (AP_SCREEN): a scrubber regex whose cost grows faster than its input ----

class TestAFAP152:
    rx = _AP_BY_ID["AF-AP-152"]

    def test_fires_on_the_nested_name_prefix_group(self):
        # the J1-1 redactor's _ENVVAL (01ca7d5): 8.14 s at 26 repeats of `A_`, doubling per repeat (J1-1-R1 D-3)
        assert self.rx.search(r'''    r"(?P<name>(?:[A-Z][A-Z0-9_]*_)*(?:KEY|TOKEN|SECRET|PASSWORD|PASSWD|API_?KEY))=\S+"''')

    def test_fires_on_an_unanchored_class_alternative(self):
        # task #187's first widening of scripts/transcript_export.py's name rule (caught at design): 17.4 s on a 40k run
        assert self.rx.search(r'''_NAME = (r"(?:AGENT_TOKEN|PC_BRIDGE_TOKEN|X-Agent-Token|[A-Za-z0-9]*[_-]key|api[_-]?key"''')

    def test_no_fire_on_the_anchored_alternative(self):
        # the shipped rule: a lookbehind in front makes the alternative start only where a name can start
        assert not self.rx.search(r'''_NAME = (r"(?:AGENT_TOKEN|PC_BRIDGE_TOKEN|X-Agent-Token|(?<![A-Za-z0-9])[A-Za-z0-9]*[_-]key|[_-]key"''')

    def test_no_fire_on_a_group_with_a_required_separator(self):
        # each repeat must begin with `-`, which the class cannot take: one way to split, linear
        assert not self.rx.search(r'''KIND_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")''')

    def test_no_fire_on_a_negated_class(self):
        assert not self.rx.search(r'''PAIRS = re.compile(r"(?:[^_]*_)*end")''')


# ---- AF-AP-175 (AP_SCREEN): a moving ref resolved per read ----

class TestAFAP175:
    rx = _AP_BY_ID["AF-AP-175"]

    def test_fires_on_each_read_of_j1_3s_harvester(self):
        # J1-3 before R1 (0d62801^:141 and :152): an admission read and a content read, each naming HEAD
        assert self.rx.search('    result = _git(root, "ls-tree", "-r", "--name-only", "-z", "HEAD")\n')
        assert self.rx.search('    result = _git(root, "cat-file", "blob", f"HEAD:{path}")\n')

    def test_fires_on_the_single_resolve(self):
        # the fix reads the ref once; the row still names it, and the message asks for the count
        assert self.rx.search('    result = _git(root, "rev-parse", "--verify", "HEAD^{commit}")\n')

    def test_no_fire_on_a_threaded_sha(self):
        assert not self.rx.search('    result = _git(root, "cat-file", "blob", f"{commit}:{path}")\n')

    def test_no_fire_on_other_refs_or_prose(self):
        assert not self.rx.search('    orig = _git(root, "rev-parse", "ORIG_HEAD")\n')
        assert not self.rx.search('        out.append(f"  {tag} NEW pyflakes hit vs HEAD: {m}")\n')


# ---- AF-AP-177 (AP_SCREEN): a parsed JSON value used as a hash key before its type is checked ----

J1_3_R1_DISPATCH_SCAN = (
    '            if not isinstance(block, dict) or block.get("type") != "tool_use" or block.get("name") not in {"Agent", "Task"}:\n'
    "                continue\n"
    '            inputs = block.get("input")\n'
    '            role = inputs.get("subagent_type") if isinstance(inputs, dict) else None\n'
    '            tool_id = block.get("id")\n'
    '            if role in {"hive-scout", "hive-reviewer"}:\n'
)


class TestAFAP177:
    rx = _AP_BY_ID["AF-AP-177"]

    def test_fires_on_a_get_tested_against_a_set(self):
        # J1-3-R1's harvester (0d62801:686): a JSON list in `name` raises TypeError, rc 1, no harvest line
        assert self.rx.search(J1_3_R1_DISPATCH_SCAN.splitlines()[0])

    def test_fires_on_the_variable_held_form(self):
        # 0d62801:689-691: the value is bound first, then tested two lines later (the first line's form removed)
        assert self.rx.search("\n".join(J1_3_R1_DISPATCH_SCAN.split("\n")[2:]))

    def test_fires_on_the_qwen_matrix_role_check(self):
        # harness-ports/bin/qwen_matrix.py:263, the sibling the registry's sweep found
        assert self.rx.search('            and message.get("role") in {"system", "user", "assistant", "tool"}\n')

    def test_no_fire_after_a_str_check(self):
        assert not self.rx.search('    ok = isinstance(block.get("name"), str) and block.get("name") in {"Agent", "Task"}\n')
        src = ('    role = inputs.get("subagent_type")\n'
               '    if not isinstance(role, str):\n'
               '        return None\n'
               '    if role in {"hive-scout", "hive-reviewer"}:\n')
        assert not self.rx.search(src)

    def test_no_fire_on_a_string_method_result(self):
        # the harvester's table-header check: .lower() returns a str, so the set test cannot raise
        assert not self.rx.search('            and headers[0].strip().lower() in {"#", "id"}\n')


# ---- AF-AP-44, the hook instance: pyflakes_delta is a tell, never a blocker ----
# 2026-09-23 (the D-048 PC run, VERIFY-REPIN-a F4): with AF_VENV unset the venv path is under /root, and a lane user
# (/root mode 0550) got PermissionError from Path.exists() outside the function's try, so the hook crashed (three
# harness suites red in a bare PC shell). Root in the sandbox is never refused by the kernel, so each test makes one
# probe of the venv path raise that error.

def test_pyflakes_delta_is_empty_when_the_venv_probe_raises(monkeypatch, tmp_path):
    path_cls = type(Path())
    real_exists = path_cls.exists

    def exists(self, *args, **kwargs):
        if str(self) == _mod._VENV_PY:
            raise PermissionError(13, "Permission denied", str(self))
        return real_exists(self, *args, **kwargs)

    monkeypatch.setattr(path_cls, "exists", exists)
    edited = tmp_path / "edited.py"
    edited.write_text("import os\n", encoding="utf-8")
    assert _mod.pyflakes_delta(str(edited), "import os\n") == []


def test_pyflakes_delta_is_empty_when_running_the_venv_python_raises(monkeypatch, tmp_path):
    path_cls = type(Path())
    real_exists, real_run = path_cls.exists, _mod.subprocess.run
    monkeypatch.setattr(path_cls, "exists", lambda self, *a, **kw: str(self) == _mod._VENV_PY or real_exists(self, *a, **kw))

    def run(argv, *args, **kwargs):
        if argv[0] == _mod._VENV_PY:
            raise PermissionError(13, "Permission denied", argv[0])
        return real_run(argv, *args, **kwargs)

    monkeypatch.setattr(_mod.subprocess, "run", run)
    edited = tmp_path / "edited.py"
    edited.write_text("import os\n", encoding="utf-8")
    assert _mod.pyflakes_delta(str(edited), "import os\n") == []


# VERIFY-K150 F-07: the two tests above pin only PermissionError, so a catch narrowed to it (or to OSError) passed them
# while the hook crashed again on the other failures of the same probes (its mutants K14 and K15, measured through the
# real main), and an absent venv answering a line (K16) printed a false tell. One control per failure.

def test_pyflakes_delta_is_empty_when_the_venv_path_is_too_long(monkeypatch, tmp_path):
    # an overlong AF_VENV: the probe raises ENAMETOOLONG, an OSError that is not a PermissionError
    path_cls = type(Path())
    real_exists = path_cls.exists

    def exists(self, *args, **kwargs):
        if str(self) == _mod._VENV_PY:
            raise OSError(errno.ENAMETOOLONG, "File name too long", str(self))
        return real_exists(self, *args, **kwargs)

    monkeypatch.setattr(path_cls, "exists", exists)
    edited = tmp_path / "edited.py"
    edited.write_text("import os\n", encoding="utf-8")
    assert _mod.pyflakes_delta(str(edited), "import os\n") == []


def test_pyflakes_delta_is_empty_when_the_venv_python_times_out(monkeypatch, tmp_path):
    # a venv python that hangs past PROBE_TIMEOUT: subprocess.TimeoutExpired, which is not an OSError
    path_cls = type(Path())
    real_exists, real_run = path_cls.exists, _mod.subprocess.run
    monkeypatch.setattr(path_cls, "exists", lambda self, *a, **kw: str(self) == _mod._VENV_PY or real_exists(self, *a, **kw))

    def run(argv, *args, **kwargs):
        if argv[0] == _mod._VENV_PY:
            raise subprocess.TimeoutExpired(argv, kwargs.get("timeout"))
        return real_run(argv, *args, **kwargs)

    monkeypatch.setattr(_mod.subprocess, "run", run)
    edited = tmp_path / "edited.py"
    edited.write_text("import os\n", encoding="utf-8")
    assert _mod.pyflakes_delta(str(edited), "import os\n") == []


def test_pyflakes_delta_is_empty_when_the_venv_is_absent(monkeypatch, tmp_path):
    # no venv python at all: no tell, not a line saying so
    monkeypatch.setattr(_mod, "_VENV_PY", str(tmp_path / "no-venv" / "bin" / "python"))
    edited = tmp_path / "edited.py"
    edited.write_text("import os\n", encoding="utf-8")
    assert _mod.pyflakes_delta(str(edited), "import os\n") == []


# ---- AF-AP-181 (TEST_SCREEN): a race handler whose fallback its own assert rejects ----

class TestAFAP181:
    rx = _TEST_BY_ID["AF-AP-181"]

    def test_fires_on_the_ci_1026_shape(self):
        # the exact shape CI run #1026 failed on (tests/test_s0_01_frame_tee.py before the fix)
        assert self.rx.search(
            '                except (OSError, IOError):\n'
            '                    proc_state = "gone"\n'
            '                assert proc_state == "Z", (\n')

    def test_fires_with_a_line_between_the_fallback_and_the_assert(self):
        assert self.rx.search(
            "    except KeyError:\n"
            "        verdict = 'missing'\n"
            "    log(verdict)\n"
            "    assert verdict == 'ok'\n")

    def test_no_fire_on_membership_of_every_acceptable_value(self):
        assert not self.rx.search(
            '                except (OSError, IOError):\n'
            '                    proc_state = "gone"\n'
            '                assert proc_state in ("Z", "gone"), (\n')

    def test_no_fire_when_the_assert_accepts_the_fallback(self):
        assert not self.rx.search(
            '    except OSError:\n'
            '        state = "gone"\n'
            '    assert state == "gone"\n')

    def test_no_fire_on_the_fixed_frame_tee_file(self):
        src = (Path(__file__).resolve().parents[1] / "tests" / "test_s0_01_frame_tee.py").read_text()
        assert not self.rx.search(src)


# ---- AF-AP-196: a trained artifact saved with no finiteness check on what is saved (VERIFY-FT1 F-1) ----

class TestAFAP196:
    rx = _AP_BY_ID["AF-AP-196"]

    def test_fires_on_the_ft1_save(self):
        assert self.rx.search("        torch.save(sd, str(tmp))\n")    # scripts/laya_ft/train.py before FT1-F

    def test_fires_on_the_other_tensor_writers(self):
        for line in ("save_file(tensors, path)", "model.save_pretrained(out_dir)", "np.save(path, arr)"):
            assert self.rx.search(line), line

    def test_no_fire_on_a_load_or_a_wrapper_call(self):
        for line in ("sd = torch.load(path, map_location='cpu')", "save_checkpoint(sd, out / 'checkpoint.pt')",
                     "torch.saved = 1"):
            assert not self.rx.search(line), line


# ---- AF-AP-197: a precondition checked after the work it protects (VERIFY-FT1 F-6) ----

class TestAFAP197:
    rx = _AP_BY_ID["AF-AP-197"]

    def test_fires_on_the_ft1_free_space_probe(self):
        assert self.rx.search("    free = shutil.disk_usage(path.parent).free\n")

    def test_fires_on_statvfs(self):
        assert self.rx.search("st = os.statvfs(out)")

    def test_no_fire_on_a_name_that_only_contains_the_word(self):
        for line in ("report = disk_usage_report", "print(statvfs_note)"):
            assert not self.rx.search(line), line


class TestAFAP200:
    rx = _AP_BY_ID["AF-AP-200"]

    def test_fires_on_the_first_stale_ids_header_parse(self):
        assert self.rx.search('        if raw.startswith("+++ "):')
        assert self.rx.search("            path = raw[6:] if raw.startswith('+++ b/') else None")

    def test_fires_on_the_skip_and_the_old_side_header(self):
        assert self.rx.search('if l.startswith("+") and not l.startswith("+++")]')
        assert self.rx.search('elif line.startswith("--- a/"):')

    def test_no_fire_on_front_matter_or_a_single_plus(self):
        for line in ('if line.startswith("---"):', 'elif raw.startswith("+"):', 'x.startswith("++")'):
            assert not self.rx.search(line), line


class TestAFAP201:
    rx = _AP_BY_ID["AF-AP-201"]

    def test_fires_on_the_crashing_request_body(self):
        assert self.rx.search('            "temperature": 0, "logprobs": True, "top_logprobs": 20, "prompt_logprobs": 0}')
        assert self.rx.search("params = SamplingParams(max_tokens=1, prompt_logprobs=0)")

    def test_fires_on_best_of(self):
        assert self.rx.search("body = {'model': m, 'best_of': 4}")
        assert self.rx.search("sp.best_of = 2")

    def test_no_fire_on_the_safe_logprob_options_names_or_a_comparison(self):
        for line in ('"logprobs": True, "top_logprobs": 20,', "report = prompt_logprobs_note",
                     "best_of_n = 3", "if params.prompt_logprobs == 0:"):
            assert not self.rx.search(line), line


class TestAFAP204:
    rx = _AP_BY_ID["AF-AP-204"]

    def test_fires_on_a_hardcoded_project_directory(self):
        # scripts/orient.sh:27 before the fix, and scripts/hiccup_scan.py:51, an open site the registry names
        assert self.rx.search('TR=$(ls -t /root/.claude/projects/-home-user-agent-factory/*.jsonl 2>/dev/null | head -1)')
        assert self.rx.search('DEFAULT_PROJECT_DIR = "/root/.claude/projects/-home-user"')

    def test_no_fire_on_the_glob_over_every_project_directory(self):
        for line in ('TR=$(ls -t /root/.claude/projects/*/*.jsonl 2>/dev/null | head -1)',
                     'cands = glob.glob("/root/.claude/projects/*/*.jsonl")', 'root = Path.home() / ".claude"'):
            assert not self.rx.search(line), line


class TestAFAP223:
    rx = _AP_BY_ID["AF-AP-223"]

    def test_fires_on_a_kill_verdict_from_the_exit_code_alone(self):
        # the verifier's mutate.py, the S1-L1 builder's harness and tasks/briefs/s0-01-b5c-support/probes/mut.py:197
        assert self.rx.search('print(f"{\'KILLED \' if r.returncode else \'SURVIVED\'} {name:70s}")')
        assert self.rx.search('results.append((name, "KILLED" if r.returncode != 0 else "SURVIVED", failed[:1], last))')
        assert self.rx.search("    killed = p.returncode != 0")
        assert self.rx.search('print((name, "KILLED" if base.returncode else "SURVIVED", last))')

    def test_no_fire_when_the_verdict_needs_a_failed_test_or_is_not_a_kill(self):
        for line in ('killed = bool(failed) and p.returncode == 1',
                     'killed = any(l.startswith("FAILED ") for l in out.splitlines())',
                     "if p.returncode != 0: raise SystemExit(p.returncode)",
                     "os.kill(pid, signal.SIGTERM) if proc.returncode is None else None",
                     "# killed when the returncode is non-zero (a comment, not a verdict)"):
            assert not self.rx.search(line), line
