def _build_jdbc(spark, cfg):
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
    return spark, jdbc_url, jdbc_props


def get_connection(cfg):
    # 1. Running ON Databricks (notebook or job) — use active session
    try:
        from pyspark.sql import SparkSession
        spark = SparkSession.getActiveSession()
        if spark:
            return _build_jdbc(spark, cfg)
    except ImportError:
        pass

    # 2. Running LOCALLY with Databricks Connect — computation on Databricks cluster
    try:
        from databricks.connect import DatabricksSession
        spark = DatabricksSession.builder.getOrCreate()
        return _build_jdbc(spark, cfg)
    except ImportError:
        pass

    # 3. Pure local fallback — pyodbc (no Spark)
    import pyodbc
    conn_str = (
        f"DRIVER={{ODBC Driver 17 for SQL Server}};"
        f"SERVER={cfg['server']};"
        f"DATABASE={cfg['database']};"
        f"UID={cfg['user']};"
        f"PWD={cfg['password']}"
    )
    return pyodbc.connect(conn_str)
