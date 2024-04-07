def chisqselector(df, label_column="label"):
    from pyspark.ml.feature import ChiSqSelector

    selector = ChiSqSelector(numTopFeatures=5, featuresCol="features", outputCol="selectedFeatures", labelCol=label_column)
    df = selector.fit(df).transform(df)
    return df


def selected_save_data(df):
    pandas_df = df.toPandas()
    pandas_df.to_csv("selected_data.csv", header=True, index=False)

