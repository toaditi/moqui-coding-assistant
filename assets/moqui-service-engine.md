# Moqui Service Engine Reference

What the service engine already provides. Check here before hand-writing
scheduling, locking, monitoring, validation, or create-or-update logic — most of
it is a framework facility. Every claim carries a citation to framework source
(verified against moqui-framework v3.5.2) or an official docs page.

Official docs (Logic and Services section):

- [Service Definition](https://www.moqui.org/m/docs/framework/Logic+and+Services/Service+Definition)
- [Service Implementation](https://www.moqui.org/m/docs/framework/Logic+and+Services/Service+Implementation)
- [Calling Services](https://www.moqui.org/m/docs/framework/Logic+and+Services/Calling+Services)
- [Service Jobs](https://www.moqui.org/m/docs/framework/Logic+and+Services/Service+Jobs)
- [Service ECA Rules](https://www.moqui.org/m/docs/framework/Logic+and+Services/Service+ECA+Rules)

## Service jobs — the entity map

Four entities, all in `framework/entity/ServiceEntities.xml`. Knowing which is
which prevents the classic mistake: monitoring against the scheduler's lock
record instead of the run history.

| Entity | Purpose | Key fields | Source |
|---|---|---|---|
| `ServiceJob` | Configuration | `jobName` (PK), `serviceName`, `cronExpression`, `paused`, `topic`, `expireLockTime`, `minRetryTime` | ServiceEntities.xml:32 |
| `ServiceJobParameter` | Name/value params passed to the service each run | `jobName` + `parameterName` (PK), `parameterValue` | ServiceEntities.xml:71 |
| `ServiceJobRun` | **One record per execution — the monitoring entity** | `jobRunId` (PK), `jobName`, `startTime`, `endTime`, `hasError`, `errors`, `messages`, `results`, `hostName`, `runThread` | ServiceEntities.xml:96 |
| `ServiceJobRunLock` | Scheduler coordination lock — **not monitoring** | `jobName` (PK), `jobRunId` (currently running instance), `lastRunTime` | ServiceEntities.xml:114 |

The official docs state it directly: "User can track execution of Jobs using
moqui.service.job.ServiceJobRun records"
([Service Jobs](https://www.moqui.org/m/docs/framework/Logic+and+Services/Service+Jobs)).
`ServiceJobRunLock`'s own description reads "Runtime data for a scheduled
ServiceJob... managed automatically by the service job runner" — it exists so
the scheduler can coordinate and recover stuck jobs, not for dashboards.

**Monitoring query pattern** — latest run for a job:

```xml
<entity-find entity-name="moqui.service.job.ServiceJobRun" list="jobRuns">
    <econdition field-name="jobName" value="my_job_name"/>
    <order-by field-name="-startTime"/>
    <limit>1</limit>
</entity-find>
```

`jobName` is indexed (`SVC_JOBRUN_NAME`, ServiceEntities.xml:112), so this is a
cheap read. Old runs are pruned by the stock `clean_ServiceJobRun_daily` job
(default 30-day retention).

**Ad-hoc run from code** — the `ServiceCallJob` interface; returns the
`jobRunId` of the created `ServiceJobRun`:

```groovy
ec.service.job("MyJobName").parameters(context).run()
```

Service jobs always run asynchronously. If `ServiceJob.topic` is set, a
notification is sent to the current user and every `ServiceJobUser`, with the
service results as the `NotificationMessage.message`
([Calling Services](https://www.moqui.org/m/docs/framework/Logic+and+Services/Calling+Services)).

## Calling services — the `ec.service` DSL

Options beyond plain `sync()` / `async()` that are commonly reimplemented by
hand ([Calling Services](https://www.moqui.org/m/docs/framework/Logic+and+Services/Calling+Services)):

- `requireNewTransaction(true)` — suspend the active transaction and begin a
  new one for the scope of this call. Equivalent to `transaction="force-new"`
  on a `<service-call>` action.
- `disableAuthz()` — disable authorization for the current thread during this
  call.
- `special().registerOnCommit()` / `special().registerOnRollback()` — register
  the service to run when the current transaction commits or rolls back. This
  interface has no `call()`; registration is the action. Use this instead of a
  hand-rolled "after commit" flag.
- `async().callFuture()` — returns a `java.util.concurrent.Future` for the
  results; the async alternative to fire-and-forget.
- `distribute(true)` — the call may run on another cluster member; all
  parameter entries must be `java.io.Serializable`.
- `multi(true)` — one map carries multiple parameter rows using `_${row}`
  suffixes (e.g. `userId_8`).

## Entity-auto services — what the engine does for you

From [Service Implementation](https://www.moqui.org/m/docs/framework/Logic+and+Services/Service+Implementation).
Verbs: `create`, `update`, `delete`, `store`. Any `${verb}#${EntityName}` call
works implicitly — no service definition needed.

- `store` = create if the record does not exist, update if it does
  (idempotent create-or-update).
- `create` with a missing sequenced primary key auto-generates it and returns
  it as an out-parameter.
- 2-part primary key: the secondary sequenced ID is auto-generated when the
  primary is given and the secondary is missing.
- A `fromDate` primary-key field not passed in is auto-set to the now
  timestamp.
- `update` on an entity with `statusId`: the engine returns `oldStatusId`
  (the prior DB value) and a boolean `statusChanged` automatically — never
  hand-write this comparison.
- Status transitions are validated against `moqui.basic.StatusFlowTransition`;
  no matching row = error. (See `moqui-framework-pitfalls.md` — the seed row
  must also be loaded into every target DB.)

Caveat: `store#`/`update#` null-clobber fields absent from the in-map when the
caller passes them as null/empty. To preserve create-only fields
(`createdDate`, `createdByUserId`), a hand-written create-vs-update branch is a
legitimate reason not to use `store#`.

## Single-instance execution — the `semaphore` attribute

For long-running or scheduled services, the service definition itself can
enforce "only one instance runs against a given database"
([Service Definition](https://www.moqui.org/m/docs/framework/Logic+and+Services/Service+Definition)).
Never hand-roll a lock table or an "isRunning" flag when this covers it.

- `semaphore="none|fail|wait"` — `none` (default), `fail` (error immediately
  if another instance holds the semaphore), `wait` (block until free).
- `semaphore-timeout` — how long `wait` blocks before timing out. Default 120s.
- `semaphore-sleep` — polling interval while waiting. Default 5s.
- `semaphore-ignore` — ignore semaphores older than this (crash recovery).
  Default 3600s.

## Parameter validation — declared, not hand-written

Validation sub-elements on `<parameter>`
([Service Definition](https://www.moqui.org/m/docs/framework/Logic+and+Services/Service+Definition)):
`matches` (regexp), `number-range`, `number-integer`, `number-decimal`,
`text-length`, `text-email`, `text-url`, `text-letters`, `text-digits`,
`time-range`, `credit-card` — combined with `val-or`/`val-and`/`val-not`.

Two facts that make declared validation strictly better than inline checks:

- XML Form fields based on the parameter get client-side JavaScript validation
  free for `required`, `matches`, `number-integer`, `number-decimal`,
  `text-email`, `text-url`, `text-digits`.
- `allow-html` on String parameters is a security contract: `none` (default,
  HTML rejected), `safe` (antisamy-filtered), `any` (unchecked — must be
  justified). Widening it silently is an exposure change.
