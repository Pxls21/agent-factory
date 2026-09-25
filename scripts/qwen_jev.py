#!/usr/bin/env python3
"""The Qwen3.8-27B Jev adapter, DIRECT vLLM path (D-079, D-082, task #241): applies simple-jev's
v1 rules to the Qwen3.8-27B served by the owner's vLLM, without loading any model of its own.

The owner ruled (D-082): System 1 connects straight to its model server; OmniRoute stays for
System 2. The measured cause of QJ1's 12-token gap (docs/research/findings/j2b-variants/qwen27b/
TRANSPORT-2026-09-24.md) was that the OmniRoute path drops the final assistant turn's
`reasoning_content` before the template runs. Straight to vLLM the field is kept, and this
adapter does better than keep it: each compiled branch is sent to
`POST /v1/completions` as the compiler's OWN token ids, so the prompt is exact BY
CONSTRUCTION and parity is checked, not assumed.

  GET  /health           -> {ok, model, prompt_policy, revision, oracle_revision, tokenizer}
                           (`revision` is the lane's LANE_ID, D-7; the J2 runner checks it)
  GET  /v1/models       -> {data:[{id: <served id>}, ...]}
  POST /v1/systemone    -> the house wire contract (D-5): {model?, state, questions}
  POST /v1/classifier   -> same handler (D-5: both routes)

D-5 (the house wire contract, mirrored from scripts/laya_systemone_server.py): a request without a
`model` gets the served id; when every question id names a state.chunks id, each question sees only
its own chunk (the Laya per-chunk fan-out); the response carries answers keyed by question id,
usage, model, and fan_out.

D-3 (the transport, D-082): each compiled branch goes to /v1/completions with EXACTLY the keys
`model`, `prompt`, `max_tokens`, `temperature`, `logprobs`: `model` is the served id read from
GET /v1/models at start; `prompt` is the branch's token_ids (the list of ints the compiler
produced); `max_tokens` 1; `temperature` 0; `logprobs` 20. No echo, no prompt_logprobs (AF-AP-201),
no best_of, no n — a body carrying them cannot be built (the body is constructed by exactly one
function). The response's model must equal the id sent, or the answer is refused. Chat is not a
scoring path; the parity probe uses it as a cross-check only.

D-4 (parity, never assumed): usage.prompt_tokens must equal len(branch.token_ids), or the branch
is refused (not scored). Each label's logprob is read from choices[0].logprobs.top_logprobs[0]
(the dict, token string to logprob) by the label's decoded token
(tokenizer.decode([output_id])). A label absent from the 20 is BOUNDED (given the lowest logprob
shown, an upper bound on its probability) and named in the answer (bounded_labels); it is never
silently filled with a real value.

D-6 (the key): the vLLM key is read in process from a private file (default
~/.config/qwen-builder/api-key, 0600 under a 0700 directory; QWEN_JEV_KEY_FILE overrides the path
for tests). It rides the Authorization header only; it never appears in argv, a log line, an
error line, or a response.

D-7 (the port): the adapter refuses to start when its port is taken (a clear error, non-zero
exit) and never treats a listener it did not start as itself (AF-AP-33: QJ1's orphaned adapter
squatted 47420 after its lane died). It binds to prove ownership; a bind that fails exits
non-zero. The J2 runner checks /health's lane revision before its first request.

D-1 (the oracle, used never copied): this refuses to serve unless the pinned simple-jev checkout
HEAD equals advisory_jev_runtimes.simple-jev.revision in upstream.lock.yaml.
"""
import argparse
import json
import os
import socket
import subprocess
import sys
import urllib.error
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import ClassVar

SIMPLE_JEV = os.path.expanduser("~/simple-jev")
TOKENIZER_DIR = os.path.expanduser("~/qwen-jev-tokenizer")
UPSTREAM_LOCK = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "upstream.lock.yaml")
KEY_FILE_DEFAULT = os.path.expanduser("~/.config/qwen-builder/api-key")  # D-6: 0600 under a 0700 directory
VLLM_BASE_DEFAULT = "http://127.0.0.1:8080"  # D-3/D-082: straight to the model server
DEFAULT_PORT = 47420
MAX_BODY = 8 * 1024 * 1024

# The verified pin (D-1), populated by make_service before the server starts; the health
# endpoint reports it. The oracle is never served before this check passes.
_pin_actual = None


def _add_simple_jev_paths():
    """D-1: import common/ and hf-server/ from the pinned checkout (used, never copied)."""
    if SIMPLE_JEV not in sys.path:
        sys.path.insert(0, SIMPLE_JEV)
    hf = os.path.join(SIMPLE_JEV, "hf-server")
    if hf not in sys.path:
        sys.path.insert(0, hf)


# The oracle is imported once the pin is verified (main() verifies before construction).
# These are bound at call time via a module-level loader so the test double path can import without the pin.
_oracle = {}


def load_oracle():
    """Import the pinned simple-jev modules and return the names this adapter drives.

    D-1: import common and hf_prompt_policies from the pinned checkout. The pin itself is
    checked separately by verify_pin(); this only does the import.
    """
    _add_simple_jev_paths()
    import common  # noqa: F401  (the v1 prompt plan, request schema and response scoring)
    from common import build_response
    from common import ClassifierRequest
    from hf_prompt_policies import prepare_policy, restore_binary_noul
    from hf_server import PromptCompiler, unique_prompt_tokens
    _oracle["common"] = common
    _oracle["build_response"] = build_response
    _oracle["ClassifierRequest"] = ClassifierRequest
    _oracle["prepare_policy"] = prepare_policy
    _oracle["restore_binary_noul"] = restore_binary_noul
    _oracle["PromptCompiler"] = PromptCompiler
    _oracle["unique_prompt_tokens"] = unique_prompt_tokens
    return _oracle


def read_key(key_file):
    """D-6: read the key from a private file. The caller controls the path (the test uses a FAKE
    file). The value is returned to the caller and is never logged, put in argv, or written to
    a response or an error line."""
    path = os.path.expanduser(key_file or KEY_FILE_DEFAULT)
    with open(path) as fh:
        value = fh.read().strip()
    if not value:
        raise RuntimeError("empty key at %s" % path)
    return value


def read_served_id(vllm_base, key):
    """D-3: the served id is read from GET /v1/models at start. Exactly one id ending in -local
    is the local serving (the premise: qwen3.8-27b-local); a single-entry list is taken as is;
    any other mix is a refusal, not a guess."""
    req = urllib.request.Request(vllm_base + "/v1/models",
                                 headers={"Authorization": "Bearer " + key})
    with urllib.request.urlopen(req, timeout=30) as r:
        ids = [m["id"] for m in json.loads(r.read()).get("data", [])]
    local = [i for i in ids if i.endswith("-local")]
    if len(local) == 1:
        return local[0]
    if len(ids) == 1:
        return ids[0]
    raise RuntimeError("cannot pick the served id from %s: expected exactly one -local entry" % ids)


def verify_pin():
    """D-1: refuse to serve unless the checkout HEAD equals upstream.lock.yaml advisory_jev_runtimes.
    Returns (ok, revision_expected, revision_actual, reason). A mismatch is a hard refusal, not a fallback."""
    try:
        actual = subprocess.run(
            ["git", "-C", SIMPLE_JEV, "rev-parse", "HEAD"],
            capture_output=True, text=True, timeout=30).stdout.strip()
    except Exception as e:  # no git / not a checkout
        return False, None, None, "cannot read the pinned checkout: %s: %s" % (type(e).__name__, e)
    expected = None
    try:
        import yaml  # present in the venv (PyYAML is a simple-jev dependency)
        with open(UPSTREAM_LOCK) as fh:
            data = yaml.safe_load(fh)
        expected = (data or {}).get("advisory_jev_runtimes", {}).get("simple-jev", {}).get("revision")
    except Exception:
        # Fallback: parse the pin without PyYAML. The lock file indents top-level
        # keys at column 0 and the simple-jev block at two spaces.
        in_block = in_simple = False
        try:
            lines = open(UPSTREAM_LOCK)
        except Exception:
            lines = ()
        for line in lines:
            if line.rstrip("\n") == "advisory_jev_runtimes:":
                in_block = True
                continue
            if in_block and line and not line.startswith(" "):
                break
            if in_block and line.startswith("  simple-jev:"):
                in_simple = True
                continue
            if in_block and in_simple and line.strip().startswith("revision:"):
                expected = line.split("revision:", 1)[1].strip().strip('"')
                break
    if not expected:
        return False, None, actual, "no advisory_jev_runtimes.simple-jev.revision in upstream.lock.yaml"
    if actual != expected:
        return False, expected, actual, "simple-jev checkout %s != pinned %s" % (actual, expected)
    return True, expected, actual, "ok"


def _logits_from_logprobs(top, branch, sq, tokenizer):
    """D-4: map each output label to its token string (via the tokenizer) and read that token's
    logprob from top_logprobs[0] (the dict, token string to logprob, as vLLM /v1/completions
    returns it). Returns (label->logprob dict, bounded-labels list). A bounded label is given
    the lowest logprob shown (an upper bound on its probability) and named, never silently
    filled with a real value."""
    row, bounded = {}, []
    lowest = min(top.values(), default=None)
    for i, label in enumerate(sq.output_labels):
        tok = tokenizer.decode([branch.output_ids[i]])
        if tok in top:
            row[label] = top[tok]
        else:
            # Bounded: the label is not in the top 20; the lowest shown logprob is an upper
            # bound on the label's probability. Named, never silent.
            row[label] = lowest if lowest is not None else 0.0
            bounded.append(label)
    return row, bounded


def completions_body(sent_id, token_ids):
    """D-3: the ONLY place a /v1/completions body is built. EXACTLY these keys, no others:
    a body carrying echo, prompt_logprobs, best_of or n cannot be built (the last such key
    OOM-killed the shared engine, AF-AP-201)."""
    return {
        "model": sent_id,
        "prompt": list(token_ids),
        "max_tokens": 1,
        "temperature": 0,
        "logprobs": 20,
    }


class JevService:
    """Bind the pinned oracle, the served tokenizer, the served id and the direct vLLM transport
    to the wire contract.

    send() is the vLLM transport; tests substitute a fake. It is threaded so a request never
    blocks on the network and the adapter's own state is read-only after construction.
    """

    served_id: ClassVar = None  # the vLLM id, read from GET /v1/models at start (D-3)

    def __init__(self, tokenizer, policy, key, served_id, send=None, *, max_branches=100):
        self.tokenizer = tokenizer
        self.policy = policy
        self._key = key
        self.sent_id = served_id  # D-3: the id the requests carry and the responses must echo
        self.vllm_base = os.environ.get("QWEN_JEV_VLLM", VLLM_BASE_DEFAULT)
        self._send = send if send is not None else self._send_completions
        self.compiler = _oracle["PromptCompiler"](tokenizer, prompt_policy=policy)
        self.max_branches = max_branches

    def _send_completions(self, branch, named):
        """D-3: one branch straight to vLLM /v1/completions, its prompt the compiler's own token
        ids (exact by construction). The key rides the Authorization header only; it is never in
        the body, a log line, or a returned error. The named argument records whether the branch
        carries the fixed reasoning (it does not change the raw-id prompt, which already contains
        it when present)."""
        body = completions_body(self.sent_id, branch.token_ids)
        req = urllib.request.Request(
            self.vllm_base + "/v1/completions",
            data=json.dumps(body).encode(),
            headers={"Content-Type": "application/json", "Authorization": "Bearer " + self._key},
        )
        try:
            with urllib.request.urlopen(req, timeout=120) as r:
                return r.status, json.loads(r.read())
        except urllib.error.HTTPError as e:
            # D-6: the error must never name the key; a transport failure is a refusal, not a fake answer.
            try:
                err = json.loads(e.read() or b"{}")
            except ValueError:
                err = {"error": {"message": str(e)[:160]}}
            return e.code, err
        except (urllib.error.URLError, TimeoutError, OSError) as e:
            return 502, {"error": {"message": "vllm transport: %s: %s" % (type(e).__name__, str(e)[:160])}}

    def _branch_logits(self, branch, sq):
        """Send one branch, D-4-check it, and return (logit-row, bounded, ok, reason, usage).
        ok is False when the branch must be refused (a non-local served model, a token count
        that does not match, or a transport failure)."""
        named = branch.reasoning_content is not None
        status, resp = self._send(branch, named)
        if status != 200 or not isinstance(resp, dict) or not resp.get("choices"):
            return None, [], False, "vllm HTTP %s: %s" % (status, str(resp)[:160]), {}
        # D-4: the response's model must equal the id sent, or the answer is refused.
        served = resp.get("model")
        if served != self.sent_id:
            return None, [], False, "served model %r is not the id sent %r" % (served, self.sent_id), {}
        usage = resp.get("usage") or {}
        prompt_tokens = usage.get("prompt_tokens")
        if prompt_tokens != len(branch.token_ids):
            # D-4: a branch that fails the token count is refused (not scored).
            return None, [], False, "token count %s != compiler %s" % (prompt_tokens, len(branch.token_ids)), usage
        top_row = (resp["choices"][0].get("logprobs") or {}).get("top_logprobs") or [{}]  # type: ignore[union-attr]
        top = top_row[0]  # type: ignore[index]
        if not isinstance(top, dict):
            # The /v1/completions shape is a dict (token -> logprob); the chat shape (a list)
            # is a different response and is refused, not guessed at.
            return None, [], False, "top_logprobs[0] is %s, not the token->logprob dict D-4 expects" % type(top).__name__, usage
        row, bounded = _logits_from_logprobs(top, branch, sq, self.tokenizer)
        return row, bounded, True, "ok", usage

    def _single(self, state, questions):
        """Compile + send + score ONE request (no fan-out). Returns the response dict (D-5
        envelope): {model, answers, usage, [fan_out], [refused], [bounded]}. Refused branches
        keep their answer shape with the refused value null, so the house J2 scripts (which
        read answers[qid][field]) never crash; the refused/bounded sets are surfaced so a
        consumer can see the parity wall."""
        if len(questions) > self.max_branches:
            raise ValueError("too many branches: %d > %d" % (len(questions), self.max_branches))
        creq = _oracle["ClassifierRequest"].model_validate(
            {"model": self.sent_id, "state": state, "questions": questions})
        plan, binary_keys = _oracle["prepare_policy"](creq, "v1", self.policy)
        compiled = self.compiler.compile(creq)
        qmap = {q.branch_id: q for q in compiled.plan.questions}
        qid_by_branch = {q.branch_id: q.question_id for q in compiled.plan.questions}
        logits, bounded_all, refused = {}, {}, {}
        usage_sum = {"input_tokens": 0, "output_tokens": 0}
        for br in compiled.branches:
            row, bounded, ok, reason, usage = self._branch_logits(br, qmap[br.branch_id])
            if not ok:
                # D-4: refused (count mismatch / non-local model / transport). Named, never silent.
                refused[qid_by_branch[br.branch_id]] = reason
                continue
            logits[br.branch_id] = row
            if bounded:
                bounded_all[qid_by_branch[br.branch_id]] = bounded
            for k in usage_sum:
                usage_sum[k] += int(usage.get(k, 0) or 0)
        # D-1: build every answer with simple-jev's own scoring. build_response requires a finite
        # logit row for EVERY planned branch; a refused branch is given an all-zero row (finite,
        # uniform) so the oracle runs, then its answer is nulled and named below, so no score is
        # reported from a refused branch.
        for br in compiled.branches:
            if br.branch_id not in logits:
                sq = qmap[br.branch_id]
                logits[br.branch_id] = {lab: 0.0 for lab in sq.output_labels}
        response = _oracle["build_response"](
            plan, logits, input_tokens=_oracle["unique_prompt_tokens"]([b.token_ids for b in compiled.branches]))
        _oracle["restore_binary_noul"](response, binary_keys)
        # Surface the parity wall without altering the oracle's answer values: a refused answer is
        # nulled (after the noul restore, so the restore cannot resurrect a refused score) and named.
        for qid, reason in refused.items():
            ans = response["answers"].get(qid)
            if isinstance(ans, dict):
                for k in ("choice", "noul", "score", "probabilities", "confidence"):
                    if k in ans:
                        ans[k] = None
                ans["refused"] = reason
            else:
                response["answers"][qid] = {"type": "refused", "refused": reason}
        if bounded_all:
            for qid, labels in bounded_all.items():
                ans = response["answers"].get(qid)
                if isinstance(ans, dict):
                    ans["bounded_labels"] = labels
        if len(questions) > 1 and all(qid in (refused or {}) or qid in response["answers"] for qid in questions):
            response["fan_out"] = len(questions)
        return response

    def systemone(self, body):
        """D-5: the house wire contract. A request without `model` gets the served id; when every
        question id names a state.chunks id, each question sees only its own chunk (the Laya
        per-chunk fan-out); otherwise one call. The response carries answers keyed by question id,
        usage, model, and fan_out."""
        body = dict(body)
        body.setdefault("model", self.sent_id)  # D-5: a request without `model` gets the served id
        state, questions = body["state"], body["questions"]
        chunks = _chunk_map(state)
        if chunks is not None and set(questions) <= set(chunks):
            # D-5 fan-out: one call per chunk, each question sees only its own chunk.
            base = {k: v for k, v in state.items() if k != "chunks"}
            answers, usage_sum, model, refused, bounded = {}, {"input_tokens": 0, "output_tokens": 0}, None, {}, {}
            for qid, q in questions.items():
                one = self._single(dict(base, chunk=chunks[qid]), {qid: q})
                answers[qid] = one["answers"][qid]
                model = one.get("model", model) or self.sent_id
                for k in usage_sum:
                    usage_sum[k] += int(one.get("usage", {}).get(k, 0) or 0)
                if "refused" in (one.get("answers", {}).get(qid) or {}):
                    refused[qid] = one["answers"][qid]["refused"]
                bl = (one.get("answers", {}).get(qid) or {}).get("bounded_labels")
                if bl:
                    bounded[qid] = bl
            out = {"model": model, "answers": answers, "usage": usage_sum, "fan_out": len(questions)}
            if refused:
                out["refused"] = refused
            if bounded:
                out["bounded_labels"] = bounded
            return out
        one = self._single(state, questions)
        out = {"model": one["model"], "answers": one["answers"], "usage": one["usage"]}
        if "refused" in one:
            out["refused"] = one["refused"]
        if "bounded_labels" in one:
            out["bounded_labels"] = one["bounded_labels"]
        if "fan_out" in one:
            out["fan_out"] = one["fan_out"]
        return out


def _chunk_map(state):
    """D-5 (the Laya pruner batch form): state.chunks=[{id,text}...] -> {id:text}; None for any other shape.
    Mirrors scripts/laya_systemone_server.py:118-127."""
    if not isinstance(state, dict) or not isinstance(state.get("chunks"), list):
        return None
    out = {}
    for c in state["chunks"]:
        if not isinstance(c, dict) or not isinstance(c.get("id"), str) or not isinstance(c.get("text"), str):
            return None
        out[c["id"]] = c["text"]
    return out


class Handler(BaseHTTPRequestHandler):
    server_version = "qwen-jev/0.2"
    service: ClassVar = None  # type: ignore[name-defined]

    def _send(self, code, obj):
        body = json.dumps(obj, ensure_ascii=False).encode()
        self.send_response(code)
        self.send_header("content-type", "application/json")
        self.send_header("content-length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format, *args):  # D-6: the access log must never carry a key; keep it terse and key-free.
        pass

    def do_GET(self):
        if self.path in ("/health", "/"):
            return self._send(200, {"ok": True, "model": self.service.sent_id,
                                    "prompt_policy": self.service.policy,
                                    "revision": os.environ.get("LANE_ID", "unlabeled"),
                                    "oracle_revision": _pin_actual,
                                    "tokenizer": TOKENIZER_DIR})
        if self.path == "/v1/models":
            return self._send(200, {"data": [{"id": self.service.sent_id}]})
        return self._send(404, {"error": "not found"})

    def do_POST(self):
        if self.path not in ("/v1/systemone", "/v1/classifier"):
            return self._send(404, {"error": "not found"})
        length = int(self.headers.get("content-length") or 0)
        if length > MAX_BODY:
            return self._send(413, {"error": "body too large"})
        try:
            body = json.loads(self.rfile.read(length) or b"{}")
        except json.JSONDecodeError:
            return self._send(400, {"error": "invalid JSON body"})
        if "state" not in body or not isinstance(body.get("questions"), dict) or not body["questions"]:
            return self._send(400, {"error": "need state and a non-empty questions map"})
        try:
            out = self.service.systemone(body)
            return self._send(200, out)
        except Exception as e:
            # D-6: the key is never in an error line; a failure is a refusal with a reason, never a fake answer.
            return self._send(503, {"error": "jev failed: %s: %s" % (type(e).__name__, str(e)[:200])})


def make_service(policy, key_file, send=None, vllm_base=None):
    """Construct the service: verify the pin (D-1), load the oracle and the served tokenizer,
    read the key (D-6), read the served id from the vLLM server (D-3)."""
    global _pin_actual
    ok, expected, actual, reason = verify_pin()
    if not ok:
        raise SystemExit("REFUSED to serve (D-1): %s" % reason)
    _pin_actual = actual
    load_oracle()  # D-1: the oracle is imported after the pin passes; JevService binds its names
    from transformers import AutoTokenizer
    tokenizer = AutoTokenizer.from_pretrained(TOKENIZER_DIR)
    key = read_key(key_file)
    base = (vllm_base or os.environ.get("QWEN_JEV_VLLM", VLLM_BASE_DEFAULT))
    served = read_served_id(base, key)
    return JevService(tokenizer, policy, key, served, send=send), (expected, actual)


def _port_taken(port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        return s.connect_ex(("127.0.0.1", port)) == 0
    finally:
        s.close()


def main(argv):
    ap = argparse.ArgumentParser(description="The Qwen3.8-27B Jev adapter, direct vLLM path (D-082).")
    ap.add_argument("--port", type=int, default=int(os.environ.get("QWEN_JEV_PORT", DEFAULT_PORT)))
    ap.add_argument("--policy", default="examples_binary", choices=["baseline", "examples_binary"])
    ap.add_argument("--key-file", default=os.environ.get("QWEN_JEV_KEY_FILE", KEY_FILE_DEFAULT))
    args = ap.parse_args(argv)
    # D-7: the port is ours only if we bound it. A listener we did not start is never treated as
    # ours (AF-AP-33): refuse up front with a clear error, and the bind below is the proof.
    if _port_taken(args.port):
        raise SystemExit("port %d is already taken by another listener; refusing to start (D-7)" % args.port)
    service, (expected, actual) = make_service(args.policy, args.key_file)
    Handler.service = service
    try:
        server = ThreadingHTTPServer(("127.0.0.1", args.port), Handler)
    except OSError as e:
        # The TOCTOU window between the check and the bind: a squatter that arrives in it fails
        # our bind. Same refusal, non-zero exit, named reason.
        raise SystemExit("port %d could not be bound (taken between check and bind?): %s (D-7)" % (args.port, e))
    # D-1/D-2: report the pin, policy and served id at startup; the key is never printed.
    print("qwen-jev on 127.0.0.1:%d policy=%s pin=%s (serving id %s)"
          % (args.port, args.policy, actual, service.sent_id), file=sys.stderr)
    server.serve_forever()


if __name__ == "__main__":
    main(sys.argv[1:])
