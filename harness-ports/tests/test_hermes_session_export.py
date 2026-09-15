"""hermes-session-export: a synthetic state.db (same columns Hermes 0.21 uses) round-trips to a
scrubbed markdown; tool-result bodies are NOT exported by default (`--tool-body-cap 0` is
byte-identical to the flag omitted — the committed transcripts' shape); `--tool-body-cap N`
exports them SCRUBBED and capped at N chars (matrix corpora on the PC); a planted secret in an
assistant turn is scrubbed; a heading-shaped line inside ANY body is indented one space so the
export grammar (consumed by qwen_matrix.parse_export) stays unambiguous; an unknown session
exits 3."""
import pathlib
import re
import sqlite3
import subprocess
import sys
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[2]
TOOL = ROOT / "harness-ports" / "bin" / "hermes-session-export.py"
QUOTED_HEADING = "## user @ 00:00:09"


def _db(path):
    con = sqlite3.connect(path)
    con.executescript("""
    create table sessions (id text primary key, source text not null, model text, started_at real not null,
      message_count integer default 0, tool_call_count integer default 0, input_tokens integer default 0,
      output_tokens integer default 0, cache_read_tokens integer default 0, reasoning_tokens integer default 0, cwd text);
    create table messages (id integer primary key autoincrement, session_id text not null, role text not null,
      content text, tool_call_id text, tool_calls text, tool_name text, timestamp real not null);
    """)
    con.execute("insert into sessions values ('s1','cli','codex/gpt-5.6-sol-ultra',1756880000.0,5,2,100,20,80,5,'/tree')")
    con.execute("insert into messages (session_id,role,content,tool_calls,timestamp) values ('s1','user','build it',NULL,1756880001.0)")
    con.execute("insert into messages (session_id,role,content,tool_calls,timestamp) values ('s1','assistant','running tests; key AGENT_TOKEN=cVMjXl1uWH1c9Ogzoc_-k60yOL5KP5pr','[{\"function\":{\"name\":\"terminal\"}}]',1756880002.0)")
    con.execute("insert into messages (session_id,role,content,tool_name,timestamp) values ('s1','tool','SECRET-RESULT-BODY sk-abcdefghijklmnopqrstuvwx','terminal',1756880003.0)")
    con.execute("insert into messages (session_id,role,content,tool_name,timestamp) values ('s1','tool',?, 'read_file',1756880003.5)",
                (f"{QUOTED_HEADING}\n\nquoted turn inside a tool body",))
    con.execute("insert into messages (session_id,role,content,tool_calls,timestamp) values ('s1','assistant','DONE report\n## assistant @ 00:00:00\n\nquoted turn inside an assistant body',NULL,1756880004.0)")
    con.commit(); con.close()


def _run(db, out, *extra):
    return subprocess.run([sys.executable, str(TOOL), "--db", str(db), "--session", "s1", "--out", str(out), *extra],
                          capture_output=True, text=True, timeout=60)


def main():
    checks = 0
    with tempfile.TemporaryDirectory() as d:
        db = pathlib.Path(d) / "state.db"; _db(db)
        out = pathlib.Path(d) / "lane.md"
        r = _run(db, out)
        assert r.returncode == 0, r.stderr
        t = out.read_text()
        assert "codex/gpt-5.6-sol-ultra" in t and "build it" in t and "DONE report" in t; checks += 1
        assert "tools: terminal" in t; checks += 1
        assert "SECRET-RESULT-BODY" not in t and "sk-abcdefghijkl" not in t, "tool result bodies must not be exported by default"; checks += 1
        assert "cVMjXl1uWH1c9Ogzoc_-k60yOL5KP5pr" not in t and "redacted" in t, "planted secret must be scrubbed"; checks += 1
        assert t.count("body not exported") == 2 and "quoted turn inside a tool body" not in t; checks += 1
        # the heading guard on an assistant body: exactly two REAL assistant turns; the quoted one indented
        assert len(re.findall(r"(?m)^## assistant @", t)) == 2 and "\n ## assistant @ 00:00:00\n" in t, "a quoted heading inside a body is indented, never a turn"; checks += 1
        # --tool-body-cap 0 is byte-identical to the flag omitted
        out0 = pathlib.Path(d) / "lane0.md"
        assert _run(db, out0, "--tool-body-cap", "0").returncode == 0 and out0.read_bytes() == out.read_bytes(); checks += 1
        # --tool-body-cap 80: both bodies exported whole (43 and 49 chars), scrubbed, the quoted heading indented
        out2 = pathlib.Path(d) / "lane-bodies.md"
        r2 = _run(db, out2, "--tool-body-cap", "80")
        assert r2.returncode == 0, r2.stderr
        t2 = out2.read_text()
        assert "SECRET-RESULT-BODY sk-<redacted>" in t2 and "sk-abcdefghijkl" not in t2, "tool bodies are exported SCRUBBED"; checks += 1
        assert t2.count("(body capped at 80)") == 2 and "body not exported" not in t2; checks += 1
        assert "quoted turn inside a tool body" in t2; checks += 1
        assert len(re.findall(r"(?m)^## user @", t2)) == 1 and f"\n {QUOTED_HEADING}\n" in t2, "a quoted heading inside a tool body is indented, never a turn"; checks += 1
        # --tool-body-cap 10 truncates BEFORE scrubbing: the first body becomes its first ten chars
        out3 = pathlib.Path(d) / "lane-capped.md"
        assert _run(db, out3, "--tool-body-cap", "10").returncode == 0
        t3 = out3.read_text()
        assert "SECRET-RESULT-BODY" not in t3 and "\n\nSECRET-RES\n" in t3 and t3.count("(body capped at 10)") == 2; checks += 1
        r4 = subprocess.run([sys.executable, str(TOOL), "--db", str(db), "--session", "nope", "--out", str(out)], capture_output=True, text=True, timeout=60)
        assert r4.returncode == 3 and "not found" in r4.stderr; checks += 1
    print(f"test_hermes_session_export: {checks} checks passed")


if __name__ == "__main__":
    main()
