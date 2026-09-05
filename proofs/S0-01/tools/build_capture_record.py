#!/usr/bin/env python3
"""Build capture.json from v2 raw files for human reading (the checker never trusts it).

Usage: build_capture_record.py <leg-dir> <leg-name>

Reads timeline.jsonl, runtime-identity.json, env.json, startup-line.txt, hermes-model.txt,
mentions/*.event.json, upstream-records/*.json, manifest-pre/post.txt.gz, buzz-acp.exit.
"""
from __future__ import annotations

import gzip
import hashlib
import json
import re
import sys
from collections import Counter
from pathlib import Path


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _sha256_file(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def _parse_manifest_gz(gz_path: Path) -> dict:
    body = gzip.decompress(gz_path.read_bytes())
    text = body.decode("utf-8")
    current, sections = None, {}
    for line in text.splitlines():
        if line.startswith("## "):
            current = line[3:].strip()
            sections[current] = ""
        elif current is not None:
            sections[current] += line + "\n"
    return {k: _sha256(v.encode("utf-8")) for k, v in sections.items()}


def main() -> int:
    check_mode = "--check" in sys.argv
    args = [a for a in sys.argv[1:] if a != "--check"]
    if len(args) < 2:
        print("usage: build_capture_record.py [--check] <leg-dir> <leg-name>", file=sys.stderr)
        return 2
    d = Path(args[0])
    leg = args[1]

    rec = {"capture": f"s0-01-golden-leg:{leg}", "version": 2}

    # timeline summary
    tl_path = d / "timeline.jsonl"
    if tl_path.exists():
        entries = [json.loads(l) for l in tl_path.read_text().splitlines() if l.strip()]
        c2a = [e["frame"] for e in entries if e["dir"] == "c2a"]
        a2c = [e["frame"] for e in entries if e["dir"] == "a2c"]
        sids = []
        resps = {}
        for e in a2c:
            if "id" in e and "method" not in e:
                resps[e["id"]] = e
                r = e.get("result") or {}
                if "sessionId" in r:
                    sids.append(r["sessionId"])
        terminals = [(e["id"], (e.get("result") or {}).get("stopReason"))
                     for e in a2c if "id" in e and "method" not in e
                     and (e.get("result") or {}).get("stopReason")]
        kinds = Counter(((e.get("params") or {}).get("update") or {}).get("sessionUpdate")
                        for e in a2c if "method" in e and "id" not in e)
        rec["timeline"] = {
            "entries": len(entries), "c2a": len(c2a), "a2c": len(a2c),
            "sessions": sids, "terminals": terminals, "update_kinds": dict(kinds),
        }

    # runtime identity
    rid_path = d / "runtime-identity.json"
    if rid_path.exists():
        rec["runtime_identity"] = json.loads(rid_path.read_text())

    # env (just the names, not values)
    env_path = d / "env.json"
    if env_path.exists():
        env = json.loads(env_path.read_text())
        rec["env_names"] = sorted(env.keys())

    # startup + config echo
    startup_path = d / "startup-line.txt"
    if startup_path.exists():
        startup = startup_path.read_text().strip()
        kvs = dict(re.findall(r"(idle_timeout|max_turn|session_policy)=(\S+)", startup))
        rec["config_echo"] = kvs

    # model
    model_path = d / "hermes-model.txt"
    if model_path.exists():
        rec["model"] = model_path.read_text().strip()

    # mentions
    mentions_dir = d / "mentions"
    if mentions_dir.is_dir():
        mentions = {}
        for ep in sorted(mentions_dir.glob("*.event.json")):
            tag = ep.name.replace(".event.json", "")
            event = json.loads(ep.read_text())
            rp = mentions_dir / f"{tag}.receipt.json"
            receipt = json.loads(rp.read_text()) if rp.exists() else {}
            mentions[tag] = {
                "event_id": event.get("id"), "pubkey": event.get("pubkey"),
                "content": event.get("content"), "accepted": receipt.get("accepted"),
            }
        rec["mentions"] = mentions

    # upstream records
    urec_dir = d / "upstream-records"
    if urec_dir.is_dir():
        rec["upstream_records"] = len(list(urec_dir.glob("*.json")))

    # manifests
    for gz_name in ("manifest-pre.txt.gz", "manifest-post.txt.gz"):
        gz_path = d / gz_name
        if gz_path.exists():
            rec.setdefault("manifests", {})[gz_name] = _parse_manifest_gz(gz_path)

    # exit code
    exit_path = d / "buzz-acp.exit"
    if exit_path.exists():
        rec["buzz_acp_exit"] = exit_path.read_text().strip()

    # file digests
    files = {}
    for name in ("timeline.jsonl", "runtime-identity.json", "env.json",
                 "startup-line.txt", "hermes-model.txt", "buzzacp.log",
                 "process-scan-after.txt", "buzz-acp.pid", "buzz-acp.exit"):
        p = d / name
        if p.exists():
            files[name] = {"sha256": _sha256_file(p), "size": p.stat().st_size}
    rec["files"] = files

    new_text = json.dumps(rec, indent=2, sort_keys=True) + "\n"
    out = d / "capture.json"
    if check_mode:
        if not out.exists():
            print(f"{leg}: capture.json does not exist (--check)", file=sys.stderr)
            return 1
        existing = out.read_text()
        if existing != new_text:
            print(f"{leg}: capture.json differs from re-derived content (--check)",
                  file=sys.stderr)
            return 1
        print(f"{leg}: capture.json matches (--check)")
        return 0
    out.write_text(new_text)
    print(f"{leg}: {len(files)} raw files, {rec.get('timeline', {}).get('entries', 0)} timeline entries")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
