#!/bin/bash
# Spark Submit Configuration Script

SPARK_HOME=${SPARK_HOME:-/opt/spark}

$SPARK_HOME/bin/spark-submit \
  --master spark://spark-master:7077 \
  --deploy-mode client \
  --driver-memory 2g \
  --executor-memory 2g \
  --executor-cores 2 \
  --num-executors 2 \
  --packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.0 \
  --conf spark.sql.streaming.checkpointLocation=/tmp/spark-checkpoints \
  --conf spark.sql.adaptive.enabled=true \
  --conf spark.sql.shuffle.partitions=10 \
  --conf spark.streaming.kafka.consumer.cache.enabled=false \
  --conf spark.sql.streaming.metricsEnabled=true \
  structured_streaming_hl7.py
