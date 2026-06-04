# Runtime Connectors

Use this reference during setup when deciding how the skill should write to Notion from a specific agent runtime.

## Supported Runtime Pattern

The skill assumes one of these connector surfaces:

- Codex Notion plugin or MCP-backed Notion tools.
- Claude Notion connector or Notion MCP server.
- WorkBuddy Connector with MCP + CLI or Skill + CLI capability.
- Any compatible runtime that can search, fetch, create/update databases, create/update pages, and query records.

## Codex

Prefer the installed Notion plugin tools when available:

- Search/fetch Notion pages and databases.
- Create databases and views.
- Update data source schema.
- Create and update database pages.
- Query data sources for deduplication and validation.

Fetch the database/data source before writing so property names and data source IDs are exact.
The connector handles authentication. Do not ask for a Notion API token in this path.

## Claude

Prefer Claude's Notion connector or a configured Notion MCP server:

- Use equivalent search, fetch, create, update, and query operations.
- Preserve the same payload semantics as Codex.
- If the connector cannot create databases, ask the user for an existing database URL and repair the schema when possible.

The connector handles authentication. Do not ask for a Notion API token in this path.

## WorkBuddy

WorkBuddy Connector brings external services into AI workflows. Its documented connector forms include:

- `MCP + CLI`, a standardized protocol bridge.
- `Skill + CLI`, built-in script capability.

For this skill:

1. Prefer a Notion MCP connector if the user's WorkBuddy environment has one configured.
2. If Notion is not built in, use WorkBuddy's custom connector path to configure a Notion-compatible MCP server.
3. If MCP write tools are unavailable, use a Skill + CLI bridge that can call a Notion API helper script, but only after the user provides credentials and explicitly approves the write path.
4. Keep the same database schema, payload, deduplication, and validation rules.
5. Treat connector access as user-scoped: operate only within the user's granted permissions and only in response to the current task.

## Capability Checklist

Before running setup or publishing, verify that the runtime can do these operations:

- Search existing pages/databases.
- Fetch database schema and page body.
- Create a database or accept an existing database URL.
- Add missing properties or report the exact missing schema.
- Create a page under a database/data source.
- Update page properties and body.
- Query the database for deduplication.

If any capability is missing, complete local report generation and stop before Notion mutation. Tell the user which connector capability is missing.

If the only missing capability is a first-class connector and the user explicitly chooses a token-based fallback, use `scripts/publish_notion_payload.py` as a single-paper fallback after validating the payload with `--dry-run`.

## Safety Boundary

- Do not create, update, or delete Notion content until the connector is authenticated and the target database/page is identified.
- Do not silently delete test pages. Ask whether to keep, archive, or delete/trash them when deletion is supported.
- Do not store API keys in generated reports or payload files.
- When using custom connectors, remind the user that access scope is controlled by that connector's configuration.
