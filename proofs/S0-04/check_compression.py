#!/usr/bin/env python3
"""S0-04 compression contract — the checker over captured legs.

Grades an evidence bundle produced on the PC by `tools/pc/run_s0_04_legs.sh` against the three
seed assertions (`seeds/seed-stage0-v1.yaml:406-422`):

  A1  the Hermes-side request carries `x-omniroute-compression: off`
      -> the `config` leg's provider block (`extra_headers`) and every request leg's
         `request.json`, which must equal the committed fixture byte for byte.
  A2  the response carries `X-OmniRoute-Compression` reporting off
      -> `response.json` headers; the name is matched case-insensitively, the value EXACTLY
         (AF-AP-38: presence is not a value).
  A3  the stub upstream's received request compares equal to the sent fixture
      -> `upstream-record.json`, the S0-01 scripted backend's own record file, against the
         fixture's committed body bytes.

HOW A3 IS ACTUALLY MEASURED, and what it cannot see
---------------------------------------------------
The sanctioned instrument (`proofs/S0-01/tools/scripted_backend.py`, `State.record` at
`:479-538`) does NOT persist the raw request bytes: `raw_body` is passed to `record()` for the
credential screen only, and the record file it writes carries `body` as the PARSED JSON object,
serialized with `sort_keys=True` (recursively — so the wire key ORDER is gone too). Verified by
running the real backend and reading its record; the record's keys are exactly
`authorization_fingerprint, body, headers, method, path, received_at, remote_addr, seq,
t_mono_ns`. A literal wire-byte compare is therefore impossible from this evidence.

What this checker compares instead, and why it is still exact:
  * the wire BYTE LENGTH — the record's `content-length` header (recorded verbatim) must equal
    the fixture body's byte length; and
  * the JSON VALUE — the record's parsed body, re-serialized in the same canonical form the
    fixture is committed in (`sort_keys=True, separators=(",",":"), ensure_ascii=True`), must
    equal the fixture's committed bytes; the fixture is asserted to BE canonical first, so the
    comparison cannot go vacuous.
Together these reject compression, re-encoding, truncation, insertion, and any change of a key
or value. The one residual, stated plainly: a re-serialization that PERMUTES keys without
changing the total byte length is invisible in this record shape. Closing it needs the raw bytes
in the record, which is a change to the S0-01 instrument and out of this proof's scope.

Exit codes: 0 PASS / 1 `failure_reason: <leg>: <reason>` / 2 `deferred: <reason>` / 64 usage.
Deferral means NOTHING was captured. Once a leg directory exists every required file in every
required leg is REQUIRED — absence is a Failure naming the leg and the file (AF-AP-40).
Stdlib only.

Usage: check_compression.py [--fixtures-dir <dir>] <evidence-root>
"""
from __future__ import annotations

import base64
import json
import re
import stat as _stat
import sys
from pathlib import Path
from urllib.parse import urlsplit

# The leg set is CLOSED and declared, never discovered: a discovered set lets a deleted leg
# shrink the proof silently (AF-AP-40), and an extra directory smuggle evidence in (AF-AP-23).
REQUIRED_LEGS = ("off", "off-large", "config")
CONFIG_LEG = "config"
LEG_FIXTURE = {"off": "request-baseline.json", "off-large": "request-large.json"}

COMPRESSION_HEADER = "x-omniroute-compression"   # matched case-insensitively
COMPRESSION_VALUE = "off"                        # docs/03_INTEGRATION_CONTRACTS.md:31-51
OMNIROUTE_PORT = 20128                           # PC-BRIDGE.md:153-163
OMNIROUTE_BASE_SUFFIX = f":{OMNIROUTE_PORT}/v1"
KEY_ENV_RE = re.compile(r"^[A-Z][A-Z0-9_]{2,63}$")
FINGERPRINT_RE = re.compile(r"^[0-9a-f]{64}$")
MAX_EVIDENCE_FILE = 8 * 1024 * 1024

# Credential screen over every bundle file (the S0-01 `_STDERR_LEAK_RE` idea, widened).
# The bare 64-hex rule would fire on the instrument's own `authorization_fingerprint`, which is
# a sha256 of the bearer and is the REDACTION, not the secret; that one value is validated for
# digest shape and then masked out of the text before the scan, so a SECOND 64-hex run anywhere
# still fails and a bearer smuggled into that field fails the shape check.
LEAK_PATTERNS = (
    ("bearer", re.compile(r"(?i)bearer\s+\S")),
    ("sk-key", re.compile(r"\bsk-[A-Za-z0-9_-]{8,}")),
    ("key-assignment", re.compile(
        r"(?i)\b(?:api[_-]?key|apikey|secret|password|passwd|token)\b"
        r"\s*[\"']?\s*[:=]\s*[\"']?[A-Za-z0-9_\-.+/]{8,}")),
    ("hex64", re.compile(r"(?<![0-9a-fA-F])[0-9a-fA-F]{64}(?![0-9a-fA-F])")),
)


class Deferred(Exception):
    pass


class Failure(Exception):
    pass


def _leak_hit(text: str):
    for name, rx in LEAK_PATTERNS:
        if rx.search(text):
            return name
    return None


def _redact(text: str) -> str:
    """Reason lines interpolate bundle values; a hostile bundle must not turn the checker into
    the leak. Any credential-shaped reason line is replaced, never printed."""
    return text if _leak_hit(text) is None else "<reason withheld: credential-shaped>"


def _short(value, limit: int = 60) -> str:
    s = value if isinstance(value, str) else repr(value)
    return s if len(s) <= limit else s[:limit] + "...(truncated)"


def _canon(obj) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode()


def _loads(data: bytes, leg: str, name: str):
    def _reject(_c):
        raise Failure(f"{leg}: malformed-evidence: NaN or Infinity in {name}")
    try:
        return json.loads(data, parse_constant=_reject)
    except (ValueError, UnicodeDecodeError) as exc:
        raise Failure(f"{leg}: malformed-evidence: {name} is not JSON ({type(exc).__name__})") from exc


def _require_file(path: Path, leg: str, name: str) -> Path:
    """Reject a non-regular file (FIFO, socket, device, directory, symlink) with a named reason
    BEFORE any read: existence alone is not enough, and a FIFO read would hang the checker."""
    if not path.exists():
        raise Failure(f"{leg}: {name} absent")
    if not _stat.S_ISREG(path.lstat().st_mode):
        raise Failure(f"{leg}: {name} is not a regular file")
    return path


def _read_json(path: Path, leg: str, name: str):
    _require_file(path, leg, name)
    if path.stat().st_size > MAX_EVIDENCE_FILE:
        raise Failure(f"{leg}: {name} exceeds {MAX_EVIDENCE_FILE} bytes")
    return _loads(path.read_bytes(), leg, name)


def _first_diff(want: bytes, got: bytes) -> int:
    n = min(len(want), len(got))
    for i in range(n):
        if want[i] != got[i]:
            return i
    return n


def _screen_tree(root: Path) -> None:
    """Every regular file under the bundle is screened for a credential-shaped value; every
    non-regular entry is a Failure (fail closed, and no read can hang)."""
    stack = [root]
    while stack:
        current = stack.pop()
        for entry in sorted(current.iterdir()):
            rel = entry.relative_to(root)
            mode = entry.lstat().st_mode
            if _stat.S_ISDIR(mode):
                stack.append(entry)
                continue
            if not _stat.S_ISREG(mode):
                raise Failure(f"evidence-not-regular-file: {rel}")
            if entry.stat().st_size > MAX_EVIDENCE_FILE:
                raise Failure(f"evidence-file-too-large: {rel}")
            text = entry.read_bytes().decode("utf-8", errors="replace")
            for fingerprint in _fingerprints(text, rel):
                text = text.replace(fingerprint, "<authorization_fingerprint>")
            hit = _leak_hit(text)
            if hit is not None:
                raise Failure(f"credential-in-evidence: {rel} matches {hit}")


def _fingerprints(text: str, rel: Path):
    """The sha256 values the instrument records in place of the bearer. Any `authorization_
    fingerprint` that is not null and not a lowercase sha256 is itself the leak."""
    try:
        obj = json.loads(text)
    except ValueError:
        return []
    out = []
    stack = [obj]
    while stack:
        node = stack.pop()
        if isinstance(node, dict):
            for key, value in node.items():
                if key == "authorization_fingerprint":
                    if value is None:
                        continue
                    if not isinstance(value, str) or not FINGERPRINT_RE.match(value):
                        raise Failure(
                            f"credential-in-evidence: {rel} authorization_fingerprint "
                            f"is not a sha256 digest")
                    out.append(value)
                else:
                    stack.append(value)
        elif isinstance(node, list):
            stack.extend(node)
    return out


def _header_values(pairs, leg: str, name: str):
    """Response headers are captured as an ORDERED LIST of [name, value] pairs, never a dict:
    a dict collapses a duplicated header to the last value, which is AF-AP-41's mechanism."""
    if not isinstance(pairs, list):
        raise Failure(f"{leg}: {name} headers are not a list of [name, value] pairs")
    out = []
    for pair in pairs:
        if (not isinstance(pair, list) or len(pair) != 2
                or not all(isinstance(x, str) for x in pair)):
            raise Failure(f"{leg}: {name} header entry is not a [name, value] string pair")
        out.append((pair[0], pair[1]))
    return out


def check_request_leg(leg: str, leg_dir: Path, fixtures_dir: Path, observations: list) -> None:
    fixture_name = LEG_FIXTURE[leg]
    fixture = _read_json(fixtures_dir / fixture_name, leg, f"fixture {fixture_name}")
    try:
        body = base64.b64decode(fixture["body_b64"], validate=True)
    except (KeyError, ValueError, TypeError) as exc:
        raise Failure(f"{leg}: fixture-unreadable: body_b64 ({type(exc).__name__})") from exc
    nonce = fixture.get("nonce")
    if not isinstance(nonce, str) or not nonce:
        raise Failure(f"{leg}: fixture-unreadable: nonce")
    # De-vacuous the compare at check time: a fixture whose committed bytes are NOT the canonical
    # form would make every canonical comparison below trivially unable to detect a difference.
    if _canon(_loads(body, leg, "fixture body")) != body:
        raise Failure(f"{leg}: fixture-not-canonical: {fixture_name}")
    if nonce.encode() not in body:
        raise Failure(f"{leg}: fixture-nonce-not-in-body: {fixture_name}")

    # A1 — what was sent must BE the committed fixture, byte for byte.
    request = _read_json(leg_dir / "request.json", leg, "request.json")
    for field in ("method", "path", "headers", "body_b64"):
        if request.get(field) != fixture.get(field):
            raise Failure(f"{leg}: request-fixture-mismatch: {field}")
    # The capture must have gone THROUGH OmniRoute: a leg pointed straight at the scripted
    # backend would preserve the request perfectly and prove nothing about the gateway. A tail
    # anchor (`endswith(path)`) would accept any host, so the port and path are pinned.
    url = request.get("url")
    parsed = urlsplit(url) if isinstance(url, str) else None
    if parsed is None or parsed.scheme != "http" or parsed.port != OMNIROUTE_PORT \
            or parsed.path != fixture["path"]:
        raise Failure(f"{leg}: request-url-unexpected: {_short(url)}")
    if not isinstance(request.get("argv"), list) or not request["argv"]:
        raise Failure(f"{leg}: request-argv-absent")
    sent = {k.lower(): v for k, v in fixture["headers"].items()}
    if sent.get(COMPRESSION_HEADER) != COMPRESSION_VALUE:
        raise Failure(f"{leg}: sent-compression-header-value: "
                      f"{_short(sent.get(COMPRESSION_HEADER))}")

    # A2 — the response reports compression off.
    response = _read_json(leg_dir / "response.json", leg, "response.json")
    if not isinstance(response.get("status"), int):
        raise Failure(f"{leg}: response-status-absent")
    values = [v for name, v in _header_values(response.get("headers"), leg, "response.json")
              if name.lower() == COMPRESSION_HEADER]
    if not values:
        raise Failure(f"{leg}: compression-header-missing")
    if len(values) > 1:
        raise Failure(f"{leg}: compression-header-duplicated: {len(values)} occurrences")
    if values[0] != COMPRESSION_VALUE:
        raise Failure(f"{leg}: compression-header-value: {_short(values[0])}")

    # A3 — the upstream received the fixture.
    record = _read_json(leg_dir / "upstream-record.json", leg, "upstream-record.json")
    if record.get("method") != fixture["method"]:
        raise Failure(f"{leg}: request-not-preserved: method {_short(record.get('method'))}")
    if record.get("path") != fixture["path"]:
        raise Failure(f"{leg}: request-not-preserved: path {_short(record.get('path'))}")
    headers = record.get("headers")
    if not isinstance(headers, dict):
        raise Failure(f"{leg}: upstream-record-malformed: headers")
    if "body" not in record:
        raise Failure(f"{leg}: upstream-record-malformed: body")
    received = _canon(record["body"])
    if nonce.encode() not in received:
        raise Failure(f"{leg}: nonce-mismatch: fixture nonce absent from upstream record")
    length = headers.get("content-length")
    if length != str(len(body)):
        raise Failure(f"{leg}: request-not-preserved: content-length "
                      f"{_short(length)} != {len(body)}")
    if received != body:
        raise Failure(f"{leg}: request-not-preserved: first diff at byte "
                      f"{_first_diff(body, received)}")
    # RECORDED, never asserted: docs/03 requires the header on the Hermes-side request and the
    # report on the response; whether OmniRoute forwards or consumes the directive is an
    # observation this proof reports, not a contract term it grades.
    upstream = headers.get(COMPRESSION_HEADER)
    observations.append(
        f"observation: {leg} upstream record "
        + (f"carries {COMPRESSION_HEADER}: {_short(upstream)}" if upstream is not None
           else f"does not carry {COMPRESSION_HEADER} (OmniRoute consumed the directive)"))


def check_config_leg(leg_dir: Path, observations: list) -> None:
    provider = _read_json(leg_dir / "hermes-provider.json", CONFIG_LEG, "hermes-provider.json")
    allowed = {"provider", "base_url", "api_mode", "key_env", "extra_headers"}
    unexpected = sorted(set(provider) - allowed)
    if unexpected:
        raise Failure(f"{CONFIG_LEG}: unexpected-provider-fields: {','.join(unexpected)}")
    extra_headers = provider.get("extra_headers")
    if not isinstance(extra_headers, dict):
        raise Failure(f"{CONFIG_LEG}: config-header-absent: extra_headers")
    hits = [(k, v) for k, v in extra_headers.items() if k.lower() == COMPRESSION_HEADER]
    if not hits:
        raise Failure(f"{CONFIG_LEG}: config-header-absent")
    if len(hits) > 1:
        raise Failure(f"{CONFIG_LEG}: config-header-duplicated: {len(hits)} keys")
    if hits[0][1] != COMPRESSION_VALUE:
        raise Failure(f"{CONFIG_LEG}: config-header-value: {_short(hits[0][1])}")
    base_url = provider.get("base_url")
    if not isinstance(base_url, str) or not base_url.endswith(OMNIROUTE_BASE_SUFFIX):
        raise Failure(f"{CONFIG_LEG}: base-url-unexpected: {_short(base_url)}")
    key_env = provider.get("key_env")
    if not isinstance(key_env, str) or not KEY_ENV_RE.match(key_env):
        raise Failure(f"{CONFIG_LEG}: key-env-not-a-name: {_short(key_env)}")
    api_mode = provider.get("api_mode")
    if not isinstance(api_mode, str) or not api_mode:
        raise Failure(f"{CONFIG_LEG}: api-mode-absent")
    # RECORDED, never asserted: docs/03 §2 pins `codex_responses` and the live profiles use
    # `chat_completions` (docs/OMNIROUTE-HERMES-FEDORA-HANDOFF.md:17). That deviation is the
    # owner's open decision (task #35); this proof reports it, it does not resolve it.
    observations.append(
        f"observation: {CONFIG_LEG} api_mode = {_short(api_mode)} "
        f"(RECORDED, not asserted - ADR 0002 deviation, owner task #35)")


def check_bundle(root: Path, fixtures_dir: Path) -> str:
    root = Path(root)
    if not root.exists():
        raise Deferred("S0-04 evidence not captured")
    if not root.is_dir():
        raise Failure(f"evidence-root-not-a-directory: {root}")
    present = sorted(p.name for p in root.iterdir())
    if not any(name in REQUIRED_LEGS for name in present):
        raise Deferred("S0-04 evidence not captured")
    unexpected = [name for name in present if name not in REQUIRED_LEGS]
    if unexpected:
        raise Failure(f"unexpected-leg: {','.join(unexpected)}")
    missing = [leg for leg in REQUIRED_LEGS if leg not in present]
    if missing:
        raise Failure(f"{missing[0]}: leg directory absent")
    _screen_tree(root)
    observations: list = []
    for leg in REQUIRED_LEGS:
        leg_dir = root / leg
        if not _stat.S_ISDIR(leg_dir.lstat().st_mode):
            raise Failure(f"{leg}: leg directory absent")
        if leg == CONFIG_LEG:
            check_config_leg(leg_dir, observations)
        else:
            check_request_leg(leg, leg_dir, fixtures_dir, observations)
    for line in observations:
        print(_redact(line))
    return f"PASS: S0-04 compression-contract - 3 assertions over {len(REQUIRED_LEGS)} legs"


def main(argv) -> int:
    args = list(argv[1:])
    fixtures_dir = None
    if "--fixtures-dir" in args:
        index = args.index("--fixtures-dir")
        if index + 1 >= len(args):
            print("usage: --fixtures-dir needs a directory", file=sys.stderr)
            return 64
        fixtures_dir = Path(args[index + 1])
        del args[index:index + 2]
    if len(args) != 1:
        print("usage: check_compression.py [--fixtures-dir <dir>] <evidence-root>",
              file=sys.stderr)
        return 64
    if fixtures_dir is None:
        fixtures_dir = Path(__file__).resolve().parent / "fixtures"
    try:
        print(check_bundle(Path(args[0]), fixtures_dir))
        return 0
    except Deferred as deferred:
        print(f"deferred: {_redact(str(deferred))}")
        return 2
    except Failure as failure:
        print(f"failure_reason: {_redact(str(failure))}")
        return 1
    except Exception as exc:                                  # noqa: BLE001 - fail closed
        print(f"failure_reason: {_redact(f'malformed evidence: {type(exc).__name__}: {exc}')}")
        return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
