---
name: moqui-verification-loop
description: Run a focused verification loop for Moqui changes using audit-first checks, narrow compile or test execution, and explicit residual-risk reporting. Use after implementing Moqui changes or before handoff when evidence is needed for what was verified and what remains unverified.
---

# Moqui Verification Loop

## Procedure

1. Run the audit script on the changed paths first:
   - `python3 ../../scripts/moqui_quality_audit.py audit --root "<repo-root>" --paths "<file-or-dir>" ...`
2. Find the narrowest verification command that matches the change:
   - component compile for XML or script wiring changes
   - targeted tests for service or logic changes
   - broader checks only when the repo does not expose narrower coverage
3. Record what ran, what passed, and what was skipped.
4. Report residual risk explicitly when runtime validation or UI exercise was not possible.

## Guardrails

- Do not claim full repo verification from a component-scoped check.
- Do not skip the audit just because compile or tests pass.
- If no safe verification command is available, say so directly and stop short of over-claiming confidence.

## References

- Checklist: `../../assets/moqui-quality-checklist.md`
