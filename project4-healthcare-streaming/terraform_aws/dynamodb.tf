# DynamoDB Table for Device Registry
resource "aws_dynamodb_table" "device_registry" {
  name           = "medical-device-registry-${var.environment}"
  billing_mode   = "PAY_PER_REQUEST"
  hash_key       = "device_id"
  
  attribute {
    name = "device_id"
    type = "S"
  }
  
  attribute {
    name = "patient_id"
    type = "S"
  }
  
  global_secondary_index {
    name            = "PatientIndex"
    hash_key        = "patient_id"
    projection_type = "ALL"
  }
  
  point_in_time_recovery {
    enabled = true
  }
  
  server_side_encryption {
    enabled     = true
    kms_key_arn = aws_kms_key.dynamodb.arn
  }
  
  tags = merge(
    var.tags,
    {
      Name = "medical-device-registry-${var.environment}"
    }
  )
}

# DynamoDB Table for Patient Metadata
resource "aws_dynamodb_table" "patient_metadata" {
  name           = "medical-patient-metadata-${var.environment}"
  billing_mode   = "PAY_PER_REQUEST"
  hash_key       = "patient_id"
  
  attribute {
    name = "patient_id"
    type = "S"
  }
  
  point_in_time_recovery {
    enabled = true
  }
  
  server_side_encryption {
    enabled     = true
    kms_key_arn = aws_kms_key.dynamodb.arn
  }
  
  tags = merge(
    var.tags,
    {
      Name = "medical-patient-metadata-${var.environment}"
    }
  )
}

# DynamoDB Table for Alert History
resource "aws_dynamodb_table" "alert_history" {
  name           = "medical-alert-history-${var.environment}"
  billing_mode   = "PAY_PER_REQUEST"
  hash_key       = "alert_id"
  range_key      = "timestamp"
  
  attribute {
    name = "alert_id"
    type = "S"
  }
  
  attribute {
    name = "timestamp"
    type = "N"
  }
  
  attribute {
    name = "patient_id"
    type = "S"
  }
  
  global_secondary_index {
    name            = "PatientAlertIndex"
    hash_key        = "patient_id"
    range_key       = "timestamp"
    projection_type = "ALL"
  }
  
  ttl {
    attribute_name = "ttl"
    enabled        = true
  }
  
  point_in_time_recovery {
    enabled = true
  }
  
  server_side_encryption {
    enabled     = true
    kms_key_arn = aws_kms_key.dynamodb.arn
  }
  
  tags = merge(
    var.tags,
    {
      Name = "medical-alert-history-${var.environment}"
    }
  )
}

# KMS Key for DynamoDB Encryption
resource "aws_kms_key" "dynamodb" {
  description             = "KMS key for DynamoDB table encryption"
  deletion_window_in_days = 10
  enable_key_rotation     = true
  
  tags = merge(
    var.tags,
    {
      Name = "dynamodb-encryption-key-${var.environment}"
    }
  )
}

resource "aws_kms_alias" "dynamodb" {
  name          = "alias/dynamodb-medical-${var.environment}"
  target_key_id = aws_kms_key.dynamodb.key_id
}
