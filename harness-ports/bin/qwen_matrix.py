#!/usr/bin/env python3
"""Build and replay lane-shaped prompts for the Qwen L1 concurrency matrix."""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import math
import os
import re
import sys
import time
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Any

DEFAULT_BASE_URL = "http://127.0.0.1:8080"
DEFAULT_KEY_FILE = Path.home() / ".config" / "qwen-builder" / "api-key"
DEFAULT_LOG = Path.home() / "qwen-builder" / "logs" / "server.log"
REQUIRED_METRICS = (
    "llamacpp:prompt_tokens_total",
    "llamacpp:tokens_predicted_total",
    "llamacpp:prompt_seconds_total",
    "llamacpp:tokens_predicted_seconds_total",
    "llamacpp:n_busy_slots_per_decode",
)
HEADING = re.compile(r"^## (user|assistant|tool result \(([^)]+)\)) @ [^\n]+(?: → tools: [^\n]+)?\n\n", re.MULTILINE)


class MatrixError(RuntimeError):
    """A named, user-actionable matrix input or server failure."""


def _finite_nonnegative(value: Any, name: str) -> float:
    try:
        number = float(value)
    except (TypeError, ValueError) as exc:
        raise MatrixError(f"{name} is not numeric: {value!r}") from exc
    if not math.isfinite(number) or number < 0:
        raise MatrixError(f"{name} must be finite and non-negative: {value!r}")
    return number


def read_key(path: Path | None) -> str | None:
    if path is None:
        return None
    try:
        key = path.read_text().strip()
    except OSError as exc:
        raise MatrixError(f"API key file unreadable: {path}: {exc.strerror}") from exc
    if not key:
        raise MatrixError(f"API key file is empty: {path}")
    return key


def request(base_url: str, path: str, key: str | None, body: dict | None = None,
            timeout: float = 180.0) -> Any:
    url = f"{base_url.rstrip('/')}{path}"
    headers = {"Accept": "application/json"}
    if key:
        headers["Authorization"] = f"Bearer {key}"
    data = None
    if body is not None:
        data = json.dumps(body, separators=(",", ":")).encode()
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(url, data=data, headers=headers,
                                 method="POST" if body is not None else "GET")
    try:
        with urllib.request.urlopen(req, timeout=timeout) as response:
            raw = response.read()
    except urllib.error.HTTPError as exc:
        # Never include response bodies: a server error may echo credential-bearing input.
        raise MatrixError(f"{path} returned HTTP {exc.code}") from exc
    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        raise MatrixError(f"{path} request failed: {exc}") from exc
    if path == "/metrics":
        return raw.decode("utf-8", errors="replace")
    try:
        return json.loads(raw)
    except json.JSONDecodeError as exc:
        raise MatrixError(f"{path} returned invalid JSON") from exc


def tokenize(messages: list[dict[str, str]], base_url: str, key: str | None) -> int:
    # Ask llama.cpp to apply its live chat template, then count the exact rendered prompt. This
    # avoids maintaining a second template and keeps server defaults in the measured contract.
    templated = request(base_url, "/apply-template", key,
                        {"messages": messages, "add_generation_prompt": True}, timeout=60)
    prompt = templated.get("prompt") if isinstance(templated, dict) else None
    if not isinstance(prompt, str):
        raise MatrixError("/apply-template response missing prompt string")
    data = request(base_url, "/tokenize", key, {"content": prompt}, timeout=60)
    tokens = data.get("tokens") if isinstance(data, dict) else None
    if not isinstance(tokens, list):
        raise MatrixError("/tokenize response missing tokens list")
    return len(tokens)


def parse_export(text: str) -> list[dict[str, str]]:
    """Parse the exporter-owned heading grammar; metadata before the first turn is ignored."""
    matches = list(HEADING.finditer(text))
    if not matches:
        raise MatrixError("session export contains no user/assistant/tool turns")
    messages: list[dict[str, str]] = []
    for index, match in enumerate(matches):
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        content = text[match.end():end].strip()
        heading = match.group(1)
        if heading == "user":
            role = "system" if not messages else "user"
        elif heading == "assistant":
            role = "assistant"
        else:
            role = "user"
            content = f"<tool_response>\ntool result ({match.group(2)}): {content}\n</tool_response>"
        if content:
            messages.append({"role": role, "content": content})
    if not messages or messages[0]["role"] != "system":
        raise MatrixError("session export does not start with a non-empty user/system prompt")
    return messages


def _scrub_messages(messages: list[dict[str, str]]) -> list[dict[str, str]]:
    exporter = Path(__file__).resolve().parents[2] / "scripts" / "transcript_export.py"
    try:
        spec = importlib.util.spec_from_file_location("qwen_matrix_transcript_export", exporter)
        if spec is None or spec.loader is None:
            raise ImportError("no module loader")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        scrub = module.scrub
    except (ImportError, OSError, AttributeError) as exc:
        raise MatrixError(f"transcript scrubber unavailable: {exporter}: {exc}") from exc
    return [{**message, "content": scrub(message["content"])} for message in messages]


def _write_prompt(path: Path, messages: list[dict[str, str]], token_count: int) -> None:
    path.write_text(json.dumps({"messages": messages, "token_count": token_count},
                               indent=2, sort_keys=True) + "\n")


def build_corpus(source: Path, target_tokens: int, out_dir: Path, base_url: str,
                 key: str | None) -> list[Path]:
    if target_tokens <= 0:
        raise MatrixError("target-tokens must be a positive integer")
    try:
        messages = _scrub_messages(parse_export(source.read_text()))
    except OSError as exc:
        raise MatrixError(f"session export unreadable: {source}: {exc.strerror}") from exc
    out_dir.mkdir(parents=True, exist_ok=True)
    for old in out_dir.glob("prompt-*.json"):
        old.unlink()

    # Replay stops at a USER/TOOL boundary, where the model must GENERATE the next assistant turn — a
    # real decode. A prefix ending at an ASSISTANT turn instead asks the model to speak after a complete
    # turn: greedy decode emits end-of-turn at once (1 token, predicted_seconds 0) and the round guard
    # rejects the empty decode (AF-AP-90). Tokenize independently because llama.cpp's /tokenize accepts
    # one rendered prompt, not an incremental state.
    candidates: list[tuple[list[dict[str, str]], int]] = []
    prefix: list[dict[str, str]] = []
    for message in messages:
        prefix.append(message)
        if message["role"] in {"user", "tool"}:
            candidates.append((list(prefix), 0))
    if not candidates:
        raise MatrixError("session export yielded no user/tool boundary for a generation prompt")

    counts: dict[int, int] = {}

    def count_candidate(index: int) -> tuple[int, int]:
        return index, tokenize(candidates[index][0], base_url, key)

    workers = min(4, len(candidates))
    with ThreadPoolExecutor(max_workers=workers) as pool:
        for index, count in pool.map(count_candidate, range(len(candidates))):
            counts[index] = count

    chosen: tuple[list[dict[str, str]], int] | None = None
    for index, (prompt_messages, _) in enumerate(candidates):
        count = counts[index]
        if count >= target_tokens:
            chosen = (prompt_messages, count)
            break
    last_count = counts[len(candidates) - 1]
    if chosen is None:
        raise MatrixError(
            f"session export exhausted at {last_count} tokens before target {target_tokens}"
        )
    path = out_dir / "prompt-001.json"
    _write_prompt(path, chosen[0], chosen[1])
    return [path]


def parse_metrics(text: str) -> dict[str, float]:
    metrics: dict[str, float] = {}
    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        fields = line.split()
        if len(fields) < 2:
            continue
        name = fields[0]
        if name not in REQUIRED_METRICS:
            continue
        metrics[name] = _finite_nonnegative(fields[-1], f"metric {name}")
    for name in REQUIRED_METRICS:
        if name not in metrics:
            raise MatrixError(f"metrics missing required counter: {name}")
    return metrics


def _metric_delta(before: dict[str, float], after: dict[str, float], name: str) -> float:
    delta = after[name] - before[name]
    if not math.isfinite(delta) or delta < 0:
        raise MatrixError(f"metrics counter moved backwards or became unusable: {name}")
    return delta


def aggregate_round(requests: list[dict[str, Any]], before: dict[str, float],
                    after: dict[str, float], re_prefills: int, wall_s: float) -> dict[str, Any]:
    if not requests:
        raise MatrixError("round completed without requests")
    wall_s = _finite_nonnegative(wall_s, "round wall time")
    if wall_s <= 0:
        raise MatrixError("round wall time must be positive")
    prompt_tokens = _metric_delta(before, after, "llamacpp:prompt_tokens_total")
    prompt_seconds = _metric_delta(before, after, "llamacpp:prompt_seconds_total")
    completion_tokens = _metric_delta(before, after, "llamacpp:tokens_predicted_total")
    completion_seconds = _metric_delta(before, after, "llamacpp:tokens_predicted_seconds_total")
    if prompt_seconds <= 0:
        raise MatrixError("metrics delta prompt seconds must be positive")
    if completion_seconds <= 0:
        raise MatrixError("metrics delta predicted seconds must be positive")
    return {
        "requests": len(requests),
        "wall_s": wall_s,
        "prompt_tokens": prompt_tokens,
        "prompt_seconds": prompt_seconds,
        "completion_tokens": completion_tokens,
        "completion_seconds": completion_seconds,
        "prompt_tps": prompt_tokens / prompt_seconds,
        "decode_tps": completion_tokens / completion_seconds,
        "busy_slots_per_decode": after["llamacpp:n_busy_slots_per_decode"],
        "re_prefill_count": int(re_prefills),
    }


def _read_prompt(path: Path) -> dict[str, Any]:
    try:
        prompt = json.loads(path.read_text())
    except (OSError, json.JSONDecodeError) as exc:
        raise MatrixError(f"prompt is unreadable JSON: {path}") from exc
    messages = prompt.get("messages") if isinstance(prompt, dict) else None
    if not isinstance(messages, list) or not messages:
        raise MatrixError(f"prompt has no messages list: {path}")
    for index, message in enumerate(messages):
        valid = (
            isinstance(message, dict)
            and message.get("role") in {"system", "user", "assistant", "tool"}
            and isinstance(message.get("content"), str)
        )
        if not valid:
            raise MatrixError(f"prompt message {index} has invalid OpenAI chat shape: {path}")
        if message["role"] == "tool" and not isinstance(message.get("tool_call_id"), str):
            message = dict(message)
            message["role"] = "user"
            message["content"] = f"<tool_response>\n{message['content']}\n</tool_response>"
            messages[index] = message
    return prompt


def _log_position(path: Path) -> tuple[int, int | None, int | None]:
    try:
        stat = path.stat()
        return stat.st_size, stat.st_dev, stat.st_ino
    except FileNotFoundError:
        return 0, None, None
    except OSError as exc:
        raise MatrixError(f"server log unreadable: {path}: {exc.strerror}") from exc


def _count_reprefills(path: Path, position: tuple[int, int | None, int | None]) -> int:
    offset, device, inode = position
    try:
        with path.open("rb") as stream:
            stat = os.fstat(stream.fileno())
            if device is None or inode is None or (stat.st_dev, stat.st_ino) != (device, inode):
                raise MatrixError(f"server log rotated during round: {path}")
            if stat.st_size < offset:
                raise MatrixError(f"server log truncated during round: {path}")
            stream.seek(offset)
            return stream.read().count(b"forcing full prompt re-processing")
    except FileNotFoundError:
        if device is None and inode is None:
            return 0
        raise MatrixError(f"server log disappeared during round: {path}") from None
    except OSError as exc:
        raise MatrixError(f"server log unreadable: {path}: {exc.strerror}") from exc


def _completion(base_url: str, key: str | None, prompt: dict[str, Any], max_tokens: int) -> dict[str, Any]:
    body = {"model": prompt.get("model", "qwen3.8-27b-local"), "messages": prompt["messages"],
            "max_tokens": max_tokens, "stream": False, "temperature": 0}
    started = time.monotonic()
    result = request(base_url, "/v1/chat/completions", key, body, timeout=600)
    wall_s = time.monotonic() - started
    if not isinstance(result, dict):
        raise MatrixError("chat completion response is not an object")
    usage = result.get("usage")
    if not isinstance(usage, dict):
        raise MatrixError("chat completion response missing usage")
    prompt_tokens = usage.get("prompt_tokens")
    completion_tokens = usage.get("completion_tokens")
    _finite_nonnegative(prompt_tokens, "usage.prompt_tokens")
    _finite_nonnegative(completion_tokens, "usage.completion_tokens")
    return {"wall_s": wall_s, "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens, "timings": result.get("timings") or {}}


def props_subset(props: Any) -> dict[str, Any]:
    if not isinstance(props, dict):
        raise MatrixError("/props response is not an object")
    defaults = props.get("default_generation_settings")
    if not isinstance(defaults, dict):
        raise MatrixError("/props missing default_generation_settings")
    n_ctx = defaults.get("n_ctx")
    if n_ctx is None and isinstance(defaults.get("params"), dict):
        n_ctx = defaults["params"].get("n_ctx")
    fields = {
        "model_alias": props.get("model_alias"),
        "total_slots": props.get("total_slots"),
        "default_generation_settings": {"n_ctx": n_ctx},
        "build_info": props.get("build_info"),
    }
    if any(value is None for value in (fields["model_alias"], fields["total_slots"], n_ctx,
                                       fields["build_info"])):
        raise MatrixError("/props missing required cell identity field")
    return fields


def _summary(rounds: list[dict[str, Any]]) -> dict[str, Any]:
    aggregates = [entry["aggregate"] for entry in rounds]
    total_prompt_tokens = sum(item["prompt_tokens"] for item in aggregates)
    total_prompt_seconds = sum(item["prompt_seconds"] for item in aggregates)
    total_completion_tokens = sum(item["completion_tokens"] for item in aggregates)
    total_completion_seconds = sum(item["completion_seconds"] for item in aggregates)
    total_wall = sum(item["wall_s"] for item in aggregates)
    if total_wall <= 0:
        raise MatrixError("run wall time must be positive")
    if total_prompt_seconds <= 0 or total_completion_seconds <= 0:
        raise MatrixError("run metric seconds must be positive")
    return {
        "requests": sum(item["requests"] for item in aggregates),
        "decode_tps": total_completion_tokens / total_completion_seconds,
        "prompt_tps": total_prompt_tokens / total_prompt_seconds,
        "busy_slots_per_decode": sum(item["busy_slots_per_decode"] for item in aggregates) / len(aggregates),
        "re_prefill_count": sum(item["re_prefill_count"] for item in aggregates),
        "wall_s": total_wall,
        "prompt_tokens": total_prompt_tokens,
        "completion_tokens": total_completion_tokens,
    }


def run_load(prompts_dir: Path, concurrency: int, max_tokens: int, rounds: int, out: Path,
             base_url: str, key: str | None, log_path: Path,
             cell: dict[str, Any] | None = None) -> dict[str, Any]:
    if concurrency <= 0 or max_tokens <= 0 or rounds <= 0:
        raise MatrixError("concurrency, max-tokens, and rounds must be positive integers")
    paths = sorted(prompts_dir.glob("prompt-*.json"))
    if not paths:
        raise MatrixError(f"no prompt-*.json files under {prompts_dir}")
    prompts = [_read_prompt(path) for path in paths]
    props = props_subset(request(base_url, "/props", key, timeout=30))
    result_rounds: list[dict[str, Any]] = []
    for round_index in range(rounds):
        indices = [(round_index + slot) % len(prompts) for slot in range(concurrency)]
        before = parse_metrics(request(base_url, "/metrics", key, timeout=30))
        log_position = _log_position(log_path)
        started = time.monotonic()
        with ThreadPoolExecutor(max_workers=concurrency) as pool:
            futures = [pool.submit(_completion, base_url, key, prompts[index], max_tokens)
                       for index in indices]
            request_rows = [future.result() for future in futures]
        wall_s = time.monotonic() - started
        after = parse_metrics(request(base_url, "/metrics", key, timeout=30))
        re_prefills = _count_reprefills(log_path, log_position)
        result_rounds.append({
            "round": round_index + 1,
            "prompt_indices": indices,
            "requests": request_rows,
            "aggregate": aggregate_round(request_rows, before, after, re_prefills, wall_s),
        })
    result = {
        "schema": "qwen-matrix-v1",
        "cell": {**(cell or {}), "props": props},
        "concurrency": concurrency,
        "max_tokens": max_tokens,
        "rounds": result_rounds,
        "summary": _summary(result_rounds),
    }
    json.dumps(result, allow_nan=False)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    return result


def _load_cell(path: Path) -> dict[str, Any]:
    cell_dir = path if path.is_dir() else path.parent
    candidate = cell_dir / "result.json" if path.is_dir() else path
    run_complete = cell_dir / "run-complete"
    run_error = cell_dir / "run-error"
    unit_text_path = cell_dir / "unit-text"
    try:
        data = json.loads(candidate.read_text())
    except (OSError, json.JSONDecodeError) as exc:
        raise MatrixError(f"cell result is unreadable JSON: {candidate}") from exc
    if not isinstance(data, dict) or not isinstance(data.get("cell"), dict) or not isinstance(data.get("summary"), dict):
        raise MatrixError(f"cell result missing cell/summary blocks: {candidate}")
    identity = data["cell"]
    argv_text = identity.get("argv_text")
    argv_sha = identity.get("argv_sha256")
    unit_sha = identity.get("unit_sha256")
    run_id = identity.get("run_id")
    if run_error.exists():
        raise MatrixError(f"cell run has error state: {run_error}")
    if not isinstance(run_id, str) or not re.fullmatch(r"[0-9a-f]{64}", run_id):
        raise MatrixError(f"cell result run_id is not lowercase sha256-shaped: {candidate}")
    try:
        completed_run_id = run_complete.read_text().strip()
    except OSError as exc:
        raise MatrixError(f"cell completion record unreadable: {run_complete}") from exc
    if completed_run_id != run_id:
        raise MatrixError(f"cell completion record does not match run_id: {run_complete}")
    if not isinstance(argv_text, str) or not argv_text:
        raise MatrixError(f"cell result missing non-empty argv_text: {candidate}")
    if not isinstance(argv_sha, str) or not re.fullmatch(r"[0-9a-f]{64}", argv_sha):
        raise MatrixError(f"cell result argv_sha256 is not lowercase sha256: {candidate}")
    if hashlib.sha256(argv_text.encode()).hexdigest() != argv_sha:
        raise MatrixError(f"cell result argv_sha256 does not match argv_text: {candidate}")
    if not isinstance(unit_sha, str) or not re.fullmatch(r"[0-9a-f]{64}", unit_sha):
        raise MatrixError(f"cell result unit_sha256 is not lowercase sha256: {candidate}")
    try:
        unit_text = unit_text_path.read_bytes()
    except OSError as exc:
        raise MatrixError(f"cell unit text unreadable: {unit_text_path}") from exc
    if hashlib.sha256(unit_text).hexdigest() != unit_sha:
        raise MatrixError(f"cell result unit_sha256 does not match unit-text: {candidate}")
    return data


def render_table(cells: list[dict[str, Any]]) -> str:
    if not cells:
        raise MatrixError("table requires at least one cell")
    by_name: dict[str, dict[str, Any]] = {}
    for cell in cells:
        name = cell["cell"].get("name")
        if not isinstance(name, str) or not name:
            raise MatrixError("cell result missing a non-empty cell name")
        if name in by_name:
            raise MatrixError(f"duplicate cell name: {name}")
        by_name[name] = cell
    if "A" not in by_name:
        raise MatrixError("table requires baseline cell A")
    baseline = by_name["A"]["summary"]
    baseline_decode = _finite_nonnegative(baseline.get("decode_tps"), "A decode_tps")
    if baseline_decode <= 0:
        raise MatrixError("A decode_tps must be positive")
    baseline_refills = int(_finite_nonnegative(baseline.get("re_prefill_count"), "A re_prefill_count"))
    lines = [
        "| Cell | Decode t/s | Prompt t/s | Busy slots/decode | Re-prefills | VRAM peak MiB |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    verdicts: list[str] = []
    for name, cell in by_name.items():
        summary = cell["summary"]
        requests = summary.get("requests")
        if type(requests) is not int or requests <= 0:
            raise MatrixError(f"{name} requests must be a positive integer: {requests!r}")
        decode = _finite_nonnegative(summary.get("decode_tps"), f"{name} decode_tps")
        prompt = _finite_nonnegative(summary.get("prompt_tps"), f"{name} prompt_tps")
        busy = _finite_nonnegative(summary.get("busy_slots_per_decode"), f"{name} busy_slots_per_decode")
        refills = int(_finite_nonnegative(summary.get("re_prefill_count"), f"{name} re_prefill_count"))
        peak = int(_finite_nonnegative(cell.get("vram_peak_mib", 0), f"{name} vram_peak_mib"))
        lines.append(f"| {name} | {decode:.3f} | {prompt:.3f} | {busy:.3f} | {refills} | {peak} |")
        if name != "A":
            ratio = decode / baseline_decode
            verdicts.append(f"{name}: aggregate decode >= 1.5x A: {'YES' if ratio >= 1.5 else 'NO'} ({ratio:.3f}x)")
            verdicts.append(f"{name}: re-prefills < A: {'YES' if refills < baseline_refills else 'NO'} ({refills} < {baseline_refills})")
    return "\n".join(lines + [""] + verdicts) + "\n"


def parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--base-url", default=os.environ.get("QWEN_MATRIX_BASE_URL", DEFAULT_BASE_URL))
    ap.add_argument("--key-file", type=Path,
                    default=Path(os.environ.get("QWEN_KEY_FILE", DEFAULT_KEY_FILE)))
    sub = ap.add_subparsers(dest="command", required=True)

    build = sub.add_parser("build-corpus")
    build.add_argument("--from", dest="source", type=Path, required=True)
    build.add_argument("--target-tokens", type=int, required=True)
    build.add_argument("--out", type=Path, required=True)

    run = sub.add_parser("run")
    run.add_argument("--prompts", type=Path, required=True)
    run.add_argument("--concurrency", type=int, required=True)
    run.add_argument("--max-tokens", type=int, default=1000)
    run.add_argument("--rounds", type=int, required=True)
    run.add_argument("--out", type=Path, required=True)
    run.add_argument("--log", type=Path, default=Path(os.environ.get("QWEN_MATRIX_LOG", DEFAULT_LOG)))
    run.add_argument("--cell", default=os.environ.get("QWEN_MATRIX_CELL", "adhoc"))
    run.add_argument("--argv-file", type=Path)
    run.add_argument("--unit-sha-file", type=Path)
    run.add_argument("--unit-text-file", type=Path)
    run.add_argument("--run-id")

    table = sub.add_parser("table")
    table.add_argument("cells", nargs="+", type=Path)
    return ap


def _sha256(path: Path) -> str:
    try:
        return hashlib.sha256(path.read_bytes()).hexdigest()
    except OSError as exc:
        raise MatrixError(f"cell identity file unreadable: {path}: {exc.strerror}") from exc


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    try:
        if args.command == "table":
            sys.stdout.write(render_table([_load_cell(path) for path in args.cells]))
            return 0
        key = read_key(args.key_file)
        if args.command == "build-corpus":
            paths = build_corpus(args.source, args.target_tokens, args.out, args.base_url, key)
            print(f"qwen-matrix: wrote {len(paths)} prompts; final={paths[-1]}")
            return 0
        cell: dict[str, Any] = {"name": args.cell}
        if not args.argv_file:
            raise MatrixError("run requires --argv-file")
        try:
            cell["argv_text"] = args.argv_file.read_text()
        except OSError as exc:
            raise MatrixError(f"cell identity file unreadable: {args.argv_file}: {exc.strerror}") from exc
        cell["argv_sha256"] = _sha256(args.argv_file)
        if not args.unit_sha_file:
            raise MatrixError("run requires --unit-sha-file")
        try:
            unit_sha = args.unit_sha_file.read_text().strip()
        except OSError as exc:
            raise MatrixError(f"cell identity file unreadable: {args.unit_sha_file}: {exc.strerror}") from exc
        if not re.fullmatch(r"[0-9a-f]{64}", unit_sha):
            raise MatrixError(f"unit sha file is not lowercase sha256: {args.unit_sha_file}")
        cell["unit_sha256"] = unit_sha
        if not args.unit_text_file:
            raise MatrixError("run requires --unit-text-file")
        unit_text_sha = _sha256(args.unit_text_file)
        if unit_text_sha != cell.get("unit_sha256"):
            raise MatrixError(f"unit sha does not match unit text: {args.unit_text_file}")
        if not args.run_id:
            raise MatrixError("run requires --run-id")
        if not re.fullmatch(r"[0-9a-f]{64}", args.run_id):
            raise MatrixError("run-id is not lowercase sha256-shaped")
        cell["run_id"] = args.run_id
        run_load(args.prompts, args.concurrency, args.max_tokens, args.rounds, args.out,
                 args.base_url, key, args.log, cell)
        print(args.out)
        return 0
    except (MatrixError, OSError) as exc:
        print(f"qwen-matrix: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
