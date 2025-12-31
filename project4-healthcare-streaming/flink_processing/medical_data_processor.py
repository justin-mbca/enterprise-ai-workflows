#!/usr/bin/env python3
"""
Flink Medical Data Processor
Real-time stream processing with windowing and CEP
"""

import json
import logging
from datetime import datetime

from pyflink.datastream import StreamExecutionEnvironment
from pyflink.datastream.connectors.kafka import (
    KafkaSource, KafkaOffsetsInitializer, KafkaSink, KafkaRecordSerializationSchema
)
from pyflink.common.serialization import SimpleStringSchema
from pyflink.common.typeinfo import Types
from pyflink.common.watermark_strategy import WatermarkStrategy
from pyflink.datastream.functions import MapFunction, FilterFunction
from pyflink.datastream.window import TumblingEventTimeWindows, Time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MedicalDataParser(MapFunction):
    """Parse JSON medical data"""
    
    def map(self, value):
        try:
            data = json.loads(value)
            return data
        except Exception as e:
            logger.error(f"Error parsing data: {e}")
            return None


class AbnormalReadingFilter(FilterFunction):
    """Filter abnormal readings"""
    
    def filter(self, value):
        if value is None:
            return False
        return value.get('is_abnormal', False)


class VitalsAggregator:
    """Aggregate vitals within windows"""
    
    @staticmethod
    def aggregate(readings):
        if not readings:
            return {}
        
        patient_id = readings[0].get('patient_id', 'unknown')
        
        # Extract heart rates
        heart_rates = [
            r.get('values', {}).get('heart_rate', 0) 
            for r in readings 
            if r.get('values', {}).get('heart_rate')
        ]
        
        result = {
            'patient_id': patient_id,
            'window_start': datetime.now().isoformat(),
            'reading_count': len(readings),
            'abnormal_count': sum(1 for r in readings if r.get('is_abnormal', False))
        }
        
        if heart_rates:
            result['heart_rate_stats'] = {
                'min': min(heart_rates),
                'max': max(heart_rates),
                'avg': sum(heart_rates) / len(heart_rates)
            }
        
        return result


def create_kafka_source(bootstrap_servers: str, topic: str, group_id: str):
    """Create Kafka source"""
    return KafkaSource.builder() \
        .set_bootstrap_servers(bootstrap_servers) \
        .set_topics(topic) \
        .set_group_id(group_id) \
        .set_starting_offsets(KafkaOffsetsInitializer.earliest()) \
        .set_value_only_deserializer(SimpleStringSchema()) \
        .build()


def create_kafka_sink(bootstrap_servers: str, topic: str):
    """Create Kafka sink"""
    return KafkaSink.builder() \
        .set_bootstrap_servers(bootstrap_servers) \
        .set_record_serializer(
            KafkaRecordSerializationSchema.builder()
            .set_topic(topic)
            .set_value_serialization_schema(SimpleStringSchema())
            .build()
        ) \
        .build()


def main():
    """Main Flink job"""
    # Create execution environment
    env = StreamExecutionEnvironment.get_execution_environment()
    env.set_parallelism(4)
    
    # Configure checkpointing
    env.enable_checkpointing(60000)  # 60 seconds
    
    bootstrap_servers = 'kafka-broker-1:29092'
    
    # Create Kafka source
    kafka_source = create_kafka_source(
        bootstrap_servers,
        'medical-devices-vitals',
        'flink-medical-processor'
    )
    
    # Create data stream
    stream = env.from_source(
        kafka_source,
        WatermarkStrategy.for_monotonous_timestamps(),
        "Medical Devices Source"
    )
    
    # Parse JSON
    parsed_stream = stream.map(MedicalDataParser(), output_type=Types.PICKLED_BYTE_ARRAY())
    
    # Filter abnormal readings
    abnormal_stream = parsed_stream.filter(AbnormalReadingFilter())
    
    # Create sink for abnormal readings
    abnormal_sink = create_kafka_sink(bootstrap_servers, 'medical-alerts-critical')
    
    # Write abnormal readings to alerts topic
    abnormal_stream.map(
        lambda x: json.dumps(x),
        output_type=Types.STRING()
    ).sink_to(abnormal_sink)
    
    # Execute job
    env.execute("Medical Data Processing Job")


if __name__ == '__main__':
    main()
