#!/usr/bin/env python3
"""Build the Laya S1 dataset: one row per scored System-1 injection (task #438; tasks/laya-s3-breakdown.md).

The question is `s1.inject` (noul, `common.S1_QUESTIONS`): is the injected context relevant to the agent's next step?
The label is the agent's own live score of the injection (S1-RATE, task #295): true when rel is 2 or 3. The state
(the breakdown's decision 1; SYNTH1's validator showed the tool input alone does not carry the score):
  task    the last prompt of the thread before the step: the owner's in the main thread, the coordinator's in a lane
  intent  the agent's last text before the step, its S1-RATE lines removed (they are the labels of other rows)
  step    the tool and its input (for an injection at prompt time: the prompt)
  kind    the injection's source, in words
  chunk   the injected text as the agent saw it, without the stamp line and the score request
Each field is scrubbed (`transcript_export.scrub_payload`), then capped in characters (the chunk at a line boundary),
then fitted to Laya's window by `laya_ft/fit.py` with the checkpoint's own tokenizer (it never cuts the chunk).

Only the tool INPUT and the texts the agent and the person wrote are read; never a tool result, never a thinking block.
`s1_scores.read_session` and `join_state` do the pairing (the ONE implementation); an injection whose text does not
match the sha256 the hook logged is refused. The split is by time: rows at or after the cutoff are held out. A state
in both splits leaves the training split; a state with two labels is dropped. Every drop is counted.

Out (outside git, e.g. .jev/laya-ft/s1-<day>/): train/ and heldout/, each with dataset.jsonl, manifest.json and
labels.jsonl in the shapes `common.load_dataset` and `common.join_labels` check; summary.json holds the counts and the
baselines a trained model must beat (no text). Run it with the Laya venv's python (the tokenizer); the known-values
check runs over the out directory before it leaves the sandbox.
"""
import argparse
import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))   # scripts/: laya_ft, s1_scores, hook_context
from laya_ft import common as C  # noqa: E402
from laya_ft import fit as FIT  # noqa: E402   (stdlib-only at import)
from laya_ft import recorded_labels as RL  # noqa: E402
import s1_scores as S  # noqa: E402   the ONE pairing of an injection with its score
from transcript_export import scrub_payload  # noqa: E402

QID = "s1.inject"
VERSION = "s1-v1"
CAPS = {"task": 300, "intent": 400, "step": 400, "chunk": 1000}   # characters, after the scrub, before the fit
KINDS = {"system1-context": "skill lines", "edit-snapshot": "the file's recent changes", "filepacks": "a file pack",
         "wiki-context": "a wiki excerpt", "search-intercept": "a code-search answer"}
NOT_A_PROMPT = ("<", "Caveat:", "[Request interrupted", "Stop hook feedback", "This session is being continued")
PROVENANCE = "s1-rate live score"
CODE = ("scripts/laya_ft/build_s1.py", "scripts/laya_ft/common.py", "scripts/laya_ft/fit.py",
        "scripts/laya_ft/recorded_labels.py", "scripts/s1_scores.py", "scripts/hook_context.py",
        "scripts/transcript_export.py")
ROOT_PREFIX = str(C.ROOT) + "/"


def prompt_of(r):
    """The text of a user record that is a prompt (the owner's, or the coordinator's to a lane), else None."""
    if r.get("type") != "user" or r.get("isMeta") or r.get("isCompactSummary"):
        return None
    c = (r.get("message") or {}).get("content")
    if isinstance(c, list):
        if any(isinstance(x, dict) and x.get("type") == "tool_result" for x in c):
            return None
        c = "\n".join(x["text"] for x in c if isinstance(x, dict) and x.get("type") == "text"
                      and isinstance(x.get("text"), str))
    if not isinstance(c, str) or not c.strip() or c.lstrip().startswith(NOT_A_PROMPT):
        return None
    return c.strip()


def intent_of(text):
    """An agent text without its S1-RATE lines (another row's label); None when nothing else is left."""
    kept = "\n".join(line for line in text.split("\n") if not S.ATTEMPT_RX.match(line)).strip()
    return kept or None


def tool_uses(r):
    msg = r.get("message") or {}
    return [b for b in msg.get("content") or [] if isinstance(b, dict) and b.get("type") == "tool_use"
            and isinstance(b.get("id"), str)]


def render_step(tool, inp):
    """A call as one text: the tool, then the input field that says what it does."""
    if not isinstance(inp, dict):
        body = json.dumps(inp, ensure_ascii=False)
    elif tool == "Bash":
        body = str(inp.get("command", ""))
    elif tool == "Read":
        body = str(inp.get("file_path", ""))
    elif tool == "Edit":
        body = "%s\n%s" % (inp.get("file_path", ""), inp.get("new_string", ""))
    elif tool == "Write":
        body = "%s\n%s" % (inp.get("file_path", ""), inp.get("content", ""))
    elif tool in ("Grep", "Glob"):
        body = " ".join(str(inp[k]) for k in ("pattern", "path", "glob", "type") if inp.get(k))
    else:
        body = json.dumps(inp, ensure_ascii=False, sort_keys=True)
    return ("%s: %s" % (tool, body)).replace(ROOT_PREFIX, "")


def files_of(paths):
    """Every transcript file the paths name, once. Overlapping paths (a main transcript brings its subagents/ files, so
    the main file and its session folder name the same files) stop the build: `s1_scores.read_session` would count
    every injection in them twice (measured 2026-10-01: 2,124 rows for 1,062 injections)."""
    files = []
    for path in paths:
        for fp in S.transcript_files(path):
            if os.path.realpath(fp) in map(os.path.realpath, files):
                raise SystemExit("build_s1: %s is read twice; give a main transcript or its folder, not both" % fp)
            files.append(fp)
    return files


def contexts(files):
    """({tool_use_id: {"tool", "input", "task", "intent"}}, {(agent, sid): {"stamped", "task", "intent"}}): every call
    and every stamped injection in the transcripts, each with the thread's last prompt and last agent text at that
    moment."""
    calls, injected = {}, {}
    for fp in files:
        threads = {}
        with open(fp, encoding="utf-8", errors="replace") as fh:
            for line in fh:
                try:
                    r = json.loads(line)
                except ValueError:
                    continue
                if not isinstance(r, dict):
                    continue
                agent = r.get("agentId") if isinstance(r.get("agentId"), str) else "main"
                th = threads.setdefault(agent, {"task": None, "intent": None})
                for kind, _ev, _tool, t, _cmd in S.injections_of(r):
                    st = S.stamp_of(kind, t)
                    if st is not None:
                        injected.setdefault((agent, st[0]), {"stamped": st[2], "task": th["task"],
                                                             "intent": th["intent"]})
                p = prompt_of(r)
                if p is not None:
                    th["task"] = p
                    continue
                text = S.text_of(r)
                if text is not None:
                    th["intent"] = intent_of(text) or th["intent"]
                if r.get("type") == "assistant":
                    for b in tool_uses(r):
                        calls.setdefault(b["id"], {"tool": b.get("name"), "input": b.get("input"),
                                                   "task": th["task"], "intent": th["intent"]})
    return calls, injected


def cap(text, n, at_line=False):
    """The head of `text` within n characters; at a line boundary when asked and the first line fits."""
    if len(text) <= n:
        return text
    if at_line:
        cut = text.rfind("\n", 0, n + 1)
        if cut > 0:
            return text[:cut]
    return text[:n]


def chunk_of(stamped, whole):
    lines = stamped.rstrip("\n").split("\n")
    return "\n".join(lines[1:-1] if whole else lines[1:])


def items_of(rows, calls, injected):
    """(items, drops): one item per scored injection whose text and step were found and whose sha256 matches."""
    items, drops = [], {}

    def drop(why):
        drops[why] = drops.get(why, 0) + 1

    for row in rows:
        if row.get("status") != "scored":
            continue
        inj = injected.get((row["agent"], row["id"]))
        if inj is None:
            drop("text_not_found")
            continue
        if row.get("sha_ok") is not True or hashlib.sha256(inj["stamped"].encode("utf-8")).hexdigest() != row.get(
                "_sha256"):
            drop("sha256_mismatch")
            continue
        if row.get("event") == "UserPromptSubmit":
            task, intent, step = "", inj["intent"], "prompt: %s" % (inj["task"] or "")
        else:
            call = calls.get(row.get("tool_use_id"))
            if call is None:
                drop("call_not_found")
                continue
            task, intent, step = call["task"], call["intent"], render_step(call["tool"], call["input"])
        state = {"task": cap(scrub_payload(task or ""), CAPS["task"]),
                 "intent": cap(scrub_payload(intent or ""), CAPS["intent"]),
                 "step": cap(scrub_payload(step), CAPS["step"]),
                 "kind": KINDS.get(row["source"], row["source"]),
                 "chunk": cap(scrub_payload(chunk_of(inj["stamped"], row.get("whole"))), CAPS["chunk"], at_line=True)}
        items.append({"time": row["time"], "state": state, "answer": "true" if row["rel"] >= 2 else "false",
                      "source": {"kind": "injection", "id": row["id"], "source": row["source"], "time": row["time"]}})
    return items, drops


class Fitter:
    """Laya's window from the checkpoint (as build_dataset.Fitter), every cut kept: an S1 state has several texts."""

    def __init__(self, model_dir):
        from laya.agent import Agent
        from transformers import AutoTokenizer

        self.fingerprint = C.model_fingerprint(Path(model_dir))
        self.max_len, self.head_max_len = self.fingerprint["max_len"], self.fingerprint["head_max_len"]
        self.tok = AutoTokenizer.from_pretrained(str(Path(model_dir) / "tokenizer"))
        self._internal = Agent._to_internal

    def fit(self, state, question):
        return FIT.fit_state(self.tok, self._internal(question), self.max_len, self.head_max_len, state)


def cutoffs_of(items, heldout_frac, cutoff=None):
    """{kind: ISO time}: rows of a kind at or after its cutoff are held out. Per kind, the newest fraction, so a kind
    that began late (the file packs began on 2026-09-30) is on both sides; one given cutoff applies to every kind."""
    times = {}
    for it in items:
        times.setdefault(it["state"]["kind"], []).append(it["time"])
    if cutoff is not None:
        return {k: cutoff for k in sorted(times)}
    return {k: sorted(v)[min(len(v) - 1, int(len(v) * (1 - heldout_frac)))] for k, v in sorted(times.items())}


def split_rows(items, fitter, cutoffs):
    """(train, heldout, counts): fitted rows, one per distinct state; a state with two labels is dropped, a state on
    both sides of its kind's cutoff is held out only."""
    q = C.S1_QUESTIONS[QID]
    groups, order, counts = {}, [], {"unfit": 0, "cut_to_window": 0}
    for it in items:
        try:
            state, cuts = fitter.fit(it["state"], q)
        except FIT.Unfit:
            counts["unfit"] += 1
            continue
        counts["cut_to_window"] += bool(cuts)
        ssha = C.state_sha(state)
        g = groups.get(ssha)
        if g is None:
            g = groups[ssha] = {"state": state, "cuts": cuts, "answers": set(), "sources": [], "sides": set()}
            order.append(ssha)
        g["answers"].add(it["answer"])
        g["sources"].append(it["source"])
        g["sides"].add("heldout" if it["time"] >= cutoffs[it["state"]["kind"]] else "train")
    out = {"train": [], "heldout": []}
    counts.update(conflicting_states=0, cross_split_states=0, merged_duplicates=0)
    for ssha in order:
        g = groups[ssha]
        if len(g["answers"]) > 1:
            counts["conflicting_states"] += 1
            continue
        counts["merged_duplicates"] += len(g["sources"]) - 1
        if len(g["sides"]) > 1:
            counts["cross_split_states"] += 1
        side = "heldout" if "heldout" in g["sides"] else "train"
        row = {"item_id": "s1-%s" % ssha[:20], "question_id": QID, "question_sha": C.question_sha(q),
               "state_sha": ssha, "options": C.options(q), "question": q, "state": g["state"],
               "sources": sorted(g["sources"], key=lambda s: (s["time"], s["id"]))}
        if g["cuts"]:
            row["cut"] = [{"field": f, "chars_from": a, "chars_to": b} for f, a, b in g["cuts"]]
        out[side].append((row, g["answers"].pop()))
    return out["train"], out["heldout"], counts


def baselines(train, heldout):
    """Held-out accuracy of the rules a trained model must beat, each fitted on the training split only."""
    def acc(pred):
        return round(sum(pred(r) == a for r, a in heldout) / len(heldout), 4) if heldout else None

    def majority(pairs):
        t = sum(a == "true" for _r, a in pairs)
        return "true" if 2 * t >= len(pairs) else "false"

    overall = majority(train) if train else "true"
    by_kind = {}
    for r, a in train:
        by_kind.setdefault(r["state"]["kind"], []).append((r, a))
    prior = {k: majority(v) for k, v in by_kind.items()}

    def words(text):
        return {w for w in "".join(c.lower() if c.isalnum() else " " for c in text).split() if len(w) > 2}

    def overlap(r):
        chunk = words(r["state"]["chunk"])
        return len(chunk & words(r["state"]["step"] + " " + r["state"]["intent"])) / len(chunk) if chunk else 0.0

    best = (0.0, -1.0)   # (threshold, train accuracy): the threshold that fits the training split best
    for th in sorted({round(overlap(r), 4) for r, _a in train}):
        a = sum(("true" if overlap(r) >= th else "false") == ans for r, ans in train) / len(train)
        if a > best[1]:
            best = (th, a)
    return {"always_true": acc(lambda r: "true"),
            "majority": {"answer": overall, "accuracy": acc(lambda r: overall)},
            "kind_prior": {"rule": prior, "accuracy": acc(lambda r: prior.get(r["state"]["kind"], overall))},
            "word_overlap": {"threshold": best[0], "accuracy": acc(lambda r: "true" if overlap(r) >= best[0] else "false")}}


def git_head(repo):
    try:
        return subprocess.run(["git", "-C", str(repo), "rev-parse", "HEAD"], capture_output=True, text=True,
                              check=True).stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        return None


def write_split(out, name, pairs, base, ts):
    rows = [r for r, _a in pairs]
    data = "".join(C.dumps(r) + "\n" for r in rows).encode("utf-8")
    labels = "".join(C.dumps(RL.label_record(r, a, PROVENANCE, ts)) + "\n" for r, a in pairs).encode("utf-8")
    manifest = dict(base, split=name, dataset={"file": C.DATASET_FILE, "sha256": C.sha256_hex(data)},
                    labels={"file": "labels.jsonl", "sha256": C.sha256_hex(labels)},
                    counts={"rows_total": len(rows), "true": sum(a == "true" for _r, a in pairs),
                            "false": sum(a == "false" for _r, a in pairs)})
    d = Path(out) / name
    d.mkdir(parents=True, exist_ok=True)
    for fname, blob in ((C.DATASET_FILE, data), ("labels.jsonl", labels),
                        (C.MANIFEST_FILE, (json.dumps(manifest, indent=1, sort_keys=True) + "\n").encode("utf-8"))):
        tmp = d / (fname + ".tmp")
        tmp.write_bytes(blob)
        os.replace(tmp, d / fname)
    return manifest


def build(paths, jev, out, fitter, cutoff=None, heldout_frac=0.2):
    files = files_of(paths)
    rows, _counts = S.read_session(paths)
    joined = S.join_state(rows, jev)
    calls, injected = contexts(files)
    items, drops = items_of(rows, calls, injected)
    if not items:
        raise SystemExit("build_s1: no scored injection could be built (drops: %s)" % drops)
    cutoff = cutoffs_of(items, heldout_frac, cutoff)
    train, heldout, counts = split_rows(items, fitter, cutoff)
    base = {"version": VERSION, "commit": git_head(C.ROOT), "cutoff": cutoff, "question": {QID: C.question_sha(
        C.S1_QUESTIONS[QID])}, "caps": CAPS, "model": fitter.fingerprint,
        "code": {p: C.sha256_hex((C.ROOT / p).read_bytes()) for p in CODE}}
    ts = max(it["time"] for it in items)
    manifests = {name: write_split(out, name, pairs, base, ts) for name, pairs in (("train", train),
                                                                                    ("heldout", heldout))}
    scored = sum(r.get("status") == "scored" for r in rows)
    summary = {"version": VERSION, "commit": base["commit"], "cutoff": cutoff, "question": base["question"],
               "scored_injections": scored, "items": len(items), "dropped": drops, "fit": counts,
               "join": joined, "splits": {k: {"rows": m["counts"], "dataset_sha256": m["dataset"]["sha256"],
                                              "labels_sha256": m["labels"]["sha256"]} for k, m in manifests.items()},
               "by_kind": {name: _by_kind(pairs) for name, pairs in (("train", train), ("heldout", heldout))},
               "baselines_on_heldout": baselines(train, heldout), "code": base["code"], "model": base["model"]}
    Path(out, "summary.json").write_text(json.dumps(summary, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    return summary


def _by_kind(pairs):
    out = {}
    for r, a in pairs:
        k = out.setdefault(r["state"]["kind"], {"true": 0, "false": 0})
        k[a] += 1
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    ap.add_argument("paths", nargs="+", help="a main transcript, a session directory, or one .jsonl")
    ap.add_argument("--jev", default=str(C.ROOT / ".jev"), help="the state directory with injections.jsonl")
    ap.add_argument("--out", required=True)
    ap.add_argument("--model-dir", default=C.DEFAULT_MODEL_DIR)
    ap.add_argument("--cutoff", help="ISO time: rows at or after it are held out (default: each kind's newest fifth)")
    ap.add_argument("--heldout-frac", type=float, default=0.2)
    args = ap.parse_args(argv)
    if not Path(args.jev, "injections.jsonl").is_file():   # AF-AP-235: a folder without the file joins nothing
        ap.error("--jev %s holds no injections.jsonl" % args.jev)
    if not 0.0 < args.heldout_frac < 1.0:
        ap.error("--heldout-frac must be between 0 and 1")
    summary = build(args.paths, args.jev, args.out, Fitter(args.model_dir), args.cutoff, args.heldout_frac)
    print(json.dumps({k: summary[k] for k in ("scored_injections", "items", "dropped", "fit", "splits",
                                              "baselines_on_heldout")}, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
