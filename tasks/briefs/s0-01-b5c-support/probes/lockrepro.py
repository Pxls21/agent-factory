"""Mechanism check: does a SIGTERM handler that re-acquires a threading.Lock already
held by the main thread self-deadlock in CPython 3.11 (the same shape as
frame_tee.py _sigterm_handler -> _write_status -> `with status_lock`)?"""
import os, signal, sys, threading, time

lock = threading.Lock()
entered = []

def handler(signum, frame):
    entered.append("handler-start")
    with lock:                      # same non-reentrant lock the main thread holds
        entered.append("handler-got-lock")
    os._exit(70)

signal.signal(signal.SIGTERM, handler)
pid = os.getpid()

def killer():
    time.sleep(0.3)
    os.kill(pid, signal.SIGTERM)

threading.Thread(target=killer, daemon=True).start()
t0 = time.monotonic()
with lock:
    time.sleep(2.0)                 # main thread holds the lock when TERM arrives
print("MAIN RETURNED after %.2fs (no deadlock); handler trace=%s" % (time.monotonic() - t0, entered))
sys.stdout.flush()
time.sleep(3)
print("still alive: handler never completed" if "handler-got-lock" not in entered else "handler completed")
