#!/usr/bin/env bash
# Deterministic contract tests for the per-lane Hermes profile helper.
# Uses a labelled fake Hermes CLI and throwaway profile root; no real profile is read or changed.
set -uo pipefail

# Hermetic: a caller's runtime/test overrides cannot redirect this suite to real profiles.
unset HERMES_BIN HERMES_PROFILES_DIR HERMES_SOURCE_PROFILE FAKE_HERMES_CALLS LANE_DONE_GATE QWEN_QUADLET 2>/dev/null || true
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
    # the lanes' route (a whole-file re-emit would drop this comment)
    key_env: OMNIROUTE_API_KEY
    default_model: auto/best-coding-fast
    discover_models: True
YAML
cp "$SOURCE/config.yaml" "$TMP/source-config.yaml"
# The quadlet the helper reads. MAX_LEN differs from the 131072 fallback so a value that came from the file is
# distinguishable from a guess; the [Service] MAX_LEN is not the container's and must be ignored.
cat > "$TMP/qwen.container" <<'UNIT'
[Unit]
Description=fixture of the PC's qwen quadlet
[Container]
ContainerName=qwen
Environment=PORT=8080
Environment=SPEC=mtp
Environment=MAX_LEN=98304
Environment=PREFIX_CACHE=1
Environment="EXTRA_ARGS=--served-model-name qwen3.8-27b-local qwen3.8-27b"
[Service]
Environment=MAX_LEN=4096
Restart=always
UNIT

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
export QWEN_QUADLET="$TMP/qwen.container"

# A second base profile in the premise's order (providers first) whose lane provider already has a models block,
# followed by another provider on another route. Each extra source is written here, before any create, so the
# base-profile hashes below cover every source the suite clones.
make_source() {
  mkdir -p "$PROFILES/$1" && printf 'OMNIROUTE_API_KEY=test-only-%s\n' "$1" > "$PROFILES/$1/.env" && cat > "$PROFILES/$1/config.yaml"
}
make_source agentfactorymodels <<'YAML'
providers:
  omniroute-fedora:
    api: http://127.0.0.1:20128/v1
    name: OmniRoute Fedora
    key_env: OMNIROUTE_API_KEY
    models:
      some-cloud-model:
        context_length: 400000
      agentfactory-build-local:
        max_tokens: 8192
        context_length: 200000
    default_model: auto/best-coding-fast
    # owner note outside the models block
    transport: openai_chat
    discover_models: True
  other-provider:
    api: http://127.0.0.1:9999/v1
    models:
      agentfactory-build-local:
        context_length: 777

model:
  default: auto/best-coding-fast
  provider: custom:omniroute-fedora
  base_url: http://127.0.0.1:20128/v1
compression:
  enabled: true
  threshold: 0.5
  target_ratio: 0.2
YAML
# No provider on the lanes' route, and a list-shaped models (an allowlist, not metadata): both must be refused.
make_source agentfactorynoroute <<'YAML'
model:
  default: auto/best-coding-fast
  provider: custom:omniroute-fedora
  base_url: http://127.0.0.1:20128/v1
providers:
  omniroute-fedora:
    api: http://127.0.0.1:20129/v1
YAML
make_source agentfactorylist <<'YAML'
model:
  default: auto/best-coding-fast
  provider: custom:omniroute-fedora
  base_url: http://127.0.0.1:20128/v1
providers:
  omniroute-fedora:
    api: http://127.0.0.1:20128/v1
    models:
    - agentfactory-build-local
YAML
base_hashes() { (cd "$PROFILES" && sha256sum agentfactory*/config.yaml agentfactory*/.env); }
base_hashes > "$TMP/base-hashes.before"

pass=0; fail=0
check() {
  if [ "$2" -eq 0 ]; then pass=$((pass+1)); printf '[PASS] %s\n' "$1"; else fail=$((fail+1)); printf '[FAIL] %s\n' "$1"; fi
  printf '         because: %s\n' "$3"
}
run_verify() {
  VERIFY_OUT="$(bash "$HELPER" verify "$1" 2>&1)"; VERIFY_RC=$?
}
reset_lane() {
  rm -rf "$PROFILES/aflane$1"
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
expected["providers"]["omniroute-fedora"]["models"] = {
    m: {"context_length": 98304}
    for m in ("agentfactory-build-local", "agentfactory-verify-local", "qwen-local/qwen3.8-27b-local")
}
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
check "create strips only the chain, adds the exact lane header and context override, preserves .env, and copies hooks/cron" $? \
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

# The disabled switch must produce exactly the standard rewrite's bytes: chain removal, header, context override.
reset_lane gateoff
LANE_DONE_GATE=0 bash "$HELPER" create gateoff >/dev/null; GATE_OFF_RC=$?
GATE_OFF="$PROFILES/aflanegateoff/config.yaml"
python3 - "$TMP/source-config.yaml" "$GATE_OFF" gateoff <<'PY'
from pathlib import Path
import re, sys
source, target, lane = Path(sys.argv[1]), Path(sys.argv[2]), sys.argv[3]
text = source.read_text()
lines = text.splitlines(keepends=True)
top = re.compile(r"^[A-Za-z_][A-Za-z0-9_-]*:")
def block(key):
    start = next((i for i, line in enumerate(lines) if line.startswith(key + ":")), None)
    if start is None: return None
    end = start + 1
    while end < len(lines) and not top.match(lines[end]): end += 1
    return start, end
span = block("fallback_providers")
if span: del lines[span[0]:span[1]]
model = block("model"); assert model
_, end = model
lines[end:end] = ["  default_headers:\n", f"    x-omniroute-session-id: {lane}\n"]
# The lane provider is the fixture's last block, so its models block is the file's new tail.
assert lines[-1] == "    discover_models: True\n", lines[-1]
lines += [
    "    models:\n",
    "      agentfactory-build-local:\n",
    "        context_length: 98304\n",
    "      agentfactory-verify-local:\n",
    "        context_length: 98304\n",
    "      qwen-local/qwen3.8-27b-local:\n",
    "        context_length: 98304\n",
]
assert target.read_bytes() == "".join(lines).encode()
PY
GATE_OFF_BYTES_RC=$?
[ "$GATE_OFF_RC" -eq 0 ] && [ "$GATE_OFF_BYTES_RC" -eq 0 ]
check "switch OFF leaves the clone byte-identical to the chain, header and context override rewrite" $? \
  "create_rc=$GATE_OFF_RC byte_compare_rc=$GATE_OFF_BYTES_RC"

# Enabled creation adds exactly one recorder and one pre_verify directive.
reset_lane gateon
LANE_DONE_GATE=1 bash "$HELPER" create gateon >/dev/null; GATE_ON_RC=$?
GATE_ON="$PROFILES/aflanegateon/config.yaml"
python3 - "$TMP/source-config.yaml" "$GATE_ON" "$(cd "$HERE/../../.." && pwd)" gateon <<'PY'
import copy, sys, yaml
source, target, root, lane = sys.argv[1:]
with open(source, encoding="utf-8") as f: before = yaml.safe_load(f)
with open(target, encoding="utf-8") as f: after = yaml.safe_load(f)
expected = copy.deepcopy(before)
expected.pop("fallback_providers", None)
expected["model"].setdefault("default_headers", {})["x-omniroute-session-id"] = lane
expected["providers"]["omniroute-fedora"]["models"] = {
    m: {"context_length": 98304}
    for m in ("agentfactory-build-local", "agentfactory-verify-local", "qwen-local/qwen3.8-27b-local")
}
helper = f"{root}/harness-ports/bin/lane-done-gate.py"
expected.setdefault("hooks", {}).setdefault("post_tool_call", []).append({
    "matcher": "terminal|patch|write_file", "command": f"python3 {helper} record", "timeout": 20,
})
expected["hooks"]["pre_verify"] = [{"command": f"python3 {helper} gate", "timeout": 20}]
assert after == expected, (after, expected)
PY
GATE_ON_SEM_RC=$?
# Verification accepts either the ordinary clone or exactly the two gate hooks,
# independent of the creation switch.
LANE_DONE_GATE=0 run_verify gateon
GATE_ON_VERIFY_OFF_RC=$VERIFY_RC; GATE_ON_VERIFY_OFF_OUT=$VERIFY_OUT
LANE_DONE_GATE=1 run_verify gateon
[ "$GATE_ON_RC" -eq 0 ] && [ "$GATE_ON_SEM_RC" -eq 0 ] \
  && [ "$GATE_ON_VERIFY_OFF_RC" -eq 0 ] && [ -z "$GATE_ON_VERIFY_OFF_OUT" ] \
  && [ "$VERIFY_RC" -eq 0 ] && [ -z "$VERIFY_OUT" ]
check "switch ON adds exactly the recorder and pre_verify entries and verify accepts them" $? \
  "create_rc=$GATE_ON_RC semantic_rc=$GATE_ON_SEM_RC verify_off_rc=$GATE_ON_VERIFY_OFF_RC verify_on_rc=$VERIFY_RC"

cp "$GATE_ON" "$TMP/gate-good.yaml"
python3 - "$GATE_ON" <<'PY'
import sys, yaml
p = sys.argv[1]
with open(p, encoding="utf-8") as f: data = yaml.safe_load(f)
data["hooks"]["post_tool_call"].append({"command": "true", "timeout": 20})
with open(p, "w", encoding="utf-8") as f: yaml.safe_dump(data, f, sort_keys=False)
PY
LANE_DONE_GATE=1 run_verify gateon
[ "$VERIFY_RC" -eq 64 ] && [ "$VERIFY_OUT" = 'lane-profile: unexpected semantic config delta' ]
check "verify refuses a third hook entry" $? "rc=$VERIFY_RC output=$VERIFY_OUT"
cp "$TMP/gate-good.yaml" "$GATE_ON"

python3 - "$GATE_ON" <<'PY'
import sys, yaml
p = sys.argv[1]
with open(p, encoding="utf-8") as f: data = yaml.safe_load(f)
data["hooks"]["pre_verify"][0]["command"] = data["hooks"]["pre_verify"][0]["command"].replace(
    "lane-done-gate.py gate", "lane-done-gate.py changed"
)
with open(p, "w", encoding="utf-8") as f: yaml.safe_dump(data, f, sort_keys=False)
PY
LANE_DONE_GATE=1 run_verify gateon
[ "$VERIFY_RC" -eq 64 ] && [ "$VERIFY_OUT" = 'lane-profile: unexpected semantic config delta' ]
check "verify refuses a changed done-gate command" $? "rc=$VERIFY_RC output=$VERIFY_OUT"

# HCTX1: each local lane model's context_length comes from the quadlet's MAX_LEN (98304 in the fixture).
override_values() {  # the sorted set of context_length values the three local models carry in one clone
  python3 - "$1" <<'PY' 2>/dev/null
import sys, yaml
with open(sys.argv[1], encoding="utf-8") as f: config = yaml.safe_load(f)
models = config["providers"]["omniroute-fedora"]["models"]
print(sorted({models[m]["context_length"] for m in (
    "agentfactory-build-local", "agentfactory-verify-local", "qwen-local/qwen3.8-27b-local")}))
PY
}
mutate_config() {  # config path, one python statement over `data`; re-emits the whole file as verify's other tests do
  python3 - "$1" "$2" <<'PY'
import sys, yaml
p, statement = sys.argv[1:]
with open(p, encoding="utf-8") as f: data = yaml.safe_load(f)
exec(statement)
with open(p, "w", encoding="utf-8") as f: yaml.safe_dump(data, f, sort_keys=False)
PY
}

reset_lane quadvalue
QUAD_OUT="$(bash "$HELPER" create quadvalue 2>"$TMP/quadvalue.err")"; QUAD_RC=$?
python3 - "$PROFILES/aflanequadvalue/config.yaml" <<'PY'
import sys, yaml
with open(sys.argv[1], encoding="utf-8") as f: config = yaml.safe_load(f)
models = config["providers"]["omniroute-fedora"]["models"]
assert models == {
    "agentfactory-build-local": {"context_length": 98304},
    "agentfactory-verify-local": {"context_length": 98304},
    "qwen-local/qwen3.8-27b-local": {"context_length": 98304},
}, models
assert all(type(settings["context_length"]) is int for settings in models.values())
assert "context_length" not in config["model"], config["model"]
PY
QUAD_SEM_RC=$?
[ "$QUAD_RC" -eq 0 ] && [ "$QUAD_OUT" = aflanequadvalue ] && [ ! -s "$TMP/quadvalue.err" ] && [ "$QUAD_SEM_RC" -eq 0 ]
check "create writes the quadlet's [Container] MAX_LEN as each local model's context_length under the lane provider" $? \
  "rc=$QUAD_RC stdout=$QUAD_OUT stderr_bytes=$(wc -c < "$TMP/quadvalue.err") models_rc=$QUAD_SEM_RC"

reset_lane fallback
FB_OUT="$(QWEN_QUADLET="$TMP/absent.container" bash "$HELPER" create fallback 2>"$TMP/fallback.err")"; FB_RC=$?
FB_WANT="lane-profile: context_length 131072: quadlet $TMP/absent.container unreadable (No such file or directory)"
FB_VALUES="$(override_values "$PROFILES/aflanefallback/config.yaml")"
QWEN_QUADLET="$TMP/absent.container" run_verify fallback
[ "$FB_RC" -eq 0 ] && [ "$FB_OUT" = aflanefallback ] && [ "$(cat "$TMP/fallback.err")" = "$FB_WANT" ] \
  && [ "$FB_VALUES" = '[131072]' ] && [ "$VERIFY_RC" -eq 0 ] && [ "$VERIFY_OUT" = "$FB_WANT" ]
check "an unreadable quadlet falls back to 131072 with exactly one stderr line naming why" $? \
  "rc=$FB_RC stdout=$FB_OUT stderr_lines=$(wc -l < "$TMP/fallback.err") values=$FB_VALUES verify_rc=$VERIFY_RC"

printf '[Container]\nEnvironment=PORT=8080\n[Service]\nEnvironment=MAX_LEN=4096\n' > "$TMP/nomax.container"
reset_lane nomaxlen
NM_OUT="$(QWEN_QUADLET="$TMP/nomax.container" bash "$HELPER" create nomaxlen 2>"$TMP/nomax.err")"; NM_RC=$?
NM_WANT="lane-profile: context_length 131072: no MAX_LEN= in the [Container] section of $TMP/nomax.container"
NM_VALUES="$(override_values "$PROFILES/aflanenomaxlen/config.yaml")"
[ "$NM_RC" -eq 0 ] && [ "$NM_OUT" = aflanenomaxlen ] && [ "$(cat "$TMP/nomax.err")" = "$NM_WANT" ] && [ "$NM_VALUES" = '[131072]' ]
check "a quadlet with no [Container] MAX_LEN falls back with its reason; a [Service] MAX_LEN is not the container's" $? \
  "rc=$NM_RC stdout=$NM_OUT stderr_lines=$(wc -l < "$TMP/nomax.err") values=$NM_VALUES"

BAD_FAILS=0; BAD_SEEN=""
refuse_case() {  # MAX_LEN text, the exact stderr expected; create must exit 64 before any clone
  local calls_before out rc
  printf '[Container]\nEnvironment=MAX_LEN=%s\n' "$1" > "$TMP/bad.container"
  calls_before="$(grep -c '^profile create ' "$FAKE_HERMES_CALLS")"
  out="$(QWEN_QUADLET="$TMP/bad.container" bash "$HELPER" create badvalue 2>"$TMP/bad.err")"; rc=$?
  if [ "$rc" -ne 64 ] || [ -n "$out" ] || [ "$(cat "$TMP/bad.err")" != "$2" ] || [ -e "$PROFILES/aflanebadvalue" ] \
    || [ "$(grep -c '^profile create ' "$FAKE_HERMES_CALLS")" != "$calls_before" ]; then
    BAD_FAILS=$((BAD_FAILS+1)); BAD_SEEN="$BAD_SEEN [$1]:rc=$rc"
  fi
  rm -rf "$PROFILES/aflanebadvalue"
}
for bad in 128k 0 00 -1 1.5 '' +131072 0x20000; do
  refuse_case "$bad" "lane-profile: quadlet MAX_LEN is not a positive integer: '$bad'"
done
refuse_case $'\xef\xbc\x91\xef\xbc\x93\xef\xbc\x91\xef\xbc\x90\xef\xbc\x97\xef\xbc\x92' \
  "lane-profile: quadlet MAX_LEN is not a positive integer: '\\uff11\\uff13\\uff11\\uff10\\uff17\\uff12'"
refuse_case '"131072' "lane-profile: quadlet $TMP/bad.container: an Environment= line does not parse"
[ "$BAD_FAILS" -eq 0 ]
check "create refuses a MAX_LEN that is not a positive integer, or an unparseable Environment= line, before cloning" $? \
  "10 cases failures=$BAD_FAILS$BAD_SEEN"

# systemd semantics: a backslash continues an Environment= line, and the last MAX_LEN assignment wins.
printf '[Container]\nEnvironment=MAX_LEN=4096\nEnvironment=PORT=8080 \\\n  MAX_LEN=106496\n' > "$TMP/continued.container"
reset_lane continued
CO_OUT="$(QWEN_QUADLET="$TMP/continued.container" bash "$HELPER" create continued 2>"$TMP/continued.err")"; CO_RC=$?
CO_VALUES="$(override_values "$PROFILES/aflanecontinued/config.yaml")"
[ "$CO_RC" -eq 0 ] && [ "$CO_OUT" = aflanecontinued ] && [ ! -s "$TMP/continued.err" ] && [ "$CO_VALUES" = '[106496]' ]
check "a backslash-continued Environment= line is read and the last MAX_LEN assignment wins" $? \
  "rc=$CO_RC stdout=$CO_OUT stderr_bytes=$(wc -c < "$TMP/continued.err") values=$CO_VALUES"

mkdir -p "$TMP/home/.config/containers/systemd"
printf '[Container]\nEnvironment=MAX_LEN=114688\n' > "$TMP/home/.config/containers/systemd/qwen.container"
reset_lane homepath
HP_OUT="$(env -u QWEN_QUADLET HOME="$TMP/home" bash "$HELPER" create homepath 2>"$TMP/homepath.err")"; HP_RC=$?
HP_VALUES="$(override_values "$PROFILES/aflanehomepath/config.yaml")"
[ "$HP_RC" -eq 0 ] && [ "$HP_OUT" = aflanehomepath ] && [ ! -s "$TMP/homepath.err" ] && [ "$HP_VALUES" = '[114688]' ]
check "with QWEN_QUADLET unset, create reads ~/.config/containers/systemd/qwen.container (the PC's quadlet path)" $? \
  "rc=$HP_RC stdout=$HP_OUT stderr_bytes=$(wc -c < "$TMP/homepath.err") values=$HP_VALUES"

# The premise's order (providers first), a models block already under the lane provider, and a second provider on
# another route: only the lane provider's models block and the header change; every other byte stays.
reset_lane modelskept
MK_OUT="$(HERMES_SOURCE_PROFILE=agentfactorymodels bash "$HELPER" create models-kept 2>&1)"; MK_RC=$?
cat > "$TMP/models-kept.expected" <<'YAML'
providers:
  omniroute-fedora:
    api: http://127.0.0.1:20128/v1
    name: OmniRoute Fedora
    key_env: OMNIROUTE_API_KEY
    models:
      some-cloud-model:
        context_length: 400000
      agentfactory-build-local:
        max_tokens: 8192
        context_length: 98304
      agentfactory-verify-local:
        context_length: 98304
      qwen-local/qwen3.8-27b-local:
        context_length: 98304
    default_model: auto/best-coding-fast
    # owner note outside the models block
    transport: openai_chat
    discover_models: True
  other-provider:
    api: http://127.0.0.1:9999/v1
    models:
      agentfactory-build-local:
        context_length: 777

model:
  default: auto/best-coding-fast
  provider: custom:omniroute-fedora
  base_url: http://127.0.0.1:20128/v1
  default_headers:
    x-omniroute-session-id: models-kept
compression:
  enabled: true
  threshold: 0.5
  target_ratio: 0.2
YAML
cmp -s "$TMP/models-kept.expected" "$PROFILES/aflanemodelskept/config.yaml"; MK_BYTES_RC=$?
HERMES_SOURCE_PROFILE=agentfactorymodels run_verify models-kept
[ "$MK_RC" -eq 0 ] && [ "$MK_OUT" = aflanemodelskept ] && [ "$MK_BYTES_RC" -eq 0 ] && [ "$VERIFY_RC" -eq 0 ] && [ -z "$VERIFY_OUT" ]
check "an existing models block keeps its other ids and settings, another route's provider is untouched, other bytes stay" $? \
  "rc=$MK_RC output=$MK_OUT byte_compare_rc=$MK_BYTES_RC verify_rc=$VERIFY_RC"

reset_lane noroute; reset_lane listmodels
NR_ERR="$(HERMES_SOURCE_PROFILE=agentfactorynoroute bash "$HELPER" create noroute 2>&1 >/dev/null)"; NR_RC=$?
LM_ERR="$(HERMES_SOURCE_PROFILE=agentfactorylist bash "$HELPER" create listmodels 2>&1 >/dev/null)"; LM_RC=$?
[ "$NR_RC" -eq 64 ] && [ "$NR_ERR" = $'config needs exactly one providers entry whose api is model.base_url\nlane-profile: config rewrite failed' ] \
  && [ "$LM_RC" -eq 64 ] && [ "$LM_ERR" = $'providers.omniroute-fedora.models must be a mapping\nlane-profile: config rewrite failed' ]
check "create refuses a base profile with no provider on the lanes' route, or with list-shaped models, with the reason" $? \
  "noroute_rc=$NR_RC listmodels_rc=$LM_RC"

reset_lane ctxverify
bash "$HELPER" create ctxverify >/dev/null; CV_RC=$?
CV_CONFIG="$PROFILES/aflanectxverify/config.yaml"; cp "$CV_CONFIG" "$TMP/ctxverify-good.yaml"
MODELS='data["providers"]["omniroute-fedora"]["models"]'
mutate_config "$CV_CONFIG" "del ${MODELS}['agentfactory-verify-local']"
run_verify ctxverify; MISS_ONE_RC=$VERIFY_RC; MISS_ONE_OUT=$VERIFY_OUT; cp "$TMP/ctxverify-good.yaml" "$CV_CONFIG"
mutate_config "$CV_CONFIG" "del data['providers']['omniroute-fedora']['models']"
run_verify ctxverify; MISS_ALL_RC=$VERIFY_RC; MISS_ALL_OUT=$VERIFY_OUT; cp "$TMP/ctxverify-good.yaml" "$CV_CONFIG"
[ "$CV_RC" -eq 0 ] \
  && [ "$MISS_ONE_RC" -eq 64 ] && [ "$MISS_ONE_OUT" = 'lane-profile: context override missing: agentfactory-verify-local' ] \
  && [ "$MISS_ALL_RC" -eq 64 ] && [ "$MISS_ALL_OUT" = 'lane-profile: context override missing: agentfactory-build-local' ]
check "verify rejects a clone missing the context override with the exact reason" $? \
  "one_id: rc=$MISS_ONE_RC $MISS_ONE_OUT | whole_block: rc=$MISS_ALL_RC $MISS_ALL_OUT"

mutate_config "$CV_CONFIG" "${MODELS}['qwen-local/qwen3.8-27b-local']['context_length'] = 200000"
run_verify ctxverify; WRONG_RC=$VERIFY_RC; WRONG_OUT=$VERIFY_OUT; cp "$TMP/ctxverify-good.yaml" "$CV_CONFIG"
mutate_config "$CV_CONFIG" "${MODELS}['agentfactory-build-local']['context_length'] = 98304.0"
run_verify ctxverify; FLOAT_RC=$VERIFY_RC; FLOAT_OUT=$VERIFY_OUT; cp "$TMP/ctxverify-good.yaml" "$CV_CONFIG"
printf '[Container]\nEnvironment=MAX_LEN=65536\n' > "$TMP/moved.container"
QWEN_QUADLET="$TMP/moved.container" run_verify ctxverify; MOVED_RC=$VERIFY_RC; MOVED_OUT=$VERIFY_OUT
run_verify ctxverify
[ "$WRONG_RC" -eq 64 ] && [ "$WRONG_OUT" = 'lane-profile: context override wrong: qwen-local/qwen3.8-27b-local=200000 (expected 98304)' ] \
  && [ "$FLOAT_RC" -eq 64 ] && [ "$FLOAT_OUT" = 'lane-profile: context override wrong: agentfactory-build-local=98304.0 (expected 98304)' ] \
  && [ "$MOVED_RC" -eq 64 ] && [ "$MOVED_OUT" = 'lane-profile: context override wrong: agentfactory-build-local=98304 (expected 65536)' ] \
  && [ "$VERIFY_RC" -eq 0 ] && [ -z "$VERIFY_OUT" ]
check "verify rejects another context_length, including one the quadlet no longer serves, with the exact reason" $? \
  "value: rc=$WRONG_RC | float: rc=$FLOAT_RC | quadlet_moved: rc=$MOVED_RC | restored: rc=$VERIFY_RC"

base_hashes > "$TMP/base-hashes.after"
cmp -s "$TMP/base-hashes.before" "$TMP/base-hashes.after"
check "no create, verify or remove in this suite wrote a base profile's config.yaml or .env" $? \
  "hashed_files=$(wc -l < "$TMP/base-hashes.before")"

echo; echo "lane profile: $pass passed, $fail failed"; [ "$fail" -eq 0 ]
