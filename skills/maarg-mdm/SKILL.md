---
name: maarg-mdm
description: Work with the Maarg Data Manager (MDM) and its file writer — bulk data import/export in the maarg-util component. Use BEFORE any work that writes a data file with co.hotwax.util.DataFileWriter (feeds, batch files, MDM imports), touches DataManagerConfig, writes an import service, queues files via create#DataManagerLog or upload#DataManagerFile, reads error files, or drives an import from code or tests. Covers DataFileWriter rules, producer rules, the consumer error contract, and how to run and verify an import.
---

# Maarg Data Manager (MDM)

Read `../../assets/maarg-data-manager.md` first — what MDM is, the flow, the
statuses, the config fields, chunking, exports, and operations. Team
reference: https://forum.hotwax.io/t/maarg-data-manager-import-flow/340

This skill is the working discipline on top of that page.

## 1. Choose the entry path

| Situation | Path |
|---|---|
| File arrives on SFTP | set `importPath` on the config — MDM polls it; no upload call |
| A human uploads | the DataManager screen's Upload File dialog |
| Code wrote the file with `DataFileWriter` | `co.hotwax.util.UtilityServices.create#DataManagerLog` with `contentLocation` (`UtilityServices.xml:230-263`); the common path, 23 files across four components |
| Code holds an uploaded `FileItem` | `co.hotwax.util.UtilityServices.upload#DataManagerFile` (`UtilityServices.xml:194-225`) |
| Anything else | does not exist — NEVER create a `DataManagerLog` row with the entity directly; the two services also write the content and parameter rows |

New config? Follow the naming families: `SYNC_*`/`UPDATE_*`/`RESET_*`
(event-driven script imports), `IMP_*`/`MDM_*`/`CRT_*` (data setup),
`EXP_*` (exports). Default `executionModeId="DMC_QUEUE"`. Only set
`multiThreading="Y"` for genuinely large files; pass `groupBy` as an
upload parameter when related rows must stay on one thread.

## 2. Writing a data file (`co.hotwax.util.DataFileWriter`)

Every data file the project writes goes through `DataFileWriter`
(`maarg-util/src/main/groovy/co/hotwax/util/DataFileWriter.groovy`, guide in
`maarg-util/docs/DataFileWriter.md`). It is used beyond MDM: feeds, SFTP files,
and batch files sent to other systems. `NdjsonWriteHelper` in the NetSuite
connector is `@deprecated use DataFileWriter`.

1. **Use the three-argument constructor:**
   `new DataFileWriter(ec, filePath, DataFileWriter.JSON)`. The writer holds up
   to 1,000 records in memory, then writes them in one go (`DEFAULT_BATCH_SIZE`).
   That is the accepted design (sponsor ruling, 2026-10-23). Do not add, ask for,
   or propose a flush or batch-size setting, and do not change maarg-util for it.
   A caller that worried about memory still gains: no list of bodies in the
   service and no multi-megabyte JSON string in a database field.
2. **The fourth argument is `maxRecordsPerFile`, never a batch size.** A number
   there splits the output into `name.json`, `name_1.json`, `name_2.json`. Pass it
   only when the receiver wants split files, as the inventory and order feeds do
   with `recordLimitPerFeed`. A batch whose message holds one location must not
   pass it: every file after the first is written and never read.
3. **Commit, then close.** `getGeneratedFiles()` or `getGeneratedFilesInfo()`
   is the commit. `close()` without a commit deletes the files. In Groovy use
   try-with-resources and take the info inside the try. In XML actions, follow
   `<set field="fileInfo" from="writer.getGeneratedFilesInfo()?.getAt(0)"/>`
   then `writer.close()` (`PurchaseOrderServices.xml:170-173` in the NetSuite
   connector). A try block can open in one `<script>` and close in a later one
   (`OrderServices.xml:1076-1104` in the NetSuite connector).
4. **No records means no file.** The file opens on the first write, so the info
   list comes back empty and `?.getAt(0)` is null. Check `fileInfo` before you
   create a message or a `DataManagerLog`.
5. **The file is not part of the database transaction.** A committed file stays
   if the transaction rolls back later. When it must go with the transaction,
   register a rollback action:
   `ec.service.special().name('<delete service>').parameters([location: location]).registerOnRollback()`
   (`framework/.../ServiceCallSpecial.java:41`), or
   `ec.transaction.registerSynchronization(...)` from Groovy.
6. **Pick the format by the reader.** `JSON` writes one array; MDM reads only
   that (`MaargDataLoaderImpl.java:650-652` refuses any other root). `JSONL` writes one object per line, for a receiver that reads line by
   line (a NetSuite batch file). `CSV` takes its headers from the first record's
   keys.
7. **Path.** Pass a path relative to the content root, for example
   `imported/${configId}/ShopifyOrderList_${dateTime}.json`. Tokens other than
   `date`, `dateTime` and `contentRoot` come from a map in
   `ec.context.fileWriterContext` (`DataFileWriter.PATH_TOKENS_KEY`). A full
   location from `MaargUtil.toContentLocation(...)` also works. Never a disk
   path. An existing file name gets a `_1` suffix, so it is not overwritten.
8. **One writer per thread.** It is not thread-safe, and it writes only to
   file-backed locations.

## 3. Writing a producer (the side that queues a file for MDM)

Copy the production stager (`shopify-connector/service/co/hotwax/shopify/
order/SqsOrderImport.xml:176-220`):

1. Put the scoping ids in `fileWriterContext` and write the file with
   `DataFileWriter` under `imported/${configId}/`, as `JSON`.
2. Record shape: **flat** fields matching the consumer's in-parameters, or
   **one wrapper key named exactly after the consumer's big in-parameter**
   (`{"payload": {...}}` for a service with `payload` as in-param).
3. Take `fileInfo` from `getGeneratedFilesInfo()?.getAt(0)`. When it is null,
   queue nothing.
4. Queue it with `create#DataManagerLog`: `configId`, `contentLocation`,
   `fileName` and `fileSize` from `fileInfo`, and a small `parameters` map with
   the scoping id (`shopId`) and correlation ids (`systemMessageId`,
   `createdByJobRunId`) for traceability.

## 4. Writing a consumer (the import service)

The loader calls your service once per record, each in its OWN new
transaction (`MaargDataLoaderImpl.java:604-648`). Therefore:

- Design for ONE record: singular noun, in-params = the record's fields
  (or one Map parameter the wrapper key names).
- Do NOT add transaction attributes — the loader owns isolation.
- A bad record must **return an error** (`ec.message.addError(...)` or
  `<return error="true">`). That is the ONLY way it reaches the error
  file. Log-and-return-success = the record is silently lost — the
  number one MDM mistake.
- Do not throw exceptions for expected validation failures; the message
  facade is the signal.
- Do not over-fail: one bad line item should not fail the whole record
  unless the record is truly unusable.

## 5. Driving an import from code or tests

- **There is no job to trigger.** The runner is a shared framework tool
  on a 60-second timer. To run now, fetch the ONE shared instance:
  `ec.factory.getTool("MDM", ScheduledDataManagerRunner.class).run()` —
  the same call the admin screen makes
  (`maarg-util/screen/DataManager/DataManagerImport/DataManagerImportList.xml:37-42`).
  Never construct your own runner with `new` — two runners fight over
  the same pending logs.
- **The runner returns before the work is done.** Wait by re-reading the
  log status until `DmlsFinished` or `DmlsFailed`, with a time limit.
  Hitting the limit is a FAILURE, never a pass.
- **`DmlsFinished` does not mean success.** The verdict is
  `errorFileContentLocation` on the `co.hotwax.datamanager.DataManagerLogDetails`
  view (`maarg-util/entity/ServiceEntities.xml:83-119`): empty = clean,
  filled = failed records exist.
- **Read files through the framework:**
  `ec.resource.getLocationReference(location).getText()` — never guess a
  filesystem path.
- **Retry** = download the error file, fix rows, re-upload to the same
  config. **Cancel** works only on `DmlsPending`.

## 6. Pitfalls

| Trap | Consequence |
|---|---|
| Consumer logs an error but returns success | record lost silently, nothing in the error file |
| `new ScheduledDataManagerRunner(...)` | second runner races the timer singleton |
| Treating `DmlsFinished` as "all good" | failed records missed — check the error file |
| Unbounded wait loop on the log status | a hung import passes silently |
| `groupBy` on independent rows | unbalanced chunks, slower than no grouping |
| Creating `DataManagerLog` rows with the entity directly | no content or parameter rows; use `create#DataManagerLog` |
| A flush or batch-size setting on `DataFileWriter` | ruled out; the 1,000-record batch is the design |
| A number as the fourth `DataFileWriter` argument | the output splits into `_1`, `_2` files nobody reads |
| `close()` without `getGeneratedFiles*()` | the file is deleted |
| Assuming the file rolls back with the transaction | a file left for a batch that never existed |
| `JSONL` for an MDM import | the loader reads a JSON array only |

## Verify before declaring done

After building or changing anything MDM-related: run one real file
through, then read `DataManagerLogDetails` for the log — status
terminal, error file empty (or containing exactly the records you
expected to fail). "It uploaded" is not a result; the log row is.
