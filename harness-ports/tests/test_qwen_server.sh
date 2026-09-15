#!/usr/bin/env bash
# Plumbing proof for harness-ports/bin/qwen-server.sh — the local build-lane model's service wrapper.
#
# WHAT THIS PROVES: the argv the unit will run carries the MEASURED shape (FINDINGS-LOCAL-BUILDER-QWEN38 §6:
# fully resident -ngl 99, 262k context over one q4_0 slot, selectable matrix/cache/speculation knobs, the effort
# kwarg, the API-key FILE — and not the brief's -ngl 54); every knob is an env override; the unit text is quoted
# by systemd's rules (bash %q is not systemd quoting); keygen writes 0600/64-hex and never prints the value;
# verify fails closed with the documented exit codes on an absent binary (2), an absent model (3), a blob/sha256
# mismatch (3), a non-GGUF (3); guard classifies real child-process routes and runs before every service mutation.
# WHAT IT DOES NOT PROVE: that llama-server starts, serves, or is fast — that is `install` + `probe` on the PC.
#
# Runs entirely under a throwaway $TMP with a FAKE llama-server, HF snapshot tree, systemctl,
# systemd-analyze and curl. Real sleeper children with test-only argv0 supply `/proc/<pid>/environ`;
# the test kills and waits for them by pid.
# No systemd, GPU, real model-server request, or real lane directory is touched.
set -uo pipefail
unset QWEN_LLAMA_SERVER QWEN_MODEL_GGUF QWEN_MODEL_REPO_DIR QWEN_MODEL_FILE QWEN_MODEL_SHA256 QWEN_ALIAS QWEN_HOST \
      QWEN_PORT QWEN_CTX QWEN_SLOTS QWEN_NGL QWEN_KV_TYPE QWEN_MTP_N QWEN_EFFORT QWEN_CACHE_REUSE QWEN_CACHE_RAM \
      QWEN_CTXCP QWEN_CMS QWEN_UBATCH QWEN_SPEC_P_MIN QWEN_SPEC_TYPE QWEN_KEY_FILE QWEN_UNIT QWEN_HOME \
      QWEN_HEALTH_WAIT_S QWEN_LANES_DIR QWEN_PROC_ROOT 2>/dev/null || true

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
QS="$HERE/../bin/qwen-server.sh"
TMP="$(mktemp -d)" || { echo "FATAL: mktemp -d failed" >&2; exit 1; }
CHILD_PIDS=""
cleanup() {
  local pid
  for pid in $CHILD_PIDS; do kill "$pid" 2>/dev/null || true; wait "$pid" 2>/dev/null || true; done
  rm -rf "$TMP"
}
trap cleanup EXIT

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
pair --cache-ram 8192; check "argv --cache-ram 8192" $? "the unit records the server's current implicit MiB default"
n=$(grep -c . "$ARGV"); [ "$n" -eq 36 ]; check "argv token count is 36" $? "got $n — exactly --cache-ram + 8192 extend the PIN's 34 tokens"

# The fixture makes the compatibility claim mechanical: only --cache-ram 8192 may extend the PIN contract.
# Its expected hash is computed at runtime because the throwaway paths change on each run.
PIN_ARGV="$TMP/pin-argv.txt"
cat > "$PIN_ARGV" <<EOF
$BIN
-m
$REPO/snapshots/4ca7/$FILE
--alias
qwen3.8-27b-local
--host
127.0.0.1
--port
65123
--api-key-file
$TMP/cfg/api-key
-ngl
99
-c
262144
-fa
on
-ctk
q4_0
-ctv
q4_0
-np
1
--cache-reuse
256
--spec-type
draft-mtp
--spec-draft-n-max
3
--jinja
--chat-template-kwargs
{"reasoning_effort":"medium"}
--metrics
--slots
EOF
NEW_WITHOUT_CACHE_RAM="$TMP/new-without-cache-ram.txt"
awk 'prev=="--cache-ram" {prev=""; next} $0=="--cache-ram" {prev=$0; next} {print}' "$ARGV" > "$NEW_WITHOUT_CACHE_RAM"
cmp -s "$PIN_ARGV" "$NEW_WITHOUT_CACHE_RAM"
check "default argv without --cache-ram is byte-identical to the pinned 34-token fixture" $? "pin=$(sha256sum "$PIN_ARGV" | awk '{print $1}') new=$(sha256sum "$NEW_WITHOUT_CACHE_RAM" | awk '{print $1}')"

# --- six matrix knobs: presence/omission, speculation shape, and fail-closed domains -------------------------
QWEN_CACHE_RAM=4096 QWEN_CTXCP=64 QWEN_CMS=32 QWEN_UBATCH=512 QWEN_SPEC_P_MIN=0.25 bash "$QS" argv > "$TMP/cell-argv.txt"
pair_file() { awk -v f="$2" -v v="$3" 'prev==f && $0==v {found=1} {prev=$0} END {exit found?0:1}' "$1"; }
pair_file "$TMP/cell-argv.txt" --cache-ram 4096 && pair_file "$TMP/cell-argv.txt" -ctxcp 64 && \
  pair_file "$TMP/cell-argv.txt" -cms 32 && pair_file "$TMP/cell-argv.txt" -ub 512 && \
  pair_file "$TMP/cell-argv.txt" --spec-draft-p-min 0.25
check "all five scalar matrix knobs render their flag/value pairs" $? "cache RAM, ctx checkpoint, cache miss size, ubatch, p-min"
! tok -ctxcp && ! tok -cms && ! tok -ub && ! tok --spec-draft-p-min
check "unset optional scalar knobs omit their flags" $? "default argv has no ctxcp/cms/ubatch/p-min tokens"
QWEN_SPEC_TYPE=none bash "$QS" argv > "$TMP/spec-none.txt"
! grep -qxF -- --spec-type "$TMP/spec-none.txt" && ! grep -qxF -- --spec-draft-n-max "$TMP/spec-none.txt"
check "QWEN_SPEC_TYPE=none omits type and draft depth" $? "speculation is disabled rather than named"
QWEN_SPEC_TYPE=ngram-mod bash "$QS" argv > "$TMP/spec-ngram.txt"
pair_file "$TMP/spec-ngram.txt" --spec-type ngram-mod && ! grep -qxF -- --spec-draft-n-max "$TMP/spec-ngram.txt"
check "QWEN_SPEC_TYPE=ngram-mod renders the type without MTP depth" $? "the ngram cell never inherits --spec-draft-n-max"
OUT=$(QWEN_SPEC_TYPE=none QWEN_MTP_N=2 bash "$QS" argv 2>&1); rc=$?
[ "$rc" -eq 3 ] && case "$OUT" in *"QWEN_MTP_N applies only to QWEN_SPEC_TYPE=draft-mtp"*) true;; *) false;; esac
check "non-MTP speculation rejects an explicit QWEN_MTP_N" $? "rc=$rc: $OUT"
OUT=$(QWEN_SPEC_TYPE= bash "$QS" argv 2>&1); rc=$?
[ "$rc" -eq 3 ] && case "$OUT" in *"QWEN_SPEC_TYPE must be one of draft-mtp, none, ngram-mod"*) true;; *) false;; esac
check "QWEN_SPEC_TYPE empty is refused instead of silently defaulting" $? "rc=$rc: $OUT"

bad_knob() { # bad_knob ENV VALUE EXACT-SUBSTRING
  local name=$1 value=$2 want=$3 out rc
  out=$(env "$name=$value" bash "$QS" argv 2>&1); rc=$?
  [ "$rc" -eq 3 ] && case "$out" in *"$want"*) return 0;; *) return 1;; esac
}
for spec in 'QWEN_CACHE_RAM|0|QWEN_CACHE_RAM must be a positive integer' \
            'QWEN_CACHE_RAM|1.5|QWEN_CACHE_RAM must be a positive integer' \
            'QWEN_CTXCP|-1|QWEN_CTXCP must be a positive integer' \
            'QWEN_CMS|zero|QWEN_CMS must be a positive integer' \
            'QWEN_UBATCH|0|QWEN_UBATCH must be a positive integer' \
            'QWEN_SPEC_P_MIN|-0.1|QWEN_SPEC_P_MIN must be a finite number in [0,1]' \
            'QWEN_SPEC_P_MIN|1.1|QWEN_SPEC_P_MIN must be a finite number in [0,1]' \
            'QWEN_SPEC_P_MIN|nan|QWEN_SPEC_P_MIN must be a finite number in [0,1]' \
            'QWEN_SPEC_TYPE|draft|QWEN_SPEC_TYPE must be one of draft-mtp, none, ngram-mod'; do
  IFS='|' read -r name value want <<< "$spec"
  bad_knob "$name" "$value" "$want"; check "$name=$value refused with rc 3 and its named message" $? "$want"
done
QWEN_SPEC_P_MIN=0 bash "$QS" argv >/dev/null && QWEN_SPEC_P_MIN=1 bash "$QS" argv >/dev/null
check "QWEN_SPEC_P_MIN accepts both closed-interval boundaries" $? "0 and 1 are valid"

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
# `resolve_model` can return an explicit path, but install must still reject an unpinned basename before creating config/state.
INSTALL_HOME="$TMP/verify-install-home"; mkdir -p "$INSTALL_HOME"
OUT=$(HOME="$INSTALL_HOME" QWEN_MODEL_GGUF="$REPO/snapshots/4ca7/$FILE" QWEN_MODEL_SHA256=deadbeef QWEN_LANES_DIR="$TMP/no-lanes" bash "$QS" install 2>&1); rc=$?
[ "$rc" -eq 3 ] && [ ! -e "$INSTALL_HOME/.config" ] && [ ! -e "$INSTALL_HOME/qwen-builder" ] && case "$OUT" in *"identity mismatch"*) true;; *) false;; esac
check "install identity refusal creates no persistent paths" $? "rc=$rc: $OUT"
REPO2="$TMP/models-notgguf"; mkdir -p "$REPO2/snapshots/s" "$REPO2/blobs"; printf 'NOTGGUF' > "$REPO2/blobs/$SHA"; ln -s "../../blobs/$SHA" "$REPO2/snapshots/s/$FILE"
OUT=$(QWEN_MODEL_REPO_DIR="$REPO2" bash "$QS" verify 2>&1); rc=$?
[ $rc -eq 3 ] && case "$OUT" in *"not a GGUF"*) true;; *) false;; esac; check "verify rc 3 on a non-GGUF blob with the right name" $? "rc=$rc: $OUT"

# --- guard: classify live lane routes from the real child process environment -------------------------------
LANES="$TMP/lanes"; mkdir -p "$LANES"
# No guard fixture mutates the real lane tree; every command binds QWEN_LANES_DIR to this throwaway path.
QWEN_LANES_DIR="$LANES" bash "$QS" guard >/dev/null; rc=$?
check "guard rc 0 with no lane pidfiles" "$rc" "empty glob means no local lane is alive"
start_lane() { # start_lane NAME [MODEL|__ABSENT__]
  local name=$1 model=${2:-__ABSENT__} pid i cmd env_lines ready=0
  mkdir -p "$LANES/$name"
  if [ "$model" = __ABSENT__ ]; then env -u HERMES_MODEL bash -c 'exec -a hermes-test-lane sleep 300' &
  else env HERMES_MODEL="$model" bash -c 'exec -a hermes-test-lane sleep 300' & fi
  pid=$!; CHILD_PIDS="$CHILD_PIDS $pid"
  for i in $(seq 1 100); do
    cmd=$(tr '\0' ' ' < "/proc/$pid/cmdline" 2>/dev/null || true)
    env_lines=$(tr '\0' '\n' < "/proc/$pid/environ" 2>/dev/null || true)
    case "$cmd" in
      *hermes-test-lane*)
        if [ "$model" = __ABSENT__ ]; then
          if ! printf '%s\n' "$env_lines" | grep -q '^HERMES_MODEL='; then ready=1; fi
        elif printf '%s\n' "$env_lines" | grep -qxF "HERMES_MODEL=$model"; then ready=1
        fi;;
    esac
    [ "$ready" -eq 0 ] || break
    sleep 0.01
  done
  [ "$ready" -eq 1 ] || { echo "FATAL: child lane environment did not become observable" >&2; exit 1; }
  printf '%s\n' "$pid" > "$LANES/$name/lane.pid"
}
kill_children() { local pid; for pid in $CHILD_PIDS; do kill "$pid" 2>/dev/null || true; wait "$pid" 2>/dev/null || true; done; CHILD_PIDS=""; }

start_lane local agentfactory-build-local
OUT=$(QWEN_LANES_DIR="$LANES" bash "$QS" guard); rc=$?
[ "$rc" -eq 7 ] && case "$OUT" in *"$LANES/local/lane.pid "*" LOCAL"*) true;; *) false;; esac
check "guard rc 7 and reports a live local-route lane" $? "rc=$rc: $OUT"
kill_children; rm -rf "$LANES"; mkdir -p "$LANES"

start_lane cloud agentfactory-build
OUT=$(QWEN_LANES_DIR="$LANES" bash "$QS" guard); rc=$?
[ "$rc" -eq 0 ] && case "$OUT" in *"$LANES/cloud/lane.pid "*" CLOUD"*) true;; *) false;; esac
check "guard rc 0 and reports a cloud-route lane without blocking" $? "rc=$rc: $OUT"
kill_children; rm -rf "$LANES"; mkdir -p "$LANES"

start_lane absent __ABSENT__
OUT=$(QWEN_LANES_DIR="$LANES" bash "$QS" guard); rc=$?
[ "$rc" -eq 7 ] && case "$OUT" in *"$LANES/absent/lane.pid "*" LOCAL"*) true;; *) false;; esac
check "guard fails closed when HERMES_MODEL is absent" $? "rc=$rc: $OUT"
kill_children; rm -rf "$LANES"; mkdir -p "$LANES"

start_lane empty ''
OUT=$(QWEN_LANES_DIR="$LANES" bash "$QS" guard); rc=$?
[ "$rc" -eq 7 ] && case "$OUT" in *"$LANES/empty/lane.pid "*" LOCAL"*) true;; *) false;; esac
check "guard fails closed when HERMES_MODEL is empty" $? "rc=$rc: $OUT"
kill_children; rm -rf "$LANES"; mkdir -p "$LANES/stale"; printf '99999999\n' > "$LANES/stale/lane.pid"
OUT=$(QWEN_LANES_DIR="$LANES" bash "$QS" guard); rc=$?
[ "$rc" -eq 0 ] && case "$OUT" in *"$LANES/stale/lane.pid 99999999 stale"*) true;; *) false;; esac
check "guard reports and ignores a stale pidfile" $? "rc=$rc: $OUT"
rm -rf "$LANES"; mkdir -p "$LANES/unreadable"; start_lane unreadable agentfactory-build
PROC_FIXTURE="$TMP/proc-fixture"; mkdir -p "$PROC_FIXTURE"
# QWEN_PROC_ROOT is an explicit test seam: the synthetic live pid has neither cmdline nor environ, so guard must fail closed.
OUT=$(QWEN_LANES_DIR="$LANES" QWEN_PROC_ROOT="$PROC_FIXTURE" bash "$QS" guard); rc=$?
[ "$rc" -eq 7 ] && case "$OUT" in *"$LANES/unreadable/lane.pid "*" LOCAL"*) true;; *) false;; esac
check "guard fails closed when a live pid's environ is unreadable" $? "rc=$rc: $OUT"
kill_children; rm -rf "$LANES"; mkdir -p "$LANES"

# --- install/service actions: guard precedes every persistent write and systemd mutation ---------------------
SHIM="$TMP/shim"; mkdir -p "$SHIM"
CALLS="$TMP/system-calls.log"; : > "$CALLS"
cat > "$SHIM/systemctl" <<'SH'
#!/usr/bin/env bash
printf 'systemctl %s\n' "$*" >> "$QWEN_TEST_CALLS"
case "$*" in *'is-active --quiet'*) exit "${QWEN_TEST_ACTIVE_RC:-0}";; esac
exit 0
SH
cat > "$SHIM/systemd-analyze" <<'SH'
#!/usr/bin/env bash
printf 'systemd-analyze %s\n' "$*" >> "$QWEN_TEST_CALLS"
exit 0
SH
chmod +x "$SHIM/systemctl" "$SHIM/systemd-analyze"
export QWEN_TEST_CALLS="$CALLS"
SERVICE_HOME="$TMP/service-home"; mkdir -p "$SERVICE_HOME/.config/systemd/user"
SERVICE_QWEN_HOME="$SERVICE_HOME/qwen-builder"
SERVICE_KEY="$SERVICE_HOME/.config/qwen-builder/api-key"
UNIT_PATH="$SERVICE_HOME/.config/systemd/user/qwen-builder.service"
printf 'original unit bytes\n' > "$UNIT_PATH"; BEFORE=$(sha256sum "$UNIT_PATH" | awk '{print $1}')
start_lane local agentfactory-verify-local
OUT=$(HOME="$SERVICE_HOME" PATH="$SHIM:$PATH" QWEN_HOME="$SERVICE_QWEN_HOME" QWEN_KEY_FILE="$SERVICE_KEY" QWEN_LANES_DIR="$LANES" QWEN_HEALTH_WAIT_S=3 bash "$QS" install 2>&1); rc=$?
AFTER=$(sha256sum "$UNIT_PATH" | awk '{print $1}')
[ "$rc" -eq 7 ] && [ "$BEFORE" = "$AFTER" ] && [ ! -s "$CALLS" ] && [ ! -e "$SERVICE_QWEN_HOME/logs" ] && [ ! -e "$SERVICE_KEY" ]
check "AF-AP-79: local lane refusal preserves unit bytes and makes zero systemd/keygen/mkdir side effects" $? "rc=$rc before=$BEFORE after=$AFTER calls=$(wc -l < "$CALLS")"
case "$OUT" in *"$LANES/local/lane.pid "*" LOCAL"*"service change refused"*) true;; *) false;; esac
check "install refusal carries the guard line and named reason" $? "rc=$rc: $OUT"
# An identical candidate is a true no-op: it validates immutable inputs but does not guard, write, or invoke systemd.
HOME="$SERVICE_HOME" QWEN_HOME="$SERVICE_QWEN_HOME" QWEN_KEY_FILE="$SERVICE_KEY" QWEN_LANES_DIR="$TMP/no-lanes" bash "$QS" unit > "$UNIT_PATH"
BEFORE=$(sha256sum "$UNIT_PATH" | awk '{print $1}'); : > "$CALLS"
OUT=$(HOME="$SERVICE_HOME" PATH="$SHIM:$PATH" QWEN_HOME="$SERVICE_QWEN_HOME" QWEN_KEY_FILE="$SERVICE_KEY" QWEN_LANES_DIR="$LANES" bash "$QS" install 2>&1); rc=$?
AFTER=$(sha256sum "$UNIT_PATH" | awk '{print $1}')
[ "$rc" -eq 0 ] && [ "$BEFORE" = "$AFTER" ] && [ ! -s "$CALLS" ] && case "$OUT" in *"unchanged; no service change needed"*) true;; *) false;; esac
check "unchanged install is an idempotent no-op even under a live local lane" $? "rc=$rc before=$BEFORE after=$AFTER calls=$(wc -l < "$CALLS"): $OUT"
kill_children; rm -rf "$LANES"; mkdir -p "$LANES"; : > "$CALLS"

# Fake health/probe traffic too: install may proceed completely without touching the real loopback server.
# AF-AP-33 classification: these are labelled sink doubles, while guard/order assertions use real child /proc state and byte/call-log oracles.
cat > "$SHIM/curl" <<'SH'
#!/usr/bin/env bash
case "$*" in *'/health'*) printf '{"status":"ok"}\n';; *'/v1/models'*) printf '{"data":[{"id":"qwen3.8-27b-local"}]}\n';; *) exit 1;; esac
SH
chmod +x "$SHIM/curl"
printf 'original unit bytes\n' > "$UNIT_PATH"
start_lane cloud agentfactory-build
OUT=$(HOME="$SERVICE_HOME" PATH="$SHIM:$PATH" QWEN_HOME="$SERVICE_QWEN_HOME" QWEN_KEY_FILE="$SERVICE_KEY" QWEN_LANES_DIR="$LANES" QWEN_HEALTH_WAIT_S=3 bash "$QS" install 2>&1); rc=$?
[ "$rc" -eq 0 ] && grep -qx 'systemctl --user daemon-reload' "$CALLS" && \
  grep -qx 'systemctl --user enable --now qwen-builder' "$CALLS" && \
  grep -qx 'systemctl --user restart qwen-builder' "$CALLS"
check "cloud lane permits changed install through daemon-reload, enable --now, and restart" $? "rc=$rc calls=$(tr '\n' ';' < "$CALLS")"
kill_children; rm -rf "$LANES"; mkdir -p "$LANES"; : > "$CALLS"

for action in start stop restart uninstall; do
  printf 'unit survives %s refusal\n' "$action" > "$UNIT_PATH"; BEFORE=$(sha256sum "$UNIT_PATH" | awk '{print $1}')
  start_lane local agentfactory-build-local
  OUT=$(HOME="$SERVICE_HOME" PATH="$SHIM:$PATH" QWEN_HOME="$SERVICE_QWEN_HOME" QWEN_KEY_FILE="$SERVICE_KEY" QWEN_LANES_DIR="$LANES" bash "$QS" "$action" 2>&1); rc=$?
  AFTER=$(sha256sum "$UNIT_PATH" | awk '{print $1}')
  [ "$rc" -eq 7 ] && [ "$BEFORE" = "$AFTER" ] && [ ! -s "$CALLS" ]
  check "$action refuses before disk or systemd change under a live local lane" $? "rc=$rc before=$BEFORE after=$AFTER calls=$(wc -l < "$CALLS")"
  kill_children; rm -rf "$LANES"; mkdir -p "$LANES"; : > "$CALLS"
done

# --- health/probe against a closed port; the usage line ------------------------------------------------------
OUT=$(bash "$QS" health 2>&1); rc=$?
[ $rc -eq 1 ] && case "$OUT" in *"/health not ok"*) true;; *) false;; esac; check "health rc 1 with no server" $? "rc=$rc: $OUT"
OUT=$(bash "$QS" probe 2>&1); rc=$?
[ $rc -eq 6 ] && case "$OUT" in *"not healthy"*) true;; *) false;; esac; check "probe rc 6 with no server" $? "rc=$rc: $OUT"
bash "$QS" bogus >/dev/null 2>&1; [ $? -eq 64 ]; check "unknown subcommand rc 64" $? "usage"

echo
echo "qwen-server: $pass passed, $fail failed"
[ "$fail" -eq 0 ]
