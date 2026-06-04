#!/usr/bin/env python3
"""Validate a Notion paper payload before publishing."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import re
from pathlib import Path
from typing import Any


IMAGE_STATUSES = {"hosted", "local_only", "placeholder", "no_images"}
DEFAULT_SCHEMA = Path(__file__).resolve().parents[1] / "config" / "notion_schema.yaml"


def load_payload(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError("Payload must be a JSON object")
    return data


def load_schema(path: Path) -> dict[str, Any]:
    try:
        import yaml  # type: ignore
    except ImportError as exc:
        raise SystemExit(
            "PyYAML is required to validate against a schema. Install requirements or run without --schema only after editing the script."
        ) from exc
    with path.open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle)
    if not isinstance(data, dict):
        raise ValueError("Schema must be a YAML object")
    return data


def schema_properties(schema: dict[str, Any]) -> list[dict[str, Any]]:
    properties = schema.get("properties", [])
    if not isinstance(properties, list):
        raise ValueError("schema.properties must be a list")
    return [prop for prop in properties if isinstance(prop, dict)]


def option_names(prop: dict[str, Any]) -> set[str]:
    options = prop.get("options", []) or []
    return {str(option.get("name", "")).strip() for option in options if isinstance(option, dict)}


def is_url_or_blank(value: Any) -> bool:
    if value in (None, ""):
        return True
    if not isinstance(value, str):
        return False
    return bool(re.match(r"^https?://\S+$", value))


def is_date_or_blank(value: Any) -> bool:
    if value in (None, ""):
        return True
    if not isinstance(value, str):
        return False
    try:
        dt.date.fromisoformat(value)
    except ValueError:
        return False
    return True


def image_links(markdown: str) -> list[str]:
    return re.findall(r"!\[[^\]]*\]\(([^)]+)\)", markdown or "")


def is_public_or_placeholder(link: str) -> bool:
    return (
        link.startswith("http://")
        or link.startswith("https://")
        or link.startswith("__PUBLIC_IMAGE_PREFIX__/")
    )


def validate_option_value(field: str, value: Any, prop: dict[str, Any], errors: list[str]) -> None:
    allowed = option_names(prop)
    if allowed and str(value).strip() not in allowed:
        errors.append(f"{field} must be one of: {', '.join(sorted(allowed))}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("payload", type=Path)
    parser.add_argument("--schema", type=Path, default=DEFAULT_SCHEMA, help="Notion schema YAML path")
    args = parser.parse_args()

    payload = load_payload(args.payload)
    schema = load_schema(args.schema)
    errors: list[str] = []
    warnings: list[str] = []

    properties = payload.get("properties")
    if not isinstance(properties, dict):
        errors.append("Missing object: properties")
        properties = {}

    content = payload.get("content")
    if not isinstance(content, dict):
        errors.append("Missing object: content")
        content = {}

    dedup = payload.get("dedup")
    if not isinstance(dedup, dict):
        errors.append("Missing object: dedup")
        dedup = {}

    for prop in schema_properties(schema):
        field = str(prop.get("name", "")).strip()
        prop_type = str(prop.get("type", "")).strip().upper()
        value = properties.get(field)
        if prop.get("required") and not str(value if value is not None else "").strip():
            errors.append(f"Missing required property: {field}")
            continue
        if value in (None, ""):
            continue
        if prop_type == "NUMBER":
            try:
                int(value)
            except (TypeError, ValueError):
                errors.append(f"{field} must be a number")
        elif prop_type == "DATE" and not is_date_or_blank(value):
            errors.append(f"{field} must be blank or an ISO date like YYYY-MM-DD")
        elif prop_type == "URL" and not is_url_or_blank(value):
            errors.append(f"{field} must be blank or an http(s) URL")
        elif prop_type == "SELECT":
            validate_option_value(field, value, prop, errors)
        elif prop_type == "STATUS":
            validate_option_value(field, value, prop, errors)
        elif prop_type == "MULTI_SELECT":
            allowed = option_names(prop)
            values = value if isinstance(value, list) else [str(value)]
            if allowed:
                for item in values:
                    if str(item).strip() not in allowed:
                        warnings.append(f"{field} value is not in configured options yet: {item}")

    if not str(dedup.get("key", "")).strip():
        errors.append("Missing dedup.key")
    if dedup.get("strategy") not in {"doi", "arxiv", "title"}:
        errors.append("dedup.strategy must be doi, arxiv, or title")

    image_status = str(content.get("image_status", "")).strip()
    if image_status not in IMAGE_STATUSES:
        errors.append("content.image_status must be hosted, local_only, placeholder, or no_images")

    report_path = str(content.get("report_path", "")).strip()
    if report_path:
        resolved = (args.payload.parent / report_path).resolve() if not Path(report_path).is_absolute() else Path(report_path)
        if not resolved.exists():
            warnings.append(f"Report path does not exist: {report_path}")

    markdown = str(content.get("notion_markdown", ""))
    if not markdown.strip():
        warnings.append("content.notion_markdown is empty")

    bad_links = [link for link in image_links(markdown) if not is_public_or_placeholder(link)]
    for link in bad_links:
        errors.append(f"Image link is not public or placeholder: {link}")

    if image_status == "no_images" and image_links(markdown):
        errors.append("image_status is no_images but markdown contains image links")

    if image_status == "local_only":
        linked_images = image_links(markdown)
        if linked_images:
            warnings.append("image_status is local_only; Notion connector publishing should replace image links with a local-image note")

    if image_status == "hosted":
        placeholder_links = [link for link in image_links(markdown) if link.startswith("__PUBLIC_IMAGE_PREFIX__/")]
        if placeholder_links:
            errors.append("image_status is hosted but markdown still contains placeholder image links")

    for warning in warnings:
        print(f"WARNING: {warning}")
    for error in errors:
        print(f"ERROR: {error}")

    if errors:
        return 1
    print("Payload validation passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
