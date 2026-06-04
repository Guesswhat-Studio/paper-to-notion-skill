#!/usr/bin/env python3
"""Validate repository packaging for Codex and Claude plugin installs."""

from __future__ import annotations

import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PLUGIN_ROOT = ROOT / "plugins" / "paper-to-notion"
PLUGIN_SKILL = PLUGIN_ROOT / "skills" / "paper-to-notion-skill"


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def read_json(path: Path, errors: list[str]) -> dict:
    try:
        with path.open("r", encoding="utf-8") as handle:
            data = json.load(handle)
    except Exception as exc:  # noqa: BLE001 - report all parse/read failures together.
        errors.append(f"{rel(path)} is not valid JSON: {exc}")
        return {}
    if not isinstance(data, dict):
        errors.append(f"{rel(path)} must contain a JSON object")
        return {}
    return data


def assert_exists(path: Path, errors: list[str]) -> None:
    if not path.exists():
        errors.append(f"Missing required file: {rel(path)}")


def assert_same(root_path: Path, plugin_path: Path, errors: list[str]) -> None:
    if not root_path.exists():
        errors.append(f"Missing source file: {rel(root_path)}")
        return
    if not plugin_path.exists():
        errors.append(f"Missing plugin copy: {rel(plugin_path)}")
        return
    if root_path.read_bytes() != plugin_path.read_bytes():
        errors.append(f"Plugin copy is out of sync: {rel(plugin_path)} should match {rel(root_path)}")


def validate_manifests(errors: list[str]) -> None:
    marketplace_path = ROOT / ".claude-plugin" / "marketplace.json"
    plugin_manifest_path = PLUGIN_ROOT / ".claude-plugin" / "plugin.json"
    marketplace = read_json(marketplace_path, errors)
    plugin = read_json(plugin_manifest_path, errors)

    if marketplace.get("name") != "guesswhat-paper-tools":
        errors.append(".claude-plugin/marketplace.json name must be guesswhat-paper-tools")

    plugins = marketplace.get("plugins")
    if not isinstance(plugins, list) or not plugins:
        errors.append(".claude-plugin/marketplace.json must list at least one plugin")
    else:
        paper_plugin = next((item for item in plugins if isinstance(item, dict) and item.get("name") == "paper-to-notion"), None)
        if paper_plugin is None:
            errors.append("Marketplace must include paper-to-notion")
        elif paper_plugin.get("source") != "./plugins/paper-to-notion":
            errors.append("paper-to-notion marketplace source must be ./plugins/paper-to-notion")

    if plugin.get("name") != "paper-to-notion":
        errors.append("plugins/paper-to-notion/.claude-plugin/plugin.json name must be paper-to-notion")
    if plugin.get("license") != "MIT":
        errors.append("plugins/paper-to-notion/.claude-plugin/plugin.json license must be MIT")


def validate_mirrors(errors: list[str]) -> None:
    assert_same(ROOT / "LICENSE", PLUGIN_ROOT / "LICENSE", errors)
    assert_same(ROOT / "SKILL.md", PLUGIN_SKILL / "SKILL.md", errors)
    assert_same(ROOT / "requirements.txt", PLUGIN_SKILL / "requirements.txt", errors)
    assert_same(ROOT / "agents" / "openai.yaml", PLUGIN_SKILL / "agents" / "openai.yaml", errors)
    assert_same(ROOT / "config" / "notion_schema.yaml", PLUGIN_SKILL / "config" / "notion_schema.yaml", errors)

    for path in sorted((ROOT / "references").glob("*.md")):
        assert_same(path, PLUGIN_SKILL / "references" / path.name, errors)

    for path in sorted((ROOT / "scripts").iterdir()):
        if path.is_file():
            assert_same(path, PLUGIN_SKILL / "scripts" / path.name, errors)


def main() -> int:
    errors: list[str] = []
    for path in [
        ROOT / "LICENSE",
        ROOT / "README.md",
        ROOT / "README.zh-CN.md",
        ROOT / "SKILL.md",
        ROOT / ".claude-plugin" / "marketplace.json",
        PLUGIN_ROOT / ".claude-plugin" / "plugin.json",
        PLUGIN_SKILL / "SKILL.md",
    ]:
        assert_exists(path, errors)

    validate_manifests(errors)
    validate_mirrors(errors)

    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1

    print("Repository packaging validation passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
