from Evaluate import regression_evaluator, classification_evoluator


# ------------------------------------Linear Regression Function-------------------------------------------#
def linear_regression(df, label_column):
    from pyspark.ml.regression import LinearRegression
    from pyspark.ml import Pipeline

    # Split the data into training and testing sets
    (trainingData, testData) = df.randomSplit([0.8, 0.2], seed=42)

    # Initialize Linear Regression model
    lr = LinearRegression(featuresCol="features", labelCol=label_column, regParam=0.01)

    # Create a pipeline with stages: Vector Assembler and Linear Regression
    pipeline = Pipeline(stages=[lr])

    # Train the model
    model = pipeline.fit(trainingData)

    # # Make predictions on the test data
    # sampledf = model.transform(trainingData)

    predictions = model.transform(df)

    return predictions


# ------------------------------------Linear Regression Function-------------------------------------------#
def logistic_regression(df, label_column):
    from pyspark.ml import Pipeline
    from pyspark.ml.classification import LogisticRegression

    # Split the data into training and testing sets
    (trainingData, testData) = df.randomSplit([0.8, 0.2], seed=42)

    lr = LogisticRegression(featuresCol='features', labelCol='Threat')

    # Creating the pipeline
    pipeline = Pipeline(stages=[lr])

    # Train the model
    model = pipeline.fit(trainingData)

    # # Make predictions on the test data
    # sampledf = model.transform(trainingData)

    predictions = model.transform(df)

    return predictions


def random_forest(df, label_column):
    from pyspark.ml.classification import RandomForestClassifier

    # ------------------------------Random Forest Model------------------------------------------------- #
    # Split data into training and testing sets
    train_data, test_data = df.randomSplit([0.8, 0.2], seed=42)
    # Random Forest Classifier
    rf = RandomForestClassifier(labelCol=label_column, featuresCol="features")
    model = rf.fit(train_data)

    # Make predictions
    predictions = model.transform(test_data)

    predictions.show(5, truncate=False)
    df.groupBy("class").count().show()
    predictions.groupBy("prediction").count().show()

    classification_evoluator(predictions)

    model_path = "./RandomForest"
    model.write().overwrite().save(model_path)


def load_random_forest(df):
    from pyspark.ml.classification import RandomForestClassificationModel

    model_path = "./SVMModel"
    model = RandomForestClassificationModel.load(model_path)

    df = model.transform(df)

    df = df.drop("rawPrediction", "features")
    df = df.withColumnRenamed("prediction", "Threat")
    df.groupBy("Threat").count().show()

    return df


def train_linear_svm(df):
    from pyspark.ml.classification import LinearSVC

    svc = LinearSVC(maxIter=100, regParam=0.0001, labelCol="class")
    model = svc.fit(df)

    predictions = model.transform(df)

    predictions.show(5, truncate=False)
    df.groupBy("class").count().show()
    predictions.groupBy("prediction").count().show()

    classification_evoluator(predictions)

    model_path = "./SVMModel"
    model.write().overwrite().save(model_path)


def load_linear_svm(df):
    from pyspark.ml.classification import LinearSVCModel

    model_path = "./SVMModel"
    model = LinearSVCModel.load(model_path)

    df = model.transform(df)

    df = df.drop("rawPrediction", "features")
    df = df.withColumnRenamed("prediction", "Threat")
    df.groupBy("Threat").count().show()

    return df
