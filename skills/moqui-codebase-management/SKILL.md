---
name: moqui-codebase-management
description: Map Moqui repository structure, locate the owning component, inspect build and runtime operations, and choose the right edit scope before coding. Use when the user asks how the codebase is organized, where a change belongs, how components fit together, or how to navigate a Moqui repository before implementation.
---

# Moqui Codebase Management

## Quick start

- `python3 ../../scripts/moqui_repo_inventory.py summary --root "<backend-root>"`
- `python3 ../../scripts/moqui_repo_inventory.py components --root "<backend-root>"`
- `python3 ../../scripts/moqui_repo_inventory.py ops --root "<backend-root>"`

## Procedure

1. Identify the backend root and confirm the repository layout.
2. Run the inventory script to get:
   - component list
   - integration surfaces
   - available Gradle operations
3. Read the target component’s `component.xml` and nearby artifacts before making change suggestions.
4. Route the task to the narrowest Moqui workflow:
   - entity, service, screen, logic, security, component, integration, or deployment
5. Prefer existing component boundaries and local patterns over abstract reorganization.

## Guardrails

- Do not assume every Moqui repo uses the same integration or deployment style.
- Do not propose new components until you confirm the existing component map is insufficient.
- Do not jump to repo-wide changes when the request is component-scoped.

## References

- Codebase guide: `../../assets/moqui-codebase-management.md`
- Layout guide: `../../assets/moqui-layout.md`
