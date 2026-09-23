#!/usr/bin/env bash
# Create, verify, or remove the isolated Hermes profile used by one PC lane.
# The source interactive profile is read-only: lane profiles are disposable clones.
set -uo pipefail

fail() { printf 'lane-profile: %s\n' "$*" >&2; exit 64; }

ACTION="${1:-}"; VALUE="${2:-}"
[ -n "$ACTION" ] && [ -n "$VALUE" ] || fail "usage: lane-profile.sh create|verify|remove <lane-id-or-profile>"
[ "$#" -eq 2 ] || fail "usage: lane-profile.sh create|verify|remove <lane-id-or-profile>"

: "${HERMES_BIN:=hermes}"
: "${HERMES_PROFILES_DIR:=$HOME/.hermes/profiles}"
: "${HERMES_SOURCE_PROFILE:=agentfactory}"
SOURCE="$HERMES_PROFILES_DIR/$HERMES_SOURCE_PROFILE"

profile_name() {
  local lane clean
  lane="$1"
  clean="$(printf '%s' "$lane" | tr '[:upper:]' '[:lower:]' | tr -cd '[:alnum:]' | cut -c1-40)"
  [ -n "$clean" ] || fail "lane id has no alphanumeric characters"
  printf 'aflane%s\n' "$clean"
}

verify_lane() {
  local lane="$1" name target source_sha target_sha verdict rc
  name="$(profile_name "$lane")" || exit $?
  target="$HERMES_PROFILES_DIR/$name"
  [ -f "$target/config.yaml" ] && [ -f "$target/.env" ] || fail "profile missing $name"
  [ -f "$SOURCE/.env" ] || fail "source env missing"

  verdict="$(python3 - "$target/config.yaml" "$lane" <<'PY'
import sys
import yaml

path, lane = sys.argv[1:]
try:
    with open(path, encoding="utf-8") as stream:
        config = yaml.safe_load(stream)
except Exception:
    print("config unreadable")
    raise SystemExit(3)
if not isinstance(config, dict):
    print("config unreadable")
    raise SystemExit(3)
if "fallback_providers" in config:
    print("chain present")
    raise SystemExit(1)
model = config.get("model")
headers = model.get("default_headers") if isinstance(model, dict) else None
got = headers.get("x-omniroute-session-id") if isinstance(headers, dict) else None
if got != lane:
    print("header missing or wrong: " + ("<missing>" if got is None else str(got)))
    raise SystemExit(2)
PY
)"; rc=$?
  case "$rc" in
    0) ;;
    1) fail "chain present";;
    2) fail "$verdict";;
    *) fail "${verdict:-config unreadable}";;
  esac

  source_sha="$(sha256sum "$SOURCE/.env" 2>/dev/null | awk '{print $1}')"
  target_sha="$(sha256sum "$target/.env" 2>/dev/null | awk '{print $1}')"
  [ -n "$source_sha" ] && [ "$source_sha" = "$target_sha" ] || fail "env drift"
}

create_lane() {
  local lane="$1" name target component
  name="$(profile_name "$lane")" || exit $?
  target="$HERMES_PROFILES_DIR/$name"
  [ -f "$SOURCE/config.yaml" ] && [ -f "$SOURCE/.env" ] || fail "source profile missing $HERMES_SOURCE_PROFILE"

  if [ -e "$target" ]; then
    verify_lane "$lane"
    printf '%s\n' "$name"
    return 0
  fi

  "$HERMES_BIN" profile create --clone-from "$HERMES_SOURCE_PROFILE" --no-alias "$name" >/dev/null \
    || fail "clone failed $name"
  [ -f "$target/config.yaml" ] && [ -f "$target/.env" ] || fail "clone incomplete $name"

  # `--clone-from` omits some profile-local directories on Hermes releases that
  # otherwise copy config/.env. Add only source components that are actually absent.
  for component in hooks cron; do
    if [ -e "$SOURCE/$component" ] && [ ! -e "$target/$component" ]; then
      cp -a "$SOURCE/$component" "$target/$component" || fail "copy failed $component"
    fi
  done

  # Preserve every untouched byte in config.yaml. Parse before and after, and refuse
  # unless the semantic delta is exactly chain removal plus this lane's request header.
  python3 - "$target/config.yaml" "$lane" <<'PY' || fail "config rewrite failed"
import copy
import os
from pathlib import Path
import re
import sys
import tempfile
import yaml

path = Path(sys.argv[1])
lane = sys.argv[2]
text = path.read_text(encoding="utf-8")
before = yaml.safe_load(text)
if not isinstance(before, dict) or not isinstance(before.get("model"), dict):
    raise SystemExit("config must contain a model mapping")
expected = copy.deepcopy(before)
expected.pop("fallback_providers", None)
headers = expected["model"].get("default_headers")
if headers is None:
    headers = {}
    expected["model"]["default_headers"] = headers
if not isinstance(headers, dict):
    raise SystemExit("model.default_headers must be a mapping")
headers["x-omniroute-session-id"] = lane

lines = text.splitlines(keepends=True)
top = re.compile(r"^[A-Za-z_][A-Za-z0-9_-]*:")

def top_block(key):
    start = next((i for i, line in enumerate(lines) if line.startswith(key + ":")), None)
    if start is None:
        return None
    end = start + 1
    while end < len(lines) and not top.match(lines[end]):
        end += 1
    return start, end

fallback = top_block("fallback_providers")
if fallback is not None:
    del lines[fallback[0]:fallback[1]]

# Recompute block locations after deletion; stale indices can insert outside the
# model mapping when fallback_providers originally followed it.
model = top_block("model")
if model is None:
    raise SystemExit("model block missing")
model_start, model_end = model
header_scalar = yaml.safe_dump(lane, default_flow_style=True).strip()
if header_scalar.endswith("\n..."):
    header_scalar = header_scalar[:-4]
header_line = f"    x-omniroute-session-id: {header_scalar}\n"
default_start = next(
    (i for i in range(model_start + 1, model_end) if re.match(r"^  default_headers:\s*(?:#.*)?$", lines[i].rstrip("\n"))),
    None,
)
if default_start is None:
    lines[model_end:model_end] = ["  default_headers:\n", header_line]
else:
    default_end = default_start + 1
    while default_end < model_end and not re.match(r"^  [A-Za-z_][A-Za-z0-9_-]*:", lines[default_end]):
        default_end += 1
    existing = next(
        (i for i in range(default_start + 1, default_end) if re.match(r"^    x-omniroute-session-id:", lines[i])),
        None,
    )
    if existing is None:
        lines[default_end:default_end] = [header_line]
    else:
        lines[existing] = header_line

updated = "".join(lines)
after = yaml.safe_load(updated)
if after != expected:
    raise SystemExit("unexpected semantic config delta")
if set(before) - set(after) != ({"fallback_providers"} if "fallback_providers" in before else set()):
    raise SystemExit("unexpected removed top-level key")
if set(after) - set(before):
    raise SystemExit("unexpected added top-level key")

mode = path.stat().st_mode
fd, tmp_name = tempfile.mkstemp(prefix=path.name + ".", dir=path.parent)
try:
    with os.fdopen(fd, "w", encoding="utf-8") as stream:
        stream.write(updated)
        stream.flush()
        os.fsync(stream.fileno())
    os.chmod(tmp_name, mode)
    os.replace(tmp_name, path)
finally:
    if os.path.exists(tmp_name):
        os.unlink(tmp_name)
PY

  verify_lane "$lane"
  printf '%s\n' "$name"
}

remove_profile() {
  local name="$1"
  case "$name" in
    aflane*[!a-z0-9]*|aflane) fail "refusing to delete non-lane profile $name";;
    aflane*) ;;
    *) fail "refusing to delete non-lane profile $name";;
  esac
  printf '%s\n' "$name" | "$HERMES_BIN" profile delete "$name" >/dev/null \
    || fail "delete failed $name"
  [ ! -e "$HERMES_PROFILES_DIR/$name" ] || fail "delete left profile $name"
}

case "$ACTION" in
  create) create_lane "$VALUE";;
  verify) verify_lane "$VALUE";;
  remove) remove_profile "$VALUE";;
  *) fail "unknown action $ACTION";;
esac
