#!/usr/bin/env python3
"""
Stream Aggregation with Kafka Streams
Windowed aggregations for medical device data
"""

import json
import logging
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from typing import Dict, List
import argparse

from kafka import KafkaConsumer, KafkaProducer
from kafka.errors import KafkaError

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class StreamAggregator:
    """Windowed aggregations for medical vitals"""
    
    def __init__(self, bootstrap_servers: str = 'localhost:9092'):
        self.bootstrap_servers = bootstrap_servers
        self.consumer = None
        self.producer = None
        
        # Window state (in-memory for simplicity)
        self.windows = defaultdict(lambda: defaultdict(list))
        self.window_size = timedelta(minutes=5)
        
    def connect(self):
        """Connect to Kafka"""
        self.consumer = KafkaConsumer(
            'medical-devices-vitals',
            'medical-devices-glucose',
            'medical-devices-ecg',
            bootstrap_servers=self.bootstrap_servers,
            group_id='medical-aggregator',
            auto_offset_reset='earliest',
            value_deserializer=lambda m: json.loads(m.decode('utf-8'))
        )
        
        self.producer = KafkaProducer(
            bootstrap_servers=self.bootstrap_servers,
            value_serializer=lambda v: json.dumps(v).encode('utf-8'),
            acks='all'
        )
        
        logger.info("Connected to Kafka")
    
    def aggregate_vitals(self, patient_id: str, readings: List[Dict]) -> Dict:
        """Aggregate vitals for a patient"""
        if not readings:
            return {}
        
        aggregated = {
            'patient_id': patient_id,
            'window_start': min(r['timestamp'] for r in readings),
            'window_end': max(r['timestamp'] for r in readings),
            'reading_count': len(readings),
            'abnormal_count': sum(1 for r in readings if r.get('is_abnormal', False))
        }
        
        # Aggregate heart rates
        heart_rates = [r['values'].get('heart_rate') for r in readings 
                      if 'heart_rate' in r.get('values', {})]
        if heart_rates:
            aggregated['heart_rate'] = {
                'min': min(heart_rates),
                'max': max(heart_rates),
                'avg': sum(heart_rates) / len(heart_rates),
                'count': len(heart_rates)
            }
        
        # Aggregate blood pressure
        bp_readings = [r['values'].get('blood_pressure') for r in readings 
                       if 'blood_pressure' in r.get('values', {})]
        if bp_readings:
            systolic = [bp['systolic'] for bp in bp_readings if 'systolic' in bp]
            diastolic = [bp['diastolic'] for bp in bp_readings if 'diastolic' in bp]
            
            if systolic:
                aggregated['blood_pressure'] = {
                    'systolic': {'min': min(systolic), 'max': max(systolic), 
                                'avg': sum(systolic) / len(systolic)},
                    'diastolic': {'min': min(diastolic), 'max': max(diastolic), 
                                 'avg': sum(diastolic) / len(diastolic)}
                }
        
        # Aggregate glucose
        glucose_readings = [r['values'].get('glucose_level') for r in readings 
                           if 'glucose_level' in r.get('values', {})]
        if glucose_readings:
            aggregated['glucose'] = {
                'min': min(glucose_readings),
                'max': max(glucose_readings),
                'avg': sum(glucose_readings) / len(glucose_readings),
                'count': len(glucose_readings)
            }
        
        return aggregated
    
    def process_windows(self):
        """Process completed windows"""
        current_time = datetime.now(timezone.utc)
        completed_windows = []
        
        for window_key, patient_data in list(self.windows.items()):
            window_start = datetime.fromisoformat(window_key)
            
            if current_time - window_start > self.window_size:
                completed_windows.append((window_key, patient_data))
                del self.windows[window_key]
        
        # Aggregate and send results
        for window_key, patient_data in completed_windows:
            for patient_id, readings in patient_data.items():
                aggregated = self.aggregate_vitals(patient_id, readings)
                
                if aggregated:
                    self.producer.send(
                        'medical-aggregated-vitals',
                        key=patient_id.encode('utf-8'),
                        value=aggregated
                    )
                    logger.info(f"Sent aggregation for {patient_id}: {aggregated['reading_count']} readings")
    
    def run(self):
        """Run the aggregator"""
        if not self.consumer:
            self.connect()
        
        logger.info("Starting stream aggregator...")
        
        try:
            for message in self.consumer:
                reading = message.value
                
                # Determine window
                timestamp = datetime.fromisoformat(reading['timestamp'].replace('Z', '+00:00'))
                window_start = timestamp.replace(minute=(timestamp.minute // 5) * 5, 
                                                 second=0, microsecond=0)
                window_key = window_start.isoformat()
                
                # Add to window
                patient_id = reading['patient_id']
                self.windows[window_key][patient_id].append(reading)
                
                # Process completed windows periodically
                if len(self.windows) > 10:
                    self.process_windows()
        
        except KeyboardInterrupt:
            logger.info("Aggregator interrupted")
        finally:
            self.close()
    
    def close(self):
        """Close connections"""
        if self.producer:
            self.producer.flush()
            self.producer.close()
        if self.consumer:
            self.consumer.close()


def main():
    parser = argparse.ArgumentParser(description='Stream Aggregator')
    parser.add_argument(
        '--bootstrap-servers',
        default='localhost:9092',
        help='Kafka bootstrap servers'
    )
    
    args = parser.parse_args()
    
    aggregator = StreamAggregator(bootstrap_servers=args.bootstrap_servers)
    aggregator.run()


if __name__ == '__main__':
    main()
