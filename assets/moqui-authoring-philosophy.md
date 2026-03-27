# Moqui Authoring Philosophy

Use these principles when creating or updating Moqui artifacts.

## Start from the existing component

- Read the nearest existing entity, service, screen, or script in the same component before editing.
- Match the established package, naming, and placement patterns unless you are intentionally correcting a defect.
- Prefer extending the current component boundary over introducing a new parallel structure.

## Choose the right artifact

- Put data contracts in `entity/`.
- Put service interfaces and exposure settings in `service/`.
- Put orchestration in XML actions when the logic is simple and readable there.
- Move non-trivial logic into `script/` Groovy when XML actions become difficult to read or reuse.
- Keep screens focused on UI composition, navigation, and thin orchestration.

## Prefer explicit contracts

- Use clear names for services, entities, transitions, and fields.
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
