"""Tests for .claude/hooks/edit-snapshot.py AP_SCREEN and TEST_SCREEN rows.

8-verify F17: asserts fire/no-fire pairs for AF-AP-33..38 so the screen rows
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
