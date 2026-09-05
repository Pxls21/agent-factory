#!/usr/bin/env python3
"""Build a leg's capture.json from a fetched frame directory (deterministic, no network).

Usage: build_capture_record.py <leg-dir> <leg-name> [--facts shutdown-facts.json|cancel-facts.json]
       [--components <initialize capture.json to copy the pinned-component block from>]

The record binds the raw frames to the pinned components, the recursive source-tree manifests taken
immediately before and after the run (manifest-pre/post.summary vs the recorded baseline), the exact
argv and environment NAMES of the buzz-acp process, the config-echo startup line, the mention events
that drove the turn, and every file's sha256. Volatile text is never copied out of the frames.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from collections import Counter
from pathlib import Path

BASELINE = {
    "hermes-agent": "1e11d5dcdf3c38ff26a972c839547c532c91dd2ec942324e75bd310def2b87cb",
    "buzz": "f00e3463f75d6b0716a3f89913de1b06db37af7c8d3433330590022e94a7d987",
    "acp": "5579023c865ec10ecc026ddaa0947f9a2104ad0e2e92ed870989a7d5d66c80d8",
}


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def manifest_summary(p: Path):
    digests, when = {}, None
    for line in p.read_text().splitlines():
        parts = line.split()
        if len(parts) >= 2 and parts[0] in BASELINE:
            digests[parts[0]] = parts[1]
        elif re.fullmatch(r"\d{4}-\d\d-\d\dT\d\d:\d\d:\d\dZ", line.strip()):
            when = line.strip()
    return digests, when


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("leg_dir"); ap.add_argument("leg_name")
    ap.add_argument("--facts", default=None); ap.add_argument("--components", default=None)
    a = ap.parse_args()
    d = Path(a.leg_dir)
    c2a = [json.loads(l) for l in (d / "frames-client-to-agent.jsonl").read_text().splitlines() if l.strip()]
    a2c = [json.loads(l) for l in (d / "frames-agent-to-client.jsonl").read_text().splitlines() if l.strip()]
    pre, pre_t = manifest_summary(d / "manifest-pre.summary")
    post, post_t = manifest_summary(d / "manifest-post.summary")
    argv = (d / "argv.txt").read_text().split("\n")[:-1]
    env_names = (d / "env-names.txt").read_text().split()
    startup = (d / "startup-line.txt").read_text().strip()
    echo = dict(re.findall(r"(idle_timeout|max_turn|session_policy|respond_to|subscribe|dedup)=([^\s]+)", startup))
    m_start = re.match(r"(\d{4}-\d\d-\d\dT[\d:.]+Z)", startup)
    mentions = {}
    for mp in sorted(d.glob("mention-*.json")):
        try:
            mj = json.loads(mp.read_text())
        except Exception:
            continue
        mentions[mp.stem.replace("mention-", "")] = {"accepted": mj.get("accepted"), "event_id": mj.get("event_id"),
                                                     "mention_pubkeys": mj.get("mention_pubkeys")}
    sids = [o["result"]["sessionId"] for o in a2c if "id" in o and isinstance(o.get("result"), dict) and "sessionId" in o["result"]]
    terminals = [(o["id"], o["result"]["stopReason"]) for o in a2c if "id" in o and isinstance(o.get("result"), dict) and "stopReason" in o["result"]]
    kinds = Counter(((o.get("params") or {}).get("update") or {}).get("sessionUpdate") for o in a2c if "method" in o and "id" not in o)
    rec = {
        "capture": f"s0-01-golden-leg:{a.leg_name}",
        "venue": "pc-bridge:fedora (isolated pinned clones under /home/rocco/s0-01-pinned; isolated relay ws://127.0.0.1:3999; model route s0-01-scripted via the managed OmniRoute)",
        "timestamps_utc": {"manifest_pre": pre_t, "buzz_acp_start": m_start.group(1) if m_start else None, "manifest_post": post_t},
        "model_route": (d / "hermes-model.txt").read_text().strip().split(":", 1)[-1].strip() if (d / "hermes-model.txt").exists() else None,
        "hermes_config_sha256_prefix": (d / "hermes-config.sha256").read_text().strip() if (d / "hermes-config.sha256").exists() else None,
        "mentions": mentions,
        "acp_sequence": {
            "client_to_agent": [[o.get("id"), o.get("method")] for o in c2a],
            "agent_to_client_order": [["RESP", o["id"]] if "id" in o else ["NOTIF", ((o.get("params") or {}).get("update") or {}).get("sessionUpdate")] for o in a2c],
            "session_update_kind_counts": dict(kinds), "session_ids": sids, "terminals": terminals,
        },
        "config_echo": {"source": "startup-line.txt", "idle_timeout": echo.get("idle_timeout"), "max_turn": echo.get("max_turn"),
                        "session_policy": echo.get("session_policy"), "respond_to": echo.get("respond_to"),
                        "argv_idle_timeout": argv[argv.index("--idle-timeout") + 1] if "--idle-timeout" in argv else None},
        "manifests": {"method": "manifest.sh: find <tree> -path ./.git -prune -o -type f -print0 | LC_ALL=C sort -z | xargs -0 sha256sum; digest = sha256 of that manifest",
                      "baseline": BASELINE, "pre_capture": pre, "post_capture": post, "identical": pre == post == BASELINE},
        "process": {"argv": argv, "env_names": env_names, "omniroute_credential_in_env": any(n.startswith("OMNIROUTE") for n in env_names),
                    "credential_source": "the owner's Hermes lane profile env (the rotated key), read at launch, never printed",
                    "buzz_acp_exit_code": int((d / "buzz-acp.exit").read_text().strip()) if (d / "buzz-acp.exit").exists() else None},
        "frames": {name.replace("-", "_").replace(".jsonl", "").replace(".txt", ""): {"file": name, "sha256": sha(d / name), "lines": len((d / name).read_text().splitlines())}
                   for name in ("frames-client-to-agent.jsonl", "frames-agent-to-client.jsonl", "argv.txt", "env-names.txt", "startup-line.txt") if (d / name).exists()},
    }
    if a.components:
        rec["components"] = json.loads(Path(a.components).read_text())["components"]
    if a.facts:
        facts = json.loads((d / a.facts).read_text())
        key = "shutdown" if "shutdown" in a.facts else "orphan_check"
        rec[key] = facts
        rec["frames"][a.facts.replace("-", "_").replace(".json", "")] = {"file": a.facts, "sha256": sha(d / a.facts)}
    (d / "capture.json").write_text(json.dumps(rec, indent=2, sort_keys=True) + "\n")
    print(f"{a.leg_name}: identical_manifests={rec['manifests']['identical']} terminals={terminals} kinds={dict(kinds)} exit={rec['process']['buzz_acp_exit_code']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
