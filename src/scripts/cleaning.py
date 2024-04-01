from pyspark.sql import functions as F
from pyspark.sql.window import Window
from pyspark.sql.functions import col

from typing import List
import pyspark.sql as sql
from pyspark.sql.functions import rand, row_number


def clean_data(df):
    print("\n----------- Cleaning Data -----------")

    # Repartition DataFrame for parallelism
    num_partitions = 8
    df = df.repartition(num_partitions)

    # Replace dots with underscores in column names (modify as needed)
    for col_name in df.columns:
        new_col_name = col_name.replace('.', '_')
        df = df.withColumnRenamed(col_name, new_col_name)

    # Drop Columns having all values null or empty string
    columns_to_drop = [col_name for col_name in df.columns if
                       all(row[col_name] == "" or row[col_name] is None for row in df.collect())]

    df_no_null_columns = df.drop(*columns_to_drop)

    # df_no_null_columns = df.drop(*[col_name for col_name in df.columns if df.select(countDistinct(col(col_name)))
    # .collect()[0][0]==0])

    return df_no_null_columns


def handle_null_values(df):
    print("\n----------- Handle Null Value -----------")
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


def outliers_handling(df):
    from pyspark.sql.functions import col
    print("\n----------- Outliers Handling -----------")
    print("Number of rows before:", df.count())

    quantitative_cols = [col_name for col_name, data_type in df.dtypes if
                         data_type in ['int', 'bigint', 'double', 'float']]

    # Compute quantiles for all quantitative columns at once
    quantile_dict = df.approxQuantile(quantitative_cols, [0.25, 0.75], 0.05)

    # Create a dictionary to store quantiles for each column
    quantile_map = dict(zip(quantitative_cols, quantile_dict))

    # Filter outliers for each column
    for col_name, quantiles in quantile_map.items():
        Q1, Q3 = float(quantiles[0]), float(quantiles[1])
        IQR = Q3 - Q1
        df = df.filter((col(col_name) >= (Q1 - 2 * IQR)) & (col(col_name) <= (Q3 + 2 * IQR)))

    print("Number of rows after:", df.count())

    return df


def balance_data(df):
    print("\n----------- Balancing Data -----------")

    under_sampling_percentage = 0.3
    minority_class_count = df.filter(col("class") == 0).count()

    # Calculate target minority count with under-sampling percentage
    target_minority_count = int(minority_class_count * (1 + under_sampling_percentage))

    # Debugging: Print class counts
    # print("Minority Class Count:", minority_class_count)
    # print("Target Minority Count:", target_minority_count)

    window_spec = Window.partitionBy("class").orderBy(F.rand())
    df = df.withColumn("row_number", F.row_number().over(window_spec))

    # Debugging: Show intermediate DataFrame
    # df.show()

    df_under_sampled = df.filter(
        (col("class") == 1) | ((col("class") == 0) & (col("row_number") <= target_minority_count)))

    # Debugging: Show filtered DataFrame
    # df_under_sampled.show()

    df_under_sampled = df_under_sampled.drop("row_number")

    print("Number of rows:", df_under_sampled.count())
    print("Number of columns:", len(df_under_sampled.columns))

    # df.groupBy("class").count().show()

    return df_under_sampled


def cleaned_save_data(df):
    print("\n----------- Saving Clean Data -----------")
    pandas_df = df.toPandas()
    pandas_df.to_csv("cleaning_data.csv", header=True, index=False)


# def replace_dots_in_column_names(df) -> sql.DataFrame:
    #     """Replace dots with underscores in column names."""
    #     for col_name in df.columns:
    #         new_col_name = col_name.replace('.', '_')
    #         df = df.withColumnRenamed(col_name, new_col_name)
    #
    #     return df
    #
    # def drop_all_null_columns(df) -> sql.DataFrame:
    #     """Drop columns having all values null or empty string."""
    #     columns_to_drop = [col_name for col_name in df.columns if
    #                        all(row[col_name] == "" or row[col_name] is None for row in df.collect())]
    #
    #     df_no_null_columns = df.drop(*columns_to_drop)
    #
    #     return df_no_null_columns
    #
    # def fill_null_values(df, threshold: int = 0) -> sql.DataFrame:
    #     """Fill NULL values in specified columns above the threshold."""
    #     null_columns = []
    #     for column in df.columns:
    #         if df.filter(col(column).isNull()).count() > threshold:
    #             null_columns.append(column)
    #
    #     if null_columns:
    #         print("Columns with null values:")
    #         for column in null_columns:
    #             print(column)
    #             df = df.fillna(0, subset=[column])
    #     else:
    #         pass
    #
    #     return df
    #
    #
    # def downsample_majority_class(df, under_sampling_percentage: float, minority_class: str) -> sql.DataFrame:
    #     """Downsample majority class to match the size of the minority class."""
    #     minority_class_count = df.filter(col(minority_class) == "0").count()
    #     target_minority_count = int(minority_class_count / (1 - under_sampling_percentage))
    #
    #     window_spec = Window.partitionBy(minority_class).orderBy(rand())
    #     df = df.withColumn("row_number", row_number().over(window_spec))
    #     df_downsampled = df.filter(((col(minority_class) == 0) & (col("row_number") <= target_minority_count)) | (
    #                 col(minority_class) == 1)).drop("row_number")
    #
    #     return df_downsampled
    #
    # def preprocess_data(df, num_partitions: int, quantitative_cols: List[str]):
    #     """Preprocess the data using multiple utilities."""
    #     df = df.repartition(num_partitions)
    #     df = replace_dots_in_column_names(df)
    #     df = drop_all_null_columns(df)
    #     df = fill_null_values(df)
    #     df = remove_outliers(df, quantitative_cols)
    #     df = downsample_majority_class(df, 0.3, "class")
    #
    #     return df
