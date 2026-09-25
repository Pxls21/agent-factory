"""P1 replay harness tests (task #231; seed seeds/seed-jev-pipes-p1-v1.yaml). Deterministic and LLM-free.

- Scorer answers: tests/fixtures/jev_pipes/answers.jsonl, recorded from the real local Laya server by record_answers.py
  and served here by request-body sha256 (a body never recorded gets a 404, so a drifted request is loud). None is typed.
- The transcript: make_fixture.py builds a synthetic session in the production record shapes; record_shapes.json (keys and
  type names captured from the real transcript) pins it (AF-AP-42).
- Fail-open (`-k failopen`): the vendored pruner through the real bridge process, against misbehaving local servers on
  temp ports, one test per trip condition, each with the original text coming back unchanged and the reason recorded.
- The floor option: the vendored `minTokensFloor` lowers the floor only when passed; a 9,999-token output still passes
  untouched without it.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import socket
import subprocess
import sys
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
FIXTURES = REPO / "tests" / "fixtures" / "jev_pipes"
VENDOR = REPO / "vendor" / "jev-pruner"
sys.path.insert(0, str(REPO / "scripts"))
sys.path.insert(0, str(FIXTURES))

from jev_pipes import accounting, replay_pruner, transcript  # noqa: E402
import capture_shapes  # noqa: E402
import make_fixture  # noqa: E402

ANSWERS = {json.loads(line)["sha256"]: json.loads(line) for line in (FIXTURES / "answers.jsonl").read_text().splitlines()}
TOOLS = {"Bash", "Read", "Grep"}


def _node_strips_types() -> bool:
    probe = subprocess.run(["node", "-e", "process.stdout.write(String(Boolean(process.features && process.features.typescript)))"],
                           capture_output=True, text=True, timeout=30)
    return probe.stdout.strip() == "true"


# Loading the vendored TypeScript (the hook, src/) needs a Node that strips types (22.18 or later). Where it cannot, these
# checks SKIP with this reason; the bridge itself is plain JavaScript and every other test runs.
needs_strip = pytest.mark.skipif(not _node_strips_types(), reason="this Node cannot strip TypeScript types (22.18 or later can)")


# ---------------------------------------------------------------- local scorers

class Scorer:
    """A local HTTP scorer on a temp port. behavior: recorded (answers.jsonl by body sha256; unknown -> 404), status500,
    not_json, no_answers, incomplete (a recorded answer less its first question id), slow503. `delay` holds each request."""

    def __init__(self, behavior: str = "recorded", delay: float = 0.0):
        self.behavior, self.delay = behavior, delay
        self.bodies: list[bytes] = []
        self.in_flight = 0
        self.max_in_flight = 0
        lock = threading.Lock()
        outer = self

        class Handler(BaseHTTPRequestHandler):
            def log_message(self, *args):
                pass

            def do_POST(self):
                body = self.rfile.read(int(self.headers.get("content-length") or 0))
                with lock:
                    outer.bodies.append(body)
                    outer.in_flight += 1
                    outer.max_in_flight = max(outer.max_in_flight, outer.in_flight)
                try:
                    time.sleep(outer.delay)
                    status, text = outer.respond(body)
                    data = text.encode()
                    self.send_response(status)
                    self.send_header("content-type", "application/json")
                    self.send_header("content-length", str(len(data)))
                    self.end_headers()
                    self.wfile.write(data)
                except (BrokenPipeError, ConnectionResetError):
                    pass
                finally:
                    with lock:
                        outer.in_flight -= 1

        self.server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        threading.Thread(target=self.server.serve_forever, daemon=True).start()
        self.url = f"http://127.0.0.1:{self.server.server_port}/v1/systemone"

    def respond(self, body: bytes) -> tuple[int, str]:
        recorded = ANSWERS.get(hashlib.sha256(body).hexdigest())
        if self.behavior == "recorded":
            return (recorded["status"], recorded["body"]) if recorded else (404, '{"error": "no recording for this body"}')
        if self.behavior == "status500":
            return 500, '{"error": "misbehaving fixture scorer"}'
        if self.behavior == "not_json":
            return 200, "this is not json"
        if self.behavior == "no_answers":
            return 200, '{"model": "fixture"}'
        if self.behavior == "incomplete":
            answer = json.loads(recorded["body"])
            del answer["answers"][sorted(answer["answers"])[0]]
            return 200, json.dumps(answer)
        if self.behavior == "slow503":
            return 503, '{"error": "busy"}'
        raise AssertionError(self.behavior)

    def close(self):
        self.server.shutdown()
        self.server.server_close()


@pytest.fixture
def fixture_transcript(tmp_path):
    return make_fixture.build(tmp_path / "fixture")


def closed_port_url() -> str:
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        port = sock.getsockname()[1]
    return f"http://127.0.0.1:{port}/v1/systemone"


def transport(url: str, mode: str = "replay", budget_ms: float = 60_000.0) -> dict:
    return dict(replay_pruner.MODES[mode], url=url, budget_ms=budget_ms)


def job_for(path: Path, tool_use_id: str, tr: dict, messages: list | None = None) -> tuple[dict, str, object]:
    """(the bridge job for one fixture result, the text the pruner prunes, the snapshot's history token set)."""
    limit = path.stat().st_size
    index = transcript.scan(str(path), limit, TOOLS, 2000, accounting.tokens)
    cand = next(c for c in index.candidates if c.tool_use_id == tool_use_id)
    gen = transcript.windows(str(path), limit, {cand.offset}, accounting.tokens)
    snap = next(gen)
    job, source = replay_pruner.build_job(cand, snap, tr)
    history = set(snap.history_tokens)
    job["messages"] = json.loads(json.dumps(messages if messages is not None else snap.messages))
    gen.close()
    job["return_stdout"] = True
    return job, source, history


def bridge(job: dict) -> dict:
    proc = subprocess.run(["node", str(replay_pruner.BRIDGE)], input=json.dumps(job) + "\n", capture_output=True,
                          text=True, timeout=120, cwd=REPO)
    assert proc.returncode == 0, proc.stderr[-2000:]
    return json.loads(proc.stdout.strip().splitlines()[-1])


def run_harness(tmp_path: Path, sources: Path, url: str, mode: str = "replay", budget_ms: float = 60_000.0) -> list[dict]:
    decisions = tmp_path / f"decisions-{mode}.jsonl"
    rc = replay_pruner.main(["--min-chars", "2000", "--out", str(tmp_path / f"out-{mode}"), "--mode", mode, "--sample", "0",
                             "--secondary-sample", "10", "--sources", str(sources), "--scorer-url", url,
                             "--budget-ms", str(budget_ms), "--decisions", str(decisions)])
    assert rc == 0
    return [json.loads(line) for line in decisions.read_text().splitlines()]


def by_id(rows: list[dict]) -> dict[str, dict]:
    return {r["result_id"]: r for r in rows}


# ---------------------------------------------------------------- fail-open, one test per trip condition (AC5)

def assert_failed_open(answer: dict, original: str, reason: str) -> None:
    assert answer["decision"] == "fail_open", answer
    assert answer["fail_open"] is True
    assert answer["fail_open_reason"] == reason
    assert reason in [t["reason"] for t in answer["trips"]]
    assert answer["output"] is None and answer["result"] is None
    assert answer["stdout_after"] == original  # the original text comes back unchanged


def test_failopen_control_recorded_scorer_answers_without_trips(fixture_transcript):
    """The negative control for every fail-open test below: the same job against the recorded real answers trips nothing."""
    scorer = Scorer("recorded")
    try:
        job, source, _ = job_for(fixture_transcript, "toolu_fx_01", transport(scorer.url))
        answer = bridge(job)
    finally:
        scorer.close()
    assert answer["fail_open"] is False and answer["trips"] == []
    assert answer["decision"] == "kept_all"  # the real scorer's answers keep every chunk
    assert answer["stdout_after"] == source


def test_failopen_refused(fixture_transcript):
    job, source, _ = job_for(fixture_transcript, "toolu_fx_01", transport(closed_port_url()))
    assert_failed_open(bridge(job), source, "refused")


def test_failopen_budget_replay_waits_and_times_the_request(fixture_transcript):
    scorer = Scorer("recorded", delay=0.6)
    try:
        job, source, _ = job_for(fixture_transcript, "toolu_fx_01", transport(scorer.url, "replay", budget_ms=200))
        answer = bridge(job)
        control_job, _, _ = job_for(fixture_transcript, "toolu_fx_01", transport(scorer.url, "replay", budget_ms=30_000))
        control = bridge(control_job)
    finally:
        scorer.close()
    assert_failed_open(answer, source, "budget")
    assert next(t for t in answer["trips"] if t["reason"] == "budget")["t_ms"] == 200
    assert answer["requests"][0]["latency_ms"] >= 600  # replay mode waited for the answer and kept its real latency
    assert control["fail_open"] is False and control["decision"] == "kept_all"


def test_failopen_budget_live_aborts_at_the_budget(fixture_transcript):
    scorer = Scorer("recorded", delay=2.0)
    try:
        job, source, _ = job_for(fixture_transcript, "toolu_fx_01", transport(scorer.url, "live", budget_ms=200))
        answer = bridge(job)
    finally:
        scorer.close()
    assert_failed_open(answer, source, "budget")
    assert answer["requests"][0]["latency_ms"] < 1500  # aborted near the budget, not after the 2 s answer


def test_failopen_non_200(fixture_transcript):
    scorer = Scorer("status500")
    try:
        job, source, _ = job_for(fixture_transcript, "toolu_fx_01", transport(scorer.url))
        answer = bridge(job)
    finally:
        scorer.close()
    assert_failed_open(answer, source, "non_200")
    assert answer["requests"][0]["status"] == 500


@pytest.mark.parametrize("behavior", ["not_json", "no_answers"])
def test_failopen_unparseable(fixture_transcript, behavior):
    scorer = Scorer(behavior)
    try:
        job, source, _ = job_for(fixture_transcript, "toolu_fx_01", transport(scorer.url))
        answer = bridge(job)
    finally:
        scorer.close()
    assert_failed_open(answer, source, "unparseable")


def test_failopen_incomplete_answer(fixture_transcript):
    scorer = Scorer("incomplete")
    try:
        job, source, _ = job_for(fixture_transcript, "toolu_fx_01", transport(scorer.url))
        answer = bridge(job)
    finally:
        scorer.close()
    assert_failed_open(answer, source, "incomplete")


def long_history() -> list[dict]:
    """A synthetic history long enough that the pruner splits it into several segments (one request each, sent at once)."""
    words = " ".join(f"fixture{w % 97:02d}" for w in range(1400))
    return [{"role": "user" if i % 2 == 0 else "assistant", "text": f"segment {i}: {words}", "toolUses": []} for i in range(30)]


def test_failopen_queue_deeper_than_one(fixture_transcript):
    scorer = Scorer("slow503", delay=0.5)
    try:
        job, source, _ = job_for(fixture_transcript, "toolu_fx_01", transport(scorer.url, "replay"), messages=long_history())
        answer = bridge(job)
    finally:
        scorer.close()
    assert_failed_open(answer, source, "queue_depth")
    assert len(answer["requests"]) >= 2
    assert [q.get("error") for q in answer["requests"][1:]] == ["queue_depth"] * (len(answer["requests"]) - 1)
    assert len(scorer.bodies) == 1  # the second request never left the bridge


def test_failopen_queue_control_serialized_requests_do_not_trip(fixture_transcript):
    scorer = Scorer("slow503", delay=0.2)
    try:
        job, source, _ = job_for(fixture_transcript, "toolu_fx_01", transport(scorer.url, "unbudgeted"), messages=long_history())
        answer = bridge(job)
    finally:
        scorer.close()
    assert "queue_depth" not in [t["reason"] for t in answer["trips"]]
    assert answer["fail_open_reason"] == "non_200"  # the 503 still fails it open, one request at a time
    assert scorer.max_in_flight == 1 and len(scorer.bodies) == 1


def test_failopen_harness_rows_record_the_reason(fixture_transcript, tmp_path):
    scorer = Scorer("status500")
    try:
        rows = run_harness(tmp_path, fixture_transcript, scorer.url)
    finally:
        scorer.close()
    reasons = {r["result_id"]: r["fail_open_reason"] for r in rows if r["requests"]}
    # toolu_fx_06's history splits in two, so its second request trips the queue rule before the first one's 500 lands
    assert reasons == {"toolu_fx_01": "non_200", "toolu_fx_04": "non_200", "toolu_fx_06": "queue_depth",
                       "toolu_fx_08": "non_200", "toolu_fx_09": "non_200"}
    assert all(r["pruned"] is False and r["chars_saved"] == 0 for r in rows)
    assert accounting.verdict([r for r in rows if r["set"] == "primary"])["verdict"] == "FAIL"


# ---------------------------------------------------------------- the accounting on the fixture (recorded answers)

EXPECTED = {  # tool_use id: (decision, following calls, next request's whole context)
    "toolu_fx_01": ("kept_all", 6, 23000),
    "toolu_fx_02": ("document", 5, 26000),
    "toolu_fx_03": ("document", 4, 29000),
    "toolu_fx_04": ("kept_all", 3, 32000),
    "toolu_fx_05": ("few_chunks", 2, 35000),
    "toolu_fx_06": ("kept_all", 1, 38000),
    "toolu_fx_07": ("tool_error", 0, 9000),
    "toolu_fx_08": ("kept_all", 3, 12000),
    "toolu_fx_09": ("budget_unfit", 2, 15000),
}


@pytest.mark.parametrize("mode", ["replay", "unbudgeted"])
def test_accounting_fixture_end_to_end(fixture_transcript, tmp_path, mode):
    scorer = Scorer("recorded")
    try:
        rows = by_id(run_harness(tmp_path, fixture_transcript, scorer.url, mode))
    finally:
        scorer.close()
    assert sorted(rows) == sorted(EXPECTED)
    for uid, (decision, following, context) in EXPECTED.items():
        row = rows[uid]
        if uid == "toolu_fx_06" and mode == "replay":
            # its history splits into two segments; the pruner sends both at once and the live queue rule trips
            decision = "fail_open"
            assert (row["fail_open_reason"], row["pruner_decision"]) == ("queue_depth", None)
            assert [q.get("error") for q in row["requests"]] == [None, "queue_depth"]
        assert (row["decision"], row["following_calls"], row["next_context_tokens"]) == (decision, following, context), uid
        assert row["fail_open"] is (decision == "fail_open") and row["pruned"] is False and row["tokens_saved"] == 0.0
    assert len(rows["toolu_fx_06"]["requests"]) == 2
    assert rows["toolu_fx_02"]["document_rule"] == "structured" and rows["toolu_fx_03"]["document_rule"] == "reference"
    assert rows["toolu_fx_06"]["secret"] is True and rows["toolu_fx_01"]["secret"] is False
    assert {rows[u]["set"] for u in ("toolu_fx_03", "toolu_fx_04")} == {"secondary"}
    assert all(s > 0.1 for s in rows["toolu_fx_01"]["scores"])  # the recorded real answers keep every chunk
    verdict = accounting.verdict([r for r in rows.values() if r["set"] == "primary"])
    assert (verdict["verdict"], verdict["pruned"], verdict["net"]) == ("FAIL", 0, 0.0)
    assert verdict["why"] == ["no result was pruned, so net tokens saved = 0"]


def test_accounting_fixture_is_deterministic(fixture_transcript, tmp_path):
    scorer = Scorer("recorded")
    try:
        first = run_harness(tmp_path / "a", fixture_transcript, scorer.url)
        second = run_harness(tmp_path / "b", fixture_transcript, scorer.url)
    finally:
        scorer.close()
    strip = lambda rows: [{k: v for k, v in r.items() if k not in ("latency_ms", "requests", "trips")} for r in rows]  # noqa: E731
    assert strip(first) == strip(second)


def test_accounting_miss_detection_on_the_fixture_lookahead(fixture_transcript):
    path = fixture_transcript
    index = transcript.scan(str(path), path.stat().st_size, TOOLS, 2000, accounting.tokens)
    cand = next(c for c in index.candidates if c.tool_use_id == "toolu_fx_08")
    gen = transcript.windows(str(path), path.stat().st_size, {cand.offset}, accounting.tokens)
    history = set(next(gen).history_tokens)
    gen.close()
    original = make_fixture.pytest_log()
    kept = "\n".join(line for line in original.splitlines() if "module_0547" not in line)
    look = [i.tokens for i in index.items[cand.item_index: cand.item_index + accounting.LOOKAHEAD]]
    calls = [index.items[i].rerun_key for i in index.tool_items[cand.tool_item_index: cand.tool_item_index + accounting.LOOKAHEAD]]
    hits, rerun = accounting.miss(original, kept, history, look, calls, cand.rerun_key)
    assert hits >= 1 and rerun is False  # a later assistant text names module_0547.o, which only the dropped line held
    assert accounting.miss(original, original, history, look, calls, cand.rerun_key) == (0, False)  # nothing dropped
    assert accounting.miss(original, kept, history | {"module_0547", "obj/module_0547.o"}, look, calls, cand.rerun_key)[0] == 0


def test_accounting_rerun_within_twenty_calls(fixture_transcript):
    path = fixture_transcript
    index = transcript.scan(str(path), path.stat().st_size, TOOLS, 2000, accounting.tokens)
    calls_after = {c.tool_use_id: [index.items[i].rerun_key for i in index.tool_items[c.tool_item_index: c.tool_item_index + 20]]
                   for c in index.candidates}
    first = next(c for c in index.candidates if c.tool_use_id == "toolu_fx_01")
    other = next(c for c in index.candidates if c.tool_use_id == "toolu_fx_02")
    assert first.rerun_key in calls_after["toolu_fx_01"]  # toolu_fx_07 runs the same command
    assert other.rerun_key not in calls_after["toolu_fx_02"]


def test_accounting_tokens_saved_and_the_bar():
    assert accounting.tokens_saved(4060, 3) == pytest.approx(3000.0)

    def rows(n, misses, cost, saved=1000.0):
        return [{"pruned": True, "tokens_saved": saved, "miss": i < misses, "miss_cost": cost if i < misses else 0}
                for i in range(n)]

    at_bar = accounting.verdict(rows(20, 1, 5000))
    assert (at_bar["verdict"], at_bar["miss_rate"], at_bar["net"]) == ("PASS", 0.05, 15000.0)
    assert accounting.verdict(rows(20, 2, 10))["verdict"] == "FAIL"  # 10% misses
    assert accounting.verdict(rows(20, 1, 30000))["verdict"] == "FAIL"  # net below zero
    assert accounting.verdict(rows(20, 0, 0, saved=0.0))["verdict"] == "FAIL"  # net exactly zero
    assert accounting.verdict([{"pruned": False}])["why"] == ["no result was pruned, so net tokens saved = 0"]
    assert accounting.verdict(rows(20, 0, 0, saved=float("nan")))["verdict"] == "FAIL"  # NaN never passes
    assert accounting.verdict(rows(20, 0, 0, saved=float("inf")))["verdict"] == "FAIL"


# ---------------------------------------------------------------- the transcript model

def test_transcript_window_is_the_runtime_view(fixture_transcript):
    path, limit = fixture_transcript, fixture_transcript.stat().st_size
    index = transcript.scan(str(path), limit, TOOLS, 2000, accounting.tokens)
    offsets = {c.tool_use_id: c.offset for c in index.candidates}
    views = {s.block["tool_use_id"]: json.loads(json.dumps(s.messages))
             for s in transcript.windows(str(path), limit, {offsets["toolu_fx_06"], offsets["toolu_fx_08"]}, accounting.tokens)}
    before = views["toolu_fx_06"]
    assert before[0] == {"role": "user", "text": "Build the widget-demo fixture and report the failing test names.", "toolUses": []}
    answered = [u for m in before for u in m["toolUses"] if u["tool_use_id"] in {f"toolu_fx_0{i}" for i in range(1, 6)}]
    assert len(answered) == 5 and all("text" in u and "result" in u for u in answered)
    pending = before[-1]["toolUses"][-1]
    assert pending["tool_use_id"] == "toolu_fx_06" and "text" not in pending and "result" not in pending
    assert sum(1 for m in before if m.get("toolResults")) == 5
    after = views["toolu_fx_08"]  # after the compaction: the summary, then only what follows
    assert len(after) == 2 and after[0]["text"].startswith("This session is being continued")
    assert after[1]["toolUses"][0]["tool_use_id"] == "toolu_fx_08"
    assert index.stats["compactions"] == 1 and index.stats["requests"] == 11


def test_fixture_matches_the_real_record_shapes(fixture_transcript):
    """AF-AP-42: the synthetic records carry the key sets and value types captured from the real transcript."""
    real = json.loads((FIXTURES / "record_shapes.json").read_text())
    kinds = set()
    for line in fixture_transcript.read_text().splitlines():
        record = json.loads(line)
        kind = capture_shapes.kind_of(record)
        kinds.add(kind)
        got = capture_shapes.shape(record)
        blocks = record["message"]["content"] if isinstance(record.get("message", {}).get("content"), list) else []
        if kind == "user:tool_result" and blocks[0]["is_error"] is True:
            got = dict(got, toolUseResult="dict")  # the measured variant: an errored Bash result stores its text (a str)
        assert got == real["record"][kind], kind
        if kind in real["message"]:
            assert capture_shapes.shape(record["message"]) == real["message"][kind], kind
        else:
            assert "message" not in record, kind
        for block in blocks:
            assert capture_shapes.shape(block) == real["block"][f"{kind}/{block['type']}"], (kind, block["type"])
        if kind == "assistant":
            assert sorted(k for k in record["message"]["usage"] if k in real["usage_keys"]["assistant"]) == real["usage_keys"]["assistant"]
        if kind == "user:tool_result" and isinstance(record["toolUseResult"], dict) and "stdout" in record["toolUseResult"]:
            fields = {k: v for k, v in capture_shapes.shape(record["toolUseResult"]).items() if not k.startswith("persisted")}
            assert fields == real["bash_tool_use_result"]["Bash"]
    assert kinds == {"user:prompt", "assistant", "user:tool_result", "system:compact_boundary", "user:compact_summary"}


def test_fixture_builder_is_deterministic(tmp_path):
    a = make_fixture.build(tmp_path / "a").read_text().replace(str(tmp_path / "a"), "<DIR>")
    b = make_fixture.build(tmp_path / "b").read_text().replace(str(tmp_path / "b"), "<DIR>")
    assert a == b


def test_stratified_sample_is_deterministic_and_floored():
    cands = [transcript.Candidate(path="/t.jsonl", offset=i, tool_use_id=f"u{i}", tool="Bash",
                                  chars=chars, is_error=False, persisted=False, rerun_key=("Bash", str(i)))
             for i, chars in enumerate([2500] * 60 + [5000] * 30 + [9000] * 6 + [20000] * 2)]
    pick = replay_pruner.stratified(cands, 20, replay_pruner.BAND_EDGES, floor=3)
    assert pick == replay_pruner.stratified(list(reversed(cands)), 20, replay_pruner.BAND_EDGES, floor=3)
    bands = [replay_pruner.band(c.chars, replay_pruner.BAND_EDGES) for c in pick]
    # floor 3 per band (the 16k+ band holds only 2), then the other 9 by largest remainder over spare 57/27/3/0
    assert {b: bands.count(b) for b in set(bands)} == {"2k-4k": 9, "4k-8k": 6, "8k-16k": 3, "16k+": 2}
    assert replay_pruner.stratified(cands, 0, replay_pruner.BAND_EDGES) == sorted(cands, key=lambda c: c.offset)


def test_decision_log_is_0600_and_holds_no_session_text(fixture_transcript, tmp_path):
    decisions = tmp_path / "decisions.jsonl"
    decisions.write_text("")
    os.chmod(decisions, 0o644)  # the negative control: a looser mode the harness must tighten
    rc = replay_pruner.main(["--min-chars", "2000", "--out", str(tmp_path / "out"), "--mode", "plan", "--sample", "0",
                             "--secondary-sample", "10", "--sources", str(fixture_transcript), "--decisions", str(decisions)])
    assert rc == 0
    assert decisions.stat().st_mode & 0o777 == 0o600
    text = decisions.read_text()
    assert len(text.splitlines()) == len(EXPECTED)
    for fragment in ("compiling widget-demo/obj", "FIXTURE_API_KEY", "processed batch_", "render_frame_", "Build the widget-demo"):
        assert fragment not in text


# ---------------------------------------------------------------- the vendored pruner and its one local change

NODE_FLOOR_CHECK = r"""
import { register } from 'node:module';
// src/*.ts imports './X.js'; point those at './X.ts' so Node's type stripping runs the TypeScript source itself
register('data:text/javascript,' + encodeURIComponent(`export async function resolve(s, c, n) {
  if (c.parentURL && c.parentURL.includes('/vendor/jev-pruner/src/') && s.startsWith('./') && s.endsWith('.js')) return n(s.slice(0, -3) + '.ts', c);
  return n(s, c);
}`));
const { exceedsOutputThreshold, MIN_OUTPUT_TOKENS, trimOutput } = await import('%(module)s');
const text = (n) => Array.from({ length: n }, () => 'aaaaaa').join('\n');  // one estimated token per line
const out = { MIN_OUTPUT_TOKENS };
out.defaults = [9999, 10000, 10001].map((n) => exceedsOutputThreshold(text(n)));
out.minTokens0 = exceedsOutputThreshold(text(500), 0);
out.floor0 = exceedsOutputThreshold(text(500), 0, 0);
out.floorNaN = exceedsOutputThreshold(text(500), 0, NaN);
out.floorNeg = exceedsOutputThreshold(text(500), 0, -5);
let asked = 0;
const asker = { async ask() { asked += 1; throw new Error('sentinel: the scorer was asked'); } };
const input = { command: 'make fixture', goal: 'fixture', output: text(9999) };
let decision = null;
const kept = await trimOutput(input, asker, { onDecision: (d) => { decision = d; } });
out.default9999 = { decision, trimmed: kept.trimmed, same: kept.output === input.output, asked };
try { await trimOutput(input, asker, { minTokensFloor: 0 }); out.lowered = 'returned'; } catch (e) { out.lowered = String(e.message); }
out.loweredAsked = asked;
console.log(JSON.stringify(out));
"""


@pytest.mark.parametrize("module", ["dist/output.js", pytest.param("src/output.ts", marks=needs_strip)])
def test_floor_option_default_unchanged_and_lowered_only_when_passed(module):
    """Run on the built dist/ AND on the TypeScript source (type-stripped), so both carry the one local change."""
    proc = subprocess.run(["node", "--input-type=module", "-e", NODE_FLOOR_CHECK % {"module": VENDOR / module}],
                          capture_output=True, text=True, timeout=60)
    assert proc.returncode == 0, proc.stderr
    out = json.loads(proc.stdout.strip().splitlines()[-1])
    assert out["MIN_OUTPUT_TOKENS"] == 10000
    assert out["defaults"] == [False, False, True]  # 9,999 and 10,000 estimated tokens stay under the upstream floor
    assert out["minTokens0"] is False  # without the option the floor stays at 10,000
    assert (out["floor0"], out["floorNaN"], out["floorNeg"]) == (True, False, True)
    assert out["default9999"] == {"decision": "below_threshold", "trimmed": False, "same": True, "asked": 0}
    assert out["lowered"] == "sentinel: the scorer was asked" and out["loweredAsked"] >= 1  # the negative control


def test_provenance_names_the_pin_and_the_license_bytes():
    provenance = (VENDOR / "PROVENANCE.md").read_text()
    assert "47d017c34eab7690b95f075ce6f4839247c5dc0a" in provenance
    assert hashlib.sha256((VENDOR / "LICENSE").read_bytes()).hexdigest() in provenance


def test_vendored_root_is_pinned_and_registered():
    import vendored_manifest as manifest
    lock = manifest.parse_lock(REPO / "upstream.lock.yaml")
    assert lock["github.com/tamaratran/jev-pruner"] == ("47d017c34eab7690b95f075ce6f4839247c5dc0a", "advisory_tooling.jev-pruner")
    _, roots = manifest.parse_provenance(REPO / "sandbox-kit" / "VENDORED-FROM.md")
    root = next(r for r in manifest.VENDORED_ROOTS if r.path == "vendor/jev-pruner/")
    assert roots["vendor/jev-pruner/"] == root.provenance_line
    assert (root.pin, root.pin_source) == ("47d017c34eab7690b95f075ce6f4839247c5dc0a", "upstream.lock.yaml:advisory_tooling.jev-pruner")
    manifest.validate_declared_roots(REPO)
    manifest.validate_pin_agreement(REPO)
    assert "| `vendor/jev-pruner/` |" in (REPO / "sandbox-kit" / "VENDORED-MANIFEST.md").read_text()


def test_bridge_mirrors_the_hooks_private_constants():
    """The three constants are module-private in the hook, so the vendored source is the only place to read them."""
    source = (VENDOR / "hooks" / "fast-jev-output.ts").read_text()
    probe = "const b = await import('%s'); console.log(JSON.stringify(b.HOOK));" % replay_pruner.BRIDGE
    proc = subprocess.run(["node", "--input-type=module", "-e", probe], capture_output=True, text=True, timeout=60, cwd=REPO)
    assert proc.returncode == 0, proc.stderr
    hook = json.loads(proc.stdout.strip().splitlines()[-1])
    assert re.search(r"^const ARCHIVE_DIR = '%s';$" % re.escape(hook["archiveDir"]), source, re.M)
    assert re.search(r"^const DEFAULT_MAX_SCORING_REQUESTS = %d;$" % hook["defaultMaxScoringRequests"], source, re.M)
    assert re.search(r"^const VISIBLE_CHARS_PER_REQUEST = %d;$" % hook["visibleCharsPerRequest"], source, re.M)


HOOK_PARITY = r"""
import { register } from 'node:module';
register('data:text/javascript,' + encodeURIComponent(`export async function resolve(s, c, n) {
  if (c.parentURL && c.parentURL.includes('/vendor/jev-pruner/hooks/') && s.startsWith('../src/') && s.endsWith('.js')) return n(s.replace('../src/', '../dist/'), c);
  return n(s, c);
}`));
const hook = await import('%(hook)s');
const bridge = await import('%(bridge)s');
const cases = %(cases)s;
console.log(JSON.stringify({
  config: hook.resolveHookConfig({}),
  mirrored: bridge.HOOK,
  goals: cases.map((m) => [hook.goalFromMessages(m), bridge.goalFromMessages(m)]),
}));
"""


@needs_strip
def test_bridge_glue_equals_the_vendored_hook(fixture_transcript):
    """The bridge's mirrored defaults and goal equal the vendored hook module's own (loaded from its TypeScript)."""
    path, limit = fixture_transcript, fixture_transcript.stat().st_size
    index = transcript.scan(str(path), limit, TOOLS, 2000, accounting.tokens)
    cases = [json.loads(json.dumps(s.messages)) for s in transcript.windows(str(path), limit, {c.offset for c in index.candidates}, accounting.tokens)]
    cases += [[], [{"role": "user", "text": "  ", "toolUses": []}],
              [{"role": "user", "text": f"prompt {i} " + "x" * 600, "toolUses": []} for i in range(5)]]
    script = HOOK_PARITY % {"hook": VENDOR / "hooks" / "fast-jev-output.ts", "bridge": replay_pruner.BRIDGE, "cases": json.dumps(cases)}
    proc = subprocess.run(["node", "--input-type=module"], input=script, capture_output=True, text=True, timeout=60, cwd=REPO)
    assert proc.returncode == 0, proc.stderr
    out = json.loads(proc.stdout.strip().splitlines()[-1])
    config, mirrored = out["config"], out["mirrored"]
    for key in ("persistedMaxChars", "chunkLines", "keepThreshold", "maxStateTokens", "model"):
        assert mirrored[key] == config[key], key
    assert config["minTokens"] == 10000  # the hook's own floor; the bridge lowers it only through the local option
    assert len(out["goals"]) == len(cases) >= 12
    assert all(ours == theirs for theirs, ours in out["goals"])
    assert any(len(theirs) > 0 for theirs, _ in out["goals"])  # the comparison ran on real goals, not only empty ones


@pytest.mark.parametrize("flag,value", [("--budget-ms", "nan"), ("--budget-ms", "0"), ("--budget-ms", "5e9"),
                                        ("--request-timeout-ms", "0.5"), ("--request-timeout-ms", "inf")])
def test_cli_refuses_a_delay_abortsignal_cannot_take(tmp_path, flag, value):
    """AbortSignal.timeout throws RangeError on a non-integer, negative or over-2^32 delay (Node 22, measured), which
    would read as a silent transport fail-open; the CLI refuses such values before any work."""
    with pytest.raises(SystemExit) as refused:
        replay_pruner.main(["--min-chars", "2000", "--out", str(tmp_path), flag, value])
    assert refused.value.code == 2
    assert not (tmp_path / "summary.json").exists()


def test_plan_all_lifts_the_request_cap_and_counts_history_segments(fixture_transcript):
    """plan-all sends nothing and lists every request the pruner would need; plan stops at the pruner's own cap."""
    history = long_history() * 8  # about 16 history segments at the pruner's 25,000-token state budget
    plans = {}
    for mode in ("plan", "plan-all"):
        job, source, _ = job_for(fixture_transcript, "toolu_fx_01", transport(closed_port_url(), mode), messages=history)
        plans[mode] = bridge(job)
    capped, full = plans["plan"], plans["plan-all"]
    assert capped["decision"] == full["decision"] == "plan" and capped["trips"] == full["trips"] == []
    assert len(capped["requests"]) == capped["request_limit"] == 12  # the hook's own cap: 1 + 11
    segments = {q["history_key"] for q in full["requests"]}
    assert len(full["requests"]) == len(segments) > 12  # one request per segment; more than the cap allows
    every_chunk = {c for q in full["requests"] for c in q["chunk_ids"]}
    assert all(set(q["chunk_ids"]) == every_chunk for q in full["requests"])
    assert not any(q["sent"] for q in capped["requests"] + full["requests"])  # nothing reached the (closed) port
