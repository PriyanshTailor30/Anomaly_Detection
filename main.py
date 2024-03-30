from scripts.dbconfig import *
from scripts.display import *

from scripts.cleaning import *
from scripts.format import *

# from scripts.feature_scaling import *
# from scripts.feature_selection import *

df = get_data("train_data")

display_information(df, "class")
df.show(5)
df.printSchema()

clean_data(df).show()

handle_null_values(df).show()

outliers_handling(df).show()

label_encoding(df).show()

balance_data(df).show()
