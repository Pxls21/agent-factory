"""S0-11: Evaluation hardening conformance checker.

Asserts:
  1. Runner design doc exists covering three AlphaEval hazards
     (host networking, chmod 777, credential passing).
  2. A rubric process runs in a separate cwd with no credential
     env vars and no network (netns applied via unshare --net).
  3. Grep sweep finds zero chmod-777 or host-network patterns
     in the proof's executable code.

Usage:
  check_eval_hardening.py <proof-dir>
  check_eval_hardening.py --rubric-neg <fixture> <proof-dir>

Exit 0 + "PASS" on success; exit 1 + reason on failure.
"""
import json
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

CREDENTIAL_VARS = [
    "OPENAI_API_KEY",
    "ANTHROPIC_API_KEY",
    "OMNIROUTE_API_KEY",
    "HERMES_API_KEY",
]

CREDENTIAL_SUFFIX = re.compile(r"(_SECRET|_TOKEN|_CREDENTIAL)$", re.IGNORECASE)

HAZARD_COVERAGE = {
    "host-networking": re.compile(
        r"(no\s+host\s+network|network\s+isolation|netns|"
        r"unshare\s+--net|CLONE_NEWNET)",
        re.IGNORECASE,
    ),
    "chmod-777": re.compile(
        r"(no.*chmod\s+777|permission\s+hardening|"
        r"never\s+appl(y|ies)\s+recursive\s+permission)",
        re.IGNORECASE,
    ),
    "credential-passing": re.compile(
        r"(no.*credential\s+pass|credential\s+isolation|"
        r"strip.*credential|credential.*strip)",
        re.IGNORECASE,
    ),
}

PROHIBITED_CODE_PATTERNS = [
    (re.compile(r"chmod\s+(-[a-zA-Z]*R[a-zA-Z]*\s+)?777"), "chmod 777"),
    (re.compile(r"--network[= ]host"), "--network host"),
    (re.compile(r"network_mode.*host"), "network_mode host"),
]


def _clean_env():
    env = {}
    for k, v in os.environ.items():
        if k in CREDENTIAL_VARS:
            continue
        if CREDENTIAL_SUFFIX.search(k):
            continue
        env[k] = v
    return env


def check_runner_design(proof_dir: Path) -> bool:
    design = proof_dir / "runner_design.md"
    if not design.exists():
        print("runner-design-missing: " + str(design))
        return False

    text = design.read_text()
    for hazard_name, pattern in HAZARD_COVERAGE.items():
        if not pattern.search(text):
            print("runner-design-incomplete: missing coverage of " + hazard_name)
            return False

    return True


def check_rubric_isolation(proof_dir: Path) -> bool:
    probe = proof_dir / "fixtures" / "rubric_probe.py"
    if not probe.exists():
        print("rubric-probe-missing: " + str(probe))
        return False

    with tempfile.TemporaryDirectory(prefix="rubric-") as rubric_cwd:
        env = _clean_env()
        env["RUBRIC_TASK_ID"] = "probe-001"
        env["RUBRIC_CWD"] = rubric_cwd

        saved_key = os.environ.get("OPENAI_API_KEY")
        os.environ["OPENAI_API_KEY"] = "sk-test-fake-credential-for-probe"
        try:
            probe_env = _clean_env()
            probe_env["RUBRIC_TASK_ID"] = "probe-001"
            probe_env["RUBRIC_CWD"] = rubric_cwd

            r = subprocess.run(
                ["unshare", "--net", "--", sys.executable, str(probe)],
                capture_output=True, text=True, timeout=15,
                cwd=rubric_cwd, env=probe_env,
            )
        finally:
            if saved_key is not None:
                os.environ["OPENAI_API_KEY"] = saved_key
            else:
                os.environ.pop("OPENAI_API_KEY", None)

        if r.returncode != 0:
            print("rubric-probe-failed: rc=" + str(r.returncode) + ": " + r.stderr)
            return False

        try:
            report = json.loads(r.stdout)
        except json.JSONDecodeError:
            print("rubric-probe-bad-output: " + repr(r.stdout))
            return False

        if report.get("has_credential_env"):
            keys = report.get("credential_keys_found", [])
            print("rubric-isolation-failure: credential env vars present: " + str(keys))
            return False

        if not report.get("net_isolated"):
            print("rubric-isolation-failure: network not isolated")
            return False

        probe_cwd = report.get("cwd", "")
        if not probe_cwd.startswith(rubric_cwd):
            print("rubric-isolation-failure: cwd mismatch (expected under " + rubric_cwd + ", got " + probe_cwd + ")")
            return False

    return True


def check_grep_sweep(proof_dir: Path) -> bool:
    for path in proof_dir.rglob("*"):
        if not path.is_file():
            continue
        if path.suffix not in (".py", ".sh"):
            continue
        if path.name == "check_eval_hardening.py":
            continue

        text = path.read_text(errors="replace")
        for pattern, label in PROHIBITED_CODE_PATTERNS:
            match = pattern.search(text)
            if match:
                rel = path.relative_to(proof_dir)
                print("grep-sweep-violation: " + str(rel) + ": " + label)
                return False

    return True


def rubric_neg(fixture: Path, proof_dir: Path) -> int:
    if not fixture.exists():
        print("fixture-missing: " + str(fixture))
        return 1

    with tempfile.TemporaryDirectory(prefix="rubric-neg-") as rubric_cwd:
        env = _clean_env()
        env["RUBRIC_TASK_ID"] = "neg-001"
        env["RUBRIC_CWD"] = rubric_cwd

        r = subprocess.run(
            ["unshare", "--net", "--", sys.executable, str(fixture)],
            capture_output=True, text=True, timeout=15,
            cwd=rubric_cwd, env=env,
        )

    if r.returncode == 0:
        print("rubric-neg-unexpected-pass: fixture succeeded (should have failed)")
        return 1

    combined = r.stdout + r.stderr
    if "rubric-isolation-violation:" not in combined:
        print("rubric-neg-wrong-reason: rc=" + str(r.returncode) +
              ", stdout=" + repr(r.stdout) + ", stderr=" + repr(r.stderr))
        return 1

    for line in combined.splitlines():
        if "rubric-isolation-violation:" in line:
            print(line)
            break

    print("exit " + str(r.returncode) + " per contract")
    return r.returncode


def main():
    if len(sys.argv) < 2:
        print("usage: check_eval_hardening.py <proof-dir>")
        print("       check_eval_hardening.py --rubric-neg <fixture> <proof-dir>")
        return 1

    if sys.argv[1] == "--rubric-neg":
        if len(sys.argv) != 4:
            print("usage: check_eval_hardening.py --rubric-neg <fixture> <proof-dir>")
            return 1
        fixture = Path(sys.argv[2]).resolve()
        proof_dir = Path(sys.argv[3]).resolve()
        return rubric_neg(fixture, proof_dir)

    proof_dir = Path(sys.argv[1]).resolve()

    if not proof_dir.is_dir():
        print("proof-dir-missing: " + str(proof_dir))
        return 1

    if not check_runner_design(proof_dir):
        return 1

    if not check_rubric_isolation(proof_dir):
        return 1

    if not check_grep_sweep(proof_dir):
        return 1

    print("PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
