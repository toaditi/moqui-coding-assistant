---
name: moqui-component
description: Manage the lifecycle of Moqui runtime components — create, retrieve, update, inspect dependencies, and package — using the repository's existing component and Gradle workflows. Use when the user asks to add a component, update installed components, or package one or more components.
---

# Moqui Component

## Quick start

- `python3 ../../scripts/moqui_repo_inventory.py components --root "<backend-root>"`
- `python3 ../../scripts/moqui_repo_inventory.py ops --root "<backend-root>"`

## Procedure

1. Inventory the current runtime components before making changes.
2. Read the target component’s `component.xml` and local artifact layout.
3. Choose the appropriate existing operation:
   - retrieve component
   - check dependencies
   - create component
   - update installed component repos
   - package one or more components
4. Preserve component boundaries and naming conventions when adding new artifacts.
5. When suggesting operational commands, use the actual Gradle tasks available in the backend root.

## Guardrails

- Do not handcraft a new component layout when `createComponent` is the intended path.
- Do not move artifacts across components without checking existing dependencies.
- Do not assume a component is deployable or shareable until `component.xml` and packaging flow are confirmed.

## References

- Component guide: `../../assets/moqui-component-management.md`
- Codebase guide: `../../assets/moqui-codebase-management.md`
