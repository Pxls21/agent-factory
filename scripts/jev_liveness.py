#!/usr/bin/env python3
"""The Jev liveness probe (task #407, D-123 item 7): is the Jev nervous system alive, and where does it fail?

It only reads; it never sends a Jev request and never prints a key or session text:
- each Jev endpoint's /health (the relay :47430, the local Laya server :47411, the Qwen adapter :47420), one second
  each, in parallel, with no proxy;
- the pruner plugins in Claude Code's user settings: which one is enabled, its size floor, its base URL;
- the pruner's decision records (vendor/jev-pruner/PROVENANCE.md local change 3): the heartbeat `last.json` and the
  day's per-decision files, from an absolute `decisionsDir` only (the hook resolves a relative one against Claude Code's
  launch directory);
- when each pruner was installed or updated (installed_plugins.json) against when the running Claude Code started: an
  update reaches the running hook only at a restart;
- the relay's data log for the day: its row count and newest time;
- the newest finished Bash call in the newest session transcript, which tells a quiet hook from a dead one.

`--line` prints one line (orient's layer 0); the default prints the report. Exit 0, or 64 on a usage error.
"""
from __future__ import annotations

import argparse
import concurrent.futures
import datetime as dt
import glob
import hashlib
import json
import os
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ENDPOINTS = {"relay": "http://127.0.0.1:47430", "laya": "http://127.0.0.1:47411", "qwen": "http://127.0.0.1:47420"}
OURS, UPSTREAM = "fast-jev-output-floor@agent-factory-vendor", "fast-jev-output@fast-jev-output"
UPSTREAM_FLOOR = 10_000  # jev-pruner src/output.ts MIN_OUTPUT_TOKENS at 47d017c
MISSED_AFTER_S = 60  # a finished Bash call this much newer than the heartbeat was not seen by the hook
TAIL_BYTES = 4_000_000


def health(url: str) -> dict:
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
    try:
        with opener.open(url.rstrip("/") + "/health", timeout=1.0) as response:
            body = json.loads(response.read(65536).decode("utf-8"))
            return {"up": True, "body": body if isinstance(body, dict) else {}}
    except Exception as error:  # any failure is "down"; the reason is printed, never raised
        reason = getattr(error, "reason", None) or error
        return {"up": False, "why": str(reason)[:80]}


def parse_at(text) -> dt.datetime | None:
    try:
        return dt.datetime.fromisoformat(str(text).replace("Z", "+00:00"))
    except ValueError:
        return None


def claude_started() -> dt.datetime | None:
    """When the Claude Code process above this one started: the plugin code it runs was loaded then."""
    try:
        boot = next(int(line.split()[1]) for line in Path("/proc/stat").read_text().splitlines() if line.startswith("btime "))
        pid = os.getppid()
        while pid > 1:
            fields = Path(f"/proc/{pid}/stat").read_text().rsplit(")", 1)[1].split()
            argv = Path(f"/proc/{pid}/cmdline").read_bytes().split(b"\0")[:2]
            if any(arg == b"claude" or arg.endswith(b"/claude") for arg in argv):
                return dt.datetime.fromtimestamp(boot + int(fields[19]) / os.sysconf("SC_CLK_TCK"), dt.timezone.utc)
            pid = int(fields[1])
    except (OSError, ValueError, IndexError, StopIteration):
        pass
    return None


def installed_at(installed_path: Path) -> dict:
    """Each plugin's newest install or update time, from Claude Code's installed_plugins.json."""
    try:
        plugins = json.loads(installed_path.read_text(encoding="utf-8")).get("plugins") or {}
    except (OSError, ValueError, AttributeError):
        return {}
    out = {}
    for plugin, rows in plugins.items():
        times = [parse_at(row.get("lastUpdated") or row.get("installedAt")) for row in rows if isinstance(row, dict)]
        times = [t for t in times if t]
        if times:
            out[plugin] = max(times)
    return out


def pruners(settings_path: Path) -> list[dict]:
    try:
        settings = json.loads(settings_path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return []
    enabled = settings.get("enabledPlugins") or {}
    configs = settings.get("pluginConfigs") or {}
    out = []
    for plugin in (OURS, UPSTREAM):
        if plugin not in enabled:
            continue
        options = (configs.get(plugin) or {}).get("options") or {}

        def number(key, default=UPSTREAM_FLOOR):
            value = options.get(key, default)
            return value if isinstance(value, (int, float)) and value == value and abs(value) != float("inf") else default
        floor = number("minTokensFloor") if plugin == OURS else UPSTREAM_FLOOR
        floor = floor if floor >= 0 else UPSTREAM_FLOOR
        out.append({"plugin": plugin, "enabled": enabled[plugin] is True, "floor": max(floor, number("minTokens")),
                    "base_url": options.get("baseUrl") or "https://api.typesafe.ai/v1/systemone",
                    "decisions_dir": options.get("decisionsDir") if plugin == OURS else None})
    return out


def decisions(directory: Path, day: str) -> dict:
    out = {"last": None, "today": {}}
    try:
        out["last"] = json.loads((directory / "last.json").read_text(encoding="utf-8"))
    except (OSError, ValueError):
        pass
    for path in sorted((directory / day).glob("*.json")):
        try:
            decision = json.loads(path.read_text(encoding="utf-8")).get("decision", "?")
        except (OSError, ValueError, AttributeError):
            decision = "unreadable"
        out["today"][decision] = out["today"].get(decision, 0) + 1
    return out


def relay_log(path: Path) -> dict:
    try:
        lines = path.read_bytes().splitlines()
    except OSError:
        return {"rows": 0, "newest": None}
    newest = None
    for line in reversed(lines):
        try:
            newest = json.loads(line).get("ts")
            break
        except (ValueError, AttributeError):
            continue
    return {"rows": len(lines), "newest": newest}


def newest_bash_finish(transcript: Path | None) -> dt.datetime | None:
    """The time the newest finished Bash call's result was recorded, from the transcript's tail."""
    if transcript is None:
        return None
    try:
        with transcript.open("rb") as handle:
            start = max(0, transcript.stat().st_size - TAIL_BYTES)
            handle.seek(start)
            tail = handle.read().splitlines()[1 if start else 0:]  # past a seek the first line is a fragment
    except OSError:
        return None
    bash_ids, newest = set(), None
    for raw in tail:
        if b'"tool_use"' not in raw and b'"tool_result"' not in raw:
            continue
        try:
            record = json.loads(raw)
        except ValueError:
            continue
        content = (record.get("message") or {}).get("content")
        for part in content if isinstance(content, list) else []:
            if not isinstance(part, dict):
                continue
            if part.get("type") == "tool_use" and part.get("name") == "Bash":
                bash_ids.add(part.get("id"))
            elif part.get("type") == "tool_result" and part.get("tool_use_id") in bash_ids:
                newest = parse_at(record.get("timestamp")) or newest
    return newest


def age(now: dt.datetime, then: dt.datetime | None) -> str:
    if then is None:
        return "never"
    seconds = int((now - then).total_seconds())
    return f"{seconds}s ago" if seconds < 120 else f"{seconds // 60}m ago" if seconds < 7200 else f"{seconds // 3600}h ago"


def probe(args) -> tuple[list[str], list[str]]:
    now = parse_at(args.now) if args.now else dt.datetime.now(dt.timezone.utc)
    day = now.strftime("%Y-%m-%d")
    endpoints = dict(ENDPOINTS, **args.endpoint)
    with concurrent.futures.ThreadPoolExecutor(max_workers=len(endpoints)) as pool:
        states = dict(zip(endpoints, pool.map(health, endpoints.values())))
    lines, warns = [], []
    for name, url in endpoints.items():
        state, port = states[name], url.rsplit(":", 1)[-1]
        if not state["up"]:
            lines.append(f"{name} :{port} down ({state['why']})")
            continue
        body, text = state["body"], f"{name} :{port} ok"
        if name == "relay":
            counts = body.get("counts") or {}
            log = relay_log(args.root / ".jev" / "relay" / f"{day}.jsonl")
            text += (f" (pid {body.get('pid')}, to {body.get('upstream_host')}; since start {counts.get('relayed', 0)} "
                     f"relayed, {counts.get('refused', 0)} refused, {counts.get('upstream_error', 0)} upstream errors; "
                     f"log today {log['rows']} rows, newest {log['newest'] or 'none'})")
            if counts.get("upstream_error"):
                warns.append(f"the relay counts {counts['upstream_error']} upstream errors since its start")
            # Identity, not only a 200 (AF-AP-33): the relay reports the sha256 of its code and of its scrubber.
            for key, path in (("relay_sha256", "scripts/jev_relay.py"), ("scrub_sha256", "scripts/transcript_export.py")):
                try:
                    here = hashlib.sha256((ROOT / path).read_bytes()).hexdigest()
                except OSError:
                    here = None
                if body.get(key) != here:
                    warns.append(f"the relay on :{port} reports {key} {str(body.get(key))[:12]}, and this tree's {path} "
                                 f"is {str(here)[:12]}: a stale or foreign relay (restart it: scripts/jev_relay_up.sh)")
        lines.append(text)
    found = pruners(args.settings)
    on = [p for p in found if p["enabled"]]
    if not on:
        lines.append("pruner: none enabled")
        warns.append("no pruner plugin is enabled: no Bash output is trimmed")
    if len(on) > 1:
        warns.append("both pruner plugins are enabled: each wraps every Bash call (enable one)")
    finish = newest_bash_finish(args.transcript)
    started = parse_at(args.claude_started) if args.claude_started else claude_started()
    updated = installed_at(args.installed)
    for p in on:
        name = "our copy" if p["plugin"] == OURS else "upstream"
        text = f"pruner {name} ({p['plugin']}) on, floor {p['floor']} tokens, to {p['base_url']}"
        # An update reaches the running hook only at a restart; an option change reloads the code already loaded.
        if started and updated.get(p["plugin"]) and updated[p["plugin"]] > started:
            warns.append(f"the {name} pruner was installed or updated at {updated[p['plugin']].isoformat(timespec='seconds')}, "
                         f"after this Claude Code started at {started.isoformat(timespec='seconds')}: the running hook is "
                         "the older code until a restart (a session resume restarts it; /reload-plugins does not run "
                         "over a remote connection)")
        if p["floor"] >= UPSTREAM_FLOOR:
            warns.append(f"the {name} pruner's floor is {p['floor']} tokens: no inline Bash output reached 10,000 in the "
                         "week measured (docs/research/findings/jev-trim/PRUNER-FLOOR-2026-10-01.md)")
        target = next((n for n, u in endpoints.items() if p["base_url"].startswith(u)), None)
        if target and not states[target]["up"]:
            warns.append(f"the {name} pruner sends to {target}, which is down: outputs past the floor pass untrimmed")
        if p["decisions_dir"] and not Path(p["decisions_dir"]).is_absolute():
            warns.append(f"the {name} pruner's decisionsDir is relative ({p['decisions_dir']}): the hook resolves it "
                         "against Claude Code's launch directory, not the repo, so its records are not read here (set "
                         "an absolute path with claude plugin configure)")
        elif p["decisions_dir"]:
            record = decisions(Path(p["decisions_dir"]), day)
            last = record["last"] or {}
            beat = parse_at(last.get("at"))
            today = ", ".join(f"{k} {v}" for k, v in sorted(record["today"].items())) or "none"
            text += (f"; heartbeat {age(now, beat)} ({last.get('decision', 'no record')}); "
                     f"today past the floor: {sum(record['today'].values())} ({today})")
            if finish and (beat is None or (finish - beat).total_seconds() > MISSED_AFTER_S):
                since = f"has not run since {last['at']}" if beat else "has written no record"
                warns.append(f"the pruner hook {since}, and a Bash call finished at "
                             f"{finish.isoformat(timespec='seconds')}: the hook is not loaded (restart Claude Code or "
                             "/reload-plugins)")
        lines.append(text)
    return lines, warns


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--line", action="store_true", help="one line, for orient's layer 0")
    parser.add_argument("--settings", type=Path, default=Path.home() / ".claude" / "settings.json")
    parser.add_argument("--installed", type=Path, default=Path.home() / ".claude" / "plugins" / "installed_plugins.json")
    parser.add_argument("--claude-started", help="when Claude Code started, ISO 8601 (tests; default: read from /proc)")
    parser.add_argument("--root", type=Path, default=ROOT, help="the project root that holds the relay's .jev/relay log")
    parser.add_argument("--transcript", type=Path, help="the session transcript (default: the newest one)")
    parser.add_argument("--endpoint", action="append", default=[], metavar="NAME=URL", help="add or replace an endpoint")
    parser.add_argument("--now", help="the clock, ISO 8601 (tests)")
    args = parser.parse_args(argv)
    pairs = [item.split("=", 1) for item in args.endpoint]
    if any(len(pair) != 2 or not pair[0] or not pair[1].startswith("http://") for pair in pairs):
        print("jev_liveness: --endpoint takes NAME=http://HOST:PORT", file=sys.stderr)
        return 64
    args.endpoint = dict(pairs)
    if args.transcript is None:
        newest = max(glob.glob(str(Path.home() / ".claude" / "projects" / "*" / "*.jsonl")), key=os.path.getmtime,
                     default=None)
        args.transcript = Path(newest) if newest else None
    lines, warns = probe(args)
    if args.line:
        print("jev: " + " · ".join(lines + [f"WARN {w}" for w in warns]))
    else:
        print("\n".join(["jev pulse"] + [f"  {line}" for line in lines] + [f"  WARN {w}" for w in warns]))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
