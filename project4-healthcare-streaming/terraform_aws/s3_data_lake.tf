# S3 Bucket for Raw Data
resource "aws_s3_bucket" "raw_data" {
  bucket = "medical-streaming-raw-data-${var.environment}-${data.aws_caller_identity.current.account_id}"
  
  tags = merge(
    var.tags,
    {
      Name = "medical-raw-data-${var.environment}"
      DataClassification = "PHI"
    }
  )
}

# Enable versioning
resource "aws_s3_bucket_versioning" "raw_data" {
  bucket = aws_s3_bucket.raw_data.id
  
  versioning_configuration {
    status = "Enabled"
  }
}

# Server-side encryption
resource "aws_s3_bucket_server_side_encryption_configuration" "raw_data" {
  bucket = aws_s3_bucket.raw_data.id
  
  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm     = "aws:kms"
      kms_master_key_id = aws_kms_key.s3.id
    }
    bucket_key_enabled = true
  }
}

# Block public access
resource "aws_s3_bucket_public_access_block" "raw_data" {
  bucket = aws_s3_bucket.raw_data.id
  
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# Lifecycle policy
resource "aws_s3_bucket_lifecycle_configuration" "raw_data" {
  bucket = aws_s3_bucket.raw_data.id
  
  rule {
    id     = "transition-to-glacier"
    status = "Enabled"
    
    transition {
      days          = 90
      storage_class = "GLACIER"
    }
    
    expiration {
      days = 2555  # 7 years (7 * 365) for HIPAA compliance
    }
  }
}

# S3 Bucket for Processed Data
resource "aws_s3_bucket" "processed_data" {
  bucket = "medical-streaming-processed-${var.environment}-${data.aws_caller_identity.current.account_id}"
  
  tags = merge(
    var.tags,
    {
      Name = "medical-processed-data-${var.environment}"
    }
  )
}

resource "aws_s3_bucket_versioning" "processed_data" {
  bucket = aws_s3_bucket.processed_data.id
  
  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "processed_data" {
  bucket = aws_s3_bucket.processed_data.id
  
  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm     = "aws:kms"
      kms_master_key_id = aws_kms_key.s3.id
    }
    bucket_key_enabled = true
  }
}

resource "aws_s3_bucket_public_access_block" "processed_data" {
  bucket = aws_s3_bucket.processed_data.id
  
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# KMS Key for S3 Encryption
resource "aws_kms_key" "s3" {
  description             = "KMS key for S3 bucket encryption"
  deletion_window_in_days = 10
  enable_key_rotation     = true
  
  tags = merge(
    var.tags,
    {
      Name = "s3-encryption-key-${var.environment}"
    }
  )
}

resource "aws_kms_alias" "s3" {
  name          = "alias/s3-medical-${var.environment}"
  target_key_id = aws_kms_key.s3.key_id
}
