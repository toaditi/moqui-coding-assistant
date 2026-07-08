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
