---
name: moqui-master-entity
description: Get and store a whole entity GRAPH (a parent plus its related rows) through a Moqui entity <master> — getMasterValueMap/oneMaster/listMaster to read a nested Map, and the entity-auto store#<Entity> to write the same-shaped Map back (recursive create-or-update). Use when the design reads or writes an order/return/parent-with-children as a unit, mirrors a record set, transports a nested document, or exposes a "create the whole thing" API. Reach for this BEFORE hand-writing a multi-entity read loop, or raw SQL / a per-table INSERT/MERGE / a "flatten then write each table" step to move a graph.
---

# Moqui Master Entities — entity-graph get & store

Read `../../assets/moqui-master-entity.md` first — the grammar (`<master>`/
`<detail>`), the read APIs, the recursive `store#` write, master-vs-DataDocument,
and the verified caveats. This skill is the working discipline on top of it.

## 1. Is this the right tool? (decide first)

| The need | Use |
|---|---|
| Read a parent + its children as one nested Map | **`<master>`** + `getMasterValueMap` / `oneMaster` / `listMaster` |
| Write a parent + its children from a nested Map | entity-auto **`store#<Entity>`** (recursive upsert) |
| Round-trip a graph between contexts (read here → store there) | master **get** → JSON → **`store#`** — no SQL either side |
| Push a **flat** document to a feed / search index on change | **DataDocument + DataFeed** (`moqui-data-feed`), not a master |
| A single entity, no children | plain `entity-find` / `create#`/`update#`/`store#` — a master is overkill |

## 2. Define it in your own component

Declare `<master name="…">` via `<extend-entity>` in **your** component; never
edit a shared entity's existing `default` master in place — other code's REST
payloads consume it. `<detail>` picks which relationships to follow (not which
fields); `use-master` nests a child's own master. No `name` = the `default`
master.

## 3. Read / write

- **Read:** `ev.getMasterValueMap(name)` (loaded value), `ef.oneMaster(name)` /
  `ef.listMaster(name)` (find + master), or REST `operation="one|list"
  masterName="…"`. Keys are relationship short-aliases → nested Map / List.
- **Write:** `ec.service.sync().name("store", "<Entity>").parameters(graphMap).call()`
  or REST `operation="store" masterName="…"`. `store#` is **upsert per entity**;
  nested Maps/Lists under relationship keys are recursed; parent PKs propagate to
  children automatically. Use `create#` for insert-only, `update#` for update-only.

## 4. Detect the anti-pattern (review discipline)

Flag as **native-first violations** — name the native path:
- an `entity-find` → iterate → `entity-find`-per-child **read loop** where a
  master read would do it in one call;
- **raw SQL / a per-table INSERT or MERGE**, or a "flatten the graph then write
  each table" step, to persist a parent + children, where `store#` of the nested
  Map does it natively.

**Deviation exception (must be cited):** raw SQL is justified only for a
constraint the engine can't meet — chiefly **bulk cross-datasource streaming**
(millions of rows between two DBs). **Per-record / per-graph** work (one order)
has no such constraint → `store#` is the default; raw SQL there is unjustified.

## 5. Verify before declaring done

1. The master resolves (relationship paths valid) — a read returns the expected
   nested shape.
2. `store#` of that shape lands every entity in the graph — check the child rows,
   not just the parent ("it ran" is not a pass).
3. Column coverage: the entities declare every field the graph needs (a master
   reads declared fields, not raw columns).
4. Datasource group: read and write entities resolve to the intended group(s);
   a master can't join, and `store#` can't write, across datasource groups.
