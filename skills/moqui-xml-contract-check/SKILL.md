---
name: moqui-xml-contract-check
description: Validate Moqui service, entity, and screen XML for parse errors, duplicate definitions, missing descriptions, risky exposure settings, and naming drift. Use when creating or refactoring Moqui XML, when XML parse errors occur, or when service/entity/screen contracts may have changed.
---

# Moqui XML Contract Check

## Procedure

1. Scope the check to the affected XML files or component.
2. Run:
   - `python3 ../../scripts/moqui_quality_audit.py audit --root "<repo-root>" --paths "<file-or-dir>" ...`
3. Inspect the XML manually for the contract details that matter to the change:
   - services: verb, noun, `allow-remote`, `authenticate`, descriptions, and script locations
   - entities: package, `entity-name`, descriptions, and table mappings
   - screens: transition names, form names, and referenced service calls
4. Compare placement and naming against `../../assets/moqui-layout.md`.
5. Summarize real contract risk, not just raw scan output.

## Guardrails

- Treat duplicate full service or entity names as likely defects until proven otherwise.
- Treat missing descriptions as a maintainability problem, not a blocker by default.
- Call out widened access separately from general XML hygiene findings.

## References

- Checklist: `../../assets/moqui-quality-checklist.md`
- Layout guide: `../../assets/moqui-layout.md`
