"""J1-1 tests: normalize -> redact -> canonical -> sha256, the seven closed
state schemas, and the committed golden digests.

Every test is LLM-free and deterministic. The negative controls (the refusal
strings, the secret-leak assertions, the order discriminator) fail for the
EXACT expected reason. The golden digests are asserted EXACTLY (pasted, not
recomputed) and a re-landed variant per type must hash to the SAME digest.

The pipeline entry point under test is the public
``state_digest(question_id, state, root)`` = sha256(canonical(redact(normalize(state))));
the two transforms are also tested directly for their separation (normalize
never redacts, redact never normalizes).

Contract: tasks/briefs/laya/J1-1-brief.md (seeds/seed-laya-j1-v1.yaml AC 1 +
AC 3; the verdict's J1 acceptance test 1 + the KC-J6 field list).
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
