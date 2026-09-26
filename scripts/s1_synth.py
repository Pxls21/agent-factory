#!/usr/bin/env python3
"""s1_synth.py: synthetic skill-relevance labels for Laya from this session's chat history (SYNTH1, task #308, D-096).

Laya is to rank the skill sections the System-1 hook injects, and real S1-RATE scores come slowly. This tool turns the
chat history into labeled (step, skill section) pairs, with a labeler that is checked against the real scores first.
The coordinator runs `label` on the PC (the vLLM server is there); the other steps run in the sandbox, where the
transcripts and the secret-value gate are.

candidates --transcript MAIN.jsonl (--out DIR | --dry-run) [--sample 2000] [--top 10] [--seed 308] [--jev DIR]
           [--s1-all REPORT] [--cache FILE]
  ITEMS. Every human-origin prompt: a `user` record the harness marks origin.kind "human", not meta, not a compaction
  summary, holding no tool_result, its text blocks joined; then the hook's own harness-event rule and an empty text drop
  it. And a sample of the real tool calls (Bash, Read, Write, Edit, Grep) of the main transcript and of every file under
  its subagents/ (s1_scores.transcript_files): stratified by tool and by the L1 situation rows each call matches
  (one call per tool a round; within a tool one per stratum a round, each stratum in a seeded shuffle; a repeated input
  counts once), the calls that carry a stamped System-1 injection first. An item is a prompt or a tool INPUT: an
  assistant record is read only for its tool_use blocks, and its text and thinking blocks are never read.
  SCRUBBING. Every string of an item goes through transcript_export.scrub_payload before anything else reads it: the
  exporters' payload scrubber (scrub's rules plus the payload shapes a tool input carries: JSON-escaped credentials,
  curl -u, *_PASS values, URL userinfo). Not scrub_strict: it rewrites every `NAME = value` line and every long mixed
  run, which wrecks the code in a Write or Edit input and the hashes in a command, and session_export runs it only on
  the OUTPUT of a command that names a secret file; an item is never an output. The text is then cut to the hook's own
  PROMPT_SCAN_CHARS (scrub, then cut: AF-AP-127), which is all the hook's ranking reads of a text.
  CANDIDATES. The live hook's own functions (.claude/hooks/system1-context.py, loaded by path; nothing re-implemented):
  the TOP best sections of rank_prompt with its four score floors lifted (MIN_PROMPT_SCORE, ONE_LEAD_MIN_SCORE,
  SHORT_MIN_SCORE, NAMED_MIN_SCORE), so the set holds negatives as well as what the gate injects; a lead word, and a
  library skill's name in the text, still decide which sections get a score at all (the ranking's scope, not a gate).
  Each is composed by plan_prompt ALONE in a fresh window (its rank_prompt answering with that section), so its text
  and `sha` are the hook's. A tool call also gets each situation row match_rows finds, composed alone by plan_tool.
  `gate` marks what the live hook injects in a fresh window: for a ranked section the prompt path's choice (the hook
  runs it on prompts only), for a row the tool path's. A gold item (a real S1-RATE score, S1-ALL's labels) also gets
  its gold section when the ranking holds it below TOP.
  OUTPUT: items.jsonl (the scrubbed texts and each item's candidates), sections.jsonl (the composed excerpts),
  manifest.json (counts, sources, digests). transcript_export's value gate (the known secrets' VALUES, counted in the
  exact bytes; AF-AP-224) runs first, and a hit writes nothing (exit 4). --dry-run writes nothing, opens no secret
  source, and prints counts only.

label --candidates DIR --out LABELS.jsonl --backend vllm|openjev [--concurrency 6] [--limit N] [--rubric r1]
      vllm: [--url http://127.0.0.1:8080] [--model qwen3.8-27b-local] [--key-file ~/.config/qwen-builder/api-key]
            [--thinking] [--max-tokens N] [--timeout 120];  openjev: [--env-file /root/.codiv/api.env]
  One request per (item, section): the rubric (the S1-RATE scale for rel; use = would this section help with this
  step), the step, then the section (the step first, so vLLM's prefix cache serves an item's other sections; the pairs
  go out item by item, gold items first). vllm: straight to the PC's vLLM chat endpoint; the body has EXACTLY the keys
  of ALLOWED_BODY_KEYS and never one of FORBIDDEN_BODY_KEYS (AF-AP-201: one such request OOM-killed the shared
  server), thinking off unless --thinking, max_tokens small; the answer is ONE line `rel=<0-3> use=<0-3> <reason>`,
  parsed exactly (a reason of any length, stored cut to REASON_MAX and marked reason_cut: the model does not keep the
  rubric's length), and anything else is stored as malformed, never guessed. openjev: teacher_label.py's Client,
  Limiter, scrubbing and key handling, by import (one Limiter shared by every thread: 60 requests a minute, 1 s
  apart); two choice questions, QUESTIONS, answered as distributions. Both: --concurrency requests in flight (a thread
  pool of that size); an append-only JSONL keyed by (item, section sha, backend, rubric), with the served model and
  the digests of what was sent; a rerun skips done keys, after it re-parses each stored malformed answer under today's
  rule: one whose stored raw answer is whole and parses gets an appended `reparsed` record and no request (--limit 0
  re-parses only); 429, 5xx and connection errors retry with backoff; the usage totals, and the file's own ok,
  reparsed and malformed counts, print at the end, also after a failure. The key is read in this process, never from
  argv, never printed.

validate --candidates DIR --transcript MAIN.jsonl [--labels LABELS.jsonl --backend B] [--rubric r1] [--jev DIR]
         [--s1-all REPORT] [--out FILE]
  The labeler's agreement with two gold sources. S1-RATE: scripts/s1_scores.py's rows of the System-1 hook with the
  status `scored` ONLY (S1RATE_CAVEAT: the scored rows are a subsample selected by reply length, and a `missing` row is
  no evidence of a non-answer); an injection's rel (and use) applies to each section it carried; a tool call's injection joins its item by
  tool_use_id (the wrapper's telemetry), a prompt's by the human prompt at most 2 s before it. S1-ALL: the 463 labels
  of its report's Appendix E (prompt id, skill, R/P/N), joined to the prompt whose promptId (else uuid) starts with
  the id, and to the best-ranked candidate section of that skill. R/P/N map to the 3-point ordinal N=0 < P=1 < R=2;
  the labeler's rel maps to it by A (primary, fixed before any label): 0,1 -> N; 2 -> P; 3 -> R, and by B: 0 -> N;
  1,2 -> P; 3 -> R. Per source: exact and within-one agreement (Wilson 95%), Spearman's rho (Fisher-z 95%, the
  mapping-free number), Kendall's tau-b, linear-weighted kappa, the confusion table, the counts behind each, and the
  plain order's numbers on the same pairs (the hook's score; D-074: a model must beat it). Without labels it prints
  the gold's coverage and the baselines.

dataset --candidates DIR --labels LABELS.jsonl --backend B --out DIR [--rubric r1] [--model-dir DIR] [--commit-dir DIR]
  The LABELED labels (ok and reparsed alike) as scripts/laya_ft/ rows (build_dataset.make_row's shape: item_id,
  question_id, question_sha, state_sha, options, question, state {query: the step, chunk: the section}, sources) and
  labels (teacher_label's record shape), two questions per pair (QUESTIONS), with a manifest. --model-dir fits each
  state to Laya's window with build_dataset.Fitter (the Laya venv). The value gate runs before --out is written;
  --commit-dir gets only what may be committed (the manifest and the labels: ids, digests, targets; no text).

Exit: 0 done; 2 usage; 3 the labeler refused (a non-retryable status, or retries spent); 4 the value gate refused;
75 another run holds the labels file.
"""
import argparse
import collections
import concurrent.futures
import datetime
import fcntl
import hashlib
import http.client
import importlib.util
import json
import math
import os
import random
import re
import statistics
import sys
import tempfile
import threading
import time
import urllib.error
import urllib.parse
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import transcript_export as TE  # noqa: E402  the exporters' scrubber and value gate

HOOK_PATH = os.path.join(ROOT, ".claude", "hooks", "system1-context.py")
S1_ALL_REPORT = os.path.join(ROOT, "tasks", "briefs", "system1", "S1-ALL-report.md")
SOURCE = "system1-context"            # the stamp source of the System-1 hook's injections (hook_context.py)
S1RATE_CAVEAT = ("scored rows only: a reply over about 200 characters before a tool call is recorded as thinking with "
                 "no text block (VERIFY-S1-RATE, task #309), so the scored rows are a subsample selected by reply "
                 "length, and a missing row is no evidence of a non-answer")
TOOLS = ("Bash", "Read", "Write", "Edit", "Grep")
FLOORS = ("MIN_PROMPT_SCORE", "ONE_LEAD_MIN_SCORE", "SHORT_MIN_SCORE", "NAMED_MIN_SCORE")
TOP, SAMPLE, SEED = 10, 2000, 308
PROMPT_LINK_S = 2.0                   # a prompt-path injection follows its prompt by 0.1 s (measured); at most this
SKILL_FILE_RX = re.compile(r"\.claude/skills/([^/]+)/SKILL\.md")
MARKER_RX = re.compile(r"<private-key-redacted>|<bridge-link-redacted>|<opaque-redacted>|sk-<redacted>|gh<redacted>"
                       r"|AIza<redacted>|xox-<redacted>|<redacted>")
ITEMS, SECTIONS, MANIFEST = "items.jsonl", "sections.jsonl", "manifest.json"
CODE = ("scripts/s1_synth.py", ".claude/hooks/system1-context.py", ".claude/hooks/system1-situations.json",
        "scripts/transcript_export.py", "scripts/s1_scores.py", "scripts/hook_context.py")

# ---------------------------------------------------------------- the rubric (versioned: a label's key carries it)

RUBRIC_VERSION = "r1"
RUBRIC = ("You rate how well one skill section fits one step of a coding agent's work in a software repository. The "
          "step is a person's prompt to the agent, or one tool call the agent made (its input only). The section is "
          "an excerpt of a skill file that a hook would show the agent right before that step.\n"
          "rel, how relevant the section is to this step: 0 unrelated; 1 same area, not this step; 2 relevant to this "
          "step; 3 governs this step (the step must follow it).\n"
          "use, would this section help with this step: 0 no (noise, or nothing in it applies); 1 it confirms what "
          "the step does; 2 the step would use it; 3 it would change what the step does.\n"
          "Answer with exactly one line and nothing else: rel=<0-3> use=<0-3> <a reason of at most 120 characters>")
USER_TEMPLATE = ("THE STEP, {kind}:\n<<<\n{text}\n>>>\n\nTHE SECTION (skill {skill}, section \"{heading}\"), as the hook "
                 "would show it:\n<<<\n{section}\n>>>")
STEP_KINDS = {"prompt": "the person's prompt to the agent",
              "Bash": "a Bash call the agent made (its command)",
              "Write": "a Write call the agent made (the file path, then the text written)",
              "Edit": "an Edit call the agent made (the file path, then the new text)",
              "Read": "a Read call the agent made (the file path)",
              "Grep": "a Grep call the agent made (the pattern, then the path, glob or type)"}
Q_REL = {"type": "choice", "instructions": "How relevant is the skill section in `chunk` to the step in `query`?",
         "criteria": {"unrelated": "The section has nothing to do with this step.",
                      "same_area": "The section is about the same area, but not about this step.",
                      "relevant": "The section is relevant to this step.",
                      "governs": "The section governs this step: the step must follow it."}}
Q_USE = {"type": "choice", "instructions": "Would the skill section in `chunk` help with the step in `query`?",
         "criteria": {"noise": "No: it is noise, or nothing in it applies to this step.",
                      "confirms": "It confirms what the step does.",
                      "used": "The step would use it.",
                      "changes": "It would change what the step does."}}
QUESTIONS = {"skill.governs": Q_REL, "skill.helps": Q_USE}     # option index = the 0-3 value (rel, use)
RUBRIC_SHA = hashlib.sha256(json.dumps({"rubric": RUBRIC, "template": USER_TEMPLATE, "kinds": STEP_KINDS,
                                        "questions": QUESTIONS}, sort_keys=True).encode("utf-8")).hexdigest()
REASON_MAX = 120                      # the STORED reason's length: a longer reason is cut and marked, never refused
ANSWER_RX = re.compile(r"rel=([0-3]) use=([0-3]) (\S.*)")      # fullmatch: ONE line (`.` stops at a newline)
THINK_RX = re.compile(r"\A\s*<think>.*?</think>\s*", re.S)
EMPTY_THINK_RX = re.compile(r"\A\s*<think>\s*</think>\s*")      # no content: never an answer
RAW_MAX = 300
LABELED = ("ok", "reparsed")          # the statuses validate and dataset use: a reparsed label is an ok label

# ---------------------------------------------------------------- the vLLM wire contract (AF-AP-201)

VLLM_URL, VLLM_MODEL = "http://127.0.0.1:8080", "qwen3.8-27b-local"
VLLM_KEY_FILE = "~/.config/qwen-builder/api-key"
ALLOWED_BODY_KEYS = frozenset(("model", "messages", "max_tokens", "temperature", "chat_template_kwargs"))
FORBIDDEN_BODY_KEYS = ("prompt_logprobs", "best_of", "echo", "n")   # per-prompt-token output or extra sequences
MAX_TOKENS, MAX_TOKENS_THINKING = 64, 1024
RETRY_STATUS = frozenset((429, 500, 502, 503, 504))
MAX_ATTEMPTS = 7


class ForbiddenParam(ValueError):
    """A vLLM request body with a key outside ALLOWED_BODY_KEYS: it is never sent."""


class Refused(Exception):
    """The labeler refused: a non-retryable status, or every attempt spent."""


class Stopped(Exception):
    """Another task of the run failed: this one stops before its next request (its pair stays pending)."""


def sha256(data):
    return hashlib.sha256(data if isinstance(data, bytes) else data.encode("utf-8")).hexdigest()


def sha16(text):
    return sha256(text)[:16]


def epoch(ts):
    try:
        return datetime.datetime.fromisoformat(ts.replace("Z", "+00:00")).timestamp()
    except (AttributeError, ValueError):
        return None


def dumps_line(obj):
    """ASCII JSON: a raw U+2028 or U+2029 in a text would split the line for a str.splitlines() reader."""
    return json.dumps(obj, ensure_ascii=True, sort_keys=True) + "\n"


def load_hook(name):
    """The live hook as a private module: its own globals, so a change to one instance never reaches another."""
    spec = importlib.util.spec_from_file_location(name, HOOK_PATH)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def s1_scores():
    import s1_scores as S   # the ONE reader of the stamp and score lines (it imports hook_context)
    return S


# ---------------------------------------------------------------- reading the transcripts

def records(path, stats):
    """The records of one transcript that can be a prompt or hold a tool call. A line that does not parse is skipped and
    counted: a torn last line while the file is written, or a whole line that is not valid JSON."""
    with open(path, "rb") as fh:
        for raw in fh:
            if b'"tool_use"' not in raw and not (b'"user"' in raw and b"human" in raw):
                continue
            try:
                r = json.loads(raw)
            except ValueError:
                stats["unparseable_lines"] += 1
                continue
            if isinstance(r, dict):
                yield r


def human_prompt(r, hook):
    """The text of a human-origin prompt record, else None."""
    if r.get("type") != "user" or r.get("isMeta") or r.get("isCompactSummary"):
        return None
    if (r.get("origin") or {}).get("kind") != "human":
        return None
    c = (r.get("message") or {}).get("content")
    if isinstance(c, list):
        if any(isinstance(b, dict) and b.get("type") == "tool_result" for b in c):
            return None
        text = "\n".join(b["text"] for b in c if isinstance(b, dict) and b.get("type") == "text"
                         and isinstance(b.get("text"), str))
    elif isinstance(c, str):
        text = c
    else:
        return None
    if not text.strip() or text.lstrip().startswith(hook.HARNESS_EVENT_PREFIXES):
        return None
    return text


def tool_uses(r):
    """[(name, input, id)] of an assistant record's tool_use blocks: the ONLY part of an assistant record read here."""
    if r.get("type") != "assistant":
        return []
    content = (r.get("message") or {}).get("content")
    return [(b["name"], b["input"], b["id"]) for b in (content if isinstance(content, list) else [])
            if isinstance(b, dict) and b.get("type") == "tool_use" and b.get("name") in TOOLS
            and isinstance(b.get("input"), dict) and isinstance(b.get("id"), str)]


def scrub(text):
    return TE.scrub_payload(text)


def scrub_value(value, counts):
    """Every string of a value (a prompt, or a tool input's fields; keys kept) through the scrubber, counting the
    redaction markers it added."""
    if isinstance(value, str):
        clean = scrub(value)
        if clean != value:
            counts["_changed"] += 1
            before, after = collections.Counter(MARKER_RX.findall(value)), collections.Counter(MARKER_RX.findall(clean))
            for k in after:
                if after[k] > before[k]:
                    counts[k] += after[k] - before[k]
        return clean
    if isinstance(value, dict):
        return {k: scrub_value(v, counts) for k, v in value.items()}
    if isinstance(value, list):
        return [scrub_value(v, counts) for v in value]
    return value


def tool_text(hook, tool, ti, cwd):
    """A tool input's text as the hook's tool path reads it (tool_fields: the repo-relative path and the written text,
    or a Bash call's command); a Read call's path; a Grep call's pattern, path, glob and type."""
    if tool in hook.TOOLS:
        path, text, _ = hook.tool_fields(tool, ti, cwd)
        return "\n".join(x for x in (path, text) if x)
    if tool == "Read":
        return hook.rel_path(ti.get("file_path"), cwd)
    parts = (ti.get("pattern"), hook.rel_path(ti.get("path"), cwd), ti.get("glob"), ti.get("type"))
    return "\n".join(x for x in parts if isinstance(x, str) and x)


def skill_of(path):
    m = SKILL_FILE_RX.fullmatch(path or "")
    return m.group(1) if m else None


def s1_rate_rows(transcript, jev):
    """The System-1 hook's stamped injections (scripts/s1_scores.py's rows; the agent's notes are dropped here), each
    section as its skill, heading and sha."""
    S = s1_scores()
    rows, _ = S.read_session([transcript])
    S.join_state(rows, jev)
    out = []
    for r in rows:
        if r.get("source") != SOURCE or r.get("kind") == "score":
            continue
        out.append({"id": r.get("id"), "event": r.get("event"), "tool": r.get("tool"), "session": r.get("session"),
                    "agent": r.get("agent"), "time": r.get("time"), "status": r.get("status"), "rel": r.get("rel"),
                    "use": r.get("use"), "tool_use_id": r.get("tool_use_id"),
                    "sections": [{"skill": skill_of(s.get("file")), "heading": s.get("heading"), "sha": s.get("sha")}
                                 for s in r.get("sections") or []]})
    return out


def parse_appendix_e(path):
    """S1-ALL's labels: [(prompt id, skill, R|P|N)] from its report's Appendix E (the fenced block under the heading)."""
    lines = open(path, encoding="utf-8").read().split("\n")
    start = next(i for i, line in enumerate(lines) if line.startswith("## Appendix E."))
    body, fences = [], 0
    for line in lines[start + 1:]:
        if line.startswith("```"):
            fences += 1
            if fences == 2:
                break
            continue
        if fences == 1:
            body.append(line)
    toks = " ".join(body).split()
    if len(toks) % 3:
        raise ValueError("Appendix E: %d tokens, not triples" % len(toks))
    out = [tuple(toks[i:i + 3]) for i in range(0, len(toks), 3)]
    bad = [t for t in out if not re.fullmatch(r"[0-9a-f]{8}", t[0]) or t[2] not in ("R", "P", "N")]
    if bad:
        raise ValueError("Appendix E: %d malformed labels, first %r" % (len(bad), bad[0]))
    return out


def prompt_link(item):
    return ((item.get("prompt_id") or item.get("uuid") or "?")[:8]) if item["kind"] == "prompt" else None


def link_prompt(prompts, session, when):
    """The human prompt item a prompt-path injection belongs to: the latest one of its session at most PROMPT_LINK_S
    before it."""
    t = epoch(when)
    best = None
    for it in prompts:
        pt = epoch(it["time"])
        if t is None or pt is None or it["session"] != session or not 0 <= t - pt <= PROMPT_LINK_S:
            continue
        if best is None or pt > epoch(best["time"]):
            best = it
    return best


# ---------------------------------------------------------------- the hook's own ranking

class Ranker:
    """The live hook, loaded twice by path: `live` as it runs, and `ungated` with the four score floors lifted. Both
    read one index, the hook's corpus_index built once into `cache_path`."""

    def __init__(self, cache_path, top=TOP):
        self.live, self.ungated = load_hook("s1_synth_hook_live"), load_hook("s1_synth_hook_ungated")
        for name in FLOORS:
            setattr(self.ungated, name, float("-inf"))
        self.table = self.live.load_table()
        self.project = set(self.table.get("project_skills") or ())
        self.idx = self.live.corpus_index(cache_path)
        self.live.corpus_index = lambda _cache, idx=self.idx: idx     # read once per run, not once per call
        self.top = top
        self.sections = {}

    def _section(self, sha, text, **fields):
        if sha16(text) != sha:
            raise AssertionError("the hook's sha does not match its own text (%s)" % sha)
        self.sections.setdefault(sha, dict(fields, sha=sha, text=text, bytes=len(text.encode("utf-8"))))

    def excerpt(self, text, entry, idf):
        """The hook's excerpt of ONE ranked section for `text`: plan_prompt in a fresh window, its rank_prompt
        answering with that section only. -> the injected entry, or None."""
        real = self.live.rank_prompt
        self.live.rank_prompt = lambda _p, _i, _pr: ([entry], idf)
        try:
            out, rec, _ = self.live.plan_prompt({"prompt": text}, self.table, set(), None)
        finally:
            self.live.rank_prompt = real
        if not rec["injected"]:
            return None
        e = rec["injected"][0]
        self._section(e["sha"], out, skill=e["skill"], heading=e["heading"], project=e["project"], source="rank",
                      row=None)
        return e

    def ranked(self, text, extra=()):
        """(candidates, why) of a text: the ungated ranking's TOP, then each (skill, heading or None) in `extra` the
        ranking holds lower (its best section), each with the live prompt gate's verdict."""
        _, live, _ = self.live.plan_prompt({"prompt": text}, self.table, set(), None)
        if live.get("why"):
            return [], live["why"]
        injected = {(e["skill"], e["heading"]) for e in live["injected"]}
        scored, idf = self.ungated.rank_prompt(text, self.idx, self.project)
        picks = list(enumerate(scored[:self.top], 1))
        for skill, heading in extra:
            if any(e[1] == skill and heading in (None, e[2]) for _, e in picks):
                continue
            deeper = [(i, e) for i, e in enumerate(scored, 1) if e[1] == skill and heading in (None, e[2])]
            if deeper:
                picks.append(deeper[0])
        out = []
        for rank, entry in picks:
            e = self.excerpt(text, entry, idf)
            if e is None:
                continue
            out.append({"sha": e["sha"], "skill": entry[1], "heading": entry[2], "project": entry[5], "source": "rank",
                        "rank": rank, "score": entry[0], "row": None, "gate": (entry[1], entry[2]) in injected})
        return out, None

    def rows(self, tool, ti, cwd, tuid):
        """(candidates, matched row ids): each situation row the input matches, composed alone by plan_tool in a fresh
        window (a one-row table), `gate` from the live tool path over the whole table."""
        if tool not in self.live.TOOLS:
            return [], []
        matched = self.live.match_rows(self.table, tool, ti, cwd)
        if not matched:
            return [], []
        payload = {"tool_name": tool, "tool_input": ti, "cwd": cwd, "tool_use_id": tuid}
        _, live, _ = self.live.plan_tool(payload, self.table, set())
        injected = {e["row"] for e in live["injected"]}
        out = []
        for row in matched:
            text, rec, _ = self.live.plan_tool(payload, dict(self.table, rows=[row]), set())
            if not rec["injected"]:
                continue
            e = rec["injected"][0]
            self._section(e["sha"], text, skill=row["skill"], heading=row["heading"],
                          project=row["skill"] in self.project, source="row", row=row["id"])
            out.append({"sha": e["sha"], "skill": row["skill"], "heading": row["heading"],
                        "project": row["skill"] in self.project, "source": "row", "rank": None, "score": None,
                        "row": row["id"], "gate": row["id"] in injected})
        return out, [row["id"] for row in matched]


# ---------------------------------------------------------------- candidates

def interleave(groups):
    """One from each group a round, in group order, until every group is spent."""
    return [g[rnd] for rnd in range(max((len(g) for g in groups), default=0)) for g in groups if rnd < len(g)]


def sample_calls(calls, budget, seed):
    """Gold calls first; then one call per tool a round (TOOLS order) until `budget`, each tool's own queue one call per
    stratum (its matched rows, sorted) a round, each stratum in a seeded shuffle. -> (calls, strata count)."""
    rng = random.Random(seed)
    strata = collections.defaultdict(list)
    for c in calls:
        if not c["gold"]:
            strata[c["stratum"]].append(c)
    per_tool = collections.defaultdict(list)
    for key in sorted(strata):
        group = sorted(strata[key], key=lambda c: (c["file_index"], c["line"], c["id"]))
        rng.shuffle(group)
        per_tool[key.split("|", 1)[0]].append(group)
    picked = [c for c in calls if c["gold"]]
    return picked + interleave([interleave(per_tool[t]) for t in TOOLS])[:max(0, budget - len(picked))], len(strata)


def build_candidates(transcript, jev, s1_all_path, sample=SAMPLE, top=TOP, seed=SEED, cache=None):
    """(items, sections, stats, S1-RATE rows, S1-ALL labels, meta) over a session's transcripts. Nothing is written."""
    S = s1_scores()
    files = S.transcript_files(transcript)
    stats = collections.Counter()
    tmp = None
    if cache is None:
        tmp = tempfile.TemporaryDirectory(prefix="s1-synth-")
        cache = os.path.join(tmp.name, "system1-cache.json")
    try:
        ranker = Ranker(cache, top)
        hook = ranker.live
        gold_rows = s1_rate_rows(transcript, jev)
        gold_tools = {r["tool_use_id"] for r in gold_rows if r["event"] == "PreToolUse" and r["tool_use_id"]}
        s1_all = parse_appendix_e(s1_all_path) if s1_all_path else []
        s1_all_skills = collections.defaultdict(list)
        for pid, skill, _grade in s1_all:
            s1_all_skills[pid].append(skill)
        red = collections.Counter()
        prompts, calls, seen_inputs = [], [], {}
        for fi, fp in enumerate(files):
            base = os.path.relpath(fp, os.path.dirname(transcript))
            line = 0
            for r in records(fp, stats):
                line += 1
                if r.get("type") == "user":
                    text = human_prompt(r, hook)
                    if text is None:
                        continue
                    counts = collections.Counter()
                    clean = scrub_value(text, counts)
                    red.update(counts)
                    prompts.append({"id": "p-" + str(r.get("uuid")), "kind": "prompt", "tool": None, "file": base,
                                    "agent": r.get("agentId") or "main", "session": r.get("sessionId"),
                                    "uuid": r.get("uuid"), "prompt_id": r.get("promptId"), "time": r.get("timestamp"),
                                    "cwd": r.get("cwd"), "raw_chars": len(text), "clean": clean})
                    continue
                for name, ti, tuid in tool_uses(r):
                    stats["tool_calls." + name] += 1
                    counts = collections.Counter()
                    clean_ti = scrub_value(ti, counts)
                    cwd = r.get("cwd")
                    text = tool_text(hook, name, clean_ti, cwd)
                    rows = [row["id"] for row in hook.match_rows(ranker.table, name, clean_ti, cwd)] \
                        if name in hook.TOOLS else []
                    gold = tuid in gold_tools
                    key = (name, sha256(text), tuple(rows))
                    if key in seen_inputs and not gold:
                        stats["duplicate_inputs"] += 1
                        continue
                    seen_inputs.setdefault(key, tuid)
                    calls.append({"id": "t-" + tuid, "tool_use_id": tuid, "kind": "tool", "tool": name, "file": base,
                                  "file_index": fi, "line": line, "agent": r.get("agentId") or "main",
                                  "session": r.get("sessionId"), "time": r.get("timestamp"), "cwd": cwd,
                                  "input": clean_ti, "clean": text, "rows_matched": rows, "raw_chars": len(text),
                                  "redactions": dict(counts), "gold": ["s1-rate"] if gold else [],
                                  "stratum": "%s|%s" % (name, "+".join(sorted(rows)) or "-")})
        stats["human_prompts"] = len(prompts)
        stats["distinct_tool_inputs"] = len(calls)
        picked, stats["strata"] = sample_calls(calls, sample, seed)
        stats["gold_tool_calls"] = sum(1 for c in picked if c["gold"])
        gold_prompt = collections.defaultdict(list)
        for r in gold_rows:
            if r["event"] == "UserPromptSubmit":
                it = link_prompt(prompts, r["session"], r["time"])
                if it is not None:
                    gold_prompt[it["id"]] += [(s["skill"], s["heading"]) for s in r["sections"] if s["skill"]]
        items = []
        for it in prompts:
            pid = prompt_link(it)
            extra = [(s, None) for s in s1_all_skills.get(pid, [])] + gold_prompt.get(it["id"], [])
            it["gold"] = sorted(({"s1-all"} if pid in s1_all_skills else set())
                                | ({"s1-rate"} if it["id"] in gold_prompt else set()))
            items.append(finish_item(ranker, it, extra, stats))
        for c in picked:
            items.append(finish_item(ranker, c, [], stats))
        for r in gold_rows:
            stats["s1_rate_injections." + (r["status"] or "none")] += 1
        stats.update({"redactions." + k: v for k, v in red.items() if k != "_changed"})
        stats["prompts_changed_by_scrub"] = red.get("_changed", 0)
        meta = {"files": len(files), "cap_chars": hook.PROMPT_SCAN_CHARS, "top": top}
        return items, ranker.sections, stats, gold_rows, s1_all, meta
    finally:
        if tmp is not None:
            tmp.cleanup()


def finish_item(ranker, it, extra, stats):
    """An item as written: its scrubbed text cut to the hook's PROMPT_SCAN_CHARS, and its candidates (a tool call's
    situation rows after its ranked sections)."""
    cap = ranker.live.PROMPT_SCAN_CHARS
    clean = it.pop("clean")
    text = clean[:cap]
    cands, why = ranker.ranked(text, extra)
    if it["kind"] == "tool":
        rows, matched = ranker.rows(it["tool"], it.pop("input"), it["cwd"], it["tool_use_id"])
        cands += [r for r in rows if r["sha"] not in {c["sha"] for c in cands}]
        red = it.pop("redactions")
        stats["tool_inputs_changed_by_scrub"] += red.get("_changed", 0) > 0
        stats.update({"redactions." + k: v for k, v in red.items() if k != "_changed"})
        for k in ("file_index", "line", "rows_matched"):
            del it[k]
        it["rows"] = matched
    it.update(text=text, text_sha=sha256(text), capped=len(clean) > cap, why=why, candidates=cands)
    return it


def candidate_files(items, sections, stats, gold_rows, s1_all, meta, transcript, args_record):
    """(files to write, manifest)."""
    items_b = "".join(dumps_line(it) for it in items).encode("utf-8")
    secs = [sections[k] for k in sorted(sections)]
    sections_b = "".join(dumps_line(s) for s in secs).encode("utf-8")
    manifest = {"kind": "s1-synth-candidates", "version": 1, "args": args_record,
                "transcript": {"main": os.path.basename(transcript), "files": meta["files"],
                               "unparseable_lines": stats.get("unparseable_lines", 0)},
                "counts": summary_counts(items, sections, stats, gold_rows, s1_all, meta["top"]),
                "hook": {"floors_lifted": list(FLOORS), "top": args_record.get("top"), "cap_chars": meta["cap_chars"]},
                "code": {p: sha256(open(os.path.join(ROOT, p), "rb").read()) for p in CODE},
                "files": {ITEMS: {"sha256": sha256(items_b), "bytes": len(items_b), "lines": len(items)},
                          SECTIONS: {"sha256": sha256(sections_b), "bytes": len(sections_b), "lines": len(secs)}}}
    return [(ITEMS, items_b), (SECTIONS, sections_b)], manifest


def summary_counts(items, sections, stats, gold_rows, s1_all, top=TOP):
    """The counts a dry run prints and the manifest keeps: ids and numbers only."""
    kinds = collections.Counter(it["tool"] or "prompt" for it in items)
    per = [len(it["candidates"]) for it in items]
    prompts = [it for it in items if it["kind"] == "prompt"]
    tools = [it for it in items if it["kind"] == "tool"]

    def top_gate(group):
        with_c = [it for it in group if any(c["source"] == "rank" for c in it["candidates"])]
        first = [next(c for c in it["candidates"] if c["source"] == "rank") for it in with_c]
        return {"items": len(group), "with_ranked": len(with_c), "top_gated": sum(1 for c in first if c["gate"])}

    by_id = {it["id"]: it for it in items}
    cov_all = collections.Counter()
    by_pid = collections.defaultdict(list)
    for it in prompts:
        by_pid[prompt_link(it)].append(it)
    for pid, skill, _g in s1_all:
        its = by_pid.get(pid, [])
        if len(its) != 1:
            cov_all["no_item" if not its else "ambiguous"] += 1
            continue
        ranks = [c["rank"] for c in its[0]["candidates"] if c["source"] == "rank" and c["skill"] == skill]
        cov_all["no_section" if not ranks else ("top" if min(ranks) <= top else "deeper")] += 1
    cov_rate = collections.Counter()
    for r in gold_rows:
        if r["status"] != "scored":
            continue
        it = by_id.get("t-%s" % r["tool_use_id"]) if r["event"] == "PreToolUse" else None
        if r["event"] == "UserPromptSubmit":
            it = link_prompt(prompts, r["session"], r["time"])
        for s in r["sections"]:
            if it is None:
                cov_rate["no_item"] += 1
                continue
            c = [c for c in it["candidates"] if c["skill"] == s["skill"] and c["heading"] == s["heading"]]
            cov_rate["no_section" if not c else ("same_text" if any(x["sha"] == s["sha"] for x in c)
                                                 else "other_text")] += 1
    rows_items = [it for it in tools if it.get("rows")]
    gold_items = [it for it in items if it.get("gold")]
    return {"items": dict(sorted(kinds.items())), "items_total": len(items),
            "population": {k: v for k, v in sorted(stats.items()) if not k.startswith("redactions.")},
            "redactions": {k.split(".", 1)[1]: v for k, v in sorted(stats.items()) if k.startswith("redactions.")},
            "capped_items": sum(1 for it in items if it["capped"]),
            "why": dict(collections.Counter(it["why"] for it in items if it["why"])),
            "candidates": {"pairs": sum(per), "zero": per.count(0), "min": min(per, default=0),
                           "median": statistics.median(per) if per else 0, "mean": round(sum(per) / max(len(per), 1), 2),
                           "max": max(per, default=0),
                           "by_source": dict(collections.Counter(c["source"] for it in items for c in it["candidates"])),
                           "gated": sum(1 for it in items for c in it["candidates"] if c["gate"])},
            "sections": len(sections),
            "gate": {"prompts": top_gate(prompts), "tools_prompt_path": top_gate(tools),
                     "tools_with_rows": len(rows_items),
                     "tools_row_injected": sum(1 for it in rows_items if any(c["gate"] for c in it["candidates"]
                                                                          if c["source"] == "row"))},
            "gold": {"s1_all_pairs": dict(cov_all), "s1_rate_sections": dict(cov_rate),
                     "first": {"items": len(gold_items), "pairs": sum(len(it["candidates"]) for it in gold_items)}},
            "chars": {"item_mean": round(sum(len(it["text"]) for it in items) / max(len(items), 1)),
                      "section_mean": round(sum(s["bytes"] for s in sections.values()) / max(len(sections), 1)),
                      "request_mean": round(sum(len(it["text"]) + sections[c["sha"]]["bytes"] for it in items
                                                for c in it["candidates"]) / max(sum(per), 1))}}


def write_files(out, files, sources):
    """transcript_export's value gate over the exact bytes, then each file through a temp file and a rename."""
    hits = TE.value_hits([data for _, data in files], TE.known_values(sources))
    if hits:
        raise TE.KnownValueRefusal(hits)
    os.makedirs(out, exist_ok=True)
    for name, data in files:
        tmp = os.path.join(out, name + ".tmp")
        with open(tmp, "wb") as fh:
            fh.write(data)
        os.replace(tmp, os.path.join(out, name))


def cmd_candidates(args, sources):
    started = time.monotonic()
    items, sections, stats, gold_rows, s1_all, meta = build_candidates(
        args.transcript, args.jev, args.s1_all or None, args.sample, args.top, args.seed, args.cache)
    record = {"sample": args.sample, "top": args.top, "seed": args.seed, "s1_all": bool(args.s1_all)}
    files, manifest = candidate_files(items, sections, stats, gold_rows, s1_all, meta, args.transcript, record)
    counts = dict(manifest["counts"], seconds=round(time.monotonic() - started, 1), transcript_files=meta["files"],
                  rubric_chars=len(RUBRIC) + len(USER_TEMPLATE), would_write={name: len(data) for name, data in files},
                  baseline_without_labels=validate(items, {}, gold_rows, s1_all, "vllm", RUBRIC_VERSION))
    if args.dry_run:
        print(json.dumps({"dry_run": True, "value_gate": "not run: a dry run writes no text", **counts}, indent=1,
                         sort_keys=True))
        return 0
    try:
        write_files(args.out, files + [(MANIFEST, (json.dumps(manifest, indent=1, sort_keys=True) + "\n")
                                        .encode("utf-8"))], sources)
    except TE.KnownValueRefusal as e:
        for line in e.args[0]:
            print("s1_synth: REFUSED, nothing written: " + line, file=sys.stderr)
        return 4
    print(json.dumps({"written": args.out, **counts}, indent=1, sort_keys=True))
    return 0


# ---------------------------------------------------------------- loading the candidates

def load_candidates(cdir):
    """(items, sections, manifest), each file checked against the manifest's digest."""
    manifest = json.load(open(os.path.join(cdir, MANIFEST), encoding="utf-8"))
    out = []
    for name in (ITEMS, SECTIONS):
        data = open(os.path.join(cdir, name), "rb").read()
        if sha256(data) != manifest["files"][name]["sha256"]:
            raise SystemExit("s1_synth: %s does not match its manifest digest" % name)
        out.append([json.loads(line) for line in data.decode("utf-8").split("\n") if line.strip()])
    items, secs = out
    return items, {s["sha"]: s for s in secs}, manifest


def label_key(item_id, sha, backend, rubric=RUBRIC_VERSION):
    return "%s|%s|%s|%s" % (item_id, sha, backend, rubric)


def pairs_of(items):
    """(item, candidate) pairs in send order: gold items first, then the rest, each item's sections together."""
    ordered = [it for it in items if it.get("gold")] + [it for it in items if not it.get("gold")]
    out, seen = [], set()
    for it in ordered:
        for c in it["candidates"]:
            if (it["id"], c["sha"]) not in seen:
                seen.add((it["id"], c["sha"]))
                out.append((it, c))
    return out


def read_labels(path):
    """({key: record}, stats) of an append-only labels file; a torn line is skipped and counted, a repeated key keeps
    its first record, except that a `reparsed` record replaces the `malformed` record it re-parses (reparse)."""
    recs, stats = {}, {"records": 0, "torn": 0, "duplicates": 0, "reparsed": 0}
    if not os.path.exists(path):
        return recs, stats
    for line in open(path, encoding="utf-8").read().split("\n"):
        if not line.strip():
            continue
        try:
            rec = json.loads(line)
            key = rec["key"]
        except (ValueError, KeyError, TypeError):
            stats["torn"] += 1
            continue
        if key in recs:
            if rec.get("status") == "reparsed" and recs[key].get("status") == "malformed":
                recs[key] = rec
                stats["reparsed"] += 1
            else:
                stats["duplicates"] += 1
            continue
        recs[key] = rec
    stats["records"] = len(recs)
    return recs, stats


# ---------------------------------------------------------------- the labeler

def step_text(item):
    """The step as the state's `query`: what it is, then its text."""
    return "%s:\n%s" % (STEP_KINDS[item["tool"] or "prompt"], item["text"])


def user_message(item, section):
    return USER_TEMPLATE.format(kind=STEP_KINDS[item["tool"] or "prompt"], text=item["text"], skill=section["skill"],
                                heading=section["heading"], section=section["text"])


def check_body(body):
    """A vLLM body leaves only with EXACTLY ALLOWED_BODY_KEYS (AF-AP-201)."""
    keys = set(body)
    bad = sorted(keys - ALLOWED_BODY_KEYS) + sorted(k for k in FORBIDDEN_BODY_KEYS if k in keys)
    if bad or keys != ALLOWED_BODY_KEYS:
        raise ForbiddenParam("a vLLM body must carry exactly %s; refused keys %s" % (sorted(ALLOWED_BODY_KEYS), bad))


def chat_body(model, item, section, thinking, max_tokens):
    """The ONLY place a vLLM body is built."""
    return {"model": model,
            "messages": [{"role": "system", "content": RUBRIC},
                         {"role": "user", "content": user_message(item, section)}],
            "max_tokens": max_tokens, "temperature": 0,
            "chat_template_kwargs": {"enable_thinking": bool(thinking)}}


def parse_answer(content, thinking=False):
    """(rel, use, reason, cut) of an answer that is exactly one line `rel=<0-3> use=<0-3> <reason>`, the reason of any
    length and kept to REASON_MAX characters (cut: it was longer); None otherwise. A leading EMPTY <think></think> block
    (a template can emit one with thinking off) is dropped; with --thinking, a leading <think> block with content too
    (it is never stored)."""
    if not isinstance(content, str):
        return None
    content = (THINK_RX if thinking else EMPTY_THINK_RX).sub("", content, count=1)
    m = ANSWER_RX.fullmatch(content.strip())
    if not m:
        return None
    reason = m.group(3)
    return int(m.group(1)), int(m.group(2)), reason[:REASON_MAX], len(reason) > REASON_MAX


def reparse(rec, thinking=False):
    """A stored `malformed` record whose raw answer parses under parse_answer now -> its `reparsed` record (the same
    key, sent_sha and raw; the answer's rel, use and reason), else None. A raw of RAW_MAX characters or more is the
    head of a longer answer whose rest (a second line?) was never stored: it is never re-parsed."""
    raw = rec.get("raw")
    if rec.get("status") != "malformed" or not isinstance(raw, str) or len(raw) >= RAW_MAX:
        return None
    parsed = parse_answer(raw, thinking)
    if parsed is None:
        return None
    return dict(rec, status="reparsed", rel=parsed[0], use=parsed[1], reason=parsed[2], reason_cut=parsed[3],
                why=None, reparsed_ts=round(time.time(), 3))


def http_post(url, data, key, timeout):
    """-> (status, body bytes, headers); a non-2xx status comes back as a status, never as an exception."""
    req = urllib.request.Request(url, data=data, method="POST", headers={
        "Content-Type": "application/json", "Authorization": "Bearer " + key})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.status, r.read(), dict(r.headers)
    except urllib.error.HTTPError as e:
        return e.code, e.read(600), dict(e.headers or {})


def read_key(path):
    """The vLLM key, read in this process: never from argv, never printed."""
    with open(os.path.expanduser(path), encoding="utf-8") as fh:
        key = fh.read().strip()
    if not key:
        raise SystemExit("s1_synth: the key file %s is empty" % path)
    return key


class VllmClient:
    """POST to vLLM's chat endpoint with retries: 429, 5xx and connection errors back off (2, 4, ... s, at most 60);
    another status refuses. Safe to share between threads."""

    def __init__(self, url, model, key, timeout, sleep=time.sleep, post=http_post):
        self.url = url.rstrip("/") + "/v1/chat/completions"
        self.endpoint = urllib.parse.urlsplit(self.url).netloc
        self.model, self._key, self.timeout, self.sleep, self.post = model, key, timeout, sleep, post
        self.usage, self._lock = collections.Counter(), threading.Lock()

    def count(self, **kw):
        with self._lock:
            self.usage.update(kw)

    def safe(self, text):
        """A message fit to print: the key replaced, then scrubbed."""
        return TE.scrub(str(text).replace(self._key, "<key>"))

    def ask(self, body, stop=None):
        check_body(body)
        data = json.dumps(body).encode("utf-8")
        why = None
        for attempt in range(MAX_ATTEMPTS):
            if stop is not None and stop.is_set():
                raise Stopped()
            self.count(requests=1)
            try:
                status, raw, _headers = self.post(self.url, data, self._key, self.timeout)
            except (urllib.error.URLError, OSError, http.client.HTTPException) as e:
                why = "%s: %s" % (type(e).__name__, e)
            else:
                if 200 <= status < 300:
                    try:
                        out = json.loads(raw)
                        choice = out["choices"][0]
                        if not isinstance(choice["message"], dict):
                            raise TypeError("message")
                        return out, attempt + 1, data
                    except (ValueError, KeyError, IndexError, TypeError):
                        why = "HTTP %d with a body that is not a chat completion" % status
                else:
                    why = "HTTP %d: %s" % (status, raw[:300].decode("utf-8", "replace"))
                    if status not in RETRY_STATUS:
                        raise Refused(self.safe(why))
            if attempt + 1 == MAX_ATTEMPTS:
                break
            self.count(retries=1)
            self.sleep(min(60.0, 2.0 ** (attempt + 1)))
        raise Refused(self.safe("gave up after %d attempts; last: %s" % (MAX_ATTEMPTS, why)))


def vllm_worker(args, sleep):
    client = VllmClient(args.url, args.model, read_key(args.key_file), args.timeout, sleep=sleep)
    max_tokens = args.max_tokens or (MAX_TOKENS_THINKING if args.thinking else MAX_TOKENS)

    def work(item, cand, section, stop):
        body = chat_body(args.model, item, section, args.thinking, max_tokens)
        out, attempts, data = client.ask(body, stop)
        choice = out["choices"][0]
        content = choice["message"].get("content")
        parsed = parse_answer(content, args.thinking)
        usage = out.get("usage") if isinstance(out.get("usage"), dict) else {}
        usage = {k: usage.get(k) if type(usage.get(k)) is int else None for k in ("prompt_tokens", "completion_tokens")}
        client.count(prompt_tokens=usage["prompt_tokens"] or 0, completion_tokens=usage["completion_tokens"] or 0,
                     **{"ok" if parsed else "malformed": 1})
        return {"status": "ok" if parsed else "malformed", "rel": parsed[0] if parsed else None,
                "use": parsed[1] if parsed else None, "reason": parsed[2] if parsed else None,
                "reason_cut": parsed[3] if parsed else None,
                "raw": None if parsed else (content if isinstance(content, str) else json.dumps(content))[:RAW_MAX],
                "why": None if parsed else "not one line `rel=<0-3> use=<0-3> <reason>`",
                "model": out.get("model"), "requested_model": args.model, "endpoint": client.endpoint,
                "sent_sha": sha256(data), "finish": choice.get("finish_reason"),
                "prompt_tokens": usage.get("prompt_tokens"), "completion_tokens": usage.get("completion_tokens"),
                "attempts": attempts}

    return work, lambda: dict(client.usage), client.safe


class LockedLimiter:
    """teacher_label's Limiter shared by every thread: one admission at a time."""

    def __init__(self, inner):
        self.inner, self.lock = inner, threading.Lock()

    def admit(self):
        with self.lock:
            self.inner.admit()


def openjev_worker(args, clock, sleep, post):
    sys.path.insert(0, HERE)
    from laya_ft import common as C
    from laya_ft import teacher_label as TL
    env = TL.read_env(args.env_file)
    shared = LockedLimiter(TL.Limiter(clock, sleep))
    local, clients, lock = threading.local(), [], threading.Lock()
    post = post or TL.http_post

    def client():
        c = getattr(local, "client", None)
        if c is None:
            c = TL.Client(env, clock=clock, sleep=sleep, post=post, timeout=args.timeout)
            c.limiter = shared
            with lock:
                clients.append(c)
            local.client = c
        return c

    def usage():
        total = collections.Counter()
        for c in clients:
            total.update(c.usage)
        return dict(total)

    def work(item, cand, section, stop):                # teacher_label's Client retries on its own: no stop check inside
        c = client()
        body = {"model": TL.MODEL, "state": TL.scrubbed({"query": step_text(item), "chunk": section["text"]}),
                "questions": TL.scrubbed(QUESTIONS)}
        data = json.dumps(body).encode("utf-8")
        rec = {"model": None, "endpoint": c.endpoint, "sent_sha": sha256(data), "attempts": None, "reason": None}
        try:
            out, attempts = c.ask(body)
            rec.update(model=out.get("model"), attempts=attempts, input_tokens=TL.input_tokens(out))
            answers = out.get("answers")
            if not isinstance(answers, dict):
                raise C.LabelError("the response has no answers")
            targets = {}
            for qid, q in QUESTIONS.items():
                if qid not in answers:
                    raise C.LabelError("the response has no answer for %s" % qid)
                targets[qid] = C.distribution(answers[qid], q)
        except C.LabelError as e:
            return dict(rec, status="malformed", rel=None, use=None, why=c.safe(e), raw=None)
        rel = max(range(4), key=lambda i: targets["skill.governs"][i])
        use = max(range(4), key=lambda i: targets["skill.helps"][i])
        return dict(rec, status="ok", rel=rel, use=use, why=None, raw=None, target_rel=targets["skill.governs"],
                    target_use=targets["skill.helps"])

    return work, usage, lambda text: TE.scrub(str(text))


def cmd_label(args, clock=time.monotonic, sleep=time.sleep, post=None):
    items, sections, _ = load_candidates(args.candidates)
    try:
        if args.backend == "vllm":
            work, usage, safe = vllm_worker(args, sleep)
        else:
            work, usage, safe = openjev_worker(args, clock, sleep, post)
    except (SystemExit, OSError) as e:                 # names the file, never a value
        where = args.key_file if args.backend == "vllm" else args.env_file
        print("s1_synth: the %s credentials (%s): %s" % (args.backend, where, type(e).__name__ if isinstance(e, OSError)
                                                          else e), file=sys.stderr)
        return 64
    started = time.monotonic()
    rc, stored, refused = 0, collections.Counter(), None
    os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
    with open(args.out, "a+", encoding="utf-8") as fh:
        try:
            fcntl.flock(fh, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            print("s1_synth: another run holds %s" % args.out, file=sys.stderr)
            return 75
        done, _ = read_labels(args.out)
        pairs = [(it, c) for it, c in pairs_of(items)
                 if label_key(it["id"], c["sha"], args.backend, args.rubric) not in done]
        todo = pairs if args.limit is None else pairs[:args.limit]
        with open(args.out, "rb") as tail:
            tail.seek(0, os.SEEK_END)
            if tail.tell():
                tail.seek(-1, os.SEEK_END)
                if tail.read(1) != b"\n":
                    fh.write("\n")                   # a torn last line stays its own (skipped) line
        rep = collections.Counter()    # a stored answer that parses under today's rule is re-parsed, never re-asked
        for key in sorted(done):
            new = reparse(done[key], args.thinking)
            if new is not None:
                fh.write(dumps_line(new))
                done[key] = new
                rep["reparsed"] += 1
            elif done[key].get("status") == "malformed" and len(done[key].get("raw") or "") >= RAW_MAX:
                rep["unchecked"] += 1              # its raw is the head of a longer answer: it stays malformed
        if rep["reparsed"]:
            fh.flush()
            os.fsync(fh.fileno())

        stop = threading.Event()       # the first failure stops the run: no task starts, no vLLM attempt follows

        def task(it, c):
            if stop.is_set():
                raise Stopped()
            sec = sections[c["sha"]]
            try:
                rec = work(it, c, sec, stop)
            except Stopped:
                raise
            except Exception:
                stop.set()
                raise
            rec.update(key=label_key(it["id"], c["sha"], args.backend, args.rubric), item=it["id"], section=c["sha"],
                       backend=args.backend, rubric=args.rubric, rubric_sha=RUBRIC_SHA, item_sha=it["text_sha"],
                       section_sha256=sha256(sec["text"]), ts=round(time.time(), 3))
            return rec

        try:
            with concurrent.futures.ThreadPoolExecutor(max_workers=args.concurrency) as pool:
                futures = [pool.submit(task, it, c) for it, c in todo]
                for fut in concurrent.futures.as_completed(futures):
                    if fut.cancelled():
                        continue
                    try:
                        rec = fut.result()
                    except Stopped:
                        continue
                    except Exception as e:                      # Refused, teacher_label's Refused, a defect
                        if refused is None:
                            refused = e
                            for other in futures:
                                other.cancel()
                        continue
                    fh.write(json.dumps(rec, ensure_ascii=True, sort_keys=True) + "\n")
                    fh.flush()
                    os.fsync(fh.fileno())
                    stored[rec["status"]] += 1
        finally:
            elapsed = time.monotonic() - started
            n = sum(stored.values())
            if refused is not None:
                print("s1_synth: refused: %s: %s" % (type(refused).__name__, safe(refused)), file=sys.stderr)
                rc = 3
            infile = collections.Counter(r.get("status") for r in done.values()     # the file's records, as read
                                         if r.get("backend") == args.backend and r.get("rubric") == args.rubric)
            infile.update(stored)
            print("usage: backend=%s rubric=%s stored=%d ok=%d malformed=%d reparsed=%d reparse_unchecked=%d "
                  "skipped_done=%d pending_left=%d file_ok=%d file_reparsed=%d file_malformed=%d seconds=%.1f "
                  "pairs_per_s=%.3f %s" % (
                      args.backend, args.rubric, n, stored["ok"], stored["malformed"], rep["reparsed"],
                      rep["unchecked"], len(done), len(pairs) - n, infile["ok"], infile["reparsed"],
                      infile["malformed"], elapsed, n / elapsed if elapsed > 0 else 0.0,
                      " ".join("%s=%s" % kv for kv in sorted(usage().items()))), flush=True)
    return rc


# ---------------------------------------------------------------- statistics (stdlib only)

def avg_ranks(xs):
    order = sorted(range(len(xs)), key=lambda i: xs[i])
    out, i = [0.0] * len(xs), 0
    while i < len(order):
        j = i
        while j + 1 < len(order) and xs[order[j + 1]] == xs[order[i]]:
            j += 1
        for k in range(i, j + 1):
            out[order[k]] = (i + j) / 2 + 1
        i = j + 1
    return out


def pearson(x, y):
    n = len(x)
    if n < 2:
        return None
    mx, my = sum(x) / n, sum(y) / n
    sxx, syy = sum((a - mx) ** 2 for a in x), sum((b - my) ** 2 for b in y)
    if sxx == 0 or syy == 0:
        return None
    return sum((a - mx) * (b - my) for a, b in zip(x, y)) / math.sqrt(sxx * syy)


def spearman(x, y):
    return pearson(avg_ranks(x), avg_ranks(y))


def kendall_tau_b(x, y):
    conc = disc = tx = ty = 0
    for i in range(len(x)):
        for j in range(i + 1, len(x)):
            dx, dy = (x[i] > x[j]) - (x[i] < x[j]), (y[i] > y[j]) - (y[i] < y[j])
            if dx == 0 and dy == 0:
                continue
            if dx == 0:
                tx += 1
            elif dy == 0:
                ty += 1
            elif dx == dy:
                conc += 1
            else:
                disc += 1
    denom = math.sqrt((conc + disc + tx) * (conc + disc + ty))
    return (conc - disc) / denom if denom else None


def wilson(k, n, z=1.959964):
    if not n:
        return None
    p, d = k / n, 1 + z * z / n
    c, h = (p + z * z / (2 * n)) / d, z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return [round(c - h, 4), round(c + h, 4)]


def fisher_ci(r, n, z=1.959964):
    """Spearman's rho, 95%: Fisher's z with Fieller's variance 1.06 / (n - 3)."""
    if r is None or n < 5 or abs(r) >= 1:
        return None
    zr, se = math.atanh(r), math.sqrt(1.06 / (n - 3))
    return [round(math.tanh(zr - z * se), 4), round(math.tanh(zr + z * se), 4)]


def weighted_kappa(a, b, k):
    """Cohen's kappa with linear weights, two ratings on 0..k-1."""
    n = len(a)
    if not n:
        return None
    w = [[abs(i - j) / (k - 1) for j in range(k)] for i in range(k)]
    pa = [sum(1 for x in a if x == i) / n for i in range(k)]
    pb = [sum(1 for x in b if x == i) / n for i in range(k)]
    expected = sum(pa[i] * pb[j] * w[i][j] for i in range(k) for j in range(k))
    observed = sum(w[x][y] for x, y in zip(a, b)) / n
    return None if expected == 0 else 1 - observed / expected


def r4(x):
    return None if x is None else round(x, 4)


def agreement(gold, lab, k):
    """Exact and within-one agreement, Spearman, Kendall, weighted kappa and the confusion table, gold on 0..k-1 and the
    labeler already on the same scale."""
    n = len(gold)
    exact = sum(1 for g, x in zip(gold, lab) if g == x)
    near = sum(1 for g, x in zip(gold, lab) if abs(g - x) <= 1)
    rho = spearman(lab, gold)
    return {"n": n, "exact": r4(exact / n) if n else None, "exact_ci": wilson(exact, n),
            "within_one": r4(near / n) if n else None, "within_one_ci": wilson(near, n),
            "spearman": r4(rho), "spearman_ci": fisher_ci(rho, n), "kendall_tau_b": r4(kendall_tau_b(lab, gold)),
            "kappa_linear": r4(weighted_kappa(gold, lab, k))}


def confusion(gold, lab, gold_names, lab_values):
    """{gold value: {labeler value: count}}."""
    return {g: {str(v): sum(1 for a, b in zip(gold, lab) if a == gi and b == v) for v in lab_values}
            for gi, g in enumerate(gold_names)}


# ---------------------------------------------------------------- the validator

GRADE = {"N": 0, "P": 1, "R": 2}
MAP_A = {0: 0, 1: 0, 2: 1, 3: 2}      # primary, fixed before any label: rel 0,1 -> N; 2 -> P; 3 -> R
MAP_B = {0: 0, 1: 1, 2: 1, 3: 2}      # the alternative: rel 0 -> N; 1,2 -> P; 3 -> R


def gold_pairs(items, gold_rows, s1_all):
    """[(source, gold value, item, candidate or None, why)] for every gold section: the sections of S1-RATE's `scored`
    rows (S1RATE_CAVEAT) and S1-ALL's labels."""
    by_id = {it["id"]: it for it in items}
    prompts = [it for it in items if it["kind"] == "prompt"]
    out = []
    for r in gold_rows:
        if r["status"] != "scored":
            continue
        if r["event"] == "UserPromptSubmit":
            it = link_prompt(prompts, r["session"], r["time"])
        else:
            it = by_id.get("t-%s" % r["tool_use_id"]) if r["tool_use_id"] else None
        for s in r["sections"]:
            gold = {"rel": r["rel"], "use": r["use"], "injection": r["id"], "sha": s["sha"]}
            if it is None:
                out.append(("s1-rate", gold, None, None, "no item"))
                continue
            cands = [c for c in it["candidates"] if c["skill"] == s["skill"] and c["heading"] == s["heading"]]
            cands.sort(key=lambda c: (c["sha"] != s["sha"], c["source"] != "row", c["rank"] or 0))
            out.append(("s1-rate", gold, it, cands[0] if cands else None, None if cands else "no section"))
    by_pid = collections.defaultdict(list)
    for it in prompts:
        by_pid[prompt_link(it)].append(it)
    for pid, skill, grade in s1_all:
        its = by_pid.get(pid, [])
        if len(its) != 1:
            out.append(("s1-all", {"grade": grade, "pid": pid, "skill": skill}, None, None,
                        "no item" if not its else "ambiguous"))
            continue
        cands = sorted((c for c in its[0]["candidates"] if c["skill"] == skill and c["source"] == "rank"),
                       key=lambda c: c["rank"])
        out.append(("s1-all", {"grade": grade, "pid": pid, "skill": skill}, its[0], cands[0] if cands else None,
                    None if cands else "no section"))
    return out


def validate(items, labels, gold_rows, s1_all, backend, rubric):
    """The agreement numbers per gold source (ids and counts only)."""
    pairs = gold_pairs(items, gold_rows, s1_all)
    res = {}
    for src in ("s1-rate", "s1-all"):
        mine = [p for p in pairs if p[0] == src]
        counts = collections.Counter(why or "joined" for _, _, _, _, why in mine)
        got = []
        for _, gold, it, cand, why in mine:
            if why:
                continue
            rec = labels.get(label_key(it["id"], cand["sha"], backend, rubric))
            if rec is None:
                counts["unlabeled"] += 1
            elif rec.get("status") not in LABELED:
                counts["malformed"] += 1
            else:
                counts["labeled"] += 1
                if rec["status"] == "reparsed":
                    counts["labeled_reparsed"] += 1
                got.append((gold, cand, rec))
        out = {"gold": len(mine), "counts": dict(counts)}
        if src == "s1-rate":
            out["caveat"] = S1RATE_CAVEAT
            out["rows_by_status"] = dict(collections.Counter(str(r.get("status")) for r in gold_rows))
            out["injections"] = len({g["injection"] for _, g, _, _, _ in mine})
            rels = [g["rel"] for _, g, _, _, _ in mine]
            out["gold_rel"] = dict(collections.Counter(str(v) for v in rels))
            if rels:    # what a constant answer scores: the most common rel, and the median within one
                med = statistics.median_low(rels)
                out["constant_baseline"] = {"majority_exact": r4(max(collections.Counter(rels).values()) / len(rels)),
                                            "median": med,
                                            "median_within_one": r4(sum(abs(v - med) <= 1 for v in rels) / len(rels))}
            if got:
                g, x = [a["rel"] for a, _, _ in got], [r["rel"] for _, _, r in got]
                out["rel"] = dict(agreement(g, x, 4), confusion=confusion(g, x, ["0", "1", "2", "3"], range(4)))
                gu, xu = [a["use"] for a, _, _ in got], [r["use"] for _, _, r in got]
                out["use"] = dict(agreement(gu, xu, 4), confusion=confusion(gu, xu, ["0", "1", "2", "3"], range(4)))
                out["same_text"] = sum(1 for a, c, _ in got if c["sha"] == a["sha"])
        else:
            out["gold_grade"] = dict(collections.Counter(g["grade"] for _, g, _, _, _ in mine))
            scored = [(GRADE[g["grade"]], c) for _, g, _, c, why in mine if not why]
            if scored:
                gg = [a for a, _ in scored]
                out["plain_order"] = {"n": len(scored),
                                      "spearman_hook_score": r4(spearman([c["score"] for _, c in scored], gg)),
                                      "spearman_gate": r4(spearman([int(c["gate"]) for _, c in scored], gg)),
                                      "spearman_rank": r4(spearman([-c["rank"] for _, c in scored], gg)),
                                      "majority_exact": r4(max(collections.Counter(gg).values()) / len(gg))}
            if got:
                g = [GRADE[a["grade"]] for a, _, _ in got]
                raw = [r["rel"] for _, _, r in got]
                out["rel_spearman_raw"] = r4(spearman(raw, g))
                out["rel_spearman_raw_ci"] = fisher_ci(spearman(raw, g), len(g))
                out["map_a"] = agreement(g, [MAP_A[v] for v in raw], 3)
                out["map_b"] = agreement(g, [MAP_B[v] for v in raw], 3)
                out["confusion_raw"] = confusion(g, raw, ["N", "P", "R"], range(4))
                plain = spearman([c["score"] for _, c, _ in got], g)
                out["plain_order_same_pairs"] = r4(plain)
                ci = out["rel_spearman_raw_ci"]      # D-074: a model must beat the plain order, here by its CI
                out["beats_plain_order"] = bool(ci and plain is not None and ci[0] > plain)
        res[src] = out
    return res


def cmd_validate(args):
    items, sections, manifest = load_candidates(args.candidates)
    labels = {}
    if args.labels:
        recs, _ = read_labels(args.labels)
        labels = {k: v for k, v in recs.items() if v.get("backend") == args.backend and v.get("rubric") == args.rubric}
    gold_rows = s1_rate_rows(args.transcript, args.jev)
    s1_all = parse_appendix_e(args.s1_all) if args.s1_all else []
    res = validate(items, labels, gold_rows, s1_all, args.backend, args.rubric)
    res["labels"] = {"file": args.labels, "backend": args.backend, "rubric": args.rubric, "records": len(labels)}
    text = json.dumps(res, indent=1, sort_keys=True)
    if args.out:
        with open(args.out, "w", encoding="utf-8") as fh:
            fh.write(text + "\n")
    print(text)
    return 0


# ---------------------------------------------------------------- the dataset

def dataset_rows(items, sections, labels, backend, rubric, fitter=None):
    """(rows, label records, counts): two rows per LABELED label (ok or reparsed, alike; QUESTIONS), in
    build_dataset.make_row's shape, and one teacher_label-shaped record per row."""
    sys.path.insert(0, HERE)
    from laya_ft import common as C
    from laya_ft import fit as FIT
    by_id = {it["id"]: it for it in items}
    rows, recs, keyed = [], [], {}
    counts = collections.Counter()
    for key in sorted(labels):
        lab = labels[key]
        if lab.get("backend") != backend or lab.get("rubric") != rubric or lab.get("status") not in LABELED:
            continue
        it, sec = by_id.get(lab["item"]), sections.get(lab["section"])
        if it is None or sec is None:
            counts["label_without_candidate"] += 1
            continue
        if lab["status"] == "reparsed":
            counts["labels_reparsed"] += 1
        state = {"query": step_text(it), "chunk": sec["text"]}
        for qid, value, dist in (("skill.governs", lab["rel"], lab.get("target_rel")),
                                 ("skill.helps", lab["use"], lab.get("target_use"))):
            q = QUESTIONS[qid]
            try:
                st, cut = fitter.fit(state, q) if fitter is not None else (state, None)
            except FIT.Unfit:                          # the section alone overflows Laya's window: no row
                counts["unfit." + qid] += 1
                continue
            ssha = C.state_sha(st)
            row = {"item_id": "s1-%s" % ssha[:20], "question_id": qid, "question_sha": C.question_sha(q),
                   "state_sha": ssha, "options": C.options(q), "question": q, "state": st,
                   "sources": [{"kind": "transcript", "item": it["id"], "section": sec["sha"], "skill": sec["skill"],
                                "heading": sec["heading"], "label": key}]}
            if cut:
                row["cut"] = cut
                counts["cut." + qid] += 1
            k = C.label_key(row["item_id"], qid)
            target = dist if dist is not None else [1.0 if i == value else 0.0 for i in range(4)]
            if k in keyed:
                keyed[k]["sources"] += row["sources"]
                counts["merged_duplicates"] += 1
                counts["conflicts"] += keyed[k]["_value"] != value
                continue
            row["_value"] = value
            keyed[k] = row
            rows.append(row)
            recs.append({"key": k, "item_id": row["item_id"], "question_id": qid, "question_sha": row["question_sha"],
                         "sent_state_sha": ssha, "labeled_state_sha": C.state_sha(state), "options": row["options"],
                         "target": target, "answer": {"choice": row["options"][value]}, "model": lab.get("model"),
                         "endpoint": lab.get("endpoint"), "input_tokens": lab.get("prompt_tokens") or
                         lab.get("input_tokens") or 0, "attempts": lab.get("attempts"), "ts": lab.get("ts"),
                         "backend": backend, "rubric": rubric, "synth_key": key})
            counts["rows." + qid] += 1
            counts["answer.%s.%s" % (qid, row["options"][value])] += 1
    for row in rows:
        row.pop("_value")
    return rows, recs, counts


def cmd_dataset(args, sources):
    sys.path.insert(0, HERE)
    from laya_ft import common as C
    items, sections, cman = load_candidates(args.candidates)
    recs, _ = read_labels(args.labels)
    fitter = None
    if args.model_dir:
        from laya_ft import build_dataset as BD
        fitter = BD.Fitter(args.model_dir)
    rows, labs, counts = dataset_rows(items, sections, recs, args.backend, args.rubric, fitter)
    body = "".join(json.dumps(r, ensure_ascii=True) + "\n" for r in rows).encode("ascii")
    labels_b = "".join(json.dumps(r, ensure_ascii=True, sort_keys=True) + "\n" for r in labs).encode("ascii")
    manifest = {"kind": "s1-synth-dataset", "version": 1, "backend": args.backend, "rubric": args.rubric,
                "rubric_sha": RUBRIC_SHA, "candidates": {"manifest_sha256": sha256(open(os.path.join(
                    args.candidates, MANIFEST), "rb").read()), "files": cman["files"]},
                "labels": {"file": os.path.basename(args.labels), "sha256": sha256(open(args.labels, "rb").read())},
                "counts": {"rows_total": len(rows), **{k: v for k, v in sorted(counts.items())}},
                "fitted": fitter is not None, "model": fitter.fingerprint if fitter is not None else None,
                "questions": {qid: C.question_sha(q) for qid, q in QUESTIONS.items()},
                "code": {p: sha256(open(os.path.join(ROOT, p), "rb").read()) for p in CODE},
                "dataset": {"file": C.DATASET_FILE, "sha256": sha256(body), "bytes": len(body)},
                "label_file": {"file": "labels.jsonl", "sha256": sha256(labels_b), "lines": len(labs)}}
    mbytes = (json.dumps(manifest, indent=1, sort_keys=True) + "\n").encode("ascii")
    try:
        write_files(args.out, [(C.DATASET_FILE, body), (C.MANIFEST_FILE, mbytes), ("labels.jsonl", labels_b)], sources)
    except TE.KnownValueRefusal as e:
        for line in e.args[0]:
            print("s1_synth: REFUSED, nothing written: " + line, file=sys.stderr)
        return 4
    if args.commit_dir:
        os.makedirs(args.commit_dir, exist_ok=True)
        for name, data in (("dataset-manifest.json", mbytes), ("labels.jsonl", labels_b)):
            with open(os.path.join(args.commit_dir, name), "wb") as fh:
                fh.write(data)
    print(json.dumps({"rows": len(rows), "labels": len(labs), "counts": dict(sorted(counts.items())),
                      "dataset_sha256": manifest["dataset"]["sha256"]}, indent=1, sort_keys=True))
    return 0


# ---------------------------------------------------------------- the command line

def main(argv=None, clock=time.monotonic, sleep=time.sleep, post=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    c = sub.add_parser("candidates")
    c.add_argument("--transcript", required=True, help="the session's main transcript (its subagents/ read too)")
    c.add_argument("--out", help="the output directory (items.jsonl, sections.jsonl, manifest.json)")
    c.add_argument("--dry-run", action="store_true", help="write nothing; print counts only")
    c.add_argument("--sample", type=int, default=SAMPLE, help="tool calls to sample (default %d)" % SAMPLE)
    c.add_argument("--top", type=int, default=TOP, help="ranked sections per item (default %d)" % TOP)
    c.add_argument("--seed", type=int, default=SEED)
    c.add_argument("--jev", default=os.path.join(ROOT, ".jev"), help="the state directory (the S1-RATE join)")
    c.add_argument("--s1-all", default=S1_ALL_REPORT, help="S1-ALL's report (its Appendix E); '' for none")
    c.add_argument("--cache", help="the hook's index cache (default: a temporary file)")
    lab = sub.add_parser("label")
    lab.add_argument("--candidates", required=True)
    lab.add_argument("--out", required=True, help="the append-only labels JSONL")
    lab.add_argument("--backend", choices=("vllm", "openjev"), required=True)
    lab.add_argument("--concurrency", type=int, default=6, help="requests in flight (default 6)")
    lab.add_argument("--limit", type=int, default=None, help="label at most N pending pairs (a smoke run)")
    lab.add_argument("--rubric", default=RUBRIC_VERSION, choices=(RUBRIC_VERSION,))
    lab.add_argument("--url", default=VLLM_URL)
    lab.add_argument("--model", default=VLLM_MODEL)
    lab.add_argument("--key-file", default=VLLM_KEY_FILE, help="read in this process, never printed")
    lab.add_argument("--thinking", action="store_true", help="let the model think (default off)")
    lab.add_argument("--max-tokens", type=int, default=None,
                     help="default %d, or %d with --thinking" % (MAX_TOKENS, MAX_TOKENS_THINKING))
    lab.add_argument("--timeout", type=float, default=120.0)
    lab.add_argument("--env-file", default="/root/.codiv/api.env", help="openjev: TYPESAFE_BASE_URL and _API_KEY")
    v = sub.add_parser("validate")
    v.add_argument("--candidates", required=True)
    v.add_argument("--transcript", required=True)
    v.add_argument("--labels")
    v.add_argument("--backend", default="vllm", choices=("vllm", "openjev"))
    v.add_argument("--rubric", default=RUBRIC_VERSION)
    v.add_argument("--jev", default=os.path.join(ROOT, ".jev"))
    v.add_argument("--s1-all", default=S1_ALL_REPORT)
    v.add_argument("--out")
    d = sub.add_parser("dataset")
    d.add_argument("--candidates", required=True)
    d.add_argument("--labels", required=True)
    d.add_argument("--backend", required=True, choices=("vllm", "openjev"))
    d.add_argument("--rubric", default=RUBRIC_VERSION)
    d.add_argument("--out", required=True, help="dataset.jsonl, manifest.json, labels.jsonl (texts: scratch or PC)")
    d.add_argument("--model-dir", help="fit each state to Laya's window (the Laya venv's python)")
    d.add_argument("--commit-dir", help="the manifest and the labels only (no text), for the repo")
    args = ap.parse_args(argv)
    if args.cmd == "candidates":
        if not args.dry_run and not args.out:
            ap.error("candidates needs --out or --dry-run")
        if args.sample < 0 or args.top < 1:
            ap.error("--sample must be >= 0 and --top >= 1")
        return cmd_candidates(args, TE.KNOWN_VALUE_SOURCES)       # the module's tuple as it is now (SCRUB1 F1)
    if args.cmd == "label":
        if args.concurrency < 1 or (args.limit is not None and args.limit < 0) or (
                args.max_tokens is not None and args.max_tokens < 1):
            ap.error("--concurrency and --max-tokens must be >= 1, --limit >= 0")
        return cmd_label(args, clock, sleep, post)
    if args.cmd == "validate":
        return cmd_validate(args)
    return cmd_dataset(args, TE.KNOWN_VALUE_SOURCES)


if __name__ == "__main__":
    sys.exit(main())
