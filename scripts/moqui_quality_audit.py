#!/usr/bin/env python3
"""Index and audit Moqui repositories for common quality issues."""

from __future__ import annotations

import argparse
import json
import re
import sys
import xml.etree.ElementTree as ET
from collections import defaultdict
from pathlib import Path


SKIP_DIRS = {
    ".git",
    ".gradle",
    ".idea",
    ".vscode",
    "build",
    "dist",
    "node_modules",
    "coverage",
    "target",
    "tmp",
    "execwartmp",
}

TEXT_PATTERNS = [
    ("warn", "println", re.compile(r"(?<![\w.])println\b"), "Avoid plain println in production Moqui code."),
    ("warn", "system-out", re.compile(r"\bSystem\.out\.println\s*\("), "Avoid System.out.println in production code."),
    ("warn", "print-stack-trace", re.compile(r"\bprintStackTrace\s*\("), "Avoid printStackTrace; use framework logging instead."),
    ("info", "todo", re.compile(r"\bTODO\b"), "Resolve TODO markers or link them to tracked follow-up work."),
    ("info", "fixme", re.compile(r"\bFIXME\b"), "Resolve FIXME markers or link them to tracked follow-up work."),
]

ATTR_RE = re.compile(r'([A-Za-z_][\w:.-]*)="([^"]*)"')

# Maximum non-blank lines allowed inside an inline <script> block within a <service>'s
# <actions>. Above this, the audit flags `service-inline-script-large` and the logic
# should be refactored into XML actions or extracted to a script/*.groovy file.
INLINE_SCRIPT_MAX_LINES = 20

SCRIPT_BLOCK_RE = re.compile(r"<script\b[^>]*>([\s\S]*?)</script>", re.DOTALL)
CDATA_WRAPPER_RE = re.compile(r"<!\[CDATA\[|\]\]>")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    for command in ("audit", "index"):
        sub = subparsers.add_parser(command)
        sub.add_argument("--root", required=True, help="Repository or component root to scan.")
        sub.add_argument(
            "--paths",
            nargs="*",
            default=[],
            help="Optional files or directories under --root to narrow the scan.",
        )
        sub.add_argument("--format", choices=("text", "json"), default="text")

    index_parser = subparsers.choices["index"]
    index_parser.add_argument(
        "--kind",
        choices=("all", "service", "entity", "screen", "form", "transition"),
        default="all",
    )
    index_parser.add_argument("--query", default="", help="Case-insensitive substring filter.")
    return parser.parse_args()


def resolve_targets(root: Path, raw_paths: list[str]) -> list[Path]:
    if not raw_paths:
        return [root]

    targets: list[Path] = []
    for raw_path in raw_paths:
        candidate = Path(raw_path)
        if not candidate.is_absolute():
            candidate = root / candidate
        if candidate.exists():
            targets.append(candidate.resolve())
    return targets or [root]


def iter_files(root: Path, targets: list[Path]) -> list[Path]:
    files: list[Path] = []
    for target in targets:
        if target.is_file():
            files.append(target)
            continue
        for path in target.rglob("*"):
            if any(part in SKIP_DIRS for part in path.parts):
                continue
            if path.is_file() and path.suffix.lower() in {".xml", ".groovy", ".java"}:
                files.append(path)
    unique_files = sorted({path.resolve() for path in files if path.exists()})
    return [path for path in unique_files if root in path.parents or path == root]


def relative_to_root(path: Path, root: Path) -> str:
    try:
        return str(path.relative_to(root))
    except ValueError:
        return str(path)


def line_for_offset(text: str, offset: int) -> int:
    return text.count("\n", 0, offset) + 1


def parse_attrs(tag_text: str) -> dict[str, str]:
    return {match.group(1): match.group(2) for match in ATTR_RE.finditer(tag_text)}


def namespace_from_service_path(path: Path, root: Path) -> str:
    relative = path.relative_to(root)
    parts = list(relative.parts)
    if "service" not in parts:
        return path.stem
    service_index = parts.index("service")
    namespace_parts = parts[service_index + 1 : -1] + [path.stem]
    return ".".join(namespace_parts) if namespace_parts else path.stem


def screen_name_from_path(path: Path, root: Path) -> str:
    relative = path.relative_to(root)
    parts = list(relative.parts)
    if "screen" not in parts:
        return path.stem
    screen_index = parts.index("screen")
    screen_parts = parts[screen_index + 1 :]
    if screen_parts:
        screen_parts[-1] = Path(screen_parts[-1]).stem
    return "/".join(screen_parts) if screen_parts else path.stem


def make_finding(severity: str, code: str, path: Path, line: int, message: str, root: Path) -> dict[str, object]:
    return {
        "severity": severity,
        "code": code,
        "path": str(path),
        "relativePath": relative_to_root(path, root),
        "line": line,
        "message": message,
    }


def add_symbol(symbols: list[dict[str, object]], kind: str, name: str, path: Path, line: int, root: Path) -> None:
    symbols.append(
        {
            "kind": kind,
            "name": name,
            "path": str(path),
            "relativePath": relative_to_root(path, root),
            "line": line,
        }
    )


def scan_service_file(path: Path, root: Path, findings: list[dict[str, object]], symbols: list[dict[str, object]]) -> None:
    text = path.read_text(encoding="utf-8", errors="replace")
    namespace = namespace_from_service_path(path, root)
    pattern = re.compile(r"<service(?!-)\b[^>]*>", re.DOTALL)

    for match in pattern.finditer(text):
        attrs = parse_attrs(match.group(0))
        line = line_for_offset(text, match.start())
        service_id = attrs.get("name")
        if not service_id:
            verb = attrs.get("verb")
            noun = attrs.get("noun")
            if verb and noun:
                service_id = f"{verb}#{noun}"
        if not service_id:
            findings.append(make_finding("warn", "service-name-missing", path, line, "Service definition is missing both `name` and `verb`/`noun`.", root))
            continue

        full_name = f"{namespace}.{service_id}"
        add_symbol(symbols, "service", full_name, path, line, root)

        end_tag = text.find("</service>", match.end())
        block = text[match.start() : end_tag if end_tag != -1 else match.end()]
        if "<description>" not in block:
            findings.append(make_finding("info", "service-description-missing", path, line, f"Service `{full_name}` is missing a `<description>` block.", root))

        if "process" in service_id.lower():
            findings.append(make_finding("info", "service-name-process", path, line, f"Service `{full_name}` uses `process` in its name.", root))

        allow_remote = attrs.get("allow-remote")
        authenticate = attrs.get("authenticate", "true")
        if allow_remote == "true" and authenticate in {"false", "anonymous-all"}:
            findings.append(make_finding("warn", "service-public-remote", path, line, f"Remote service `{full_name}` is exposed with authenticate=`{authenticate}`.", root))

        # Skip script-type services entirely — the whole "body" lives in an external groovy file.
        if attrs.get("type") == "script":
            continue
        for script_match in SCRIPT_BLOCK_RE.finditer(block):
            body = CDATA_WRAPPER_RE.sub("", script_match.group(1))
            nonblank = sum(1 for body_line in body.splitlines() if body_line.strip())
            if nonblank > INLINE_SCRIPT_MAX_LINES:
                script_line = line_for_offset(text, match.start() + script_match.start())
                findings.append(
                    make_finding(
                        "warn",
                        "service-inline-script-large",
                        path,
                        script_line,
                        (
                            f"Inline `<script>` in service `{full_name}` has {nonblank} non-blank lines "
                            f"(threshold {INLINE_SCRIPT_MAX_LINES}). Refactor into XML actions, or extract "
                            f"to a `script/*.groovy` file referenced via `type=\"script\" location=\"...\"`."
                        ),
                        root,
                    )
                )


def scan_entity_file(path: Path, root: Path, findings: list[dict[str, object]], symbols: list[dict[str, object]]) -> None:
    text = path.read_text(encoding="utf-8", errors="replace")
    pattern = re.compile(r"<(entity|view-entity)\b[^>]*>", re.DOTALL)

    for match in pattern.finditer(text):
        tag_name = match.group(1)
        attrs = parse_attrs(match.group(0))
        line = line_for_offset(text, match.start())
        entity_name = attrs.get("entity-name") or attrs.get("name")
        if not entity_name:
            continue
        package = attrs.get("package")
        full_name = f"{package}.{entity_name}" if package else entity_name
        add_symbol(symbols, "entity", full_name, path, line, root)

        closing_tag = f"</{tag_name}>"
        end_tag = text.find(closing_tag, match.end())
        block = text[match.start() : end_tag if end_tag != -1 else match.end()]
        if "<description>" not in block:
            findings.append(make_finding("info", "entity-description-missing", path, line, f"Entity `{full_name}` is missing a `<description>` block.", root))
        if not attrs.get("short-alias"):
            findings.append(make_finding("info", "entity-short-alias-missing", path, line, f"Entity `{full_name}` is missing `short-alias`.", root))

        for relation_match in re.finditer(r"<relationship\b[^>]*>", block, re.DOTALL):
            rel_attrs = parse_attrs(relation_match.group(0))
            rel_type = rel_attrs.get("type")
            if rel_type in {"one", "many"} and not rel_attrs.get("short-alias"):
                relation_line = line_for_offset(text, match.start() + relation_match.start())
                related = rel_attrs.get("related", "unknown-related")
                findings.append(
                    make_finding(
                        "info",
                        "relationship-short-alias-missing",
                        path,
                        relation_line,
                        f"Relationship to `{related}` in entity `{full_name}` is missing `short-alias`.",
                        root,
                    )
                )


def scan_screen_file(path: Path, root: Path, findings: list[dict[str, object]], symbols: list[dict[str, object]]) -> None:
    text = path.read_text(encoding="utf-8", errors="replace")
    screen_name = screen_name_from_path(path, root)

    screen_match = re.search(r"<screen\b[^>]*>", text, re.DOTALL)
    if screen_match:
        add_symbol(symbols, "screen", screen_name, path, line_for_offset(text, screen_match.start()), root)

    transition_names: defaultdict[str, list[int]] = defaultdict(list)
    form_names: defaultdict[str, list[int]] = defaultdict(list)

    for match in re.finditer(r"<transition\b[^>]*name=\"([^\"]+)\"[^>]*>", text, re.DOTALL):
        line = line_for_offset(text, match.start())
        name = match.group(1)
        transition_names[name].append(line)
        add_symbol(symbols, "transition", f"{screen_name}::{name}", path, line, root)
        if "process" in name.lower():
            findings.append(make_finding("info", "transition-name-process", path, line, f"Transition `{name}` uses `process` in its name.", root))

    for match in re.finditer(r"<form-(?:single|list)\b[^>]*name=\"([^\"]+)\"[^>]*>", text, re.DOTALL):
        line = line_for_offset(text, match.start())
        name = match.group(1)
        form_names[name].append(line)
        add_symbol(symbols, "form", f"{screen_name}::{name}", path, line, root)

    for name, lines in transition_names.items():
        if len(lines) > 1:
            findings.append(make_finding("warn", "duplicate-transition", path, lines[0], f"Transition `{name}` is defined multiple times in the same screen.", root))
    for name, lines in form_names.items():
        if len(lines) > 1:
            findings.append(make_finding("warn", "duplicate-form", path, lines[0], f"Form `{name}` is defined multiple times in the same screen.", root))

    # `condition` is silently dropped on <container>/<container-box> (not in xml-screen-3.xsd);
    # the container always renders. Use a <section condition="..."> wrapper instead.
    for match in re.finditer(r"<container(?:-box)?\b[^>]*\bcondition=\"[^\"]*\"[^>]*>", text, re.DOTALL):
        line = line_for_offset(text, match.start())
        findings.append(
            make_finding(
                "warn",
                "screen-container-condition",
                path,
                line,
                "`condition` is ignored on `<container>`/`<container-box>` and the block always renders. "
                "Wrap it in `<section name=\"...\" condition=\"...\">` instead.",
                root,
            )
        )

    # <list-options> key/text are expand strings, not field names. A bare value like
    # key="endpoint" renders the literal word, never the row's field; it must be ${endpoint}.
    for match in re.finditer(r"<list-options\b[^>]*>", text, re.DOTALL):
        attrs = parse_attrs(match.group(0))
        line = line_for_offset(text, match.start())
        for attr in ("key", "text"):
            value = attrs.get(attr)
            if value and "${" not in value:
                findings.append(
                    make_finding(
                        "warn",
                        "screen-list-options-literal",
                        path,
                        line,
                        f"`<list-options {attr}=\"{value}\">` is a literal string, not a field reference. "
                        f"Interpolate the row field as `{attr}=\"${{{value}}}\"`.",
                        root,
                    )
                )


def scan_text_patterns(path: Path, root: Path, findings: list[dict[str, object]]) -> None:
    text = path.read_text(encoding="utf-8", errors="replace")
    for severity, code, pattern, message in TEXT_PATTERNS:
        if code == "println" and path.suffix.lower() == ".xml":
            continue
        for match in pattern.finditer(text):
            findings.append(make_finding(severity, code, path, line_for_offset(text, match.start()), message, root))


def scan_xml_parse(path: Path, root: Path, findings: list[dict[str, object]]) -> None:
    try:
        ET.parse(path)
    except ET.ParseError as exc:
        line = exc.position[0] if hasattr(exc, "position") and exc.position else 1
        findings.append(make_finding("error", "xml-parse", path, line, str(exc), root))


def collect(root: Path, targets: list[Path]) -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    findings: list[dict[str, object]] = []
    symbols: list[dict[str, object]] = []
    files = iter_files(root, targets)

    for path in files:
        suffix = path.suffix.lower()
        if suffix == ".xml":
            scan_xml_parse(path, root, findings)
            parts = path.parts
            if "service" in parts:
                scan_service_file(path, root, findings, symbols)
            if "entity" in parts:
                scan_entity_file(path, root, findings, symbols)
            if "screen" in parts:
                scan_screen_file(path, root, findings, symbols)
        scan_text_patterns(path, root, findings)

    service_defs: defaultdict[str, list[dict[str, object]]] = defaultdict(list)
    entity_defs: defaultdict[str, list[dict[str, object]]] = defaultdict(list)
    for symbol in symbols:
        if symbol["kind"] == "service":
            service_defs[str(symbol["name"])].append(symbol)
        elif symbol["kind"] == "entity":
            entity_defs[str(symbol["name"])].append(symbol)

    for name, defs in service_defs.items():
        if len(defs) > 1:
            first = defs[0]
            findings.append(
                make_finding(
                    "warn",
                    "duplicate-service",
                    Path(str(first["path"])),
                    int(first["line"]),
                    f"Service `{name}` is defined {len(defs)} times in the scan scope.",
                    root,
                )
            )
    for name, defs in entity_defs.items():
        if len(defs) > 1:
            first = defs[0]
            findings.append(
                make_finding(
                    "warn",
                    "duplicate-entity",
                    Path(str(first["path"])),
                    int(first["line"]),
                    f"Entity `{name}` is defined {len(defs)} times in the scan scope.",
                    root,
                )
            )

    severity_order = {"error": 0, "warn": 1, "info": 2}
    findings.sort(key=lambda item: (severity_order.get(str(item["severity"]), 9), str(item["relativePath"]), int(item["line"])))
    symbols.sort(key=lambda item: (str(item["kind"]), str(item["name"]), str(item["relativePath"]), int(item["line"])))
    return findings, symbols


def render_text_findings(findings: list[dict[str, object]]) -> str:
    if not findings:
        return "No findings."
    return "\n".join(
        f"{finding['severity'].upper():5} {finding['code']:24} {finding['relativePath']}:{finding['line']} {finding['message']}"
        for finding in findings
    )


def render_text_symbols(symbols: list[dict[str, object]]) -> str:
    if not symbols:
        return "No symbols."
    return "\n".join(
        f"{symbol['kind']:10} {symbol['name']}  {symbol['relativePath']}:{symbol['line']}"
        for symbol in symbols
    )


def main() -> int:
    args = parse_args()
    root = Path(args.root).resolve()
    targets = resolve_targets(root, args.paths)
    findings, symbols = collect(root, targets)

    if args.command == "audit":
        payload = {"root": str(root), "targets": [str(target) for target in targets], "findings": findings}
        if args.format == "json":
            print(json.dumps(payload, indent=2))
        else:
            print(render_text_findings(findings))
        return 1 if any(finding["severity"] in {"error", "warn"} for finding in findings) else 0

    query = args.query.lower()
    filtered = []
    for symbol in symbols:
        if args.kind != "all" and symbol["kind"] != args.kind:
            continue
        if query and query not in str(symbol["name"]).lower():
            continue
        filtered.append(symbol)

    payload = {"root": str(root), "targets": [str(target) for target in targets], "symbols": filtered}
    if args.format == "json":
        print(json.dumps(payload, indent=2))
    else:
        print(render_text_symbols(filtered))
    return 0


if __name__ == "__main__":
    sys.exit(main())
