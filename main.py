from src import dbconfig
from src import format, mlmodel, Evaluate


def main():
    df = dbconfig.get_data("labeled")

    dbconfig.cursor.execute("SELECT DISTINCT targetUserName FROM labeled",)
    distinct_users = dbconfig.cursor.fetchall()
    users_list = [user[0] for user in distinct_users]
    print("List of Users:")
    print(users_list)

    user_counter = {}

    # Iterate over each row of the DataFrame
    for row in df.collect():
        if row['task'] == 'LoginFailure':
            if row['targetUserName'] not in user_counter:
                user_counter[row['targetUserName']] = 0

            user_counter[row['targetUserName']] += 1

            if user_counter[row['targetUserName']] >= 3:
                query = f'UPDATE anomaly_detection.labeled SET label = "1" WHERE id = %s'
                dbconfig.cursor.execute(query, (row['id'],))
                dbconfig.connection.commit()
        elif row['task'] == "LogOn":
            user_counter[row['targetUserName']] = 0

        elif row['task'] == "LogOff":
            pass

    print(user_counter)

    # Close the cursor and connection
    dbconfig.cursor.close()
    dbconfig.connection.close()

    df.show(truncate=False)
    df.printSchema()

    hash_df = format.hash_encoding(df)
    print("Formatting")
    hash_df.show(3, truncate=False)

    assembled_df = format.vector_assemble(hash_df, "label")
    print("Vector Assembler")
    assembled_df.show(3)
    assembled_df.groupby("label").count().show()

    result_df = mlmodel.logistic_regression(assembled_df, "label")
    result_df.show()
    result_df.groupby("prediction").count().show()
    
    # df = df.toPandas()
    # csv_file_path = r".data\processed\usecase1.csv"
    # df.to_csv(csv_file_path, index=False)
    # print("Saving Done")


if __name__ == "__main__":
    main()
