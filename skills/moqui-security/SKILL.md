---
name: moqui-security
description: Author or edit Moqui security artifacts and exposure settings while preserving the existing authorization strategy and avoiding accidental public access. Use when the user asks to change ArtifactGroups, ArtifactAuthz, service exposure (`allow-remote`, `authenticate`), screen access (`require-authentication`), or related security data.
---

# Moqui Security

## Procedure

1. Identify whether the change is contract exposure or explicit security data:
   - service `allow-remote` or `authenticate`
   - screen `require-authentication`
   - security data under `data/*Security*.xml`
2. Read the nearest existing security or exposure pattern in the same component before editing.
3. Keep the change aligned with the current authorization strategy:
   - reuse existing artifact groups where appropriate
   - preserve naming and grouping conventions
   - update security data when new artifacts require authorization
4. Run:
   - `python3 ../../scripts/moqui_quality_audit.py audit --root "<repo-root>" --paths "<changed-files>"`
5. Call out every access widening explicitly in the final summary.

## instance_purpose — the instance safety switch

Every instance declares its purpose in the Moqui conf:
`dev` (MoquiDevConf), `production` (default and docker conf). Read it
ONE way: `System.getProperty('instance_purpose')`.

Rules:

- **Dev-only tooling** (test-data generators, fixture loaders, debug
  surfaces) must gate on `== 'dev'` and refuse otherwise. The
  framework default is `production` (`MoquiDefaultConf.xml:11`), so an
  unset property fails closed — keep it that way: check for the exact
  value `dev`, never for "not production".
- **Never gate business logic on it** — it selects safety posture,
  not behavior. An order flows the same on every instance.
- Show it on ops/about screens (the oms and maarg-util screens
  already do) so a human can always see what an instance thinks it is.

## Guardrails

- Do not widen anonymous or remote access as a side effect of a functional change.
- Do not assume service exposure alone is sufficient; inspect artifact-group and authorization implications where applicable.
- Treat missing verification of access control behavior as residual risk, not as success.

## References

- Philosophy: `../../assets/moqui-authoring-philosophy.md`
- Change sequence: `../../assets/moqui-change-sequence.md`
- Checklist: `../../assets/moqui-quality-checklist.md`
