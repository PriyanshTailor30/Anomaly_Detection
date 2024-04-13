import mysql.connector
from pyspark.sql import SparkSession
from utils.db_config import get_database_connection
# Access environment variables
# user = config('user_VARIABLE')
# password = config('password_VARIABLE')
# host = config('host_Variable')
# schema = config('schema_variable')
sql_connection = get_database_connection()

sql_cursor = sql_connection.cursor()

user = 'root'
password = 'root'
host = '127.0.0.1'
schema = 'anomaly_detection'

connection = mysql.connector.connect(
    host=host,
    user=user,
    password=password,
    database=schema
)

cursor = connection.cursor()

spark = SparkSession.builder \
    .appName("AnomalyDetection") \
    .config("spark.ui.port", 4042) \
    .config("spark.jars.packages", "") \
    .config("spark.sql.debug.maxToStringFields", 100) \
    .getOrCreate()

# Get SparkContext
sc = spark.sparkContext
# Set the desired logging level
sc.setLogLevel("OFF")


def get_data(dataset):
    query = f'SELECT * FROM {schema}.{dataset}'
    cursor.execute(query)
    results = cursor.fetchall()
    column_names = [desc[0] for desc in cursor.description]
    df_pyspark = spark.createDataFrame(results, schema=column_names)
    return df_pyspark
