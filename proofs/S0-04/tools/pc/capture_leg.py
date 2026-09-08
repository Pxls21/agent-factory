#!/usr/bin/env python3
"""S0-04 leg capture — runs ON THE PC, never in the sandbox. Stdlib only (except `--config`).

Three modes, one per artifact the evidence bundle needs:

  capture   --leg <name> --fixture <fixture.json> --out <leg-dir> [--base-url URL]
            Sends the committed fixture through real OmniRoute (`127.0.0.1:20128` by default)
            and writes `request.json` (what was sent, plus the URL and this argv) and
            `response.json` (status + headers verbatim as an ORDERED LIST of pairs, with every
            credential-named header redacted AT CAPTURE, + body_b64).

  --config  --profile <hermes config.yaml> --provider <name> --out <leg-dir>
            Writes `hermes-provider.json`: ONLY `provider`, `base_url`, `api_mode`, `key_env`
            (the NAME) and `extra_headers`. An inline `api_key` is never read into the artifact.

  --find-record --record-dir <dir> --nonce <s> --out <leg-dir>
            Copies the S0-01 scripted backend's record file carrying this leg's nonce, byte for
            byte, to `upstream-record.json`. Exactly one match is required.

THE KEY IS READ IN PLACE AND NEVER LEAVES MEMORY: the env file is named by `OMNIROUTE_KEY_FILE`
(or the repo's existing `OMNIROUTE_API_KEY_FILE`, or `--key-file`), it carries an
`OMNIROUTE_API_KEY=...` line, and the value goes only into the outgoing Authorization header —
never into argv, never into an artifact, never onto stdout.

Exit codes: 0 ok / 1 named failure / 64 usage.
"""
from __future__ import annotations

import argparse
import base64
import json
import os
import re
import shutil
import stat as _stat
import sys
from pathlib import Path

CREDENTIAL_HEADERS = frozenset({
    "authorization", "proxy-authorization", "x-api-key", "api-key",
    "x-auth-token", "cookie", "set-cookie",
})
KEY_LINE_RE = re.compile(r"^OMNIROUTE_API_KEY=(.*)$")
MAX_RECORD_FILE = 8 * 1024 * 1024
# An exception message must never become the leak the redaction elsewhere prevents.
LEAK_RE = re.compile(r"(?i)bearer\s+\S|\bsk-[A-Za-z0-9_-]{8,}")


class CaptureError(Exception):
    pass


def safe(text: str) -> str:
    return "<message withheld: credential-shaped>" if LEAK_RE.search(text) else text


def read_key(explicit: str | None) -> str:
    """Resolve the key file ONCE, explicitly; `os.environ` is not a config channel beyond this
    single resolution point. The value is returned to the caller and never logged."""
    path = explicit or os.environ.get("OMNIROUTE_KEY_FILE") or os.environ.get("OMNIROUTE_API_KEY_FILE")
    if not path:
        raise CaptureError("no key file: set OMNIROUTE_KEY_FILE (or pass --key-file)")
    file = Path(path)
    if not file.exists():
        raise CaptureError(f"key file not found: {file}")
    if not _stat.S_ISREG(file.lstat().st_mode):
        raise CaptureError(f"key file is not a regular file: {file}")
    if file.stat().st_mode & 0o077:
        raise CaptureError(f"key file {file} is group/other readable; must be 0600 or 0400")
    for line in file.read_text().splitlines():
        match = KEY_LINE_RE.match(line.strip())
        if match and match.group(1).strip().strip('"\''):
            return match.group(1).strip().strip('"\'')
    raise CaptureError(f"no OMNIROUTE_API_KEY= line in {file}")


def redact_headers(pairs) -> list:
    """Header pairs in WIRE ORDER, duplicates preserved (a dict would collapse them —
    AF-AP-41); every credential-named header's value replaced at capture time."""
    return [[name, "<redacted>" if name.lower() in CREDENTIAL_HEADERS else value]
            for name, value in pairs]


def build_request_record(leg: str, fixture_name: str, fixture: dict, url: str, argv: list) -> dict:
    return {
        "leg": leg,
        "fixture": fixture_name,
        "method": fixture["method"],
        "path": fixture["path"],
        "headers": fixture["headers"],
        "body_b64": fixture["body_b64"],
        "url": url,
        "argv": list(argv),
    }


def provider_block(profile: dict, provider: str) -> dict:
    """The redacted provider block. `api_key` (an inline secret in the live profiles) is never
    read into the artifact; `key_env` carries the NAME only, or null when the profile has none —
    which the checker then fails as `key-env-not-a-name`, an honest finding, not a silent pass."""
    providers = profile.get("providers")
    if not isinstance(providers, dict):
        raise CaptureError("profile has no `providers` mapping")
    block = providers.get(provider)
    if not isinstance(block, dict):
        raise CaptureError(f"profile has no provider named {provider!r}")
    key_env = block.get("key_env")
    return {
        "provider": provider,
        "base_url": block.get("base_url"),
        "api_mode": block.get("api_mode"),
        "key_env": key_env if isinstance(key_env, str) else None,
        "extra_headers": block.get("extra_headers") if isinstance(block.get("extra_headers"), dict) else {},
    }


def find_record(record_dir: Path, nonce: str) -> Path:
    if not record_dir.is_dir():
        raise CaptureError(f"record dir not found: {record_dir}")
    matches = []
    for path in sorted(record_dir.glob("*.json")):
        if not _stat.S_ISREG(path.lstat().st_mode):
            continue
        if path.stat().st_size > MAX_RECORD_FILE:
            continue
        if nonce in path.read_text(errors="replace"):
            matches.append(path)
    if not matches:
        raise CaptureError(f"no record in {record_dir} carries the nonce")
    if len(matches) > 1:
        raise CaptureError(
            f"{len(matches)} records carry the nonce ({', '.join(p.name for p in matches)}); "
            f"use a fresh record dir per run")
    return matches[0]


def read_regular(path: Path, what: str) -> str:
    """Operator-supplied paths are read only after an S_ISREG gate: a FIFO left at a fixture or
    profile path would hang the capture, which on the PC looks like a stalled run."""
    if not path.exists():
        raise CaptureError(f"{what} not found: {path}")
    if not _stat.S_ISREG(path.lstat().st_mode):
        raise CaptureError(f"{what} is not a regular file: {path}")
    return path.read_text()


def _write(path: Path, obj) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.is_symlink() or path.exists():
        path.unlink()          # never write THROUGH an existing symlink or hardlink
    path.write_text(json.dumps(obj, indent=2, sort_keys=True) + "\n")


def do_capture(args, argv) -> int:
    import http.client
    from urllib.parse import urlsplit

    fixture_path = Path(args.fixture)
    fixture = json.loads(read_regular(fixture_path, "fixture"))
    body = base64.b64decode(fixture["body_b64"], validate=True)
    split = urlsplit(args.base_url)
    if split.scheme != "http" or not split.hostname:
        raise CaptureError(f"--base-url must be http://host:port, got {args.base_url!r}")
    url = f"{args.base_url.rstrip('/')}{fixture['path']}"
    headers = dict(fixture["headers"])
    headers["Authorization"] = f"Bearer {read_key(args.key_file)}"
    connection = http.client.HTTPConnection(split.hostname, split.port or 80, timeout=args.timeout)
    try:
        connection.request(fixture["method"], fixture["path"], body=body, headers=headers)
        response = connection.getresponse()
        payload = response.read()
        status, pairs = response.status, response.getheaders()
    finally:
        connection.close()
    out = Path(args.out)
    _write(out / "request.json",
           build_request_record(args.leg, fixture_path.name, fixture, url, argv))
    _write(out / "response.json", {
        "leg": args.leg,
        "status": status,
        "headers": redact_headers(pairs),
        "body_b64": base64.b64encode(payload).decode(),
    })
    print(f"capture_leg: {args.leg} status {status} response_bytes {len(payload)} -> {out}")
    return 0


def do_config(args) -> int:
    try:
        import yaml
    except ImportError as exc:
        raise CaptureError(
            "PyYAML is required for --config on this host; install it or export the Hermes "
            "profile to JSON — the provider block is not parsed by hand") from exc
    profile = yaml.safe_load(read_regular(Path(args.profile), "profile"))
    if not isinstance(profile, dict):
        raise CaptureError(f"profile {args.profile} is not a YAML mapping")
    _write(Path(args.out) / "hermes-provider.json", provider_block(profile, args.provider))
    print(f"capture_leg: config provider {args.provider} -> {args.out}")
    return 0


def do_find_record(args) -> int:
    source = find_record(Path(args.record_dir), args.nonce)
    destination = Path(args.out) / "upstream-record.json"
    destination.parent.mkdir(parents=True, exist_ok=True)
    if destination.is_symlink() or destination.exists():
        destination.unlink()
    shutil.copyfile(source, destination)          # verbatim bytes, no re-serialization
    print(f"capture_leg: record {source.name} -> {destination}")
    return 0


def main(argv=None) -> int:
    argv = list(sys.argv if argv is None else argv)
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0], add_help=True)
    parser.add_argument("--leg", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--fixture")
    parser.add_argument("--base-url", default="http://127.0.0.1:20128")
    parser.add_argument("--key-file")
    parser.add_argument("--timeout", type=float, default=60.0)
    parser.add_argument("--config", action="store_true")
    parser.add_argument("--profile")
    parser.add_argument("--provider", default="factory-router")
    parser.add_argument("--find-record", action="store_true")
    parser.add_argument("--record-dir")
    parser.add_argument("--nonce")
    args = parser.parse_args(argv[1:])
    try:
        if args.config and args.find_record:
            print("usage: --config and --find-record are exclusive", file=sys.stderr)
            return 64
        if args.config:
            if not args.profile:
                print("usage: --config needs --profile", file=sys.stderr)
                return 64
            return do_config(args)
        if args.find_record:
            if not args.record_dir or not args.nonce:
                print("usage: --find-record needs --record-dir and --nonce", file=sys.stderr)
                return 64
            return do_find_record(args)
        if not args.fixture:
            print("usage: capture needs --fixture", file=sys.stderr)
            return 64
        return do_capture(args, argv)
    except CaptureError as error:
        print(f"capture_leg: {safe(str(error))}", file=sys.stderr)
        return 1
    except Exception as exc:                                   # noqa: BLE001 - fail closed
        print(f"capture_leg: {safe(f'{type(exc).__name__}: {exc}')}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
