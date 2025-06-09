#!/bin/bash

# Terraform Deployment Script for LLM Interviewer
# Usage: ./scripts/deploy-terraform.sh [environment] [aws-region]

set -e

# Configuration
ENVIRONMENT=${1:-production}
AWS_REGION=${2:-us-east-1}
TERRAFORM_DIR="terraform"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${GREEN}🚀 Starting Terraform deployment for LLM Interviewer...${NC}"

# Check prerequisites
echo -e "${YELLOW}📋 Checking prerequisites...${NC}"

if ! command -v terraform &> /dev/null; then
    echo -e "${RED}❌ Terraform not found. Please install it first.${NC}"
    echo -e "${BLUE}💡 Install from: https://www.terraform.io/downloads${NC}"
    exit 1
fi

if ! command -v aws &> /dev/null; then
    echo -e "${RED}❌ AWS CLI not found. Please install it first.${NC}"
    exit 1
fi

if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker not found. Please install it first.${NC}"
    exit 1
fi

# Check AWS credentials
if ! aws sts get-caller-identity &> /dev/null; then
    echo -e "${RED}❌ AWS credentials not configured. Please run 'aws configure'.${NC}"
    exit 1
fi

# Get AWS Account ID
AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
echo -e "${GREEN}✅ AWS Account ID: ${AWS_ACCOUNT_ID}${NC}"

# Check if terraform.tfvars exists
if [ ! -f "${TERRAFORM_DIR}/terraform.tfvars" ]; then
    echo -e "${YELLOW}⚠️  terraform.tfvars not found. Creating from example...${NC}"
    cp "${TERRAFORM_DIR}/terraform.tfvars.example" "${TERRAFORM_DIR}/terraform.tfvars"
    echo -e "${RED}❌ Please edit terraform/terraform.tfvars with your configuration and run again.${NC}"
    echo -e "${BLUE}💡 Don't forget to set your OpenAI API key!${NC}"
    exit 1
fi

# Change to terraform directory
cd "${TERRAFORM_DIR}"

# Initialize Terraform
echo -e "${YELLOW}🔧 Initializing Terraform...${NC}"
terraform init

# Validate configuration
echo -e "${YELLOW}✅ Validating Terraform configuration...${NC}"
terraform validate

# Plan deployment
echo -e "${YELLOW}📋 Planning Terraform deployment...${NC}"
terraform plan \
    -var="environment=${ENVIRONMENT}" \
    -var="aws_region=${AWS_REGION}" \
    -out=tfplan

# Confirm deployment
echo -e "${YELLOW}❓ Do you want to apply this plan? (y/N)${NC}"
read -r confirmation
if [[ ! "$confirmation" =~ ^[Yy]$ ]]; then
    echo -e "${YELLOW}❌ Deployment cancelled.${NC}"
    exit 0
fi

# Apply Terraform
echo -e "${YELLOW}🚀 Applying Terraform configuration...${NC}"
terraform apply tfplan

# Get outputs
echo -e "${YELLOW}📤 Getting deployment outputs...${NC}"
ECR_URL=$(terraform output -raw ecr_repository_url)
ALB_DNS=$(terraform output -raw load_balancer_dns)
APP_URL=$(terraform output -raw application_url)

echo -e "${GREEN}✅ Infrastructure deployed successfully!${NC}"

# Change back to project root
cd ..

# Build and push Docker image
echo -e "${YELLOW}🐳 Building and pushing Docker image...${NC}"

# Login to ECR
aws ecr get-login-password --region "${AWS_REGION}" | docker login --username AWS --password-stdin "${ECR_URL}"

# Generate timestamp
TIMESTAMP=$(date +%Y%m%d%H%M%S)

# Build image with specific tag
echo "Building image with timestamp: ${TIMESTAMP}"
docker build -t llm-interviewer .

# Tag the image properly
docker tag llm-interviewer:latest "${ECR_URL}:latest"
docker tag llm-interviewer:latest "${ECR_URL}:${TIMESTAMP}"

# Verify tags exist before pushing
echo "Verifying tags..."
docker images | grep llm-interviewer

# Push images
echo "Pushing latest tag..."
docker push "${ECR_URL}:latest"
echo "Pushing timestamped tag..."
docker push "${ECR_URL}:${TIMESTAMP}"

echo -e "${GREEN}✅ Image pushed successfully${NC}"

# Update ECS service to force new deployment
echo -e "${YELLOW}🔄 Updating ECS service...${NC}"
cd "${TERRAFORM_DIR}"
CLUSTER_NAME=$(terraform output -raw ecs_cluster_name)
SERVICE_NAME=$(terraform output -raw ecs_service_name)
cd ..

aws ecs update-service \
    --cluster "${CLUSTER_NAME}" \
    --service "${SERVICE_NAME}" \
    --force-new-deployment \
    --region "${AWS_REGION}" > /dev/null

echo -e "${YELLOW}⏳ Waiting for service to stabilize...${NC}"
aws ecs wait services-stable \
    --cluster "${CLUSTER_NAME}" \
    --services "${SERVICE_NAME}" \
    --region "${AWS_REGION}"

echo -e "${GREEN}🎉 Deployment completed successfully!${NC}"
echo -e "${GREEN}🌐 Your application is available at: ${APP_URL}${NC}"
echo -e "${YELLOW}💡 Note: It may take a few minutes for the application to become fully available.${NC}"

# Display useful information
echo -e "\n${BLUE}📊 Deployment Information:${NC}"
echo -e "${BLUE}─────────────────────────${NC}"
echo -e "Application URL: ${APP_URL}"
echo -e "Load Balancer DNS: ${ALB_DNS}"
echo -e "ECR Repository: ${ECR_URL}"
echo -e "ECS Cluster: ${CLUSTER_NAME}"
echo -e "ECS Service: ${SERVICE_NAME}"
echo -e "AWS Region: ${AWS_REGION}"
echo -e "Environment: ${ENVIRONMENT}"

echo -e "\n${BLUE}🛠️  Useful Commands:${NC}"
echo -e "${BLUE}─────────────────────${NC}"
echo -e "View logs: aws logs tail /ecs/llm-interviewer --follow --region ${AWS_REGION}"
echo -e "Scale service: aws ecs update-service --cluster ${CLUSTER_NAME} --service ${SERVICE_NAME} --desired-count <count> --region ${AWS_REGION}"
echo -e "Destroy infrastructure: cd terraform && terraform destroy"
