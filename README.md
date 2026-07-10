# Moqui Coding Assistant

A Claude Code plugin that teaches AI agents to build Moqui applications
the way the Moqui ecosystem builds them: find what the framework already
provides, use it, and prove the result — never reinvent, never trust an
unverified green.

## What's inside

- **13 skills** — task discipline for entities, services, screens,
  integrations, security, FreeMarker, the Maarg Data Manager,
  deployment, verification, and running an agent team.
- **4 agent roles** — a Business Analyst (writes requirements as
  business process stories), an Architect (reviews designs and PRs
  citation-by-citation against framework code), a Builder (implements
  one task, never certifies its own work), and a QA Technician
  (verifies claims adversarially; hunts tests that can never fail).
- **15 reference assets** — the knowledge the skills and agents cite:
  framework pitfalls, authoring philosophy, integration patterns, the
  HEMP requirements method, agent orchestration, and more.

## Why an agent team?

Because coding was never the bottleneck — **supervision** was. One
person feeding context to ten agents and checking every change is not
ten engineers; it is one tired person with ten browser tabs. This
plugin's agent roles work over a plain GitHub issue board, with
mechanical gates between hand-offs — the code must compile, the tests
must pass with exact expected counts, the design must use what the
framework provides. The human states the goal and judges the result.

Read the story: **[The Supervision Bottleneck](docs/the-supervision-bottleneck.md)** —
how one campaign went from requirements to 78 passing tests with no
human in the inner loop, and what went wrong on the way (including the
green test suite that was lying).

Position statement: [what this is and what it builds on](docs/agent-team-position.md) ·
Verified sources: [prior-art-agent-teams.md](docs/prior-art-agent-teams.md)
