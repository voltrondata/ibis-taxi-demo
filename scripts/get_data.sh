#!/bin/bash

set -e

SCRIPT_DIR=$(dirname ${0})
# Source the .env file for the AWS env vars needed for authentication
source ${SCRIPT_DIR}/.env

DATA_DIR="${SCRIPT_DIR}/../data"

aws s3 cp s3://nyc-tlc/"trip data"/fhvhv_tripdata_2022-11.parquet ${DATA_DIR}
