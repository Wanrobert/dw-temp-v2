from config import get_db_config
from utils.db_connection import get_connection
from src.transformation.transform_wfa_customer import transform_labs
from src.load.load_wfa_customer import load_labs

QUERY = """
    SELECT
        id               AS lab_id,
        hiveentityid     AS hive_entity_id,
        name,
        lms_id,
        _fivetran_synced AS updated_at
    FROM bronze_dbo.labs
"""


def run():
    cfg = get_db_config()
    conn = get_connection(cfg)

    # Ingestion
    if isinstance(conn, tuple):
        spark, jdbc_url, props = conn
        df = spark.read.jdbc(url=jdbc_url, table=f"({QUERY}) AS labs", properties=props)
    else:
        import pandas as pd
        df = pd.read_sql(QUERY, conn)
        conn.close()

    # Transformation
    df = transform_labs(df)

    # Load
    load_labs(df, cfg)


if __name__ == "__main__":
    run()
