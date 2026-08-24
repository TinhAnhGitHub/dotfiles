# Official PyMongo 4.17 source map

The stable API documentation currently serves PyMongo **4.17.0**. Use it as the canonical API
surface; the user-supplied versioned API root is retained below for fixed-version links.

## API package trees

- BSON index: https://pymongo.readthedocs.io/en/stable/api/bson/index.html
  - Child modules: `binary`, `codec_options`, `datetime_ms`, `decimal128`, `errors`, `int64`,
    `json_util`, `objectid`, `raw_bson`, `regex`, `son`, `timestamp`, and `tz_util`.
- PyMongo index: https://pymongo.readthedocs.io/en/stable/api/pymongo/index.html
  - Child modules: `mongo_client`, `database`, `collection`, `cursor`, `command_cursor`,
    `client_session`, `change_stream`, `errors`, `monitoring`, `operations`, `results`,
    `read_concern`, `read_preferences`, `write_concern`, `server_api`, `collation`, and
    `client_options`.
- Async API: https://pymongo.readthedocs.io/en/stable/api/pymongo/asynchronous/index.html
- Versioned 4.17 API root: https://pymongo.readthedocs.io/en/4.17.0/api/

## Driver-guide landing pages and recursive sections

- Connect: https://www.mongodb.com/docs/languages/python/pymongo-driver/current/connect/
  - `mongoclient/`, `connection-options/connection-pools/`, `connection-options/csot/`,
    `connection-options/network-compression/`, `connection-options/server-selection/`, and
    `connection-options/stable-api/`.
- Databases and collections: https://www.mongodb.com/docs/languages/python/pymongo-driver/current/databases-collections/
- CRUD: https://www.mongodb.com/docs/languages/python/pymongo-driver/current/crud/
  - `insert/`, `update/`, `replace/`, `delete/`, `bulk-write/`, `configure/`, and `query/` with
    `find/`, `cursors/`, `count/`, `distinct/`, `specify-query/`, and
    `specify-documents-to-return/`.
- Aggregation: https://www.mongodb.com/docs/languages/python/pymongo-driver/current/aggregation/
- Data formats: https://www.mongodb.com/docs/languages/python/pymongo-driver/current/data-formats/
  - `bson/`, `extended-json/`, `dates-and-times/`, `uuid/`, `time-series/`, and
    `custom-types/{serialization,type-codecs}/`.
- Indexes: https://www.mongodb.com/docs/languages/python/pymongo-driver/current/indexes/
- Commands: https://www.mongodb.com/docs/languages/python/pymongo-driver/current/run-command/
- Atlas Search: https://www.mongodb.com/docs/languages/python/pymongo-driver/current/atlas-search/
- Monitoring/logging: https://www.mongodb.com/docs/languages/python/pymongo-driver/current/monitoring-and-logging/
  - `monitoring/`, `logging/`, and `change-streams/`.

## Refreshing documentation

For current guide navigation, start at the official documentation manifest:
https://www.mongodb.com/docs/languages/python/pymongo-driver/current/llms.txt
