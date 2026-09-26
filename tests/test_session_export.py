"""scripts/session_export.py (task #252; brief tasks/briefs/jev-laya/SESSION-EXPORT-brief.md and its AMENDMENTS 1 and 2):
every payload shape a transcript can carry a secret in is scrubbed, dropped or strict-passed (D-2, D-6); the stream keeps the
brief's schema, roles and the harness's own outcome, model and stop fields (D-1, G2); the cap keeps head and tail, larger for
Read results, Write inputs, file changes and pruner archives, and its seam forms no secret shape (D-3, G3); edited files are
harness notices (G1); a repeated notification is kept once (G4); Bash file changes and pruner archives follow their result
(G5, A2); a value only the opaque-run rule takes becomes a keyed pseudonym (G6); every project folder is read and convert()
resumes from a byte offset (A2); fixed offsets give byte-identical output (D-4); the leak gate counts and prints no match
(D-6). SESSION-EXPORT-R1 (tasks/briefs/jev-laya/SESSION-EXPORT-R1-brief.md, AMENDMENT 3): a credential behind an escaped
quote is redacted (R-1); a call that names the pseudonym key loses its result (R-2); more named shapes and secret-path
spellings (R-3); a run the repo's tracked files hold stays as it is (R-4). Synthetic transcripts only, in the record shapes
the real ones have (the report's survey). Every secret is a FAKE canary from session_export.CANARIES, assembled in code; a
failure message names canaries and never prints one. Every export reads the committed runs of a small git repo made here,
never of this repo."""
import base64
import hashlib
import hmac
import importlib.util
import json
import lzma
import os
import pathlib
import re
import shutil
import stat
import subprocess
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]
TOOL = ROOT / "scripts" / "session_export.py"
SID = "0f0f0f0f-fake-4a4a-8b8b-00000000cafe"
MAIN = "-home-user/" + SID + ".jsonl"
SECOND = "-home-user-agent-factory/" + SID + ".jsonl"          # the same session id under another project folder
KEYS = ["seq", "src", "line", "ts", "role", "kind", "tool", "call_id", "text", "truncated", "outcome", "model", "stop_reason"]
ROLES = {"owner", "coordinator", "agent", "tool", "hook", "system"}
KINDS = {"text", "thinking", "tool_call", "tool_result", "hook", "notification", "summary", "harness_notice", "api_error",
         "file_change", "pruner_archive"}
DROPPED = "[payload dropped: secret path]"
NEVER_READ = {"last-prompt", "queue-op", "signature"}     # canaries in records or fields the export never reads
SHA1 = "0f1e2d3c4b5a6978" * 2 + "0f1e2d3c"                  # fake 40-hex commit ids (G6)
SHA2 = "a1b2c3d4e5f60718" * 2 + "a1b2c3d4"
ARCHIVES = os.path.join(".claude", "fast-jev-output")
# AMENDMENT 3: the text the fixture repo commits. Fake, and never a canary: the export keeps it, so the gate would count it.
COMMITTED_NAME = "test_zq_committed_evidence_name_that_runs_past_forty_characters"
UNCOMMITTED_NAME = "test_zq_uncommitted_evidence_name_that_runs_past_forty_chars"
COMMITTED_PATH = "tests/test_zq_s0_01_committed_path.py"
COMMITTED_BRANCH = "claude/zq-committed-branch-01"
COMMITTED_FAKE = "ZQfake0committed0fixture0token0v1"
COMMITTED_TEXT = "Evidence: %s in `%s` on `%s`.\nfixture token %s\n" % (COMMITTED_NAME, COMMITTED_PATH, COMMITTED_BRANCH,
                                                                      COMMITTED_FAKE)
GIT = ["git", "-c", "user.name=zq", "-c", "user.email=zq@example.invalid", "-c", "commit.gpgsign=false",
       "-c", "core.hooksPath=/dev/null", "-c", "init.defaultBranch=main"]
REPO = {}


def _git(repo, *args):
    r = subprocess.run(GIT + ["-C", str(repo), *args], capture_output=True, text=True, timeout=60)
    assert r.returncode == 0, r.stderr[-500:]
    return r.stdout.strip()


def make_repo(path, *texts):
    """A git repo whose commits each add docs/zq-<i>.md holding one of `texts`; the commit ids, oldest first."""
    path.mkdir(parents=True)
    _git(path, "init", "-q")
    commits = []
    for i, text in enumerate(texts):
        (path / "docs").mkdir(exist_ok=True)
        (path / "docs" / ("zq-%d.md" % i)).write_text(text)
        _git(path, "add", "docs")
        _git(path, "commit", "-q", "-m", "zq %d" % i)
        commits.append(_git(path, "rev-parse", "HEAD"))
    return commits


@pytest.fixture(scope="module", autouse=True)
def repo(tmp_path_factory):
    """AMENDMENT 3: the repo every export here reads its committed runs from: a readme, then COMMITTED_TEXT. Reading this
    repo instead (187 MB) would cost each export about 13 s and tie the tests to what is committed here."""
    path = tmp_path_factory.mktemp("repo") / "r"
    REPO.update(path=path, commits=make_repo(path, "a readme\n", COMMITTED_TEXT))
    return REPO


@pytest.fixture(scope="module")
def se():
    spec = importlib.util.spec_from_file_location("session_export_under_test", TOOL)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


class Tape:
    """One JSONL transcript in the real record shapes; add() returns the record's 1-based line number."""

    def __init__(self, cwd, agent=None):
        self.lines, self.cwd, self.agent, self.asst = [], str(cwd), agent, set()

    def _base(self, kind):
        n = len(self.lines) + 1
        r = {"parentUuid": None, "isSidechain": self.agent is not None, "userType": "external", "cwd": self.cwd,
             "sessionId": SID, "version": "2.1.0", "gitBranch": "fake", "type": kind, "uuid": "u-%05d" % n,
             "timestamp": "2026-09-25T01:%02d:%02d.000Z" % divmod(n, 60)}
        if self.agent:
            r["agentId"] = self.agent
        return r

    def add(self, rec):
        # compact, as the harness writes every record (0 of 317 real transcripts hold a spaced `"cwd": "`)
        self.lines.append(rec if isinstance(rec, str) else json.dumps(rec, separators=(",", ":")))
        return len(self.lines)

    def user(self, content, **extra):
        r = self._base("user")
        r["message"] = {"role": "user", "content": content}
        r.update(extra)
        return self.add(r)

    def owner(self, content):
        return self.user(content, origin={"kind": "human"}, promptSource="sdk", permissionMode="auto")

    def assistant(self, blocks, stop="tool_use", model="claude-fake", **extra):
        r = self._base("assistant")
        r["requestId"] = "req_fake%05d" % len(self.lines)
        r["message"] = {"model": model, "id": "msg_fake%05d" % len(self.lines), "type": "message",
                        "role": "assistant", "content": blocks, "stop_reason": stop,
                        "usage": {"input_tokens": 1, "output_tokens": 1}}
        r.update(extra)
        line = self.add(r)
        self.asst.add(line)
        return line

    def call(self, cid, name, inp):
        return self.assistant([{"type": "tool_use", "id": cid, "name": name, "input": inp, "caller": {"type": "direct"}}])

    def result(self, cid, content, is_error=None, tur=None, denial=None):
        b = {"tool_use_id": cid, "type": "tool_result", "content": content}
        if is_error is not None:
            b["is_error"] = is_error
        extra = {"sourceToolAssistantUUID": "u-fake"}
        if tur is not None:
            extra["toolUseResult"] = tur
        if denial is not None:
            extra["toolDenialKind"] = denial
        return self.user([b], **extra)

    def attachment(self, att):
        r = self._base("attachment")
        r["attachment"] = att
        return self.add(r)

    def system(self, subtype, **fields):
        r = self._base("system")
        r["subtype"] = subtype
        r.update(fields)
        return self.add(r)

    def write(self, path, tail=""):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("\n".join(self.lines) + "\n" + tail)


def bash_tur(stdout, **extra):
    return {"stdout": stdout, "stderr": "", "interrupted": False, "isImage": False, "noOutputExpected": False, **extra}


def note(tid, tu, status):
    """A task notification in the harness's XML fields (no task id or no tool-use id when None)."""
    return ("<task-notification>\n" + ("<task-id>%s</task-id>\n" % tid if tid else "")
            + ("<tool-use-id>%s</tool-use-id>\n" % tu if tu else "")
            + "<status>%s</status>\n<summary>Background command completed</summary>\n</task-notification>" % status)


def event(tid, body):
    return "<task-notification>\n<task-id>%s</task-id>\n<summary>Monitor event</summary>\n<event>%s</event>\n" \
           "</task-notification>" % (tid, body)


def xxd(data):
    """xxd's layout: the offset, eight 2-byte hex groups, the printable bytes (the column the strict pass left, F-4)."""
    rows = []
    for i in range(0, len(data), 16):
        row = data[i:i + 16]
        hx = " ".join(row[j:j + 2].hex() for j in range(0, len(row), 2))
        rows.append("%08x: %-39s  %s" % (i, hx, "".join(chr(b) if 32 <= b < 127 else "." for b in row)))
    return "\n".join(rows) + "\n"


PARTIAL = '{"type": "user", "message": {"role": "user", "content": "cut'     # a live file's unfinished last line
BIG_HEAD = 24576 - 12 - 16         # where `PC_BRIDGE_TOKEN=` starts: 12 characters of its value fall inside the kept head
DIFF = {"changedFiles": ["/home/user/agent-factory/scripts/zq.py", "/home/user/agent-factory/docs/zq.md", "/srv/app/zq.env"],
        "files": [{"filePath": "/home/user/agent-factory/scripts/zq.py",
                   "hunks": [{"oldStart": 1, "oldLines": 1, "newStart": 1, "newLines": 2,
                              "lines": ["-x = 1", "+x = 2", "+API_KEY = 'CANARY-KEY'"]}]},
                  {"filePath": "/srv/app/zq.env", "created": True,
                   "hunks": [{"oldStart": 0, "oldLines": 0, "newStart": 1, "newLines": 1, "lines": ["+ZQ_DB=CANARY-ENV"]}]}],
        "moreFiles": 2}


def build_tree(root, C, proj):
    """Under `root` (a projects directory): a session, a subagent, a workflow agent and a workflow journal in `-home-user/`
    and the same session id in `-home-user-agent-factory/`; the pruner's archives under `proj` (every record's cwd).
    Returns {name: (src, line)} and, under "asst", {src: the lines of its assistant records}."""
    L = {}
    m = Tape(proj)

    def at(name, line, src=MAIN):
        L[name] = (src, line)

    host = lambda k: C[k] + ".trycloudflare.com"                                           # noqa: E731
    queued = lambda text: m.attachment({"type": "queued_command", "commandMode": "task-notification", "prompt": text})  # noqa
    at("banner", m.owner("BRIDGE READY https://%s/exec AGENT_TOKEN=%s" % (host("bridge-host"), C["bridge-token"])))
    at("thinking", m.assistant([{"type": "thinking", "thinking": "the token is " + C["gh-thinking"], "signature": "x"}]))
    at("signature-only", m.assistant([{"type": "thinking", "thinking": "", "signature": C["signature"]}]))
    at("text", m.assistant([{"type": "text", "text": "Plan: write the env file"}], stop="end_turn"))
    m.call("toolu_fake_w1", "Write", {"file_path": "/srv/app/.env",
                                      "content": "ZQ_SETTING=%s\nPC_BRIDGE_TOKEN=%s\n" % (C["env-write"], C["env-write-2"])})
    at("write-env", len(m.lines))
    at("write-env-result", m.result("toolu_fake_w1", "File created successfully at: /srv/app/.env",
                                    tur={"type": "create", "filePath": "/srv/app/.env", "content": C["env-write"]}))
    env_out = "PC_BRIDGE_URL=https://%s\nPC_BRIDGE_TOKEN=%s\nZQ_ENDPOINT=%s\n" % (host("bridge-host-2"), C["bridge-token-2"],
                                                                               C["env-line"])
    at("bash-env", m.call("toolu_fake_b1", "Bash", {"command": "cat /home/user/agent-factory/.pc-bridge.env",
                                                     "description": "show env"}))
    at("bash-env-result", m.result("toolu_fake_b1", env_out, is_error=False, tur=bash_tur(env_out)))
    m.call("toolu_fake_b2", "Bash", {"command": "grep -n ZQ /srv/app/prod.env"})
    at("bash-grep-result", m.result("toolu_fake_b2", "4:ZQ_KEYRING=" + C["env-grep"], is_error=False))
    m.call("toolu_fake_b3", "Bash", {"command": "cat ~/.config/qwen-builder/api-key"})
    at("bash-key-result", m.result("toolu_fake_b3", C["keyfile-bash"] + "\n", is_error=False))
    m.call("toolu_fake_b4", "Bash", {"command": "cat /tmp/fake-curl.cfg"})
    at("curl-cfg-result", m.result("toolu_fake_b4", 'url = "https://%s/exec"\nheader = "X-Agent-Token: %s"\n'
                                   % (host("bridge-host-3"), C["curl-token"]), is_error=False))
    at("bash-curl", m.call("toolu_fake_b5", "Bash", {"command": "curl -s -H 'Authorization: Bearer %s' %s/exec"
                                                      % (C["bearer"], host("bridge-host-4"))}))
    at("bash-curl-result", m.result("toolu_fake_b5", "Exit code 7\ncurl: (7) Failed to connect", is_error=True))
    m.call("toolu_fake_b6", "Bash", {"command": "psql postgres://zqfake:%s@db.internal/app -c 'select 1'" % C["url-password"]})
    at("bash-timeout-result", m.result("toolu_fake_b6", "Command timed out", is_error=True,
                                       tur=bash_tur("", timedOutAfterMs=120000)))
    m.call("toolu_fake_b7", "Bash", {"command": "curl -H 'Authorization: Basic %s' http://10.9.8.7/x" % C["basic-auth"]})
    at("bash-denied-result", m.result("toolu_fake_b7", "Permission for this action was denied.", is_error=True,
                                      tur="Error: denied", denial="automode-blocked"))
    m.call("toolu_fake_b8", "Bash", {"command": "echo done"})
    at("exit-prose-result", m.result("toolu_fake_b8", "Exit code 3\nis only printed text here", is_error=False))
    m.call("toolu_fake_r1", "Read", {"file_path": "/home/user/.ssh/id_fake"})
    pem = ["-----BEGIN OPENSSH PRIVATE KEY-----", "b3BlbnNzaC1rZXktdjE" + C["pem"], "-----END OPENSSH PRIVATE KEY-----"]
    at("read-pem-result", m.result("toolu_fake_r1", "".join("%6d\t%s\n" % (i + 1, s) for i, s in enumerate(pem))))
    at("read-key", m.call("toolu_fake_r2", "Read", {"file_path": "/home/rocco/.config/qwen-jev/omniroute.key"}))
    at("read-key-result", m.result("toolu_fake_r2", "     1\t" + C["keyfile"]))
    at("read-pkey", m.call("toolu_fake_r4", "Read", {"file_path": "/root/.config/session-export/pseudonym.key"}))
    at("read-pkey-result", m.result("toolu_fake_r4", "     1\t" + C["pkey-read"]))
    at("edit-hermes", m.call("toolu_fake_e1", "Edit", {"file_path": "/home/rocco/.hermes/profiles/aflanezq/config.yaml",
                                                       "old_string": "api_base: " + C["hermes-old"],
                                                       "new_string": "api_base: " + C["hermes-new"], "replace_all": False}))
    at("edit-hermes-result", m.result("toolu_fake_e1", "The file has been updated successfully."))
    at("grep-env", m.call("toolu_fake_g1", "Grep", {"pattern": "SETTING", "path": "/srv/app/.env", "output_mode": "content"}))
    at("grep-env-result", m.result("toolu_fake_g1", "PC_EXTRA_SETTING=" + C["grep-tool"]))
    m.call("toolu_fake_f1", "WebFetch", {"url": "https://example.com/page", "prompt": "summarize"})
    at("webfetch-result", m.result("toolu_fake_f1", [{"type": "text", "text": "found " + C["gh-result"] + " in page"},
                                                     {"type": "tool_reference", "tool_name": "Read"}]))
    big = "w " * (BIG_HEAD // 2) + "PC_BRIDGE_TOKEN=" + C["cap-straddle"] + " " + "v " * 20000
    m.call("toolu_fake_b9", "Bash", {"command": "python3 dump.py"})
    at("big-result", m.result("toolu_fake_b9", big, is_error=False))
    L["big-raw-len"] = len(big)
    at("queued-owner", m.attachment({"type": "queued_command", "prompt": "new banner https://%s token=%s"
                                     % (host("bridge-host-5"), C["queued-token"]), "commandMode": "prompt",
                                     "origin": {"kind": "human"}, "humanTurn": True, "timestamp": "t"}))
    at("queued-notif", m.attachment({"type": "queued_command", "commandMode": "task-notification", "timestamp": "t",
                                     "prompt": "<task-notification>\n<task-id>bzq1</task-id>\n<status>completed</status>\n"
                                               "</task-notification>"}))
    at("queued-agent", m.attachment({"type": "queued_command", "commandMode": "prompt", "isMeta": True,
                                     "origin": {"kind": "peer"}, "prompt": '<agent-message from="zq">hello</agent-message>'}))
    at("peer-user", m.user("Another agent reports: done", isMeta=True, origin={"kind": "peer"}))
    at("hook-success", m.attachment({"type": "hook_success", "hookName": "PostToolUse:Edit", "hookEvent": "PostToolUse",
                                     "toolUseID": "toolu_fake_e1", "command": "python3 hook.py", "content": "ok",
                                     "stdout": "Authorization: Bearer " + C["hook-bearer"], "stderr": "", "exitCode": 0,
                                     "durationMs": 12}))
    at("hook-context", m.attachment({"type": "hook_additional_context", "content": ["EDIT SNAPSHOT fine"],
                                     "hookEvent": "PostToolUse", "hookName": "PostToolUse:Edit", "toolUseID": "toolu_x"}))
    at("att-file", m.attachment({"type": "file", "filename": "/home/user/agent-factory/.pc-bridge.env",
                                 "displayPath": ".pc-bridge.env",
                                 "content": {"type": "text", "file": {"filePath": "/home/user/agent-factory/.pc-bridge.env",
                                                                      "content": "ZQ_FILE_SETTING=" + C["att-file"],
                                                                      "numLines": 1, "startLine": 1, "totalLines": 1}}}))
    at("att-edited", m.attachment({"type": "edited_text_file", "filename": "/srv/app/.env", "snippet": "ZQ_X=" + C["att-edited"]}))
    at("tokens", m.attachment({"type": "total_tokens_reminder", "text": "<total_tokens>5 tokens left</total_tokens>"}))
    at("future-att", m.attachment({"type": "zq_future_kind", "note": "keep me"}))
    at("stop-summary", m.system("stop_hook_summary", hookCount=1, hookInfos=[{"command": "~/.claude/stop-hook.sh",
                                                                               "durationMs": 30}],
                                hookErrors=["push the branch; link https://%s/x" % host("stop-hook-host")],
                                preventedContinuation=False, stopReason="", hasOutput=True, level="suggestion",
                                toolUseID="toolu_fake_s1", hookAdditionalContext=[]))
    at("stop-feedback", m.user("Stop hook feedback:\n[~/.claude/stop-hook.sh]: push the branch", isMeta=True))
    at("compact", m.user("Summary of the session. AGENT_TOKEN=" + C["compact-token"], isCompactSummary=True,
                         isVisibleInTranscriptOnly=True))
    at("notif-user", m.user("<task-notification>\n<status>completed</status>\n</task-notification>",
                            origin={"kind": "task-notification"}, promptSource="system"))
    at("reminder", m.user("<system-reminder>be brief</system-reminder>", isMeta=True))
    at("image", m.owner([{"type": "image", "source": {"type": "base64", "media_type": "image/png", "data": "iVBORw0KGgo="}},
                         {"type": "text", "text": "what is this"}]))
    at("interrupt", m.user([{"type": "text", "text": "[Request interrupted by user]"}]))
    at("command-name", m.user("<command-name>/model</command-name>"))
    at("boundary", m.system("compact_boundary", content="Conversation compacted", level="info",
                            compactMetadata={"trigger": "auto", "preTokens": 1}))
    at("last-prompt", m.add({"type": "last-prompt", "lastPrompt": "prompt " + C["last-prompt"], "leafUuid": "u",
                             "sessionId": SID}))
    at("queue-op", m.add({"type": "queue-operation", "operation": "enqueue", "content": "queued " + C["queue-op"],
                          "sessionId": SID, "timestamp": "2026-09-25T02:00:00.000Z"}))
    at("atis", m.add({"type": "atis-latch", "atis": "x", "sessionId": SID}))
    # AMENDMENT 1: G2 API errors, G1 a harness notice, G3 large and small caps, G4 notifications, G5 Bash file changes,
    # G6 join keys and a long value a named rule takes
    at("api-error", m.assistant([{"type": "text", "text": "API Error: 429 rate limited; Authorization: Bearer "
                                                          + C["api-error-bearer"]}], stop="stop_sequence",
                                model="<synthetic>", isApiErrorMessage=True, error="rate_limit", apiErrorStatus=429))
    at("sys-api-error", m.system("api_error", level="error", error={"type": "overloaded_error"}, retryAttempt=1,
                                 retryInMs=500, maxRetries=10, source="fake"))
    at("notice", m.attachment({"type": "edited_text_file", "filename": "/home/user/agent-factory/scripts/zq.py",
                               "snippet": "     3\tzq_token=" + C["notice-token"]}))
    m.call("toolu_fake_r3", "Read", {"file_path": "/home/user/agent-factory/docs/zq-big.md"})
    at("read-big-result", m.result("toolu_fake_r3", "r " * 75000))
    at("write-big", m.call("toolu_fake_w2", "Write", {"file_path": "/tmp/zq-big.txt", "content": "x " * 70000}))
    at("write-big-result", m.result("toolu_fake_w2", "File created successfully at: /tmp/zq-big.txt"))
    m.call("toolu_fake_b11", "Bash", {"command": "python3 dump2.py"})
    at("bash-big-result", m.result("toolu_fake_b11", "y " * 20000, is_error=False))
    at("note-1", queued(note("bzq7", "toolu_fake_n1", "completed")))
    at("note-1-again", m.user(note("bzq7", "toolu_fake_n1", "completed"), origin={"kind": "task-notification"}))
    at("note-2", queued(note("bzq7", "toolu_fake_n2", "completed")))     # a reused task id, another call: kept
    at("note-3", m.user(note(None, None, "completed"), origin={"kind": "task-notification"}))
    at("note-3-again", m.user(note(None, None, "completed"), origin={"kind": "task-notification"}))   # no task id: kept
    at("event-1", queued(event("bzq8", "line one")))
    at("event-1-again", queued(event("bzq8", "line one")))
    at("event-2", queued(event("bzq8", "line two")))
    diff = json.loads(json.dumps(DIFF).replace("CANARY-KEY", C["bash-diff-key"]).replace("CANARY-ENV", C["bash-diff-env"]))
    at("bash-diff", m.call("toolu_fake_b12", "Bash", {"command": "bash scripts/zq-setup.sh"}))
    at("bash-diff-result", m.result("toolu_fake_b12", "ok", is_error=False, tur=bash_tur("ok", bashEditDiff=diff)))
    at("push", m.call("toolu_fake_p1", "Bash", {"command": "git push origin " + SHA1}))
    at("push-result", m.result("toolu_fake_p1", "== pushing %s ==\nparent %s" % (SHA1, SHA2), is_error=False))
    m.call("toolu_fake_c1", "mcp__github__actions_list", {"owner": "zq", "repo": "zq"})
    at("ci-result", m.result("toolu_fake_c1", json.dumps({"head_sha": SHA1, "conclusion": "success"})))
    at("long-token", m.owner("new token PC_BRIDGE_TOKEN=" + C["long-token"]))
    at("long-gh", m.owner("new key ghp_" + C["long-token"]))          # 44 characters: the GitHub rule's, not a pseudonym
    at("orphan-result", m.result("toolu_fake_missing", "ZQ_ORPHAN=" + C["orphan"]))

    # SESSION-EXPORT-R1. `bash` records a Bash call and its result under `name` and `name`-result.
    def bash(name, cid, command, result="ok\n"):
        at(name, m.call(cid, "Bash", {"command": command, "description": "x"}))
        at(name + "-result", m.result(cid, result, is_error=False, tur=bash_tur(result)))
    # R-1: a credential behind a JSON-escaped quote in a tool input, a hook, a notification and a stop-hook summary (the
    # verifier's json-* shapes), one escape level deeper, as a JSON Basic header, under a PASS name, and a 44-character token
    # (redacted, not a pseudonym: G6)
    bash("esc-export", "toolu_fake_x1", 'export PC_BRIDGE_TOKEN="%s" && bash scripts/pc.sh ls' % C["esc-export"])
    bash("esc-body", "toolu_fake_x2", "curl -s -d '{\"password\": \"%s\"}' https://api.example.com/login" % C["esc-body"])
    at("esc-write", m.call("toolu_fake_x3", "Write", {"file_path": "/srv/app/service.json", "content":
                                                      '{\n  "api_key": "%s",\n  "region": "eu"\n}\n' % C["esc-write"]}))
    m.result("toolu_fake_x3", "File created successfully at: /srv/app/service.json")
    at("esc-edit", m.call("toolu_fake_x4", "Edit", {"file_path": "/srv/app/app.yaml", "old_string": 'token: "x"',
                                                     "new_string": 'token: "%s"' % C["esc-edit"], "replace_all": False}))
    m.result("toolu_fake_x4", "The file has been updated successfully.")
    at("esc-hook", m.attachment({"type": "hook_success", "hookName": "PostToolUse:Bash", "hookEvent": "PostToolUse",
                                 "toolUseID": "toolu_fake_x1", "command": "python3 hook.py", "content": "ok",
                                 "stdout": '{"token": "%s"}' % C["esc-hook"], "stderr": "", "exitCode": 0,
                                 "durationMs": 5}))
    at("esc-notice", m.attachment({"type": "structured_output", "data": {"note": 'secret: "%s"' % C["esc-notice"]}}))
    at("esc-stop", m.system("stop_hook_summary", hookCount=1, hookInfos=[{"command": "~/.claude/stop.sh", "durationMs": 3}],
                            hookErrors=['retry with password="%s"' % C["esc-stop"]], preventedContinuation=False,
                            stopReason="", hasOutput=True, level="suggestion", toolUseID="toolu_fake_s2",
                            hookAdditionalContext=[]))
    bash("esc-deep", "toolu_fake_x5", 'curl -d "{\\"password\\": \\"%s\\"}" https://api.example.com/login' % C["esc-deep"])
    at("esc-basic", m.call("toolu_fake_x6", "Write", {"file_path": "/srv/app/h.json", "content":
                                                      '{"headers": {"Authorization": "Basic %s"}}' % C["esc-basic"]}))
    m.result("toolu_fake_x6", "File created successfully at: /srv/app/h.json")
    bash("esc-pass", "toolu_fake_x7", 'export DB_PASS="%s" && ./run.sh' % C["esc-pass"])
    bash("esc-long", "toolu_fake_x8", 'export PC_BRIDGE_TOKEN="%s" && bash scripts/pc.sh ls' % C["esc-long"])
    # R-2: a call that names the pseudonym key, in any spelling, loses its result; the xxd column is what the strict pass
    # left (F-4). Its input stays.
    for name, cid, command in (("key-xxd", "toolu_fake_k1", "xxd /root/.config/session-export/pseudonym.key; "
                                                             "cat /root/.config/session-export/pseudonym.key"),
                               ("key-rel", "toolu_fake_k2", "cd /root/.config/session-export && xxd pseudonym.key"),
                               ("key-lone", "toolu_fake_k3", "xxd pseudonym.key && base64 -w 16 pseudonym.key")):
        bash(name, cid, command, xxd(C[name].encode()) + C[name] + "\n")
    # R-3: named shapes the payload pass missed (F-5, F-6)
    bash("bearer-lower", "toolu_fake_n1", "python3 show_headers.py", "authorization: bearer %s\n" % C["bearer-lower"])
    bash("curl-user", "toolu_fake_n2", "curl -s -u bob:%s https://api.example.com/v1/me" % C["curl-user"], "{}\n")
    bash("db-pass", "toolu_fake_n3", "printenv | grep DB_", "DB_HOST=db.internal\nDB_PASS=%s\n" % C["db-pass"])
    bash("url-user", "toolu_fake_n4", "git remote -v", "origin https://%s@github.com/zq/zq.git (fetch)\n" % C["url-user"])
    bash("url-at-tail", "toolu_fake_n5", "git remote -v",
         "origin https://bob:zqp1zqp1@%s@db.example.com/app (fetch)\n" % C["url-at-tail"])
    # R-3 (F-7): secret-path spellings. Each result holds its canary alone on a line, which only the strict pass takes.
    for name, cid, command in (("path-home", "toolu_fake_q1", "cat $HOME/.config/qwen-builder/api-key"),
                               ("path-tilde", "toolu_fake_q2", "cat ~/.config/qwen-jev/omniroute.key"),
                               ("path-rel", "toolu_fake_q3", "cd ~/.config/qwen-builder && cat api-key"),
                               ("path-quoted", "toolu_fake_q4", "cat '/root/.config/qwen-builder'/api-key"),
                               ("path-glob", "toolu_fake_q5", "cat ~/.config/qwen-*/api-key")):
        bash(name, cid, command, C[name] + "\n")
    bash("path-glob-env", "toolu_fake_q6", "cat '/home/user/agent-factory/.pc-bridge.e'*",
         "ZQ_ENDPOINT=%s\n" % C["path-glob-env"])
    for name, cid, path in (("path-dot", "toolu_fake_q7", "/root/.config/qwen-builder/./api-key"),
                            ("path-dslash", "toolu_fake_q8", "/root/.config/qwen-builder//api-key")):
        at(name, m.call(cid, "Read", {"file_path": path}))
        at(name + "-result", m.result(cid, "     1\t" + C[name]))
    # ... and in an attachment's path and a Bash file change's path
    at("att-spelled", m.attachment({"type": "file", "filename": "/root/.config/qwen-builder//api-key",
                                    "content": {"type": "text", "file": {"filePath": "/root/.config/qwen-builder//api-key",
                                                                         "content": "zq fake key body", "numLines": 1}}}))
    spelled = {"changedFiles": ["/root/.config/qwen-builder/./api-key"],
               "files": [{"filePath": "/root/.config/qwen-builder/./api-key",
                          "hunks": [{"oldStart": 0, "oldLines": 0, "newStart": 1, "newLines": 1,
                                     "lines": ["+zq fake key body"]}]}]}
    at("diff-spelled", m.call("toolu_fake_q9", "Bash", {"command": "bash scripts/zq-rotate.sh", "description": "x"}))
    at("diff-spelled-result", m.result("toolu_fake_q9", "ok\n", is_error=False, tur=bash_tur("ok\n", bashEditDiff=spelled)))
    # AMENDMENT 3 (R-4): a run the fixture repo commits stays as it is, in the payload pass and the strict pass; an
    # uncommitted one becomes a pseudonym or is redacted; the named rules still take a committed fake token first
    bash("a3-normal", "toolu_fake_a1", "python3 -m pytest -q tests/test_zq.py",
         "%s::%s PASSED\n%s::%s FAILED\n" % (COMMITTED_PATH, COMMITTED_NAME, COMMITTED_PATH, UNCOMMITTED_NAME))
    bash("a3-strict", "toolu_fake_a2", "set -a; . ./.pc-bridge.env; set +a; bash scripts/zq-suite.sh",
         "%s::test_zq_x PASSED\n%s\nZQ_BRANCH=%s\nZQ_RUN=%s\nPC_BRIDGE_TOKEN=%s\n%s\n" % (
             COMMITTED_PATH, COMMITTED_PATH, COMMITTED_BRANCH, C["a3-strict"], COMMITTED_FAKE, COMMITTED_FAKE))
    at("bad-line", m.add("not json at all"))
    m.write(root / MAIN, tail=PARTIAL)

    sub = "-home-user/%s/subagents/agent-azqfake01.jsonl" % SID
    s = Tape(proj, agent="azqfake01")
    at("sub-prompt", s.user("You are a fake lane. api_key: " + C["sub-prompt"]), sub)
    at("sub-text", s.assistant([{"type": "text", "text": "key sk-" + C["sk-key"]}], stop="end_turn"), sub)
    at("sub-thinking", s.assistant([{"type": "thinking", "thinking": "thinking about it", "signature": "x"}]), sub)
    at("sub-call", s.call("toolu_fake_sb1", "Bash", {"command": "ls"}), sub)
    at("sub-result", s.result("toolu_fake_sb1", "a\nb", is_error=False, tur=bash_tur("a\nb")), sub)
    at("sub-reminder", s.user("<system-reminder>r</system-reminder>", isMeta=True), sub)
    at("sub-meta-coord", s.user("Coordinator note: keep going", isMeta=True, origin={"kind": "coordinator"}), sub)
    at("sub-notif", s.user("Background task done", isMeta=True, origin={"kind": "task-notification"}), sub)
    at("sub-followup", s.attachment({"type": "queued_command", "isMeta": True, "origin": {"kind": "coordinator"},
                                     "prompt": "Coordinator follow-up: password=" + C["sub-followup"]}), sub)
    at("sub-later", s.user([{"type": "text", "text": "please continue"}]), sub)
    s.write(root / sub)

    jr = "-home-user/%s/subagents/workflows/wf_zqfake-001/journal.jsonl" % SID
    j = Tape(proj)
    at("journal-started", j.add({"type": "started", "agentId": "azqwf01", "key": "build"}), jr)
    at("journal-result", j.add({"type": "result", "agentId": "azqwf01", "key": "build",
                                "result": {"notes": "token " + C["journal-gh"]}}), jr)
    j.write(root / jr)

    wf = "-home-user/%s/subagents/workflows/wf_zqfake-001/agent-azqwf01.jsonl" % SID
    w = Tape(proj, agent="azqwf01")
    at("wf-prompt", w.user("Repo at /x. Build it."), wf)
    at("wf-text", w.assistant([{"type": "text", "text": "done"}], stop="end_turn"), wf)
    w.write(root / wf)

    t = Tape(proj)
    at("second-owner", t.owner("hello from the second folder"), SECOND)
    at("second-text", t.assistant([{"type": "text", "text": "noted"}], stop="end_turn"), SECOND)
    t.write(root / SECOND)

    arch = pathlib.Path(proj) / ARCHIVES                      # the pruner's archives, as it writes them
    arch.mkdir(parents=True, exist_ok=True)
    (arch / ".gitignore").write_text("*\n")
    (arch / "bash-toolu_fake_b11.txt").write_text("y " * 20000 + "\nAGENT_TOKEN=" + C["archive-token"] + "\n")
    (arch / "bash-toolu_fake_b1.txt").write_text("ZQ_ENDPOINT=" + C["archive-env"] + "\n")
    (arch / "bash-1727000000000.txt").write_text("a clock-named archive: no call id\n")
    (arch / "bash-toolu_fake_none.txt").write_text("an archive whose call is in no transcript\n")
    L["asst"] = {MAIN: m.asst, sub: s.asst, jr: j.asst, wf: w.asst, SECOND: t.asst}
    return L


def _run(*args):
    return subprocess.run([sys.executable, str(TOOL), *map(str, args)], capture_output=True, text=True, timeout=600)


def _key(where):
    """A pseudonym key made by the CLI's own init-key (32 bytes, mode 0600); returns (path, bytes)."""
    path = pathlib.Path(where) / "cfg" / "pseudonym.key"
    r = _run("init-key", "--key", path)
    assert r.returncode == 0, r.stderr[-500:]
    return path, path.read_bytes()


def _export(tree, out, key, *extra, jobs=2):
    return _run("export", "--root", tree, "--out", out, "--jobs", jobs, "--key", key, "--repo", REPO["path"], *extra)


def _say(text, C):
    """A process's output for a failure message, withheld whole if it holds a canary."""
    return "<output withheld: it holds a canary>" if _leaks(text, C) else text[-3000:]


def _leaks(blob, canaries):
    """Names of the canaries whose value, or any 8-character window of it, is in blob. Never the values."""
    return sorted(n for n, v in canaries.items() if v in blob or any(v[i:i + 8] in blob for i in range(len(v) - 7)))


def _blob(out):
    """Every exported byte as text: each .xz decompressed as a stream, and the manifest."""
    parts = []
    for p in sorted(out.rglob("*")):
        if p.name.endswith(".xz"):
            with lzma.open(p, "rt", encoding="utf-8") as fh:
                parts.extend(fh)
        elif p.is_file():
            parts.append(p.read_text())
    return "".join(parts)


def _events(out):
    ev = {}
    for p in sorted(out.rglob("*.jsonl.xz")):
        src = str(p.relative_to(out))[:-3]
        with lzma.open(p, "rt", encoding="utf-8") as fh:
            ev[src] = [json.loads(line) for line in fh]
    return ev


def _manifest(out):
    return json.loads((out / "manifest.json").read_text())


def _main_entry(out):
    return next(s for s in _manifest(out)["sources"] if s["src"] == MAIN)


def _hmac12(key, value):
    return hmac.new(key, value.encode(), hashlib.sha256).hexdigest()[:12]


def _canon(obj):
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _digests(events):
    """Each event as a digest: a list comparison that fails prints no payload."""
    return [hashlib.sha256(_canon(e).encode()).hexdigest()[:16] for e in events]


def _expect(C, actual, expected, what):
    """actual == expected, else an AssertionError naming `what`, the first differing character, both lengths and the
    canaries in `actual`, never the text: a printed canary would reach this session's transcript, which the next real
    export's leak gate counts."""
    if actual != expected:
        a, e = (x if isinstance(x, str) else _canon(x) for x in (actual, expected))
        i = next((k for k, (p, q) in enumerate(zip(a, e)) if p != q), min(len(a), len(e)))
        raise AssertionError("%s differs at character %d (lengths %d, %d); canaries in it: %s"
                             % (what, i, len(a), len(e), _leaks(a, C)))


@pytest.fixture(scope="module")
def exported(tmp_path_factory, se):
    """One export of the synthetic tree through the real CLI (two workers), shared by the read-only tests below."""
    base = tmp_path_factory.mktemp("export")
    tree = base / "tree"
    L = build_tree(tree, se.CANARIES, base / "proj")
    key_path, key = _key(base)
    r = _export(tree, base / "out", key_path)
    return tree, base / "out", L, r, key


def test_the_canaries_are_many_long_and_share_no_window(se):
    # the window check below names the canary that leaked only if no two canaries share an 8-character window
    C = se.CANARIES
    sizes = sorted(len(v) for v in C.values())
    owner, clashes = {}, set()
    for name, value in C.items():
        for i in range(len(value) - 7):
            other = owner.setdefault(value[i:i + 8], name)
            if other != name:
                clashes.add((other, name))
    clashes = sorted(clashes)
    assert len(sizes) >= 30 and sizes[0] >= 16 and clashes == [], (len(sizes), sizes[0], clashes)


def test_no_canary_survives_the_export(se, exported):
    C = se.CANARIES
    tree, out, L, r, key = exported
    rc, said = r.returncode, r.stdout + r.stderr
    assert rc == 0, _say(said, C)
    leaked_export, leaked_said = _leaks(_blob(out), C), _leaks(said, C)
    assert leaked_export == [] and leaked_said == []
    gate = _manifest(out)["gate"]
    assert gate["total"] == 0 and gate["files"] == 5, gate
    g = _run("gate", out)
    grc, gsaid = g.returncode, g.stdout + g.stderr
    leaked_gate = _leaks(gsaid, C)
    assert grc == 0 and leaked_gate == [], _say(gsaid, C)


def test_the_canaries_show_when_the_protections_are_off(tmp_path, se, monkeypatch):
    # negative control: with the scrubbers and the path denylist disabled, every canary the export reads reaches the
    # output (so the test above can fail), and the gate counts them; the records it never reads stay out
    C = se.CANARIES
    tree = tmp_path / "tree"
    build_tree(tree, C, tmp_path / "proj")
    key_path, _ = _key(tmp_path)
    monkeypatch.setattr(se, "scrub_payload", lambda s, opaque=None: s)
    monkeypatch.setattr(se, "scrub_strict", lambda s, opaque=None, keep=(): s)
    monkeypatch.setattr(se, "SECRET_PATH", re.compile(r"(?!)"))          # every spelling of a secret path goes through it
    out = tmp_path / "out"
    rc = se.main(["export", "--root", str(tree), "--out", str(out), "--jobs", "1", "--key", str(key_path),
                  "--repo", str(REPO["path"])])
    shown, expected = _leaks(_blob(out), C), sorted(set(C) - NEVER_READ)
    assert rc == 3 and shown == expected
    gate = _manifest(out)["gate"]
    missed = sorted(n for n in set(C) - NEVER_READ - {"cap-straddle"} if not gate["canaries"].get(n))
    assert gate["total"] > 0 and missed == [], missed


def _one(ev, L, name, kind=None):
    src, line = L[name]
    got = [e for e in ev[src] if e["line"] == line and (kind is None or e["kind"] == kind)]
    assert len(got) == 1, (name, [(e["kind"], e["role"]) for e in got])
    return got[0]


def test_events_keep_the_schema(se, exported):
    tree, out, L, r, key = exported
    ev = _events(out)
    assert sorted(ev) == sorted({MAIN, SECOND, L["sub-prompt"][0], L["journal-started"][0], L["wf-prompt"][0]})
    for src, events in ev.items():
        assert [e["seq"] for e in events] == list(range(len(events)))
        assert [e["line"] for e in events] == sorted(e["line"] for e in events)
        for e in events:
            assert list(e) == KEYS and e["src"] == src and e["role"] in ROLES and e["kind"] in KINDS, e["kind"]
            assert isinstance(e["text"], str) and (e["ts"] is None or isinstance(e["ts"], str))
            assert (e["outcome"] is not None) == (e["kind"] == "tool_result" or (src, e["line"]) in (L["stop-summary"],
                                                                                                        L["esc-stop"]))
            assert (e["tool"] is not None) <= (e["kind"] in ("tool_call", "tool_result", "file_change", "pruner_archive"))


def test_every_project_folder_is_read(se, exported):
    # AMENDMENT 2: every folder under the projects root; `src` names the folder, so one session id in two folders is two
    # sources, and a transcript directly in its folder is a session transcript (the owner's text)
    tree, out, L, r, key = exported
    folders = {k: v["sources"] for k, v in _manifest(out)["totals"]["folders"].items()}
    assert folders == {"-home-user": 4, "-home-user-agent-factory": 1}
    second = _events(out)[SECOND]
    assert [(e["role"], e["kind"], e["text"]) for e in second] == [("owner", "text", "hello from the second folder"),
                                                                    ("coordinator", "text", "noted")]


def test_roles_follow_the_transcript_type(se, exported):
    tree, out, L, r, key = exported
    ev = _events(out)
    want = {"banner": ("owner", "text"), "thinking": ("coordinator", "thinking"), "text": ("coordinator", "text"),
            "write-env": ("coordinator", "tool_call"), "write-env-result": ("tool", "tool_result"),
            "queued-owner": ("owner", "text"), "queued-notif": ("system", "notification"),
            "queued-agent": ("agent", "text"), "peer-user": ("agent", "text"),
            "hook-success": ("hook", "hook"), "hook-context": ("hook", "hook"),
            "att-file": ("system", "notification"), "future-att": ("system", "notification"),
            "att-edited": ("system", "harness_notice"), "notice": ("system", "harness_notice"),
            "api-error": ("system", "api_error"), "sys-api-error": ("system", "api_error"),
            "stop-summary": ("hook", "hook"), "stop-feedback": ("hook", "hook"), "compact": ("system", "summary"),
            "notif-user": ("system", "notification"), "reminder": ("system", "notification"),
            "interrupt": ("system", "notification"), "command-name": ("owner", "text"),
            "boundary": ("system", "notification"), "orphan-result": ("tool", "tool_result"),
            "sub-prompt": ("coordinator", "text"), "sub-text": ("agent", "text"), "sub-thinking": ("agent", "thinking"),
            "sub-call": ("agent", "tool_call"), "sub-result": ("tool", "tool_result"),
            "sub-reminder": ("system", "notification"), "sub-meta-coord": ("coordinator", "text"),
            "sub-notif": ("system", "notification"), "sub-followup": ("coordinator", "text"),
            "sub-later": ("coordinator", "text"), "journal-started": ("system", "notification"),
            "journal-result": ("system", "notification"), "wf-prompt": ("coordinator", "text"), "wf-text": ("agent", "text")}
    got = {name: (_one(ev, L, name)["role"], _one(ev, L, name)["kind"]) for name in want}
    assert got == want
    image = [e for e in ev[L["image"][0]] if e["line"] == L["image"][1]]
    assert [(e["role"], e["text"]) for e in image] == [("owner", "[image: image/png]"), ("owner", "what is this")]


def test_outcomes_are_the_harness_fields(se, exported):
    tree, out, L, r, key = exported
    ev = _events(out)
    want = {"bash-env-result": {"is_error": False}, "bash-curl-result": {"is_error": True, "exit_code": 7},
            "bash-timeout-result": {"is_error": True, "timed_out_after_ms": 120000},
            "bash-denied-result": {"is_error": True, "denial_kind": "automode-blocked"},
            "exit-prose-result": {"is_error": False},                  # `Exit code N` counts only on an error result
            "write-env-result": {}, "read-pem-result": {}, "orphan-result": {}}
    assert {name: _one(ev, L, name, "tool_result")["outcome"] for name in want} == want
    assert _one(ev, L, "stop-summary")["outcome"] == {"hook_errors": ["push the branch; link https://<bridge-link-redacted>"]}
    assert _one(ev, L, "bash-curl-result")["tool"] == "Bash" and _one(ev, L, "bash-curl-result")["call_id"] == "toolu_fake_b5"
    assert _one(ev, L, "orphan-result")["tool"] is None


def test_model_and_stop_reason_come_from_the_record(se, exported):
    # G2: every event carries the model and stop reason of its record: an assistant record's, null for any other
    tree, out, L, r, key = exported
    ev = _events(out)
    wrong = [(src, e["line"], e["kind"]) for src, events in ev.items() for e in events
             if (e["model"] is not None) != (e["line"] in L["asst"][src]) or (e["model"] is None and e["stop_reason"] is not None)]
    assert wrong == []
    api = _one(ev, L, "api-error")
    assert (api["model"], api["stop_reason"], api["outcome"]) == ("<synthetic>", "stop_sequence", None)
    _expect(se.CANARIES, api["text"], "API Error: 429 rate limited; Authorization: Bearer <redacted>", "api-error")
    assert (_one(ev, L, "text")["model"], _one(ev, L, "text")["stop_reason"]) == ("claude-fake", "end_turn")
    assert _one(ev, L, "bash-env")["stop_reason"] == "tool_use" and _one(ev, L, "sys-api-error")["model"] is None
    assert json.loads(_one(ev, L, "sys-api-error")["text"])["error"] == {"type": "overloaded_error"}


def test_edited_files_are_harness_notices(se, exported):
    # G1: the harness's edited_text_file attachment is its own kind; the path denylist still drops a secret file's
    tree, out, L, r, key = exported
    ev = _events(out)
    _expect(se.CANARIES, json.loads(_one(ev, L, "notice")["text"]), {
        "filename": "/home/user/agent-factory/scripts/zq.py", "snippet": "     3\tzq_token=<redacted>",
        "type": "edited_text_file"}, "notice")
    _expect(se.CANARIES, _one(ev, L, "att-edited")["text"], DROPPED, "att-edited")


def test_secret_paths_are_dropped_or_strict_passed(se, exported):
    C = se.CANARIES
    tree, out, L, r, key = exported
    ev = _events(out)
    for name in ("write-env", "write-env-result", "read-key", "read-key-result", "read-pkey", "read-pkey-result",
                 "edit-hermes", "edit-hermes-result", "att-file", "att-edited"):
        _expect(C, _one(ev, L, name)["text"], DROPPED, name)
    _expect(C, _one(ev, L, "bash-env")["text"],
            _canon({"command": "cat /home/user/agent-factory/.pc-bridge.env", "description": "show env"}), "bash-env")
    _expect(C, _one(ev, L, "bash-env-result", "tool_result")["text"],
            "PC_BRIDGE_URL=<redacted>\nPC_BRIDGE_TOKEN=<redacted>\nZQ_ENDPOINT=<redacted>\n", "bash-env-result")
    _expect(C, _one(ev, L, "bash-grep-result")["text"], "4:ZQ_KEYRING=<redacted>", "bash-grep-result")
    _expect(C, _one(ev, L, "bash-key-result")["text"], "<redacted>\n", "bash-key-result")
    _expect(C, _one(ev, L, "grep-env-result")["text"], "PC_EXTRA_SETTING=<redacted>", "grep-env-result")  # any tool
    _expect(C, _one(ev, L, "orphan-result")["text"], "ZQ_ORPHAN=<redacted>", "orphan-result")    # no call seen: strict
    _expect(C, json.loads(_one(ev, L, "grep-env")["text"])["path"], "/srv/app/.env", "grep-env")  # the input stays
    bearer = "Bearer <redacted>" in _one(ev, L, "bash-curl")["text"]
    assert bearer, "bash-curl: no redacted Bearer token"
    main = _main_entry(out)
    # 11 and 6 before R1; R1 adds 3 key results, 2 Reads (a call and its result each), a spelled attachment and a spelled
    # file change dropped, and 7 strict results (6 path spellings and the AMENDMENT 3 source-only call)
    assert (main["dropped_secret_path"], main["strict_results"]) == (20, 13)


def test_cap_keeps_head_and_tail(se, exported):
    tree, out, L, r, key = exported
    e = _one(_events(out), L, "big-result")
    scrubbed_len = L["big-raw-len"] - len(se.CANARIES["cap-straddle"]) + len("<redacted>")
    assert e["truncated"] == {"kept_head": 24576, "kept_tail": 8192, "dropped": scrubbed_len - 32768}
    tail_ok = len(e["text"]) == 32768 and e["text"].endswith("v " * 100)
    assert tail_ok, "big-result: not 32,768 characters ending in the source's tail"
    _expect(se.CANARIES, e["text"][:24576], "w " * (BIG_HEAD // 2) + "PC_BRIDGE_TOKEN=<redacted> v", "big-result head")


def test_read_results_and_write_inputs_get_the_large_cap(se, exported):
    # G3: a Read result and a Write input keep 98,304 + 32,768 characters; every other event 24,576 + 8,192
    tree, out, L, r, key = exported
    ev = _events(out)
    read, write = _one(ev, L, "read-big-result"), _one(ev, L, "write-big")
    bash = _one(ev, L, "bash-big-result", "tool_result")
    write_len = len(_canon({"content": "x " * 70000, "file_path": "/tmp/zq-big.txt"}))
    assert read["truncated"] == {"kept_head": 98304, "kept_tail": 32768, "dropped": 150000 - 131072}
    assert write["truncated"] == {"kept_head": 98304, "kept_tail": 32768, "dropped": write_len - 131072}
    assert bash["truncated"] == {"kept_head": 24576, "kept_tail": 8192, "dropped": 40000 - 32768}
    assert (len(read["text"]), len(write["text"]), len(bash["text"])) == (131072, 131072, 32768)
    assert write["text"].endswith('x ","file_path":"/tmp/zq-big.txt"}')
    assert _main_entry(out)["capped"] == {"tool_call": 1, "tool_result": 3}


def test_a_repeated_notification_is_kept_once(se, exported):
    # G4: the first of two records with one notification identity (task id, tool-use id, status or event) stays
    tree, out, L, r, key = exported
    ev = _events(out)
    kept = ["note-1", "note-2", "note-3", "note-3-again", "event-1", "event-2", "queued-notif", "notif-user"]
    gone = ["note-1-again", "event-1-again"]
    lines = {src: {e["line"] for e in events} for src, events in ev.items()}
    assert [n for n in kept if L[n][1] not in lines[L[n][0]]] == [] and [n for n in gone if L[n][1] in lines[L[n][0]]] == []
    assert _main_entry(out)["duplicate_notifications"] == 2


def test_bash_file_changes_follow_the_result(se, exported):
    # G5: toolUseResult.bashEditDiff becomes one file_change per changed file, right after the result, in the
    # changedFiles order; a secret file's change is dropped; a changed file with no recorded diff says so
    tree, out, L, r, key = exported
    src, line = L["bash-diff-result"]
    events = [e for e in _events(out)[src] if e["line"] == line]
    assert [(e["role"], e["kind"], e["tool"], e["call_id"], e["outcome"]) for e in events] == \
        [("tool", "tool_result", "Bash", "toolu_fake_b12", {"is_error": False})] + \
        [("tool", "file_change", "Bash", "toolu_fake_b12", None)] * 3
    _expect(se.CANARIES, [e["text"] for e in events[1:]], [
        "/home/user/agent-factory/scripts/zq.py\n@@ -1,1 +1,2 @@\n-x = 1\n+x = 2\n+API_KEY = '<redacted>'",
        "/home/user/agent-factory/docs/zq.md\n[diff not recorded]",
        DROPPED], "file changes")
    assert [e["seq"] for e in events] == list(range(events[0]["seq"], events[0]["seq"] + 4))
    assert _main_entry(out)["file_changes_unrecorded"] == 2


def test_pruner_archives_follow_their_results(se, exported):
    # AMENDMENT 2: the pruner's archive of a result it trimmed is one pruner_archive event right after that result,
    # through the result's own scrub (the strict pass where its call named a secret file) and the large cap
    tree, out, L, r, key = exported
    ev = _events(out)
    src, line = L["bash-big-result"]
    at = [e for e in ev[src] if e["line"] == line]
    assert [(e["kind"], e["role"], e["tool"], e["call_id"]) for e in at] == [
        ("tool_result", "tool", "Bash", "toolu_fake_b11"), ("pruner_archive", "tool", "Bash", "toolu_fake_b11")]
    _expect(se.CANARIES, at[1]["text"], "y " * 20000 + "\nAGENT_TOKEN=<redacted>\n", "archive of toolu_fake_b11")
    assert at[1]["truncated"] is None and at[1]["outcome"] is None and at[1]["seq"] == at[0]["seq"] + 1
    _expect(se.CANARIES, _one(ev, L, "bash-env-result", "pruner_archive")["text"], "ZQ_ENDPOINT=<redacted>\n",
            "archive of toolu_fake_b1")
    m = _manifest(out)
    tot = m["totals"]
    assert (tot["archives"], tot["pruner_archives"], tot["archives_unlinked"], tot["archives_unmatched"],
            tot["archives_skipped"]) == (4, 2, 1, 1, 0)
    assert sorted(x["call_id"] or "-" for x in m["archives"]) == ["-", "toolu_fake_b1", "toolu_fake_b11", "toolu_fake_none"]


def test_opaque_values_become_stable_keyed_pseudonyms(se, exported):
    # G6: a value only the opaque-run rule takes becomes [opaque:<HMAC-SHA256(key, value)[:12]>], the same in every
    # event; another value another pseudonym; a long value a named rule takes stays redacted
    tree, out, L, r, key = exported
    ev = _events(out)
    p1, p2 = "[opaque:%s]" % _hmac12(key, SHA1), "[opaque:%s]" % _hmac12(key, SHA2)
    assert p1 != p2
    C = se.CANARIES
    _expect(C, _one(ev, L, "push")["text"], _canon({"command": "git push origin " + p1}), "push")
    _expect(C, _one(ev, L, "push-result")["text"], "== pushing %s ==\nparent %s" % (p1, p2), "push-result")
    _expect(C, json.loads(_one(ev, L, "ci-result")["text"]), {"head_sha": p1, "conclusion": "success"}, "ci-result")
    _expect(C, _one(ev, L, "long-token")["text"], "new token PC_BRIDGE_TOKEN=<redacted>", "long-token")
    _expect(C, _one(ev, L, "long-gh")["text"], "new key gh<redacted>", "long-gh")   # no fixed point repairs a pseudonym
    blob = _blob(out)
    gone = SHA1 not in blob and SHA2 not in blob
    # 4 commit-id pseudonyms, and R1's uncommitted test name (AMENDMENT 3); the escaped 44-character token is redacted
    assert gone and _main_entry(out)["pseudonyms"] == 5, "a commit id survived, or the pseudonym count moved"


def test_the_key_is_never_exported_or_printed(se, exported):
    tree, out, L, r, key = exported
    seen = _blob(out) + r.stdout + r.stderr
    forms = [key.hex(), key.hex().upper(), base64.b64encode(key).decode(), base64.urlsafe_b64encode(key).decode()]
    found = [i for i, f in enumerate(forms) if f in seen]
    assert found == []
    kid = hmac.new(key, b"session-export key id", hashlib.sha256).hexdigest()[:12]
    m = _manifest(out)
    assert m["pseudonym_key_id"] == kid and all(m["gate"]["canaries"][n] == 0 for n in se.key_forms(key))


def test_init_key_creates_the_key_once(tmp_path, se):
    path = tmp_path / "cfg" / "pseudonym.key"
    r1 = _run("init-key", "--key", path)
    body = path.read_bytes()
    said1 = r1.stdout + r1.stderr
    assert r1.returncode == 0 and len(body) == 32 and stat.S_IMODE(path.stat().st_mode) == 0o600
    assert body.hex() not in said1 and base64.b64encode(body).decode() not in said1
    r2 = _run("init-key", "--key", path)
    assert r2.returncode == 2 and "exists" in r2.stderr and path.read_bytes() == body


def test_a_missing_or_loose_key_refuses(tmp_path, se):
    # G6: no key, a short key, a key others can read or a link to a key: the export refuses and writes nothing; it
    # never falls back
    tree = tmp_path / "tree"
    build_tree(tree, se.CANARIES, tmp_path / "proj")
    good, _ = _key(tmp_path)
    short, loose, link = tmp_path / "short.key", tmp_path / "loose.key", tmp_path / "link.key"
    short.write_bytes(os.urandom(16))
    short.chmod(0o600)
    loose.write_bytes(os.urandom(32))
    loose.chmod(0o644)
    link.symlink_to(good)
    for i, key in enumerate((tmp_path / "missing.key", short, loose, link)):
        out = tmp_path / ("o%d" % i)
        r = _export(tree, out, key, jobs=1)
        rc, err = r.returncode, _say(r.stderr, se.CANARIES)
        wrote = out.exists() and any(out.iterdir())
        assert rc == 2 and "key" in err and not wrote, (i, err)
    assert "init-key" in _export(tree, tmp_path / "o9", tmp_path / "missing.key", jobs=1).stderr
    with pytest.raises(se.KeyRefused):
        se.convert(str(tree / MAIN), MAIN)                    # the library path refuses too: no key, no events


def test_convert_in_parts_gives_the_same_events_as_one_pass(tmp_path, se):
    # AMENDMENT 2: a live file converted in three parts, each cut in the middle of a line the writer had not finished,
    # gives the one-pass events; the state carries the calls (a Read of a secret file in part 1, its result in part 2),
    # the notifications (the repeat in part 3) and the counters
    tree, proj = tmp_path / "tree", tmp_path / "proj"
    L = build_tree(tree, se.CANARIES, proj)
    key = os.urandom(32)
    archives = {x["call_id"]: x for x in se.find_archives([str(proj / ARCHIVES)]) if x["call_id"]}
    full = (tree / MAIN).read_bytes()
    whole, end, _ = se.convert(str(tree / MAIN), MAIN, 0, None, key=key, archives=archives)
    lines = full.split(b"\n")

    def mid(name):
        i = L[name][1] - 1
        return len(b"\n".join(lines[:i])) + 1 + len(lines[i]) // 2

    live = tmp_path / "live.jsonl"
    parts, offsets, offset, state = [], [], 0, None
    for cut in (mid("read-key-result"), mid("note-1-again"), len(full)):
        live.write_bytes(full[:cut])
        part, offset, state = se.convert(str(live), MAIN, offset, state, key=key, archives=archives)
        parts.append(part)
        offsets.append(offset)
    assert _digests([e for p in parts for e in p]) == _digests(whole) and len(whole) > 50
    assert offset == end == len(full) - len(PARTIAL) and offsets[0] < mid("read-key-result") < offsets[1]
    # negative control: the second part without the first part's state numbers its events from 0 again and does not know
    # the Read of a secret file its first result answers
    alone, _, _ = se.convert(str(live), MAIN, offsets[0], None, key=key, archives=archives)
    first = [e for e in alone if e["line"] == L["read-key-result"][1]][0]
    assert alone[0]["seq"] == 0 and parts[1][0]["seq"] == len(parts[0]) and first["text"] != DROPPED
    _expect(se.CANARIES, [e for e in parts[1] if e["line"] == L["read-key-result"][1]][0]["text"], DROPPED, "part 2")
    with pytest.raises(ValueError):
        se.convert(str(live), MAIN, offsets[0] + 1, None, key=key)          # not at a line boundary
    with pytest.raises(ValueError):
        se.convert(str(live), MAIN, 0, state, key=key)                      # a state from another offset


def test_thinking_and_skipped_records_are_counted(se, exported):
    tree, out, L, r, key = exported
    ev = _events(out)
    assert not [e for e in ev[L["signature-only"][0]] if e["line"] == L["signature-only"][1]]
    for name in ("tokens", "last-prompt", "queue-op", "atis"):
        assert not [e for e in ev[L[name][0]] if e["line"] == L[name][1]], name
    main = _main_entry(out)
    assert main["thinking_signature_only"] == 1 and main["bad_lines"] == 1
    assert main["skipped_attachments"] == {"total_tokens_reminder": 1}
    assert main["skipped_records"] == {"atis-latch": 1, "last-prompt": 1, "queue-operation": 1}
    raw = (tree / MAIN).read_bytes()
    assert main["offset"] == len(raw) - len(PARTIAL) and main["lines"] == raw.count(b"\n")
    assert main["input_sha256"] == hashlib.sha256(raw[:main["offset"]]).hexdigest()


def test_the_cap_seam_forms_no_secret_shape(tmp_path, se):
    # a 20-character run ends the head and a 24-character run starts the tail: joined they would be one 44-character run,
    # which the opaque rule reads as a secret; the cut moves inward to a seam that forms none, and says so
    fill = "w " * 20000
    text = fill[:24576 - 20] + "A1" * 10 + fill[:6000] + "B2" * 12 + fill[:8192 - 24]
    t = Tape(tmp_path / "proj")
    t.call("toolu_fake_z1", "Bash", {"command": "python3 seam.py"})
    line = t.result("toolu_fake_z1", text, is_error=False)
    tree = tmp_path / "tree"
    t.write(tree / "-seam" / "seam.jsonl")
    key_path, _ = _key(tmp_path)
    r = _export(tree, tmp_path / "out", key_path, jobs=1)
    assert r.returncode == 0, r.stderr[-2000:]
    e = [e for e in _events(tmp_path / "out")["-seam/seam.jsonl"] if e["line"] == line][0]
    assert e["truncated"] == {"kept_head": 24576 - 64, "kept_tail": 8192 - 64, "dropped": len(text) - 32768 + 128}
    assert e["text"] == text[:24576 - 64] + text[-(8192 - 64):]
    assert re.search(r"[A-Za-z0-9_\-]{40,}", e["text"]) is None
    assert _manifest(tmp_path / "out")["sources"][0]["seam_adjusted"] == 1


def _shas(out):
    return {str(p.relative_to(out)): hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(out.rglob("*.xz"))}


def test_fixed_offsets_give_byte_identical_output(tmp_path, se):
    C = se.CANARIES
    tree, proj = tmp_path / "tree", tmp_path / "proj"
    build_tree(tree, C, proj)
    key_path, _ = _key(tmp_path)
    r1 = _export(tree, tmp_path / "o1", key_path)
    rc1 = r1.returncode
    assert rc1 == 0, _say(r1.stderr, C)
    main = tree / MAIN
    with open(main, "a") as fh:                              # the live file grows: the partial line ends, one more comes
        fh.write('"}\n' + json.dumps({"type": "user", "message": {"role": "user", "content": "ZQ-APPENDED-LATER"},
                                      "origin": {"kind": "human"}}) + "\n")
    (proj / ARCHIVES / "bash-toolu_fake_b4.txt").write_text("ZQ-ARCHIVED-LATER\n")   # and the pruner writes one more
    r2 = _export(tree, tmp_path / "o2", key_path, "--offsets", tmp_path / "o1" / "manifest.json")
    rc2 = r2.returncode
    assert rc2 == 0, _say(r2.stderr, C)
    s1, s2 = _shas(tmp_path / "o1"), _shas(tmp_path / "o2")
    assert s1 == s2 and len(s1) == 5
    m1 = _manifest(tmp_path / "o1")
    assert {s["output"]: s["output_sha256"] for s in m1["sources"]} == s1
    blob2 = _blob(tmp_path / "o2")
    past = "ZQ-APPENDED-LATER" in blob2 or "ZQ-ARCHIVED-LATER" in blob2
    assert not past, "the rerun read past its offsets"
    r3 = _export(tree, tmp_path / "o3", key_path)                                      # negative control: new offsets
    blob3 = _blob(tmp_path / "o3")
    rc3, later = r3.returncode, "ZQ-APPENDED-LATER" in blob3 and "ZQ-ARCHIVED-LATER" in blob3
    assert rc3 == 0 and later
    assert _shas(tmp_path / "o3")[MAIN + ".xz"] != s1[MAIN + ".xz"]


def test_offsets_refuse_a_changed_prefix_or_archive(tmp_path, se):
    tree, proj = tmp_path / "tree", tmp_path / "proj"
    build_tree(tree, se.CANARIES, proj)
    key_path, _ = _key(tmp_path)
    assert _export(tree, tmp_path / "o1", key_path, jobs=1).returncode == 0
    main = tree / MAIN
    original = main.read_bytes()
    main.write_bytes(original.replace(b"Plan: write", b"Plan: wrote", 1))
    r = _export(tree, tmp_path / "o2", key_path, "--offsets", tmp_path / "o1" / "manifest.json", jobs=1)
    rc, err, wrote = r.returncode, _say(r.stderr, se.CANARIES), (tmp_path / "o2" / "manifest.json").exists()
    assert rc == 2 and "changed" in err and not wrote, err
    main.write_bytes(original)
    (proj / ARCHIVES / "bash-toolu_fake_b11.txt").write_text("rewritten after the offsets were fixed\n")
    r = _export(tree, tmp_path / "o3", key_path, "--offsets", tmp_path / "o1" / "manifest.json", jobs=1)
    rc, err, wrote = r.returncode, _say(r.stderr, se.CANARIES), (tmp_path / "o3" / "manifest.json").exists()
    assert rc == 2 and "archive" in err and not wrote, err


def test_export_refuses_a_used_out_dir(tmp_path, se):
    tree = tmp_path / "tree"
    build_tree(tree, se.CANARIES, tmp_path / "proj")
    key_path, _ = _key(tmp_path)
    (tmp_path / "o").mkdir()
    (tmp_path / "o" / "old.txt").write_text("x")
    r = _export(tree, tmp_path / "o", key_path, jobs=1)
    rc, err = r.returncode, _say(r.stderr, se.CANARIES)
    assert rc == 2 and "not empty" in err, err


def test_gate_counts_patterns_and_canaries_and_prints_none(tmp_path, se):
    C = se.CANARIES
    fake = "Fk1eGateValue0001"                                 # fake, credential-shaped, left unscrubbed on purpose
    d = tmp_path / "exp"
    d.mkdir()
    long_name = "mcp__Fake_Server_Name__some_long_tool_name_x"   # 44 identifier characters: a harness tool name
    rows = [{"seq": 0, "text": "AGENT_TOKEN=" + fake}, {"seq": 1, "text": "AGENT_TOKEN=<redacted> is a fixed point"},
            {"seq": 2, "text": "holds " + C["bridge-token"]}, {"seq": 3, "outcome": {"hook_errors": ["ghp_" + "Zq9" * 9]}},
            {"seq": 4, "tool": long_name, "call_id": "toolu_" + "Q1" * 20},   # names: the opaque-run rule skips them
            {"seq": 5, "text": long_name},                                    # the same string as text: counted
            {"seq": 6, "tool": "x " + "q" * 44},                              # not one identifier: counted
            {"seq": 7, "text": "pushed [opaque:0123456789ab] and [opaque:ba9876543210]"}]   # pseudonyms: not counted
    r1 = {"escaped-credential": 'export PC_BRIDGE_TOKEN=\\"Fk1eGateEsc0002\\" && ls',          # R1: one of each new shape
          "bearer-lower": "authorization: bearer Fk1eGateLow0003", "curl-user": "curl -u bob:Fk1eGateCurl0004 https://x",
          "pass-name": "DB_PASS=Fk1eGatePass0005", "url-token-user": "https://Fk1eGateUser0006x@github.com/zq"}
    rows += [{"seq": 8 + i, "text": t} for i, t in enumerate(r1.values())]
    with lzma.open(d / "x.jsonl.xz", "wt", encoding="utf-8") as fh:
        fh.writelines(json.dumps(r) + "\n" for r in rows)
    r = _run("gate", d)
    rc, said = r.returncode, r.stdout + r.stderr
    leaked = _leaks(said, C)
    assert rc == 3 and said.count(fake) == 0 and said.count("Zq9Zq9Zq9") == 0 and leaked == []
    assert [v for v in ("Fk1eGateEsc", "Fk1eGateLow", "Fk1eGateCurl", "Fk1eGatePass", "Fk1eGateUser") if v in said] == []
    counts = dict(re.findall(r"^(\S+) (\d+)$", r.stdout, re.M))
    assert counts.get("pattern:credential") == "1" and counts.get("pattern:github-token") == "1", r.stdout
    assert counts.get("pattern:opaque-run") == "2" and counts.get("canary:bridge-token") == "1", r.stdout
    assert {n: counts.get("pattern:" + n) for n in r1} == {n: "1" for n in r1}, r.stdout
    # SCRUB2: the lower-case bearer header is also the scrub's own authorization-scheme shape now
    assert counts.get("pattern:authorization-scheme") == "1" and counts.get("total") == "11", r.stdout


# SESSION-EXPORT-R1 (task #252; VERIFY-SESSION-EXPORT F-1, F-4 to F-7; AMENDMENT 3), on the shared export above.
def test_escaped_credentials_are_redacted(se, exported):
    # R-1 (F-1): each value behind a JSON-escaped quote is redacted and the rest of the canonical JSON stays whole; the
    # 44-character token is redacted, not a pseudonym (G6); a stop-hook summary's canonical text as well as its outcome
    C = se.CANARIES
    tree, out, L, r, key = exported
    ev = _events(out)
    R = "<redacted>"
    want = {
        "esc-export": {"command": 'export PC_BRIDGE_TOKEN="%s" && bash scripts/pc.sh ls' % R, "description": "x"},
        "esc-body": {"command": "curl -s -d '{\"password\": \"%s\"}' https://api.example.com/login" % R, "description": "x"},
        "esc-write": {"content": '{\n  "api_key": "%s",\n  "region": "eu"\n}\n' % R, "file_path": "/srv/app/service.json"},
        "esc-edit": {"file_path": "/srv/app/app.yaml", "new_string": 'token: "%s"' % R, "old_string": 'token: "x"',
                     "replace_all": False},
        "esc-deep": {"command": 'curl -d "{\\"password\\": \\"%s\\"}" https://api.example.com/login' % R, "description": "x"},
        "esc-basic": {"content": '{"headers": {"Authorization": "Basic %s"}}' % R, "file_path": "/srv/app/h.json"},
        "esc-pass": {"command": 'export DB_PASS="%s" && ./run.sh' % R, "description": "x"},
        "esc-long": {"command": 'export PC_BRIDGE_TOKEN="%s" && bash scripts/pc.sh ls' % R, "description": "x"},
    }
    for name, obj in want.items():
        _expect(C, _one(ev, L, name, "tool_call")["text"], _canon(obj), name)
    _expect(C, json.loads(_one(ev, L, "esc-hook")["text"])["stdout"], '{"token": "%s"}' % R, "esc-hook")
    _expect(C, json.loads(_one(ev, L, "esc-notice")["text"])["data"], {"note": 'secret: "%s"' % R}, "esc-notice")
    stop = _one(ev, L, "esc-stop")
    _expect(C, json.loads(stop["text"])["hookErrors"], ['retry with password="%s"' % R], "esc-stop text")
    _expect(C, stop["outcome"], {"hook_errors": ['retry with password="%s"' % R]}, "esc-stop outcome")


def test_a_call_that_names_the_pseudonym_key_loses_its_result(se, exported):
    # R-2 (F-4): the result becomes DROPPED whatever the spelling of the key's path (the strict pass left an xxd dump's
    # printable column); the call's own input stays, scrubbed
    C = se.CANARIES
    tree, out, L, r, key = exported
    ev = _events(out)
    for name, command in (("key-xxd", "xxd /root/.config/session-export/pseudonym.key; "
                                      "cat /root/.config/session-export/pseudonym.key"),
                          ("key-rel", "cd /root/.config/session-export && xxd pseudonym.key"),
                          ("key-lone", "xxd pseudonym.key && base64 -w 16 pseudonym.key")):
        _expect(C, _one(ev, L, name + "-result", "tool_result")["text"], DROPPED, name)
        _expect(C, _one(ev, L, name, "tool_call")["text"], _canon({"command": command, "description": "x"}), name + " call")


def test_secret_path_spellings_are_seen(se, exported):
    # R-3 (F-7): $HOME/, ~/, a quoted path, a relative path and a glob name a secret file, so the result is strict-passed
    # (its canary alone on a line goes); a Read through ./ or // is dropped
    C = se.CANARIES
    tree, out, L, r, key = exported
    ev = _events(out)
    for name in ("path-home", "path-tilde", "path-rel", "path-quoted", "path-glob"):
        _expect(C, _one(ev, L, name + "-result", "tool_result")["text"], "<redacted>\n", name)
    _expect(C, _one(ev, L, "path-glob-env-result", "tool_result")["text"], "ZQ_ENDPOINT=<redacted>\n", "path-glob-env")
    for name in ("path-dot", "path-dslash"):
        _expect(C, [_one(ev, L, name, "tool_call")["text"], _one(ev, L, name + "-result")["text"]], [DROPPED, DROPPED], name)
    _expect(C, _one(ev, L, "att-spelled")["text"], DROPPED, "att-spelled")                 # an attachment's path
    src, line = L["diff-spelled-result"]
    changes = [e["text"] for e in ev[src] if e["line"] == line and e["kind"] == "file_change"]
    _expect(C, changes, [DROPPED], "diff-spelled")                                          # a Bash file change's path


def test_r3_named_shapes_are_scrubbed_through_the_cli(se, exported):
    # R-3 (F-5, F-6): a lowercase bearer, a -u user:pass flag, a *_PASS assignment, a token alone in a URL's userinfo, a
    # URL password with a raw @ in it
    C = se.CANARIES
    tree, out, L, r, key = exported
    ev = _events(out)
    res = lambda name: _one(ev, L, name + "-result", "tool_result")["text"]          # noqa: E731
    _expect(C, res("bearer-lower"), "authorization: bearer <redacted>\n", "bearer-lower")
    _expect(C, _one(ev, L, "curl-user", "tool_call")["text"],
            _canon({"command": "curl -s -u bob:<redacted> https://api.example.com/v1/me", "description": "x"}), "curl-user")
    _expect(C, res("db-pass"), "DB_HOST=db.internal\nDB_PASS=<redacted>\n", "db-pass")
    _expect(C, res("url-user"), "origin https://<redacted>@github.com/zq/zq.git (fetch)\n", "url-user")
    _expect(C, res("url-at-tail"), "origin https://bob:<redacted>@db.example.com/app (fetch)\n", "url-at-tail")


# The run shapes, typed from the rules (the opaque rule, the strict key run, the token-line class): the oracle below
# builds the committed set from the fixture repo's own text with these, not with the exporter's code.
ORACLE_SHAPES = (re.compile(r"(?:\b|(?a:\b))[A-Za-z0-9_\-]{40,}(?:\b|(?a:\b))"), re.compile(r"[A-Za-z0-9_\-+/=]{20,}"),
                 re.compile(r"[A-Za-z0-9_\-+/=.~:]{12,}"))


def test_committed_runs_stay_as_they_are(se, exported):
    # AMENDMENT 3 (R-4): a run the repo's tracked files hold is neither a pseudonym nor strict-redacted; an uncommitted
    # one is; a committed fake token under a credential name is still redacted (the named rules run first). The manifest
    # names the commit, the run count and the set's digest, each equal to the oracle's
    C = se.CANARIES
    tree, out, L, r, key = exported
    ev = _events(out)
    _expect(C, _one(ev, L, "a3-normal-result", "tool_result")["text"], "%s::%s PASSED\n%s::[opaque:%s] FAILED\n" % (
        COMMITTED_PATH, COMMITTED_NAME, COMMITTED_PATH, _hmac12(key, UNCOMMITTED_NAME)), "a3-normal")
    _expect(C, _one(ev, L, "a3-strict-result", "tool_result")["text"],
            "%s::test_zq_x PASSED\n%s\nZQ_BRANCH=%s\nZQ_RUN=<redacted>\nPC_BRIDGE_TOKEN=<redacted>\n%s\n" % (
                COMMITTED_PATH, COMMITTED_PATH, COMMITTED_BRANCH, COMMITTED_FAKE), "a3-strict")
    head = REPO["commits"][-1]
    oracle = set()
    for f in ("docs/zq-0.md", "docs/zq-1.md"):
        text = _git(REPO["path"], "show", "%s:%s" % (head, f))
        for rx in ORACLE_SHAPES:
            oracle.update(rx.findall(text))
    assert [rx.pattern for rx in ORACLE_SHAPES] == [rx.pattern for rx in se.RUN_SHAPES]
    assert COMMITTED_NAME in oracle and COMMITTED_FAKE in oracle and UNCOMMITTED_NAME not in oracle
    assert _manifest(out)["repo"] == {"path": str(REPO["path"]), "commit": head, "runs": len(oracle),
                                      "runs_sha256": hashlib.sha256("\n".join(sorted(oracle)).encode()).hexdigest()}
    assert "committed runs %d at %s" % (len(oracle), head) in r.stdout


def test_the_gate_reads_the_committed_runs_its_manifest_names(tmp_path, se, exported):
    # the gate CLI rebuilds the set from the repo and commit the manifest names and reads 0; negative control: the same
    # export with the manifest naming the repo's first commit, which holds none of them, counts the committed run it kept
    tree, out, L, r, key = exported
    g = _run("gate", out)
    assert g.returncode == 0 and re.search(r"^total 0$", g.stdout, re.M), _say(g.stdout + g.stderr, se.CANARIES)
    copy = tmp_path / "copy"
    shutil.copytree(out, copy)
    m = _manifest(copy)
    m["repo"]["commit"] = REPO["commits"][0]
    (copy / "manifest.json").write_text(json.dumps(m))
    g = _run("gate", copy)
    counts = dict(re.findall(r"^(\S+) (\d+)$", g.stdout, re.M))
    assert (g.returncode, counts.get("pattern:opaque-run"), counts.get("total")) == (3, "1", "1"), \
        _say(g.stdout + g.stderr, se.CANARIES)


def _one_call_tree(tmp_path, name, result):
    """A projects tree with one transcript: a Bash call and its result."""
    t = Tape(tmp_path / "proj")
    t.call("toolu_fake_m1", "Bash", {"command": "python3 -m pytest -q"})
    t.result("toolu_fake_m1", result, is_error=False)
    t.write(tmp_path / "tree" / "-mv" / (name + ".jsonl"))
    return tmp_path / "tree"


def test_an_offsets_rerun_reads_the_commit_its_manifest_names(tmp_path, se):
    # AF-AP-175: the commit is resolved once and named in the manifest; a rerun with --offsets reads that commit's runs
    # even after the repo's HEAD moves on (byte-identical output); negative control: a fresh export reads the new HEAD
    repo = tmp_path / "repo"
    c1 = make_repo(repo, COMMITTED_TEXT)[0]
    tree = _one_call_tree(tmp_path, "mv", "%s FAILED\n" % UNCOMMITTED_NAME)
    key_path, key = _key(tmp_path)

    def run(out, *extra):
        return _run("export", "--root", tree, "--out", out, "--jobs", 1, "--key", key_path, "--repo", repo, *extra)
    r1 = run(tmp_path / "o1")
    assert r1.returncode == 0, r1.stderr[-2000:]
    (repo / "docs" / "zq-9.md").write_text(UNCOMMITTED_NAME + "\n")               # HEAD moves: it now holds the name
    _git(repo, "add", "docs")
    _git(repo, "commit", "-q", "-m", "moved")
    r2, r3 = run(tmp_path / "o2", "--offsets", tmp_path / "o1" / "manifest.json"), run(tmp_path / "o3")
    assert (r2.returncode, r3.returncode) == (0, 0), r2.stderr[-2000:] + r3.stderr[-2000:]
    assert _shas(tmp_path / "o2") == _shas(tmp_path / "o1")
    commits = [_manifest(tmp_path / o)["repo"]["commit"] for o in ("o1", "o2", "o3")]
    assert commits[:2] == [c1, c1] and commits[2] == _git(repo, "rev-parse", "HEAD") != c1
    text = lambda o: _events(tmp_path / o)["-mv/mv.jsonl"][1]["text"]              # noqa: E731
    assert text("o1") == "[opaque:%s] FAILED\n" % _hmac12(key, UNCOMMITTED_NAME) and text("o3") == UNCOMMITTED_NAME + " FAILED\n"


def test_a_repo_git_cannot_read_refuses_and_a_copy_outside_git_exempts_nothing(tmp_path, se):
    # an explicit --repo or --commit that git cannot read refuses before any output; the default is this script's own
    # repo, and a copy of the script outside any git work tree exports with nothing exempt, and says so
    tree = _one_call_tree(tmp_path, "mv", "%s FAILED\n" % COMMITTED_NAME)
    key_path, key = _key(tmp_path)
    for i, extra in enumerate((["--repo", tree], ["--repo", REPO["path"], "--commit", "0" * 40])):
        out = tmp_path / ("bad%d" % i)
        r = _run("export", "--root", tree, "--out", out, "--jobs", 1, "--key", key_path, *extra)
        assert (r.returncode, "committed runs" in r.stderr, out.exists()) == (2, True, False), r.stderr[-500:]
    copy = tmp_path / "copy" / "scripts"
    copy.mkdir(parents=True)
    for f in ("session_export.py", "transcript_export.py"):
        shutil.copy(ROOT / "scripts" / f, copy / f)
    r = subprocess.run([sys.executable, str(copy / "session_export.py"), "export", "--root", str(tree), "--out",
                        str(tmp_path / "o"), "--jobs", "1", "--key", str(key_path)], capture_output=True, text=True,
                       timeout=600)
    assert r.returncode == 0 and "no run is exempt" in r.stdout, r.stdout[-2000:] + r.stderr[-2000:]
    assert _manifest(tmp_path / "o")["repo"] is None
    assert _events(tmp_path / "o")["-mv/mv.jsonl"][1]["text"] == "[opaque:%s] FAILED\n" % _hmac12(key, COMMITTED_NAME)


# R-3 (F-7) and R-2 in process: the secret paths each spelling names (SECRET_PATH's matches), and ordinary commands that
# name none (a glob needs two literal characters of a secret name; a bare `*` or `dir/*` names nothing).
SPELLED = (
    ("cat $HOME/.config/qwen-builder/api-key", {"qwen-builder/api-key"}),
    ("cat ~/.config/qwen-jev/omniroute.key", {"qwen-jev/omniroute.key"}),
    ("cat /root/.config/qwen-builder/./api-key", {"qwen-builder/api-key"}),
    ("cat /root/.config/qwen-builder//api-key", {"qwen-builder/api-key"}),
    ("cd ~/.config/qwen-builder && cat api-key", {"qwen-builder/api-key"}),
    ("cat '/root/.config/qwen-builder'/api-key", {"qwen-builder/api-key"}),
    ('{"command":"cat \\"/root/.config/qwen-bui\\"lder/api-key\\""}', {"qwen-builder/api-key"}),
    ("cat ~/.config/qwen-*/api-key", {"qwen-builder/api-key"}),
    ("cat ~/.config/qwen-builder/*", {"qwen-builder/api-key"}),
    ("cat '/home/user/agent-factory/.pc-bridge.e'*", {".env"}),
    ("cat /srv/app/prod.e*", {".env"}),
    ("cat /srv/app/*.env", {".env"}),
    ("cat /srv/app/x.en?", {".env"}),
    ("cat /srv/app/prod.e'nv'", {".env"}),                   # a quote inside the name: only the normalized text
    ("ls ~/.hermes/prof*/aflane/config.yaml", {".hermes/profiles/"}),
    ("cd ~/.hermes && cat profiles/aflane/config.yaml", {".hermes/profiles/"}),
    ("xxd pseudonym.key", {"session-export/pseudonym.key"}),
    ("cd /root/.config/session-export && xxd pseudonym.key", {"session-export/pseudonym.key"}),
    ("od -c /root/.config/session-export/pseudonym.k*", {"session-export/pseudonym.key"}),
    ("cat .env && xxd /root/.config/session-export/pseudonym.key", {".env", "session-export/pseudonym.key"}),
)
NOT_SECRET = ("ls *", "rm -rf /tmp/zq/*", "git add *.py", "ls */*", "cat *.md", "grep -rn api-key docs/",
              "systemctl --user status qwen-builder", "echo '**bold** text'", "python3 -c 'print(x[0])'",
              "cd ~/.config && ls", "cat notes/*.environment", "pytest tests/test_*.py -k 'not env'",
              "rm -f /tmp/zq-*", "ls scripts/pc_*", "ls tests/test_*", "ls .e")


@pytest.mark.parametrize("text,named", SPELLED)
def test_named_secrets_sees_each_spelling(se, text, named):
    assert se.named_secrets(text) == named


@pytest.mark.parametrize("text", NOT_SECRET)
def test_named_secrets_leaves_ordinary_commands(se, text):
    assert se.named_secrets(text) == set()


def test_call_modes(se):
    # (the call's mode, its result's mode): a file tool on a secret path drops both; a call naming the pseudonym key drops
    # its result only (R-2); a call naming another secret path strict-passes its result
    cm = se.call_mode
    assert cm("Read", {"file_path": "/root/.config/qwen-builder/./api-key"}, "x") == ("drop", "drop")
    assert cm("Bash", {"command": "xxd pseudonym.key"}, _canon({"command": "xxd pseudonym.key"})) == (None, "drop")
    assert cm("Bash", {"command": "cat .env"}, _canon({"command": "cat .env"})) == (None, "strict")
    assert cm("Bash", {"command": "ls"}, _canon({"command": "ls"})) == (None, None)


def test_repo_runs_refuses_a_blob_git_cannot_give(tmp_path, se):
    # a blob the listing names but the object store lacks (a partial clone, a damaged repo) is a refusal (ValueError, which
    # the CLI turns into rc 2), never a crash and never a set with that file missing
    repo = tmp_path / "repo"
    commit = make_repo(repo, COMMITTED_TEXT)[0]
    blob = _git(repo, "rev-parse", commit + ":docs/zq-0.md")
    (repo / ".git" / "objects" / blob[:2] / blob[2:]).unlink()
    with pytest.raises(ValueError):
        se.repo_runs(str(repo), commit)
