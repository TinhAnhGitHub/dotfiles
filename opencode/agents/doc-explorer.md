---
description: >
  Explores online technical documentation, API references, and tutorials from
  the web. Follows doc hierarchy (TOC -> sections -> subsections) in BFS/DFS
  style. Can fall back to local read/grep for project-internal docs.
mode: all
model: opencode-go/deepseek-v4-flash
temperature: 0.1
color: "#4488ff"
steps: 30
permission:
  webfetch: allow
  crawl4ai_*: allow
  task: allow
  read:
    "*": ask
    "docs/**": allow
    "**/*.md": allow
  grep:
    "*": ask
    "docs/**": allow
  edit: deny
  bash: deny
  glob: deny
  todowrite: deny
---
{file:./prompts/doc-explorer.txt}
