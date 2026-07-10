# The Supervision Bottleneck

*How a team of AI agents takes a feature from requirements to delivered code —
and why the human is no longer the pipe the work flows through.*

---

## The problem

By early 2026, AI agents could code. Give one a clear task and a real codebase,
and it writes the change, runs the compiler, and returns something close to right.

Coding was not the problem. The problem was everything around it:

- Re-explaining the project at the start of every session.
- Reading every change to decide if it was correct.
- Pushing the work from one step to the next, by hand.

The agent did the typing. The human did the supervising. And there is only one
human. Ten agents that each need a person to feed them context and check their
output are not ten engineers. They are one tired person with ten browser tabs.

We call this the **supervision bottleneck**: total speed is capped by human
attention. Adding more agents makes it worse, not better.

One incident made the cost real. Our test suite reported more than one hundred
passing tests. On inspection, ten of them checked nothing — they compared
results against empty expected lists, so they could never fail. The suite was
green, and the green was a lie. A human had to catch it personally. We call
this **hollow green**. (It is not just us: a 2026 study found that 80% of test
code written by coding agents has weak or no real checks — see "Building on
published work" below.)

So the real question was: **who holds the work between the agents, and who
checks it, if not a human at every step?**

## What we built

A team of agents that takes a feature from requirements to delivered code.
The human states what the business needs, and judges the result. The agents
do the work in between:

- An **analyst agent** writes the requirement as a business process story —
  a short text where each sentence is one named actor doing one action, in
  order. ("Packer scans the picklist barcode.")
- An **architect agent** shapes the design and reviews every change before it
  is merged.
- **Builder agents** write the code, one task each, each in its own workspace.
- A **QA agent** verifies the outcome and hunts for hollow green.

Each role is a versioned text document — the prompt *is* the role. Change the
document, and the role changes.

The work moves between the agents over a **shared board**: our normal GitHub
issues. An issue carries a status label — ready, claimed, in review, merged,
verified — and exactly one label at a time. The label is the state. No agent
talks to another directly; they read and write the board. There is no special
server. The board a human team already uses is the whole machine.

A small watcher process polls the board, sees a ready issue, and starts the
right agent for it. That is all the "orchestration" there is.

## The checks

Every hand-off has a check that does not depend on anyone's opinion:

- The code must **compile**.
- The full test suite must pass with the **exact expected counts** — for
  example, exactly 78 tests, 0 failed, 0 skipped — and every test asserts
  expected values field by field. The count catches a suite that silently
  shrinks; the field-by-field checks catch tests that pass while checking
  nothing. Both are needed: in our hollow-green incident the count was stable
  and only the field checks could have caught it.
- The design must **use what the framework already provides** instead of
  reinventing it. Hand-written code where a native mechanism exists is treated
  as a defect, even if it works.

That last check is not new to us. It is how the OFBiz and Moqui community has
always reviewed code: first question, "does this pattern already exist?" We
taught the same discipline to the agents and made it mechanical.

Instructions in a document are advisory — an agent can miss them in a long
session. A failing check is not. Agents respond to a red build far more
reliably than to a rule written in a file. So the rules that matter are
expressed as checks.

One more principle sits on top: **mechanical truth outranks model opinion.**
An AI reviewer's judgment is useful, but it sits above the checks, never in
place of them. The story below shows why.

## Building on published work

None of the building blocks is our invention, and their published results tell
us the approach is sound. Credit where it is due:

- **Agent teams with roles** (planner, builder, reviewer, tester): MetaGPT and
  ChatDev showed this in 2023. A 2025 study of 94 systems found role-based
  teams are the most common design in the field (46.8% of systems). The same
  study found something else: almost nobody (5.3%) designs the human's place
  and the checks around it. That gap is exactly where our work sits.
- **Coordination over a shared board** (the "blackboard" pattern — agents
  read and write one shared surface instead of messaging each other): applied
  to LLM agents by Han & Zhang (2025) and CodeCRDT (2025). PatchBoard (2026)
  went further: a rule-based checker validates every agent's change to the
  shared state, and reports large gains in success rate and cost. Our
  label-gated GitHub board is the same idea, mounted on a tool the team
  already uses.
- **Rules as executable checks**: the "architecture fitness function" pattern —
  write the rule as an automated test and let the agent fix code until it
  passes. Practitioners also documented the failure our story below shows: an
  AI reviewer will *rationalize* a violation ("probably fine") unless a
  mechanical check stops it.
- **Why niche frameworks need a repair loop**: an SAP ABAP benchmark (2026)
  found top models succeed only 19–24% on first try in a niche enterprise
  language — but reach 77% with a few rounds of compiler feedback. Moqui is
  also a niche, model-driven framework. This is why we both feed framework
  knowledge *in* (skill documents the agents read) and gate the output —
  context going in and checks coming out are two halves of one answer.
- **The weak-test problem is measured**: "All Smoke, No Alarm" (2026) found
  80.2% of agent-written test patches have weak or no real assertions, across
  the five major coding agents it studied. Our hollow-green incident is an
  instance of an industry-wide phenomenon.
- **The honest counter-position**: Cognition ("Don't Build Multi-Agents",
  2025) warns that parallel agents make conflicting decisions. We agree with
  the warning. Our answer is that writes stay serial — one issue, one builder,
  one workspace — and the extra agents contribute judgment, not parallel
  writes. That matches Cognition's own 2026 revision of their position.

## The day it ran itself

The test was a real campaign: converting our order-test corpus from a
hand-written variable substitution engine to FreeMarker, the framework's own
template engine. Ten tasks, one real Moqui component, touching production
import code.

It ran as a board. The architect approved the plan. Builders claimed tasks,
built each in its own workspace, and the architect reviewed every merge —
eleven reviews. No human in the inner loop. The end state: **78 tests, 0
failed, 0 skipped**, with per-family results identical to the baseline.

A clean finish is not the interesting part. Three times, the machine caught
its own mistakes:

**It caught its own plan — twice.** The first task assumed a missing method
would fail at compile time. It cannot: dynamic Groovy fails at runtime. The
gate re-derived the correct check and the plan was amended. Later, a builder
refused a plan step that would change a field's type, traced the real
consumer of that field, and showed six of eight scenarios would crash. The
architect verified this independently, and a later task was corrected
*before* it was dispatched. The plan bent to the code, not the reverse.

**It caught its own reviewer.** A builder shipped a task and correctly
flagged a small doubt in a new test. The architect reviewed, approved the
merge, and waved the doubt off with a stated reason: "the JSON parser is
lenient about unquoted strings." That claim is false. The QA gate below the
architect re-ran the full suite against the merged result: **78 tests, 1
failed** — exactly the waved-off test. The parser in the real code path is
strict. The gate refused to verify the merge, wrote up the root cause, and a
builder fixed it in the next cycle. No human touched any of it.

The lesson is not that the reviewer was careless. Frontier-model judgment is
good, and mostly right. The lesson is that a confident, plausible sentence
can be wrong — and the only reliable defense is a check that does not care
how plausible the sentence sounds. The compiler, the counts, the strict
parser: these have no opinions. That is why mechanical truth outranks model
opinion at every gate.

## Honest limits

- **One run is one run.** One operator, one repository, one week. It is a
  pilot, not a statistic.
- **The checks need a clear true/false answer.** Our campaign had one — a
  deterministic test suite (an "oracle": something that tells you, reliably,
  whether the result is right). Where no such oracle exists, the
  gate-refutes-the-reviewer move is not available, and the system leans back
  on model opinion. The method's strength is exactly the boundary of where
  it applies.
- **Agent seats cost money.** We pay for strong models where judgment matters
  (architect, verification) and use cheaper ones for retrieval and mechanical
  edits. The checks are what make the cheap seats safe.
- **Portability is untested.** Everything above happened with one person who
  holds the whole system in their head. Whether a second person can take the
  goal-holder seat and get the same result is the next question. It is filed
  as an issue, like everything else.

## The measure

Our measure of success is simple: the human — analyst or programmer — gets
what they asked for, and the code reads as if the ecosystem wrote it.

---

*Position statement: [agent-team-position.md](agent-team-position.md).
Verified sources for every citation above:
[prior-art-agent-teams.md](prior-art-agent-teams.md). Orchestration engine
(normative): [moqui-agent-orchestration.md](../assets/moqui-agent-orchestration.md).*
