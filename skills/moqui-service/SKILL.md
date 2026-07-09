---
name: moqui-service
description: Author or edit Moqui service definitions while preserving local namespace, contract, authentication, and implementation patterns. Use when the user asks to add, change, or refactor a Moqui service in `service/*.xml`, or when a service contract or exposure setting must change.
---

# Moqui Service

## Procedure

1. Find the target component and the closest existing service file in the same namespace.
2. Read the neighboring service definitions before editing.
3. Decide the implementation in this order of preference: `entity-auto` if it fits, then XML actions, then a dedicated Groovy script. Choose Groovy only when XML actions are demonstrably the wrong tool — not for convenience. Read `../../assets/moqui-service-engine.md` first — entity-auto and the calling API do more than most authors assume.
4. Decide the execution mode before implementing: sync, async, or scheduled `ServiceJob`. For scheduled or recurring work, define a `ServiceJob` record — do not build custom scheduling.
5. Preserve local naming and folder patterns:
   - keep the current namespace shape when adding to an existing file set
   - use explicit `verb` and `noun` or a deliberate full `name`
   - avoid `process` in service names
6. Review contract and exposure fields explicitly:
   - `<description>`
   - `authenticate`
   - `allow-remote`
   - transaction settings
   - `semaphore` for scheduled or long-running services
   - parameter validations and `allow-html` on String parameters
   - script `location` when used
7. Run:
   - `python3 ../../scripts/moqui_quality_audit.py audit --root "<repo-root>" --paths "<service-file>"`
8. Run the narrowest service or component verification available and report gaps.

## Guardrails

- Do not widen `allow-remote` or anonymous access silently.
- Do not introduce a new service namespace if the component already has an established location for that concern.
- Do not reach for Groovy when XML actions can express the logic cleanly. Prefer XML; use Groovy only when it is demonstrably the right tool.
- Do not let an inline `<script>` block exceed ~30% of the service body. If it does, extract it to a dedicated `script/**/*.groovy` file and call it via `<script location="..."/>`.
- Do not add a service that drives an entity's `statusId` to a new value without also seeding the matching `moqui.basic.StatusFlowTransition` row and loading it into every target DB — the entity-auto `update#<Entity>` validates the transition and otherwise fails at runtime with `[400] Status change not allowed`. See Framework pitfalls.
- Do not hand-roll concurrency locks (lock tables, "isRunning" flags); the `semaphore` attribute on the service definition covers single-instance execution.
- Do not hand-write input validation the parameter validation sub-elements cover (`matches`, `number-range`, `text-length`, `text-email`, ...); declared validations also generate client-side form validation free.
- Job monitoring reads `ServiceJobRun` (one record per execution: `startTime`, `endTime`, `hasError`, `errors`), never `ServiceJobRunLock` (scheduler lock). See Framework pitfalls and the service engine reference.

## References

- Philosophy: `../../assets/moqui-authoring-philosophy.md`
- Change sequence: `../../assets/moqui-change-sequence.md`
- Checklist: `../../assets/moqui-quality-checklist.md`
- Framework pitfalls: `../../assets/moqui-framework-pitfalls.md`
- Service engine reference: `../../assets/moqui-service-engine.md`
