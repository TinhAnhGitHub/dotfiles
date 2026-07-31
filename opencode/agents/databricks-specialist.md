---
description: >
  Databricks specialist for architecture, data engineering, SQL warehouses,
  Lakebase Postgres, Unity Catalog/governance, data sharing, Genie/AI-BI,
  apps, ML/MLOps, agents, Spark, compute, bundles, CLI/SDK/API, Terraform,
  notebooks, tables, and best practices. Can research official docs and
  Databricks GitHub examples, delegate documentation exploration, use
  Databricks skills, and—when explicitly asked to end/consolidate a
  session—convert lessons into Databricks skills or update this agent's rules.
mode: all
model: opencode-go/deepseek-v4-flash
temperature: 0.2
color: "#ff6f00"
steps: 160
permission:
  read: allow
  glob: allow
  grep: allow
  list: allow
  lsp: allow
  todowrite: allow
  question: allow
  task: allow
  skill: allow
  webfetch: allow
  crawl4ai_*: allow
  context7_*: allow
  codebase-memory-mcp_*: allow
  edit: ask
  write: ask
  bash:
    "*": ask
    "databricks *": ask
    "python *": ask
    "pip *": ask
    "uv *": ask
    "uvx *": ask
    "git status*": allow
    "git diff*": allow
    "git log*": allow
    "git show*": allow
    "pwd": allow
    "ls": allow
    "ls *": allow
    "rg *": allow
  external_directory:
    "*": ask
    "$HOME/.config/opencode/**": ask
    "$HOME/.config/opencode/agents/**": ask
    "$HOME/.config/opencode/skills/**": ask
    "$HOME/.agents/skills/databricks/**": ask
    "$HOME/.claude/skills/databricks-platform/**": ask
---
{file:./prompts/databricks-specialist.txt}
