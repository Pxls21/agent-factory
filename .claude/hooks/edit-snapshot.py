#!/usr/bin/env python3
"""EDIT-SNAPSHOT hook (owner directive 2026-08-25): after every Edit/Write,
hand the coordinator an automatic snapshot of what the edit touched — the
enclosing symbol(s), their upstream blast radius (GitNexus), and a screen of
the new code against the ANTI-PATTERN REGISTRY's mechanical signatures
(docs/INCIDENT-LOG.md) — so per-edit awareness is presented, not remembered.

Contract: PostToolUse hook on Edit|Write. Reads the hook JSON on stdin,
prints a compact snapshot to stdout, ALWAYS exits 0 — this hook informs,
it never blocks (a broken instrument must not stop an edit; the reviewer
loop stays the enforcement point). Every external probe is time-bounded.

Extend the AP screen when a new registry row lands (bug-echo mandate:
registry and this screen move together).
"""
import os
import ast
import json
import re
import subprocess
import sys
from pathlib import Path

_EMIT_OPEN = re.compile(r"emit_(?:runtime_event|event|decision|metric)\s*\(")
_NONE_KWARG = re.compile(r"=\s*None\s*(?:#.*)?$")


class _EmitNoneKwarg:
    """AP-59 tell with a balanced-paren scan (TN3-F7, 2026-09-02).

    The regex form `emit_x\\((?:[^)]|\\n)*?=\\s*None` cannot cross the `)` of an
    earlier kwarg that is itself a call (`per_fold_coverage=list(...)`), so it
    was blind to every real emit — including the one the registry cites. This
    walks the emit's argument list and flags a DEPTH-1 kwarg whose value is the
    literal None. Same `.search()` surface as a compiled regex.
    """

    def search(self, text):
        for m in _EMIT_OPEN.finditer(text):
            depth, buf = 1, []
            i = m.end()
            while i < len(text) and depth:
                c = text[i]
                if c in "([{":
                    depth += 1
                elif c in ")]}":
                    depth -= 1
                if depth == 1 and c == ",":
                    if _NONE_KWARG.search("".join(buf).strip()):
                        return m
                    buf = []
                elif depth >= 1:
                    buf.append(c)
                i += 1
            if _NONE_KWARG.search("".join(buf).rstrip(") \n").strip()):
                return m
        return None


# AF-AP-139 (2026-09-23, S0-05's C0 probe): an HTTP stand-in that answers the same literal 2xx on every path — the
# E1-E3 stand-ins answered 200 to `GET /v1/models`, where the real OmniRoute answers 401 and the real relay 404, so
# the live leg's positive control would have failed. The tell: a do_<METHOD> handler that reaches a literal-2xx
# send_response with no `if … self.path` line before it (logging the path is not a branch on it). Stand-ins live in
# tests and in production stubs, and the hook screens /tests/ paths with TEST_SCREEN only, so the row is in both.
# Widened 2026-09-24 (VERIFY-K150 F-06): a `-> None` return annotation and a 2xx HTTPStatus member are the same class.
_AF_AP_139 = (
    "AF-AP-139",
    re.compile(r"""def\s+do_[A-Z]+\(\s*self\b[^)]*\)\s*(?:->\s*None\s*)?:(?:(?!\bif\b[^\n]*\bself\.path\b|\bdef\s)[\s\S]){0,1000}?\bsend_response\(\s*(?:2\d\d|(?:http\.)?HTTPStatus\.(?:OK|CREATED|ACCEPTED|NON_AUTHORITATIVE_INFORMATION|NO_CONTENT|RESET_CONTENT|PARTIAL_CONTENT|MULTI_STATUS|ALREADY_REPORTED|IM_USED))\s*\)"""),
    "an HTTP stand-in that sends a literal 2xx with no branch on `self.path` — more permissive than the service it "
    "stands in for, so the positive control is graded against nothing; measure the real service's answer to the "
    "probe's exact request, key the stand-in's status on the path, and add a negative control that refuses on the "
    "probe path (AF-AP-139)",
)


class _PathScoped:
    """A row whose class lives in one family of paths. A row carries no path, so the hook's main, which knows the
    edited file, asks for_path(path) for the pattern to apply there. The callers that pass text alone
    (scripts/ap_screen.py, scripts/lint_delta.py) get no match from search()/finditer(): they cannot apply the scope,
    and the pattern unscoped would fire on every such call in the tree."""

    def __init__(self, paths, rx):
        self.paths, self.rx = paths, rx

    def for_path(self, path):
        return self.rx if self.paths.search(path) else self

    def search(self, text):
        return None

    def finditer(self, text):
        return iter(())


class _ExitTrapCleanup:
    """AF-AP-145's two tells, each found in one pass, so the cost stays linear in the text: a lookahead that re-scanned
    the rest of the text from every function definition took 0.68 s on 2,000 of them (AF-AP-152's class). The names an
    EXIT trap runs are collected first, so a trap line above its function is seen as well."""

    _IGNORE = r"""[ \t]*trap[ \t]+(?:''|"")[ \t]+(?:INT[ \t]+TERM|TERM[ \t]+INT)\b"""
    _TRAPPED = re.compile(r"""^[ \t]*trap[ \t]+(['"]?)([A-Za-z_]\w*)\1[ \t]+(?:[A-Z0-9]+[ \t]+)*EXIT\b""", re.MULTILINE)
    # a function body that does not open with the ignore (a `$?` capture or a comment may come first)
    _BODY = re.compile(r"""^[ \t]*(?:function[ \t]+)?([A-Za-z_]\w*)[ \t]*\(\)[ \t]*\{[ \t]*(?:#[^\n]*)?\n"""
                       r"""(?!(?:[ \t]*(?:#[^\n]*|(?:local[ \t]+)?[A-Za-z_]\w*=\$\?[ \t]*(?:#[^\n]*)?)\n)*""" + _IGNORE + ")",
                       re.MULTILINE)
    # an INT/TERM handler string that does not open with the ignore
    _HANDLER = re.compile(r"""^[ \t]*trap[ \t]+(['"])(?!\1)(?!""" + _IGNORE + r""")(?:(?!\1)[^\n])*\1[ \t]+"""
                          r"""(?:[A-Z0-9]+[ \t]+)*(?:INT|TERM)\b""", re.MULTILINE)
    # the third tell (VERIFY-GW1-R1 R1-F-1, 2026-09-24): a bare `exit` after the INT/TERM handler traps, in a script
    # whose EXIT trap runs a cleanup; the exit hands over to the EXIT trap with INT and TERM live, so ONE signal in the
    # gap runs the handler's own exit inside it. An exit on a line that ignores first (`trap '' INT TERM; exit`) is fine.
    _ARMS = re.compile(r"""^[ \t]*trap[ \t]+(['"])(?:(?!\1)[^\n])+\1[ \t]+(?:[A-Z0-9]+[ \t]+)*(?:INT|TERM)\b[^\n]*$""",
                       re.MULTILINE)   # a non-empty handler: `trap '' INT TERM` is the ignore, not a handler
    _EXIT = re.compile(r"""^(?![ \t]*#)(?![^\n]*""" + _IGNORE + r"""[ \t]*;[ \t]*exit\b)[^\n#]*?(?<![\w-])exit(?![\w-])""",
                       re.MULTILINE)

    def finditer(self, text):
        trapped = {m.group(2) for m in self._TRAPPED.finditer(text)}
        hits = [m for m in self._BODY.finditer(text) if m.group(1) in trapped]
        arms = [m.end() for m in self._ARMS.finditer(text)]
        if trapped and arms:
            hits += list(self._EXIT.finditer(text, max(arms)))
        return iter(sorted(hits + list(self._HANDLER.finditer(text)), key=lambda m: m.start()))

    def search(self, text):
        return next(self.finditer(text), None)


# Mechanical signatures distilled from the ANTI-PATTERN REGISTRY (id: regex,
# message). Only patterns that are cheaply greppable in a diff hunk belong
# here; judgment-class rows stay in review.
AP_SCREEN = [
    ("AP-44", re.compile(r"(run_gate|gate_final_population)\((?![^)]*deflator_n_override)"),
     "gate call without deflator_n_override — weak-default gate mints the strict 'certified' spelling (AP-44); thread deflator/threshold/admission or state the weak arm in the label"),
    ("AP-1", re.compile(r"os\.environ\.get|getenv\("),
     "env read in edited code — config channel? resolve ONCE at construction, thread explicitly"),
    ("AP-2", re.compile(r"os\.environ\[[^\]]+\]\s*=|environ\.setdefault\("),
     "os.environ WRITE — process-global and sticky; almost always wrong mid-run"),
    ("AP-3", re.compile(r"\bisnan\b(?![^\n]*isfinite)"),
     "isnan without isfinite nearby — inf rides through; guard the WHOLE unusable class"),
    ("AP-31", re.compile(r"(Integer|Real)\(bounds="),
     "numeric-bounded search variable — if its values are category labels/slots, use Choice (router bug class)"),
    ("AP-32", re.compile(r"(sha256|md5|hash)\("),
     "hashing in edited code — is the hashed form EXACTLY what the store holds? (stamp-store mismatch class)"),
    ("AP-24", re.compile(r"except\s+(Exception|BaseException)?\s*:\s*(pass|continue)\b"),
     "swallowed exception — fail-soft must be fail-LOUD"),
    # AF-AP-12 (2026-09-03): jsonschema registers `date-time` only when rfc3339-validator imports;
    # a FormatChecker built without asserting its checkers leaves every `format` keyword unchecked.
    ("AF-AP-12", re.compile(r"FormatChecker\(\)"),
     "FormatChecker() without asserting the needed checkers are registered — an unregistered `format` is silently unchecked; assert presence and fail loud (AF-AP-12)"),
    ("AP-39", re.compile(r"(api_key|api_secret|auth_token|bearer_token)\s*:\s*Optional\[str\]\s*=\s*None"),
     "optional credential param — verify a PRODUCTION call site supplies it (cred-param-without-supplier class)"),
    ("AP-x", re.compile(r"int\(round\("),
     "int(round(...)) coercion — silent rounding masked a data-path defect once; prefer strict"),
    ("AP-36", re.compile(r"^\s+from\s+agent_factory\.[a-z_.]+\s+import\s"),
     "indented from-import — if the function uses this name on an EARLIER line, it is UnboundLocalError-on-arrival (late-local-import shadow; prefer the module-level import)"),
    ("AP-34", re.compile(r'(open\([^)]*,\s*["\']w|shutil\.copy2?\()[^\n]*(prod|_path|batch_|stages|runner)'),
     "write/copy toward a possibly-PRODUCTION path — a test/audit must mutate a tmp_path COPY, never the real module (crash window hard-wires the mutant; RA-8 F1)"),
    ("AP-50", re.compile(r'["\'][a-z_]+_applied["\']\s*:'),
     "provenance '*_applied' stamp — stamp the value only when the transform actually RAN, never the requested param (provenance-stamps-intent class)"),
    ("AP-51", re.compile(r"byte-identical|bitwise-identical", re.IGNORECASE),
     "byte/bitwise-identity claim — if this diff adds a dataclass field feeding an asdict sink, the claim is FALSE (fields serialize as null keys); say 'additive keys, null when OFF'"),
    # ECHO-V4 (2026-09-02). AP-59 misses None nested inside a payload dict
    # (depth-1 kwargs only); AP-54 is the noisiest row — fires on the
    # OFF-path analysis scripts too, informational only.
    ("AP-59", _EmitNoneKwarg(),
     "decision emit with a literal-None kwarg — if that field is a CONJUNCT of the decision, thread the value or NARRATE the absence in `reason` (UNMEASURED, not zero); pattern to copy: stages.py:3088-3104 (AP-59)"),
    ("AP-54", re.compile(r"generate_signals\((?![^)]*(?:flat_specialist_enabled|\*\*))"),
     "generate_signals without flat_specialist_enabled and without a **flags splat — resolve_blend_flags returns ONLY the 4 _BLEND_FLAG_KEYS, so an un-merged **blend_flags does NOT carry the flat flag; check the sibling callees in this same function (AP-54)"),
    # AF-AP-36 (2026-09-05): a PASS/"checks" literal in a checker's success line — the success
    # line must be DERIVED from the executed-check list, never a literal string.
    ("AF-AP-36", re.compile(r"""PASS:\s*\d+\s*checks"""),
     "PASS line with a literal check count — the success line must be DERIVED from the executed-check list, never hardcoded (AF-AP-36)"),
    # AF-AP-37 (2026-09-05): hand-typed test counts in code/prose.
    ("AF-AP-37", re.compile(r"""\d+\s+(?:tests?|passed)\s+green""", re.I),
     "hand-typed test count — paste the test_summary.sh line verbatim, never type it (AF-AP-37)"),
    # AF-AP-38 (2026-09-05): presence instead of exact value on a pin.
    # F21: pin-adjacent `if x.get():` OR `assert x.get()` — both are presence, not exact value.
    ("AF-AP-38", re.compile(r"""(?:if\s+\w+\.get\([^)]*\)\s*:(?=[^\n]*PINNED_)|assert\s+\w+\.get\()"""),
     "presence/truthiness check on a value that should be compared == against a pin (AF-AP-38)"),
    # AF-AP-39 (2026-09-05): a secret interpolated into a command line (`KEY='$VALUE'`, `KEY=${V}`,
    # f"...KEY={v}") lives in /proc/<pid>/cmdline and lands in ps-derived evidence.
    ("AF-AP-39", re.compile(r"""^(?![^\n]*\.write(?:_text|lines)?\()[^\n]*?\b\w*(?:_KEY|TOKEN|SECRET|PASSWORD)\w*=(?:'?\$|\{)""", re.MULTILINE),
     "secret interpolated into a command line — argv is world-readable for the process lifetime; build the env from files and Popen(argv, env=...) (AF-AP-39)"),
    # AF-AP-40 (2026-09-05): a presence-gated check makes a required artifact optional — deleting
    # the file switches the check off. The `if not x.exists(): raise` form is the correct one.
    # `else\b` added 2026-09-08 (VERIFY-P5a F7): the TERNARY form `v = read(p) if p.exists() else {}`
    # is the same defect with no colon and no `and` — the screen walked past
    # build_capture_record.py's `receipt = json.loads(rp.read_text()) if rp.exists() else {}`, which
    # recorded an absent relay receipt as `"accepted": null`. Extended in place rather than added as a
    # second row: the row id IS the registry class, and tests/test_edit_snapshot_ap_screen.py keys its
    # rows by id, so two rows sharing "AF-AP-40" would leave one of them untested.
    ("AF-AP-40", re.compile(r"""if\s+(?:\([^()\n]*\)|\w[\w.]*(?:\([^()\n]*\))?)\.(?:exists|is_file|is_dir)\(\)\s*(?::|and\b|else\b)"""),
     "presence-gated check — a required artifact must FAIL when absent, never skip its check (AF-AP-40)"),
    # AF-AP-41 (2026-09-05): dict(re.findall(...)) is last-wins — a duplicated key token overrides
    # the real value.
    ("AF-AP-41", re.compile(r"""dict\(\s*(?:re|\w+)\.findall\("""),
     "last-wins parse of an echo line — require each pinned key EXACTLY ONCE, then compare == (AF-AP-41)"),
    # AF-AP-45 (2026-09-06): liveness from ps presence / /proc existence without the state column — a
    # zombie (<defunct>) reads as a running survivor until its parent reaps it.
    # 2026-09-07 (VERIFY-B5e F15): an existence probe on /proc/<pid>/stat is the STATE-AWARE form the row asks
    # for (field 3 read next) — excluded, so the correct implementation stops tripping the screen.
    ("AF-AP-45", re.compile(r"""ps\b[^\n]*-e?o\b[^\n]*?\b(?:pid|ppid)\b(?![^\n]*\bstat\b)|(?:exists|isdir|is_dir)\(\s*f?["'][^"'\n]*/proc/(?![^"'\n]*/stat\b)"""),
     "process liveness without the STATE column — a killed-but-unreaped child is a zombie, not a survivor; enumerate `stat`, exclude Z, count zombies separately (AF-AP-45)"),
    # AF-AP-43 (2026-09-05): a timestamp sampled before the lock that assigns the sequence number
    # yields inversions under honest concurrency.
    ("AF-AP-43", re.compile(r"""(?:monotonic(?:_ns)?|time\.time|perf_counter(?:_ns)?|datetime\.now|utcnow)\(\)[\s\S]{0,240}?\bwith\s+[\w.]*lock\b"""),
     "ordering field sampled OUTSIDE the ordering lock — take seq and every timestamp in the same critical section (AF-AP-43)"),
    # AF-AP-55 (2026-09-06): an identity read from /proc/<pid>/exe right after spawn is the identity of whatever exec
    # stage exists at that instant — env, a shell wrapper — not of the worker (VERIFY-N5e F1: 9/12 env, 3/3 dash). The
    # reading must be pinned to the first event only the final stage can produce (the first protocol byte).
    ("AF-AP-55", re.compile(r"""readlink\(\s*f?["']/proc/[^"'\n]*/exe"""),
     "identity sampled from /proc/<pid>/exe — pin the reading to the first event only the FINAL exec stage can produce (the first protocol byte) and keep a multi-stage fixture (env shebang / exec wrapper) in the suite (AF-AP-55)"),
    # AF-AP-58 (2026-09-07): a RAISING signal handler installed before the `try:` that catches it turns every event in
    # the gap into an uncaught exception (tee F13: TERM at 51/68 ms -> traceback, rc 1, no status file). Advisory: every
    # install fires; confirm the catching scope starts on the very next statement.
    ("AF-AP-58", re.compile(r"""\bsignal\.signal\(\s*signal\.SIG[A-Z]+\s*,"""),
     "signal handler install — if the handler RAISES, the try that catches it must begin on the NEXT statement and wrap everything after (pre-init every local the except path reads); test the gap deterministically (long window, child-exists poll), never with a fixed delay (AF-AP-58)"),
    # AF-AP-70 (2026-09-08): classify-then-open by pathname — a guard proves what the NAME is at t0 (S_ISREG, is_file,
    # lstat, _refuse_non_regular) and the open at t1 trusts it; a FIFO planted in between hangs the opener forever
    # (VERIFY-D5m F1/F2: the record slot and the pidfile, a 300 ms barrier). The write must be ONE atomic
    # open that validates the fd it got (O_CREAT|O_EXCL|O_NOFOLLOW|O_NONBLOCK, then fstat), never a path check
    # followed by write_text()/open().
    ("AF-AP-70", re.compile(r"""(?:S_ISREG|_refuse_non_regular|\.is_(?:file|dir|symlink)\(\)|os\.l?stat\()[\s\S]{0,400}?(?:\.write_(?:text|bytes)\(|\bopen\((?![^)\n]*O_EXCL))"""),
     "a path classified, then opened by NAME — the type can change between the check and the open (a FIFO hangs it); make the write ONE atomic open (O_CREAT|O_EXCL|O_NOFOLLOW|O_NONBLOCK) and validate the fd (fstat), with a barrier race test (AF-AP-70)"),
    # AF-AP-71 (2026-09-08): a bounded query upstream of a completeness/uniqueness gate — `LIMIT n` before the filter
    # that selects the window makes "exactly one row" true whenever the concurrent row is the (n+1)th
    # (VERIFY-O2 V-O2-1: 49 + 1 + 1 rows, LIMIT 50, PASS).
    ("AF-AP-71", re.compile(r"""\bLIMIT\s+(?:\?|\d+|\$\{?\w+|%s|:\w+)"""),
     "a SQL LIMIT on a query whose rows feed a completeness or uniqueness gate — bound the query by the WINDOW (parameterised, parseable stamps) or fail when the cap is reached; a truncated set cannot prove 'exactly one' (AF-AP-71)"),
    # AF-AP-72 (2026-09-08): a typed upstream field coerced by truthiness/constructor — bool("false") is True, int("1.0")
    # raises, int(1.9) is 1; the malformed upstream shape vanishes at the ONE producer boundary (VERIFY-B2 F2 the relay
    # receipt's `accepted`; VERIFY-G2 F5 the observer uid coerced by int()).
    ("AF-AP-72", re.compile(r"""\b(?:bool|int|float)\(\s*\w+(?:\[[^\]\n]+\]|\.get\([^)\n]*\))\s*\)"""),
     "an upstream field COERCED (bool()/int()/float() of a subscript or .get()) — the string \"false\" becomes True; accept only the declared type (`type(v) is bool`) and name the malformed shape in the receipt/error (AF-AP-72)"),
    # AF-AP-110 (2026-09-22, VERIFY-GOV2c authoring): an isolated gpg homedir (a TemporaryDirectory as GNUPGHOME) auto-starts a
    # gpg-agent that OUTLIVES the deleted directory — one orphan daemon per production call (review.py:136 measured +1 per call).
    ("AF-AP-110", re.compile(r"""GNUPGHOME\s*=|["']GNUPGHOME["']\s*:"""),
     "an isolated gpg homedir (GNUPGHOME) — gpg auto-starts `gpg-agent --homedir <it> --daemon` and the agent OUTLIVES the deleted directory, one orphan per call; tear it down with `gpgconf --homedir <home> --kill all` BEFORE removing the directory (or `--no-autostart` on every call that needs no agent), gated by a before/after process census around ONE production call — never the test fixture's own kill (AF-AP-110)"),
    # AF-AP-115 (2026-09-22, VERIFY-GOV2c-B F1): the executable a verifier TRUSTS resolved from the caller's PATH — a scratch
    # `gpg` printing a shaped GOODSIG line made the real verify_review accept an unsigned record (review.py:114 / :136).
    ("AF-AP-115", re.compile(r"""shutil\.which\(|os\.environ(?:\.get\(|\[)\s*["']PATH["']"""),
     "a trust-boundary executable resolved from the caller's PATH (`shutil.which(...)` / `os.environ[\"PATH\"]` forwarded into the child) — whoever controls the environment supplies the verifier; resolve a FIXED absolute path list once and run the fake-PATH regression through the real consumer (AF-AP-115)"),
    # AF-AP-117 (2026-09-22, VERIFY-J1-0-R1 §0): a fixture step changed the mode of a SHARED system path it did not create —
    # `chmod 755 /tmp /tmp/vj10r1` stripped the sandbox's sticky world-writable /tmp for two hours; make only the scratch root
    # you created traversable, never a system directory.
    ("AF-AP-117", re.compile(r"""\bchmod\b(?:\s+-[A-Za-z]+)*(?:\s+(?:[0-7]{3,4}|[ugoa]*[+-=][rwxstXugo]+))?\s+(?:/tmp|/|/home|/root|/var/tmp)(?=\s|$)"""),
     "a fixture changes the mode of a shared system path it did not create (`chmod … /tmp`, `/`, `/home`, `/root`, `/var/tmp`) — make only the scratch root you created traversable (mkdir -p + chmod on that root), never a system directory (AF-AP-117)"),
    # AF-AP-118 (2026-09-22, VERIFY-K1-g's route measurement): a harness-level fallback chain (Hermes `fallback_providers`)
    # silently re-routed "strict raw id" lanes to cloud models after local errors; a lane's route label is a call_logs
    # measurement (`requested_model`), never the dispatch parameter — any production file that writes the key is reviewed.
    # AF-AP-127 (2026-09-23): a cap applied BEFORE a pattern redaction cuts a straddling secret below its
    # pattern's minimum (or cuts a key block's END line off) and the stub survives — the two transcript
    # exporters did `scrub(text[:cap])`; the J1-1 contract truncated inside normalize before redact.
    ("AF-AP-127", re.compile(r"""\b(?:scrub|redact|sanitize|mask_secrets?|_redact_str)\w*\(\s*[\w.]+\[\s*:[^\]\n]*\]\s*\)"""),
     "a redaction/scrub applied to an already-capped slice (`scrub(x[:cap])`) — a secret straddling the cap falls below its pattern's minimum and its stub survives; redact the WHOLE text, then cap (`scrub(x)[:cap]`) (AF-AP-127)"),
    # AF-AP-159 (2026-09-23, VERIFY-J1-0-R5 V5-05): a PyYAML node's start_mark is its first PROPERTY (&anchor,
    # !!tag), which can sit on the line above the value, so `node.start_mark.line + k` named a line outside it.
    # Widened 2026-09-24 (issue #57 F-2): the sum with the start line as the RIGHT operand is the same line map.
    ("AF-AP-159", re.compile(r"""\.start_mark\.line\s*\+|\+\s*[\w.\[\]]*\bstart_mark\.line\b"""),
     "a line number computed from a node's start_mark — a YAML node starts at its first property (&anchor, !!tag), which can sit on an earlier line than the value; take the scalar TOKEN's line (yaml.scan, keyed by the node's end_mark.index) (AF-AP-159)"),
    ("AF-AP-118", re.compile(r"""\bfallback_providers\b"""),
     "a harness fallback chain (`fallback_providers`) written into a lane/profile config — the chain IS a route: a lane on it is HYBRID until its calls are measured (call_logs `requested_model`), and the harvest line must read the served model (AF-AP-118)"),
    _AF_AP_139,
    # AF-AP-25, the line-parser form (2026-09-23, VERIFY-REPIN-a F11): `parse_lock` / `parse_sbom` in
    # scripts/vendored_manifest.py re.fullmatch each line and SKIP a line no pattern spells out, so one trailing
    # space on a lock line dropped a pin from validate_pin_agreement with no error. The tell: a loop over a file's
    # lines whose body re.match-es / re.fullmatch-es each line (a pattern compiled into a name is not seen).
    ("AF-AP-25", re.compile(r"""\bfor\s+[\w, ]+\s+in\s+[^\n]*(?:\.splitlines\(\)|\.readlines\(\)|\bopen\()[^\n]*:[ \t]*(?:#[^\n]*)?\n[\s\S]{0,400}?\bre\.(?:full)?match\("""),
     "a line loop that regex-matches each line of a structured file (a lock, an SBOM, a config, a registry) — a line no pattern spells out (a trailing space, a YAML comment, a quoted value) is SKIPPED, and a pin silently drops out of the gate that consumes the parse; refuse every non-blank, non-comment line the loop does not recognise, by line number, or parse with a real parser (yaml.safe_load with a duplicate-key refusal) (AF-AP-25)"),
    # AF-AP-89's doubled escape (2026-09-23, the T94 landing; AF-AP-162): T94's poll probe in scripts/pc_lane.sh
    # escaped its PC-side lookups twice inside the double-quoted bridge argument, so the lookups ran in the SANDBOX and
    # the PC received a syntax error; the text-matching test double never ran the probe (AF-AP-162). The tell: a doubled
    # escape before `$(` or before an escaped quote inside a double-quoted bridge / scripts/pc.sh argument.
    # Shell/bridge pattern: ap_screen.py catches it on explicitly-passed .sh files; the .py PostToolUse hook does not fire on shell edits.
    ("AF-AP-89", re.compile(r"""(?:\bbridge|\bpc\.sh)[ \t]+"(?:[^"\\]|\\[\s\S])*?\\\\(?:\$\(|\\")"""),
     r'''a doubled escape (`\\$(` or `\\\"`) inside a double-quoted `bridge` / `scripts/pc.sh` argument — `\\$(` is a literal backslash and then a command substitution that runs in the SANDBOX, so the PC receives a wrong or empty value; escape a remote substitution ONCE (`\$(…)`) and test the rendered remote program by RUNNING it against a fake PC root, never with a double that matches its text; the one legitimate `\\\"` travels verbatim into a quoted heredoc (<<'PY') (AF-AP-89; AF-AP-162)'''),
    # AF-AP-132 (2026-09-23): a line number computed with str.splitlines(), which also breaks on U+2028, U+2029, U+0085,
    # \x0b, \x0c and \x1c-\x1e, so a tool that reports file:line reads every later line late (report_lint graded 28 of
    # J1-2-R1's 56 citations MISS, two lines late after a literal separator). The tells: enumerate over a .splitlines()
    # call; a list bound from .splitlines() and enumerated with a start within 15 lines; a literal U+2028/U+2029/U+0085
    # on a line that decoded (a binary read with errors="replace" holds U+FFFD: 275 false hits in 11 .gz evidence files).
    ("AF-AP-132", re.compile(r"""\benumerate\(\s*[^\n]*?\.splitlines\(\)|^[ \t]*(\w+)[ \t]*=(?!=)[^\n]*\.splitlines\(\)[^\n]*\n(?:[^\n]*\n){0,15}?[^\n]*\benumerate\(\s*\1(?:\[[^\]\n]*\])?\s*,|^(?![^\n]*\ufffd)[^\n]*?[\u2028\u2029\u0085]""", re.MULTILINE),
     r"""a line number computed with `.splitlines()` (enumerate over it, or over a list taken from it), or a literal U+2028/U+2029/U+0085 in source — splitlines also breaks on those, on \x0b, \x0c and \x1c-\x1e, so a tool that reports file:line numbers every later line late against git, grep and Python, and the literal is invisible; number lines on "\n" only (`text.split("\n")`) and write a separator as its escape (AF-AP-132)"""),
    # AF-AP-141 (2026-09-23, CI-GATE-R1): a history-walk exit code read as a yes/no. merge-base --is-ancestor exits 1
    # with `error: Could not read <sha>` when its walk meets a missing object, even for a TRUE ancestor (git 2.43,
    # measured), and cat-file -e fails the same way on a corrupt or unreadable object. The tells: either call in an argv
    # (a line that binds the call's error text, `rc, _, err = ...`, reads it and stays quiet), or on a shell command line.
    # Shell/bridge pattern: ap_screen.py catches it on explicitly-passed .sh files; the .py PostToolUse hook does not fire on shell edits.
    ("AF-AP-141", re.compile(r"""^(?=[^\n]*?(?:["']--is-ancestor["']|["']cat-file["'][ \t]*,[ \t]*["']-e["']))(?![^\n]*\b\w+[ \t]*,[ \t]*\w+[ \t]*,[ \t]*(?!_\b)\w+[ \t]*=(?!=))[^\n]*?(?:["']--is-ancestor["']|["']cat-file["'][ \t]*,[ \t]*["']-e["'])|\bgit\b[^\n;|&]*?\b(?:merge-base[ \t]+--is-ancestor|cat-file[ \t]+-e)\b""", re.MULTILINE),
     "a `merge-base --is-ancestor` or `cat-file -e` exit code used as a yes/no — exit 1 also comes with `error: Could not "
     "read <sha>` when the walk meets a missing object (even for a TRUE ancestor), and cat-file -e fails the same way on a "
     "corrupt object; read stderr with the code (exit 1 with no `error:`/`fatal:` line is a no, anything else means git "
     "cannot tell) or prove the history complete first (`rev-list --quiet <sha>`) (AF-AP-141)"),
    # AF-AP-144 (2026-09-23, VERIFY-B9 F-13): a proof checker promises one named failure line and rc 1 for every refused
    # bundle, but a raw parse call whose error main does not catch dies with a traceback and no reason line. Scoped to
    # proofs/*/check_*.py by the hook's main (_PathScoped). Not checked: whether main catches everything or the reader
    # converts the error, so a checker that fails closed through a catch-all is a false hit here.
    ("AF-AP-144", _PathScoped(re.compile(r"""(?:^|/)proofs/[^/]+/check_[^/]+\.py$"""),
                              re.compile(r"""\bjson\.loads\(|\byaml\.safe_load\(|\.decode\(|\.read_text\(\)""")),
     "a raw parse call (json.loads, yaml.safe_load, .decode, a default-encoding .read_text()) in a proof checker — unless "
     "main catches it or the reader converts it, a malformed evidence file ends in a traceback, rc 1 and no failure_reason "
     "line (refused by accident, unnamed, and a spec leg that expects a reason cannot match it); convert the parse error "
     "to the checker's named failure at the reader (AF-AP-144)"),
    # AF-AP-145 (2026-09-23, VERIFY-E3 F3): an EXIT-trap cleanup a second signal can abort. Cleanup runs with INT and TERM
    # live, so a second signal (a double Ctrl-C, a stop sent to the group) leaves the teardown half done; E3-R1 measured
    # that the ignore is needed first in cleanup AND first in each INT/TERM handler. The tells: a function an EXIT trap
    # names whose body does not open with the ignore (a `$?` capture or a comment may come first), and an INT/TERM
    # handler string that does not open with it (_ExitTrapCleanup). Not seen: a one-line function body. Refined by
    # VERIFY-GW1-R1 (R1-F-1): a bare `exit` after the handler traps is the third tell (one signal, not two).
    # Shell pattern: ap_screen.py catches it on explicitly-passed .sh files; the .py PostToolUse hook does not fire on shell edits.
    ("AF-AP-145", _ExitTrapCleanup(),
     r"""an EXIT-trap cleanup function, or an INT/TERM handler, that does not open with the signal ignore (`trap '' INT TERM`) — a second signal while cleanup runs (a double Ctrl-C, a stop sent to the process group) aborts the teardown half done and leaves host state (namespaces, rules, units, restored configs) behind; make the ignore the first command of the cleanup function AND of each INT/TERM handler (`trap 'trap "" INT TERM; exit 143' TERM`): E3-R1 measured the cleanup ignore alone still aborting 26 of 60 trials — AND before every exit after the handler traps (`leave() { trap '' INT TERM; exit "$1"; }`): one signal right after a bare exit runs the handler's exit inside the EXIT trap (VERIFY-GW1-R1: 25 of 150) (AF-AP-145)"""),
    # AF-AP-149 (2026-09-23, VERIFY-AF-AP-127 F1): a private-key redaction rule written for one label spelling. A rule
    # that wants PRIVATE KEY right before the closing dashes misses GnuPG's armor (PGP PRIVATE KEY BLOCK, the PGP 2.x
    # PGP SECRET KEY BLOCK), and a rule that needs the END line misses a block cut at its source: the body reaches the
    # output whole (9 of 15 body lines through both transcript exporters). The tell, on a BEGIN line written as a regex
    # (a class, `.*`, `.+`): no SECRET/BLOCK alternative, or an END with no end-of-text (\Z) alternative on the line.
    ("AF-AP-149", re.compile(r"""-----BEGIN (?=[^\n]*?(?:\.\*|\.\+|\[\\s\\S\]|\[A-Z|\[\^))(?:(?![^\n]*(?:SECRET|BLOCK))[^\n]*?PRIVATE KEY-----|(?![^\n]*\\Z)[^\n]*?-----END)"""),
     r"""a private-key block rule written for one label spelling — a pattern that wants PRIVATE KEY right before the closing dashes misses GnuPG's armor (PGP PRIVATE KEY BLOCK, PGP 2.x PGP SECRET KEY BLOCK), and one that needs the END line misses a block cut at its source, so the body lines reach the output whole; match (?:PRIVATE|SECRET) KEY(?: BLOCK)? and end at the END line OR at the end of the text (|\Z) (AF-AP-149)"""),
    # AF-AP-152 (2026-09-23; J1-1-R1 D-3, task #187): a scrubber regex whose cost grows faster than its input. A repeated
    # group whose body ends with a character its own quantified class also takes backtracks exponentially (an
    # upper-case name-prefix group repeated under *: 8.14 s at 26 repeats, doubling per repeat); an alternative that
    # opens with a quantified class before a literal re-scans a long run from every start (a compound `...key` name rule:
    # 17.4 s on a 40k run, 0.005 s behind a lookbehind). Not seen: \w-style shorthands in the second form, a hand-written
    # scanner (the third instance), whether the pattern runs over free text.
    ("AF-AP-152", re.compile(r"""\(\?:[^()\n]*?(?:\[(?!\^)[^\]\n]*?([\w-])[^\]\n]*\][*+]\1|\\w[*+]\w|(?:\\S|\.)[*+][^\s()\\|])\)(?:[*+]|\{\d*,\d*\})|(?<!\\)\|\[[^\]\n]+\][*+](?:\[[^\]\n]+\])?[A-Za-z0-9_]{2}"""),
     "a regex whose cost grows faster than its input — a repeated group whose body ends with a character its own "
     "quantified class also matches backtracks exponentially, and an alternative that opens with a quantified class "
     "before a literal re-scans a long run from every start position; one long line then stalls a scrub that runs in "
     "the commit hook and on every push: make the separator unambiguous, anchor the alternative (a lookbehind such as "
     "`(?<![A-Za-z0-9])`) and pin a timing test on a long run (AF-AP-152)"),
    # AF-AP-175 (2026-09-24, J1-3 F-03): a moving ref resolved per read. Each git call that names HEAD sees whatever
    # commit it points at then, so a commit landing mid-run mixes two commits' bytes in one record (45 of 300 racer
    # runs). The registry asks for a per-file count (two or more reads); a row sees one hunk or one file's text and
    # counts nothing, so this is the line form: every quoted HEAD literal. The count is the reader's (ap_screen.py
    # prints the hits per file).
    ("AF-AP-175", re.compile(r"""["']HEAD(?=["':^~@{])"""),
     "a quoted HEAD passed to git — if this process names the ref more than once (an admission check and a later read, "
     "ls-tree then cat-file), a commit landing mid-run mixes two commits' bytes in one record; resolve it once "
     "(`rev-parse --verify HEAD^{commit}`), thread the SHA to every read, and test with the ref moved between the first "
     "and the last read (AF-AP-175)"),
    # AF-AP-177 (2026-09-24, VERIFY-J1-3-R1 follow-up 1): a parsed JSON value used as a hash key before its type is
    # checked. A list or an object there raises TypeError (unhashable) and crashes the run instead of refusing the record
    # (J1-3's harvester: rc 1, no harvest line). The tells: a .get(...) value tested with `in {…}`, and a name bound
    # from a .get(...) and tested with `in {…}` within 8 lines, neither with an isinstance(…, str) check first. Not seen:
    # a set held in a name (`in ALLOWED`), a subscript read (`rec["k"] in {…}`).
    ("AF-AP-177", re.compile(r"""^(?=[^\n]*?\.get\()(?![^\n]*\bisinstance\([^\n]*?,[ \t]*str[ \t]*\))[^\n]*?\.get\([^()\n]*\)[ \t]+(?:not[ \t]+)?in[ \t]+\{|^[ \t]*(\w+)[ \t]*=(?!=)[^\n]*?\.get\([^()\n]*\)[^\n]*\n(?:(?![^\n]*\bisinstance\([ \t]*\1[ \t]*,[ \t]*str[ \t]*\))[^\n]*\n){0,8}?(?![^\n]*\bisinstance\([ \t]*\1[ \t]*,[ \t]*str[ \t]*\))[^\n]*?\b\1[ \t]+(?:not[ \t]+)?in[ \t]+\{""", re.MULTILINE),
     "a value read from parsed JSON tested with `in {…}` before its type is checked — a list or an object there raises "
     "TypeError (unhashable) and crashes the run instead of refusing the record; check `isinstance(v, str)` (or the "
     "declared type) first, refuse the record by name, and give the parser's hostile-input tests a list and an object "
     "in every field it tests by membership (AF-AP-177)"),
    # AF-AP-196 (2026-09-24, VERIFY-FT1 F-1): a trained artifact saved with no finiteness check on what is saved. The
    # trainer checked the loss BEFORE each step, so the last step's NaN weights (31 of 31 tensors after one `--lr inf`
    # step) were saved with rc 0 and the evaluator scored them BLOCKER 7/7. The tell: a tensor save in the hunk.
    ("AF-AP-196", re.compile(r"""\b(?:torch\.save|save_file|save_pretrained|np\.save)\("""),
     "a model artifact is saved — is EVERY saved tensor (and the final metric) checked finite before this write, with a "
     "refusal that writes nothing? A guard on a step's input does not cover the step's output (AF-AP-196)"),
    # AF-AP-197 (2026-09-24, VERIFY-FT1 F-6): a precondition checked after the work it protects. The free-space refusal
    # ran at save time, after training, so a full disk threw the trained weights away. The tell: a free-space probe.
    ("AF-AP-197", re.compile(r"""\b(?:disk_usage|statvfs)\("""),
     "a free-space probe — does it run BEFORE the expensive work it protects (the size is usually known up front) as "
     "well as at the write? A check after the work only chooses which loss you take (AF-AP-197)"),
    # AF-AP-200 (2026-09-24, task #243): a parser of git's diff text keyed on a header prefix. The first stale_ids.py
    # took a path only from `+++ b/` and skipped every added line it could not attribute, so `diff.noprefix`, a quoted
    # path and an added line starting `++` each hid a stale citation and the push went through.
    ("AF-AP-200", re.compile(r"""startswith\(\s*["'](?:\+\+\+|--- a/)"""),
     "a diff header parsed by its prefix — pass explicit --src-prefix=a/ --dst-prefix=b/, treat `+++` as a header only "
     "between `diff --git` and the first `@@`, and never drop an added line whose path did not parse: a diff.noprefix "
     "config, a quoted path or an added line starting `++` otherwise hides it (AF-AP-200)"),
    # AF-AP-201 (2026-09-24, task #241): a request option that makes the shared model server allocate outside its
    # reserved memory. A transport probe sent `prompt_logprobs: 0` through OmniRoute to the vLLM `qwen` container: a
    # float32 log-softmax over the whole vocabulary for every prompt token (758 MiB, 148 MiB free) OOM-killed the engine
    # and systemd restarted qwen.service for every user. The tell: the option set as a key or a keyword.
    ("AF-AP-201", re.compile(r"""(?:["']|\b)(?:prompt_logprobs|best_of)["']?\s*[:=](?!=)"""),
     "a request option that makes the model server compute output for every prompt token (prompt_logprobs) or extra "
     "sequences (best_of) — vLLM allocates it OUTSIDE its reserved memory; on the PC's 3090 `prompt_logprobs` "
     "OOM-killed the engine and restarted qwen for every user: never send it to a shared server (AF-AP-201)"),
    # AF-AP-204 (2026-09-25, JEV-FIT audit A): one Claude Code project directory assumed for session transcripts. The
    # harness files a session under the slug of its launch cwd, and this container holds two; scripts/orient.sh read the
    # stale -home-user-agent-factory file (2026-09-22) at every session start. The tell: a literal project slug path.
    ("AF-AP-204", re.compile(r"""\.claude/projects/-[A-Za-z0-9]"""),
     "a hardcoded Claude Code project directory — sessions land under the slug of their launch cwd, and a container "
     "can hold several: glob /root/.claude/projects/*/ (the newest file for the current session, every file for an "
     "export of all session data) (AF-AP-204)"),
    # AF-AP-223 (2026-09-25, the S1-L1-R1 premise run): a mutation harness scored KILLED from the exit code alone, with
    # no unmutated control run. Its --basetemp parent had been deleted, every run errored at setup ("2 passed, 1 error"),
    # and all 8 mutants read KILLED where 7 survive. The tell: a killed verdict taken from returncode (!= 0, or bare).
    ("AF-AP-223", re.compile(r"""(?i)\bkilled\b[^#\n]*\breturncode\b(?:\s*!=\s*0\b|\s+else\b|\s*\)|\s*$)"""),
     "a mutation verdict read from the exit code alone — pytest also exits non-zero on a setup or collection error, "
     "an internal error, a usage error and no tests collected, so a broken setup reads as every mutant KILLED: count a "
     "kill only when a test FAILED, score an error-only run INVALID, and run the unmutated control first (AF-AP-223)"),
    # AF-AP-224 (2026-09-25, L5's adjacent finding, reproduced with fake keys): transcript_export's provider-key rules
    # start with \b, so a key glued to a preceding `_`, letter or digit (`mcp__srv__sk-…`, `my_sk-…`) passed unscrubbed
    # unless its whole run reached the 40-character opaque rule. The tell: a key-prefix rule anchored on \b.
    ("AF-AP-224", re.compile(r"""\\b(?:\(\?:)?(?:sk-|gh[opusr][|_)]|AIza|xox)"""),
     "a secret-shape rule anchored on a word boundary — `\\b` needs a non-word character before the key, so a key glued "
     "to a preceding `_`, letter or digit passes: anchor on `(?<![A-Za-z0-9])` (an underscore then counts as a "
     "separator), test the glued forms, and keep a value check (known_values_check.py) behind the shapes (AF-AP-224)"),


]

# V6 (2026-09-02). Test files skip AP_SCREEN (production-only), so AP-66 gets its
# own screen: a direct attribute reassignment on something other than self/cls
# (`EM.emit = spy`, `setattr(mod, "emit", spy)`) with no restore leaks into every
# later test in the process. monkeypatch.setattr never matches (method call).
# AP-63/64/65 have no regex shape — the registry names their instruments.
TEST_SCREEN = [
    # AF-AP-11 (2026-09-03): a repo CLI spawned through its shebang runs on whatever python3 PATH
    # finds — the PC's system python carried jsonschema and minted a green the venv could not.
    ("AF-AP-11", re.compile(r"subprocess\.(?:run|Popen|check_output|check_call|call)\(\s*\[\s*str\("),
     "CLI spawned through its shebang — inherits the host interpreter's site-packages, not the declared toolchain; put sys.executable first (AF-AP-11)"),
    # AF-AP-33 (2026-09-05): an unmanaged OmniRoute squatted :20128 serving the wrong DB while
    # /api/health said 200 — port-level health is blind to WHICH instance answers.
    ("AF-AP-33", re.compile(r"""/(?:api/)?health["']"""),
     "health-endpoint-only liveness — a squatting duplicate answers 200 while serving the wrong dataset; also assert ownership (pid -> cgroup/pidfile) and a dataset-discriminating probe (AF-AP-33)"),
    # AF-AP-34 (2026-09-04): four `pkill -x buzz-relay` aimed at an isolated relay restarted the
    # owner's production relay container — a bare binary name is shared across installs.
    ("AF-AP-34", re.compile(r"\b(?:pkill|killall)\b|\bkill\b[^\n]*\$\(\s*pgrep"),
     "name-based process kill — matches other installs and container processes on a shared host; kill the PID from YOUR pidfile after /proc/<pid>/exe or the cgroup confirms ownership (AF-AP-34)"),
    # AF-AP-35 (2026-09-04): a redaction built from the secret's VALUE echoed the value into the log.
    ("AF-AP-35", re.compile(r"(?:re\.sub|\.replace)\(\s*(?:re\.escape\()?\s*\w*(?:key|secret|token|password|passwd)\w*\b", re.I),
     "redaction keyed on a secret's VALUE — the value lands in argv/output/transcript; redact by KEY NAME or pattern class and dry-run on a dummy (AF-AP-35)"),
    # AF-AP-44 (2026-09-06): a module-scope venue probe that can RAISE (PermissionError under CI's non-root
    # identity) aborts collection for the whole job — probe inside try/except OSError, return absent.
    ("AF-AP-44", re.compile(r"""skipif\(\s*not\s+[\w.]+(?:\([^()\n]*\))?\.(?:exists|is_file|is_dir)\(\)"""),
     "module-scope venue probe in a skipif — Path.exists() RAISES PermissionError under another identity and kills collection; wrap the probe (return absent on OSError) (AF-AP-44)"),
    # AF-AP-48 (2026-09-06): a set-shaped reason assertion — `assert reason in {c1, c2, …}` where the reason is
    # deterministic — is the set-shaped sibling of `ok or <substring>`: a reordering of the checks, or a different pin
    # failing first, passes unnoticed (VERIFY-N5c F5 on the coordinator's own producer-pin test).
    ("AF-AP-48", re.compile(r"""assert\s+[^\n=]+?\s+in\s*\{\s*["']"""),
     "set-shaped reason assertion — assert the ONE exact value; a set is admissible only for a genuinely nondeterministic outcome, each member with its own producing test (AF-AP-48)"),
    # AF-AP-59 (2026-09-07): a world-scoped process sweep in a test (`pgrep -f <pattern>` over the whole box, a bare
    # `ps -e` census) asserts an empty world that only a serial venue provides; a sibling xdist worker's process lands in
    # it (the PC gate, run 20260907T161133Z). Own-pid checks (`pgrep -P <own pid>`, /proc/<own pid>/stat) do not match.
    # VERIFY-B5h F2/F3a (2026-09-07): the row must carry pkill (the member of the class that KILLS — a deleted hand-typed
    # pin had caught it) and a -f that is not adjacent to the command (`["pgrep", "-a", "-f", …]`). `pgrep -P <pid>` stays legal.
    ("AF-AP-59", re.compile(r"""["']p(?:grep|kill)["'](?:\s*,\s*["']-[a-zA-Z]+["'])*\s*,\s*["']-f["']|\bp(?:grep|kill)\s+(?:-[a-zA-Z]+\s+)*-f\b|["']ps["']\s*,\s*["']-e[a-z]*["']"""),
     "world-scoped process sweep in a test — the result includes every sibling worker's processes; assert your OWN pids (from a pid file / pgrep -P <own pid> / /proc/<own pid>/stat) exactly and the admissibility of the rest, never emptiness (AF-AP-59)"),
    # AF-AP-57 (2026-09-07): a fake that picks its behaviour by call ORDINAL ("call 1 fails, call 2 succeeds") encodes the
    # current loop shape — the first thing a mutant changes (DL-INLINE survived a call-count killer: the mutated loop's
    # 2nd attempt landed on the success ordinal with the identical error text). Gate fakes on PHASE/state instead.
    # VERIFY-N5h F11 (2026-09-08): the alternation offered `[0]` to `calls`/`attempts` but not to `call_count`,
    # so `if _call_count[0] == 1:` — the commonest spelling — never matched: the screen reported ONE ordinal
    # gate on the probe test's parent where a broad grep found FIVE across four fakes. The subscript is now
    # optional for every name, so the row screens the class rather than three of its spellings.
    ("AF-AP-57", re.compile(r"""\bif\s+(?:not\s+)?\w*(?:calls?|call_count|n_calls|attempts?|count)\s*(?:\[0\])?\s*(?:==|!=|<=|>=|<|>)\s*\d"""),
     "ordinal gate in a fake — behaviour selected by call count encodes the loop shape a mutant changes; gate on observable PHASE/state (a thread the code starts later, a file the later stage writes) and assert the mechanism from the wrapper (AF-AP-57)"),
    ("AP-66", re.compile(r"^\s*(?:(?!self\.|cls\.)[A-Za-z_][\w.]*\.\w+\s*=\s*(?!=)|setattr\(\s*(?!self\b|cls\b)\w+\s*,)", re.MULTILINE),
     "direct attribute reassignment in a test — leaks into every later test unless restored; use monkeypatch.setattr or a finally-restoring context manager (AP-66)"),
    # TN3-F4 (2026-09-02): a blanket except in a test hollows any call-count
    # assertion — the loop aborting on item 1 satisfies `call_count == 1` too.
    ("AP-70", re.compile(r"except\s*(?:\([^)\n]*\bException\b[^)\n]*\)|Exception)\s*:\s*\n\s*(?:pass|continue)\b"),
     "blanket except swallowing the run under test — a call-count/once assertion after it cannot tell hoisted from aborted; size the fixture and drop the swallow, or add an iteration counter (AP-70)"),
    # AF-AP-60 (2026-09-07, VERIFY-D5k F3): a `grep -c` guard read an empty stdout as zero hits — a grep without -P,
    # a renamed file or a bad PATH turns the guard green over the very defect it bans.
    ("AF-AP-60", re.compile(r"""\[\s*["']grep["']\s*,"""),
     "grep-based guard in a test — an empty stdout on ANY tool failure reads as zero hits; assert r.returncode in (0, 1) or walk the AST of the parsed files instead (AF-AP-60)"),
    # AF-AP-61 (2026-09-07, VERIFY-D5k F4): a regex over source text bans one SPELLING of the class; the two-line
    # rewrite `_b = …["body"]; assert _b != MARKER` restored the exact hollow green the ban exists to prevent.
    ("AF-AP-61", re.compile(r"""re\.(?:compile|search|findall|finditer)\(\s*r?["'][^"'\n]*\bassert\b|r?["']\^\\s\*assert\\s"""),
     "class ban as a source-text pattern — bans one spelling, not the class; ban it structurally (ast.Compare + ast.NotEq naming the marker) and make every 'served' test assert the positive recorded value (AF-AP-61)"),
    # AF-AP-80 (2026-09-15): a source-text pin as the ONLY guard of a behavioral property — three instances in one day
    # (a presence check where exclusivity was claimed; a flag listed in a source inventory dropped from the call it guards;
    # a file-wide `close_fds=True` substring satisfied by a comment). Pair every such pin with a behavioral negative control
    # and scope it to the AST node it guards.
    ("AF-AP-80", re.compile(r"""\bassert\b[^\n]*\bin\s+(?:[^\n]*?\.read_text\(\)|(?:[A-Za-z_][\w.]*\.)?(?:source|src|SOURCE|SRC|module_text|file_text)\b|ast\.unparse\()"""),
     "a source-text pin (`in …read_text()` / `in source` / `in ast.unparse(...)`) standing in for a behavioral property — a comment or a second call satisfies it; pair it with a negative control that fails when the PROPERTY fails and scope the pin to the AST node (AF-AP-80)"),
     # AF-AP-87 (2026-09-15, QM0-b): a `! kill -0` liveness gate reads a zombie (Z/defunct, unreaped) PID as alive.
     # Shell-test pattern: ap_screen.py catches it on explicitly-passed .sh files; the .py PostToolUse hook does not fire on shell edits.
     ("AF-AP-87", re.compile(r"""!\s*kill -0\b"""),
      "a `! kill -0 <pid>` liveness gate reads a zombie (Z/defunct, unreaped) PID as ALIVE — treat dead as absent OR /proc/<pid>/stat=Z (an is_dead helper), or pair the pid with a persisted terminal rc, never kill -0 alone (AF-AP-87)"),
    # AF-AP-181 (2026-09-24, CI run #1026): a race handler whose fallback value its own assert rejects. The except
    # branch anticipates the exists-then-read race on /proc and assigns "gone"; the assert that follows accepts only
    # "Z", so the race the handler was written for still fails the test.
    ("AF-AP-181", re.compile(r"""except\b[^\n]*:[ \t]*\n[ \t]*(\w+)[ \t]*=[ \t]*(["'])([^"'\n]*)\2[ \t]*\n(?:[^\n]*\n){0,2}?[ \t]*assert[ \t]+\1[ \t]*==[ \t]*(["'])(?!\3\4)[^"'\n]*\4"""),
     "an except branch assigns a fallback that the next assert rejects: the race it handles still fails; read once through one helper and assert membership of every acceptable value (`in (\"Z\", \"gone\")`)"),
    _AF_AP_139,  # the same row as in AP_SCREEN: the registry's instance was a test stand-in (tests/test_s0_05_egress.py)
]

MAX_SYMBOLS = 2
PROBE_TIMEOUT = 8

# Rows whose tell needs the WHOLE file, not just the hunk (ECHO 2026-09-02,
# I3g: AP-60 free-variable-resolved-only-in-caller, AP-61 np/pd used with
# no module-level import). Both are hard-blocked at commit time by
# scripts/hooks/pre-commit (pyflakes delta); this is the same detector at
# edit time. A regex "is the name bound anywhere in the file" tell was tried
# first and MISSED the real AP-60 shape (the name WAS bound — inside main(),
# a different scope), so scoping is left to pyflakes, not re-implemented.
_NP_PD = re.compile(r"(?<![\w.])(np|pd)\.")
_VENV_PY = os.environ.get("AF_VENV", "/root/venv-agent-factory") + "/bin/python"  # PC lanes export AF_VENV


def _pyflakes_msgs(py: str, text: str) -> dict:
    """pyflakes messages for one source text, line numbers dropped (a hunk
    above shifts every line; the delta compares WHAT, not WHERE)."""
    p = subprocess.run([py, "-m", "pyflakes"], input=text, capture_output=True,
                       text=True, timeout=PROBE_TIMEOUT)
    out: dict = {}
    for l in p.stdout.splitlines():
        parts = l.split(":", 3)  # <stdin>:LINE:COL: message
        msg = parts[3].strip() if len(parts) == 4 else l.strip()
        out[msg] = out.get(msg, 0) + 1
    return out


def pyflakes_delta(fp: str, src: str) -> list[str]:
    """NEW pyflakes hits in this file vs its HEAD version. [] when the venv
    pyflakes is absent or anything fails — a tell, never a blocker. Every probe
    of the venv path is inside the try: under another identity (a PC lane user,
    /root mode 0550) Path.exists() RAISES PermissionError (AF-AP-44)."""
    try:
        if not Path(_VENV_PY).exists():
            return []
        root = subprocess.run(["git", "rev-parse", "--show-toplevel"], capture_output=True, text=True,
                              cwd=Path(fp).parent, timeout=PROBE_TIMEOUT).stdout.strip()
        rel = str(Path(fp).resolve().relative_to(root)) if root else fp
        shown = subprocess.run(["git", "show", f"HEAD:{rel}"], capture_output=True, text=True,
                               cwd=root or None, timeout=PROBE_TIMEOUT)
        base = _pyflakes_msgs(_VENV_PY, shown.stdout) if shown.returncode == 0 else {}
        now = _pyflakes_msgs(_VENV_PY, src)
    except Exception:
        return []
    new = {m: n - base.get(m, 0) for m, n in now.items() if n > base.get(m, 0)}
    out = []
    for m in sorted(new):
        if m.startswith("undefined name") and m.split("'")[1] not in ("np", "pd"):
            tag = "AP-60 "
        elif m.startswith("undefined name") or "imported but unused" in m:
            tag = "AP-61 "
        else:
            tag = "LINT  "
        out.append(f"  {tag} NEW pyflakes hit vs HEAD: {m}" + (f" (x{new[m]})" if new[m] > 1 else "")
                   + " — the pre-commit hook will BLOCK on this")
    return out


def file_aware_screen(hunk: str, src: str) -> list[str]:
    out = []
    mods = {"np": "numpy", "pd": "pandas"}
    for alias in sorted({m.group(1) for m in _NP_PD.finditer(hunk)}):
        if not re.search(rf"^import {mods[alias]} as {alias}\b", src, re.M):
            out.append(f"  AP-61  `{alias}.` used but no module-level `import {mods[alias]} as {alias}` in THIS file — "
                       "an import in a sibling module / docstring / embedded script string does not bind it (AP-61)")
    return out


def enclosing_symbols(src: str, needle: str) -> list[str]:
    """Names of the innermost def/class containing the first occurrence of
    needle's first non-empty line. Best-effort; [] on any failure."""
    first_line = next((l for l in needle.splitlines() if l.strip()), "")
    if not first_line:
        return []
    pos = src.find(first_line.strip())
    if pos < 0:
        return []
    lineno = src.count("\n", 0, pos) + 1
    try:
        tree = ast.parse(src)
    except SyntaxError:
        return []
    hits: list[tuple[int, str]] = []
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            end = getattr(node, "end_lineno", node.lineno)
            if node.lineno <= lineno <= end:
                hits.append((end - node.lineno, node.name))
    hits.sort()  # innermost (smallest span) first
    return [name for _, name in hits[:MAX_SYMBOLS]]


def chronology(symbol: str, fp: str, n: int = 4) -> list[str]:
    """Last n edits to the function (git log -L funcname), one line each —
    the owner's 'histogram at a glance'. [] on any failure/timeout."""
    try:
        out = subprocess.run(
            ["git", "log", "-n", str(n), "--format=%h %ad %s", "--date=short",
             "-L", f":{symbol}:{fp}", "--no-patch"],
            capture_output=True, text=True, timeout=PROBE_TIMEOUT,
        ).stdout
        return [l for l in out.splitlines() if l.strip()][:n]
    except Exception:
        return []


def file_chronology(fp: str, n: int = 3) -> list[str]:
    try:
        out = subprocess.run(
            ["git", "log", "-n", str(n), "--format=%h %ad %s", "--date=short", "--", fp],
            capture_output=True, text=True, timeout=PROBE_TIMEOUT,
        ).stdout
        return [l for l in out.splitlines() if l.strip()][:n]
    except Exception:
        return []


def gitnexus_impact(symbol: str) -> str:
    try:
        out = subprocess.run(
            ["gitnexus", "impact", symbol],
            capture_output=True, text=True, timeout=PROBE_TIMEOUT,
        ).stdout
        d = json.loads(out[out.index("{"):])
        if d.get("risk") in (None, "UNKNOWN"):
            return f"{symbol}: not in index (new symbol? index rebuilding)"
        s = d.get("summary", {}) or {}
        return (f"{symbol}: risk {d.get('risk')} · {s.get('direct', '?')} direct callers · "
                f"{s.get('processes_affected', '?')} flows")
    except Exception:
        if Path("/tmp/gitnexus-analyze.lock").exists():
            return f"{symbol}: index rebuilding (post-commit reanalyze) — impact unmapped THIS edit; re-check before commit"
        return f"{symbol}: impact unavailable (instrument down — unmapped, not safe)"


def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except Exception:
        return 0
    tin = payload.get("tool_input") or {}
    tool = payload.get("tool_name", "")
    fp = tin.get("file_path", "")
    if not fp.endswith(".py") or "sandbox-kit/" in fp:
        return 0
    if "/tests/" in fp:
        # test files get only the test-specific screen (AP-66); no impact/history
        if tool == "Read":
            return 0
        hunk = tin.get("new_string") or tin.get("content") or ""
        hits = [f"  {ap_id:6s}{msg}" for ap_id, rx, msg in TEST_SCREEN if rx.search(hunk)]
        if hits:
            print(f"EDIT SNAPSHOT · {Path(fp).name}\n  registry screen (TELLS, not verdicts):")
            print("\n".join(hits))
        return 0
    p = Path(fp)
    if not p.is_file():
        return 0

    # READ branch (owner directive 2026-08-25, "histogram at a glance"): a
    # lightweight file-level chronology on every production-code read — the
    # full per-symbol treatment stays on edits, where the stakes are.
    if tool == "Read":
        hist = file_chronology(fp)
        if hist:
            print(f"READ CONTEXT · {p.name} — last {len(hist)} changes "
                  f"(full story: scripts/why.sh {fp} [symbol]):")
            for h in hist:
                print(f"  {h}")
        return 0

    new_code = tin.get("new_string") or tin.get("content") or ""
    if not new_code.strip():
        return 0
    try:
        src = p.read_text()
    except Exception:
        return 0

    lines = [f"EDIT SNAPSHOT · {p.name}"]
    syms = enclosing_symbols(src, new_code)
    if syms:
        for s in syms:
            lines.append("  impact  " + gitnexus_impact(s))
        hist = chronology(syms[0], fp)
        if hist:
            lines.append(f"  history {syms[0]} — last {len(hist)} edits "
                         f"(why: scripts/why.sh {fp} {syms[0]}):")
            lines.extend(f"    {h}" for h in hist)
    else:
        lines.append("  impact  module-level edit (no enclosing symbol resolved)")
        hist = file_chronology(fp)
        if hist:
            lines.append("  history file — last changes:")
            lines.extend(f"    {h}" for h in hist)

    flagged = []
    for ap_id, rx, msg in AP_SCREEN:
        if isinstance(rx, _PathScoped):  # only here is the edited file's path known
            rx = rx.for_path(fp)
        if rx.search(new_code):
            flagged.append(f"  {ap_id:6s}{msg}")
    flagged.extend(file_aware_screen(new_code, src))
    flagged.extend(pyflakes_delta(fp, src))
    if flagged:
        lines.append("  registry screen (verify each — these are TELLS, not verdicts):")
        lines.extend(flagged)
    else:
        lines.append("  registry screen: no mechanical anti-pattern tells in this hunk")

    print("\n".join(lines))
    return 0


if __name__ == "__main__":
    sys.exit(main())
