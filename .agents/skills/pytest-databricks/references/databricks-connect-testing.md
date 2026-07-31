# Databricks Connect Testing Reference

> Source: https://docs.databricks.com/aws/en/dev-tools/databricks-connect/python/testing
> and related Databricks Connect documentation

## Table of Contents

- [Overview](#overview)
- [Installation](#installation)
- [Profile Configuration](#profile-configuration)
- [Getting a SparkSession](#getting-a-sparksession)
- [Serverless Compute](#serverless-compute)
- [Testing with Databricks Connect](#testing-with-databricks-connect)
- [Running pytest from Terminal](#running-pytest-from-terminal)
- [Troubleshooting](#troubleshooting)
- [PySpark vs Databricks Connect](#pyspark-vs-databricks-connect)

---

## Overview

Databricks Connect lets you run Spark code from your local machine that executes on a
remote Databricks cluster or serverless compute. This bridges the gap between:
- **Unit tests** (no Spark, mocked everything) — fast but low fidelity
- **End-to-end tests** (real workspace resources) — slow but high fidelity

Databricks Connect gives you **real Spark execution** without needing a local Spark install.

---

## Installation

```bash
pip install databricks-connect
```

**Critical**: Databricks Connect and PySpark are mutually exclusive. They both include
`pyspark` as a dependency but with different patches. Use separate virtual environments:

```bash
# For Databricks Connect testing
conda create -n dbconnect python=3.12
conda activate dbconnect
pip install databricks-connect pytest

# For local PySpark testing (if needed)
conda create -n pyspark python=3.12
conda activate pyspark
pip install pyspark pytest
```

---

## Profile Configuration

The user's Databricks profile is `TA`. Configure authentication:

### Option 1: CLI Configuration

```bash
# Configure the TA profile
databricks configure --profile TA

# Generate a token for the TA profile
databricks auth token --profile TA
```

### Option 2: Environment Variables

```bash
export DATABRICKS_HOST=<your-workspace-url>
export DATABRICKS_TOKEN=<your-token>
export DATABRICKS_CLUSTER_ID=<cluster-id>  # or use serverless
```

### Option 3: `.databrickscfg` File

```ini
[TA]
host = https://your-workspace.databricks.net
token = dapi...
cluster_id = 0708-200540-...
```

---

## Getting a SparkSession

### Default (uses DEFAULT profile or env vars)

```python
from databricks.connect import DatabricksSession
from pyspark.sql import SparkSession

def get_spark() -> SparkSession:
    return DatabricksSession.builder.getOrCreate()
```

### Using a Specific Profile

```python
from databricks.connect import DatabricksSession

spark = DatabricksSession.builder.profile("TA").getOrCreate()
```

### Via Environment Variable

```bash
export DATABRICKS_CONFIG_PROFILE=TA
```

```python
from databricks.connect import DatabricksSession
spark = DatabricksSession.builder.getOrCreate()  # picks up TA from env
```

---

## Serverless Compute

Serverless compute is the recommended test target — no cluster to start/stop, faster startup:

```bash
export DATABRICKS_SERVERLESS_COMPUTE_ID=auto
```

When set to `auto`, Databricks Connect ignores `cluster_id` and uses serverless compute.

If set to a specific serverless cluster ID, that cluster is used (not recommended —
serverless clusters are ephemeral by design).

---

## Testing with Databricks Connect

### Example Application Code

```python
# nyctaxi_functions.py
from databricks.connect import DatabricksSession
from pyspark.sql import DataFrame, SparkSession

def get_spark() -> SparkSession:
    spark = DatabricksSession.builder.getOrCreate()
    return spark

def get_nyctaxi_trips() -> DataFrame:
    spark = get_spark()
    df = spark.read.table("samples.nyctaxi.trips")
    return df
```

### Example Test

```python
# test_nyctaxi_functions.py
import pyspark.sql.connect.session
from nyctaxi_functions import get_spark, get_nyctaxi_trips

def test_get_spark():
    spark = get_spark()
    assert isinstance(spark, pyspark.sql.connect.session.SparkSession)

def test_get_nyctaxi_trips():
    df = get_nyctaxi_trips()
    assert df.count() > 0
```

### Running Tests

```bash
$ pytest
=================== test session starts ====================
platform darwin -- Python 3.11.7, pytest-8.1.1, pluggy-1.4.0
rootdir: project-root
collected 2 items

test_nyctaxi_functions.py ..                               [100%]
======================== 2 passed ==========================
```

---

## Running pytest from Terminal

**Important**: When running Databricks Connect from the terminal, pytest only works with
the DEFAULT configuration profile by default.

To use a non-default profile (like `TA`), either:

1. **Set the environment variable**:
```bash
export DATABRICKS_CONFIG_PROFILE=TA
pytest
```

2. **Use the `.profile()` builder** in your code:
```python
spark = DatabricksSession.builder.profile("TA").getOrCreate()
```

3. **Set `DATABRICKS_HOST` and `DATABRICKS_TOKEN` directly**:
```bash
export DATABRICKS_HOST=https://your-workspace.databricks.net
export DATABRICKS_TOKEN=your-token
pytest
```

---

## Troubleshooting

### "Conflicting PySpark installations"

Databricks Connect and PySpark cannot coexist. If you see this error:

```
This error occurs because Databricks Connect and PySpark both install pyspark,
but with different patches.
```

**Fix**: Use separate virtual environments (see Installation section).

### "SparkSession not available"

If `DatabricksSession.builder.getOrCreate()` fails:
- Check that `DATABRICKS_HOST` is set correctly
- Verify your token: `databricks auth token --profile TA`
- Ensure `databricks-connect` is installed in the active environment

### "ModuleNotFoundError: No module named 'databricks.connect'"

Install the package:
```bash
pip install databricks-connect
```

### Tests hang or timeout

- If using a cluster, ensure it's running
- If using serverless, set `DATABRICKS_SERVERLESS_COMPUTE_ID=auto`
- Use `pytest-timeout` to prevent indefinite hangs:
```bash
pytest --timeout=300
```

---

## PySpark vs Databricks Connect

| Aspect | Local PySpark | Databricks Connect |
|--------|--------------|-------------------|
| Installation | `pip install pyspark` | `pip install databricks-connect` |
| Execution | Local JVM | Remote Databricks cluster/serverless |
| Data access | Local files only | Unity Catalog, volumes, all Databricks data |
| Speed | Fast startup | Network latency, cluster startup |
| Cost | Free | Databricks compute costs |
| Best for | Unit testing transformations | Integration testing with real data |
| Mutual exclusivity | Cannot coexist with Databricks Connect | Cannot coexist with PySpark |

### When to Use Which

- **Local PySpark**: For unit testing pure transformation logic (takes DataFrame, returns
  DataFrame). Fast, no network, no cost.
- **Databricks Connect**: For integration testing code that reads from Unity Catalog,
  writes to Delta tables, or uses Databricks-specific features. Real data, real execution.