---
name: moqui-navigation
description: Map a Moqui repository, locate the owning component, and find where services, entities, screens, transitions, or forms are defined before editing. Use when the user asks where a change belongs, how the repo or components are organized, or to find a Moqui artifact definition before refactoring or debugging.
---

# Moqui Navigation

The single entry point for "where is this in the repo" and "where does my change belong". Use this before any authoring or verification skill.

## Quick start

Repo and component map:

- `python3 ../../scripts/moqui_repo_inventory.py summary --root "<backend-root>"`
- `python3 ../../scripts/moqui_repo_inventory.py components --root "<backend-root>"`
- `python3 ../../scripts/moqui_repo_inventory.py ops --root "<backend-root>"`

Find a specific artifact:

- `python3 ../../scripts/moqui_quality_audit.py index --root "<repo-root>"`
- `python3 ../../scripts/moqui_quality_audit.py index --root "<repo-root>" --kind service --query "<verb#Noun>"`
- `python3 ../../scripts/moqui_quality_audit.py index --root "<repo-root>" --kind entity --query "<EntityName>"`

## Procedure

1. Identify the backend root and confirm the repository layout against `../../assets/moqui-layout.md`.
2. Inventory components, integration surfaces, and available Gradle operations with `moqui_repo_inventory.py`.
3. To find a specific definition, use the `moqui_quality_audit.py index` command narrowed by `--kind` and `--query`. Fall back to `rg` for usages and related contracts after the definition is located.
4. Read the target component's `component.xml` and nearby artifacts before recommending an edit scope.
5. Route the task to the narrowest authoring skill: entity, service, screen, logic, security, integration, or component.

## Guardrails

- Do not refactor based on file names alone; confirm the actual XML or script definition.
- When a definition appears in multiple components, confirm whether the names are intentionally namespaced before changing anything.
- Do not propose new components until the existing component map is confirmed insufficient.
- Do not jump to repo-wide changes when the request is component-scoped.

## References

- Layout guide: `../../assets/moqui-layout.md`
- Codebase guide: `../../assets/moqui-codebase-management.md`
