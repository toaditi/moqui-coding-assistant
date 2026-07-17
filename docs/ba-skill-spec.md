# BA agent — skill spec (living doc)

Source: the HEMP book (D.E. Jones, 2013) + live BA training session (2026-07-10,
Anil as trainee, Claude as tutor/Expert User). **Method: every trainee mistake
becomes an agent rule; every exercise becomes an eval case.** Rules feed
`agents/moqui-business-analyst.md` and `assets/moqui-hemp-method.md`; eval cases
verify the upgraded agent actually holds the skill.

Format per rule: the rule, and (where one exists) the real training failure that
surfaced it.

## A. Story grammar (lintable — the agent self-checks every sentence it writes)

- **A1. Named actor + active verb, every sentence.** Passive voice is a defect.
  *Failure: "sellable inventory is recorded... item is put on the shelf."*
- **A2. Banned phrases:** "the system", "in the system", "should be able to",
  submit / enter / display / see / click / screen / dropdown. Swap for business
  verbs: record / review / notify / approve / receive.
  *Failure: "in the system" recurred three exercises running — a personal tell.*
- **A3. "Company automatically ..."** is the pattern for automatic work. The
  system-under-build is never named; actor systems are always named (Shopify,
  NetSuite, the carrier).
  *Failure: "update the CSR's system data with the remote system" — both
  directions wrong in one sentence.*
- **A4. Enumerate the fields** the actor records or reviews. Stop at fields;
  heavier detail goes to a linked supporting doc.

## B. The knife (requirements vs designs)

- **B1. Extract before you cut.** A design-shaped statement usually *wears* a
  requirement. Cutting the design and losing the requirement inside it is the
  classic trap — always ask: what business need was this design serving?
  *Failure: nightly sync job cut; the keep-refund-status-current requirement
  vanished with it.*
- **B2. Mechanism, frequency, and format words hide requirements.** "Nightly"
  hides a freshness need; "report" hides contents + purpose; "dashboard" hides
  a review activity. Each becomes an open question, never an assumption.
- **B3. The pen-and-paper test.** If the sentence could be satisfied without
  any computer (paper, phone, clipboard), it is requirement-grade wording.
- **B4. "What do you do with it next?"** beats every format/mechanism question.
  The answer is the next activity in the flow — and real constraints (e.g. a
  downstream actor system needing machine-readable data) fall out on their own.

## C. Flow control

- **C1. Alternate flows:** the distinguishing condition is the FIRST words of
  the paragraph; the alternate sits next to its branch point; the sentence that
  returns to the main flow names the step it rejoins.
- **C2. Time-triggered work is systematically lost by flow interviews.** Flow
  memory drops scheduled work — the agent must run an explicit sweep: "what
  happens daily / weekly / at month-end?" Time flow is a separate section.
  *Failure: the Friday accounting review died three times — client ramble,
  first draft, second draft.*
- **C3. Crosscutting rules** get woven into every affected activity (idea to
  incorporate); non-weavable constraints become requirement statements.

## D. Never invent (the hard discipline)

- **D1. Three invention flavors to catch:**
  1. *slang → invented roles* — "the guys" became Receiver + QA Inspector,
     an unverified business fact;
  2. *why → invented activity* — "for the insurance claim" (a rationale)
     became a whole claim-preparing activity;
  3. *musing → fact* — the client's hedged "maybe printouts?... stores only
     have the receipt printer" became "associates print the picklist."
- **D2. Client hedges are not facts.** "Maybe", "I figured", "I don't know",
  "somehow" — each is either an open question or design freedom, never story
  content.
- **D3. "You figure it out" = design freedom to record**, not a hole to fill.
  The story states only the outcome activity ("Company notifies the store of
  new pickup orders"); the mechanism stays the designer's open field.
- **D4. Every unknown → a numbered open question, specific enough that the
  answer slots straight into the story.** "Tell me about X" is interview talk;
  the written artifact asks "When an item is scrapped, does someone file an
  insurance claim? Who, and what do they need?" Plain language — no jargon
  (client may not know "SOP", "BOPIS" is fine if the client used it first).

## E. Elicitation conduct (the interactive loop)

- **E1. One question per turn.** Multi-question turns get selective answers —
  the client answers what's comfortable and the most important question gets
  the thinnest answer. *Failure: a 3-question turn; the "somehow" question got
  "I don't know" while the easy questions got paragraphs.*
- **E2. Read back what the expert SAID; never propose what they didn't say.**
  Leading questions produce worthless yeses that launder inventions into
  "confirmed" facts. *Failure: "find the order by customer name" — the client
  had said "shows their phone"; the leading question got it rubber-stamped.*
- **E3. Chase the vaguest word** in every answer ("...we get the order to the
  store **somehow**..."). The vaguest word is the next question.
- **E4. Emotion marks priority.** "Never again. Ugly one-star review" flags the
  most important requirement in the conversation — capture it as an alternate
  flow + business-case pain, immediately.
- **E5. Park design-talk visibly** ("noted — that goes to the designer"), then
  return to the flow. Parking it out loud keeps the client's trust without
  letting the design into the story.
- **E6. Mine every ramble into the artifact before the next question:** story
  sentences / parked items / open questions. An unmined ramble is lost data.
- **E7. Pin the business goal first** (one line, business case) — it shapes
  every later judgment about scope and priority.

## F. Gap/overlap (book rules; live training pending)

- **F1.** Verify every overlap against the real system before recording it;
  cite service/entity/screen by stable name, not file:line.
- **F2.** Overlap descriptions double as end-user documentation — write them
  step-by-step for someone who has never seen the system.
- **F3.** Partial overlap: describe the gap only where the activity breaks.
  Partial gap: name the reusable existing artifacts.
- **F4.** An existing *manual* process (the phone-hold shelf) is not a system
  overlap — it's an analog to model the story on. Park it as reference.

## G. The artifact review gate (surfaced by the training itself)

The coaching that produced this spec IS the missing pipeline stage: BA
artifacts currently have no reviewer, while code has the architect and claims
have QA. Every rule above doubles as a **review checklist** for auditing any
BA artifact — whoever produced it, agent or human.

- **G1. Provenance audit (the core check).** Every story sentence must trace
  to something the Expert User actually said — or be a numbered open question.
  A sentence with no source utterance is an invention. This is the
  requirements-side mirror of the architect's rule ("every design element
  needs a working-code citation").
- **G1a. Keep the tape.** The BA preserves the Expert User's words — the
  interview record / session notes — alongside the artifacts. Provenance
  review is impossible without the source record. (The book already requires
  capturing corrections verbatim; this extends it to all Expert User input.)
- **G2. Mechanical lint** (section A): passive voice, banned words, unnamed
  actors, missing fields.
- **G3. Completeness sweeps:** time flow present? alternates adjacent to
  branch points? every activity marked overlap/gap (when extending)? every
  hedge converted to a question or design-freedom note?
- **G4. Question quality:** each open question specific enough that the
  answer slots into the story (D4).
- **G5. Overlap verification check:** was each overlap actually verified
  against the real system, with a stable-name citation — including EVERY
  condition of any cited configuration (F5)?
- **G6. The reviewer's expectations are claims too.** A disagreement between
  reviewer and artifact is resolved by reading the source (code, transcript,
  contract) — never by authority. (Evidence: three citation disputes across
  rounds 1–2; the source won all three, twice against the reviewer.)
- **G7. Audit even the client's self-assessment.** "Did I ever bring it up?"
  is a checkable claim — check the record before writing it down.

**Wiring (per house doctrine — no role certifies its own work):**

1. **BA self-check** — the lintable rules (A + G2/G3), run before delivering.
2. **QA Technician adversarial review** — provenance audit (G1), invention
   hunt, UNTESTABLE verdict on vague activities; QA already owns adversarial
   verification, so story artifacts join its remit.
3. **Expert User (human) review** — the book-mandated final gate, on business
   truth only ("is this what we actually do?"). The two gates above run first
   so the human never spends attention on grammar.

## Round 1 — self-play training results (2026-07-10, Pre-Order, real feature)

Trainee: the current `moqui-business-analyst` definition (cold, no docs).
Client: Claude as "Priya," briefed from real Pre-Order docs + legacy code.
Deliverable: `maarg-sd/docs/pre-order-requirements/` (7 artifacts, real).

**Confirmed on the agent (rules hold as written):**
- E1 — it fired an 8-question volley in exchange 2 (client answered
  selectively; one thread went silent). The loop text alone doesn't prevent
  this → promote to a hard rule in the agent's Rules section.
- C2 — it closed the interview with NO time-flow sweep; the daily morning
  report only surfaced because the client volunteered it at sign-off.
- G1a — it kept no interview log. Provenance review ran only because the
  reviewer kept a client-side tape.

**New rules surfaced by round 1:**
- **E8. Pre-sign-off sweep.** Before requesting sign-off, run an explicit
  checklist: time-triggered work ("what happens daily / weekly / month-end?
  what reports does the business run on?"), every actor defined, every
  routed-away thread resolved or listed, every hedge converted.
- **E9. Read-back extensions are labeled as proposals.** An inference the
  Expert User never said is read back as a QUESTION ("I assume you want the
  same treatment here — correct?"), never as a recorded fact. (The trainee
  recorded one; the read-back caught it — the label removes the luck.)
- **G6. The reviewer's answer key is also a claim.** Round 1: the reviewer's
  key was wrong twice (missed order-routing's parking-release rule; credited
  draft job-registry entries as capability) and the trainee's citations won.
  A disagreement between reviewer and artifact is resolved by reading the
  code, never by reviewer authority.

**Positive patterns to encode (the trainee invented these; keep them):**
- Component pins recorded in the gap/overlap header (doc-drift discipline —
  a verdict is stamped against specific versions).
- "Answered questions" section with dates — the story history artifact.
- Ideas-to-incorporate entries that document their own provenance
  ("proposed by the analyst, explicitly confirmed by the Expert User").
- Defects found in the existing system during overlap verification (drifted
  descriptions, dangling configs) go into "notes for the Architect" — the BA
  reports them, never fixes them.
- Undefined scope gets a section that says exactly that ("No activities are
  written here until that session happens") — visible non-invention.
- Design-candidates table maps every parked design to the requirement it
  serves.

## Round 2 — document-input training results (2026-07-10, same engagement)

Input: two sponsor-supplied legacy engineering documents handed to the BA
mid-engagement (after sign-off), with no hint of contents. Tested: mining
documents vs interviews, reconciling records against Expert User beliefs,
late-change flow, and the review gate on its own output.

**Demonstrated (encode as positive patterns):**
- **Belief-vs-record disclosure.** Two engineering records contradicted what
  the Expert User believes her system does (the page date never rolled; no
  real sell-out cap). Correct move, executed: disclose the discrepancy to
  the Expert User plainly, requirements unchanged, reclassified from
  "keep what works" to "build what legacy only pretended to do."
- **The legacy-evidence artifact** — document sources get their own
  provenance record: facts mined / contradictions / reliability cautions
  (routed to the Architect, never smuggled in as requirements) /
  corrections-applied log. This is G1a for document input.
- **Explicit non-requirement.** The Expert User declined speculative
  flexibility (embargo holds) — recorded as a non-requirement with "a new
  conversation, not a hidden feature." YAGNI made visible.
- **Correction protocol.** On a review finding against its own claim: fix
  the artifacts FIRST, then disclose to the Expert User, take the blame
  plainly, and convert the correction into a handoff safeguard (the
  no-date-filter instruction to the architects).
- **Unchosen behavior ≠ requirement.** Found an undocumented legacy behavior
  (release waits for the promise date) and asked whether it was deliberate
  before carrying it — "maybe it's just how it was built and nobody chose
  it."
- **Migration-regression framing:** a legacy behavior missing in the new
  suite (cancellation ATP give-back) flagged as "without a build, migration
  would regress it."

**New rules from round-2 failures:**
- **B5. Every hard-stop rule needs a leak policy.** A "never X" requirement
  is an intent, not a guarantee — enforcement always has a race window. For
  every such rule ask: "when it leaks anyway, what happens, how fast, who is
  told?" (Failure: R1 written as absolute; the overflow flow was missing
  until the review gate forced the question — despite the agent's own
  evidence showing the leak was the client's worst incident.)
- **F5. Report every condition in a cited configuration.** (Failure: cited a
  routing config's parking filter as proof of release-on-stock while the
  same block carried a `promiseDaysCutoff` date gate two lines below —
  a partial read of its own citation, announced to the client as good news.)
- **E1 enforcement note:** the volley stopped in round 2 only after the
  dispatch made "one topic at a time" explicit → the rule must live in the
  agent definition as a hard rule, not only in the loop description.

**G6 evidence, now symmetric:** round 1 — reviewer's key wrong twice,
producer right; round 2 — producer wrong once, reviewer right. Three
citation disputes, all resolved by reading the code. Neither seat is
trustworthy alone; the disagreement protocol is the gate.

## Round 3 — real-client interview training (2026-07-11, real client engagement)

Trainee: the UPGRADED agent definition (post fold-in). Client: Claude as
the client's founder, RECORD-BOUND (real client; answers only from 7
recorded meetings + contract + rulings; unrecorded decisions defer and stay
open). Sources feeding the persona: meeting-notes summaries + one full
transcript. Fixture: `maarg-sd/docs/ba-training/` (tape + client briefing —
kept in the private workspace; client identity never enters this repo).

**Validated (the upgraded agent held every prior rule):** E1 one topic/turn
across 7 topics; read-back every turn; escalation line held under direct
client pressure ("when do I get the phase answer?" → factual state, no
promise, urgency quoted to sponsor); deferrals stayed open (Q29 accounting;
Q32 region-face; Q34 widths; Q35 audit; Q36 ledger mechanics); musing ≠
decision (demand-decides-split parked labeled); current-state ≠ target
(manual split recorded as temporary workaround).

**New rules from round 3:**
- **E10. Weight every recorded item: FIRM / LEAN / THEORY / HOMEWORK.** A
  technical client thinks aloud; the record must carry his labels ("write
  that as my lean and confirm it when there's actual checkout copy"). A
  lean gets an open confirmation item, never a rule. A working theory gets
  a pressure-test owner, never adoption.
- **E11. Client confidentiality across engagements.** Never quote one
  client's configuration or behavior to another ("brand X always
  split-ships"). Elicit this client's grain without disclosing that
  client's. (Failure: the trainee cited another brand's default to the
  client in interview.)
- **B6. Undefined words in signed documents: define it or delete it.** An
  undefined term in a signed contract is unpriced scope waiting to happen.
  Establish who authored the word (vendor vocabulary is not a client
  requirement), whether it is on the launch bar, and route it to the
  written clarification list with a define-or-delete disposition.
- **B7. Elicit the minimum launchable bar.** When scope phasing is
  disputed, convert the dispute into the client's concrete acceptance
  criteria ("at go-live, which of these must be true?") so the sponsor's
  ruling lands against a real bar, not a vibe.
- **G7. Audit even the client's self-assessment.** "Did I ever bring it
  up?" is a checkable claim — check it before writing it down (the trainee
  verified zero waitlist mentions across seven meetings before recording
  the disowning).
- **D5 (extends D-family). Meeting-AI summaries are hearsay.** A summary
  line is never load-bearing provenance — pull the transcript for any claim
  that changes scope, money, or phase. (Round-2 meeting-mining finding — incident record now in the tape:
  the summary inverted the client's "manual V1" meaning; the transcript
  reversed the escalation.)

**Pattern worth keeping:** requirement↔limitation wiring — when a client
states a requirement that contradicts a platform limitation already found
in gap/overlap, bind them explicitly ("your words are now the requirement
it contradicts") so the build item carries both sides.

## Round 5 — record-bound corpus engagement (2026-07-11, real-prospect-as-ICP, real client)

Trainee: the current agent definition. No live client: the record was a
15-then-18-transcript meeting corpus (a REAL prospect + its consultants)
plus two sponsor-supplied documents (a vendor proposal, a consolidated
fit-gap brief). Deliverable (real, two-outputs): the ICP business process
story → gap/overlap against a DEMO/reference store → a signal-cited
backlog. Fixture: EC5 (the agency repo's private `fixtures/ba/` — client
identity never enters this public repo).

**Validated (prior fold-ins held in a new domain):** E1 across four rounds
(one question per return, every time); G1a tape discipline; C2/E8 time
flow present unprompted; weighted recording (95 FIRM / 11 LEAN / 13
THEORY+HOMEWORK on round 1); E10 labels; fix-first correction protocol;
D-family under a reviewer trap (coach flagged a proposal detail as
suspected boilerplate; the agent VERIFIED it in the record — client
speech — instead of absorbing or reflex-rejecting).

**New rules from round 5:**
- **G1b. Quotes are verbatim to the character.** Transcription artifacts
  are preserved with a [bracketed] gloss ("start sinking [syncing] the
  warehouse inventory"), never silently corrected — a provenance grep on
  quoted text must always land in the source. Quote marks mean
  source-verbatim only; editorial phrases are never quoted.
  *Failure: the agent normalized "sinking"→"syncing" inside quote marks;
  the reviewer's provenance grep missed; the agent's own audit then found
  104 non-verbatim quotes and 16 editorial phrases wearing quote marks.*
- **D6. A referenced-but-absent document is an open item, not a blocker.**
  When the record cites a document the corpus does not contain, name it,
  route it to the sponsor with an owner, mark dependent artifacts
  "reconciliation pending", and proceed. Verifying what you have does not
  wait on what you don't.
  *Failure: the agent declared gap/overlap blocked until the client's
  master gap list was obtained; coach overruled.*
- **D7. Vendor speech is capability claims.** In a client meeting record,
  the vendor's statements ("we support X", "we'll ship that next month")
  are capability claims and roadmap promises — gap/overlap and
  design-candidate input, never client requirements, never story content.
  A vendor's recollection of a client statement is VENDOR RECALL until
  the client's own words confirm it.
- **G1c. Corpus intake.** A transcript corpus is interview tape already
  taken: process chronologically, ONE file at a time, mining into
  disk-backed artifacts before opening the next (an unmined transcript is
  lost data); keep a per-meeting evidence log (speaker + weight per fact).
  Recorder-AI summaries are hearsay (D5) — load-bearing claims come only
  from the verbatim text. When late records are recovered, identifiers
  stay stable (renumbering breaks every cross-reference); headers carry
  the chronology.
- **F8. Reference-store gap/overlap.** When the "existing system" is a
  configured instance (a demo or reference store), platform capability
  alone is never full overlap. Three tiers: OVERLAP (the store
  demonstrably exercises the activity — data/config/wiring evidence),
  PARTIAL platform-only (capability verified; the store carries nothing
  exercising it), GAP (neither). State once, in the header, what the
  checkout cannot prove (runtime-only state, out-of-repo apps).

**Refinement (a G6 event — the reviewer's key corrected):** escalation is
for conflicts the record leaves OPEN. A conflict with a recorded ruling by
the client's decision-owner is RESOLVED: quote the ruling, preserve both
positions and the history, carry the ruling as the firm position. *The
coach's key held "must stay escalated"; the agent marked it resolved by
the client's recorded end-of-record ruling; the transcript supported the
agent. Program G6 tally: keys wrong 3, producer wrong 1 — the
read-the-source protocol remains the only trustworthy gate.*

**Patterns worth keeping (agent inventions, round 5):**
- Scripted quote-verbatim audit (whitespace-folded, gloss-stripped,
  character-exact), logged as a handoff safeguard any reviewer can re-run.
- Pin tables record branch + dirty-file state per component, method
  stated — not just versions.
- Scripted self-count of summary figures; hand-count corrected in the
  open (62→102) — non-hollow counting applied to one's own artifacts.
- Backlog items carry their own honesty flags ("platform verification
  pending") instead of overclaiming.
- "Not on this backlog" section: N/A rows, declined scope, and
  architect-owned defects, one line each — visible non-invention at plan
  level.
- Decision-gated planning: a structural unknown rides the backlog top as
  DESIGN DECISION REQUIRED; work items are flagged decision-invariant vs
  blocked-on-decision, so planning stays actionable while the sponsor
  decides.
- Arc-origin history: when a late position reverses an early one, the
  story's scope history records the ORIGIN too — an endpoint without its
  origin misreads the client.

## Round 6 — three-engagement audit (2026-07-17, coach audit round 2)

Source: adversarial audit of the Pre-Order requirements package (PR #301 state) and the
notnaked-ICP package, every finding verified in the source. The strengths held (weighted
recording exemplary; Q31 escalation held under client pressure; transcript-over-summary
verification; explicit non-requirements; 12+ gap/overlap citations re-verified in the pinned
tree). The failures cluster in PACKAGE MAINTENANCE and the DEMO-NAMING seam:

- **G8. Package-currency sweep.** Before any delivery, re-derive every hand-typed count, version,
  and status line that mirrors another artifact; re-stamp the entry-point README; a table legend
  covers every verdict value its rows use; a contract-silent FIRM rule added late triggers a
  coverage-map re-stamp (the unpriced-scope list is live, not write-once). *Failures: README stuck
  at "story v12 / R1–R16" while the package stood at v18 / R1–R19; the story's v18 header said "NO
  escalations remain open" while Q31 was open in three sibling artifacts; the coverage map used a
  RESOLVED verdict its legend never defines; R17–R19 (contract-silent, client-FIRM) never entered
  the unpriced list; the mandate's 13/5/5/1 coverage tally is irreproducible from the 22-row map
  (real tally 12/4/4 + 2 RESOLVED); the clarification list had three different lengths across
  three artifacts.*
- **G2 (extended). The story lint runs on EVERY story document** — admin and supplemental stories
  included — and every acting subject must be a defined actor. *Failures: "The system" as acting
  subject in the five tool-requirements stories; "enters" in the admin story; "the business" acting
  in the main story without an actor definition.*
- **B8. Requirement statements pass the same knife as stories.** An R-rule that names entities,
  ledger mechanics, presentation formats, or refresh mechanisms is a design wearing a requirement
  costume — extract the need, park the mechanism. *Failure: the board/trace/actions requirement
  series fused entity names and refresh mechanics into requirement text.*
- **G11. A readiness verdict discloses the sign-off state of every gate input.** "READY" resting on
  an unsigned story without saying so is an over-claim. *Failure: readiness-admin stamped READY
  with gate (a) met by a story that was never signed off.*
- **G12. Legacy-behavior claims cite their evidence file.** A "the legacy does X" statement
  traceable to no evidence document is an invention until sourced. *Failure: "the legacy references
  PRE_ORDER_DATE/BACKORDER_DATE" appears in the sync spec and dev notes; no evidence file carries
  it.*
- **G9. Every numeric claim carries its reproducible tally** — the method and source stated, or
  the number is not stated. (The record-mining rule "every count carries its exact query,"
  generalized to all artifacts.) *Failure: the notnaked backlog's repetition counts claim a
  re-tally "in the evidence record" that exists nowhere.*
- **D8. Demo-naming lint.** Demo-facing artifacts are grep-audited against the naming map before
  delivery: no real people or brands, dropped demo names swept everywhere (glosses included), and
  the sweep re-runs when the map changes. *Failures: Bloomingdale's (the client's real concession
  partner) in the demo-facing story; the real vendor-side first name "Aditya" in demo artifacts;
  three dropped demo brands surviving in actors/business-case/backlog after the naming ruling.*
- **G10. Rule-retrofit sweep.** A rule earned mid-engagement triggers a re-audit of the SAME
  engagement's already-produced artifacts before close. *Failure: D7 (vendor speech is capability
  claims) was earned in round 5, yet a vendor-recommended warehouse-only constraint survived in
  that engagement's own story as requirement content, cited to a client evidence entry that does
  not contain it.*
- **B1a. The extracted requirement is the ACTIVITY, not only its quality constraint.** When
  parking a mechanism ("an hourly sync job pulling X"), the surviving requirement includes the
  business activity itself ("Company automatically records X from Shopify") — plus the freshness
  question. Extracting only a freshness constraint and demoting the recording activity to design
  freedom loses the requirement inside the design. *Live exam failure (EC1v, 2026-07-17): R3
  captured freshness; the auto-record activity itself was handed to the designer as an open
  mechanism choice.*
- **D9. A rationale-implied activity stays OUT of the flow until confirmed.** The owned open
  question alone carries it; writing it into the story with an "[implied activity]" label is
  still an invention — honest hedging does not make a rationale a process step. *Live exam
  failure (EC2v, 2026-07-17): "that's for the warranty claim" produced a claim-filing step in
  the alternate flow, hedged but present.*
- **G1a (extended). The quote chain is per-entry:** every quoted string greps into the SPECIFIC
  evidence entry it cites, not merely somewhere in the corpus; run the scripted quote audit per
  artifact. *Failure: a story quote cited F1.3; the F1.3 entry does not contain it.*

## Eval cases (replay these on the upgraded agent)

| # | Input | Expected | Traps it must avoid |
|---|---|---|---|
| EC1 | "OMS needs a returns dashboard where the CSR can click a return and see its Shopify refund status. Also a nightly sync job... so the dashboard stays current." | 2 requirements (CSR reviews return incl. refund status; Company automatically records refund status from Shopify), 2 parked designs (dashboard, sync job), why → business case, freshness → open question | losing the sync-requirement when cutting the design; keeping "nightly" as fact |
| EC2 | Warehouse-return ramble ("the guys check it... scrap it... every Friday accounting wants a report... photographed for insurance") | main flow + damaged-alternate + time flow; photo rule woven in; scrap activity kept; Qs for actor roles, claim process, report contents/purpose | passive voice; dropping the Friday review; inventing roles; why→activity |
| EC3 | BOPIS interview (multi-turn role-play vs an Expert User) | parks "one screen"; chases "somehow"; reads back, no leading questions; catches the "Never again" alternate; records notify-the-store as design freedom | inventing the picklist from a hedged musing; "by customer name" vs "shows their phone" |
| EC4 | Pre-Order full engagement (cold agent; briefed role-play client; real Maarg suite for gap/overlap) — fixtures (interview tape + client briefing) are INTERNAL, kept outside this public repo in the agency repo's `fixtures/ba/` (placement ruling 2026-07-17) | full artifact set incl. time flow + owner-named questions; parks all design leaks; routes thresholds to sponsor; late-scope additions flow into story; gap/overlap citations verify against the suite; sponsor-bucket threads all land | 8-question volley (E1); missing time-flow sweep (E8); no interview log (G1a); extension recorded as fact (E9); citing draft job-registry entries as capability |
| EC5 | Record-bound corpus engagement (18 real-client transcripts + 2 documents → ICP story → reference-store gap/overlap → signal-cited backlog) — fixture (engagement briefing + four-round tape) is INTERNAL, in the agency repo's `fixtures/ba/` (placement ruling 2026-07-17) | per-sentence provenance to file+speaker; time flow; weighted recording; escalations vs recorded rulings handled per the round-5 refinement; F8 three-tier verdicts with pins; decision-gated backlog; documents reconciled with document-evidence record | silent quote normalization (G1b); blocking on an absent referenced document (D6); vendor claims entering the story (D7); AI-summary provenance (D5); averaging a scope arc instead of carrying the final ruling with history |

## Status

- **Trained live (human trainee, Anil):** the knife (B), story grammar (A),
  flow control (C), invention discipline (D), elicitation (E — BOPIS exercise
  paused mid-way).
- **Trained via self-play (agent trainee, rounds 1–2, Pre-Order):** full
  engagement — elicitation, all artifacts incl. business case + actor
  definitions, gap/overlap against the real suite (F), document input,
  belief-vs-record, late change, the review gate (G) end-to-end.
- **Trained via record-bound corpus engagement (round 5, real-prospect-as-ICP):**
  meeting-corpus intake at scale (G1c), document reconciliation against a
  live record (vendor proposal + fit-gap brief), reference-store
  gap/overlap (F8), decision-gated backlog planning, quote-verbatim
  provenance (G1b) — sponsor-approved and folded in 2026-07-11.
- **Still untrained:** user experience story as a distinct artifact, the
  churn signal in anger, board-mode (Requirements-issue) operation.
- **Next:** replay EC1–EC5 on any future definition change; a fixture that
  fails blocks the fold-in.
