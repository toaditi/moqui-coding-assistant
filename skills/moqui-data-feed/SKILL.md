---
name: moqui-data-feed
description: Design and build with Moqui DataDocument and DataFeed — nested cross-entity documents defined as data, pushed to a service in real time on entity change. Use when the design needs to push data to an external system or a search index when records change (returns, orders, customers, shipments), when asked to sync on data change without polling, when reading a whole entity graph as one nested document, or when creating/enabling/disabling a feed at runtime. Reach for this BEFORE hand-writing a SECA that calls an external service, or a multi-entity read loop.
---

# Moqui DataDocument & DataFeed

Read `../../assets/moqui-data-feed.md` first — the entities, the two feed
types, the receive-service contract, the real-time mechanism, runtime control,
and the real HotWax feeds. This skill is the working discipline on top of it.

## 1. Is this the right tool? (decide first)

| The need | Use |
|---|---|
| Push a record's data to an external system / search index **when it changes** | **DataFeed** (`DTFDTP_RT_PUSH`) |
| Read a whole entity graph (primary + related) as one nested document | **DataDocument** + `ec.entity.getDataDocuments(...)` |
| Pull a batch of changed documents on a schedule / on demand | **DataFeed** `DTFDTP_MAN_PULL` + `get#DataFeedLatestDocuments` |
| Bulk load thousands of rows | **NOT a feed** — feeds fire per write; disable them (`enableDataFeed=N`) during the load |
| A simple one-entity lookup | plain `entity-find` — a DataDocument is overkill |

The strongest signal you should have used a feed: a SECA that reacts to a
status change by calling an external service. That is a feed. (The suite even
left a `FIXME` admitting one such hand-rolled path should be a feed —
`oms/service/co/hotwax/oms/search/... oms.secas.xml`.)

## 2. Define the DataDocument (data, not code)

Seed rows in `data/*.xml` (`ext-seed` for client data). Minimum:

1. `DataDocument` — `dataDocumentId`, `documentName`, `primaryEntityName`.
2. `DataDocumentField` per output field — `fieldPath` is a relationship path
   `Rel:Rel:fieldName` from the primary entity (e.g. `items:product:productName`),
   `fieldNameAlias` is the unique output name. Use `functionName` for
   aggregates (count/sum).
3. `DataDocumentCondition` to SCOPE it — feed only the subset you mean
   (the NetSuite feed excludes Loop/AfterShip returns this way). Prefer a
   query condition; use `postQuery=Y` only when the value isn't queryable.

Verify the paths against the real relationships on `primaryEntityName` before
committing — a wrong `fieldPath` fails at document build, not at load.

## 3. Wire the real-time feed

1. `DataFeed` row — `dataFeedTypeEnumId="DTFDTP_RT_PUSH"`,
   `feedReceiveServiceName="<your receive service>"`.
2. `DataFeedDocument` row linking the feed to the document.
3. The receive service:
   - `<implements service="org.moqui.EntityServices.receive#DataFeed"/>` —
     this gives you `dataFeedId`, `feedStamp`, `documentList`.
   - **Iterate `documentList`** — one Map per document. Do the push per doc.
   - Design it **retryable and side-effect-safe**: it runs AFTER the write
     commits, on a worker thread, in a new transaction. Its failure does NOT
     roll back the data change (see the asset).
   - Errors: log and handle; do not assume the caller will retry for you.

## 4. Non-negotiables (the three that bite)

- **Async, post-commit delivery.** The receiver is not in the writer's
  transaction. Never assume the push and the write commit or roll back
  together. Pair a real-time feed with a **periodic reconciliation job** for
  anything the feed can drop (disabled, dropped event, receiver failure) —
  every mature HotWax feed does.
- **Bulk kills it.** A feed fires per entity write. For bulk, disable it
  (`EntityDataLoader.disableDataFeed(true)` / `DataManagerConfig.enableDataFeed=N`).
  A feed on a bulk path is a performance defect.
- **New-entity wiring needs a restart.** Enabling/disabling/editing a feed on
  an entity ALREADY in a real-time feed is live (clear the
  `entity.data.feed.info` cache to apply instantly). But wiring a **brand-new**
  entity into a real-time feed for the first time needs a **server restart** —
  the registry's negative set is built once at startup
  (`EntityDataFeed.groovy:251-254`). State this in any design that adds a feed
  to a new entity.

## 5. Runtime control (the "without restart" capability)

- Create/edit/enable/disable feeds via REST: `/rest/s1/admin/dataFeeds`,
  `/rest/s1/admin/dataDocuments` (`maarg-util/service/admin.rest.xml:131-170`);
  the `hotwax/job-manager` app is the UI over it.
- Apply a change immediately: Tools → Cache → clear `entity.data.feed.info`
  (otherwise it lands within the 15-minute TTL).
- Subject to the new-entity boundary in §4.

## Verify before declaring done

1. Load the document + feed seed data; confirm the rows exist.
2. Change one tracked record; confirm the receive service ran (log/side effect)
   AFTER commit, once per affected document.
3. Confirm a scoping condition actually excludes the rows it should.
4. If the feed touches a bulk path, confirm the feed is disabled there.
5. If it wired a new entity, confirm behavior after a restart — and say so.
