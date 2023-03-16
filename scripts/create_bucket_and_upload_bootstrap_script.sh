#!/bin/bash

set -e

# Get the AWS Account ID
AWS_ACCOUNT_ID=$(aws sts get-caller-identity | jq -r '.Account')

BOOTSTRAP_BUCKET_NAME="emr-bootstrap-bucket-${AWS_ACCOUNT_ID}"

# Create the bootstrap script bucket for use with EMR
aws s3api create-bucket --bucket ${BOOTSTRAP_BUCKET_NAME}

# Upload our bootstrap shell script
chmod u=rwx,g=rx,o=rx ./emr_ibis_bootstrap.sh
aws s3 cp emr_ibis_bootstrap.sh s3://${BOOTSTRAP_BUCKET_NAME}/
