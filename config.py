import os


def _get_dbutils():
    if not os.environ.get("DATABRICKS_RUNTIME_VERSION"):
        return None  # not on Databricks, skip entirely

    # Notebooks: dbutils is injected into IPython namespace
    try:
        import IPython
        shell = IPython.get_ipython()
        if shell and "dbutils" in shell.user_ns:
            return shell.user_ns["dbutils"]
    except ImportError:
        pass

    # Jobs/scripts: create via DBUtils using importlib to avoid linter warnings
    try:
        import importlib
        from pyspark.sql import SparkSession
        spark = SparkSession.getActiveSession()
        if spark:
            DBUtils = importlib.import_module("pyspark.dbutils").DBUtils
            return DBUtils(spark)
    except Exception:
        pass

    return None


def get_db_config():
    dbutils = _get_dbutils()
    if dbutils:
        # Running on Databricks — use secret scope
        return {
            "server":   dbutils.secrets.get(scope="dw", key="DB_SERVER"),
            "user":     dbutils.secrets.get(scope="dw", key="DB_USER"),
            "password": dbutils.secrets.get(scope="dw", key="DB_PASSWORD"),
            "database": dbutils.secrets.get(scope="dw", key="DB_DATABASE"),
        }

    # Running locally — use .env
    from dotenv import load_dotenv
    load_dotenv()
    return {
        "server":   os.environ["DB_SERVER"],
        "user":     os.environ["DB_USER"],
        "password": os.environ["DB_PASSWORD"],
        "database": os.environ["DB_DATABASE"],
    }
