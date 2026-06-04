# Paper To Notion Skill

[English](README.md) | [简体中文](README.zh-CN.md)

`paper-to-notion-skill` 是一个面向 Codex、Claude、WorkBuddy 以及兼容 MCP/CLI agent runtime 的论文阅读与 Notion 发布 skill。它会把论文整理成一个可长期维护的 Notion 记录：数据库里保留轻量索引字段，页面正文里承载深度阅读报告、公式、图表、实验结果、代码检查、局限性和复现笔记。

默认报告语言是英文。你也可以要求中文报告或中英双语报告。

## 安装

### 方式 1：让 Agent 自动安装

如果你已经在用 Codex 或 Claude Code，最省事的方式是直接把安装任务交给 agent。它会安装 skill，并继续完成第一次工作流设置。

#### Codex 用户

把下面这段话发给 Codex：

```text
请帮我安装这个 skill：
https://github.com/Guesswhat-Studio/paper-to-notion-skill

请把它安装到我的 Codex skills 目录，然后使用 $paper-to-notion-skill 设置我的 Notion 论文阅读工作流。请自动完成后续设置：准备本地 Python 环境，创建或复用 Paper Reading Library 数据库，校验 schema，运行 Attention Is All You Need smoke test，保存 .paper-notion/config.json，最后只告诉我数据库或页面 URL、验证结果，以及还需要我手动处理的事项。
```

#### Claude Code 用户

把下面这段话发给 Claude Code：

```text
请帮我安装这个 Claude Code plugin：
https://github.com/Guesswhat-Studio/paper-to-notion-skill

请把它添加为 plugin marketplace，安装 paper-to-notion@guesswhat-paper-tools，然后使用 /paper-to-notion:paper-to-notion-skill 设置我的 Notion 论文阅读工作流。请自动完成后续设置：准备本地 Python 环境，创建或复用 Paper Reading Library 数据库，校验 schema，运行 Attention Is All You Need smoke test，保存 .paper-notion/config.json，最后只告诉我数据库或页面 URL、验证结果，以及还需要我手动处理的事项。
```

你也可以在 Claude Code 交互会话里直接运行：

```text
/plugin marketplace add Guesswhat-Studio/paper-to-notion-skill
/plugin install paper-to-notion@guesswhat-paper-tools
/reload-plugins
/paper-to-notion:paper-to-notion-skill set up my Notion paper reading workflow
```

如果你更喜欢一条终端命令：

```bash
claude plugin marketplace add Guesswhat-Studio/paper-to-notion-skill && claude plugin install paper-to-notion@guesswhat-paper-tools && claude -p "Use /paper-to-notion:paper-to-notion-skill to set up my Notion paper reading workflow. Keep the setup automatic: prepare the local Python environment, create or reuse the Paper Reading Library database, validate the schema, run the Attention Is All You Need smoke test, save .paper-notion/config.json, and only report the final database/page URLs, validation status, and any action I must take."
```

Claude 网页聊天不会直接加载 Claude Code plugin。请使用 Claude Code，或在支持插件的 Claude Cowork 里安装。

### 方式 2：手动安装

#### Codex

Windows 默认 Codex skills 目录：

```cmd
git clone https://github.com/Guesswhat-Studio/paper-to-notion-skill.git "%USERPROFILE%\.codex\skills\paper-to-notion-skill"
```

Windows 自定义 `CODEX_HOME`：

```cmd
git clone https://github.com/Guesswhat-Studio/paper-to-notion-skill.git "%CODEX_HOME%\skills\paper-to-notion-skill"
```

macOS 或 Linux：

```bash
git clone https://github.com/Guesswhat-Studio/paper-to-notion-skill.git "$HOME/.codex/skills/paper-to-notion-skill"
```

安装完成后，在 Codex 里说：

```text
Use $paper-to-notion-skill to set up my Notion paper reading workflow.
```

#### Claude Code

把仓库添加为 Claude Code plugin marketplace，并安装插件：

```bash
claude plugin marketplace add Guesswhat-Studio/paper-to-notion-skill
claude plugin install paper-to-notion@guesswhat-paper-tools
```

然后启动 Claude Code 并输入：

```text
Use /paper-to-notion:paper-to-notion-skill to set up my Notion paper reading workflow.
```

Claude Cowork 用户可以在 `Customize -> Plugins` 里添加同一个 GitHub 仓库作为 marketplace，然后从 `guesswhat-paper-tools` 安装 `Paper To Notion`。

如果仓库仍是 private，安装者需要拥有 `Guesswhat-Studio/paper-to-notion-skill` 的访问权限。Claude Code 会把这个 GitHub 仓库当作 marketplace，再安装 `paper-to-notion@guesswhat-paper-tools`。相关 Claude 官方文档：

- [Discover and install plugins](https://code.claude.com/docs/en/discover-plugins)
- [Create and distribute plugin marketplaces](https://code.claude.com/docs/en/plugin-marketplaces)
- [Plugins reference](https://code.claude.com/docs/en/plugins-reference)

## CI

GitHub Actions 会在 push 和 pull request 时运行轻量验证：

- 编译 Python helper scripts。
- 用 `tools/validate_repository.py` 检查仓库打包结构和 Claude plugin 副本同步。
- 校验 Notion schema。
- 检查 helper CLI 入口。

arXiv network smoke test 只在手动 `workflow_dispatch` 且设置 `run_network_smoke=true` 时运行，避免临时网络或 arXiv 波动阻塞普通 PR。

## 这个 Skill 能做什么

- 从本地 PDF、arXiv URL、DOI、论文 URL 或论文标题开始阅读。
- 从论文原文或官方来源核对标题、作者、日期、venue、DOI、arXiv、代码仓库等元数据。
- 写报告前先建立 source registry 和 reading pack，减少无来源推断。
- arXiv 论文优先使用官方 HTML 渲染：`https://arxiv.org/html/<arxiv_id>`。
- arXiv HTML 里的 figure 图片 URL 如果是 HTTPS 可访问，可以直接作为 Notion hosted image 外链使用。
- 抽取并解释关键证据：公式、图、表、算法、定理、模型结构图、实验结果、消融、鲁棒性分析等。
- 生成 Notion-ready 报告，保留 LaTeX 公式、Markdown 表格、代码和复现检查记录。
- 使用 DOI、arXiv ID 或规范化原始标题去重，创建或更新 Notion 数据库页面。
- 数据库只保留索引字段，长分析放进页面正文。
- 附带本地脚本：环境检查、schema 校验、payload 构建、payload 验证、Notion REST fallback 和 smoke test。

## 仓库结构

```text
paper-to-notion-skill/
  .claude-plugin/marketplace.json  # Claude Code marketplace catalog
  LICENSE                          # MIT license
  SKILL.md                         # 主 skill 指令
  requirements.txt                 # Python 依赖
  agents/openai.yaml               # agent 配置示例
  config/notion_schema.yaml        # 默认 Notion 数据库 schema
  plugins/paper-to-notion/         # Claude Code plugin package
  references/                      # 阅读、发布、连接器、环境设置参考
  scripts/                         # 环境、payload、校验、发布辅助脚本
```

## 环境要求

- Python 3.10 或更新版本。
- Codex、Claude、WorkBuddy，或兼容 MCP/CLI 的 agent runtime。
- 通过 runtime connector 获得 Notion 读写权限；只有在使用 REST fallback 时才需要 Notion integration token。
- 可选：`uv`，用于更快地创建本地环境。
- 可选：`gh`、`git`、`tesseract`，用于 GitHub 检查、代码仓库核查和扫描版 PDF OCR。

## Agent 会自动设置什么

安装完成后，Codex 或 Claude 应该根据 `SKILL.md` 继续完成这些设置：

- 检测当前 runtime 和可用的 Notion connector。
- 创建或复用 `Paper Reading Library`。
- 校验 `config/notion_schema.yaml`。
- 准备 skill-local Python 环境。
- 网络可用时运行 `Attention Is All You Need` smoke test。
- 在工作区保存 `.paper-notion/config.json`。
- 验证 Notion 数据库可以 fetch 和 query。

## Notion 数据库

默认数据库名是 `Paper Reading Library`。默认字段保持紧凑：

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

长篇贡献分析、技术核心、实验解释、局限性、复现记录和证据链放在 Notion 页面正文里。机器可读 schema 位于：

```text
config/notion_schema.yaml
```

## 常用调用方式

设置工作流：

```text
Use $paper-to-notion-skill to set up my Notion paper reading workflow.
```

常见输入路由保持简单：

- 本地 PDF：走 PDF 解析和证据截图路径。
- arXiv 链接或 ID：优先尝试官方 arXiv HTML，包括 figure 图片 URL；HTML 不可用再回退 PDF。
- Publisher URL、DOI 或标题：先抓 metadata 和可访问的 full-text HTML；如果页面需要权限，请用户提供 PDF。
- 已有 report 或 payload：跳过阅读，只做 payload 校验和 Notion 发布。

阅读并发布英文报告：

```text
Use $paper-to-notion-skill to read this paper in English and save it to my Notion paper database:

https://arxiv.org/abs/1706.03762

Please resolve the paper identity, extract verified metadata, capture important evidence, generate a Notion-ready report with formulas, figures, tables, code and reproducibility notes, create or update the database record, and verify the Notion page after publishing.
```

阅读并发布中文报告：

```text
Use $paper-to-notion-skill to read this paper in Chinese and save it to my Notion paper database:

<PDF path, DOI, arXiv URL, paper URL, or title>

Please keep the official English title in Original Title, write the report body in Chinese, preserve formulas in LaTeX, include key figures and tables, and verify the database record after publishing.
```

发布已有报告：

```text
Use $paper-to-notion-skill to publish this existing report to my Notion paper database:

Report path: <report.md>
Metadata path: <metadata.json>

Please build or validate notion_payload.json, deduplicate by DOI/arXiv/title, create or update the Notion page, and verify the result.
```

## 手动环境命令

这些命令主要给维护者、调试或离线环境使用。普通用户可以让 Codex 或 Claude 自动处理。

创建 skill-local 虚拟环境并安装依赖：

```bash
python scripts/setup_environment.py --use-uv --install --json-report .paper-notion/environment-check.json
```

只检查当前环境：

```bash
python scripts/setup_environment.py --check-only
```

校验 Notion schema：

```bash
python scripts/schema_tool.py --command validate
```

从 arXiv HTML 生成结构化 reading pack：

```bash
python scripts/fetch_arxiv_html.py 1706.03762 --output .paper-notion/arxiv-html-test --limit 5
```

运行本地 smoke test：

```bash
python scripts/smoke_test_attention.py --output .paper-notion/smoke-test
```

生成 schema 摘要：

```bash
python scripts/schema_tool.py --command summary
```

生成 Notion 建库说明：

```bash
python scripts/schema_tool.py --command ddl
```

如果 Notion connector 不支持 `STATUS` 或 `PEOPLE` 字段，可以生成 fallback 说明：

```bash
python scripts/schema_tool.py --command ddl --use-fallbacks
```

## 免费图床和图片托管

如果 Notion connector 支持原生上传图片，优先让 connector 直接上传。connector 无法上传本地图片时，可以考虑这些免费或有免费额度的方案：

- **GitHub public repo + [jsDelivr](https://github.com/jsdelivr/jsdelivr)**：适合公开研究笔记和静态证据图片。把图片提交到公开仓库后，使用 `https://cdn.jsdelivr.net/gh/<owner>/<repo>@<commit>/<path>` 这类 URL。jsDelivr 对开源文件免费，并支持 GitHub-backed CDN。
- **[Cloudinary free plan](https://cloudinary.com/documentation/billing_and_plans)**：适合需要 API 上传、素材管理后台、图片变换和 CDN 的场景。Cloudinary free plan 当前提供每月 credits，可用于 transformations、storage 和 bandwidth。
- **Local evidence pack**：适合不便公开的图片、受版权限制的图，或还没准备发布的报告。使用 `scripts/build_evidence_pack.py` 生成本地 HTML evidence pack，然后在 Notion 页面里说明或链接这个本地包。

如果论文 license 或团队策略不允许公开分发图片，不建议把论文图表上传到公共图床。

## Payload 工作流

从 metadata 和 Markdown report 构建 Notion payload：

```bash
python scripts/build_notion_payload.py \
  --metadata metadata.json \
  --report report.md \
  --output notion_payload.json \
  --language English \
  --image-status local_only
```

校验 payload：

```bash
python scripts/validate_notion_payload.py notion_payload.json
```

把 Markdown 里的本地图片链接打包成自包含 HTML evidence pack：

```bash
python scripts/build_evidence_pack.py \
  --report report.md \
  --output evidence-pack.html \
  --title "Evidence Pack"
```

只有在没有一等 Notion connector，并且你明确选择 token fallback 时，才使用 REST fallback：

```bash
export NOTION_TOKEN="<notion integration token>"
export NOTION_DATA_SOURCE_ID="<notion data source id>"
python scripts/publish_notion_payload.py notion_payload.json --dry-run
python scripts/publish_notion_payload.py notion_payload.json --if-exists update
```

推荐路径始终是 runtime 自带的已认证 Notion connector。REST fallback 只覆盖单篇论文的 create/update 流程。

## 证据和报告策略

- 事实性表述需要能追溯到论文或官方来源。
- 重要公式保留 LaTeX。
- 关键数值对比整理成 Markdown 表格。
- Notion connector 无法上传本地图片时，用 `scripts/build_evidence_pack.py` 生成本地 evidence pack。
- 代码和复现笔记需要说明检查过什么、哪些仍未验证。
- 不确定推断需要明确标注。

## 本地配置状态

工作区相关的设置状态保存在仓库外：

```text
.paper-notion/config.json
```

常见字段：

- `runtime`
- `notion_database_id`
- `notion_data_source_id`
- `schema_version`
- `default_report_language`

`.paper-notion/` 已被 Git 忽略，因为它可能包含本地 runtime 状态。

## Roadmap

- 从 `.txt`、`.md`、`.csv`、Zotero export 或 Notion backlog 批量导入。
- 可选 GitHub/jsDelivr 图片托管 helper，生成 Notion 可访问图片 URL。
- 更深入的 arXiv source asset extraction，在官方 HTML 渲染之外获取更高质量的图和表。
- Semantic Scholar 或 OpenAlex citation enrichment。
- 可选每日论文发现模式：arXiv 分类、关键词兴趣、评分和会议追踪。
- 团队阅读模式：assignee、priority、review status、weekly digest。
- 本地向量索引，支持对已读论文继续问答。

## License

MIT License。见 [LICENSE](LICENSE)。
