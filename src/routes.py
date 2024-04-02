from collections import Counter
from flask import flash, redirect, render_template, request, session, url_for, jsonify
from src import app
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

                # print("user_id Selection:", user_id)
                # print("Database Selection:", database_selection)
                # print("Cleaning Selection:", cleaning_selection)
                # print("Formatting Selection:", formatting_selection)
                # print("Scaling Selection:", scaling_selection)
                # print("Feature Selection:", feature_selection)
                # print("Model Selection:", model_selection)

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
    user_data = None
    selection = None  # Initialize selection variable
    selection_column = None  # Initialize selection column variable

    if user_id:
        try:
            # Retrieve user data
            connection = get_database_connection()
            cursor = connection.cursor()  # Use dictionary cursor for easier data access

            cursor.execute("SELECT name, email FROM register WHERE id=%s", (user_id,))
            user_data = cursor.fetchone()

            # Fetch options for each category
            cursor.execute("SELECT timestamp FROM anomaly_detection.user_selections")
            options = cursor.fetchall()

            query = "SELECT duration,protocol_type,service,flag,class FROM train_data"
            cursor.execute(query)
            data = cursor.fetchall()
            column_names = [i[0] for i in cursor.description]
            connection.commit()

            query = "SELECT 'anomaly' AS class, SUM(CASE WHEN class='anomaly' THEN 1 ELSE 0 END ) as count FROM train_data UNION ALL SELECT 'normal' AS class, SUM(CASE WHEN class='normal' THEN 1 ELSE 0 END ) as count FROM train_data"
            cursor.execute(query)
            collect = cursor.fetchall()

            # Count occurrences of each class
            anomaly = collect[0][1]
            normal = collect[1][1]

            if request.method == "POST":
                timestamp = request.form["timestamp"]
                query = "SELECT database_selection, cleaning_selection, formatting_selection, scaling_selection, feature_selection, model_selection FROM anomaly_detection.user_selections WHERE timestamp = %s"
                cursor.execute(query, (timestamp,))
                selection = cursor.fetchall()

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
        user_data=user_data,
        options=options,
        selection=selection,
        selection_column=["Database","Cleaning","Formating","Feature Scaling","Feature Selection","Selected Model"],
    )