# Lambda Function for Kinesis Stream Processing
resource "aws_lambda_function" "kinesis_processor" {
  filename         = "lambda_kinesis_processor.zip"
  function_name    = "medical-kinesis-processor-${var.environment}"
  role            = aws_iam_role.lambda_kinesis.arn
  handler         = "index.lambda_handler"
  source_code_hash = fileexists("lambda_kinesis_processor.zip") ? filebase64sha256("lambda_kinesis_processor.zip") : null
  runtime         = "python3.11"
  timeout         = var.lambda_timeout
  memory_size     = var.lambda_memory_size
  
  environment {
    variables = {
      ENVIRONMENT       = var.environment
      ALERT_TOPIC_ARN   = aws_sns_topic.critical_alerts.arn
      DYNAMODB_TABLE    = aws_dynamodb_table.device_registry.name
    }
  }
  
  dead_letter_config {
    target_arn = aws_sqs_queue.lambda_dlq.arn
  }
  
  tags = var.tags
}

# Lambda Event Source Mapping for Kinesis
resource "aws_lambda_event_source_mapping" "kinesis_trigger" {
  event_source_arn  = aws_kinesis_stream.medical_devices.arn
  function_name     = aws_lambda_function.kinesis_processor.arn
  starting_position = "LATEST"
  batch_size        = 100
  maximum_batching_window_in_seconds = 5
  
  destination_config {
    on_failure {
      destination_arn = aws_sqs_queue.lambda_dlq.arn
    }
  }
}

# Lambda Function for Firehose Transformation
resource "aws_lambda_function" "firehose_transformer" {
  filename         = "lambda_firehose_transformer.zip"
  function_name    = "medical-firehose-transformer-${var.environment}"
  role            = aws_iam_role.lambda_firehose.arn
  handler         = "index.lambda_handler"
  source_code_hash = fileexists("lambda_firehose_transformer.zip") ? filebase64sha256("lambda_firehose_transformer.zip") : null
  runtime         = "python3.11"
  timeout         = 60
  memory_size     = 256
  
  tags = var.tags
}

# IAM Role for Kinesis Lambda
resource "aws_iam_role" "lambda_kinesis" {
  name = "lambda-kinesis-processor-role-${var.environment}"
  
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action = "sts:AssumeRole"
      Effect = "Allow"
      Principal = {
        Service = "lambda.amazonaws.com"
      }
    }]
  })
  
  tags = var.tags
}

resource "aws_iam_role_policy_attachment" "lambda_kinesis_basic" {
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
  role       = aws_iam_role.lambda_kinesis.name
}

resource "aws_iam_role_policy" "lambda_kinesis" {
  name = "lambda-kinesis-policy"
  role = aws_iam_role.lambda_kinesis.id
  
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "kinesis:GetRecords",
          "kinesis:GetShardIterator",
          "kinesis:DescribeStream",
          "kinesis:ListShards",
          "kinesis:ListStreams"
        ]
        Resource = aws_kinesis_stream.medical_devices.arn
      },
      {
        Effect = "Allow"
        Action = [
          "dynamodb:GetItem",
          "dynamodb:PutItem",
          "dynamodb:UpdateItem",
          "dynamodb:Query"
        ]
        Resource = aws_dynamodb_table.device_registry.arn
      },
      {
        Effect = "Allow"
        Action = ["sns:Publish"]
        Resource = aws_sns_topic.critical_alerts.arn
      },
      {
        Effect = "Allow"
        Action = ["sqs:SendMessage"]
        Resource = aws_sqs_queue.lambda_dlq.arn
      },
      {
        Effect = "Allow"
        Action = [
          "kms:Decrypt",
          "kms:GenerateDataKey"
        ]
        Resource = aws_kms_key.kinesis.arn
      }
    ]
  })
}

# IAM Role for Firehose Lambda
resource "aws_iam_role" "lambda_firehose" {
  name = "lambda-firehose-transformer-role-${var.environment}"
  
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action = "sts:AssumeRole"
      Effect = "Allow"
      Principal = {
        Service = "lambda.amazonaws.com"
      }
    }]
  })
  
  tags = var.tags
}

resource "aws_iam_role_policy_attachment" "lambda_firehose_basic" {
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
  role       = aws_iam_role.lambda_firehose.name
}

# CloudWatch Log Groups
resource "aws_cloudwatch_log_group" "lambda_kinesis" {
  name              = "/aws/lambda/${aws_lambda_function.kinesis_processor.function_name}"
  retention_in_days = 7
  
  tags = var.tags
}

resource "aws_cloudwatch_log_group" "lambda_firehose" {
  name              = "/aws/lambda/${aws_lambda_function.firehose_transformer.function_name}"
  retention_in_days = 7
  
  tags = var.tags
}

# SNS Topic for Critical Alerts
resource "aws_sns_topic" "critical_alerts" {
  name = "medical-critical-alerts-${var.environment}"
  
  tags = var.tags
}

# SQS Dead Letter Queue
resource "aws_sqs_queue" "lambda_dlq" {
  name                      = "medical-lambda-dlq-${var.environment}"
  message_retention_seconds = 1209600  # 14 days
  
  tags = var.tags
}
