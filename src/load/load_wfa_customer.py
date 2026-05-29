TARGET_TABLE = "silver.wfa_labs_test"


def load_labs(df, cfg):
    # Databricks — Spark JDBC write
    if _is_spark_df(df):
        _load_spark(df, cfg)
    else:
        _load_pandas(df, cfg)


def _is_spark_df(df):
    try:
        from pyspark.sql import DataFrame
        return isinstance(df, DataFrame)
    except ImportError:
        return False


def _load_spark(df, cfg):
    from databricks.connect import DatabricksSession
    from pyspark.sql import SparkSession

    spark = SparkSession.getActiveSession() or DatabricksSession.builder.getOrCreate()
    jdbc_url = (
        f"jdbc:sqlserver://{cfg['server']};"
        f"databaseName={cfg['database']};"
        "encrypt=true;trustServerCertificate=true"
    )
    jdbc_props = {
        "user": cfg["user"],
        "password": cfg["password"],
        "driver": "com.microsoft.sqlserver.jdbc.SQLServerDriver",
    }
    df.write.jdbc(url=jdbc_url, table=TARGET_TABLE, mode="overwrite", properties=jdbc_props)
    print(f"Loaded {df.count()} rows to {TARGET_TABLE}")


def _load_pandas(df, cfg):
    from sqlalchemy import create_engine
    import urllib.parse

    password = urllib.parse.quote(cfg["password"])
    engine = create_engine(
        f"mssql+pymssql://{cfg['user']}:{password}@{cfg['server']}/{cfg['database']}"
    )
    schema, table = TARGET_TABLE.split(".")
    df.to_sql(table, engine, schema=schema, if_exists="replace", index=False)
    print(f"Loaded {len(df)} rows to {TARGET_TABLE}")
