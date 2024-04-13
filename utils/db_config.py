# ------------------------------- Imports ------------------------------------#
import mysql.connector

# ------------------------------- Connections ------------------------------------#
HOST = "localhost"
USER = "root"
PASSWORD = "root"
DATABASE = "anomaly_detection"


# ------------------------------- Check already available ------------------------------------#
def database_exists(cursor, database_name):
    cursor.execute("SHOW DATABASES")
    databases = cursor.fetchall()
    for db in databases:
        if db[0] == database_name:
            return True
    return False


def table_exists(cursor, table_name):
    cursor.execute("USE `{}`".format(DATABASE))
    cursor.execute("SHOW TABLES LIKE '{}'".format(table_name))
    return cursor.fetchone() is not None


def is_table_empty(cursor, table_name):
    cursor.execute("SELECT COUNT(*) FROM '{}'".format(table_name))
    count = cursor.fetchone()[0]
    return count == 0


# ------------------------------- Create Database / Table ------------------------------------#


def create_database(cursor, database_name):
    cursor.execute("CREATE DATABASE {}".format(database_name))


def create_register_table(cursor):
    try:
        cursor.execute(
            """
            CREATE TABLE `Register` (
                `id` INT NOT NULL AUTO_INCREMENT,
                `name` VARCHAR(45) NOT NULL,
                `email` VARCHAR(45) NOT NULL,
                `password` VARCHAR(45) NOT NULL,
                PRIMARY KEY (`id`),
                UNIQUE INDEX `id_UNIQUE` (`id` ASC) VISIBLE,
                UNIQUE INDEX `email_UNIQUE` (`email` ASC) VISIBLE
            );
        """
        )
    except Exception as e:
        print("Error:", e)


def create_contactus_table(cursor):
    try:
        cursor.execute(
            """ 
            CREATE TABLE `anomaly_detection`.`contact_us` (
                `id` INT NOT NULL AUTO_INCREMENT,
                `name` VARCHAR(45) NOT NULL,
                `email` VARCHAR(45) NOT NULL,
                `subject` VARCHAR(45) NOT NULL,
                `message` VARCHAR(45) NOT NULL,
                PRIMARY KEY (`id`),
                UNIQUE INDEX `id_UNIQUE` (`id` ASC) VISIBLE);
        """
        )
    except Exception as e:
        print("Error:", e)


def create_newsletter_table(cursor):
    try:
        cursor.execute(
            """ 
            CREATE TABLE `anomaly_detection`.`newsletter` (
                `id` INT NOT NULL AUTO_INCREMENT,
                `email` VARCHAR(45) NULL,
                PRIMARY KEY (`id`),
                UNIQUE INDEX `id_UNIQUE` (`id` ASC) VISIBLE,
                UNIQUE INDEX `email_UNIQUE` (`email` ASC) VISIBLE);
        """
        )
    except Exception as e:
        print("Error:", e)


def create_configml_table(cursor):
    try:
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS `anomaly_detection`.`config_ml` (
                `id` INT NOT NULL AUTO_INCREMENT,
                `category` VARCHAR(45) NOT NULL,
                `name` VARCHAR(45) NOT NULL,
                PRIMARY KEY (`id`)
            );
        """
        )
        cursor.connection.commit()
    except Exception as e:
        print("Error:", e)


def create_userselection_table(cursor):
    try:
        cursor.execute(
            """
            CREATE TABLE `anomaly_detection`.`user_selections`(
                `id` INT AUTO_INCREMENT PRIMARY KEY,
                `userid` INT NOT NULL,
                `timestamp` TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
                `database_selection` VARCHAR(55) NOT NULL,
                `cleaning_selection` VARCHAR(55) NOT NULL,
                `formatting_selection` VARCHAR(55) NOT NULL,
                `scaling_selection` VARCHAR(55) NOT NULL,
                `feature_selection` VARCHAR(55) NOT NULL,
                `model_selection` VARCHAR(55) NOT NULL,
                FOREIGN KEY (`userid`) REFERENCES `anomaly_detection`.`register` (`id`)
            );
        """
        )
        cursor.connection.commit()
    except Exception as e:
        print("Error:", e)


def create_labeled_table(cursor):
    try:
        # Construct the SQL queries
        create_query = (
            f"CREATE TABLE anomaly_detection.labeled LIKE anomaly_detection.windows"
        )
        insert_query = f"INSERT INTO anomaly_detection.labeled SELECT * FROM anomaly_detection.windows"
        add_label = (
            f"ALTER TABLE anomaly_detection.labeled ADD COLUMN label INT DEFAULT 0;"
        )
        add_id = f"ALTER TABLE anomaly_detection.labeled ADD COLUMN id INT AUTO_INCREMENT PRIMARY KEY FIRST;"

        # Execute the queries
        cursor.execute(create_query)
        cursor.execute(insert_query)
        cursor.execute(add_label)
        cursor.execute(add_id)

    except Exception as e:
        print("Error:", e)

    # ------------------------------- Insert Data in table ------------------------------------#


def insert_config(cursor):
    try:
        insert_query = """
            INSERT INTO anomaly_detection.config_ml (category, name) 
            VALUES 
            ('database', 'test_data'), 
            ('database', 'firewall'), 
            ('database', 'windows'), 
            ('database', 'Cisco'), 
            ('cleaning', 'Clean_data'), 
            ('cleaning', 'Handle_null_values'), 
            ('cleaning', 'Remove_outliers'), 
            ('cleaning', 'Balance_data'), 
            ('formatting', 'Lebel_encoding'), 
            ('formatting', 'Hash_encoding'), 
            ('formatting', 'HashingTF_Encoding'), 
            ('feature_scaling', 'Standered_scaler'), 
            ('feature_scaling', 'Robust_scaler'), 
            ('feature_scaling', 'Minmax_scaler'), 
            ('feature_scaling', 'MinAbs_scaler'), 
            ('feature_scaling', 'Bucketizer'), 
            ('feature_selection', 'Chisqselector'), 
            ('select_model', 'Random_forest'),
            ('select_model', 'Linear_regression'), 
            ('select_model', 'Logistic_regression'), 
            ('select_model', 'Linear_SVM')
        """
        cursor.execute(insert_query)
    except Exception as e:
        print("Error:", e)


# ------------------------------- Get Connection ------------------------------------#
def get_database_connection():
   
    try:
        connection = mysql.connector.connect(
            host=HOST,
            user=USER,
            password=PASSWORD,
        )
        cursor = connection.cursor()
    
        if not database_exists(cursor, DATABASE):
            create_database(cursor, DATABASE)
        if not table_exists(cursor, "register"):
            create_register_table(cursor)
            connection.commit()
        if not table_exists(cursor, "config_ml"):
            create_configml_table(cursor)
            insert_config(cursor)
            connection.commit()
        if not table_exists(cursor, "contact_us"):
            create_contactus_table(cursor)
            connection.commit()
        if not table_exists(cursor, "newsletter"):
            create_newsletter_table(cursor)
            connection.commit()
        if not table_exists(cursor, "labeled"):
            create_labeled_table(cursor)
            connection.commit()
        if not table_exists(cursor, "user_selections"):
            create_userselection_table(cursor)
            connection.commit()

    except mysql.connector.Error as e:
        print("Error:", e)

    return connection
