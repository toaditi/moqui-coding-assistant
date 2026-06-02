---
name: moqui-screen
description: Author or edit Moqui XML screens while preserving local hierarchy, transition, form, and security patterns. Use when the user asks to change files under `screen/`, add transitions or subscreens, or refactor screen orchestration in a Moqui component.
---

# Moqui Screen

## Procedure

1. Find the target screen and read the parent screen plus a nearby sibling screen first.
2. Follow the current component structure for:
   - subscreens and default items
   - transition naming
   - form placement and naming
   - `require-authentication` usage
3. Keep screens thin:
   - UI composition and navigation in the screen
   - non-trivial reusable logic in services or Groovy scripts
4. When adding transitions, confirm the backing service or script already exists or is part of the same change.
5. Run:
   - `python3 ../../scripts/moqui_quality_audit.py audit --root "<repo-root>" --paths "<screen-file>"`
6. If the screen calls services or depends on entities changed in the same task, verify those contracts too.

## Guardrails

- Do not bury substantial business logic in screen XML just because the edit started there.
- Do not add duplicate transition or form names in the same screen.
- Do not widen public screen access without checking the component’s existing security posture.
- Do not put `condition` on `<container>` or `<container-box>` — it is silently ignored and the block always renders. Use a `<section name="..." condition="...">` wrapper instead (audit code `screen-container-condition`).
- Do not write bare `key`/`text` on `<list-options>` — they are expand strings, not field names. Interpolate the row field: `key="${idField}" text="${labelField}"` (audit code `screen-list-options-literal`).

## References

- Philosophy: `../../assets/moqui-authoring-philosophy.md`
- Change sequence: `../../assets/moqui-change-sequence.md`
- Layout guide: `../../assets/moqui-layout.md`
- Framework pitfalls: `../../assets/moqui-framework-pitfalls.md`
