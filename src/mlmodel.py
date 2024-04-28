from src import Evaluate


# ------------------------------------Linear Regression Function-------------------------------------------#
def linear_regression(df, label_column="label"):
    from pyspark.ml.regression import LinearRegression
    from pyspark.sql.functions import when

    # # Split the data into training and testing sets
    # (trainingData, testData) = df.randomSplit([0.8, 0.2], seed=42)

    lr = LinearRegression(featuresCol="features", labelCol=label_column, regParam=0.01)

    model = lr.fit(df)

    model_path = "./Models/linear_regression"
    model.write().overwrite().save(model_path)
  
    predictions = model.transform(df)
    
    Evaluate.classification_evoluator(predictions,label_column)

    predictions = predictions.withColumn("predicted_label", when(predictions["prediction"] >= 0.8, 1).otherwise(0))
    
    predictions = predictions.drop("prediction").withColumnRenamed("predicted_label", "prediction")

    return predictions


# ------------------------------------Logistic Regression Function-------------------------------------------#
def logistic_regression(df, label_column="label"):
    from pyspark.ml import Pipeline
    from pyspark.ml.classification import LogisticRegression

    lr = LogisticRegression(featuresCol="features", labelCol=label_column)

    # Creating the pipeline
    pipeline = Pipeline(stages=[lr])

    # Train the model
    model = pipeline.fit(df)

  
    predictions = model.transform(df)

    Evaluate.classification_evoluator(predictions,label_column)

    model_path = "./Models/LogisticRegression"
    model.write().overwrite().save(model_path)

    # # Drop the label column for predictions
    # df_for_predictions = df.drop(label_column)

    # # Generate predictions using the model
    # predictions = model.transform(df_for_predictions)
       

    return predictions


# ------------------------------Random Forest Model------------------------------------------------- #
def random_forest(df, label_column="label"):
    from pyspark.ml.classification import RandomForestClassifier
    from pyspark.ml.classification import RandomForestClassificationModel

    # Random Forest Classifier
    rf = RandomForestClassifier(labelCol=label_column, featuresCol="features")
    
    # Train the model
    model = rf.fit(df)

    # Make predictions
    predictions = model.transform(df)

    Evaluate.classification_evoluator(predictions)

    model_path = "./Models/RandomForest"
    model.write().overwrite().save(model_path)

    # model = RandomForestClassificationModel.load(model_path)

    # df = model.transform(df)

    # df = df.drop("rawPrediction", "features")
    # df = df.withColumnRenamed("prediction", label_column)
    # df.groupBy(label_column).count().show()

    return predictions

def linear_svm(df, label_column="label"):
    from pyspark.ml.classification import LinearSVC
    from pyspark.ml.classification import LinearSVCModel

    svc = LinearSVC(maxIter=100, regParam=0.0001, labelCol=label_column)

    model = svc.fit(df)

    predictions = model.transform(df)

    # # df.groupBy(label_column).count().show()
    # predictions.groupBy("prediction").count().show()

    Evaluate.classification_evoluator(predictions)

    model_path = "./Models/SVMModel"
    model.write().overwrite().save(model_path)

    # model = LinearSVCModel.load(model_path)
    # df = model.transform(df)

    # df = df.drop("rawPrediction", "features")
    # df = df.withColumnRenamed("prediction", label_column)
    # df.groupBy(label_column).count().show()
    
    return predictions