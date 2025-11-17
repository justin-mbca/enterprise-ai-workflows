terraform {
  required_version = ">= 1.3.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = ">= 5.0"
    }
  }
}

provider "aws" {
  region = var.region
}

# Ubuntu 22.04 LTS (Jammy) AMD64
data "aws_ami" "ubuntu" {
  most_recent = true
  owners      = ["099720109477"] # Canonical

  filter {
    name   = "name"
    values = ["ubuntu/images/hvm-ssd/ubuntu-jammy-22.04-amd64-server-*"]
  }
}

resource "aws_security_group" "mlops" {
  name        = "mlops-sg"
  description = "Security group for MLOps stack"
  vpc_id      = data.aws_vpc.default.id

  ingress {
    description = "SSH"
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = [var.allowed_cidr]
  }

  dynamic "ingress" {
    for_each = toset([5000, 5001, 8000, 8888])
    content {
      description = "MLOps port ${ingress.value}"
      from_port   = ingress.value
      to_port     = ingress.value
      protocol    = "tcp"
      cidr_blocks = [var.allowed_cidr]
    }
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

data "aws_vpc" "default" {
  default = true
}

data "aws_subnets" "default" {
  filter {
    name   = "vpc-id"
    values = [data.aws_vpc.default.id]
  }
}

resource "aws_instance" "mlops" {
  ami                         = data.aws_ami.ubuntu.id
  instance_type               = var.instance_type
  subnet_id                   = data.aws_subnets.default.ids[0]
  vpc_security_group_ids      = [aws_security_group.mlops.id]
  key_name                    = var.key_name

  user_data = <<-EOT
  #cloud-config
  runcmd:
    - bash -lc "apt-get update -y && apt-get install -y curl"
    - bash -lc "curl -fsSL https://raw.githubusercontent.com/justin-mbca/enterprise-ai-workflows/main/project2-mlops-pipeline/deploy/cloud-deploy.sh | bash"
  EOT

  tags = {
    Name = "mlops-pipeline"
  }
}

output "public_ip" {
  value = aws_instance.mlops.public_ip
}

output "public_dns" {
  value = aws_instance.mlops.public_dns
}

output "endpoints" {
  value = {
    mlflow       = "http://${aws_instance.mlops.public_ip}:5000"
    mlflow_proxy = "http://${aws_instance.mlops.public_ip}:5001"
    jupyter      = "http://${aws_instance.mlops.public_ip}:8888"
    api_docs     = "http://${aws_instance.mlops.public_ip}:8000/docs"
  }
}
