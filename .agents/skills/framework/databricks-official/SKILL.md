---
name: databricks-official
description: Official Databricks Agent Skills collection. Use for any Databricks task, then load the matching databricks-* product skill from stable/ or an explicitly requested experimental skill.
license: Databricks License
---

# Databricks Official

This collection vendors the official skills from
`databricks/databricks-agent-skills` separately from the existing custom
`databricks` skill.

For Databricks work:

1. Load `databricks-official-core` first.
2. Load the narrowest matching `databricks-official-*` skill from `stable/`.
3. Use skills under `experimental/` only when explicitly requested or when no
   stable skill covers the task. Experimental skills are not officially
   supported.

Skill names are prefixed with `databricks-official-` to avoid collisions with
the existing custom Databricks collection. Supporting assets remain unchanged.
