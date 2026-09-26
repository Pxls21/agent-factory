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
: "${QWEN_QUADLET:=$HOME/.config/containers/systemd/qwen.container}"
SOURCE="$HERMES_PROFILES_DIR/$HERMES_SOURCE_PROFILE"
# The local lane models (HCTX1): OmniRoute tells Hermes 200,000 for the two combos (128,000 for the raw node), but the
# vLLM behind them serves the quadlet's MAX_LEN, so each lane profile states that value per model.
CONTEXT_MODELS=(agentfactory-build-local agentfactory-verify-local qwen-local/qwen3.8-27b-local)

profile_name() {
  local lane clean
  lane="$1"
  clean="$(printf '%s' "$lane" | tr '[:upper:]' '[:lower:]' | tr -cd '[:alnum:]' | cut -c1-40)"
  [ -n "$clean" ] || fail "lane id has no alphanumeric characters"
  printf 'aflane%s\n' "$clean"
}

# The context the local model server really serves: MAX_LEN in the quadlet's [Container] section (systemd quoting and
# line continuation; the last assignment wins). Unreadable or unset: 131072 with one stderr line naming why. A value
# that is not a positive integer fails (never a silent guess). No message echoes another Environment= value.
quadlet_context_length() {
  python3 - "$QWEN_QUADLET" <<'PY'
import re
import shlex
import sys

path, fallback = sys.argv[1], 131072
try:
    with open(path, encoding="utf-8") as stream:
        text = stream.read()
except (OSError, UnicodeError) as exc:
    why = getattr(exc, "strerror", None) or type(exc).__name__
    sys.stderr.write(f"lane-profile: context_length {fallback}: quadlet {path} unreadable ({why})\n")
    print(fallback)
    raise SystemExit(0)
section, value = None, None
for line in (raw.strip() for raw in text.replace("\\\n", " ").splitlines()):
    if not line or line[0] in "#;":
        continue
    if line.startswith("[") and line.endswith("]"):
        section = line[1:-1]
        continue
    key, eq, assignments = line.partition("=")
    if section != "Container" or not eq or key.strip() != "Environment":
        continue
    try:
        words = shlex.split(assignments)
    except ValueError:
        sys.stderr.write(f"lane-profile: quadlet {path}: an Environment= line does not parse\n")
        raise SystemExit(64)
    for word in words:
        name, eq, assigned = word.partition("=")
        if eq and name == "MAX_LEN":
            value = assigned
if value is None:
    sys.stderr.write(f"lane-profile: context_length {fallback}: no MAX_LEN= in the [Container] section of {path}\n")
    print(fallback)
    raise SystemExit(0)
if not re.fullmatch(r"[0-9]+", value) or int(value) <= 0:
    sys.stderr.write(f"lane-profile: quadlet MAX_LEN is not a positive integer: {value[:40]!a}\n")
    raise SystemExit(64)
print(int(value))
PY
}

verify_lane() {
  local lane="$1" name target source_sha target_sha verdict rc
  name="$(profile_name "$lane")" || exit $?
  target="$HERMES_PROFILES_DIR/$name"
  [ -f "$target/config.yaml" ] && [ -f "$target/.env" ] || fail "profile missing $name"
  [ -f "$SOURCE/.env" ] || fail "source env missing"

  verdict="$(python3 - "$target/config.yaml" "$lane" "$SOURCE/config.yaml" "$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)" \
    "$CONTEXT_LENGTH" "${CONTEXT_MODELS[@]}" <<'PY'
import copy
import sys
import yaml

path, lane, source_path, root, context = sys.argv[1:6]
context_length, context_models = int(context), sys.argv[6:]


def lane_provider(conf):
    """The one providers entry whose api is model.base_url (the lanes' OmniRoute route), or None."""
    model, providers = conf.get("model"), conf.get("providers")
    url = str(model.get("base_url") or "").strip().rstrip("/") if isinstance(model, dict) else ""
    keys = [key for key, entry in providers.items() if isinstance(entry, dict)
            and str(entry.get("api") or "").strip().rstrip("/") == url] if url and isinstance(providers, dict) else []
    return keys[0] if len(keys) == 1 else None


def add_override(entry, model_ids, value):
    """Set models.<id>.context_length on one provider entry, keeping every other id and key. Returns a reason or None."""
    models = {} if entry.get("models") is None else entry["models"]
    if not isinstance(models, dict):
        return "models must be a mapping"
    for model_id in model_ids:
        settings = {} if models.get(model_id) is None else models[model_id]
        if not isinstance(settings, dict):
            return f"models.{model_id} must be a mapping"
        settings["context_length"] = value
        models[model_id] = settings
    entry["models"] = models
    return None


try:
    with open(path, encoding="utf-8") as stream:
        config = yaml.safe_load(stream)
    with open(source_path, encoding="utf-8") as stream:
        source = yaml.safe_load(stream)
except Exception:
    print("config unreadable")
    raise SystemExit(3)
if not isinstance(config, dict) or not isinstance(source, dict):
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
provider = lane_provider(source)
if provider is None:
    print("source needs exactly one providers entry whose api is model.base_url")
    raise SystemExit(3)
entry = config.get("providers", {}).get(provider) if isinstance(config.get("providers"), dict) else None
models = entry.get("models") if isinstance(entry, dict) else None
for model_id in context_models:
    settings = models.get(model_id) if isinstance(models, dict) else None
    got = settings.get("context_length") if isinstance(settings, dict) else None
    if got is None:
        print(f"context override missing: {model_id}")
        raise SystemExit(2)
    if type(got) is not int or got != context_length:
        print(f"context override wrong: {model_id}={got!r} (expected {context_length})")
        raise SystemExit(2)

expected = copy.deepcopy(source)
expected.pop("fallback_providers", None)
expected.setdefault("model", {}).setdefault("default_headers", {})["x-omniroute-session-id"] = lane
reason = add_override(expected["providers"][provider], context_models, context_length)
if reason:
    print(f"providers.{provider}.{reason}")
    raise SystemExit(3)
helper = f"{root}/harness-ports/bin/lane-done-gate.py"
record = {
    "matcher": "terminal|patch|write_file",
    "command": f"python3 {helper} record",
    "timeout": 20,
}
gate = {"command": f"python3 {helper} gate", "timeout": 20}
expected_gate = copy.deepcopy(expected)
expected_gate.setdefault("hooks", {}).setdefault("post_tool_call", []).append(record)
expected_gate["hooks"]["pre_verify"] = [gate]
if config not in (expected, expected_gate):
    print("unexpected semantic config delta")
    raise SystemExit(3)
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
  # unless the semantic delta is exactly chain removal, this lane's request header,
  # the local models' context_length under the lane provider, and, when enabled, the
  # two lane done-gate hooks.
  python3 - "$target/config.yaml" "$lane" "${LANE_DONE_GATE:-0}" "$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)" \
    "$CONTEXT_LENGTH" "${CONTEXT_MODELS[@]}" <<'PY' || fail "config rewrite failed"
import copy
import os
from pathlib import Path
import re
import sys
import tempfile
import yaml

path = Path(sys.argv[1])
lane = sys.argv[2]
gate_enabled = sys.argv[3] == "1"
root = Path(sys.argv[4])
context_length, context_models = int(sys.argv[5]), sys.argv[6:]


def lane_provider(conf):
    """The one providers entry whose api is model.base_url (the lanes' OmniRoute route), or None."""
    model, providers = conf.get("model"), conf.get("providers")
    url = str(model.get("base_url") or "").strip().rstrip("/") if isinstance(model, dict) else ""
    keys = [key for key, entry in providers.items() if isinstance(entry, dict)
            and str(entry.get("api") or "").strip().rstrip("/") == url] if url and isinstance(providers, dict) else []
    return keys[0] if len(keys) == 1 else None


def add_override(entry, model_ids, value):
    """Set models.<id>.context_length on one provider entry, keeping every other id and key. Returns a reason or None."""
    models = {} if entry.get("models") is None else entry["models"]
    if not isinstance(models, dict):
        return "models must be a mapping"
    for model_id in model_ids:
        settings = {} if models.get(model_id) is None else models[model_id]
        if not isinstance(settings, dict):
            return f"models.{model_id} must be a mapping"
        settings["context_length"] = value
        models[model_id] = settings
    entry["models"] = models
    return None


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
provider = lane_provider(expected)
if provider is None:
    raise SystemExit("config needs exactly one providers entry whose api is model.base_url")
reason = add_override(expected["providers"][provider], context_models, context_length)
if reason:
    raise SystemExit(f"providers.{provider}.{reason}")
if gate_enabled:
    helper = root / "harness-ports" / "bin" / "lane-done-gate.py"
    hooks = expected.setdefault("hooks", {})
    if not isinstance(hooks, dict):
        raise SystemExit("hooks must be a mapping")
    post = hooks.setdefault("post_tool_call", [])
    if not isinstance(post, list):
        raise SystemExit("hooks.post_tool_call must be a list")
    if "pre_verify" in hooks:
        raise SystemExit("source profile already has hooks.pre_verify")
    post.append({
        "matcher": "terminal|patch|write_file",
        "command": f"python3 {helper} record",
        "timeout": 20,
    })
    hooks["pre_verify"] = [{
        "command": f"python3 {helper} gate",
        "timeout": 20,
    }]

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

# The context override goes after the lane provider's last line, or re-emits that
# provider's existing models block (other ids and settings kept); the semantic
# equality guard below rejects any collateral change.
def indent(i):
    return len(lines[i]) - len(lines[i].lstrip(" "))

span = top_block("providers")
rows = [] if span is None else [
    i for i in range(span[0] + 1, span[1]) if lines[i].strip() and not lines[i].lstrip().startswith("#")
]
key_line = re.compile(r" *(?:%s):\s*(?:#.*)?$" % "|".join(re.escape(q % provider) for q in ("%s", "'%s'", '"%s"')))
head = next((i for i in rows if indent(i) == indent(rows[0]) and key_line.match(lines[i])), None)
body = []
for i in rows:
    if head is not None and i > head:
        if indent(i) <= indent(head):
            break
        body.append(i)
if not body:
    raise SystemExit(f"providers.{provider} is not a block mapping")
child = indent(body[0])
rendered = yaml.safe_dump(
    {"models": expected["providers"][provider]["models"]},
    default_flow_style=False, sort_keys=False, allow_unicode=True,
)
block = [" " * child + row for row in rendered.splitlines(keepends=True)]
models_at = next((i for i in body if indent(i) == child and lines[i].lstrip().startswith("models:")), None)
if models_at is None:
    if "models" in before["providers"][provider]:
        raise SystemExit(f"providers.{provider}.models is not a block key")
    if not lines[body[-1]].endswith("\n"):
        lines[body[-1]] += "\n"
    lines[body[-1] + 1:body[-1] + 1] = block
else:
    last = models_at
    for i in body:
        if i > models_at:
            if indent(i) <= child:
                break
            last = i
    lines[models_at:last + 1] = block

if gate_enabled:
    helper = root / "harness-ports" / "bin" / "lane-done-gate.py"
    # The source profile has no pre_verify today. Appending at EOF preserves all
    # existing bytes and puts the recorder after existing post_tool_call entries.
    hook_block = yaml.safe_dump(
        {
            "hooks": {
                "post_tool_call": [{
                    "matcher": "terminal|patch|write_file",
                    "command": f"python3 {helper} record",
                    "timeout": 20,
                }],
                "pre_verify": [{
                    "command": f"python3 {helper} gate",
                    "timeout": 20,
                }],
            }
        },
        sort_keys=False,
        allow_unicode=True,
    )
    current = yaml.safe_load("".join(lines))
    current_hooks = current.get("hooks") if isinstance(current, dict) else None
    if current_hooks is None:
        lines.append(hook_block)
    else:
        # Preserve the existing hooks mapping through a targeted block rewrite;
        # the semantic equality guard below rejects any collateral change.
        hook_span = top_block("hooks")
        if hook_span is None or not isinstance(current_hooks, dict):
            raise SystemExit("hooks block unreadable")
        current_hooks.setdefault("post_tool_call", []).append({
            "matcher": "terminal|patch|write_file",
            "command": f"python3 {helper} record",
            "timeout": 20,
        })
        current_hooks["pre_verify"] = [{
            "command": f"python3 {helper} gate",
            "timeout": 20,
        }]
        replacement = yaml.safe_dump(
            {"hooks": current_hooks}, sort_keys=False, allow_unicode=True
        )
        lines[hook_span[0]:hook_span[1]] = [replacement]

updated = "".join(lines)
after = yaml.safe_load(updated)
if after != expected:
    raise SystemExit("unexpected semantic config delta")
removed = {"fallback_providers"} if "fallback_providers" in before else set()
added = {"hooks"} if gate_enabled and "hooks" not in before else set()
if set(before) - set(after) != removed:
    raise SystemExit("unexpected removed top-level key")
if set(after) - set(before) != added:
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

# Resolved once per run: create's own verify reuses it, so a fallback prints one line.
case "$ACTION" in
  create) CONTEXT_LENGTH="$(quadlet_context_length)" || exit $?; create_lane "$VALUE";;
  verify) CONTEXT_LENGTH="$(quadlet_context_length)" || exit $?; verify_lane "$VALUE";;
  remove) remove_profile "$VALUE";;
  *) fail "unknown action $ACTION";;
esac
