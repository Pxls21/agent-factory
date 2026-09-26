"""I59-A (task #312, issue #59 F-1): every repo file a proof's checker reads while it grades is attested.

A proof's entry in `proofs/registry.yaml` may carry `extra_attested_inputs`: repo files OUTSIDE its directory that its
checker reads (an S0-01 module another proof loads, `upstream.lock.yaml`, an ADR). `proof_attestation()` hashes them beside
the proof's own files, so a change to one makes that proof INVALID. Three parts:

1. the registry key: each refusal by its exact finding (negative controls first), then the accepted declaration;
2. the attestation: a declared file hashed under its root-relative path, a proof's key set otherwise unchanged, a
   changed, deleted or never-present declared file INVALID, and the canonical runner recording the declaration;
3. the DRIFT GUARD: every proof's spec legs run as scripts/proof-runner runs them, with two instruments loaded in their
   Python processes, and every repo file a leg's processes open (the audit hook's `open` events) or test for existence
   or type (the second instrument: `os.stat`, `os.lstat` and `os.access` wrapped, so `os.path.exists/isfile/isdir` and
   `Path.exists/is_file/is_dir/stat` are seen) must be in that proof's attestation. A path built at run time is caught
   because the calls are observed, not parsed. Its negative controls plant, in a scratch copy of S0-09, one undeclared
   read of each shape and one undeclared existence test of each shape. (VERIFY-I59-A F-1: S0-12 tests two repo files
   for existence and never opens them; the contract amendment counts such a file as an input.)

What the guard cannot see (named here, not hidden):
- a child process that does not load the instruments (one started with an `env=` that drops PYTHONPATH, or with
  -I/-S/-E) and a non-Python child: a checker that starts a child process must be named in UNOBSERVED_CHILDREN with its
  reason, or the guard fails;
- a stat made below the `os` module (a C extension, or the import system's own `posix.stat`); a stat called with
  `dir_fd` (the wrapper skips it: its path is relative to a directory descriptor); an `os.readlink` type test (not
  wrapped); a test of a DIRECTORY or of a file's ABSENCE (neither can be declared: a declaration names a regular file
  that exists);
- a directory listing (`os.listdir`, `os.scandir`, `glob`, `Path.iterdir`);
- a C-level reader that raises no `open` audit event (`sqlite3.connect`, a `ctypes` `fopen`); no checker uses one today.
A stat of a `__pycache__` file is ignored (bytecode caches are never attested; S0-11's sweep stats its own, then skips
it). A proof whose leg defers (exit 2, the runner's capability-unavailable signal) or grades a path outside the repo that
this venue lacks is SKIPPED by name: its reads are not observed there.
"""
import hashlib
import importlib.machinery
import importlib.util
import json
import os
import py_compile
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
VALIDATOR = ROOT / "scripts" / "validate-ledger"
RUNNER = ROOT / "scripts" / "proof-runner"
PROOF_IDS = [f"S0-{index:02d}" for index in range(1, 13)]
KEY = "extra_attested_inputs"
LONG_SEGMENT = "docs/" + "a" * 256 + ".md"            # one segment over NAME_MAX (255 bytes)
LONG_MULTIBYTE = "docs/" + "\u00e9" * 128 + ".md"     # 131 characters but 259 bytes: NAME_MAX counts bytes
LONG_PATH = "/".join(["d" * 200] * 21) + "/input.md"  # every segment short, the whole path over PATH_MAX (4096 bytes)
# scripts/proof-runner `_clean_env`: a leg sees these from the parent, plus its spec's own env.
PASSTHROUGH_ENV = ("PATH", "HOME", "LANG")
# A checker that starts a child process the hook cannot reach, with the reason. Only S0-11: its rubric children run
# under the checker's own isolation (`unshare --net` + `setpriv` to uid 65534, and the allow-listed environment of
# `_allow_env()`, which drops PYTHONPATH), the very property S0-11 proves, so the hook cannot be passed in without
# changing what it measures. Those children run S0-11's own fixtures (`proofs/S0-11/fixtures/*.py`, attested with the
# proof); its `nsenter` probes and the unwrapped control run inherit the hook and are observed.
UNOBSERVED_CHILDREN = {
    "S0-11": "the isolated rubric children (allow-listed env, uid 65534) run proofs/S0-11/fixtures/*.py unobserved",
}

# The audit hook every leg's Python processes load (a sitecustomize on PYTHONPATH). It records each path a process
# opens, in any mode (a module's source, a spec_from_file_location load and the main script included: the legs run
# with an empty bytecode prefix, so every import opens its source), and each process it starts. It never raises: an
# exception in an audit hook would fail the audited call.
HOOK = r'''
import json, os, sys

_LOG = os.environ.get("ATTESTED_INPUTS_READ_LOG")
_OUT = None
if _LOG:
    try:
        _OUT = open(_LOG, "a", buffering=1)
    except OSError:
        _OUT = None


def _emit(kind, value):
    try:
        _OUT.write(json.dumps([kind, value]) + "\n")
    except Exception:
        pass


def _hook(event, args):
    try:
        if event == "open" and isinstance(args[0], (str, bytes, os.PathLike)):
            _emit("read", os.path.abspath(os.fsdecode(args[0])))
        elif event in ("subprocess.Popen", "os.system", "os.exec", "os.posix_spawn", "os.spawn"):
            _emit("spawn", event + " " + repr(args[:2])[:240])
    except Exception:
        pass


def _observed(name):
    """Wrap os.<name> (stat, lstat, access): record the path, then call the original, unchanged. A module attribute is
    what os.path.exists/isfile/isdir and pathlib's exists/is_file/is_dir/stat look up at call time."""
    real = getattr(os, name)

    def wrapper(path, *args, **kwargs):
        try:
            if kwargs.get("dir_fd") is None and isinstance(path, (str, bytes, os.PathLike)):
                _emit("stat", os.path.abspath(os.fsdecode(path)))
        except Exception:
            pass
        return real(path, *args, **kwargs)

    for group in (os.supports_dir_fd, os.supports_fd, os.supports_follow_symlinks, os.supports_effective_ids):
        if real in group:  # keep `os.stat in os.supports_dir_fd` true (shutil.rmtree decides its path on it)
            group.add(wrapper)
    return wrapper


if _OUT is not None:
    sys.addaudithook(_hook)
    for _name in ("stat", "lstat", "access"):
        setattr(os, _name, _observed(_name))
'''


def _load_validator():
    loader = importlib.machinery.SourceFileLoader("stage0_validate_ledger", str(VALIDATOR))
    module = importlib.util.module_from_spec(importlib.util.spec_from_loader(loader.name, loader))
    loader.exec_module(module)
    return module


def _load_registry(root):
    text = (root / "proofs" / "registry.yaml").read_text()
    return json.loads("\n".join(line for line in text.splitlines() if not line.lstrip().startswith("#")))


def _write_registry(root, registry):
    (root / "proofs" / "registry.yaml").write_text(json.dumps(registry, indent=1) + "\n")


def _declare(root, proof_id, value):
    registry = _load_registry(root)
    entry = next(proof for proof in registry["proofs"] if proof["proof_id"] == proof_id)
    entry[KEY] = value
    _write_registry(root, registry)


def _copy_contract(tmp_path):
    """A minimal root: the real registry (its declarations name files this root does not carry) and the schemas."""
    root = tmp_path / "repo"
    (root / "proofs").mkdir(parents=True)
    shutil.copy(ROOT / "proofs" / "registry.yaml", root / "proofs" / "registry.yaml")
    shutil.copytree(ROOT / "proofs" / "schemas", root / "proofs" / "schemas")
    return root


def _integrity(root):
    return subprocess.run([sys.executable, str(VALIDATOR), "integrity", "--root", str(root)],
                          capture_output=True, text=True, timeout=30)


def _findings_about_the_key(stdout):
    return [line for line in stdout.splitlines() if KEY in line]


def _run_leg(leg):
    return {
        "leg": leg,
        "cmd": ["python3", "-c", "print('ok')"],
        "started_at": "2026-09-26T00:00:00Z",
        "finished_at": "2026-09-26T00:00:01Z",
        "exit_code": 0 if leg == "positive" else 1,
        "stdout_sha256": hashlib.sha256(b"").hexdigest(),
        "stderr_sha256": hashlib.sha256(b"").hexdigest(),
    }


def _mint(root, proof_id):
    """A result for `proof_id` in `root` whose attestation the REAL validator computes over that root."""
    proof_dir = root / "proofs" / proof_id
    proof_dir.mkdir(parents=True, exist_ok=True)
    (proof_dir / "spec.json").write_text(json.dumps({"proof_id": proof_id}) + "\n")
    runs = [_run_leg("positive"), _run_leg("negative")]
    result = {
        "proof_id": proof_id,
        "classification": next(p for p in _load_registry(root)["proofs"] if p["proof_id"] == proof_id)["classification"],
        "recorded_at": "2026-09-26T00:00:02Z",
        "env_fingerprint": "sandbox:test",
        "runs": runs,
        "negative_control": {"fixture": "f", "expected_failure_reason": "r", "observed_failure_reason": "r"},
        "attestation": _load_validator().proof_attestation(root, proof_id),
        "digest": hashlib.sha256(json.dumps(runs, sort_keys=True, separators=(",", ":")).encode()).hexdigest(),
    }
    (proof_dir / "result.json").write_text(json.dumps(result, indent=2) + "\n")
    return result


# --- 1. the registry key: negative controls first ------------------------------------------------------------------

@pytest.mark.parametrize(
    ("value", "finding"),
    [
        ("upstream.lock.yaml", "must be a non-empty list of paths"),
        ([], "must be a non-empty list of paths"),
        ([7], "item 0 is not a string"),
        (["/etc/hostname"], "/etc/hostname is absolute"),
        (["docs/../upstream.lock.yaml"], "docs/../upstream.lock.yaml has a .. segment"),
        (["docs/adr/*.md"], "docs/adr/*.md has a glob character"),
        (["docs/adr/000?-x.md"], "docs/adr/000?-x.md has a glob character"),
        (["docs/[ab].md"], "docs/[ab].md has a glob character"),
        (["./upstream.lock.yaml"], "./upstream.lock.yaml is not in canonical form"),
        (["docs//a.md"], "docs//a.md is not in canonical form"),
        (["upstream.lock.yaml", "upstream.lock.yaml"], "upstream.lock.yaml is a duplicate"),
        (["proofs/S0-05/spec.json"], "proofs/S0-05/spec.json is inside proofs/S0-05/ (already attested)"),
        (["proofs/S0-05/fixtures/x.json"], "proofs/S0-05/fixtures/x.json is inside proofs/S0-05/ (already attested)"),
        (["scripts/proof-runner"], "scripts/proof-runner is in the attestation closure (already attested)"),
        (["scripts/validate-ledger"], "scripts/validate-ledger is in the attestation closure (already attested)"),
        (["proofs/registry.yaml"], "proofs/registry.yaml is in the attestation closure (already attested)"),
        ([LONG_SEGMENT], f"{LONG_SEGMENT} has a segment over 255 bytes"),
        ([LONG_MULTIBYTE], f"{LONG_MULTIBYTE} has a segment over 255 bytes"),
        (["proofs/schemas/result.schema.json"],
         "proofs/schemas/result.schema.json is in the attestation closure (already attested)"),
    ],
    ids=["string", "empty", "non-string", "absolute", "dotdot", "star", "question", "bracket", "dot-segment",
         "doubled-slash", "duplicate", "own-directory", "own-directory-nested", "closure", "closure-validator",
         "closure-registry", "long-segment", "long-segment-multibyte", "schema"],
)
def test_the_registry_refuses_a_malformed_declaration_by_name(tmp_path, value, finding):
    root = _copy_contract(tmp_path)
    _declare(root, "S0-05", value)

    completed = _integrity(root)

    assert completed.returncode == 1, completed.stdout + completed.stderr
    assert f"registry-schema: S0-05 {KEY} {finding}" in completed.stdout.splitlines(), completed.stdout
    assert completed.stderr == ""


def _symlink_to_file(root):
    (root / "docs").mkdir()
    (root / "docs" / "real.md").write_text("real\n")
    (root / "docs" / "input.md").symlink_to("real.md")


def _directory(root):
    (root / "docs" / "input.md").mkdir(parents=True)


def _through_a_symlinked_directory(root):
    (root / "elsewhere").mkdir()
    (root / "elsewhere" / "input.md").write_text("real\n")
    (root / "docs").symlink_to("elsewhere")


def _dangling_symlink(root):
    (root / "docs").mkdir()
    (root / "docs" / "input.md").symlink_to("missing.md")


@pytest.mark.parametrize("shape", [_symlink_to_file, _directory, _through_a_symlinked_directory, _dangling_symlink],
                         ids=["symlink", "directory", "symlinked-parent", "dangling-symlink"])
def test_the_registry_refuses_a_declared_path_that_is_not_a_regular_file(tmp_path, shape):
    root = _copy_contract(tmp_path)
    shape(root)
    _declare(root, "S0-05", ["docs/input.md"])

    completed = _integrity(root)

    assert completed.returncode == 1, completed.stdout + completed.stderr
    assert f"registry-schema: S0-05 {KEY} docs/input.md is not a regular file" in completed.stdout.splitlines()


def test_the_registry_accepts_a_declared_regular_file(tmp_path):
    """The positive control of the two refusal tests above: the same key and a regular file is no finding."""
    root = _copy_contract(tmp_path)
    (root / "docs").mkdir()
    (root / "docs" / "input.md").write_text("input\n")
    _declare(root, "S0-05", ["docs/input.md", "upstream.lock.yaml"])

    completed = _integrity(root)

    assert completed.returncode == 0, completed.stdout + completed.stderr
    assert _findings_about_the_key(completed.stdout) == []


def test_the_committed_declarations_pass_the_registry_check():
    """Every committed declaration is well formed and names a regular file. The rc is not asserted: it stays 1 until the
    re-mint that lands with this key (every committed result.json attests the validator and the registry)."""
    completed = _integrity(ROOT)

    assert _findings_about_the_key(completed.stdout) == [], completed.stdout
    declared = {p["proof_id"] for p in _load_registry(ROOT)["proofs"] if KEY in p}
    assert declared == {"S0-02", "S0-03", "S0-05", "S0-06", "S0-09", "S0-10", "S0-12"}


# --- 2. the attestation ----------------------------------------------------------------------------------------------

def _independent_attestation(root, proof_id):
    """The attestation derived another way (os.walk, the registry read here): the closure files present, the schemas,
    every file under the proof's directory except __pycache__ and its own two artifacts (a fixture of either name deeper
    down is kept), and each declared path."""
    expected = {}
    for rel in ("scripts/proof-runner", "scripts/validate-ledger", "proofs/registry.yaml"):
        if (root / rel).is_file():
            expected[rel] = hashlib.sha256((root / rel).read_bytes()).hexdigest()
    for name in os.listdir(root / "proofs" / "schemas"):
        if name.endswith(".json"):
            expected[f"proofs/schemas/{name}"] = hashlib.sha256((root / "proofs" / "schemas" / name).read_bytes()).hexdigest()
    for directory, subdirectories, names in os.walk(root / "proofs" / proof_id):
        subdirectories[:] = [name for name in subdirectories if name != "__pycache__"]
        for name in names:
            path = Path(directory) / name
            if path.parent == root / "proofs" / proof_id and name in ("result.json", "blocked.json"):
                continue
            if path.is_file():
                expected[path.relative_to(root).as_posix()] = hashlib.sha256(path.read_bytes()).hexdigest()
    entry = next(p for p in _load_registry(root)["proofs"] if p["proof_id"] == proof_id)
    for rel in entry.get(KEY, []):
        expected[rel] = hashlib.sha256((root / rel).read_bytes()).hexdigest()
    return expected


@pytest.mark.parametrize("proof_id", PROOF_IDS)
def test_the_attestation_is_the_closure_the_directory_and_the_declared_files(proof_id):
    """Over the real tree: a proof with no declaration gets exactly the pre-I59-A key set (the closure, the schemas, its
    directory), and a declaring proof exactly that set plus its declared paths, each under its root-relative path."""
    assert _load_validator().proof_attestation(ROOT, proof_id) == _independent_attestation(ROOT, proof_id)


def test_a_changed_declared_input_makes_only_its_proof_invalid(tmp_path):
    root = _copy_contract(tmp_path)
    (root / "docs").mkdir()
    (root / "docs" / "input.md").write_text("input\n")
    _declare(root, "S0-05", ["docs/input.md"])
    recorded = _mint(root, "S0-05")["attestation"]
    _mint(root, "S0-04")  # declares nothing: the control that must stay PRESENT
    assert recorded.get("docs/input.md") == hashlib.sha256(b"input\n").hexdigest()
    before = _integrity(root)
    assert before.returncode == 0, before.stdout
    assert {"S0-04 PRESENT", "S0-05 PRESENT"} <= set(before.stdout.splitlines())

    (root / "docs" / "input.md").write_text("inpuT\n")  # one byte
    after = _integrity(root).stdout.splitlines()

    assert "S0-05 INVALID" in after and "S0-04 PRESENT" in after, after
    assert "attestation-mismatch: S0-05 docs/input.md" in after, after


def test_a_deleted_declared_input_makes_its_proof_invalid(tmp_path):
    root = _copy_contract(tmp_path)
    (root / "docs").mkdir()
    (root / "docs" / "input.md").write_text("input\n")
    _declare(root, "S0-05", ["docs/input.md"])
    _mint(root, "S0-05")
    assert "S0-05 PRESENT" in _integrity(root).stdout.splitlines()

    (root / "docs" / "input.md").unlink()
    after = _integrity(root).stdout.splitlines()

    assert "S0-05 INVALID" in after, after
    assert "attestation-mismatch: S0-05 docs/input.md" in after, after
    assert f"registry-schema: S0-05 {KEY} docs/input.md is not a regular file" in after, after


def test_a_result_minted_while_its_declared_input_was_absent_is_invalid(tmp_path):
    """The attestation skips an absent file (as it skips an absent closure file), so a result minted without its
    declared input records no key for it and the recorded-vs-current comparison agrees; the verdict binding refuses it."""
    root = _copy_contract(tmp_path)
    _declare(root, "S0-05", ["docs/input.md"])
    assert "docs/input.md" not in _mint(root, "S0-05")["attestation"]

    after = _integrity(root).stdout.splitlines()

    assert "S0-05 INVALID" in after, after
    assert f"registry-schema: S0-05 {KEY} docs/input.md is not a regular file" in after, after
    assert not any(line.startswith("attestation-mismatch: S0-05") for line in after), after


def test_only_the_proofs_own_artifacts_are_left_out_of_its_attestation(tmp_path):
    """A file named result.json or blocked.json deeper in a proof's directory is an input and is hashed; only the
    proof's own two artifacts, directly in its directory, are left out. The live case: S0-08's marker-gate leg grades
    proofs/S0-08/fixtures/malformed-marker/blocked.json, which the old skip-anywhere rule left unattested (I59-A A1)."""
    root = _copy_contract(tmp_path)
    proof_dir = root / "proofs" / "S0-05"
    (proof_dir / "fixtures" / "marker").mkdir(parents=True)
    for rel in ("result.json", "blocked.json", "fixtures/result.json", "fixtures/marker/blocked.json"):
        (proof_dir / rel).write_text(json.dumps({"file": rel}) + "\n")

    attestation = _load_validator().proof_attestation(root, "S0-05")

    assert attestation.get("proofs/S0-05/fixtures/result.json") == \
        hashlib.sha256((proof_dir / "fixtures" / "result.json").read_bytes()).hexdigest()
    assert attestation.get("proofs/S0-05/fixtures/marker/blocked.json") == \
        hashlib.sha256((proof_dir / "fixtures" / "marker" / "blocked.json").read_bytes()).hexdigest()
    assert "proofs/S0-05/result.json" not in attestation and "proofs/S0-05/blocked.json" not in attestation
    live = _load_validator().proof_attestation(ROOT, "S0-08")
    assert "proofs/S0-08/fixtures/malformed-marker/blocked.json" in live, sorted(live)


def test_a_changed_fixture_named_like_an_artifact_makes_its_proof_invalid(tmp_path):
    """The binding end to end: a result minted with a fixture named blocked.json, then one byte of that fixture
    changed, is INVALID for exactly that file (the old skip-anywhere rule left it PRESENT). S0-04 declares nothing, so
    the minimal root needs no declared input."""
    root = _copy_contract(tmp_path)
    fixture = root / "proofs" / "S0-04" / "fixtures" / "marker" / "blocked.json"
    fixture.parent.mkdir(parents=True)
    fixture.write_text('{"marker": "malformed"}\n')
    _mint(root, "S0-04")
    assert "S0-04 PRESENT" in _integrity(root).stdout.splitlines()

    fixture.write_text('{"marker": "malformeD"}\n')  # one byte
    after = _integrity(root).stdout.splitlines()

    assert "S0-04 INVALID" in after, after
    assert "attestation-mismatch: S0-04 proofs/S0-04/fixtures/marker/blocked.json" in after, after


@pytest.mark.parametrize("name", ["LICENSE-DECISION.md", "THIRD-PARTY-NOTICES.md"])
def test_removing_a_file_s0_12_tests_for_invalidates_its_minted_result(tmp_path, name):
    """VERIFY-I59-A F-1: S0-12's checker requires LICENSE-DECISION.md and THIRD-PARTY-NOTICES.md to EXIST
    (proofs/S0-12/check_pin_diff.py:23-24) and never opens them, so its verdict depends on them and they are declared.
    Minted by the canonical runner in a minimal root, S0-12 is PRESENT and attests both; with either removed its checker
    fails, so the minted result must not stay PRESENT."""
    root = tmp_path / "repo"
    for rel in ("scripts/proof-runner", "scripts/validate-ledger", "proofs/registry.yaml", "SBOM.yaml",
                "upstream.lock.yaml", "LICENSE-DECISION.md", "THIRD-PARTY-NOTICES.md"):
        (root / rel).parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(ROOT / rel, root / rel)
    shutil.copytree(ROOT / "proofs" / "schemas", root / "proofs" / "schemas")
    shutil.copytree(ROOT / "proofs" / "S0-12", root / "proofs" / "S0-12",
                    ignore=shutil.ignore_patterns("__pycache__", "result.json"))
    minted = subprocess.run([sys.executable, str(root / "scripts" / "proof-runner"), "run", "--proof", "S0-12",
                             "--venue", "sandbox", "--root", str(root)], capture_output=True, text=True, timeout=120)
    assert minted.returncode == 0, minted.stdout + minted.stderr
    assert name in json.loads((root / "proofs" / "S0-12" / "result.json").read_text())["attestation"]
    assert "S0-12 PRESENT" in _integrity(root).stdout.splitlines()

    (root / name).unlink()
    leg = subprocess.run([sys.executable, "proofs/S0-12/check_pin_diff.py", "."], cwd=root, capture_output=True,
                         text=True, timeout=60)
    after = _integrity(root).stdout.splitlines()

    assert leg.returncode == 1 and f"sbom-missing-file: {name} does not exist" in leg.stdout, leg.stdout
    assert "S0-12 INVALID" in after, after
    assert f"attestation-mismatch: S0-12 {name}" in after, after


def test_a_declared_path_the_filesystem_refuses_never_crashes_the_validator_or_the_runner(tmp_path):
    """VERIFY-I59-A FU-2: a declared path the filesystem refuses must not crash. A segment over 255 bytes is refused by
    name (the table above); a path over PATH_MAX made of short segments still reaches the filesystem, where
    _is_regular_file reads its OSError (ENAMETOOLONG) as not a regular file. Before the fix the OSError crashed the
    validator and, through the runner, deleted a minted result."""
    try:
        assert _load_validator()._is_regular_file(tmp_path, LONG_PATH) is False
    except OSError as error:
        pytest.fail(f"_is_regular_file raised {error!r}")
    root = _copy_contract(tmp_path)
    spec = {"proof_id": "S0-04", "legs": [
        {"leg": "negative", "cmd": [sys.executable, "-c", "import sys; print('denied'); raise SystemExit(1)"],
         "cwd": ".", "timeout_s": 10, "expect": {"exit_code": 1, "failure_reason": "denied"}},
        {"leg": "positive", "cmd": [sys.executable, "-c", "print('ok')"], "cwd": ".", "timeout_s": 10,
         "expect": {"exit_code": 0}},
    ]}
    (root / "proofs" / "S0-04").mkdir()
    (root / "proofs" / "S0-04" / "spec.json").write_text(json.dumps(spec) + "\n")
    runner = [sys.executable, str(RUNNER), "run", "--proof", "S0-04", "--venue", "sandbox", "--root", str(root)]
    assert subprocess.run(runner, capture_output=True, text=True, timeout=60).returncode == 0
    _declare(root, "S0-04", [LONG_PATH])

    again = subprocess.run(runner, capture_output=True, text=True, timeout=60)
    completed = _integrity(root)

    assert again.returncode == 0 and (root / "proofs" / "S0-04" / "result.json").is_file(), again.stderr[-300:]
    assert completed.stderr == "", completed.stderr[-300:]
    assert "S0-04 INVALID" in completed.stdout.splitlines()
    assert f"registry-schema: S0-04 {KEY} {LONG_PATH} is not a regular file" in completed.stdout.splitlines()


def test_a_result_minted_while_its_declared_input_was_a_symlink_is_invalid(tmp_path):
    """VERIFY-I59-A FU-3 (N5): a declared symlink is never hashed, so a result minted over one records no key for it and
    the recorded-vs-current comparison agrees; the verdict binding (a regular file, not merely an existing path) refuses
    it. The registry-level finding alone would leave the state PRESENT."""
    root = _copy_contract(tmp_path)
    (root / "docs").mkdir()
    (root / "docs" / "real.md").write_text("real\n")
    (root / "docs" / "input.md").symlink_to("real.md")
    _declare(root, "S0-05", ["docs/input.md"])
    assert "docs/input.md" not in _mint(root, "S0-05")["attestation"]

    after = _integrity(root).stdout.splitlines()

    assert "S0-05 INVALID" in after, after
    assert f"registry-schema: S0-05 {KEY} docs/input.md is not a regular file" in after, after


def test_a_declared_symlink_is_never_hashed(tmp_path):
    """The attestation reads no file through a symlink: a declared link to a file outside the root is not hashed (the
    registry check refuses it by name, test above), so the validator never reads outside the tree it attests."""
    root = _copy_contract(tmp_path)
    (tmp_path / "outside.txt").write_text("outside the root\n")
    (root / "docs").mkdir()
    (root / "docs" / "input.md").symlink_to(tmp_path / "outside.txt")
    _declare(root, "S0-05", ["docs/input.md"])

    assert "docs/input.md" not in _load_validator().proof_attestation(root, "S0-05")


def test_the_canonical_runner_records_the_declared_input(tmp_path):
    """The runner's call site (scripts/proof-runner `validator.proof_attestation`): a real mint records the declared
    file, the validator accepts it, and a one-byte change to that file turns the minted proof INVALID."""
    root = _copy_contract(tmp_path)
    (root / "docs").mkdir()
    (root / "docs" / "input.md").write_text("input\n")
    _declare(root, "S0-05", ["docs/input.md"])
    spec = {"proof_id": "S0-05", "legs": [
        {"leg": "negative", "cmd": [sys.executable, "-c", "import sys; print('denied'); raise SystemExit(1)"],
         "cwd": ".", "timeout_s": 10, "expect": {"exit_code": 1, "failure_reason": "denied"}},
        {"leg": "positive", "cmd": [sys.executable, "-c", "print('ok')"], "cwd": ".", "timeout_s": 10,
         "expect": {"exit_code": 0}},
    ]}
    (root / "proofs" / "S0-05").mkdir()
    (root / "proofs" / "S0-05" / "spec.json").write_text(json.dumps(spec) + "\n")

    minted = subprocess.run([sys.executable, str(RUNNER), "run", "--proof", "S0-05", "--venue", "sandbox",
                             "--root", str(root)], capture_output=True, text=True, timeout=60)

    assert minted.returncode == 0, minted.stdout + minted.stderr
    attestation = json.loads((root / "proofs" / "S0-05" / "result.json").read_text())["attestation"]
    assert attestation.get("docs/input.md") == hashlib.sha256(b"input\n").hexdigest()
    assert "S0-05 PRESENT" in _integrity(root).stdout.splitlines()
    (root / "docs" / "input.md").write_text("inpuT\n")
    assert "attestation-mismatch: S0-05 docs/input.md" in _integrity(root).stdout.splitlines()


# --- 3. the drift guard ----------------------------------------------------------------------------------------------

def _observe(root, proof_id, scratch):
    """Run every leg of the proof's spec as scripts/proof-runner runs it (the literal command, the leg's cwd, the
    runner's clean environment and the leg's env) with the audit hook loaded and a fresh, empty bytecode prefix per leg,
    so every import opens its source, never a .pyc left in the tree. Returns (exits, reads, stats, spawns): each leg's
    (index, exit, expected, output tail); the root-relative files any hooked process opened; the ones it tested for
    existence or type; each process start."""
    hook_dir = scratch / "hook"
    hook_dir.mkdir(parents=True, exist_ok=True)
    (hook_dir / "sitecustomize.py").write_text(HOOK)
    real_root = os.path.realpath(root)
    spec = json.loads((root / "proofs" / proof_id / "spec.json").read_text())
    exits, reads, stats, spawns = [], set(), set(), []
    for index, leg in enumerate(spec["legs"]):
        log = scratch / f"leg{index}.jsonl"
        environment = {name: os.environ[name] for name in PASSTHROUGH_ENV if name in os.environ}
        environment.update(leg.get("env") or {})
        environment["PYTHONPATH"] = os.pathsep.join(filter(None, [str(hook_dir), environment.get("PYTHONPATH")]))
        environment["ATTESTED_INPUTS_READ_LOG"] = str(log)
        environment["PYTHONPYCACHEPREFIX"] = str(scratch / f"bytecode{index}")
        completed = subprocess.run(leg["cmd"], cwd=root / leg["cwd"], env=environment, capture_output=True,
                                   timeout=leg["timeout_s"])
        tail = (completed.stdout + completed.stderr).decode(errors="replace")[-300:]
        exits.append((index, completed.returncode, leg["expect"]["exit_code"], tail))
        for line in log.read_text().splitlines() if log.exists() else []:
            kind, value = json.loads(line)
            if kind == "spawn":
                spawns.append(value)
                continue
            real = os.path.realpath(value)
            if real.startswith(real_root + os.sep) and os.path.isfile(real):
                (stats if kind == "stat" else reads).add(Path(os.path.relpath(real, real_root)).as_posix())
    return exits, reads, stats, spawns


def _verdict(root, proof_id, observation):
    """The guard: every leg graded (its spec's exit code), the hook saw each leg's own script, every repo file read or
    tested for existence outside the proof's directory is in its attestation (the closure or a declaration), every such
    file inside it is too, and no child process escaped unnamed. The proof's own two artifacts are exempt: a re-mint may
    read the result it replaces (S0-11's forbidden-op sweep reads every non-.md file of its directory), and an artifact
    cannot attest itself. A stat of a __pycache__ file is ignored: bytecode caches are never attested (the same sweep
    stats its own cache, then skips it). An AssertionError names what is wrong."""
    exits, reads, stats, spawns = observation
    wrong = [(index, got, want, tail) for index, got, want, tail in exits if got != want]
    assert not wrong, f"{proof_id}: leg(s) did not grade (index, exit, expected, output tail): {wrong}"
    spec = json.loads((root / "proofs" / proof_id / "spec.json").read_text())
    scripts = {Path(os.path.relpath(os.path.realpath(root / leg["cwd"] / leg["cmd"][1]), os.path.realpath(root))).as_posix()
               for leg in spec["legs"] if len(leg["cmd"]) > 1 and leg["cmd"][1].endswith(".py")}
    assert scripts <= reads, f"{proof_id}: the hook did not observe the legs' own scripts {sorted(scripts - reads)}"
    own = f"proofs/{proof_id}/"
    covered = set(_load_validator().proof_attestation(root, proof_id)) | {own + "result.json", own + "blocked.json"}
    uncovered = reads - covered
    tested = {path for path in stats - covered if "__pycache__" not in path.split("/")}
    outside = sorted(path for path in uncovered if not path.startswith(own))
    assert not outside, (f"{proof_id}: its checker reads repo files its attestation does not cover; declare them in "
                         f"proofs/registry.yaml {KEY}: {outside}")
    outside_tested = sorted(path for path in tested if not path.startswith(own))
    assert not outside_tested, (f"{proof_id}: its checker tests the existence or type of repo files its attestation does "
                                f"not cover; declare them in proofs/registry.yaml {KEY}: {outside_tested}")
    inside = sorted(path for path in uncovered | tested if path.startswith(own))
    assert not inside, f"{proof_id}: its checker reads files inside its directory that its attestation does not cover: {inside}"
    if proof_id not in UNOBSERVED_CHILDREN:
        assert not spawns, (f"{proof_id}: its checker starts child processes the hook may not reach; observe them or "
                            f"name the proof in UNOBSERVED_CHILDREN: {spawns[:3]}")


def _absent_outside_paths(spec):
    """The (leg, argument) pairs naming an absolute path this venue lacks (S0-07's Fubuki checkout on CI)."""
    return [(index, argument) for index, leg in enumerate(spec["legs"]) for argument in leg["cmd"]
            if argument.startswith("/") and not os.path.exists(argument)]


def _deferred_legs(observation):
    """The legs that exited 2, scripts/proof-runner's capability-unavailable signal, where the spec expects otherwise."""
    return [(index, tail) for index, got, want, tail in observation[0] if got == 2 and want != 2]


@pytest.mark.parametrize("proof_id", PROOF_IDS)
def test_every_repo_file_a_checker_reads_is_attested(tmp_path, proof_id):
    absent = _absent_outside_paths(json.loads((ROOT / "proofs" / proof_id / "spec.json").read_text()))
    if absent:
        pytest.skip(f"{proof_id}: leg(s) grade paths outside the repo that this venue lacks, so its reads are not "
                    f"observed here: {absent}")
    observation = _observe(ROOT, proof_id, tmp_path)
    deferred = _deferred_legs(observation)
    if deferred:
        pytest.skip(f"{proof_id}: leg(s) deferred with exit 2 (capability unavailable on this venue), so its reads are "
                    f"not observed here: {deferred}")
    _verdict(ROOT, proof_id, observation)


PLANTED = {
    # a spec_from_file_location on a path joined at run time
    "spec_from_file_location": (
        "proofs/S0-01/planted_a.py",
        "import importlib.util as _iu, os as _os\n"
        "_spec = _iu.spec_from_file_location('planted_a', _os.path.join(_os.path.dirname(_os.path.abspath(__file__)),"
        " '..', 'S0-01', 'planted_a.py'))\n"
        "_spec.loader.exec_module(_iu.module_from_spec(_spec))\n",
    ),
    # a read_text on a root-relative Path expression
    "read_text": (
        "docs/planted_b.md",
        "from pathlib import Path as _Path\n"
        "_Path(__file__).resolve().parents[2].joinpath('docs', 'planted_b.md').read_text()\n",
    ),
    # an import through a sys.path entry
    "sys_path_import": (
        "lib/planted_c.py",
        "import sys as _sys\n"
        "from pathlib import Path as _Path\n"
        "_sys.path.insert(0, str(_Path(__file__).resolve().parents[2] / 'lib'))\n"
        "import planted_c  # noqa: E402,F401\n",
    ),
}


PLANTED_STATS = {
    # Path.exists on a Path expression built at run time (S0-12's shape, VERIFY-I59-A F-1)
    "pathlib_exists": (
        "docs/stat_j.md",
        "from pathlib import Path as _Path\n"
        "_Path(__file__).resolve().parents[2].joinpath('docs', 'stat_j.md').exists()\n",
    ),
    # os.path.isfile on an os.path.join
    "os_path_isfile": (
        "docs/stat_k.md",
        "import os as _os\n"
        "_os.path.isfile(_os.path.join(_os.path.dirname(_os.path.abspath(__file__)), '..', '..', 'docs', 'stat_k.md'))\n",
    ),
    # os.stat on an os.path.join
    "os_stat": (
        "lib/stat_l.txt",
        "import os as _os\n"
        "_os.stat(_os.path.join(_os.path.dirname(_os.path.abspath(__file__)), '..', '..', 'lib', 'stat_l.txt'))\n",
    ),
    # os.access (F_OK), wrapped on its own: it never calls os.stat (VERIFY-I59-A FU-8, V-S4)
    "os_access": (
        "docs/stat_m.md",
        "import os as _os\n"
        "_os.access(_os.path.join(_os.path.dirname(_os.path.abspath(__file__)), '..', '..', 'docs', 'stat_m.md'), _os.F_OK)\n",
    ),
    # os.path.lexists, which calls os.lstat, not os.stat (VERIFY-I59-A FU-8, V-S4)
    "os_path_lexists": (
        "docs/stat_n.md",
        "import os as _os\n"
        "_os.path.lexists(_os.path.join(_os.path.dirname(_os.path.abspath(__file__)), '..', '..', 'docs', 'stat_n.md'))\n",
    ),
}


def _scratch_s0_09(tmp_path, planted_code=None, declare=()):
    """A scratch copy of S0-09 (its directory, the files it declares, the registry) whose checker runs `planted_code`
    at import time, before it grades; every PLANTED target exists in it. `declare` adds paths to S0-09's declaration."""
    root = tmp_path / "scratch"
    shutil.copytree(ROOT / "proofs" / "S0-09", root / "proofs" / "S0-09", ignore=shutil.ignore_patterns("__pycache__"))
    (root / "proofs" / "S0-09" / "result.json").unlink(missing_ok=True)
    shutil.copy(ROOT / "proofs" / "registry.yaml", root / "proofs" / "registry.yaml")
    for rel in next(p for p in _load_registry(ROOT)["proofs"] if p["proof_id"] == "S0-09").get(KEY, []):
        (root / rel).parent.mkdir(parents=True, exist_ok=True)
        shutil.copy(ROOT / rel, root / rel)
    for rel, _code in [*PLANTED.values(), *PLANTED_STATS.values()]:
        (root / rel).parent.mkdir(parents=True, exist_ok=True)
        (root / rel).write_text("VALUE = 1\n")
        if rel.endswith(".py"):  # a valid .pyc beside it, as the live tree has: only the empty prefix makes the source read
            py_compile.compile(str(root / rel), doraise=True)
    if planted_code is not None:
        checker = root / "proofs" / "S0-09" / "check_conformance.py"
        text = checker.read_text()
        anchor = 'if __name__ == "__main__":'
        assert text.count(anchor) == 1
        checker.write_text(text.replace(anchor, planted_code + "\n\n" + anchor))
    if declare:
        registry = _load_registry(root)
        entry = next(p for p in registry["proofs"] if p["proof_id"] == "S0-09")
        entry[KEY] = sorted(set(entry.get(KEY, [])) | set(declare))
        _write_registry(root, registry)
    return root


def test_the_guard_passes_the_unplanted_scratch_copy(tmp_path):
    """The baseline of the planted controls below: the copy itself is clean."""
    root = _scratch_s0_09(tmp_path)
    _verdict(root, "S0-09", _observe(root, "S0-09", tmp_path / "observe"))


@pytest.mark.parametrize("shape", sorted(PLANTED))
def test_the_guard_reds_on_an_undeclared_read(tmp_path, shape):
    """NEGATIVE CONTROL: one undeclared read of each shape, its path built at run time."""
    target, code = PLANTED[shape]
    root = _scratch_s0_09(tmp_path, code)

    with pytest.raises(AssertionError) as caught:
        _verdict(root, "S0-09", _observe(root, "S0-09", tmp_path / "observe"))

    assert f"{KEY}: {[target]}" in str(caught.value), str(caught.value)


@pytest.mark.parametrize("shape", sorted(PLANTED))
def test_the_guard_passes_the_same_read_once_declared(tmp_path, shape):
    """The negative control's pair: the same planted read, declared, is covered by the attestation, so the only reason
    the control above reds is the missing declaration."""
    target, code = PLANTED[shape]
    root = _scratch_s0_09(tmp_path, code, declare=[target])
    _verdict(root, "S0-09", _observe(root, "S0-09", tmp_path / "observe"))


@pytest.mark.parametrize("shape", sorted(PLANTED_STATS))
def test_the_guard_reds_on_an_undeclared_existence_test(tmp_path, shape):
    """NEGATIVE CONTROL of the second instrument: one undeclared existence or type test of each shape, its path built at
    run time, on a file the checker never opens (VERIFY-I59-A F-1's class)."""
    target, code = PLANTED_STATS[shape]
    root = _scratch_s0_09(tmp_path, code)

    with pytest.raises(AssertionError) as caught:
        _verdict(root, "S0-09", _observe(root, "S0-09", tmp_path / "observe"))

    assert "tests the existence or type of repo files" in str(caught.value), str(caught.value)
    assert f"{KEY}: {[target]}" in str(caught.value), str(caught.value)


@pytest.mark.parametrize("shape", sorted(PLANTED_STATS))
def test_the_guard_passes_the_same_existence_test_once_declared(tmp_path, shape):
    """The pair: the same planted existence test, declared, is covered, so the only reason the control above reds is
    the missing declaration."""
    target, code = PLANTED_STATS[shape]
    root = _scratch_s0_09(tmp_path, code, declare=[target])
    _verdict(root, "S0-09", _observe(root, "S0-09", tmp_path / "observe"))


def test_the_guard_ignores_a_stat_of_a_bytecode_cache(tmp_path):
    """A POSITIVE control: a checker that stats a __pycache__ file inside its directory (S0-11's sweep stats every file,
    then skips the caches) depends on no attested input, and the guard stays green."""
    code = ("from pathlib import Path as _Path\n"
            "_Path(__file__).resolve().parent.joinpath('__pycache__', 'cached.cpython-311.pyc').is_file()\n")
    root = _scratch_s0_09(tmp_path, code)
    (root / "proofs" / "S0-09" / "__pycache__").mkdir()
    (root / "proofs" / "S0-09" / "__pycache__" / "cached.cpython-311.pyc").write_bytes(b"not bytecode\n")
    _verdict(root, "S0-09", _observe(root, "S0-09", tmp_path / "observe"))


def test_the_guard_reds_on_an_unattested_read_inside_the_proof_directory(tmp_path):
    """The inside rule: a file inside the proof's directory that its attestation leaves out is not covered. Since the
    fixture-named gap closed, what the attestation leaves out inside a directory is __pycache__ (and the proof's own two
    artifacts, which the guard exempts), so the planted read is a data file under a __pycache__ directory."""
    code = ("from pathlib import Path as _Path\n"
            "_Path(__file__).resolve().parent.joinpath('fixtures', '__pycache__', 'planted.json').read_text()\n")
    root = _scratch_s0_09(tmp_path, code)
    (root / "proofs" / "S0-09" / "fixtures" / "__pycache__").mkdir(parents=True)
    (root / "proofs" / "S0-09" / "fixtures" / "__pycache__" / "planted.json").write_text("{}\n")

    with pytest.raises(AssertionError) as caught:
        _verdict(root, "S0-09", _observe(root, "S0-09", tmp_path / "observe"))

    assert "reads files inside its directory that its attestation does not cover: " \
           "['proofs/S0-09/fixtures/__pycache__/planted.json']" in str(caught.value), str(caught.value)


def test_the_guard_reds_on_a_leg_that_did_not_grade(tmp_path):
    """A checker that dies before it reads anything must not read as clean."""
    root = _scratch_s0_09(tmp_path, "raise SystemExit(3)\n")

    with pytest.raises(AssertionError) as caught:
        _verdict(root, "S0-09", _observe(root, "S0-09", tmp_path / "observe"))

    assert "S0-09: leg(s) did not grade" in str(caught.value)
    assert "(0, 3, 0, " in str(caught.value) and "(1, 3, 1, " in str(caught.value), str(caught.value)


def test_the_guard_reds_on_an_unnamed_child_process(tmp_path):
    """A checker that starts a child process is named in UNOBSERVED_CHILDREN or the guard reds."""
    root = _scratch_s0_09(tmp_path, "import subprocess as _sp, sys as _sys\n"
                                    "_sp.run([_sys.executable, '-c', 'pass'], check=True)\n")

    with pytest.raises(AssertionError) as caught:
        _verdict(root, "S0-09", _observe(root, "S0-09", tmp_path / "observe"))

    assert "S0-09: its checker starts child processes" in str(caught.value)


def test_the_guard_reds_when_the_hook_saw_nothing():
    """A hook that never loaded (an environment that dropped it) observes no read at all, so every coverage check would
    pass over an empty set: the guard's own-script check refuses that observation."""
    with pytest.raises(AssertionError) as caught:
        _verdict(ROOT, "S0-09", ([(0, 0, 0, ""), (1, 1, 1, "")], set(), set(), []))

    assert "S0-09: the hook did not observe the legs' own scripts ['proofs/S0-09/check_conformance.py']" \
        in str(caught.value), str(caught.value)


def test_the_skips_name_only_what_cannot_run_on_this_venue(tmp_path):
    """A skip is not a pass: only an absent absolute argument or a deferring leg skips, never a failing one."""
    present = tmp_path / "present"
    present.mkdir()
    spec = {"legs": [{"cmd": ["python3", "proofs/S0-07/check.py", str(present)]},
                     {"cmd": ["python3", "relative/missing.py", str(tmp_path / "absent")]}]}
    assert _absent_outside_paths(spec) == [(1, str(tmp_path / "absent"))]
    assert _deferred_legs(([(0, 2, 0, "deferred"), (1, 1, 0, "failed"), (2, 2, 2, "expected two")], set(), set(), [])) \
        == [(0, "deferred")]
