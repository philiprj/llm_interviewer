# Terraform Backend Configuration
# Uncomment and configure this after creating the S3 bucket and DynamoDB table

# terraform {
#   backend "s3" {
#     bucket         = "your-terraform-state-bucket"
#     key            = "llm-interviewer/terraform.tfstate"
#     region         = "us-east-1"
#     dynamodb_table = "terraform-locks"
#     encrypt        = true
#   }
# }

# To set up the S3 backend, run these AWS CLI commands first:
#
# 1. Create S3 bucket for state:
# aws s3 mb s3://your-terraform-state-bucket --region us-east-1
#
# 2. Enable versioning:
# aws s3api put-bucket-versioning \
#   --bucket your-terraform-state-bucket \
#   --versioning-configuration Status=Enabled
#
# 3. Create DynamoDB table for locking:
# aws dynamodb create-table \
#   --table-name terraform-locks \
#   --attribute-definitions AttributeName=LockID,AttributeType=S \
#   --key-schema AttributeName=LockID,KeyType=HASH \
#   --provisioned-throughput ReadCapacityUnits=5,WriteCapacityUnits=5
#
# 4. Then uncomment the backend configuration above and run:
# terraform init -reconfigure
