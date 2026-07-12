# DataDocument & DataFeed — the framework's data-push mechanism

**What it is:** a DataDocument turns a primary entity plus its related
entities into one nested JSON document, defined as **data** (not code). A
DataFeed pushes those documents to a service the moment the underlying data
changes — real-time, driven by rows you can add, enable, or disable at
runtime.

Official reference: https://www.moqui.org/m/docs/framework/Data+and+Resources/Data+Feed
(All framework file:line citations verified 2026-07-10 against `moqui-framework`.)

## The two ideas

1. **DataDocument = a query, expressed as data.** One `DataDocument` row
   names a `primaryEntityName`; child rows name the fields to include (by
   relationship path) and conditions to scope it. `ec.entity.getDataDocuments(...)`
   runs ONE query across the whole graph and returns a list of nested Maps —
   no hand-written multi-entity joins, no N+1.
2. **DataFeed = push those documents on change.** A `DataFeed` row links to
   one or more DataDocuments and names a **receive service**. When any tracked
   entity is written, the framework regenerates the affected documents and
   calls that service. You never poll and you never write a SECA per external
   sync — the feed is the mechanism.

## The entities (all in `framework/entity/EntityEntities.xml`)

| Entity | Key fields | Purpose |
|---|---|---|
| `moqui.entity.document.DataDocument` | `dataDocumentId` (PK), `primaryEntityName`, `indexName`, `manualDataServiceName` | the document definition (`:94-127`) |
| `DataDocumentField` | `dataDocumentId`+`fieldSeqId`, `fieldPath`, `fieldNameAlias`, `functionName` | one field; `fieldPath` is a `Rel:Rel:fieldName` relationship path or a Groovy expression (`:129-152`) |
| `DataDocumentCondition` | `dataDocumentId`+`conditionSeqId`, `fieldNameAlias`, `operator`, `fieldValue`, `postQuery` | scope the document; `postQuery=Y` filters in memory after the query (`:163-176`) |
| `DataDocumentRelAlias` | `dataDocumentId`+`relationshipName`, `documentAlias` | rename a relationship in the output tree (`:155-161`) |
| `moqui.entity.feed.DataFeed` | `dataFeedId` (PK), `dataFeedTypeEnumId`, `feedReceiveServiceName`, `feedDeleteServiceName`, `indexOnStartEmpty` | the feed (`:208-220`) |
| `DataFeedDocument` | `dataFeedId`+`dataDocumentId` | links a document to a feed (`:230-235`) |
| view `DataFeedAndDocument` | — | the view the real-time dispatcher queries (`:236-242`) |

**Feed types** (`DataFeed.dataFeedTypeEnumId`, seed at `EntityEntities.xml:223-227`):

- `DTFDTP_RT_PUSH` — **real-time push.** Fires on entity change. Every real
  HotWax feed uses this.
- `DTFDTP_MAN_PULL` — **manual pull.** Retrieved on demand via
  `get#DataFeedLatestDocuments` (uses `DataFeed.lastFeedStamp` as the window).
- (`DTFDTP_PER_PUSH` "periodic" exists commented-out — not usable.)

## The receive-service contract

Every `feedReceiveServiceName` must implement the interface
`org.moqui.EntityServices.receive#DataFeed`
(`framework/service/org/moqui/EntityServices.xml:16-33`):

- **in:** `dataFeedId`, `feedStamp` (Timestamp), `documentList` (a List of
  Maps — each Map is one document, with `_id`, `_type`=dataDocumentId,
  `_index`, `_timestamp`, plus the primary-entity fields and nested
  related-entity lists).
- The service **iterates `documentList`** and does its work per document.

The framework ships a default implementation:
`org.moqui.search.SearchServices.index#DataDocuments`
(`framework/service/org/moqui/search/SearchServices.xml:17-37`) — bulk-indexes
the documents into ElasticSearch. A feed that names no receive service uses
this. `feedDeleteServiceName` implements `receive#DataFeedDelete` for removals.

## How the real-time push actually works (verified — two surprises)

The mechanism is **not** a declarative `<eeca>` rule. It is hard-wired into
`EntityValueBase` create/update/delete
(`EntityValueBase.java:1531, 1684, 1770`), handled by
`EntityDataFeed.groovy`.

**Surprise 1 — delivery is asynchronous, after commit, per transaction.**
Changes are accumulated during the transaction by a JTA `Synchronization`
and dispatched only in `afterCompletion(COMMITTED)` — on a **worker thread,
in a brand-new transaction** (`EntityDataFeed.groovy:508-515`). Consequences
you must design for:

- The receive service runs **after** the triggering write has committed. It
  is not in the same transaction.
- A receive-service failure **does not roll back** the write. The data change
  stands; only the push failed. (Design the receiver to be retryable, and
  consider a reconciliation job as a safety net — the D365 feed does exactly
  this.)
- Multiple writes to the same document in one transaction are **debounced**:
  the document is regenerated once and pushed once.
- The dispatcher regenerates the WHOLE affected document (one query per
  affected primary-entity PK set) and calls the receive service with the
  fresh documents — the receiver always sees current state, not a diff.

**Surprise 2 — runtime enable/disable is real, but has ONE hard boundary.**
The "which entities feed which documents" registry lives in a local cache
`entity.data.feed.info` (15-minute TTL, `MoquiDefaultConf.xml:128-129`) plus a
fast-negative `Set entitiesWithDataFeed`.

- For an entity **already known** to participate in a real-time feed:
  enabling/disabling a feed, changing its receive service, or editing its
  fields/conditions takes effect **without a restart** — within 15 minutes,
  or **instantly** by clearing the `entity.data.feed.info` cache from the
  Tools → Cache admin screen. This is the "manage feeds without restart"
  capability.
- **The boundary:** wiring a **brand-new entity** (one never referenced by
  any real-time DataDocument since server start) into a feed for the first
  time needs a **server restart**. The `entitiesWithDataFeed` set is built
  once at startup and never reset — the framework says so in a source comment
  (`EntityDataFeed.groovy:251-254`): *"if an entity is added to a DataDocument
  at runtime it won't pick it up."* Clearing the cache does not fix this.

## Runtime control — the admin surface

- **REST CRUD** on DataDocument/DataFeed rows:
  `maarg-util/service/admin.rest.xml:131-170` — `/rest/s1/admin/dataDocuments`
  and `/rest/s1/admin/dataFeeds` (create/edit feeds, fields, conditions live).
- **UI:** the `hotwax/job-manager` Vue app is built on that REST API —
  browse, create, edit, preview documents, schedule exports.
- **Apply a change instantly:** Tools → Cache → clear `entity.data.feed.info`
  (`runtime/base-component/tools/screen/System/Cache/CacheList.xml`).

## The bulk caveat — feeds are for events, not batches

A feed fires once **per entity write**. For a bulk load of thousands of rows
that is thousands of document regenerations — it does not scale. The framework
gives you the off switch, and the suite uses it:

- `EntityDataLoader.disableDataFeed(true)` suppresses feed firing during a load
  (`ofbiz-oms-usl/service/co/hotwax/ofbiz/MigrationServices.xml:146-153`).
- MDM wires this to a per-config flag: `DataManagerConfig.enableDataFeed`
  (default `N`) — feeds stay OFF during bulk imports unless a config opts in
  (`ScheduledDataManagerRunner.groovy:288,680-694`).
- The lesson, learned in production: HotWax's one attempt to drive a product
  search index through a feed was **commented out** —
  *"data feeds are not performing well with bulk product uploads"*
  (`oms/data/BA_SeedInitial_AF_DocumentData.xml:53-59`). Reach for a feed for
  **eventful, per-record** changes (a return closes, an order ships), not for
  batch reindexing.

## Real HotWax feeds (the reference patterns)

| Feed | Documents | Receive service does | Where |
|---|---|---|---|
| `WebhookEvents` | order / shipment / item status | pushes to external webhook subscribers | `oms/data/AI_WebhookDataFeed.xml`; receiver `oms/service/co/hotwax/webhook/WebhookServices.xml:231+` |
| `NetSuiteReturnsFeed` | return lifecycle (conditioned to exclude Loop/AfterShip) | drives NetSuite return sync (RMA, credit memo) | `gorjana-maarg/data/DJ_ExtSeed_NetSuiteReturnLifecycleFeedData.xml`; receiver `ReturnSyncServices.xml:5+` |
| `D365CustomersFeed` / `D365ReturnsFeed` | customer / return docs | pushes into Dynamics 365 + a fallback reconciliation job | `hotwax/hotwax-d365` (GitHub) |

All are `DTFDTP_RT_PUSH`; all receivers `implements receive#DataFeed` and
iterate `documentList`; all scope with `<conditions>` where they need to feed
only a subset. Note the recurring pattern: **a real-time feed paired with a
periodic reconciliation job** to catch anything the feed missed (feed disabled,
event dropped, receiver failed post-commit).
