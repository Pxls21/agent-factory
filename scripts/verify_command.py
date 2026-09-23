#!/usr/bin/env python3
"""Classify whether a shell command is a test/build/lint check whose exit status
reaches the caller.

Port of qkal/canny @ f2c5e53, src/checks.ts:8-93.

Regex semantics: every regex here runs with ``re.ASCII`` -- the VERIFY list,
the three not-a-check patterns, the six inline calls in ``executed``,
``is_verify`` and ``with_pipefail``, the C1-A2 patterns, and every user
pattern -- so ``\\b``, ``\\w`` and ``\\s`` match only ASCII characters.  For
``\\b`` and ``\\w`` that is the JS behavior (no ``u`` flag).  JS ``\\s``
matches Unicode spaces (NBSP, U+2028) while Python ``\\s`` under ``re.ASCII``
does not; bash does not split words on NBSP either, so here a Unicode space
inside ``set -o pipefail`` does not make a ``set`` statement, and a Unicode
space before ``#`` does not start a comment.  A test row for U+00A0 before
``--help`` pins this choice.  The flag has a cost, declared below: ``\\b``
after ``pipefail`` also matches before a non-ASCII letter.

Deviation 1 from Canny: an invalid regex string in *patterns* raises
``ValueError`` naming the bad pattern.  Canny's ``safeRegex`` silently turns it
into "never matches"; here a silently dead pattern is a fail-soft that we refuse.
"Invalid" means invalid in Python's ``re`` dialect, which is not JS's: an inline
flag such as ``(?i)`` is valid here and dead in Canny, and a variable-length
lookbehind such as ``(?<=a+)`` is valid in Canny and raises here.

Deviation 2 from Canny (AMENDMENT C1-A2): a status-integrity pre-filter,
because C2 (not built yet) will consume ``is_verify`` as a gate.  ``is_verify``
returns False when, in the executed text: (a) the last segment contains ``||``
anywhere, not only in the ``&&``-part that carries the check; (b) any segment
begins with ``trap``; (c) the command contains a carriage return; (d) the
command contains a backslash line continuation; (e) any segment begins with
``exec`` or ``coproc``.  A segment is a piece of the executed text between
``;`` and newline.  (d) also refuses an escaped backslash at a line end, and
(e) also refuses ``exec 2>&1; pytest``: both carry the status, the cheap
direction.

Known hollow greens: each command below counts while bash exits 0 with the
check failing.  Each is pinned by a ``strict`` xfail test that asserts the safe
answer, so a fix turns it into an XPASS failure.  The list is not exhaustive.

- H7, a builtin or a prefix assignment swallows the status:
  ``export R=$(pytest)``.
- H8, a shell function shadows the check: ``pytest(){ return 0; }; pytest``.
- H9, the first-word rules (the print/inspect denylist, NEGATED, (b), (e))
  are bypassed by a path, quoting, a wrapper or a backslash: ``/bin/echo tsc``.
- A here-doc terminator line reads as a command: ``cat <<'pytest'``, newline,
  ``foo``, newline, ``pytest``.
- (b) and (e) see only segment starts: ``true && trap 'exit 0' EXIT; pytest``.
  ``with_pipefail`` builds this shape itself: for
  ``trap 'exit 0' EXIT; pytest | tail`` it returns
  ``set -o pipefail && trap 'exit 0' EXIT; pytest | tail``.
- The pipefail scan ends in ``pipefail\\b``, so a character that bash keeps
  in the option word passes it: ``set -o pipefail-x; pnpm test | tail``.
  Under ``re.ASCII`` a non-ASCII letter passes too (``pipefail`` followed by
  U+00E9), which the port refused before C1-R1.

MIT License

Copyright (c) 2026 Kal

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

Ported by agent-factory (D-052); behavior matches src/checks.ts:8-93 except
where this docstring says otherwise.
"""
from __future__ import annotations

import re
import sys
from typing import List, Optional

# checks.ts:8-12 -- the three VERIFY regexes, 78 alternatives verbatim.
VERIFY = [
    re.compile(
        r"\b(pytest|vitest|jest|mocha|ava|cypress|playwright test|go test"
        r"|cargo test|swift test|xcodebuild test|gradlew? test|mvn test"
        r"|dotnet test|rspec|phpunit|mix test|bun test|deno test|node --test"
        r"|node --run test|npm test|pnpm test|yarn test|make test|just test"
        r"|python -m pytest|python -m unittest|npm run test|pnpm run test"
        r"|yarn run test|tox|nox)\b",
        re.ASCII,
    ),
    re.compile(
        r"\b(tsc|cargo build|go build|go vet|swift build|xcodebuild"
        r"|gradlew? (build|assemble)|mvn (package|compile|verify)"
        r"|dotnet build|npm run build|pnpm build|pnpm run build|yarn build"
        r"|make build|just build|bun run build|vite build|next build"
        r"|esbuild|webpack)\b",
        re.ASCII,
    ),
    re.compile(
        r"\b(eslint|oxlint|biome (check|lint)|prettier --check"
        r"|ruff (check|format --check)|flake8|pylint|mypy|pyright|pyrefly"
        r"|ty check|pnpm type-check|npm run lint|pnpm lint|pnpm run lint"
        r"|yarn lint|golangci-lint|cargo clippy|swiftlint|swift-format lint"
        r"|pre-commit run|just lint|just check|rubocop|shellcheck)\b",
        re.ASCII,
    ),
]

# checks.ts:35-36
_PRINTS_OR_INSPECTS = re.compile(
    r"^\s*(?:echo|printf|cat|grep|rg|ls|which|type|command|man|head|tail|git)\b",
    re.ASCII,
)

# checks.ts:39
_ASKS_ONLY = re.compile(r"\s--(?:version|help)\b", re.ASCII)

# checks.ts:42
_NEGATED = re.compile(r"^\s*!", re.ASCII)


def _not_a_check(part: str) -> bool:
    """checks.ts:44-45"""
    return bool(
        _PRINTS_OR_INSPECTS.search(part)
        or _ASKS_ONLY.search(part)
        or _NEGATED.search(part)
    )


# AMENDMENT C1-A2 (b) and (e): first words matched at the start of a segment.
_TRAP = re.compile(r"trap\b", re.ASCII)
_EXEC_OR_COPROC = re.compile(r"(?:exec|coproc)\b", re.ASCII)


def _hides_status(bare: str, segments: List[str], last: str) -> bool:
    """AMENDMENT C1-A2: shapes whose exit status need not carry the check's."""
    return bool(
        "||" in last  # (a)
        or any(_TRAP.match(s) for s in segments)  # (b)
        or "\r" in bare  # (c)
        or "\\\n" in bare  # (d)
        or any(_EXEC_OR_COPROC.match(s) for s in segments)  # (e)
    )


def _compile_patterns(patterns: List[str]) -> List[re.Pattern[str]]:
    """Compile user-supplied patterns, raising ValueError on an invalid one."""
    compiled = []
    for p in patterns:
        try:
            compiled.append(re.compile(p, re.ASCII))
        except re.error as exc:
            raise ValueError(f"invalid pattern: {p!r}: {exc}") from exc
    return compiled


def executed(command: str) -> str:
    """The shell text that runs: quoted strings and ``#`` comments are dropped.

    checks.ts:48-50
    """
    # Drop quoted strings first.
    bare = re.sub(r'"[^"]*"|\'[^\']*\'', "", command, flags=re.ASCII)
    # Drop comments: a ``#`` after an escaped space is part of a word.
    bare = re.sub(r"(^|(?<!\\)\s)#[^\n]*", r"\1", bare, flags=re.ASCII)
    return bare


def is_verify(
    command: str, patterns: Optional[List[str]] = None
) -> bool:
    """Whether *command* is a test/build/lint check whose exit status reaches
    the caller.

    checks.ts:58-80

    *patterns* replaces the built-in VERIFY list when given (it does not add to
    it).  Each entry is a regex string tested with ``re.search`` against the
    check command.
    """
    bare = executed(command)

    # checks.ts:61-62 -- pipefail: the last ``set`` statement wins.
    pipefail = False
    for m in re.finditer(
        r"(?:^|[;&\n])\s*set\s+([+-])\w*o\s+pipefail\b", bare, flags=re.ASCII
    ):
        pipefail = m.group(1) == "-"

    # checks.ts:63-67 -- last non-empty segment after splitting on ; and \n.
    segments = [s.strip() for s in re.split(r"[;\n]", bare, flags=re.ASCII)]
    last = ""
    for s in reversed(segments):
        if s:
            last = s
            break

    # checks.ts:68-79
    user_re = _compile_patterns(patterns) if patterns is not None else None

    # Deviation 2 (AMENDMENT C1-A2).  It runs after the compile above, so an
    # invalid pattern still raises when a rule refuses the command.
    if _hides_status(bare, segments, last):
        return False

    for raw in last.split("&&"):
        part = raw.strip()
        if "||" in part:  # checks.ts:69; rule (a) already refused this.
            continue
        if not pipefail and "|" in part:
            continue
        # checks.ts:72 -- lone ``&`` backgrounds; ``2>&1`` and ``&>`` are
        # redirections.
        if re.search(r"(?<!>)&(?!>)", part, flags=re.ASCII):
            continue
        # checks.ts:74 -- under pipefail the check is the pipe feeder.
        check = part.split("|")[0].strip()
        if _not_a_check(check):
            continue
        if user_re is not None:
            if any(r.search(check) for r in user_re):
                return True
        else:
            if any(r.search(check) for r in VERIFY):
                return True

    return False


def with_pipefail(
    command: str, patterns: Optional[List[str]] = None
) -> Optional[str]:
    """Prepend ``set -o pipefail &&`` if that would make the command count.

    checks.ts:88-93

    Returns ``None`` when the command already counts, when prepending pipefail
    would not help, or when the pipe feeds something other than ``tail`` (which
    reads to the end; ``head`` or ``grep -q`` quit early and SIGPIPE the check).
    """
    if is_verify(command, patterns):
        return None
    candidate = f"set -o pipefail && {command}"
    if not is_verify(candidate, patterns):
        return None
    # Only if the pipe feeds tail (not head, grep, etc.).
    bare = executed(command)
    if re.search(r"(?<!\|)\|(?!\|)(?!\s*tail\b)", bare, flags=re.ASCII):
        return None
    return candidate


def _cli() -> None:
    """CLI entry point.

    Usage: python3 scripts/verify_command.py [--pattern REGEX]... [--with-pipefail] -- COMMAND
    """
    args = sys.argv[1:]
    user_patterns: List[str] = []
    do_pipefail = False
    command_parts: List[str] = []
    saw_dashdash = False

    i = 0
    while i < len(args):
        if saw_dashdash:
            command_parts.append(args[i])
            i += 1
            continue
        if args[i] == "--":
            saw_dashdash = True
            i += 1
            continue
        if args[i] == "--pattern":
            if i + 1 >= len(args):
                print("--pattern requires a value", file=sys.stderr)
                sys.exit(2)
            if args[i + 1] == "":
                # An empty regex matches every check: a silent catch-all.
                print("--pattern value is empty", file=sys.stderr)
                sys.exit(2)
            user_patterns.append(args[i + 1])
            i += 2
            continue
        if args[i] == "--with-pipefail":
            do_pipefail = True
            i += 1
            continue
        print(f"unknown option: {args[i]}", file=sys.stderr)
        sys.exit(2)

    if not saw_dashdash:
        print("missing -- before COMMAND", file=sys.stderr)
        sys.exit(2)

    # COMMAND is ONE argument: joining several would classify words the
    # caller's shell has already unquoted.
    if len(command_parts) > 1:
        print(
            f"COMMAND must be one argument, got {len(command_parts)}; quote it",
            file=sys.stderr,
        )
        sys.exit(2)

    command = command_parts[0] if command_parts else ""
    if not command.strip():
        print("COMMAND is empty", file=sys.stderr)
        sys.exit(2)

    pats = user_patterns if user_patterns else None

    # Validate patterns early.
    if pats is not None:
        try:
            _compile_patterns(pats)
        except ValueError as exc:
            print(str(exc), file=sys.stderr)
            sys.exit(2)

    if do_pipefail:
        result = with_pipefail(command, pats)
        if result is not None:
            try:
                print(result)
            except UnicodeEncodeError as exc:
                # Exit 1 means "no rewrite"; a failed write is an error.
                print(f"cannot write the rewrite: {exc}", file=sys.stderr)
                sys.exit(2)
            sys.exit(0)
        else:
            sys.exit(1)
    else:
        if is_verify(command, pats):
            print("counts")
            sys.exit(0)
        else:
            print("does-not-count")
            sys.exit(1)


if __name__ == "__main__":
    _cli()
