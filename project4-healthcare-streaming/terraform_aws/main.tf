terraform {
  required_version = ">= 1.5.0"
  
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
  
  backend "s3" {
    bucket         = "medical-streaming-terraform-state"
    key            = "streaming/terraform.tfstate"
    region         = "us-east-1"
    dynamodb_table = "medical-streaming-terraform-locks"
    encrypt        = true
  }
}

provider "aws" {
  region = var.aws_region
  
  default_tags {
    tags = {
      Project     = "Medical Streaming Infrastructure"
      Environment = var.environment
      ManagedBy   = "Terraform"
      Owner       = "DataEngineering"
    }
  }
}

# Data sources
data "aws_caller_identity" "current" {}
data "aws_region" "current" {}
