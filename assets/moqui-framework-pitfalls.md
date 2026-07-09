# Moqui Framework Pitfalls

Framework behaviors that silently do the wrong thing or fail at runtime. None of these
produce an XML parse error or a compile warning, so they are easy to ship and hard to
diagnose after the fact. Check the relevant section before authoring screens, logic, or
status/seed changes; the static-detectable ones are also flagged by the audit script.

## Screens

### `condition` is ignored on `<container>` / `<container-box>`

`condition` is **not** a valid attribute on `<container>` or `<container-box>`. Per
`framework/xsd/xml-screen-3.xsd`, `condition` is only defined on `<section>`,
`<section-iterate>`, `<label>`, `<button-menu>`, `<container-dialog>`, `<dynamic-dialog>`,
and similar elements. A `<container condition="X">` parses fine but the attribute is
**silently dropped** — the container always renders.

- **Symptom:** a block that "should be hidden" renders anyway; a `${someNullVar}` inside it
  expands to the literal string `"null"`.
- **Fix:** wrap conditional multi-widget blocks in
  `<section name="MyName" condition="..."><widgets>…</widgets></section>`. For a single
  widget that already supports `@condition` (label, button-menu, …), put `condition`
  directly on that element.
- **Audit code:** `screen-container-condition` (warn).

### `<list-options>` `key`/`text` are expand strings, not field names

`<list-options list="X" key="Y" text="Z"/>` treats `key` and `text` as **expandable
strings**, not field references. `key="endpoint"` renders the literal word `endpoint` for
every option and submits that literal as the parameter value — the row's `endpoint` field
is never read. You must interpolate: `key="${endpoint}" text="${description}"`.

- **Symptom:** every dropdown option shows the same literal word; selecting any option
  submits that word instead of the row value, so the downstream call fails.
- **Fix:** `<list-options list="myList" key="${idField}" text="${labelField}"/>`.
- **Audit code:** `screen-list-options-literal` (warn).

## Services

### `ServiceJobRunLock` is not run history

`moqui.service.job.ServiceJobRunLock` holds one row per job with a bare
`lastRunTime` that the scheduler writes as a coordination lock (its own
description: "managed automatically by the service job runner"). Code that reads
it for monitoring runs fine and shows a timestamp — but has no duration, no
error flag, no error text, and misses ad-hoc runs' outcomes. The run-history
entity is `moqui.service.job.ServiceJobRun`: one record per execution with
`startTime`, `endTime`, `hasError`, `errors`, `messages`. The official docs are
explicit: "track execution of Jobs using moqui.service.job.ServiceJobRun
records."

- **Symptom:** a job dashboard or health check shows "last run" but never shows
  failures; errors are invisible until someone reads the log.
- **Fix:** query `ServiceJobRun` by `jobName`, `order-by="-startTime"`, limit 1
  (the `jobName` index makes this cheap). See `moqui-service-engine.md`.

## Logic (Groovy)

### `EntityList.findAll` / `find` / `filter` cast the closure result straight to `boolean`

An `EntityList` (what `<entity-find list="...">` returns) overrides `findAll`, `find`, and
`filter` to take a `Closure<Boolean>` and cast the closure's return value **directly to a
primitive `boolean`**. Groovy truthiness does **not** apply. So
`someEntityList.findAll{ it.orderId }` throws
`java.lang.ClassCastException: java.lang.String cannot be cast to java.lang.Boolean` at
runtime whenever the list is non-empty (surfaced via REST as HTTP 400).

- **Subtlety:** the cast only fires for **non-empty** lists, so an empty/not-found path can
  mask the bug (e.g. a real id 400s while a bogus id cleanly 404s).
- **Fix:** always return a real boolean from the closure: `find{ it.orderId != null }`.
- **Safe alternatives:** `.collect` / `.groupBy` / `.collectEntries` / `.each` are **not**
  overridden — they fall through to Groovy DGM and keep normal truthiness.
- **Diagnosis:** the stack trace names `EntityListImpl.findAll(...)` + `Error running
  groovy script`. Do not confuse this with `Error in condition [...]`, which comes from an
  `<econdition ignore="...">` expression and is a different problem.

## Status & seed data

### `statusId` updates are validated against `StatusFlowTransition`

Changing a status-bearing entity's `statusId` through the entity-auto `update#<Entity>`
service is **not** a plain field write. Moqui validates the change against
`moqui.basic.StatusFlowTransition`; a transition with no matching row fails with
`[400] Status change not allowed from <X> to <Y>`. This is enforced, not advisory.

- **Fix:** when you add a new status transition (a new `complete`/`receive`/etc. action),
  you must **both** (1) seed the `StatusFlowTransition` row and (2) actually load that seed
  into every DB that runs the code. The code change alone is insufficient.
- **Caching:** status-flow lookups are entity-cached, so a direct SQL insert will not take
  effect without a reload/restart. See `moqui-deployment-operations.md` for loading seed.

### New entity columns and new seed rows need an explicit apply step

On a typical dev setup with `entity_add_missing_startup=true` /
`entity_add_missing_runtime=false`:

- **New entity fields:** a **restart** auto-`ALTER`s tables to add the columns (logged by
  `EntityDbMeta` "Added column …"). A **running** server will not pick them up — you get
  `[400] Unknown column … in 'field list'` until you restart.
- **New seed/ext-seed rows** (enums, `StatusFlowTransition`, config records): a restart does
  **not** load data. You must run an explicit `load` (e.g. `load types=ext-seed`, or
  `load location=component://<comp>/data/<File>.xml` for one file) against the target DB,
  then restart. Loads are idempotent upserts.
- Order matters when both apply: stop the server (it holds the txlog lock), load seed, then
  relaunch so new-column ALTERs and new seed rows are both present.
