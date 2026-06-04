#!/usr/bin/env python3
"""Publish a validated paper payload to a Notion data source.

This script is a single-paper fallback for runtimes that do not expose a
first-class Notion connector. It intentionally stays small: it maps the default
paper schema, queries for an existing DOI/arXiv/title match, and creates or
updates one Notion page.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Any

import requests


DEFAULT_SCHEMA = Path(__file__).resolve().parents[1] / "config" / "notion_schema.yaml"
DEFAULT_NOTION_VERSION = "2026-03-11"
NOTION_API_BASE = "https://api.notion.com/v1"
MAX_RICH_TEXT = 1900
MAX_CHILDREN = 100
WRITABLE_TYPES = {"TITLE", "RICH_TEXT", "DATE", "URL", "SELECT", "STATUS", "MULTI_SELECT", "NUMBER"}
READONLY_TYPES = {"CREATED_TIME", "LAST_EDITED_TIME", "FORMULA", "ROLLUP", "UNIQUE_ID"}


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return data


def load_schema(path: Path) -> dict[str, str]:
    try:
        import yaml  # type: ignore
    except ImportError as exc:
        raise SystemExit("PyYAML is required. Run scripts/setup_environment.py --use-uv --install.") from exc

    with path.open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle)
    if not isinstance(data, dict):
        raise ValueError("Schema must be a YAML object")

    fields: dict[str, str] = {}
    for prop in data.get("properties", []):
        if not isinstance(prop, dict):
            continue
        name = str(prop.get("name", "")).strip()
        prop_type = str(prop.get("type", "")).strip().upper()
        if name and prop_type:
            fields[name] = prop_type
    return fields


def run_validation(payload_path: Path) -> None:
    validator = Path(__file__).with_name("validate_notion_payload.py")
    subprocess.check_call([sys.executable, str(validator), str(payload_path)])


def rich_text(text: Any) -> list[dict[str, Any]]:
    value = str(text if text is not None else "")
    return [
        {"type": "text", "text": {"content": value[index : index + MAX_RICH_TEXT]}}
        for index in range(0, len(value), MAX_RICH_TEXT)
    ]


def plain_text(text: str) -> str:
    text = re.sub(r"!\[[^\]]*\]\([^)]+\)", "", text)
    text = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r"\1 (\2)", text)
    text = re.sub(r"(\*\*|__|\*|`)", "", text)
    return text.strip()


def code_language(raw: str) -> str:
    language = raw.strip().lower()
    allowed = {
        "bash",
        "c",
        "c++",
        "c#",
        "css",
        "html",
        "java",
        "javascript",
        "json",
        "latex",
        "markdown",
        "plain text",
        "python",
        "rust",
        "sql",
        "typescript",
        "yaml",
    }
    return language if language in allowed else "plain text"


def block(block_type: str, payload: dict[str, Any]) -> dict[str, Any]:
    return {"object": "block", "type": block_type, block_type: payload}


def text_block(block_type: str, text: str) -> dict[str, Any]:
    return block(block_type, {"rich_text": rich_text(plain_text(text))})


def image_block(alt: str, link: str) -> dict[str, Any]:
    if link.startswith(("http://", "https://")):
        return block(
            "image",
            {
                "type": "external",
                "external": {"url": link},
                "caption": rich_text(alt),
            },
        )
    return text_block("paragraph", f"Image placeholder: {alt or link} ({link})")


def flush_paragraph(lines: list[str], blocks: list[dict[str, Any]]) -> None:
    if not lines:
        return
    text = " ".join(line.strip() for line in lines).strip()
    if text:
        blocks.append(text_block("paragraph", text))
    lines.clear()


def flush_table(lines: list[str], blocks: list[dict[str, Any]]) -> None:
    if not lines:
        return
    blocks.append(block("code", {"rich_text": rich_text("\n".join(lines)), "language": "plain text"}))
    lines.clear()


def markdown_to_blocks(markdown: str) -> list[dict[str, Any]]:
    blocks: list[dict[str, Any]] = []
    paragraph: list[str] = []
    table: list[str] = []
    code_lines: list[str] = []
    in_code = False
    language = "plain text"

    for raw_line in markdown.splitlines():
        line = raw_line.rstrip()

        if line.startswith("```"):
            if in_code:
                blocks.append(block("code", {"rich_text": rich_text("\n".join(code_lines)), "language": language}))
                code_lines = []
                in_code = False
                language = "plain text"
            else:
                flush_paragraph(paragraph, blocks)
                flush_table(table, blocks)
                in_code = True
                language = code_language(line.strip("`").strip())
            continue

        if in_code:
            code_lines.append(line)
            continue

        if line.startswith("|"):
            flush_paragraph(paragraph, blocks)
            table.append(line)
            continue
        flush_table(table, blocks)

        if not line.strip():
            flush_paragraph(paragraph, blocks)
            continue

        image = re.match(r"^!\[([^\]]*)\]\(([^)]+)\)$", line.strip())
        if image:
            flush_paragraph(paragraph, blocks)
            blocks.append(image_block(image.group(1), image.group(2)))
            continue

        if line.strip() in {"---", "***"}:
            flush_paragraph(paragraph, blocks)
            blocks.append(block("divider", {}))
            continue

        heading = re.match(r"^(#{1,3})\s+(.+)$", line)
        if heading:
            flush_paragraph(paragraph, blocks)
            level = len(heading.group(1))
            blocks.append(text_block(f"heading_{level}", heading.group(2)))
            continue

        bullet = re.match(r"^\s*[-*]\s+(.+)$", line)
        if bullet:
            flush_paragraph(paragraph, blocks)
            blocks.append(text_block("bulleted_list_item", bullet.group(1)))
            continue

        numbered = re.match(r"^\s*\d+\.\s+(.+)$", line)
        if numbered:
            flush_paragraph(paragraph, blocks)
            blocks.append(text_block("numbered_list_item", numbered.group(1)))
            continue

        quote = re.match(r"^\s*>\s+(.+)$", line)
        if quote:
            flush_paragraph(paragraph, blocks)
            blocks.append(text_block("quote", quote.group(1)))
            continue

        paragraph.append(line)

    if in_code:
        blocks.append(block("code", {"rich_text": rich_text("\n".join(code_lines)), "language": language}))
    flush_table(table, blocks)
    flush_paragraph(paragraph, blocks)
    return blocks


def notion_property(prop_type: str, value: Any) -> dict[str, Any] | None:
    if prop_type in READONLY_TYPES:
        return None
    if value in (None, "") and prop_type != "TITLE":
        return None
    if prop_type == "TITLE":
        return {"title": rich_text(value)}
    if prop_type == "RICH_TEXT":
        return {"rich_text": rich_text(value)}
    if prop_type == "DATE":
        return {"date": {"start": str(value)}}
    if prop_type == "URL":
        return {"url": str(value)}
    if prop_type == "SELECT":
        return {"select": {"name": str(value)}}
    if prop_type == "STATUS":
        return {"status": {"name": str(value)}}
    if prop_type == "MULTI_SELECT":
        values = value if isinstance(value, list) else [value]
        return {"multi_select": [{"name": str(item)} for item in values if str(item).strip()]}
    if prop_type == "NUMBER":
        return {"number": int(value)}
    return None


def build_notion_properties(payload: dict[str, Any], schema: dict[str, str]) -> dict[str, Any]:
    source = payload.get("properties", {})
    if not isinstance(source, dict):
        raise ValueError("payload.properties must be an object")

    properties: dict[str, Any] = {}
    for name, value in source.items():
        prop_type = schema.get(name)
        if not prop_type or prop_type not in WRITABLE_TYPES:
            continue
        mapped = notion_property(prop_type, value)
        if mapped is not None:
            properties[name] = mapped
    return properties


class NotionClient:
    def __init__(self, token: str, version: str) -> None:
        self.session = requests.Session()
        self.session.headers.update(
            {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json",
                "Notion-Version": version,
            }
        )

    def request(self, method: str, path: str, body: dict[str, Any] | None = None) -> dict[str, Any]:
        response = self.session.request(method, f"{NOTION_API_BASE}{path}", json=body, timeout=60)
        if response.status_code >= 400:
            try:
                detail = response.json()
            except ValueError:
                detail = response.text
            raise RuntimeError(f"Notion API {method} {path} failed with {response.status_code}: {detail}")
        data = response.json()
        if not isinstance(data, dict):
            raise RuntimeError(f"Unexpected Notion API response from {method} {path}")
        return data

    def query(self, data_source_id: str, body: dict[str, Any]) -> dict[str, Any]:
        return self.request("POST", f"/data_sources/{data_source_id}/query", body)

    def create_page(self, data_source_id: str, properties: dict[str, Any], children: list[dict[str, Any]]) -> dict[str, Any]:
        return self.request(
            "POST",
            "/pages",
            {
                "parent": {"data_source_id": data_source_id},
                "properties": properties,
                "children": children[:MAX_CHILDREN],
            },
        )

    def update_page(self, page_id: str, properties: dict[str, Any]) -> dict[str, Any]:
        return self.request("PATCH", f"/pages/{page_id}", {"properties": properties})

    def append_children(self, block_id: str, children: list[dict[str, Any]]) -> None:
        for index in range(0, len(children), MAX_CHILDREN):
            self.request("PATCH", f"/blocks/{block_id}/children", {"children": children[index : index + MAX_CHILDREN]})

    def retrieve_page(self, page_id: str) -> dict[str, Any]:
        return self.request("GET", f"/pages/{page_id}")


def duplicate_filter(properties: dict[str, Any]) -> dict[str, Any] | None:
    filters: list[dict[str, Any]] = []
    doi = str(properties.get("DOI", "")).strip()
    arxiv = str(properties.get("arXiv", "")).strip()
    original_title = str(properties.get("Original Title", "")).strip()
    name = str(properties.get("Name", "")).strip()

    if doi:
        filters.append({"property": "DOI", "url": {"equals": doi}})
    if arxiv:
        filters.append({"property": "arXiv", "url": {"equals": arxiv}})
    if original_title:
        filters.append({"property": "Original Title", "rich_text": {"equals": original_title}})
    if name and name != original_title:
        filters.append({"property": "Name", "title": {"equals": name}})

    if not filters:
        return None
    if len(filters) == 1:
        return filters[0]
    return {"or": filters}


def find_existing_page(client: NotionClient, data_source_id: str, payload: dict[str, Any]) -> dict[str, Any] | None:
    properties = payload.get("properties", {})
    if not isinstance(properties, dict):
        return None
    filter_body = duplicate_filter(properties)
    if not filter_body:
        return None
    data = client.query(data_source_id, {"filter": filter_body, "page_size": 5})
    results = data.get("results", [])
    if isinstance(results, list) and results:
        first = results[0]
        return first if isinstance(first, dict) else None
    return None


def data_source_id(args: argparse.Namespace, payload: dict[str, Any]) -> str:
    database = payload.get("database", {})
    if not isinstance(database, dict):
        database = {}
    return (
        args.data_source_id
        or os.environ.get("NOTION_DATA_SOURCE_ID", "")
        or str(database.get("data_source_id", ""))
    ).strip()


def report_markdown(payload: dict[str, Any], payload_path: Path) -> str:
    content = payload.get("content", {})
    if not isinstance(content, dict):
        return ""
    markdown = str(content.get("notion_markdown", ""))
    if markdown.strip():
        return markdown
    report_path = str(content.get("report_path", "")).strip()
    if not report_path:
        return ""
    resolved = (payload_path.parent / report_path).resolve() if not Path(report_path).is_absolute() else Path(report_path)
    return resolved.read_text(encoding="utf-8") if resolved.exists() else ""


def publish(args: argparse.Namespace) -> dict[str, Any]:
    payload = load_json(args.payload)
    schema = load_schema(args.schema)
    if not args.skip_validation:
        run_validation(args.payload)

    notion_properties = build_notion_properties(payload, schema)
    markdown = report_markdown(payload, args.payload)
    blocks = markdown_to_blocks(markdown)
    children_to_write = blocks if args.body_mode == "append" else []

    summary = {
        "properties": sorted(notion_properties.keys()),
        "block_count": len(blocks),
        "data_source_id": data_source_id(args, payload),
    }
    if args.dry_run:
        return {"status": "dry_run", **summary}

    token = args.token or os.environ.get("NOTION_TOKEN") or os.environ.get("NOTION_API_KEY")
    if not token:
        raise SystemExit("Set NOTION_TOKEN or pass --token before publishing.")

    target_data_source_id = data_source_id(args, payload)
    if not target_data_source_id:
        raise SystemExit("Set NOTION_DATA_SOURCE_ID, pass --data-source-id, or add database.data_source_id to the payload.")

    client = NotionClient(token, args.notion_version)
    existing = find_existing_page(client, target_data_source_id, payload)

    if existing:
        page_id = str(existing.get("id", ""))
        if args.if_exists == "fail":
            raise SystemExit(f"Duplicate page found: {page_id}")
        if args.if_exists == "skip":
            return {"status": "skipped_existing", "page_id": page_id, "url": existing.get("url"), **summary}
        page = client.update_page(page_id, notion_properties)
        if children_to_write:
            client.append_children(page_id, [block("divider", {})] + children_to_write)
        verified = client.retrieve_page(page_id)
        return {"status": "updated", "page_id": page_id, "url": verified.get("url") or page.get("url"), **summary}

    page = client.create_page(target_data_source_id, notion_properties, children_to_write)
    page_id = str(page.get("id", ""))
    if len(children_to_write) > MAX_CHILDREN:
        client.append_children(page_id, children_to_write[MAX_CHILDREN:])
    verified = client.retrieve_page(page_id)
    return {"status": "created", "page_id": page_id, "url": verified.get("url") or page.get("url"), **summary}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("payload", type=Path, help="notion_payload.json path")
    parser.add_argument("--schema", type=Path, default=DEFAULT_SCHEMA)
    parser.add_argument("--data-source-id", default="", help="Overrides payload.database.data_source_id and NOTION_DATA_SOURCE_ID")
    parser.add_argument("--token", default="", help="Notion integration token. Prefer NOTION_TOKEN.")
    parser.add_argument("--notion-version", default=os.environ.get("NOTION_VERSION", DEFAULT_NOTION_VERSION))
    parser.add_argument("--if-exists", choices=["update", "skip", "fail"], default="update")
    parser.add_argument("--body-mode", choices=["append", "none"], default="append")
    parser.add_argument("--skip-validation", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    result = publish(args)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
