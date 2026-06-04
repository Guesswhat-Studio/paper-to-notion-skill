# Notion Publishing

Use this reference after reading the paper or when publishing an existing report.

## Principle

The Notion database row is the index. The Notion page body is the report. Do not put long analysis into database properties.

## Connector Preparation

Read `runtime-connectors.md` first when runtime capabilities are unclear.

When using Codex Notion plugin tools:

1. Fetch the Notion enhanced Markdown spec if the tool requires it before `create_pages` or `update_page`.
2. Fetch the database or data source before writing pages.
3. Use the exact property names from the fetched schema.
4. Use `data_source_id` or `collection://...` for database-page creation when the connector requires a data source rather than a database ID.
5. Use the connector's existing authentication. Do not ask the user for a Notion API token in the Codex connector flow.

When using Claude Notion connector:

1. Use equivalent search, fetch, create, update, and database operations.
2. Preserve the same schema and payload semantics.
3. Use the connector's existing authentication. Do not ask the user for a Notion API token in the Claude connector flow.

When using WorkBuddy Connector:

1. Prefer a configured Notion MCP connector.
2. If Notion is not available as a built-in connector, use a custom MCP connector when the user has configured one.
3. If only Skill + CLI is available, publish through a user-approved CLI/API bridge and keep credentials out of reports and payloads.
4. Preserve the same schema, payload, deduplication, and verification semantics as Codex/Claude.

## Connectorless REST Fallback

Use this only when no Codex, Claude, WorkBuddy, MCP, or equivalent Notion connector can write pages and the user explicitly chooses a token-based fallback. It is not part of the normal Codex/Claude connector path.

First validate without writing:

```bash
python scripts/publish_notion_payload.py path/to/notion_payload.json --dry-run
```

Then publish after the user has supplied credentials through the environment:

```powershell
$env:NOTION_TOKEN = "secret_..."
$env:NOTION_DATA_SOURCE_ID = "..."
python scripts/publish_notion_payload.py path/to/notion_payload.json
```

On macOS/Linux, use `export NOTION_TOKEN=...` and `export NOTION_DATA_SOURCE_ID=...`. The fallback uses Notion's current data source API by default and can be pointed at another API version with `NOTION_VERSION` or `--notion-version`.

## Output Files

For each paper run, keep a dedicated local folder when possible:

```text
paper-output/
  report.md
  notion_payload.json
  images/
```

`report.md` is the page body source. `notion_payload.json` is the structured bridge to Notion.

## Payload Shape

Use this JSON shape:

```json
{
  "database": {
    "database_id": "",
    "data_source_id": ""
  },
  "dedup": {
    "key": "",
    "strategy": "doi|arxiv|title"
  },
  "properties": {
    "Name": "",
    "Original Title": "",
    "Authors": "",
    "Publication Date": "",
    "Year": 0,
    "Venue": [],
    "Field": [],
    "Type": [],
    "Keywords": "",
    "Reading Status": "Read",
    "Read Date": "",
    "Rating": "",
    "DOI": "",
    "arXiv": "",
    "Code": "",
    "Report Language": "English"
  },
  "content": {
    "report_path": "report.md",
    "image_status": "hosted|local_only|placeholder|no_images",
    "public_image_prefix": "",
    "notion_markdown": ""
  }
}
```

Use blank strings for unknown optional URLs. Omit `Rating` or use blank if the reader has not rated the paper.

## Image Policy

- PDF images and evidence crops should be extracted locally when useful. Keep them in `images/`.
- The current Codex/Claude Notion connector path can write page content and external image URLs, but it does not expose a local binary upload tool for Notion image/file blocks.
- If the user says not to use external hosting, do not use a public image prefix and do not write local filesystem image paths as Markdown images in Notion. Instead, state `image_status: local_only` and build a self-contained local evidence pack:

```bash
python scripts/build_evidence_pack.py --report report.md --output evidence_pack.html
```

  In the Notion page, include a concise local-image note that points to the single `evidence_pack.html` file and lists the evidence images by caption. This gives the reader one local artifact to open while keeping the Notion page honest about connector limits.
- If a connector later exposes local file upload, use it and mark images as embedded. Until then, do not pretend local images were embedded.
- If the user explicitly allows hosted images, use public image URLs in `notion_markdown`.

## Math Policy

- Keep `report.md` in normal Markdown/LaTeX syntax, such as `$K$` and `$$...$$`.
- Before writing through the Codex/Claude Notion connector, build the payload with the default `--math-format notion`. This converts inline math into the connector's enhanced Markdown equation form, such as ``$`K`$``.
- Use `--math-format markdown` only when publishing to a renderer that reliably supports ordinary `$...$` inline math.

If images have already been hosted, pass a public prefix while building the payload:

```bash
python scripts/build_notion_payload.py --metadata metadata.json --report report.md --output notion_payload.json --image-status hosted --public-image-prefix https://cdn.example.com/papers/paper-slug
```

The builder replaces `__PUBLIC_IMAGE_PREFIX__` in the report body with the supplied prefix before validation.

## Dedup Query

Prefer DOI, then arXiv, then normalized title.

Example SQL-style query for connectors that support data source SQL:

```sql
SELECT * FROM "collection://DATA_SOURCE_ID"
WHERE "DOI" = ? OR "arXiv" = ? OR "Original Title" = ?
LIMIT 5
```

If DOI or arXiv is blank, omit that predicate.

## Create Or Update Logic

1. Build and validate `notion_payload.json`.
2. Query the database for duplicates.
3. If no duplicate exists, create a database page with:
   - Properties from `payload.properties`.
   - Content from `payload.content.notion_markdown` or `report.md`.
4. If a duplicate exists:
   - Fetch the page.
   - Update properties.
   - Replace or append report content according to the user's request.
   - Prefer replacing the generated report section when the old page is clearly generated by this skill.
5. Fetch the page after writing.
6. Query the database to confirm the record appears through title, DOI/arXiv, or keyword search.

## Property Mapping Notes

- `Publication Date` and `Read Date`: When a connector requires expanded date properties, use the connector-specific date format.
- `Year`: Use a number, not a string.
- `Venue`, `Field`, `Type`: Use comma-separated or connector-supported multi-select values according to the fetched schema.
- `Keywords`: Use paper-specific keywords or topic phrases as comma-separated text. Do not put paper type labels such as `method`, `survey`, or `empirical` here.
- `Rating`: Use one of `1 star`, `2 stars`, `3 stars`, `4 stars`, `5 stars`, or blank.
- `Report Language`: Use `English`, `Chinese`, or `Bilingual`.

## REST Fallback Behavior

`scripts/publish_notion_payload.py` supports one-paper create/update:

- `--dry-run`: Validate the payload and show mapped properties, block count, and data source ID without calling Notion.
- `--if-exists update|skip|fail`: Choose how to handle a DOI/arXiv/title duplicate. The default is `update`.
- `--body-mode append|none`: Append the report body or update only properties. The default is `append`.
- Existing pages get updated properties and an appended report body separated by a divider.
- New pages are created under `data_source_id`, with content appended in batches when the report exceeds Notion's per-request child block limit.

The fallback intentionally does not create databases, repair schemas, upload local images, or delete existing page content. Use connector tools or a user-approved custom helper for those operations.

## Verification Checklist

After publishing:

- The page exists under the paper database.
- The report body is present and starts with the title or first report section.
- Images are hosted, explicitly placeholdered, or intentionally absent.
- The database properties match the payload.
- The record can be found by title and at least one of DOI, arXiv, author, or keyword when available.
- Any manual remaining step is reported to the user.
