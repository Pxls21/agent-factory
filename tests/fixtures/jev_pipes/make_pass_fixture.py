#!/usr/bin/env python3
"""The P1 replay's PASS-path fixture and its oracle (P1-R1, task #267; VERIFY-P1 G-PASS and F-PERSIST).

    python3 tests/fixtures/jev_pipes/make_pass_fixture.py <dir> <variant>   # writes <dir>/transcript.jsonl, prints the oracle

A synthetic session in which the vendored pruner DOES prune, built only with make_fixture.py's production-shape records,
and the values the harness must report, computed from the fixture's own event list. The oracle imports nothing from
scripts/jev_pipes/: it restates the brief's accounting on its own (tests/test_jev_pipes_replay.py holds that import
boundary). Adapted from VERIFY-P1's scratch probe pass_path.py (its section 4).

Each Bash result has 60 lines in three 20-line chunks (the pruner's chunkLines): c1 and c3 plain lines, c2 planted noise
(NOISE plus a per-result token noisetok_rRR_nNN). The test's loopback scorer answers 0.02 for a chunk that holds NOISE and
0.93 for any other, so the pruner drops c2 alone (it keeps a chunk at 0.5 or above, or above 0.1). A persisted result's
FILE has 100 lines (c1, three noise chunks, c5); the model saw only its stub, a header and the file's first 2,000
characters. Compactions follow results 5, 10 and 15; fillers sit between results.

The accounting, as the repaired harness must count it (VERIFY-P1 F-PERSIST): for a persisted result the saving, the miss
baseline and the keep rate's denominator count the stub the model saw, never the file the pruner read; for any other
result they count the pruner's input, its stdout, as before (the hook keeps stderr, so stderr is never saved or dropped).

Variants (the first five are VERIFY-P1's; edge20 and persisted_miss are this repair's):
  v0              nothing planted: every result pruned, no miss
  v1              a later tool input uses a token of result 3's dropped chunk: 1 miss of 20 (5%, at the bar: PASS)
  v2              v1 plus result 7's command re-run within 20 calls: 2 of 20 (10%: FAIL)
  v1neg           result 5's token at the 21st lookahead item, result 9's command at the 21st call: outside, no miss
  edge20          the same two at the 20th item and the 20th call: inside, 2 misses (FAIL)
  persisted       v0 plus one persisted result (VERIFY-P1's case)
  persisted_miss  v0 plus two persisted results and one result with stderr, each followed by a planted use inside the
                  window: a token only the first FILE holds (no miss: the model never saw it), a token the second stub
                  showed and the prune dropped (a miss), a token only the stderr holds (no miss: stderr stays)
Every string is synthetic.
"""
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import make_fixture as mf  # noqa: E402  (the production-shape record builders, AF-AP-42)

NOISE = "NOISEFILL"
# the pruner's compact rendering (vendor/jev-pruner/src/output.ts: COMPACT_HEADER, recoveryFooter, the omission marker)
HEADER = "[fast-jev-output trimmed; retained lines verbatim; omissions marked]\n"
ARCHIVE_DIR = ".claude/fast-jev-output"  # where the hook archives a non-persisted output (hooks/fast-jev-output.ts)
# the brief's accounting (tasks/briefs/jev-pipes/P1-brief.md DESIGN 3) and the seed's bar, stated here on their own
CHARS_PER_TOKEN = 4.06
LOOKAHEAD = 20
MISS_RATE_BAR = 0.05
RESULTS = 20
COMPACT_AFTER = (5, 10, 15)
VARIANTS = ("v0", "v1", "v2", "v1neg", "edge20", "persisted", "persisted_miss")
PLANTED_MISSES = {"v0": 0, "v1": 1, "v2": 2, "v1neg": 0, "edge20": 2, "persisted": 0, "persisted_miss": 1}
TOKEN = re.compile(r"\b(?:noise|err)tok_[a-z0-9]+_n\d\d\b")

# where each variant plants a later use: result -> [(kind, argument)], kind token | rerun | token_at | rerun_at
PLANS = {
    "v1": {3: [("token", "noisetok_r03_n05")]},
    "v2": {3: [("token", "noisetok_r03_n05")], 7: [("rerun", 7)]},
    "v1neg": {5: [("token_at", ("noisetok_r05_n05", 21))], 9: [("rerun_at", (9, 21))]},
    "edge20": {5: [("token_at", ("noisetok_r05_n05", 20))], 9: [("rerun_at", (9, 20))]},
    "persisted_miss": {14: [("token", "errtok_r14_n00")]},
}
# results whose tool record carries stderr: the model saw stdout and stderr, the pruner read (and trims) stdout alone
STDERR = {"persisted_miss": {14: "warning: widget cache rebuilt errtok_r14_n00"}}
# persisted results: (after result, tag, tool_use id, command, the token a later tool input uses, or None)
PERSISTED = {
    "persisted": [(12, "p", "toolu_pp_px", "run-widget --dump", None)],
    "persisted_miss": [(12, "a", "toolu_pp_pxa", "run-widget --dump a", "noisetok_pa_n45"),
                       (17, "b", "toolu_pp_pxb", "run-widget --dump b", "noisetok_pb_n05")],
}


def result_lines(r):
    c1 = [f"stage r{r:02d} step {i:02d} widget alpha ok" for i in range(20)]
    c2 = [f"{NOISE} r{r:02d} line {i:02d} noisetok_r{r:02d}_n{i:02d} zz" for i in range(20)]
    c3 = [f"stage r{r:02d} tail {i:02d} widget gamma ok" for i in range(20)]
    return c1, c2, c3


def persisted_lines(tag):
    head = [f"p{tag} head {i:02d} ok" for i in range(20)]
    noise = [f"{NOISE} p{tag} line {i:02d} noisetok_p{tag}_n{i:02d} zz padding padding" for i in range(60)]
    tail = [f"p{tag} tail {i:02d} ok" for i in range(20)]
    return head, noise, tail


def footer(path):
    return f"\n\n[fast-jev-output full output: {path} (Read or grep it if needed)]"


def build(directory, variant):
    """-> (transcript path, events). Events, in file order: req (ctx), item_text and item_tool (text: the assistant text
    or the command), result (seen: the text the model saw; pruner_text: the text the pruner read; the kept lines, the
    omitted line count and the footer's path), boundary."""
    if variant not in VARIANTS:
        raise ValueError(f"unknown variant {variant!r}")
    mf._counter[0] = 0
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=True)
    recs, events = [], []
    state = {"last": None, "req": 0, "ctx": 2000}  # contexts stay above 1,100 (make_fixture.assistant writes ctx - 1100)

    def add(rec):
        recs.append(rec)
        state["last"] = rec["uuid"]

    def request(blocks):
        state["req"] += 1
        state["ctx"] += 7
        add(mf.assistant(state["last"], f"req_pp_{state['req']:03d}", state["ctx"], blocks))
        events.append({"kind": "req", "ctx": state["ctx"]})

    def small_call(uid, command):
        request([mf.tool_use(uid, "Bash", {"command": command, "description": "check"})])
        events.append({"kind": "item_tool", "text": command})
        add(mf.tool_result(state["last"], uid, "ok", mf.bash_record("ok")))

    def filler(n):
        for _ in range(n):
            request([{"text": "noted", "type": "text"}])
            events.append({"kind": "item_text", "text": "noted"})

    add(mf.prompt("00000000-0000-4000-8000-000000000000", "Run the widget stages and report."))
    plan = PLANS.get(variant, {})
    stderr_of = STDERR.get(variant, {})
    persisted = {spec[0]: spec for spec in PERSISTED.get(variant, [])}
    for r in range(1, RESULTS + 1):
        c1, c2, c3 = result_lines(r)
        out = "\n".join(c1 + c2 + c3)
        stderr = stderr_of.get(r, "")
        seen = out + ("\n" + stderr if stderr else "")
        uid, command = f"toolu_pp_{r:02d}", f"run-widget --stage {r}"
        request([{"text": f"Stage {r}.", "type": "text"}, mf.tool_use(uid, "Bash", {"command": command, "description": "Run a stage"})])
        events.append({"kind": "item_text", "text": f"Stage {r}."})
        events.append({"kind": "item_tool", "text": command})
        add(mf.tool_result(state["last"], uid, seen, mf.bash_record(out, stderr=stderr)))
        events.append({"kind": "result", "uid": uid, "command": command, "seen": seen, "pruner_text": out, "persisted": False,
                       "kept_head": c1, "omitted": len(c2), "kept_tail": c3, "path": f"{ARCHIVE_DIR}/bash-{uid}.txt"})
        have = 2 + r % 3  # the lookahead items after the result so far: its fillers
        filler(have)
        for kind, arg in plan.get(r, []):
            if kind == "token":
                small_call(f"toolu_pp_m{r:02d}", f"grep {arg} build.log")
            elif kind == "rerun":
                small_call(f"toolu_pp_rr{r:02d}", f"run-widget --stage {arg}")
            elif kind == "token_at":  # the use lands at lookahead item `at`
                token, at = arg
                filler(at - 1 - have)
                small_call(f"toolu_pp_m{r:02d}", f"grep {token} build.log")
            elif kind == "rerun_at":  # the re-run is tool call `at` after the result
                again, at = arg
                for k in range(at - 1):
                    small_call(f"toolu_pp_pad{r:02d}_{k:02d}", f"true pad {r} {k}")
                small_call(f"toolu_pp_rr{r:02d}", f"run-widget --stage {again}")
        if r in persisted:
            _, tag, puid, pcommand, use = persisted[r]
            head, noise, tail = persisted_lines(tag)
            full = "\n".join(head + noise + tail)
            ppath = directory / f"persisted-p{tag}.txt"
            ppath.write_text(full)
            # the stub names the file by its base name (as make_fixture.py's does); the record carries the real path
            stub = (f"Output too large ({len(full)} characters). Full output saved to: persisted-p{tag}.txt"
                    + "\n\nPreview (first 2KB):\n" + full[:2000])
            request([mf.tool_use(puid, "Bash", {"command": pcommand, "description": "Dump"})])
            events.append({"kind": "item_tool", "text": pcommand})
            add(mf.tool_result(state["last"], puid, stub,
                               mf.bash_record(full[:2000], persistedOutputPath=str(ppath), persistedOutputSize=len(full))))
            events.append({"kind": "result", "uid": puid, "command": pcommand, "seen": stub, "pruner_text": full,
                           "persisted": True, "kept_head": head, "omitted": len(noise), "kept_tail": tail, "path": str(ppath)})
            filler(3)
            if use:
                small_call(f"toolu_pp_mp{tag}", f"grep {use} dump.log")
        if r in COMPACT_AFTER:
            boundary = mf._base("system", state["last"])
            boundary.update({"compactMetadata": {"preTokens": state["ctx"], "trigger": "auto"}, "content": "Conversation compacted",
                             "level": "info", "logicalParentUuid": state["last"], "subtype": "compact_boundary"})
            boundary["parentUuid"] = None
            add(boundary)
            events.append({"kind": "boundary"})
            summary = mf._base("user", state["last"])
            summary.update({"isCompactSummary": True, "isVisibleInTranscriptOnly": True, "promptId": "prompt-fixture-1",
                            "turnOrigin": "compact", "message": {"content": "This session is being continued. Summary: stages ran.",
                                                                 "role": "user"}})
            add(summary)
            filler(1)
    filler(2)
    path = directory / "transcript.jsonl"
    path.write_text("".join(json.dumps(rec, sort_keys=True) + "\n" for rec in recs))
    return path, events


def oracle(events):
    """-> (per result, the bar), from the event list alone: the requests after each result until the next compaction, the
    next request's context (the miss cost), the pruner's compact rendering, the characters counted before and after, and
    the misses (a counted token the prune dropped, used within the next 20 items, tool inputs and assistant texts; or the
    same command re-run within the next 20 tool calls). `uses` maps each token of this result that a later item uses to
    that item's position, inside the window or not; `rerun_at` is the position of the re-run among the later calls."""
    per = {}
    for i, event in enumerate(events):
        if event["kind"] != "result":
            continue
        later = events[i + 1:]
        following = 0
        for e in later:
            if e["kind"] == "boundary":
                break
            following += e["kind"] == "req"
        next_context = next((e["ctx"] for e in later if e["kind"] == "req"), None)
        rendered = (HEADER + "\n".join(event["kept_head"] + [f"[{event['omitted']} lines omitted]"] + event["kept_tail"])
                    + footer(event["path"]))
        counted = event["seen"] if event["persisted"] else event["pruner_text"]
        dropped = set(TOKEN.findall(counted)) - set(TOKEN.findall(rendered))
        # a construction check, not a harness claim: no dropped token occurs before the result (the history clause)
        assert not any(dropped & set(TOKEN.findall(e.get("seen") or e.get("text") or "")) for e in events[:i]), event["uid"]
        items = [e for e in later if e["kind"] in ("item_text", "item_tool")]
        calls = [e["text"] for e in items if e["kind"] == "item_tool"]
        mine = set(TOKEN.findall(event["seen"])) | set(TOKEN.findall(event["pruner_text"]))
        uses = {}
        for n, e in enumerate(items, 1):
            for token in sorted(set(TOKEN.findall(e["text"])) & mine):
                uses.setdefault(token, n)
        rerun_at = next((n for n, c in enumerate(calls, 1) if c == event["command"]), None)
        token_miss = any(n <= LOOKAHEAD and token in dropped for token, n in uses.items())
        rerun = rerun_at is not None and rerun_at <= LOOKAHEAD
        chars_saved = len(counted) - len(rendered)
        chunks = 5 if event["persisted"] else 3
        per[event["uid"]] = {
            "decision": "pruned", "pruned": True, "persisted": event["persisted"], "following_calls": following,
            "next_context_tokens": next_context, "chars_saved": chars_saved,
            "tokens_saved": chars_saved / CHARS_PER_TOKEN * following, "miss": token_miss or rerun,
            "miss_tokens>0": token_miss, "miss_rerun": rerun, "miss_cost": next_context if (token_miss or rerun) else 0,
            "chunks": chunks, "kept": 2, "dropped": chunks - 2, "alignment": "ok",
            "chunks_kept": [{"id": "c1", "reason": "first"}, {"id": f"c{chunks}", "reason": "last"}],
            "chunks_dropped": [{"id": f"c{k}", "score": 0.02} for k in range(2, chunks)],
            "uses": uses, "rerun_at": rerun_at, "chars_counted": len(counted),
        }
    rows = list(per.values())
    saved = sum(r["tokens_saved"] for r in rows)
    cost = sum(r["miss_cost"] for r in rows)
    misses = sum(1 for r in rows if r["miss"])
    rate = misses / len(rows)
    net = saved - cost
    bar = {"pruned": len(rows), "misses": misses, "miss_rate": rate, "tokens_saved": saved, "miss_cost": cost, "net": net,
           "verdict": "PASS" if rate <= MISS_RATE_BAR and net > 0 else "FAIL",
           "char_keep_rate": 1 - sum(r["chars_saved"] for r in rows) / sum(r["chars_counted"] for r in rows)}
    return per, bar


if __name__ == "__main__":
    transcript_path, fixture_events = build(sys.argv[1], sys.argv[2])
    expected, fixture_bar = oracle(fixture_events)
    print(json.dumps({"transcript": str(transcript_path), "bar": fixture_bar, "results": expected}, indent=1))
