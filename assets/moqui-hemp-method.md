# HEMP — requirements and design discipline for Moqui projects

**HEMP** = Holistic Enterprise Mechanization Process, by **David E. Jones** —
creator of the Moqui Framework, Mantle Business Artifacts, and Apache OFBiz.
This is not a foreign methodology brought in from outside: it is the
requirements-and-design discipline written by the author of this stack. The
same UDM (`Party`, `WorkEffort`, `WorkEffortParty`, `UserAccount`) that HEMP's
appendix models is the UDM your entities extend.

HEMP is the **requirements→design front half** that feeds a build→verify→ship
pipeline. This asset is shared reference for every role in this plugin —
requirements, design, and build all draw on it, each for a different piece.

## The principles (the durable rules)

1. **Requirements vs designs — the top rule.** Requirements = *who / what /
   when* (business activities, system-agnostic). Designs = *how / where*
   (the system). A design masquerading as a requirement is a defect — the
   same "code must read true" standard applied to specs. Keep *why* out of
   both; it goes in a separate business case.
2. **Business process story = the primary requirements artifact.** One
   sentence per business activity: a named actor + an action, in sequence,
   active voice ("record" / "review", not "submit" / "display"). The system
   being built stays unnamed; other systems (the e-commerce platform, the
   ERP, carriers, gateways) are actor systems and are named.
3. **Gap/overlap analysis when extending an existing system** — the normal
   mode for Moqui work, since most Moqui projects extend an existing
   component suite rather than start from a blank slate.
4. **Minimum effective artifact set; artifacts stand alone** — plain
   language, no diagram zoo, understandable without tribal knowledge.

## The HEMP artifact set → this plugin's skills

Every HEMP artifact has a home in this plugin. This table is for every role,
not only the analyst — the architect and builder ground their work in the
same artifacts the analyst produced, using the matching skill:

| HEMP artifact | Purpose | Skill of this plugin |
|---|---|---|
| **Business process story** | requirements: actors + actions in sequence | (produced by the business-analyst agent) |
| Requirement statement / idea to incorporate | rules or crosscutting concerns not fitting the flow | linked from the story |
| Actor definition | who the actors are; a short "day in the life" per actor | linked from the story |
| Business case | *why* / objectives (kept separate from the requirement itself) | its own document |
| **Overlap / gap description** | how the existing system supports an activity vs what must be built | linked from the story — the extend-existing-system mode |
| **Data statement** (subject-verb-object) | bridges requirements to the physical model | `moqui-entity` |
| Data model | the physical entities | `moqui-entity` (entity / view-entity definitions) |
| Screen outline / wireframe / screen flow / menu | UI design | `moqui-screen` / `moqui-navigation` |
| Data mapping | field-to-entity mapping between an external system and this one | its own document, referenced by the design |
| Automated process outline | services / jobs, described before they're coded | `moqui-service` / `moqui-logic` |
| System interface design | connectors and integrations | `moqui-integration` |
| Initial & test data | seed and test fixtures | this plugin's data-loading conventions |

## HEMP roles → this plugin's agents

| HEMP role | In this plugin |
|---|---|
| **Expert User / Sponsor** | the **human** — the source of business truth; agents never invent business activities |
| Business Analyst | `moqui-business-analyst` agent — writes the business process story + verified gap/overlap from the Expert User's input |
| System Architect | `moqui-architect` agent — grounds designs in working-code precedent; every deviation evaluated twice |
| Software Developer | `moqui-builder` agent — one claimed issue, own worktree, never self-certifies |
| UI Designer | no dedicated agent yet — folded into the builder's work using `moqui-screen`; split out into its own agent when a project needs it |
| QA Technician | `moqui-qa-technician` agent — derives tests FROM the story, verifies adversarially, runs non-hollow checks |
| *(Manager / orchestrator)* | not a HEMP role — the host project's own coordinating session (see `moqui-agent-orchestration.md`); not one of this plugin's agents |

## How it feeds the build

```
Expert User (human) ── business activities
      │  business process story (+ actor defs, gap/overlap)
      ▼
   design: screen outline/wireframe, data statement → data model, data mapping, process outline
      │  (moqui-entity / moqui-service / moqui-screen / moqui-integration skills)
      ▼
   build → verify → ship (this plugin's agent-team orchestration, or the host project's own pipeline)
      │  acceptance tests derive FROM the business process story
      ▼
   delivered, with acceptance = the story's activities pass
```

## Primary-source grounding

*Making Apps with Moqui* (Jones, 2014) states HEMP's top rule years before the
HEMP book itself: requirements "distinct and separate from the designs," an
implementation → design → requirement reference chain, and "with
implementation artifacts that naturally map to design artifacts both tasking
and testing are straightforward" (pp. 18-19). Mantle UBPL is described as "a
set of business process stories... that drive the design of business
applications" (p. 165) — story-first requirements are native to the
Moqui/Mantle lineage, not an import. The Mantle Spock process suites are
named per business process (`OrderToCashBasicFlow`, etc., pp. 219-259):
test = process story = HEMP artifact, the same idea in three names.

## Caveats (get these right)

- **The Expert User must stay human.** Agents accelerate documenting,
  designing, building, and verifying — never the *source* of what the
  business actually needs.
- **"System-agnostic" has a nuance for integration work.** An e-commerce
  platform, an ERP, a payment gateway — these are *actor systems* in the
  story and may be named ("Shopify notifies the Company of a new order").
  Only the system *being built or customized* stays unnamed. Getting this
  line right is the skill.
- **Some diagrams are fine** (wireframes, screen flow, state machines) — HEMP
  just doesn't lead with them or let them replace the text they're based on.

## Guardrails (from HEMP ch. 9)

- Don't call a design a requirement. Question an outlandish or expensive
  design where a simpler one meets the same requirement. Don't try to
  predict or build for a future that hasn't been asked for.
- Stick to one agreed, simple artifact set; every artifact must stand alone —
  no interpreter needed.
- If new requirements keep surfacing mid-build, requirements are the
  problem — stop and do a fresh requirements pass + gap/overlap on what's
  built so far.
- On large projects with a short timeline: one initial requirements pass
  over the whole business first, then detailed analysis/design/build per
  part, in parallel. Handle late change by updating the process story — the
  change flows through to design and build from there, not around it.

## The business analyst's artifact templates

These are the **requirements-side** artifacts the business analyst produces
(HEMP ch. 3–4). The design-side artifacts below them in the artifact table —
data statement, data model, screen outline, data mapping, process outline,
system interface — are **not** the analyst's: the architect and UI designer
own those, working from the story the analyst wrote. Keep every artifact
stand-alone: understandable with no author present.

### Business process story (the primary artifact)

```
# <Feature / scope name>
Business case: <link to the objective(s) this serves>
Actors: <names — each defined in the actor list>

## Main flow
<n>. <Actor> <active verb> <object, with the fields recorded or reviewed>.
     — system-under-build stays UNNAMED ("Company automatically notifies the
       Customer"); actor systems are NAMED (Shopify, NetSuite, the carrier,
       the payment gateway). Verbs: record / review / notify / approve /
       receive — never submit / enter / display / click.

   Alternate — <condition>: the distinguishing condition is the FIRST words
   of the paragraph. Keep it next to the branch point. The sentence that
   returns to the main flow names the step it rejoins.

## Time flow (activities triggered by time, not by the flow above)
<nightly / per settlement / month-end> — <Actor> <verb> <object>.
```

On a large scope: write ONE high-level story first, **bold** each high-level
activity, then break each bold sentence into its own linked sub-story whose
title IS that sentence. Detail stops at the fields an actor records/reviews;
heavier field/rule detail goes in a linked supporting doc.

### Idea to incorporate

A crosscutting business rule/objective that **can** be woven into the story.
Record it once in an "Ideas to Incorporate" list so the interview keeps
flowing; later break it into steps and add those steps to **every** activity
it touches. (Book example: address validation added to every activity that
records a postal address.)

### Requirement statement

An idea that **cannot** be woven into a flow — a standing rule or a system
constraint. Keep it as a short standalone statement used alongside the story;
if it applies to one activity, link it from that activity.

### Actor definition

`<Name> — <person / system>; <primary role>; <how it overlaps/differs from
other actors>.` Actor systems (Shopify, NetSuite, carrier) are actors too.
Reviewing actor definitions often leads to **merging or splitting actors** —
when that happens, update every process story so each actor keeps one
consistent name throughout (book, ch. 3).

### User experience story

A "day in the life" of ONE important actor (a customer, a heavy or
complex-role user). Single actor, so the actor need not be named each
sentence; light design hints allowed but minimized. Use it to surface
activities, then fold every activity it reveals back into the business
process story. It is never a design basis.

### Business case

Why / objectives, structured by objective (not by flow), cross-linked to the
story activities each objective drives. **No confidential ROI or budget** —
everyone on the project reads it. Write it first when used, so objectives
shape the story.

### Overlap description (extend-existing-system mode)

The activities it covers, plus step-by-step instructions for how those
activities are **already** done in the system — detailed enough for someone
who has never seen it, citing the service/entity/screen by **stable name**
(not `file:line`, which rots in a durable doc). **Verify against the real
system and validate with the Expert User** — an unverified overlap is the
most expensive requirements bug. Doubles as end-user documentation. *Partial
overlap*: mostly supported — describe the gap only at the point the activity
breaks; leave the rest.

### Gap description

The activities NOT supported, plus an optional sub-list of existing artifacts
(entities, services) worth reusing when designing the gap. *Partial gap*: an
unsupported activity where some data model or logic already exists. Link each
gap from the story. When every activity is marked overlap or gap, the story
becomes the supported-vs-build map that scopes the design.

### Open questions (to the Expert User)

Numbered list of what the story cannot answer yet. Never fill a hole with an
invention — a hole becomes a question. "Q3: when a POS return arrives without
a receipt, who approves the credit?"

## Worked example — a Shopify order, then a return

A compact end-to-end in the templates above (the OMS mode: extend an existing
system). The system-under-build stays unnamed; Shopify / NetSuite / the
carrier are named actor systems. Every overlap cites a real, verified service
or entity in the suite.

**Business case (excerpt).** Objective: capture every channel's orders in one
operational system so fulfillment and finance work from a single record.

**Actors.**
- Customer — buys and returns goods; interacts rarely.
- Shopify (actor system) — the e-commerce platform; captures the order and the
  return request.
- Company — the organization running fulfillment (the system-under-build,
  unnamed).
- Warehouse Worker — picks, packs, ships, receives returns.
- NetSuite (actor system) — the ERP; the financial ledger.
- Carrier (actor system) — moves the parcel.

**Business process story (high-level; bold expands to a sub-story).**

**Company captures the order.** Shopify notifies Company of a new order.
Company records the order: customer, items, quantities, prices, ship-to
address, payment status.

**Company fulfills the order.** Company assigns the order to a warehouse.
Warehouse Worker picks and packs the items. Company notifies the Carrier of
the shipment. Warehouse Worker records the shipment. Company notifies the
Customer.
> Alternate — item out of stock: If the assigned warehouse cannot fill an
> item, Company reassigns the item to a warehouse that has it, or notifies the
> Customer of a backorder. Rejoining "Company fulfills the order", Warehouse
> Worker picks the reassigned items.

**Company records the sale in the ledger.** Company notifies NetSuite of the
shipped order.

**Customer returns an item.** Customer requests a return in Shopify. Shopify
notifies Company of the return request. Company records the requested return:
order, items, reason. Warehouse Worker receives the returned items and records
their condition. Company authorizes the refund and notifies NetSuite. Company
notifies the Customer that the refund is issued.

*Idea to incorporate:* every activity that records a postal address validates
it against the address service — add to the order ship-to and the return
ship-from.

**Gap / overlap.**

| Activity | Overlap / Gap | Evidence (verified name) |
|---|---|---|
| Company records the order | Overlap | shopify-oms-bridge `create#ShopifyOrder` (webhook path `OrdersCreate` → `consume#OrdersCreateWebhookPayloadSystemMessage`); lands `OrderHeader` / `OrderItem` (oms, ofbiz-oms-udm) |
| Company records the requested return | Overlap | shopify-oms-bridge `create#ShopifyInProgressReturn` / `create#ShopifyCompletedReturn`; lands `ReturnHeader` (oms, ofbiz-oms-udm) |
| Company notifies NetSuite of the shipped order | Overlap | mantle-netsuite-connector `generate#NewOrdersSyncFeed` / `generate#FulfilledOrderItemsFeed` |
| <client-specific twist, e.g. a bespoke exchange rule> | Gap | — the design+build focuses here |

**Open questions.**
- Q1: When a returned item arrives with no originating Shopify return request,
  who authorizes the refund, and at what value?

**Handoff.** The architect turns each gap into data statements → data model
(`moqui-entity`) and process / interface designs; QA turns each story activity
into an acceptance scenario (the story IS the test spec).

## Engagement-hardened additions (from a full real engagement)

Practices and three artifact shapes proven in a complete pre-order
requirements engagement (multi-round elicitation, then document, contract,
and defect-history reconciliation). Rule rationale + evidence:
`docs/ba-skill-spec.md`.

**Record-keeping practices (all artifacts):**
- Version every artifact; the story header carries the **sign-off stamp**
  ("SIGNED OFF by the Expert User (name), date — vN") and what changed per
  version.
- Open questions carry a **named owner**; answered ones move to an
  `## Answered` log with the answer, who, and the date — the story history.
- **Escalations quote BOTH conflicting sources verbatim** and are marked
  "escalated, not resolved" until the sponsor rules — or until the record
  itself carries the client decision-owner's ruling: a recorded ruling
  RESOLVES the conflict, with both positions and their history preserved
  (including the origin of any reversed position).
- **Quotes are verbatim to the character**: transcription artifacts keep
  the source's spelling with a [bracketed] gloss; quote marks never wrap
  the analyst's own phrasing — a provenance grep on any quote must land
  in the source.
- What the business explicitly declines is an **explicit non-requirement**
  ("no embargo holds — if that changes it is a new conversation, not a
  hidden feature").
- Gap/overlap headers **pin the component versions** the verdicts were
  checked against; report **every condition** of any cited configuration.
- **Keep the tape**: the Expert User's words (interview record), preserved
  alongside the artifacts — provenance review is impossible without it.
- **Package-currency sweep before delivery**: hand-typed counts, versions,
  and status lines that mirror another artifact are re-derived; the
  entry-point README is re-stamped; a legend covers every value its table
  uses.
- **Numbers are reproducible**: a numeric claim states its tally method and
  source, or it is not stated.
- **Demo-naming lint** (demo-facing artifacts): grep against the naming map —
  no real people or brands; dropped demo names swept everywhere.

**Legacy-evidence record** (when engineering documents are a source):
facts mined (Fn) · contradictions with the Expert User's understanding
(Cn: their belief, the record, the disclosure outcome — requirements
usually stand, reclassified "keep what works" → "build what legacy only
pretended to do") · reliability cautions for the Architect (Bn — defects
not to rebuild) · corrections applied to the other artifacts.

**Contract coverage map** (when a signed contract is a source): promise by
promise — Pn | contract § | verdict COVERED / PARTIAL / MISSING /
CONFLICTS | where it landed (story step / R-rule / Qn). Plus contract
internal contradictions (recommend closing them with the client in
writing), and package requirements the contract never priced — the sponsor
carries those knowingly.

**Defect-history traceability** (when a regression/issue list is a
source): per case — issue link | verdict STORY-COVERED (step/rule) /
IMPLICIT-REQUIREMENT-MISSING (draft the missing sentence) / LEGACY-ONLY
(reason; another client's integrations never enter this client's scope) —
handed to QA so regression cases stay mapped to the story.

**Meeting-record corpus intake** (when the source is a pile of
transcripts): the corpus is interview tape already taken. Chronological,
one file at a time, mined into disk-backed artifacts before the next file;
a per-meeting evidence log carries fact + speaker + weight. Recorder-AI
summaries are hearsay. Vendor speech = capability claims, never client
requirements. A referenced-but-absent document is an owned open item, not
a blocker ("reconciliation pending"). Late-recovered records keep stable
identifiers; headers carry the chronology.

**Reference-store gap/overlap** (when the "existing system" is a
configured demo/reference instance): platform capability alone is never
full overlap. Three tiers — OVERLAP (the store demonstrably exercises the
activity), PARTIAL platform-only, GAP — with a header stating what the
checkout cannot prove (runtime-only state, out-of-repo apps) and pins
recording branch + dirty state, not just versions.
