# Position Statement

*(Adopted 2026-07-06. The story behind it:
[the-supervision-bottleneck.md](the-supervision-bottleneck.md); the verified
sources: [prior-art-agent-teams.md](prior-art-agent-teams.md).)*

We are building a team of AI agents that takes a feature from requirements to
delivered code. A human states what the business needs and judges the result.
The agents do the work in between: an analyst agent writes the requirements
as a business process story, an architect agent shapes and reviews the design,
builder agents write the code, and a QA agent verifies the outcome. The work
moves between them over a shared board — no person pushes it from step to step.

Every hand-off has a check that does not depend on anyone's opinion: the code
must compile, the tests must pass with the exact expected counts, the design
must use what the framework already provides instead of reinventing it. That
last check is how the OFBiz and Moqui community has always reviewed code —
we taught the same discipline to the agents.

Others have published the building blocks we use, and their results tell us
the approach is sound: MetaGPT and ChatDev on agent roles, the blackboard line
of work on shared-state coordination, PatchBoard on deterministic validation,
the fitness-function pattern on rules as executable checks, and the ABAP
benchmark on why niche frameworks need a verify-and-repair loop. We build on
their work with credit.

Our measure of success is simple: the human gets what they asked for, and the
code reads as if the ecosystem wrote it.
