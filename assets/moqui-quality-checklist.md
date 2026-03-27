# Moqui Quality Checklist

Use this checklist before handoff, review approval, or merge.

## XML integrity

- XML files parse cleanly.
- Service, entity, and screen definitions do not collide with existing definitions.
- Screen transitions and form names are unique within each file.

## Contracts and naming

- Services use explicit `verb` and `noun` or an intentional `name`.
- Avoid `process` in service, transition, file, and variable names.
- Services and entities include `<description>` blocks.
- Entity full names remain stable when package or `entity-name` changes.

## Exposure and safety

- Public or remote services have deliberate authentication settings.
- `allow-remote="true"` is justified and not paired with accidental public access.
- Changes do not widen access silently.

## Implementation hygiene

- Groovy and Java code do not use `System.out.println`, `println`, or `printStackTrace`.
- `TODO` and `FIXME` markers are either removed or backed by a tracked follow-up.
- Logging uses framework-appropriate patterns.

## Verification

- Run the audit script on the affected paths.
- Run the narrowest relevant compile or test tasks available in the repo.
- Report every verification gap explicitly instead of implying coverage.
