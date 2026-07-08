---
name: maarg-mdm
description: Work with the Maarg Data Manager (MDM) — bulk data import/export in the maarg-util component. Use BEFORE any work that touches DataManagerConfig, writes an import service, uploads files via upload#DataManagerFile, reads error files, or drives an import from code or tests. Covers producer rules, the consumer error contract, and how to run and verify an import.
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
| Code uploads | `co.hotwax.util.UtilityServices.upload#DataManagerFile` |
| Anything else | does not exist — NEVER create a `DataManagerLog` row directly |

New config? Follow the naming families: `SYNC_*`/`UPDATE_*`/`RESET_*`
(event-driven script imports), `IMP_*`/`MDM_*`/`CRT_*` (data setup),
`EXP_*` (exports). Default `executionModeId="DMC_QUEUE"`. Only set
`multiThreading="Y"` for genuinely large files; pass `groupBy` as an
upload parameter when related rows must stay on one thread.

## 2. Writing a producer (the side that uploads)

Copy the production stager pattern (`mantle-shopify-connector/service/co/
hotwax/shopify/order/SqsOrderImport.xml:118-145`):

1. Stage the file under `runtime://datamanager/<area>/` — resolve the
   directory with `ec.resource.getLocationReference(...)`, never a
   hardcoded absolute path.
2. Build a `DiskFileItem` and stream the JSON into its output stream —
   `contentFile` is a FileItem, not a path string.
3. The file is a JSON array. Record shape: **flat** fields matching the
   consumer's in-parameters, or **one wrapper key named exactly after
   the consumer's big in-parameter** (`{"payload": {...}}` for a service
   with `payload` as in-param).
4. Pass `parameters` as a small map converted with
   `.entrySet().toList()` — carry the scoping id (`shopId`) and
   correlation ids (`systemMessageId`, `createdByJobRunId`) for
   traceability.
5. Name files `${SemanticName}_${configId}_${UUID}.json`.

## 3. Writing a consumer (the import service)

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

## 4. Driving an import from code or tests

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

## 5. Pitfalls

| Trap | Consequence |
|---|---|
| Consumer logs an error but returns success | record lost silently, nothing in the error file |
| `new ScheduledDataManagerRunner(...)` | second runner races the timer singleton |
| Treating `DmlsFinished` as "all good" | failed records missed — check the error file |
| Unbounded wait loop on the log status | a hung import passes silently |
| `groupBy` on independent rows | unbalanced chunks, slower than no grouping |
| Creating `DataManagerLog` rows directly | bypasses staging; no content/parameter rows; nothing else does this |

## Verify before declaring done

After building or changing anything MDM-related: run one real file
through, then read `DataManagerLogDetails` for the log — status
terminal, error file empty (or containing exactly the records you
expected to fail). "It uploaded" is not a result; the log row is.
