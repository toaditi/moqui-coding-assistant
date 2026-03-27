# Moqui Artifact Map

Use this map to locate the right artifact type before editing or reviewing.

## Common component layout

- `runtime/component/<component>/entity/`
  - Entity and view-entity definitions
- `runtime/component/<component>/service/`
  - Service XML definitions and REST service descriptors
- `runtime/component/<component>/screen/`
  - XML screens, transitions, forms, and menus
- `runtime/component/<component>/script/`
  - Groovy scripts referenced by services and screens
- `runtime/component/<component>/data/`
  - Seed, demo, or migration data
- `runtime/component/<component>/template/`
  - FreeMarker templates and macros

## Review heuristics

- If a service XML changed, inspect nearby screen and script references.
- If an entity XML changed, inspect service calls, screen forms, and seed data that depend on it.
- If a screen XML changed, inspect transitions, form names, and referenced service names.
- If a script changed, inspect the XML service or screen that dispatches to it.
