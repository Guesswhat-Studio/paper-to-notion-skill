# Notion Database Schema

Use this reference for setup, schema verification, schema repair, and view creation.

The machine-readable source of truth is `config/notion_schema.yaml`. Users should customize that YAML file, not this reference, when changing database fields. Use `scripts/schema_tool.py` to validate and render DDL from the YAML.

## Database Purpose

The database is an index, not the report itself. Keep it small enough to scan, filter, sort, and review. Put long summaries, technical analysis, formulas, screenshots, tables, code audit notes, limitations, and rating rationale inside the Notion page body.

Default database title: `Paper Reading Library`.

## Required Properties

These are the default required/index properties from `config/notion_schema.yaml`.

| Property | Type | Purpose |
| --- | --- | --- |
| `Name` | `TITLE` | Display title. English by default. |
| `Original Title` | `RICH_TEXT` | Official paper title. |
| `Authors` | `RICH_TEXT` | Author list as written in the paper. |
| `Publication Date` | `DATE` | Publication, arXiv, conference, or journal date when known. |
| `Year` | `NUMBER` | Numeric year for filtering and charts. |
| `Created Date` | `CREATED_TIME` | Notion-created timestamp. |
| `Venue` | `MULTI_SELECT` | Venue labels such as arXiv, NeurIPS, ICML, ACL, Journal, Workshop. |
| `Field` | `MULTI_SELECT` | Broad research area labels. |
| `Type` | `MULTI_SELECT` | Paper or contribution type labels such as method, survey, benchmark, empirical. |
| `Keywords` | `RICH_TEXT` | Paper-specific keywords or topic phrases, comma-separated. |
| `Reading Status` | `STATUS` or `SELECT` | Workflow state: To Read, Reading, Read, Reviewed. |
| `Read Date` | `DATE` | Date the report was written or last substantially updated. |
| `Rating` | `SELECT` | Reader rating: 1 star through 5 stars. |
| `DOI` | `URL` | DOI URL, preferably `https://doi.org/...`. |
| `arXiv` | `URL` | arXiv abstract URL. |
| `Code` | `URL` | Official code or best verified implementation URL. |
| `Report Language` | `SELECT` | English, Chinese, or Bilingual. |

## Codex Notion DDL

When the Codex Notion plugin exposes `create_database`, generate DDL from the YAML:

```bash
python scripts/schema_tool.py --command ddl
```

If the tool rejects custom options for `STATUS`, render fallback types:

```bash
python scripts/schema_tool.py --command ddl --use-fallbacks
```

The default generated DDL should look like this:

```sql
CREATE TABLE (
  "Name" TITLE,
  "Original Title" RICH_TEXT,
  "Authors" RICH_TEXT,
  "Publication Date" DATE,
  "Year" NUMBER,
  "Created Date" CREATED_TIME,
  "Venue" MULTI_SELECT('arXiv':gray, 'NeurIPS':blue, 'ICML':blue, 'ICLR':purple, 'ACL':green, 'EMNLP':green, 'CVPR':red, 'ICCV':red, 'ECCV':red, 'SIGGRAPH':orange, 'KDD':yellow, 'WWW':yellow, 'AAAI':purple, 'IJCAI':purple, 'Journal':brown, 'Workshop':gray, 'Preprint':gray),
  "Field" MULTI_SELECT('Machine Learning':blue, 'Natural Language Processing':green, 'Computer Vision':red, 'Robotics':orange, 'Systems':gray, 'Theory':purple, 'HCI':pink, 'Data':yellow, 'Security':brown),
  "Type" MULTI_SELECT('method':blue, 'survey':purple, 'benchmark':yellow, 'dataset':green, 'theory':purple, 'system':gray, 'empirical':orange, 'application':pink),
  "Keywords" RICH_TEXT,
  "Reading Status" STATUS,
  "Read Date" DATE,
  "Rating" SELECT('1 star':red, '2 stars':orange, '3 stars':yellow, '4 stars':green, '5 stars':blue),
  "DOI" URL,
  "arXiv" URL,
  "Code" URL,
  "Report Language" SELECT('English':blue, 'Chinese':green, 'Bilingual':purple)
)
```

## Setup Procedure

1. Search Notion for an existing database named `Paper Reading Library` or the user-provided localized name.
2. If found, fetch the database and identify its data source URL, usually `collection://...`.
3. Compare the existing properties to the required schema.
4. If required properties are missing, use the connector's schema update operation to add only missing fields.
5. If no database exists, create it with DDL generated from `config/notion_schema.yaml`.
6. Create or confirm useful views:
   - `All Papers`: table, sorted by `Read Date` descending.
   - `By Venue`: board or table grouped by `Venue` when supported.
   - `To Review`: table, filtered to records not marked `Reviewed`.
   - `Top Rated`: table, sorted by `Rating` descending when the connector supports select sorting.
7. Save `.paper-notion/config.json` in the active workspace:

```json
{
  "runtime": "codex|claude|workbuddy|compatible",
  "notion_database_id": "",
  "notion_data_source_id": "",
  "schema_version": "1.0.0",
  "default_report_language": "English",
  "default_database_title": "Paper Reading Library",
  "environment_manager": "uv",
  "venv": ".paper-notion/.venv",
  "python_windows": ".paper-notion/.venv/Scripts/python.exe",
  "python_posix": ".paper-notion/.venv/bin/python",
  "last_environment_check": ".paper-notion/environment-check.json",
  "last_smoke_test": ".paper-notion/smoke-test/notion_payload.json"
}
```

## Property Value Rules

- `Name`: Use the original English title by default. Use a Chinese title only when the user requests Chinese-first records.
- `Authors`: Keep names in the original author spelling. Do not translate names.
- `Publication Date`: Use the most official precise date available. If only the year is known, write `Year` and omit `Publication Date`.
- `Venue`: Use multiple values if needed, such as `arXiv` plus `NeurIPS`.
- `Type`: Use one or more controlled paper/contribution type labels. Put values like `method`, `survey`, `benchmark`, or `empirical` here.
- `Keywords`: Use paper-specific terms from the paper, such as method names, tasks, datasets, mechanisms, or domains. Store them as comma-separated text.
- `Rating`: Leave blank unless the user provides a rating or the reading report includes a clearly stated reader rating.
- `DOI`, `arXiv`, `Code`: Use blank values when unknown. Do not put search-result guesses into URL fields.

## Optional Research-Flow Extensions

Do not create these fields by default. They are defined under `optional_extensions.research_flow` in `config/notion_schema.yaml`. Add them only when the user asks for daily paper discovery, conference tracking, paper scoring, or team reading workflows.

| Property | Type | Purpose |
| --- | --- | --- |
| `Score` | `NUMBER` | Composite score for discovery triage. |
| `Relevance Score` | `NUMBER` | Interest/category match score. |
| `Recency Score` | `NUMBER` | Freshness score. |
| `Popularity Score` | `NUMBER` | Citation/venue signal. |
| `Social Score` | `NUMBER` | GitHub stars, social mentions, or community signal. |
| `Quality Score` | `NUMBER` | Abstract/method/author/venue quality estimate. |
| `Assignee` | `PEOPLE` or `RICH_TEXT` | Team reader assignment. |
| `Priority` | `SELECT` | Triage priority. |
| `Discovery Source` | `SELECT` | arXiv, Semantic Scholar, DBLP, OpenReview, manual, etc. |
| `Conference Year` | `NUMBER` | Conference tracking. |

When using optional scores, explain scoring formulas in the page body or setup notes. Keep the default reading database usable without these fields.

## Duplicate Keys

Prefer deduplication in this order:

1. DOI URL.
2. arXiv ID.
3. Normalized original title.

The normalized title should be lowercase ASCII where possible, with punctuation collapsed and whitespace normalized.
