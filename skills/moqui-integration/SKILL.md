---
name: moqui-integration-management
description: Design, update, and review Moqui external integrations while preserving the repository’s current patterns for remote services, system-message configuration, connector components, and remote endpoint storage. Use when the user asks to manage external integrations, outbound API calls, inbound webhook handling, remote configuration, or integration-specific components in a Moqui repository.
---

# Moqui Integration Management

## Quick start

- `python3 ../../scripts/moqui_repo_inventory.py integrations --root "<backend-root>"`

## Procedure

1. Inventory current integration surfaces before changing anything.
2. Identify the owning component and existing integration style:
   - public or remote facade service
   - system-message workflow
   - connector component
   - direct outbound REST client usage
3. Read the nearest existing config and flow before editing.
4. Keep remote configuration in Moqui-managed records or seed data when the component already uses that pattern.
5. Audit exposure and reliability after the change.

## Guardrails

- Do not introduce a new integration pattern if the component already has a stable one.
- Do not hardcode credentials or remote URLs into logic when the repo uses `SystemMessageRemote` or equivalent configuration storage.
- Do not widen public access without explicitly calling it out.

## References

- Integration guide: `../../assets/moqui-integration-patterns.md`
- Philosophy: `../../assets/moqui-authoring-philosophy.md`
