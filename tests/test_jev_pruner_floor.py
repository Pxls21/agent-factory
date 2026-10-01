"""T408 (task #408, D-118 item 2): the vendored pruner hook's `minTokensFloor` option, and the copy as an installable
plugin. Deterministic and LLM-free; nothing leaves the process.

The hook is the REAL module, vendor/jev-pruner/hooks/fast-jev-output.ts. Node's type stripping runs its TypeScript and
the src/*.ts it imports. The test drives it through its own exports: `resolveHookConfig` (the option resolution) and
`register` (the entry). Its Bash handler runs with a fake `$`: `http.fetch` counts the call and throws, and `fs` is a map.

Two gates hold the threshold. Gate 1 is the handler's own check: its diagnostics line reads `below_threshold` at stage
`read_output`. Gate 2 is trimOutput's check (src/output.ts trimOutputAttempt). A pass-through wrapper around the real
trimOutput records the options the handler passed it. The real trimOutput then runs gate 2 on every output of the case
with those options, so the two gates are compared on both sides of the threshold.

The manifests (.claude-plugin/plugin.json and marketplace.json) are the upstream files of commit 47d017c (their git blob
ids below) plus the local changes vendor/jev-pruner/PROVENANCE.md lists. `claude plugin validate` must accept them where
the CLI runs here, in a network namespace of its own with a HOME of its own.
"""
from __future__ import annotations

import hashlib
import json
import math
import re
import shutil
import subprocess
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
VENDOR = REPO / "vendor" / "jev-pruner"
HOOK = VENDOR / "hooks" / "fast-jev-output.ts"
PLUGIN_JSON = VENDOR / ".claude-plugin" / "plugin.json"
MARKETPLACE_JSON = VENDOR / ".claude-plugin" / "marketplace.json"

UPSTREAM_FLOOR = 10_000  # MIN_OUTPUT_TOKENS at 47d017c (src/output.ts:7)
# git blob ids at 47d017c (`git ls-tree -r 47d017c` in the upstream checkout; PROVENANCE.md "Added 2026-09-30")
UPSTREAM_PLUGIN_JSON_BLOB = "db3a0b1ed98aaae664a4c2ac8c5143c9d2c0b3d6"
UPSTREAM_MARKETPLACE_JSON_BLOB = "6b3748fc216ab50a65eccdbbad4197dd2b2a147b"
UPSTREAM_NAME = "fast-jev-output"  # the plugin's and the marketplace's upstream name; the owner has it installed
UPSTREAM_MIN_TOKENS_DESCRIPTION = (
    "Stdout at or below this estimated token count passes through untouched. Minimum: 10000."
)
PLUGIN_NAME, MARKETPLACE_NAME = "fast-jev-output-floor", "agent-factory-vendor"
CHANGE_3_OPTIONS = ("baseUrl", "archiveDir", "decisionsDir")  # PROVENANCE.md local change 3
CHANGE_4_OPTIONS = ("historyTokens",)  # PROVENANCE.md local change 4
# PROVENANCE.md local change 4: our copy's version, raised so `claude plugin update` installs a new landing
UPSTREAM_VERSION, OUR_VERSION = "0.1.0", "0.1.1"
UPSTREAM_SYSTEM_ONE_URL = "https://api.typesafe.ai/v1/systemone"  # src/jev.ts:1 at 47d017c
UPSTREAM_ARCHIVE_DIR = ".claude/fast-jev-output"  # hooks/fast-jev-output.ts ARCHIVE_DIR at 47d017c

NAN, INF = float("nan"), float("inf")
# name: (plugin options, resolved (minTokensFloor, minTokens), {estimated output tokens: passes the threshold})
CASES = {
    "no_option": ({}, (10_000, 10_000), {9_999: False, 10_000: False, 10_001: True}),
    "floor_500_min_600": ({"minTokensFloor": 500, "minTokens": 600}, (500, 600),
                          {500: False, 550: False, 600: False, 601: True}),
    "min_under_the_floor": ({"minTokensFloor": 500, "minTokens": 100}, (500, 500),
                            {101: False, 300: False, 500: False, 501: True}),
    "floor_0_min_0": ({"minTokensFloor": 0, "minTokens": 0}, (0, 0), {0: False, 60: True}),
    # The documented fallback: a floor that is not a finite number of at least 0 counts as unset (10,000).
    "negative_floor": ({"minTokensFloor": -1, "minTokens": 600}, (10_000, 10_000),
                       {601: False, 10_000: False, 10_001: True}),
    "nan_floor": ({"minTokensFloor": NAN, "minTokens": 600}, (10_000, 10_000), {601: False, 10_001: True}),
    "infinite_floor": ({"minTokensFloor": INF, "minTokens": 600}, (10_000, 10_000), {601: False, 10_001: True}),
    "minus_infinite_floor": ({"minTokensFloor": -INF, "minTokens": 600}, (10_000, 10_000),
                             {601: False, 10_001: True}),
}


def _node_strips_types() -> bool:
    try:
        probe = subprocess.run(
            ["node", "-e", "process.stdout.write(String(Boolean(process.features && process.features.typescript)))"],
            capture_output=True, text=True, timeout=30)
    except OSError:
        return False
    return probe.stdout.strip() == "true"


# Loading the hook needs a Node that strips TypeScript types (22.18 or later). Where it cannot, the hook tests SKIP with
# this reason; the manifest tests still run.
needs_strip = pytest.mark.skipif(not _node_strips_types(),
                                 reason="this Node cannot strip TypeScript types (22.18 or later can)")

DRIVER = r"""
import { register } from 'node:module';
import { pathToFileURL } from 'node:url';

const input = [];
for await (const chunk of process.stdin) input.push(chunk);
const job = JSON.parse(Buffer.concat(input).toString('utf8'), (key, value) =>
  value !== null && typeof value === 'object' && typeof value.$number === 'string' ? Number(value.$number) : value);

const hookUrl = pathToFileURL(job.hook).href;
const rootUrl = new URL('../', hookUrl).href;
const outputUrl = new URL('src/output.ts', rootUrl).href;
// A pass-through wrapper around the real trimOutput: it records the options the handler passes, then calls it unchanged.
const wrapperUrl = 'data:text/javascript,' + encodeURIComponent([
  `import { trimOutput as realTrimOutput } from ${JSON.stringify(outputUrl)};`,
  `export * from ${JSON.stringify(outputUrl)};`,
  'export async function trimOutput(input, asker, options) {',
  '  globalThis.t408TrimCalls.push(options);',
  '  return realTrimOutput(input, asker, options);',
  '}',
].join('\n'));
// The vendored TypeScript imports '../src/X.js' and './X.js'. The engine's host resolves them to the .ts sources
// (`claude plugin validate` reports `cannot import "../src/jev.js"` when src/ is gone); this does the same.
register('data:text/javascript,' + encodeURIComponent([
  `const HOOK = ${JSON.stringify(hookUrl)}, ROOT = ${JSON.stringify(rootUrl)}, WRAPPER = ${JSON.stringify(wrapperUrl)};`,
  'export async function resolve(specifier, context, next) {',
  "  if (context.parentURL === HOOK && specifier === '../src/output.js') return { url: WRAPPER, shortCircuit: true };",
  "  if (context.parentURL && context.parentURL.startsWith(ROOT) && (specifier.startsWith('./') || specifier.startsWith('../'))",
  "      && specifier.endsWith('.js')) return next(specifier.slice(0, -3) + '.ts', context);",
  '  return next(specifier, context);',
  '}',
].join('\n')));

globalThis.t408TrimCalls = [];
const hook = await import(hookUrl);
const output = await import(outputUrl);
const { estimateTokens } = await import(new URL('src/jev.ts', rootUrl).href);

const show = (v) => (v === undefined ? 'absent' : typeof v === 'number' && !Number.isFinite(v) ? String(v) : v);
const text = (n) => Array.from({ length: n }, () => 'aaaaaa').join('\n');  // one estimated token per line
const apiKey = ['t408', 'fake', String(process.pid)].join('-');  // built at run time; the fake fetch drops it
const results = [];
for (const c of job.cases) {
  const resolved = hook.resolveHookConfig(c.options);
  const registered = [];
  let handler;
  await hook.register((name, matcher, fn) => { registered.push([name, matcher]); handler = fn; },
    { ...c.options, diagnostics: true, apiKey });
  const first = globalThis.t408TrimCalls.length;
  const runs = [];
  for (const tokens of c.tokens) {
    const stdout = text(tokens);
    const logs = [];
    const files = new Map();
    let fetches = 0;
    const $ = {
      fs: {
        read: async () => { throw new Error('t408: no persisted output in this test'); },
        exists: async (path) => files.has(path),
        write: async (path, data) => { files.set(path, data); },
      },
      env: { get: async () => undefined },
      settings: { read: async () => ({}) },
      session: { messages: async () => [] },
      http: { fetch: async () => { fetches += 1; throw new Error('t408: the scorer was reached; nothing is sent'); } },
      ui: { log: (line) => { logs.push(line); }, toast: () => {} },
    };
    const answer = { result: { stdout, stderr: '' } };
    const before = globalThis.t408TrimCalls.length;
    const back = await handler($, { command: 'make fixture', tool_use_id: `toolu_t408_${c.name}_${tokens}` },
      async () => answer);
    const line = logs.find((l) => l.startsWith('fast-jev-output decision '));
    const diagnostics = line ? JSON.parse(line.slice('fast-jev-output decision '.length)) : {};
    runs.push({
      tokens, estimated: estimateTokens(stdout), decision: diagnostics.decision ?? null, stage: diagnostics.stage ?? null,
      fetches, trimCalls: globalThis.t408TrimCalls.length - before, returnedUnchanged: back === answer,
    });
  }
  const passed = globalThis.t408TrimCalls.slice(first);
  if (passed.length > 0) {
    // Gate 2 on every output of the case: the real trimOutput, with the options the handler itself passed it.
    const { onDecision, ...options } = passed[0];
    for (const run of runs) {
      let decision = null;
      let asked = 0;
      const asker = { async ask() { asked += 1; throw new Error('t408: gate 2 passed, the scorer was asked'); } };
      try {
        await output.trimOutput({ command: 'make fixture', goal: '', output: text(run.tokens) }, asker,
          { ...options, onDecision: (d) => { decision = d; } });
      } catch (error) {
        if (asked === 0) throw error;
      }
      run.gate2 = { decision, asked };
    }
  }
  results.push({
    name: c.name, registered,
    resolved: { minTokens: show(resolved.minTokens), minTokensFloor: show(resolved.minTokensFloor) },
    trimOptions: passed.map((o) => ({ minTokens: show(o.minTokens), minTokensFloor: show(o.minTokensFloor) })),
    runs,
  });
}
console.log(JSON.stringify({ node: process.version, MIN_OUTPUT_TOKENS: output.MIN_OUTPUT_TOKENS, results }));
"""


def _for_node(value):
    """JSON has no NaN or Infinity: send a non-finite float as {"$number": <JavaScript's own spelling>}."""
    if isinstance(value, float) and not math.isfinite(value):
        return {"$number": "NaN" if math.isnan(value) else ("Infinity" if value > 0 else "-Infinity")}
    if isinstance(value, dict):
        return {key: _for_node(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_for_node(item) for item in value]
    return value


@pytest.fixture(scope="module")
def hook_runs():
    job = {"hook": str(HOOK),
           "cases": [{"name": name, "options": options, "tokens": sorted(passes)}
                     for name, (options, _, passes) in CASES.items()]}
    proc = subprocess.run(["node", "--input-type=module", "-e", DRIVER],
                          input=json.dumps(_for_node(job), allow_nan=False),
                          capture_output=True, text=True, timeout=180, cwd=REPO)
    assert proc.returncode == 0, proc.stderr[-4000:]
    return json.loads(proc.stdout.strip().splitlines()[-1])


def _gate1_passed(run: dict) -> bool:
    return not (run["decision"] == "below_threshold" and run["stage"] == "read_output")


def _case_problems(name: str, result: dict) -> list[str]:
    _, (floor, min_tokens), passes = CASES[name]
    problems = []
    if result["registered"] != [["tool.call", {"tool": "Bash"}]]:
        problems.append(f"register() added {result['registered']}, not one tool.call hook on Bash")
    for run in result["runs"]:
        tokens, expected, gate1 = run["tokens"], passes[run["tokens"]], _gate1_passed(run)
        if run["estimated"] != tokens:
            problems.append(f"the {tokens}-token fixture is estimated at {run['estimated']} tokens")
        if gate1 != expected:
            problems.append(f"gate 1 {'passed' if gate1 else 'held back'} a {tokens}-token output, expected it "
                            f"{'passed' if expected else 'held back'} (decision={run['decision']}, stage={run['stage']})")
        if gate1 and (run["trimCalls"] != 1 or run["decision"] == "below_threshold" or run["fetches"] < 1):
            problems.append(f"gate 2 held back a {tokens}-token output that gate 1 passed (trimCalls={run['trimCalls']}, "
                            f"decision={run['decision']}, stage={run['stage']}, fetches={run['fetches']})")
        if not gate1 and (run["trimCalls"] or run["fetches"] or not run["returnedUnchanged"]):
            problems.append(f"a {tokens}-token output held back at gate 1 still went on (trimCalls={run['trimCalls']}, "
                            f"fetches={run['fetches']}, returnedUnchanged={run['returnedUnchanged']})")
    resolved = result["resolved"]
    if (resolved["minTokensFloor"], resolved["minTokens"]) != (floor, min_tokens):
        problems.append(f"resolveHookConfig gave minTokensFloor={resolved['minTokensFloor']} "
                        f"minTokens={resolved['minTokens']}, expected {floor} and {min_tokens}")
    if not result["trimOptions"]:
        problems.append("no output reached trimOutput, so gate 2 was not compared with gate 1")
    for options in result["trimOptions"]:
        if (options["minTokensFloor"], options["minTokens"]) != (floor, min_tokens):
            problems.append(f"the handler passed trimOutput minTokensFloor={options['minTokensFloor']} "
                            f"minTokens={options['minTokens']}, expected {floor} and {min_tokens}")
    for run in result["runs"]:
        if "gate2" in run and (run["gate2"]["decision"] != "below_threshold") != _gate1_passed(run):
            problems.append(f"the gates disagree on a {run['tokens']}-token output: gate 1 "
                            f"{'passed' if _gate1_passed(run) else 'held it back'}, gate 2 decided {run['gate2']}")
    return problems


@needs_strip
@pytest.mark.parametrize("name", list(CASES))
def test_hook_floor_case(name, hook_runs):
    """Each case through the hook's option resolution, its handler (gate 1) and trimOutput's gate (gate 2)."""
    result = next(r for r in hook_runs["results"] if r["name"] == name)
    problems = _case_problems(name, result)
    assert problems == [], f"{name}: " + "; ".join(problems)


@needs_strip
def test_the_driver_loads_the_vendored_typescript(hook_runs):
    """The threshold constant comes from the vendored src/output.ts itself, and every case ran."""
    assert hook_runs["MIN_OUTPUT_TOKENS"] == UPSTREAM_FLOOR
    assert [r["name"] for r in hook_runs["results"]] == list(CASES)
    assert sum(len(r["runs"]) for r in hook_runs["results"]) == sum(len(p) for _, _, p in CASES.values())


def _git_blob_id(data: bytes) -> str:
    return hashlib.sha1(b"blob %d\0" % len(data) + data).hexdigest()


def test_plugin_manifest_is_the_upstream_one_plus_the_local_changes():
    """Undo the documented local changes and the upstream bytes come back (git blob id at 47d017c)."""
    text = PLUGIN_JSON.read_text()
    manifest = json.loads(text)
    config = manifest["userConfig"]
    floor = config["minTokensFloor"]
    assert set(floor) == {"type", "title", "description", "default", "min"}
    assert (floor["type"], floor["default"], floor["min"]) == ("number", UPSTREAM_FLOOR, 0)
    assert floor["title"].strip() and floor["description"].strip()
    assert list(config).index("minTokensFloor") == list(config).index("minTokens") + 1
    assert config["minTokens"]["default"] == UPSTREAM_FLOOR
    description = config["minTokens"]["description"]
    assert "minTokensFloor" in description and description != UPSTREAM_MIN_TOKENS_DESCRIPTION
    # local changes 3 and 4: three string options, then one number option with no default, in this order, between
    # maxScoringRequests and model
    names = list(config)
    assert names[names.index("maxScoringRequests") + 1:names.index("model")] == [*CHANGE_3_OPTIONS, *CHANGE_4_OPTIONS]
    for name, kind, change in [*((n, "string", 3) for n in CHANGE_3_OPTIONS), *((n, "number", 4) for n in CHANGE_4_OPTIONS)]:
        assert set(config[name]) == {"type", "title", "description"} and config[name]["type"] == kind
        assert config[name]["title"].strip() and f"local change {change}" in config[name]["description"]
    assert manifest["name"] == PLUGIN_NAME != UPSTREAM_NAME

    upstream = text
    for name in ("minTokensFloor", *CHANGE_3_OPTIONS, *CHANGE_4_OPTIONS):
        blocks = re.findall(r'^    "' + name + r'": \{\n(?:      .*\n)+?    \},\n', upstream, re.M)
        assert len(blocks) == 1, name
        upstream = upstream.replace(blocks[0], "")
    assert upstream.count(json.dumps(description)) == 1
    upstream = upstream.replace(json.dumps(description), json.dumps(UPSTREAM_MIN_TOKENS_DESCRIPTION))
    assert upstream.count(f'"name": "{PLUGIN_NAME}"') == 1
    upstream = upstream.replace(f'"name": "{PLUGIN_NAME}"', f'"name": "{UPSTREAM_NAME}"')
    assert manifest["version"] == OUR_VERSION and upstream.count(f'"version": "{OUR_VERSION}"') == 1
    upstream = upstream.replace(f'"version": "{OUR_VERSION}"', f'"version": "{UPSTREAM_VERSION}"')
    assert _git_blob_id(upstream.encode()) == UPSTREAM_PLUGIN_JSON_BLOB


def _plugin_path_problems(marketplace_root: Path, entry: dict) -> list[str]:
    """What is wrong with one marketplace entry's plugin path: it must hold the plugin the entry names."""
    plugin_root = (marketplace_root / entry["source"]).resolve()
    manifest_path = plugin_root / ".claude-plugin" / "plugin.json"
    if not manifest_path.is_file():
        return [f"{entry['name']}: no plugin manifest at {manifest_path}"]
    manifest = json.loads(manifest_path.read_text())
    problems = [f"{entry['name']}: the manifest there says {key}={manifest.get(key)!r}"
                for key in ("name", "version") if manifest.get(key) != entry[key]]
    hooks = json.loads((plugin_root / "hooks" / "hooks.json").read_text())
    problems += [f"{entry['name']}: hook module {module} is missing"
                 for module in hooks["modules"] if not (plugin_root / "hooks" / module).is_file()]
    return problems


def test_marketplace_is_the_upstream_one_renamed_and_names_a_plugin_path_that_exists():
    text = MARKETPLACE_JSON.read_text()
    marketplace = json.loads(text)
    assert marketplace["name"] == MARKETPLACE_NAME
    assert [entry["name"] for entry in marketplace["plugins"]] == [PLUGIN_NAME]
    # both names differ from the owner's fast-jev-output@fast-jev-output, so the two install side by side
    assert UPSTREAM_NAME not in (MARKETPLACE_NAME, PLUGIN_NAME)

    root = MARKETPLACE_JSON.parent.parent  # the marketplace root holds .claude-plugin/
    for entry in marketplace["plugins"]:
        assert _plugin_path_problems(root, entry) == []
    # the negative control: the same check refuses a path that holds no plugin
    missing = dict(marketplace["plugins"][0], source="./no-such-plugin")
    assert _plugin_path_problems(root, missing) == [f"{PLUGIN_NAME}: no plugin manifest at "
                                                    f"{(root / 'no-such-plugin').resolve() / '.claude-plugin' / 'plugin.json'}"]

    for name in (MARKETPLACE_NAME, PLUGIN_NAME):
        assert text.count(f'"name": "{name}"') == 1
    upstream = text.replace(f'"name": "{MARKETPLACE_NAME}"', f'"name": "{UPSTREAM_NAME}"')
    upstream = upstream.replace(f'"name": "{PLUGIN_NAME}"', f'"name": "{UPSTREAM_NAME}"')
    assert upstream.count(f'"version": "{OUR_VERSION}"') == 1
    upstream = upstream.replace(f'"version": "{OUR_VERSION}"', f'"version": "{UPSTREAM_VERSION}"')
    assert _git_blob_id(upstream.encode()) == UPSTREAM_MARKETPLACE_JSON_BLOB


def _offline_cli_unavailable() -> str | None:
    if shutil.which("claude") is None:
        return "the claude CLI is not on PATH"
    try:
        probe = subprocess.run(["unshare", "--net", "true"], capture_output=True, timeout=30)
    except OSError as error:
        return f"unshare cannot run: {error}"
    if probe.returncode != 0:
        return "this user cannot make a network namespace (unshare --net), so the CLI would run with the network"
    return None


def _validate(path: Path, home: Path) -> dict:
    """`claude plugin validate --json` in a network namespace of its own, with a HOME of its own and no inherited env."""
    home.mkdir(parents=True, exist_ok=True)
    env = {"PATH": str(Path(shutil.which("claude")).parent) + ":/usr/local/bin:/usr/bin:/bin", "HOME": str(home),
           "CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC": "1", "DISABLE_TELEMETRY": "1", "DISABLE_AUTOUPDATER": "1"}
    proc = subprocess.run(["unshare", "--net", "claude", "plugin", "validate", "--json", str(path)],
                          capture_output=True, text=True, timeout=120, env=env)
    report = json.loads(proc.stdout)
    assert (proc.returncode == 0) == report["success"], (proc.returncode, proc.stderr[-2000:])
    return report


def _errors(report: dict) -> list[str]:
    return [error["message"] for part in [report["manifest"], *report["contents"]] for error in part["errors"]]


def test_claude_cli_validates_the_plugin_and_the_marketplace(tmp_path):
    reason = _offline_cli_unavailable()
    if reason:
        pytest.skip(f"claude plugin validate not run: {reason}; the JSON checks above still hold")
    plugin = _validate(PLUGIN_JSON, tmp_path / "home")
    assert plugin["success"] and plugin["manifest"]["type"] == "plugin" and _errors(plugin) == [], _errors(plugin)
    notes = [note for part in plugin["contents"] if part["type"] == "hooks" for note in part["notes"]]
    assert "./fast-jev-output.ts hooks: tool.call{tool=Bash}" in notes  # the validator loaded the changed module
    marketplace = _validate(MARKETPLACE_JSON, tmp_path / "home")
    assert (marketplace["success"] and marketplace["manifest"]["type"] == "marketplace"
            and _errors(marketplace) == []), _errors(marketplace)

    # negative controls, on a copy of the plugin's load closure: the validator refuses a key the schema lacks
    # ("minimum"; the schema's bound is "min") and a hook module whose import closure is broken.
    copy = tmp_path / "copy"
    for part in (".claude-plugin", "hooks", "src"):
        shutil.copytree(VENDOR / part, copy / part)
    manifest = json.loads(PLUGIN_JSON.read_text())
    manifest["userConfig"]["minTokensFloor"]["minimum"] = manifest["userConfig"]["minTokensFloor"].pop("min")
    (copy / ".claude-plugin" / "plugin.json").write_text(json.dumps(manifest, indent=2) + "\n")
    refused = _validate(copy / ".claude-plugin" / "plugin.json", tmp_path / "home")
    assert not refused["success"] and _errors(refused) == ['Unrecognized key: "minimum"']
    (copy / ".claude-plugin" / "plugin.json").write_text(PLUGIN_JSON.read_text())
    (copy / "src" / "history.ts").unlink()
    broken = _validate(copy / ".claude-plugin" / "plugin.json", tmp_path / "home")
    # since local change 4 the hook imports src/history.ts itself, so the validator names the hook's own import
    assert not broken["success"] and any('cannot import "../src/history.js" (from hooks/fast-jev-output.ts)' in error
                                         for error in _errors(broken))


# Local change 3 (PROVENANCE.md): the scorer's URL, the archive folder and the decision records, through the real hook.
DRIVER3 = r"""
import { register } from 'node:module';
import { pathToFileURL } from 'node:url';

const input = [];
for await (const chunk of process.stdin) input.push(chunk);
const job = JSON.parse(Buffer.concat(input).toString('utf8'));
const hookUrl = pathToFileURL(job.hook).href;
const rootUrl = new URL('../', hookUrl).href;
register('data:text/javascript,' + encodeURIComponent([
  `const ROOT = ${JSON.stringify(rootUrl)};`,
  'export async function resolve(specifier, context, next) {',
  "  if (context.parentURL && context.parentURL.startsWith(ROOT) && (specifier.startsWith('./') || specifier.startsWith('../'))",
  "      && specifier.endsWith('.js')) return next(specifier.slice(0, -3) + '.ts', context);",
  '  return next(specifier, context);',
  '}',
].join('\n')));

const hook = await import(hookUrl);
const text = (n) => Array.from({ length: n }, () => 'aaaaaa').join('\n');  // one estimated token per line
const apiKey = ['c3', 'fake', String(process.pid)].join('-');  // built at run time; the fake fetch drops it
const results = [];
for (const c of job.cases) {
  let handler;
  await hook.register((name, matcher, fn) => { handler = fn; }, { ...c.options, apiKey });
  const files = new Map();
  const urls = [];
  const $ = {
    fs: {
      read: async () => { throw new Error('c3: no persisted output in this test'); },
      exists: async (path) => files.has(path),
      write: async (path, data) => {
        if (c.failRecordWrites && path.startsWith(String(c.options.decisionsDir) + '/')) throw new Error('c3: record write');
        files.set(path, data);
      },
    },
    env: { get: async () => undefined },
    settings: { read: async () => ({}) },
    session: { messages: async () => [] },
    http: { fetch: async (url) => { urls.push(url); throw new Error('c3: the scorer was reached; nothing is sent'); } },
    ui: { log: () => {}, toast: () => {} },
  };
  const answer = { result: { stdout: text(c.tokens), stderr: '' } };
  const back = await handler($, { command: 'make fixture', tool_use_id: c.toolUseId }, async () => answer);
  results.push({ name: c.name, urls, files: Object.fromEntries(files), returnedUnchanged: back === answer });
}
console.log(JSON.stringify({ results }));
"""

RELAY_URL = "http://127.0.0.1:9/v1/systemone"  # port 9 (discard): never reached, the fake fetch throws first
CHANGE_3_CASES = [
    {"name": "upstream_defaults", "options": {"minTokensFloor": 0, "minTokens": 0}, "tokens": 60,
     "toolUseId": "toolu_c3_a"},
    {"name": "all_three_set", "options": {"minTokensFloor": 0, "minTokens": 0, "baseUrl": RELAY_URL,
                                          "archiveDir": "scratch/arch", "decisionsDir": "scratch/dec"},
     "tokens": 60, "toolUseId": "toolu_c3:b"},
    {"name": "below_the_floor", "options": {"decisionsDir": "scratch/dec"}, "tokens": 60, "toolUseId": "toolu_c3_c"},
    {"name": "record_write_fails", "options": {"minTokensFloor": 0, "minTokens": 0, "decisionsDir": "scratch/dec"},
     "tokens": 60, "toolUseId": "toolu_c3_d", "failRecordWrites": True},
]


@pytest.fixture(scope="module")
def change3_runs():
    job = {"hook": str(HOOK), "cases": CHANGE_3_CASES}
    proc = subprocess.run(["node", "--input-type=module", "-e", DRIVER3], input=json.dumps(job),
                          capture_output=True, text=True, timeout=180, cwd=REPO)
    assert proc.returncode == 0, proc.stderr[-4000:]
    return {r["name"]: r for r in json.loads(proc.stdout.strip().splitlines()[-1])["results"]}


@needs_strip
def test_change3_unset_options_keep_the_upstream_url_and_archive(change3_runs):
    run = change3_runs["upstream_defaults"]
    assert run["urls"] and set(run["urls"]) == {UPSTREAM_SYSTEM_ONE_URL}
    assert sorted(run["files"]) == [f"{UPSTREAM_ARCHIVE_DIR}/.gitignore", f"{UPSTREAM_ARCHIVE_DIR}/bash-toolu_c3_a.txt"]


@needs_strip
def test_change3_options_move_the_url_the_archive_and_write_the_records(change3_runs):
    run = change3_runs["all_three_set"]
    assert run["urls"] and set(run["urls"]) == {RELAY_URL}
    archive = sorted(path for path in run["files"] if path.startswith("scratch/arch/"))
    assert archive == ["scratch/arch/.gitignore", "scratch/arch/bash-toolu_c3:b.txt"]
    assert not any(path.startswith(UPSTREAM_ARCHIVE_DIR) for path in run["files"])
    records = sorted(path for path in run["files"] if path.startswith("scratch/dec/"))
    assert len(records) == 2 and records[1] == "scratch/dec/last.json", records
    assert re.fullmatch(r"scratch/dec/(\d{4}-\d{2}-\d{2})/\1T\d{9}Z-toolu_c3_b\.json", records[0]), records[0]
    line = run["files"]["scratch/dec/last.json"]
    assert run["files"][records[0]] == line and line.endswith("\n") and line.count("\n") == 1
    record = json.loads(line)
    assert record["toolUseId"] == "toolu_c3:b" and record["sourceEstimatedTokens"] == 60
    assert record["decision"] not in ("below_threshold", "missing_key") and record["requests"] >= 1
    assert record["at"][:10] == records[0][len("scratch/dec/"):][:10]
    assert "aaaaaa" not in line and "fixture" not in line  # counts only: never the output or the command


@needs_strip
def test_change3_a_call_below_the_floor_writes_the_heartbeat_only(change3_runs):
    run = change3_runs["below_the_floor"]
    assert run["urls"] == [] and run["returnedUnchanged"]
    assert sorted(run["files"]) == ["scratch/dec/last.json"]
    record = json.loads(run["files"]["scratch/dec/last.json"])
    assert (record["decision"], record["stage"], record["sourceEstimatedTokens"]) == ("below_threshold", "read_output", 60)


@needs_strip
def test_change3_a_failing_record_write_never_changes_the_result(change3_runs):
    run = change3_runs["record_write_fails"]
    assert run["urls"]  # the call went past the floor, so both record writes were attempted
    assert not any(path.startswith("scratch/dec/") for path in run["files"])
    assert run["returnedUnchanged"]


# Local change 4 (PROVENANCE.md): Jev scores against the newest historyTokens of the session, through the real hook. The
# fake scorer answers noul 0 for every chunk it is asked about, so whether a chunk is dropped turns on coverage alone.
DRIVER4 = r"""
import { register } from 'node:module';
import { pathToFileURL } from 'node:url';

const input = [];
for await (const chunk of process.stdin) input.push(chunk);
const job = JSON.parse(Buffer.concat(input).toString('utf8'), (key, value) =>
  value !== null && typeof value === 'object' && typeof value.$number === 'string' ? Number(value.$number) : value);
const hookUrl = pathToFileURL(job.hook).href;
const rootUrl = new URL('../', hookUrl).href;
const outputUrl = new URL('src/output.ts', rootUrl).href;
// A pass-through wrapper around the real trimOutput: it records the input the handler passes, then calls it unchanged.
const wrapperUrl = 'data:text/javascript,' + encodeURIComponent([
  `import { trimOutput as realTrimOutput } from ${JSON.stringify(outputUrl)};`,
  `export * from ${JSON.stringify(outputUrl)};`,
  'export async function trimOutput(input, asker, options) {',
  '  globalThis.c4Inputs.push(input);',
  '  return realTrimOutput(input, asker, options);',
  '}',
].join('\n'));
register('data:text/javascript,' + encodeURIComponent([
  `const HOOK = ${JSON.stringify(hookUrl)}, ROOT = ${JSON.stringify(rootUrl)}, WRAPPER = ${JSON.stringify(wrapperUrl)};`,
  'export async function resolve(specifier, context, next) {',
  "  if (context.parentURL === HOOK && specifier === '../src/output.js') return { url: WRAPPER, shortCircuit: true };",
  "  if (context.parentURL && context.parentURL.startsWith(ROOT) && (specifier.startsWith('./') || specifier.startsWith('../'))",
  "      && specifier.endsWith('.js')) return next(specifier.slice(0, -3) + '.ts', context);",
  '  return next(specifier, context);',
  '}',
].join('\n')));

globalThis.c4Inputs = [];
const hook = await import(hookUrl);
const { estimateStateTokens } = await import(new URL('src/jev.ts', rootUrl).href);
const { historyEntries } = await import(new URL('src/history.ts', rootUrl).href);
const cost = (messages) => estimateStateTokens(JSON.stringify(historyEntries(messages)));

// The session: 380 prompts and replies, then 10 tool cycles with no prompt in them, so the task (the last three prompts)
// lies outside a short window; more than 100,000 estimated tokens in all.
const words = (n, tag) => Array.from({ length: n }, (_, i) => `${tag}word${String.fromCharCode(97 + (i % 26))}`).join(' ');
const session = [];
for (let i = 0; i < 380; i += 1) {
  session.push(i % 2 === 0
    ? { role: 'user', text: `PROMPT-${i} ` + words(280, 'p'), toolUses: [] }
    : { role: 'assistant', text: words(280, 'r'), toolUses: [] });
}
for (let i = 0; i < 10; i += 1) {
  session.push({ role: 'assistant', text: '', toolUses: [{ tool_use_id: `toolu_c4_${i}`, tool: 'Bash', input: { command: 'ls' } }] });
  session.push({ role: 'user', text: '', toolUses: [], toolResults: [{ tool_use_id: `toolu_c4_${i}`, text: words(250, 'o') }] });
}
const output = Array.from({ length: 300 }, (_, i) => `row ${String(i).padStart(4, '0')} alpha beta gamma delta epsilon`).join('\n');
const apiKey = ['c4', 'fake', String(process.pid)].join('-');  // built at run time; the fake fetch drops it

const results = [];
for (const c of job.cases) {
  const resolved = hook.resolveHookConfig(c.options);
  if (!c.run) { results.push({ name: c.name, historyTokens: resolved.historyTokens ?? 'absent' }); continue; }
  let handler;
  await hook.register((name, matcher, fn) => { handler = fn; }, { ...c.options, apiKey });
  const files = new Map();
  let fetches = 0;
  const $ = {
    fs: {
      read: async () => { throw new Error('c4: no persisted output in this test'); },
      exists: async (path) => files.has(path),
      write: async (path, data) => { files.set(path, data); },
    },
    env: { get: async () => undefined },
    settings: { read: async () => ({}) },
    session: { messages: async () => session },
    http: { fetch: async (url, init) => {
      fetches += 1;
      const answers = Object.fromEntries(Object.keys(JSON.parse(init.body).questions).map((id) => [id, { noul: 0 }]));
      return { status: 200, ok: true, text: JSON.stringify({ answers }) };
    } },
    ui: { log: () => {}, toast: () => {} },
  };
  const answer = { result: { stdout: output, stderr: '' } };
  const before = globalThis.c4Inputs.length;
  const back = await handler($, { command: 'make fixture', tool_use_id: `toolu_c4_${c.name}` }, async () => answer);
  const passed = globalThis.c4Inputs.slice(before);
  const stdout = (back.result ?? answer.result).stdout;
  results.push({
    name: c.name, historyTokens: resolved.historyTokens ?? 'absent', fetches, trimCalls: passed.length,
    record: JSON.parse(files.get(`${c.options.decisionsDir}/last.json`)),
    returnedUnchanged: back === answer, stdoutChars: stdout.length, outputChars: output.length,
    omittedMarker: /\[\d+ lines omitted\]/.test(stdout),
    goal: passed[0]?.goal ?? null, goalOfSession: hook.goalFromMessages(session),
    windowLength: passed[0]?.messages.length ?? null,
    windowIsTheNewest: passed[0] ? passed[0].messages.every((m, i, w) => m === session[session.length - w.length + i]) : null,
  });
}
// recentMessages itself: at a budget equal to the cost of the newest k messages it returns exactly k; one token under,
// k - 1.
const unit = [];
for (const k of [1, 3, 7]) {
  const exact = cost(session.slice(-k));
  unit.push({ k, exact, at: hook.recentMessages(session, exact).length,
              under: hook.recentMessages(session, exact - 1).length, nextCost: cost(session.slice(-(k + 1))) });
}
const tooBig = [{ role: 'user', text: words(500, 'x'), toolUses: [] }];
console.log(JSON.stringify({ results, unit, sessionLength: session.length, sessionCost: cost(session),
  empty: hook.recentMessages([], 1000).length, tooBig: hook.recentMessages(tooBig, 10).length }));
"""

CHANGE_4_BASE = {"minTokensFloor": 0, "minTokens": 0, "maxStateTokens": 8000, "decisionsDir": "scratch/dec",
                 "archiveDir": "scratch/arch"}
CHANGE_4_CASES = [
    {"name": "whole_session", "options": CHANGE_4_BASE, "run": True},
    {"name": "window", "options": {**CHANGE_4_BASE, "historyTokens": 2000}, "run": True},
    {"name": "negative", "options": {**CHANGE_4_BASE, "historyTokens": -5}, "run": True},
    # the option's resolution only
    {"name": "absent", "options": {}}, {"name": "one", "options": {"historyTokens": 1}},
    {"name": "fraction", "options": {"historyTokens": 2000.7}}, {"name": "half", "options": {"historyTokens": 0.5}},
    {"name": "zero", "options": {"historyTokens": 0}}, {"name": "nan", "options": {"historyTokens": NAN}},
    {"name": "inf", "options": {"historyTokens": INF}}, {"name": "minus_inf", "options": {"historyTokens": -INF}},
    {"name": "string", "options": {"historyTokens": "2000"}},
]


@pytest.fixture(scope="module")
def change4_runs():
    job = {"hook": str(HOOK), "cases": CHANGE_4_CASES}
    proc = subprocess.run(["node", "--input-type=module", "-e", DRIVER4], input=json.dumps(_for_node(job), allow_nan=False),
                          capture_output=True, text=True, timeout=300, cwd=REPO)
    assert proc.returncode == 0, proc.stderr[-4000:]
    out = json.loads(proc.stdout.strip().splitlines()[-1])
    out["by_name"] = {r["name"]: r for r in out["results"]}
    return out


@needs_strip
def test_change4_the_option_takes_a_finite_number_of_at_least_one(change4_runs):
    got = {r["name"]: r["historyTokens"] for r in change4_runs["results"]}
    assert got == {"whole_session": "absent", "window": 2000, "negative": "absent", "absent": "absent", "one": 1,
                   "fraction": 2000, "half": "absent", "zero": "absent", "nan": "absent", "inf": "absent",
                   "minus_inf": "absent", "string": "absent"}


@needs_strip
def test_change4_the_whole_session_outruns_the_requests_and_nothing_is_pruned(change4_runs):
    """The upstream behaviour, and the negative control for the window: the same session and scorer, no window."""
    assert change4_runs["sessionLength"] == 400 and change4_runs["sessionCost"] > 100_000
    for name in ("whole_session", "negative"):
        run = change4_runs["by_name"][name]
        record = run["record"]
        assert record["decision"] == "incomplete_coverage" and record["dropped"] == 0, (name, record)
        assert run["fetches"] == record["requests"] == record["requestLimit"] == 12, (name, record)
        assert run["returnedUnchanged"] and run["trimCalls"] == 1
        assert run["windowLength"] == record["historyMessages"] == record["sessionMessages"] == 400


@needs_strip
def test_change4_the_window_prunes_and_the_task_stays_whole(change4_runs):
    run = change4_runs["by_name"]["window"]
    record = run["record"]
    assert record["decision"] == "pruned" and record["dropped"] > 0, record
    assert run["fetches"] == record["requests"] < record["requestLimit"], record
    assert not run["returnedUnchanged"] and run["omittedMarker"] and run["stdoutChars"] < run["outputChars"]
    assert record["sessionMessages"] == 400 and 0 < record["historyMessages"] == run["windowLength"] < 20
    assert run["windowIsTheNewest"] is True
    # the task: the session's last three prompts, all older than the window
    assert run["goal"] == run["goalOfSession"] and run["goal"].count("PROMPT-") == 3


@needs_strip
def test_change4_recent_messages_is_the_longest_newest_run_that_fits(change4_runs):
    for row in change4_runs["unit"]:
        assert (row["at"], row["under"]) == (row["k"], row["k"] - 1) and row["nextCost"] > row["exact"], row
    assert change4_runs["empty"] == 0 and change4_runs["tooBig"] == 0
