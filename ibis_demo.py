import ibis
from ibis import _
from pathlib import Path
import pandas as pd


# Setup pandas
pd.set_option("display.width", 0)
pd.set_option("display.max_columns", 99)
pd.set_option("display.max_colwidth", None)
pd.set_option("display.float_format", '{:,.2f}'.format)

# Setup some Path constants
SCRIPT_DIR = Path(__file__).parent.resolve()
LOCAL_DATA_DIR = (SCRIPT_DIR / "data").resolve()


def main():
    con = ibis.duckdb.connect("duckdb://", threads=4, memory_limit="1GB")

    trip_data = con.read_parquet((LOCAL_DATA_DIR / "*.parquet").as_posix())

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


if __name__ == "__main__":
    main()
