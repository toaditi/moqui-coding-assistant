---
name: moqui-quality-review
description: Review Moqui changes for correctness, XML contract drift, naming and logging violations, public service exposure risk, missing descriptions, and verification gaps. Use when the user asks for a code review, cleanup pass, hardening pass, or merge-readiness check in a Moqui repository.
---

# Moqui Quality Review

## Output contract

- Report findings first.
- Order findings by severity.
- Include exact file references and concrete risk statements.
- If there are no findings, say so explicitly and list residual risks or verification gaps.

## Procedure

1. Identify the smallest review scope that matches the request.
   - Prefer changed files from git diff.
   - If the scope is unclear, start with the affected component instead of the entire monorepo.
2. Run the bundled audit:
   - `python3 ../../scripts/moqui_quality_audit.py audit --root "<repo-root>"`
   - Add `--paths "<file-or-dir>" ...` to narrow the scan.
3. Read the changed files plus the nearby service, entity, screen, or script contracts needed to judge impact.
4. Cross-check the result against `../../assets/moqui-quality-checklist.md`.
5. Report only material bugs, regressions, contract mismatches, and verification gaps.

## Guardrails

- Do not treat XML parse errors or duplicate definitions as style nits.
- Do not ignore public remote services without explicit justification.
- Do not rely on the script alone; confirm suspicious findings against the source before reporting them.

## References

- Checklist: `../../assets/moqui-quality-checklist.md`
- Layout guide: `../../assets/moqui-layout.md`
