def regression_evaluator(predictions, label_column="label"):
    from pyspark.ml.evaluation import RegressionEvaluator

    # Evaluate the model
    evaluator = RegressionEvaluator(labelCol=label_column, predictionCol="prediction", metricName="rmse")
    rmse = evaluator.evaluate(predictions)
    print(f"Error (RMSE) on data = {rmse}")

    evaluator = RegressionEvaluator(labelCol=label_column, predictionCol="prediction", metricName="mse")
    mse = evaluator.evaluate(predictions)
    print(f"Error (mse) on data = {mse}")

    evaluator = RegressionEvaluator(labelCol=label_column, predictionCol="prediction", metricName="r2")
    r2 = evaluator.evaluate(predictions)
    print(f"Error (r2) on data = {r2}")

    evaluator = RegressionEvaluator(labelCol=label_column, predictionCol="prediction", metricName="var")
    var = evaluator.evaluate(predictions)
    print(f"Error (var) on data = {var}")

    evaluator = RegressionEvaluator(labelCol=label_column, predictionCol="prediction", metricName="mae")
    mae = evaluator.evaluate(predictions)
    print(f"Error (mae) on data = {mae}")


def classification_evoluator(predictions, label_column="label"):
    from pyspark.ml.evaluation import BinaryClassificationEvaluator, MulticlassClassificationEvaluator

    # Evaluation the model
    evaluator = BinaryClassificationEvaluator(labelCol=label_column, rawPredictionCol="prediction",
                                              metricName="areaUnderROC")
    accuracy = evaluator.evaluate(predictions)
    print("Area Under ROC:", accuracy)

    evaluator = BinaryClassificationEvaluator(labelCol=label_column, rawPredictionCol="prediction",
                                              metricName="areaUnderPR")
    accuracy = evaluator.evaluate(predictions)
    print("Area Under PR:", accuracy)

    evaluator = MulticlassClassificationEvaluator(labelCol=label_column, predictionCol="prediction",
                                                  metricName="f1")
    f1 = evaluator.evaluate(predictions)
    print("F1-score:", f1)

    # MulticlassClassificationEvaluator for precision and recall
    evaluator = MulticlassClassificationEvaluator(labelCol=label_column, predictionCol="prediction",
                                                  metricName="weightedPrecision")
    precision = evaluator.evaluate(predictions)
    print("Precision:", precision)

    evaluator = MulticlassClassificationEvaluator(labelCol=label_column, predictionCol="prediction",
                                                  metricName="weightedRecall")
    recall = evaluator.evaluate(predictions)
    print("Recall:", recall)
