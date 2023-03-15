#!/bin/bash

# Get the AWS Account ID
AWS_ACCOUNT_ID=$(aws sts get-caller-identity | jq -r '.Account')

aws s3api create-bucket --bucket emr-log-bucket-${AWS_ACCOUNT_ID}
