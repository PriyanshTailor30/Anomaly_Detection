def display_information(df, lebel_column="No"):
    print("-----------Dataframe Information:-----------")
    if lebel_column != "No":
        df.groupBy(lebel_column).count().show()

    print("Number of rows:", df.count())
    print("Number of columns:", len(df.columns))

    # df.show(10, truncate=False)
    # df.describe().show()
    # df.printSchema()

    print("-------------------------------------------------\n")
