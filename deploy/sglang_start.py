"""sglang_start.py - starts the SGLang model server inside the qwen container (task #454, the switch; D-129, D-131).

The key stays off every command line, and out of the log. The script reads the API key from the mounted key file and
the context length from MAX_LEN, writes both to a YAML config only this user can read, and runs SGLang with
--config, so the key is in no process's argv (ps, /server_info's launch_command). SGLang logs its resolved arguments,
the key among them, at startup (engine.py:1109 at 94602c9c, unmasked), so every line the server writes passes through
here and the key is replaced before the line reaches the journal. MAX_LEN is the unit's one statement of the context:
harness-ports/bin/lane-profile.sh reads the same Environment= line for every lane profile.
TERM and INT go to the server; its exit code is this script's (128+N when a signal ended it).

Usage (the unit's Exec= line): python3 sglang_start.py --model-path ... [every other SGLang flag]
Environment: MAX_LEN (required, a positive integer); SGL_KEY_FILE (default /app/api_key.txt).
"""
import json
import os
import re
import signal
import subprocess
import sys
import tempfile

KEY_FILE_DEFAULT = "/app/api_key.txt"
OWN_FLAGS = ("--api-key", "--context-length", "--config")  # set here, never on the command line
# the key's value in a printed mapping or argument form, as a second guard beside the exact value
KEY_FORM = re.compile(rb"((?:admin_)?api[_-]key['\"]?\s*[:=]\s*['\"])[^'\"]+")


def die(msg):
    print(f"sglang_start: {msg}", file=sys.stderr, flush=True)
    sys.exit(64)


def read_key(path):
    try:
        with open(path, encoding="utf-8") as fh:
            key = fh.read().strip()
    except (OSError, UnicodeError) as e:
        die(f"the key file {path} is unreadable ({type(e).__name__})")
    if not key:
        die(f"the key file {path} is empty")
    if any(c.isspace() or not c.isprintable() for c in key):
        die(f"the key file {path} holds more than one printable word")
    return key


def main(argv):
    for a in argv:
        if a.split("=", 1)[0] in OWN_FLAGS:
            die(f"{a.split('=', 1)[0]} is set by this script, never on the command line")
    max_len = os.environ.get("MAX_LEN", "")
    if not re.fullmatch(r"[0-9]+", max_len) or int(max_len) <= 0:
        die("MAX_LEN must be a positive integer")
    key = read_key(os.environ.get("SGL_KEY_FILE", KEY_FILE_DEFAULT))
    cfg_dir = tempfile.mkdtemp(prefix="sglang-start-")  # 0700
    cfg = os.path.join(cfg_dir, "config.yaml")
    fd = os.open(cfg, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(fd, "w", encoding="utf-8") as fh:
        # a JSON string is a YAML double-quoted scalar
        fh.write(f"api-key: {json.dumps(key)}\ncontext-length: {int(max_len)}\n")

    child, pending = None, []

    def forward(signum, _frame):
        if child is None:
            pending.append(signum)
        else:
            child.send_signal(signum)

    signal.signal(signal.SIGTERM, forward)
    signal.signal(signal.SIGINT, forward)
    env = dict(os.environ, PYTHONUNBUFFERED="1")
    child = subprocess.Popen([sys.executable, "-m", "sglang.launch_server", "--config", cfg] + argv,
                             stdout=subprocess.PIPE, stderr=subprocess.STDOUT, env=env)
    for s in pending:
        child.send_signal(s)
    secret = key.encode()
    out = sys.stdout.buffer
    for raw in iter(child.stdout.readline, b""):
        out.write(KEY_FORM.sub(rb"\1<redacted>", raw.replace(secret, b"<redacted>")))
        out.flush()
    rc = child.wait()
    return rc if rc >= 0 else 128 - rc


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
