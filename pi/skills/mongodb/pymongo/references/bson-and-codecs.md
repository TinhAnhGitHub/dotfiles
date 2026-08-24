# BSON, Extended JSON, and codecs

## BSON essentials

- Prefer module functions `bson.encode`, `decode`, `decode_all`, and `decode_iter`; the `BSON`
  class adds avoidable overhead.
- `ObjectId` accepts an ObjectId, 12-byte value, or valid hex string. Validate untrusted IDs and
  convert them at the boundary rather than querying with a string.
- Use `bson.json_util.dumps/loads` for Extended JSON. Relaxed EJSON is human-friendly; Canonical
  EJSON preserves types for reliable interchange.
- `RawBSONDocument` preserves raw BSON for passthrough/lazy decoding and is read-only. Use it only
  when profiling justifies the complexity.

## Dates, UUIDs, and decimals

- MongoDB stores UTC. Naive Python datetimes are treated as UTC; aware datetimes are converted to
  UTC. Prefer `datetime.now(datetime.timezone.utc)` and configure `CodecOptions(tz_aware=True)`
  when reads must be aware. `datetime.date` cannot be encoded directly.
- BSON supports a wider date range than Python. `DatetimeMS` and `DatetimeConversion.DATETIME_AUTO`
  safely represent mixed in-range/out-of-range BSON dates; default conversion can raise.
- `UuidRepresentation.UNSPECIFIED` is the default and rejects native `uuid.UUID` writes. Use
  `UuidRepresentation.STANDARD` for new data; use legacy representations only to interoperate with
  an established subtype-3 encoding.
- Use `Decimal128` or registered `DecimalEncoder`/`DecimalDecoder` for exact decimal persistence.

## CodecOptions and custom types

- `CodecOptions` configures `document_class`, timezone behavior, UUID representation, datetime
  conversion, and a `TypeRegistry` at client/database/collection scope.
- Use `TypeEncoder`, `TypeDecoder`, or `TypeCodec` for custom types. A registry is immutable, does
  not support customizing built-in types, and encoders do not chain—the transformed value must be
  BSON-encodable.
- A fallback encoder is a last resort after built-in and registered encoders. Custom decoders do
  not apply to `Database.command()` results or GridFS.

```python
from bson.codec_options import CodecOptions, UuidRepresentation

codec_options = CodecOptions(
    tz_aware=True,
    uuid_representation=UuidRepresentation.STANDARD,
)
events = db.get_collection("events", codec_options=codec_options)
```

## Sources

- https://www.mongodb.com/docs/languages/python/pymongo-driver/current/data-formats/
- https://www.mongodb.com/docs/languages/python/pymongo-driver/current/data-formats/bson/
- https://www.mongodb.com/docs/languages/python/pymongo-driver/current/data-formats/extended-json/
- https://www.mongodb.com/docs/languages/python/pymongo-driver/current/data-formats/dates-and-times/
- https://www.mongodb.com/docs/languages/python/pymongo-driver/current/data-formats/uuid/
- https://www.mongodb.com/docs/languages/python/pymongo-driver/current/data-formats/custom-types/type-codecs/
- https://pymongo.readthedocs.io/en/stable/api/bson/index.html
