variable "aws_region" {
  description = "AWS region for resources"
  type        = string
  default     = "us-east-1"
}

variable "environment" {
  description = "Environment name (dev, staging, prod)"
  type        = string
  default     = "dev"
  
  validation {
    condition     = contains(["dev", "staging", "prod"], var.environment)
    error_message = "Environment must be dev, staging, or prod."
  }
}

variable "kinesis_shard_count" {
  description = "Number of shards for Kinesis streams"
  type        = number
  default     = 5
}

variable "kinesis_retention_hours" {
  description = "Data retention period in hours (24-8760)"
  type        = number
  default     = 168  # 7 days
  
  validation {
    condition     = var.kinesis_retention_hours >= 24 && var.kinesis_retention_hours <= 8760
    error_message = "Retention must be between 24 and 8760 hours."
  }
}

variable "lambda_memory_size" {
  description = "Lambda function memory size in MB"
  type        = number
  default     = 512
}

variable "lambda_timeout" {
  description = "Lambda function timeout in seconds"
  type        = number
  default     = 60
}

variable "msk_instance_type" {
  description = "MSK broker instance type"
  type        = string
  default     = "kafka.m5.large"
}

variable "msk_broker_count" {
  description = "Number of MSK brokers per AZ"
  type        = number
  default     = 1
}

variable "enable_enhanced_monitoring" {
  description = "Enable enhanced monitoring for Kinesis"
  type        = bool
  default     = true
}

variable "tags" {
  description = "Additional tags for resources"
  type        = map(string)
  default     = {}
}
