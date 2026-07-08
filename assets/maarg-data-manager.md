# MDM in short — the data import pipeline

**What it is:** MDM (Maarg Data Manager, in the `maarg-util` component) is
how bulk data enters the OMS. Team reference:
https://forum.hotwax.io/t/maarg-data-manager-import-flow/340

It works like this: you give it a file and a config name. It imports
the file, one record at a time, and keeps a full log.

*(All file:line references verified 2026-07-08.)*

## The three ideas

1. **A config says what an import IS.** A `DataManagerConfig` row maps a
   name to an import service. Example: `SYNC_SHOPIFY_ORDER` →
   `sync#ShopifyOrder`. The config is data; no code changes to add one.
2. **A log tracks every file.** Each uploaded file gets a
   `DataManagerLog` row with a status. The file itself and any error
   file are linked as `DataManagerContent` rows. Extra values (like
   `shopId`) are stored as `DataManagerParameter` rows.
3. **Import is per record.** The loader reads the file as a JSON array
   and calls the import service once per record, each in its own
   transaction. One bad record does not stop the rest.

## The flow

```
upload#DataManagerFile (configId + file + parameters)
      │  saves file under runtime/datamanager/imported/<configId>/
      │  creates DataManagerLog, status = DmlsPending
      ▼
background timer (every 60 seconds)          ← there is NO ServiceJob
      │  picks up all pending logs
      ▼
loader imports the file record by record
      │  each record: own transaction, parameters merged in
      │  failed records → collected into an error file
      ▼
DataManagerLog updated: DmlsFinished or DmlsFailed
      error file (if any) linked as DataManagerContent
```

## The pieces, with code locations

| Piece | What it does | Where |
|---|---|---|
| `upload#DataManagerFile` | takes the file in, creates the log (pending) | `maarg-util/service/co/hotwax/util/UtilityServices.xml:159-236` |
| `ScheduledDataManagerRunner` | the background worker; runs every 60s | `maarg-util/src/main/groovy/co/hotwax/mdm/ScheduledDataManagerRunner.groovy` |
| `MaargDataLoaderImpl` | reads the file, calls the import service per record | `maarg-util/src/main/java/co/hotwax/datamanager/MaargDataLoaderImpl.java:604-648` |
| `DataManagerLogDetails` | one view with everything: status, failed count, error file | `maarg-util/entity/ServiceEntities.xml:83-119` |

## Statuses of a log

| Status | Meaning |
|---|---|
| `DmlsPending` | file staged, waiting for the runner |
| `DmlsQueued` / `DmlsRunning` | runner picked it up / import in progress |
| `DmlsFinished` | import ran to the end (failed records may still exist!) |
| `DmlsFailed` | the run itself failed |
| `DmlsCancelled` | cancelled by a user (only possible while pending) |
| `DmlsCrashed` | set by crash-recovery after a server restart |

**Important:** `DmlsFinished` does NOT mean all records succeeded. A
record that failed goes to the error file, and the log still finishes.
The real check is: `errorFileContentLocation` empty = all clean;
filled = some records failed. Both are on the `DataManagerLogDetails`
view.

## The error file

The only way a bad record is captured is when the import service
**returns an error** for it. The loader then writes that record into
`Error_<filename>.json` next to the source file, and links it to the
log. This is the operator's retry file. (A service that logs a problem
but returns success = the record is lost silently — the number one MDM
mistake.)

## The config, fully

A `DataManagerConfig` says more than just the import service:

| Field | Meaning |
|---|---|
| `importServiceName` | the service called once per record |
| `executionModeId` | `DMC_QUEUE` = one file at a time (the default, safest) · `DMC_ASYNC` = thread pool · `DMC_SYNC` = right now, in the caller's thread |
| `priority` | above 6 → the priority pool (3 threads); others → the normal pool (3 threads). Pending files are picked up in priority order |
| `multiThreading` | `Y` = a big file is split into chunks, imported in parallel |
| `importPath` | set = the file comes from SFTP; MDM polls that folder itself — nobody calls upload |
| `exportServiceName` / `exportContentId` | the export side (below) |

**Chunking:** when `multiThreading` is on, a big file splits by the
`groupBy` field if one was passed as an upload parameter (rows with the
same value stay together), otherwise into chunks of 50,000 records.
After the run, all chunk error files merge into one.

## Two shapes of a record

A file is always a JSON array. Each record is one of two shapes:

1. **Flat** — fields match the import service's parameters directly:
   `{"productId": "...", "facilityId": "...", "salesVelocity": "..."}`
2. **Wrapper** — one key holding the whole object, named after the
   service's big parameter: `{"payload": { ...the shopify order... }}`.
   The key name must equal the parameter name.

## One rule for producers

Everything that puts work into MDM goes through **`upload#DataManagerFile`**
(or arrives by SFTP via `importPath`). Nothing in the codebase creates a
`DataManagerLog` row directly — don't be the first.

## Exports

MDM also runs exports: a log with type `DmltExport`, driven by the
config's `exportServiceName` (often a generic CSV exporter over a
prepared `exportContentId`). Same log/content/status machinery, opposite
direction.

## Operating it

- **Retry:** there is no retry button. Download the error file, fix the
  bad rows, upload it again to the **same** config. The error file is
  already in the right shape for this.
- **Cancel:** only a `DmlsPending` log can be cancelled.
- **Screens:** DataManager → Config (per-config view: upload dialog,
  sample-template download, log grid, pool dashboard) and
  DataManager → Imports (all logs across configs).
- **After a crash:** on server restart, logs stuck in queued/running are
  re-queued automatically.

