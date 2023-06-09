import ibis
from ibis import _
import pandas as pd
from pyspark.sql import SparkSession

# Setup pandas
pd.set_option("display.width", 0)
pd.set_option("display.max_columns", 99)
pd.set_option("display.max_colwidth", None)
pd.set_option("display.float_format", '{:,.2f}'.format)

# Get a Spark Session
spark = SparkSession \
    .builder \
    .appName(name="Ibis-Rocks!") \
    .getOrCreate()

# Connect the Ibis PySpark back-end to the Spark Session
con = ibis.pyspark.connect(spark)

# Read the parquet data into an ibis table
trip_data = con.read_parquet("s3://nyc-tlc/trip data/fhvhv_tripdata_*.parquet")

trip_data = trip_data.mutate(total_amount=_.base_passenger_fare + _.tolls + _.sales_tax + _.congestion_surcharge + _.tips)

trip_summary = (trip_data.group_by([_.hvfhs_license_num])
.aggregate(
    trip_count=_.count(),
    trip_miles_total=_.trip_miles.sum(),
    trip_miles_avg=_.trip_miles.mean(),
    cost_total=_.total_amount.sum(),
    cost_avg=_.total_amount.mean()
)
)

print(trip_summary.execute())
