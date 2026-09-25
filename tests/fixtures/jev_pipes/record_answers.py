#!/usr/bin/env python3
"""Record the REAL local Laya scorer's answers to the P1 fixture's requests; the tests replay them (AF-AP-42).

    python3 tests/fixtures/jev_pipes/record_answers.py      # needs the local Laya server on 127.0.0.1:47411

Builds the synthetic fixture (make_fixture.py) in a temp dir, runs the replay harness over it in `unbudgeted` mode (every
request the pruner plans, one at a time) through a recording proxy, and writes, next to this file:
  answers.jsonl       one line per request: the sha256 of the request body the pruner built, the question ids, and the
                      scorer's HTTP status and body verbatim. Nothing is typed; every answer is the server's.
  answers.meta.json   when, from which scorer (its /health), over which fixture bytes, and the counts.
"""
import hashlib
import json
import subprocess
import sys
import tempfile
import threading
import urllib.error
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
SCORER = "http://127.0.0.1:47411"
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(REPO / "scripts"))
import make_fixture  # noqa: E402
from jev_pipes import replay_pruner  # noqa: E402

RECORDS = []


class Proxy(BaseHTTPRequestHandler):
    def log_message(self, *args):
        pass

    def do_POST(self):
        body = self.rfile.read(int(self.headers.get("content-length") or 0))
        request = urllib.request.Request(SCORER + self.path, data=body, method="POST",
                                         headers={"content-type": "application/json"})
        try:
            with urllib.request.urlopen(request, timeout=900) as response:
                status, text = response.status, response.read()
        except urllib.error.HTTPError as error:
            status, text = error.code, error.read()
        questions = sorted(json.loads(body)["questions"])
        RECORDS.append({"sha256": hashlib.sha256(body).hexdigest(), "questions": questions, "status": status,
                        "body": text.decode("utf-8")})
        self.send_response(status)
        self.send_header("content-type", "application/json")
        self.send_header("content-length", str(len(text)))
        self.end_headers()
        self.wfile.write(text)


def main():
    with urllib.request.urlopen(SCORER + "/health", timeout=10) as response:
        health = json.loads(response.read())
    server = ThreadingHTTPServer(("127.0.0.1", 0), Proxy)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    with tempfile.TemporaryDirectory() as tmp:
        transcript = make_fixture.build(Path(tmp) / "fixture")
        rc = replay_pruner.main(["--min-chars", "2000", "--out", str(Path(tmp) / "out"), "--mode", "unbudgeted",
                                 "--sample", "0", "--secondary-sample", "10", "--sources", str(transcript),
                                 "--scorer-url", f"http://127.0.0.1:{server.server_port}/v1/systemone",
                                 "--decisions", str(Path(tmp) / "decisions.jsonl")])
        fixture_sha = hashlib.sha256(transcript.read_bytes().replace(str(transcript.parent).encode(), b"<FIXTURE>")).hexdigest()
    server.shutdown()
    (HERE / "answers.jsonl").write_text("".join(json.dumps(r, sort_keys=True) + "\n" for r in RECORDS))
    stamp = subprocess.run(["date", "-u", "+%Y-%m-%dT%H:%M:%SZ"], capture_output=True, text=True, check=True).stdout.strip()
    meta = {"captured_at": stamp, "scorer": SCORER, "health": {k: health.get(k) for k in ("snapshot", "subfolder", "device", "revision")},
            "fixture_sha256_with_dir_placeholder": fixture_sha, "harness_mode": "unbudgeted", "harness_rc": rc,
            "requests": len(RECORDS), "statuses": sorted({r["status"] for r in RECORDS})}
    (HERE / "answers.meta.json").write_text(json.dumps(meta, indent=1, sort_keys=True) + "\n")
    print(json.dumps(meta))
    return 0 if rc == 0 and RECORDS else 1


if __name__ == "__main__":
    raise SystemExit(main())
