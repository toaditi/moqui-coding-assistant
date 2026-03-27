---
name: moqui-entity-delivery
description: Create or update Moqui entities and view-entities while preserving local data model patterns, naming, descriptions, relationships, and short-alias conventions. Use when the user asks to add fields, relationships, entities, or view-entities in `entity/*.xml`.
---

# Moqui Entity Delivery

## Procedure

1. Find the target component and inspect the nearest entity file that models related data.
2. Read adjacent entities and view-entities before editing so field naming, package usage, and relationship style stay consistent.
3. Preserve local modeling patterns while applying Moqui defaults:
   - `UpperCamelCase` entity names
   - `lowerCamelCase` fields
   - `short-alias` on entities and relationships where the component uses them
   - `<description>` blocks
4. Keep structural changes narrow:
   - prefer extending an existing entity file when it already owns the same area
   - add indexes, relationships, and audit or encryption flags only where the requirement justifies them
5. Run:
   - `python3 ../../scripts/moqui_quality_audit.py audit --root "<repo-root>" --paths "<entity-file>"`
6. Verify the smallest compile or runtime path that exercises the changed entity contract.

## Guardrails

- Do not create a parallel entity package when the component already has a stable package for the domain.
- Do not rename entity packages or primary identifiers casually; treat them as contract changes.
- Do not add fields or relationships without checking how nearby services and screens consume them.

## References

- Philosophy: `../../assets/moqui-authoring-philosophy.md`
- Change sequence: `../../assets/moqui-change-sequence.md`
- Layout guide: `../../assets/moqui-layout.md`
