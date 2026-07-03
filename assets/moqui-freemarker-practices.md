# Moqui FreeMarker Practices

How FreeMarker is actually used across the Moqui framework, and the discipline required
when a template emits machine syntax. Citations reference moqui-framework / moqui-runtime
source (verified against 3.x). Companion skill: `skills/moqui-ftl/SKILL.md`.

## What FTL is in Moqui

FreeMarker is the framework's general text-transformation engine, not a page renderer:

- **A compiler.** The XML-actions mini-language compiles to Groovy source through ONE
  template (`framework/src/main/resources/template/XmlActions.groovy.ftl`); the result is
  compiled by groovyc and cached (`XmlAction.java`). Every declarative service body passes
  through it.
- **A multi-target document renderer.** One screen definition renders through per-format
  macro libraries: `runtime/template/screen-macro/DefaultScreenMacros.html.ftl`, `.csv.ftl`,
  `.xsl-fo.ftl` (PDF), `.text.ftl`, and the Vue-oriented variants.
- **A machine-syntax generator.** Components in the ecosystem render SQL queries, GraphQL
  documents, rules files, CSV exports, and JSON payloads through the same engine.

Decision rule: FTL wins when the output is a *document with a stable, reviewable skeleton
and variable values*. Arbitrary object graphs (REST responses) go through Jackson /
`JsonBuilder` — the framework itself does this (`WebFacadeImpl`, `RestClient`).

## Pattern 1 — Workers think, templates type

All non-trivial work is delegated to a helper object in the context; templates splice
finished strings.

- Screen macros call `sri` (ScreenRenderImpl) for everything: value extraction and
  formatting via `getFieldValueString` / `getFieldValuePlainString`
  (`ScreenRenderImpl.groovy` ~1498-1527), URL building, entity lookups. Side-effect
  methods return `""` so `${sri.startFormListRow(...)}` emits nothing.
- Java statics reach templates through the configuration-level `Static` shared variable
  (`FtlTemplateRenderer.java` ~120) — helpers build the syntax-varying fragment (a SQL
  WHERE clause, a mapping lookup); the template holds the readable skeleton.
- The html macros use `getFieldValuePlainString` with an explicit comment — "so we don't
  do timezone conversions, etc" — values reach FTL pre-formatted as Strings.
- Variable-cardinality substructures: serialize the whole fragment in the worker
  (`groovy.json.JsonOutput.toJson`) and bind it as ONE placeholder spliced unquoted.
  Never `<#list>` inside a data-like template.

## Pattern 2 — Build the context first; seal it for machine output

The caller assembles one map of everything the template needs, then renders; the template
only reads.

- The framework's own parsed-output path uses a **sealed plain Map**:
  `XmlAction.getGroovyString` builds `new HashMap<>(1)`, then
  `template.createProcessingEnvironment(root, writer)` on a private `Environment`
  (`XmlAction.java` ~114-119). Configuration-level `Static` remains available.
- `ec.resource.template(location, writer)` renders against the ambient contextStack
  (`FtlTemplateRenderer.java` ~61) and has NO map-taking overload
  (`ResourceFacade.java` ~48-51) — by design. Correct for screens and email; wrong for
  deterministic machine output, where a typo'd placeholder can silently resolve to an
  unrelated ambient variable.
- `ContextStack.pushContext()/popContext()` is the heavier in-stack isolation idiom
  (used by the service runners); for template rendering the sealed-Map shape is simpler
  and matches the codegen precedent.

## Pattern 3 — Fail loud

The default `MoquiTemplateExceptionHandler` (installed once on the shared Configuration,
`FtlTemplateRenderer.java` ~139, ~193-227) writes `[Template Error: ...]` INTO THE OUTPUT
and continues — it never rethrows. For a web page that is graceful degradation; for
machine output it is silent corruption (the marker can land inside a quoted string and the
result still parses).

- On machine-output renders, set `TemplateExceptionHandler.RETHROW_HANDLER` on the private
  `Environment` before `process()` — the exact hook the codegen path exposes.
- FTL treats a null binding as *missing*, so RETHROW also enforces hard-fail-on-unbound —
  stricter than string substitution, and usually what a generator wants. If a template
  legitimately needs a JSON `null`, bind the literal string `null` into an unquoted
  placeholder as an explicit convention.
- The framework's own compensations are downstream and worth copying: its screen-test
  harness scans rendered output for the `[Template Error` marker, and the codegen path
  lets corrupted output fail the Groovy compiler loudly.

## Pattern 4 — Parse the output

The downstream parser is the cheapest validator you can deploy. Generated Groovy fails
groovyc; generated JSON must go through a JSON parser (`JsonSlurper.parseText`) immediately
after render, with parse failure treated as render failure. This is established component
practice for JSON-emitting templates and catches everything the other guards miss.

## Pattern 5 — The locale number trap

FreeMarker's default `number_format` is locale-sensitive human formatting: interpolating
the number `6906004000` renders `6,906,004,000`. In HTML that is a feature; inside a SQL
`LIMIT`, a JSON id, or generated code it is a wrong-values bug that usually still parses.
Real-world instance: a query template interpolating an Integer batch size broke only when
the batch crossed 1000 — dormant until then, then a syntax error in production.

The framework never sets `number_format` globally (`makeFtlConfiguration`,
`FtlTemplateRenderer.java` ~116-144, configures object wrapper, `Static`, the exception
handler, whitespace, UTF-8 — not number format), so protection is per-site, in preference
order:

1. Convert Numbers to plain Strings in the worker (`ObjectUtilities.toPlainString` — no
   grouping, no scientific notation) so the engine never formats them.
2. `?c` (computer format) on any numeric expression in machine syntax — the pattern the
   macro libraries themselves use where numbers land in JS/JSON positions.
3. `number_format="computer"` on the private `Environment` as a belt-and-suspenders
   default for the whole render.

## Escaping — in the worker, not the template

- Established per-syntax idioms: one wrapper per output syntax (a `csvValue` macro for CSV;
  `StringUtilities.encodeForXmlAttribute` for XML attributes; `?js_string` at JS sites in
  the html macros).
- For JSON: escape String content in the binder/worker
  (`org.apache.commons.text.StringEscapeUtils.escapeJson`; commons-text is already a
  dependency), numbers via `toPlainString`, booleans as literals. Templates then carry
  zero escaping syntax, and JSON quoting in the template is the visible type contract:
  `"${V}"` renders a string regardless of the bound Java type — which also eliminates the
  Long-vs-String class of downstream bugs.
- Anti-pattern seen in the wild: `<#ftl output_format="HTML">` plus an HTML-unescape
  round-trip on non-markup output. Auto-escape output formats fight machine syntax; fix
  escaping at the source instead.

## Template loading

Load through the shared configuration for caching + hot-reload:
`...ftlTemplateRenderer.getFtlConfiguration().getTemplate(location)` — the Moqui
Configuration override resolves `component://` locations and caches compiled templates
with lastModified invalidation (`FtlTemplateRenderer.java` ~153-169). Rendering from a
String uses `new Template(name, new StringReader(s), conf)`; if includes may ever be used,
the template name must look like a plain filename.
