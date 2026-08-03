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

## Entities

### `entity-find-one` is a primary-key lookup, not a generic single-record shortcut

`<entity-find-one>` (and `EntityFind.one()` in Groovy for a full-PK condition set) is
documented as "does a find by primary key." Every real usage in the framework's own
services (`moqui.basic.Geo` by `geoId`, `moqui.basic.Uom` by `uomId`, `WikiPageAlias` by its
actual composite PK `wikiSpaceId`+`aliasPath`) targets the entity's *declared* PK fields —
never a non-PK field combination. Using it for a lookup by non-PK fields (e.g. an entity whose
real PK is `parentId`+`childId`, but you're querying by `parentId`+`externalRefId`) diverges
from the tag's documented contract and every precedent in the framework.

- **Fix:** for a non-PK condition, use a plain `<entity-find list="...">` (list-based) and
  take the first result, or a Groovy `ec.entity.find(...).condition(...).list()`. Reserve
  `entity-find-one` strictly for genuine PK lookups.
- **Check before converting:** compare the field names in the condition against the
  entity's `is-pk="true"` fields in its definition — don't assume a lookup is PK-based just
  because it returns "one" record in practice.

### `EntityFind.one()` does **not** throw on multiple matching rows

Unlike JPA's `getSingleResult()` (which throws `NonUniqueResultException`), Moqui's
`.one()` (see `EntityFindImpl.oneExtended`) simply takes the **first row** of the result set
and, at most, emits a `trace`-level log line if a second row exists — never an error, never
a warning. Do not assume `.one()` gives you a fail-fast guarantee against duplicate/
ambiguous data; it silently picks one row and moves on.

- **Symptom:** a lookup you expected to "prove" a row is unique (or fail loudly if it isn't)
  passes quietly even when two rows match, with no log above trace level.
- **Fix:** if uniqueness genuinely matters, check it explicitly (e.g. `.list().size() > 1`
  guard) rather than relying on `.one()` to catch it. When converting a `.one()` call to a
  native `<entity-find-one>` or list-based `<entity-find>`, know that "take the first row" is
  the real, faithful semantics to preserve — not "error if not unique."

### `EntityList.getFirst()` is the safe way to take the first result — not `.first()` or `list[0]`

An `EntityList` (what `<entity-find list="...">` / `.list()` return) declares its **own**
`getFirst()` that returns **null** on an empty list — it never throws. This is *not* the
same as Groovy's generic `DefaultGroovyMethods.first()` (throws `NoSuchElementException` on
empty) or plain `list[0]` indexing (throws `IndexOutOfBoundsException` on empty), and it
takes precedence over any JDK `SequencedCollection.getFirst()` default because it's a
class-declared override.

- **Fix:** `someEntityList.getFirst()?.someField` instead of a truthy-guard-then-`[0]`
  dance, or a generic `.first()` that requires its own try/catch.

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

### Catching `ec.message.hasError()` does not undo a transaction already marked rollback-only

A nested service call (an entity-auto `create#`/`update#` service, or any custom service) that
throws — e.g. from a real SQL error, not a graceful `<return error="true">` — runs inside the
*caller's own transaction* by default (`transaction` unset = use-or-begin). The service
engine catches the throw, rolls back, and marks that transaction rollback-only. Your
Groovy/XML catching `ec.message.hasError()` afterward and calling `ec.message.clearErrors()`
only clears the **message facade** — it does *nothing* to the JTA rollback-only flag. Every
subsequent write in that same transaction (including unrelated work later in the same
script) will then fail with something like "transaction not in operable status (Marked
Rollback-Only)."

- **Symptom:** one nested-service failure (e.g. a too-long description hitting a column
  limit) cascades into an unrelated, later, seemingly-unconnected failure further down the
  same script — very confusing to debug, since the *reported* error is the second, unrelated
  one.
- **Fix:** if a nested service call's failure must not be allowed to poison the rest of the
  calling transaction's work, isolate it: `transaction="force-new"` on the *service
  definition*, or `.requireNewTransaction(true)` on the `ServiceCallSync` builder from
  Groovy/inline script (`ec.service.sync().name(...).requireNewTransaction(true)...call()`).
  Both use the same suspend-current/begin-new/rollback-only-scoped-to-the-new-tx mechanism
  (`ServiceCallSyncImpl`) — verify by tracing `sd.txForceNew`/`requireNewTransaction` in that
  class if in doubt, don't assume from the attribute name alone.
- **Only found by running it**: this class of bug does not show up from reading the code —
  it requires actually triggering the nested failure against a real transactional datasource
  (a live test run, not a mocked/unit-style test) to observe the cascade.

### `component://` URIs resolve by the *registered* component name, not the directory name

The `name` attribute in a component's `component.xml` is what `component://<name>/...`
resolves against — and it is not guaranteed to match the directory the component lives in
(a directory can be renamed across a repo's history while `component.xml`'s `name` stays
the same, or vice versa). A `<script location="component://my-directory-name/...">` built
from the folder name alone can silently fail to resolve, or resolve to the wrong component.

- **Fix:** always read the target component's `component.xml` `name` attribute directly
  before writing a new `component://` reference (script location, template location,
  dbresource path) — don't infer it from the directory name, even when they usually match.
  If the component already has *other* `component://` self-references (e.g. its own FTL
  templates), grep for one and match its prefix instead of guessing fresh.

### Description/comment/log-message fields have a real column length limit

A field typed `text-medium` (or similar) maps to a real, finite database column
(`VARCHAR(255)` in at least one observed MySQL schema) — not an unbounded text blob. Task
descriptions, comment/note fields, and similar columns built by interpolating raw
identifiers (long external-system reference ids/URIs, verbose multi-clause sentences) can
silently exceed the real limit and fail with `EntitySqlException: ... text value too long` /
`Data truncation: Data too long for column '...'` at write time — a failure that, per the
pitfall above, can also cascade into rollback-only poisoning of the whole transaction if the
write isn't isolated.

- **Fix:** resolve identifiers to their short/internal form before interpolating into a
  stored message, and keep generated description/comment text concise. When in doubt, check
  the field's actual entity-definition type and the target database's real column width —
  don't assume "it's text, it'll fit."

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

## Testing (Spock)

### A selective/differential filter test needs both an included AND an excluded case

A test that only sets up ONE scenario (e.g. one record with the value the filter should
reject) and asserts it was skipped cannot tell "the filter correctly excluded this" apart
from "the filter — or the whole batch — excludes/skips everything, silently." A completely
broken implementation (always-skip, always-fail-silently) can pass a one-sided test just as
easily as a correct one.

- **Fix:** in the same test run, include a second, genuine case that *should* pass the
  filter/guard, and assert both outcomes — the excluded case stayed excluded, and the
  included case was actually processed. This applies to any guard/filter test.
- **Also watch quantity/ordering traps**: a test proving "unit X must never be selected"
  needs the *selection loop's own math* to actually reach unit X under the buggy behavior —
  e.g. if the loop stops once it has satisfied a desired count, and the excluded unit sits
  *after* enough genuinely-eligible units to satisfy that count, the test passes regardless
  of whether the exclusion logic works. Put the excluded unit where the buggy path would
  reach it first (or size the desired count so the loop must consider it).

### In a long-lived, shared Spock spec, grep the WHOLE file for chosen test IDs before finalizing

When cleanup only runs once at the very end of a spec file (`cleanupSpec()`), not after each
individual test (`cleanup()` resets shared fixtures only), every test's fixture rows sit in
the database for the whole run. Picking an id (an order id, a mock response id, etc.) that
happens to collide with a *different, untouched, previously-passing* test later in the file
causes a duplicate-primary-key SQL error — collateral damage to a test that was never
touched, and confusing to debug since the failure looks unrelated to your change.

- **Fix:** before finalizing any new/modified test's ids, grep the entire spec file for
  every declaration of that id pattern, not just the tests near your edit — ids picked in
  isolation across a long editing session are exactly how this collision gets introduced.

### Raw brace/paren character counting is not a syntax check — compile instead

Counting `{`/`}` or `(`/`)` characters across a Groovy file to sanity-check an edit is
unreliable: natural-language comments (`"(the loop marker, must be excluded)"`, a stray
unmatched parenthesis in prose) throw the count off with no bearing on real syntax validity.
A large apparent mismatch can be pure comment noise; a real error can hide inside a count
that happens to balance.

- **Fix:** run the actual compile task for the module (e.g.
  `./gradlew :path:to:module:compileTestGroovy` for a test source set) — it needs no runtime/
  database setup, only the module's classpath, and gives a definitive yes/no on syntax
  validity instead of a noisy character tally.

### Verify a "we already fixed this" comment against the general/shared seed data, not just "a file exists somewhere"

A comment claiming a magic string was already replaced with "a real, pre-existing value"
can be wrong even when a file defining that value genuinely exists in the repo — if that
file is a *client/tenant-specific* seed data file, not the shared/general seed data every
environment loads. A value that "works" in one person's local database (because they happen
to have that tenant's data loaded too) is not portable.

- **Fix:** when verifying an enum/type id is real, confirm it's defined in the *general*
  seed data path the component actually depends on — not just anywhere in the monorepo.
  Cross-check by tracing which data files the specific test/component setup actually loads.

### Live-test verification catches what careful code review alone misses

Several real bugs in a large review pass (a transaction rollback-only cascade, a wrong
assumption baked into a new test's setup, an unseeded/tenant-specific enum) were only caught
by actually running the test suite against a live database — not by re-reading the code,
however carefully, multiple times. Manual/agent code review is necessary but not sufficient
for anything touching transactions, real data constraints, or service call chains; budget
for an actual run before calling a change verified.
