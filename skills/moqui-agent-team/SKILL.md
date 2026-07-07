---
name: moqui-agent-team
description: Set up and operate the agent-team orchestration — a manager + worker pool coordinated over GitHub Issues with label state, an architect PR gate, and a QA merge gate. Use when the user asks to enable team mode, set up the agent board, start the watcher, or check why the pool is not picking up an issue.
---

# Moqui Agent Team

Sets up the coordination model described in
`../../assets/moqui-agent-orchestration.md` (read it first — it is the
normative document; this skill only automates its setup).

## Quick start

```bash
# the three lifecycle labels (idempotent — safe to re-run)
gh label create "status:ready"   --repo "<issue-repo>" --color 0E8A16 --description "claimable by the agent pool" --force
gh label create "status:claimed" --repo "<issue-repo>" --color FBCA04 --description "in progress; paired with worker:<id>" --force
gh label create "status:blocked" --repo "<issue-repo>" --color D93F0B --description "on hold" --force
```

## Procedure

1. **Collect the four config values** (ask the user; write them into the
   project's `PROJECT.md` or CLAUDE.md so every future session sees them):
   - `«issue repo»` — where the pool's issues live
   - `«org»` — the GitHub org (or user) the watcher polls
   - `«owner»` — the pool owner login; issues assigned to it are the pool's
     work queue
   - `«feature branch»` — the integration branch agent PRs merge into
     (never main/release)
2. **Create the three labels** in `«issue repo»` (Quick start above).
3. **Check issue types.** The routing uses native issue types
   (Requirements / Design / Build / Defect / Verify). These are an
   organization-wide GitHub setting. If they don't exist, tell the user how to
   add them (org Settings → Planning → Issue types) — and note the fallback:
   no type = treated as Build.
4. **Verify access.** Confirm `gh auth status` works, the authenticated
   account can label issues in `«issue repo»`, and `«owner»` exists.
5. **Dry-run the watcher search** and show the user the result:
   `gh search issues --owner="«org»" --assignee="«owner»" --state=open --label=status:ready`
   An empty list is a correct result on a fresh board.
6. **Start the watcher** when the user says go: a persistent session on a
   cheap model that runs the search every ~4–5 minutes, routes each hit by
   issue type to the matching agent of this plugin, enforces the WIP limit
   (≤ 3 claimed at once), and does no issue work itself.
7. **File the first issue** with the user: title, type, assign to `«owner»`,
   add `status:ready`. Watch the pool claim it.

## Operating checks (when "the pool is stuck")

- Issue not picked up → is it assigned to `«owner»`? Does it have
  `status:ready`? Is it `status:blocked` or blocked-by an open issue?
- Claimed but no PR → past the claim TTL, revert to `status:ready`
  (remove `status:claimed` + `worker:*`).
- Two `worker:*` labels on one issue → the claim race: lowest worker id wins;
  revert the other.
- Merged but not closed → the QA merge gate has not run or REFUTED; read the
  issue's `QA GATE:` comment.

## Guardrails

- Never merge `«feature branch»` into main/release, deploy, or write to any
  external system without an explicit human ok — these are the hard stops.
- One status label per issue at any time; the label IS the state.
- Do not invent extra labels for facts GitHub already stores natively (type,
  priority, dependencies, PR state) — see the asset's state model.
- The watcher spawns workers; it never works an issue itself. The manager
  files and verifies; it never codes while the pool runs.

## References

- Orchestration model (normative): `../../assets/moqui-agent-orchestration.md`
- Architect PR gate: `../../agents/moqui-architect.md`
