#!/bin/bash

set -e

AVAILABILITY_ZONE="us-east-1a"

SCRIPT_DIR=$(dirname ${0})
KEY_DIR="${SCRIPT_DIR}/.ssh"

SSH_KEY="${KEY_DIR}/keypair.pem"

# Create an ssh keypair
rm -f ${SSH_KEY}
aws ec2 delete-key-pair --key-name sparkKey || echo "n/a"
aws ec2 create-key-pair --key-name sparkKey | jq --raw-output .KeyMaterial > ${SSH_KEY}
chmod u=r,g=,o= ${SSH_KEY}

# Create default roles if needed
aws emr create-default-roles

# Get the default subnet for the availability zone
SUBNET_ID=$(aws ec2 describe-subnets | jq -r --arg az "$AVAILABILITY_ZONE" '.Subnets[] | select(.AvailabilityZone==$az and .DefaultForAz==true) | .SubnetId')

# Create the cluster
CLUSTER_ID=$(aws emr create-cluster \
              --name "Sparky1" \
              --release-label emr-6.10.0 \
              --applications Name=Spark \
              --ec2-attributes KeyName=sparkKey,SubnetId="${SUBNET_ID}" \
              --instance-type m5.xlarge \
              --instance-count 2 \
              --use-default-roles \
              --no-auto-terminate \
              --auto-termination-policy IdleTimeout=3600 |  jq -r '.ClusterId'
            )

echo "The EMR Cluster ID is: ${CLUSTER_ID}"

# Loop until the command returns a non-null value
while [[ $(aws emr describe-cluster --cluster-id ${CLUSTER_ID} | jq -r '.Cluster.MasterPublicDnsName') == "null" ]]; do
  echo "Waiting for EMR cluster to start..."
  sleep 10
done

# Set the environment variable to the returned value
export MASTER_DNS=$(aws emr describe-cluster --cluster-id ${CLUSTER_ID} | jq -r '.Cluster.MasterPublicDnsName')
echo "The EMR Cluster Public DNS Name is: ${MASTER_DNS}"

EMR_SECURITY_GROUP=$(aws emr describe-cluster --cluster-id ${CLUSTER_ID} | jq -r '.Cluster.Ec2InstanceAttributes.EmrManagedMasterSecurityGroup')

# Allow ssh traffic to the EMR cluster
aws ec2 authorize-security-group-ingress \
--group-id ${EMR_SECURITY_GROUP} \
--ip-permissions '[{"IpProtocol": "tcp", "FromPort": 22, "ToPort": 22, "IpRanges": [{"CidrIp": "0.0.0.0/0"}]}]' || echo "ingress already setup"

echo -e "Use this SSH command to connect to the EMR cluster: \nssh -i ${SSH_KEY} hadoop@${MASTER_DNS}"
