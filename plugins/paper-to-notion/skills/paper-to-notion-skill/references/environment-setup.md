# Environment Setup

Use this reference during setup and troubleshooting. The goal is to make local PDF reading, figure handling, report payload generation, and sample-paper validation reproducible.

## Managed Environment

Prefer a skill-local uv-managed virtual environment:

```text
paper-to-notion-skill/
  .venv/
  .paper-notion/
    environment-check.json
    smoke-test/
```

From the skill directory, create or check it with:

```bash
python scripts/setup_environment.py --use-uv --install --json-report .paper-notion/environment-check.json
```

Check without installing:

```bash
python scripts/setup_environment.py --check-only
```

If the host already has a reliable Python environment, it is acceptable to use that environment for bootstrapping, but the durable runtime should be the skill-local `.venv`.

## Platform Support

Support Windows, macOS, and Linux:

- Windows: use PowerShell commands and `.venv/Scripts/python.exe`.
- macOS/Linux: use POSIX shell commands and `.venv/bin/python`.
- The Python scripts use `pathlib` and avoid OS-specific path assumptions.
- The bootstrap scripts create the venv in the same skill-local `.venv` location on every platform.

## No Python Available

If Python is missing but shell access and network access are available, bootstrap with uv.

Windows PowerShell:

```powershell
.\scripts\bootstrap_uv.ps1 -InstallUv
```

macOS/Linux:

```bash
INSTALL_UV=1 sh scripts/bootstrap_uv.sh
```

The bootstrap scripts use the official Astral uv installer only when the user explicitly allows uv installation. Then `uv python install` installs a uv-managed Python and creates `.venv` inside the skill directory.

Do not silently install system software. If `uv` and Python are both missing, explain the bootstrap command and ask the user to approve running it.

## Required Python Packages

Install from `requirements.txt`.

| Package | Why it is needed |
| --- | --- |
| `PyMuPDF` | PDF probing, text extraction, rendering pages, cropping figures/tables/equations. |
| `Pillow` | Image verification and simple image handling. |
| `requests` | Download arXiv PDFs, DOI pages, and official metadata pages when needed. |
| `beautifulsoup4` | Parse simple HTML metadata pages. |
| `lxml` | Faster/more tolerant HTML parsing backend. |
| `PyYAML` | Parse and validate the Notion schema YAML. |

## Optional Capabilities

These are useful but not required:

- `git`: Inspect code repositories and commit state.
- `gh`: Query GitHub more reliably when authenticated.
- `tesseract`: OCR scanned PDFs. Python packages alone are not enough; the native binary must also be installed.
- `uv`: Faster reproducible dependency setup when the user prefers it.

When optional tools are missing, continue with degraded behavior and say which feature is unavailable.

## Environment Validation

The setup is healthy when:

- Python is 3.10 or newer.
- Required packages import successfully.
- PyMuPDF can create/open a PDF document.
- Pillow can create/read an image.
- `requests` can make HTTPS requests when network is enabled.
- `scripts/build_notion_payload.py` and `scripts/validate_notion_payload.py` run successfully on a small sample.
- `scripts/schema_tool.py --command validate` runs successfully.
- `scripts/fetch_arxiv_html.py 1706.03762 --output .paper-notion/arxiv-html-test --limit 5` runs successfully when arXiv HTML and network access are available.
- `scripts/publish_notion_payload.py <payload> --dry-run` runs successfully for a valid sample payload.

## Sample Paper Smoke Test

After setup, run:

```bash
python scripts/smoke_test_attention.py --output .paper-notion/smoke-test
```

When using the skill-local venv on Windows:

```bash
.venv/Scripts/python.exe scripts/smoke_test_attention.py --output .paper-notion/smoke-test
```

When using the skill-local venv on macOS/Linux:

```bash
.venv/bin/python scripts/smoke_test_attention.py --output .paper-notion/smoke-test
```

The smoke test uses:

- Title: `Attention Is All You Need`
- arXiv: `https://arxiv.org/abs/1706.03762`
- PDF: `https://arxiv.org/pdf/1706.03762`

It should:

1. Download the PDF.
2. Open it with PyMuPDF.
3. Confirm the title appears in the extracted text.
4. Render a first-page header image.
5. Write `metadata.json`.
6. Write a short `report.md`.
7. Build `notion_payload.json`.
8. Validate the payload.

This test verifies local paper-reading mechanics. It does not prove that Notion publishing works unless the agent also creates or updates a test Notion page.

## Optional Notion Publishing Test

When the user asks for end-to-end validation and Notion write access is available:

1. Use the smoke-test `notion_payload.json`.
2. Change `Name` to `[TEST] Attention Is All You Need`.
3. Create or update a database page.
4. Fetch the page.
5. Query the database by `[TEST] Attention Is All You Need`.
6. Ask the user whether to keep the test page, archive it, or delete it if the connector supports deletion/trashing.

Never silently delete user pages. If deletion/trashing is needed, ask explicitly.

## Common Failures

- Missing `PyMuPDF`: install dependencies into the skill-local `.venv`.
- Native OCR unavailable: proceed with text-layer PDFs and report that scanned PDFs need `tesseract`.
- Network blocked: skip PDF download smoke test and validate only local scripts.
- Notion plugin/connector unavailable: complete local setup and stop before database operations.
