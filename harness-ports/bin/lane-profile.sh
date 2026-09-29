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
# LANE_CONTEXT_ENGINE (task #365, H1; docs/HARNESS-PORTS.md §7 "LCM-X lane mode"). Unset or empty: every profile this
# script writes is byte-identical to the rule above. lcm-x: the profile also gets the LCM-X plugin pinned in
# pc-lane.lock.yaml (lane_context_plugins.hermes-lcm-x; D-110), its engine, and lcm-x.env, the settings pc-lane.sh exports
# to the lane's hermes; verify checks all of it. Any other value fails.
ENGINE="${LANE_CONTEXT_ENGINE:-}"
case "$ENGINE" in
  ''|lcm-x) ;;
  *) fail "unknown LANE_CONTEXT_ENGINE (lcm-x, or unset): $(printf '%s' "$ENGINE" | head -c 40)";;
esac
: "${LCM_X_DIR:=$HOME/lcm-x}"
: "${LCM_X_DEPS_DIR:=$HOME/lcm-x-deps}"
: "${LCM_X_TIKTOKEN_DIR:=$HOME/lcm-x-tiktoken}"
# The tools that can reach another session's rows (the tool-by-tool read is in docs/HARNESS-PORTS.md §7).
LCM_X_TOOLS_OFF="lcm_grep,lcm_recall,lcm_load_session,lcm_describe,lcm_expand,lcm_expand_query,lcm_evidence_pack"
LCM_X_TOOLS_OFF="$LCM_X_TOOLS_OFF,lcm_compile_evidence,lcm_compute,lcm_query_state,lcm_retrieve,lcm_doctor"

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

# lcm-x mode only. The paths go into lcm-x.env as they are, and the lane's hermes runs in the lane tree, so each must
# be absolute and one line; PYTHONPATH splits on ':'.
lcm_x_paths_ok() {
  local v
  for v in LCM_X_DIR LCM_X_DEPS_DIR LCM_X_TIKTOKEN_DIR HERMES_PROFILES_DIR; do
    case "${!v}" in /*) ;; *) fail "lcm-x: $v is not an absolute path";; esac
    case "${!v}" in *$'\n'*) fail "lcm-x: $v holds a newline";; esac
  done
  case "$LCM_X_DEPS_DIR" in *:*) fail "lcm-x: LCM_X_DEPS_DIR holds a ':' (the PYTHONPATH separator)";; esac
}

# The exact bytes of <profile>/lcm-x.env: the settings pc-lane.sh gives the lane's hermes process as environment. Never
# written into the profile's .env, which Hermes loads with override=True (hermes_cli/env_loader.py:349-350 at b3399c1).
lcm_x_settings() {
  printf 'LCM_DISABLED_TOOLS=%s\nLCM_DATABASE_PATH=%s\nLCM_EMBEDDINGS_ENABLED=false\nTIKTOKEN_CACHE_DIR=%s\nPYTHONPATH=%s\n' \
    "$LCM_X_TOOLS_OFF" "$1/lcm.db" "$LCM_X_TIKTOKEN_DIR" "$LCM_X_DEPS_DIR"
}

# lcm-x mode only: the plugin link and the settings file, each written only when it differs (a relaunch writes none).
lcm_x_install() {
  local target="$1" name="$2" link tmp
  if [ -L "$target/plugins" ] || { [ -e "$target/plugins" ] && [ ! -d "$target/plugins" ]; }; then
    fail "lcm-x (a): $name/plugins is not a real directory"
  fi
  mkdir -p "$target/plugins" || fail "lcm-x (a): cannot create $name/plugins"
  link="$target/plugins/hermes-lcm-x"
  if [ -L "$link" ]; then
    [ "$(readlink "$link")" = "$LCM_X_DIR" ] || ln -sfn "$LCM_X_DIR" "$link" \
      || fail "lcm-x (a): cannot repoint $name/plugins/hermes-lcm-x"
  elif [ -e "$link" ]; then
    fail "lcm-x (a): $name/plugins/hermes-lcm-x exists and is not a symlink"
  else
    ln -s "$LCM_X_DIR" "$link" || fail "lcm-x (a): cannot link $name/plugins/hermes-lcm-x"
  fi
  [ ! -L "$target/lcm-x.env" ] || fail "lcm-x (c): $name/lcm-x.env is a symlink"
  if ! cmp -s <(lcm_x_settings "$target") "$target/lcm-x.env"; then
    tmp="$(mktemp "$target/lcm-x.env.XXXXXX")" || fail "lcm-x (c): cannot write $name/lcm-x.env"
    { lcm_x_settings "$target" > "$tmp" && mv -f "$tmp" "$target/lcm-x.env"; } \
      || { rm -f "$tmp"; fail "lcm-x (c): cannot write $name/lcm-x.env"; }
  fi
}

# Conditions a to d of task #365 (D-108 item 7); each failure names its item. The pins come from pc-lane.lock.yaml.
verify_lcm_x() {
  local target="$1" verdict rc
  verdict="$(python3 - "$target" "$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)" "$LCM_X_DIR" "$LCM_X_DEPS_DIR" \
    "$LCM_X_TIKTOKEN_DIR" "$HERMES_BIN" "${LCM_X_PYTHON:-}" "$(lcm_x_settings "$target")" <<'PY'
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import yaml

target, root, plugin_dir, deps_dir, tokenizer_dir, hermes_bin, lane_python, settings = sys.argv[1:9]
settings += "\n"  # the shell's $(...) dropped the file's final newline
plugin_name, engine_name = "hermes-lcm-x", "lcm-x"  # plugin_identity.py:24-25 at the pin


def refuse(item, why):
    print(f"lcm-x ({item}): {why}")
    raise SystemExit(2)


def git(*args):
    try:
        done = subprocess.run(["git", "-C", plugin_dir, *args], capture_output=True, text=True, timeout=30,
                              env={**os.environ, "GIT_OPTIONAL_LOCKS": "0"})
    except (OSError, subprocess.SubprocessError) as exc:
        refuse("a", f"git in LCM_X_DIR failed: {type(exc).__name__}")
    if done.returncode != 0:
        refuse("a", f"git {args[0]} in LCM_X_DIR failed (rc {done.returncode})")
    return done.stdout


def dotenv_names(path):
    """KEY names a dotenv file assigns, by Hermes's own scanner (hermes_cli/env_loader.py:49-68); values are never kept."""
    try:
        text = open(path, encoding="utf-8", errors="replace").read()
    except OSError:
        return set()
    names = set()
    for line in text.splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            name = line.removeprefix("export ").split("=", 1)[0].strip()
            if name:
                names.add(name)
    return names


# The pins: pc-lane.lock.yaml (D-110: the PC-lane tool pins, never upstream.lock.yaml), lane_context_plugins.hermes-lcm-x.
# Never a second copy.
try:
    with open(os.path.join(root, "pc-lane.lock.yaml"), encoding="utf-8") as stream:
        pin = yaml.safe_load(stream)["lane_context_plugins"]["hermes-lcm-x"]
    revision = pin["revision"]
    runtime = {entry["name"]: entry for entry in pin["runtime_imports"]}
    tokenizer = pin["tokenizer"]
    cache_file, tokenizer_digest = tokenizer["cache_file"], tokenizer["digest"]
except Exception:
    refuse("a", "pc-lane.lock.yaml has no readable lane_context_plugins.hermes-lcm-x entry")
if not re.fullmatch(r"[0-9a-f]{40}", str(revision)):
    refuse("a", "the lock's revision is not 40 lowercase hex")
if cache_file != hashlib.sha1(str(tokenizer["url"]).encode()).hexdigest():
    refuse("c", "the lock's tokenizer cache_file is not sha1(url) (tiktoken/load.py:51)")

# (a) The plugin: <profile>/plugins/hermes-lcm-x is a symlink to LCM_X_DIR, a clean clone at the lock's revision.
plugins = os.path.join(target, "plugins")
link = os.path.join(plugins, plugin_name)
if os.path.islink(plugins) or not os.path.isdir(plugins):
    refuse("a", "the profile's plugins directory is missing or a symlink")
if not os.path.islink(link):
    refuse("a", f"plugins/{plugin_name} is not a symlink to LCM_X_DIR")
if os.readlink(link) != plugin_dir:
    refuse("a", f"plugins/{plugin_name} points somewhere other than LCM_X_DIR")
for child in sorted(os.listdir(plugins)):
    manifest = os.path.join(plugins, child, "plugin.yaml")
    if child != plugin_name and os.path.isfile(manifest):
        try:
            other = (yaml.safe_load(open(manifest, encoding="utf-8")) or {}).get("name")
        except Exception:
            other = None
        if other in (plugin_name, "hermes-lcm"):
            refuse("a", f"plugins/{child} is a second LCM plugin ({other})")
try:
    with open(os.path.join(plugin_dir, "plugin.yaml"), encoding="utf-8") as stream:
        manifest_name = (yaml.safe_load(stream) or {}).get("name")
except Exception:
    manifest_name = None
if manifest_name != plugin_name:
    refuse("a", f"LCM_X_DIR has no plugin.yaml naming {plugin_name}")
head = git("rev-parse", "HEAD").strip()
if head != revision:
    refuse("a", f"LCM_X_DIR is at {head[:12] or '<none>'}, not the lock's revision {revision[:12]}")
if git("status", "--porcelain", "--untracked-files=all").strip():
    refuse("a", "LCM_X_DIR has changes against its revision")

# (b) The config: plugins.enabled lists the plugin, plugins.disabled does not, context.engine is the engine, and
# compression is not off (Hermes calls the engine only when it is on, agent/agent_init.py:1860).
try:
    with open(os.path.join(target, "config.yaml"), encoding="utf-8") as stream:
        config = yaml.safe_load(stream)
except Exception:
    refuse("b", "config.yaml unreadable")
config = config if isinstance(config, dict) else {}
plugin_cfg = config.get("plugins") if isinstance(config.get("plugins"), dict) else {}
enabled, disabled = plugin_cfg.get("enabled"), plugin_cfg.get("disabled")
if not isinstance(enabled, list) or plugin_name not in enabled:
    refuse("b", f"plugins.enabled does not list {plugin_name}")
if isinstance(disabled, list) and plugin_name in disabled:
    refuse("b", f"plugins.disabled lists {plugin_name}, and the deny-list wins")
context = config.get("context")
engine = context.get("engine") if isinstance(context, dict) else None
if engine != engine_name:
    refuse("b", f"context.engine is {'absent' if engine is None else repr(engine)[:40]}, not {engine_name}")
compression = config.get("compression")
if isinstance(compression, dict) and compression.get("enabled") is False:
    refuse("b", "compression.enabled is false, so Hermes never calls the engine")

# (c) The settings: lcm-x.env holds exactly the expected lines, .env sets none of them, the tokenizer file is the
# pinned one, and the runtime imports come from LCM_X_DEPS_DIR under the Python the lane's hermes runs on.
settings_path = os.path.join(target, "lcm-x.env")
if os.path.islink(settings_path) or not os.path.isfile(settings_path):
    refuse("c", "lcm-x.env is missing or a symlink")
got = open(settings_path, encoding="utf-8", errors="replace").read()
want_pairs = dict(line.split("=", 1) for line in settings.splitlines())
got_pairs = {}
for line in got.splitlines():
    key, eq, value = line.partition("=")
    if not eq or key not in want_pairs or key in got_pairs:
        refuse("c", f"lcm-x.env has an unexpected line: {key[:40]}")
    got_pairs[key] = value
left_on = sorted(set(want_pairs["LCM_DISABLED_TOOLS"].split(",")) - set(got_pairs.get("LCM_DISABLED_TOOLS", "").split(",")))
if left_on:
    refuse("c", f"a cross-session tool is left on: {','.join(left_on)}")
for key in want_pairs:
    if got_pairs.get(key) != want_pairs[key]:
        refuse("c", f"lcm-x.env sets {key} {'to another value' if key in got_pairs else 'nowhere'}")
if got != settings:
    refuse("c", "lcm-x.env differs from the expected bytes")
shadowed = sorted(name for name in dotenv_names(os.path.join(target, ".env"))
                  if name.startswith("LCM_") or name == "TIKTOKEN_CACHE_DIR")
if shadowed:
    refuse("c", f"the profile's .env sets {', '.join(shadowed)}, and Hermes loads it with override=True")
cache_path = os.path.join(tokenizer_dir, cache_file)
if not os.path.isfile(cache_path):
    refuse("c", f"the tokenizer file {cache_file} is absent from LCM_X_TIKTOKEN_DIR")
with open(cache_path, "rb") as stream:
    if "sha256:" + hashlib.sha256(stream.read()).hexdigest() != tokenizer_digest:
        refuse("c", f"the tokenizer file {cache_file} is altered (sha256 differs from the lock)")
if not lane_python:
    found = shutil.which(hermes_bin)
    first = b""
    if found:
        with open(os.path.realpath(found), "rb") as stream:
            first = stream.readline(512)
    words = first[2:].decode("utf-8", "replace").split() if first.startswith(b"#!") else []
    if words and os.path.basename(words[0]) == "env":
        words = words[1:]
        while words and words[0].startswith("-"):  # env's own options (-S); the interpreter's follow its name
            words = words[1:]
    if not words or not os.path.basename(words[0]).startswith("python"):
        refuse("c", "HERMES_BIN is not a Python script, so its interpreter is unknown; set LCM_X_PYTHON")
    if any(word.startswith("-") and not word.startswith("--") and set(word[1:]) & set("IE") for word in words[1:]):
        refuse("c", "HERMES_BIN's interpreter runs with -I or -E, which ignore PYTHONPATH")
    lane_python = words[0] if "/" in words[0] else (shutil.which(words[0]) or words[0])
probe = (
    "import json, os, sys\n"
    "sys.modules['requests'] = None  # a cache miss fails here instead of downloading (tiktoken/load.py:15)\n"
    "sys.modules['blobfile'] = None\n"
    "import importlib.metadata as metadata\n"
    "import tiktoken\n"
    "tiktoken.get_encoding('cl100k_base').encode('lcm-x verify')\n"
    "print(json.dumps({'file': os.path.realpath(tiktoken.__file__), 'version': metadata.version('tiktoken')}))\n"
)
inherited = os.environ.get("PYTHONPATH", "")
env = {**os.environ, "PYTHONPATH": deps_dir + (":" + inherited if inherited else ""),
       "TIKTOKEN_CACHE_DIR": tokenizer_dir, "PYTHONDONTWRITEBYTECODE": "1"}
try:
    done = subprocess.run([lane_python, "-c", probe], capture_output=True, text=True, timeout=120, env=env)
except (OSError, subprocess.SubprocessError) as exc:
    refuse("c", f"the lane's Python {lane_python} did not run: {type(exc).__name__}")
try:
    seen = json.loads(done.stdout.strip().splitlines()[-1]) if done.returncode == 0 else None
except (ValueError, IndexError):
    seen = None
why = (done.stderr.strip().splitlines() or ["no output"])[-1][:160]
if seen is None:
    refuse("c", f"tiktoken does not import and load cl100k_base from LCM_X_DEPS_DIR under {lane_python}: {why}")
deps_real = os.path.realpath(deps_dir) + os.sep
if not seen["file"].startswith(deps_real):
    refuse("c", "tiktoken imports from outside LCM_X_DEPS_DIR under the lane's Python")
if seen["version"] != str(runtime["tiktoken"]["version"]):
    refuse("c", f"tiktoken {seen['version'][:20]} is in LCM_X_DEPS_DIR, not the lock's {runtime['tiktoken']['version']}")

# (d) Summaries through OmniRoute only. LCM-X calls call_llm(task="compression") with no provider (escalation.py:303-340
# at the pin); with auxiliary.compression on auto that is the main OmniRoute route, and on a failure Hermes walks the task's
# fallback_chain, then fallback_providers and fallback_model, then the discovery chain (agent/auxiliary_client.py:
# 4195-4220, 6835-6908 at b3399c1). The first three must be absent; the discovery chain's credentials are reported by
# name, never by value.
if config.get("fallback_providers") or config.get("fallback_model"):
    refuse("d", "a fallback_providers or fallback_model entry would carry a summary off OmniRoute")
auxiliary = config.get("auxiliary")
task = auxiliary.get("compression") if isinstance(auxiliary, dict) else None
if task is not None and not isinstance(task, dict):
    refuse("d", "auxiliary.compression is not a mapping")
task = task or {}
if str(task.get("provider") or "auto").strip().lower() != "auto":
    refuse("d", "auxiliary.compression.provider is not auto (the main OmniRoute route)")
for key in ("base_url", "api_key", "fallback_chain"):
    if task.get(key):
        refuse("d", f"auxiliary.compression.{key} is set")
main_route = json.dumps(config.get("providers"), default=str) + json.dumps(config.get("model"), default=str)
credential = re.compile(r"[A-Z0-9_]+(?:_API_KEY|_TOKEN|_KEY_ID|_ACCESS_KEY|_SECRET_KEY|_CREDENTIALS)|AWS_PROFILE")
names = {"the profile's .env": dotenv_names(os.path.join(target, ".env")), "the environment": set(os.environ)}
report = []
for where, found in names.items():
    other = sorted(n for n in found if credential.fullmatch(n) and n not in main_route)
    if other:
        report.append(f"{where}: {', '.join(other)}")
if os.path.exists(os.path.join(target, "auth.json")):
    report.append("auth.json (stored provider logins)")
print("lcm-x (d) note: credentials the auxiliary fallback chain can reach: " + ("; ".join(report) or "none found"),
      file=sys.stderr)
PY
)"; rc=$?
  [ "$rc" -eq 0 ] || fail "${verdict:-lcm-x: verify failed}"
}

verify_lane() {
  local lane="$1" name target source_sha target_sha verdict rc
  name="$(profile_name "$lane")" || exit $?
  target="$HERMES_PROFILES_DIR/$name"
  [ -f "$target/config.yaml" ] && [ -f "$target/.env" ] || fail "profile missing $name"
  [ -f "$SOURCE/.env" ] || fail "source env missing"
  [ "$ENGINE" != lcm-x ] || verify_lcm_x "$target"

  verdict="$(python3 - "$target/config.yaml" "$lane" "$SOURCE/config.yaml" "$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)" \
    "$ENGINE" "$CONTEXT_LENGTH" "${CONTEXT_MODELS[@]}" <<'PY'
import copy
import sys
import yaml

path, lane, source_path, root, engine, context = sys.argv[1:7]
context_length, context_models = int(context), sys.argv[7:]


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
if engine == "lcm-x":  # the create rule's two keys; every other key stays the source's
    for conf in (expected, expected_gate):
        plugins = {} if conf.get("plugins") is None else conf["plugins"]
        context = {} if conf.get("context") is None else conf["context"]
        enabled = plugins.get("enabled") if isinstance(plugins, dict) else None
        enabled = [] if enabled is None else enabled
        if not isinstance(plugins, dict) or not isinstance(context, dict) or not isinstance(enabled, list):
            print("source plugins, plugins.enabled or context has the wrong shape")
            raise SystemExit(3)
        plugins["enabled"] = enabled + [name for name in ["hermes-lcm-x"] if name not in enabled]
        context["engine"] = "lcm-x"
        conf["plugins"], conf["context"] = plugins, context
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
  local lane="$1" name target component from
  name="$(profile_name "$lane")" || exit $?
  target="$HERMES_PROFILES_DIR/$name"
  [ -f "$SOURCE/config.yaml" ] && [ -f "$SOURCE/.env" ] || fail "source profile missing $HERMES_SOURCE_PROFILE"

  if [ -e "$target" ]; then
    # A relaunch reuses the lane's profile. Its config.yaml is re-derived from the SOURCE by
    # the same rule as a new clone (below), so a profile cut under an older rule or from an
    # older source gets the current one; state.db, .env and every other file stay as they
    # are. A symlink counts as not a directory: the rewrite must never land where it points.
    [ -d "$target" ] && [ ! -L "$target" ] || fail "profile not a directory $name"
    [ -f "$target/config.yaml" ] || fail "profile has no config.yaml $name"
    from="$SOURCE/config.yaml"
  else
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
    from="$target/config.yaml"
  fi

  # Rewrite config.yaml from $from, preserving every untouched byte of it. Parse before and
  # after, and refuse unless the semantic delta is exactly chain removal, this lane's request
  # header, the local models' context_length under the lane provider, and, when enabled, the
  # two lane done-gate hooks and the lcm-x engine's two keys. A result equal to the lane's
  # current bytes is not written.
  python3 - "$from" "$target/config.yaml" "$lane" "${LANE_DONE_GATE:-0}" "$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)" \
    "$ENGINE" "$CONTEXT_LENGTH" "${CONTEXT_MODELS[@]}" <<'PY' || fail "config rewrite failed"
import copy
import os
from pathlib import Path
import re
import sys
import tempfile
import yaml

# The text to rewrite (a new clone's own copy, or on a relaunch the source profile's), and the lane's config.yaml.
src, path = Path(sys.argv[1]), Path(sys.argv[2])
lane = sys.argv[3]
gate_enabled = sys.argv[4] == "1"
root = Path(sys.argv[5])
lcm_x = sys.argv[6] == "lcm-x"
context_length, context_models = int(sys.argv[7]), sys.argv[8:]


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


text = src.read_text(encoding="utf-8")
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
if lcm_x:
    # Hermes b3399c1 loads a user plugin only when plugins.enabled names it (hermes_cli/plugins_discovery.py:213,
    # plugins.disabled wins at 192) and selects the engine from context.engine (agent/agent_init.py:1746-1752).
    plugins = {} if expected.get("plugins") is None else expected["plugins"]
    context = {} if expected.get("context") is None else expected["context"]
    enabled = plugins.get("enabled") if isinstance(plugins, dict) else None
    enabled = [] if enabled is None else enabled
    if not isinstance(plugins, dict) or not isinstance(context, dict) or not isinstance(enabled, list):
        raise SystemExit("lcm-x needs plugins and context to be mappings and plugins.enabled a list")
    if isinstance(plugins.get("disabled"), list) and "hermes-lcm-x" in plugins["disabled"]:
        raise SystemExit("plugins.disabled lists hermes-lcm-x, and the deny-list wins")
    plugins["enabled"] = enabled + [name for name in ["hermes-lcm-x"] if name not in enabled]
    context["engine"] = "lcm-x"
    expected["plugins"], expected["context"] = plugins, context

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

if lcm_x:
    # Re-emit (or append) the two top-level blocks the lcm-x rule changes; trailing blank and comment lines stay
    # outside the re-emitted block. The semantic equality guard below rejects any collateral change.
    for key in ("plugins", "context"):
        rendered = yaml.safe_dump({key: expected[key]}, default_flow_style=False, sort_keys=False, allow_unicode=True)
        span = top_block(key)
        if span is None:
            if lines and not lines[-1].endswith("\n"):
                lines[-1] += "\n"
            lines.append(rendered)
        else:
            start, end = span
            while end > start + 1 and (not lines[end - 1].strip() or lines[end - 1].lstrip().startswith("#")):
                end -= 1
            lines[start:end] = [rendered]

updated = "".join(lines)
after = yaml.safe_load(updated)
if after != expected:
    raise SystemExit("unexpected semantic config delta")
removed = {"fallback_providers"} if "fallback_providers" in before else set()
added = {"hooks"} if gate_enabled and "hooks" not in before else set()
if lcm_x:
    added |= {key for key in ("plugins", "context") if key not in before}
if set(before) - set(after) != removed:
    raise SystemExit("unexpected removed top-level key")
if set(after) - set(before) != added:
    raise SystemExit("unexpected added top-level key")
if path.read_bytes() == updated.encode("utf-8"):
    raise SystemExit(0)  # already current (a second create): nothing is written

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

  [ "$ENGINE" != lcm-x ] || lcm_x_install "$target" "$name"
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

# lcm-x mode: the paths are checked before create or verify clones or writes anything.
case "$ACTION" in create|verify) [ "$ENGINE" != lcm-x ] || lcm_x_paths_ok;; esac
# Resolved once per run: create's own verify reuses it, so a fallback prints one line.
case "$ACTION" in
  create) CONTEXT_LENGTH="$(quadlet_context_length)" || exit $?; create_lane "$VALUE";;
  verify) CONTEXT_LENGTH="$(quadlet_context_length)" || exit $?; verify_lane "$VALUE";;
  remove) remove_profile "$VALUE";;
  *) fail "unknown action $ACTION";;
esac
