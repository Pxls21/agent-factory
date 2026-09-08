#!/usr/bin/env python3
"""connect_probe.py — the bounded connection instrument behind C2/C3/C4/C5.

Three modes, all of which send ZERO application bytes to the target:
  tcp <ip> <port> <timeout>            TCP connect, then close
  tls <ip> <port> <timeout> <sni>      TCP connect + TLS handshake, then close
  udp <ip> <port> <timeout>            one DNS query datagram, then wait for an answer

Exit codes reuse curl's vocabulary so one denial set covers every canary:
  0   the connection/handshake SUCCEEDED (an egress-permitted observation)
  6   the name could not be resolved (curl (6); this instrument takes addresses, so unused)
  7   the peer could not be reached: ENETUNREACH / EHOSTUNREACH / ECONNREFUSED / EPERM
  28  the attempt timed out
  9   the instrument itself could not run (bad arguments) — never a denial
The exact OS diagnostic is printed on stdout; check_egress.py matches it against the
mechanism's denial vocabulary, so a failure produced by something else (an ambient proxy, a
missing binary) is rejected rather than counted as containment.
"""
import errno
import socket
import ssl
import sys

UNREACHABLE = {errno.ENETUNREACH, errno.EHOSTUNREACH, errno.ECONNREFUSED, errno.EPERM,
               errno.EACCES, errno.ENETDOWN}
DNS_QUERY = (b"\x00\x01\x01\x00\x00\x01\x00\x00\x00\x00\x00\x00"
             b"\x07example\x03com\x00\x00\x01\x00\x01")


def _fail(exc):
    print(f"{type(exc).__name__} {exc}")
    if isinstance(exc, (socket.timeout, TimeoutError)):
        return 28
    if isinstance(exc, ssl.SSLError):
        return 7
    if isinstance(exc, OSError) and exc.errno in UNREACHABLE:
        return 7
    if isinstance(exc, socket.gaierror):
        return 6
    print(f"unclassified {type(exc).__name__}")
    return 7


def main(argv):
    if len(argv) < 4:
        print("usage: connect_probe.py tcp|tls|udp <ip> <port> <timeout> [sni]")
        return 9
    mode, ip, port, timeout = argv[0], argv[1], int(argv[2]), float(argv[3])
    if mode == "udp":
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.settimeout(timeout)
        try:
            sock.sendto(DNS_QUERY, (ip, port))
            data, _ = sock.recvfrom(512)
            print(f"answered {len(data)} bytes")
            return 0
        except Exception as exc:              # noqa: BLE001 - classified in _fail
            return _fail(exc)
        finally:
            sock.close()
    if mode not in ("tcp", "tls"):
        print(f"unknown mode {mode}")
        return 9
    try:
        sock = socket.create_connection((ip, port), timeout=timeout)
    except Exception as exc:                  # noqa: BLE001 - classified in _fail
        return _fail(exc)
    try:
        if mode == "tcp":
            print("connected")
            return 0
        sni = argv[4] if len(argv) > 4 else ip
        context = ssl.create_default_context()
        with context.wrap_socket(sock, server_hostname=sni) as tls:
            print(f"handshake ok {tls.version()}")
            return 0
    except Exception as exc:                  # noqa: BLE001 - classified in _fail
        return _fail(exc)
    finally:
        try:
            sock.close()
        except OSError:
            pass


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
