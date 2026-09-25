# Upstream issue texts (D-091 items 2 and 4; task #289)

The owner files these (the session's GitHub access does not reach third-party repositories: `add_repo` for
DeusData/codebase-memory-mcp was refused by the permission classifier on 2026-09-25). Each text holds only public facts:
versions, timings and a reproduction, no repository content.

## 1. DeusData/codebase-memory-mcp

**Title:** `hook-augment` reads its whole executable on every call, so it always misses its 2,000 ms deadline and adds nothing

**Body:**

Version: codebase-memory-mcp 0.10.8, the prebuilt Linux x86_64 release binary (293,213,352 bytes).

What happens: the Claude Code hooks the installer registers (`cbm-code-discovery-gate`, which runs
`codebase-memory-mcp hook-augment`) never add context. `~/.cache/codebase-memory-mcp/logs/` fills with
`hook-augment: deadline_exceeded ms=2000` (3,361 lines in one week on our machine). Each Read, Grep and Glob still
waits about 2.0 s for the hook.

Why, from one call under strace (`CBM_HOOK_DEADLINE_MS=10000` so that it completes):

- +0.00 s: opens `/proc/<pid>/exe`.
- +0.02 s to +2.79 s: 4,475 `pread64` calls on that descriptor, 293,213,352 bytes in total: the whole executable.
- +2.80 s: connects to the daemon socket (`/tmp/cbm-daemon-0/cbm-<hash>.sock`).
- +2.87 s: exits, with 614 bytes of context on stdout.

About 97% of each call reads the binary; it looks like a full-file hash that names the daemon's socket or version
cohort. The real work takes about 70 ms. Under the default 2,000 ms deadline the call stops before it reaches the
daemon: 2.02 s wall time and 0 bytes out, on every call. The index size is not the cause (a 91 MB index gives the same
2.0 s). The CLI one-shots pay the same start cost (about 2.4 s for a `search_graph`).

Reproduction:

```
echo '{"session_id":"x","transcript_path":"/dev/null","cwd":"<repo>","hook_event_name":"PreToolUse","tool_name":"Grep","tool_input":{"pattern":"<a symbol in the repo>"}}' \
  | CBM_HOOK_DEADLINE_MS=10000 strace -f -ttt -e trace=openat,pread64,connect codebase-memory-mcp hook-augment
```

Suggestion: compute the binary's identity once and cache it (keyed by path, inode, size and mtime), or take it from the
ELF build id or the embedded version string instead of hashing the whole file.

Workaround we use: we removed the hooks and kept the MCP server and the CLI. `CBM_HOOK_DEADLINE_MS=10000` makes the hook
return context in about 2.7 s, which is too slow to run before every tool call.

## 2. rafal-qa/slopo

Waits for SLOPO2 (task #285): its report drafts the text with the measured numbers (the PC's first index took 1,389 s
because `scan_directory` walks every file under `source_dir`, 18.1 million of them excluded, before it applies the
exclude list).
