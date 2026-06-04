---
name: paper-to-notion-skill
description: Evidence-driven paper reading and Notion publishing workflow. Use when an agent needs to set up a Notion paper-reading database, read an academic paper from a local PDF, arXiv URL, DOI, paper URL, or title, extract metadata and source-grounded evidence, generate an English-by-default report with embedded figures, formulas, tables, code/reproducibility notes, optional Chinese or bilingual output, and create or update a record in a Notion paper database across Codex, Claude, WorkBuddy, or compatible MCP/CLI runtimes.
---

# Paper To Notion Skill

## Overview

Use this skill to turn papers into durable Notion records: a lean database row for indexing, plus a rich Notion page report that carries the actual reading work. Default to English reports unless the user requests Chinese or bilingual output.

## Workflow Decision

- **Setup request**: If the user asks to connect Notion, initialize a paper database, inspect or customize the schema, prepare the workflow, install dependencies, validate the environment, or run a sample-paper test, follow `references/runtime-connectors.md`, `references/environment-setup.md`, `references/notion-database-schema.md`, `references/schema-customization.md`, and the setup prompt in `references/prompt-pack.md`.
- **Paper reading request**: If the user provides a PDF, arXiv URL, DOI, paper URL, or title and asks to read, summarize, explain, review, or save it to Notion, follow `references/deep-reading-contract.md`, then publish with `references/notion-publishing.md`.
- **Publish-only request**: If the user already has a report or `notion_payload.json`, skip PDF reading and run only the Notion publishing and validation steps.
- **Research-flow request**: If the user asks for daily arXiv discovery, conference tracking, paper scoring, team assignment, or weekly digests, treat that as an optional extension. Keep the default database lean unless the user approves discovery/team fields.

## Simple Input Router

Keep routing practical and limited to common cases:

1. **Local PDF**: Use the PDF path. Extract the text layer, crop useful evidence images, and use OCR only when the text layer is missing or unusable.
2. **arXiv link or ID**: Resolve the arXiv ID, fetch metadata from the abstract page, then try `scripts/fetch_arxiv_html.py`. If official HTML is available, use it for sections, formulas, tables, and verified figure URLs. If HTML is unavailable or incomplete, fall back to the PDF path.
3. **Publisher URL, DOI, or title**: Fetch public metadata and resolve the official page. If full-text HTML is accessible, parse it. If access is blocked or only abstract metadata is public, ask the user for the PDF and continue through the PDF path.
4. **Existing report or payload**: Skip reading. Validate or build `notion_payload.json`, deduplicate, publish, and verify.

For arXiv HTML figures, official `https://arxiv.org/html/...` image URLs may be used directly as hosted external image links in Notion only when they are present and accessible. Use the URLs emitted by `scripts/fetch_arxiv_html.py`; it resolves relative image paths against the actual HTML page and marks `image_accessible`. If an image URL is missing or inaccessible, do not embed it in Notion. Fall back to PDF crops plus a local evidence pack, or cite the figure/table label in text. For long-term public archives or high-traffic use, prefer caching accessible images to a user-controlled host such as GitHub/jsDelivr or Cloudinary.

## Setup Layer

1. Detect the runtime and Notion capability.
   - In Codex, search for or use Notion plugin tools for search, fetch, create database, update data source, create pages, update pages, create views, and query data sources.
   - In Claude, use the Notion connector with equivalent read/write operations.
   - When a Codex or Claude Notion connector is available, use the connector's existing authentication. Do not ask the user for a Notion API token.
   - In WorkBuddy, use its Connector capability. Prefer a configured Notion MCP connector; otherwise use a custom MCP connector or Skill + CLI bridge with equivalent read/write operations.
   - If Notion is unavailable or unauthenticated, ask the user to connect it and stop before changing local state.
2. Prepare and verify the local paper-reading environment.
   - Read `references/environment-setup.md`.
   - Check Python, required Python packages, optional OCR/tools, and network access.
   - Prefer a uv-managed `.venv` inside the skill directory.
   - If Python is already available, use `python scripts/setup_environment.py --use-uv --install`.
   - If Python is missing, do not try to run Python scripts. Use the OS bootstrap script after the user approves uv/Python installation: `.\scripts\bootstrap_uv.ps1 -InstallUv` on Windows, or `INSTALL_UV=1 sh scripts/bootstrap_uv.sh` on macOS/Linux.
   - Run `python scripts/smoke_test_attention.py` after dependency setup when network access is available.
3. Create or reuse the Notion database.
   - Use `config/notion_schema.yaml` as the machine-readable schema source.
   - Validate customized schemas with `scripts/schema_tool.py --command validate`.
   - Default database title: `Paper Reading Library`.
   - If the user asks for a localized name, use that name while keeping the same schema.
   - Keep database fields focused on indexing and workflow state.
4. Save local setup state in `.paper-notion/config.json` in the active workspace.
   - Include `runtime`, `notion_database_id`, `notion_data_source_id`, `schema_version`, and `default_report_language`.
5. Verify by fetching the database schema and running a minimal query or harmless test write when the connector supports it.
6. If the user asks for end-to-end verification, publish the smoke-test report as a `[TEST] Attention Is All You Need` database page and fetch it back.

## Reading Layer

Read `references/deep-reading-contract.md` before processing a paper. The reading layer must:

- Resolve the paper identity from PDF, arXiv, DOI, URL, or title.
- Build a compact source registry and reading pack before writing.
- Extract and verify metadata from the paper itself or official sources.
- For arXiv papers, prefer the official arXiv HTML rendering at `https://arxiv.org/html/<arxiv_id>` when available. Use `scripts/fetch_arxiv_html.py` to build a structured reading pack with validated figure URLs before falling back to PDF text/crops.
- Classify the paper type and adapt the reading strategy.
- Capture evidence: title/author header, formulas, algorithms, theorems, models, architecture diagrams, result figures, tables, ablations, and robustness panels as applicable.
- Explain every evidence block in terms of its role in the paper's argument.
- Search for official code or implementation evidence, then record what was checked.
- Keep factual claims source-grounded and mark uncertain inferences explicitly.

## Writing And Publishing Layer

Read `references/notion-publishing.md` before writing to Notion. The writing layer must:

- Create a complete Notion-ready report body. The report carries deep method, formula, experiment, ablation, limitation, and reproducibility analysis; the database row carries metadata and indexing fields.
- Do not include a dedicated metadata section in the page body by default. Put metadata in database properties.
- Extract useful local evidence images from the PDF when possible. If the Notion connector cannot upload local files and the user does not allow external hosting, keep images local and state the image status honestly instead of embedding broken local paths.
- When using local-only images, build a self-contained local evidence pack with `scripts/build_evidence_pack.py` and link or mention that single HTML file in the Notion page instead of only listing an image folder.
- Preserve formulas as LaTeX and convert important numerical comparisons into Markdown tables.
- Analyze experiments, baselines, metrics, result values, ablations, and conclusion boundaries. A shallow summary is not acceptable for a paper-reading request.
- Generate `notion_payload.json` before writing when possible, then validate it with `scripts/validate_notion_payload.py`. If `content.image_status` is `hosted`, run the validator with `--check-image-urls` before writing to Notion.
- If the runtime has no first-class Notion connector, optionally publish one paper with `scripts/publish_notion_payload.py` only after the user explicitly chooses a token-based fallback.
- Use DOI, arXiv ID, or normalized original title for deduplication.
- Create a new page in the paper database when no match exists; update the existing page when a match exists.
- Fetch or query Notion after writing to verify that the record is searchable and the page body was created.

## Language Policy

- Default report language: English.
- Use Chinese only when the user asks for Chinese output.
- Use bilingual output when the user asks for bilingual, dual-language, English and Chinese, or similar wording.
- For bilingual reports, prefer an English full report with a compact Chinese overview unless the user asks for full section-by-section bilingual writing.
- Store the selected language in the `Report Language` database property.

## Required Database Fields

Use this compact schema unless the user asks to customize it:

- `Name`
- `Original Title`
- `Authors`
- `Publication Date`
- `Year`
- `Created Date`
- `Venue`
- `Field`
- `Type`
- `Keywords`
- `Reading Status`
- `Read Date`
- `Rating`
- `DOI`
- `arXiv`
- `Code`
- `Report Language`

Do not add long analytical fields such as contribution, technical core, limitations, or evidence summary to the database by default. Put those in the report page.

## Useful Scripts

- `scripts/setup_environment.py`: Check Python/PDF dependencies and optionally create the skill-local `.venv`.
- `scripts/fetch_arxiv_html.py`: Fetch official arXiv HTML renderings and extract title, authors, abstract, sections, verified figures, tables, and equation counts into a reading pack.
- `scripts/smoke_test_attention.py`: Download and parse the Attention Is All You Need paper, then generate a local test report and payload.
- `scripts/schema_tool.py`: Validate `config/notion_schema.yaml` and render Notion DDL/add-column statements.
- `scripts/build_notion_payload.py`: Normalize metadata and report paths into a `notion_payload.json` file.
- `scripts/build_evidence_pack.py`: Build a self-contained local HTML evidence pack from Markdown image links.
- `scripts/validate_notion_payload.py`: Validate required fields, language, rating, URLs, dedup key, report existence, and optionally hosted image reachability before publishing.
- `scripts/publish_notion_payload.py`: Single-paper Notion REST fallback. Validates a payload, deduplicates by DOI/arXiv/title, then creates or updates one Notion page.

## Public Positioning

Read `references/positioning.md` when preparing GitHub copy, roadmap notes, or comparisons with adjacent paper-to-Notion tools.

## Final Response

When the task completes, report only the useful handoff details:

- Notion database or page URL.
- Local report path, if one was produced.
- Image status: hosted, local-only, placeholder, or no images.
- Validation result and any remaining manual step.
