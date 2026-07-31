# PySpark Testing Reference

> Sources: Databricks community blog, Apache Spark docs, chispa docs

## Table of Contents

- [Why PySpark Testing is Different](#why-pyspark-testing-is-different)
- [Strategies for Testable PySpark Code](#strategies-for-testable-pyspark-code)
- [Local SparkSession Fixture](#local-sparksession-fixture)
- [DataFrame Equality Testing](#dataframe-equality-testing)
- [Chispa Library](#chispa-library)
- [Mocking Spark and dbutils](#mocking-spark-and-dbutils)
- [Refactoring Notebooks for Testability](#refactoring-notebooks-for-testability)
- [Running pytest Inside Databricks Notebooks](#running-pytest-inside-databricks-notebooks)
- [Best Practices Summary](#best-practices-summary)

---

## Why PySpark Testing is Different

Databricks/PySpark testing has unique challenges:

1. **Runtime-Specific Libraries**: Code relies on `dbutils`, which is unavailable outside
   the Databricks environment.
2. **Global SparkSession**: The `SparkSession` provided by Databricks is automatically
   initialized and may not be accessible outside its runtime.
3. **Notebook-Based Workflows**: Many workflows are written in notebooks, complicating
   modular testing.
4. **Distributed Nature**: Spark's distributed execution makes debugging and testing harder.

---

## Strategies for Testable PySpark Code

### 1. Extract Transformation Logic

Move data processing into standalone Python functions:

```python
# databricks_notebook.py
from pyspark.sql import functions as F
from pyspark.sql import DataFrame

def process_data(df: DataFrame) -> DataFrame:
    """Pure transformation — no I/O, no dbutils."""
    return df.select("name", "birthDate").filter(F.col("dob") >= F.lit("2000-01-01"))

if __name__ == "__main__":
    # Main notebook logic — only runs in notebook context
    uc_volume_path = "volume://my_catalog.my_schema.my_volume/my_data"
    dbutils.fs.mkdirs(uc_volume_path)
    df = spark.read.table("my_table")
    result = process_data(df)
    result.write.mode("overwrite").saveAsTable("processed_table")
```

### 2. Minimize Direct dbutils Dependencies

Use dependency injection:

```python
# Bad — hard to test
def get_config():
    return dbutils.widgets.get("config_path")

# Good — testable
def get_config(dbutils=None):
    if dbutils is None:
        from databricks.sdk.runtime import dbutils as real_dbutils
        dbutils = real_dbutils
    return dbutils.widgets.get("config_path")
```

### 3. Control Notebook Execution

Wrap main execution in `if __name__ == "__main__"`:

```python
def main(spark, dbutils):
    """Entry point — accepts dependencies for testing."""
    config = get_config(dbutils)
    df = spark.read.table("source")
    result = process_data(df)
    result.write.mode("overwrite").saveAsTable("target")

if __name__ == "__main__":
    main(spark, dbutils)
```

---

## Local SparkSession Fixture

For unit testing PySpark transformations locally (no Databricks Connect needed):

```python
import pytest
from pyspark.sql import SparkSession

@pytest.fixture(scope="session")
def spark_session():
    """Session-scoped local Spark for testing."""
    spark = SparkSession.builder \
        .master("local[*]") \
        .appName("PyTest") \
        .getOrCreate()
    yield spark
    spark.stop()
```

Usage:

```python
def test_process_data(spark_session):
    from pyspark.sql.types import StructType, StructField, StringType
    from databricks_notebook import process_data

    data = [("Alpha", "2000-01-01"), ("Beta", "1980-05-12")]
    schema = StructType([
        StructField("name", StringType(), True),
        StructField("birthDate", StringType(), True)
    ])
    df = spark_session.createDataFrame(data, schema)
    result_df = process_data(df)

    assert result_df.count() == 1
```

---

## DataFrame Equality Testing

### `assertDataFrameEqual` (Spark 3.5+ / DBR 14.2+)

Built-in methods from `pyspark.testing.utils`:

```python
from pyspark.testing.utils import assertDataFrameEqual, assertSchemaEqual

def test_dataframe_equality(spark_session):
    df1 = spark_session.createDataFrame([("Alpha", 20)], ["name", "age"])
    df2 = spark_session.createDataFrame([("Alpha", 20)], ["name", "age"])

    assertSchemaEqual(df1.schema, df2.schema)  # Check schema
    assertDataFrameEqual(df1, df2)  # Check schema + data
```

### Manual DataFrame Comparison

For older Spark versions or more control:

```python
def assert_df_equal(actual, expected, check_order=False):
    """Compare two DataFrames for equality."""
    if not check_order:
        actual = actual.orderBy(actual.columns)
        expected = expected.orderBy(expected.columns)

    assert actual.schema == expected.schema, \
        f"Schema mismatch:\n{actual.schema}\nvs\n{expected.schema}"
    assert actual.collect() == expected.collect(), "Data mismatch"
```

---

## Chispa Library

[Chispa](https://github.com/chispa-dev/chispa) provides richer DataFrame comparison with
better error messages.

### Installation

```bash
pip install chispa
```

### DataFrame Equality

```python
from chispa.dataframe_compression import assert_df_equality

def test_with_chispa(spark):
    df1 = spark.createDataFrame([("Alice", 30)], ["name", "age"])
    df2 = spark.createDataFrame([("Alice", 30)], ["name", "age"])

    assert_df_equality(df1, df2)  # Checks schema and data
    
    # Ignore row order (useful for unordered transformations)
    assert_df_equality(df1, df2, ignore_row_order=True)
```

### Column Equality

```python
from chispa.dataframe_compression import assert_column_equality

def test_column_equality(spark):
    df1 = spark.createDataFrame([("a",), ("b",)], ["col1"])
    df2 = spark.createDataFrame([("a",), ("b",)], ["col1"])
    
    assert_column_equality(df1, "col1", df2, "col1")
```

### Chispa vs assertDataFrameEqual

| Feature | assertDataFrameEqual | Chispa |
|---------|---------------------|--------|
| Built-in | Yes (Spark 3.5+) | No (third-party) |
| Error messages | Basic | Detailed, row-by-row |
| Ignore row order | No | Yes (`ignore_row_order=True`) |
| Column comparison | No | Yes |
| Approximate equality | No | Yes |
| Schema-only check | Yes (`assertSchemaEqual`) | Yes |

---

## Mocking Spark and dbutils

### Mocking dbutils

```python
from unittest.mock import MagicMock

def test_dbutils_interaction():
    mock_dbutils = MagicMock()
    mock_dbutils.fs.mkdirs.return_value = None

    uc_volume_path = "volume://my_catalog.my_schema.my_volume/my_data"
    mock_dbutils.fs.mkdirs(uc_volume_path)

    mock_dbutils.fs.mkdirs.assert_called_once_with(uc_volume_path)
```

### Reusable dbutils Fixture

```python
@pytest.fixture
def mock_dbutils():
    """Provide a mock dbutils for tests."""
    dbutils = MagicMock()
    dbutils.fs.mkdirs.return_value = None
    dbutils.fs.cp.return_value = None
    dbutils.fs.rm.return_value = True
    dbutils.widgets.get.return_value = "default_value"
    return dbutils
```

### Mocking SparkSession

For unit tests where you don't want real Spark execution:

```python
from unittest.mock import MagicMock

def test_with_mock_spark():
    mock_spark = MagicMock()
    mock_df = MagicMock()
    mock_spark.read.table.return_value = mock_df
    mock_df.filter.return_value = mock_df
    mock_df.count.return_value = 42

    result = process_data(mock_spark.read.table("my_table"))
    
    assert result.count() == 42
```

### Stubbing pyspark.pipelines (DLT)

For testing DLT pipeline code outside Databricks:

```python
# conftest.py
import sys
from unittest.mock import MagicMock

def _create_dummy_decorator(*args, **kwargs):
    def decorator(func):
        return func
    return decorator

class MockDP:
    table = staticmethod(_create_dummy_decorator)
    expect = staticmethod(_create_dummy_decorator)
    expect_or_drop = staticmethod(_create_dummy_decorator)
    expect_or_fail = staticmethod(_create_dummy_decorator)
    expect_all = staticmethod(_create_dummy_decorator)
    view = staticmethod(_create_dummy_decorator)

    @staticmethod
    def read(table_name, **kwargs):
        return MagicMock()

    @staticmethod
    def read_stream(table_name, **kwargs):
        return MagicMock()

    @staticmethod
    def create_streaming_table(name, **kwargs):
        pass

    @staticmethod
    def create_streaming_view(name, **kwargs):
        pass

sys.modules["pyspark.pipelines"] = MockDP()
```

---

## Refactoring Notebooks for Testability

### Pattern: Extract → Test → Wrap

```python
# Step 1: Extract pure transformation
def filter_active_users(df):
    return df.filter(F.col("status") == "active")

def add_full_name(df):
    return df.withColumn("full_name", F.concat("first_name", F.lit(" "), "last_name"))

# Step 2: Test the transformation
def test_filter_active_users(spark_session):
    df = spark_session.createDataFrame(
        [("Alice", "active"), ("Bob", "inactive")],
        ["name", "status"]
    )
    result = filter_active_users(df)
    assert result.count() == 1

# Step 3: Wrap in notebook execution
if __name__ == "__main__":
    df = spark.read.table("users")
    result = add_full_name(filter_active_users(df))
    result.write.mode("overwrite").saveAsTable("active_users")
```

---

## Running pytest Inside Databricks Notebooks

```python
# Cell 1: Install pytest
%pip install pytest

# Cell 2: Run tests
import pytest

retcode = pytest.main([".", "-v", "-p", "no:cacheprovider"])
assert retcode == 0, "Some tests failed!"
```

Benefits:
- Tests run in the exact same environment as production code
- Access to `dbutils`, `spark`, and all Databricks utilities
- Can be integrated into Databricks jobs for CI/CD

---

## Best Practices Summary

1. **Isolate Business Logic**: Keep transformation logic separate from runtime-specific
   operations like I/O or utility calls.
2. **Use Synthetic Data**: Create small sample datasets within test cases instead of relying
   on production data.
3. **Optimise SparkSession Usage**: Share a single SparkSession across tests (session scope)
   to reduce initialization overhead.
4. **Integrate Testing into CI/CD**: Automate testing using GitHub Actions or Azure DevOps.
5. **Test Locally Before Deployment**: Validate code locally before running in Databricks.
6. **Use the Right Tier**: Unit tests for logic, integration tests for Spark, E2E for
   workspace resources.
7. **Mock External Dependencies**: Mock `dbutils`, SDK clients, and external services in
   unit tests.
8. **Use DataFrame Equality Helpers**: `assertDataFrameEqual` or chispa for clear failure
   messages.