---
description: >
  Explores websites, blogs, and articles by crawling links in BFS/DFS hybrid
  style. Given URLs and keywords, it navigates sections to retrieve
  comprehensive content via webfetch and crawl4ai.
mode: all
model: opencode-go/deepseek-v4-flash
temperature: 0.2
color: "#00ff88"
steps: 25
permission:
  webfetch: allow
  crawl4ai_*: allow
  task: allow
  read: allow
  edit: deny
  bash: allow
  glob: allow
  grep: allow
  todowrite: allow
---
{file:./prompts/web-explorer.txt}
