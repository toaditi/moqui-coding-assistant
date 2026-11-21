# Moqui House Rules

Rules the sponsor has set in review, one line each with its reason. They are not
framework facts (those are in `moqui-framework-pitfalls.md`). They are how this
team writes Moqui code and designs. Each rule was a correction at least once,
and several were corrections more than once.

Read the part for your role before you write or review anything:

- Builder: **Code** and **Data files**. Run the self-check at the end before the PR.
- Architect: **Design**, and use **Code** and **Data files** as review criteria.
- QA Technician: **Test data and local servers**, and use the rest to judge a "done" claim.

A rule's id (C1, D3, T2) is stable. Fixtures and review findings cite it.

## Code

**C1. No comments in code.** No `<!-- -->` inside XML actions, no `//` or `/* */`
in Groovy or Java. Names, small steps and a decision visible where it is made say
it. A service or entity keeps its short `<description>`: that is the contract.
When you touch a file, add no comments and remove the ones the code already says.
Why: comments drift from the code and hide unclear code.

**C2. No boolean flags.** Do not compute `isNew`, `hasItems` or any boolean into
a variable in one step and test it in another. Do the work inside the branch
where the fact is known. Each decision point asks its own question with the data
in hand. This holds for contracts and tables too: no `created` or `waiting`
out-parameter, no "sent" or marker field when a recorded fact already says it.
Why: a flag separates the decision from the place it is made, and goes stale.

**C3. No alias variables.** Do not collect a value in a local variable and copy
it to the out-parameter at the end. Use the out-parameter from the start.

**C4. A variable says what it holds and where it came from.** Hold a state read
from the database under a name that says so. Do not spill a find into the
context with `out-map="context"`. Name a fact for the fact, not for what you do
with it.

**C5. Service logic is XML actions.** `entity-find`, `set`, `if`, `iterate`,
`service-call`. Put joining and filtering in a view-entity so the service stays a
few declarative steps. Before writing a loop with lookups, ask what one query
would return. No new files under `script/`. No `type="java"` class that only
wraps finds and service calls. No new closure inside an existing script: add a
service and call it. A real algorithm goes in a class under `src/` that the
actions call. A one-line `<script>` is fine.
Why: the team reads XML actions; a script hides the rules, and a loop in Groovy
usually means the query was not designed.

**C6. Service calls pass named parameters.** Never `in-map="true"` or
`in-map="context"`. List the values the callee declares.

**C7. A service only reads what it was given.** Never remove, overwrite or add
fields on the maps and lists passed in. Build a new map or list in the shape the
next service needs. Why: Moqui copies only the top level of service parameters,
so nested lists and maps are shared with the caller. An import service that
edits its input corrupts the caller's record, for example the row a file import
writes to its error file.

**C8. Parameters are declared one by one.** One `<parameter>` per known field,
each with its own `<description>`; never a prose list of field names inside one
description. A list parameter takes flat values and the actions build the nested
shape. A parameter that mirrors a remote API field carries the remote API's own
name. Fields that only one installation has go in one pass-through map that the
shared service never names. Children declared under a `type="List"` parameter
are not enforced, so the actions check what matters.

**C9. No `transaction` attribute by habit.** Write the service and the
service-call without it. The default is right in almost every case. Add
`transaction="force-new"` only for a failure you can show, and name it in the
pull request; the pitfalls file describes the one known case, a sub-call whose
failure must not mark the caller's transaction. `transaction="ignore"` needs the
sponsor's approval. For long work use `transaction-timeout`.

**C10. Lock a real row to make writers wait.** Use
`<entity-find-one ... for-update="true"/>` inside the service transaction.
`semaphore="wait"` with `semaphore-parameter` does not serialize calls that
start together. Test a lock with parallel calls, never one at a time.

**C11. Use the verbs the codebase already uses.** Count them before naming a
service: `grep -rhoE '<service verb="[a-zA-Z]+"' . | sort | uniq -c | sort -rn`.
A service that asks another system for data is `get#`. A service that makes a
row is `create#`. A one-time data fill is `migrate#<Noun>` in the component's
`MigrationServices.xml`. Never invent `record#`, `pull#` or `fill#`, and say
"update", never "patch". A job is named after its service verb.

**C12. Log messages follow one pattern.** `[Entity] [Context] - [Action]`, for
example `Order [ID: ${orderId}] - Validation failed for missing productId`. Every
dynamic value goes inside the context block as `[Key: ${value}]`. The text after
the dash stays the same on every occurrence; only a trailing error detail may be
appended. Use the right level and no `Error` or `Warning` prefix. Never log a
bare exception. Why: log tools group and count by message text.

**C13. One file is ordered by layer and calls one way.** Reads and record
writes first, then steps, then the services that orchestrate them. Each layer
calls only the ones above it. Two service files that call each other are a
defect.

**C14. Moqui has no tenant.** Never send or document `tenantId` in a login, an
API call or a data file.

**C15. Screens use Moqui widgets only.** Screens, `form-single`, `form-list`,
field widgets, containers, dialogs and transitions. No custom CSS or JavaScript,
no `<render-mode>` HTML block. Make it usable through layout, field order, help
text, defaults and drop-downs.

**C16. Three traps that fail without an error.**
- A script service whose last statement is a Map returns that Map as the whole
  result, and the out-parameters vanish. End with an explicit `return` of the
  out-parameters.
- `value ?: -1` turns a real `0` into `-1`, because 0 is false in Groovy. Check
  `containsKey` or `null` for numeric codes.
- A purpose or role filter on an association entity is ignored when the field is
  not on that entity. Read the entity definition first. A contact mechanism's
  purpose lives in a separate purpose entity, read through the view for that
  domain.

## Data files

**F1. A primary key written by hand is a readable id or a number below 100000.**
Prefer a text id in upper snake case that names the thing in full
(`STORE_CREDIT`, not `SC`), 20 characters or fewer. Moqui generates ids from
100000 up, so a hand-written value there can collide and reads as runtime data.
Every row carries its primary key: a row without one makes a new record on every
load.

**F2. Never rename an id a live system already holds.** Seed data does not move
existing rows; a rename makes a second record and splits the children. Check the
component's `upgrade/` files first. A row that mirrors a record production
already holds keeps production's id, even a generated one.

**F3. Upgrade steps travel with the change.** A commit that adds upgrade SQL,
upgrade data, a job, a configuration, authz rows, a new tool or a REST path also
adds `upgrade/UpcomingRelease/UpgradeSteps.md` in the same commit: what loads by
itself, each manual step, who can use it, and the check after deploy. Check
`git diff --cached --name-only` before every commit.

**F4. Jobs ship paused.** Every job a change adds or switches on is paused in
seed data and in upgrade data. A real-time data feed ships as manual pull. The
upgrade steps say when to unpause, after the old job is stopped.

**F5. Data goes in its own PR.** Products, mappings and their upgrade steps go in
a small PR of their own. The code branch assumes them and carries no duplicate
rows. Before inventing a mapping key, check whether the live system already has
one under another name.

## Design

**D1. List what exists before designing.** Name the existing entities, views,
services and jobs that touch the same facts, and the open pull requests for the
same need. Say for each why it is reused or not. A second record of a fact that
is already stored is a defect. Never wrap a service that already does the step.

**D2. A change to an entity goes in the component that defines it.** An index,
a field or a fix on a shared entity is a change to the shared component, on the
branch its users run. A client component's `extend-entity` hides a product fix
in one client.

**D3. No framework-internal entities in an application component.** Do not
define job, scheduler or runtime tables there, even to ship a data fix. Deliver
a one-time SQL runbook and a prevention change in the shared component.

**D4. Core components carry no dependency on one external system.** Every
entity, view, service, message type and document that exists because of how one
external system works lives in that system's connector, shaped for its
workflows. No external system's id as a field on a core entity. A client
component holds data: mapping rows, ids, schedules.

**D5. Keep logic in the external system to a minimum.** A script that runs
inside the external system sends its own record in its own terms, and the
connector maps it. An endpoint script takes what the application decided and
makes the record. It never reads state and decides.

**D6. Select by a business date, never by the audit stamp.** Window and filter
on a status date, a shipped date or an entry date. `lastUpdatedTxStamp` moves on
any unrelated update, so it does not mean a business event happened. Do not
design, index or tune for it. Report existing use as a gap.

**D7. A time-window reader overlaps and keeps history.** A record is stamped
when the code runs and committed later, so a job that reads "changed since the
last run" can pass it. Overlap the previous window and keep a per-row history so
a re-read is safe. Prefer a state-based due view to a time window.

**D8. Derive, do not store.** A value that can be computed from stored data is a
view-entity aggregate. Denormalize only when measured performance forces it.
`fromDate` and `thruDate` mean effective dating; a creation time is
`createdDate`.

**D9. Mapping keys are codes.** A mapping row's key is a code or an id, never a
sentence of display text from another system. Translate received text to an id
in the code that receives it, and store the id.

**D10. Contact mechanisms are immutable.** Never update a contact mechanism, a
postal address or a phone number in place. Expire the association and create a
new record with a new association.

**D11. New behaviour goes in new files while production runs the old path.** A
new service has a new name in a new file. The old service, data row and script
stay as they are. Removing the old path is its own task after the cutover. Design
the new path as the only path, not for running beside the old one.

**D12. A backport is the same code as the main line.** Same tables, services,
message types and job names. Design on the main line first. List what the
upgrade must carry over: rows, bookmarks, queued messages, jobs. Compare the two
again after every review change.

**D13. Stay close to Moqui's own code patterns.** Shape a model, its cached
definition and its renderer the way the framework shapes screens, forms and
entity definitions. An algorithm is a class; a service is XML actions over it.
When the framework refuses a shape, the model is wrong: find the shape the
engine renders correctly instead of a workaround in code.

**D14. A diagnostic read runs the application's own query.** To answer "does
the list show this record, and why not", run the list's own view with its own
filters. Declare a left-joined view for the explanation columns. Never rebuild
the joins in a script.

**D15. Views are declared, and queries are proved.** No SQL text inside a
view-entity; a sub-select is a member with `sub-select`. Start from the plainest
join that answers the rule. Before a commit that adds a query, capture the SQL,
run EXPLAIN, name the indexes and say what grows.

**D16. Check the product's pattern before a framework conclusion.** Before
writing "the framework does not do X" or "nothing checks X", search the product
components for the established pattern. Engine behaviour is not system
behaviour, and a gap claim needs evidence of cost.

## Test data and local servers

**T1. Test data is captured data, not code.** A scenario is a cleansed captured
payload, its variables and the expected rows, replayed through the real entry
service. Never build a class hierarchy per test family.

**T2. Commit only what the corpus reads, and compute that set.** One script
scans the scenarios and writes the needed ids; another cuts the capture down to
them and fails loudly when an id is missing. Keep whole parents. A hand-written
list goes stale in silence. Store configuration is exempt.

**T3. One server per project folder.** Before a server start, a build or a data
load, list running servers by working directory: `pgrep -f moqui.war`, then
`lsof -a -p <pid> -d cwd`. Two JVMs from one folder share the temp jars, the
transaction log, the database and the file-import runner. Never clear all caches
on a running shared instance.

## Self-check before a pull request

Search your own diff for each of these. One hit is a rule broken.

| Search for | Rule |
|---|---|
| `<!--` inside `<actions>`, `//` or `/*` in Groovy | C1 |
| `<set field="is` or `<set field="has` | C2 |
| a new file under `script/`, a new `Closure`, `type="java"` | C5 |
| `in-map="true"`, `in-map="context"`, `out-map="context"` | C4, C6 |
| `.remove(`, `.put(` or `<set field=` on an in-parameter | C7 |
| `transaction=` on a service or service-call | C9 |
| `verb="record"`, `verb="pull"`, `verb="fill"`, "patch" | C11 |
| `logger.` or `<log` with `${` after the dash, or a bare exception | C12 |
| `tenantId` | C14 |
| `<render-mode>`, `.css`, `.js` in a screen change | C15 |
| `?: 0`, `?: -1` on a number | C16 |
| a hand-written id of 100000 or more, or longer than 20 characters | F1 |
| anything under `upgrade/` or a `ServiceJob` row, with no `UpgradeSteps.md` | F3 |
| `paused="N"` on a new job | F4 |
