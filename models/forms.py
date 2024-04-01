
from models import *
df = Anomaly_Detection.dbconfig.get_data("train_data")

display.display_information(df, "class")
df.show(5)
df.printSchema()

cleaning.clean_data(df).show()

# handle_null_values(df).show()

# outliers_handling(df).show()

format.label_encoding(df).show()
