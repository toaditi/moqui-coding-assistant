---
name: moqui-logic
description: Author or edit Moqui business logic (XML actions or Groovy) while preserving existing service and screen contracts, execution-context patterns, and logging style. Use when the user asks to implement or refactor logic in `script/**/*.groovy` files or XML action blocks inside service or screen XML.
---

# Moqui Logic

## Procedure

1. Identify the owning service or screen before editing the logic.
2. Read the calling XML contract and a nearby script in the same component first.
3. Decide where the logic belongs. **XML is the default; Groovy is the exception:**
   - If the logic can be expressed cleanly with built-in action tags (`<entity-find>`, `<service-call>`, `<set>`, `<if>`, `<iterate>`, `<return>`, etc.), write it in XML.
   - Use Groovy only when XML actions are demonstrably the wrong tool: complex branching, non-trivial transformations, regex/string work, or logic that is genuinely easier to read and test in Groovy. "Faster to type" is not a reason.
   - **The 30% rule:** if the Groovy needed exceeds ~30% of the service body, extract it to its own `script/**/*.groovy` file and call it via `<script location="..."/>`. Do not hide a script-sized chunk inside an inline `<script>` block.
4. Preserve framework-native patterns:
   - use `ec.entity`, `ec.service`, `ec.logger`, and `ec.message`
   - avoid `println`, `System.out.println`, and `printStackTrace`
   - keep logging purposeful and specific
5. Run:
   - `python3 ../../scripts/moqui_quality_audit.py audit --root "<repo-root>" --paths "<script-or-xml-file>"`
6. Verify the narrowest relevant service, screen, or component command available.

## Guardrails

- Do not change script behavior without checking the caller contract.
- Do not reach for Groovy when XML actions can express the logic cleanly. XML first; Groovy only when XML is genuinely the wrong tool.
- Do not let an inline `<script>` block grow past ~30% of the service body — extract it to a dedicated `script/**/*.groovy` file and reference it with `<script location="..."/>`.
- Do not introduce Groovy utilities or helpers when the component already has a clearer local pattern.
- Do not use broad refactors when the task only needs a local behavior correction.
- Do not pass a non-boolean-returning closure to `EntityList.findAll`/`find`/`filter` — those methods cast the result straight to `boolean` (no Groovy truthiness), so `findAll{ it.someId }` throws `ClassCastException` at runtime on non-empty lists. Always return a real boolean: `find{ it.someId != null }`. See Framework pitfalls.

## References

- Philosophy: `../../assets/moqui-authoring-philosophy.md`
- Change sequence: `../../assets/moqui-change-sequence.md`
- Checklist: `../../assets/moqui-quality-checklist.md`
- Framework pitfalls: `../../assets/moqui-framework-pitfalls.md`
