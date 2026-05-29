# Moqui Authoring Philosophy

Use these principles when creating or updating Moqui artifacts.

## Start from the existing component

- Read the nearest existing entity, service, screen, or script in the same component before editing.
- Match the established package, naming, and placement patterns unless you are intentionally correcting a defect.
- Prefer extending the current component boundary over introducing a new parallel structure.

## Choose the right artifact

- Put data contracts in `entity/`.
- Put service interfaces and exposure settings in `service/`.
- **Prefer XML actions.** If the logic can be expressed cleanly with `<entity-find>`, `<service-call>`, `<set>`, `<if>`, `<iterate>`, and the other built-in action tags, write it in XML. XML is the default; Groovy is the deliberate exception.
- Reach for Groovy only when XML actions are demonstrably the wrong tool: complex branching, non-trivial transformations, regex/string manipulation that the action tags cannot express, or logic that is genuinely easier to read and test in Groovy. "I can type Groovy faster" is not a reason.
- **The 30% rule for inline `<script>`.** If the Groovy needed for a service exceeds roughly 30% of the service body, move it to its own `script/**/*.groovy` file and call it via `<script location="..."/>`. Inline `<script>` blocks are for short, local fragments — not for hiding a script-sized chunk inside an XML service.
- Keep screens focused on UI composition, navigation, and thin orchestration.

## Prefer explicit contracts

- Use clear names for services, entities, transitions, and fields.
- Reference entities by their fully qualified name (e.g. `org.apache.ofbiz.order.order.OrderHeader`), as Moqui convention expects. Apply the same fully qualified pattern consistently in service code, data files, and other framework artifacts.
- Avoid `process` in names when a more precise verb exists.
- Add `<description>` blocks to services and entities.
- Treat authentication, `allow-remote`, and security group membership as part of the contract, not as afterthoughts.

## Preserve local consistency

- Reuse existing service namespaces and folder organization.
- Keep screen hierarchy and transition naming consistent with neighboring screens.
- Preserve existing entity package strategy and relationship naming.
- If the surrounding code has a better established pattern than the generic guideline, follow the local pattern unless it is clearly broken.

## Verify every change

- Run the Moqui audit on the files you changed.
- Run the narrowest relevant compile or test command available.
- Report what you did not verify.
