---
name: moqui-entity
description: Author or edit Moqui entities and view-entities while preserving local data model patterns, naming, descriptions, relationships, and short-alias conventions. Use when the user asks to add fields, relationships, entities, or view-entities in `entity/*.xml`.
---

# Moqui Entity

## Procedure

1. Find the target component and inspect the nearest entity file that models related data.
2. Read adjacent entities and view-entities before editing so field naming, package usage, and relationship style stay consistent.
3. Preserve local modeling patterns while applying Moqui defaults:
   - `UpperCamelCase` entity names
   - `lowerCamelCase` fields
   - fully qualified entity names when referencing entities (e.g. `org.apache.ofbiz.order.order.OrderHeader`), matching Moqui convention; use the same qualified pattern in data files and other framework artifacts
   - `short-alias` on entities and relationships where the component uses them
   - `<description>` blocks
4. Keep structural changes narrow:
   - prefer extending an existing entity file when it already owns the same area
   - add indexes, relationships, and audit or encryption flags only where the requirement justifies them
5. Run:
   - `python3 ../../scripts/moqui_quality_audit.py audit --root "<repo-root>" --paths "<entity-file>"`
6. Verify the smallest compile or runtime path that exercises the changed entity contract.

## Smell words — when a description means "view-entity"

| When the design or code says… | It means… |
|---|---|
| "for each X, look up its Y" | a loop with lookups → one view-entity find |
| "filter X by a field that lives on Y" | a join → view-entity |
| "check it is still valid / current / not expired" | `<date-filter/>` on the dated member |
| "then sort and take the first / second" | `<order-by>` in the find — never sort in memory |
| "count / total per group" | alias with `function="count|sum"` — never accumulate in a loop |

Before declaring a new view: search the component's `entity/*.xml`
and the framework's built-ins — the join often already exists
(`GeoAssocAndToDetail`, `FacilityContactDetailByPurpose`,
`ShopifyShopAndProduct`…). Reuse beats redeclaring.

## Guardrails

- Do not create a parallel entity package when the component already has a stable package for the domain.
- Do not rename entity packages or primary identifiers casually; treat them as contract changes.
- Do not add fields or relationships without checking how nearby services and screens consume them.

## References

- Philosophy: `../../assets/moqui-authoring-philosophy.md`
- Change sequence: `../../assets/moqui-change-sequence.md`
- Layout guide: `../../assets/moqui-layout.md`
