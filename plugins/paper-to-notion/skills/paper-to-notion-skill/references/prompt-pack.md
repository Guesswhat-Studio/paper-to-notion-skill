# Prompt Pack

These prompts are examples for users or future agents. The skill itself should follow `SKILL.md` and the references directly.

## Setup Prompt

```text
Use $paper-to-notion-skill to set up my Notion paper reading workflow.

Please detect whether this environment is Codex, Claude, WorkBuddy, or another compatible MCP/CLI runtime; check whether the OS is Windows, macOS, or Linux; check whether Notion read/write access is available through the runtime connector; create or reuse a Notion database named Paper Reading Library; ensure it has the required paper index fields; create useful views; prepare a skill-local uv-managed .venv for PDF reading; if Python is missing, explain and request approval before bootstrapping uv and uv-managed Python; run the Attention Is All You Need smoke test; save .paper-notion/config.json in this workspace; and verify that the database can be fetched and queried.
```

## Environment-Only Prompt

```text
Use $paper-to-notion-skill to check and prepare my local paper-reading environment.

Please detect Windows/macOS/Linux, create the skill-local .venv with uv if useful, install the required Python packages, validate PyMuPDF/Pillow/requests/HTML parsing support, report optional tool availability, and run the Attention Is All You Need smoke test if network access is available.
```

## Default English Reading Prompt

```text
Use $paper-to-notion-skill to read this paper in English and save it to my Notion paper database:

<PAPER_INPUT>

Please resolve the paper identity, extract verified metadata, classify the paper type, capture the important evidence, generate a Notion-ready report with embedded images, formulas, tables, code and reproducibility notes, create or update the database record, and verify the Notion page after publishing.
```

## Chinese Reading Prompt

```text
Use $paper-to-notion-skill to read this paper in Chinese and save it to my Notion paper database:

<PAPER_INPUT>

Please keep the official English title in Original Title, write the report body in Chinese, preserve formulas in LaTeX, include the key figures and tables in the Notion page, and verify the database record after publishing.
```

## Bilingual Reading Prompt

```text
Use $paper-to-notion-skill to read this paper bilingually and save it to my Notion paper database:

<PAPER_INPUT>

Please write the full report in English, add a compact Chinese overview near the top, embed important evidence images, preserve formulas, and write Report Language as Bilingual in the database.
```

## Publish Existing Report Prompt

```text
Use $paper-to-notion-skill to publish this existing report to my Notion paper database:

Report path: <REPORT_PATH>
Metadata path, if available: <METADATA_OR_PAYLOAD_PATH>

Please build or validate notion_payload.json, deduplicate by DOI/arXiv/title, create or update the Notion page, and verify the result.
```

## Publish With REST Fallback Prompt

```text
Use $paper-to-notion-skill to publish this validated notion_payload.json with the single-paper REST fallback only because no Notion connector is available:

Payload path: <PAYLOAD_PATH>

Please run the publish script in --dry-run mode first. If validation passes and NOTION_TOKEN plus NOTION_DATA_SOURCE_ID are available, create or update the matching Notion page by DOI/arXiv/title and verify the page URL.
```

## Optional Research-Flow Extension Prompt

```text
Use $paper-to-notion-skill to extend my Notion paper database for daily discovery and team reading.

Please keep the default paper-reading fields intact, ask before adding optional scoring/team properties, then add only the fields needed for arXiv discovery, conference tracking, paper scoring, assignee tracking, and weekly digest views.
```
