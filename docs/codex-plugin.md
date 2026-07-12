# Codex plugin layout and validation

This repository contains a Codex plugin under `.codex-plugin/`. The plugin
manifest points at the repository's `skills/` directory and declares the
optional hook and MCP configuration files.

## Keep the package self-contained

The skill files are not independent single-file prompts. Several of them load
shared material through paths such as `../../assets/...` and
`../../scripts/...`. The agent-team skill also uses `../../agents/...` and
`../../docs/...`. As a result, packaging only the `skills/` directory produces
an incomplete installation.

When copying or publishing the plugin, preserve these directories alongside
the skills:

```text
.codex-plugin/plugin.json
skills/*/SKILL.md
assets/*.md
agents/*.md
docs/*.md
scripts/*.py
hooks.json
.mcp.json
```

The `.claude-plugin/` directory is retained for Claude Code compatibility. It
is not a substitute for `.codex-plugin/`.

The four role files under `agents/` are canonical definitions. Their matching
Codex skills under `skills/moqui-architect/`, `skills/moqui-builder/`,
`skills/moqui-business-analyst/`, and `skills/moqui-qa-technician/` are thin
entry points that load those definitions. This makes the roles discoverable as
Codex skills without duplicating their long instructions.

## Validate before publishing

Run the repository validator from the repository root:

```bash
python3 scripts/validate_codex_plugin.py
```

The validator checks that:

- the Codex manifest exists and points to real paths;
- every skill directory contains `SKILL.md`;
- shared files referenced by skills resolve from their installed layout; and
- declared hooks and MCP configuration files are present.

It exits non-zero when a package is incomplete, which makes it suitable for a
pre-publish check or CI job.

## Troubleshooting

If the validator reports a missing reference, restore the repository-relative
directory rather than changing the reference to an absolute local path. The
relative layout is what lets the same plugin work for different users and
checkout locations.
