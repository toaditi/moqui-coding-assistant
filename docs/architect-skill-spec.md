# Architect agent — skill spec (living doc)

Source: the HEMP book ch. 5–6 (technical design) + the sponsor's hybrid
data-model doctrine (2026-07-11). Method: every observed failure becomes a
rule with its evidence; every engagement becomes an eval fixture. Owner:
the Agent Coach (maarg-agent-coach plugin). Covers the AUTHORING half of
the System Architect role (data statements → model → mappings → outlines);
the review half lives in `agents/moqui-architect.md` and is already strong.

## S. Data statements (book-derived seed rules)

- **S1.** One sentence per fact: subject–verb–object, any relationship verb.
  Readable by a nontechnical stakeholder — that is the artifact's purpose.
- **S2.** One statement for every piece of information an actor records or
  reviews — stated or implied — per story activity. Provenance per
  statement: the story step or R-rule it comes from.
- **S3.** Full story pass BEFORE grouping; grouping + dedupe BEFORE mapping;
  never model entity-by-entity as you go.
- **S4.** Map only where concepts truly align — "a product is not a web
  page." EXISTS / EXTEND / NEW are the only verdicts; UNVERIFIED is never
  dressed as EXISTS.
- **S5.** Statements are conceptual: no PK shapes, no field types, no
  entity names inside the statement text itself — those live in the
  mapping column.

## H. The hybrid data model (sponsor doctrine — absolute)

- **H1.** Three entity families share the database: customized OFBiz
  (`org.apache.ofbiz.*`), Moqui framework (`moqui.*`), HotWax custom
  (`co.hotwax.*`). Every mapping names its family AND its defining file.
- **H2.** Mappings resolve against the checked-out codebase (ofbiz-oms-udm
  + oms extensions, pinned versions) — NEVER against memory of upstream
  OFBiz, Mantle, or the HEMP book's appendix (which is Mantle-based: form
  yes, mappings no).
- **H3.** The local model is CUSTOMIZED: verify fields exist as claimed
  (e.g. `OrderItem.correspondingPoId` is a HotWax field, not vanilla
  OFBiz). A plausible upstream memory is the most dangerous kind of wrong.
- **H4.** Moqui framework entities are legitimate design citizens
  (SystemMessage, DataManagerConfig, StatusFlowTransition) — validated
  against framework source; adopted Moqui practices govern their use.

## Eval fixtures

| # | Fixture | Traps |
|---|---|---|
| AEC1 | Pre-Order data-statement pass, sitting 1 (story main flow) — fixture grows in maarg-agent-coach | unit-grain vs `correspondingPoId` order-grain mismatch must SURFACE, not map smoothly |

## Status

Seeded 2026-07-11, before the first training sitting. Rules from observed
failures land below as rounds, same as `ba-skill-spec.md`.

## Round 1 — sitting 1, Pre-Order main flow (2026-07-11)

Trainee: supplemented dispatch under the architect definition + this spec.
Result: **21 statements, PASS at the highest bar.** Coach spot-verified 8
citations in the entity XMLs/services — all exact. AEC1 (the planted
unit-grain catch) fully surfaced: verdict NEW with the nearest precedent
cited and shown misaligned at BOTH allocator sites (the full-cover skip
conditions), including the silent-skip collision with R13's spirit. Zero
failure rules this sitting — recorded honestly as a clean pass.

**Patterns codified from the trainee's own inventions:**
- **S6. End every sitting with an honesty ledger** — the UNVERIFIED list,
  stated plainly ("none of these were dressed as EXISTS"). Adopted as a
  required section of the deliverable.
- **H1a. The hybrid annotation:** a HotWax field extending an OFBiz entity
  is marked "[H field on O entity]" — the two-family reality of one
  mapping, visible at a glance.
- **S7. Smells ride along.** Name-vs-meaning mismatches found while mapping
  (a "confirmed" date in a field named "estimated"; a hold expressed as a
  location; one word covering two reservation mechanisms) are reported in a
  dedicated smells list — they are design input, not statement content.

Deliverable value beyond training: 8 smells, of which #1 (line-grain vs
unit-grain allocation, no spanning) and #3 (ATP as a bare counter with no
allocation ledger — cannot give units back) point at the same missing
concept and are expected to shape the NEW-entity phase.

## Round 2 — sittings 2–6 + consolidation, Pre-Order data-statement pass (2026-07-11)

Five section sittings (alternates, kits, regional, time-flow, R-sweep) run in
parallel + a consolidation pass. Result: **~100 statements → 47 deduped, PASS
throughout.** Every EXISTS carried family + defining file; the hybrid-model
discipline (H1–H4) held on every mapping. Coach spot-verified the boldest
claims in code — all exact.

**Demonstrated (encode as positive patterns, confirmed across five trainees):**
- **The honesty ledger (S6)** caught real limits every sitting — none dressed
  UNVERIFIED as EXISTS.
- **Smells-ride-along (S7)** surfaced FIVE latent existing-code defects while
  mapping (dead inverted kit guard; `thudate` typo; `prendingOrderCountList`
  NPE; dropped `CommunicationEvent` params; UDM-doc `pseudoId` drift). Bonus
  deliverable value far beyond the statements.
- **Convergent-concept synthesis** — the consolidation named "the Allocation
  Ledger" from six independent sitting findings (unit grain, give-back, kit
  components, region coverage, history, per-shipment sums). Codify:

- **S8. Consolidation names the concept.** Phase 2–3's job is not just
  dedupe — it is to NAME the new concepts that multiple NEW verdicts share,
  so the design phase gets one target, not six symptoms.
- **H5. A dead/defective precedent is still NEW, and its defects are
  reported.** When the only code shape for a required fact is dead code
  (zero callers) or defective (inverted guard, typo), the verdict is NEW —
  and the defect goes to the honesty/notes section, never cited as EXISTS.
- **H6. Never read the package name as provenance.** A HotWax entity can sit
  in an `org.apache.ofbiz.*` package (family masquerade); the defining file
  and author decide the family, not the namespace string.

**Infra note:** the safety-classifier outage blocked subagent dispatch for the
consolidation; the Coach performed phase 2–3 in the main session directly
(legitimate — consolidation is coach judgment work, not a delegable sitting).
The five parallel sittings had completed before the outage.

## Status

Rounds 1–2 complete; the authoring half of the architect role is validated on
a full real deliverable (the Pre-Order data-statement pass). AEC1 caught in
round 1; five latent defects surfaced in round 2. **Next:** sponsor/business
validation of the statements (plain true/false read), then fold the authoring
half + the Write-tool grant decision into `agents/moqui-architect.md`, then
replay AEC1.

## Round 3 — naming + verification-scope rules folded (2026-07-14)

Three generic authoring/review rules added to `agents/moqui-architect.md`, from
observed gaps:
1. **Meaningful status / enum / id values** — mechanism first
   (`StatusItem` + `StatusFlowTransition` for a guarded lifecycle vs a reason
   `Enumeration` for an append-only ledger row, which has NO status) → connect
   every value to its entity (`statusTypeId` / `enumTypeId`; prefixed `enumId`s) →
   name for the right subject → derive the PK from the archetype (Master → single
   `<entity>Id`; Detail → compound `{masterPK, <entity>SeqId}`) → verify
   collisions + VARCHAR(40) + framework type sizes.
2. **Verify beyond the pinned checkout** — check legacy/predecessor systems and
   newer/open PRs before any absence verdict; found-only-there → "reuse gated on a
   named dependency", never "gap".
3. **No strawman rejects for framework rules** — settled conventions are stated
   as facts; the rejected-alternative reasoning is only for genuine deviations.

**Eval (AEC2):** a generic entity-naming scenario — design the status, the reason
enum + enumType, and the PK for a sample master + append-only detail pair. The
right answer applies rule 1 (archetype-derived compound Detail PK; a
`statusTypeId`-connected status on the master; a reason `Enumeration` — not a
status — on the detail) and rule 3 (no strawman for the StatusFlowTransition
choice).

## Round 4 — three-engagement audit (2026-07-17, coach audit round 2)

Source: adversarial audit of the Pre-Order design package (PR #301 state) and the recovered
Transfer-Order v1 design, every finding verified in the source before landing here. Citation
fidelity was strong where it counts (10/10 spot-checked bold EXISTS claims EXACT in code; honesty
ledger and smells list real and used). The failures cluster in ARTIFACT MAINTENANCE and
SELF-LINT COVERAGE, not in code reading:

- **H7. Ruling-compliance sweep.** After any sponsor design-walk ruling, sweep EVERY design
  artifact for surviving instructions that contradict the ruling — an instruction the ruling
  reversed is a defect wherever it still stands. *Failure: data-statements.md still told builders
  to DROP `OrderInvPromiseHistory` after the Sponsor ruled KEEP (D6, 2026-07-13); the doc was
  edited after the ruling but never reconciled.*
- **H8. Cite the exemplar's ACTUAL mechanism.** Before claiming "exactly as X does it", re-read X —
  if the cited exemplar deliberately abandoned the mechanism you name, the claim is wrong.
  *Failure: FutureInvItemRes PK-generation claimed `setSequencedIdSecondary` "exactly as
  InventoryItemDetail" — the cited exemplar deliberately does NOT use it.*
- **H9. Deprecation status rides every reuse citation.** A cited reuse surface carries its
  lifecycle state; pointing a capability at a deprecated endpoint without saying so sells dead
  road. *Failure: D25/D23/D20 direct capability F at ProductStoreSetting REST endpoints without
  noting their deprecation.*
- **H10. Cross-check the package's own defect list before asserting "existing working
  capability".** A capability the same package's defect record shows NPE-ing on a live branch is
  not "existing working capability" — state both halves. *Failure: HOLD_PRORD_PHYCL_INV queue-hold
  presented as working while the package's defect list records the branch NPE.*
- **S9. Process outlines may only reference states the data design defines.** A lifecycle word
  ("promotes committed to reserved") that the entity design does not define — on rows the design
  declares immutable — is a state-machine contradiction. *Failure: A6 release mapping vs the Res
  design's append-only rows.*
- **S10. Package-currency sweep (the BA's G8, applied to design docs).** Internal citations
  (file/line/claim references between the package's own docs), pin tables, and version headers are
  re-derived before delivery. *Failures: design-proposal cites data-statement line numbers that no
  longer exist; three artifacts state three different pin sets; "draft v1" header on a
  sponsor-validated doc.*

**Review gate — the architect's pre-delivery self-lint (run on every authored artifact):**
1. Provenance coverage 100%: every statement row carries its story-step/R-rule. *(Failure: the
   PC1–PC10 table shipped with no provenance column.)*
2. Family-tag coverage 100%: every EXISTS/EXTEND mapping carries its [O]/[M]/[H] tag, and the tag
   matches the defining file. *(Failure: 23 of 92 rows untagged; one tag wrong by the doc's own
   rule.)*
3. Statement-text purity (S5): no system identifiers inside statement text; one fact per sentence.
4. Verdict vocabulary closed: only the declared verdict values appear.
5. Ruling-compliance sweep (H7) + internal-citation currency (S10).

