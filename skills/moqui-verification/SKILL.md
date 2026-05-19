---
name: moqui-verification
description: Verify Moqui changes by running the bundled audit (XML contract checks, naming and logging violations, public-exposure risk, missing descriptions), then the narrowest compile or test command available, and finally reporting findings plus residual risk. Use after implementing Moqui changes, when reviewing a diff, before merge-readiness, or when XML parse errors or contract drift are suspected.
---

# Moqui Verification

The single verification entry point. Combines what was previously split across quality review, XML contract checks, and a verification loop. Always run audit first, then narrow runtime checks, then report.

## Output contract

- Report findings first, ordered by severity.
- Include exact file references and concrete risk statements.
- If there are no findings, say so explicitly and list residual risks or verification gaps.
- Call out widened access (public, anonymous, remote) separately from general hygiene findings.

## Procedure

1. Identify the smallest review scope that matches the request.
   - Prefer changed files from `git diff`.
   - If scope is unclear, start with the affected component, not the whole repo.
2. Run the audit:
   - `python3 ../../scripts/moqui_quality_audit.py audit --root "<repo-root>"`
   - Add `--paths "<file-or-dir>" ...` to narrow.
3. Inspect the XML or scripts manually for the contract details that matter to the change:
   - services: verb, noun, `allow-remote`, `authenticate`, descriptions, script locations
   - entities: package, `entity-name`, descriptions, table mappings
   - screens: transition names, form names, referenced service calls
   - scripts: framework-native patterns (`ec.entity`, `ec.service`, `ec.logger`, `ec.message`)
4. Cross-check findings against `../../assets/moqui-quality-checklist.md` and placement against `../../assets/moqui-layout.md`.
5. Run the narrowest runtime verification command available:
   - component compile for XML or script wiring changes
   - targeted tests for service or logic changes
   - broader checks only if no narrower coverage exists
6. Record what ran, what passed, what was skipped, and what remains unverified.

## Guardrails

- Do not treat XML parse errors or duplicate full service/entity names as style nits.
- Do not ignore public remote services without explicit justification.
- Do not claim full repo verification from a component-scoped check.
- Do not skip the audit just because compile or tests pass.
- If no safe verification command is available, say so directly. Do not over-claim confidence.
- Confirm suspicious findings against the source before reporting them.

## References

- Checklist: `../../assets/moqui-quality-checklist.md`
- Layout guide: `../../assets/moqui-layout.md`
