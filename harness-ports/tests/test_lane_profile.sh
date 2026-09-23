#!/usr/bin/env bash
# Deterministic contract tests for the per-lane Hermes profile helper.
# Uses a labelled fake Hermes CLI and throwaway profile root; no real profile is read or changed.
set -uo pipefail

# Hermetic: a caller's runtime/test overrides cannot redirect this suite to real profiles.
unset HERMES_BIN HERMES_PROFILES_DIR HERMES_SOURCE_PROFILE FAKE_HERMES_CALLS 2>/dev/null || true
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
HELPER="$HERE/../bin/lane-profile.sh"
TMP="$(mktemp -d)" || exit 1
trap 'rm -rf "$TMP"' EXIT
PROFILES="$TMP/profiles"; SOURCE="$PROFILES/agentfactory"; BIN="$TMP/bin"
mkdir -p "$SOURCE/hooks" "$SOURCE/cron" "$BIN"
printf 'hook-marker\n' > "$SOURCE/hooks/marker"
printf 'cron-marker\n' > "$SOURCE/cron/marker"
printf 'OMNIROUTE_API_KEY=test-only\n' > "$SOURCE/.env"
cat > "$SOURCE/config.yaml" <<'YAML'
model:
  default: auto/best-coding-fast
  provider: custom:omniroute-fedora
  base_url: http://127.0.0.1:20128/v1
  api_mode: chat_completions
fallback_providers:
- provider: custom
  model: codex/example
  base_url: http://127.0.0.1:20128/v1
  key_env: OMNIROUTE_API_KEY
agent:
  max_turns: 60
providers:
  omniroute-fedora:
    api: http://127.0.0.1:20128/v1
    key_env: OMNIROUTE_API_KEY
YAML
cp "$SOURCE/config.yaml" "$TMP/source-config.yaml"

cat > "$BIN/hermes" <<'SH'
#!/usr/bin/env bash
set -u
printf '%s\n' "$*" >> "${FAKE_HERMES_CALLS:?}"
case "${1:-} ${2:-}" in
  'profile create')
    name="${!#}"; mkdir -p "$HERMES_PROFILES_DIR/$name"
    cp "$HERMES_PROFILES_DIR/$HERMES_SOURCE_PROFILE/config.yaml" "$HERMES_PROFILES_DIR/$name/config.yaml"
    cp "$HERMES_PROFILES_DIR/$HERMES_SOURCE_PROFILE/.env" "$HERMES_PROFILES_DIR/$name/.env"
    ;;
  'profile delete')
    name="${3:-}"; IFS= read -r answer || true
    [ "$answer" = "$name" ] || exit 3
    rm -rf "$HERMES_PROFILES_DIR/$name"
    ;;
  *) exit 2;;
esac
SH
chmod +x "$BIN/hermes"
export HERMES_BIN="$BIN/hermes" HERMES_PROFILES_DIR="$PROFILES" HERMES_SOURCE_PROFILE=agentfactory
export FAKE_HERMES_CALLS="$TMP/hermes.calls"; : > "$FAKE_HERMES_CALLS"

pass=0; fail=0
check() {
  if [ "$2" -eq 0 ]; then pass=$((pass+1)); printf '[PASS] %s\n' "$1"; else fail=$((fail+1)); printf '[FAIL] %s\n' "$1"; fi
  printf '         because: %s\n' "$3"
}
run_verify() {
  VERIFY_OUT="$(bash "$HELPER" verify "$1" 2>&1)"; VERIFY_RC=$?
}

# Name normalization is observed through create output, not a duplicate test implementation.
NAME1="$(bash "$HELPER" create 'pc-t92')"; RC1=$?
NAME2="$(bash "$HELPER" create 'PC_T92.R2')"; RC2=$?
LONG_ID='ABCDEFGHIJKLMNOPQRSTUVWXYZ-1234567890-abcdefghijk'
NAME3="$(bash "$HELPER" create "$LONG_ID")"; RC3=$?
[ "$RC1" -eq 0 ] && [ "$NAME1" = aflanepct92 ] \
  && [ "$RC2" -eq 0 ] && [ "$NAME2" = aflanepct92r2 ] \
  && [ "$RC3" -eq 0 ] && [ "$NAME3" = aflaneabcdefghijklmnopqrstuvwxyz1234567890abcd ]
check "the name rule lowercases, drops non-alphanumerics, and truncates the lane portion to 40" $? \
  "pc-t92=$NAME1 PC_T92.R2=$NAME2 long=$NAME3"

TARGET="$PROFILES/$NAME1"
python3 - "$TMP/source-config.yaml" "$TARGET/config.yaml" pc-t92 <<'PY'
import copy, sys, yaml
source, target, lane = sys.argv[1:]
with open(source, encoding="utf-8") as f: before = yaml.safe_load(f)
with open(target, encoding="utf-8") as f: after = yaml.safe_load(f)
expected = copy.deepcopy(before)
expected.pop("fallback_providers", None)
expected["model"].setdefault("default_headers", {})["x-omniroute-session-id"] = lane
assert after == expected, (after, expected)
assert set(before) - set(after) == {"fallback_providers"}
assert set(after) - set(before) == set()
PY
CONFIG_RC=$?
SOURCE_SHA="$(sha256sum "$SOURCE/.env" | awk '{print $1}')"
TARGET_SHA="$(sha256sum "$TARGET/.env" | awk '{print $1}')"
[ "$CONFIG_RC" -eq 0 ] && [ "$SOURCE_SHA" = "$TARGET_SHA" ] \
  && [ "$(cat "$TARGET/hooks/marker")" = hook-marker ] \
  && [ "$(cat "$TARGET/cron/marker")" = cron-marker ]
check "create strips only the chain, adds the exact lane header, preserves .env, and copies hooks/cron" $? \
  "semantic-diff-rc=$CONFIG_RC env_equal=$([ "$SOURCE_SHA" = "$TARGET_SHA" ] && echo yes || echo no)"

BEFORE_SHA="$(sha256sum "$TARGET/config.yaml" | awk '{print $1}')"
BEFORE_CREATES="$(grep -c '^profile create ' "$FAKE_HERMES_CALLS")"
REUSED="$(bash "$HELPER" create pc-t92)"; REUSE_RC=$?
AFTER_SHA="$(sha256sum "$TARGET/config.yaml" | awk '{print $1}')"
AFTER_CREATES="$(grep -c '^profile create ' "$FAKE_HERMES_CALLS")"
[ "$REUSE_RC" -eq 0 ] && [ "$REUSED" = "$NAME1" ] && [ "$BEFORE_SHA" = "$AFTER_SHA" ] && [ "$BEFORE_CREATES" = "$AFTER_CREATES" ]
check "create reuses an existing verified profile without cloning or rewriting it" $? \
  "rc=$REUSE_RC create_calls=$BEFORE_CREATES->$AFTER_CREATES config_sha_equal=$([ "$BEFORE_SHA" = "$AFTER_SHA" ] && echo yes || echo no)"

cp "$TARGET/config.yaml" "$TMP/good-config.yaml"; cp "$TARGET/.env" "$TMP/good-env"
printf '\nfallback_providers:\n- provider: custom\n  model: codex/mutant\n' >> "$TARGET/config.yaml"
run_verify pc-t92
[ "$VERIFY_RC" -ne 0 ] && [ "$VERIFY_OUT" = 'lane-profile: chain present' ]
check "verify rejects a restored fallback chain with the exact reason" $? "rc=$VERIFY_RC output=$VERIFY_OUT"
cp "$TMP/good-config.yaml" "$TARGET/config.yaml"

python3 - "$TARGET/config.yaml" <<'PY'
from pathlib import Path
import re
import sys
p = Path(sys.argv[1]); s = p.read_text()
s, count = re.subn(r'(x-omniroute-session-id:\s*)[^\n]+', r'\1wrong-lane', s, count=1)
assert count == 1
p.write_text(s)
PY
run_verify pc-t92
[ "$VERIFY_RC" -ne 0 ] && [ "$VERIFY_OUT" = 'lane-profile: header missing or wrong: wrong-lane' ]
check "verify rejects a wrong lane header with the exact reason" $? "rc=$VERIFY_RC output=$VERIFY_OUT"
cp "$TMP/good-config.yaml" "$TARGET/config.yaml"

printf 'DRIFT=1\n' >> "$TARGET/.env"
run_verify pc-t92
[ "$VERIFY_RC" -ne 0 ] && [ "$VERIFY_OUT" = 'lane-profile: env drift' ]
check "verify rejects changed environment bytes with the exact reason" $? "rc=$VERIFY_RC output=$VERIFY_OUT"
cp "$TMP/good-env" "$TARGET/.env"

run_verify pc-t92
[ "$VERIFY_RC" -eq 0 ] && [ -z "$VERIFY_OUT" ]
check "verify accepts the restored exact clone" $? "rc=$VERIFY_RC output=${VERIFY_OUT:-<empty>}"

REFUSE_OUT="$(bash "$HELPER" remove agentfactory 2>&1)"; REFUSE_RC=$?
[ "$REFUSE_RC" -eq 64 ] && [ "$REFUSE_OUT" = 'lane-profile: refusing to delete non-lane profile agentfactory' ] \
  && [ -d "$SOURCE" ] && ! grep -Fq 'profile delete agentfactory' "$FAKE_HERMES_CALLS"
check "remove refuses a profile without the aflane prefix before the Hermes CLI" $? \
  "rc=$REFUSE_RC output=$REFUSE_OUT source_exists=$([ -d "$SOURCE" ] && echo yes || echo no)"

REMOVE_OUT="$(bash "$HELPER" remove "$NAME1" 2>&1)"; REMOVE_RC=$?
[ "$REMOVE_RC" -eq 0 ] && [ ! -e "$TARGET" ] && grep -Fq "profile delete $NAME1" "$FAKE_HERMES_CALLS"
check "remove confirms and deletes an aflane profile" $? \
  "rc=$REMOVE_RC target_exists=$([ -e "$TARGET" ] && echo yes || echo no)"

echo; echo "lane profile: $pass passed, $fail failed"; [ "$fail" -eq 0 ]
