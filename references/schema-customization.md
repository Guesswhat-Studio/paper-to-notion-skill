# Schema Customization

Use `config/notion_schema.yaml` to customize the Notion database. The YAML is the source of truth for setup, DDL generation, payload validation, and user-facing schema documentation.

## Basic Workflow

1. Copy `config/notion_schema.yaml` if you want a project-specific schema.
2. Edit property names, types, options, defaults, or optional extensions.
3. Validate:

```bash
python scripts/schema_tool.py --schema config/notion_schema.yaml --command validate
```

4. Render create-database DDL:

```bash
python scripts/schema_tool.py --schema config/notion_schema.yaml --command ddl
```

5. Render add-column statements for missing fields:

```bash
python scripts/schema_tool.py --schema config/notion_schema.yaml --command add-columns
```

## Supported Property Fields

Each property object supports:

```yaml
- name: "Rating"
  type: "SELECT"
  fallback_type: "RICH_TEXT"
  required: false
  default: ""
  readonly: false
  purpose: "Reader rating."
  options:
    - { name: "5 stars", color: "blue" }
```

`fallback_type` is useful when a connector/runtime does not support a preferred Notion type. For example, `Reading Status` can fall back from `STATUS` to `SELECT`, and `Assignee` can fall back from `PEOPLE` to `RICH_TEXT`.

## Supported Types

The schema tool accepts common Notion DDL types:

```text
TITLE, RICH_TEXT, DATE, PEOPLE, CHECKBOX, URL, EMAIL, PHONE_NUMBER,
STATUS, FILES, SELECT, MULTI_SELECT, NUMBER, FORMULA, RELATION,
ROLLUP, UNIQUE_ID, CREATED_TIME, LAST_EDITED_TIME
```

Keep exactly one `TITLE` property.

## Select And Multi-Select Options

Use option objects with `name` and `color`:

```yaml
options:
  - { name: "English", color: "blue" }
  - { name: "Chinese", color: "green" }
```

Valid colors:

```text
default, gray, brown, orange, yellow, green, blue, purple, pink, red
```

For `MULTI_SELECT`, payload validation warns when a value is not preconfigured but does not fail, because controlled categories can still evolve. Store open-ended paper topic phrases in `Keywords` as text. For `SELECT`, validation fails unless the value is listed.

## Design Guidance

- Keep the default database lean. Add long analysis to the report page, not properties.
- Prefer properties that support filtering, sorting, status, review, and retrieval.
- Put scoring/team/discovery fields under `optional_extensions` until the user asks for those workflows.
- Keep `DOI`, `arXiv`, and `Original Title` stable because deduplication depends on them.
