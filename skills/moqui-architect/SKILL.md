---
name: moqui-architect
description: Review or author Moqui technical designs using the Moqui Architect role, with working-code citations and a native-first framework analysis. Use before non-trivial Moqui design work or when reviewing a Moqui plan or pull request.
---

# Moqui Architect

This is the Codex entry point for the canonical Architect role. Read the full
role definition at `../../agents/moqui-architect.md` before acting. Also read
`../../docs/architect-skill-spec.md` when authoring or reviewing a design.

Follow the role's boundaries exactly:

- Review mode may inspect and report, but must not change the artifact under review.
- Authoring mode may write design documents only; it must not write product code,
  entity/service XML, or data files.
- Ground every design claim in working-code citations. If evidence is missing,
  report that gap instead of relying on framework memory.

For implementation requests, hand off to the matching implementation skill and
use `moqui-verification` after the change.
