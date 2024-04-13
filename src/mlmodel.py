from src import Evaluate


# ------------------------------------Linear Regression Function-------------------------------------------#
def linear_regression(df, label_column="label"):
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
def logistic_regression(df, label_column="label"):
    from pyspark.ml import Pipeline
    from pyspark.ml.classification import LogisticRegression

    lr = LogisticRegression(featuresCol="features", labelCol=label_column)

    # Creating the pipeline
    pipeline = Pipeline(stages=[lr])

    # Train the model
    model = pipeline.fit(df)

    # model_path = "./LogisticRegression"
    # model.write().overwrite().save(model_path)
  
    # Drop the label column for predictions
    df_for_predictions = df.drop(label_column)

    # Generate predictions using the model
    predictions = model.transform(df_for_predictions)
       
    # Evaluate.classification_evoluator(predictions,label_column)

    return predictions


# ------------------------------Random Forest Model------------------------------------------------- #
def random_forest(df, label_column="label"):
    from pyspark.ml import Pipeline
    from pyspark.ml.classification import RandomForestClassifier

    # Random Forest Classifier
    rf = RandomForestClassifier(labelCol=label_column, featuresCol="features")
    
    # Creating the pipeline
    pipeline = Pipeline(stages=[rf])

    # Train the model
    model = pipeline.fit(df)

    # Make predictions
    predictions = model.transform(df)

    # Evaluate.classification_evoluator(predictions)

    model_path = "./RandomForest"
    model.write().overwrite().save(model_path)


def load_random_forest(df,label_column="label"):
    from pyspark.ml.classification import RandomForestClassificationModel

    model_path = "./SVMModel"
    model = RandomForestClassificationModel.load(model_path)

    df = model.transform(df)

    df = df.drop("rawPrediction", "features")
    df = df.withColumnRenamed("prediction", label_column)
    df.groupBy(label_column).count().show()

    return df


def train_linear_svm(df, label_column="label"):
    from pyspark.ml.classification import LinearSVC

    svc = LinearSVC(maxIter=100, regParam=0.0001, labelCol=label_column)
    model = svc.fit(df)

    predictions = model.transform(df)

    df.groupBy(label_column).count().show()
    predictions.groupBy("prediction").count().show()

    Evaluate.classification_evoluator(predictions)

    # model_path = "./SVMModel"
    # model.write().overwrite().save(model_path)
    

def load_linear_svm(df,label_column="label"):
    from pyspark.ml.classification import LinearSVCModel

    model_path = "./SVMModel"
    model = LinearSVCModel.load(model_path)

    df = model.transform(df)

    df = df.drop("rawPrediction", "features")
    df = df.withColumnRenamed("prediction", label_column)
    df.groupBy(label_column).count().show()

    return df
