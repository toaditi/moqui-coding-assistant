# Master Entities — the framework's entity-graph get **and** store mechanism

**What it is:** an entity `<master>` is a **named graph shape** declared on an
entity as data — the primary entity plus a tree of its related entities. That
one definition drives graph I/O in **both** directions:

- **GET** — `getMasterValueMap` / `oneMaster` / `listMaster` read the primary
  and its related rows as **one nested Map** (no hand-written joins, no N+1).
- **STORE** — the entity-auto `store#<Entity>` service takes a **same-shaped
  nested Map** and recursively creates-or-updates the whole graph (no
  hand-written per-table INSERT/MERGE, no flatten step).

So a graph you read as a Map you can write back as a Map. This is the native
answer to "read/write a whole order (or any parent + children) at once."

Official reference: https://www.moqui.org/m/docs/framework/Data+and+Resources/Entity+Master+Definition
(All framework `file:line` citations verified 2026-07-24 against `moqui-framework` `release-3.5.2`.)

## Defining a master (the graph shape, as data)

On the entity (or via `<extend-entity>`), declare `<master>` with a tree of
`<detail>` elements. Each `<detail>` names a **relationship** to follow; a
detail may point at another entity's master via `use-master` to nest deeper.

```xml
<extend-entity entity-name="OrderHeader" package="org.apache.ofbiz.order.order">
  <relationship type="many" related="...OrderItem"          short-alias="items"/>
  <relationship type="many" related="...OrderItemShipGroup" short-alias="shipGroups"/>
  <master name="orderMirror">
    <detail relationship="items"/>
    <detail relationship="shipGroups" use-master="shipGroupMaster"/>  <!-- nest deeper -->
  </master>
</extend-entity>
```

- A master with **no `name`** is the **`default`** master; `getMasterDefinition(null)`
  resolves `"default"` (`EntityDefinition.groovy:730`). `MasterDefinition` /
  `MasterDetail` are built from the `<master>`/`<detail>` nodes
  (`EntityDefinition.groovy:729-758`).
- `<detail>` controls **which related entities** are traversed — NOT which
  fields of each entity are returned. Every entity in the tree contributes its
  full declared field set (see "reads declared fields" caveat).
- Define the master in **your own** component via `<extend-entity>`; never edit
  a shared entity's existing master in place — other code's REST payloads
  consume it.

## GET — read a graph as a nested Map

| API | Returns | Where |
|---|---|---|
| `EntityValue.getMasterValueMap(name)` | one nested Map for a loaded value | `EntityValueBase.java:1239-1295` |
| `EntityFind.oneMaster(name)` | find-one + master, one Map | `EntityFind.java:267` |
| `EntityFind.listMaster(name)` | find-list + master, `List<Map>` | `EntityFind.java:274` |
| REST `<entity … operation="one\|list" masterName="…">` | the graph as JSON | `RestApi.groovy:369-391` |

The output shape (`internalMasterValueMap`, `EntityValueBase.java:1246-1294`):
the primary entity's fields, plus one key **per detail** named by the
relationship's `short-alias` — value is a nested Map (`type="one"`) or a
`List<Map>` (`type="many"`), each carrying an `_entity` marker. Nulls are
stripped. It runs `findRelatedOne`/`findRelated` per detail, so it is a small
number of indexed finds, not a hand-rolled join.

## STORE — write a graph from a nested Map (the symmetric half)

The entity-auto **`store#<Entity>`** service takes a Map whose keys are the
entity's fields **plus relationship names/aliases whose values are nested
Maps/Lists**, and persists the whole graph:

```groovy
ec.service.sync().name("store", "OrderHeader").parameters(orderGraphMap).call()
// orderGraphMap = [orderId:…, statusId:…, items:[[orderId:…,orderItemSeqId:…,…], …], shipGroups:[…]]
```

Verified mechanics (`EntityAutoServiceRunner.groovy`):
- **Recursion** — `storeRecursive` → `storeRelated` walks the parameters Map;
  any key that is a mutable relationship whose value is a Map or List is stored
  as a sub-entity (`:245-300`, `:363`). Nesting is arbitrary depth; comment at
  `:226`: *"we allow other entities to be nested, and they may have nested
  records that depend on ANY ancestor's PKs."*
- **Upsert per entity** — `store` looks the row up by PK; **absent → `create()`,
  present → `setFields`/update** (`:314-344`). `create#` is insert-only,
  `update#` update-only, `store#` create-or-update.
- **PK propagation** — a child inherits the parent's PK fields automatically
  (`getTargetParameterMap`, `:268`/`:399`) — you don't repeat `orderId` on every
  nested item if the relationship key-map covers it.
- **REST** — `<entity … operation="store" masterName="…">` (POST/PUT a nested
  JSON body) is exactly this service (`RestApi.groovy:400-402`).

## The round trip

`getMasterValueMap(m)` out → JSON → `store#<Entity>` in. The read Map is
essentially the store input (drop the `_entity` markers). This is the whole
point: **move an entity graph between contexts without writing SQL on either
side**, and the entity engine enforces validation, type conversion, and
optimistic-lock on the way in — which a hand-rolled MERGE never does.

## When to use it — and how to DETECT when it wasn't (architect's job)

**Use it** for ANY multi-entity read or write of a parent + its children:
reading an order graph, mirroring a record set, transporting a nested document,
an inbound "create the whole thing" API. This is the **entity-facade rung** of
the native-first ladder for *graphs*, exactly as `create#/update#/store#` and
view-entities are for single entities and joins.

**Detect the violation.** These are native-first misses — flag them, name the
native path:
- a hand-written **multi-table read loop** (`entity-find` → iterate →
  `entity-find` per child) where a `<master>` + `getMasterValueMap`/`oneMaster`
  would do it in one call → **REDESIGN**;
- **raw SQL / a per-table INSERT or MERGE** to write a parent + children, or a
  "flatten the graph then write each table" step, where `store#<Entity>` of the
  nested Map does it natively → **REDESIGN**.

**The honest exception (deviation protocol).** Raw SQL for graph movement is
justified ONLY by a constraint the engine genuinely can't meet — and it must
cite that constraint:
- **bulk, cross-datasource streaming** — copying millions of rows between two
  databases (e.g. a MySQL source → an H2 mirror) can't go row-by-row through
  `store#`; a streamed `MERGE` is the right tool. **Justified.**
- **per-record / per-graph** work — one order, one return — has no such
  constraint. `store#` is the default; raw SQL here is an **unjustified**
  deviation. (Real miss, 2026-07-24: an order-mirror design flattened each
  order's graph and wrote it with a per-table raw MERGE — the per-order write
  should have been a native `store#` of the master map.)

## Master vs DataDocument — which graph reader

Both read a graph; they differ in **shape**, so they serve different needs:

| | `<master>` + `getMasterValueMap` | DataDocument + `getDataDocuments` |
|---|---|---|
| Output | **nested** per-entity Maps (distinct row sets preserved) | **flat**, denormalized one-row-per-leaf |
| Best for | CRUD / mirror / transport / a `store#` round-trip | feeds, search-index docs, reporting projections |
| Write side | symmetric — `store#` takes the same shape | one-way (feed push); no store counterpart |

Reach for a **master** when you will re-store or need distinct per-table rows;
reach for a **DataDocument** when you need a flat document pushed on change (see
`moqui-data-feed.md`). Mirroring distinct tables through a DataDocument is a
shape mismatch.

## Caveats (verified — the ones that bite)

- **Reads *declared fields*, not raw columns.** A master find selects the
  entity's full declared field set; a source column the entity doesn't declare
  won't come through, and a declared field whose column is missing errors
  (`Unknown column`). Confirm the entity model covers the columns you need.
- **One entity, one datasource group.** A master traversal (and a `store#`)
  runs in the entity's `group-name`. A `<master>` can't join across groups
  (different databases), and `store#` writes to the entity's group — so a
  read-from-source / write-to-mirror flow needs the read entities and write
  entities in the right groups (often distinct entities per group).
- **`store#` null-clobbers absent fields.** `store` sets every field in the
  in-Map, nulling create-only fields (`createdDate`, `createdByUserId`) if
  they're absent. To preserve them, hand-write the create-vs-update branch or
  omit them from the update path.
- **Don't confuse the group-name *cache* with the effective binding.**
  `EntityFacade.getEntityGroupName(name)` can return a stale cached value for a
  freshly (re)bound entity; finds and `getMasterValueMap` resolve the group from
  the live entity definition and read correctly regardless. Don't branch on that
  call.

## Real HotWax reference pattern

`OrderHeader`'s **`default`** master (`oms/entity/OrderExtendedEntities.xml:58-71`)
is the production "one order, full graph" reader — nested roles+party, ship
groups→items, contact mechs, adjustments, statuses. It is consumed read-side by
poorti's `GET orders/{orderId}` (`poorti/service/poorti.rest.xml` — `operation="one"
masterName="default"`) and the oms REST list. `EntityValueBase.writeXmlTextMaster`
(`:1102`) even serializes a master to XML off the same map. Define your own named
master beside it (never edit `default`) for a purpose-built graph shape.
