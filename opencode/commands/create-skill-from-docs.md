---
description: Research framework or library documentation recursively and create or update a structured OpenCode skill from URLs and topics
agent: skill-manager
model: openai/gpt-5.6-luna
---

Create or update an OpenCode skill from the documentation request below.

This command is generic. It works for any framework, library, SDK, CLI tool,
platform, or cloud service. Do not assume a domain: evaluation, ML, web, data,
infrastructure, and every other area follow the same workflow below.

## User request

$ARGUMENTS

## Operating instructions

You are the skill-manager. Do the work; do not respond with a research plan
only. Treat every URL in the request as a documentation root and every named
topic as a required coverage area.

### 1. Parse and scope the request

Extract:

- The framework, library, SDK, or platform name (package, service, CLI, or API).
- All documentation URLs, including any sub-folders the user asks to discover
  recursively.
- The requested topics, workflows, APIs, configuration options, and code examples.
- Any requested integrations with companion frameworks or existing skills.
- The desired skill name; if absent, derive a lowercase hyphenated name from the
  framework or library.

If the request is ambiguous, make the smallest reasonable assumption and record it
in the resulting skill rather than stopping for a question. Preserve the user's
terminology, while correcting obvious spelling errors in headings and code.

### 2. Research in parallel

Spawn multiple subagents concurrently before drafting. Use both documentation-focused
and web-focused explorers whenever available:

- `doc-explorer`: official API/reference pages, navigation trees, version notes, and
  runnable examples.
- `web-explorer`: recursively discover child pages, nested topic folders, tutorials,
  migration notes, and related official guides.

Use the model `opencode/deepseek-v4-flash-free` for research subagents when that model
is available. If the configured provider exposes the model under another exact ID,
use the closest configured DeepSeek V4 Flash model and state the resolved ID in the
source ledger. Do not use unofficial blog posts when an official source exists.

Divide research by topic so agents do not duplicate work. For each topic, ask the
subagent to return:

1. Source URLs actually read, including discovered child pages.
2. Version, preview, and platform-scope caveats.
3. The conceptual workflow and why each step exists.
4. API signatures and complete minimal code examples.
5. Automation patterns, failure modes, security/privacy concerns, and operational
   limits.
6. Cross-links to companion skills and prerequisites.

Require agents to distinguish documented facts from inference and to flag conflicting
or stale examples. Recurse through official documentation navigation until the
requested topic is covered or the site reaches unrelated material; do not crawl the
entire domain indiscriminately.

### 3. Synthesize the skill

Create the skill as a sibling subfolder under the appropriate parent skill, for example:

```text
~/.config/opencode/skills/<parent>/<skill-name>/
├── SKILL.md
├── references/
│   ├── source-ledger.md
│   ├── workflows.md
│   ├── api-patterns.md
│   └── troubleshooting.md
├── scripts/                 # only for deterministic helper utilities
└── evals/evals.json
```

If the parent skill does not exist, create a concise parent `SKILL.md` with routing
to this subskill. Update the parent routing table when adding a new subskill. Follow
the OpenCode skill format: lowercase hyphenated folder/name, YAML frontmatter with
`name` and a trigger-rich `description`, and progressive disclosure. Keep the main
`SKILL.md` below roughly 500 lines; move detailed material into references.

The skill must be practical, not a documentation dump. Distill reusable patterns for
each requested topic and include complete, copyable code with imports, inputs, and
outputs. Include:

- A mandatory environment/version preflight (language runtime, package or SDK
  versions, platform accounts, and feature flags).
- A quick-start path for the smallest successful implementation.
- A conceptual end-to-end workflow and decision table.
- A canonical API contract showing the important components and their data shapes.
- Topic-specific workflows, code patterns, and automation boundaries.
- OSS versus managed/cloud, or major-version, behavior where relevant.
- Authentication, permissions, cost, privacy/PII, nondeterminism, and version gates.
- A troubleshooting section for common failures.
- Official source links for every rapidly changing or preview API.

When the documentation describes an iterative workflow (training or tuning loops,
feedback loops, build–test–deploy cycles, data pipelines, review cycles), distill
the loop explicitly: its stages, the inputs and outputs at each stage, and which
steps can be automated. This applies to every domain; treat it as a general rule,
not a domain-specific requirement.

### 4. Validate and test the skill

Create `evals/evals.json` with 2–3 realistic prompts that should trigger the new skill.
Run the skill creator's quick validation if available. Check:

- Frontmatter and name/folder consistency.
- All referenced files exist.
- Code blocks have imports and internally consistent API names.
- URLs are official and source-ledger entries identify what each page contributed.
- Parent routing points to the new subskill.

Do not fabricate undocumented APIs. If an API could not be verified, mark it as
version-dependent and provide a verification command or documentation link.

### 5. Final response

Report:

1. Files created or updated.
2. Topics covered and any explicitly unresolved gaps.
3. Research subagents used and the resolved model ID.
4. Validation performed and its result.
5. The command to restart OpenCode so the new skill/command is loaded.

Do not overwrite unrelated skills or configuration. Never include secrets, tokens, or
private user data in the generated skill.
