---
description: >
  Creates, modifies, and manages agent skills. Handles the full skill lifecycle:
  capture intent, research via web/doc-explorers, draft SKILL.md, run test cases
  in parallel, evaluate outputs, iterate on feedback, optimize description with
  trigger evals, and package. Analyzes codebase patterns via codebase-memory-mcp.
mode: all
model: opencode-go/deepseek-v4-flash
temperature: 0.2
color: "#ff8800"
steps: 50
permission:
  read: allow
  edit: allow
  write: allow
  glob: allow
  grep: allow
  lsp: allow
  webfetch: allow
  crawl4ai_*: allow
  codebase-memory-mcp_*: allow
  task: allow
  todowrite: allow
  skill: allow
  question: allow
  bash:
    "*": ask
    "python *aggregate_benchmark*": allow
    "python *generate_review*": allow
    "python *run_loop*": allow
    "python *package_skill*": allow
    "cp -r *": ask
    "kill *": ask
    "nohup *": ask
  external_directory:
    "C:\\Users\\UAG3HC\\.agents\\skills\\*": allow
    "C:\\Users\\UAG3HC\\.config\\opencode\\skills\\*": allow
---
{file:./prompts/skill-manager.txt}
