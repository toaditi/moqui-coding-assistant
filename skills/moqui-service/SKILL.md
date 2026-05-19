---
name: moqui-service-delivery
description: Create or update Moqui service definitions while preserving local namespace, contract, authentication, and implementation patterns. Use when the user asks to add, change, or refactor a Moqui service in `service/*.xml`, or when a service contract or exposure setting must change.
---

# Moqui Service Delivery

## Procedure

1. Find the target component and the closest existing service file in the same namespace.
2. Read the neighboring service definitions before editing.
3. Decide whether the service should stay declarative, use `entity-auto`, or delegate to Groovy script logic.
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
- Do not put complex business logic in XML actions when it would be clearer in Groovy.

## References

- Philosophy: `../../assets/moqui-authoring-philosophy.md`
- Change sequence: `../../assets/moqui-change-sequence.md`
- Checklist: `../../assets/moqui-quality-checklist.md`
