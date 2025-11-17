variable "region" {
  description = "AWS region"
  type        = string
  default     = "us-east-1"
}

variable "instance_type" {
  description = "EC2 instance type"
  type        = string
  default     = "t3.small"
}

variable "key_name" {
  description = "EC2 Key Pair name for SSH access"
  type        = string
}

variable "allowed_cidr" {
  description = "CIDR allowed to access exposed ports (22,5000,5001,8000,8888)"
  type        = string
  default     = "0.0.0.0/0"
}
