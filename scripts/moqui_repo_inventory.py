#!/usr/bin/env python3
"""Inventory Moqui repository components, integration surfaces, and operations."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
import xml.etree.ElementTree as ET


INTERESTING_TASK_PREFIXES = (
    "get",
    "git",
    "load",
    "deploy",
    "zip",
    "addRuntime",
    "run",
    "clean",
    "createComponent",
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    for command in ("summary", "components", "integrations", "ops"):
        sub = subparsers.add_parser(command)
        sub.add_argument("--root", required=True, help="Moqui backend root containing build.gradle and runtime/component.")
        sub.add_argument("--format", choices=("text", "json"), default="text")
    return parser.parse_args()


def rel(path: Path, root: Path) -> str:
    return str(path.relative_to(root))


def line_for_offset(text: str, offset: int) -> int:
    return text.count("\n", 0, offset) + 1


def count_files(path: Path, suffixes: tuple[str, ...]) -> int:
    if not path.exists():
        return 0
    return sum(1 for candidate in path.rglob("*") if candidate.is_file() and candidate.suffix.lower() in suffixes)


def find_component_dirs(root: Path) -> list[Path]:
    component_root = root / "runtime" / "component"
    if not component_root.exists():
        return []
    return sorted(path for path in component_root.iterdir() if path.is_dir())


def collect_components(root: Path) -> list[dict[str, object]]:
    components = []
    for component_dir in find_component_dirs(root):
        component_xml = component_dir / "component.xml"
        record: dict[str, object] = {
            "directory": component_dir.name,
            "path": rel(component_dir, root),
            "componentXml": component_xml.exists(),
            "entityFiles": count_files(component_dir / "entity", (".xml",)),
            "serviceFiles": count_files(component_dir / "service", (".xml",)),
            "screenFiles": count_files(component_dir / "screen", (".xml",)),
            "dataFiles": count_files(component_dir / "data", (".xml",)),
            "scriptFiles": count_files(component_dir / "script", (".groovy",)),
            "sourceFiles": count_files(component_dir / "src", (".groovy", ".java", ".kt")),
        }
        if component_xml.exists():
            try:
                node = ET.parse(component_xml).getroot()
                record["name"] = node.attrib.get("name", component_dir.name)
                record["version"] = node.attrib.get("version", "")
                record["declaresEntity"] = any(child.tag.endswith("entity-file") for child in node)
                record["declaresService"] = any(child.tag.endswith("service-directory") for child in node)
                record["declaresScreen"] = any(child.tag.endswith("screen-file") for child in node)
            except ET.ParseError as exc:
                record["parseError"] = str(exc)
        else:
            record["name"] = component_dir.name
            record["version"] = ""
        components.append(record)
    return components


def service_id_from_attrs(attrs: dict[str, str], namespace: str) -> str | None:
    if "name" in attrs:
        return f"{namespace}.{attrs['name']}"
    if "verb" in attrs and "noun" in attrs:
        return f"{namespace}.{attrs['verb']}#{attrs['noun']}"
    return None


def collect_integrations(root: Path) -> dict[str, object]:
    component_root = root / "runtime" / "component"
    if not component_root.exists():
        return {"remoteServices": [], "systemMessageRecords": [], "outboundRestCalls": [], "restXmlFiles": []}

    remote_services = []
    system_messages = []
    outbound_rest_calls = []
    rest_xml_files = []

    for path in sorted(component_root.rglob("*")):
        if not path.is_file():
            continue
        if path.suffix.lower() == ".xml":
            text = path.read_text(encoding="utf-8", errors="replace")
            if path.name.endswith(".rest.xml"):
                rest_xml_files.append({"path": rel(path, root)})
            if "/service/" in path.as_posix():
                namespace_parts = list(path.relative_to(root).parts)
                if "service" in namespace_parts:
                    service_index = namespace_parts.index("service")
                    namespace = ".".join(namespace_parts[service_index + 1 : -1] + [path.stem])
                else:
                    namespace = path.stem
                for match in re.finditer(r"<service(?!-)\b[^>]*>", text, re.DOTALL):
                    attrs = {m.group(1): m.group(2) for m in re.finditer(r'([A-Za-z_][\w:.-]*)="([^"]*)"', match.group(0))}
                    service_name = service_id_from_attrs(attrs, namespace)
                    if not service_name:
                        continue
                    if attrs.get("allow-remote") == "true" or attrs.get("type") in {"remote-rest", "rest"}:
                        remote_services.append(
                            {
                                "service": service_name,
                                "path": rel(path, root),
                                "line": line_for_offset(text, match.start()),
                                "authenticate": attrs.get("authenticate", "true"),
                                "allowRemote": attrs.get("allow-remote", "false"),
                                "type": attrs.get("type", ""),
                            }
                        )
            if "/data/" in path.as_posix():
                for match in re.finditer(
                    r"<(moqui\.service\.message\.SystemMessageType|moqui\.service\.message\.SystemMessageRemote|moqui\.service\.message\.SystemMessage)\b[^>]*>",
                    text,
                    re.DOTALL,
                ):
                    tag = match.group(1)
                    attrs = {m.group(1): m.group(2) for m in re.finditer(r'([A-Za-z_][\w:.-]*)="([^"]*)"', match.group(0))}
                    record_id = attrs.get("systemMessageTypeId") or attrs.get("systemMessageRemoteId") or attrs.get("systemMessageId", "")
                    system_messages.append(
                        {
                            "kind": tag.split(".")[-1],
                            "id": record_id,
                            "path": rel(path, root),
                            "line": line_for_offset(text, match.start()),
                        }
                    )
        elif path.suffix.lower() == ".groovy":
            text = path.read_text(encoding="utf-8", errors="replace")
            for match in re.finditer(r"ec\.service\.rest\s*\(", text):
                outbound_rest_calls.append(
                    {
                        "path": rel(path, root),
                        "line": line_for_offset(text, match.start()),
                    }
                )

    return {
        "remoteServices": remote_services,
        "systemMessageRecords": system_messages,
        "outboundRestCalls": outbound_rest_calls,
        "restXmlFiles": rest_xml_files,
    }


def collect_ops(root: Path) -> list[dict[str, str]]:
    build_file = root / "build.gradle"
    if not build_file.exists():
        return []
    text = build_file.read_text(encoding="utf-8", errors="replace")
    tasks = []
    task_regex = re.compile(r"^\s*task\s+([A-Za-z_]\w*)", re.MULTILINE)
    descriptions = {m.group(1): m.group(2).strip() for m in re.finditer(r'^\s*task\s+([A-Za-z_]\w*).*?\n\s*description\s+"([^"]+)"', text, re.MULTILINE)}
    for match in task_regex.finditer(text):
        name = match.group(1)
        if name.startswith(INTERESTING_TASK_PREFIXES) or name in {"checkRuntime"}:
            tasks.append(
                {
                    "task": name,
                    "description": descriptions.get(name, ""),
                }
            )
    unique = []
    seen = set()
    for task in tasks:
        if task["task"] in seen:
            continue
        seen.add(task["task"])
        unique.append(task)
    return unique


def collect_summary(root: Path) -> dict[str, object]:
    components = collect_components(root)
    integrations = collect_integrations(root)
    ops = collect_ops(root)
    return {
        "backendRoot": str(root),
        "componentCount": len(components),
        "components": components,
        "integrationCounts": {
            "remoteServices": len(integrations["remoteServices"]),
            "systemMessageRecords": len(integrations["systemMessageRecords"]),
            "outboundRestCalls": len(integrations["outboundRestCalls"]),
            "restXmlFiles": len(integrations["restXmlFiles"]),
        },
        "opsCount": len(ops),
    }


def render_components(components: list[dict[str, object]]) -> str:
    if not components:
        return "No components found."
    return "\n".join(
        f"{component['name']}  {component['path']}  entities={component['entityFiles']} services={component['serviceFiles']} screens={component['screenFiles']} scripts={component['scriptFiles'] + component['sourceFiles']}"
        for component in components
    )


def render_integrations(integrations: dict[str, object]) -> str:
    lines = []
    remote_services = integrations["remoteServices"]
    system_messages = integrations["systemMessageRecords"]
    outbound_rest_calls = integrations["outboundRestCalls"]
    rest_xml_files = integrations["restXmlFiles"]
    lines.append(f"Remote services: {len(remote_services)}")
    for item in remote_services[:20]:
        lines.append(f"  {item['service']}  {item['path']}:{item['line']} auth={item['authenticate']} type={item['type'] or 'script'}")
    lines.append(f"System message records: {len(system_messages)}")
    for item in system_messages[:20]:
        lines.append(f"  {item['kind']} {item['id']}  {item['path']}:{item['line']}")
    lines.append(f"Outbound rest calls: {len(outbound_rest_calls)}")
    for item in outbound_rest_calls[:20]:
        lines.append(f"  {item['path']}:{item['line']}")
    lines.append(f"REST XML files: {len(rest_xml_files)}")
    for item in rest_xml_files[:20]:
        lines.append(f"  {item['path']}")
    return "\n".join(lines)


def render_ops(ops: list[dict[str, str]]) -> str:
    if not ops:
        return "No build.gradle tasks found."
    return "\n".join(f"{task['task']}  {task['description']}".rstrip() for task in ops)


def main() -> int:
    args = parse_args()
    root = Path(args.root).resolve()

    if args.command == "summary":
        payload = collect_summary(root)
    elif args.command == "components":
        payload = {"backendRoot": str(root), "components": collect_components(root)}
    elif args.command == "integrations":
        payload = {"backendRoot": str(root), **collect_integrations(root)}
    else:
        payload = {"backendRoot": str(root), "ops": collect_ops(root)}

    if args.format == "json":
        print(json.dumps(payload, indent=2))
        return 0

    if args.command == "summary":
        summary = payload
        print(
            f"Backend root: {summary['backendRoot']}\n"
            f"Components: {summary['componentCount']}\n"
            f"Remote services: {summary['integrationCounts']['remoteServices']}\n"
            f"System message records: {summary['integrationCounts']['systemMessageRecords']}\n"
            f"Outbound rest calls: {summary['integrationCounts']['outboundRestCalls']}\n"
            f"REST XML files: {summary['integrationCounts']['restXmlFiles']}\n"
            f"Operational tasks: {summary['opsCount']}"
        )
    elif args.command == "components":
        print(render_components(payload["components"]))
    elif args.command == "integrations":
        print(render_integrations(payload))
    else:
        print(render_ops(payload["ops"]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
