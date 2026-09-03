#!/usr/bin/env python3
"""Probe whether OmniRoute accepts the explicitly supplied bearer credential."""
import os
import sys
import urllib.error
import urllib.request


def main():
    key = os.environ.get("OMNIROUTE_API_KEY")
    if not key:
        return 10
    request = urllib.request.Request(
        sys.argv[1],
        headers={"Authorization": f"Bearer {key}"},
        method="GET",
    )
    try:
        with urllib.request.urlopen(request, timeout=5) as response:
            return 0 if 200 <= response.status < 300 else 11
    except urllib.error.HTTPError:
        return 11
    except urllib.error.URLError:
        return 11


if __name__ == "__main__":
    raise SystemExit(main())
