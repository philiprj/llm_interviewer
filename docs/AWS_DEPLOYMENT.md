# AWS Deployment Guide

This guide covers deploying the LLM Interviewer application to AWS using Infrastructure as Code (IaC) with both Terraform and CloudFormation options.

## 🏗️ Architecture Overview

The application is deployed using the following AWS services:

- **ECS Fargate**: Serverless container hosting
- **Application Load Balancer**: HTTP load balancing and health checks
- **ECR**: Container image registry
- **VPC**: Isolated network environment
- **Secrets Manager**: Secure API key storage
- **CloudWatch**: Logging and monitoring
- **Auto Scaling**: Automatic scaling based on CPU utilization

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                                INTERNET                                     │
└─────────────────────────┬───────────────────────────────────────────────────┘
                          │
┌─────────────────────────▼───────────────────────────────────────────────────┐
│                   APPLICATION LOAD BALANCER                                │
│                     (Port 80/443 - HTTP)                                   │
│                    Health Check: /_stcore/health                           │
└─────────────────────────┬───────────────────────────────────────────────────┘
                          │
┌─────────────────────────▼───────────────────────────────────────────────────┐
│                          VPC (10.0.0.0/16)                                 │
│  ┌─────────────────┐                          ┌─────────────────┐          │
│  │  Public Subnet  │                          │  Public Subnet  │          │
│  │  10.0.1.0/24    │                          │  10.0.2.0/24    │          │
│  │   (AZ-1)        │                          │   (AZ-2)        │          │
│  │                 │                          │                 │          │
│  │ ┌─────────────┐ │                          │ ┌─────────────┐ │          │
│  │ │ ECS Fargate │ │                          │ │ ECS Fargate │ │          │
│  │ │   Tasks     │ │                          │ │   Tasks     │ │          │
│  │ │ (Streamlit) │ │                          │ │ (Streamlit) │ │          │
│  │ │  Port 8501  │ │                          │ │  Port 8501  │ │          │
│  │ └─────────────┘ │                          │ └─────────────┘ │          │
│  └─────────────────┘                          └─────────────────┘          │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│                           SUPPORTING SERVICES                              │
│                                                                             │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐            │
│  │ Amazon ECR      │  │ Secrets Manager │  │ CloudWatch Logs │            │
│  │ (Docker Images) │  │ (OpenAI API Key)│  │ (Application    │            │
│  │                 │  │                 │  │  Logs)          │            │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘            │
│                                                                             │
│  ┌─────────────────┐  ┌─────────────────┐                                  │
│  │ Auto Scaling    │  │ IAM Roles       │                                  │
│  │ (CPU-based)     │  │ (ECS Task &     │                                  │
│  │ 1-10 instances  │  │  Execution)     │                                  │
│  └─────────────────┘  └─────────────────┘                                  │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│                           EXTERNAL SERVICES                                │
│                                                                             │
│  ┌─────────────────┐                                                       │
│  │ OpenAI API      │                                                       │
│  │ (GPT-4)         │                                                       │
│  │                 │                                                       │
│  └─────────────────┘                                                       │
└─────────────────────────────────────────────────────────────────────────────┘
```

## 🚀 Deployment Options

### Option 1: Terraform (Recommended)

Terraform provides better state management, modularity, and multi-cloud support.

#### Prerequisites

1. **Install Terraform** (>= 1.0)
   ```bash
   # macOS
   brew install terraform

   # Linux
   wget https://releases.hashicorp.com/terraform/1.6.0/terraform_1.6.0_linux_amd64.zip
   unzip terraform_1.6.0_linux_amd64.zip
   sudo mv terraform /usr/local/bin/
   ```

2. **Configure AWS CLI**
   ```bash
   aws configure
   # Enter your AWS Access Key ID, Secret Access Key, region, and output format
   ```

3. **Docker** for building and pushing images

#### Quick Deploy

1. **Clone and configure**
   ```bash
   git clone <your-repo>
   cd llm-interviewer

   # Copy and edit configuration
   cp terraform/terraform.tfvars.example terraform/terraform.tfvars
   ```

2. **Edit `terraform/terraform.tfvars`**
   ```hcl
   # Required
   openai_api_key = "your-openai-api-key-here"

   # Optional customizations
   project_name = "llm-interviewer"
   environment  = "production"
   aws_region   = "us-east-1"
   desired_count = 2
   task_cpu     = 1024
   task_memory  = 2048
   ```

3. **Deploy using the automation script**
   ```bash
   chmod +x scripts/deploy-terraform.sh
   ./scripts/deploy-terraform.sh production us-east-1
   ```

4. **Manual deployment (alternative)**
   ```bash
   cd terraform
   terraform init
   terraform plan
   terraform apply
   ```

#### Terraform Backend Setup (Optional but Recommended)

For team environments, configure remote state storage:

1. **Create S3 bucket and DynamoDB table**
   ```bash
   aws s3 mb s3://your-terraform-state-bucket --region us-east-1
   aws s3api put-bucket-versioning \
     --bucket your-terraform-state-bucket \
     --versioning-configuration Status=Enabled

   aws dynamodb create-table \
     --table-name terraform-locks \
     --attribute-definitions AttributeName=LockID,AttributeType=S \
     --key-schema AttributeName=LockID,KeyType=HASH \
     --provisioned-throughput ReadCapacityUnits=5,WriteCapacityUnits=5
   ```

2. **Uncomment and configure `terraform/backend.tf`**
   ```hcl
   terraform {
     backend "s3" {
       bucket         = "your-terraform-state-bucket"
       key            = "llm-interviewer/terraform.tfstate"
       region         = "us-east-1"
       dynamodb_table = "terraform-locks"
       encrypt        = true
     }
   }
   ```

3. **Initialize with remote backend**
   ```bash
   terraform init -reconfigure
   ```

### Option 2: CloudFormation

AWS-native infrastructure as code solution.

!TODO!

## 🔄 CI/CD with GitHub Actions

### Setup

1. **Add GitHub Secrets**
   Go to your repository → Settings → Secrets and add:
   ```
   AWS_ACCESS_KEY_ID: Your AWS access key
   AWS_SECRET_ACCESS_KEY: Your AWS secret key
   OPENAI_API_KEY: Your OpenAI API key
   SLACK_WEBHOOK_URL: (Optional) For deployment notifications
   ```

2. **Create environments**
   - Go to Settings → Environments
   - Create `staging` and `production` environments
   - Add protection rules for production

### Workflow

The GitHub Actions workflow (`.github/workflows/deploy-aws.yml`) provides:

- **Pull Requests**: Terraform plan validation
- **Develop branch**: Auto-deploy to staging
- **Main branch**: Auto-deploy to production
- **Testing**: Linting, type checking, and unit tests

## ⚙️ Configuration Options

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `OPENAI_API_KEY` | OpenAI API key (required) | - |
| `MODEL_PROVIDER` | LLM provider | `openai` |
| `MODEL_NAME` | Model name | `gpt-4` |
| `TEMPERATURE` | Model temperature | `0.05` |
| `MAX_TOPICS` | Maximum topics per interview | `2` |
| `MAX_QUESTIONS_PER_TOPIC` | Questions per topic | `3` |

### Infrastructure Scaling

#### Terraform Variables

```hcl
# Basic scaling
desired_count = 2           # Number of containers
task_cpu      = 1024        # CPU units (1024 = 1 vCPU)
task_memory   = 2048        # Memory in MB

# Auto scaling
enable_autoscaling = true
min_capacity      = 1
max_capacity      = 2
```

#### Manual Scaling

```bash
# Scale ECS service
aws ecs update-service \
  --cluster llm-interviewer-cluster \
  --service llm-interviewer-service \
  --desired-count 5 \
  --region us-east-1
```

## 🔍 Monitoring and Logging

### CloudWatch Logs

```bash
# View real-time logs
aws logs tail /ecs/llm-interviewer --follow --region us-east-1

# View specific time range
aws logs filter-log-events \
  --log-group-name /ecs/llm-interviewer \
  --start-time 1635724800000 \
  --end-time 1635728400000
```

### Health Checks

The application includes health checks at:
- **Load Balancer**: `/_stcore/health`
- **Container**: Internal health check every 30 seconds

### Metrics

Monitor these key metrics in CloudWatch:
- ECS Service CPU/Memory utilization
- ALB target health
- Request count and latency
- Error rates (4xx, 5xx)

## 🛠️ Maintenance

### Updates and Deployments

1. **Code updates**: Push to main/develop branch for automatic deployment
2. **Infrastructure updates**: Modify Terraform files and run `terraform apply`
3. **Scaling**: Update `desired_count` in Terraform or use AWS CLI

### Rollbacks

```bash
# Terraform rollback
cd terraform
terraform apply -target=aws_ecs_service.app -var="desired_count=0"
terraform apply -var="desired_count=2"

# ECS rollback to previous task definition
aws ecs update-service \
  --cluster llm-interviewer-cluster \
  --service llm-interviewer-service \
  --task-definition llm-interviewer:PREVIOUS_REVISION
```

### Cleanup

```bash
# Terraform cleanup
cd terraform
terraform destroy

## 💰 Cost Optimization

### Estimated Monthly Costs (us-east-1)

| Service | Configuration | Monthly Cost |
|---------|---------------|--------------|
| ECS Fargate | 2 tasks × 1 vCPU × 2GB | ~$30 |
| Application Load Balancer | Standard | ~$16 |
| NAT Gateway | Not used (public subnets) | $0 |
| CloudWatch Logs | 10GB/month | ~$5 |
| **Total** | | **~$51/month** |

### Cost Reduction Tips

1. **Use Fargate Spot** for non-production environments
2. **Enable auto-scaling** to scale down during low usage
3. **Optimize log retention** (default: 30 days)
4. **Use reserved capacity** for predictable workloads

## 🔒 Security Best Practices

### Implemented Security Features

- ✅ **Secrets Manager** for API keys
- ✅ **VPC with private subnets** for ECS tasks
- ✅ **Security Groups** with minimal required access
- ✅ **IAM roles** with least privilege principle
- ✅ **ECR image scanning** enabled
- ✅ **CloudWatch logging** for audit trails

### Additional Recommendations

1. **Enable AWS Config** for compliance monitoring
2. **Use AWS WAF** for application-level protection
3. **Implement VPC Flow Logs** for network monitoring
4. **Regular security updates** for base images

## 🐛 Troubleshooting

### Common Issues

1. **ECS tasks failing to start**
   ```bash
   # Check service events
   aws ecs describe-services --cluster CLUSTER_NAME --services SERVICE_NAME

   # Check task logs
   aws logs tail /ecs/llm-interviewer --follow
   ```

2. **Load balancer health checks failing**
   - Verify security groups allow traffic on port 8501
   - Check application health endpoint: `/_stcore/health`

3. **Image push failures**
   ```bash
   # Re-authenticate with ECR
   aws ecr get-login-password --region us-east-1 | \
     docker login --username AWS --password-stdin ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com
   ```

4. **Terraform state issues**
   ```bash
   # Refresh state
   terraform refresh

   # Import existing resources
   terraform import aws_ecs_cluster.main cluster-name
   ```

### Support Resources

- **AWS Documentation**: [ECS](https://docs.aws.amazon.com/ecs/), [Fargate](https://docs.aws.amazon.com/AmazonECS/latest/developerguide/AWS_Fargate.html)
- **Terraform AWS Provider**: [Documentation](https://registry.terraform.io/providers/hashicorp/aws/latest/docs)
- **Streamlit Cloud**: [Alternative deployment option](https://share.streamlit.io/)

## 📈 Scaling for Production

### High Availability Setup

For production environments, consider:

1. **Multi-AZ deployment**
   ```hcl
   public_subnets_cidr = ["10.0.1.0/24", "10.0.2.0/24", "10.0.3.0/24"]
   ```

2. **Database integration** (if needed)
   - RDS for persistent storage
   - ElastiCache for session management

3. **CDN integration**
   - CloudFront for static assets
   - S3 for file storage

4. **Monitoring and alerting**
   - CloudWatch alarms
   - SNS notifications
   - AWS X-Ray for tracing
