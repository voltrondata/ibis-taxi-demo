import ibis
from ibis import _
import pandas as pd

# Setup pandas
pd.set_option("display.width", 0)
pd.set_option("display.max_columns", 99)
pd.set_option("display.max_colwidth", None)
pd.set_option("display.float_format", '{:,.2f}'.format)

con = ibis.pyspark.connect(spark)

spark_df = spark.read.parquet("s3://nyc-tlc/trip data/yellow_tripdata_2022-11.parquet")
spark_df.createOrReplaceTempView("trip_data")
trip_data = con.table("trip_data")

trip_summary = (trip_data[_.passenger_count > 0]
.group_by([_.VendorID])
.aggregate(
    trip_count=_.count(),
    passenger_total=_.passenger_count.sum(),
    trip_distance_total=_.trip_distance.sum(),
    trip_distance_avg=_.trip_distance.mean(),
    cost_total=_.total_amount.sum(),
    cost_avg=_.total_amount.mean()
)
)

print(trip_summary.execute())
