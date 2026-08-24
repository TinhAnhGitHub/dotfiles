# PyMongo connection and lifecycle

## Choose and construct the client

- Sync: `from pymongo import MongoClient`; async: `from pymongo import AsyncMongoClient`.
- Use a URI or keyword arguments. Keywords validate unknown option names early; never hard-code
  credentials—use an environment variable/secret manager.
- `mongodb+srv://` enables TLS. `mongodb://` needs `tls=True` when TLS is required.
- Create one application-scoped client and reuse it. Close it during controlled shutdown; a
  context manager is appropriate for scripts. `close()` in `__del__` can deadlock.

```python
from pymongo import MongoClient

client = MongoClient(uri, appname="my-service")
client.admin.command("ping")
db = client.get_database("app")
# close client only when the process/application shuts down
```

## TLS and authentication

- Certificate and hostname validation are enabled by default. For a private CA, set `tlsCAFile`.
- Client certificate and private key must be in the same PEM referenced by
  `tlsCertificateKeyFile`. OCSP and CRL cannot be used together.
- Do not disable certificate or hostname verification in production. Document the narrowly scoped
  local-test exception if an invalid-certificate flag is unavoidable.
- Authentication defaults to the URI's database or `admin`; set `authSource` deliberately for
  SCRAM/X.509/AWS IAM/OIDC/LDAP/Kerberos deployments.

## Pools, processes, and deadlines

- Important options: `maxPoolSize` (100 default), `minPoolSize` (0), `maxConnecting` (2),
  `maxIdleTimeMS`, `connectTimeoutMS`, `socketTimeoutMS`, and `waitQueueTimeoutMS`.
- Derive values from peak concurrent operations, latency, topology, app-instance count, and server
  connection capacity; defer sizing policy to `mongodb/connection`.
- Create a new client after `fork()`/in each multiprocessing child. Do not inherit a parent's
  client, even though PyMongo resets some locks after fork.
- `with pymongo.timeout(seconds):` establishes one client-side deadline over selection, checkout,
  encoding, and execution. Nested scopes can shorten—not extend—the outer deadline; it overrides
  `timeoutMS` inside its scope. Check `PyMongoError.timeout` to classify expiry.

```python
import pymongo

with pymongo.timeout(5):
    doc = db.orders.find_one({"_id": order_id}, comment="api:get-order")
```

## Async difference

- `AsyncMongoClient` does not accept `connect`; it is event-loop confined and not thread-safe.
- Await network methods and `client.close()`. In an ASGI app, create and close it in application
  lifespan hooks, not per request.

## Sources

- https://www.mongodb.com/docs/languages/python/pymongo-driver/current/connect/
- https://www.mongodb.com/docs/languages/python/pymongo-driver/current/connect/mongoclient/
- https://www.mongodb.com/docs/languages/python/pymongo-driver/current/connect/connection-options/
- https://www.mongodb.com/docs/languages/python/pymongo-driver/current/connect/connection-options/connection-pools/
- https://www.mongodb.com/docs/languages/python/pymongo-driver/current/connect/connection-options/csot/
- https://www.mongodb.com/docs/languages/python/pymongo-driver/current/security/tls/
- https://www.mongodb.com/docs/languages/python/pymongo-driver/current/security/authentication/
