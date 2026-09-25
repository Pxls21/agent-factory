#!/usr/bin/env python3
"""installation.py — S1A evidence demand 7 (the coordinator's addition, D-090): is each tool the workflow names installed?

For every item: where the workflow names it (CLAUDE.md lines, SKILL.md files, hook files, scripts/setup.sh lines,
harness-ports/bin/pc-setup.sh lines, upstream.lock.yaml lines; a regex per item, printed), whether it is installed in the
sandbox and how it is found (PATH or an absolute path), its version (the smoke command's first line and rc) against the
pin in upstream.lock.yaml, the setup.sh / pc-setup.sh lines that install it (a second regex per item), and whether
setup.sh re-installs it on a fresh container. The PC column only quotes what pc-setup.sh claims; it is NOT measured (no
bridge). Read-only: version and help commands only; nothing is installed or changed.

Usage: installation.py > demand7.md
"""
import glob
import os
import re
import shutil
import subprocess
import sys

REPO = "/home/user/agent-factory"
SETUP = REPO + "/scripts/setup.sh"
PCSETUP = REPO + "/harness-ports/bin/pc-setup.sh"
LOCK = REPO + "/upstream.lock.yaml"
HOOK_FILES = sorted(glob.glob(REPO + "/.claude/hooks/*") + glob.glob(REPO + "/scripts/hooks/*"))
SKILLS = sorted(glob.glob(REPO + "/.claude/skills/*/SKILL.md"))

# name, mention regex, how to find it (a PATH name or an absolute path), smoke command, pin (lock key text or None),
# installer regex (setup.sh and pc-setup.sh lines that install it), fresh-container note
ITEMS = [
    ("graft", r"\bgraft\b", "graft", "graft --version", None, r"@nanonets/graft", ""),
    ("GitNexus", r"[Gg]it[Nn]exus|gitnexus", "gitnexus", "gitnexus --version", None, r"gitnexus@", ""),
    ("codebase-memory (cbm)", r"codebase-memory", "/root/.local/bin/codebase-memory-mcp",
     "/root/.local/bin/codebase-memory-mcp --version", None, r"codebase-memory-mcp/install\.sh", ""),
    ("code-review-graph (crg)", r"code-review-graph|\bcrg\b", "/root/venv-crg/bin/code-review-graph",
     "/root/venv-crg/bin/code-review-graph --version", None, r"pip3? install[^\n]*code-review-graph", ""),
    ("ripwire", r"ripwire", "ripwire", "ripwire --version", "ripwire", r"ripwire/releases/download", ""),
    ("sentrux", r"sentrux", "sentrux", "sentrux --version", "sentrux", r"sentrux/releases/download", ""),
    ("slopo", r"\bslopo\b", "slopo", "slopo --version", None, r"slopo", ""),
    ("prism skills (5)", r"\bprism-(scan|full|3way|discover|reflect)\b|\bprism\b", REPO + "/.claude/skills/prism-scan/SKILL.md",
     "ls " + REPO + "/.claude/skills/ | grep -c '^prism-'", None, r"prism", "vendored in git (.claude/skills), not installed by a script"),
    ("honey plugin (honey@greenpt)", r"\bhoney\b", "/root/.claude/plugins/cache/greenpt/honey",
     "node /root/.claude/plugins/cache/greenpt/honey/1.3.1/hooks/honey-session.js < /dev/null", None,
     r"claude plugin (install honey|marketplace add)", ""),
    ("jev plugin (fast-jev-output@fast-jev-output)", r"fast-jev-output|jev-pruner", "/root/.claude/plugins/cache/fast-jev-output",
     "ls /root/.claude/plugins/cache/fast-jev-output/fast-jev-output/0.1.0/hooks/fast-jev-output.ts", "jev-pruner",
     r"fast-jev-output|jev-pruner", ""),
    ("aegis plugin (aegis@aegis-dev)", r"\baegis\b", "/root/.claude/plugins/cache/aegis-dev/aegis",
     "CLAUDE_PLUGIN_ROOT=/root/.claude/plugins/cache/aegis-dev/aegis/2.10.6 bash /root/.claude/plugins/cache/aegis-dev/aegis/2.10.6/hooks/run-hook.cmd session-start < /dev/null", None,
     r"aegis", ""),
    ("wiki compiler (/wiki-*, wiki-compiler skill)", r"wiki-compile|wiki compiler|llm-wiki-compiler", "/root/.claude/skills/wiki-compiler/SKILL.md",
     "ls /root/.claude/commands/ | grep -c '^wiki-'", None, r"llm-wiki-compiler/install\.sh", ""),
    ("council (/council, council-* agents)", r"\bcouncil\b", "/root/.claude/skills/council/SKILL.md",
     "ls /root/.claude/agents/ | grep -c '^council-'", None, r"council-of-high-intelligence/install\.sh", ""),
    ("Ouroboros (ouroboros, ooo)", r"[Oo]uroboros|\booo\b", "ouroboros", "ouroboros --version", None,
     r"uv tool install ouroboros", ""),
    ("aleph (MCP server)", r"\baleph\b", "/root/venv-agent-factory/bin/aleph", "/root/venv-agent-factory/bin/aleph --help", None,
     r"aleph\[mcp\]", ""),
    ("phoenix-docs (http MCP)", r"phoenix-docs", "(http MCP, no binary)", "", None, r"mcp add --transport http phoenix-docs",
     "registered, not installed; smoke not run (network)"),
    ("Laya venv (sandbox)", r"venv-laya|\bLaya\b", "/root/venv-laya-probe/bin/python",
     "/root/venv-laya-probe/bin/python -c 'import importlib.metadata as m; print(\"laya\", m.version(\"laya\"))'",
     "laya-typed-decisions", r"venv-laya|laya-server", ""),
    ("RWKV / fla venv", r"venv-rwkv|\bfla\b|flash-linear-attention", "/root/venv-rwkv/bin/python", "/root/venv-rwkv/bin/python --version",
     "rwkv7-goose-world2.9-0.4b", r"venv-rwkv|flash-linear", ""),
    ("node", r"\bnode\b", "node", "node --version", None, r"nodesource|install node|nvm install", "comes with the container image"),
    ("npm", r"\bnpm\b", "npm", "npm --version", None, r"install npm", "comes with the container image"),
    ("uv / uvx", r"\buvx?\b", "uv", "uv --version", None, r"astral\.sh/uv|install uv", "comes with the container image"),
    ("pytest", r"\bpytest\b", "/root/venv-agent-factory/bin/python", "/root/venv-agent-factory/bin/python -m pytest --version",
     None, r"pip install[^\n]*pytest", ""),
    ("pytest-xdist", r"pytest-xdist|\bxdist\b|-n 8\b", "/root/venv-agent-factory/bin/python",
     "/root/venv-agent-factory/bin/python -c 'import xdist'", None, r"pytest-xdist", ""),
    ("pyflakes", r"pyflakes", "/root/venv-agent-factory/bin/python", "/root/venv-agent-factory/bin/python -m pyflakes --version",
     None, r"pip install[^\n]*pyflakes", ""),
    ("mcp==1.29.1 (aleph's SDK pin)", r"mcp==1\.29\.1", "/root/venv-agent-factory/bin/python",
     "/root/venv-agent-factory/bin/python -c 'import importlib.metadata as m; print(m.version(\"mcp\"))'", None, r"mcp==1\.29\.1", ""),
    ("ripgrep (rg; search-intercept, jev_context)", r"\brg\b|ripgrep", "rg", "rg --version", None, r"ripgrep|install rg", "comes with the container image"),
    ("jq (the CCR Stop hook)", r"\bjq\b", "jq", "jq --version", None, r"install jq", "comes with the container image"),
    ("git", r"\bgit\b", "git", "git --version", None, r"install git", "comes with the container image"),
    ("claude CLI (plugin and MCP registration)", r"\bclaude (mcp|plugin)\b", "claude", "claude --version", None, r"@anthropic-ai/claude-code",
     "comes with the container image"),
    ("gpg (tests/test_proof_status.py)", r"\bgpg\b", "gpg", "gpg --version", None, r"install gnupg", "comes with the container image"),
    ("gh (GitHub CLI)", r"\bgh\b", "gh", "gh --version", None, r"install gh|cli\.github\.com", ""),
    ("output styles (~/.claude/output-styles)", r"output-styles|Attention-kind", "/root/.claude/output-styles",
     "ls /root/.claude/output-styles | wc -l", None, r"output-styles", ""),
    ("session hooks (/home/user/.claude/settings.json)", r"install_session_hooks", "/home/user/.claude/settings.json",
     "python3 " + REPO + "/scripts/install_session_hooks.py --check", None, r"install_session_hooks\.py", ""),
    ("git hooks (core.hooksPath=scripts/hooks)", r"core\.hooksPath|scripts/hooks", "git config", "git -C " + REPO + " config core.hooksPath",
     None, r"core\.hooksPath", ""),
]


# The package name whose `==<version>` or `@<version>` on the setup.sh install line is the item's own pin.
OWN_PIN_TOKEN = {"graft": "@nanonets/graft", "GitNexus": "gitnexus", "code-review-graph (crg)": "code-review-graph",
                 "Ouroboros (ouroboros, ooo)": "ouroboros-ai", "pytest": "pytest", "pyflakes": "pyflakes",
                 "mcp==1.29.1 (aleph's SDK pin)": "mcp"}

# Installers outside pc-setup.sh that a PC row depends on (read from the files; NOT measured on the PC).
PC_NOTES = {
    "Laya venv (sandbox)": "; harness-ports/bin/laya-server.sh:8 installs ~/venv-laya (a user service), not pc-setup.sh",
    "RWKV / fla venv": "; ~/venv-rwkv and ~/venv-rwkv-b are named by PC-BRIDGE.md:216 and scripts/gpu_side_by_side.sh:65; no "
                       "script in the repo creates them",
}


def sh(cmd, timeout=60):
    try:
        p = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=timeout, cwd=REPO)
        first = re.sub(r"\x1b\[[0-9;]*m", "", (p.stdout or p.stderr).strip().splitlines()[0] if (p.stdout or p.stderr).strip() else "")
        return p.returncode, first[:70]
    except subprocess.TimeoutExpired:
        return "timeout", ""


def lines_matching(path, rx):
    try:
        return [i for i, line in enumerate(open(path, errors="replace"), 1) if re.search(rx, line)]
    except OSError:
        return []


def fmt_lines(ls, cap=6):
    return ("," .join(str(x) for x in ls[:cap]) + ("…" if len(ls) > cap else "")) if ls else "-"


def lock_pin(key):
    if not key:
        return "no pin"
    try:
        import yaml
        d = yaml.safe_load(open(LOCK))
    except Exception as exc:
        return f"(lock unreadable: {type(exc).__name__})"
    for sec in d.values():
        if isinstance(sec, dict) and key in sec and isinstance(sec[key], dict):
            v = sec[key]
            parts = [f"{k}={str(v[k])[:14]}" for k in ("release_tag", "commit", "package_version", "binary_sha256", "weights_digest")
                     if k in v]
            return f"{key}: " + (", ".join(parts) if parts else "entry with no version field")
    return f"no entry {key!r}"


def main() -> int:
    claude_md = open(REPO + "/CLAUDE.md", errors="replace").read().splitlines()
    print("| item | named in: CLAUDE.md lines · SKILL.md files · hook files · setup.sh lines · pc-setup.sh lines · lock lines "
          "(mention regex) | installed in the sandbox | found via | smoke: command → rc, first line | pin in upstream.lock.yaml (and the setup.sh line's own pin) | "
          "installed by (install regex: setup.sh lines; pc-setup.sh lines) | setup.sh re-installs it on a fresh container | "
          "PC (pc-setup.sh claims; NOT measured) |")
    print("|" + "---|" * 9)
    summary = {"installed": 0, "not installed": 0, "no installer in setup.sh": 0, "no pin": 0}
    for name, mrx, find, smoke, pin, irx, note in ITEMS:
        n_claude = sum(1 for line in claude_md if re.search(mrx, line))
        n_skills = sum(1 for f in SKILLS if re.search(mrx, open(f, errors="replace").read()))
        n_hooks = sum(1 for f in HOOK_FILES if os.path.isfile(f) and re.search(mrx, open(f, errors="replace").read()))
        named = (f"{n_claude} · {n_skills} · {n_hooks} · {fmt_lines(lines_matching(SETUP, mrx))} · "
                 f"{fmt_lines(lines_matching(PCSETUP, mrx))} · {fmt_lines(lines_matching(LOCK, mrx))} (`{mrx}`)")
        if find.startswith("/"):
            present = os.path.exists(find) or bool(glob.glob(find + "*"))
            how = find if present else f"absent: {find}"
        elif find.startswith("("):
            present, how = None, find
        elif find == "git config":
            present, how = True, "git config"
        else:
            w = shutil.which(find)
            present = w is not None
            how = f"PATH: {w}" if w else f"not on PATH ({find})"
        rc, first = sh(smoke) if smoke else ("-", "not run")
        if name.startswith("pytest-xdist") or name.startswith("session hooks"):
            present = present and rc == 0
        inst_setup = lines_matching(SETUP, irx)
        inst_pc = lines_matching(PCSETUP, irx)
        fresh = ("yes (setup.sh:" + fmt_lines(inst_setup) + ")") if inst_setup else ("no — " + (note or "no install line"))
        pcol = ("pc-setup.sh:" + fmt_lines(inst_pc)) if inst_pc else "nothing in pc-setup.sh"
        state = "yes" if present else ("n/a" if present is None else "NO")
        summary["installed" if present else "not installed"] += 1 if present is not None else 0
        summary["no installer in setup.sh"] += 0 if inst_setup else 1
        summary["no pin"] += 1 if not pin else 0
        pcol += PC_NOTES.get(name, "")
        src = open(SETUP, errors="replace").read().splitlines()
        tok = OWN_PIN_TOKEN.get(name)
        own = sorted({m.group(1) for i in inst_setup
                      for m in re.finditer(re.escape(tok) + r"(?:==|@)(\d[\w.]*)", src[i - 1])}) if tok else []
        if name in ("ripwire", "sentrux"):
            own = sorted({m.group(1) for m in re.finditer(r"^%s_VER=\"(v[\d.]+)\"" % name.upper(), "\n".join(src), re.M)})
        cells = [name, named, state, how, f"`{smoke or '-'}` → {rc}, {first or '-'}",
                 lock_pin(pin) + ("; the setup.sh install line pins " + ", ".join(own) if own else "; the setup.sh install line pins no version" if inst_setup else ""),
                 f"setup.sh: {fmt_lines(inst_setup)}; pc-setup.sh: {fmt_lines(inst_pc)} (`{irx}`)", fresh, pcol]
        print("| " + " | ".join(str(c).replace("|", "\\|") for c in cells) + " |")
    print()
    print(f"Items: {len(ITEMS)}. " + ", ".join(f"{k}: {v}" for k, v in summary.items()) + ".")
    print()
    print("Pin checks against upstream.lock.yaml and the provenance files (each line: the command's result):")
    checks = [
        ("sentrux binary sha256 = lock binary_sha256", "sha256sum /root/.local/bin/sentrux | cut -c1-64",
         "3237f80fe20d54aad4deefa8a143f0d60543bb5d2d6ad891eb42432f155725a6"),
        ("ripwire binary sha256 = lock binary_sha256", "sha256sum /root/.local/bin/ripwire | cut -c1-64",
         "6a1957b829f74e29b16caf550e90ea5504afa3ebd200c0b253f2f3afaae76aa3"),
        ("laya package in /root/venv-laya-probe = lock package_version",
         "/root/venv-laya-probe/bin/python -c 'import importlib.metadata as m; print(m.version(\"laya\"))'", "0.3.5"),
        ("jev-pruner source clone HEAD (/root/jev-plugins/jev-pruner) = lock commit",
         "git -C /root/jev-plugins/jev-pruner rev-parse HEAD", "47d017c34eab7690b95f075ce6f4839247c5dc0a"),
        ("Aegis source clone HEAD (/root/jev-plugins/Aegis) = PROVENANCE-AEGIS.md commit",
         "git -C /root/jev-plugins/Aegis rev-parse --short=7 HEAD", "60321ed"),
        ("graft installed vs latest on npm (graft's own update notice)", "graft version 2>&1 | head -3 | tr '\\n' ' '", None),
    ]
    for label, cmd, want in checks:
        rc, first = sh(cmd)
        verdict = "" if want is None else (" — matches" if first.strip() == want else f" — DIFFERS (want {want[:16]})")
        print(f"- {label}: `{cmd}` → rc {rc}, {first[:70]}{verdict}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
