# Paper To Notion Skill

Evidence-driven paper reading for Codex, Claude, WorkBuddy, and compatible MCP/CLI agent runtimes. This skill turns an academic paper into a durable Notion record: a lean database row for indexing, plus a rich report page with grounded evidence, formulas, figures, tables, code checks, limitations, and reproducibility notes.

The default report language is English. Chinese and bilingual reports are supported when requested.

## Install

### Option 1: Agent-Assisted Install

If you already use Codex or Claude Code, the easiest path is to ask the agent to install the skill and run the first setup pass for you.

For Codex, paste this into a Codex session:

```text
Please install this skill:
https://github.com/Guesswhat-Studio/paper-to-notion-skill

Install it into my Codex skills directory, then use $paper-to-notion-skill to set up my Notion paper reading workflow. Please handle the setup automatically: prepare the local Python environment, create or reuse the Paper Reading Library database, validate the schema, run the Attention Is All You Need smoke test, save .paper-notion/config.json, and only report the final database/page URLs, validation status, and any action I must take.
```

For Claude Code, paste this into Claude Code:

```text
Please install this Claude Code plugin:
https://github.com/Guesswhat-Studio/paper-to-notion-skill

Add it as a plugin marketplace, install paper-to-notion@guesswhat-paper-tools, then use /paper-to-notion:paper-to-notion-skill to set up my Notion paper reading workflow. Please handle the setup automatically: prepare the local Python environment, create or reuse the Paper Reading Library database, validate the schema, run the Attention Is All You Need smoke test, save .paper-notion/config.json, and only report the final database/page URLs, validation status, and any action I must take.
```

Claude Code users can also run the install inside an interactive Claude Code session:

```text
/plugin marketplace add Guesswhat-Studio/paper-to-notion-skill
/plugin install paper-to-notion@guesswhat-paper-tools
/reload-plugins
/paper-to-notion:paper-to-notion-skill set up my Notion paper reading workflow
```

If you prefer a single terminal command for Claude Code:

```bash
claude plugin marketplace add Guesswhat-Studio/paper-to-notion-skill && claude plugin install paper-to-notion@guesswhat-paper-tools && claude -p "Use /paper-to-notion:paper-to-notion-skill to set up my Notion paper reading workflow. Keep the setup automatic: prepare the local Python environment, create or reuse the Paper Reading Library database, validate the schema, run the Attention Is All You Need smoke test, save .paper-notion/config.json, and only report the final database/page URLs, validation status, and any action I must take."
```

Claude chat on the web does not load Claude Code plugins directly. Use Claude Code or Claude Cowork plugin support for this repository.

### Option 2: Manual Install

#### Codex

Windows default Codex skills directory:

```cmd
git clone https://github.com/Guesswhat-Studio/paper-to-notion-skill.git "%USERPROFILE%\.codex\skills\paper-to-notion-skill"
```

Windows with a custom `CODEX_HOME`:

```cmd
git clone https://github.com/Guesswhat-Studio/paper-to-notion-skill.git "%CODEX_HOME%\skills\paper-to-notion-skill"
```

macOS or Linux:

```bash
git clone https://github.com/Guesswhat-Studio/paper-to-notion-skill.git "$HOME/.codex/skills/paper-to-notion-skill"
```

After cloning, ask Codex:

```text
Use $paper-to-notion-skill to set up my Notion paper reading workflow.
```

#### Claude Code

Add the repository as a Claude Code plugin marketplace and install the plugin:

```bash
claude plugin marketplace add Guesswhat-Studio/paper-to-notion-skill
claude plugin install paper-to-notion@guesswhat-paper-tools
```

Then start Claude Code and ask:

```text
Use /paper-to-notion:paper-to-notion-skill to set up my Notion paper reading workflow.
```

Claude Cowork users can add the same GitHub repository as a plugin marketplace from Customize -> Plugins, then install `Paper To Notion` from `guesswhat-paper-tools`.

For private repository installs, the user must already have GitHub access to `Guesswhat-Studio/paper-to-notion-skill`. Claude Code can add a GitHub repository as a plugin marketplace, then install `paper-to-notion@guesswhat-paper-tools`. The marketplace and plugin structure in this repo follows the Claude Code plugin docs:

- [Discover and install plugins](https://code.claude.com/docs/en/discover-plugins)
- [Create and distribute plugin marketplaces](https://code.claude.com/docs/en/plugin-marketplaces)
- [Plugins reference](https://code.claude.com/docs/en/plugins-reference)

## What It Does

- Reads papers from a local PDF, arXiv URL, DOI, paper URL, or title.
- Resolves paper identity and verifies metadata from the paper or official sources.
- Builds a source registry and reading pack before writing the report.
- Extracts evidence from formulas, figures, tables, algorithms, theorems, model diagrams, ablations, robustness panels, and result sections when available.
- Generates Notion-ready reports with source-grounded claims and explicit uncertainty markers.
- Creates or updates a Notion database page using DOI, arXiv ID, or normalized original title for deduplication.
- Keeps the Notion database compact while putting deep analysis in the page body.
- Provides local validation scripts, schema tooling, and a smoke test based on "Attention Is All You Need".

## Repository Contents

```text
paper-to-notion-skill/
  .claude-plugin/marketplace.json  # Claude Code marketplace catalog
  SKILL.md                         # Main skill instructions
  requirements.txt                 # Python dependencies
  agents/openai.yaml               # Agent configuration example
  config/notion_schema.yaml        # Default Notion database schema
  plugins/paper-to-notion/         # Claude Code plugin package
  references/                      # Reading, publishing, connector, and setup contracts
  scripts/                         # Environment, payload, validation, and publishing helpers
```

## Requirements

- Python 3.10 or newer.
- A compatible agent runtime, such as Codex, Claude, WorkBuddy, or another MCP/CLI runtime.
- Notion read/write access through the runtime connector, or a Notion integration token only when using the optional REST fallback.
- Optional: `uv` for faster environment setup.
- Optional: `gh`, `git`, and `tesseract` for GitHub checks, repository inspection, and OCR support.

## Maintainer Notes

The install section above is the intended user path. The commands below are for maintainers, debugging, and air-gapped setup.

Clone the repository:

```bash
git clone https://github.com/Guesswhat-Studio/paper-to-notion-skill.git
cd paper-to-notion-skill
```

Install it as a Codex skill by placing the folder under your Codex skills directory:

```bash
mkdir -p ~/.codex/skills
cp -R paper-to-notion-skill ~/.codex/skills/
```

On Windows PowerShell, copy it to:

```powershell
New-Item -ItemType Directory -Force $env:USERPROFILE\.codex\skills
Copy-Item -Recurse . $env:USERPROFILE\.codex\skills\paper-to-notion-skill
```

For Claude Code plugin testing from a local checkout:

```bash
claude plugin validate .
claude plugin validate ./plugins/paper-to-notion
claude plugin marketplace add .
claude plugin install paper-to-notion@guesswhat-paper-tools
```

For WorkBuddy or other compatible runtimes, add this repository as a skill/workflow directory and make `SKILL.md` available to the agent.

## What The Agent Sets Up

After installation, Codex or Claude should perform the remaining setup from the skill instructions:

- Detect the runtime and available Notion connector.
- Create or reuse `Paper Reading Library`.
- Validate the default schema in `config/notion_schema.yaml`.
- Prepare a skill-local Python environment.
- Run the `Attention Is All You Need` smoke test when network access is available.
- Save workspace state in `.paper-notion/config.json`.
- Verify that the Notion database can be fetched and queried.

## Manual Environment Commands

From the skill directory, create a skill-local virtual environment and install dependencies:

```bash
python scripts/setup_environment.py --use-uv --install --json-report .paper-notion/environment-check.json
```

If you already have a Python environment and only want to check it:

```bash
python scripts/setup_environment.py --check-only
```

Validate the default Notion schema:

```bash
python scripts/schema_tool.py --command validate
```

Run the local smoke test:

```bash
python scripts/smoke_test_attention.py --output .paper-notion/smoke-test
```

The smoke test downloads "Attention Is All You Need", opens it with PyMuPDF, renders a first-page evidence image, writes sample metadata and report files, builds `notion_payload.json`, and validates the payload.

## Notion Database

The default database is named `Paper Reading Library`. It intentionally stays lean:

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

Long analytical material belongs in the Notion page body, not in database properties.

The machine-readable schema lives in:

```text
config/notion_schema.yaml
```

Render a schema summary:

```bash
python scripts/schema_tool.py --command summary
```

Render Notion setup instructions:

```bash
python scripts/schema_tool.py --command ddl
```

If your Notion connector does not support `STATUS` or `PEOPLE` fields, render fallback instructions:

```bash
python scripts/schema_tool.py --command ddl --use-fallbacks
```

## Typical Agent Usage

Set up the workflow:

```text
Use $paper-to-notion-skill to set up my Notion paper reading workflow.

Please detect my runtime, check whether Notion read/write access is available, create or reuse a Notion database named Paper Reading Library, prepare the local Python environment, run the Attention Is All You Need smoke test, save .paper-notion/config.json, and verify the database can be fetched and queried.
```

Read and publish a paper in English:

```text
Use $paper-to-notion-skill to read this paper in English and save it to my Notion paper database:

https://arxiv.org/abs/1706.03762

Please resolve the paper identity, extract verified metadata, capture important evidence, generate a Notion-ready report with formulas, figures, tables, code and reproducibility notes, create or update the database record, and verify the Notion page after publishing.
```

Read and publish a paper in Chinese:

```text
Use $paper-to-notion-skill to read this paper in Chinese and save it to my Notion paper database:

<PDF path, DOI, arXiv URL, paper URL, or title>

Please keep the official English title in Original Title, write the report body in Chinese, preserve formulas in LaTeX, include key figures and tables, and verify the database record after publishing.
```

Publish an existing report:

```text
Use $paper-to-notion-skill to publish this existing report to my Notion paper database:

Report path: <report.md>
Metadata path: <metadata.json>

Please build or validate notion_payload.json, deduplicate by DOI/arXiv/title, create or update the Notion page, and verify the result.
```

## Payload Workflow

Build a Notion payload from paper metadata and a Markdown report:

```bash
python scripts/build_notion_payload.py \
  --metadata metadata.json \
  --report report.md \
  --output notion_payload.json \
  --language English \
  --image-status local_only
```

Validate the payload:

```bash
python scripts/validate_notion_payload.py notion_payload.json
```

Build a self-contained local evidence pack from Markdown image links:

```bash
python scripts/build_evidence_pack.py \
  --report report.md \
  --output evidence-pack.html \
  --title "Evidence Pack"
```

Use the REST fallback only when no first-class Notion connector is available and you explicitly choose token-based publishing:

```bash
export NOTION_TOKEN="<notion integration token>"
export NOTION_DATA_SOURCE_ID="<notion data source id>"
python scripts/publish_notion_payload.py notion_payload.json --dry-run
python scripts/publish_notion_payload.py notion_payload.json --if-exists update
```

The preferred path is always the runtime's authenticated Notion connector. The REST fallback is intentionally limited to single-paper create/update flows.

## Evidence And Report Policy

- Every factual claim should be traceable to the paper or an official source.
- Important formulas stay in LaTeX.
- Important numerical comparisons should become Markdown tables.
- Local-only images should be packaged with `scripts/build_evidence_pack.py` when the Notion connector cannot upload files.
- Code and reproducibility notes should say what was checked and what remains unverified.
- Uncertain inferences should be labeled as uncertain.

## Configuration State

Workspace-specific setup state should live outside the repository in:

```text
.paper-notion/config.json
```

Typical fields:

- `runtime`
- `notion_database_id`
- `notion_data_source_id`
- `schema_version`
- `default_report_language`

This folder is ignored by Git because it can contain local runtime state.

## Roadmap

- Batch import from text files, CSV, Zotero exports, or Notion backlogs.
- Optional GitHub/jsDelivr image hosting helper for Notion-safe image URLs.
- arXiv source asset extraction for higher-quality figures and tables.
- Semantic Scholar or OpenAlex citation enrichment.
- Optional daily discovery mode with arXiv categories, scoring, and conference tracking.
- Team-reading workflows with assignment, priority, review status, and weekly digests.
- Local vector index for follow-up Q&A over processed papers.

## License

No license has been selected yet. Add a license before publishing this repository for broad external reuse.
