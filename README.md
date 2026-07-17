# Moqui Coding Assistant

A Claude Code and Codex plugin that teaches AI agents to build Moqui applications
the way the Moqui ecosystem builds them: find what the framework already
provides, use it, and prove the result — never reinvent, never trust an
unverified green.

## Codex plugin

The Codex package is declared in `.codex-plugin/plugin.json`. Keep the
repository layout intact when installing it: skills use relative references to
the shared `assets/`, `agents/`, `docs/`, and `scripts/` directories. The
package can be checked before publishing with:

```bash
python3 scripts/validate_codex_plugin.py
```

See [Codex plugin layout and validation](docs/codex-plugin.md) for the package
contract and troubleshooting notes.

## What's inside

- **17 skills** — task discipline for entities, services, screens,
  integrations, security, FreeMarker, the Maarg Data Manager,
  deployment, verification, running an agent team, and four role entry points
  for the Architect, Builder, Business Analyst, and QA Technician.
- **4 agent roles** — a Business Analyst (writes requirements as
  business process stories), an Architect (reviews designs and PRs
  citation-by-citation against framework code), a Builder (implements
  one task, never certifies its own work), and a QA Technician
  (verifies claims adversarially; hunts tests that can never fail).
- **19 reference assets** — the knowledge the skills and agents cite:
  framework pitfalls, authoring philosophy, integration patterns, the
  HEMP requirements method, agent orchestration, integration testing, and more.

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
