#!/usr/bin/env python3
"""P1 (task #231): replay the vendored jev-pruner over this session's recorded tool results and print PASS or FAIL.

    python3 scripts/jev_pipes/replay_pruner.py --min-chars 2000 --out <dir>

It runs the pruner's own trimOutput (vendor/jev-pruner, through scripts/jev_pipes/bridge.mjs) with the real local Laya
scorer on the Bash results of --min-chars characters or more (the verdict set) and on a Read/Grep sample (a secondary
table). The history the pruner reads is rebuilt from the transcript prefix up to each result (transcript.py). One decision
row per result goes to .jev/pipes/ (mode 0600, gitignored): pointers, counts and scores, never session text. The verdict
is the seed's bar (seeds/seed-jev-pipes-p1-v1.yaml): misses at or under 5% of pruned results AND net tokens saved above
zero. Modes (the budget and the queue rule are the seed's fail-open trips):
  replay      default: the live trips, but an in-flight request is waited for (never abandoned) and timed
  live        abort at the budget as a hook would; abandoned requests keep the shared scorer busy, so tests only
  unbudgeted  no budget or queue trip, requests one at a time: what the pruner decides with a patient scorer
  plan        no request: the requests and questions the pruner would send (planning only, never a verdict)
  plan-all    as plan, with the pruner's request cap lifted: every request it would need to cover every chunk
Advisory only; never a gate.
"""
from __future__ import annotations

import argparse
import collections
import glob
import hashlib
import json
import math
import os
import shlex
import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from jev_pipes import accounting, transcript  # noqa: E402

REPO = Path(__file__).resolve().parents[2]
BRIDGE = Path(__file__).resolve().with_name("bridge.mjs")
SOURCES = "/root/.claude/projects/*/*.jsonl"
SCORER_URL = "http://127.0.0.1:47411/v1/systemone"
PRIMARY = ("Bash",)
SECONDARY = ("Read", "Grep")
BAND_EDGES = (2000, 4000, 8000, 16000)
BAND_FLOOR = 20
MODES = {
    "replay": {"abort_at_budget": False, "enforce_budget": True, "serialize": False, "request_timeout_ms": 900_000, "plan_only": False},
    "live": {"abort_at_budget": True, "enforce_budget": True, "serialize": False, "request_timeout_ms": 30_000, "plan_only": False},
    "unbudgeted": {"abort_at_budget": False, "enforce_budget": False, "serialize": True, "request_timeout_ms": 300_000, "plan_only": False},
    "plan": {"abort_at_budget": False, "enforce_budget": False, "serialize": False, "request_timeout_ms": 0, "plan_only": True},
    "plan-all": {"abort_at_budget": False, "enforce_budget": False, "serialize": False, "request_timeout_ms": 0, "plan_only": True,
                 "plan_all_requests": True},
}


def band(chars: int, edges: tuple[int, ...]) -> str:
    lower = [e for e in edges if e <= chars]
    lo = lower[-1] if lower else 0
    higher = [e for e in edges if e > chars]
    return f"{lo // 1000}k-{higher[0] // 1000}k" if higher else f"{lo // 1000}k+"


def stratified(cands: list, n: int, edges: tuple[int, ...], floor: int = BAND_FLOOR) -> list:
    """A deterministic sample of `n` by size band: a floor per band, the rest proportional (largest remainder); inside a
    band, the order is sha256 of the pointer, so the pick spreads over the session and never depends on content."""
    ordered = sorted(cands, key=lambda c: (c.path, c.offset))
    if n <= 0 or n >= len(ordered):
        return ordered
    groups: dict[str, list] = collections.defaultdict(list)
    for c in ordered:
        groups[band(c.chars, edges)].append(c)
    for members in groups.values():
        members.sort(key=lambda c: hashlib.sha256(f"{c.path}:{c.offset}".encode()).hexdigest())
    floor = min(floor, n // len(groups))
    alloc = {b: min(len(g), floor) for b, g in groups.items()}
    rest = n - sum(alloc.values())
    spare = {b: len(g) - alloc[b] for b, g in groups.items()}
    total = sum(spare.values())
    if rest > 0 and total > 0:
        quota = {b: rest * spare[b] / total for b in groups}
        extra = {b: math.floor(q) for b, q in quota.items()}
        for b in sorted(groups, key=lambda b: (-(quota[b] - extra[b]), b))[: rest - sum(extra.values())]:
            extra[b] += 1
        for b in groups:
            alloc[b] += min(extra[b], spare[b])
    picked = [c for b, members in groups.items() for c in members[: alloc[b]]]
    return sorted(picked, key=lambda c: (c.path, c.offset))


def render_command(tool: str, call_input: object) -> str:
    """The command string the pruner classifies. Bash: the command. Read/Grep have none; the secondary table uses the
    closest shell form (Grep is ripgrep), so the pruner's own category rules apply unchanged."""
    if not isinstance(call_input, dict):
        return tool
    if tool == "Bash":
        return call_input["command"] if isinstance(call_input.get("command"), str) else ""
    if tool == "Read":
        return f"Read {call_input.get('file_path', '')}"
    if tool == "Grep":
        parts = ["rg", str(call_input.get("pattern", ""))] + ([str(call_input["path"])] if call_input.get("path") else [])
        return shlex.join(parts)
    return tool


def read_text(path: str) -> str | None:
    try:
        return Path(path).read_text(encoding="utf-8", errors="replace")
    except OSError:
        return None


def build_job(cand, snap, transport: dict) -> tuple[dict, str | None]:
    """(the bridge job, the text the pruner prunes). The job is the hook's view of one tool call (tool.call's answer)."""
    text = transcript.result_text(snap.block)
    tur = snap.record.get("toolUseResult")
    persisted_text = None
    if cand.tool == "Bash":
        result = None
        if isinstance(tur, dict) and isinstance(tur.get("stdout"), str):
            result = {"stdout": tur["stdout"], "stderr": tur["stderr"] if isinstance(tur.get("stderr"), str) else ""}
            if cand.persisted:
                result["persistedOutputPath"] = tur["persistedOutputPath"]
                persisted_text = read_text(tur["persistedOutputPath"])
        source = persisted_text if cand.persisted else (result or {}).get("stdout")
        stem = "bash"
    else:
        result = {"stdout": text, "stderr": ""}
        source, stem = text, cand.tool.lower()
    job = {
        "id": f"{cand.path}:{cand.offset}", "tool": cand.tool, "tool_use_id": cand.tool_use_id,
        "command": render_command(cand.tool, snap.call_input), "archive_stem": stem,
        "answer": {"isError": cand.is_error, "text": text, "result": result},
        "persisted_text": persisted_text, "messages": snap.messages, "transport": transport,
    }
    return job, source


class Bridge:
    def __init__(self) -> None:
        self.proc = subprocess.Popen(["node", str(BRIDGE)], stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                     text=True, encoding="utf-8", cwd=REPO)

    def run(self, job: dict) -> dict:
        assert self.proc.stdin and self.proc.stdout
        self.proc.stdin.write(json.dumps(job, ensure_ascii=True) + "\n")
        self.proc.stdin.flush()
        line = self.proc.stdout.readline()
        if not line:
            raise RuntimeError(f"the bridge exited (rc {self.proc.poll()})")
        answer = json.loads(line)
        if answer.get("bridge_error") or answer.get("id") != job["id"]:
            raise RuntimeError(f"bridge error on {job['id']}: {answer.get('bridge_error') or 'id mismatch'}")
        return answer

    def close(self) -> None:
        if self.proc.stdin:
            self.proc.stdin.close()
        self.proc.wait(timeout=60)


def decision_row(cand, set_name: str, index, answer: dict, source: str | None, history: set, mode: str,
                 transport: dict) -> dict:
    result = answer.get("result") or {}
    pruned = answer.get("fail_open") is False and result.get("trimmed") is True
    following, next_context = index.following(cand.offset)
    chars_saved = result["charsBefore"] - result["charsAfter"] if pruned else 0
    row = {
        "result_id": cand.tool_use_id, "transcript_path": cand.path, "byte_offset": cand.offset, "tool": cand.tool,
        "set": set_name, "band": band(cand.chars, BAND_EDGES), "result_chars": cand.chars,
        "source_chars": answer.get("source_chars"), "mode": mode, "venue": "sandbox",
        "scorer": f"laya-cpu-general {transport['url']}", "budget_ms": transport["budget_ms"],
        "decision": answer["decision"], "pruner_decision": answer.get("pruner_decision"), "stage": answer["stage"],
        "fail_open": answer["fail_open"], "fail_open_reason": answer["fail_open_reason"], "trips": answer["trips"],
        "request_limit": answer.get("request_limit"), "requests": answer["requests"], "latency_ms": answer["elapsed_ms"],
        "chunks": result.get("chunks"), "kept": result.get("kept"), "dropped": result.get("dropped"),
        "scores": result.get("scores"), "alignment": (answer.get("chunk_labels") or {}).get("alignment"),
        "chunks_kept": (answer.get("chunk_labels") or {}).get("kept"),
        "chunks_dropped": (answer.get("chunk_labels") or {}).get("dropped"),
        "pruned": pruned, "chars_saved": chars_saved, "following_calls": following,
        "next_context_tokens": next_context, "tokens_saved": accounting.tokens_saved(chars_saved, following),
        "miss": False, "miss_tokens": 0, "miss_rerun": False, "miss_cost": 0, "secret": answer.get("secret"),
        "document_rule": answer.get("document_rule"),
    }
    if pruned and isinstance(source, str) and isinstance(answer.get("output"), str):
        look = index.items[cand.item_index: cand.item_index + accounting.LOOKAHEAD]
        calls = [index.items[i].rerun_key for i in index.tool_items[cand.tool_item_index: cand.tool_item_index + accounting.LOOKAHEAD]]
        hits, rerun = accounting.miss(source, answer["output"], history, [i.tokens for i in look], calls, cand.rerun_key)
        row.update(miss=hits > 0 or rerun, miss_tokens=hits, miss_rerun=rerun)
        row["miss_cost"] = (next_context or 0) if row["miss"] else 0
    return row


def open_log(path: Path, resume: bool):
    path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | (os.O_APPEND if resume else os.O_TRUNC), 0o600)
    os.fchmod(fd, 0o600)
    return os.fdopen(fd, "a" if resume else "w", encoding="utf-8")


def prefix_sha256(path: str, limit: int) -> str:
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        left = limit
        while left > 0:
            block = handle.read(min(1 << 20, left))
            if not block:
                break
            digest.update(block)
            left -= len(block)
    return digest.hexdigest()


def summarize(rows: list[dict]) -> dict:
    """Counts, rates, latency and the verdict for one set of rows. Nothing here reads session text."""
    reached = [r for r in rows if any(q.get("sent") for q in r["requests"])]
    reached_keys = {(r["transcript_path"], r["byte_offset"]) for r in reached}
    requests = [q for r in rows for q in r["requests"] if q.get("sent") and isinstance(q.get("latency_ms"), (int, float))]
    per_question = [q["latency_ms"] / q["questions"] for q in requests if q.get("status") == 200 and q["questions"]]
    spread = [q["scores"] for q in requests if isinstance(q.get("scores"), list) and len(q["scores"]) >= 2]
    scored = [r for r in rows if isinstance(r.get("chunks"), int) and r["chunks"] > 0]
    chars_before = sum(r["source_chars"] or 0 for r in rows)
    out = {
        "results": len(rows),
        "decisions": dict(collections.Counter(r["decision"] for r in rows).most_common()),
        "document_rules": dict(collections.Counter(r.get("document_rule") for r in rows if r["decision"] == "document").most_common()),
        "fail_open_by_reason": dict(collections.Counter(r["fail_open_reason"] for r in rows if r["fail_open"]).most_common()),
        "planned_requests": sum(len(r["requests"]) for r in rows),
        "planned_questions": sum(q["questions"] for r in rows for q in r["requests"]),
        "reached_scorer": len(reached),
        "latency_ms_p50": accounting.percentile([r["latency_ms"] for r in reached], 50),
        "latency_ms_p90": accounting.percentile([r["latency_ms"] for r in reached], 90),
        "request_ms_p50": accounting.percentile([q["latency_ms"] for q in requests], 50),
        "request_ms_p90": accounting.percentile([q["latency_ms"] for q in requests], 90),
        "ms_per_question_p50": accounting.percentile(per_question, 50),
        "ms_per_question_p90": accounting.percentile(per_question, 90),
        "requests_answered": len(per_question),
        "requests_with_2plus_questions": len(spread),
        "requests_all_scores_equal": sum(1 for s in spread if max(s) - min(s) <= 1e-12),
        "score_spread_p50": accounting.percentile([max(s) - min(s) for s in spread], 50),
        "score_spread_max": max((max(s) - min(s) for s in spread), default=None),
        "score_min": min((x for q in requests for x in (q.get("scores") or [])), default=None),
        "score_max": max((x for q in requests for x in (q.get("scores") or [])), default=None),
        "requests_prefix_over_4096_chars": sum(1 for q in requests if (q.get("prefix_chars") or 0) > 4096),
        "requests_with_prefix": sum(1 for q in requests if isinstance(q.get("prefix_chars"), int)),
        "chunk_keep_rate": (sum(r["kept"] for r in scored) / sum(r["chunks"] for r in scored)) if scored else None,
        "char_keep_rate": (1 - sum(r["chars_saved"] for r in rows) / chars_before) if chars_before else None,
        "miss_by_kind": {"token": sum(1 for r in rows if r["pruned"] and r["miss_tokens"] > 0),
                         "rerun": sum(1 for r in rows if r["pruned"] and r["miss_rerun"])},
        "by_band": {},
    }
    for name in sorted({r["band"] for r in rows}):
        members = [r for r in rows if r["band"] == name]
        out["by_band"][name] = {
            "results": len(members), "reached_scorer": sum(1 for r in members if (r["transcript_path"], r["byte_offset"]) in reached_keys),
            "fail_open": sum(1 for r in members if r["fail_open"]), "pruned": sum(1 for r in members if r["pruned"]),
            "chars_saved": sum(r["chars_saved"] for r in members),
        }
    planned = [r for r in rows if r["decision"] == "plan" and r["requests"]]
    if any("history_key" in q for r in planned for q in r["requests"]):
        segments = [len({q.get("history_key") for q in r["requests"]}) for r in planned]
        out["history_segments_p50"] = accounting.percentile(segments, 50)
        out["history_segments_max"] = max(segments)
        out["results_needing_more_requests_than_the_cap"] = sum(
            1 for r in planned if len(r["requests"]) > (r.get("request_limit") or 0))
        out["results_first_request_covers_every_chunk"] = sum(
            1 for r in planned
            if set(r["requests"][0].get("chunk_ids") or []) == {c for q in r["requests"] for c in (q.get("chunk_ids") or [])})
    out.update(accounting.verdict(rows))
    return out


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--min-chars", type=int, required=True, help="the pipeline's entry floor in characters (the brief: 2000)")
    ap.add_argument("--out", type=Path, required=True, help="directory for summary.json and progress.json")
    ap.add_argument("--mode", choices=sorted(MODES), default="replay")
    ap.add_argument("--sample", type=int, default=300, help="primary (Bash) results to replay, stratified by size band; 0 = all")
    ap.add_argument("--secondary-sample", type=int, default=60, help="Read/Grep results for the secondary table; 0 = none")
    ap.add_argument("--budget-ms", type=float, default=2000.0, help="the venue budget per tool result (sandbox: 2000)")
    ap.add_argument("--request-timeout-ms", type=float, default=None, help="override the mode's wait cap for one request")
    ap.add_argument("--scorer-url", default=SCORER_URL)
    ap.add_argument("--sources", default=SOURCES, help="glob of main-session transcripts (top-level *.jsonl only)")
    ap.add_argument("--decisions", type=Path, default=None, help="decision log (default .jev/pipes/p1-decisions[-MODE].jsonl)")
    ap.add_argument("--resume", action="store_true", help="append to the decision log and skip pointers already in it")
    args = ap.parse_args(argv)

    # AbortSignal.timeout (the bridge) refuses a non-integer or out-of-range delay with RangeError; refuse it here, loudly
    limit = 4294967295
    if not (math.isfinite(args.budget_ms) and 0 < args.budget_ms <= limit) or args.min_chars < 1:
        ap.error("--budget-ms must be finite, positive and at most 4294967295; --min-chars at least 1")
    if args.request_timeout_ms is not None and not (math.isfinite(args.request_timeout_ms) and 1 <= args.request_timeout_ms <= limit):
        ap.error("--request-timeout-ms must be finite, from 1 to 4294967295")
    transport = dict(MODES[args.mode], url=args.scorer_url, budget_ms=args.budget_ms)
    if args.request_timeout_ms is not None:
        transport["request_timeout_ms"] = args.request_timeout_ms
    decisions = args.decisions or REPO / ".jev" / "pipes" / ("p1-decisions.jsonl" if args.mode == "replay" else f"p1-decisions-{args.mode}.jsonl")
    args.out.mkdir(parents=True, exist_ok=True)
    started = time.time()

    sources = sorted(glob.glob(args.sources))
    pins = {path: os.stat(path).st_size for path in sources}
    indexes = {path: transcript.scan(path, pins[path], set(PRIMARY + SECONDARY), args.min_chars, accounting.tokens) for path in sources}
    cands = [c for i in indexes.values() for c in i.candidates]
    primary_all = [c for c in cands if c.tool in PRIMARY]
    secondary_all = [c for c in cands if c.tool in SECONDARY]
    primary = stratified(primary_all, args.sample, BAND_EDGES)
    grep = [c for c in secondary_all if c.tool == "Grep"][: max(0, args.secondary_sample)]
    fill = args.secondary_sample - len(grep)  # stratified() reads n <= 0 as "all", so ask only for a positive fill
    reads = stratified([c for c in secondary_all if c.tool == "Read"], fill, BAND_EDGES, 5) if fill > 0 else []
    secondary = sorted(grep + reads, key=lambda c: (c.path, c.offset))
    chosen = {(c.path, c.offset): ("primary" if c.tool in PRIMARY else "secondary", c) for c in primary + secondary}

    done: set = set()
    if args.resume and decisions.exists():
        for line in decisions.read_text(encoding="utf-8").splitlines():
            row = json.loads(line)
            if row.get("mode") == args.mode:
                done.add((row["transcript_path"], row["byte_offset"]))
    log = open_log(decisions, args.resume)
    bridge = Bridge()
    processed = 0
    try:
        for path in sources:
            wanted = {offset for (p, offset) in chosen if p == path and (p, offset) not in done}
            if not wanted:
                continue
            for snap in transcript.windows(path, pins[path], wanted, accounting.tokens):
                set_name, cand = chosen[(path, snap.offset)]
                job, source = build_job(cand, snap, transport)
                answer = bridge.run(job)
                row = decision_row(cand, set_name, indexes[path], answer, source, snap.history_tokens, args.mode, transport)
                log.write(json.dumps(row) + "\n")
                log.flush()
                processed += 1
                progress = {"processed": processed, "of": len(chosen) - len(done), "elapsed_s": round(time.time() - started),
                            "last_decision": row["decision"]}
                (args.out / "progress.json").write_text(json.dumps(progress) + "\n")
                if processed % 10 == 0:
                    print(f"progress {processed}/{progress['of']} {progress['elapsed_s']}s", file=sys.stderr, flush=True)
    finally:
        bridge.close()
        log.close()

    rows = [json.loads(line) for line in decisions.read_text(encoding="utf-8").splitlines()]
    rows = [r for r in rows if r.get("mode") == args.mode]
    elapsed = time.time() - started
    per_hour = processed / elapsed * 3600 if elapsed > 0 and processed else None
    summary = {
        "mode": args.mode, "min_chars": args.min_chars, "budget_ms": args.budget_ms, "scorer_url": args.scorer_url,
        "transport": transport, "decisions_log": str(decisions), "elapsed_s": round(elapsed, 1),
        "results_per_hour": per_hour,
        "full_primary_set_hours_at_this_rate": (len(primary_all) / per_hour) if per_hour else None,
        "sources": [{"path": p, "pinned_bytes": pins[p], "sha256": prefix_sha256(p, pins[p]),
                     "stats": dict(indexes[p].stats)} for p in sources],
        "candidates": {"primary": len(primary_all), "secondary": len(secondary_all),
                       "by_tool": dict(collections.Counter(c.tool for c in cands)),
                       "primary_by_band": dict(collections.Counter(band(c.chars, BAND_EDGES) for c in primary_all))},
        "replayed": {"primary": len(primary), "secondary": len(secondary),
                     "primary_sample": "all" if len(primary) == len(primary_all) else f"stratified {len(primary)} of {len(primary_all)}"},
        "primary": summarize([r for r in rows if r["set"] == "primary"]),
        "secondary": {tool: summarize([r for r in rows if r["set"] == "secondary" and r["tool"] == tool]) for tool in SECONDARY},
    }
    (args.out / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    p = summary["primary"]
    rate = "n/a (nothing pruned)" if p["miss_rate"] is None else f"{p['miss_rate']:.4f}"
    print(f"results {p['results']} (mode {args.mode}); pruned {p['pruned']}; misses {p['misses']}; miss rate {rate}; "
          f"tokens saved {p['tokens_saved']:.1f}; miss cost {p['miss_cost']}; net {p['net']:.1f}")
    print(f"fail-open by reason: {p['fail_open_by_reason']}")
    if args.mode in ("plan", "plan-all"):
        print("PLAN ONLY: no request was sent, so there is no verdict")
        return 0
    print(f"{p['verdict']}: {'; '.join(p['why']) or 'misses at or under 5% of pruned results and net tokens above zero'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
