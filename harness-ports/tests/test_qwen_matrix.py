#!/usr/bin/env python3
"""Deterministic contracts for qwen_matrix.py; no GPU, network, or real server state."""
from __future__ import annotations

import contextlib
import hashlib
import importlib.util
import json
import pathlib
import tempfile
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

ROOT = pathlib.Path(__file__).resolve().parents[2]
TOOL = ROOT / "harness-ports" / "bin" / "qwen_matrix.py"
SPEC = importlib.util.spec_from_file_location("qwen_matrix", TOOL)
assert SPEC is not None and SPEC.loader is not None
QM = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(QM)

METRICS = """# HELP llamacpp:prompt_tokens_total Number of prompt tokens processed.
# TYPE llamacpp:prompt_tokens_total counter
llamacpp:prompt_tokens_total 100
# HELP llamacpp:prompt_seconds_total Prompt process time
# TYPE llamacpp:prompt_seconds_total counter
llamacpp:prompt_seconds_total 4
# HELP llamacpp:tokens_predicted_total Number of generation tokens processed.
# TYPE llamacpp:tokens_predicted_total counter
llamacpp:tokens_predicted_total 40
# HELP llamacpp:tokens_predicted_seconds_total Predict process time
# TYPE llamacpp:tokens_predicted_seconds_total counter
llamacpp:tokens_predicted_seconds_total 2
# HELP llamacpp:n_busy_slots_per_decode Average number of busy slots per llama_decode() call
# TYPE llamacpp:n_busy_slots_per_decode gauge
llamacpp:n_busy_slots_per_decode 1.5
"""

EXPORT = """# Hermes lane session synthetic

- model: test

## user @ 00:00:01

SYSTEM-A system text

## assistant @ 00:00:02

ASSISTANT-A

## tool result (terminal) @ 00:00:03 — 9 chars (body not exported)

## user @ 00:00:04

USER-B

## assistant @ 00:00:05

ASSISTANT-B
"""


class FixtureServer(BaseHTTPRequestHandler):
    bodies: list[dict] = []
    concurrent = 0
    peak = 0
    metrics_reads = 0
    lock = threading.Lock()
    barrier: threading.Barrier | None = None

    def log_message(self, format, *args):
        del format, args
        return

    def _json(self, value, status=200):
        data = json.dumps(value).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        if self.path == "/metrics":
            if self.headers.get("Authorization") != "Bearer fixture-secret":
                self._json({"error": "unauthorized"}, 401)
                return
            step = (type(self).metrics_reads + 1) // 2
            text = (METRICS.replace("prompt_tokens_total 100", f"prompt_tokens_total {100 + 120 * step}")
                    .replace("prompt_seconds_total 4", f"prompt_seconds_total {4 + 3 * step}")
                    .replace("tokens_predicted_total 40", f"tokens_predicted_total {40 + 60 * step}")
                    .replace("tokens_predicted_seconds_total 2", f"tokens_predicted_seconds_total {2 + 2 * step}"))
            type(self).metrics_reads += 1
            data = text.encode()
            self.send_response(200)
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)
        elif self.path == "/props":
            if self.headers.get("Authorization") != "Bearer fixture-secret":
                self._json({"error": "unauthorized"}, 401)
                return
            self._json({"model_alias": "fixture", "total_slots": 2,
                        "default_generation_settings": {"n_ctx": 200000}, "build_info": "fixture-build"})
        elif self.path == "/health":
            self._json({"status": "ok"})
        else:
            self._json({"error": "not found"}, 404)

    def do_POST(self):
        if self.headers.get("Authorization") != "Bearer fixture-secret":
            self._json({"error": "unauthorized"}, 401)
            return
        length = int(self.headers.get("Content-Length", "0"))
        body = json.loads(self.rfile.read(length))
        type(self).bodies.append(body)
        if self.path == "/tokenize":
            # A deterministic stand-in for llama.cpp's tokenizer: one token per word.
            self._json({"tokens": list(range(len(body["content"].split())))})
            return
        if self.path == "/apply-template":
            rendered = "".join(
                f"<|im_start|>{message['role']}\n{message['content']}<|im_end|>\n"
                for message in body["messages"]
            )
            self._json({"prompt": rendered})
            return
        if self.path == "/v1/chat/completions":
            with type(self).lock:
                type(self).concurrent += 1
                type(self).peak = max(type(self).peak, type(self).concurrent)
            barrier = type(self).barrier
            if barrier is not None:
                barrier.wait(timeout=5)
            self._json({"model": "fixture", "choices": [{"message": {"content": "ok"}}],
                        "usage": {"prompt_tokens": 12, "completion_tokens": 3},
                        "timings": {"prompt_n": 12, "prompt_ms": 6, "predicted_n": 3,
                                    "predicted_ms": 2, "predicted_per_second": 1500}})
            with type(self).lock:
                type(self).concurrent -= 1
            return
        self._json({"error": "not found"}, 404)


@contextlib.contextmanager
def server():
    FixtureServer.bodies = []
    FixtureServer.concurrent = 0
    FixtureServer.peak = 0
    FixtureServer.metrics_reads = 0
    FixtureServer.barrier = None
    httpd = ThreadingHTTPServer(("127.0.0.1", 0), FixtureServer)
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    try:
        yield f"http://127.0.0.1:{httpd.server_port}"
    finally:
        httpd.shutdown()
        thread.join(timeout=5)
        httpd.server_close()


def test_metrics_parser():
    parsed = QM.parse_metrics(METRICS)
    assert parsed == {
        "llamacpp:prompt_tokens_total": 100.0,
        "llamacpp:prompt_seconds_total": 4.0,
        "llamacpp:tokens_predicted_total": 40.0,
        "llamacpp:tokens_predicted_seconds_total": 2.0,
        "llamacpp:n_busy_slots_per_decode": 1.5,
    }
    try:
        QM.parse_metrics(METRICS.replace("llamacpp:prompt_seconds_total 4\n", ""))
    except QM.MatrixError as exc:
        assert str(exc) == "metrics missing required counter: llamacpp:prompt_seconds_total"
    else:
        raise AssertionError("missing metric did not fail")


def test_aggregate():
    before = QM.parse_metrics(METRICS)
    after_text = (METRICS.replace("prompt_tokens_total 100", "prompt_tokens_total 220")
                  .replace("prompt_seconds_total 4", "prompt_seconds_total 7")
                  .replace("tokens_predicted_total 40", "tokens_predicted_total 100")
                  .replace("tokens_predicted_seconds_total 2", "tokens_predicted_seconds_total 4"))
    result = QM.aggregate_round([
        {"wall_s": 1.0, "prompt_tokens": 55, "completion_tokens": 25,
         "timings": {"predicted_per_second": 25.0}},
        {"wall_s": 2.0, "prompt_tokens": 65, "completion_tokens": 35, "timings": {}},
    ], before, QM.parse_metrics(after_text), 3, 2.0)
    assert result["decode_tps"] == 30.0
    assert result["prompt_tps"] == 40.0
    assert result["prompt_seconds"] == 3.0
    assert result["completion_seconds"] == 2.0
    assert result["re_prefill_count"] == 3
    assert result["busy_slots_per_decode"] == 1.5
    assert result["requests"] == 2


def test_export_and_live_fixture():
    with tempfile.TemporaryDirectory() as tmp, server() as base:
        root = pathlib.Path(tmp)
        export = root / "session.md"
        export.write_text(EXPORT)
        out = root / "prompts"
        key = root / "api-key"
        key.write_text("fixture-secret\n")
        secret = QM.read_key(key)
        try:
            QM.request(base, "/props", None)
        except QM.MatrixError as exc:
            assert str(exc) == "/props returned HTTP 401"
        else:
            raise AssertionError("missing bearer key did not fail")
        # The first assistant boundary crosses the target; later turns are excluded.
        manifests = QM.build_corpus(export, 4, out, base, secret)
        assert [p.name for p in manifests] == ["prompt-001.json"]
        payload = json.loads((out / "prompt-001.json").read_text())
        assert [m["role"] for m in payload["messages"]] == ["system", "assistant"]
        expected_rendered = "".join(
            f"<|im_start|>{m['role']}\n{m['content']}<|im_end|>\n" for m in payload["messages"]
        )
        assert payload["token_count"] == len(expected_rendered.split())
        assert any(body.get("add_generation_prompt") is True for body in FixtureServer.bodies)
        assert payload["messages"][0]["content"] == "SYSTEM-A system text"
        assert "USER-B" not in json.dumps(payload)

        secret_export = root / "secret-session.md"
        secret_export.write_text(EXPORT.replace(
            "SYSTEM-A system text",
            "Authorization: Bearer bearer-token-12345 api-key=apikey-secret-12345 sk-abcdefghijklmnop",
        ))
        secret_out = root / "secret-prompts"
        secret_manifest = QM.build_corpus(secret_export, 4, secret_out, base, secret)[0]
        secret_payload = secret_manifest.read_text()
        for literal in ("bearer-token-12345", "apikey-secret-12345", "sk-abcdefghijklmnop"):
            assert literal not in secret_payload
        assert "Bearer <redacted>" in secret_payload
        assert "api-key=<redacted>" in secret_payload
        assert "sk-<redacted>" in secret_payload

        # A larger but reachable target emits the first target-sized cumulative prompt and preserves tool markers.
        manifests = QM.build_corpus(export, 15, out, base, secret)
        assert [p.name for p in manifests] == ["prompt-001.json"]
        second = json.loads(manifests[0].read_text())
        assert second["messages"][2]["role"] == "user"
        assert "tool result (terminal)" in second["messages"][2]["content"]
        assert second["messages"][2]["content"].startswith("<tool_response>")
        assert second["messages"][-2:] == [
            {"role": "user", "content": "USER-B"},
            {"role": "assistant", "content": "ASSISTANT-B"},
        ]
        try:
            QM.build_corpus(export, 99, out, base, secret)
        except QM.MatrixError as exc:
            message = str(exc)
            assert message.startswith("session export exhausted at ")
            assert message.endswith(" before target 99")
            assert not list(out.glob("prompt-*.json")), "failed corpus left target-mislabeled prompts"
        else:
            raise AssertionError("undersized export was mislabeled as target-sized")

        rotation_log = root / "rotation.log"
        rotation_log.write_text("old line padded beyond the replacement offset\n")
        old_position = QM._log_position(rotation_log)
        replacement = root / "rotation.new"
        replacement.write_text("forcing full prompt re-processing\n" + "x" * old_position[0])
        replacement.replace(rotation_log)
        try:
            QM._count_reprefills(rotation_log, old_position)
        except QM.MatrixError as exc:
            assert str(exc) == f"server log rotated during round: {rotation_log}"
        else:
            raise AssertionError("same-size-or-larger rotated log was read from a stale offset")

        prompt2 = root / "run-prompts"
        prompt2.mkdir()
        for index, marker in enumerate(("P0", "P1"), 1):
            (prompt2 / f"prompt-{index:03d}.json").write_text(json.dumps(
                {"messages": [{"role": "user", "content": marker}], "token_count": 1}))
        log = root / "server.log"
        log.write_text("old forcing full prompt re-processing\n")
        FixtureServer.barrier = threading.Barrier(2)
        result = QM.run_load(prompt2, 2, 4, 2, root / "result.json", base, secret, log,
                             cell={"name": "T", "argv_sha256": "a", "unit_sha256": "b"})
        assert FixtureServer.peak == 2, "requests were not concurrent"
        posted = [body["messages"][0]["content"] for body in FixtureServer.bodies
                  if "messages" in body and "max_tokens" in body]
        assert [set(posted[:2]), set(posted[2:])] == [{"P0", "P1"}, {"P0", "P1"}], posted
        assert [r["prompt_indices"] for r in result["rounds"]] == [[0, 1], [1, 0]]
        assert result["rounds"][0]["aggregate"]["requests"] == 2
        assert result["cell"]["props"]["model_alias"] == "fixture"
        assert result["cell"]["props"]["default_generation_settings"]["n_ctx"] == 200000
        assert json.loads((root / "result.json").read_text()) == result


def cell_unit_text(name):
    del name
    return b"[Service]\nExecStart=fake --cache-ram 8192\n"


def cell_run_id(name):
    return hashlib.sha256(f"run:{name}".encode()).hexdigest()


def cell_record(name, **summary_overrides):
    argv_text = f"fake-server --cell {name}\n"
    unit_text = cell_unit_text(name)
    run_id = cell_run_id(name)
    summary = {"requests": 1, "decode_tps": 10, "prompt_tps": 20,
               "re_prefill_count": 4, "busy_slots_per_decode": 1}
    summary.update(summary_overrides)
    return {
        "cell": {"name": name, "argv_text": argv_text,
                 "argv_sha256": hashlib.sha256(argv_text.encode()).hexdigest(),
                 "unit_sha256": hashlib.sha256(unit_text).hexdigest(),
                 "run_id": run_id},
        "summary": summary,
        "vram_peak_mib": 100,
    }


def test_table():
    cells = [
        cell_record("A"),
        cell_record("D", decode_tps=16, prompt_tps=19, re_prefill_count=3,
                    busy_slots_per_decode=2, requests=2),
        cell_record("B", decode_tps=9, prompt_tps=21, re_prefill_count=2),
    ]
    text = QM.render_table(cells)
    assert "| A | 10.000 | 20.000 | 1.000 | 4 | 100 |" in text
    assert "D: aggregate decode >= 1.5x A: YES (1.600x)" in text
    assert "D: re-prefills < A: YES (3 < 4)" in text
    assert "B: aggregate decode >= 1.5x A: NO (0.900x)" in text
    try:
        QM.render_table([{**cells[0], "summary": {**cells[0]["summary"], "decode_tps": float("nan")}}])
    except QM.MatrixError as exc:
        assert str(exc) == "A decode_tps must be finite and non-negative: nan"
    else:
        raise AssertionError("NaN table value did not fail closed")

    for bad_requests in (0, -1, 1.5, True, "1"):
        try:
            QM.render_table([cell_record("A", requests=bad_requests)])
        except QM.MatrixError as exc:
            assert str(exc) == f"A requests must be a positive integer: {bad_requests!r}"
        else:
            raise AssertionError(f"invalid request count was accepted: {bad_requests!r}")

    with tempfile.TemporaryDirectory() as tmp:
        cell_dir = pathlib.Path(tmp) / "A"
        cell_dir.mkdir()
        result = cell_dir / "result.json"
        unit_text = cell_unit_text("A")
        run_id = cell_run_id("A")
        result.write_text(json.dumps(cell_record("A")))
        (cell_dir / "unit-text").write_bytes(unit_text)

        try:
            QM.render_table([QM._load_cell(cell_dir)])
        except QM.MatrixError as exc:
            assert str(exc) == f"cell completion record unreadable: {cell_dir / 'run-complete'}"
        else:
            raise AssertionError("cell without completion record rendered")

        (cell_dir / "run-error").write_text("load generator failed\n")
        try:
            QM.render_table([QM._load_cell(cell_dir)])
        except QM.MatrixError as exc:
            assert str(exc) == f"cell run has error state: {cell_dir / 'run-error'}"
        else:
            raise AssertionError("cell with run-error rendered")
        (cell_dir / "run-error").unlink()

        (cell_dir / "run-complete").write_text(run_id + "\n")
        assert QM._load_cell(cell_dir) == cell_record("A")
        assert "| A | 10.000 | 20.000 | 1.000 | 4 | 100 |" in QM.render_table(
            [QM._load_cell(cell_dir)]
        )

        result_path_load = QM._load_cell(result)
        assert result_path_load == cell_record("A")

        (cell_dir / "run-complete").write_text("f" * 64 + "\n")
        try:
            QM._load_cell(cell_dir)
        except QM.MatrixError as exc:
            assert str(exc) == f"cell completion record does not match run_id: {cell_dir / 'run-complete'}"
        else:
            raise AssertionError("mismatched completion record was accepted")
        (cell_dir / "run-complete").write_text(run_id + "\n")

        mismatch = cell_record("A")
        mismatch["cell"]["argv_sha256"] = "0" * 64
        result.write_text(json.dumps(mismatch))
        try:
            QM._load_cell(cell_dir)
        except QM.MatrixError as exc:
            assert str(exc) == f"cell result argv_sha256 does not match argv_text: {result}"
        else:
            raise AssertionError("mismatched argv identity was accepted")

        malformed_unit = cell_record("A")
        malformed_unit["cell"]["unit_sha256"] = "NOT-A-SHA"
        result.write_text(json.dumps(malformed_unit))
        try:
            QM._load_cell(cell_dir)
        except QM.MatrixError as exc:
            assert str(exc) == f"cell result unit_sha256 is not lowercase sha256: {result}"
        else:
            raise AssertionError("malformed unit identity was accepted")

        mismatched_unit = cell_record("A")
        mismatched_unit["cell"]["unit_sha256"] = "b" * 64
        result.write_text(json.dumps(mismatched_unit))
        try:
            QM._load_cell(cell_dir)
        except QM.MatrixError as exc:
            assert str(exc) == f"cell result unit_sha256 does not match unit-text: {result}"
        else:
            raise AssertionError("mismatched unit identity was accepted")

        result.write_text(json.dumps(cell_record("A")))
        (cell_dir / "unit-text").write_bytes(unit_text + b"tampered\n")
        try:
            QM._load_cell(cell_dir)
        except QM.MatrixError as exc:
            assert str(exc) == f"cell result unit_sha256 does not match unit-text: {result}"
        else:
            raise AssertionError("tampered persisted unit text was accepted")


def main():
    tests = [test_metrics_parser, test_aggregate, test_export_and_live_fixture, test_table]
    for test in tests:
        test()
    print(f"test_qwen_matrix: {len(tests)} tests passed")


if __name__ == "__main__":
    main()
