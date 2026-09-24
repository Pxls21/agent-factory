"""Tests for scripts/mojev_probe.py, the MoJev Gate 0 probe (tasks #210/#230; PC brief tasks/briefs/pc/pc-mojev-g0.md).

No model, no torch, no mojev. Every model-facing path is driven by the in-file doubles below (FakeEngine,
FakeTokenizer) or by scripted child processes. The doubles are never the source of a number in the findings:
the PC run is the only producer of docs/research/findings/mojev-probe-0.json.

The brief's numbers are written out here again (BRIEF_*) so the plan is checked against the brief, not against
the probe's own constants.
"""
import copy
import hashlib
import importlib.util
import json
import logging
import math
import os
import re
import statistics
import subprocess
import sys
import time
import warnings
import zlib
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "mojev_probe.py"
FINDINGS_JSON = ROOT / "docs" / "research" / "findings" / "mojev-probe-0.json"
FINDINGS_MD = ROOT / "docs" / "research" / "findings" / "MOJEV-PROBE-0.md"

# Set to True in the commit that files the PC run's findings (both files). While False the committed-findings test
# is SKIPPED BY DECLARATION, and test_findings_declaration_matches_the_tree turns red as soon as either file appears
# with the flag unflipped: the absence of a file never disarms an armed check.
FINDINGS_FILED = False

BRIEF_TOKENS = (2048, 4096, 8192, 16384)
BRIEF_CANDIDATES = (5, 10, 16)
BRIEF_DTYPES = ("released_bf16", "fp32")
BRIEF_CELLS = [f"{t}x{c}/{d}" for t in BRIEF_TOKENS for c in BRIEF_CANDIDATES for d in BRIEF_DTYPES]
BRIEF_BLOCKS = ("g0_3_truncation", "g0_4_order", "g0_5_determinism")
BRIEF_WEIGHTS_SIZE = 1_710_234_304
BRIEF_WEIGHTS_SHA256 = "eae27bf03e0e44501316cafab2406b1505732ddf4b836d19fbb8deb642f55f50"
BRIEF_CODE_HEAD = "a74d58cd19ec573e83e8e27f9fecd837b8d830fb"


def _load_probe():
    spec = importlib.util.spec_from_file_location("mojev_probe_under_test", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


probe = _load_probe()
STATUS = {"VmRSS": 5_000_000, "VmHWM": 6_000_000}
INTEGRITY = {"model_safetensors": {"verified": True, "size": BRIEF_WEIGHTS_SIZE, "sha256": BRIEF_WEIGHTS_SHA256}}
META = {"probe": {"script": "scripts/mojev_probe.py"}, "host": {}, "plan": {}}


# ---------------------------------------------------------------- test doubles

class FakeTensor:
    def __init__(self, data):
        self.data = data

    def tolist(self):
        return self.data


class FakeTokenizer:
    """Word-level stand-in for the snapshot tokenizer's call surface: a str or a list, offsets, truncation side."""

    PIECE = re.compile(r"\S+\s*|\s+")

    def __init__(self, truncation_side="right"):
        self.truncation_side = truncation_side

    def spans(self, text):
        return [m.span() for m in self.PIECE.finditer(text)]

    def __call__(self, text, add_special_tokens=True, return_offsets_mapping=False, truncation=False, max_length=None):
        rows = text if isinstance(text, list) else [text]
        ids, offsets = [], []
        for item in rows:
            spans = self.spans(item)
            row = [zlib.crc32(item[a:b].encode()) % 50021 for a, b in spans]
            if truncation and max_length is not None and len(row) > max_length:
                keep = slice(None, max_length) if self.truncation_side == "right" else slice(-max_length, None)
                row, spans = row[keep], spans[keep]
            ids.append(row)
            offsets.append(spans)
        out = {"input_ids": ids if isinstance(text, list) else ids[0]}
        if return_offsets_mapping:
            out["offset_mapping"] = offsets if isinstance(text, list) else offsets[0]
        return out


class BoundaryTokenizer(FakeTokenizer):
    """A text's last word, when two letters or fewer, merges into the word before it: a cut there miscounts."""

    def spans(self, text):
        spans = super().spans(text)
        if len(spans) >= 2 and len(text[spans[-1][0]:spans[-1][1]].strip()) <= 2:
            spans = spans[:-2] + [(spans[-2][0], spans[-1][1])]
        return spans


class PairTokenizer(FakeTokenizer):
    """Every word is two tokens, so every count is even: an odd target has no exact cut."""

    def spans(self, text):
        return [span for span in super().spans(text) for _ in (0, 1)]


class FakeField:
    def __init__(self, name, kind, options, description):
        listed = f" | options: {', '.join(options[:8])}" if len(options) <= 8 else ""
        self.prompt = f"{name.replace('_', ' ')} | kind: {kind}{listed}"


class FakeRecorder:
    def __init__(self):
        self.batch = None
        self.forward_ns = None


def _context_term(context, text):
    """Per candidate: a term shared by every candidate would cancel in the softmax and hide the state."""
    return (zlib.crc32((json.dumps(context[:3] + context[-3:]) + text).encode()) % 1000) * 1e-4


def slot_score(context, slot, text, dtype):
    """Moves with the packed slot (what G0-4 must detect); the fp32 double differs from the bf16 one."""
    return -0.05 * slot + (zlib.crc32(text.encode()) % 13) * 0.01 + _context_term(context, text) + (
        1e-3 * slot if dtype == "fp32" else 0.0)


def strong_slot_score(context, slot, text, dtype):
    """The slot decides the winner outright: the answer in slot 0 always wins."""
    return -1.0 * slot


def answer_score(context, slot, text, dtype):
    """Blind to the slot and to the label: only the answer's own words score."""
    answer = re.sub(r"^[A-P]\. ", "", text)
    return (zlib.crc32(answer.encode()) % 13) * 0.01 + _context_term(context, answer)


class FakeEngine:
    """Engine.answer's contract as read at mojev/serve.py:182-231: sort the menu by text (mojev/full.py:83), pack
    state + field prompt + candidates (mojev/full.py:167-192), one forward, softmax, unsort (serve.py:225), answers
    keyed by criterion (serve.py:122-127), usage.input_tokens = the packed length (serve.py:227-230)."""

    def __init__(self, tokenizer, dtype, score=slot_score, context_tokens=16384, on_truncate=None, truncate=True):
        self.tokenizer = tokenizer
        self.dtype = dtype
        self.score = score
        self.context_tokens = context_tokens
        self.on_truncate = on_truncate
        self.truncate = truncate
        self.model = FakeRecorder()
        self._Field = FakeField

    def answer(self, state, questions):
        (name, question), = questions.items()
        options = list(question["criteria"])
        order = sorted(range(len(options)), key=lambda i: options[i])
        menu = [options[i] for i in order]
        whole = self.tokenizer([state])["input_ids"][0]
        context = self.tokenizer([state], truncation=self.truncate, max_length=self.context_tokens)["input_ids"][0]
        if len(context) < len(whole) and self.on_truncate is not None:
            self.on_truncate()
        prompt = self.tokenizer([FakeField(name, "choice", tuple(menu), "").prompt])["input_ids"][0][:32]
        packed = context + prompt + [t for m in menu for t in self.tokenizer([m])["input_ids"][0]]
        n, c, f = len(packed), len(context), len(prompt)
        self.model.batch = {"packed_ids": FakeTensor([packed]), "packed_mask": FakeTensor([[True] * n]),
                            "context_span": FakeTensor([[1.0] * c + [0.0] * (n - c)]),
                            "field_span": FakeTensor([[[0.0] * c + [1.0] * f + [0.0] * (n - c - f)]])}
        self.model.forward_ns = 2_000_000
        exps = [math.exp(self.score(context, slot, m, self.dtype)) for slot, m in enumerate(menu)]
        total = math.fsum(exps)  # order-blind: a slot-blind scorer must read exactly 0.0
        probabilities = [0.0] * len(options)
        for slot, original in enumerate(order):
            probabilities[original] = exps[slot] / total
        best = max(range(len(options)), key=probabilities.__getitem__)
        answer = {"type": "choice", "choice": options[best], "confidence": probabilities[best],
                  "probabilities": dict(zip(options, probabilities))}
        return {name: answer}, {"input_tokens": n, "output_tokens": 0}


def fake_loader(truncation_side="right", score=slot_score, on_truncate=None, truncate=True, context_tokens=16384):
    def load(spec):
        engine = FakeEngine(FakeTokenizer(truncation_side), spec["dtype"], score, context_tokens, on_truncate, truncate)
        encoder = {"torch.float32": 10} if spec["dtype"] == "fp32" else {"torch.bfloat16": 10}
        facts = {"load_s": 1.5, "cast_s": 0.25 if spec["dtype"] == "fp32" else 0.0, "processor_load_s": 0.5,
                 "dtypes": {"encoder": encoder, "head": {"torch.float32": 4}}, "dtype_variant": spec["dtype"],
                 "env": {"python": "test-double", "torch": "none", "transformers": "none"}}
        return engine, facts
    return load


class FakeClock:
    """perf_counter_ns stand-in: requests take 20, 30, 10, 70, 20, ... ms. A cell's timed runs are then 30, 10 and
    70 ms: their median (30) is not their mean (36.7), so a p50 computed as a mean is caught."""

    STEPS_MS = (20, 30, 10, 70)

    def __init__(self):
        self.now = 0
        self.ticks = 0

    def __call__(self):
        if self.ticks % 2:
            self.now += self.STEPS_MS[self.ticks // 2 % len(self.STEPS_MS)] * 1_000_000
        self.ticks += 1
        return self.now


def make_source():
    words = [f"w{i % 97}x{i}" + ("\n" if i % 13 == 12 else " ") for i in range(24_000)]
    return "".join(words)


def spec_for(task, source_path):
    data = Path(source_path).read_bytes()
    return dict(task, pin="(test double)", snapshot="(test double)", source_path=str(source_path),
                source_sha256=hashlib.sha256(data).hexdigest(), threads=6)


def run_in_process(spec, loader):
    events = []
    probe.run_child_task(spec, loader, events.append, clock=FakeClock(), status=STATUS.__getitem__)
    return events, probe.record_from_events(spec["id"], events, exit_code=0, stop=None, elapsed_s=2.0,
                                            parent_max_rss_kb=7_000_000)


def task_by_id(task_id):
    return next(t for t in probe.build_plan() if t["id"] == task_id)


@pytest.fixture(scope="module")
def source_file(tmp_path_factory):
    path = tmp_path_factory.mktemp("source") / "state-source.txt"
    path.write_bytes(make_source().encode("utf-8"))
    return path


@pytest.fixture(scope="module")
def fake_run(source_file):
    tasks = probe.build_plan()
    records = {t["id"]: run_in_process(spec_for(t, source_file), fake_loader())[1] for t in tasks}
    return tasks, records


@pytest.fixture()
def fake_result(fake_run):
    tasks, records = fake_run
    return probe.assemble_result(tasks, copy.deepcopy(records), INTEGRITY, META)


# ---------------------------------------------------------------- the module, the plan, the dry run

def test_module_loads_without_torch_transformers_or_mojev():
    code = ("import importlib.util, sys\n"
            f"spec = importlib.util.spec_from_file_location('p', {str(SCRIPT)!r})\n"
            "module = importlib.util.module_from_spec(spec)\n"
            "spec.loader.exec_module(module)\n"
            "print(sorted(m for m in ('torch', 'transformers', 'mojev') if m in sys.modules))\n")
    out = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True, timeout=60)
    assert out.returncode == 0, out.stderr
    assert out.stdout.strip() == "[]"


def test_pins_and_limits_equal_the_briefs():
    assert (probe.WEIGHTS_SIZE, probe.WEIGHTS_SHA256, probe.CODE_HEAD) == (
        BRIEF_WEIGHTS_SIZE, BRIEF_WEIGHTS_SHA256, BRIEF_CODE_HEAD)
    assert probe.SNAPSHOT_REVISION == "0c8695b6252f4205907433d4e196a94f032e60c3"
    assert (probe.TEXT_REV, probe.TEXT_PATH) == ("8c684be", "docs/INCIDENT-LOG.md")
    assert (probe.THREADS, probe.NICE, probe.PHASE_TIMEOUT_S, probe.RSS_CAP_KB) == (6, 10, 600.0, 32 * 1024 * 1024)
    assert probe.CHILD_ENV["CUDA_VISIBLE_DEVICES"] == ""
    assert (probe.CHILD_ENV["HF_HUB_OFFLINE"], probe.CHILD_ENV["TRANSFORMERS_OFFLINE"]) == ("1", "1")


def test_plan_holds_the_brief_matrix_cheap_first():
    tasks = probe.build_plan()
    ids = [t["id"] for t in tasks]
    cells = [t for t in tasks if t["task"] == "cell" and not t["id"].startswith("g0_5")]
    assert sorted(t["id"] for t in cells) == sorted(BRIEF_CELLS)
    assert len(set(ids)) == len(ids)
    assert ids[0] == "2048x5/released_bf16"
    assert [t["tokens"] for t in cells] == sorted(t["tokens"] for t in cells)
    assert all(t["runs"] == 4 for t in cells)  # one warm-up and three timed runs
    for d in BRIEF_DTYPES:
        assert ids.count(f"g0_3/{d}") == ids.count(f"g0_4/{d}") == ids.count(f"g0_5-fresh/4096x10/{d}") == 1
    assert [t["task"] for t in tasks[-2:]] == ["truncation", "truncation"]  # the dearest last
    assert probe.build_plan() == tasks


def test_plan_g0_3_and_g0_4_shapes():
    tasks = probe.build_plan()
    for t in (t for t in tasks if t["task"] == "truncation"):
        assert (t["tokens"], t["budget"]) == (20_000, 16_384)
    for t in (t for t in tasks if t["task"] == "order"):
        assert (t["tokens"], t["candidates"]) == (4096, 16)
        assert len(t["labelings"]) >= 6  # the identity reference and at least five seeded orderings
        for perms in (t["controls"], t["labelings"]):
            assert all(sorted(p) == list(range(16)) for p in perms)
            assert len({tuple(p) for p in perms}) == len(perms)
            assert perms[0] == list(range(16))
    assert len(probe.LABELS) == 16 and sorted(probe.LABELS) == list(probe.LABELS)
    assert len(set(probe.ANSWERS)) == 16


def test_dry_run_prints_every_task_cut_and_candidate_and_writes_nothing(tmp_path):
    out = subprocess.run([sys.executable, str(SCRIPT), "--dry-run"], cwd=tmp_path, capture_output=True, text=True,
                         timeout=120)
    assert out.returncode == 0, out.stderr
    lines = out.stdout.split("\n")
    for cid in BRIEF_CELLS:
        tokens, candidates = cid.split("/")[0].split("x")
        wanted = f" {cid}: state = first {tokens} tokens (exact), candidates = first {candidates}, "
        assert [line for line in lines if wanted in line], f"no plan line for {cid}"
    trunc = [line for line in lines if " g0_3/" in line]
    assert len(trunc) == 2 and all("first 20000 tokens" in line and "its last 16384" in line for line in trunc)
    listed = [line.split(". ", 1)[1] for line in lines if re.match(r"^\s+\d+\. ", line)]
    assert listed == list(probe.ANSWERS)
    assert "matrix cells: 24 (planned 24); tasks: 30;" in out.stdout
    assert sorted(tmp_path.iterdir()) == []


def test_dry_run_flags_a_missing_path(tmp_path):
    out = subprocess.run([sys.executable, str(SCRIPT), "--dry-run", "--pin", str(tmp_path / "absent")],
                         capture_output=True, text=True, timeout=120)
    assert out.returncode == 2
    assert f"pin: {tmp_path / 'absent'} MISSING" in out.stdout


def test_only_refuses_an_unknown_task():
    out = subprocess.run([sys.executable, str(SCRIPT), "--only", "no-such-task", "--dry-run"], capture_output=True,
                         text=True, timeout=120)
    assert out.returncode == 64
    assert "unknown task id(s) ['no-such-task']" in out.stderr


# ---------------------------------------------------------------- G0-1 integrity

def test_weights_refuse_a_wrong_size(tmp_path):
    weights = tmp_path / "model.safetensors"
    weights.write_bytes(b"0123456789")
    with pytest.raises(probe.Refusal) as refused:
        probe.check_weights(weights, expected_size=11, expected_sha256="0" * 64)
    assert str(refused.value) == "G0-1: model.safetensors size 10 != pinned 11"


def test_weights_refuse_a_wrong_hash(tmp_path):
    weights = tmp_path / "model.safetensors"
    weights.write_bytes(b"0123456789")
    wrong = hashlib.sha256(b"another file").hexdigest()
    with pytest.raises(probe.Refusal) as refused:
        probe.check_weights(weights, expected_size=10, expected_sha256=wrong)
    actual = hashlib.sha256(b"0123456789").hexdigest()
    assert str(refused.value) == f"G0-1: model.safetensors sha256 {actual} != pinned {wrong}"


def test_weights_accept_the_pair_passed(tmp_path):
    weights = tmp_path / "model.safetensors"
    weights.write_bytes(b"0123456789")
    digest = hashlib.sha256(b"0123456789").hexdigest()
    record = probe.check_weights(weights, expected_size=10, expected_sha256=digest)
    assert (record["verified"], record["size"], record["sha256"]) == (True, 10, digest)


def test_weights_refuse_a_missing_file(tmp_path):
    with pytest.raises(probe.Refusal) as refused:
        probe.check_weights(tmp_path / "model.safetensors")
    assert refused.value.code == "G0-1" and "unreadable" in refused.value.detail


def test_cli_refuses_wrong_weights_before_any_load(tmp_path):
    snapshot, pin, out = tmp_path / "snapshot", tmp_path / "pin", tmp_path / "out"
    for d in (snapshot, pin, out):
        d.mkdir()
    (snapshot / "model.safetensors").write_bytes(b"x" * 10)
    run = subprocess.run([sys.executable, str(SCRIPT), "--pin", str(pin), "--snapshot", str(snapshot),
                          "--out", str(out / "result.json")], capture_output=True, text=True, timeout=120)
    assert run.returncode == 2
    assert run.stderr == f"REFUSED G0-1: model.safetensors size 10 != pinned {BRIEF_WEIGHTS_SIZE}\n"
    assert sorted(out.iterdir()) == []  # no work directory, so no child and no result


def _git_pin(tmp_path):
    repo = tmp_path / "pin"
    (repo / "mojev").mkdir(parents=True)
    (repo / "mojev" / "serve.py").write_text("class Engine:\n")
    git = ["git", "-C", str(repo), "-c", "user.name=probe-test", "-c", "user.email=probe-test@example.invalid",
           "-c", "commit.gpgsign=false", "-c", "core.hooksPath=/dev/null"]
    for args in (["init", "-q"], ["add", "-A"], ["commit", "-q", "-m", "pin"]):
        subprocess.run(git + args, check=True, capture_output=True)
    head = subprocess.run(["git", "-C", str(repo), "rev-parse", "HEAD"], capture_output=True, text=True, check=True)
    return repo, head.stdout.strip()


def test_code_pin_accepts_its_head_and_refuses_another(tmp_path):
    repo, head = _git_pin(tmp_path)
    assert probe.check_code(repo, expected_head=head)["verified"] is True
    with pytest.raises(probe.Refusal) as refused:
        probe.check_code(repo, expected_head="0" * 40)
    assert str(refused.value) == f"G0-1: code HEAD {head} != pinned {'0' * 40}"


def test_code_pin_refuses_a_tracked_change_and_a_non_checkout(tmp_path):
    repo, head = _git_pin(tmp_path)
    (repo / "mojev" / "serve.py").write_text("class Engine:  # edited\n")
    with pytest.raises(probe.Refusal) as refused:
        probe.check_code(repo, expected_head=head)
    assert str(refused.value).startswith("G0-1: code checkout has tracked changes:")
    plain = tmp_path / "plain"
    plain.mkdir()
    with pytest.raises(probe.Refusal) as refused:
        probe.check_code(plain, expected_head=head)
    assert "is not a readable git checkout" in refused.value.detail


def _cited_pin(root, filler_extra=""):
    files = {}
    for rel, line, text in probe.CITATIONS:
        files.setdefault(rel, {})[line] = text
    for rel, rows in files.items():
        body = [rows.get(i, f"# filler {i}{filler_extra}") for i in range(1, max(rows) + 1)]
        (root / rel).parent.mkdir(parents=True, exist_ok=True)
        (root / rel).write_text("\n".join(body) + "\n", encoding="utf-8")


def test_citations_are_read_by_line_number(tmp_path):
    _cited_pin(tmp_path)
    assert [row["ok"] for row in probe.verify_citations(tmp_path)] == [True] * len(probe.CITATIONS)
    serve = tmp_path / "mojev" / "serve.py"
    lines = serve.read_text(encoding="utf-8").split("\n")
    lines[192] = "order = list(range(len(options)))"  # line 193: the sort removed
    serve.write_text("\n".join(lines), encoding="utf-8")
    bad = [row["at"] for row in probe.verify_citations(tmp_path) if not row["ok"]]
    assert bad == ["mojev/serve.py:193"]


def test_citations_count_lines_on_newline_only(tmp_path):
    # A U+2028 inside a line is not a line break (AF-AP-132): splitlines() would shift every later line number.
    _cited_pin(tmp_path, filler_extra=chr(0x2028) + "tail")
    assert [row["ok"] for row in probe.verify_citations(tmp_path)] == [True] * len(probe.CITATIONS)


# ---------------------------------------------------------------- D-3 exact cuts

def test_cut_head_counts_exactly():
    tok, text = FakeTokenizer(), make_source()
    for n in (1, 7, 64, 2048):
        cut = probe.cut_head(tok, text, n)
        assert probe.count_tokens(tok, cut) == n and text.startswith(cut)


def test_cut_head_scans_past_a_boundary_miscount():
    tok, n = BoundaryTokenizer(), 40
    text = " ".join(["alpha"] * (n - 1) + ["of", "to"] + ["omega"] * 30)
    offsets = tok(text, add_special_tokens=False, return_offsets_mapping=True)["offset_mapping"]
    assert probe.count_tokens(tok, text[:offsets[n - 1][1]]) == n - 1  # the naive cut miscounts
    cut = probe.cut_head(tok, text, n)
    assert probe.count_tokens(tok, cut) == n and cut.rstrip().endswith("of to")


def test_cut_refuses_when_no_exact_cut_exists():
    with pytest.raises(probe.Refusal) as refused:
        probe.cut_head(PairTokenizer(), make_source(), 41)
    assert refused.value.code == "exact-cut-failed"
    with pytest.raises(probe.Refusal) as refused:
        probe.cut_tail(PairTokenizer(), " ".join(["word"] * 200), 41)
    assert refused.value.code == "exact-cut-failed"


def test_cut_refuses_a_short_source():
    with pytest.raises(probe.Refusal) as refused:
        probe.cut_head(FakeTokenizer(), " ".join(["word"] * 10), 11)
    assert refused.value.code == "state-source-too-short"


def test_cut_tail_counts_exactly():
    words = [f"t{i}" for i in range(100)]
    cut = probe.cut_tail(FakeTokenizer(), " ".join(words), 30)
    assert cut == " ".join(words[-30:])


# ---------------------------------------------------------------- one request through the Engine contract

def test_score_request_maps_probabilities_back_to_the_callers_order():
    engine = FakeEngine(FakeTokenizer(), "released_bf16", score=strong_slot_score)
    candidates = ["zeta", "alpha", "mid"]  # sorted slots: alpha 0, mid 1, zeta 2
    result = probe.score_request(engine, "one two three four", candidates, clock=FakeClock())
    p = dict(zip(candidates, result["probabilities"]))
    assert p["alpha"] > p["mid"] > p["zeta"] and result["choice"] == "alpha"
    assert (result["context_tokens_in_batch"], result["nonfinite"], result["wall_ms"]) == (4, False, 20.0)
    assert result["packed_tokens"] == result["usage_input_tokens"]


def test_score_request_marks_nonfinite_probabilities():
    engine = FakeEngine(FakeTokenizer(), "released_bf16", score=lambda c, slot, t, d: math.inf if slot == 0 else 0.0)
    result = probe.score_request(engine, "one two", ["a", "b"], clock=FakeClock())
    assert result["nonfinite"] is True and result["probabilities"] == ["nan", "0.0"]


def test_child_env_forces_cpu_offline_threads_and_the_pin():
    base = {"PATH": "/bin", "PYTHONPATH": "/x", "CUDA_VISIBLE_DEVICES": "0"}
    env = probe.child_env(base, "/pin")
    assert (env["CUDA_VISIBLE_DEVICES"], env["HF_HUB_OFFLINE"], env["OMP_NUM_THREADS"]) == ("", "1", "6")
    assert env["PYTHONPATH"] == os.pathsep.join(["/pin", "/x"]) and base["CUDA_VISIBLE_DEVICES"] == "0"


def test_dtype_variant_must_take():
    released = {"encoder": {"torch.bfloat16": 10}, "head": {"torch.float32": 4}}
    probe.check_dtypes("released_bf16", released)
    probe.check_dtypes("fp32", {"encoder": {"torch.float32": 10}, "head": {"torch.float32": 4}})
    for variant, dtypes in (("fp32", released),
                            ("fp32", {"encoder": {"torch.float32": 9, "torch.bfloat16": 1}, "head": {"torch.float32": 4}}),
                            ("released_bf16", {"encoder": {"torch.float32": 10}, "head": {"torch.float32": 4}}),
                            ("released_bf16", {"encoder": {"torch.bfloat16": 10}, "head": {"torch.bfloat16": 4}})):
        with pytest.raises(probe.Refusal) as refused:
            probe.check_dtypes(variant, dtypes)
        assert refused.value.code == "dtype-variant"


# ---------------------------------------------------------------- child tasks, in process

def test_cell_task_measures_the_planned_state(source_file):
    task = task_by_id("2048x5/released_bf16")
    events, record = run_in_process(spec_for(task, source_file), fake_loader())
    phases = [(e["phase"], e["state"]) for e in events if e["event"] == "phase"]
    names = ["load", "setup", "run-0", "run-1", "run-2", "run-3"]
    assert phases == [(name, state) for name in names for state in ("start", "end")]
    assert record["status"] == "OK" and events[-1]["event"] == "result"
    assert all(record["phases"][f"run-{k}"]["context_tokens_in_batch"] == 2048 for k in range(4))
    cell = probe.assemble_cell(task, record)
    timed = [record["phases"][f"run-{k}"]["wall_ms"] for k in (1, 2, 3)]
    assert (cell["p50_ms"], cell["max_ms"], cell["peak_rss_kb"]) == (statistics.median(timed), max(timed), 6_000_000)
    assert cell["in_process"]["bitwise_equal"] is True and cell["state"]["tokens"] == 2048


@pytest.mark.parametrize("side,kept", [("right", "first"), ("left", "last")])
def test_truncation_task_names_the_kept_end(source_file, side, kept):
    task = task_by_id("g0_3/released_bf16")
    _, record = run_in_process(spec_for(task, source_file), fake_loader(truncation_side=side))
    block = probe.assemble_truncation(task, record)
    assert block["kept"] == kept and block["dropped_tokens"] == 20_000 - 16_384
    assert block["compare"]["full_vs_head"]["bitwise_equal"] is (kept == "first")
    assert block["compare"]["full_vs_tail"]["bitwise_equal"] is (kept == "last")
    assert block["setup"]["head_cut"]["equals_first"] and block["setup"]["tail_cut"]["equals_last"]
    assert block["setup"]["truncation_side"] == side


def test_truncation_verdict_reads_neither_when_nothing_is_cut(source_file):
    task = task_by_id("g0_3/released_bf16")
    _, record = run_in_process(spec_for(task, source_file), fake_loader(truncate=False))
    block = probe.assemble_truncation(task, record)
    assert (block["kept"], block["dropped_tokens"]) == ("neither", 0)


def _noisy_cut():
    warnings.warn("double: state truncated", UserWarning)
    logging.getLogger("double.collator").warning("double: tokens dropped")
    os.write(2, b"double: a line on stderr\n")


def test_truncation_task_keeps_what_a_caller_could_see(source_file):
    task = task_by_id("g0_3/released_bf16")
    _, record = run_in_process(spec_for(task, source_file), fake_loader(on_truncate=_noisy_cut))
    reported = probe.assemble_truncation(task, record)["reported"]
    assert reported["full"]["warnings"] == ["UserWarning: double: state truncated"]
    assert reported["full"]["log_records"] == ["double.collator WARNING: double: tokens dropped"]
    assert "double: a line on stderr" in reported["full"]["stdio"]
    assert (reported["head"]["any"], reported["tail"]["any"]) == (False, False)


def test_order_task_detects_a_slot_dependent_scorer(source_file):
    task = task_by_id("g0_4/released_bf16")
    _, record = run_in_process(spec_for(task, source_file), fake_loader(score=strong_slot_score))
    block = probe.assemble_order(task, record)
    assert block["control"]["bitwise_equal"] is True and block["control"]["packed_inputs_equal"] is True
    labeled = block["labeled"]
    assert labeled["orderings"] == 5 and labeled["argmax_changes"] == 5 and labeled["largest_change"] > 0.5
    assert labeled["argmax_answers"][0] == probe.ANSWERS[0]  # identity labels: answer 0 holds slot 0
    # the brief's measure: per answer, the largest change against the reference (identity) ordering
    probs = [record["phases"][f"label-{k}"]["probabilities"] for k in range(6)]
    per = labeled["per_candidate"]
    assert [row["max_abs_change"] for row in per] == [max(abs(p[i] - probs[0][i]) for p in probs[1:])
                                                      for i in range(16)]
    assert [row["slots"] for row in per] == [[a[i] for a in task["labelings"]] for i in range(16)]


def test_order_task_reads_zero_for_a_slot_blind_scorer(source_file):
    task = task_by_id("g0_4/released_bf16")
    _, record = run_in_process(spec_for(task, source_file), fake_loader(score=answer_score))
    labeled = probe.assemble_order(task, record)["labeled"]
    assert (labeled["largest_change"], labeled["argmax_changes"]) == (0.0, 0)
    assert len(labeled["per_candidate"]) == 16


def test_task_refuses_a_state_the_batch_did_not_keep(source_file):
    # A collator that kept 1,000 of the 2,048 planned state tokens: the cell would time the wrong request.
    with pytest.raises(probe.Refusal) as refused:
        run_in_process(spec_for(task_by_id("2048x5/released_bf16"), source_file), fake_loader(context_tokens=1000))
    assert refused.value.code == "state-tokens"
    assert refused.value.detail == "run-0: 1000 state tokens in the batch, planned 2048"


def test_truncation_task_refuses_another_budget(source_file):
    with pytest.raises(probe.Refusal) as refused:
        run_in_process(spec_for(task_by_id("g0_3/fp32"), source_file), fake_loader(context_tokens=8192))
    assert str(refused.value) == "budget: checkpoint context_tokens 8192 != planned 16384"


def test_task_refuses_an_image_marker_in_the_state(tmp_path):
    source = tmp_path / "state-source.txt"
    source.write_bytes(("<|image_pad|>/etc/hostname " + make_source()).encode("utf-8"))
    with pytest.raises(probe.Refusal) as refused:
        run_in_process(spec_for(task_by_id("2048x5/fp32"), source), fake_loader())
    assert refused.value.code == "image-marker"


def test_run_tasks_logs_every_record_and_stops_at_the_first_refusal(tmp_path):
    plan = probe.build_plan()[:4]
    canned = {plan[0]["id"]: "OK", plan[1]["id"]: "REFUSED"}

    def spawn(task):
        status = canned[task["id"]]
        refusal = {"code": "processor", "detail": "double"} if status == "REFUSED" else None
        return {"task": task["id"], "status": status, "phases": {}, "final": {}, "stop": None, "refusal": refusal,
                "error": None, "exit_code": 3 if refusal else 0, "elapsed_s": 1.0}

    lines = []
    records, refused = probe.run_tasks(plan, spawn, tmp_path / "partial.jsonl", log=lines.append)
    logged = [json.loads(line) for line in (tmp_path / "partial.jsonl").read_text().split("\n") if line]
    assert list(records) == [t["id"] for t in plan[:2]] and refused["refusal"]["code"] == "processor"
    assert [r["task"] for r in logged] == list(records) and len(lines) == 2


# ---------------------------------------------------------------- the parent: one child process per task

EVENTS = "import json, sys, time\ndef ev(**fields):\n    print(json.dumps(fields), flush=True)\n"


def _child(body):
    return [sys.executable, "-c", EVENTS + body]


def _run(tmp_path, body, **limits):
    limits = dict({"timeout_s": 30.0, "rss_cap_kb": 1 << 30, "poll_s": 0.05}, **limits)
    return probe.run_child(_child(body), dict(os.environ), tmp_path / "child.stderr.log", "task", **limits)


def test_run_child_reads_a_complete_task(tmp_path):
    body = ("print('not an event', flush=True)\n"
            "ev(event='phase', phase='load', state='start')\n"
            "ev(event='phase', phase='load', state='end', data={'load_s': 1.0})\n"
            "ev(event='phase', phase='run-0', state='start')\n"
            "ev(event='phase', phase='run-0', state='end', data={'wall_ms': 5.0})\n"
            "ev(event='result', data={'hwm_end_kb': 123})\n")
    record = _run(tmp_path, body)
    assert (record["status"], record["exit_code"], record["final"]) == ("OK", 0, {"hwm_end_kb": 123})
    assert record["phases"] == {"load": {"load_s": 1.0}, "run-0": {"wall_ms": 5.0}}
    assert record["noise"] == ["not an event"]


def test_run_child_stops_a_run_past_the_limit(tmp_path):
    started = time.monotonic()
    record = _run(tmp_path, "ev(event='phase', phase='run-2', state='start')\ntime.sleep(60)\n", timeout_s=1.0)
    assert (record["status"], record["stop"]["phase"], record["stop"]["signal"]) == ("TIMEOUT", "run-2", "SIGTERM")
    assert 1.0 <= record["stop"]["elapsed_s"] < 30 and record["exit_code"] == -15
    assert time.monotonic() - started < 30


def test_run_child_stops_silence_between_phases(tmp_path):
    body = ("ev(event='phase', phase='load', state='start')\n"
            "ev(event='phase', phase='load', state='end', data={})\ntime.sleep(60)\n")
    record = _run(tmp_path, body, timeout_s=1.0)
    assert (record["status"], record["stop"]["phase"]) == ("TIMEOUT", "after load")


def test_run_child_stops_a_child_over_the_rss_cap(tmp_path):
    body = "ev(event='phase', phase='run-0', state='start')\nblob = 'x' * (160 << 20)\ntime.sleep(60)\n"
    record = _run(tmp_path, body, rss_cap_kb=64 * 1024)
    assert (record["status"], record["stop"]["phase"]) == ("RSS_CAP", "run-0")
    assert record["stop"]["rss_kb_at_stop"] > 64 * 1024 and record["exit_code"] < 0


def test_run_child_passes_a_refusal_through(tmp_path):
    body = "ev(event='refusal', code='processor', detail='no torchvision')\nsys.exit(3)\n"
    record = _run(tmp_path, body)
    assert (record["status"], record["refusal"], record["exit_code"]) == (
        "REFUSED", {"code": "processor", "detail": "no torchvision"}, 3)


def test_run_child_records_a_crash_with_its_stderr(tmp_path):
    record = _run(tmp_path, "sys.stderr.write('boom\\n')\nsys.exit(1)\n")
    assert (record["status"], record["exit_code"], record["stderr_tail"]) == ("ERROR", 1, ["boom"])


def test_real_child_without_torch_fails_loudly_and_measures_nothing(tmp_path, source_file):
    # This container has no torch and no pin: the real child must fail at the load, with no number produced.
    spec = spec_for(task_by_id("2048x5/released_bf16"), source_file)
    spec.update(pin=str(tmp_path / "no-pin"), snapshot=str(tmp_path / "no-snapshot"))
    record = probe.run_child([sys.executable, str(SCRIPT), "--child", json.dumps(spec)], dict(os.environ),
                             tmp_path / "child.stderr.log", spec["id"], timeout_s=60.0, poll_s=0.05)
    assert (record["status"], record["exit_code"], record["phases"]) == ("ERROR", 1, {})
    assert "No module named" in record["error"]


# ---------------------------------------------------------------- the result and its writer

def test_complete_result_writes_and_projects(fake_result, tmp_path):
    path = tmp_path / "result.json"
    digest = probe.write_result(fake_result, path)
    text = path.read_text(encoding="utf-8")
    doc = json.loads(text)
    assert digest == hashlib.sha256(text.encode("utf-8")).hexdigest() and "NaN" not in text
    assert sorted(doc["g0_2_matrix"]["cells"]) == sorted(BRIEF_CELLS)
    for block in BRIEF_BLOCKS:
        assert sorted(doc[block]) == sorted(BRIEF_DTYPES)
        assert all(doc[block][d]["status"] == "OK" for d in BRIEF_DTYPES)
    projected = doc["g0_6_gate1_feasibility"]["cells"]
    for cid in ("8192x10/released_bf16", "8192x10/fp32", "16384x16/released_bf16", "16384x16/fp32"):
        cell = doc["g0_2_matrix"]["cells"][cid]
        assert projected[cid]["projected_s"] == 100 * statistics.median(cell["runs_ms"]) / 1000


def test_result_compares_dtypes_on_every_request_scored_in_both(fake_result):
    rows = fake_result["g0_2_matrix"]["dtype_agreement"]
    expected = [f"{t}x{c}" for t in BRIEF_TOKENS for c in BRIEF_CANDIDATES]
    expected += [f"g0_3:{n}" for n in ("full", "head", "tail")]
    expected += [f"g0_4:control-{k}" for k in range(3)] + [f"g0_4:label-{k}" for k in range(6)]
    assert sorted(rows) == sorted(expected)
    assert all(isinstance(r["argmax_agree"], bool) and r["max_abs_diff"] > 0 for r in rows.values())


def test_determinism_block_reports_a_fresh_process_difference(fake_run):
    tasks, records = fake_run
    records = copy.deepcopy(records)
    probabilities = records["g0_5-fresh/4096x10/fp32"]["phases"]["run-0"]["probabilities"]
    probabilities[3] += 1e-7
    block = probe.assemble_result(tasks, records, INTEGRITY, META)["g0_5_determinism"]
    assert block["released_bf16"]["fresh_process"]["bitwise_equal"] is True
    assert block["fp32"]["fresh_process"]["bitwise_equal"] is False
    assert block["fp32"]["fresh_process"]["max_abs_diff"] == pytest.approx(1e-7, rel=1e-6)
    assert block["fp32"]["in_process"]["bitwise_equal"] is True and block["fp32"]["in_process"]["count"] == 4


@pytest.mark.parametrize("cid", BRIEF_CELLS)
def test_writer_refuses_a_missing_cell_by_name(fake_result, tmp_path, cid):
    del fake_result["g0_2_matrix"]["cells"][cid]
    with pytest.raises(probe.HollowResult) as refused:
        probe.write_result(fake_result, tmp_path / "result.json")
    assert f"missing-cell:{cid}" in refused.value.problems and sorted(tmp_path.iterdir()) == []


@pytest.mark.parametrize("block", BRIEF_BLOCKS)
def test_writer_refuses_a_missing_block_by_name(fake_result, tmp_path, block):
    del fake_result[block]
    with pytest.raises(probe.HollowResult) as refused:
        probe.write_result(fake_result, tmp_path / "result.json")
    assert refused.value.problems == [f"missing-block:{block}"] and sorted(tmp_path.iterdir()) == []


def test_writer_refuses_a_block_missing_one_dtype(fake_result, tmp_path):
    del fake_result["g0_4_order"]["fp32"]
    with pytest.raises(probe.HollowResult) as refused:
        probe.write_result(fake_result, tmp_path / "result.json")
    assert refused.value.problems == ["missing-block:g0_4_order/fp32"]


def test_writer_refuses_an_unmeasured_cell_and_unverified_weights(fake_result, tmp_path):
    fake_result["g0_2_matrix"]["cells"]["4096x5/fp32"]["status"] = "ERROR"
    fake_result["g0_1_integrity"] = {"model_safetensors": {"verified": False}}
    with pytest.raises(probe.HollowResult) as refused:
        probe.write_result(fake_result, tmp_path / "result.json")
    assert refused.value.problems == ["integrity-not-verified", "unmeasured-cell:4096x5/fp32:ERROR"]


@pytest.mark.parametrize("damage,problem", [
    (lambda r: r["g0_4_order"]["released_bf16"]["labeled"].update(orderings=4), "incomplete-block:g0_4_order/released_bf16"),
    (lambda r: r["g0_3_truncation"]["fp32"].pop("kept"), "incomplete-block:g0_3_truncation/fp32"),
    (lambda r: r["g0_5_determinism"]["fp32"]["in_process"].update(count=1), "incomplete-block:g0_5_determinism/fp32"),
    (lambda r: r["g0_2_matrix"]["cells"]["8192x10/fp32"].update(runs_ms=[1.0, 2.0]), "bad-runs:8192x10/fp32"),
    (lambda r: r["g0_2_matrix"]["cells"]["8192x10/fp32"].update(p50_ms=1.0), "bad-p50-or-max:8192x10/fp32"),
    (lambda r: r["g0_2_matrix"]["cells"]["8192x10/fp32"].update(peak_rss_kb=None), "missing-peak_rss_kb:8192x10/fp32"),
    (lambda r: r["g0_2_matrix"]["cells"]["2048x16/fp32"]["probabilities"].pop(), "bad-probabilities:2048x16/fp32"),
    (lambda r: r["g0_6_gate1_feasibility"]["cells"].pop("8192x10/fp32"), "missing-projection:8192x10/fp32"),
])
def test_writer_names_an_incomplete_part(fake_result, tmp_path, damage, problem):
    damage(fake_result)
    with pytest.raises(probe.HollowResult) as refused:
        probe.write_result(fake_result, tmp_path / "result.json")
    assert refused.value.problems == [problem]


def _timed_out(record, phase):
    names = list(record["phases"])
    events = [{"event": "phase", "phase": name, "state": "end", "data": record["phases"][name]}
              for name in names[:names.index(phase)]]
    stop = {"status": "TIMEOUT", "phase": phase, "elapsed_s": 600.4, "limit_s": 600.0, "signal": "SIGTERM"}
    return probe.record_from_events(record["task"], events, exit_code=-15, stop=stop, elapsed_s=1900.2,
                                    parent_max_rss_kb=9_000_000)


def test_a_timeout_cell_counts_with_its_elapsed_time(fake_run, tmp_path):
    tasks, records = fake_run
    records = copy.deepcopy(records)
    records["16384x16/fp32"] = _timed_out(records["16384x16/fp32"], "run-2")
    result = probe.assemble_result(tasks, records, INTEGRITY, META)
    cell = result["g0_2_matrix"]["cells"]["16384x16/fp32"]
    assert (cell["status"], cell["p50_ms"], cell["stop"]["elapsed_s"], len(cell["runs_ms"])) == (
        "TIMEOUT", None, 600.4, 1)
    assert result["g0_6_gate1_feasibility"]["cells"]["16384x16/fp32"]["projected_s_lower_bound"] == 60_000.0
    probe.write_result(result, tmp_path / "result.json")
    del cell["stop"]["elapsed_s"]
    with pytest.raises(probe.HollowResult) as refused:
        probe.write_result(result, tmp_path / "again.json")
    assert refused.value.problems == ["stop-without-elapsed:16384x16/fp32"]


def test_compare_is_bitwise_and_refuses_nonfinite():
    assert probe.compare([0.25, 0.75], [0.25, 0.75]) == {"comparable": True, "bitwise_equal": True, "max_abs_diff": 0.0}
    near = probe.compare([0.25, 0.75], [0.25, math.nextafter(0.75, 1.0)])
    assert near["bitwise_equal"] is False and 0 < near["max_abs_diff"] < 1e-15
    for bad in ([math.nan, 0.5], [math.inf, 0.0], ["nan", 0.5], [0.5]):
        assert probe.compare(bad, [0.5, 0.5]) == {"comparable": False, "bitwise_equal": False, "max_abs_diff": None}


# ---------------------------------------------------------------- the committed findings (the PC run's output)

def findings_problems(doc, md_text):
    """The committed findings, checked independently of the probe's own validator."""
    problems = []
    cells = (doc.get("g0_2_matrix") or {}).get("cells") or {}
    md_lines = md_text.split("\n")
    for cid in BRIEF_CELLS:
        cell = cells.get(cid)
        status = cell.get("status") if isinstance(cell, dict) else None
        if cell is None:
            problems.append(f"missing-cell:{cid}")
        elif status == "OK":
            p50 = cell.get("p50_ms")
            if not (isinstance(p50, float) and math.isfinite(p50) and p50 > 0):
                problems.append(f"bad-p50:{cid}")
            elif not [line for line in md_lines if cid in line and f"{p50:.1f}" in line]:
                problems.append(f"p50-not-quoted:{cid}")
        elif status == "TIMEOUT" or status == "RSS_CAP":
            elapsed = (cell.get("stop") or {}).get("elapsed_s")
            if not (isinstance(elapsed, (int, float)) and math.isfinite(elapsed) and elapsed > 0):
                problems.append(f"stop-without-elapsed:{cid}")
        else:
            problems.append(f"unmeasured-cell:{cid}")
    for block in BRIEF_BLOCKS:
        entry = doc.get(block)
        if not isinstance(entry, dict) or sorted(entry) != sorted(BRIEF_DTYPES):
            problems.append(f"missing-block:{block}")
    return problems


def test_findings_checker_accepts_a_complete_fixture(fake_result):
    doc = json.loads(json.dumps(fake_result))
    assert findings_problems(doc, probe.render_cells_md(fake_result)) == []


def test_findings_checker_names_each_defect(fake_result):
    md = probe.render_cells_md(fake_result)
    doc = json.loads(json.dumps(fake_result))
    del doc["g0_2_matrix"]["cells"]["2048x5/fp32"]
    doc["g0_2_matrix"]["cells"]["4096x10/fp32"].update(status="TIMEOUT", stop={"phase": "run-1"})
    del doc["g0_3_truncation"]["fp32"]
    unquoted = "\n".join(line for line in md.split("\n") if "8192x16/released_bf16" not in line)
    assert findings_problems(doc, unquoted) == [
        "missing-cell:2048x5/fp32", "stop-without-elapsed:4096x10/fp32", "p50-not-quoted:8192x16/released_bf16",
        "missing-block:g0_3_truncation"]


def test_findings_declaration_matches_the_tree():
    filed = [p.name for p in (FINDINGS_JSON, FINDINGS_MD) if p.is_file()]
    expected = [FINDINGS_JSON.name, FINDINGS_MD.name] if FINDINGS_FILED else []
    assert filed == expected, "file both findings and set FINDINGS_FILED = True in the same commit"


@pytest.mark.skipif(not FINDINGS_FILED, reason="NOT run here: declared unfiled until the coordinator's MOJEV-G0 PC run "
                                               "files mojev-probe-0.json and MOJEV-PROBE-0.md (FINDINGS_FILED)")
def test_committed_findings_hold_every_cell_block_and_quoted_p50():
    doc = json.loads(FINDINGS_JSON.read_text(encoding="utf-8"))
    problems = findings_problems(doc, FINDINGS_MD.read_text(encoding="utf-8"))
    assert problems == []
