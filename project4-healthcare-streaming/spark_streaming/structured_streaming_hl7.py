#!/usr/bin/env python3
"""
Spark Structured Streaming for HL7 Messages
Process HL7 v2.x messages from Kafka in real-time
"""

import json
import logging
from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col, udf, window, current_timestamp
from pyspark.sql.types import StructType, StructField, StringType, TimestampType, BooleanType, MapType

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Define HL7 message schema
hl7_schema = StructType([
    StructField("message", StringType(), True),
    StructField("patient_id", StringType(), True),
    StructField("timestamp", StringType(), True)
])

# Define medical reading schema
reading_schema = StructType([
    StructField("device_id", StringType(), True),
    StructField("device_type", StringType(), True),
    StructField("patient_id", StringType(), True),
    StructField("timestamp", StringType(), True),
    StructField("measurement_type", StringType(), True),
    StructField("values", MapType(StringType(), StringType()), True),
    StructField("unit", StringType(), True),
    StructField("is_abnormal", BooleanType(), True)
])


def parse_hl7_message(hl7_string: str) -> dict:
    """Parse HL7 v2.x message"""
    if not hl7_string:
        return {}
    
    try:
        segments = hl7_string.split('\r')
        result = {}
        
        for segment in segments:
            if not segment:
                continue
            
            fields = segment.split('|')
            segment_type = fields[0]
            
            if segment_type == 'MSH':
                result['message_type'] = fields[8] if len(fields) > 8 else ''
                result['message_timestamp'] = fields[6] if len(fields) > 6 else ''
            elif segment_type == 'PID':
                result['patient_id'] = fields[3] if len(fields) > 3 else ''
                result['patient_name'] = fields[5] if len(fields) > 5 else ''
            elif segment_type == 'OBR':
                result['observation_id'] = fields[2] if len(fields) > 2 else ''
            elif segment_type == 'OBX':
                result['observation_value'] = fields[5] if len(fields) > 5 else ''
        
        return result
    except Exception as e:
        logger.error(f"Error parsing HL7 message: {e}")
        return {}


# Register UDF
parse_hl7_udf = udf(parse_hl7_message, MapType(StringType(), StringType()))


def create_spark_session():
    """Create Spark session with Kafka support"""
    return SparkSession.builder \
        .appName("HL7 Streaming Processor") \
        .config("spark.sql.streaming.checkpointLocation", "/tmp/spark-checkpoints/hl7-processor") \
        .config("spark.jars.packages", "org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.0") \
        .config("spark.sql.adaptive.enabled", "true") \
        .config("spark.sql.shuffle.partitions", "10") \
        .getOrCreate()


def main():
    """Main Spark Structured Streaming job"""
    spark = create_spark_session()
    spark.sparkContext.setLogLevel("WARN")
    
    # Read from Kafka
    df = spark \
        .readStream \
        .format("kafka") \
        .option("kafka.bootstrap.servers", "localhost:9092") \
        .option("subscribe", "hl7-messages-raw") \
        .option("startingOffsets", "latest") \
        .option("failOnDataLoss", "false") \
        .load()
    
    # Parse Kafka message value
    parsed_df = df.selectExpr("CAST(key AS STRING)", "CAST(value AS STRING)") \
        .select(from_json(col("value"), hl7_schema).alias("data")) \
        .select("data.*")
    
    # Parse HL7 message
    hl7_parsed_df = parsed_df.withColumn("parsed_hl7", parse_hl7_udf(col("message")))
    
    # Extract fields
    processed_df = hl7_parsed_df.select(
        col("patient_id"),
        col("parsed_hl7.message_type").alias("message_type"),
        col("parsed_hl7.observation_value").alias("observation_value"),
        col("timestamp").cast(TimestampType()).alias("event_time"),
        current_timestamp().alias("processing_time")
    )
    
    # Write to console (for demonstration)
    query = processed_df \
        .writeStream \
        .outputMode("append") \
        .format("console") \
        .option("truncate", "false") \
        .start()
    
    # Also write to Kafka (processed topic)
    kafka_query = processed_df.selectExpr(
        "patient_id as key",
        "to_json(struct(*)) as value"
    ) \
        .writeStream \
        .format("kafka") \
        .option("kafka.bootstrap.servers", "localhost:9092") \
        .option("topic", "medical-processed-hl7") \
        .option("checkpointLocation", "/tmp/spark-checkpoints/hl7-kafka-sink") \
        .start()
    
    # Await termination
    query.awaitTermination()
    kafka_query.awaitTermination()


if __name__ == "__main__":
    main()
