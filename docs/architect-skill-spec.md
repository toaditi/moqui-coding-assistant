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
| NREV1 | A review fixture: a design whose service queries a record list and loops it in Groovy, wrapping each element in `runRequireNew` to import/sync it | must verdict REDESIGN → MDM (one-record `importServiceName` + `DataManagerConfig`, `upload#DataManagerFile`); NOT accept the hand loop; NOT flag it only as a style nit |

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

## Round 5 — native graph I/O in the native-first ladder (2026-07-24, harvest)

Source: the order-mirror design engagement (sim-routing). A design flattened each order's entity
graph and wrote it to the LIVE mirror with a per-table raw-JDBC MERGE — the architect's native-first
ladder did not catch it. Moqui moves an entity GRAPH natively in **both** directions; ladder rung 1
now names it, and `assets/moqui-master-entity.md` + the `moqui-master-entity` skill carry the full
reference.

- **N1. Entity-graph get/store is native — flag raw SQL that moves a graph.** Reading a parent + its
  children is `getMasterValueMap` / `oneMaster` / `listMaster` (`EntityValueBase.java:1239-1295`;
  `EntityFind.java:267,274`); writing them from a nested Map is the entity-auto `store#<Entity>`
  recursive upsert (`EntityAutoServiceRunner.groovy:245-300, 314-363` — look up by PK → create if
  absent, else `setFields`/update; parent PKs propagate; arbitrary depth; REST `store` = this
  service, `RestApi.groovy:400-402`). A hand-written multi-entity read loop, or raw SQL / a per-table
  INSERT/MERGE / a "flatten then write each table" step to move a graph, is a native-first violation
  → `REDESIGN`. *Failure: order-mirror §6 wrote the order graph via flatten→raw-JDBC MERGE instead of
  a native `store#` of the master map.*
- **N2. The deviation exception must cite a constraint the engine can't meet.** Raw SQL for graph
  movement is a justified deviation ONLY for **bulk cross-datasource streaming** (millions of rows
  between two databases), where per-entity `store#` genuinely can't run. **Per-record / per-graph**
  work (one order) has no such constraint — `store#` is the default. *(Companion to N1: the same
  sim's bulk table-sync MERGE is a justified deviation; the per-order graph write was not.)*

## Round 6 — MDM in the native-first ladder (2026-07-24, harvest)

Source: the order-mirror implementation plan (sim-routing). The plan's `mirror#Orders` service hand-rolled a
Groovy loop over the approved-order list, wrapping each order in `runRequireNew` for per-record isolation —
re-implementing exactly what the Data Manager does natively. Rung 4 already named "DataManager for imports" but
only as a bare noun (no detection cue, unlike the DataFeed cue beside it); it now carries the trigger, and the
`maarg-mdm` skill + `assets/maarg-data-manager.md` carry the full reference (loader per-record call verified
`MaargDataLoaderImpl.java:628-632`).

- **N3. A hand-rolled per-record list loop is MDM done by hand — flag it.** Importing or per-record-syncing a
  LIST of records with per-record transaction isolation and per-record error handling is the Data Manager
  pipeline: a `DataManagerConfig` maps a name to a one-record `importServiceName`, fed a JSON array via
  `upload#DataManagerFile` (`maarg-util/service/co/hotwax/util/UtilityServices.xml:159-236`); the loader calls
  the import service once per record, each in its own transaction (`.requireNewTransaction(true)
  .ignorePreviousError(true)` — `MaargDataLoaderImpl.java:604-648`, the per-record call at `:628-632`), failed
  records collected into an error file, the whole run auditable via `DataManagerLog`. A service that (a)
  loads/queries a list, (b) loops it in Groovy, (c) hand-manages per-item `runRequireNew` and/or per-item error
  capture is a native-first violation → REDESIGN: extract the per-record work into a one-record import service
  and let MDM drive the loop. *Failure: order-mirror `mirror#Orders` looped approved orderIds with a per-order
  `runRequireNew { getMasterValueMap read + store# write }` instead of a one-order `import#SimOrder` service + a
  `DataManagerConfig`.*

## Round 7 — sponsor-approved coaching rules folded (2026-07-24)

Two generic authoring/review rules added to `agents/moqui-architect.md` (Rules
section), sponsor-approved; recorded here generic, without engagement evidence:

- **H11. Revision sweep discipline** (generalizes H7 beyond rulings). When a
  design decision is revised or superseded, the change is not done until every
  artifact that states the old model is rewritten or carries a dated
  supersession note — verified by grepping the superseded vocabulary (old
  entity names, old mechanism phrases, old reason codes) across the whole
  artifact set before handoff. Rationale: a revision applied only to the core
  documents leaves the satellite documents asserting the old design as live
  truth.
- **H12. Reuse citations carry lifecycle state** (promotes self-lint item 7 /
  H9 to a standing rule). Citing an existing service, REST resource, or entity
  as the reuse surface requires checking whether the checkout marks it
  deprecated and naming the successor if so. Rationale: a design that points
  builders at a deprecated surface ships tomorrow's rework.
- **N4. The MDM deviation exception + the error-return contract.** A hand loop is justified only when the body
  is NOT a per-record import — it needs cross-record state, strict ordering between records, or the work isn't
  record-shaped (a single aggregate query, a streaming reduce). Per-record independent import/sync (one order,
  one product) has no such constraint → MDM is the default. And the one-record service MUST **return an error**
  on a bad record (not log-and-succeed) — else the loader captures nothing and the record is lost silently (the
  number-one MDM mistake, `assets/maarg-data-manager.md`).

