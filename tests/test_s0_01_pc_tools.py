"""The S0-01 PC capture tools as a COMPONENT: one leg-file list, and every tool fail-loud.

Why this file exists (SWEEP-prod row #1, the largest open S0-01 defect): the checker's private
`_LEG_REQUIRED_FILES` and what the PC capture pipeline actually writes had drifted apart — the real corpus
leg run-1 carries 8 names the F21 allowlist REJECTS and lacks 2 it REQUIRES — and no test had ever run a
checker rule over a real collected leg. The PC tools were never verified as a component at all.

What is pinned here:
  * `pins.PINNED_LEG_FILES` / `PINNED_LEG_DIRS` is the ONE list. Three directions are checked, so drift on
    either side is loud: the real corpus is a SUBSET of the mapping (a), every "required" name is really
    present in every corpus positive leg (b), and the producers' own write set is a subset of the mapping
    with no orphan entries (c). The rejected alternative was extending the checker's private set — which is
    how the two lists drifted in the first place.
  * `build_capture_record.py` takes that required list instead of its twelve default-on-absent gates (#27/#28).
  * `pc_launch.py`'s six fail-loud fixes (#12, #25, #31, #32, #48, #52), each through the extracted helper
    with the primitive monkeypatched — the full paths are PC-only and are NOT run here.
  * `pc_negative.py` propagates the probe's exit code (#33), through a real subprocess and a stub probe.
  * `collect_leg.sh`'s `--exclude` list and the mapping agree, in both directions.

The real-leg corpus is a DECLARED input (VERIFY-CK10 F-R10-25): with `S0_01_REAL_LEG_DIR` set the corpus
tests FAIL when it is absent or incomplete, never skip; CI leaves it unset and skips by declaration.
"""
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "proofs" / "S0-01"))
sys.path.insert(0, str(ROOT / "proofs" / "S0-01" / "tools" / "pc"))
import pins  # noqa: E402 — the ONE list under test; never re-typed as literals here
import pc_launch  # noqa: E402 — module import has no side effects (pins is read, nothing is opened)
import pc_negative  # noqa: E402 — main() is guarded by __main__, so importing runs nothing

_REAL_LEG_DIR = Path(os.environ["S0_01_REAL_LEG_DIR"]) if os.environ.get("S0_01_REAL_LEG_DIR") else None
_POSITIVE_LEGS = ("run-1", "cancel", "shutdown", "two-users")
_STATUSES = {"required", "optional", "excluded_on_collect"}   # three, not four: VERIFY-P5a F10 retired `transient`
_COLLECTED = {"required", "optional"}   # what a collected leg may carry: the consumer's entry allowlist
BUILD_CAPTURE = ROOT / "proofs" / "S0-01" / "tools" / "build_capture_record.py"
COLLECT_LEG = ROOT / "proofs" / "S0-01" / "tools" / "pc" / "collect_leg.sh"
RUN_LEG = ROOT / "proofs" / "S0-01" / "tools" / "pc" / "run_leg.sh"


def _corpus():
    """The declared corpus, or a skip. Absent-when-declared is a FAILURE, raised by the caller."""
    if _REAL_LEG_DIR is None:
        pytest.skip("S0_01_REAL_LEG_DIR unset (real-leg corpus not declared for this venue)")
    if not _REAL_LEG_DIR.is_dir():
        pytest.fail(f"declared corpus absent: {_REAL_LEG_DIR} (restore: bash scripts/realleg_sync.sh pull)")
    return _REAL_LEG_DIR


def _corpus_version():
    """The whole corpus's contract version: the OLDEST any of its legs claims, so a mixed corpus is graded by
    the set every leg can satisfy.

    The per-leg detector is `pins.corpus_version` — the ONE detector (VERIFY-P5a F2 / item 13). This file used
    to carry its own, and `build_capture_record.py` carried none at all, which is exactly how the tool came to
    reject every leg the pipeline has ever produced while this file stayed green. The old mirror also folded a
    `tee-status.json` presence check into the version answer: a leg with a v2.4 header but no tee-status.json
    was silently downgraded to v2.2 and then passed. It is not folded in here — the header IS the version, and
    the missing file is a required-name failure, which is a truer answer and a louder one."""
    if _REAL_LEG_DIR is None:
        return "unknown"
    versions = []
    for leg in _POSITIVE_LEGS:
        ld = _REAL_LEG_DIR / leg
        if not ld.is_dir():
            return "v2.2"
        versions.append(pins.corpus_version(ld))
    return min(versions, key=lambda v: tuple(int(x) for x in v[1:].split(".")))


# --------------------------------------------------------------------------------------------------
# (c) the producers' write set
# --------------------------------------------------------------------------------------------------
# Every producer that writes into a leg framedir, and which leg shape it writes. The parse below reads the
# scripts themselves: a producer that starts writing a new name fails the subset test until the ONE list
# learns it, and a mapping entry no producer writes fails the orphan test.
_PRODUCERS = {
    "proofs/S0-01/tools/pc/pc_launch.py": "positive",
    "proofs/S0-01/tools/pc/pc_post.sh": "positive",
    "proofs/S0-01/tools/pc/pc_manifest.sh": "positive",
    "proofs/S0-01/tools/pc/pc_mention.sh": "positive",
    "proofs/S0-01/tools/frame_tee.py": "positive",
    "proofs/S0-01/tools/build_capture_record.py": "positive",
    "proofs/S0-01/tools/acp_probe.py": "negative",
}
# The idioms the producers use to name a framedir entry. VERIFY-P5a F3/F15: the first version of this set
# anchored on `os.path.join(FD|framedir, ...)` and a bare `$FD/`, and was blind to four forms — including the
# lowercase `fd` that the six helpers extracted from pc_launch.py's main() all use, so the refactor SHRANK the
# gate from 18 recognised names to 16 and a planted `leak-report-v1.json` survived. Every form below has a
# live site in the producers today, and the per-producer coverage floor at _PRODUCER_NAME_FLOOR fails loudly
# if a future refactor hides writes from this parse again.
_PY_JOIN = re.compile(r"""os\.path\.join\(\s*(?:FD|fd|framedir)\s*,\s*['"]([^'"\n]+)['"]""")
_PY_PATH = re.compile(r"""\bPath\(\s*(?:FD|fd|framedir)\s*,\s*['"]([^'"\n]+)['"]""")
_PY_DIV = re.compile(r"""\bd\s*/\s*['"]([^'"\n]+)['"]""")
_PY_FSTR = re.compile(r"""\{fd\}/([A-Za-z0-9._${}-]+)""")
_SH_FD = re.compile(r"""["']?\$\{?FD\}?["']?/([A-Za-z0-9._${}-]+)""")
_SH_OUT_ASSIGN = re.compile(r"""^OUT=\$\{?FD\}?/(\S+)$""", re.M)
_SH_OUT_USE = re.compile(r"""\$\{?OUT\}?((?:\.[A-Za-z0-9]+)*)""")
_PLACEHOLDERS = (("$PHASE", ("pre", "post")), ("{mode}", ("after", "teardown")))


def _expand(name):
    out = [name]
    for placeholder, values in _PLACEHOLDERS:
        out = [n.replace(placeholder, v) if placeholder in n else n for n in out for v in values]
    return sorted(set(out))


def _framedir_names(rel, root=None):
    """Root entries a producer writes into (or reads from) a leg framedir, from the script's own text.

    Anchored on the framedir variable in every form the producers use — `os.path.join(FD|fd|framedir, "x")`,
    `Path(FD|fd|framedir, "x")`, `d / "x"`, `f"{fd}/x"`, `$FD/x` quoted or bare (`"$FD"/x`, `"${FD}"/x`), and
    pc_manifest.sh's `OUT=$FD/...` plus its `$OUT.gz` suffixes. Only
    the ROOT entry is taken (`$FD/mentions/$TAG.receipt.json` is the directory `mentions`), and any token
    that still carries an unresolved placeholder fails LOUD rather than being dropped: a name this parser
    cannot resolve is a blind spot in the gate, not a name to skip.

    Dot-prefixed names are skipped: they are atomic-write scratch, not leg entries (see pins.PINNED_LEG_FILES)."""
    text = ((root or ROOT) / rel).read_text()
    raw = set()
    for rx in (_PY_JOIN, _PY_PATH, _PY_DIV, _PY_FSTR, _SH_FD):
        raw |= set(rx.findall(text))
    assign = _SH_OUT_ASSIGN.search(text)
    if assign:
        raw |= {assign.group(1) + suffix for suffix in set(_SH_OUT_USE.findall(text))}
    names = set()
    for token in raw:
        entry = token.split("/", 1)[0]
        if entry.startswith("."):
            continue
        for expanded in _expand(entry):
            assert "$" not in expanded and "{" not in expanded, \
                f"{rel}: unresolved placeholder in a framedir name: {expanded!r}"
            names.add(expanded)
    return names


def test_the_status_vocabulary_is_closed_and_the_dirs_are_named():
    assert set(pins.PINNED_LEG_FILES.values()) <= _STATUSES, sorted(set(pins.PINNED_LEG_FILES.values()))
    assert set(pins.PINNED_LEG_DIRS.values()) <= _STATUSES
    assert set(pins.PINNED_LEG_DIRS) == {"mentions", "upstream-records"}
    assert set(pins.PINNED_LEG_FILES_SINCE) <= set(pins.PINNED_LEG_FILES)
    # a name is a file OR a directory, never both
    assert not (set(pins.PINNED_LEG_FILES) & set(pins.PINNED_LEG_DIRS))


def test_every_corpus_leg_entry_is_in_the_pinned_mapping():
    """(a) SWEEP-prod #1, the defect this list exists to close: run the mapping over what the pipeline really
    produced. Against the checker's private allowlist this assertion fails on 8 names per leg."""
    corpus = _corpus()
    allowed = {n for n, s in pins.PINNED_LEG_FILES.items() if s in _COLLECTED} | set(pins.PINNED_LEG_DIRS)
    unexpected = {}
    for leg in _POSITIVE_LEGS:
        entries = {p.name for p in (corpus / leg).iterdir()}
        if entries - allowed:
            unexpected[leg] = sorted(entries - allowed)
    assert unexpected == {}, f"corpus entries no consumer would admit: {unexpected}"


def test_no_collected_leg_may_carry_an_excluded_name():
    """The other half of (a): `excluded_on_collect` is a claim that a collected leg NEVER carries these names.
    A corpus that carried one would mean the status is a fiction — which is what `transient` was until
    VERIFY-P5a F10 retired it and collect_leg.sh started excluding manifest-*.txt for real."""
    corpus = _corpus()
    never = {n for n, s in pins.PINNED_LEG_FILES.items() if s not in _COLLECTED}
    assert never, "the mapping claims nothing is dropped on collect — the statuses have gone missing"
    for leg in _POSITIVE_LEGS:
        entries = {p.name for p in (corpus / leg).iterdir()}
        assert not (entries & never), f"{leg}: carries a name the mapping says is never collected: {sorted(entries & never)}"


def test_every_required_name_is_present_in_every_corpus_positive_leg():
    """(b) with the corpus-version rule mirrored from the checker suite: `tee-status.json` is required only
    from v2.3 on, so a v2.2 corpus is graded without it instead of being failed by it."""
    corpus = _corpus()
    version = _corpus_version()
    required = pins.required_files(version)
    missing = {}
    for leg in _POSITIVE_LEGS:
        absent = sorted(n for n in required if not (corpus / leg / n).is_file())
        if absent:
            missing[leg] = absent
    assert missing == {}, f"corpus version {version}: required names absent: {missing}"


def test_the_corpus_version_rule_actually_discriminates():
    """The negative control of the ONE detector: the gated name must really be gated, since dropping it is the
    whole difference between the two answers, and an unknown version must RAISE rather than pick a default."""
    assert _corpus_version() in ("v2.2", "v2.3", "v2.4", "unknown")
    assert pins.required_files("v2.4") - pins.required_files("v2.2") == set(pins.PINNED_LEG_FILES_SINCE)
    assert "tee-status.json" in pins.required_files("v2.4")
    assert pins.required_files("v2.3") == pins.required_files("v2.4")   # SINCE says v2.3, so both carry it
    with pytest.raises(ValueError, match="unknown capture-contract version"):
        pins.required_files("v9.9")


@pytest.mark.parametrize("line, expected", [
    ("", "v2.2"),                                                     # the corpus's shutdown leg: 0 bytes
    ("2726031 2725866 25 /usr/bin/sleep 60\n", "v2.2"),               # the pre-header shape: line 1 is a row
    ("# process-scan v2.3 mode=after rows=0 utc=x\n", "v2.3"),
    ("# process-scan v2.4 mode=after rows=0 utc=x\n", "v2.4"),
])
def test_the_one_corpus_version_detector_reads_the_header(tmp_path, line, expected):
    (tmp_path / "process-scan-after.txt").write_text(line)
    assert pins.corpus_version(tmp_path) == expected


@pytest.mark.parametrize("line", ["# process-scan v9.9 mode=after rows=0 utc=x\n", "# process-scan\n",
                                  "#\n", "# process-scan v2.4mode=after\n"])
def test_the_one_corpus_version_detector_refuses_to_default(tmp_path, line):
    """A line that CLAIMS to be an enumeration header and names a version this pin does not know must raise.
    Defaulting it to v2.2 would grade a NEWER capture by an OLDER required set — silently admitting a leg that
    is missing artefacts its own contract requires, which is the drift PINNED_LEG_FILES_SINCE exists to stop."""
    (tmp_path / "process-scan-after.txt").write_text(line)
    with pytest.raises(ValueError, match="unrecognised process-scan header version"):
        pins.corpus_version(tmp_path)


def test_the_corpus_version_detector_defers_to_the_completeness_gate_when_there_is_no_scan(tmp_path):
    """No process-scan-after.txt at all is v2.2, not an exception: the name is itself `required`, so the
    caller's own completeness gate names it — a better diagnosis than a version error."""
    assert pins.corpus_version(tmp_path) == "v2.2"
    assert "process-scan-after.txt" in pins.required_files("v2.2")


def test_the_entry_allowlist_is_the_three_admissible_statuses():
    """`pins.entry_allowlist()` is what a consumer admits in a collected leg. Exported as a FUNCTION so the
    union is never re-typed (the checker's private `_LEG_REQUIRED_FILES` was that second copy)."""
    allow = pins.entry_allowlist()
    assert allow == {n for n, s in pins.PINNED_LEG_FILES.items() if s in _COLLECTED} | set(pins.PINNED_LEG_DIRS)
    assert "capture.json" in allow                                  # optional, admitted
    assert "buzzacp.raw.log" not in allow                           # excluded_on_collect, never admitted
    assert "manifest-post.txt" not in allow                         # F10: the retired `transient` pair
    assert pins.required_files("v2.4") <= allow


def test_every_pinned_dir_is_present_in_every_corpus_positive_leg():
    corpus = _corpus()
    for leg in _POSITIVE_LEGS:
        for name, status in pins.PINNED_LEG_DIRS.items():
            if status == "required":
                assert (corpus / leg / name).is_dir(), f"{leg}: {name}/ absent"


def test_the_negative_corpus_leg_is_exactly_the_pinned_negative_set():
    """The negative leg has its own pin (`NEGATIVE_REQUIRED_FILES`) and its own producer (acp_probe.py); it is
    deliberately NOT in PINNED_LEG_FILES. This pins that the two describe the same directory."""
    corpus = _corpus()
    entries = {p.name for p in (corpus / "negative").iterdir()}
    assert entries == set(pins.NEGATIVE_REQUIRED_FILES), sorted(entries ^ set(pins.NEGATIVE_REQUIRED_FILES))


# How many framedir entry names this parse resolves per producer, measured 2026-09-08 on the final bytes.
# A FLOOR, not an equality (VERIFY-P5a F3 asked for "the per-producer NAME COUNT is pinned; a refactor that
# hides a write fails loudly"): the defect direction is SHRINKAGE — the F3 refactor took pc_launch.py from 18
# recognised names to 16 with every test still green — and a floor fails on exactly that. Growth needs no
# equality here: a name a producer starts writing is already caught by the subset direction below (it must be
# in the ONE list) and by the orphan direction, while an equality would turn any other lane's legitimate new
# write into a red in THIS file rather than in theirs.
_PRODUCER_NAME_FLOOR = {
    "proofs/S0-01/tools/pc/pc_launch.py": 17,
    "proofs/S0-01/tools/pc/pc_post.sh": 19,
    "proofs/S0-01/tools/pc/pc_manifest.sh": 10,
    "proofs/S0-01/tools/pc/pc_mention.sh": 3,
    "proofs/S0-01/tools/frame_tee.py": 5,
    "proofs/S0-01/tools/build_capture_record.py": 9,
    "proofs/S0-01/tools/acp_probe.py": 4,
}


@pytest.mark.parametrize("rel", sorted(_PRODUCERS))
def test_every_producer_write_lands_in_the_pinned_mapping(rel):
    """(c) parse the producers themselves. A producer that starts writing a name outside the ONE list — the
    way `capture.json` and the eight launch/post markers got outside the checker's allowlist — fails here."""
    known = set(pins.PINNED_LEG_FILES) | set(pins.PINNED_LEG_DIRS)
    if _PRODUCERS[rel] == "negative":
        known |= set(pins.NEGATIVE_REQUIRED_FILES)
    names = _framedir_names(rel)
    assert names, f"{rel}: the parser found no framedir-anchored name — the parse is blind, not the file empty"
    assert names <= known, f"{rel}: writes names outside pins.PINNED_LEG_FILES: {sorted(names - known)}"


@pytest.mark.parametrize("rel", sorted(_PRODUCERS))
def test_the_producer_parse_does_not_lose_coverage(rel):
    """The gate on the GATE (VERIFY-P5a F3). `test_every_producer_write_lands_in_the_pinned_mapping` is a
    SUBSET assertion, so it gets greener the fewer names the parse resolves: the refactor that moved
    pc_launch.py's writes behind a lowercase `fd` made two names invisible and the suite said nothing. A
    per-producer floor makes shrinkage loud, and names the two directions apart."""
    floor = _PRODUCER_NAME_FLOOR[rel]
    names = _framedir_names(rel)
    assert len(names) >= floor, (
        f"{rel}: the parse resolves {len(names)} framedir names, below the pinned floor {floor} — a write is "
        f"hidden from the subset gate, or an idiom is missing from the parser: {sorted(names)}")


def test_every_pinned_name_has_a_producer():
    """The orphan direction: a mapping entry no producer writes is a list that has stopped describing the
    pipeline. (`agent-stderr.txt` is the live specimen and is deliberately NOT in this mapping — no positive-leg
    producer writes it; it belongs to the negative leg's own pin.)"""
    produced = set()
    for rel in _PRODUCERS:
        produced |= _framedir_names(rel)
    orphans = sorted((set(pins.PINNED_LEG_FILES) | set(pins.PINNED_LEG_DIRS)) - produced)
    assert orphans == [], f"pinned names no producer writes: {orphans}"


def test_no_positive_leg_producer_writes_agent_stderr_txt():
    """The finding that keeps `agent-stderr.txt` out of the mapping, pinned so a fix flips this test: it is
    written ONLY by acp_probe.py, into the NEGATIVE leg. The checker's F20 (`agent-stderr.txt` REQUIRED in
    every positive leg) is therefore unsatisfiable by the current pipeline — see this lane's report."""
    positive = set()
    for rel, shape in _PRODUCERS.items():
        if shape == "positive":
            positive |= _framedir_names(rel)
    assert "agent-stderr.txt" not in positive
    assert "agent-stderr.txt" in _framedir_names("proofs/S0-01/tools/acp_probe.py")
    assert "agent-stderr.txt" in pins.NEGATIVE_REQUIRED_FILES


def test_the_framedir_parser_fails_loud_on_an_unresolved_placeholder(tmp_path):
    """Negative control of the parse itself: an unexpanded `$VAR` in a framedir name must fail, never be
    silently dropped — a name the parser cannot resolve is a hole in the subset gate."""
    (tmp_path / "fake_producer.sh").write_text('echo x > "$FD/mystery-$UNKNOWN.json"\n')
    with pytest.raises(AssertionError, match="unresolved placeholder"):
        _framedir_names("fake_producer.sh", root=tmp_path)
    # the positive twin: a placeholder the parser DOES know is expanded, not rejected
    (tmp_path / "known.sh").write_text('echo x > "$FD/manifest-$PHASE.done"\n')
    assert _framedir_names("known.sh", root=tmp_path) == {"manifest-pre.done", "manifest-post.done"}


@pytest.mark.parametrize("source, expected", [
    ('open(os.path.join(fd, "a.json"), "w")', {"a.json"}),
    ('open(os.path.join(FD, "b.json"), "w")', {"b.json"}),
    ('open(os.path.join(framedir, "c.json"), "w")', {"c.json"}),
    ('Path(framedir, "d.json").write_text("")', {"d.json"}),
    ('Path(fd, "e.json").write_text("")', {"e.json"}),
    ('(d / "f.json").write_text("")', {"f.json"}),
    ('open(f"{fd}/g.json", "w")', {"g.json"}),
    ('echo x > $FD/h.json', {"h.json"}),
    ('echo x > "$FD"/i.json', {"i.json"}),
    ('echo x > "${FD}"/j.json', {"j.json"}),
    ('cp "$FD"/upstream-records/000001.json /tmp/x', {"upstream-records"}),   # only the ROOT entry
])
def test_the_producer_parser_recognises_every_declared_idiom(tmp_path, source, expected):
    """One row per idiom the parser claims to know — the committed control for its own vocabulary.

    VERIFY-P5a F3/F15 were blind spots no test could see, because the subset gate they feed gets GREENER the
    less the parser resolves. The per-producer floor closes that for the idioms a producer uses today, and
    only for those: mutant P8 (dropping the `Path(FD|fd|framedir, ...)` row) survived the floor, because no
    current producer writes that way. An idiom in the parser with no live site and no test is a check that
    cannot fire — so each one is pinned here instead."""
    (tmp_path / "producer_fixture").write_text(source + "\n")
    assert _framedir_names("producer_fixture", root=tmp_path) == expected


# --------------------------------------------------------------------------------------------------
# build_capture_record.py — #27/#28
# --------------------------------------------------------------------------------------------------
def _capture(*args):
    return subprocess.run([sys.executable, str(BUILD_CAPTURE), *args], capture_output=True, text=True, timeout=120)


def test_build_capture_record_fails_on_a_leg_with_no_timeline(tmp_path):
    """SWEEP-prod #27, the sweep's exact run: `build_capture_record.py <empty-dir> run-1` exited 0 and wrote
    `{"capture": ..., "files": {}, "version": 2}` — a record of nothing, green."""
    r = _capture(str(tmp_path), "run-1")
    assert r.returncode == 1, (r.returncode, r.stdout, r.stderr)
    assert r.stderr.startswith("run-1: missing required leg files: ")
    assert "timeline.jsonl" in r.stderr
    assert not (tmp_path / "capture.json").exists()


# The leg the tests below build comes from the ONE shared fixture in tests/conftest.py (`synthetic_leg`), not
# from a copy here: VERIFY-P5a F1 was a second, hand-written leg in another test file drifting from this list.


def test_build_capture_record_writes_the_record_for_a_complete_leg(tmp_path, synthetic_leg):
    """The positive control of the gate above: a leg carrying every required name passes and the record is
    written — so the red result is the missing files, not a tool that can no longer run."""
    leg = synthetic_leg(tmp_path / "run-1")
    r = _capture(str(leg), "run-1")
    assert r.returncode == 0, (r.returncode, r.stdout, r.stderr)
    rec = json.loads((leg / "capture.json").read_text())
    assert rec["capture"] == "s0-01-golden-leg:run-1" and rec["timeline"]["entries"] == 1


@pytest.mark.parametrize("dropped", ["timeline.jsonl", "owned-pids.json", "process-scan-teardown.txt",
                                     "tee-status.json", "mentions"])
def test_build_capture_record_takes_its_required_list_from_pins(tmp_path, synthetic_leg, dropped):
    """#28: the required list is the ONE list, not a local copy — dropping any `required` name from a leg the
    tool otherwise accepts fails it, naming that name. `owned-pids.json` and `process-scan-teardown.txt` are
    names the tool never reads: only a list-driven gate can notice them. `mentions` is the DIRECTORY arm: the
    tool's own `mentions_dir.is_dir()` gate would otherwise write a record with no mentions key and exit 0.
    `tee-status.json` is the VERSION arm: the fixture's leg declares v2.4 in its scan header, so the name
    PINNED_LEG_FILES_SINCE gates is genuinely required of it (a v2.2 leg is graded without it — the test
    below)."""
    leg = synthetic_leg(tmp_path / "run-1")
    if (leg / dropped).is_dir():
        (leg / dropped).rmdir()
    else:
        (leg / dropped).unlink()
    r = _capture(str(leg), "run-1")
    assert r.returncode == 1, (r.returncode, r.stdout, r.stderr)
    assert r.stderr.strip() == f"run-1: missing required leg files: {dropped}"
    assert not (leg / "capture.json").exists()


@pytest.mark.parametrize("shape", ["dir", "fifo"])
def test_build_capture_record_requires_a_regular_file_not_just_an_entry(tmp_path, synthetic_leg, shape):
    """VERIFY-P5a F9: the gate says `is_file()`, and nothing pinned that it means it. Relaxing it to
    `exists()` — the natural "simplification" — left all 55 tests green while a DIRECTORY named
    `owned-pids.json`, or a FIFO named `env.json`, satisfied the completeness gate and was then read by the
    tool (a FIFO with no writer would block it forever). Both shapes are rejected by name."""
    leg = synthetic_leg(tmp_path / "run-1")
    (leg / "owned-pids.json").unlink()
    if shape == "dir":
        (leg / "owned-pids.json").mkdir()
    else:
        os.mkfifo(leg / "owned-pids.json")
    r = _capture(str(leg), "run-1")
    assert r.returncode == 1, (r.returncode, r.stdout, r.stderr)
    assert r.stderr.strip() == "run-1: missing required leg files: owned-pids.json"
    assert not (leg / "capture.json").exists()


def test_build_capture_record_accepts_a_v2_2_corpus_leg(tmp_path):
    """VERIFY-P5a F2, the regression that mattered most: the tool hard-failed EVERY leg the pipeline has ever
    produced. It read the raw mapping and never consulted PINNED_LEG_FILES_SINCE, so a v2.2 corpus leg died on
    `missing required leg files: tee-status.json` — while the version rule sat in this file, correct and
    unused. Run over a real corpus leg copied to tmp_path (the corpus is a DECLARED input)."""
    corpus = _corpus()
    leg = tmp_path / "run-1"
    shutil.copytree(corpus / "run-1", leg)
    assert pins.corpus_version(leg) == "v2.2"
    assert "tee-status.json" not in pins.required_files("v2.2")
    r = _capture(str(leg), "run-1")
    assert r.returncode == 0, (r.returncode, r.stdout, r.stderr)
    assert r.stdout.strip() == "run-1: 9 raw files, 11 timeline entries"
    assert json.loads((leg / "capture.json").read_text())["timeline"]["entries"] == 11


def test_build_capture_record_fails_on_an_empty_timeline(tmp_path, synthetic_leg):
    """VERIFY-P5a F6: presence is not content. #27's defect survived in a narrower form — a complete leg whose
    `timeline.jsonl` is 0 bytes (a tee that died before its first frame, or a truncated collect) passed the
    completeness gate and produced `"timeline": {"entries": 0, ...}` at rc 0: a record of nothing, green."""
    leg = synthetic_leg(tmp_path / "run-1")
    (leg / "timeline.jsonl").write_text("")
    r = _capture(str(leg), "run-1")
    assert r.returncode == 1, (r.returncode, r.stdout, r.stderr)
    assert r.stderr.strip() == "run-1: timeline.jsonl is empty (0 bytes) — the leg records no frames"
    assert not (leg / "capture.json").exists()


def test_build_capture_record_fails_on_a_mention_with_no_receipt(tmp_path, synthetic_leg):
    """VERIFY-P5a F7: `mentions/<tag>.receipt.json` is not in PINNED_LEG_FILES (only the DIRECTORY is), so no
    gate dominated the ternary that read it — an absent receipt was written into the record as
    `"accepted": null`, a silent unknown presented as an observation."""
    leg = synthetic_leg(tmp_path / "run-1")
    (leg / "mentions" / "owner.event.json").write_text(json.dumps({"id": "a" * 64, "pubkey": "b" * 64,
                                                                  "content": pins.MENTION_TEXT}) + "\n")
    r = _capture(str(leg), "run-1")
    assert r.returncode == 1, (r.returncode, r.stdout, r.stderr)
    assert r.stderr.strip() == "run-1: mention receipt absent: mentions/owner.receipt.json"
    assert not (leg / "capture.json").exists()
    # the positive twin: with the receipt beside it the leg builds, and `accepted` is the receipt's own value
    (leg / "mentions" / "owner.receipt.json").write_text(json.dumps({"accepted": True}) + "\n")
    r = _capture(str(leg), "run-1")
    assert r.returncode == 0, (r.returncode, r.stdout, r.stderr)
    assert json.loads((leg / "capture.json").read_text())["mentions"]["owner"]["accepted"] is True


def test_build_capture_record_check_mode_keeps_its_own_diagnosis(tmp_path, synthetic_leg):
    """VERIFY-P5a F1/F16: `--check` asks ONE question — does the committed record still re-derive, byte for
    byte. Running the completeness gate in front of it cost that mode its diagnosis (a tampered record over an
    incomplete leg answered `missing required leg files`) and turned a round-trip unit test of the function
    red. Completeness is the BUILD path's contract; byte-identity is this one's."""
    leg = synthetic_leg(tmp_path / "run-1")
    assert _capture(str(leg), "run-1").returncode == 0
    (leg / "owned-pids.json").unlink()                       # incomplete AND tampered
    cj = leg / "capture.json"
    cj.write_text(cj.read_text().replace('"version": 2', '"version": 99'))
    r = _capture("--check", str(leg), "run-1")
    assert r.returncode == 1, (r.returncode, r.stdout, r.stderr)
    assert r.stderr.strip() == "run-1: capture.json differs from re-derived content (--check)"


def test_capture_json_is_admitted_by_the_pinned_mapping():
    """#28's other half: the tool's own output name must be a name a consumer admits. The checker rejected
    `capture.json` as an `unexpected entry` in every leg the tool had ever been run on."""
    assert pins.PINNED_LEG_FILES["capture.json"] in _COLLECTED


# --------------------------------------------------------------------------------------------------
# pc_launch.py — #12, #25, #31, #32, #48, #52 (the full paths are PC-only; the primitives are driven here)
# --------------------------------------------------------------------------------------------------
class _NoSleep:
    """Stand-in for the `time` module: the waits under test are 30 s and 300 s of real sleeping."""
    slept = 0.0

    def sleep(self, seconds):
        _NoSleep.slept += seconds


@pytest.fixture
def nosleep(monkeypatch):
    monkeypatch.setattr(pc_launch, "time", _NoSleep())


def test_pre_manifest_wait_breaks_on_a_manifest_error(tmp_path, nosleep):
    """#32: pc_manifest.sh dies with its own reason in manifest-pre.log and never touches `.done`; the
    success-only wait spent the full 300 s and then reported a TIMEOUT for a manifest that died at once."""
    (tmp_path / "manifest-pre.log").write_text("pc_manifest: tree venv-hermes missing at /home/rocco/x\n")
    with pytest.raises(SystemExit) as exc:
        pc_launch.wait_for_manifest(str(tmp_path), "pre", tries=600)
    assert "pre manifest failed before its .done marker" in str(exc.value)
    assert "tree venv-hermes missing" in str(exc.value)          # the tail is surfaced, not swallowed
    assert _NoSleep.slept < 1.0                                   # and it did not wait out the 300 s


def test_pre_manifest_wait_returns_when_the_marker_lands(tmp_path, nosleep):
    """Positive control: the marker wins over a non-empty log, so a late log line cannot fail a good run."""
    (tmp_path / "manifest-pre.done").write_text("")
    (tmp_path / "manifest-pre.log").write_text("noise\n")
    pc_launch.wait_for_manifest(str(tmp_path), "pre", tries=600)   # returns, no exit


def test_pre_manifest_wait_still_times_out_when_nothing_happens(tmp_path, nosleep):
    """The third arm: silence is still a timeout, and it names the budget it waited."""
    with pytest.raises(SystemExit, match="pre manifest did not finish within 3 s"):
        pc_launch.wait_for_manifest(str(tmp_path), "pre", tries=6)


def test_pc_launch_survives_an_empty_pre_manifest_summary(tmp_path):
    """#48: an empty or truncated summary raised IndexError from a display-only `[-1]`, killing the launcher
    right after the 300 s manifest wait and before env.json / argv.txt were ever written."""
    empty = tmp_path / "manifest-pre.summary"
    empty.write_text("")
    assert pc_launch.summary_tail(str(empty)) == "<empty summary>"
    full = tmp_path / "manifest-post.summary"
    full.write_text("hermes-agent abc\nbuzz def\n2026-09-06T05:09:59Z\n")
    assert pc_launch.summary_tail(str(full)) == "2026-09-06T05:09:59Z"


def test_pc_launch_fails_when_the_tee_identity_never_appears(tmp_path, nosleep):
    """#31: the `_note` default let the launcher report success; the failure then surfaced downstream as a
    runtime-identity KEY SET mismatch that never says "the tee never started"."""
    with pytest.raises(SystemExit, match=r"the tee did not write runtime-identity\.json within 15 s"):
        pc_launch.wait_for_tee_identity(str(tmp_path), tries=30)
    (tmp_path / "runtime-identity.json").write_text("{}")
    assert pc_launch.wait_for_tee_identity(str(tmp_path), tries=30) == str(tmp_path / "runtime-identity.json")


def test_pc_launch_names_a_buzz_exit_during_identity_capture(monkeypatch):
    """#12: `os.readlink("/proc/<pid>/exe")` and `sha256_file` on the same path raise FileNotFoundError once
    buzz-acp has exited — an uncaught traceback that left no identity merge, no owned-pids.json and no
    launch.ready, so run_leg.sh's READY poll spun 60 s before reporting "launch failed" with no reason."""
    def boom(path):
        raise FileNotFoundError(2, "No such file or directory", path)
    monkeypatch.setattr(pc_launch.os, "readlink", boom)
    with pytest.raises(SystemExit) as exc:
        pc_launch.buzz_identity(4242, 137)
    assert str(exc.value).startswith("pc_launch: buzz-acp exited during identity capture (rc=137)")


def test_pc_launch_captures_the_identity_of_a_live_process():
    """Positive control of the same helper on a LIVE pid (this test's own): the guard did not turn the
    capture into a silent no-op."""
    exe, sha = pc_launch.buzz_identity(os.getpid(), None)
    assert exe == os.readlink(f"/proc/{os.getpid()}/exe")
    assert re.fullmatch(r"[0-9a-f]{64}", sha)


def test_pc_launch_owned_closure_is_scoped_to_the_buzz_session():
    """#52: the closure used to be walked over the FULL `ps -eo pid,ppid` table, so any row whose ppid landed in
    the owned set was adopted into owned-pids.json — a stranger written into the evidence after one pid reuse.
    buzz-acp is spawned with start_new_session=True, so scoping `ps` to its session is the exact fix.

    The discriminator is the DETACHED grandchild: its ppid is inside the closure, so the full-table walk adopts
    it, while the session walk does not. That is a deliberate narrowing and it costs something — a descendant
    that calls setsid() for itself stops being tracked. The pinned tree does not: frame_tee.py spawns the agent
    with a plain Popen (no start_new_session), so the real buzz-acp -> tee -> agent chain stays in one session,
    which is what the real corpus's process-scan-after.txt shows."""
    parent = subprocess.Popen(
        [sys.executable, "-c", "import subprocess, sys, time;"
         " g = subprocess.Popen([sys.executable, '-c', 'import time; time.sleep(120)']);"
         " d = subprocess.Popen([sys.executable, '-c', 'import time; time.sleep(120)'], start_new_session=True);"
         " print(g.pid, d.pid, flush=True); time.sleep(120)"],
        stdout=subprocess.PIPE, text=True, start_new_session=True)
    outsider = subprocess.Popen([sys.executable, "-c", "import time; time.sleep(120)"])
    child = detached = None
    try:
        child, detached = (int(x) for x in parent.stdout.readline().split())
        owned = pc_launch.session_closure(parent.pid)
        assert owned == {parent.pid, child}, sorted(owned)
        assert detached not in owned              # ppid IS in the closure; the full-table walk would adopt it
        assert outsider.pid not in owned          # a live process outside the session is never adopted
        assert os.getpid() not in owned           # nor is the test runner, whatever the ppid chain says
    finally:
        for pid in (p for p in (child, detached) if p):
            try:
                os.kill(pid, 9)
            except ProcessLookupError:
                pass
        for proc in (parent, outsider):
            proc.kill()
            proc.wait(timeout=10)


def test_pc_launch_owned_closure_fails_loud_on_a_dead_session():
    """The negative control: no session, no closure — never a silent `{pid}` that would be written to
    owned-pids.json as a complete answer."""
    dead = subprocess.Popen([sys.executable, "-c", "pass"], start_new_session=True)
    dead.wait(timeout=10)
    with pytest.raises(SystemExit, match=r"listed no process .*session is gone"):
        pc_launch.session_closure(dead.pid)


def test_env_redaction_fingerprints_the_raw_bytes():
    """#25: `len` and `sha256_12` were computed on the string AFTER `decode(errors="replace")`, so for a value
    carrying any non-UTF-8 byte the recorded fingerprint described a mangled value, not the secret — and
    `check_env` only asserts `redacted is True`, so nothing downstream would ever notice."""
    import hashlib
    red = re.compile(pins.REDACTED_ENV_KEY_RE)
    secret = "sécret".encode() + b"\xff"   # 8 raw bytes; decode(replace) yields 7 characters
    out = pc_launch.redact_environ(b"PATH=/usr/bin\x00OMNIROUTE_API_KEY=" + secret + b"\x00", red)
    assert out["PATH"] == "/usr/bin"                       # non-secret values still decode for reading
    assert out["OMNIROUTE_API_KEY"]["redacted"] is True
    assert out["OMNIROUTE_API_KEY"]["len"] == len(secret)
    assert out["OMNIROUTE_API_KEY"]["sha256_12"] == hashlib.sha256(secret).hexdigest()[:12]
    # the negative control: this is NOT what the lossy path recorded
    lossy = secret.decode("utf-8", errors="replace")
    assert out["OMNIROUTE_API_KEY"]["sha256_12"] != hashlib.sha256(lossy.encode()).hexdigest()[:12]
    assert out["OMNIROUTE_API_KEY"]["len"] != len(lossy)


def test_env_redaction_covers_every_pinned_secret_key_name():
    """The redaction pattern is applied to KEY NAMES; this pins that the two env keys the launcher reads from
    files are actually caught by it (a pattern edit that stopped matching them would leak them into env.json)."""
    red = re.compile(pins.REDACTED_ENV_KEY_RE)
    raw = b"\x00".join(k.encode() + b"=v" for k in sorted(pins.PINNED_ENV_KEYS)) + b"\x00"
    out = pc_launch.redact_environ(raw, red)
    for key in ("BUZZ_PRIVATE_KEY", "OMNIROUTE_API_KEY"):
        assert out[key] == {"redacted": True, "len": 1, "sha256_12": out[key]["sha256_12"]}
    assert out["PATH"] == "v" and out["HERMES_HOME"] == "v"


# --------------------------------------------------------------------------------------------------
# pc_negative.py — #33
# --------------------------------------------------------------------------------------------------
def _stub_probe(tmp_path, ending):
    repo = tmp_path / "repo" / "proofs" / "S0-01" / "tools"
    repo.mkdir(parents=True)
    (repo / "acp_probe.py").write_text(
        "import os, sys\n"
        "fd = os.environ['S0_01_FRAMEDIR']\n"
        "open(os.path.join(fd, 'timeline.jsonl'), 'w').write('{\"seq\": 1}\\n')\n"
        f"{ending}\n")
    return tmp_path / "repo"


@pytest.mark.parametrize("ending, expected", [
    ("sys.exit(3)", 3),
    ("sys.exit(1)", 1),
    ("sys.exit(0)", 0),
    ("os.kill(os.getpid(), 9)", 137),      # VERIFY-P5a F8: a SIGKILLed probe
])
def test_pc_negative_propagates_the_probe_exit_code(tmp_path, monkeypatch, capsys, ending, expected):
    """#33: the wrapper ended on a `print` and exited 0 whatever the probe returned — run_leg.sh runs it under
    `set -euo pipefail` and walked on to collect_leg.sh with a failed negative leg in hand. Driven through the
    REAL wrapper and a REAL subprocess (a stub probe standing in for the PC's pinned agent, which is not here).

    The SIGKILL row is VERIFY-P5a F8: subprocess reports a signal death as -9, `raise SystemExit(-9)` hands
    the OS status 247, and the class was untested — so a `max(rc, 0)`-shaped regression would have made a
    KILLED probe report SUCCESS with all 55 tests green. 128+signal is the convention the shell shares."""
    monkeypatch.setattr(pc_negative, "BASE", str(tmp_path / "base"))
    monkeypatch.setattr(pc_negative, "REPO", str(_stub_probe(tmp_path, ending)))
    monkeypatch.setattr(pc_negative, "read_kv", lambda *_a: "not-a-real-token")
    assert pc_negative.main() == expected
    out = capsys.readouterr().out
    assert "timeline.jsonl" in out                     # the wrapper really ran and listed the leg
    if expected == 137:
        assert "probe rc -9" in out                    # the raw truth from subprocess is still printed ...
        assert "probe killed by signal 9; exit 137" in out   # ... and the mapping names its own reason
    else:
        assert f"probe rc {expected}" in out
        assert "killed by signal" not in out


# --------------------------------------------------------------------------------------------------
# collect_leg.sh / run_leg.sh — item 6
# --------------------------------------------------------------------------------------------------
# Every `--exclude=` pattern collect_leg.sh passes to tar, and what it is for. Each disposition is CHECKED
# against the mapping below, so a new or removed exclusion fails here rather than silently changing which
# names reach a collected leg.
_EXCLUDE_DISPOSITION = {
    "buzzacp.raw.log": "dropped",            # every mapping name it matches must be excluded_on_collect
    "manifest-*.txt": "dropped",             # VERIFY-P5a F10: the retired `transient` pair, excluded for real
    "manifest-*.log": "dropped",
    "manifest-*.txt.gz": "restored_by_name",  # matched names are re-supplied by collect_leg.sh itself
    "*.launch.log": "not_a_leg_file",         # the launch log lives in the markers dir, never in a framedir
}


def _exclude_patterns():
    return sorted(set(re.findall(r"--exclude=(?:'([^']+)'|([^\s'\"]+))", COLLECT_LEG.read_text())))


def test_collect_leg_exclusions_and_the_pinned_mapping_agree():
    patterns = {a or b for a, b in _exclude_patterns()}
    assert patterns == set(_EXCLUDE_DISPOSITION), sorted(patterns ^ set(_EXCLUDE_DISPOSITION))
    text = COLLECT_LEG.read_text()
    tar_line = next(ln for ln in text.splitlines() if "--exclude=" in ln)
    for pattern, disposition in _EXCLUDE_DISPOSITION.items():
        matched = {n for n in pins.PINNED_LEG_FILES if _glob_match(pattern, n)}
        if disposition == "dropped":
            assert matched, f"{pattern}: matches no pinned name — a stale exclusion"
            for name in matched:
                assert pins.PINNED_LEG_FILES[name] == "excluded_on_collect", \
                    f"{pattern} drops {name}, which the mapping calls {pins.PINNED_LEG_FILES[name]}"
        elif disposition == "restored_by_name":
            assert matched, f"{pattern}: matches no pinned name — a stale exclusion"
            for name in matched:
                assert pins.PINNED_LEG_FILES[name] in _COLLECTED, name
                stem = name.replace("pre", "$p").replace("post", "$p")
                assert any(stem in ln for ln in text.splitlines() if ln != tar_line), \
                    f"{pattern} drops {name} from the tar and nothing restores it"
        else:
            assert not matched, f"{pattern}: matches pinned names {sorted(matched)} but is declared {disposition}"


def test_every_excluded_on_collect_name_is_really_excluded():
    """The reverse direction: the mapping's `excluded_on_collect` claim must be backed by a pattern that
    actually drops the name — otherwise the status is a comment, not a fact."""
    patterns = {a or b for a, b in _exclude_patterns()}
    for name, status in pins.PINNED_LEG_FILES.items():
        if status == "excluded_on_collect":
            assert any(_glob_match(p, name) for p in patterns), f"{name}: no collect_leg.sh --exclude drops it"


def _glob_match(pattern, name):
    import fnmatch
    return fnmatch.fnmatchcase(name, pattern)


def test_the_leg_drivers_stop_on_the_first_failure():
    """`set -euo pipefail` in both drivers: a failed PC step must stop the leg, never fall through to collect
    (SWEEP-prod #33's blast radius — pc_negative.py's dropped exit code was harmless only because nothing
    else in run_leg.sh ignored a failure)."""
    for script in (RUN_LEG, COLLECT_LEG):
        assert "set -euo pipefail" in script.read_text(), script.name


def test_the_collected_shape_is_the_mapping_minus_what_collect_drops(tmp_path):
    """End to end over the CLAIM, with a real tar: a framedir carrying every mapping name, packed with
    collect_leg.sh's own exclusion list, must unpack to exactly the names the mapping calls collectable
    (plus the manifest bodies the script restores by name). This is what proves the four statuses describe
    one pipeline rather than four opinions."""
    fd = tmp_path / "fd"
    fd.mkdir()
    for name in pins.PINNED_LEG_FILES:
        (fd / name).write_text("x")
    for name in pins.PINNED_LEG_DIRS:
        (fd / name).mkdir()
    patterns = sorted({a or b for a, b in _exclude_patterns()})
    out = tmp_path / "leg.tgz"
    r = subprocess.run(["tar", "czf", str(out), *[f"--exclude={p}" for p in patterns], "."],
                       cwd=fd, capture_output=True, text=True, timeout=60)
    assert r.returncode == 0, r.stderr
    dst = tmp_path / "dst"
    dst.mkdir()
    subprocess.run(["tar", "xzf", str(out), "-C", str(dst)], check=True, timeout=60)
    got = {p.name for p in dst.iterdir()}
    restored = {n for n in pins.PINNED_LEG_FILES if _glob_match("manifest-*.txt.gz", n)}
    # VERIFY-P5a F10: this assertion used to end `| {n ... if s == "transient"}` — an escape hatch admitting
    # the two names the mapping claimed were never collected, i.e. the real tar proved the opposite of the
    # status. The hatch is gone because the exclusion is real; the consumer's allowlist is the whole expectation.
    assert got | restored == pins.entry_allowlist(), f"unpacked {sorted(got)}"
    assert "manifest-post.txt" not in got, "the uncompressed POST manifest body reached a collected leg"
    assert "manifest-pre.txt" not in got


# --------------------------------------------------------------------------------------------------
# pins.is_pinned_argv — the ONE pinned-ness rule (VERIFY-P5a F4/F5)
# --------------------------------------------------------------------------------------------------
@pytest.mark.parametrize("cmd, pinned, why", [
    (f"{pins.PINNED_BUZZ_ACP_EXE_REALPATH} --relay-url ws://127.0.0.1:3999", True, "the pinned binary"),
    (f"/usr/bin/python3 {pins.PINNED_TEE_PATH}", True, "an interpreter running the pinned tee"),
    (f"/home/rocco/s0-01-pinned/.venv-hermes/bin/python3.13 {pins.PINNED_AGENT_REALPATH}", True,
     "a venv interpreter running the pinned agent"),
    (f"/usr/bin/cat {pins.PINNED_TEE_PATH}", False, "F4: a bystander whose FIRST OPERAND is a pinned script"),
    (f"/usr/bin/vim {pins.PINNED_AGENT_REALPATH}", False, "F4: an editor open on the pinned agent"),
    (f"/usr/bin/sha256sum {pins.PINNED_TEE_PATH} -", False, "F4: a checksum over the pinned tee"),
    (f"python3 -c 'time.sleep(120) # {pins.PINNED_TEE_PATH}'", False, "#6: a decoy that only MENTIONS the path"),
    ("/usr/bin/sleep 120", False, "an unrelated process"),
    (f"python3 {pins.PINNED_TEE_PATH}", True, "the real corpus's own tee row (bare `python3`)"),
])
def test_is_pinned_argv_matches_the_entry_point_only(cmd, pinned, why):
    """VERIFY-P5a F4, reproduced with a REAL process before this fix: `argv[1] in PINNED_SCRIPTS` alone
    counted `/usr/bin/cat <tee>` as one of the proof's own pinned processes — so an owner opening frame_tee.py
    during a capture put a bystander into the leg's evidence body AND into `pinned_present`, and the checker
    then failed the leg for it (a survivor at :1263, or "not in the buzz-acp descendant tree" at :1325). The
    interpreter arm now also requires argv[0] to BE an interpreter."""
    assert pins.is_pinned_argv(cmd.split()) is pinned, why


def test_is_pinned_argv_does_not_count_a_pinned_binary_reached_by_another_path():
    """The DOCUMENTED LIMIT (VERIFY-P5a F5), pinned so it is a decision and not an accident: a pinned binary
    invoked through a symlink or bind path to the same file is not counted, and is dropped from the body.
    Closing it would need /proc/<pid>/exe, which the CHECKER — computing this same predicate over a COLLECTED
    text file — does not have; two venues computing two predicates over one body is the drift this function
    exists to remove. Bounded elsewhere: pc_launch.alive_pinned_buzz reads /proc/<pid>/exe and refuses to
    launch while a pinned buzz-acp lives, so the escape also needs the pidfile gone."""
    assert pins.is_pinned_argv("/alt/path/buzz-acp --relay-url ws://127.0.0.1:3999".split()) is False
    assert pins.is_pinned_argv([]) is False


def test_is_pinned_argv_matches_every_row_of_the_real_corpus_scan():
    """The positive control against reality: the narrowing must not lose a real row. Every body row of a real
    collected leg's process-scan-after.txt is one of the proof's three pinned processes."""
    corpus = _corpus()
    rows = (corpus / "run-1" / "process-scan-after.txt").read_text().splitlines()
    assert len(rows) == 3, rows
    for row in rows:
        cmd = row.split(None, 3)[3]
        assert pins.is_pinned_argv(cmd.split()) is True, cmd


def test_the_scan_producer_and_its_test_shim_read_one_rule():
    """AF-AP-42: the predicate was written three times — in pc_post.sh's heredoc, in the checker, and in the
    scan test's shim. The heredoc already imports pins by path, so there is no reason for a copy."""
    post = (ROOT / "proofs" / "S0-01" / "tools" / "pc" / "pc_post.sh").read_text()
    assert "pins.is_pinned_argv(cmd.split())" in post
    assert "PINNED_SCRIPTS" not in post, "a second copy of the rule is back in the producer"
    shim = (ROOT / "tests" / "test_s0_01_pc_post_scan.py").read_text()
    assert "pins.is_pinned_argv" in shim


# --------------------------------------------------------------------------------------------------
# the S0-03 launcher seam (tasks/briefs/s0-03-support/O1-report.md section 6)
# --------------------------------------------------------------------------------------------------
def test_the_s0_01_legs_keep_their_closed_set_without_a_profile():
    """The default path is unchanged: every S0-01 leg resolves to the pinned home's config.yaml, a foreign leg
    name is refused, and a leg's pinned model is still enforced. These were argparse `choices`, which enforced
    the sets and made them unopenable at the same time — S0-03's leg B could not use this capture path at all."""
    for leg in pins.LEGS:
        home, cfg = pc_launch.resolve_launch_profile(leg, pins.EXPECTED_MODEL[leg], None, pins.PINNED_HERMES_HOME)
        assert home == pins.PINNED_HERMES_HOME
        assert cfg == os.path.join(pins.PINNED_HERMES_HOME, "config.yaml")
    with pytest.raises(SystemExit, match=r"--leg 's0-03-hermes' is not an S0-01 leg"):
        pc_launch.resolve_launch_profile("s0-03-hermes", "s0-01-pong", None, pins.PINNED_HERMES_HOME)
    with pytest.raises(SystemExit, match="leg run-1 pins model s0-01-pong, got s0-01-slow"):
        pc_launch.resolve_launch_profile("run-1", "s0-01-slow", None, pins.PINNED_HERMES_HOME)


@pytest.mark.parametrize("argv, expected", [
    (["--leg", "s0-03-hermes", "--model", "foo"],
     "pc_launch: --leg 's0-03-hermes' is not an S0-01 leg (run-1, run-2, cancel, shutdown, two-users); "
     "a leg from another proof needs --profile <hermes config.yaml>"),
    (["--leg", "run-1", "--model", "s0-01-slow"],
     "pc_launch: leg run-1 pins model s0-01-pong, got s0-01-slow"),
    (["--leg", "run-1", "--model", "s0-01-pong", "--profile", "/etc/hostname"],
     "pc_launch: --leg run-1 is an S0-01 leg and always launches against the pinned Hermes home; "
     "--profile is for another proof's leg"),
])
def test_the_launcher_cli_really_reaches_the_leg_validator(argv, expected):
    """The wiring, through the REAL entry point. `--leg` and `--model` used to be argparse `choices`, which
    enforced the closed sets before `main()` ran; moving the rule into `resolve_launch_profile` is only a fix
    if the CLI still reaches it — a validator no argv can trigger is an emitted-but-unreachable check, which
    is how a fix becomes a hollow green. Driven as a subprocess, so nothing here is monkeypatched: each of the
    three refusals happens before any PC path is touched, which is why it runs in the sandbox at all."""
    r = subprocess.run([sys.executable, str(ROOT / "proofs" / "S0-01" / "tools" / "pc" / "pc_launch.py"), *argv],
                       capture_output=True, text=True, timeout=120)
    assert r.returncode == 1, (r.returncode, r.stdout, r.stderr)
    assert r.stderr.strip() == expected
    assert r.stdout == ""


def test_a_foreign_leg_launches_against_its_own_profile(tmp_path):
    """The seam itself, fail-closed in BOTH directions: a foreign leg needs `--profile` and then runs against
    that proof's own config, whose directory is the launch HERMES_HOME — so no other proof writes into S0-01's
    pinned tree; and an S0-01 leg REFUSES a foreign profile, so an S0-01 capture can never be taken quietly
    against someone else's config."""
    profile = tmp_path / "s0-03" / "config.yaml"
    profile.parent.mkdir()
    profile.write_text("default: agentfactory-build\n")
    home, cfg = pc_launch.resolve_launch_profile("s0-03-hermes", "agentfactory-build", str(profile),
                                                 pins.PINNED_HERMES_HOME)
    assert (home, cfg) == (str(profile.parent), str(profile))
    with pytest.raises(SystemExit, match="always launches against the pinned"):
        pc_launch.resolve_launch_profile("run-1", "s0-01-pong", str(profile), pins.PINNED_HERMES_HOME)
    with pytest.raises(SystemExit, match="is not an existing file"):
        pc_launch.resolve_launch_profile("s0-03-hermes", "m", str(tmp_path / "gone.yaml"),
                                         pins.PINNED_HERMES_HOME)


def test_the_launch_env_carries_the_profile_home_and_the_leg_name(tmp_path):
    """What the launch actually hands buzz-acp. The values below are fixture strings, never a real secret."""
    sec = tmp_path / ".secrets"
    sec.mkdir()
    (sec / "agent.env").write_text("BUZZ_PRIVATE_KEY=fixture-value-not-a-key\n")
    (sec / "owner.pub").write_text("f" * 64 + "\n")
    henv = tmp_path / "hermes.env"
    henv.write_text("OMNIROUTE_API_KEY=fixture-value-not-a-key\n")
    home = tmp_path / "s0-03-home"
    home.mkdir()
    markers = str(tmp_path / ".markers")
    fd = pc_launch.leg_framedir(markers, "s0-03-hermes")
    env = pc_launch.launch_env("s0-03-hermes", fd, str(home), "owner-only", "", str(sec), str(henv))
    assert env["HERMES_HOME"] == str(home)
    assert env["S0_01_FRAMEDIR"] == fd and fd.endswith("/v2-s0-03-hermes")
    assert set(env) == set(pins.PINNED_ENV_KEYS)          # the pinned key SET is unchanged by the seam
    # the S0-01 default is untouched: same helper, pinned home in and pinned home out
    s0_01 = pc_launch.launch_env("run-1", pc_launch.leg_framedir(markers, "run-1"), pins.PINNED_HERMES_HOME,
                                 "owner-only", "", str(sec), str(henv))
    assert s0_01["HERMES_HOME"] == pins.PINNED_HERMES_HOME
    assert s0_01["S0_01_FRAMEDIR"].endswith("/v2-run-1")


def _pins_in_subprocess(env_extra, expr="print(pins.hermes_home())"):
    env = {k: v for k, v in os.environ.items() if k != "S0_01_HERMES_HOME"}
    env["PYTHONPATH"] = str(ROOT / "proofs" / "S0-01")
    env.update(env_extra)
    return subprocess.run([sys.executable, "-c", f"import pins; {expr}"], env=env,
                          capture_output=True, text=True, timeout=120)


def test_the_hermes_home_override_is_validated(tmp_path):
    """The env override S0-03 asked for, and its negative control. An override that does not name an existing
    directory exits 64 with the name in the message, rather than launching a capture against a tree that is
    not there; unset means the S0-01 pin, unchanged."""
    r = _pins_in_subprocess({})
    assert r.returncode == 0 and r.stdout.strip() == pins.PINNED_HERMES_HOME, (r.returncode, r.stderr)
    r = _pins_in_subprocess({"S0_01_HERMES_HOME": str(tmp_path)})
    assert r.returncode == 0 and r.stdout.strip() == str(tmp_path), (r.returncode, r.stderr)
    for bad in (str(tmp_path / "does-not-exist"), ""):
        r = _pins_in_subprocess({"S0_01_HERMES_HOME": bad})
        assert r.returncode == 64, (bad, r.returncode, r.stdout, r.stderr)
        assert r.stderr.strip() == f"pins: S0_01_HERMES_HOME={bad!r} is not an existing directory"


def test_the_override_never_moves_the_pin_the_checker_compares_against(tmp_path):
    """The fail-open this seam must NOT open. `check_acp_conformance.py:468` and `negative_contract.py:210`
    compare a CAPTURED leg's env.json against pins.PINNED_HERMES_HOME. If the environment variable moved that
    constant, anyone running the checker with it set would make a leg captured under a foreign Hermes home
    pass its own oracle — an os.environ config channel opening a hole in the gate spine. Only the launcher
    reads the override, and it reads it once."""
    r = _pins_in_subprocess({"S0_01_HERMES_HOME": str(tmp_path)},
                            expr="print(pins.PINNED_HERMES_HOME); print(pins.hermes_home())")
    assert r.returncode == 0, r.stderr
    pinned, resolved = r.stdout.split()
    assert pinned == pins.PINNED_HERMES_HOME       # the checker's expectation did not move
    assert resolved == str(tmp_path)               # the launcher's did
