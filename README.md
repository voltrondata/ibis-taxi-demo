# Ibis Taxi Demo

This repo demonstrates how to run Ibis with a DuckDB back-end for local development and a PySpark backend for distributed compute when processing larger data sets. 

## Setup

### 1. Clone the repo
```shell
git clone https://github.com/voltrondata/ibis-taxi-demo
```

### 2. Python setup
Create a new Python 3.8+ virtual environment and install requirements with:
```shell
cd ibis-taxi-demo

# Create the virtual environment
python3 -m venv ./venv

# Activate the virtual environment
. ./venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install requirements
pip install --requirement requirements.txt
```

### 3. AWS Client 
Make sure you have the AWS CLI installed (if not, see these [instructions](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html)).

To use the scripts directory with AWS - create a .env file locally in the [scripts](scripts) directory.  Note: It will be git ignored.

Authenticate to AWS - and get the AWS environment variable credentials.

Paste the contents in the .env file - example contents:

```
export AWS_ACCESS_KEY_ID="put value from AWS here"
export AWS_SECRET_ACCESS_KEY="put value from AWS here"
export AWS_SESSION_TOKEN="put value from AWS here"
export AWS_DEFAULT_REGION="us-east-1"
```

Note: You'll have to update this file when your token expires...

## Local Development - Ibis DuckDB back-end demo

### 1. Assuming you've run the setup steps above - run this command to download parquet data locally to the ./data folder:
```shell
pushd scripts
./get_data.sh
popd
```

### 2. Now run the Python Ibis code to process the local parquet data using DuckDB:
```shell
python ibis_demo_duckdb.py
```

You should see output similar to the following:
```text
  hvfhs_license_num  trip_count  trip_miles_total  trip_miles_avg     cost_total  cost_avg
0            HV0003    12968005     65,717,423.00            5.07 390,289,500.33     30.10
1            HV0005     5117891     25,352,368.39            4.95 137,708,332.74     26.91
```

## Distributed Compute - Ibis PySpark back-end demo using Amazon EMR Spark
For larger datasets, you'll likely need a distributed compute engine such as Spark.

**Important**: You'll need to have an AWS account which has privileges to create S3 buckets and provision EMR clusters in your AWS Account.

These steps show how to provision an interactive AWS EMR Spark cluster which will run a special bootstrap script to upgrade the default Python version from 3.7 to 3.10 so that you can use the latest Ibis version features with the Ibis PySpark backend.

**Important**: make sure you have fresh AWS credentials in the local scripts/.env file (see setup step #3 above)

### 1. Setup (one time step)
```shell
pushd scripts

# Create an EMR logging bucket
./create_emr_log_bucket.sh

# Create an EMR bootstrap bucket, and upload the bootstrap shell script for upgrading Python and installing Ibis requirements in EMR
./create_bucket_and_upload_bootstrap_script.sh
```

### 2. Provisioning the interactive EMR Cluster   
Assuming you've run the setup step #1 above and that you have an AWS account authenticated which has privileges to provision EMR clusters, run this script:
```shell
./provision_emr_spark_cluster.sh
```

**Note**: the provisioning script will create a SSH key and place it into the [scripts/.ssh](scripts/.ssh) directory.  The file will be git ignored for security reasons.

The script will run for several minutes and eventually have output like this example:
```
Cluster status: BOOTSTRAPPING
Cluster status: WAITING
Cluster is ready!
Use this SSH command to connect to the EMR cluster: 
ssh -i ./.ssh/keypair.pem hadoop@ec2-xx-xxx-xx-xxx.compute-1.amazonaws.com
```

Go ahead and connect using the ssh command output by the script (not the example above).

When you connect the first time, ssh will ask: ``Are you sure you want to continue connecting (yes/no/[fingerprint])?"``

Type: ``yes``   
then hit Enter.

Once connected, type ``pyspark`` and then hit enter to start the interactive PySpark shell.

Copy and paste the contents of file: [ibis_demo_pyspark.py](ibis_demo_pyspark.py) into the shell to run the Ibis code against a much larger dataset and the local DuckDB example.  This code will use Spark's distributed compute capabilities to divide and conquer the larger data workload.

You should see output similar to the following:
```text
...
>>> print(trip_summary.execute())
  hvfhs_license_num  trip_count  trip_miles_total  trip_miles_avg        cost_total  cost_avg
0            HV0005   201571786  1,008,864,430.87            5.00  5,121,759,734.73     25.41
1            HV0003   561586224  2,684,517,922.50            4.78 13,824,901,291.98     24.62
2            HV0002     6388934     27,129,772.50            4.25    122,262,575.55     20.81
3            HV0004    13884957     53,652,525.62            3.86    201,049,319.02     14.48
```

**Note**: The EMR Cluster should self-terminate after being idle for 1 hour.
