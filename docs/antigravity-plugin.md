# Antigravity plugin layout and validation

This repository contains an Antigravity plugin under `.antigravity-plugin/` and workspace configuration under `.agents/`. The plugin manifests point to the repository's `skills/` and `agents/` directories and declare hook and MCP configuration files.

## Keep the package self-contained

The skill files are not independent single-file prompts. Several of them load shared material through relative paths such as `../../assets/...` and `../../scripts/...`. The agent-team skill also uses `../../agents/...` and `../../docs/...`. As a result, packaging only the `skills/` directory produces an incomplete installation.

When copying or publishing the plugin for Google Antigravity (Antigravity IDE, Antigravity 2.0, or `agy` CLI), preserve these directories alongside the skills:

```text
.antigravity-plugin/plugin.json
.agents/plugin.json
skills/*/SKILL.md
assets/*.md
agents/*.md
docs/*.md
scripts/*.py
hooks.json
.mcp.json
```

The four role files under `agents/` are canonical definitions. Their matching skills under `skills/moqui-architect/`, `skills/moqui-builder/`, `skills/moqui-business-analyst/`, and `skills/moqui-qa-technician/` are entry points that load those definitions.

## Validate before publishing

Run the Antigravity repository validator from the repository root:

```bash
python3 scripts/validate_antigravity_plugin.py
```

The validator checks that:

- the Antigravity plugin manifests exist and point to real paths;
- every skill directory contains `SKILL.md`;
- shared files referenced by skills resolve from their installed layout; and
- declared hooks, agents, and MCP configuration files are present.

It exits non-zero when a package is incomplete.

## Usage in Antigravity

1. **Workspace setup**: Open this repository in Antigravity IDE or Antigravity 2.0. Antigravity automatically detects the `.agents/` folder and registers the project skills and roles.
2. **Plugin installation**: Copy the repository or install via `.antigravity-plugin/` into your global plugins folder (`~/.gemini/config/plugins/moqui-coding-assistant`).
