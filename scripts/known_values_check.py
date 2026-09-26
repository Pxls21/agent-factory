#!/usr/bin/env python3
"""known_values_check.py: count real secret values inside files, in process, printing NAMES and COUNTS only.

The scrubber and the export gate know secret SHAPES; a secret in a shape they do not know passes both. This check knows
the VALUES: it reads each secret where it lives (an env file, a raw key file, an environment variable), never prints one,
and counts how often each appears in the targets, whole and in pieces:
  - the whole value (for a URL also its host, a bridge link's secret part);
  - every 8-byte window of a token-like value (16+ characters of one run, letters and digits), so a cut or
    wrapped copy (an `xxd` column, a line-broken paste) still counts;
  - a raw key file's printed forms: hex, base64 and base64url, with and without padding, and their 8-byte windows.

  known_values_check.py [--env-file PATH]... [--token-file PATH]... [--raw-file PATH]... [--env NAME]... [--skip KEY]... TARGET...

--token-file PATH: the file's whole content, stripped, is one secret (an API key file).

--skip KEY leaves out an env-file key that holds no secret (a public base URL); the skipped names are printed.

TARGET is a file or a directory (every regular file below it). Output: one line per secret form,
`<source>:<name> <form> whole=N windows=H/T`, then a total line. Exit 0 no hit, 3 a hit, 2 a source could not be read, is
not a regular file (a FIFO is refused at once, never read) or held no value, 64 usage. An env line whose name is not an
env name is printed as `<malformed line N>`. Born 2026-09-25 (task #252): the session export's known-values step before any ship.
"""
import argparse
import base64
import errno
import os
import re
import stat
import sys
from urllib.parse import urlsplit

MIN_VALUE = 8          # shorter env values are not secrets (flags, ports, "true")
WINDOW = 8
TOKENISH = re.compile(rb"[A-Za-z0-9_\-+/=.~]{16,}")
ENV_NAME = re.compile(r"[A-Za-z_][A-Za-z0-9_]*")


class NotRegularFile(OSError):
    """A source that is not a regular file (a FIFO, a device): refused at once, never read."""


def _read_regular(path):
    """A source's bytes, from one open that never blocks: a plain open of a FIFO waits for a writer and hung the
    transcript export's gate (VERIFY-SCRUB1 F10). A directory raises IsADirectoryError, any other file that is not
    regular NotRegularFile; a link is followed."""
    fd = os.open(path, os.O_RDONLY | os.O_NONBLOCK)
    try:
        mode = os.fstat(fd).st_mode
        if stat.S_ISDIR(mode):
            raise IsADirectoryError(errno.EISDIR, "a directory", path)
        if not stat.S_ISREG(mode):
            raise NotRegularFile(errno.EINVAL, "not a regular file", path)
        chunks = []
        while True:
            chunk = os.read(fd, 1 << 20)
            if not chunk:
                return b"".join(chunks)
            chunks.append(chunk)
    finally:
        os.close(fd)


def _env_values(path, skip=()):
    """[(name, value)] of an env file's NAME=value lines whose value has MIN_VALUE+ bytes. The name is printed, so a line
    whose part before `=` is not an env name (a malformed line, which may hold anything) is named `<malformed line N>`
    instead (VERIFY-SCRUB1 F13)."""
    out = []
    for n, text in enumerate(_read_regular(path).split(b"\n"), 1):   # N counts "\n" lines, as grep does (AF-AP-132)
        for raw in text.splitlines():                                  # a lone \r still ends an entry, as it did
            line = raw.strip()
            if not line or line.startswith(b"#") or b"=" not in line:
                continue
            key, _, val = line.partition(b"=")
            key = key.removeprefix(b"export ").strip().decode("utf-8", "replace")
            val = val.strip().strip(b"'\"")
            if key in skip:
                continue
            if len(val) >= MIN_VALUE:
                out.append((key if ENV_NAME.fullmatch(key) else "<malformed line %d>" % n, val))
    return out


def _forms(name, value):
    """-> [(form label, bytes, windowed?)] for one text value."""
    forms = [("value", value, bool(TOKENISH.fullmatch(value)) and re.search(rb"\d", value) is not None)]
    if value.startswith((b"http://", b"https://")):
        host = urlsplit(value.decode("utf-8", "replace")).hostname or ""
        if len(host) >= MIN_VALUE:
            forms.append(("host", host.encode(), False))
    return forms


def _raw_forms(data):
    b64, b64u = base64.b64encode(data), base64.urlsafe_b64encode(data)
    return [("hex", data.hex().encode(), True), ("HEX", data.hex().upper().encode(), True),
            ("base64", b64, True), ("base64-nopad", b64.rstrip(b"="), True),
            ("base64url", b64u, True), ("base64url-nopad", b64u.rstrip(b"="), True)]


def _windows(value):
    return sorted({value[i:i + WINDOW] for i in range(len(value) - WINDOW + 1)})


def _targets(paths):
    for p in paths:
        if os.path.isdir(p):
            for root, dirs, files in os.walk(p):
                dirs.sort()
                for f in sorted(files):
                    fp = os.path.join(root, f)
                    if os.path.isfile(fp) and not os.path.islink(fp):
                        yield fp
        elif os.path.isfile(p):
            yield p
        else:
            raise FileNotFoundError(p)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--env-file", action="append", default=[])
    ap.add_argument("--token-file", action="append", default=[])
    ap.add_argument("--raw-file", action="append", default=[])
    ap.add_argument("--env", action="append", default=[])
    ap.add_argument("--skip", action="append", default=[])
    ap.add_argument("targets", nargs="+")
    try:
        a = ap.parse_args(argv)
    except SystemExit as e:
        return 64 if e.code else 0
    secrets = []   # (label, form, bytes, windowed)
    try:
        for p in a.env_file:
            vals = _env_values(p, set(a.skip))
            if not vals:
                print("known-values: %s holds no value of %d+ characters" % (p, MIN_VALUE), file=sys.stderr)
                return 2
            for name, v in vals:
                secrets += [("%s:%s" % (os.path.basename(p), name), f, b, w) for f, b, w in _forms(name, v)]
        for p in a.token_file:
            v = _read_regular(p).strip()
            if len(v) < MIN_VALUE:
                print("known-values: %s holds fewer than %d characters" % (p, MIN_VALUE), file=sys.stderr)
                return 2
            secrets += [("%s:token" % os.path.basename(p), f, b, w) for f, b, w in _forms("token", v)]
        for p in a.raw_file:
            data = _read_regular(p)
            if len(data) < MIN_VALUE:
                print("known-values: %s holds fewer than %d bytes" % (p, MIN_VALUE), file=sys.stderr)
                return 2
            secrets += [("%s:raw" % os.path.basename(p), f, b, w) for f, b, w in _raw_forms(data)]
        for name in a.env:
            v = os.environ.get(name, "").encode()
            if len(v) < MIN_VALUE:
                print("known-values: $%s is unset or shorter than %d characters" % (name, MIN_VALUE), file=sys.stderr)
                return 2
            secrets += [("env:%s" % name, f, b, w) for f, b, w in _forms(name, v)]
    except OSError as e:
        print("known-values: cannot read a source (%s)" % type(e).__name__, file=sys.stderr)
        return 2
    counts = [[0, set()] for _ in secrets]
    wins = [_windows(b) if w else [] for _, _, b, w in secrets]
    nfiles = nbytes = 0
    try:
        for fp in _targets(a.targets):
            with open(fp, "rb") as fh:
                data = fh.read()
            nfiles += 1
            nbytes += len(data)
            for i, (_, _, b, _) in enumerate(secrets):
                counts[i][0] += data.count(b)
                counts[i][1].update(w for w in wins[i] if w in data)
    except FileNotFoundError as e:
        print("known-values: no such target: %s" % e, file=sys.stderr)
        return 64
    hits = 0
    for (label, form, _, _), (whole, seen), w in zip(secrets, counts, wins):
        print("%s %s whole=%d windows=%d/%d" % (label, form, whole, len(seen), len(w)))
        hits += whole + len(seen)
    if a.skip:
        print("known-values: skipped keys %s" % ", ".join(sorted(a.skip)))
    print("known-values: %d secret forms, %d files, %d bytes, %s" % (
        len(secrets), nfiles, nbytes, "NO HIT" if hits == 0 else "%d HIT(S)" % hits))
    return 3 if hits else 0


if __name__ == "__main__":
    sys.exit(main())
