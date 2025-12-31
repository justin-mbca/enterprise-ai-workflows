# Kinesis Data Streams

resource "aws_kinesis_stream" "medical_devices" {
  name             = "medical-devices-stream-${var.environment}"
  shard_count      = var.kinesis_shard_count
  retention_period = var.kinesis_retention_hours
  
  shard_level_metrics = var.enable_enhanced_monitoring ? [
    "IncomingBytes",
    "IncomingRecords",
    "OutgoingBytes",
    "OutgoingRecords",
    "WriteProvisionedThroughputExceeded",
    "ReadProvisionedThroughputExceeded",
    "IteratorAgeMilliseconds"
  ] : []
  
  encryption_type = "KMS"
  kms_key_id      = aws_kms_key.kinesis.id
  
  tags = merge(
    var.tags,
    {
      Name = "medical-devices-stream-${var.environment}"
    }
  )
}

resource "aws_kinesis_stream" "medical_alerts" {
  name             = "medical-alerts-stream-${var.environment}"
  shard_count      = 2
  retention_period = var.kinesis_retention_hours
  
  encryption_type = "KMS"
  kms_key_id      = aws_kms_key.kinesis.id
  
  tags = merge(
    var.tags,
    {
      Name = "medical-alerts-stream-${var.environment}"
    }
  )
}

# KMS Key for Kinesis Encryption
resource "aws_kms_key" "kinesis" {
  description             = "KMS key for Kinesis stream encryption"
  deletion_window_in_days = 10
  enable_key_rotation     = true
  
  tags = merge(
    var.tags,
    {
      Name = "kinesis-encryption-key-${var.environment}"
    }
  )
}

resource "aws_kms_alias" "kinesis" {
  name          = "alias/kinesis-${var.environment}"
  target_key_id = aws_kms_key.kinesis.key_id
}

# Kinesis Data Firehose

resource "aws_kinesis_firehose_delivery_stream" "medical_data_to_s3" {
  name        = "medical-data-to-s3-${var.environment}"
  destination = "extended_s3"
  
  kinesis_source_configuration {
    kinesis_stream_arn = aws_kinesis_stream.medical_devices.arn
    role_arn           = aws_iam_role.firehose.arn
  }
  
  extended_s3_configuration {
    role_arn   = aws_iam_role.firehose.arn
    bucket_arn = aws_s3_bucket.raw_data.arn
    prefix     = "medical-devices/year=!{timestamp:yyyy}/month=!{timestamp:MM}/day=!{timestamp:dd}/"
    error_output_prefix = "errors/medical-devices/!{firehose:error-output-type}/year=!{timestamp:yyyy}/month=!{timestamp:MM}/day=!{timestamp:dd}/"
    
    buffering_size     = 5  # MB
    buffering_interval = 300  # seconds (5 minutes)
    compression_format = "GZIP"
    
    cloudwatch_logging_options {
      enabled         = true
      log_group_name  = aws_cloudwatch_log_group.firehose.name
      log_stream_name = "medical-data-delivery"
    }
    
    processing_configuration {
      enabled = true
      
      processors {
        type = "Lambda"
        
        parameters {
          parameter_name  = "LambdaArn"
          parameter_value = "${aws_lambda_function.firehose_transformer.arn}:$LATEST"
        }
      }
    }
  }
  
  tags = var.tags
}

# CloudWatch Log Group for Firehose
resource "aws_cloudwatch_log_group" "firehose" {
  name              = "/aws/kinesisfirehose/medical-data-${var.environment}"
  retention_in_days = 7
  
  tags = var.tags
}

# IAM Role for Firehose
resource "aws_iam_role" "firehose" {
  name = "firehose-medical-data-role-${var.environment}"
  
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action = "sts:AssumeRole"
      Effect = "Allow"
      Principal = {
        Service = "firehose.amazonaws.com"
      }
    }]
  })
  
  tags = var.tags
}

resource "aws_iam_role_policy" "firehose" {
  name = "firehose-policy"
  role = aws_iam_role.firehose.id
  
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "s3:AbortMultipartUpload",
          "s3:GetBucketLocation",
          "s3:GetObject",
          "s3:ListBucket",
          "s3:ListBucketMultipartUploads",
          "s3:PutObject"
        ]
        Resource = [
          aws_s3_bucket.raw_data.arn,
          "${aws_s3_bucket.raw_data.arn}/*"
        ]
      },
      {
        Effect = "Allow"
        Action = [
          "kinesis:DescribeStream",
          "kinesis:GetShardIterator",
          "kinesis:GetRecords",
          "kinesis:ListShards"
        ]
        Resource = aws_kinesis_stream.medical_devices.arn
      },
      {
        Effect = "Allow"
        Action = [
          "kms:Decrypt",
          "kms:GenerateDataKey"
        ]
        Resource = aws_kms_key.kinesis.arn
      },
      {
        Effect = "Allow"
        Action = [
          "logs:PutLogEvents"
        ]
        Resource = "${aws_cloudwatch_log_group.firehose.arn}:*"
      },
      {
        Effect = "Allow"
        Action = [
          "lambda:InvokeFunction"
        ]
        Resource = aws_lambda_function.firehose_transformer.arn
      }
    ]
  })
}
