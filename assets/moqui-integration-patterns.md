# Moqui Integration Patterns

Use this guide when adding or modifying external integrations.

## Prefer the current repo pattern first

In this codebase, external integration is primarily managed through:

- facade services with deliberate `allow-remote` and `authenticate` settings
- `SystemMessageRemote` records for remote endpoints and credentials
- `SystemMessageType` flows for queued or reliable messaging
- component-specific integration modules such as `netsuite-darpan` and `moqui-sftp`
- Groovy logic that reads remote configuration from entities instead of hardcoding it

## Current repo observations

- Runtime components do not currently expose `*.rest.xml` files.
- Public API behavior is mainly expressed through service contracts and facade services.
- SFTP integration is modeled through the system-message framework in `moqui-sftp`.
- Darpan stores remote configuration such as JDBC and provider settings in `SystemMessageRemote`.

## Integration workflow

1. Find the owning component for the external system.
2. Read the nearest existing remote configuration and service flow first.
3. Decide whether the integration should be:
   - synchronous service call
   - facade-exposed service
   - reliable system-message workflow
   - component-specific connector
4. Keep URLs, credentials, and remote identifiers in Moqui-managed configuration where the component already does so.
5. Audit exposure, reliability, and configuration drift after the change.
