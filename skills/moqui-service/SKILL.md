---
name: moqui-service
description: Author or edit Moqui service definitions while preserving local namespace, contract, authentication, and implementation patterns. Use when the user asks to add, change, or refactor a Moqui service in `service/*.xml`, or when a service contract or exposure setting must change.
---

# Moqui Service

## Procedure

1. Find the target component and the closest existing service file in the same namespace.
2. Read the neighboring service definitions before editing.
3. Decide the implementation in this order of preference: `entity-auto` if it fits, then XML actions, then a dedicated Groovy script. Choose Groovy only when XML actions are demonstrably the wrong tool — not for convenience.
4. Preserve local naming and folder patterns:
   - keep the current namespace shape when adding to an existing file set
   - use explicit `verb` and `noun` or a deliberate full `name`
   - avoid `process` in service names
5. Review contract and exposure fields explicitly:
   - `<description>`
   - `authenticate`
   - `allow-remote`
   - transaction settings
   - script `location` when used
6. Run:
   - `python3 ../../scripts/moqui_quality_audit.py audit --root "<repo-root>" --paths "<service-file>"`
7. Run the narrowest service or component verification available and report gaps.

## Guardrails

- Do not widen `allow-remote` or anonymous access silently.
- Do not introduce a new service namespace if the component already has an established location for that concern.
- Do not reach for Groovy when XML actions can express the logic cleanly. Prefer XML; use Groovy only when it is demonstrably the right tool.
- Do not let an inline `<script>` block exceed ~30% of the service body. If it does, extract it to a dedicated `script/**/*.groovy` file and call it via `<script location="..."/>`.
- Do not add a service that drives an entity's `statusId` to a new value without also seeding the matching `moqui.basic.StatusFlowTransition` row and loading it into every target DB — the entity-auto `update#<Entity>` validates the transition and otherwise fails at runtime with `[400] Status change not allowed`. See Framework pitfalls.

## References

- Philosophy: `../../assets/moqui-authoring-philosophy.md`
- Change sequence: `../../assets/moqui-change-sequence.md`
- Checklist: `../../assets/moqui-quality-checklist.md`
- Framework pitfalls: `../../assets/moqui-framework-pitfalls.md`
