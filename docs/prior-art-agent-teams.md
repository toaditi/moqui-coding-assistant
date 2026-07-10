# Prior Art — Verified Sources

**What this file is:** the list of earlier work our agent-team idea builds on.
Every source below was checked against the live page on 2026-07-06 by an
independent verification agent. Verdicts: **CONFIRMED** = the source says what
we claim. **DRIFTED** = the source is real, but our claim overstated it (the
corrected claim is given).

**Why it exists:** our rule is to build on prior work, not re-invent. The essay
(`docs/the-supervision-bottleneck.md`) must only cite what this table supports.

---

## 1. Agent teams with roles (planner / builder / reviewer / tester)

| Source | What it says | Verdict |
|---|---|---|
| He, Treude, Lo — [arXiv 2404.04834](https://arxiv.org/abs/2404.04834) (2024, v4 2025) | Systematic review of **71 studies** on LLM multi-agent systems for software engineering (search cutoff Nov 2024). | CONFIRMED |
| Cai et al. — [arXiv 2511.08475](https://arxiv.org/abs/2511.08475) (Nov 2025) | Studied 94 systems. Role-based cooperation is the most common design pattern: **46.8%**. Human-in-the-loop reflection appears in only **5.3%**. | CONFIRMED |
| MAAD — [arXiv 2606.01385](https://arxiv.org/abs/2606.01385) (May 2026) | Four role agents (Analyst, Modeler, Designer, Evaluator) turn requirements into architecture. Benchmarked against MetaGPT. | CONFIRMED |

**What this means for us:** role-based agent teams are the most common pattern in
the field — not our invention. But almost nobody (5.3%) designs the human seat
and the checking gates. That gap is where our work sits.

## 2. Shared-board coordination (blackboard / stigmergy) on LLM agents

*Blackboard = agents coordinate by reading and writing one shared surface, not
by talking to each other. Stigmergy = the same idea; ants coordinate this way.*

| Source | What it says | Verdict |
|---|---|---|
| Han & Zhang — [arXiv 2507.01701](https://arxiv.org/abs/2507.01701) (Jul 2025) | Applies the classical blackboard pattern to LLM multi-agent systems. | CONFIRMED |
| CodeCRDT — [arXiv 2510.18893](https://arxiv.org/abs/2510.18893) (Oct 2025) | Agents coordinate by watching a shared state, not by messages. For code generation. | CONFIRMED (the detail "explicitly names blackboard" is unchecked — full text not read) |
| PatchBoard — [arXiv 2605.29313](https://arxiv.org/abs/2605.29313) (May 2026) | Agents write validated JSON changes to a shared state; a **deterministic kernel** (a rule-based checker, no AI opinion) validates every change. Results: 84.6% task success vs 30.8% (LangGraph), at ~1/8 the tokens. | CONFIRMED |

**What this means for us:** "blackboard for LLM agents" is already published,
including the deterministic-checker-over-the-board idea (PatchBoard). Our essay
must NOT claim we operationalized this first. Our narrower, true claim: we ran
it on an **unmodified real GitHub board, in a live legacy codebase**.

## 3. The supervision bottleneck is a known problem

| Source | What it says | Verdict |
|---|---|---|
| Navneet & Chandra — [arXiv 2508.11824](https://arxiv.org/abs/2508.11824) (Aug 2025) | Catalogs failure modes of autonomous AI coding pipelines. Argues oversight must be **redesigned, not just added**, as autonomy grows. | CONFIRMED |
| Dam et al. — [arXiv 2512.02329](https://arxiv.org/abs/2512.02329) (Dec 2025) | Proposes agents that follow **norms** (formal commitments, obligations, prohibitions between agents) for human-AI software teams. BDI reasoning + deontic norms. | **DRIFTED** — the paper does NOT mention Contract Net, blackboard, or an "oversight bottleneck." Cite it only as the competing design: agents constrain themselves by norms, where we constrain them by external gates. |

## 4. Gates beat instructions (convention compliance for AI code)

| Source | What it says | Verdict |
|---|---|---|
| [Architecture Fitness Function pattern](https://aipatternbook.com/architecture-fitness-function) | Architecture rules written as automated tests. Key quote: an agent "responds to automated signals more reliably than to documentation" — a build failure gets fixed; a rule in an instruction file gets lost. | CONFIRMED |
| [Operationalizing ADRs](https://platformtoolsmith.com/blog/operationalizing-adrs-fitness-functions/) | An agent checks PR diffs against recorded architecture decisions in CI. Real catch: a forbidden Datadog integration, 6 months after the team standardized on OpenSearch. Also documents that LLM reviewers **rationalize violations away** ("probably fine") unless told to report without judging. | CONFIRMED |
| Blyth et al. — [arXiv 2508.14419](https://arxiv.org/abs/2508.14419) (Aug 2025) | Static-analysis feedback loop with GPT-4o: security issues >40%→13%, readability >80%→11% in 10 iterations (best-case figures). Also honest limits: static tools miss real defects and raise false positives. | CONFIRMED (cite the numbers as best-case) |

**What this means for us:** "mechanical truth outranks model opinion" has
published support — including the exact failure our architect showed in #196
(a reviewer rationalizing a violation). Our essay should cite this as a known
failure mode, not present it as a discovery.

## 5. Low-code platforms: the closest product precedent

*Low-code = platforms where a business expert builds apps through models and
visual tools instead of writing code. Moqui itself is model-driven (XML
entities, services, screens) — so this lineage is directly ours.*

| Vendor | What they ship | Verdict |
|---|---|---|
| [Mendix](https://www.mendix.com/blog/mendix-release-11-12/) (11.12, Jun 2026) | "Maia" agentic AI builds **into visual models, not raw code**, using the org's "architecture, guidelines, standards, and approved components." Governance rules defined once, applied to every app. Human approval steps. | CONFIRMED |
| [OutSystems Mentor](https://www.outsystems.com/low-code-platform/mentor-ai-app-generation) | Orchestrates 10+ agents to produce "fully compliant" apps from natural language or requirement docs. Built-in governance; human sign-off on plans. | CONFIRMED |
| [Appian Agent Studio](https://appian.com/products/platform/artificial-intelligence) | Agents run inside governed business processes; permissions, audit logs, policy constraints, escalation paths. | CONFIRMED |

**What this means for us:** "domain expert directs, platform enforces compliant
output" is now a shipping product category. We are doing to Moqui what Mendix
does to Mendix. This is the strongest lineage for the BA-delivers-a-feature
goal — and the essay currently does not mention it at all.

---

# Part 2 — Coverage holes filled (Phase 2, 2026-07-06)

Four targeted searches. Findings below include "searched, not found" results —
those are evidence for what is genuinely ours.

## 6. The big agent products: who is the human?

| Source | What it says | Maps to us |
|---|---|---|
| SWE-agent — [arXiv 2405.15793](https://arxiv.org/abs/2405.15793) (2024) | Single agent, no roles. Verification = the agent runs tests itself. Says nothing about who reviews. | No human-seat design at all. |
| AutoGen — [arXiv 2308.08155](https://arxiv.org/abs/2308.08155) (2023) | Human involvement is a dial: `ALWAYS` / `TERMINATE` / `NEVER`. Own guideline: start with a human always in the loop. The "gate" is code execution + a Safeguard agent. | `NEVER` mode removes the human but puts nothing in its place. We are "NEVER mode + gates instead." |
| Devin — [2025 performance review](https://cognition.com/blog/devin-annual-performance-review-2025) (Nov 2025) | "Human review is still necessary, because code quality is not straightforwardly verifiable." Devin = a junior engineer; "Engineers... have to learn how to 'manage' Devin." | Their human is explicitly an engineer. Ours is a BA — direct contradiction of their assumption. |
| Cognition — ["Don't Build Multi-Agents"](https://cognition.com/blog/dont-build-multi-agents) (Jun 2025) | Parallel subagents make conflicting decisions; prefer one agent with full context. 2026 revision (Yan): multi-agent works "when writes stay single-threaded and the additional agents contribute intelligence rather than actions." | The strongest counter-position. Our answer: the board serializes writes (one issue = one worktree); reviewers are read-only. That matches Yan's 2026 revision. Must be engaged in the essay. |
| GitHub Copilot coding agent — [docs](https://docs.github.com/copilot/concepts/agents/coding-agent/about-coding-agent) (2025) | Hard human gate: the agent "cannot approve or merge PRs. It always produces a PR for human review." Requester cannot self-approve. | The opposite bet: human review is mandatory by design. |
| OpenAI Codex — [best practices](https://developers.openai.com/codex/learn/best-practices) | "At OpenAI, Codex reviews 100% of PRs" (agent reviews agent). But a developer still merges. | Closest to our architect gate — with a developer kept as final approver. |
| Claude Code — [agent teams docs](https://code.claude.com/docs/en/agent-teams) | Ships lead+teammates, task claiming with file locks, hook-based quality gates, plan approval by the lead. No built-in deterministic test gate. | The mechanisms exist as a toolkit; the gate design is left to the user. |
| LangGraph / CrewAI docs | Human-in-the-loop is role-agnostic: "a human" approves tool calls. Never says who the human must be. | The human seat is simply undesigned — consistent with the 5.3% survey figure. |

Late additions from the follow-up sweeps (all verbatim-verified):

- **MetaGPT / ChatDev deep-read** (MetaGPT arXiv 2308.00352, Aug 2023; ChatDev
  arXiv 2307.07924, Jul 2023): the human is a one-line-prompt customer. MetaGPT's
  "boss" appears once, undefined, inside a sample generated document. ChatDev's default
  Reviewer is an AI agent; a human may optionally take that seat. Neither paper says
  anything about the human's skill level. Our BA-as-analyst design is an inversion:
  their analyst is an agent and the human is a customer; our analyst IS the human.
- **Product survey (Aider, Copilot Workspace, Devin, Jules, Amazon Q, Codex):** all
  explicitly or implicitly assume a **developer** reviews the diffs. Copilot Workspace
  says it outright: "ask your team members for human code review."
- **Replit Agent / Lovable:** the nearest thing to a non-programmer supervisor —
  "No coding experience needed"; the agent self-tests via a browser. But no engineered
  verification framework and no statement of who holds review responsibility. This is
  supervision by vibes, not by gates.
- **Claude Code best-practices docs** use our exact term: a Stop hook "as a
  deterministic gate," and note instructions are "advisory" while "hooks are
  deterministic." The vocabulary is converging on the same idea — as a per-session
  developer tool, not a team pipeline.

**Key negative finding (searched, not found):** no framework or product publishes
a design where a **non-programmer** is the accountable supervisor of a coding-agent
pipeline, with engineered verification replacing code review. The field splits
into: (a) a developer reviews every diff (Devin, Copilot, Codex, Jules, Amazon Q),
or (b) no real review at all (Replit/Lovable "vibe coding", MetaGPT — where the
analyst is an *agent* and the human is just a customer). The middle position is
unoccupied.

## 7. LLM agents on model-driven / DSL frameworks (the Moqui angle)

| Source | What it says | Maps to us |
|---|---|---|
| ABAP benchmark — [arXiv 2601.15188](https://arxiv.org/html/2601.15188v1) (2026) | GPT-5 / Claude get only **19–24% first-try success** on ABAP (closed, low-resource enterprise language). With 5 rounds of compiler feedback: **77%**. | Best comparator found. Proves niche framework code needs a verify-and-repair loop — exactly our lint + moqui-verification pattern. |
| DSL survey — [arXiv 2410.03981](https://arxiv.org/abs/2410.03981) (ACM TOSEM 2025) | 111 papers: DSLs are **harder** for LLMs, mainly from training-data scarcity. No standard benchmark exists. | Validates our Moqui skills/context investment as necessary, not optional. |
| Salesforce CodeGen/Einstein — [vendor blog](https://developer.salesforce.com/blogs/2023/11/inside-codegen-our-in-house-open-source-llm) (2023) | Fine-tuned a model for Apex + grounding in org metadata. | Industry answer = fine-tuning. Ours = skills + gates. Both unpublished as research. |
| LLM4MDE workshop (STAF 2024) | The academic LLM+model-driven-engineering field is early and thin. | The lineage exists but is young. |
| Constrained decoding — XGrammar, SynCode | Mature tech forces output to match a JSON schema, "100% adherence by construction." Almost never applied to XSD/XML. | Open opportunity: Moqui's XSDs as a hard generation gate. Nobody has done it. |
| **Moqui/OFBiz + LLM research** | **Searched, not found.** Only HotWax's own blog and one practitioner repo (`moqui-agent-os`). Zero papers. | If we publish, we are first. |

## 8. Framework-idiom compliance ("use the framework's way")

| Source | What it says | Maps to us |
|---|---|---|
| API-misuse literature (GPTAid, Dr.Fix, 2025–26) | "Misuse" always means a bug or security flaw — wrong parameter, hallucinated API. | **Nobody treats "hand-rolled code where a native mechanism exists" as its own defect class.** Our reads-true/native-first gate fills a real gap. |
| ["LLMs reinvent instead of reuse"](https://arxiv.org/abs/2409.20550) (2024) | "LLMs often invent... non-existent APIs or produce variants of already existing code." | Our core failure-mode claim, published, citable. |
| [CodeRabbit ast-grep linter](https://coderabbit.ai/blog/ai-native-universal-linter-ast-grep-llm) (2024) | One example: flags raw SQL, suggests the ORM. | The single closest hit — one example, not a maintained idiom ruleset. |
| Semgrep custom rules; [Thoughtbot RuboCop hook](https://thoughtbot.com/blog/enforcing-your-ruby-style-guide-on-ai-generated-code); [Factory.ai lint-directs-agents](https://factory.ai/news/using-linters-to-direct-agents) (2025) | The *mechanism* (convention → executable check → gate the agent) is an active trend. | Mechanism precedented; a **named, maintained framework-idiom ruleset is not**. Our Moqui pattern catalog + lint appears original. |
| De-Hallucinator — [arXiv 2401.01701](https://arxiv.org/html/2401.01701v3) (2024) | Feeding API context INTO generation gives 23–61% API-recall gains. | Honest counterpoint: the field invests in the *generate* side; we bet on the *verify* side. The essay should say we do both (skills in, gates out). |

## 9. Hollow-green tests and the count oracle

| Source | What it says | Maps to us |
|---|---|---|
| "All Smoke, No Alarm" — [arXiv 2606.18168](https://arxiv.org/html/2606.18168v1) (Jun 2026) | **80.2% of agent-written test patches have weak or no real assertions** (Codex, Copilot, Devin, Cursor, Claude Code). Coins "test theater." Warns: test-presence gates overestimate quality. | Our hollow-green incident is a measured, industry-wide phenomenon. |
| Rotten Green Tests — Delplanque et al., [ICSE 2019](https://dl.acm.org/doi/abs/10.1109/ICSE.2019.00062) | Tests that pass without executing their assertions; found 294 in 19,905 real tests. | The academic root of "green but checks nothing." |
| Test-smell catalogs ("Missing Assertions") | Assertion-free tests are a long-catalogued smell. | Precedented vocabulary. |
| Berkeley RDI benchmark exploits (2026); reward-hacking benchmarks | Agents actively fake green: pytest hooks forcing "passed", patched test runners. No maintainer used count-based detection. | The attack class is studied; our defense is not. |
| Count oracle as a named technique | **Searched, not found.** Nobody documents "pin the exact expected test count in CI." | Original packaging — ours. |
| Mutation testing (Meta ACH, 2025) | The field's deep answer to weak tests: mutate the code, check tests catch it. Expensive. | Complementary layer above our cheap count check. |

**Honest limit (must go in the essay):** a count-only gate would NOT have caught
our own hollow-green incident — the count was stable; the assertions were empty.
What caught it was the count PLUS field-by-field expected-row assertions. State
the gate accurately or a careful reader will catch the overclaim.

---

## Score

- Phase 1: 9 claim groups → **8 CONFIRMED, 1 DRIFTED**, 0 GONE.
- Phase 2: 4 coverage holes filled; **four "searched, not found" results** now
  ground the novelty claim: (1) non-programmer supervisor with engineered
  verification; (2) Moqui/OFBiz + LLM research; (3) a maintained framework-idiom
  ruleset gating AI code; (4) the count oracle as a named technique.
- Open follow-ups (minor): CodeCRDT full-text blackboard detail; Aider/Replit/
  Cursor human-seat survey still running.

## Verification method

Parallel agents, adversarial posture (assume the claim is wrong until the live
source proves it), each verdict backed by an exact quote and a working URL.
Run 2026-07-06 from this session.
