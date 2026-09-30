# SCRUB2-R1: the D-115 review (the deadlock break)

2026-09-30 03:4xZ. The coordinator's review under D-115 (skill `contract-gate` §4). The evidence is the round table,
`tasks/briefs/system1/SCRUB2-R1-ROUND-TABLE.md` (§ numbers below are its sections). The owner chooses.

## The answer

The scrubber's repair rounds stop here. Five verify rounds (R0 to R4) were all NOT-READY, and one class of blocker came
back in four rounds in a row. I recommend a REDESIGN: the PIN's scrubber runs first and whole, and the new rules run
after it, on its output. A new rule can then hide more text, but it can never show a value the PIN hid.

## Why the review is due

All four D-115 triggers hold.

| Trigger | Measured |
|---|---|
| The repair budget is spent | D-031's budget ended after round 3; D-108, D-112 and D-114 each allowed one more round (§4) |
| A blocker in a class an earlier round fixed | the run-over class (AF-AP-157) blocked rounds 1, 2, 3 and 4: B3, N2, R3V-1, R4V-1 (§3) |
| The blocker count does not fall | one blocker in round 3, one in round 4 (§4) |
| A repair made a blocker in the code it changed | round 1's repair made B1, B2, B3 and V4; round 2's made N1 and N2; round 4's keep branch is step 2 of R4V-1 (§4) |

Two more facts from the table. The next verifier falsified each builder's closure claim (C7). Two blockers were already
in the code one round before a verifier named them: R3V-1 in round 2, R4V-1 in round 3 (§3).

## The round table in short

| Round | Blockers, as ruled | In the run-over class | Fix the next round tried |
|---|---|---|---|
| R0 | F1, F7, F15 | none | read JSON escapes as escapes; bound the private-key rule |
| R1 | B1, B2, B3, V4 | B3 | linear classes; the Negotiate token kept on its line; an escape ends a value unless a value character follows |
| R2 | N1, N2 | N2 | floors count characters; three stops before later heads |
| R3 | R3V-1 | R3V-1 | an order: the PIN's heads first, the new heads after |
| R4 | R4V-1 | R4V-1 | a shield for kept values (round 5 on the cloud route, a record only; round 5Q running) |

## The assumption that failed

The repairs assumed that the no-loss item ("no redaction the PIN makes may be lost") can hold rule by rule: that each
new rule, and each changed PIN rule, can be tuned (a stop, a bound, a place in the order, a shield) so that it never
takes a later head's name.

The scrubber is a sequence of substitutions: `scrub()` in `scripts/transcript_export.py` loops over `SECRET_PATTERNS`.
Each rule changes the text that the next rule reads. So any change that moves where a value ends (a new head, an escape
rule, a floor) can take the name of a later head, and that head's rule then never fires. Each round closed the path its
verifier found, and the next verifier found another path. The paths are not a list that ends: each new head, escape or
floor adds more. Round 4 shows it. Its order put every new head after the PIN's heads, and the loss came from a CHANGED
PIN rule instead: the credentials floor, changed for F15 and N1, is step 1 of R4V-1 (VR4:85).

## The options

### A. REDESIGN: the PIN first, the new rules after it (recommended)

- **Design.** `scrub(text)` runs the PIN's rules (their bytes unchanged, except F7's one rule below), then the new rules
  over that output. `scrub_payload` runs the new rules after the PIN's whole `scrub_payload`. The PIN already uses this
  idea for its own payload rules: "Each rule matches only what scrub's named rules left" (`scripts/transcript_export.py`,
  the comment above `_PASS`).
- **Why no loss can happen.** The new rules read the PIN's output, where every value the PIN hides is already a
  marker. A substitution replaces text with a marker or keeps it; it never writes text that was not in its input. So the
  run-over class can make over-redaction, never a loss.
- **What it keeps.** F1's contexts: the new rules add a Cookie, pwd or credentials head after a JSON escape, a literal
  `\n`, a non-ASCII letter or an escaped quote. F7: the lenient private-key rule made linear, the one PIN rule that
  changes, checked by the no-loss differential. Round 2's linear classes (B1).
- **What it gives up: F15.** F15 is the PIN's own over-redaction. In the raw view, the credentials rule takes the next
  line of ordinary code: 11 raw regions in the corpus, 10 of them code or prose and the 11th a probe line; the decoded
  view is not affected (VERIFY-SCRUB2 §5g). To fix F15, the PIN's rule must hide less, and the no-loss item forbids
  that. V4 showed the conflict on one shape: 93 of 10,595 fake tokens lost (VR1:137). F15 stays open as a stated
  over-redaction, with no leak.
- **Cost.** One build lane and one verify. The change drops the stops, the order, the keep branch and the shield.
- **Convergence test (the verify's contract).**
  1. Zero losses against the PIN on every red file and generator of rounds 1 to 4 (the 12 R4V-1 items, round 3's 11,
     round 2's 16, the random differentials), in all six views.
  2. F7's rule hides every span that the PIN's rule hides, and it runs in linear time on the dash and no-END rows.
  3. F1's cases are hidden (VR0:159-190).
  4. Every new rule runs in linear time on the backslash rows (B1's class).
  5. The new rules' ordinary-text cost is measured on the corpus and stated (class C, F15's lesson).

  One loss against the PIN means the construction is wrong at its root. The scrubber then goes to PARK, never to a
  repair round.

### B. RE-SCOPE: F7 alone

- Land only F7's fix. File F1 and F15 as issues with their measured exposure (F1: 0 uncommitted instances; F15:
  over-redaction, no leak).
- Cost: a small lane and a short verify. Convergence test: zero losses against the PIN, and linear time on the dash
  rows.
- It gives up F1: a value after a JSON escape, a literal `\n`, a non-ASCII letter or an escaped quote stays visible.

### C. ONE MORE ROUND: verify round 5Q's shield

- Round 5Q is still running on the PC (launched 23:51Z on the raw local id, D-114).
- Cost: its verify lane. Convergence test: zero losses on the 12 R4V-1 items, the collision test and the generators.
- D-115 asks for a written reason. It would have to say why a fifth path-specific fix closes a class that four did not,
  and the shield's own brief names a flaw: a stand-in text can collide (BR5Q:75). I have no such reason.

### D. PARK

- Keep the PIN's scrubber (the tree has it now). File F1, F7 and F15 as issues. VERIFY-JEV-RELAY goes ahead on the
  PIN's scrubber.
- Cost: none now. The open risk: F1's missed contexts, and F7's quadratic time on a long dash run (0 present exposure;
  the longest dash run in the corpus is 278).

## The recommendation: A

- It ends the class by construction, not by closing one more path.
- Its test is binary: one loss against the PIN ends the program.
- Its price is F15, the one blocker that is an over-redaction and not a leak. Over-redaction is the safe side.

## Round 5Q under each choice

- A, B or D: round 5Q stops (one TERM to its lane pid). Its draft and patch stay on the PC as a record, as round 5's
  cloud build did. That frees the one long-context local lane (D-061).
- C: round 5Q runs to its end, then its verify.

## After a choice of A

A brief with the PIN (the tree's exporter: sha256 prefix 6ad316dc, last changed by cdbc1b8), this review, the round
table, and the convergence test above as its contract. Then a verify. VERIFY-JEV-RELAY (task #373) runs after the
redesign lands.
