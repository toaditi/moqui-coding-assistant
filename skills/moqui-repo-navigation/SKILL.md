---
name: moqui-repo-navigation
description: Map Moqui services, entities, screens, transitions, and forms before refactoring or debugging. Use when the user needs to find where a Moqui artifact is defined, trace the local component layout, or build edit scope before changing a Moqui repository.
---

# Moqui Repo Navigation

## Quick start

- `python3 ../../scripts/moqui_quality_audit.py index --root "<repo-root>"`
- `python3 ../../scripts/moqui_quality_audit.py index --root "<repo-root>" --kind service --query "save#RuleSet"`
- `python3 ../../scripts/moqui_quality_audit.py index --root "<repo-root>" --kind entity --query "JsonSchema"`

## Procedure

1. Use the bundled index to find likely definition sites.
2. Narrow by `--kind` and `--query` before falling back to broad repo search.
3. After locating a definition, use `rg` to find usages and related contracts.
4. Use `../../assets/moqui-layout.md` to confirm whether the artifact sits in the expected component boundary.

## Guardrails

- Do not refactor based on file names alone; confirm the actual XML or script definition.
- When a definition appears in multiple components, confirm whether the names are intentionally namespaced before changing anything.

## References

- Layout guide: `../../assets/moqui-layout.md`
