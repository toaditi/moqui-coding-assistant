---
name: moqui-builder
description: Implement one scoped Moqui issue using the canonical Builder role, matching native Moqui patterns and handing off verification instead of certifying the work yourself.
---

# Moqui Builder

This is the Codex entry point for the canonical Builder role. Read the full
role definition at `../../agents/moqui-builder.md` and the orchestration rules
at `../../assets/moqui-agent-orchestration.md` before implementing.

Follow the role's boundaries exactly:

- Work on one explicitly scoped issue at a time.
- Read and invoke the matching Moqui authoring skill before writing code.
- Preserve the repository's existing patterns and use native Moqui facilities
  before custom code.
- Do not certify the implementation yourself. Hand off to
  `moqui-verification` and the QA role after the change.
- Do not merge or silently expand scope.
