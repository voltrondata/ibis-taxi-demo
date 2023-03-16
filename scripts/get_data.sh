#!/bin/bash

SCRIPT_DIR=$(dirname ${0})
DATA_DIR="${SCRIPT_DIR}/../data"

aws s3 cp s3://nyc-tlc/"trip data"/fhvhv_tripdata_2022-11.parquet ${DATA_DIR}
