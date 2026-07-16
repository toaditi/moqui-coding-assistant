# Pipeline Health Runbook — agent-team pool

How to tell the pool is actually working, what to do when it isn't, and when a human gets paged.
The failure modes below were hit for real on a live board, not invented.

## What "healthy" looks like

- Every `status:ready` issue assigned to `«owner»` gets claimed within a few poll cycles (~5–15 min).
- Every merged PR carries an `ARCHITECT REVIEW: APPROVED` comment that predates the merge commit —
  no exceptions, no silent skips.
- No issue sits `status:claimed` with no PR opened for longer than the claim TTL (default 2h).
- No issue bounces `claimed → ready` more than twice in a row.
- A closed issue carries a `QA GATE: VERIFIED` comment and no leftover in-flight label
  (`status:claimed` + `worker:*` must be gone at close).
- `status:blocked` issues are either genuinely blocked on a dependency, or explicitly staged by a
  human with a comment saying so — never silently stuck with no explanation.

If any of these is false, the pipeline is unhealthy even if the watcher window looks like it's
running — silence and stalled progress look identical from a distance.

## How to check (the manager runs this — on demand, or periodically)

```bash
gh search issues --owner=«org» --assignee=«owner» --state=open --json repository,number,title,labels,updatedAt --limit 30
date -u +"%Y-%m-%dT%H:%M:%SZ"
```
Read every `status:ready` result's `updatedAt`, not just the newest overall — a healthy pool can be
actively working one issue while a DIFFERENT ready issue sits ignored because the watcher is stale
on routing for that issue's type. Compare each `status:ready` issue's age against now; anything
over ~20 minutes idle is a candidate incident, not just the org-wide max.

For gate integrity, spot-check a recently merged PR:
```bash
gh pr view <n> --repo «org»/<repo> --json comments,mergedAt --jq '{merged: .mergedAt, reviewed: [.comments[] | select(.body|startswith("ARCHITECT REVIEW"))] | length}'
```
`reviewed: 0` on a merged PR is a process violation, independent of whether the code is fine.

For a closed issue, check no in-flight label was left behind:
```bash
gh issue view <n> --repo «org»/<repo> --json state,labels --jq '{state, labels:[.labels[].name]}'
```

## Failure modes

| Symptom | Likely cause | Fix | Notify? |
|---|---|---|---|
| A specific `status:ready` issue sits idle while others move | Watcher is stale on routing for that issue's native TYPE (e.g. Design routes to an agent the watcher's cached protocol doesn't know about yet) | Tell the watcher directly to re-read its prompt file now; if repeated, the "re-read every poll" instruction itself has regressed | **Yes** |
| Board silent org-wide with `status:ready` work pending | Watcher session died or was never relaunched (machine sleep, closed window) | Relaunch: open a session at the workspace root, set a cheap model, run the watcher's launch line (`moqui-pool-watcher-prompt.md`) | **Yes** — nothing moves until a human acts |
| Watcher window shows repeated permission prompts, no spawns succeeding | Tool-permission settings regressed on that machine (spawn/agent tools no longer allowed) | Restore the machine's permission mode / allow-list for agent spawning | **Yes** — blocks all execution |
| An issue's labels look empty/inconsistent for a moment | Normal claim-race transition (two label writes, not atomic) | None — should self-resolve within one poll. If it doesn't clear in a few minutes, treat as stuck | Only if stuck |
| Issue `status:claimed`, no PR, past the TTL | Worker died mid-task or never actually started | Manager reverts it to `status:ready` (the watcher reports these, it does not reclaim itself by design) | No — routine, log only |
| Same issue bounces `claimed → ready` 3+ times | Something about the issue itself is unworkable (bad instructions, missing prerequisite) | Read the issue, fix the ambiguity or its blocker, don't just keep letting it re-claim | **Yes** |
| A closed issue still carries an in-flight label (`status:claimed`) | Whoever closed it didn't relabel before/at close | Manually correct the label; check whether the same worker pattern recurs | No, unless it recurs across many issues |
| A merged PR has zero `ARCHITECT REVIEW` comments predating the merge | **Confirmed root cause (live incident, 2026-07): an out-of-band direct merge (human GitHub-UI click or an out-of-protocol `gh pr merge`) raced ahead of an architect review dispatch already in flight.** Not a routing bug — the board never saw the merge transition, so no agent merge-step ran at all. Nothing on the repo technically *prevents* this; the gate is a convention agents follow, not something GitHub enforces | Apply branch protection requiring an approving review before merge on any repo running this pool — that closes the gap structurally instead of relying on discipline (see below) | **Yes** — treat as urgent until branch protection is on |
| A genuinely blocked prerequisite needs a human action (e.g. an org-admin setting) | By design — some things can't be agent-done | Worker/watcher comments what's needed and stops; a human does the one step | **Yes** |

## Branch protection (structural fix for the merge-race failure mode)

The architect gate is enforced only by every agent following its prompt — nothing stops a direct
merge (human or a mis-sequenced dispatch) from bypassing it entirely, and the only trace left
behind is a review comment that arrives late or never. The structural fix is repo-level, not
prompt-level: require an approving review before merge (branch protection), so an unreviewed merge
becomes impossible rather than merely off-protocol.

**Known trade-off while all agents share ONE GitHub identity:** GitHub forbids self-approval, so
requiring an approval would make merges physically impossible until a human personally clicks
Approve on each PR — trading "convention can be silently bypassed" for "the pipeline stalls on the
manual bottleneck you just automated." Apply branch protection the day a second account (human or
machine) joins the pool — at that point a real approval becomes obtainable without a human doing it
every time. Until then, the gate-integrity spot-check above (which screams after the fact) is the
interim backstop.

## Notification policy

Push-notification-worthy: watcher down, permission/auth failures blocking all execution, a bouncing
issue, a missing-review process violation, a genuine human-only blocker. Routine self-healing
(claim races, ordinary stale-claim reverts) is log-only — paging a human for something the system
already fixed itself is noise, and noise trains people to ignore the channel.

## Who runs this

The manager, ambiently via its own board monitoring and explicitly whenever asked "is the pool
healthy." This is verification, not role work — it doesn't require dispatching anyone.
