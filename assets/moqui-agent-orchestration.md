# Agent orchestration — manager + worker pool over GitHub Issues

Project-agnostic coordination model for autonomous build work by AI agents.
**GitHub Issues ARE the runtime** — no in-memory orchestrator, no bespoke queue.
Everything the system needs is either a native GitHub construct or, where none
exists, the smallest possible label.

Instantiate per project by declaring four values (in the project's own
`PROJECT.md` or CLAUDE.md):

| Config | Meaning |
|---|---|
| `«issue repo»` | where the pool's issues live |
| `«org»` | the GitHub org (or user) the watcher polls |
| `«owner»` | the pool owner: the one GitHub login whose assigned issues the pool executes (a machine user, or a designated member) |
| `«feature branch»` | the integration branch agent PRs merge into — never main/release |

**Two distinct identities — do not conflate them:**
- **Reporter/author** — whoever's session files the issue: whichever GitHub
  account is authenticated locally on that person's machine. Any team member
  can operate a Manager session, filing issues as themselves.
- **`«owner»`** — the pool owner. A per-team constant, not derived from who
  reports.

**Assignment is the explicit routing decision, made per issue, by whoever files it:**
- Assigned to `«owner»` → the pool picks it up and executes it.
- Assigned to anyone else (including the reporter) → a human-owned issue; the
  watcher ignores it. This is an ordinary path — not every issue needs the pool.

## State model

**Native GitHub constructs carry these facts — never duplicate them in a label:**

| Fact | Native home |
|---|---|
| First-touch role for an issue | the issue's **type** (Requirements / Design / Build / Defect / Verify) |
| Queue order among ready issues | the native **Priority** field |
| How much judgment the work needs | the native **Effort** field — this, not type alone, decides the model tier |
| A genuine deadline (rare) | the native **Target date** field |
| Dependencies | native issue-to-issue **blocked-by** relationships |
| PR open / reviewed / merged | the **linked PR**'s actual state and its review comments |
| Human viewing surface | a **GitHub Project** — a view over the above; defines no fields of its own |

**Stored as labels — only what GitHub cannot yet derive:**

| Label | Meaning |
|---|---|
| `status:ready` | claimable now |
| `status:claimed` + `worker:<id>` | in progress; the claim mutex |
| `status:blocked` | on hold |

That is the entire stored state. (GitHub's issue-search API does not yet filter
by native field *value*, only by label — the sole reason lifecycle stays
label-based; see Roadmap.)

## Issue-type → role routing

| Native issue type | First-touch role (this plugin's agents) | Produces |
|---|---|---|
| Requirements | business analyst | gap/overlap analysis → a Design issue |
| Design | `moqui-architect` | an approved design → Build issue(s) |
| Build | builder | a PR → architect gate → merge → QA gate |
| Defect | builder | same as Build; originates from an RCA or a QA REFUTE |
| Verify | QA technician | ad-hoc verification/audit not tied to a specific merge |

No type set (custom issue types are an org-wide GitHub setting; until they
exist, GitHub's default `Task` type stands in) → treat as Build. Genuine bugs
found by a gate use the `Defect` type.

## Roles (separated on purpose — the tester is not the fixer)

- **MANAGER** — the main session, the human's conversational counterpart.
  Files + curates every issue (type, Priority when genuinely urgent, native
  blocked-by, assigned to `«owner»`), verifies outcomes. Never codes, never
  dispatches workers while the pool is on.
- **BUSINESS ANALYST / ARCHITECT / BUILDER / QA** — the role bench. Each claims
  one issue, works in its own git worktree/branch, and hands off through the
  issue/PR. Builders never test/certify; the architect never merges; QA never
  fixes.

## Lifecycle

```
manager files (type, blocked-by, Priority, assign «owner») → status:ready
   ──claim (+worker)──► status:claimed ──PR w/ "Closes #N"──► [PR open, derived]
   ──architect review──► [PR approved, derived] ──merge (merge-lock)──► [PR merged, derived]
        ↘ CHANGES-REQUESTED → builder fixes the SAME PR branch, posts FINDINGS RESPONSE, pushes
   [PR merged, issue still open] ──QA merge gate (suite run + non-hollow checks)──► verdict
        VERIFIED → issue CLOSED (native)      REFUTED → status:ready (+ RCA) for a fix cycle
   closing an issue → its native blocked-by dependents become claimable
   stale claim (no PR within the TTL) → reverted to status:ready
```

## Claim protocol (GitHub Issues has no atomic compare-and-set on labels)

1. List `assignee:«owner» label:status:ready`, excluding `status:blocked`,
   within the WIP limit; order by Priority, then oldest.
2. Add `status:claimed` + `worker:<id>`, remove `status:ready`.
3. Re-read: if two `worker:*` labels appear, lowest worker-id wins; the loser
   reverts and retries.
4. Stale reclaim: `status:claimed` with no PR within the TTL reverts to
   `status:ready`.

*Zero-race upgrade, if ever needed:* an atomic lock file via the GitHub
Contents API with an expected blob SHA — a true compare-and-set; one writer
wins, the rest get 409.

## Coordination rules

- **WIP limit** ≤ 3 issues claimed/in-review at once — the top lever on cost
  and conflicts.
- **Dependencies** — native blocked-by; a worker skips an issue whose blockers
  aren't closed.
- **Serialized merge** — one builder merges at a time (merge-lock); rebase and
  resolve first.

## Architect PR review (pre-merge gate)

Every PR is reviewed by the architect (this plugin's `moqui-architect` agent)
before merge:

- Scope: conformance to the approved design; native-first / reads-true (no
  reinvented facilities, no dead code, docs match behavior); the change stays
  within the issue's scope; citations anchor in framework/suite/project-other
  code, never only the diff under review. Not behavior testing — that is the
  QA gate's job.
- Verdict: a structured PR comment (`ARCHITECT REVIEW: APPROVED` /
  `CHANGES-REQUESTED` + a findings table). The merge proceeds only once the
  newest such comment postdates the PR's last push.
- A re-review after a fix verdicts every prior finding explicitly
  (RESOLVED / UNRESOLVED against the builder's FINDINGS RESPONSE ledger)
  before approving.
- The architect is read-only: it never merges, never pushes fixes.

Why a comment convention instead of GitHub's native PR approval: when all
agents share one GitHub login, GitHub forbids self-approval. With a second
account in the pool, switch to native reviews (see Roadmap).

## QA merge gate (post-merge, pre-verify)

On a merged PR, the QA technician is the one role allowed to run the project's
exclusive test suite — one claim in flight at a time gives a shared DB/runtime
the exclusivity it needs. It first confirms an `ARCHITECT REVIEW: APPROVED`
comment predates the merge (a process-violation verdict if not, independent of
test results), then updates to the merged tip, runs the suite, and applies
non-hollow checks: **counts must match expectations exactly — a green-but-
shrunk suite is REFUTED, not VERIFIED.** Verdict: `QA GATE: VERIFIED` (close
the issue) or `QA GATE: REFUTED` (RCA comment, back to `status:ready` for a
fix cycle).

## Guardrails

- Serialized mutation (merge-lock); one runtime for suite runs; fan-out is
  non-mutating.
- **Hard stops (never without explicit human ok):** merging `«feature branch»`
  into main/release; deploying; writing to any external system; destructive
  operations. A PR based on `main`/`master`/`release-*` is refused at three
  independent layers: a builder won't open one without asking, the architect
  auto-`CHANGES-REQUESTS` it, and the merge-step builder verifies the base
  before merging.
- **Honesty:** any role's "done" is a lead, not proof — the next gate down
  confirms before advancing.

## Execution model

**Pool (the standard):** work passes agent-to-agent through GitHub Issues; the
manager files and verifies but does not call workers. A persistent **watcher
session** polls and spawns role workers:

- **Scope:** every repo in `«org»`, one search:
  `gh search issues --owner=«org» --assignee=«owner» --state=open --label=status:ready`.
  `status:ready` + assigned to `«owner»` is the universal go signal.
- **Routing:** native issue type → role (table above). No type → builder.
- **Model tier:** derived per issue from (role, issue type, native Effort).
  Principle: pay for judgment (architect review, QA verification, ambiguous
  requirements), economize on retrieval and mechanical edits. Effort is the
  manager's one lever for an exception — set the native field; never invent a
  body-line convention.
- **Watcher mechanics:** one persistent session on a cheap model, polling
  every ~4–5 minutes. It re-reads its own prompt file every poll (protocol
  changes must reach a live watcher). Does no issue work itself; spawns a
  worker on the derived model, enforces the WIP limit, resumes watching.
- **The manager under the pool:** files and curates, verifies QA gate
  outcomes, handles escalations. Does not dispatch workers or work issues
  while the pool runs.

**Direct dispatch (fallback):** the manager dispatches role agents directly.
Use when the pool isn't running, for ad-hoc interactive work, or for
non-mutating research/verification fan-outs that never touch an issue.

## Roadmap

1. The day a second human account joins the pool: architect verdicts move to
   native PR reviews, and branch protection (require one approval, no
   self-merge) becomes enforceable.
2. The day GitHub's search API filters by native issue-field value:
   `status:ready`/`claimed`/`blocked` collapse into a native single-select
   Status field, and stored state drops to just the claim tag.
