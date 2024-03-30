def bucketizer(df):
    from pyspark.ml.feature import Bucketizer
    columns = [col_name for (col_name, dtype) in df.dtypes if dtype == 'string']
    splits = [-float("inf"), -0.5, 0.0, 0.5, float("inf")]

    for col_name in columns:
        bucketizer = Bucketizer(splits=splits, inputCol=col_name, outputCol=f"{col_name}_bucketized")
        df = bucketizer.transform(df).drop(col_name).withColumnRenamed(f"{col_name}_bucketized", col_name)
    return df


def l1Normalizer(df):
    from pyspark.ml.feature import Normalizer
    columns = [col_name for (col_name, dtype) in df.dtypes if dtype == 'string']

    for col_name in columns:
        normalizer = Normalizer(p=1.0, inputCol=col_name, outputCol=col_name + "normFeatures")
        df = normalizer.transform(df)

    return df


def minAbsScaler(df):
    from pyspark.ml.feature import MaxAbsScaler
    columns = [col_name for (col_name, dtype) in df.dtypes if dtype == 'string']
    for col_name in columns:
        scaler = MaxAbsScaler(inputCol=col_name, outputCol="scaled_features")

    scalerModel = scaler.fit(df)
    df = scalerModel.transform(df).drop("features").withColumnRenamed("scaled_features", "features")
    return df


def minMaxScaler(df):
    from pyspark.ml.feature import MinMaxScaler
    scaler = MinMaxScaler(inputCol="features", outputCol="scaled_features")
    scaler_model = scaler.fit(df)
    df = scaler_model.transform(df)
    df = scaler_model.transform(df).drop("features").withColumnRenamed("scaled_features", "features")
    # Print results (optional)
    # print("Features scaled to range:", scaler.getMin(), scaler.getMax())
    # df.select("features", "scaledFeatures").show()

    return df


def standerd_scaler(df):
    from pyspark.ml.feature import StandardScaler
    scaler = StandardScaler(inputCol="features", outputCol="scaled_features", withStd=True, withMean=True)
    scaler_model = scaler.fit(df)
    df = scaler_model.transform(df).drop("features").withColumnRenamed("scaled_features", "features")
    return df


def robustScaler(df):
    from pyspark.ml.feature import RobustScaler
    scaler = RobustScaler(inputCol="features", outputCol="scaled_features")
    scaler_model = scaler.fit(df)
    df = scaler_model.transform(df).drop("features").withColumnRenamed("scaled_features", "features")
    return df


def scaled_save_data(df):
    pandas_df = df.toPandas()
    pandas_df.to_csv("scaled_data.csv", header=True, index=False)



