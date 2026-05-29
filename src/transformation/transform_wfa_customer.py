def transform_labs(df):
    try:
        # Spark DataFrame
        from pyspark.sql import functions as F
        return df.withColumn("name", F.initcap(F.col("name")))
    except ImportError:
        # pandas DataFrame
        df = df.copy()
        df["name"] = df["name"].str.title()
        return df
