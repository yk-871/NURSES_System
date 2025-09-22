#!/bin/bash

# AWS ECS Deployment Script for Nurse Scheduling System

set -e

# Configuration
AWS_REGION="us-east-1"
ECR_REPO="nurse-scheduler"
CLUSTER_NAME="nurse-scheduler-cluster"
SERVICE_NAME="nurse-scheduler-service"

echo "Starting deployment to AWS ECS..."

# 1. Create ECR repository if it doesn't exist
echo "Creating ECR repository..."
aws ecr describe-repositories --repository-names $ECR_REPO --region $AWS_REGION || \
aws ecr create-repository --repository-name $ECR_REPO --region $AWS_REGION

# 2. Get ECR login token
echo "Logging into ECR..."
aws ecr get-login-password --region $AWS_REGION | docker login --username AWS --password-stdin $(aws sts get-caller-identity --query Account --output text).dkr.ecr.$AWS_REGION.amazonaws.com

# 3. Build and tag Docker image
echo "Building Docker image..."
cd ..
docker build -t $ECR_REPO .
docker tag $ECR_REPO:latest $(aws sts get-caller-identity --query Account --output text).dkr.ecr.$AWS_REGION.amazonaws.com/$ECR_REPO:latest

# 4. Push image to ECR
echo "Pushing image to ECR..."
docker push $(aws sts get-caller-identity --query Account --output text).dkr.ecr.$AWS_REGION.amazonaws.com/$ECR_REPO:latest

# 5. Deploy CloudFormation stack
echo "Deploying CloudFormation stack..."
cd deploy
aws cloudformation deploy \
  --template-file aws-deploy.yml \
  --stack-name nurse-scheduler-stack \
  --parameter-overrides \
    VpcId=$(aws ec2 describe-vpcs --filters "Name=is-default,Values=true" --query "Vpcs[0].VpcId" --output text) \
    SubnetIds=$(aws ec2 describe-subnets --filters "Name=vpc-id,Values=$(aws ec2 describe-vpcs --filters "Name=is-default,Values=true" --query "Vpcs[0].VpcId" --output text)" --query "Subnets[*].SubnetId" --output text | tr '\t' ',') \
  --capabilities CAPABILITY_IAM \
  --region $AWS_REGION

# 6. Get the load balancer URL
echo "Getting application URL..."
LB_URL=$(aws cloudformation describe-stacks --stack-name nurse-scheduler-stack --query "Stacks[0].Outputs[?OutputKey=='LoadBalancerURL'].OutputValue" --output text --region $AWS_REGION)

echo "Deployment complete!"
echo "Application URL: $LB_URL"
echo "Note: It may take a few minutes for the service to be fully available."