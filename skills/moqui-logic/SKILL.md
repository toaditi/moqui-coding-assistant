---
name: moqui-logic-delivery
description: Create or update Moqui Groovy or XML action logic while preserving existing service and screen contracts, execution-context patterns, and logging style. Use when the user asks to implement or refactor business logic in `script/**/*.groovy` files or XML action blocks in Moqui XML.
---

# Moqui Logic Delivery

## Procedure

1. Identify the owning service or screen before editing the logic.
2. Read the calling XML contract and a nearby script in the same component first.
3. Decide where the logic belongs:
   - XML actions for straightforward orchestration
   - Groovy for more complex branching, reuse, or non-trivial transformation
4. Preserve framework-native patterns:
   - use `ec.entity`, `ec.service`, `ec.logger`, and `ec.message`
   - avoid `println`, `System.out.println`, and `printStackTrace`
   - keep logging purposeful and specific
5. Run:
   - `python3 ../../scripts/moqui_quality_audit.py audit --root "<repo-root>" --paths "<script-or-xml-file>"`
6. Verify the narrowest relevant service, screen, or component command available.

## Guardrails

- Do not change script behavior without checking the caller contract.
- Do not introduce Groovy utilities or helpers when the component already has a clearer local pattern.
- Do not use broad refactors when the task only needs a local behavior correction.

## References

- Philosophy: `../../assets/moqui-authoring-philosophy.md`
- Change sequence: `../../assets/moqui-change-sequence.md`
- Checklist: `../../assets/moqui-quality-checklist.md`
