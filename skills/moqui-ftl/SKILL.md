---
name: moqui-ftl
description: Author or edit FreeMarker (FTL) templates and template-rendering code in Moqui while preserving the framework's worker/helper, context-building, and machine-output disciplines. Use when the user asks to create or change `*.ftl` files, generate text output (SQL, JSON, GraphQL, CSV, code, email) from templates, or render templates from services or scripts.
---

# Moqui FreeMarker (FTL)

FreeMarker in Moqui is the general text engine, not a screen tool: the framework compiles
XML actions to Groovy through one template, screens render to HTML/CSV/XSL-FO/text via
per-format macro libraries, and components generate SQL, GraphQL, rules, and JSON payloads
through it. Prefer a template + a context map over a new code module for "generate X from
data" needs — but only when the output is template-shaped (stable reviewable skeleton,
variable values). Building JSON from an arbitrary object graph is a serializer's job
(Jackson / `JsonBuilder` / `JsonOutput`), not FTL's.

## Procedure

1. Classify the output before writing anything: **human text** (HTML screen, email) or
   **machine syntax** (SQL, JSON, GraphQL, generated code, CSV). The defaults are tuned for
   human text; machine syntax needs every step below.
2. Read a nearby precedent first: the component's existing `*.ftl` and the Groovy/XML that
   renders it. Match its context-prep and helper conventions.
3. Build the full context BEFORE rendering. The caller assembles one map with everything
   the template reads; the template never fetches. Keep logic, lookups, formatting, and
   escaping in a Groovy/Java worker (or a `Static` helper) — templates interpolate
   finished strings.
4. Choose the render path by output class:
   - Human text in ambient context: `ec.resource.template(location, writer)` is fine.
   - Machine syntax: render against a **sealed plain Map** via
     `template.createProcessingEnvironment(map, writer)` on a private `Environment`
     (the framework's own codegen pattern in `XmlAction.getGroovyString`). Load the
     compiled template through the shared configuration
     (`...ftlTemplateRenderer.getFtlConfiguration().getTemplate(location)`) to keep
     caching and hot-reload.
5. For machine syntax, set on the private `Environment`:
   - `TemplateExceptionHandler.RETHROW_HANDLER` — the default Moqui handler writes
     `[Template Error: ...]` INTO the output and continues, which is silent corruption in
     machine output. RETHROW also hard-fails unbound/null placeholders.
   - `number_format="computer"` — the locale default renders `6906004000` as
     `6,906,004,000` inside SQL/JSON/ids, silently. Prefer converting numbers to plain
     Strings in the worker (`ObjectUtilities.toPlainString` idiom) and keep this setting
     as the safety net; `?c` per numeric expression is the in-template fallback.
6. Escape in the worker, not the template: JSON string content via
   `StringEscapeUtils.escapeJson` (commons-text is on the classpath), XML attributes via
   `StringUtilities.encodeForXmlAttribute`, CSV via a single wrapper macro. Templates
   should carry zero escaping syntax; in JSON templates, quoting is the type contract
   (`"${V}"` = string, unquoted = number/boolean/null).
7. Parse the output before using it: generated JSON through a JSON parser, generated
   Groovy through the compiler, generated SQL at least through the DB's prepare. The
   downstream parser is the cheapest validator and the framework's own precedent.
8. Run:
   - `python3 ../../scripts/moqui_quality_audit.py audit --root "<repo-root>" --paths "<changed-files>"`
9. Verify with the narrowest available command, and for machine output diff a rendered
   sample against a known-good capture.

## Guardrails

- Do not put `<#if>` / `<#list>` / `<#assign>` logic in data-like templates (payload
  goldens, config artifacts). Serialize variable-cardinality fragments in the worker
  (`JsonOutput.toJson`) and splice them as one placeholder. Macro *libraries* may be
  logic-rich; data templates must stay interpolation-only.
- Do not render machine syntax through `ec.resource.template` — it reads the ambient
  contextStack (a typo'd placeholder silently picks up an unrelated variable) and its
  error handler swallows failures into the output. It has no map-taking overload by
  design; that absence is the signal to switch patterns.
- Do not interpolate a raw Number into machine syntax. `${limit}` with an Integer ≥ 1000
  renders with locale grouping and the output often still parses — wrong values, no error.
- Do not escape per-field in templates with `?json_string`/`?js_string` when a worker can
  pre-escape the bound values once — per-field builtins are easy to miss on the next
  edit and the omission is invisible until data contains a quote.
- Do not use `<#ftl output_format="HTML">` plus an unescape round-trip on non-markup
  output — auto-escape formats fight machine syntax; fix the escaping at the source.
- Do not build response/API JSON with FTL; use the framework's serializers. FTL is for
  documents whose skeleton is worth versioning and reviewing.

## References

- Philosophy: `../../assets/moqui-authoring-philosophy.md`
- FreeMarker practices (mechanics + framework citations): `../../assets/moqui-freemarker-practices.md`
- Pitfalls: `../../assets/moqui-framework-pitfalls.md`
- Checklist: `../../assets/moqui-quality-checklist.md`
