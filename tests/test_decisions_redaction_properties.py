"""J1-1-R4 (task #198; owner ruling D-069; contract D-070): property tests of redact as ONE detection and a
span union (tasks/briefs/laya/J1-1-R4-REDESIGN-brief.md: C1, C2, C3, C6; C5's named shapes are in
tests/test_decisions_canonical.py and tests/test_decisions_ledger.py).

The oracle is independent of the implementation. A seeded generator plants FAKE secret values in the forms the
detectors define -- written out here from the brief's rule 6, never imported -- inside random context: prose,
delimiters, other names in random case and with prefixes, glued "bearer" and "sk-" runs, whole placeholders, chains
of two and three assignments. It remembers each value it planted and where. A planted value LEAKS from an output
when one of its DISTINCTIVE windows is there: a 4-character window of the value that occurs nowhere else in the
input, in no placeholder and in no fixed row text, so that only the value itself can put it in an output. A window
with a quote or a backslash is searched in JSON text in its escaped form.

  C1  no covered value leaks into decision_state, canonical(), the appended ledger line (make_row -> append) or
      replay's row.
  C2  every planted value (covered or not) that the redaction of d556c9b or fdac751 hides is hidden by the new
      redaction. Both references run from `git show <rev>:<path>` in a scratch directory. Through decision_state,
      a value the new code shows and a reference's cut hid is counted apart: the reference's own redactor shows
      it there (VERIFY-J1-1-R3 F-5, the cut shift), and the test asserts that no other kind exists.
  C3  decision_state is a fixed point of itself on every generated state (make_row's fixed-point check too).
  C6  the detection stays linear: the worst inputs found finish far under 2 s at 20,000 and 100,000 characters.

The default run sweeps 5,000 inputs (2,500 per seed); J1R4_FULL=1 sweeps 100,000 per seed on up to four
processes. Values never hold "<" or ">" (a value could otherwise spell a placeholder). A `paths` list holds one
item: normalize sorts a list BEFORE redact, so two items can change order on a second pass (a defect of normalize,
outside this lane: J1-1-R4 report).
"""
from __future__ import annotations

import collections
import importlib.util
import json
import multiprocessing
import os
import random
import signal
import string
import subprocess
import sys
import tempfile
import time
from pathlib import Path

import pytest

from agent_factory.decisions import DecisionStateError, decision_state, normalize, redact
from agent_factory.decisions.canonical import canonical
from agent_factory.decisions.ledger import _ROW_FIELDS, _SOURCE_REF_FIELDS, append, make_row, replay

ROOT = Path(__file__).resolve().parents[1]
FULL = os.environ.get("J1R4_FULL") == "1"
SEEDS = (20260924, 198)
PER_SEED = 100_000 if FULL else 2_500
# The references (brief C2): d556c9b's volatile.py and fdac751's (the PIN's code before this lane).
REFS = {"d556c9b": "20ebcd54f3ed", "fdac751": "2d5cf0072469"}

I_DOT, I_DOTLESS, LONG_S = chr(0x130), chr(0x131), chr(0x17F)
SPECIAL = I_DOT + I_DOTLESS + LONG_S
ALNUM = string.ascii_letters + string.digits
SK_ALPHA = ALNUM + "_-"
BEARER_ALPHA = ALNUM + "._~+/-" + SPECIAL
TOKEN_ALPHA = ALNUM + "+/" + SPECIAL
WIDE_ALPHA = ALNUM + "!#$%()*+-./:=?@[]^_`{|}~" + SPECIAL  # [^\s"'&,;] without < >
ENVVAL_ALPHA = WIDE_ALPHA + "\"'&,;\\"  # \S without < >
B64 = ALNUM + "+/"
PLACEHOLDER_TEXTS = ("<redacted:sk>", "<redacted:token>", "<redacted:bearer>", "<redacted:envval>", "<redacted:privkey>")
NAMES = ("KEY", "TOKEN", "SECRET", "PASSWORD", "PASSWD", "API_KEY", "APIKEY")
LABELS = ("RSA PRIVATE KEY", "PRIVATE KEY", "OPENSSH PRIVATE KEY", "ENCRYPTED PRIVATE KEY", "EC PRIVATE KEY",
          "PGP PRIVATE KEY BLOCK", "PGP SECRET KEY BLOCK")
WORDS = ("the", "run", "set", "now", "value", "check", "used", "rejected", "ok", "sorted order", "done", "tail",
         "rest", "step", "gate", "note", "see", "plain", "text", "item", "row", "field", "log", "curl -H", "Auth:",
         "Authorization:", "type=Bearer&h=", '{"auth":"', "x", "ab")
DELIMS = (" ", " ", " ", ",", ";", "&", '"', "'", ":", "=", "(", ")", "/", ".", "-", "_", "!", "\t", "  ", "<", ">",
          "|", "==", "\n")
JOINERS = ("", "", "", " ", " ", " ", ",", ";", "&", '"', "'", ":", "(", ")", "-", "_", "=", "/", ".")
NOISE_PREFIXES = ("", "", "task-", "desk-", "mask-", "flask-", "ask-", "db_", "DB_", "my", "My_", "x-", "AWS_SECRET_",
                  "client_", "Authorization: Bearer ")

# The seven closed schemas' text-carrying fields (the enum fields stay fixed), and a safe base state for each.
BASE = {
    "b2.hit_role": {"sym": "s", "file": "src/a.py", "snippet": "x"},
    "b1.finding_sev": {"file": "src/a.py", "kind": "k", "msg": "x"},
    "b1.finding_kind": {"file": "src/a.py", "kind": "k", "msg": "x"},
    "d1.bug_echo_scores": {"class_slug": "c", "finding_title": "x"},
    "v1.finding_class": {"lane": "l", "finding_id": "f", "title": "x", "paths": ["src/a.py"], "disposition": "BLOCKING"},
    "ap.violates_row": {"action_kind": "edit", "action_target": "a/b.py", "action_excerpt": "x", "row_id": "r",
                        "row_title": "t"},
    "wf.drift": {"step_id": "count-pasted", "expected": "e", "observed": "x", "drift_kind": "prose-claim"},
}
FIELDS = [(q, k) for q, base in BASE.items() for k in base if k not in ("disposition", "action_kind", "step_id",
                                                                        "drift_kind")]
PATH_FIELDS = {"file", "action_target", "paths"}
SOURCE_REF = {"kind": "incident_log", "path": "docs/INCIDENT-LOG.md", "source_digest": "a" * 64, "locator": "x"}
PRODUCER = "decide-harvest/incident-log"


def _windows(s: str) -> set:
    return {s[i:i + 4] for i in range(len(s) - 3)}


# Every string in a row that is not the planted field's text: the keys, the other fields, the enum values, the
# ledger's constants and the placeholders. A window found in them is never distinctive.
FIXED_WINDOWS = set()
for _q, _base in BASE.items():
    for _k, _v in _base.items():
        FIXED_WINDOWS |= _windows(_k) | _windows(json.dumps(_v))
    FIXED_WINDOWS |= _windows(_q)
# The row's own keys come from the ledger module (a hand list missed "producer": three false hits in the first
# full sweep, all in that key); the sweep also counts any window found in a line's non-state text apart.
for _text in PLACEHOLDER_TEXTS + _ROW_FIELDS + _SOURCE_REF_FIELDS + tuple(SOURCE_REF.values()) + (
        PRODUCER, "incumbent", "none", "accepted"):
    FIXED_WINDOWS |= _windows(_text)


def _esc(window: str) -> str:
    return json.dumps(window, ensure_ascii=False)[1:-1]


def _in_json(windows, text: str) -> bool:
    # A window with a quote or a backslash is escaped in JSON; one without them can only match string content.
    return any((_esc(w) if ('"' in w or "\\" in w) else w) in text for w in windows)


def _strings(value):
    if isinstance(value, str):
        yield value
    elif isinstance(value, list):
        for item in value:
            yield from _strings(item)
    elif isinstance(value, dict):
        for item in value.values():
            yield from _strings(item)


def _in_state(windows, state) -> bool:
    return any(w in s for s in _strings(state) for w in windows)


# ---------------------------------------------------------------------------
# The generator. A piece is a list of (text, planted) segments; planted is None for context, else (covered, form).
# ---------------------------------------------------------------------------


def _rand(rnd, alpha, lo, hi):
    return "".join(rnd.choice(alpha) for _ in range(rnd.randint(lo, hi)))


def _any_case(rnd, name):
    # Random case per letter; now and then I as U+0130/U+0131 and S as U+017F (the case-blind forms take them).
    out = []
    for c in name:
        r = rnd.random()
        if c in "Ii" and r < 0.1:
            out.append(rnd.choice((I_DOT, I_DOTLESS)))
        elif c in "Ss" and r < 0.1:
            out.append(LONG_S)
        else:
            out.append(c.upper() if rnd.random() < 0.5 else c.lower())
    return "".join(out)


def _sk(rnd):
    return [("sk-", None), (_rand(rnd, SK_ALPHA, 8, 40), (True, "sk"))]


def _bearer(rnd):
    word = "".join(c.upper() if rnd.random() < 0.3 else c for c in "bearer")
    pad = rnd.choice(("", "", "=", "=="))
    return [(word + rnd.choice((" ", " ", "\t", "  ")), None), (_rand(rnd, BEARER_ALPHA, 16, 48), (True, "bearer")),
            (pad, None)]


def _envval(rnd):
    head = rnd.choice(("", "", "DB_", "AWS_SECRET_", "MY_", "X", "task-")) + rnd.choice(NAMES) + "="
    return [(head, None), (_rand(rnd, ENVVAL_ALPHA, 1, 30), (True, "envval"))]


def _token(rnd):
    # (?:\b|(?<=_))token, an optional quote, "", " ", or [:=] with at most one space each side, an optional quote.
    name = rnd.choice(("token", "Token", "TOKEN", "access_token", "AGENT_TOKEN", "X-Agent-Token", "_token",
                       "PC_BRIDGE_TOKEN"))
    mid = rnd.choice(("", " ", ":", "=", " :", " =", ": ", "= ", " : ", " = "))
    head = name + rnd.choice(("", "", '"', "'")) + mid + rnd.choice(("", "", '"', "'"))
    return [(head, None), (_rand(rnd, TOKEN_ALPHA, 32, 60), (True, "token"))]


def _wide(rnd):
    name = rnd.choice(("", "", "db_", "my_", "client_", "x-", "task-", "desk-")) + _any_case(rnd, rnd.choice(NAMES))
    head = (name + rnd.choice(("", "", '"', "'")) + rnd.choice(("", " ")) + rnd.choice((":", "="))
            + rnd.choice(("", " ")) + rnd.choice(("", "", '"', "'")))
    return [(head, None), (_rand(rnd, WIDE_ALPHA, 8, 30), (True, "wide"))]


def _privkey(rnd):
    label = rnd.choice(LABELS)
    sep = rnd.choice(("\n", " "))
    out = [("-----BEGIN " + label + "-----", None)]
    for _ in range(rnd.randint(1, 4)):
        out += [(sep, None), (_rand(rnd, B64, 16, 64), (True, "privkey"))]
    if rnd.random() < 0.8:
        out.append((sep + "-----END " + label + "-----", None))
    return out


def _near_miss(rnd):
    # A value NO form covers on its own (under a floor, or no secret name): C2's material, never C1's.
    kind = rnd.choice(("wide-short", "bearer-short", "sk-short", "token-space-short", "lower-key", "no-name"))
    if kind == "wide-short":
        head, value = _any_case(rnd, rnd.choice(NAMES)) + ": ", _rand(rnd, WIDE_ALPHA, 4, 7)
    elif kind == "bearer-short":
        head, value = "bearer ", _rand(rnd, BEARER_ALPHA, 8, 15)
    elif kind == "sk-short":
        head, value = "sk-", _rand(rnd, SK_ALPHA, 4, 7)
    elif kind == "token-space-short":
        head, value = " token ", _rand(rnd, TOKEN_ALPHA, 8, 31)
    elif kind == "lower-key":
        head, value = "key=", _rand(rnd, WIDE_ALPHA, 4, 7)
    else:
        head, value = rnd.choice(("code: ", "id ", "note=", "ref ")), _rand(rnd, WIDE_ALPHA, 8, 20)
    return [(head, None), (value, (False, kind)), (" ", None)]


COVERED = (_sk, _bearer, _envval, _token, _wide, _privkey)


def _context(rnd):
    r = rnd.random()
    if r < 0.35:
        return [(rnd.choice(WORDS), None)]
    if r < 0.6:
        return [(rnd.choice(DELIMS), None)]
    if r < 0.85:  # another name in random case, with a prefix, and no value of its own
        return [(rnd.choice(NOISE_PREFIXES) + _any_case(rnd, rnd.choice(NAMES)) + rnd.choice(("", ":", "=", " ", ": ")),
                 None)]
    return [(rnd.choice(PLACEHOLDER_TEXTS), None)]


def _needs_boundary(piece) -> bool:
    # The bare token name needs \b before it: a word character before it breaks the token form, and without
    # ":" or "=" in its separator the widened form does not cover it either.
    head = piece[0][0]
    return head[:5].lower() == "token" and not (":" in head or "=" in head)


def gen_text(rnd):
    """(text, plants): plants are (start, end, covered, form) of each planted value in text."""
    text, plants = "", []
    for _ in range(rnd.randint(1, 10)):
        r = rnd.random()
        if r < 0.4:
            piece = rnd.choice(COVERED)(rnd)
        elif r < 0.5:  # a chain of two or three assignments, glued or with a delimiter between them
            piece = []
            for j in range(rnd.randint(2, 3)):
                if j:
                    piece.append((rnd.choice(("", "", ";", "&", '"', "'", " ", ",")), None))
                part = rnd.choice((_envval, _token, _wide, _wide))(rnd)
                if _needs_boundary(part):
                    part = [(" ", None)] + part
                piece += part
        elif r < 0.6:
            piece = _near_miss(rnd)
        else:
            piece = _context(rnd)
        joiner = rnd.choice(JOINERS)
        if _needs_boundary(piece):
            joiner += " "
        text += joiner
        for seg, planted in piece:
            if planted is not None:
                plants.append((len(text), len(text) + len(seg), planted[0], planted[1]))
            text += seg
    return text, plants


def gen_input(seed: int, i: int):
    """(qid, key, raw_state, plants, field_text) for input i of seed (independent of any other input)."""
    rnd = random.Random(f"{seed}:{i}")
    qid, key = FIELDS[i % len(FIELDS)]
    text, plants = gen_text(rnd)
    prefix = "p/" if key in PATH_FIELDS else ""
    suffix = " end" if key == "lane" else ""  # normalize strips a trailing "--<hex>" from a lane
    field = prefix + text + suffix
    plants = [(s + len(prefix), e + len(prefix), covered, form) for s, e, covered, form in plants]
    raw = dict(BASE[qid])
    raw[key] = [field] if key == "paths" else field
    return qid, key, raw, plants, field


def distinctive(field: str, start: int, end: int) -> set:
    """The value's 4-character windows that nothing but the value can put in an output."""
    rest = _windows(field[:start] + "\x00" + field[end:])
    return {w for w in _windows(field[start:end])
            if not any(c.isspace() for c in w) and w not in rest and w not in FIXED_WINDOWS}


# ---------------------------------------------------------------------------
# The references, run from git show in a scratch directory (never the tree).
# ---------------------------------------------------------------------------

_REF_MODULES: dict = {}


def _load_refs(scratch: Path) -> dict:
    path = "src/agent_factory/decisions/volatile.py"
    for rev, blob in REFS.items():
        if rev in _REF_MODULES:
            continue
        got = subprocess.run(["git", "-C", str(ROOT), "rev-parse", "--short=12", f"{rev}:{path}"],
                             capture_output=True, text=True, check=True).stdout.strip()
        assert got == blob, f"{rev}: volatile.py blob {got} != {blob}"
        source = subprocess.run(["git", "-C", str(ROOT), "show", f"{rev}:{path}"],
                                capture_output=True, text=True, check=True).stdout
        target = scratch / rev / "volatile.py"
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(source, encoding="utf-8")
        spec = importlib.util.spec_from_file_location(f"j1r4_ref_{rev}", target)
        module = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = module  # its dataclass resolves string annotations through sys.modules
        spec.loader.exec_module(module)
        _REF_MODULES[rev] = module
    return _REF_MODULES


# ---------------------------------------------------------------------------
# One sweep: C1, C2 and C3 on the same inputs.
# ---------------------------------------------------------------------------


def sweep(seed: int, lo: int, hi: int, workdir: str) -> dict:
    stats = collections.Counter()
    examples = []
    for i in range(lo, hi):
        qid, key, raw, plants, field = gen_input(seed, i)
        stats["inputs"] = stats["inputs"] + 1
        try:
            out = decision_state(qid, raw)
        except DecisionStateError as exc:
            stats["refused " + exc.reason] += 1
            continue
        ctext = canonical(out)
        # C3: a fixed point of itself.
        if decision_state(qid, out) != out:
            stats["C3 non-idempotent"] += 1
            examples.append(("C3", seed, i))
        # C1 through the real ledger path.
        source_ref = dict(SOURCE_REF, locator=f"canary {seed}-{i}")
        ledger = os.path.join(workdir, f"l{seed}-{i}.jsonl")
        line, replayed_state, replayed_line, row_text = "", None, "", ""
        try:
            row = make_row(producer=PRODUCER, question_id=qid, raw_state=raw, incumbent_answer="accepted",
                           source_ref=source_ref, root=None)
            append(ledger, row)
            with open(ledger, encoding="utf-8") as fh:
                line = fh.read()
            rows = replay(ledger)
            assert rows == [row]
            replayed_state, replayed_line = rows[0]["state"], canonical(rows[0])
            for masked in (row["state_digest"], row["row_id"], row["row_digest"], source_ref["source_digest"],
                           source_ref["locator"]):
                line = line.replace(masked, "\x00")
                replayed_line = replayed_line.replace(masked, "\x00")
            # The line without its state: a window found here is the oracle's miss, never a leak.
            row_text = line.replace(canonical(row["state"]), "\x00", 1)
            assert row_text != line
        except DecisionStateError as exc:
            stats["ledger refused " + exc.reason] += 1
            examples.append(("ledger", seed, i, exc.reason))
        finally:
            if os.path.exists(ledger):
                os.unlink(ledger)
        # C2 material: each redactor's uncut output of the field, and each decision_state's field.
        new_r = redact(normalize(qid, raw))[key]
        views = {}
        for rev, module in _REF_MODULES.items():
            try:
                views[rev] = (module.redact(module.normalize(qid, raw))[key], module.decision_state(qid, raw)[key])
            except DecisionStateError:
                stats[f"C2 {rev} refused"] += 1
        for start, end, covered, form in plants:
            windows = distinctive(field, start, end)
            stats["planted"] += 1
            if not windows:
                stats["planted, no distinctive window"] += 1
                continue
            stats["checked " + ("covered" if covered else "near-miss")] += 1
            if _in_json(windows, row_text):
                stats["oracle: a window in the row's non-state text"] += 1
                examples.append(("oracle", seed, i, form))
            if covered:
                for sink, hit in (("state", _in_state(windows, out)), ("canonical", _in_json(windows, ctext)),
                                  ("line", _in_json(windows, line)),
                                  ("replay", _in_state(windows, replayed_state) or _in_json(windows, replayed_line))):
                    if hit:
                        stats[f"C1 leak {sink} {form}"] += 1
                        examples.append(("C1", seed, i, form, sink))
            vis_new_r = _in_state(windows, new_r)
            vis_new_ds = _in_state(windows, out[key])
            for rev, (ref_r, ref_ds) in views.items():
                vis_ref_r = _in_state(windows, ref_r)
                vis_ref_ds = _in_state(windows, ref_ds)
                stats[f"C2 {rev} hidden by its redactor"] += not vis_ref_r
                if not vis_ref_r and vis_new_r:
                    stats[f"C2 {rev} newly visible (redactor)"] += 1
                    examples.append(("C2r", rev, seed, i, form))
                if not vis_ref_ds and vis_new_ds:
                    kind = "cut shift" if vis_ref_r else "redactor"
                    stats[f"C2 {rev} newly visible (decision_state, {kind})"] += 1
                    stats[f"C2 {rev} cut shift of a {'covered' if covered else 'near-miss'} value"] += vis_ref_r
                    if kind == "redactor":
                        examples.append(("C2ds", rev, seed, i, form))
    stats["examples"] = examples[:20]
    return dict(stats)


def _sweep_chunk(args):
    return sweep(*args)


def _run_seed(seed: int, count: int, scratch: Path) -> dict:
    _load_refs(scratch / "refs")
    workdir = tempfile.mkdtemp(dir=scratch)
    if count <= 5000:
        return sweep(seed, 0, count, workdir)
    procs = min(4, os.cpu_count() or 1)
    step = -(-count // (procs * 8))
    chunks = [(seed, lo, min(lo + step, count), workdir) for lo in range(0, count, step)]
    total = collections.Counter()
    examples = []
    with multiprocessing.get_context("fork").Pool(procs) as pool:
        for part in pool.imap(_sweep_chunk, chunks):
            examples += part.pop("examples")
            total.update(part)
    total["examples"] = examples[:20]
    return dict(total)


def _report(seed, stats):
    lines = [f"seed {seed}:"]
    zeros = ["C1 leak (every sink, every form)", "C3 non-idempotent", "refused (normalize, ledger, references)",
             "oracle: a window in the row's non-state text"]
    for rev in REFS:
        zeros += [f"C2 {rev} newly visible (redactor)", f"C2 {rev} newly visible (decision_state, redactor)"]
    shown = dict(stats)
    shown["C1 leak (every sink, every form)"] = sum(v for k, v in stats.items() if k.startswith("C1 leak"))
    shown["refused (normalize, ledger, references)"] = sum(v for k, v in stats.items() if "refused" in k)
    for k in zeros:
        shown.setdefault(k, 0)
    for k in sorted(k for k in shown if k != "examples"):
        lines.append(f"  {k}: {shown[k]}")
    if stats["examples"]:
        lines.append(f"  examples: {stats['examples']}")
    print("\n".join(lines))


@pytest.mark.parametrize("seed", SEEDS)
def test_c1_c2_c3_canary_sweep(seed, tmp_path):
    stats = _run_seed(seed, PER_SEED, tmp_path)
    _report(seed, stats)
    assert stats["inputs"] == PER_SEED
    # The sweep did its work: values were planted and checked in every form, near misses included.
    assert stats["checked covered"] > PER_SEED, stats
    assert stats["checked near-miss"] > PER_SEED // 20, stats
    refused = {k: v for k, v in stats.items() if "refused" in k}
    assert not refused, refused
    assert stats.get("oracle: a window in the row's non-state text", 0) == 0, stats["examples"]
    leaks = {k: v for k, v in stats.items() if k.startswith("C1 leak")}
    assert not leaks, (leaks, stats["examples"])
    assert stats.get("C3 non-idempotent", 0) == 0, stats["examples"]
    for rev in REFS:
        assert stats[f"C2 {rev} hidden by its redactor"] > PER_SEED, (rev, stats)
        assert stats.get(f"C2 {rev} newly visible (redactor)", 0) == 0, (rev, stats["examples"])
        assert stats.get(f"C2 {rev} newly visible (decision_state, redactor)", 0) == 0, (rev, stats["examples"])


def test_the_oracle_sees_every_covered_value_when_nothing_is_redacted():
    # Negative control: the oracle's two searches (a state's strings; JSON text, escaped) find every covered value
    # in a state that normalize alone produced -- so a zero in the sweep is the redaction's, not the oracle's.
    # (action_target keeps only its first token, so a value after it is dropped, not hidden: not counted here.)
    seen = collections.Counter()
    for i in range(300):
        qid, key, raw, plants, field = gen_input(SEEDS[0], i)
        if key == "action_target":
            continue
        state = normalize(qid, raw)
        for start, end, covered, form in plants:
            windows = distinctive(field, start, end)
            if not covered or not windows:
                continue
            seen["covered"] += 1
            seen["state"] += _in_state(windows, state)
            seen["canonical"] += _in_json(windows, canonical(state))
    assert seen["covered"] > 300, seen
    assert seen["state"] == seen["canonical"] == seen["covered"], seen


def test_generator_plants_every_form_and_context_class():
    forms = collections.Counter()
    texts = []
    for i in range(2000):
        _, _, _, plants, field = gen_input(SEEDS[1], i)
        texts.append(field)
        for _s, _e, covered, form in plants:
            forms[(covered, form)] += 1
    for form in ("sk", "bearer", "envval", "token", "wide", "privkey"):
        assert forms[(True, form)] > 100, (form, forms)
    for form in ("wide-short", "bearer-short", "sk-short", "token-space-short", "lower-key", "no-name"):
        assert forms[(False, form)] > 20, (form, forms)
    joined = "\x00".join(texts)
    for needle in PLACEHOLDER_TEXTS + (I_DOT, I_DOTLESS, LONG_S, "flask-", "Authorization: Bearer "):
        assert needle in joined, needle


# ---------------------------------------------------------------------------
# The rules, one named case each (the mutants' killers).
# ---------------------------------------------------------------------------

V = "X4Z9X4Z9X4Z9"


def _msg(text):
    return decision_state("b1.finding_sev", {"file": "src/a.py", "kind": "k", "msg": text})["msg"]


@pytest.mark.parametrize(
    "raw, want",
    [
        # rule 2: a head inside another value of its form is found (re.finditer would skip it and free V)
        (f"flask-tapasswd=aAPI_KEY : {V}", "fla<redacted:sk>=<redacted:envval> : <redacted:envval>"),
        (f"KEY=aKEY=bKEY= {V}", "KEY=<redacted:envval> <redacted:envval>"),
        # rule 5: the value is greedy to its natural end, never stopped at another head
        (f"password: mykey={V}", "password: <redacted:envval>"),
        ("password: mykey=X4Z9Q", "password: <redacted:envval>"),
    ],
    ids=["head-inside-a-value", "upper-head-inside-a-value", "value-over-a-head", "stub-example"],
)
def test_every_start_and_greedy_value(raw, want):
    got = _msg(raw)
    assert got == want, got
    assert "X4Z9" not in got and "4Z9Q" not in got


@pytest.mark.parametrize(
    "raw, want",
    [
        # rule 3: overlapping spans merge into ONE placeholder named by the earliest start (the widened value
        # then runs on through that placeholder to the space, so "token:" goes too: _spans)
        (f"password:plain{V[:4]}bearer abcdefghijklmnop==token: {V}",
         "password:<redacted:envval> <redacted:envval>"),
        (f"sk-abcdefgh-token {V}{V}{V}bearer abcdefghijklmnop", "<redacted:sk> <redacted:token>"),
        # the union takes the longest member's end (first-wins would free the tail)
        (f"password: x{V}Bearer QZJ8QZJ8QZJ8QZJ8QZJ8", "password: <redacted:envval>"),
    ],
    ids=["widened-value-and-glued-bearer", "token-run-and-glued-bearer", "union-takes-the-longer-end"],
)
def test_union_merges_overlapping_spans(raw, want):
    got = _msg(raw)
    assert got == want, got
    assert not set(got) & set("QJ"), got
    assert "X4Z9" not in got


@pytest.mark.parametrize(
    "raw, want",
    [
        # rule 3's ties: at the same start held > privkey > sk > bearer > envval (NAME=) > token > widened
        ("password: <redacted:sk>", "password: <redacted:sk>"),
        (f"password: sk-{V}", "password: <redacted:sk>"),
        (f"token: {V}{V}{V}-{V}", "token: <redacted:token>"),
        (f"PC_BRIDGE_TOKEN={V}{V}{V}-x", "PC_BRIDGE_TOKEN=<redacted:envval>"),
        (f"KEY=sk-{V}", "KEY=<redacted:sk>"),
        (f"KEY=-----BEGIN RSA PRIVATE KEY----- {V} -----END RSA PRIVATE KEY-----", "KEY=<redacted:privkey>"),
    ],
    ids=["held-over-widened", "sk-over-widened", "token-over-widened", "upper-envval-over-token",
         "sk-over-upper-envval", "privkey-over-upper-envval"],
)
def test_tie_at_the_same_start_goes_by_the_fixed_priority(raw, want):
    got = _msg(raw)
    assert got == want, got
    assert "X4Z9" not in got


@pytest.mark.parametrize(
    "text",
    ["password: <redacted:token>", "KEY=<redacted:bearer>", "API_KEY=<redacted:sk> rest", '"api_key": "<redacted:privkey>"',
     "<redacted:sk><redacted:bearer>"],
)
def test_a_held_placeholder_keeps_its_class_and_bytes(text):
    # rule 4: a whole placeholder is a span of its own class with the top rank: redact leaves the text as it is.
    assert redact({"msg": text})["msg"] == text


@pytest.mark.parametrize("head", ["password: ", "KEY=", "API_KEY=", '"api_key": "', "token = "])
def test_a_cut_placeholder_at_the_end_is_no_span(head):
    # rule 4: a value that is a proper prefix of a placeholder and ends the text is one that bound cut. The
    # upper-case NAME= form needs this too: through decision_state, a cut inside a held placeholder after
    # KEY= must stay the same prefix on the next pass (C3).
    for placeholder in PLACEHOLDER_TEXTS:
        for end in range(1, len(placeholder)):
            text = head + placeholder[:end]
            assert redact({"msg": text})["msg"] == text, text
    for placeholder in PLACEHOLDER_TEXTS:
        for cut in range(1, len(placeholder)):
            state = {"file": "src/a.py", "kind": "k", "msg": "a" * (200 - cut - len(head) - 1) + " " + head + placeholder}
            out = decision_state("b1.finding_sev", state)
            assert out["msg"].endswith((head + placeholder[:cut]).rstrip()), (head, placeholder, cut, out["msg"][-30:])
            assert decision_state("b1.finding_sev", out) == out, (head, placeholder, cut)


@pytest.mark.parametrize(
    "text, want",
    [
        ("password: short", "password: short"),
        ("password: X4Z9X4Z", "password: X4Z9X4Z"),  # 7 characters: under the widened form's floor, by design
        ("password: X4Z9X4Z9", "password: <redacted:envval>"),
        ("key: sorted order", "key: sorted order"),
    ],
    ids=["prose", "seven", "eight", "prose-key"],
)
def test_the_widened_floor_is_eight(text, want):
    assert redact({"msg": text})["msg"] == want


@pytest.mark.parametrize(
    "raw, want",
    [
        # rule 5 read after the replacement: an envval or widened value that meets a span holding a delimiter
        # runs through it (its placeholder holds none) and on. Both references hid each tail; the union alone
        # left ":tail" (or v2), and its output was not a fixed point of redact.
        ("password: xyBearer QZJ8QZJ8QZJ8QZJ8:tail", "password: <redacted:envval>"),
        ("KEY=abcBearer QZJ8QZJ8QZJ8QZJ8:tail", "KEY=<redacted:envval>"),
        ("password: x-----BEGIN RSA PRIVATE KEY----- QZJ8 -----END RSA PRIVATE KEY-----:tail",
         "password: <redacted:envval>"),
        # a head inside another span counts too (the C2 finding, seed 198 input 638, reduced)
        (f"keY: =PASSWD=abcbEarEr v0FzXxFcy6uj0dab'x_|key={V[:7]}", "keY: <redacted:envval>"),
        # a value under the floor that runs into a span meets its floor there
        ("key: aKEY=b", "key: <redacted:envval>"),
    ],
    ids=["widened-over-bearer", "upper-over-bearer", "widened-over-key-block", "head-inside-a-span",
         "under-the-floor-into-a-span"],
)
def test_a_value_runs_through_a_span_it_meets(raw, want):
    got = redact({"msg": raw})["msg"]
    assert got == want, got
    assert "4Z9" not in got and "QZJ8" not in got
    assert redact({"msg": got})["msg"] == got


def test_a_key_block_glued_to_an_end_line_is_hidden():
    # rule 2 for the key block: a BEGIN line that shares the dashes of the END line before it starts its own
    # block (d556c9b showed the second body).
    text = ("-----BEGIN RSA PRIVATE KEY----- QZJ8AB -----END RSA PRIVATE KEY-----BEGIN RSA PRIVATE KEY----- "
            + V + " -----END RSA PRIVATE KEY----- rest")
    got = redact({"msg": text})["msg"]
    assert got == "<redacted:privkey> rest", got


# ---------------------------------------------------------------------------
# The linear detection is the forms, and it is linear (C6).
# ---------------------------------------------------------------------------

# The forms as whole patterns, matched at EVERY start (a lookahead): the rule 6 definitions, written here.
_NAME = r"(?:KEY|TOKEN|SECRET|PASSWORD|PASSWD|API_?KEY)"
_WHOLE = [
    ("sk", r"(?=(sk-[A-Za-z0-9_-]{8,}))", True),
    ("bearer", r"(?=((?i:bearer)\s+(?i:[A-Za-z0-9._~+/-]){16,}=*))", True),
    ("envval", r"(?=" + _NAME + r"=(\S+))", False),
    ("token", r"(?=(?i:(?:\b|(?<=_))token[\"']?(?: ?[:=] ?| )?[\"']?)((?i:[A-Za-z0-9+/]){32,}))", False),
    ("wide", r"(?=(?i:" + _NAME + r")[\"']?\s?[:=]\s?[\"']?([^\s\"'&,;]{8,}))", False),
    ("privkey", r"(?=(-----BEGIN [A-Z0-9 ]*(?:PRIVATE|SECRET) KEY(?: BLOCK)?-----.*?"
                r"(?:-----END [A-Z0-9 ]*(?:PRIVATE|SECRET) KEY(?: BLOCK)?-----|\Z)))", True),
]


def _whole_spans(text):
    import re

    out = {(m.start(), m.end(), "held") for m in re.finditer(r"<redacted:(?:sk|token|bearer|envval|privkey)>", text)}
    for form, pattern, from_head in _WHOLE:
        for m in re.finditer(pattern, text, re.S if form == "privkey" else 0):
            start, end = m.span(1)
            value = text[start:end]
            if form in ("envval", "wide") and end == len(text) and any(
                    p != value and p.startswith(value) for p in PLACEHOLDER_TEXTS):
                continue
            out.add((m.start() if from_head else start, end, form))
    return out


def test_the_linear_detection_equals_every_form_matched_at_every_start():
    # _matches (before the closure) against each form written here as a whole pattern at every start.
    from agent_factory.decisions.volatile import _RANK, _matches

    names = {rank: name for name, rank in _RANK.items()}
    pieces = ["sk-", "bearer ", "BEARER\t", "token", "_token", "token: ", "KEY=", "API_KEY=", "api_key: ", "Key :",
              "password=", "SECRET", "=", "==", ":", " ", "  ", '"', "'", "&", ",", ";", "<redacted:sk>",
              "<redacted:envval>", "<redacted:tok", "-----BEGIN RSA PRIVATE KEY-----", "-----END RSA PRIVATE KEY-----",
              "-----", "+", "/", ".", "~", "_", "-", I_DOT, I_DOTLESS, LONG_S, "QZJ8", "QZJ8QZJ8", "X4Z9X4Z9X4Z9X4Z9",
              "ab" * 16, "abcdefghijklmnop", "x", "<", ">"]
    rnd = random.Random(7)
    kinds = collections.Counter()
    for _ in range(20000):
        text = "".join(rnd.choice(pieces) for _ in range(rnd.randint(1, 30)))
        want = _whole_spans(text)
        got = {(start, end, names[rank]) for start, rank, end, _cls in _matches(text)[0]}
        assert got == want, (text, sorted(want - got), sorted(got - want))
        kinds.update(k for _s, _e, k in want)
    for kind in ("held", "privkey", "sk", "bearer", "envval", "token", "wide"):
        assert kinds[kind] > 50, kinds


class _Runaway(Exception):
    pass


def _alarm(signum, frame):
    raise _Runaway()


def _worst_cases(n):
    return {
        "API_KEY= heads": ("API_KEY=" * (n // 8 + 1))[:n],
        "sk- runs": ("sk-" * (n // 3 + 1))[:n],
        "bearer runs": ("bearer " * (n // 7 + 1))[:n],
        "bearer + 16-run": ("bearer abcdefghijklmnopq" * (n // 24 + 1))[:n],
        "key: heads": ("key:" * (n // 4 + 1))[:n],
        "token+ heads": ("token+" * (n // 6 + 1))[:n],
        "BEGIN lines, no END": ("-----BEGIN PRIVATE KEY-----" * (n // 27 + 1))[:n],
        "BEGIN glued to END": ("-----BEGIN PRIVATE KEY-----END PRIVATE KEY-----" * (n // 47 + 1))[:n],
        "placeholders": ("<redacted:sk>" * (n // 13 + 1))[:n],
        "widened over placeholders": ("password:x<redacted:sk>" * (n // 23 + 1))[:n],
        "mixed heads": ("API_KEY=key:sk-token+bearer " * (n // 28 + 1))[:n],
        "BEGIN + a long label run": ("-----BEGIN " + "PRIVATE KEY " * (n // 12 + 1))[:n],
        "END + a long label run": ("-----END " + "PRIVATE KEY " * (n // 12 + 1))[:n],
        "bearer + whitespace runs": (("bearer" + " " * 50 + "x") * (n // 57 + 1))[:n],
        "sk- + one long run": "sk-" + "a" * (n - 3),
        "API_KEY= + one long value": "API_KEY=" + "a" * (n - 8),
    }


def test_the_detection_stays_linear_on_the_worst_inputs():
    # C6. Each worst case finishes far under 2 s at 20,000 and at 100,000 characters (a form matched whole at
    # every start took 1.26 s for 20,000 characters of "API_KEY=" and grows four times per doubling). The alarm
    # stops a runaway match instead of hanging the suite.
    previous = signal.signal(signal.SIGALRM, _alarm)
    times = {}
    try:
        for n in (20_000, 100_000):
            for name, text in _worst_cases(n).items():
                signal.setitimer(signal.ITIMER_REAL, 10.0)
                try:
                    start = time.perf_counter()
                    redact({"msg": text})
                    times[(name, n)] = time.perf_counter() - start
                except _Runaway:
                    pytest.fail(f"{name} at {n} characters ran over 10 s")
                finally:
                    signal.setitimer(signal.ITIMER_REAL, 0)
    finally:
        signal.signal(signal.SIGALRM, previous)
    print("\n".join(f"C6 {name:28s} {n:>7d} chars {t * 1000:9.1f} ms" for (name, n), t in sorted(times.items())))
    slow = {k: v for k, v in times.items() if v >= 2.0}
    assert not slow, slow
