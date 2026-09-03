"""hermes-session-export: a synthetic state.db (same columns Hermes 0.21 uses) round-trips to a
scrubbed markdown; tool-result bodies are NOT exported; a planted secret in an assistant turn is
scrubbed; an unknown session exits 3."""
import pathlib
import sqlite3
import subprocess
import sys
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[2]
TOOL = ROOT / "harness-ports" / "bin" / "hermes-session-export.py"


def _db(path):
    con = sqlite3.connect(path)
    con.executescript("""
    create table sessions (id text primary key, source text not null, model text, started_at real not null,
      message_count integer default 0, tool_call_count integer default 0, input_tokens integer default 0,
      output_tokens integer default 0, cache_read_tokens integer default 0, reasoning_tokens integer default 0, cwd text);
    create table messages (id integer primary key autoincrement, session_id text not null, role text not null,
      content text, tool_call_id text, tool_calls text, tool_name text, timestamp real not null);
    """)
    con.execute("insert into sessions values ('s1','cli','codex/gpt-5.6-sol-ultra',1756880000.0,3,1,100,20,80,5,'/tree')")
    con.execute("insert into messages (session_id,role,content,tool_calls,timestamp) values ('s1','user','build it',NULL,1756880001.0)")
    con.execute("insert into messages (session_id,role,content,tool_calls,timestamp) values ('s1','assistant','running tests; key AGENT_TOKEN=cVMjXl1uWH1c9Ogzoc_-k60yOL5KP5pr','[{\"function\":{\"name\":\"terminal\"}}]',1756880002.0)")
    con.execute("insert into messages (session_id,role,content,tool_name,timestamp) values ('s1','tool','SECRET-RESULT-BODY sk-abcdefghijklmnopqrstuvwx','terminal',1756880003.0)")
    con.execute("insert into messages (session_id,role,content,tool_calls,timestamp) values ('s1','assistant','DONE report',NULL,1756880004.0)")
    con.commit(); con.close()


def main():
    checks = 0
    with tempfile.TemporaryDirectory() as d:
        db = pathlib.Path(d) / "state.db"; _db(db)
        out = pathlib.Path(d) / "lane.md"
        r = subprocess.run([sys.executable, str(TOOL), "--db", str(db), "--session", "s1", "--out", str(out)], capture_output=True, text=True, timeout=60)
        assert r.returncode == 0, r.stderr
        t = out.read_text()
        assert "codex/gpt-5.6-sol-ultra" in t and "build it" in t and "DONE report" in t; checks += 1
        assert "tools: terminal" in t; checks += 1
        assert "SECRET-RESULT-BODY" not in t and "sk-abcdefghijkl" not in t, "tool result bodies must not be exported"; checks += 1
        assert "cVMjXl1uWH1c9Ogzoc_-k60yOL5KP5pr" not in t and "redacted" in t, "planted secret must be scrubbed"; checks += 1
        assert "body not exported" in t; checks += 1
        r2 = subprocess.run([sys.executable, str(TOOL), "--db", str(db), "--session", "nope", "--out", str(out)], capture_output=True, text=True, timeout=60)
        assert r2.returncode == 3 and "not found" in r2.stderr; checks += 1
    print(f"test_hermes_session_export: {checks} checks passed")


if __name__ == "__main__":
    main()
