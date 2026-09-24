#!/usr/bin/env python3
"""Label the Laya fine-tune dataset with a teacher System One API: OpenJev on codiv.ai (D-075, D-078; brief FT1 D-5).

  teacher_label.py --dataset DIR --out LABELS.jsonl [--env-file /root/.codiv/api.env] [--limit N] [--questions a,b]

One request per (item, question): POST <TYPESAFE_BASE_URL>/v1/systemone with model `openjev-latest` and {state, questions},
the wire format of docs/research/findings/j2b-variants/openjev_j2.py. Every string in the body (keys included) passes
transcript_export.scrub first. The answer's full probability distribution (a choice's `probabilities` in option order, a
noul's [1 - p, p]) is validated and appended as the soft target to an append-only JSONL keyed by (item id, question id),
beside the digests of the state and question as sent; a rerun skips done keys. Pending keys are taken round-robin across
the question ids, so a small --limit covers every question type. At most 60 requests in any 60 s window and at least 1 s
apart (codiv's limit is 60 per minute per key; a retry is a request); 429 and 5xx retry with backoff (Retry-After when the
server sends one). The key is read from the env file in this process: never from argv, never printed, never logged (every
message is redacted of it). An ordinary User-Agent (codiv's Cloudflare refuses Python's default with 403 "error code:
1010"). The usage totals print at the end, also after a failure.
Exit: 0 done; 3 the API refused (a non-retryable status, or retries spent); 4 a malformed answer (not stored);
64 usage (a bad argument, or the env file lacks a name); 75 another run holds the labels file.
"""
import argparse
import collections
import fcntl
import http.client
import itertools
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))   # scripts/: the laya_ft package
from laya_ft import common as C  # noqa: E402

MODEL = "openjev-latest"
DEFAULT_ENV = "/root/.codiv/api.env"
USER_AGENT = "python-httpx/0.28.1"   # the value openjev_j2.py sends, which codiv's edge accepts
PER_WINDOW, WINDOW_S, MIN_GAP_S = 60, 60.0, 1.0
RETRY_STATUS = frozenset([429, 500, 502, 503, 504])
MAX_ATTEMPTS = 7
MAX_RETRY_AFTER_S = 120.0


class Refused(Exception):
    """The API refused: a non-retryable status, or every attempt spent."""


class Limiter:
    """Admit a request only when fewer than `per_window` were admitted in the last `window` seconds and the last one is
    at least `min_gap` seconds old. `clock` and `sleep` are injectable (tests run on a fake clock)."""

    def __init__(self, clock, sleep, per_window=PER_WINDOW, window=WINDOW_S, min_gap=MIN_GAP_S):
        self.clock, self.sleep = clock, sleep
        self.per_window, self.window, self.min_gap = per_window, window, min_gap
        self.admitted = collections.deque()

    def admit(self):
        while True:
            now = self.clock()
            while self.admitted and now - self.admitted[0] >= self.window:
                self.admitted.popleft()
            waits = []
            if self.admitted and now - self.admitted[-1] < self.min_gap:
                waits.append(self.min_gap - (now - self.admitted[-1]))
            if len(self.admitted) >= self.per_window:
                waits.append(self.window - (now - self.admitted[0]))
            if not waits:
                self.admitted.append(now)
                return
            self.sleep(max(waits))


def read_env(path):
    """KEY=VALUE lines -> dict (the openjev_j2.py reading). The values are never printed."""
    pairs = (line.split("=", 1) for line in Path(path).read_text(encoding="utf-8").splitlines() if "=" in line)
    env = {k.strip(): v.strip() for k, v in pairs}
    for name in ("TYPESAFE_BASE_URL", "TYPESAFE_API_KEY"):
        if not env.get(name):
            raise SystemExit("teacher_label: %s names no %s" % (path, name))
    return env


def scrubbed(value):
    """Every string in the request, keys included, through transcript_export.scrub; other JSON types unchanged."""
    if isinstance(value, str):
        return C.scrub(value)
    if isinstance(value, dict):
        return {scrubbed(k): scrubbed(v) for k, v in value.items()}
    if isinstance(value, list):
        return [scrubbed(v) for v in value]
    return value


def schedule(rows, done, wanted):
    """Pending rows in dataset order, taken round-robin across the question ids (sorted)."""
    groups = collections.defaultdict(list)
    for row in rows:
        if row["question_id"] in wanted and C.label_key(row["item_id"], row["question_id"]) not in done:
            groups[row["question_id"]].append(row)
    order = []
    for batch in itertools.zip_longest(*(groups[q] for q in sorted(groups))):
        order.extend(r for r in batch if r is not None)
    return order


def http_post(url, data, key, timeout):
    """-> (status, body bytes, headers). Non-2xx comes back as a status, never as an exception."""
    req = urllib.request.Request(url, data=data, method="POST", headers={
        "Content-Type": "application/json", "User-Agent": USER_AGENT, "Authorization": "Bearer " + key})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.status, r.read(), dict(r.headers)
    except urllib.error.HTTPError as e:
        return e.code, e.read(600), dict(e.headers or {})


class Client:
    def __init__(self, env, clock=time.monotonic, sleep=time.sleep, post=http_post, timeout=120.0):
        self.url = env["TYPESAFE_BASE_URL"].rstrip("/") + "/v1/systemone"
        self.endpoint = urllib.parse.urlsplit(self.url).netloc
        self._key = env["TYPESAFE_API_KEY"]
        self.limiter, self.sleep, self.post, self.timeout = Limiter(clock, sleep), sleep, post, timeout
        self.usage = {"requests": 0, "retries": 0, "answers": 0, "input_tokens": 0}

    def safe(self, text):
        """A message fit to print: the key replaced, then scrubbed."""
        return C.scrub(str(text).replace(self._key, "<key>"))

    def ask(self, body):
        data = json.dumps(body).encode("utf-8")
        for attempt in range(MAX_ATTEMPTS):
            self.limiter.admit()
            self.usage["requests"] += 1
            try:
                status, raw, headers = self.post(self.url, data, self._key, self.timeout)
            except (urllib.error.URLError, OSError, http.client.HTTPException) as e:   # connection, timeout: retry
                status, raw, headers, why = None, b"", {}, "%s: %s" % (type(e).__name__, e)
            else:
                if 200 <= status < 300:
                    try:
                        out = json.loads(raw)
                    except ValueError:
                        raise C.LabelError("the response is not JSON")
                    if not isinstance(out, dict):
                        raise C.LabelError("the response is not a JSON object")
                    self.usage["input_tokens"] += input_tokens(out)
                    return out, attempt + 1
                why = "HTTP %d: %s" % (status, raw[:300].decode("utf-8", "replace"))
                if status not in RETRY_STATUS:
                    raise Refused(self.safe(why))
            if attempt + 1 == MAX_ATTEMPTS:
                raise Refused(self.safe("gave up after %d attempts; last: %s" % (MAX_ATTEMPTS, why)))
            self.usage["retries"] += 1
            wait = min(60.0, 2.0 ** (attempt + 1))
            retry_after = {k.lower(): v for k, v in headers.items()}.get("retry-after")
            try:
                wait = min(MAX_RETRY_AFTER_S, max(wait, float(retry_after))) if retry_after is not None else wait
            except ValueError:
                pass
            self.sleep(wait)
        raise AssertionError("unreachable")


def input_tokens(out):
    n = (out.get("usage") or {}).get("input_tokens") if isinstance(out.get("usage"), dict) else None
    return int(n) if isinstance(n, (int, float)) and not isinstance(n, bool) else 0


def label_row(client, row):
    """Ask the teacher one row's question. -> the label record (not yet written)."""
    qid, question = row["question_id"], row["question"]
    body = {"model": MODEL, "state": scrubbed(row["state"]), "questions": {qid: scrubbed(question)}}
    out, attempts = client.ask(body)
    answers = out.get("answers") if isinstance(out, dict) else None
    if not isinstance(answers, dict) or qid not in answers:
        raise C.LabelError("the response has no answer for %s" % qid)
    target = C.distribution(answers[qid], question)
    client.usage["answers"] += 1
    return {"key": C.label_key(row["item_id"], qid), "item_id": row["item_id"], "question_id": qid,
            "question_sha": C.question_sha(body["questions"][qid]), "sent_state_sha": C.state_sha(body["state"]),
            "options": C.options(question), "target": target, "answer": answers[qid], "model": out.get("model"),
            "endpoint": client.endpoint, "input_tokens": input_tokens(out),
            "attempts": attempts, "ts": round(time.time(), 3)}


def main(argv=None, clock=time.monotonic, sleep=time.sleep, post=http_post):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--dataset", required=True, help="a build_dataset.py output directory")
    ap.add_argument("--out", required=True, help="the append-only labels JSONL")
    ap.add_argument("--env-file", default=DEFAULT_ENV, help="KEY=VALUE file with TYPESAFE_BASE_URL and TYPESAFE_API_KEY")
    ap.add_argument("--limit", type=int, default=None, help="label at most N pending keys (smoke runs)")
    ap.add_argument("--questions", default=",".join(C.QUESTIONS), help="question ids to label (comma list)")
    ap.add_argument("--timeout", type=float, default=120.0)
    args = ap.parse_args(argv)
    wanted = set(args.questions.split(","))
    if not wanted <= set(C.QUESTIONS) or (args.limit is not None and args.limit < 0):
        ap.error("--questions must name %s; --limit must be >= 0" % sorted(C.QUESTIONS))
    try:
        env = read_env(args.env_file)
    except (SystemExit, OSError) as e:   # the message names the file, never a value
        print("teacher_label: %s" % e, file=sys.stderr)
        return 64
    rows, manifest = C.load_dataset(args.dataset)
    client = Client(env, clock=clock, sleep=sleep, post=post, timeout=args.timeout)
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    rc, stored, scrub_changed = 0, 0, 0
    with open(out, "a+", encoding="utf-8") as fh:
        try:
            fcntl.flock(fh, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            print("teacher_label: another run holds %s" % out, file=sys.stderr)
            return 75
        done, stats = C.read_labels(out)
        order = schedule(rows, set(done), wanted)
        todo = order if args.limit is None else order[:args.limit]
        fh.seek(0, os.SEEK_END)
        if fh.tell() and out.read_bytes()[-1:] != b"\n":   # a torn last line stays its own (skipped) line
            fh.write("\n")
        try:
            for row in todo:
                rec = label_row(client, row)
                scrub_changed += rec["sent_state_sha"] != row["state_sha"]
                fh.write(json.dumps(rec, ensure_ascii=True) + "\n")
                fh.flush()
                os.fsync(fh.fileno())
                stored += 1
                print("labeled %s type=%s k=%d attempts=%d input_tokens=%d" % (
                    rec["key"], row["question"]["type"], len(rec["target"]), rec["attempts"], rec["input_tokens"]),
                    flush=True)
        except Refused as e:
            print("teacher_label: refused: %s" % e, file=sys.stderr)
            rc = 3
        except C.LabelError as e:
            print("teacher_label: malformed answer, not stored: %s" % client.safe(e), file=sys.stderr)
            rc = 4
    u = client.usage
    print("usage: requests=%d retries=%d answers=%d input_tokens=%d stored=%d skipped_done=%d pending_left=%d "
          "scrub_changed=%d endpoint=%s dataset=%s" % (
              u["requests"], u["retries"], u["answers"], u["input_tokens"], stored, len(done),
              len(order) - stored, scrub_changed, client.endpoint, manifest["dataset"]["sha256"][:16]), flush=True)
    return rc


if __name__ == "__main__":
    sys.exit(main())
