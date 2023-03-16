import ibis
from ibis import _
import pandas as pd
from pathlib import Path

# Setup pandas
pd.set_option("display.width", 0)
pd.set_option("display.max_columns", 99)
pd.set_option("display.max_colwidth", None)
pd.set_option("display.float_format", '{:,.2f}'.format)

# Setup some Path constants
SCRIPT_DIR = Path(__file__).parent.resolve()
LOCAL_DATA_DIR = (SCRIPT_DIR / "data").resolve()

# Get our DuckDB connection (to an ephemeral in-memory database)
con = ibis.duckdb.connect(threads=4, memory_limit="1GB")

# This assumes you've run the "get_data.sh" shell script to download the parquet file locally
trip_data = con.read_parquet((LOCAL_DATA_DIR / "fhvhv_tripdata_2022-11.parquet").as_posix())

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

ibis.show_sql(trip_summary)

print(trip_summary.execute())
