from pyspark.ml import Pipeline
from pyspark.sql.functions import col
from pyspark.ml.feature import VectorAssembler, StringIndexer, StandardScaler, ChiSqSelector
from pyspark.sql import SparkSession
from pyspark.ml.classification import LinearSVC, LinearSVCModel, RandomForestClassifier, RandomForestClassificationModel
from pyspark.ml.evaluation import MulticlassClassificationEvaluator, BinaryClassificationEvaluator


# from pyspark.ml.stat import Correlation
# import matplotlib.pyplot as plt
# import seaborn as sns


def create_spark_session(app_name="AnomalyDetection"):
    return SparkSession.builder \
        .appName(app_name) \
        .config("spark.ui.port", 4042) \
        .config("spark.jars.packages", "") \
        .config("spark.sql.debug.maxToStringFields", 1000) \
        .getOrCreate()


def read_data(spark, train_path, test_path):
    train_data = spark.read.csv(train_path, header=True, inferSchema=True)
    test_data = spark.read.csv(test_path, header=True, inferSchema=True)
    return train_data, test_data


def display_information(df, target_col="No"):
    print("Dataframe Information:")
    if target_col != "No":
        df.groupBy(target_col).count().show()
    print("Number of rows:", df.count())
    print("Number of columns:", len(df.columns))
    df.show(10, truncate=False)
    df.describe().show()
    df.printSchema()


def check_column_types(df):
    print("Column Types:\n")
    string_columns = [col_name for (col_name, dtype) in df.dtypes if dtype == 'string']
    quantitative_cols = [col_name for col_name, data_type in df.dtypes if
                         data_type in ['int', 'bigint', 'double', 'float']]
    categorical_cols = list(set(df.columns) - set(quantitative_cols) - set(string_columns))
    print("string_columns: " + str(len(string_columns)))
    print("quantitative_cols: " + str(len(quantitative_cols)))
    print("categorical_cols: " + str(len(categorical_cols)))
    return string_columns, quantitative_cols, categorical_cols


def handle_null_values(df):
    print("Null Values:\n")
    null_columns = [col(column) for column in df.columns if df.filter(col(column).isNull()).count() > 0]
    if null_columns:
        print("Columns with null values:")
        for column in null_columns:
            print(column)
            df = df.fillna(0, subset=[column])
    else:
        print('\n-------------------------------')
        print("No columns contain null values.")
        print('-------------------------------\n')
    return df


def outliers_handling(df, quantitative_cols):
    for variable in quantitative_cols:
        quantiles = df.approxQuantile(variable, [0.25, 0.75], 0.05)
        Q1, Q3 = float(quantiles[0]), float(quantiles[1])
        IQR = Q3 - Q1
        df = df.filter((col(variable) >= (Q1 - 2 * IQR)) & (col(variable) <= (Q3 + 2 * IQR)))
    df.show(5, truncate=False)
    return df


def label_encoding(df, string_columns):
    print("Label Encoding:\n")
    indexer = [StringIndexer(inputCol=col, outputCol=col + "_index") for col in string_columns]
    pipeline = Pipeline(stages=indexer)
    pipeline_model = pipeline.fit(df)
    df = pipeline_model.transform(df).drop(*string_columns)

    for col_name in string_columns:
        indexed_col_name = col_name + "_index"
        df = df.withColumnRenamed(indexed_col_name, col_name)
    df.show(5, truncate=False)
    return df


def feature_scaling(df, feature_columns, exclude_columns=None):
    if exclude_columns is None:
        exclude_columns = []

    assembler = VectorAssembler(inputCols=[col for col in feature_columns if col not in exclude_columns],
                                outputCol="features")
    df = assembler.transform(df)

    scaler = StandardScaler(inputCol="features", outputCol="scaled_features", withStd=True, withMean=True)
    scaler_model = scaler.fit(df)
    df = scaler_model.transform(df).drop("features").withColumnRenamed("scaled_features", "features")
    df.show(5, truncate=False)
    return df


def chisqselector(train_data):
    # Use ChiSqSelector for feature selection
    selector = ChiSqSelector(numTopFeatures=5, featuresCol="features", outputCol="selectedFeatures", labelCol="class")
    train_data = selector.fit(train_data).transform(train_data)
    train_data.show(5, truncate=False)
    return train_data


def train_and_evaluate_model(train_df):
    # svc = LinearSVC(maxIter=100, regParam=0.0001, labelCol="class")
    svc = RandomForestClassifier(featuresCol="features", labelCol="class")
    model = svc.fit(train_df)
    predictions = model.transform(train_df)
    evaluate_model(predictions)

    predictions.show(5, truncate=False)
    train_df.groupBy("class").count().show()
    predictions.groupBy("prediction").count().show()

    # model_path = "./SVMModel"
    model_path = "./RandomForestModel"
    model.write().overwrite().save(model_path)


def test_model(df, model):
    df = model.transform(df)
    df = df.drop("rawPrediction", "features")
    df = df.withColumnRenamed("prediction", "Threat")
    df.groupBy("Threat").count().show()
    return df


def load_and_test_model(test_data):
    # model_path = "./SVMModel"
    model_path = "./RandomForestModel"
    model = RandomForestClassificationModel.load(model_path)
    test_data = model.transform(test_data)
    test_data = test_data.drop("rawPrediction", "features")
    test_data = test_data.withColumnRenamed("prediction", "Threat")
    test_data.groupBy("Threat").count().show()
    return test_data


def evaluate_model(predictions):
    evaluator = MulticlassClassificationEvaluator(predictionCol="prediction", labelCol="class", metricName="accuracy")
    accuracy = evaluator.evaluate(predictions)
    print(f"Test Accuracy = {accuracy}")

    evaluator = MulticlassClassificationEvaluator(predictionCol="prediction", labelCol="class", metricName="f1")
    f1 = evaluator.evaluate(predictions)
    print(f"f1 test = {f1}")

    evaluator = MulticlassClassificationEvaluator(predictionCol="prediction", labelCol="class",
                                                  metricName="falsePositiveRateByLabel")
    falsePositiveRateByLabel = evaluator.evaluate(predictions)
    print(f"false positive = {falsePositiveRateByLabel}")

    evaluator = MulticlassClassificationEvaluator(predictionCol="prediction", labelCol="class",
                                                  metricName="precisionByLabel")
    precisionByLabel = evaluator.evaluate(predictions)
    print(f"precisionByLabel = {precisionByLabel}")

    evaluator = MulticlassClassificationEvaluator(predictionCol="prediction", labelCol="class",
                                                  metricName="recallByLabel")
    recallByLabel = evaluator.evaluate(predictions)
    print(f"recallByLabel = {recallByLabel}")

    evaluator = BinaryClassificationEvaluator(rawPredictionCol="rawPrediction", labelCol="class",
                                              metricName="areaUnderROC")
    areaUnderROC = evaluator.evaluate(predictions)
    print(f"areaUnderROC = {areaUnderROC}")


def main():
    spark = create_spark_session()
    train_data, test_data = read_data(spark, 'Train_data.csv', 'Test_data.csv')

    # Train Data
    display_information(train_data, 'class')
    string_columns, quantitative_cols, categorical_cols = check_column_types(train_data)
    train_data = handle_null_values(train_data)
    train_data = label_encoding(train_data, string_columns)
    train_data = feature_scaling(train_data, train_data.columns, exclude_columns=["class"])
    train_data = chisqselector(train_data)
    train_and_evaluate_model(train_data)

    # Test Data
    display_information(test_data)
    string_columns, quantitative_cols, categorical_cols = check_column_types(test_data)

    # test_data = handle_null_values(test_data)
    test_data = label_encoding(test_data, string_columns)
    test_data = feature_scaling(test_data, test_data.columns)

    # test_data = test_model(test_data, model)
    test_data = load_and_test_model(test_data)
    test_data.show()

    # pd = test_data.toPandas()
    # pd.to_csv("predicted.csv")

    # pandas_df = test_data.toPandas()
    #
    # services = pandas_df['service'].unique().tolist()
    # service_counts = pandas_df['service'].value_counts()
    # threats = pandas_df['Threat'].unique().tolist()
    # threat_counts = pandas_df['Threat'].value_counts()
    #
    # fig, ax1 = plt.subplots(figsize=(10, 5))
    # ax1.bar(services, service_counts)
    # ax1.set_title('Unique Services')
    # ax1.set_xticklabels(services, rotation=90)
    # ax1.set_ylabel('Count')
    #
    # # Create space for next subplot
    # fig.tight_layout()
    #
    # ax2 = ax1.twinx()
    # ax2.bar(threats, threat_counts, color='r', alpha=0.5)
    # ax2.set_ylabel('Threat Count', color='red')
    # ax2.tick_params(axis='y', colors='red')
    # ax2.set_yticks([])
    #
    # plt.show()
    #
    # sns.pairplot(pandas_df[['service', 'Threat']], hue='Threat')
    # plt.show()

    # maxiter=1000 = 0.9484757065735154
    # maxiter=1000 = 0.9484757065735154
    # maxiter=100  = 0.9484360114322007
    # maxiter=5    = 0.9427993013655128
    # maxiter=100 , regParam=0.0000001 = 0.9538345506510003
    # maxIter= 100, regParam=0.0001    = 0.9558986979993649
    # maxiter=100 , regParam=0.001     = 0.9543505874880914
    # maxiter=100 , regParam=0.01      = 0.9484360114322007
    # maxiter=100 , regParam=0.1       = 0.9459749126706891
    # maxiter=100 , regParam=1         = 0.8965941568751985


if __name__ == "__main__":
    main()
