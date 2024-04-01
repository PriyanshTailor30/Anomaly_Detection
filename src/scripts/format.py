def label_encoding(df):
    from pyspark.ml import Pipeline
    from pyspark.ml.feature import StringIndexer

    print("\n----------- Lebel Encoding -----------")
    string_columns = [col_name for (col_name, dtype) in df.dtypes if dtype == 'string']

    indexer = [StringIndexer(inputCol=col, outputCol=col + "_index") for col in string_columns]
    pipeline = Pipeline(stages=indexer)
    pipeline_model = pipeline.fit(df)
    df = pipeline_model.transform(df).drop(*string_columns)

    for col_name in string_columns:
        indexed_col_name = col_name + "_index"
        df = df.withColumnRenamed(indexed_col_name, col_name)
    print(f"Affected Columns: {string_columns}")
    return df


def hash_encoding(df):
    from pyspark.sql.functions import hash

    print("\n----------- Hash Encoding -----------")
    string_columns = [col_name for (col_name, dtype) in df.dtypes if dtype == 'string']

    for col_name in string_columns:
        if col_name != "class":
            df = df.withColumn(col_name, hash(col_name))
    return df


def hashing_tf(df):
    from pyspark.ml.feature import HashingTF, Tokenizer

    print("\n----------- HashingTF Encoding -----------")
    string_columns = [col_name for (col_name, dtype) in df.dtypes if dtype == 'string']

    for col_name in string_columns:
        tokenizer = Tokenizer(inputCol=col_name, outputCol=col_name + "_words")
        df = tokenizer.transform(df)
        hashingTF = HashingTF(inputCol=tokenizer.getOutputCol(), outputCol=col_name + "_features")
        df = hashingTF.transform(df)
        df = df.drop(col_name + "_words", col_name)
        df = df.withColumnRenamed(col_name + "_features", col_name)
    return df


def vector_assemble(df,lebel_column="none"):
    from pyspark.ml.feature import VectorAssembler

    print("\n\n----------- Vector Assemble -----------")
    if lebel_column != "none":
        assembler = VectorAssembler(inputCols=[col for col in df.columns], outputCol="features")
        df = assembler.transform(df)
    else:
        assembler = VectorAssembler(inputCols=[col for col in df.columns[:-1]], outputCol="features")
        df = assembler.transform(df)
    return df


def formated_save_data(df):
    print("\n\n----------- Saving Format Data -----------")
    pandas_df = df.toPandas()
    pandas_df.to_csv('formated_data.csv', header=True, index=False)

