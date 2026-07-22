---
description: >
  Interactive wizard that designs and creates opencode agents end-to-end. Asks
  the user about purpose, mode, model, tools/permissions, rules, and skills;
  advises on choices (runs `opencode models`, recommends built-in vs custom
  tools, picks appropriate skills); then writes the agent file, optional
  AGENTS.md rules, optional custom tools, and registers everything in
  opencode.json. Validates against the config schema and reminds the user to
  restart opencode.
mode: all
model: opencode-go/mimo-v2.5
temperature: 0.2
color: "#cc44ff"
steps: 100
permission:
  read: allow
  glob: allow
  grep: allow
  list: allow
  lsp: allow
  edit: allow
  write: allow
  todowrite: allow
  question: allow
  task: allow
  skill: allow
  webfetch: allow
  crawl4ai_*: allow
  codebase-memory-mcp_*: allow
  context7_*: allow
  bash:
    "*": ask
    "opencode models*": allow
    "opencode model *": allow
    "opencode agent list*": allow
    "opencode agent create*": ask
    "opencode --version*": allow
    "opencode -v*": allow
    "pwd": allow
    "ls *": allow
    "ls": allow
    "cat *": allow
    "head *": allow
    "tail *": allow
    "rg *": allow
    "grep *": allow
    "find *": allow
    "git status*": allow
    "git diff*": allow
    "git log*": allow
    "git show*": allow
    "mkdir *": allow
    "mkdir -p *": allow
    "test -d *": allow
    "test -f *": allow
  external_directory:
    "*": ask
    "C:\\Users\\UAG3HC\\.config\\opencode\\**": allow
    "C:\\Users\\UAG3HC\\.config\\opencode\\agents\\**": allow
    "C:\\Users\\UAG3HC\\.config\\opencode\\tools\\**": allow
    "C:\\Users\\UAG3HC\\.config\\opencode\\skills\\**": allow
    "C:\\Users\\UAG3HC\\.agents\\skills\\**": allow
---
{file:./prompts/agent-builder.txt}
