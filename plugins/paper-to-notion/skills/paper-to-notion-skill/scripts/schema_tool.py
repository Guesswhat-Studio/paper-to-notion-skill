#!/usr/bin/env python3
"""Validate and render the Notion database schema YAML."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any


VALID_TYPES = {
    "TITLE",
    "RICH_TEXT",
    "DATE",
    "PEOPLE",
    "CHECKBOX",
    "URL",
    "EMAIL",
    "PHONE_NUMBER",
    "STATUS",
    "FILES",
    "SELECT",
    "MULTI_SELECT",
    "NUMBER",
    "FORMULA",
    "RELATION",
    "ROLLUP",
    "UNIQUE_ID",
    "CREATED_TIME",
    "LAST_EDITED_TIME",
}

VALID_COLORS = {
    "default",
    "gray",
    "brown",
    "orange",
    "yellow",
    "green",
    "blue",
    "purple",
    "pink",
    "red",
}


def load_yaml(path: Path) -> dict[str, Any]:
    try:
        import yaml  # type: ignore
    except ImportError as exc:
        raise SystemExit(
            "PyYAML is required for schema_tool.py. Install requirements or run setup_environment.py --use-uv --install."
        ) from exc
    with path.open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle)
    if not isinstance(data, dict):
        raise ValueError("Schema YAML must contain an object")
    return data


def quote_sql(value: str) -> str:
    return value.replace("'", "''")


def validate_option(option: Any, field_name: str) -> str | None:
    if not isinstance(option, dict):
        return f"{field_name}: each option must be an object"
    name = str(option.get("name", "")).strip()
    if not name:
        return f"{field_name}: option missing name"
    color = str(option.get("color", "default")).strip() or "default"
    if color not in VALID_COLORS:
        return f"{field_name}: option {name!r} has invalid color {color!r}"
    return None


def validate_schema(schema: dict[str, Any]) -> list[str]:
    errors: list[str] = []

    database = schema.get("database")
    if not isinstance(database, dict):
        errors.append("Missing database object")
    elif not str(database.get("title", "")).strip():
        errors.append("database.title is required")

    properties = schema.get("properties")
    if not isinstance(properties, list) or not properties:
        errors.append("properties must be a non-empty list")
        return errors

    names: set[str] = set()
    title_count = 0
    for index, prop in enumerate(properties):
        if not isinstance(prop, dict):
            errors.append(f"properties[{index}] must be an object")
            continue
        name = str(prop.get("name", "")).strip()
        prop_type = str(prop.get("type", "")).strip().upper()
        if not name:
            errors.append(f"properties[{index}] missing name")
            continue
        if name in names:
            errors.append(f"Duplicate property name: {name}")
        names.add(name)
        if prop_type not in VALID_TYPES:
            errors.append(f"{name}: invalid type {prop_type!r}")
        if prop_type == "TITLE":
            title_count += 1
        fallback = str(prop.get("fallback_type", "")).strip().upper()
        if fallback and fallback not in VALID_TYPES:
            errors.append(f"{name}: invalid fallback_type {fallback!r}")
        if prop_type in {"SELECT", "MULTI_SELECT", "STATUS"}:
            options = prop.get("options", [])
            if options is not None and not isinstance(options, list):
                errors.append(f"{name}: options must be a list")
            else:
                for option in options or []:
                    error = validate_option(option, name)
                    if error:
                        errors.append(error)

    if title_count != 1:
        errors.append(f"Schema must have exactly one TITLE property, found {title_count}")

    views = schema.get("views", [])
    if views is not None and not isinstance(views, list):
        errors.append("views must be a list")
    elif isinstance(views, list):
        for index, view in enumerate(views):
            if not isinstance(view, dict):
                errors.append(f"views[{index}] must be an object")
                continue
            if not str(view.get("name", "")).strip():
                errors.append(f"views[{index}] missing name")
            if not str(view.get("type", "")).strip():
                errors.append(f"views[{index}] missing type")

    return errors


def ddl_type(prop: dict[str, Any], use_fallbacks: bool = False) -> str:
    prop_type = str(prop.get("type", "")).strip().upper()
    fallback = str(prop.get("fallback_type", "")).strip().upper()
    if use_fallbacks and fallback:
        prop_type = fallback

    options = prop.get("options") or []
    if prop_type in {"SELECT", "MULTI_SELECT"} and options:
        rendered = ", ".join(
            f"'{quote_sql(str(option['name']))}':{str(option.get('color', 'default'))}" for option in options
        )
        return f"{prop_type}({rendered})"
    if prop_type == "NUMBER" and prop.get("format"):
        return f"NUMBER FORMAT '{quote_sql(str(prop['format']))}'"
    if prop_type == "UNIQUE_ID" and prop.get("prefix"):
        return f"UNIQUE_ID PREFIX '{quote_sql(str(prop['prefix']))}'"
    return prop_type


def render_create_table(schema: dict[str, Any], use_fallbacks: bool = False) -> str:
    properties = schema["properties"]
    lines = []
    for prop in properties:
        name = str(prop["name"])
        lines.append(f'  "{name}" {ddl_type(prop, use_fallbacks)}')
    return "CREATE TABLE (\n" + ",\n".join(lines) + "\n)"


def render_add_columns(schema: dict[str, Any], use_fallbacks: bool = False) -> str:
    statements = []
    for prop in schema["properties"]:
        prop_type = str(prop.get("type", "")).strip().upper()
        if prop_type == "TITLE":
            continue
        statements.append(f'ADD COLUMN "{prop["name"]}" {ddl_type(prop, use_fallbacks)}')
    return ";\n".join(statements)


def render_summary(schema: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": schema.get("schema_version"),
        "database": schema.get("database", {}),
        "properties": [
            {
                "name": prop.get("name"),
                "type": prop.get("type"),
                "required": bool(prop.get("required", False)),
                "options": [option.get("name") for option in prop.get("options", []) or []],
            }
            for prop in schema.get("properties", [])
        ],
        "views": schema.get("views", []),
        "deduplication": schema.get("deduplication", {}),
        "optional_extensions": list((schema.get("optional_extensions") or {}).keys()),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--schema", type=Path, default=Path(__file__).resolve().parents[1] / "config" / "notion_schema.yaml")
    parser.add_argument("--command", choices=["validate", "ddl", "add-columns", "summary"], default="validate")
    parser.add_argument("--use-fallbacks", action="store_true", help="Use fallback_type when present, useful if STATUS/PEOPLE is unsupported")
    parser.add_argument("--output", type=Path, help="Write command output to a file")
    args = parser.parse_args()

    schema = load_yaml(args.schema)
    errors = validate_schema(schema)
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1

    if args.command == "validate":
        output = f"Schema validation passed: {args.schema}"
    elif args.command == "ddl":
        output = render_create_table(schema, args.use_fallbacks)
    elif args.command == "add-columns":
        output = render_add_columns(schema, args.use_fallbacks)
    else:
        output = json.dumps(render_summary(schema), ensure_ascii=False, indent=2)

    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(output + "\n", encoding="utf-8")
    else:
        print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
