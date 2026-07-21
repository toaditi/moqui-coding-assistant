#!/usr/bin/env python3
"""Validate the self-contained Antigravity plugin package in this repository."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path


RELATIVE_REFERENCE_RE = re.compile(r"`(\.\./\.\./[^`]+)`")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--root",
        type=Path,
        default=Path(__file__).resolve().parents[1],
        help="Repository root containing plugin manifests (default: this repository).",
    )
    return parser.parse_args()


def validate_manifest(root: Path, manifest_path: Path) -> list[str]:
    errors: list[str] = []
    if not manifest_path.is_file():
        return [f"missing Antigravity plugin manifest: {manifest_path}"]

    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return [f"cannot read Antigravity plugin manifest {manifest_path}: {exc}"]

    for field in ("name", "version", "skills"):
        if not manifest.get(field):
            errors.append(f"manifest {manifest_path.relative_to(root)} is missing required field: {field}")

    skills_rel = manifest.get("skills", "")
    skills_path = (manifest_path.parent / skills_rel).resolve()
    if not skills_path.is_dir():
        errors.append(f"manifest skills path is not a directory: {skills_path}")
        return errors

    for manifest_field in ("hooks", "mcpServers", "agents"):
        configured_path = manifest.get(manifest_field)
        if configured_path:
            target_path = (manifest_path.parent / configured_path).resolve()
            if not target_path.exists():
                errors.append(f"manifest {manifest_field} path does not exist: {configured_path} -> {target_path}")

    skill_dirs = sorted(path for path in skills_path.iterdir() if path.is_dir())
    if not skill_dirs:
        errors.append(f"no skill directories found under: {skills_path}")

    for skill_dir in skill_dirs:
        skill_file = skill_dir / "SKILL.md"
        if not skill_file.is_file():
            errors.append(f"missing SKILL.md: {skill_file.relative_to(root)}")
            continue
        try:
            text = skill_file.read_text(encoding="utf-8")
        except OSError as exc:
            errors.append(f"cannot read {skill_file.relative_to(root)}: {exc}")
            continue
        for reference in RELATIVE_REFERENCE_RE.findall(text):
            target = (skill_dir / reference).resolve()
            if not target.is_file():
                errors.append(
                    f"missing reference from {skill_file.relative_to(root)}: "
                    f"{reference} -> {target}"
                )

    return errors


def validate(root: Path) -> list[str]:
    errors: list[str] = []
    
    # Validate root plugin.json
    root_manifest = root / "plugin.json"
    errors.extend(validate_manifest(root, root_manifest))

    # Validate .antigravity-plugin/plugin.json
    antigravity_manifest = root / ".antigravity-plugin" / "plugin.json"
    errors.extend(validate_manifest(root, antigravity_manifest))

    # Validate .agents/plugin.json
    agents_manifest = root / ".agents" / "plugin.json"
    errors.extend(validate_manifest(root, agents_manifest))

    return errors


def main() -> int:
    args = parse_args()
    root = args.root.resolve()
    errors = validate(root)
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        print(f"Antigravity plugin validation failed with {len(errors)} error(s).", file=sys.stderr)
        return 1
    print(f"Antigravity plugin validation passed: {root}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
