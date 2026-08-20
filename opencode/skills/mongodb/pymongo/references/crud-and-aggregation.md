# Databases, collections, CRUD, and aggregation

## Database and collection handles

- Access with `client["db"]`/`db["collection"]`; an insert implicitly creates a collection.
- Use `create_collection()` when options matter (capped, collation, time series). Use
  `with_options()` to apply deliberate read/write concern, read preference, or codec choices.
- Treat `drop()` and `drop_database()` as destructive. State the target and impact before use.
- Use `TypedDict` plus `Collection[DocumentType]` for application type checking.

## CRUD and result handling

- Writes: `insert_one`, `insert_many`, `update_one/many`, `replace_one`, `delete_one/many`.
  Use `upsert=True` only when creation-on-miss is intended. A replacement removes every field but
  immutable `_id`.
- Inspect acknowledged results (`inserted_id`, `matched_count`, `modified_count`, `deleted_count`,
  `upserted_id`). For unacknowledged writes, accessing many result attributes raises
  `InvalidOperation`.
- Use `collection.bulk_write([InsertOne(...), UpdateOne(...)], ordered=...)`; unordered batches
  attempt remaining operations after an error. Client-level multi-namespace `bulk_write` requires
  PyMongo 4.9+ and MongoDB Server 8.0+.
- Read with `find_one()` (document or `None`) or `find()` (cursor). Convert URL IDs to `ObjectId`
  before querying. Use filter, projection, sort, limit, `hint`, `max_time_ms`, and `comment`
  intentionally.
- Iterate a cursor instead of materializing it. Use `with collection.find(...) as cursor:` when a
  cursor could outlive a short scope. `count_documents()` is accurate; metadata-based
  `estimated_document_count()` is approximate.

```python
from bson import ObjectId

doc = collection.find_one(
    {"_id": ObjectId(item_id), "status": "active"},
    {"title": 1, "updated_at": 1},
    comment="api:get-item",
)
```

## Aggregation and transactions

- Pass a list of stage documents to `aggregate()`. Place selective `$match` early and only use
  `allowDiskUse=True` after considering server capacity. Result documents remain limited to 16 MB;
  standard pipeline stages have a 100 MB memory limit, and `$graphLookup` ignores `allowDiskUse`.
- Explain an aggregation with `pymongoexplain` or a controlled `explain` command; remove `$out`
  for execution-statistics explain.
- Use explicit sessions/`with_transaction()` for multi-document atomicity. The callback can run
  more than once, so keep external side effects idempotent or outside it.

## Sources

- https://www.mongodb.com/docs/languages/python/pymongo-driver/current/databases-collections/
- https://www.mongodb.com/docs/languages/python/pymongo-driver/current/crud/
- https://www.mongodb.com/docs/languages/python/pymongo-driver/current/crud/query/
- https://www.mongodb.com/docs/languages/python/pymongo-driver/current/aggregation/
- https://pymongo.readthedocs.io/en/stable/api/pymongo/collection.html
- https://pymongo.readthedocs.io/en/stable/api/pymongo/client_session.html
