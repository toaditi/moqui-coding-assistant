# Proposal: Service Engine Knowledge for the moqui-service Skill

**Date:** 2026-07-09
**Author:** Anil Patel
**Status:** Proposed

## The Motivating Bug

The `moqui-architect` agent reviewed a dashboard design that needed "last run time"
for a ServiceJob. The agent correctly found that `lastRunTime` is not on `ServiceJob`,
but then stopped at `ServiceJobRunLock` and recommended it for monitoring.

That is wrong. `ServiceJobRunLock` is a scheduler coordination lock. The correct
entity is `ServiceJobRun` — one record per execution, with `startTime`, `endTime`,
`hasError`, and `errors`. The official Moqui docs say it directly:

> "User can track execution of Jobs using moqui.service.job.ServiceJobRun records."
> — https://www.moqui.org/m/docs/framework/Logic+and+Services/Service+Jobs

The agent made this mistake because nothing in the plugin describes the service
engine's entities and runtime behaviors. The skill says *what to do* (procedure,
guardrails) but no asset says *what the engine provides*.

## Audit: moqui-service Skill vs Official Docs

We audited the skill and its assets against the five pages in the
"Logic and Services" section of moqui.org. Six gaps:

| # | Gap | Source |
|---|---|---|
| 1 | Service Jobs entities (`ServiceJob`, `ServiceJobParameter`, `ServiceJobRun`, `ServiceJobRunLock`) — not mentioned anywhere in the plugin | [Service Jobs](https://www.moqui.org/m/docs/framework/Logic+and+Services/Service+Jobs) |
| 2 | `semaphore` attribute (`none`/`fail`/`wait`) — the native single-instance lock for long-running services | [Service Definition](https://www.moqui.org/m/docs/framework/Logic+and+Services/Service+Definition) |
| 3 | Parameter validation sub-elements (`matches`, `number-range`, `text-length`, `text-email`, etc.) and the security-relevant `allow-html` attribute | [Service Definition](https://www.moqui.org/m/docs/framework/Logic+and+Services/Service+Definition) |
| 4 | The full `ec.service` calling API — `requireNewTransaction`, `disableAuthz`, `special().registerOnCommit()/registerOnRollback()`, `callFuture()`, `distribute()` | [Calling Services](https://www.moqui.org/m/docs/framework/Logic+and+Services/Calling+Services) |
| 5 | SECA `when` phases and context variables (`parameters` before, `results` after), `run-on-error` | [Service ECA Rules](https://www.moqui.org/m/docs/framework/Logic+and+Services/Service+ECA+Rules) |
| 6 | Entity-auto automatic behaviors — `store` semantics, sequenced ID generation, `fromDate` auto-set, `oldStatusId`/`statusChanged`, `StatusFlowTransition` enforcement | [Service Implementation](https://www.moqui.org/m/docs/framework/Logic+and+Services/Service+Implementation) |

The consequence of each gap is the same: builders hand-write code the engine
already provides (locking, validation, create-or-update logic), and reviewers
cannot catch it because the reference does not exist.

## The Balance Rule: Skill vs Asset

The plugin's current division of labor is sound. Keep it, and make it explicit:

- A fact needed by **more than one skill or agent** → **asset**.
- An **imperative applied at edit time** → **skill** (one line, pointing at the asset).
- Anything moqui.org states → **docs map pointer**; an asset carries only the
  summary agents need offline, with the citation.

The skill stays thin. The knowledge goes in one new asset. The docs map gets the
missing pointers.

## Proposed Changes

### 1. New asset: `assets/moqui-service-engine.md`

The "what the engine gives you" reference. Every claim cited to a framework
file:line or a moqui.org URL. Sections:

**Job entity map**

| Entity | Purpose | Key fields |
|---|---|---|
| `ServiceJob` | Configuration | `jobName`, `serviceName`, `cronExpression`, `paused`, `topic` |
| `ServiceJobParameter` | Params passed to the service on each run | `parameterName`, `parameterValue` |
| `ServiceJobRun` | **One record per execution — the monitoring entity** | `startTime`, `endTime`, `hasError`, `errors`, `messages`, `results` |
| `ServiceJobRunLock` | Scheduler coordination lock — **not monitoring** | `jobRunId` (currently running instance), `lastRunTime` |

Monitoring query pattern (latest run):

```xml
<entity-find entity-name="moqui.service.job.ServiceJobRun" list="jobRuns" limit="1">
    <econdition field-name="jobName" value="my_job_name"/>
    <order-by field-name="-startTime"/>
</entity-find>
```

Ad-hoc run from code — returns the `jobRunId`:

```groovy
ec.service.job("MyJobName").parameters(context).run()
```

**Calling API options** (`ec.service`)

- `sync()` / `async()` / `callFuture()` — execution modes
- `requireNewTransaction(true)` — suspend current TX, begin a new one for this call
- `disableAuthz()` — skip authorization for this call
- `special().registerOnCommit()` / `registerOnRollback()` — run a service when the
  current TX commits or rolls back
- `distribute(true)` — may run on another cluster node; params must be Serializable

**Entity-auto automatic behaviors**

- `store` verb = create if absent, update if present (idempotent)
- Missing sequenced PK is auto-generated and returned as an out-parameter
- 2-part PK: secondary sequenced ID auto-generated when primary is given
- `fromDate` PK field auto-set to now when not passed
- `statusId` change: `oldStatusId` and `statusChanged` returned automatically
- Status transitions validated against `moqui.basic.StatusFlowTransition` — no
  matching row = error (already in pitfalls; cross-reference)

**Service concurrency: `semaphore`**

- `semaphore="none|fail|wait"` on the service definition — DB-backed lock so only
  one instance runs against a given database
- `semaphore-timeout` (default 120s), `semaphore-sleep` (5s), `semaphore-ignore` (3600s)
- Guardrail: never hand-roll a locking table or flag when this attribute covers it

### 2. Edit `skills/moqui-service/SKILL.md` (three small changes)

- **Procedure**: add a step — "Decide the execution mode before implementing:
  sync, async, or scheduled ServiceJob. For scheduled work, define a `ServiceJob`
  record — do not build custom scheduling."
- **Contract review list** (step 5): add `semaphore`, parameter validations,
  `allow-html`.
- **Guardrails**: add three —
  - Do not hand-roll concurrency locks; use the `semaphore` attribute.
  - Do not hand-write input validation the parameter validators cover.
  - Job monitoring reads `ServiceJobRun`, never `ServiceJobRunLock`.
- **References**: add the new asset.

### 3. Edit `assets/moqui-framework-pitfalls.md` (one new entry)

Under a new "Services" section:

> **`ServiceJobRunLock` is not run history.** It holds one row per job with a
> bare `lastRunTime` the scheduler writes as a coordination lock. Code that reads
> it for monitoring runs fine and shows a timestamp — but has no duration, no
> error flag, no error text. Use `ServiceJobRun` (one record per execution:
> `startTime`, `endTime`, `hasError`, `errors`). Confirmed by the official docs:
> "track execution of Jobs using moqui.service.job.ServiceJobRun records."

### 4. Edit `assets/moqui-quality-checklist.md` (two lines)

- Under "Exposure and safety": user-facing String parameters have a deliberate
  `allow-html` setting (`none` is the default; `safe`/`any` must be justified).
- Under "Contracts and naming": scheduled or long-running services declare a
  `semaphore` policy.

### 5. Edit `assets/moqui-official-docs-map.md` (missing pointers)

The Services section lists only 4 of the 6 pages. Add:

- [Calling Services](https://www.moqui.org/m/docs/framework/Logic+and+Services/Calling+Services) —
  the `ec.service` DSL: sync/async/job, `requireNewTransaction`, `disableAuthz`,
  `special()` TX hooks, `distribute`.
- [Service Implementation](https://www.moqui.org/m/docs/framework/Logic+and+Services/Service+Implementation) —
  script/inline/java/entity-auto runners; entity-auto automatic behaviors.

And expand the Service Jobs entry with the doc's own sentence: "track execution
using ServiceJobRun records."

### 6. Edit `agents/moqui-architect.md`

Add `assets/moqui-service-engine.md` to the architect's reference list. The
architect made the motivating mistake; the fix must reach the reviewer, not just
the builder.

## Verification Evidence

All claims verified 2026-07-09 against:

- moqui.org official docs (five pages of Logic and Services section, live)
- `framework/entity/ServiceEntities.xml` in moqui-framework v3.5.2:
  - `ServiceJob` — line 32 (no run-history fields)
  - `ServiceJobRun` — line 96 (`startTime`, `endTime`, `hasError`, `errors`)
  - `ServiceJobRunLock` — line 114 (description: "Runtime data for a scheduled
    ServiceJob... managed automatically by the service job runner")

## Delivery

One PR to `toaditi/moqui-coding-assistant` with this doc plus the changes above.
The new asset is the bulk of the work; the skill/checklist/pitfalls/docs-map/agent
edits are each a few lines.
