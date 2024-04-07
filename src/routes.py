from collections import Counter
from flask import flash, redirect, render_template, request, session, url_for, jsonify
from src import (
    app,
    dbconfig,
    display,
    format,
    feature_selections,
    cleaning,
    Evaluate,
    feature_scaling,
    mlmodel,
)
from pyspark.sql import functions as F
from utils.db_config import get_database_connection
from flask import request, render_template, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash  # Import the hash function


@app.route("/login.html", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form[
            "password"
        ]  # Assuming the password field name is 'password'

        # Connect to the MySQL database
        conn = get_database_connection()

        cursor = conn.cursor()

        # Check if the email and password match in the database
        cursor.execute(
            "SELECT id FROM anomaly_detection.register WHERE email = %s AND password = %s",
            (email, password),
        )
        user_id = cursor.fetchone()

        if user_id:
            # Store the user's ID in the session
            session["user_id"] = user_id[0]
            conn.close()
            flash("Login Successful!", "success")
            return redirect(
                url_for("dashboard")
            )  # Redirect to the user's dashboard route

        conn.close()
        flash("Invalid email or password. Please try again.", "danger")

    return render_template("login.html")


@app.route("/signup.html", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]

        # Connect to the MySQL database
        conn = get_database_connection()

        cursor = conn.cursor()

        # Check if the email already exists in the database
        cursor.execute(
            "SELECT id FROM anomaly_detection.register WHERE email = %s", (email,)
        )
        existing_user = cursor.fetchone()

        if existing_user:
            conn.close()
            flash(
                "Email already exists. Please use a different email address.", "error"
            )
            return redirect(url_for("signup"))

        # If the email doesn't exist, proceed with insertion
        cursor.execute(
            "INSERT INTO anomaly_detection.register (name, email, password) VALUES (%s, %s, %s)",
            (name, email, password),
        )
        conn.commit()

        # Retrieve the newly inserted user's ID
        cursor.execute(
            "SELECT id FROM anomaly_detection.register WHERE email = %s", (email,)
        )
        user_id = cursor.fetchone()

        if user_id:
            # Store the user's ID in the session
            session["user_id"] = user_id[0]
            conn.close()
            return jsonify(
                {
                    "success": True,
                    "message": "Registration Successful! You are now logged in.",
                }
            )

        conn.close()

    return render_template("signup.html")


@app.route("/logout.html")
def logout():
    session.pop("user_id", None)  # Remove the user ID from the session
    if "_flashes" in session:
        session["_flashes"] = []
    return redirect(url_for("login"))


@app.route("/index.html", methods=["GET", "POST"])
@app.route("/", methods=["GET", "POST"])
def contact_us():
    if request.method == "POST":
        if request.form["form_type"] == "contact_us":
            name = request.form["name"]
            email = request.form["email"]
            subject = request.form["subject"]
            message = request.form["message"]

            # Connect to the MySQL database
            conn = get_database_connection()
            cursor = conn.cursor()

            cursor.execute(
                "INSERT INTO anomaly_detection.contact_us (name, email, subject, message) VALUES (%s,%s,%s,%s)",
                (name, email, subject, message),
            )
            conn.commit()
            conn.close()

            return jsonify({"success": True})
        elif request.form["form_type"] == "newsletter":
            email = request.form["email"]

            # Connect to the MySQL database
            conn = get_database_connection()
            cursor = conn.cursor()

            cursor.execute(
                "INSERT INTO anomaly_detection.newsletter (email) VALUES (%s)", (email,)
            )
            conn.commit()
            conn.close()

            return jsonify({"success": True})

    return render_template("index.html")


@app.route("/dashboard.html", methods=["GET", "POST"])
def dashboard():
    user_id = session.get("user_id")
    user_data = None
    options = None

    if user_id:
        # Retrieve user data
        connection = get_database_connection()
        cursor = connection.cursor()  # Use dictionary cursor for easier data access

        cursor.execute("SELECT name, email FROM register WHERE id=%s", (user_id,))
        user_data = cursor.fetchone()

        # Fetch options for each category
        cursor.execute("SELECT category, name FROM config_ml")
        options = cursor.fetchall()

        if request.method == "POST":
            try:
                database_selection = request.form["database"]
                formatting_selection = request.form["formatting"]
                scaling_selection = request.form["scaling"]
                feature_selection = request.form["selection"]
                model_selection = request.form["model"]

                cleaning = request.form.getlist(
                    "cleaning[]"
                )  # Accessing the list of selected cleaning options
                cleaning_selection = (
                    ",".join(cleaning) if cleaning else ""
                )  # Joining the list into a single string

                # Insert user selections into the database
                cursor.execute(
                    "INSERT INTO `anomaly_detection`.`user_selections` (`userid`, `database_selection`, `cleaning_selection`, `formatting_selection`, `scaling_selection`, `feature_selection`, `model_selection`) VALUES (%s, %s, %s, %s, %s, %s, %s)",
                    (
                        user_id,
                        database_selection,
                        cleaning_selection,
                        formatting_selection,
                        scaling_selection,
                        feature_selection,
                        model_selection,
                    ),
                )
                connection.commit()

            except Exception as e:
                print("Error:", e)
                connection.rollback()  # Rollback the transaction in case of an error
            finally:
                cursor.close()
                connection.close()  # Close the connection

    return render_template("dashboard.html", user_data=user_data, options=options)


@app.route("/visualize.html", methods=["GET", "POST"])
def visualize():
    user_id = session.get("user_id")
    selection = None  # Initialize selection variable
    selection_column = None  # Initialize selection column variable

    if user_id:
        try:
            connection = get_database_connection()
            cursor = connection.cursor()  

            # Fetch options for each category
            query="SELECT timestamp FROM anomaly_detection.user_selections where userid =%s"
            cursor.execute(query,(user_id,))
            options = cursor.fetchall()

            query = "SELECT * FROM anomaly_detection.windows"
            cursor.execute(query)
            data = cursor.fetchall()
            column_names = [i[0] for i in cursor.description]
            connection.commit()



            if request.method == "POST":

                timestamp = request.form["timestamp"]

                query = "SELECT database_selection, cleaning_selection, formatting_selection, scaling_selection, feature_selection, model_selection FROM anomaly_detection.user_selections WHERE timestamp = %s"

                cursor.execute(query, (timestamp,))
                selection = cursor.fetchall()
                
                database_selection = selection[0][0]
                cleaning_selection = selection[0][1]
                formatting_selection = selection[0][2]
                scaling_selection = selection[0][3]
                feature_selection = selection[0][4]
                model_selection = selection[0][5]

                print(database_selection)
                print(cleaning_selection)
                print(formatting_selection)
                print(scaling_selection)
                print(feature_selection)
                print(model_selection)
                
                # Call the corresponding PySpark methods based on selections
                if database_selection:
                    data = dbconfig.get_data("labeled")
                    data.show(5)
                    
                    user_counter = {}
                    # Iterate over each row of the DataFrame
                    for row in data.collect():
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
                data.show(5, truncate=False)
                display.display_information(data)

                # if "Clean_data" in cleaning_selection:
                #     data = cleaning.clean_data(data)
                # if "Handle_null_values" in cleaning_selection:
                #     data = cleaning.handle_null_values(data)
                # if "Remove_outliers" in cleaning_selection:
                #     data = cleaning.outliers_handling(data)
                # if "Balance_data" in cleaning_selection:
                #     data = cleaning.balance_data(data)
                data.show(5, truncate=False)
                if formatting_selection == "Lebel_encoding":
                    data = format.label_encoding(data)
                    data = format.vector_assemble(data)
                elif formatting_selection == "One_hot_encoding":
                    data = format.hash_encoding(data)
                    data = format.vector_assemble(data)
                elif formatting_selection == "HashingTF_Encoding":
                    data = format.hashing_tf(data)
                    data = format.vector_assemble(data)
                elif formatting_selection == "Hash_encoding":
                    data = format.hash_encoding(data)
                    data = format.vector_assemble(data)
                data.show(5, truncate=False)
                if scaling_selection == "Standered_scaler":
                    data = feature_scaling.standerd_scaler(data)
                elif scaling_selection == "Robust_scaler":
                    data = feature_scaling.robustScaler(data)
                elif scaling_selection == "Minmax_scaler":
                    data = feature_scaling.minMaxScaler(data)
                elif scaling_selection == "MinAbs_scaler":
                    data = feature_scaling.minAbsScaler(data)
                elif scaling_selection == "Bucketizer":
                    data = feature_scaling.bucketizer(data)
                data.show(5, truncate=False)
                if feature_selection == "Chisqselector":
                    data = feature_selections.chisqselector(data)
                data.show(5, truncate=False)
                if model_selection == "Random_forest":
                    data = mlmodel.random_forest(data)
                elif model_selection == "Linear_regression":
                    data = mlmodel.linear_regression(data)
                elif model_selection == "Logistic_regression":
                    data = mlmodel.logistic_regression(data)
                elif model_selection == "Linear_SVM":
                    data = mlmodel.train_linear_svm(data)
                data.show(5, truncate=False)

                grouped_counts = data.groupby("prediction").count()
                normal = grouped_counts.filter(grouped_counts["prediction"] == 0).select(F.col("count")).first()[0]
                anomaly = grouped_counts.filter(grouped_counts["prediction"] == 1).select(F.col("count")).first()[0]
            else:
                query="SELECT label, COUNT(*) AS count FROM labeled GROUP BY label;"
                dbconfig.cursor.execute(query)
                # Fetch the results
                results = dbconfig.cursor.fetchall()
                
                # Initialize counts
                normal, anomaly = 0, 0

                # Iterate through results to extract counts
                for row in results:
                    if row[0] == 0:
                        normal = row[1]
                    elif row[0] == 1:
                        anomaly = row[1]
        except Exception as e:
            print("Error:", e)
        finally:
            connection.close()

    return render_template(
        "visualize.html",
        data=data,
        columns=column_names,
        anomaly=anomaly,
        normal=normal,
        options=options,
        selection=selection,
        selection_column=[
            "Database",
            "Cleaning",
            "Formating",
            "Feature Scaling",
            "Feature Selection",
            "Selected Model",
        ],
    )
