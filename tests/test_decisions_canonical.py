"""J1-1 tests: normalize -> redact -> canonical -> sha256, the seven closed
state schemas, and the committed golden digests.

Every test is LLM-free and deterministic. The negative controls (the refusal
strings, the secret-leak assertions, the order discriminator) fail for the
EXACT expected reason. The golden digests are asserted EXACTLY (pasted, not
recomputed) and a re-landed variant per type must hash to the SAME digest.

The pipeline entry point under test is the public
``state_digest(question_id, state, root)`` = sha256(canonical(decision_state(state))),
where ``decision_state`` = bound(redact(normalize(state))) (AMENDMENT 1, D-056);
the transforms are also tested directly for their separation (normalize
never redacts, redact never normalizes, normalize never cuts).

Contract: tasks/briefs/laya/J1-1-brief.md (seeds/seed-laya-j1-v1.yaml AC 1 +
AC 3; the verdict's J1 acceptance test 1 + the KC-J6 field list), amended by
tasks/briefs/laya/J1-1-R1-brief.md (A1-A5),
tasks/briefs/laya/J1-1-R2-brief.md (B1-B5) and
tasks/briefs/laya/J1-1-R3-brief.md (C1-C5).
"""
from __future__ import annotations

import json
import os

import pytest

from agent_factory.decisions.canonical import canonical, state_digest
from agent_factory.decisions.volatile import DecisionStateError, normalize, redact

GOLDEN_DIR = os.path.join(os.path.dirname(__file__), "fixtures", "decisions", "golden")

# The seven question types, each with one golden fixture.
GOLDEN_IDS = [
    "b2.hit_role",
    "b1.finding_sev",
    "b1.finding_kind",
    "d1.bug_echo_scores",
    "v1.finding_class",
    "ap.violates_row",
    "wf.drift",
]

# The committed golden digests (pasted from the fixtures the lane produced;
# asserted EXACTLY, never recomputed into the assertion).
GOLDEN_DIGESTS = {
    "b2.hit_role": "3ced4cd39a61faa5519dd3c491b9019347cfc12d447448bc53fc49118bc6423e",
    "b1.finding_sev": "8c42d5dd1e8c349e6e94ab40189e706dcc3ada5e262d44077734ef91c178350d",
    "b1.finding_kind": "9e18ed7e5146a2c3762ec1e00ae233351928e06ef07308563e844b07aec16abf",
    "d1.bug_echo_scores": "5a8c4ad2659c0e6b5dd2b2638bc2a546adca5e55f7246e073197fa30f5971bb8",
    "v1.finding_class": "f41a299c4a38ab305fc612dfc61cedd4481b9e6c6f9d3e1ffe24a229f10ad43e",
    "ap.violates_row": "594584bde9869086e1814489784747f00dbee9918e12c3d4f4bdb4f90702deef",
    "wf.drift": "a51a56c48e98cca60a95923da2a34a25bfb3609c1b23197588ad32af90cfc06b",
}


def _load(qid: str) -> dict:
    with open(os.path.join(GOLDEN_DIR, qid + ".json"), encoding="utf-8") as fh:
        return json.load(fh)


# ---------------------------------------------------------------------------
# Golden digests: the committed values, asserted EXACTLY, twice (bitwise).
# ---------------------------------------------------------------------------


def test_golden_digests_exact():
    # Run the pipeline twice per type; the two results must be bitwise
    # identical and must equal the pasted golden digest for all seven types.
    first = {}
    for qid in GOLDEN_IDS:
        fixture = _load(qid)
        first[qid] = state_digest(qid, fixture["state"], fixture.get("root"))
    for qid in GOLDEN_IDS:
        fixture = _load(qid)
        again = state_digest(qid, fixture["state"], fixture.get("root"))
        assert first[qid] == again, f"{qid}: pipeline not bitwise-stable"
        assert first[qid] == GOLDEN_DIGESTS[qid], (
            f"{qid}: digest {first[qid]} != golden {GOLDEN_DIGESTS[qid]}"
        )


# ---------------------------------------------------------------------------
# Re-landing stability: a re-landed variant (absolute path under the root,
# a PIN suffix, extra whitespace, NFD instead of NFC) hashes to the SAME
# digest as the clean base.
# ---------------------------------------------------------------------------


def test_relanding_stable():
    for qid in GOLDEN_IDS:
        fixture = _load(qid)
        root = fixture.get("root")
        base = state_digest(qid, fixture["state"], root)
        variant = state_digest(qid, fixture["variant"], root)
        assert variant == base, (
            f"{qid}: re-landed variant {variant} != base {base} "
            f"(variant={json.dumps(fixture['variant'])})"
        )
        assert base == GOLDEN_DIGESTS[qid], f"{qid}: base {base} != golden"


# ---------------------------------------------------------------------------
# The injected-secret test: for every secret class, a state carrying the
# secret hashes IDENTICAL to the same state with the secret absent (the
# clean form contains the placeholder, so the placeholder equals the
# redaction of the absent form), and the secret bytes appear in no output
# (asserted over the canonical bytes of the pipeline input).
# ---------------------------------------------------------------------------


def test_secret_redacted_every_class():
    # (qid, secret-bearing state, clean state containing the placeholder,
    #  a distinctive raw-secret substring that must not survive)
    cases = [
        (
            "b1.finding_sev",
            {"file": "src/a.py", "kind": "k", "msg": "key is sk-abcdef1234567890"},
            {"file": "src/a.py", "kind": "k", "msg": "key is <redacted:sk>"},
            "sk-abcdef1234567890",
        ),
        (
            "b1.finding_kind",
            {"file": "src/a.py", "kind": "k", "msg": "hdr Bearer 0123456789abcdef0123456789abcdef"},
            {"file": "src/a.py", "kind": "k", "msg": "hdr <redacted:bearer>"},
            "0123456789abcdef0123456789abcdef",
        ),
        (
            "b2.hit_role",
            {"file": "src/a.py", "snippet": "token: 0123456789abcdef0123456789abcdef", "sym": "s"},
            {"file": "src/a.py", "snippet": "token: <redacted:token>", "sym": "s"},
            "0123456789abcdef0123456789abcdef",
        ),
        (
            "ap.violates_row",
            {
                "action_excerpt": "API_KEY=abcd1234abcd1234abcd1234abcd",
                "action_kind": "edit",
                "action_target": "a/b.py",
                "row_id": "AF-AP-1",
                "row_title": "t",
            },
            {
                "action_excerpt": "API_KEY=<redacted:envval>",
                "action_kind": "edit",
                "action_target": "a/b.py",
                "row_id": "AF-AP-1",
                "row_title": "t",
            },
            "abcd1234abcd1234abcd1234abcd",
        ),
        (
            "wf.drift",
            {
                "drift_kind": "mirror-test",
                "expected": "the key block follows",
                "observed": (
                    "-----BEGIN RSA PRIVATE KEY-----\n"
                    "MIIBOgIBAAJBAKj34GkSqaCn74a3\n"
                    "-----END RSA PRIVATE KEY-----"
                ),
                "step_id": "verify-seam-first",
            },
            {
                "drift_kind": "mirror-test",
                "expected": "the key block follows",
                "observed": "<redacted:privkey>",
                "step_id": "verify-seam-first",
            },
            "MIIBOgIBAAJBAKj34GkSqaCn74a3",
        ),
    ]
    for qid, secret_state, clean_state, raw_secret in cases:
        # The clean form must contain the placeholder (the placeholder equals
        # the redaction of the absent form).
        clean_text = canonical(redact(normalize(qid, clean_state)))
        assert "<redacted:" in clean_text, f"{qid}: clean form must contain the placeholder"
        # The secret-bearing state must hash IDENTICAL to the clean state.
        secret_digest = state_digest(qid, secret_state)
        clean_digest = state_digest(qid, clean_state)
        assert secret_digest == clean_digest, (
            f"{qid}: secret-bearing {secret_digest} != clean {clean_digest} "
            f"(redaction must equal the redaction of the absent form)"
        )
        # The raw secret bytes must appear in NO output: the canonical bytes
        # of the pipeline input (normalize -> redact) must not carry it.
        pipeline_input = canonical(redact(normalize(qid, secret_state)))
        assert raw_secret not in pipeline_input, f"{qid}: raw secret leaked into the digest input"
        assert raw_secret not in clean_text, f"{qid}: raw secret leaked into the clean canonical"


# ---------------------------------------------------------------------------
# The closed-schema refusals: exact contract strings.
# ---------------------------------------------------------------------------


def test_unknown_key_refused():
    fixture = _load("b1.finding_sev")
    state = dict(fixture["state"])
    state["timestamp"] = "2026-09-22T20:47:50Z"  # a locator key, never state
    with pytest.raises(DecisionStateError) as exc:
        normalize("b1.finding_sev", state, fixture["root"])
    assert exc.value.reason == "decision-state-unknown-key"
    assert str(exc.value) == "decision-state-unknown-key: b1.finding_sev.timestamp"


def test_missing_key_refused():
    state = {"kind": "gpg-sign", "msg": "m"}  # missing 'file' (required)
    with pytest.raises(DecisionStateError) as exc:
        normalize("b1.finding_sev", state, "/home/rocco/agent-factory")
    assert exc.value.reason == "decision-state-missing-key"
    assert str(exc.value) == "decision-state-missing-key: b1.finding_sev.file"


def test_bad_enum_refused():
    state = {
        "lane": "pc-j1-1",
        "finding_id": "F-1",
        "title": "t",
        "paths": ["src/a.py"],
        "disposition": "MAYBE",  # not in {BLOCKING,NON-BLOCKING}
    }
    with pytest.raises(DecisionStateError) as exc:
        normalize("v1.finding_class", state, "/home/rocco/agent-factory")
    assert exc.value.reason == "decision-state-bad-enum"
    assert str(exc.value) == "decision-state-bad-enum: v1.finding_class.disposition=MAYBE"


def test_closed_schema_refuses_incumbent_answer_key():
    # Incumbent answers belong to row provenance (J1-2), not stable state.
    state = {"sym": "normalize", "file": "src/a.py", "snippet": "def normalize", "role": "def"}
    with pytest.raises(DecisionStateError) as exc:
        normalize("b2.hit_role", state, "/home/rocco/agent-factory")
    assert str(exc.value) == "decision-state-unknown-key: b2.hit_role.role"


def test_command_target_uses_leading_token_and_pin_strip_is_exact():
    root = "/home/rocco/agent-factory"
    command = {
        "action_kind": "command",
        "action_target": "python3 scripts/check.py --strict",
        "action_excerpt": "ran the checker",
        "row_id": "AF-AP-1",
        "row_title": "checker",
    }
    assert normalize("ap.violates_row", command, root)["action_target"] == "python3"
    finding = {
        "lane": "team--alpha--330803c",
        "finding_id": "F-1",
        "title": "t",
        "paths": ["src/a.py"],
        "disposition": "blocking",
    }
    assert normalize("v1.finding_class", finding, root)["lane"] == "team--alpha"
    finding["lane"] = "team--alpha"
    assert normalize("v1.finding_class", finding, root)["lane"] == "team--alpha"


def test_unknown_question_refused():
    with pytest.raises(DecisionStateError) as exc:
        normalize("not.a.question", {"file": "a"}, "/home/rocco/agent-factory")
    assert exc.value.reason == "decision-question-unknown"
    assert str(exc.value) == "decision-question-unknown: not.a.question"


def test_abs_path_outside_root_refused():
    # An absolute path NOT under the repo root is refused, never relativized.
    state = {"file": "/etc/passwd", "kind": "k", "msg": "m"}
    with pytest.raises(DecisionStateError) as exc:
        normalize("b1.finding_sev", state, "/home/rocco/agent-factory")
    assert exc.value.reason == "decision-state-abs-path"
    assert exc.value.detail == "file"
    assert str(exc.value) == "decision-state-abs-path: file"


def test_float_refused():
    # canonical accepts only int/str/list/dict; a float is refused with its
    # key's path. (bool is an int subclass and is refused explicitly, never
    # printed as true.)
    with pytest.raises(DecisionStateError) as exc:
        canonical({"score": 1.5})
    assert exc.value.reason == "decision-canonical-float"
    assert exc.value.detail == "$.score"
    with pytest.raises(DecisionStateError) as exc2:
        canonical({"flag": True})
    assert exc2.value.reason == "decision-canonical-float"
    assert exc2.value.detail == "$.flag"


# ---------------------------------------------------------------------------
# The two transforms have two jobs, one fixed order (normalize -> redact).
# ---------------------------------------------------------------------------


def test_normalize_does_not_redact():
    # A secret survives normalize ALONE (normalize is stability, not security).
    state = {"file": "src/a.py", "kind": "k", "msg": "key is sk-abcdef1234567890"}
    normed = normalize("b1.finding_sev", state, "/home/rocco/agent-factory")
    assert "sk-abcdef1234567890" in normed["msg"], (
        "normalize must NOT redact: the secret survives normalize alone"
    )
    assert "sk-abcdef1234567890" not in redact(normed)["msg"], (
        "redact (applied after normalize) must remove it"
    )


def test_redact_does_not_normalize():
    # Whitespace (a double space) SURVIVES redact ALONE (redact is security,
    # not stability): the run is only collapsed by normalize.
    state = {"file": "src/a.py", "kind": "k", "msg": "a  secret"}
    redacted = redact(state)
    assert "a  secret" == redacted["msg"], (
        "redact must NOT collapse whitespace: a run survives redact alone"
    )
    assert normalize("b1.finding_sev", state, "/home/rocco/agent-factory")["msg"] == "a secret"


def test_order_is_normalize_then_redact():
    # A secret SPLIT BY A WHITESPACE RUN is caught only in the right order.
    # raw: "token:  <run>" (a colon followed by TWO spaces before the 32+ run).
    # The token rule (colon + at most ONE space, or a single space) cannot
    # bridge a two-space run, so redact-first MISSES it; only after normalize
    # has collapsed the run to a single space does the rule match. The test
    # goes through the public pipeline: the split secret must hash to the
    # SAME digest as the clean placeholder form.
    raw = {"file": "src/a.py", "kind": "k", "msg": "token:  0123456789abcdef0123456789abcdef"}
    clean = {"file": "src/a.py", "kind": "k", "msg": "token: <redacted:token>"}
    run = "0123456789abcdef0123456789abcdef"
    # The wrong order (redact FIRST, then normalize): the two-space run is
    # present when redact runs, so the token rule cannot bridge it and the
    # secret survives into the normalized output (normalize does not redact).
    wrong_input = canonical(normalize("b1.finding_sev", redact(raw)))
    assert run in wrong_input, (
        "redact-first must MISS the whitespace-run-split token (it is only caught "
        "after normalize collapses the run) -- this is the order discriminator"
    )
    # The right order (normalize -> redact, the pipeline's order): the split
    # secret is caught and hashes IDENTICAL to the clean placeholder form.
    assert state_digest("b1.finding_sev", raw) == state_digest("b1.finding_sev", clean), (
        "normalize-first must CATCH the whitespace-run-split token (same digest as the clean form)"
    )
    right_input = canonical(redact(normalize("b1.finding_sev", raw)))
    assert run not in right_input, "normalize-first must CATCH the whitespace-run-split token"
    assert "<redacted:token>" in right_input, "normalize-first must leave the token placeholder"


# ===========================================================================
# J1-1-R1 -- AMENDMENT 1 to J1-1 (D-056): the state is bounded AFTER
# redaction, through ONE public composition
#     decision_state(qid, state, root) = bound(redact(normalize(state)))
# that state_digest and both ledger call sites use
# (tasks/briefs/laya/J1-1-R1-brief.md, A1-A5).
#
# Every secret below is FAKE. A secret BODY uses only the letters Q Z X J,
# which occur in no name, separator, placeholder or filler these tests put
# next to a body: "no byte of the body reaches the output" is checked one
# character at a time, so a one-character leak is red.
# ===========================================================================

_BODY_ALPHABET = frozenset("QZXJ")


def _body(n: int) -> str:
    """A FAKE secret body of n characters over the body alphabet."""
    return ("QZXJ" * (n // 4 + 1))[:n]


def _decision_state(qid, state, root=None):
    # Imported at call time: the name does not exist at the PIN, so each test
    # that needs it is red on its own while the rest of the file collects.
    from agent_factory.decisions import decision_state

    return decision_state(qid, state, root)


def _bound(qid, state):
    from agent_factory.decisions.volatile import bound

    return bound(qid, state)


# Every bounded free-text key and its limit, pinned here (the amendment keeps
# the limits' values). The enum keys are bounded too, but a value outside its
# enum is refused before bound runs, so an enum key never carries a secret.
_BOUNDED = {
    ("b2.hit_role", "sym"): 120,
    ("b2.hit_role", "snippet"): 400,
    ("b1.finding_sev", "kind"): 80,
    ("b1.finding_sev", "msg"): 200,
    ("b1.finding_kind", "kind"): 80,
    ("b1.finding_kind", "msg"): 200,
    ("d1.bug_echo_scores", "class_slug"): 80,
    ("d1.bug_echo_scores", "finding_title"): 120,
    ("v1.finding_class", "lane"): 80,
    ("v1.finding_class", "finding_id"): 80,
    ("v1.finding_class", "title"): 120,
    ("ap.violates_row", "action_excerpt"): 400,
    ("ap.violates_row", "row_id"): 40,
    ("ap.violates_row", "row_title"): 120,
    ("wf.drift", "expected"): 400,
    ("wf.drift", "observed"): 400,
}
_ENUM_BOUNDED = {
    ("v1.finding_class", "disposition"): 40,
    ("ap.violates_row", "action_kind"): 20,
    ("wf.drift", "step_id"): 40,
    ("wf.drift", "drift_kind"): 40,
}

# A short, valid, secret-free state per question type.
_BASE = {
    "b2.hit_role": {"sym": "s", "file": "src/a.py", "snippet": "x"},
    "b1.finding_sev": {"file": "src/a.py", "kind": "k", "msg": "x"},
    "b1.finding_kind": {"file": "src/a.py", "kind": "k", "msg": "x"},
    "d1.bug_echo_scores": {"class_slug": "c", "finding_title": "x"},
    "v1.finding_class": {
        "lane": "l",
        "finding_id": "f",
        "title": "x",
        "paths": ["src/a.py"],
        "disposition": "BLOCKING",
    },
    "ap.violates_row": {
        "action_kind": "edit",
        "action_target": "a/b.py",
        "action_excerpt": "x",
        "row_id": "r",
        "row_title": "t",
    },
    "wf.drift": {
        "step_id": "count-pasted",
        "expected": "e",
        "observed": "x",
        "drift_kind": "prose-claim",
    },
}


def _forms(body_len: int = 40):
    """(class, secret text, the same text with its placeholder in the
    secret's place). Each secret is the whole matched form; its body is FAKE."""
    b = _body(body_len)
    return [
        ("sk", "sk-" + b, "<redacted:sk>"),
        ("bearer", "Bearer " + b, "<redacted:bearer>"),
        ("token", "token: " + b, "token: <redacted:token>"),
        ("token C-F3a", "AGENT_TOKEN: " + b, "AGENT_TOKEN: <redacted:token>"),
        ("envval", "API_KEY=" + b, "API_KEY=<redacted:envval>"),
        ("envval C-F3b", '"api_key": "' + b + '"', '"api_key": "<redacted:envval>"'),
        ("envval TOKEN name, short value", "SECRET_TOKEN = " + b[:20], "SECRET_TOKEN = <redacted:envval>"),
        ("envval base64url token value", "token: " + b[:16] + "-" + b[16:32], "token: <redacted:envval>"),
        (
            "privkey",
            "-----BEGIN RSA PRIVATE KEY----- " + b + " -----END RSA PRIVATE KEY-----",
            "<redacted:privkey>",
        ),
        (
            "privkey GnuPG",
            "-----BEGIN PGP PRIVATE KEY BLOCK----- " + b + " -----END PGP PRIVATE KEY BLOCK-----",
            "<redacted:privkey>",
        ),
    ]


def _assert_bounded_and_clean(qid, out, context):
    text = canonical(out)
    leaked = sorted(set(text) & _BODY_ALPHABET)
    assert not leaked, f"{context}: secret body bytes {leaked} in the decision state {text!r}"
    for (q, key), limit in list(_BOUNDED.items()) + list(_ENUM_BOUNDED.items()):
        if q != qid:
            continue
        assert len(out[key]) <= limit, f"{context}: {key} has {len(out[key])} > {limit} characters"
        assert out[key] == out[key].rstrip(), f"{context}: {key} ends with whitespace"


def test_normalize_never_cuts():
    # A1: normalize keeps every other step and no longer cuts a bounded field.
    state = dict(_BASE["ap.violates_row"], action_excerpt="a" * 399 + "  b" + " c" * 100)
    assert normalize("ap.violates_row", state)["action_excerpt"] == "a" * 399 + " b" + " c" * 100
    finding = {
        "lane": "pc-j1-1--330803c",
        "finding_id": "F-1",
        "title": "  " + "t " * 100,
        "paths": ["b.py", "a.py"],
        "disposition": "non-blocking",
    }
    out = normalize("v1.finding_class", finding)
    assert out == {
        "lane": "pc-j1-1",
        "finding_id": "F-1",
        "title": ("t " * 100).strip(),
        "paths": ["a.py", "b.py"],
        "disposition": "NON-BLOCKING",
    }


def test_straddle_every_class_every_bounded_key():
    # A2 + A5: a secret that STRADDLES a bounded key's limit -- its first k
    # characters before the limit, the rest after it, for k = 1 .. len-1 --
    # is replaced whole before the cut. No body byte survives, the digest
    # equals the placeholder form's, every bounded field is within its limit,
    # and decision_state is a fixed point of itself (the sweep moves the cut
    # through every position inside every placeholder).
    cases = 0
    for (qid, key), limit in _BOUNDED.items():
        for cls, secret, placeholder in _forms():
            for k in range(1, min(len(secret), limit - 1)):
                prefix = "a" * (limit - k - 1) + " "
                state = dict(_BASE[qid], **{key: prefix + secret + " tail"})
                clean = dict(_BASE[qid], **{key: prefix + placeholder + " tail"})
                context = f"{qid}.{key} {cls} k={k}"
                assert state_digest(qid, state) == state_digest(qid, clean), (
                    f"{context}: the straddling secret does not hash as its placeholder form"
                )
                out = _decision_state(qid, state)
                _assert_bounded_and_clean(qid, out, context)
                assert _decision_state(qid, out) == out, f"{context}: not idempotent"
                cases += 1
    assert cases > 5000, cases


def test_over_limit_identity_every_class():
    # A5 / item 6 for over-limit fields: the secret sits wholly INSIDE the
    # limit and a long tail takes the field past it. The secret-bearing state
    # hashes IDENTICAL to the state with the placeholder in its place
    # (VERIFY-J1-1 section 4 measured 374 vs 400 kept characters at the PIN).
    cases = 0
    for (qid, key), limit in _BOUNDED.items():
        for cls, secret, placeholder in _forms():
            if len(secret) + 4 > limit:
                continue
            tail = " " + "w" * (2 * limit)
            state = dict(_BASE[qid], **{key: "a b " + secret + tail})
            clean = dict(_BASE[qid], **{key: "a b " + placeholder + tail})
            context = f"{qid}.{key} {cls}"
            assert state_digest(qid, state) == state_digest(qid, clean), (
                f"{context}: an over-limit field breaks the secret/placeholder identity"
            )
            out = _decision_state(qid, state)
            _assert_bounded_and_clean(qid, out, context)
            assert out == _decision_state(qid, clean), context
            cases += 1
    assert cases >= 90, cases


def test_private_key_blocks_longer_than_the_limit_gnupg_and_endless():
    # A4 privkey: the transcript scrubber's label family (PEM, OpenSSH and
    # GnuPG armor), a block longer than the field's limit, and a block whose
    # END line is missing (redacted to the end of the value, VERIFY-J1-1 F-11).
    body = "\n".join(_body(64) for _ in range(24))  # a FAKE 1,559-character body
    labels = (
        "RSA PRIVATE KEY",
        "PRIVATE KEY",
        "OPENSSH PRIVATE KEY",
        "ENCRYPTED PRIVATE KEY",
        "PGP PRIVATE KEY BLOCK",
        "PGP SECRET KEY BLOCK",
    )
    for label in labels:
        for with_end in (True, False):
            block = f"-----BEGIN {label}-----\n{body}"
            if with_end:
                raw = "block follows: " + block + f"\n-----END {label}-----" + " then more"
                want = "block follows: <redacted:privkey> then more"
            else:
                raw = "block follows: " + block + " and words after it"
                want = "block follows: <redacted:privkey>"
            state = dict(_BASE["wf.drift"], observed=raw)
            clean = dict(_BASE["wf.drift"], observed=want)
            context = f"{label} end={with_end}"
            redacted = redact(normalize("wf.drift", state))
            assert redacted["observed"] == want, f"{context}: {redacted['observed'][:80]!r}"
            assert state_digest("wf.drift", state) == state_digest("wf.drift", clean), context
            out = _decision_state("wf.drift", state)
            _assert_bounded_and_clean("wf.drift", out, context)
            assert out["observed"] == want, context


def test_token_assignment_forms_redacted():
    # A4 / C-F3a: a 32+ [A-Za-z0-9+/] run after token, *_token or *_TOKEN in
    # the assignment forms is redacted (VERIFY-J1-1 sections 4 and 8). The
    # forms the PIN caught stay caught, in the same class.
    run = _body(40)
    forms = [
        (f"token = {run}", "token = <redacted:token>"),
        (f"access_token={run}", "access_token=<redacted:token>"),
        (f'"token": "{run}"', '"token": "<redacted:token>"'),
        (f"PC_BRIDGE_TOKEN: {run}", "PC_BRIDGE_TOKEN: <redacted:token>"),
        (f"AGENT_TOKEN: {run}", "AGENT_TOKEN: <redacted:token>"),
        (f"token: {run}", "token: <redacted:token>"),
        (f"Token={run}", "Token=<redacted:token>"),
        (f"token {run}", "token <redacted:token>"),
        (f"X-Agent-Token: {run}", "X-Agent-Token: <redacted:token>"),
        (f"PC_BRIDGE_TOKEN={run}", "PC_BRIDGE_TOKEN=<redacted:envval>"),
    ]
    for raw, want in forms:
        state = {"file": "src/a.py", "kind": "k", "msg": "set " + raw + " now"}
        clean = {"file": "src/a.py", "kind": "k", "msg": "set " + want + " now"}
        got = redact(normalize("b1.finding_sev", state))["msg"]
        assert got == "set " + want + " now", f"{raw!r} -> {got!r}"
        assert state_digest("b1.finding_sev", state) == state_digest("b1.finding_sev", clean), raw


def test_env_assignment_forms_redacted_and_prose_kept():
    # A4 / C-F3b: the env-assignment names matched without regard to case,
    # with optional spaces around "=" or ":" and an optional quote; a value of
    # 8+ characters becomes the envval placeholder and the name is kept. The
    # PIN's upper-case NAME=value form stays, for any value length.
    value = _body(20)
    forms = [
        (f"password={value}", "password=<redacted:envval>"),
        (f"PASSWORD = {value}", "PASSWORD = <redacted:envval>"),
        (f"password: {value}", "password: <redacted:envval>"),
        (f"SECRET_KEY: {value}", "SECRET_KEY: <redacted:envval>"),
        (f'"api_key": "{value}"', '"api_key": "<redacted:envval>"'),
        (f"db_passwd='{value}'", "db_passwd='<redacted:envval>'"),
        (f"API_KEY={value}", "API_KEY=<redacted:envval>"),
        ("KEY=x", "KEY=<redacted:envval>"),
    ]
    for raw, want in forms:
        state = {"file": "src/a.py", "kind": "k", "msg": "set " + raw + " now"}
        clean = {"file": "src/a.py", "kind": "k", "msg": "set " + want + " now"}
        got = redact(normalize("b1.finding_sev", state))["msg"]
        assert got == "set " + want + " now", f"{raw!r} -> {got!r}"
        assert state_digest("b1.finding_sev", state) == state_digest("b1.finding_sev", clean), raw
    # Negative control: prose is not a secret. A value under 8 characters stays
    # (the transcript scrubber's floor, scripts/transcript_export.py:33).
    for prose in (
        "key: sorted order",
        "the owner key must be pinned before re-sign",
        "password: short",
        "set key = value pairs",
    ):
        state = {"file": "src/a.py", "kind": "k", "msg": prose}
        assert redact(normalize("b1.finding_sev", state))["msg"] == prose, prose


def test_env_assignment_redaction_does_not_backtrack_exponentially():
    # J1-1-R1 D-3: the PIN's nested name-prefix group "(?:[A-Z][A-Z0-9_]*_)*"
    # backtracked exponentially ("A_" * 26, 52 characters, took 8.6 s), and a
    # case-insensitive copy of it does the same on lower-case snake_case.
    # redact now sees a whole unbounded field (A1), so each input below must
    # finish at once: it takes microseconds without the nested group and
    # hours with it. The alarm interrupts a runaway match (the re engine
    # checks signals) and fails the test instead of hanging the suite.
    import signal

    class _Runaway(Exception):
        pass

    def _alarm(signum, frame):
        raise _Runaway()

    previous = signal.signal(signal.SIGALRM, _alarm)
    try:
        for text in ("A_" * 40, "a_" * 40, "Ab9_" * 30 + "x", "SECRET_" * 30 + "value"):
            signal.setitimer(signal.ITIMER_REAL, 5.0)
            try:
                out = redact({"msg": text})
            except _Runaway:
                pytest.fail(f"redact backtracked for over 5 s on {text[:24]!r}...")
            finally:
                signal.setitimer(signal.ITIMER_REAL, 0)
            assert out == {"msg": text}, text[:24]
    finally:
        signal.signal(signal.SIGALRM, previous)


def test_bound_cuts_code_points_strips_trailing_whitespace_every_field_within_limit():
    # A2: bound cuts each bounded field at its limit on a code-point boundary,
    # then strips trailing whitespace; lists and unbounded fields pass
    # unchanged; every bounded field is at most its limit.
    qid = "ap.violates_row"
    # VERIFY-J1-1 F-3: a cut right after a space no longer leaves the space.
    out = _decision_state(qid, dict(_BASE[qid], action_excerpt="a" * 399 + " b"))
    assert out["action_excerpt"] == "a" * 399
    # The cut counts code points, never bytes or UTF-16 units.
    for ch in ("é", "中", "\U0001f600"):
        out = _decision_state(qid, dict(_BASE[qid], action_excerpt=ch * 450))
        assert out["action_excerpt"] == ch * 400, repr(ch)
    # Every bounded field of every question type ends within its limit. Each
    # limit is a multiple of 5, so every cut lands right after a space here.
    for q, base in _BASE.items():
        state = dict(base)
        for (qq, key), limit in _BOUNDED.items():
            if qq == q:
                state[key] = "word " * limit
        out = _decision_state(q, state)
        normed = normalize(q, state)
        for key in base:
            limit = _BOUNDED.get((q, key))
            if limit is None:
                assert out[key] == normed[key], (q, key)
            else:
                assert out[key] == ("word " * limit)[:limit].rstrip(), (q, key)
                assert len(out[key]) == limit - 1, (q, key)
    # bound itself, called directly: a list and an unbounded field pass
    # unchanged; bounded fields are cut and stripped.
    got = _bound(
        "v1.finding_class",
        {
            "lane": "x" * 100,
            "finding_id": "f",
            "title": "t " * 100,
            "paths": ["z/b.py", "a.py"],
            "disposition": "BLOCKING",
        },
    )
    assert got == {
        "lane": "x" * 80,
        "finding_id": "f",
        "title": ("t " * 60).rstrip(),
        "paths": ["z/b.py", "a.py"],
        "disposition": "BLOCKING",
    }
    got = _bound("ap.violates_row", dict(_BASE[qid], action_target="t" * 500, action_excerpt="e" * 500))
    assert got["action_target"] == "t" * 500
    assert got["action_excerpt"] == "e" * 400
    with pytest.raises(DecisionStateError) as exc:
        _bound("not.a.question", {})
    assert str(exc.value) == "decision-question-unknown: not.a.question"


def test_decision_state_idempotent_including_a_cut_inside_each_placeholder():
    # A3: decision_state is a fixed point of itself (the ledger's fixed-point
    # check depends on it), including when the cut lands inside a placeholder.
    for qid in GOLDEN_IDS:
        fixture = _load(qid)
        for which in ("state", "variant"):
            out = _decision_state(qid, fixture[which], fixture.get("root"))
            assert _decision_state(qid, out) == out, (qid, which)
    texts = (
        "<redacted:sk>",
        "<redacted:bearer>",
        "token: <redacted:token>",
        "AGENT_TOKEN: <redacted:token>",
        "API_KEY=<redacted:envval>",
        "password: <redacted:envval>",
        "SECRET_TOKEN = <redacted:envval>",
        '"api_key": "<redacted:envval>"',
        "<redacted:privkey>",
    )
    cases = 0
    for (qid, key), limit in _BOUNDED.items():
        for text in texts:
            for cut in range(1, len(text)):
                state = dict(_BASE[qid], **{key: "a" * (limit - cut - 1) + " " + text + " tail"})
                out = _decision_state(qid, state)
                assert out[key].endswith(text[:cut].rstrip()), (qid, key, text, cut, out[key][-40:])
                assert _decision_state(qid, out) == out, (qid, key, text, cut)
                cases += 1
    assert cases > 1000, cases


def test_state_digest_is_sha256_of_canonical_decision_state():
    # A3: ONE public composition, exported from agent_factory.decisions, and
    # state_digest = sha256(canonical(decision_state(...))).
    import hashlib

    import agent_factory.decisions as decisions

    assert "decision_state" in decisions.__all__
    states = []
    for qid in GOLDEN_IDS:
        fixture = _load(qid)
        states.append((qid, fixture["state"], fixture.get("root")))
        states.append((qid, fixture["variant"], fixture.get("root")))
    states.append(
        (
            "ap.violates_row",
            dict(_BASE["ap.violates_row"], action_excerpt="a" * 390 + " sk-" + _body(40) + " tail"),
            None,
        )
    )
    states.append(("wf.drift", dict(_BASE["wf.drift"], observed="word " * 200), None))
    for qid, state, root in states:
        text = canonical(decisions.decision_state(qid, state, root))
        assert state_digest(qid, state, root) == hashlib.sha256(text.encode("utf-8")).hexdigest(), qid


# ---------------------------------------------------------------------------
# The D-1 ruling (coordinator, option D). The class order, first match wins:
# privkey, sk, bearer, the upper-case NAME=value env form (TOKEN included,
# as at the PIN), the token class (a 32+ run after a TOKEN name), then the
# widened env form WITH TOKEN, whose guard never replaces a value that
# already is a placeholder. The placeholders are pinned here, not imported.
# ---------------------------------------------------------------------------

_PLACEHOLDER_TEXTS = (
    "<redacted:sk>",
    "<redacted:token>",
    "<redacted:bearer>",
    "<redacted:envval>",
    "<redacted:privkey>",
)

# (id, raw text, the redacted text). Each shape leaked before the ruling: the
# widened env form left TOKEN out (J1-1-R1 report, D-1).
_RESIDUAL_SHAPES = [
    ("token-colon-short", "token: " + _body(10), "token: <redacted:envval>"),
    ("underscore-token-equals-short", "access_token=" + _body(10), "access_token=<redacted:envval>"),
    ("prefixed-upper-spaced-short", "SECRET_TOKEN = " + _body(10), "SECRET_TOKEN = <redacted:envval>"),
    ("bridge-name-colon-short", "PC_BRIDGE_TOKEN: " + _body(10), "PC_BRIDGE_TOKEN: <redacted:envval>"),
    ("base64url-dash", "token: " + _body(16) + "-" + _body(16), "token: <redacted:envval>"),
    ("base64url-underscore", "token: " + _body(16) + "_" + _body(16), "token: <redacted:envval>"),
    ("run-then-base64url-tail", "token: " + _body(40) + "-" + _body(12), "token: <redacted:envval>"),
]


@pytest.mark.parametrize(
    "raw, want",
    [(raw, want) for _, raw, want in _RESIDUAL_SHAPES],
    ids=[shape_id for shape_id, _, _ in _RESIDUAL_SHAPES],
)
def test_token_named_residual_shape_redacted(raw, want):
    # A TOKEN-named assignment whose value is NOT a 32+ [A-Za-z0-9+/] run
    # becomes envval through the widened form, which runs after the token
    # class; no byte of the value survives.
    state = {"file": "src/a.py", "kind": "k", "msg": "set " + raw + " now"}
    clean = {"file": "src/a.py", "kind": "k", "msg": "set " + want + " now"}
    got = redact(normalize("b1.finding_sev", state))["msg"]
    assert got == "set " + want + " now", f"{raw!r} -> {got!r}"
    assert not (set(got) & _BODY_ALPHABET), got
    assert state_digest("b1.finding_sev", state) == state_digest("b1.finding_sev", clean), raw


def test_token_run_keeps_the_token_placeholder_and_no_placeholder_is_relabelled():
    # A 32+ run after a TOKEN name ends with the token placeholder only --
    # never an envval around it -- because the widened env form's guard never
    # replaces a value that already is a placeholder.
    run = _body(40)
    for lead in (
        "token = ",
        "access_token=",
        '"token": "',
        "PC_BRIDGE_TOKEN: ",
        "AGENT_TOKEN: ",
        "token: ",
        "Token=",
        "X-Agent-Token: ",
    ):
        got = redact({"msg": lead + run})["msg"]
        assert got == lead + "<redacted:token>", f"{lead + run!r} -> {got!r}"
    # The guard holds for every placeholder after a widened-form name, whole
    # or as the bound cut it (every prefix the value pattern could match).
    for lead in ("password: ", "token = ", '"api_key": "'):
        for placeholder in _PLACEHOLDER_TEXTS:
            for end in range(8, len(placeholder) + 1):
                text = lead + placeholder[:end]
                assert redact({"msg": text})["msg"] == text, text


# ===========================================================================
# J1-1-R2 -- AMENDMENT 2 to J1-1 (D-057; tasks/briefs/laya/J1-1-R2-brief.md,
# B1-B5): a secret NAME that the sk or bearer class would swallow never frees
# its value (VERIFY-J1-1-R1 V-1: "task-password: v" gave "ta<redacted:sk>: v"
# and v reached the ledger). sk and bearer still fire where their PIN forms
# fire; the run they replace ends before a secret assignment that a later
# class redacts, unless that value holds another assignment head (then the
# PIN's output stays, byte for byte).
#
# The rows are the brief's appendix driver, each as b1.finding_sev's msg.
# FAKE bodies only: "QZJ8" runs. No other byte of these states is a Q, Z, J
# or 8, so "no byte of the value" is checked one character at a time.
# ===========================================================================

_V = "QZJ8" * 5  # the driver's 20-character FAKE value body
_RUN = "QZJ8" * 10  # the driver's 40-character FAKE token run
_DRIVER_BODY = frozenset("QZJ8")

# (id, raw text, the redacted text). Each leaks at the PIN.
_V1_ROWS = [
    ("V1-a", f"task-password: {_V}", "ta<redacted:sk>password: <redacted:envval>"),
    ("V1-b", f"ask-password={_V}", "a<redacted:sk>password=<redacted:envval>"),
    ("V1-c", f'"task-password": "{_V}"', '"ta<redacted:sk>password": "<redacted:envval>"'),
    ("V1-d", f"desk-secret_key: {_V}", "de<redacted:sk>key: <redacted:envval>"),
    ("V1-e", f"flask-access_token={_RUN}", "fla<redacted:sk>token=<redacted:token>"),
    ("V1-f", "disk-PASSWORD=QZJ8QZ", "di<redacted:sk>PASSWORD=<redacted:envval>"),
    ("V1-g", f"bearer my-service-password: {_V}", "<redacted:bearer>password: <redacted:envval>"),
    ("V1-h", f"sk-abcdefgh-password={_V}", "<redacted:sk>password=<redacted:envval>"),
]
# The driver's controls keep the PIN's redaction byte for byte. C-4 is the
# row the verifier's option B leaks: a bearer token followed by a colon.
_V1_CONTROLS = [
    ("C-1", f"mask-token: {_RUN}", "mask-token: <redacted:token>"),
    ("C-2", f"task-api_key: {_V}", "task-api_key: <redacted:envval>"),
    ("C-3", f"db_password={_V}", "db_password=<redacted:envval>"),
    ("C-4", f"Authorization: Bearer {_V}: rejected", "Authorization: <redacted:bearer>: rejected"),
    ("C-5", f"key sk-{_V} used", "key <redacted:sk> used"),
    ("C-6", f'"sk-{_V}"', '"<redacted:sk>"'),
]
# The same class beyond the driver. The first ten leak at the PIN: each other
# secret name (after a prefix with ":" or "=", and as an upper-case NAME= with
# a short value, V1-f's form), and the token class's space form. The last
# nine keep the PIN's own output: a value that holds a second assignment head
# (each assignment form; an upper-case NAME='s value runs past ";" and the
# token class's space head counts too: the value would swallow that name and
# free its value), a token whose tail spells a name but no value follows, a
# lower-case "=" (the upper-case NAME= form is case-sensitive), base64 "="
# padding, and "token" with a space but no 32+ run.
_V1_CLASS_ROWS = [
    ("name-secret", f"desk-client_secret: {_V}", "de<redacted:sk>secret: <redacted:envval>"),
    ("name-passwd", f"desk-db_passwd={_V}", "de<redacted:sk>passwd=<redacted:envval>"),
    ("name-api_key", f"desk-my_api_key: {_V}", "de<redacted:sk>api_key: <redacted:envval>"),
    ("upper-key-short", "desk-SERVICE_KEY=QZJ8QZ", "de<redacted:sk>KEY=<redacted:envval>"),
    ("upper-token-short", "desk-SERVICE_TOKEN=QZJ8QZ", "de<redacted:sk>TOKEN=<redacted:envval>"),
    ("upper-secret-short", "desk-SERVICE_SECRET=QZJ8QZ", "de<redacted:sk>SECRET=<redacted:envval>"),
    ("upper-passwd-short", "desk-SERVICE_PASSWD=QZJ8QZ", "de<redacted:sk>PASSWD=<redacted:envval>"),
    ("upper-api_key-short", "desk-SERVICE_API_KEY=QZJ8QZ", "de<redacted:sk>API_KEY=<redacted:envval>"),
    ("token-space-sk", f"desk-access-token {_RUN}", "de<redacted:sk>token <redacted:token>"),
    ("token-space-bearer", f"bearer my-service-access-token {_RUN}", "<redacted:bearer>token <redacted:token>"),
    ("chain-widened", f"flask-tapasswd=aAPI_KEY : {_V}", "fla<redacted:sk>=aAPI_KEY : <redacted:envval>"),
    ("chain-upper", f"mask-PASSWORD=xtoken: {_V}", "ma<redacted:sk>=xtoken: <redacted:envval>"),
    ("chain-upper-past-a-stop", f"mask-PASSWORD=plainvalue;token: {_V}", "ma<redacted:sk>=plainvalue;token: <redacted:envval>"),
    ("chain-upper-token-space", f"mask-PASSWORD=abc_token {_RUN}", "ma<redacted:sk>=abc_token <redacted:token>"),
    (
        "chain-token-run",
        f"bearer my-service-access-token {'ab' * 16}key: {_V}",
        f"<redacted:bearer> {'ab' * 16}key: <redacted:envval>",
    ),
    ("no-value", f"Authorization: Bearer {_V[:13]}key: ok", "Authorization: <redacted:bearer>: ok"),
    ("lower-equals", f"Authorization: Bearer {_V[:13]}key=ok", "Authorization: <redacted:bearer>ok"),
    ("padding", f"Authorization: Bearer {_V}KEY==", "Authorization: <redacted:bearer>"),
    ("token-space-no-run", "bearer QZJ8-service-access-token ok", "<redacted:bearer> ok"),
]


def _assert_driver_row(raw, want):
    state = {"file": "src/a.py", "kind": "k", "msg": "set " + raw + " now"}
    out = _decision_state("b1.finding_sev", state)
    text = canonical(out)
    leaked = sorted(set(text) & _DRIVER_BODY)
    assert not leaked, f"{raw!r}: value body bytes {leaked} in {text!r}"
    assert "abcdefgh" not in text, f"{raw!r}: the sk value left its placeholder: {text!r}"
    assert out["msg"] == "set " + want + " now", f"{raw!r} -> {out['msg']!r}"
    assert _decision_state("b1.finding_sev", out) == out, f"{raw!r}: not a fixed point"
    # Two different FAKE values hash the same: the value is not state.
    other = dict(state, msg=state["msg"].replace("QZJ8", "Q8JZ"))
    assert other != state
    assert state_digest("b1.finding_sev", other) == state_digest("b1.finding_sev", state), raw


@pytest.mark.parametrize(
    "raw, want", [(raw, want) for _, raw, want in _V1_ROWS], ids=[row_id for row_id, _, _ in _V1_ROWS]
)
def test_v1_name_swallowed_by_sk_or_bearer_frees_no_value(raw, want):
    # B1 + B4 at decision_state: no byte of the value body in the output or in
    # canonical() of it, the exact redacted text, a fixed point of itself.
    _assert_driver_row(raw, want)


@pytest.mark.parametrize(
    "raw, want", [(raw, want) for _, raw, want in _V1_CONTROLS], ids=[row_id for row_id, _, _ in _V1_CONTROLS]
)
def test_v1_control_keeps_its_pin_redaction(raw, want):
    # B2: every control is redacted exactly as at the PIN (green at both; the
    # negative control is a mutant: the verifier's option B leaks C-4).
    _assert_driver_row(raw, want)


@pytest.mark.parametrize(
    "raw, want",
    [(raw, want) for _, raw, want in _V1_CLASS_ROWS],
    ids=[row_id for row_id, _, _ in _V1_CLASS_ROWS],
)
def test_v1_class_beyond_the_driver(raw, want):
    # B1 for the other names and the token space form; B2 for the guards
    # that keep the PIN's output where a yield would free or split nothing
    # new (each guard's negative control is a mutant that drops it).
    _assert_driver_row(raw, want)


def _v1_forms():
    """(id, a V-1 text, the same text with the value's placeholder in its
    place). The bodies are FAKE, over the Q Z X J body alphabet."""
    b, r = _body(20), _body(40)
    return [
        ("V1-a", "task-password: " + b, "task-password: <redacted:envval>"),
        ("V1-b", "ask-password=" + b, "ask-password=<redacted:envval>"),
        ("V1-c", '"task-password": "' + b + '"', '"task-password": "<redacted:envval>"'),
        ("V1-d", "desk-secret_key: " + b, "desk-secret_key: <redacted:envval>"),
        ("V1-e", "flask-access_token=" + r, "flask-access_token=<redacted:token>"),
        ("V1-f", "disk-PASSWORD=" + b[:6], "disk-PASSWORD=<redacted:envval>"),
        ("V1-g", "bearer my-service-password: " + b, "bearer my-service-password: <redacted:envval>"),
        ("V1-h", "sk-abcdefgh-password=" + b, "sk-abcdefgh-password=<redacted:envval>"),
    ]


def test_v1_rows_straddle_every_bounded_key_and_stay_fixed_points():
    # B1 + B4 under the bound: each V-1 text straddles every bounded key's
    # limit at every cut position. No body byte survives, the digest equals
    # the value-placeholder form's, every field is within its limit, and
    # decision_state is a fixed point of itself -- also when the cut lands
    # right after the name (a form that stayed silent there would redact the
    # bare "sk-password" on the second pass).
    cases = 0
    for (qid, key), limit in _BOUNDED.items():
        for row_id, secret, clean_text in _v1_forms():
            for k in range(1, min(len(secret), limit - 1)):
                prefix = "a" * (limit - k - 1) + " "
                state = dict(_BASE[qid], **{key: prefix + secret + " tail"})
                clean = dict(_BASE[qid], **{key: prefix + clean_text + " tail"})
                context = f"{qid}.{key} {row_id} k={k}"
                assert state_digest(qid, state) == state_digest(qid, clean), (
                    f"{context}: the straddling value does not hash as its placeholder form"
                )
                out = _decision_state(qid, state)
                _assert_bounded_and_clean(qid, out, context)
                assert "abcdefgh" not in canonical(out), context
                assert _decision_state(qid, out) == out, f"{context}: not idempotent"
                cases += 1
    assert cases > 3000, cases


# The verifier's 43 shapes (VERIFY-J1-1-R1 report, section 2), rebuilt from
# its table: the 35 that are body-free after this repair -- the 27 the PIN
# redacts and the 8 V-1 rows. The other 8 still leak and are filed
# follow-ups (V-6: full-width and zero-width separators; V-7: SK-/Sk-, a
# 7-character mixed-case value, a lower-case PEM label).
_VERIFIER_SHAPES = [
    f"password: sk-{_V}",
    f"KEY=sk-{_V}",
    f"token = {_RUN}-QZJ8QZJ8",
    f"password: Bearer {_V}",
    f"PASSWORD=Bearer {_V}",
    f'api_key="Bearer {_V}"',
    f"TOKEN: Bearer {_V}",
    "the <redacted:token> is here",
    "password: <redacted:token>",
    "KEY=<redacted:token>",
    f"password: {_V} token: {_RUN}",
    f"sk-{_V} Bearer {_V}",
    f"API_KEY={_V} password: {_V}",
    f"password={_V},token={_RUN}",
    f"password:\t{_V}",
    f"password:\u00a0{_V}",
    f"password\u00a0: {_V}",
    f"password:\u3000{_V}",
    f"password:  {_V}",
    f"BEARER {_V}",
    f"bEaReR {_V}",
    f"ToKeN: {_RUN}",
    f"Password={_V}",
    f"Api_Key: {_V}",
    f"mask-token: {_RUN}",
    f"task-api_key: {_V}",
    f"db_password={_V}",
] + [raw for _, raw, _ in _V1_ROWS]


def test_verifier_shapes_keep_every_pin_redaction():
    # B2's differential as a test: no shape the PIN redacts leaks, every V-1
    # row is closed, and each output is a fixed point of decision_state.
    assert len(_VERIFIER_SHAPES) == 35
    for raw in _VERIFIER_SHAPES:
        state = {"file": "src/a.py", "kind": "k", "msg": "set " + raw + " now"}
        out = _decision_state("b1.finding_sev", state)
        text = canonical(out)
        leaked = sorted(set(text) & _DRIVER_BODY)
        assert not leaked, f"{raw!r}: value body bytes {leaked} in {text!r}"
        assert _decision_state("b1.finding_sev", out) == out, f"{raw!r}: not a fixed point"


# ===========================================================================
# J1-1-R3 -- AMENDMENT 3 to J1-1 (D-059; tasks/briefs/laya/J1-1-R3-brief.md,
# C1-C5): the sk/bearer yield guard reads the value its class actually takes.
# VERIFY-J1-1-R2 found three regressions of J1-1-R2, each a value body the
# PIN d556c9b redacted reaching the ledger, and one V-1 residue:
#   R-1  the bearer run lost the PIN's case-insensitive letters (U+0130,
#        U+0131, U+017F), so a token holding one stayed visible;
#   R-2  the token check read the run case-sensitively while _TOKEN does not,
#        so a special letter hid the next head and that head's value was freed;
#   R-4  the env checks judged a value before the bearer pass merged it with
#        the text after "bearer <run>", and the merged value swallowed the
#        next head (pure ASCII);
#   R-3  "NAME= v" (upper case, a space after "=") behind sk or bearer.
# In a chain row the FIRST value keeps the PIN's output (the chain design,
# the chain-* rows above): "plainval" or a run of "ab" stands there, and the
# FAKE "QZJ8" body is the value the PIN redacts. No other byte is a Q, Z, J
# or 8.
# ===========================================================================

_TR = "ab" * 16  # a 32-character token run that a chain row leaves as the PIN does

# Each row but the last leaks at J1-1-R2 (fb016d0): the token stays visible.
_R1_ROWS = [
    ("dotless-i-inside", f"Authorization: Bearer {_V[:8]}\u0131{_V}", "Authorization: <redacted:bearer>"),
    ("dotless-i-first", f"Authorization: Bearer \u0131{_V}", "Authorization: <redacted:bearer>"),
    ("long-s-tail", f"Authorization: Bearer {_V}\u017f{_V[:8]}", "Authorization: <redacted:bearer>"),
    ("dotted-I-inside", f"Authorization: Bearer {_V[:10]}\u0130{_V[:12]}", "Authorization: <redacted:bearer>"),
    ("ascii-control", f"Authorization: Bearer {_V}{_V[:8]}", "Authorization: <redacted:bearer>"),
]
# Each row but the last leaks at J1-1-R2: the token run's special letter hid
# the second head from the check, the run swallowed it and freed its value.
_R2_ROWS = [
    (
        "sk-dotless-i",
        f"sk-abcdefgh-token {_TR}\u0131password: {_V}",
        f"<redacted:sk> {_TR}\u0131password: <redacted:envval>",
    ),
    (
        "bearer-long-s",
        f"Bearer abcdefghijklmnop-token {_TR}\u017fkey={_V}",
        f"<redacted:bearer> {_TR}\u017fkey=<redacted:envval>",
    ),
    (
        "sk-quote-dotted-I",
        f'sk-abcdefgh_token"{_TR}\u0130secret: {_V}',
        f'<redacted:sk>"{_TR}\u0130secret: <redacted:envval>',
    ),
    ("ascii-control", f"sk-abcdefgh-token {_TR}password: {_V}", f"<redacted:sk> {_TR}password: <redacted:envval>"),
]
# Each row but the last leaks at J1-1-R2. The first five glue the value to
# "bearer": after the bearer pass the value runs on past "<redacted:bearer>"
# and swallows the next head -- behind the widened form, the upper-case NAME=
# form, a bearer's own yield, a head the bearer run leaves (that one also
# leaks at d556c9b), and a bearer run holding U+0131 (J1-1-R2 left that
# token visible: R-1). The control has a space before "bearer": no merge.
_R4_ROWS = [
    (
        "widened-bearer-padding",
        f"task-password:plainvalbearer abcdefghijklmnop==token: {_V}",
        "ta<redacted:sk>:plainval<redacted:bearer>token: <redacted:envval>",
    ),
    (
        "upper-bearer-padding",
        f"task-PASSWORD=plainvalbearer abcdefghijklmnop==token: {_V}",
        "ta<redacted:sk>=plainval<redacted:bearer>token: <redacted:envval>",
    ),
    (
        "bearer-yield-then-bearer",
        f"Bearer abcdefghijklmnoppassword:plainvalBearer abcdefghijklmnop)key: {_V}",
        "<redacted:bearer>:plainval<redacted:bearer>)key: <redacted:envval>",
    ),
    (
        "head-the-bearer-leaves",
        f"task-password:plainvalbearer abcdefghijklmnoppassword: {_V}",
        "ta<redacted:sk>:plainval<redacted:bearer>password: <redacted:envval>",
    ),
    (
        "special-letter-in-the-merged-run",
        f"task-password:plainvalbearer abcdefgh\u0131jklmnop==token: {_V}",
        "ta<redacted:sk>:plainval<redacted:bearer>token: <redacted:envval>",
    ),
    (
        "space-before-bearer-control",
        f"task-password:plainval bearer abcdefghijklmnop==token: {_V}",
        "ta<redacted:sk>password:<redacted:envval> <redacted:bearer>token: <redacted:envval>",
    ),
]
# C2 (R-3): an upper-case NAME, "=", a space, then the value, behind sk or
# bearer. Each row but the last leaks at d556c9b and at J1-1-R2. The padding
# form "NAME==v" behind sk or bearer is a declared residue (the lane report),
# deliberately not pinned here.
_R3_ROWS = [
    ("sk-name-space", f"task-DB_PASSWORD= {_V}", "ta<redacted:sk>PASSWORD= <redacted:envval>"),
    (
        "bearer-name-space",
        f"Authorization: Bearer abcdefghijklmnopAPI_KEY= {_V}",
        "Authorization: <redacted:bearer>API_KEY= <redacted:envval>",
    ),
    ("sk-value-then-name-space", f"sk-abcdefgh-SECRET= {_V}", "<redacted:sk>SECRET= <redacted:envval>"),
    ("no-prefix-control", f"DB_PASSWORD= {_V}", "DB_PASSWORD= <redacted:envval>"),
]
# C3: the three mutants VERIFY-J1-1-R2 showed surviving all 121 tests (its
# section 8), each a row that the mutant leaks and the code redacts: V-M3
# (the token check case-sensitive), V-M11 (the token check without its
# "_token" form), V-M4 (the head's token form case-sensitive, so a chain
# guard misses "_TOKEN <run>" and the upper-case value swallows it). The
# last row is for its V-M10 (_ENVVAL_HEAD without "APIKEY"): the NAME= check
# then no longer mirrors _ENVVAL, the run yields to "APIKEY='", and _ENVVAL's
# \S+ value swallows the next head and frees its value.
_MUTANT_ROWS = [
    ("V-M3-upper-token-space", f"desk-access-TOKEN {_RUN}", "de<redacted:sk>TOKEN <redacted:token>"),
    ("V-M11-underscore-token-space", f"desk-access_token {_RUN}", "de<redacted:sk>token <redacted:token>"),
    ("V-M4-upper-token-head-in-a-chain", f"mask-PASSWORD=abc_TOKEN {_RUN}", "ma<redacted:sk>=abc_TOKEN <redacted:token>"),
    (
        "V-M10-upper-apikey-chain",
        f"task-DB_APIKEY='plainvalue'&Secret = {_V}",
        "ta<redacted:sk>='plainvalue'&Secret = <redacted:envval>",
    ),
]
# C4 against J1-1-R2: the step over a bearer match is exact, so every value
# J1-1-R2 redacts here stays redacted. A glued "bearer" that is no merge
# (under 16 run characters: 7, and 15 with a head after it), a merge with no
# head after it, a head the bearer run consumes (its value one character
# under the widened form's 8), and a token run glued to a bearer (the token
# check takes no step: _TOKEN's run stops at the "<").
_MERGE_CONTROL_ROWS = [
    ("merge-no-head", f"task-password:{_V[:8]}bearer abcdefghijklmnop rest", "ta<redacted:sk>password:<redacted:envval> rest"),
    (
        "short-bearer-no-merge",
        f"task-password:{_V[:8]}bearer abcdkey: {_V[:8]}",
        "ta<redacted:sk>password:<redacted:envval> abcdkey: <redacted:envval>",
    ),
    (
        "bearer-run-of-15-glued",
        f"task-password:plainvalbearer bcdfghmnuvwbcdf==token: {_V}",
        "ta<redacted:sk>password:<redacted:envval> bcdfghmnuvwbcdf==token: <redacted:envval>",
    ),
    (
        "head-the-bearer-consumes",
        f"task-PASSWORD={_V[:8]}bearer abcdefghijklmnopapi_key= plainvl",
        "ta<redacted:sk>PASSWORD=<redacted:envval> plainvl",
    ),
    (
        "token-run-glued-to-bearer",
        f"sk-abcdefgh-token {_RUN[:32]}bearer abcdefghijklmnop",
        "<redacted:sk>token <redacted:token><redacted:bearer>",
    ),
]


def _rows(rows):
    return pytest.mark.parametrize(
        "raw, want", [(raw, want) for _, raw, want in rows], ids=[row_id for row_id, _, _ in rows]
    )


@_rows(_R1_ROWS)
def test_r1_bearer_run_takes_the_pin_letters(raw, want):
    # C1 (R-1): no byte of the token in the output or canonical(), the exact
    # redacted text, a fixed point of itself.
    _assert_driver_row(raw, want)


@_rows(_R2_ROWS)
def test_r2_token_check_reads_the_run_as_the_token_class_does(raw, want):
    # C1 (R-2): the second value is redacted; the run keeps the PIN's output.
    _assert_driver_row(raw, want)


@_rows(_R4_ROWS)
def test_r4_env_check_reads_the_value_after_the_bearer_merge(raw, want):
    # C1 (R-4): the value after the swallowed head is redacted.
    _assert_driver_row(raw, want)


@_rows(_R3_ROWS)
def test_r3_upper_name_equals_space_value_behind_sk_or_bearer(raw, want):
    # C2: "NAME= v" yields to the widened form, which redacts v.
    _assert_driver_row(raw, want)


@_rows(_MUTANT_ROWS)
def test_surviving_mutant_rows_stay_redacted(raw, want):
    # C3: green at J1-1-R2 and after; each negative control is its mutant.
    _assert_driver_row(raw, want)


@_rows(_MERGE_CONTROL_ROWS)
def test_bearer_merge_step_keeps_every_j1_1_r2_redaction(raw, want):
    # C4: green at J1-1-R2 and after; the negative controls are mutants (the
    # verifier's FIX-A as written, a step that re-enters the bearer run).
    _assert_driver_row(raw, want)
