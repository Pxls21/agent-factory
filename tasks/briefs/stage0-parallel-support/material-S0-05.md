# MATERIAL PACK — S0-05 (no direct model egress, over live units)

> EVIDENCE ONLY. Verbatim extraction + located inventory. No design, no judgement, no
> recommendation. Assembled 2026-09-07/08 from the working tree at branch
> `claude/soundbox-kit-migration-iz1jwf`, HEAD `cc46704`. Other lanes hold uncommitted edits.
> **The 18 defect classes and the mint-wide AF-AP rows are carried once in
> `material-S0-02.md` §7 — read that section with this pack.**

---

## 0. INVENTORY TABLE

| item | source file:line | exists? | venue |
|---|---|---|---|
| Seed per-proof block S0-05 | `seeds/seed-stage0-v1.yaml:423-441` | yes | — |
| Frozen `spike_to_class_mapping` entry (`selective-egress`) | `seeds/seed-stage0-v1.yaml:583-586`; `proofs/registry.yaml:33` | yes | — |
| Breakdown increment #6 (the Wave-0 mechanism spike) | `tasks/stage0-breakdown.md:57` | yes | sandbox |
| Breakdown increment #16 (the full proof) | `tasks/stage0-breakdown.md:67` | yes | PC |
| Pinned decision — the S0-05 split | `tasks/stage0-breakdown.md:23` | yes | — |
| Findings per-proof constraint | `docs/research/FINDINGS-STAGE0-v1.md:46` | yes | — |
| Findings §6a addendum 1 (bare netns is total isolation) | `docs/research/FINDINGS-STAGE0-v1.md:98-108` | yes | — |
| Council KC-1 | `docs/research/COUNCIL-VERDICT-STAGE0-v1.md:33` | yes | — |
| Council compromise 4 (the verbatim label) | `docs/research/COUNCIL-VERDICT-STAGE0-v1.md:29` | yes | — |
| Plan-doc seam `docs/05` §6 network segmentation | `docs/05_SECURITY.md:74-85` | yes | — |
| Plan-doc seam `docs/05` §8 release-blocking test | `docs/05_SECURITY.md:102` | yes | — |
| upstream pin `gvisor` (containment layer S0-05 meets) | `upstream.lock.yaml:39-43` | yes | — |
| `proofs/S0-05/` directory | `ls proofs/` | **no** | — |
| `proofs/S0-05/spec.json` / `result.json` / canaries | — | **no**; ledger state `ABSENT` | — |
| Registry entry S0-05 | `proofs/registry.yaml:16` | yes | — |
| Wave-0 spike artifact | `spikes/selective-egress/result.json` (54 lines) | yes — POSITIVE | sandbox |
| Wave-0 spike script | `spikes/selective-egress/probe.sh` (7,800 bytes, executable) | yes | sandbox (root) |
| gVisor rootless-network caveat | `spikes/runsc/result.json:35`, `:49-54` | yes | sandbox / PC |
| Live-unit venue | `PC-BRIDGE.md:69`; `tasks/stage0-breakdown.md:31` | yes | PC |
| Blocked marker for S0-05 | — | **no** (execution_proof) | — |
| Ledger task rows | `todo/BUILD-TASKLIST.md:63` (spike DONE), `:73` (#16 pending) | yes | — |

---

## 1. THE SEED

### 1.1 `seeds/seed-stage0-v1.yaml:423-441` (verbatim)

```yaml
- proof_id: S0-05
  classification: execution_proof
  wave: 2
  increment_index: 16
  ledger_denominator: execution
  spike_dependency: [selective-egress]
  fixture_format: paired positive/negative egress probes from inside the contained unit;
    mechanism spike artifact at spikes/selective-egress
  assertions:
  - 'mechanism (Wave 0, label: mechanism proven, containment unproven): a veth/proxy-shaped
    netns lets the unit reach the OmniRoute endpoint (positive leg) while a model endpoint
    fails with the exact denial reason (negative leg) — bare unshare is proven total-block
    and is NOT acceptable evidence'
  - 'full proof (live units): network canaries FAIL from every non-OmniRoute unit, and each
    canary first proves its positive control (the unit CAN reach its allowed target)'
  negative_control:
    mutation: switch the egress gate off -> the canary suite goes RED
    expected_failure_reason: 'egress-permitted: gate-disabled'
  owner_placeholder: none
```

### 1.2 Frozen `spike_to_class_mapping` entry (`seeds/seed-stage0-v1.yaml:583-586`, verbatim)

```yaml
- spike: selective-egress
  probe: veth/proxy netns where the unit reaches a local OmniRoute listener but not a model endpoint
  negative_effect: {affected_proof: S0-05, rescope: mechanism increment becomes an egress-broker design task, rule_id: map-egress-s005, note: KC-1}
  positive_effect: {affected_proof: S0-05, class: execution_proof, label: mechanism proven, containment unproven}
```

The registry's machine-read copy (`proofs/registry.yaml:33`, verbatim) — note the added
`rule_id` on the positive branch:

```json
  {"spike": "selective-egress", "probe": "veth/proxy netns where the unit reaches a local OmniRoute listener but not a model endpoint", "negative_effect": {"affected_proof": "S0-05", "rescope": "mechanism increment becomes an egress-broker design task", "rule_id": "map-egress-s005", "note": "KC-1"}, "positive_effect": {"affected_proof": "S0-05", "class": "execution_proof", "rule_id": "map-egress-s005", "label": "mechanism proven, containment unproven"}},
```

with the in-file coordinator note (`proofs/registry.yaml:28`, verbatim):

```
# COORDINATOR DECISION — RULE IDS (2026-09-03, updated 2026-09-04): every branch that names a class carries its rule_id IN THIS FILE (the seed's positive branches had none). The validator honours ONLY transitions declared here — no rule id lives in code (AF-AP-13). The runsc positive branch uses from_class/to_class (not the shorthand class) because the transition is cross-class (blocked_host→execution_proof). The dockerd positive branch declares an identity transition (blocked_host→blocked_host) because Docker working does not unblock S0-08.
```

`proofs/registry.yaml:16` records `"spike_dependencies": ["selective-egress"]` for S0-05,
matching the seed.

### 1.3 Seed constraints binding S0-05 (`seeds/seed-stage0-v1.yaml:103-113`, verbatim excerpts)

```yaml
- 'The wave-plan-v2 council verdict is SETTLED and must not be re-litigated: four-way
  proof classification, separate ledger denominators, Wave-0 spikes first, then Wave
  1 (S0-01/02/07 + decision shells), Wave 2 spine (S0-03/04/05), Wave 3 (S0-11)'
- Execution proofs are exactly S0-01, S0-02, S0-04, S0-05-mechanism, S0-07, S0-11;
  conformance-checked decisions are exactly S0-09, S0-10, S0-12
- Every proof ships a spec-time negative control that fails for a named exact reason
- All gates are deterministic and LLM-free; no LLM judge anywhere in the gate spine
```

**Recorded, not resolved:** the constraint list enumerates "S0-05-**mechanism**" among the
execution proofs, while the per-proof block (`:423-441`) carries both the mechanism assertion and
the "full proof (live units)" assertion under one `proof_id`, and `proofs/registry.yaml:16`
records `"assertion_count": 2` with a single `execution_proof` class.

---

## 2. THE BREAKDOWN

### 2.1 Increment #6 — the Wave-0 mechanism spike (`tasks/stage0-breakdown.md:57`, verbatim row)

```
| 6 | Spike: selective-egress (S0-05 mechanism) | `spikes/selective-egress/result.json` + the veth/proxy netns script | Positive leg: unit reaches a local OmniRoute-stand-in listener; negative leg: same unit fails a model endpoint with the exact denial reason; label `mechanism proven, containment unproven` | Bare `unshare --net` offered as evidence ⇒ rejected (blocks BOTH legs — Chairman probe); gate-off mutation ⇒ RED | in-sandbox (Wave 0; KC-1 if negative) |
```

### 2.2 Increment #16 — the full proof (`tasks/stage0-breakdown.md:67`, verbatim row)

```
| 16 | S0-05 full egress proof | `proofs/s0-05/` canary suite over live units | Every non-OmniRoute unit's canary FAILS after its positive control proves reachability of its allowed target | Egress gate off ⇒ suite RED (`egress-permitted: gate-disabled`) | Wave 2; depends on #6 mechanism + live units from #7/#14 |
```

### 2.3 Pinned decision with its rejected alternative (`tasks/stage0-breakdown.md:23`, verbatim)

```
| S0-05 split: mechanism (Wave 0, selective egress via veth/proxy — bare `unshare --net` is proven TOTAL block) vs full live-unit proof (Wave 2) | Wholesale host-deferral of S0-05 | council + Chairman probe |
```

Full table: `material-S0-02.md` §2.2.

### 2.4 Venue update clause (`tasks/stage0-breakdown.md:32`, verbatim excerpt)

```
S0-06 (#13); S0-05's full canaries (#16).
```

### 2.5 Ordering rationale clause (`tasks/stage0-breakdown.md:73-75`, verbatim excerpt)

```
#3–6 Wave-0 spikes in parallel (facts that reorder the plan); #7–12 Wave 1 in
parallel (disjoint components, real pinned binaries); #13 when its spike resolves; #14–16 the
spine (credential-gated S0-03 first so its RED-pending state is visible early);
```

### 2.6 NOT-built ledger lines touching S0-05

Breakdown-time (`:79-82`): "Nothing below exists yet: … any spike, any proof, any fixture …".
Live (`todo/BUILD-TASKLIST.md:32`, verbatim excerpt): "· ABSENT 4 — S0-02, S0-04, S0-05, S0-06".

Live rows (`todo/BUILD-TASKLIST.md:63, 73`, verbatim excerpts):
```
| s0-06-spike-selective-egress | #6 spike selective egress (S0-05 mechanism; veth/proxy, never bare unshare) | DONE 2026-09-04 — POSITIVE: veth pair + iptables in a dedicated network namespace; four legs all passed (positive: stand-in reached 200, negative-blocked-port: iptables DROP timeout, negative-external: no route, gate-off mutation: blocked port reachable after flushing iptables — de-vacuous). AF-AP-1 respected (NOT bare unshare --n…
```
```
| s0-16-s0-05-full-egress | #16 S0-05 full canary suite over live units | pending | s0-06, s0-07, s0-14 | every unit's canary FAILS after its positive control; gate-off → RED |
```

`todo/BUILD-TASKLIST.md:557` (verbatim excerpt): "S0-05 mechanism proven, containment unproven per
`map-egress-s005` — full canary suite over live".

### 2.7 Owner answers (`tasks/stage0-breakdown.md:84-89`)

None names S0-05; #16's `blocked-by` list includes `s0-14` (S0-03), whose credential answer is
quoted in `material-S0-03.md` §2.3.

---

## 3. FINDINGS + COUNCIL

### 3.1 Per-proof constraint (`docs/research/FINDINGS-STAGE0-v1.md:46`, verbatim)

```
| S0-05 | No direct model egress | Network canaries FAIL from every non-OmniRoute unit (`05` §8) |
```

### 3.2 Chairman-verified addendum 1 — the probe that reshaped S0-05 (`docs/research/FINDINGS-STAGE0-v1.md:92-108`, verbatim)

```
## 6a. Chairman-verified addenda (council session 2026-09-02, reproduced by coordinator)

The council verdict (`COUNCIL-VERDICT-STAGE0-v1.md`) adopted **wave-plan-v2** unanimously; the
Chairman's independent probes then surfaced two defects the panel missed. Both were REPRODUCED
by the coordinator before landing here:

1. **Bare netns is TOTAL isolation, not selective egress.** Probes (coordinator, this session):
   - `curl https://pypi.org/simple/` → `200` (positive control, normal shell)
   - `unshare --net -- curl https://pypi.org/simple/` → `curl (6)` DNS unresolvable
   - local listener `python3 -m http.server 9099 --bind 127.0.0.1`: host → `200`; inside
     `unshare --net` → `000` (curl rc=7 — the fresh namespace has its own empty loopback)
   Consequence: the proven Wave-0 mechanism blocks EVERYTHING, including a host-local
   OmniRoute. S0-05's architecture needs SELECTIVE egress (OmniRoute reachable, model
   endpoints not). The Wave-0 spike must therefore produce a veth/proxy-shaped selective
   design; a bare-netns canary offered as S0-05 evidence would be a vacuous negative control
   (admissible only as "mechanism exists" evidence, labeled *mechanism proven, containment
   unproven*).
```

### 3.3 Cross-cutting invariants (`docs/research/FINDINGS-STAGE0-v1.md:60-69`, verbatim excerpts)

```
- No-LLM-judge spine: all Stage 0 exit evidence is deterministic (exit codes, fixtures, header
  asserts, canary failures).
- Negative-control discipline: S0-02/S0-05/S0-08 are *defined by* their failing legs; every
  other proof needs at least one violating fixture failing for the exact expected reason.
- Environment blockers are surfaced, not routed around: if gVisor (or dockerd) cannot run here,
  the proof is delivered as spec + fixture + explicit `NOT run here: <reason>` + host runbook,
  never a fake green.
```

Environment row bearing on S0-05's venue (`:26`, verbatim): "| bwrap | ABSENT (unshare present) |
no bubblewrap isolation for local gates |"; and (`:27`) "| uid | 0 (root) | root-start/priv-drop
tests partially representable |".

### 3.4 Council lines that touch S0-05 (verbatim)

Acceptable compromise 4 (`docs/research/COUNCIL-VERDICT-STAGE0-v1.md:29`):
```
4. **S0-05 ships split**: mechanism in Wave 0, full architectural proof in Wave 2, labelled verbatim *"mechanism proven, containment unproven."*
```

Kill Criterion 1 (`:33`):
```
1. **If, within the first Wave-0 execution session, the S0-05 mechanism spike cannot demonstrate *selective* egress — a contained unit reaching OmniRoute while failing to reach a model endpoint** — then the verdict's Wave-0 placement of S0-05's mechanism is invalidated, and S0-05 must be re-scoped as an egress-broker design proof (veth/proxy) *before* any canary is authored. (Chairman probe evidence: the currently-proven mechanism blocks both legs.)
```

Unresolved question 4 (`:48`):
```
4. **Can S0-05's mechanism be made selective?** Unexamined by the panel. Chairman probe: a bare `unshare --net` netns blocks a host-local OmniRoute as thoroughly as it blocks the internet. Necessary for containment, insufficient for the architecture.
```

Recommended next step 2 (`:56`, verbatim):
```
2. Run the Wave-0 spike matrix as four independent, parallel, minutes-scale probes: Rust-1.95 availability · dockerd-in-sandbox · runsc static install · **selective**-egress netns (veth/proxy, not bare `unshare`). Each returns a fact that reorders the plan; none depends on another.
```

Recommended next step 5 (`:59`, the S0-05 clause) — quoted verbatim in `material-S0-02.md` §3.6.

Feynman's key insight (`:74`, verbatim):
```
- **Feynman** — *the mechanism/proof split.* His enforcement-round counterfactual refused the consensus's wholesale deferral of S0-05 and separated its containment *mechanism* (zero-dependency, minutes) from its *architectural proof* (needs a live OmniRoute-fronted unit), with an explicit flip condition. The probe ran, the mechanism worked, and the plan changed. This is the only position in the deliberation decided by measurement rather than argument. His self-indictment of his own 8/12 tally — bucketing S0-09/10/12 as "real-here" without separating decision content from checkable artifact — is what made the three-way split possible.
```

Ada's R2 correction (`:76`, verbatim excerpt):
```
Her R2 correction of Socrates — that S0-05's under-instrumentation is a *fixture* problem, not a *venue* problem, so his own remedy is executable here — is what unblocked S0-05 and set up Feynman's split.
```

Follow-up Trigger A (`:97`, verbatim excerpt): "if the selective-egress spike fails (KC-1) or
dockerd succeeds (KC-6), the wave plan's premises changed and the panel should re-cut Waves 1-2 on
the new capability table, with a seat added to argue schedule cost."

---

## 4. PLAN-DOC SEAMS AND PINS

### 4.1 `docs/05_SECURITY.md:74-85` (verbatim — §6 network segmentation, the table the canaries encode)

```
## 6. Network segmentation

| Source | Allowed destinations |
|---|---|
| `buzz-acp` | Buzz relay and local/private `hermes-acp` endpoint/process only |
| Hermes | OmniRoute, composite memory adapter, policy, approved tool broker |
| Memory adapter | ai-memory and audit sink |
| ai-memory | OmniRoute only when explicitly enabled for embeddings/consolidation |
| OmniRoute | Approved model providers and persistence dependencies |
| Dream/Foundry/candidate/evaluator | Isolated test services and artifact sink only |
| PandaProbe | Redacted telemetry sink and OmniRoute if reviewed judge/repair is enabled |
| HarnessRouter (conditional) | Approved harnesses and OmniRoute only |
```

### 4.2 `docs/05_SECURITY.md` other verbatim lines

`:6` — "2. All model/embedding API traffic goes through OmniRoute."
`:7` — "3. Compromised runtime and research code is contained from host, other scopes, secrets, and unrestricted egress."
`:21` — "| Direct model egress | No upstream keys, network enforcement | DNS/connection canaries and egress logs |"
`:102` — "- Hermes, ai-memory, dream, JIT, evaluator, PandaProbe, and conditional HarnessRouter cannot reach providers directly."
`:106` — "- gVisor host-read/escape and evaluation exfiltration canaries fail."

### 4.3 `docs/01_ARCHITECTURE.md:121` (verbatim)

```
| Runtime → host/network | gVisor, narrow mounts, resource limits, controlled egress |
```

`docs/01_ARCHITECTURE.md:95` (verbatim): "- OmniRoute failure fails the model turn; Hermes never
falls back to a direct provider."

### 4.4 `docs/02_COMPONENT_AUDIT.md:56` (verbatim — the boundary S0-05 does and does not cover)

```
- OmniRoute is sole model API egress, not automatically sole web/tool egress.
```

`docs/02_COMPONENT_AUDIT.md:80` (verbatim): "gVisor initially contains the whole Hermes runtime,
including tools; it is not per-tool isolation without a broker. The first-party policy service
provides fail-closed semantic authorization. Research/evaluation workers also use isolated gVisor
profiles."

### 4.5 `docs/09_PREMORTEM.md` (verbatim lines)

`:19` — "| 13 | Direct provider path returns during debugging | Upstream key in a non-OmniRoute service | Secret ownership rule, egress deny, recurring canaries |"
`:34` (stop-the-line) — "- any component reaches a model provider without OmniRoute;"
`:41` (stop-the-line) — "- production or research containment is bypassed."

### 4.6 `docs/07_BUILD_PLAN.md:13` (verbatim)

```
| S0-05 | No direct model egress | Network canaries fail from every non-OmniRoute unit |
```

### 4.7 `docs/06_EVALUATION.md:43` (verbatim — the same dimension in the evaluation plane)

```
| Security | Runtime and all research workers | Denial, escape, egress, secret, scope-leak tests |
```

`docs/11_DREAM_PHASE.md:84` (verbatim): "- Worker has no route to ai-memory admin, Buzz, policy
mutation, production workspace, or providers except a scoped OmniRoute analysis key if explicitly
enabled."

### 4.8 ADR

`docs/adr/0002-omniroute-sole-model-egress.md:16` (verbatim — Consequences): "OmniRoute is a
critical dependency and must be persistent, monitored, and load-tested. Direct fallback is
prohibited. Tool/web egress is a different boundary and still needs its own proxy and policy."
No ADR under `docs/adr/` is specifically about egress enforcement mechanics —
**NOT SPECIFIED in `docs/adr/`**.

### 4.9 `upstream.lock.yaml` pins bearing on the contained units (verbatim, `:21-43`)

```yaml
  omniroute:
    repository: https://github.com/diegosouzapw/OmniRoute.git
    commit: 488f57e9d3fccc8d1741fdf21d35d5730b118a18
    observed_version: 3.8.51
    license: MIT
    role: sole_model_api_gateway
  fubuki-os:
    repository: https://github.com/NerdHerderDani/fubuki-os.git
    commit: 7375e56d6a5dc857bfd43ceccbc09bbc817d575a
    observed_version: 0.1.0
    license: Apache-2.0
    role: governance_packet_compiler_and_bounds
  ai-memory:
    repository: https://github.com/akitaonrails/ai-memory.git
    commit: 73715b6f1b2f0abb0a8b0ed47c1f69b1bd1b806e
    observed_version: 1.39.0
    license: MIT
    role: durable_memory_substrate_for_four_logical_scopes
  gvisor:
    repository: https://github.com/google/gvisor.git
    commit: 80bb741691be65cedb6688ac518bef3664af0fcc
    license: Apache-2.0
    role: runtime_and_research_worker_containment
```

---

## 5. WHAT EXISTS TODAY

### 5.1 `ls -la proofs/S0-05/`

```
ls: cannot access 'proofs/S0-05/': No such file or directory
```

No spec, no canary suite, no result, no blocked marker. What exists is the Wave-0 spike (§6.2).

### 5.2 Registry entry (`proofs/registry.yaml:16`, verbatim)

```json
  {"proof_id": "S0-05", "title": "No direct model egress", "classification": "execution_proof", "wave": 2, "spike_dependencies": ["selective-egress"], "required_negative_controls": 1, "assertion_count": 2},
```

Ledger state (`proofs/ledger.json`):
```json
    {
      "classification": "execution_proof",
      "proof_id": "S0-05",
      "state": "ABSENT"
    },
```

### 5.3 Schemas

`spec.schema.json` / `result.schema.json` verbatim: `material-S0-02.md` §5.3. The spike artifact
S0-05 already has is governed by a third schema, `proofs/schemas/spike.schema.json` (verbatim,
`:6-44`):

```json
  "additionalProperties": false,
  "required": ["spike_id", "schema", "outcome", "ran_at", "env_fingerprint", "runs", "facts", "classification_effect", "not_verified"],
  "properties": {
    "spike_id": {"type": "string", "minLength": 1},
    "schema": {"const": "proofs/schemas/spike.schema.json"},
    "outcome": {"enum": ["positive", "negative", "errored"]},
    "ran_at": {"type": "string", "format": "date-time"},
    "env_fingerprint": {"type": "string", "minLength": 1},
    "runs": {
      "type": "array",
      "items": {
        "type": "object",
        "additionalProperties": false,
        "required": ["command", "exit_code", "stdout_digest"],
        "properties": {
          "command": {"type": "string"},
          "exit_code": {"type": "integer"},
          "stdout_digest": {"type": "string"}
        }
      }
    },
    "facts": {"type": "object"},
    "classification_effect": {
      "type": "array",
      "items": {
        "type": "object",
        "additionalProperties": false,
        "required": ["affected_proof", "from_class", "to_class", "rule_id"],
        "properties": {
          "affected_proof": {"type": "string", "pattern": "^S0-(0[1-9]|1[0-2])$"},
          "from_class": {"type": "string", "minLength": 1},
          "to_class": {"type": "string", "minLength": 1},
          "rule_id": {"type": "string", "minLength": 1},
          "reason": {"type": "string", "minLength": 1}
        }
      }
    },
    "not_verified": {"type": "array", "items": {"type": "string"}}
  }
```

### 5.4 Exemplars

S0-07 / S0-11 (execution) and S0-09 (decision): verbatim `spec.json`, checker skeletons and
S0-07's attestation block in `material-S0-02.md` §5.4.

S0-11's spec is the closest committed analogue of a paired-control isolation proof — its two
negative legs pin complete deterministic reasons
(`rubric-isolation-violation: credential env absent by construction`;
`rubric-isolation-violation: cwd-not-isolated,env-not-allowlisted,netns-not-isolated`) and its
checker carries the netns/loopback discriminator machinery
(`_net_ns` L91-95, `_iso_launch` L98-108, `_LoopbackListener` L111-132, `_nsenter_reach`
L174-194, `_capability_status` L311-332 — full skeleton in `material-S0-02.md` §5.4).

### 5.5 Runner and validator

Mint path `scripts/proof-runner:131-223` (verbatim in `material-S0-02.md` §5.5); validator check
map `scripts/validate-ledger` (verbatim in `material-S0-02.md` §5.6). The spike-specific
validator rule (`scripts/validate-ledger:373-393`, verbatim):

```python
def _mapped_spikes(root, registry, spike_schema, findings):
    names = sorted({rule["spike"] for rule in registry["spike_to_class_mapping"]})
    aliases = registry["class_aliases"]
    allowed = _allowed_transitions(registry)
    for name in names:
        path = root / "spikes" / name / "result.json"
        if not path.exists():
            continue
        try:
            artifact = _load_json(path)
        except Exception as error:
            findings.add(f"spike-artifact-invalid: {name} {error}")
            continue
        if not _validate(artifact, spike_schema, f"spike-artifact-invalid: {name}", findings):
            continue
        for effect in artifact["classification_effect"]:
            from_class = aliases.get(effect["from_class"], effect["from_class"])
            to_class = aliases.get(effect["to_class"], effect["to_class"])
            transition = (effect["affected_proof"], from_class, to_class)
            if transition not in allowed.get(effect["rule_id"], set()):
                findings.add(f"undeclared-transition: {name} {from_class}->{to_class}")
```

and the transition resolver it uses (`scripts/validate-ledger:345-370`, verbatim):

```python
def _branch_transition(effect, branch, aliases):
    affected = branch.get("affected_proof")
    if affected != effect.get("affected_proof"):
        return None
    if "from_class" in branch or "to_class" in branch:
        from_class = aliases.get(branch.get("from_class"), branch.get("from_class"))
        to_class = aliases.get(branch.get("to_class"), branch.get("to_class"))
        return (affected, from_class, to_class)
    class_name = aliases.get(branch.get("class"), branch.get("class"))
    if class_name:
        return (affected, class_name, class_name)
    return None


def _allowed_transitions(registry):
    aliases = registry["class_aliases"]
    allowed = {}
    for rule in registry["spike_to_class_mapping"]:
        for branch_name in ("negative_effect", "positive_effect"):
            branch = rule.get(branch_name)
            if not isinstance(branch, dict) or not branch.get("rule_id"):
                continue
            transition = _branch_transition(branch, branch, aliases)
            if transition:
                allowed.setdefault(branch["rule_id"], set()).add(transition)
    return allowed
```

---

## 6. VENUE FACTS

### 6.1 Which host each leg needs

`PC-BRIDGE.md:69` (verbatim excerpt): "- **PC via bridge:** … · the full S0-05 egress canaries
over live units."
`PC-BRIDGE.md:68` (verbatim excerpt): "- **Sandbox:** machinery (#1–2), fixture authoring, Fubuki
(S0-07), ADR shells (S0-09/10/12), rubric-isolation fixtures (S0-11), selective-egress netns
mechanism spike."

`spikes/pc-bridge/result.json:24` (verbatim — the PC's own network posture):
```json
  "network": "outbound curl to github.com -> 200 (unrestricted); cloudflared present",
```
`:27` (verbatim): `"ports_in_use": "5432 (pg), 8010 (vllm), 11434/11435 (ollama), 20128 (omniroute)"`.

`docs/OBSERVABILITY-RUNBOOK.md:44-46` (verbatim): "`NOT built.` here: no exporter, no envelope
emitter, no dashboards wired …".

### 6.2 What the Wave-0 spike proved — `spikes/selective-egress/result.json` (verbatim, whole file)

```json
{
  "spike_id": "selective-egress",
  "schema": "proofs/schemas/spike.schema.json",
  "outcome": "positive",
  "ran_at": "2026-09-04T08:24:06+00:00",
  "env_fingerprint": "ccr-sandbox:linux:6.18.44-fc-v24",
  "runs": [
    {
      "command": "ip netns exec egress-spike curl -sS --connect-timeout 5 http://10.200.0.1:12800/v1/models",
      "exit_code": 0,
      "stdout_digest": "259351a97ba4343b875fd93efd6a8d83feb615627514495296a44e57c1493113"
    },
    {
      "command": "ip netns exec egress-spike curl -sS --connect-timeout 5 http://10.200.0.1:12801/v1/models",
      "exit_code": 28,
      "stdout_digest": "cc2c5e906252b0896c90bd5b11dd905eff284884ffd7c86bb547ea38c6119927"
    },
    {
      "command": "ip netns exec egress-spike curl -sS --connect-timeout 5 http://1.1.1.1/",
      "exit_code": 7,
      "stdout_digest": "82f9f3cc636afcaf52ae6d962b7bb17056547ea1ed7e723b8179085e2b2effd1"
    },
    {
      "command": "iptables -F + -P ACCEPT inside netns, then curl the previously-blocked port",
      "exit_code": 0,
      "stdout_digest": "2eb09f16650f9c0ec4d84d95813ffe9f88fa5d5af258f58e4fd6548b670a6d30"
    }
  ],
  "facts": {
    "iproute2": "installed (apt)",
    "iptables": "available (/usr/sbin/iptables)",
    "ip_netns": "works (create, move veth, exec)",
    "veth_pairs": "works",
    "curl_inside_netns": "works",
    "af_ap_1_respected": "bare unshare --net NOT used; veth pair provides selective connectivity"
  },
  "classification_effect": [
    {
      "affected_proof": "S0-05",
      "from_class": "execution_proof",
      "to_class": "execution_proof",
      "rule_id": "map-egress-s005",
      "reason": "veth + iptables selective egress mechanism works in the sandbox: allowed traffic passes, blocked traffic is denied by the namespace firewall, and the gate-off mutation proves the gate is the barrier"
    }
  ],
  "not_verified": [
    "Full canary suite over live production units (Wave 2, increment #16)",
    "UDP/ICMP egress filtering (only TCP tested)",
    "DNS resolution inside the netns (no resolver configured)",
    "Performance and throughput under load",
    "Persistence across process restarts",
    "Integration with runsc/gVisor containment layer"
  ]
}
```

### 6.3 The spike's mechanism script — `spikes/selective-egress/probe.sh:1-58` (verbatim head)

```bash
#!/usr/bin/env bash
# Selective-egress spike: prove that a veth/proxy netns mechanism can
# selectively allow traffic to an OmniRoute stand-in while blocking
# everything else.  This is NOT bare `unshare --net` (AF-AP-1: total
# isolation blocks both legs).
#
# Architecture:
#   Host netns:  veth-host  10.200.0.1/24  — runs the stand-in listener
#   Test netns:  veth-egress 10.200.0.2/24 — iptables allow only 10.200.0.1:12800
#
# Positive leg: curl inside netns reaches the stand-in → 200
# Negative leg: curl inside netns to a blocked port → connection refused / timeout
set -euo pipefail

NS="egress-spike"
VETH_HOST="veth-host"
VETH_NS="veth-egress"
HOST_IP="10.200.0.1"
NS_IP="10.200.0.2"
ALLOWED_PORT=12800
BLOCKED_PORT=12801
RESULT_FILE="${1:-/dev/stdout}"
STANDIN_PID=""
BLOCKED_PID=""

cleanup() {
  [ -n "$STANDIN_PID" ] && kill "$STANDIN_PID" 2>/dev/null || true
  [ -n "$BLOCKED_PID" ] && kill "$BLOCKED_PID" 2>/dev/null || true
  ip link del "$VETH_HOST" 2>/dev/null || true
  ip netns del "$NS" 2>/dev/null || true
}
trap cleanup EXIT

echo "=== setup ===" >&2

ip netns del "$NS" 2>/dev/null || true
ip link del "$VETH_HOST" 2>/dev/null || true

ip netns add "$NS"
ip link add "$VETH_HOST" type veth peer name "$VETH_NS"
ip link set "$VETH_NS" netns "$NS"

ip addr add "${HOST_IP}/24" dev "$VETH_HOST"
ip link set "$VETH_HOST" up

ip netns exec "$NS" ip addr add "${NS_IP}/24" dev "$VETH_NS"
ip netns exec "$NS" ip link set "$VETH_NS" up
ip netns exec "$NS" ip link set lo up

ip netns exec "$NS" iptables -P OUTPUT DROP
ip netns exec "$NS" iptables -P INPUT DROP
ip netns exec "$NS" iptables -P FORWARD DROP

ip netns exec "$NS" iptables -A OUTPUT -d "$HOST_IP" -p tcp --dport "$ALLOWED_PORT" -j ACCEPT
ip netns exec "$NS" iptables -A INPUT  -s "$HOST_IP" -p tcp --sport "$ALLOWED_PORT" -j ACCEPT

ip netns exec "$NS" iptables -A OUTPUT -o lo -j ACCEPT
ip netns exec "$NS" iptables -A INPUT  -i lo -j ACCEPT

echo "=== stand-in listener on ${HOST_IP}:${ALLOWED_PORT} ===" >&2
```

(File is 7,800 bytes, mode `-rwxr-xr-x`; the remainder runs the four legs and writes the result
JSON to `$RESULT_FILE`.)

### 6.4 The gVisor interaction the spike explicitly did NOT test

`spikes/runsc/result.json:35` (verbatim fact): `"sandbox_network": "not supported rootless (host
network used)"`.
`spikes/runsc/result.json:49-54` (verbatim `not_verified`):
```json
  "not_verified": [
    "Docker + runsc integration (--runtime=runsc not tested; requires Docker daemon configuration)",
    "Podman + runsc integration (podman absent in sandbox; available on the PC)",
    "Network namespace isolation under gVisor (rootless mode uses host network)",
    "cgroup enforcement under gVisor rootless"
  ]
```
`spikes/selective-egress/result.json:52` (verbatim `not_verified` item): "Integration with
runsc/gVisor containment layer".

### 6.5 Blocked marker

**None.** S0-05 is `execution_proof` (`proofs/registry.yaml:16`); no `probe.json`, no
`blocked.json`.

---

## 7. CLASS PREFLIGHT

**The 18 defect classes** — verbatim in `material-S0-02.md` §7.2-§7.3.
**Mint-wide AF-AP rows** (AF-AP-36, AF-AP-56, AF-AP-27, AF-AP-29, AF-AP-30) — verbatim in
`material-S0-02.md` §7.5.

### 7.1 AF-AP rows whose mechanism names the S0-05 subject (egress, netns, containment, reachability)

`docs/INCIDENT-LOG.md:145` (AF-AP-1 — the S0-05 row itself, verbatim):
```
| AF-AP-1 | total-isolation instrument offered as a selective-egress negative control (the canary fails for a reason other than the gate under test) | `unshare --net` in any S0-05 fixture without a positive-control leg reaching the allowed target | findings §6a (Chairman probe, reproduced) | SWEPT(2026-09-04) — spike #6 landed the veth/iptables design with gate-off mutation |
```

`docs/INCIDENT-LOG.md:166` (AF-AP-22 — tautological isolation/reachability assertion, verbatim):
```
| AF-AP-22 | tautological isolation/reachability assertion — a containment check whose positive observation is satisfied by the ambient environment independent of the isolating mechanism, so a pass-through wrapper still "passes" | an isolation checker that runs its probe ONLY through the wrapper (`unshare`/`nsenter`/`firejail`), with no un-wrapped run of the same probe proving the assertion flips; "cannot reach $EXTERNAL_HOST" used as network-isolation proof inside an already-egress-filtered venue | S0-11 `net_isolated` (1.1.1.1 unreachable regardless of `unshare`), owner review 2026-09-04 | SWEPT(2026-09-04) — checker now proves netns IDENTITY (`/proc/self/ns/net` inode) + a loopback-listener reachability discriminator + a non-vacuity gate (same predicate re-run un-wrapped must breach every axis); `test_mutant_passthrough_unshare_caught`, `test_negative_control_covers_all_axes`. Design signature (missing paired control), not an AP_SCREEN regex; project sweep found no other isolation assertions. **Cycle-4 reopen:** the active network discriminator FAILED OPEN — `nsenter` returning `None` (never ran, e.g. non-root) was accepted as a pass, so the loopback discriminator never ran in green CI. Re-swept: it is now a REQUIRED PAIRED control (wrapped `net_reachable is False`, un-wrapped `is True`) and the preflight requires `nsenter` to actually run, deferring (exit 2) where it cannot rather than fail-open. Rule sharpened: an active discriminator that returns "could not run" is a DEFER, never a pass. `test_wrapped_child_has_fresh_cwd_and_refuses_listener`, `test_parent_observes_unwrapped_child_as_breached` |
```

`docs/INCIDENT-LOG.md:172` (AF-AP-28 — a security assertion that trusts the subject's self-report,
verbatim):
```
| AF-AP-28 | a security assertion trusts the SUBJECT's self-report — the isolated process reports its own uid/netns/env and the checker believes it; a fake/pass-through wrapper fabricates a clean report. Sibling: an isolation/privilege binary resolved via `PATH` can be replaced. | a checker that reads the child's stdout/JSON for its own isolation state; `unshare`/`nsenter`/`setpriv` invoked by bare name (PATH-resolved) rather than absolute path | S0-11 round-2 read a child-authored JSON report of uid/netns/env; `unshare --user --net` even makes the child self-report uid 65534 while its host uid stays 0 | SWEPT(2026-09-04) — the child only signals ready + blocks; the PARENT reads kernel truth from `/proc/<pid>/status|ns/net|environ` and `nsenter`s the child netns to test the listener; wrappers are absolute-path; a real privilege drop (`setpriv --reuid`) is used. `test_parent_observes_unwrapped_child_as_breached`, `test_positive_fails_without_real_isolation`. Rule = observe the subject from OUTSIDE (kernel/parent), never trust its self-report. Design signature |
```

`docs/INCIDENT-LOG.md:168` (AF-AP-24 — proxy capability preflight; the class that governs whether
a canary leg may run at all, and the runner-level DEFER, verbatim):
```
| AF-AP-24 | proxy capability preflight — a skip/availability guard tests a PROXY signal (a uid change) instead of the EXACT predicate the real check consumes, so it green-lights a host the real check then hard-fails | a `skipif`/availability probe that checks one capability while the checked code reads several (`/proc/self/ns/net`, a listener, a uid); preflight and consumer diverge | S0-11 round-2 pytest `_isolation_available` checked only uid; on a host with `/proc/self/ns/net` unreadable it ran and the positive check failed (owner: 2 failed) | SWEPT(2026-09-04) — the preflight IS the checker's own `--selftest` (parent+child netns readable + `unshare --user --net` runs); positive returns exit 2 (capability-unavailable) so pytest skips, never fails. Rule = preflight the exact consumer predicate. **Round-3 extension:** EVERY namespace-reading leg is gated, not a selected subset (round-2 left the four-axis negative test ungated → the owner's host failed it); `test_positive_defers_on_incapable_host` proves the incapable path returns exit 2. Verify every leg under BOTH a capable and an incapable environment. **Cycle-4 reopen:** "every leg gated" was still only the pytest DECORATOR — the checker's own `--rubric-neg` CLI mode never ran the preflight, so the canonical runner did not defer consistently on an incapable venue. Re-swept: every namespace-reading CLI leg (`positive`, `--rubric-neg`) runs `_capability_status` and returns exit 2; `test_every_namespace_leg_defers_on_incapable`. Gate the CONSUMER (the CLI leg), not just its test. **Cycle-5 reopen (recurrence 3):** the cycle-4 gating lived in the CHECKER; the CANONICAL runner (`scripts/proof-runner`) itself did NOT defer — it removed result.json FIRST then failed `leg-exit-mismatch … got 2`, destroying the capable-venue artifact, and the "canonical-invocation" test actually invoked the checker legs directly (skipped on incapable CI, so never exercised the runner). Re-swept: the runner treats exit 2 as DEFER and PRESERVES the artifact; `test_canonical_runner_defers_and_preserves_on_incapable_venue` + `test_canonical_runner_runs_on_capable_venue` drive the REAL runner in BOTH venue states. Rule: execute the actual consumer, in both venue states — a proxy test that bypasses the consumer proves nothing about it. Design signature |
```

`docs/INCIDENT-LOG.md:170` (AF-AP-26 — permissive-default / relative-only security predicate,
verbatim):
```
| AF-AP-26 | permissive-default / relative-only security predicate — a validator reads evidence with a safe default (`report.get(k, [])`) so MISSING evidence passes, or asserts only a relative bound (`uid != parent`) without the absolute floor (`uid != 0`) | `.get(field)`/`.get(field, <benign>)` on a required field in a gate; an identity/limit check that omits the absolute boundary | S0-11 round-2 `_violations` accepted `uid==0` for a non-root parent and defaulted missing `uid`/`env_keys` to a pass | SWEPT(2026-09-04) — mandatory-field check rejects a malformed report; uid axis asserts `!= parent AND != 0`. **Round-3 extension:** `isinstance(True, int)` and `isinstance(-1, int)` are BOTH true, so `uid: true`/`uid: -1` slipped the "typed" check — a numeric evidence field needs exact type + range (`type(x) is int and x >= 0`), never bare `isinstance(_, int)`. Here it is dissolved entirely: the uid is parsed from `/proc/<pid>/status` (kernel-supplied unsigned int), not a child-authored JSON value. `test_report_validation_root_and_missing`. Design signature |
```

`docs/INCIDENT-LOG.md:195` (AF-AP-51 — fail-closed encoded as a data value, verbatim):
```
| AF-AP-51 | fail-closed encoded as a data value — a boolean-intent decision ("fail closed") returned as a value the consumer interprets by membership/equality fails OPEN when the consumer does not recognise it (D5e's `frozenset({s, "FAIL_CLOSED"})` under `token in form`) | a sentinel string/element standing in for a decision; a consumer that tests `x in forms` | a fail-closed decision is a distinct boolean or an exception, and its test is a bound-exceeded input that must be REJECTED | 2026-09-06 VERIFY-D5e F1/F3 |
```

`docs/INCIDENT-LOG.md:148` (AF-AP-4 — sandbox-probe-as-world): quoted verbatim in
`material-S0-03.md` §7.1. Its parallel-execution cousin, AF-AP-59, is quoted in
`material-S0-08.md` §7.1.
