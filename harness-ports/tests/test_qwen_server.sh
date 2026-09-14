#!/usr/bin/env bash
# Plumbing proof for harness-ports/bin/qwen-server.sh — the local build-lane model's service wrapper.
#
# WHAT THIS PROVES: the argv the unit will run carries the MEASURED shape (FINDINGS-LOCAL-BUILDER-QWEN38 §6:
# fully resident -ngl 99, 262k context over four q4_0 slots, MTP n=3, the effort kwarg, the API-key FILE — and
# not the brief's -ngl 54); every knob is an env override; the unit text is quoted by systemd's rules (bash %q
# is not systemd quoting); keygen writes 0600/64-hex and never prints the value; verify fails closed with the
# documented exit codes on an absent binary (2), an absent model (3), a blob/sha256 mismatch (3), a non-GGUF (3).
# WHAT IT DOES NOT PROVE: that llama-server starts, serves, or is fast — that is `install` + `probe` on the PC.
#
# Runs entirely under a throwaway $TMP with a FAKE llama-server (a shell stub) and a FAKE HF snapshot tree.
# No systemd, no GPU, no network; `health`/`probe` are exercised only against a closed port.
set -uo pipefail
unset QWEN_LLAMA_SERVER QWEN_MODEL_GGUF QWEN_MODEL_REPO_DIR QWEN_MODEL_FILE QWEN_MODEL_SHA256 QWEN_ALIAS QWEN_HOST \
      QWEN_PORT QWEN_CTX QWEN_SLOTS QWEN_NGL QWEN_KV_TYPE QWEN_MTP_N QWEN_EFFORT QWEN_CACHE_REUSE QWEN_KEY_FILE \
      QWEN_UNIT QWEN_HOME QWEN_HEALTH_WAIT_S 2>/dev/null || true

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
QS="$HERE/../bin/qwen-server.sh"
TMP="$(mktemp -d)" || { echo "FATAL: mktemp -d failed" >&2; exit 1; }
trap 'rm -rf "$TMP"' EXIT

pass=0; fail=0
check() { # check <label> <cond-rc> <why>
  if [ "$2" -eq 0 ]; then pass=$((pass+1)); echo "[PASS] $1"; else fail=$((fail+1)); echo "[FAIL] $1"; fi
  echo "         because: $3"
}

SHA=40fac4050e940397dbf13087afd50f4734a11805bf9d65ef8ddd7483470e6199   # the real blob name = sha256 of the GGUF
FILE=Qwen3.8-27B-UD-IQ4_XS.gguf

# --- the FAKE inputs (labelled test doubles: a stub binary, a stub HF snapshot tree) --------------------------
BIN="$TMP/llama-server"; printf '#!/bin/sh\necho "version: 1 (fake)"\n' > "$BIN"; chmod +x "$BIN"
REPO="$TMP/models--unsloth--Qwen3.8-27B-GGUF"
mkdir -p "$REPO/snapshots/4ca7" "$REPO/blobs"
printf 'GGUF\x03\x00\x00\x00rest' > "$REPO/blobs/$SHA"
ln -s "../../blobs/$SHA" "$REPO/snapshots/4ca7/$FILE"
export QWEN_LLAMA_SERVER="$BIN" QWEN_MODEL_REPO_DIR="$REPO" QWEN_HOME="$TMP/qwen-home" \
       QWEN_KEY_FILE="$TMP/cfg/api-key" QWEN_PORT=65123 QWEN_HOST=127.0.0.1

bash -n "$QS"; check "bash -n qwen-server.sh" $? "the script parses"

# --- argv: the measured shape, one token per line -----------------------------------------------------------
ARGV="$TMP/argv.txt"; bash "$QS" argv > "$ARGV"; rc=$?
check "argv rc 0" $rc "argv is the testable surface"
pair() { # pair FLAG VALUE — FLAG on line N and VALUE on line N+1
  awk -v f="$1" -v v="$2" 'prev==f && $0==v {found=1} {prev=$0} END {exit found?0:1}' "$ARGV"
}
tok() { grep -qxF -- "$1" "$ARGV"; }
[ "$(head -1 "$ARGV")" = "$BIN" ]; check "argv[0] is the llama-server binary" $? "$(head -1 "$ARGV")"
pair -m "$REPO/snapshots/4ca7/$FILE"; check "argv -m resolves the HF snapshot path" $? "resolve_model globs snapshots/*/$FILE"
pair --alias qwen3.8-27b-local; check "argv --alias qwen3.8-27b-local" $? "the model id OmniRoute will expose as qwen-local/qwen3.8-27b-local"
pair --host 127.0.0.1 && pair --port 65123; check "argv --host 127.0.0.1 --port \$QWEN_PORT" $? "loopback only; the port is an env knob"
pair --api-key-file "$TMP/cfg/api-key"; check "argv --api-key-file (a FILE, never --api-key on the cmdline)" $? "the key must not show in ps"
pair -ngl 99; check "argv -ngl 99 (fully resident)" $? "the brief's -ngl 54 measured 7.0x slower (§6)"
! pair -ngl 54; check "argv NOT -ngl 54" $? "negative control on the default"
pair -c 262144; check "argv -c 262144" $? "the full context fits at 19.7 GiB with q4_0 KV (§6)"
pair -fa on && pair -ctk q4_0 && pair -ctv q4_0; check "argv -fa on -ctk q4_0 -ctv q4_0" $? "the measured KV shape"
pair -np 1; check "argv -np 1 (ONE slot = the whole 262k for one lane)" $? "N5k overflowed a 65k slot four times at 8 min (2026-09-14); Hermes compacts at 75 % of the 200k it is told"
! pair -np 4; check "argv NOT -np 4" $? "negative control on the slot default"
QWEN_SLOTS=4 bash "$QS" argv | awk 'prev=="-np" && $0=="4" {f=1} {prev=$0} END {exit f?0:1}'; check "QWEN_SLOTS=4 overrides -np" $? "parallel lanes stay one env away (after a Hermes-side context cap)"
pair --spec-type draft-mtp && pair --spec-draft-n-max 3; check "argv MTP n=3" $? "86.9 t/s at 90 % acceptance (§6); n=2 measured slower"
pair --chat-template-kwargs '{"reasoning_effort":"medium"}' && tok --jinja; check "argv --jinja + effort kwarg" $? "server-side default effort; a request's own reasoning_effort wins"
pair --cache-reuse 256; check "argv --cache-reuse 256" $? "prompt-prefix reuse for repeated lane system prompts"
n=$(grep -c . "$ARGV"); [ "$n" -eq 34 ]; check "argv token count is 34" $? "got $n — an added or dropped flag changes this"

# --- env overrides win --------------------------------------------------------------------------------------
QWEN_NGL=54 bash "$QS" argv | awk 'prev=="-ngl" && $0=="54" {f=1} {prev=$0} END {exit f?0:1}'
check "QWEN_NGL=54 overrides -ngl" $? "every knob is an env override"
QWEN_MODEL_GGUF=/x/y.gguf bash "$QS" argv | awk 'prev=="-m" && $0=="/x/y.gguf" {f=1} {prev=$0} END {exit f?0:1}'
check "QWEN_MODEL_GGUF pins -m explicitly" $? "an explicit path skips the snapshot glob"
QWEN_EFFORT=high QWEN_MTP_N=2 bash "$QS" argv > "$TMP/argv2.txt"
grep -qxF -- '{"reasoning_effort":"high"}' "$TMP/argv2.txt" && awk 'prev=="--spec-draft-n-max" && $0=="2" {f=1} {prev=$0} END {exit f?0:1}' "$TMP/argv2.txt"
check "QWEN_EFFORT / QWEN_MTP_N override" $? "the effort kwarg and the MTP depth are knobs"

# --- unit: systemd quoting, not bash quoting ----------------------------------------------------------------
UNIT="$TMP/unit.txt"; bash "$QS" unit > "$UNIT"; rc=$?
check "unit rc 0" $rc "prints the user unit"
grep -qx '\[Unit\]' "$UNIT" && grep -qx '\[Service\]' "$UNIT" && grep -qx '\[Install\]' "$UNIT"
check "unit has [Unit]/[Service]/[Install]" $? "the three sections"
EXEC=$(grep '^ExecStart=' "$UNIT")
[ "${EXEC#ExecStart=}" != "" ] && case "$EXEC" in "ExecStart=\"$BIN\" \"-m\" \"$REPO/snapshots/4ca7/$FILE\" "*) true;; *) false;; esac
check "ExecStart starts with the quoted binary and -m path" $? "${EXEC:0:90}…"
case "$EXEC" in *'"--chat-template-kwargs" "{\"reasoning_effort\":\"medium\"}"'*) true;; *) false;; esac
check "ExecStart quotes the JSON by systemd rules (\"{\\\"…\\\"}\")" $? "systemd.syntax(7): double quotes with \\\" inside"
! grep -q '\\{' "$UNIT"; check "ExecStart carries no bash-%q escapes (\\{)" $? "systemd keeps unknown escapes verbatim → broken JSON at llama-server"
grep -qx 'Restart=on-failure' "$UNIT" && grep -qx 'WantedBy=default.target' "$UNIT" && grep -qx "WorkingDirectory=$TMP/qwen-home" "$UNIT"
check "unit Restart=on-failure, WantedBy=default.target, WorkingDirectory=\$QWEN_HOME" $? "a user unit that restarts on a crash"
grep -qx "StandardOutput=append:$TMP/qwen-home/logs/server.log" "$UNIT"; check "unit logs append to \$QWEN_HOME/logs/server.log" $? "one log file for the server"
grep -qx 'StartLimitBurst=3' "$UNIT"; check "unit StartLimitBurst=3" $? "a model that OOMs at load does not restart forever"
# a token that needs every escape: backslash, quote, dollar, percent
QWEN_ALIAS='a\b"c$d%e' bash "$QS" unit | grep -qF -- '"--alias" "a\\b\"c$$d%%e"'
check "sd_quote escapes \\ \" \$ % per systemd.syntax(7)" $? "\\\\ \\\" \$\$ %% — a literal in each class survives"

# --- keygen: 0600, 64 hex, never printed, idempotent ---------------------------------------------------------
OUT=$(bash "$QS" keygen); rc=$?
check "keygen rc 0" $rc "$OUT"
KEY=$(cat "$TMP/cfg/api-key" 2>/dev/null)
[ "${#KEY}" -eq 64 ] && [[ "$KEY" =~ ^[0-9a-f]{64}$ ]]; check "key file is 64 hex chars" $? "openssl rand -hex 32"
[ "$(stat -c %a "$TMP/cfg/api-key")" = "600" ]; check "key file mode 0600" $? "got $(stat -c %a "$TMP/cfg/api-key")"
[ "$(stat -c %a "$TMP/cfg")" = "700" ]; check "key dir mode 0700" $? "got $(stat -c %a "$TMP/cfg")"
case "$OUT" in *"$KEY"*) false;; *) true;; esac; check "keygen output never carries the key value" $? "the value is written, not printed"
OUT2=$(bash "$QS" keygen); [ "$(cat "$TMP/cfg/api-key")" = "$KEY" ] && case "$OUT2" in *"present"*) true;; *) false;; esac
check "keygen is idempotent (second run keeps the key)" $? "$OUT2"

# --- verify: the positive, then four negative controls with the documented exit codes -----------------------
OUT=$(bash "$QS" verify 2>&1); rc=$?
check "verify rc 0 on the fake-but-consistent tree" $rc "$OUT"
case "$OUT" in *"inputs verified"*"$SHA"*) true;; *) false;; esac; check "verify names the sha256 it checked" $? "$OUT"
OUT=$(QWEN_LLAMA_SERVER="$TMP/absent" bash "$QS" verify 2>&1); rc=$?
[ $rc -eq 2 ] && case "$OUT" in *"binary absent"*) true;; *) false;; esac; check "verify rc 2 on an absent binary" $? "rc=$rc: $OUT"
OUT=$(QWEN_MODEL_REPO_DIR="$TMP/no-models" bash "$QS" verify 2>&1); rc=$?
[ $rc -eq 3 ] && case "$OUT" in *"model GGUF absent"*) true;; *) false;; esac; check "verify rc 3 on an absent model" $? "rc=$rc: $OUT"
OUT=$(QWEN_MODEL_SHA256=deadbeef bash "$QS" verify 2>&1); rc=$?
[ $rc -eq 3 ] && case "$OUT" in *"identity mismatch"*"deadbeef"*) true;; *) false;; esac; check "verify rc 3 on a blob/sha256 mismatch" $? "rc=$rc: $OUT"
REPO2="$TMP/models-notgguf"; mkdir -p "$REPO2/snapshots/s" "$REPO2/blobs"; printf 'NOTGGUF' > "$REPO2/blobs/$SHA"; ln -s "../../blobs/$SHA" "$REPO2/snapshots/s/$FILE"
OUT=$(QWEN_MODEL_REPO_DIR="$REPO2" bash "$QS" verify 2>&1); rc=$?
[ $rc -eq 3 ] && case "$OUT" in *"not a GGUF"*) true;; *) false;; esac; check "verify rc 3 on a non-GGUF blob with the right name" $? "rc=$rc: $OUT"

# --- health/probe against a closed port; the usage line ------------------------------------------------------
OUT=$(bash "$QS" health 2>&1); rc=$?
[ $rc -eq 1 ] && case "$OUT" in *"/health not ok"*) true;; *) false;; esac; check "health rc 1 with no server" $? "rc=$rc: $OUT"
OUT=$(bash "$QS" probe 2>&1); rc=$?
[ $rc -eq 6 ] && case "$OUT" in *"not healthy"*) true;; *) false;; esac; check "probe rc 6 with no server" $? "rc=$rc: $OUT"
bash "$QS" bogus >/dev/null 2>&1; [ $? -eq 64 ]; check "unknown subcommand rc 64" $? "usage"

echo
echo "qwen-server: $pass passed, $fail failed"
[ "$fail" -eq 0 ]
