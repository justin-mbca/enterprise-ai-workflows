# Outputs

output "kinesis_stream_names" {
  description = "Names of Kinesis streams"
  value = {
    devices = aws_kinesis_stream.medical_devices.name
    alerts  = aws_kinesis_stream.medical_alerts.name
  }
}

output "kinesis_stream_arns" {
  description = "ARNs of Kinesis streams"
  value = {
    devices = aws_kinesis_stream.medical_devices.arn
    alerts  = aws_kinesis_stream.medical_alerts.arn
  }
}

output "s3_bucket_names" {
  description = "S3 bucket names"
  value = {
    raw_data       = aws_s3_bucket.raw_data.id
    processed_data = aws_s3_bucket.processed_data.id
  }
}

output "dynamodb_table_names" {
  description = "DynamoDB table names"
  value = {
    device_registry  = aws_dynamodb_table.device_registry.name
    patient_metadata = aws_dynamodb_table.patient_metadata.name
    alert_history    = aws_dynamodb_table.alert_history.name
  }
}

output "lambda_function_arns" {
  description = "Lambda function ARNs"
  value = {
    kinesis_processor     = aws_lambda_function.kinesis_processor.arn
    firehose_transformer  = aws_lambda_function.firehose_transformer.arn
  }
}

output "sns_topic_arn" {
  description = "SNS topic ARN for critical alerts"
  value       = aws_sns_topic.critical_alerts.arn
}

output "cloudwatch_log_groups" {
  description = "CloudWatch log group names"
  value = {
    firehose          = aws_cloudwatch_log_group.firehose.name
    lambda_kinesis    = aws_cloudwatch_log_group.lambda_kinesis.name
    lambda_firehose   = aws_cloudwatch_log_group.lambda_firehose.name
  }
}
