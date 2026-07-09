# Official Moqui documentation — map and how it corroborates this plugin

The Moqui project publishes its own documentation at
[moqui.org/docs](https://www.moqui.org/docs), maintained independently of this
plugin. This asset is a **pointer map**, not a copy — link out to the live
page rather than duplicating its text, so this plugin never drifts from a
source it doesn't own. Update this map if a linked page moves.

## Why this asset exists

Several rules in this plugin (native-first ordering, ECA scoping, screen
command/query separation) were originally sourced from *Making Apps with
Moqui* (Jones, 2014) with a PDF page citation. Reading the official docs
confirmed the same rules **verbatim, on a public URL** — a stronger citation
than a book page, and proof the rule is still current framework doctrine, not
just something one book said once. Where a rule below has both a book page
and a doc-page citation, the two independently agree.

## Data model

- [Data Model Patterns](https://www.moqui.org/m/docs/framework/Data+and+Resources/Data+Model+Patterns) —
  the framework's own pattern catalog: **Master Entity** (independent
  records, single-field PK), **Detail Entity** (adds fields to a master via
  a composite PK), **Join Entity** (many-to-many association, often with
  `fromDate`/`thruDate` effective dating), **Dependent Entities** (the
  reverse-relationship hierarchy), **Enumerations**, **Status/Flow/
  Transition/History**, **Units of Measure**, **Geographic Boundaries**.
  Cross-reference: `moqui-hemp-method.md`'s data-statement guidance and this
  plugin's own pattern findings should use these exact names.
- [Data Model Definition](https://www.moqui.org/m/docs/framework/Data+and+Resources/Data+Model+Definition) —
  entity XML syntax reference.
- [The Entity Facade](https://www.moqui.org/m/docs/framework/Data+and+Resources/The+Entity+Facade) —
  `ec.entity`, entity-auto services (`create#`/`update#`/`store#` — "you
  don't have to explicitly set the sequenced primary ID"), view-entity
  aliasing optimization, `conditionDate()` for effective-date queries.
- [Entity Data Import and Export](https://www.moqui.org/m/docs/framework/Data+and+Resources/Entity+Data+Import+and+Export) —
  `EntityDataLoader`, the core loader types (`seed`, `seed-initial`, `demo`);
  a host project may layer its own types (e.g. `ext-seed`) on top — that is
  project convention, not core framework.
- [Entity ECA Rules](https://www.moqui.org/m/docs/framework/Data+and+Resources/Entity+ECA+Rules) —
  when EECA fires (`on-create`/`on-update`/`on-delete`/`on-find-*`), and the
  scoping rule verbatim: **"EECA rules should not generally be used for
  triggering business processes because the rules are applied too widely.
  Service ECA rules are a better tool for triggering processes."**

## Services

- [Service Definition](https://www.moqui.org/m/docs/framework/Logic+and+Services/Service+Definition) —
  XML actions vs Groovy, in/out parameters, validation sub-elements
  (`matches`, `number-range`, `text-email`, ...), `allow-html`, and the
  `semaphore` attribute (native single-instance execution for long-running
  services).
- [Service Implementation](https://www.moqui.org/m/docs/framework/Logic+and+Services/Service+Implementation) —
  script/inline/java/entity-auto runners; entity-auto automatic behaviors
  (`store` create-or-update, sequenced ID generation, `fromDate` auto-set,
  `oldStatusId`/`statusChanged`, `StatusFlowTransition` enforcement).
- [Calling Services](https://www.moqui.org/m/docs/framework/Logic+and+Services/Calling+Services) —
  the `ec.service` DSL: sync/async/job, `requireNewTransaction`,
  `disableAuthz`, `special()` TX commit/rollback hooks, `callFuture()`,
  `distribute`.
- [Service ECA Rules](https://www.moqui.org/m/docs/framework/Logic+and+Services/Service+ECA+Rules) —
  SECA's 7 firing phases relative to the named service call: **pre-auth,
  pre-validate, pre-service, post-service, post-commit, tx-commit,
  tx-rollback.** Confirms SECA is the tool for triggering business processes
  and extending services you can't modify — the counterpart to EECA's "don't
  use me for that" above.
- [Overview of XML Actions](https://www.moqui.org/m/docs/framework/Logic+and+Services/Overview+of+XML+Actions) —
  the mini-language used inside services and screens.
- [Service Jobs](https://www.moqui.org/m/docs/framework/Logic+and+Services/Service+Jobs) —
  scheduled/recurring service execution via `ServiceJob` records. States the
  monitoring rule verbatim: **"User can track execution of Jobs using
  moqui.service.job.ServiceJobRun records"** (`ServiceJobRunLock` is the
  scheduler's lock, not run history). Ad-hoc runs:
  `ec.service.job("name").parameters(ctx).run()` returns the `jobRunId`.

## User interface

- [XML Screen](https://www.moqui.org/m/docs/framework/User+Interface/XML+Screen) —
  screen hierarchy vs the transition graph, subscreens, security settings,
  render modes. States the command/query split verbatim: **"The logic in
  transitions... should be used only for processing input, and not for
  preparing data for display"** / **"Screen actions should be used only for
  preparing data for output."**
- [XML Form](https://www.moqui.org/m/docs/framework/User+Interface/XML+Form) —
  `form-single`/`form-list` definitions.
- [Templates](https://www.moqui.org/m/docs/framework/User+Interface/Templates) —
  FreeMarker and other template engines in the render pipeline.

## System interfaces

- [System Message](https://www.moqui.org/m/docs/framework/System+Interfaces/System+Message) —
  the integration-flow mechanism for inbound/outbound async messages.
- [Web Service](https://www.moqui.org/m/docs/framework/System+Interfaces/Web+Service) —
  REST/SOAP exposure.
- [Data and Logic Level Interfaces](https://www.moqui.org/m/docs/framework/System+Interfaces/Data+and+Logic+Level+Interfaces) —
  the same data-level (EECA/entity sync) vs logic-level (SECA/service call)
  split named above, stated as an integration architecture choice.

## Security

- [Security](https://www.moqui.org/m/docs/framework/Security) — authentication
  (Apache Shiro, `UserFacade.loginUser()`), simple permissions
  (`ec.user.hasPermission()`), artifact-aware authorization (`ArtifactGroup`,
  `ArtifactAuthz`, authz types ALWAYS/ALLOW/DENY), record-level authorization,
  artifact tarpit (rate limiting).

## Getting started (for a reader new to the framework)

Recommended order per the official site: Introduction →
[Framework Features](https://www.moqui.org/m/docs/framework/Framework+Features) →
[Run and Deploy](https://www.moqui.org/m/docs/framework/Run+and+Deploy) →
[Quick Tutorial](https://www.moqui.org/m/docs/framework/Quick+Tutorial) →
[Tool and Config Overview](https://www.moqui.org/m/docs/framework/Tool+and+Config+Overview).

## Related official spaces (not yet mapped in detail)

- [Mantle Business Artifacts](https://www.moqui.org/m/docs/mantle) — the UDM
  this plugin's entity guidance builds on.
- [Applications](https://www.moqui.org/m/docs/apps) — the reference
  application suite.
- Full page index: [All Pages — Framework](https://www.moqui.org/m/alldocs/framework)
