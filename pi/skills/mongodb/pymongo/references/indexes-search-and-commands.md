# Indexes, Atlas Search, and database commands

## Standard indexes and explain

- Use `create_index`/`create_indexes`, inspect with `list_indexes`, and remove only named,
  confirmed non-`_id_` indexes. Indexes cost write throughput and storage; design them around an
  observed filter/sort/projection workload.
- Capture the representative filter, sort, collation, limit, and projection. Compare unhinted
  `queryPlanner` then controlled `executionStats` results before/after a change. Look for
  `COLLSCAN`, `IXSCAN`, scan-to-return ratio, sort work, bounds, and rejected plans.
- Explain ignores the normal plan cache and output shape differs by server execution engine; parse
  it defensively. Use a `comment` to correlate diagnostics. Delegate optimization decisions to
  `mongodb/query-optimizer`.

## Atlas Search and Vector Search

- Regular indexes and Search/Vector Search indexes are different APIs. Use
  `create_search_index`, `list_search_indexes`, `update_search_index`, and
  `drop_search_index` for the latter, and poll until an asynchronous index change is ready.
- Give `$search` an explicit index name. In `compound`, put non-scoring `equals`, `range`, or `in`
  constraints in `filter`; use `must`, `should`, and `mustNot` according to relevance semantics.
  Project `$meta: "searchScore"` while evaluating relevance and limit result transfer.
- A vector index needs a matching embedding field, `numDimensions`, and similarity metric. Keep
  `knnBeta` out of new work (deprecated). Delegate broader Search design to
  `mongodb/search-and-ai`.

## Database commands

- Prefer driver methods, then use `Database.command()` only for an unavailable public API.
  `cursor_command()` is for command results returned as cursors.
- Treat arbitrary commands as privileged: classify as diagnostic, mutable, or destructive; use
  least-privileged credentials, bounded timeouts, and explicit approval before writes, DDL,
  administration, topology, or plan-cache changes.
- `Database.command()` does not automatically inherit database read preference outside a
  transaction; pass `read_preference=` explicitly when a secondary read is intentional.

```python
plan = db.command({
    "explain": {"find": collection.name, "filter": query_filter},
    "verbosity": "executionStats",
    "comment": "agent:index-review",
})
```

## Sources

- https://www.mongodb.com/docs/languages/python/pymongo-driver/current/indexes/
- https://www.mongodb.com/docs/languages/python/pymongo-driver/current/run-command/
- https://www.mongodb.com/docs/languages/python/pymongo-driver/current/atlas-search/
- https://www.mongodb.com/docs/manual/reference/command/explain/
- https://www.mongodb.com/docs/atlas/atlas-search/compound/
- https://pymongo.readthedocs.io/en/stable/api/pymongo/database.html
