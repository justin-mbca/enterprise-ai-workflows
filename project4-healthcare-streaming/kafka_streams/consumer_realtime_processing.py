#!/usr/bin/env python3
"""
Real-time Medical Data Consumer
Processes medical device data from Kafka with validation and alerting
"""

import json
import logging
import signal
import sys
from datetime import datetime, timezone
from typing import Dict, List, Set, Tuple
import argparse

from kafka import KafkaConsumer
from kafka.errors import KafkaError
import psycopg2
from psycopg2.extras import execute_batch

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class MedicalDataConsumer:
    """Real-time consumer for medical device data"""
    
    def __init__(
        self,
        bootstrap_servers: str = 'localhost:9092',
        group_id: str = 'medical-realtime-processor',
        topics: List[str] = None,
        postgres_config: Dict = None
    ):
        """Initialize the consumer"""
        self.bootstrap_servers = bootstrap_servers
        self.group_id = group_id
        self.topics = topics or [
            'medical-devices-ecg',
            'medical-devices-glucose',
            'medical-devices-vitals'
        ]
        self.consumer = None
        self.db_conn = None
        self.db_cursor = None
        self.postgres_config = postgres_config or {
            'host': 'localhost',
            'port': 5433,
            'database': 'timeseries_medical',
            'user': 'postgres',
            'password': 'postgres'
        }
        
        self.metrics = {
            'messages_processed': 0,
            'messages_invalid': 0,
            'alerts_triggered': 0
        }
        
        self.running = True
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        logger.info("Shutdown signal received, closing consumer...")
        self.running = False
    
    def connect_kafka(self):
        """Connect to Kafka"""
        try:
            self.consumer = KafkaConsumer(
                *self.topics,
                bootstrap_servers=self.bootstrap_servers,
                group_id=self.group_id,
                auto_offset_reset='earliest',
                enable_auto_commit=False,
                value_deserializer=lambda m: json.loads(m.decode('utf-8')),
                key_deserializer=lambda k: k.decode('utf-8') if k else None,
                max_poll_records=100,
                session_timeout_ms=30000,
                heartbeat_interval_ms=10000
            )
            logger.info(f"Connected to Kafka, subscribed to: {self.topics}")
        except Exception as e:
            logger.error(f"Failed to connect to Kafka: {e}")
            raise
    
    def connect_database(self):
        """Connect to TimescaleDB"""
        try:
            self.db_conn = psycopg2.connect(**self.postgres_config)
            self.db_cursor = self.db_conn.cursor()
            self._create_tables()
            logger.info("Connected to TimescaleDB")
        except Exception as e:
            logger.error(f"Failed to connect to database: {e}")
            raise
    
    def _create_tables(self):
        """Create necessary tables if they don't exist"""
        create_table_sql = """
        CREATE TABLE IF NOT EXISTS medical_readings (
            time TIMESTAMPTZ NOT NULL,
            patient_id TEXT NOT NULL,
            device_id TEXT NOT NULL,
            device_type TEXT NOT NULL,
            measurement_type TEXT NOT NULL,
            values JSONB NOT NULL,
            unit TEXT,
            is_abnormal BOOLEAN DEFAULT FALSE,
            metadata JSONB,
            PRIMARY KEY (time, patient_id, device_id)
        );
        
        SELECT create_hypertable('medical_readings', 'time', 
            if_not_exists => TRUE,
            chunk_time_interval => INTERVAL '1 day'
        );
        
        CREATE INDEX IF NOT EXISTS idx_patient_id ON medical_readings(patient_id, time DESC);
        CREATE INDEX IF NOT EXISTS idx_device_type ON medical_readings(device_type, time DESC);
        CREATE INDEX IF NOT EXISTS idx_abnormal ON medical_readings(is_abnormal, time DESC) WHERE is_abnormal = TRUE;
        """
        
        try:
            self.db_cursor.execute(create_table_sql)
            self.db_conn.commit()
            logger.info("Database tables verified/created")
        except Exception as e:
            logger.error(f"Error creating tables: {e}")
            self.db_conn.rollback()
    
    def validate_reading(self, reading: Dict) -> Tuple[bool, List[str]]:
        """
        Validate medical reading
        
        Returns:
            (is_valid, errors)
        """
        errors = []
        
        # Required fields
        required_fields = ['device_id', 'device_type', 'patient_id', 'timestamp', 'values']
        for field in required_fields:
            if field not in reading:
                errors.append(f"Missing required field: {field}")
        
        # Validate timestamp
        if 'timestamp' in reading:
            try:
                datetime.fromisoformat(reading['timestamp'].replace('Z', '+00:00'))
            except (ValueError, AttributeError):
                errors.append(f"Invalid timestamp format: {reading.get('timestamp')}")
        
        # Validate values
        if 'values' in reading and not isinstance(reading['values'], dict):
            errors.append("'values' must be a dictionary")
        
        # Device-specific validation
        if reading.get('device_type') == 'ECG':
            if 'values' in reading and 'heart_rate' in reading['values']:
                hr = reading['values']['heart_rate']
                if not (20 <= hr <= 250):
                    errors.append(f"Heart rate out of valid range: {hr}")
        
        elif reading.get('device_type') in ['GLUCOSE_METER', 'CGM']:
            if 'values' in reading and 'glucose_level' in reading['values']:
                glucose = reading['values']['glucose_level']
                if not (20 <= glucose <= 600):
                    errors.append(f"Glucose level out of valid range: {glucose}")
        
        return len(errors) == 0, errors
    
    def check_critical_alerts(self, reading: Dict) -> List[Dict]:
        """Check for critical conditions requiring immediate attention"""
        alerts = []
        
        if reading.get('device_type') == 'ECG':
            hr = reading.get('values', {}).get('heart_rate', 0)
            if hr < 40 or hr > 150:
                alerts.append({
                    'alert_type': 'CRITICAL_HEART_RATE',
                    'severity': 'CRITICAL',
                    'message': f"Heart rate critically {'low' if hr < 40 else 'high'}: {hr} bpm",
                    'value': hr,
                    'threshold': '40-150 bpm'
                })
            
            rhythm = reading.get('values', {}).get('rhythm', '')
            if rhythm in ['AFIB', 'VTACH']:
                alerts.append({
                    'alert_type': 'CRITICAL_RHYTHM',
                    'severity': 'CRITICAL',
                    'message': f"Dangerous cardiac rhythm detected: {rhythm}",
                    'value': rhythm
                })
        
        elif reading.get('device_type') in ['GLUCOSE_METER', 'CGM']:
            glucose = reading.get('values', {}).get('glucose_level', 0)
            if glucose < 54:
                alerts.append({
                    'alert_type': 'SEVERE_HYPOGLYCEMIA',
                    'severity': 'CRITICAL',
                    'message': f"Severe hypoglycemia: {glucose} mg/dL",
                    'value': glucose,
                    'threshold': '< 54 mg/dL'
                })
            elif glucose > 250:
                alerts.append({
                    'alert_type': 'SEVERE_HYPERGLYCEMIA',
                    'severity': 'HIGH',
                    'message': f"Severe hyperglycemia: {glucose} mg/dL",
                    'value': glucose,
                    'threshold': '> 250 mg/dL'
                })
        
        elif reading.get('device_type') in ['BP_MONITOR', 'VITALS']:
            bp = reading.get('values', {}).get('blood_pressure', {})
            systolic = bp.get('systolic', 0)
            diastolic = bp.get('diastolic', 0)
            
            if systolic >= 180 or diastolic >= 120:
                alerts.append({
                    'alert_type': 'HYPERTENSIVE_CRISIS',
                    'severity': 'CRITICAL',
                    'message': f"Hypertensive crisis: {systolic}/{diastolic} mmHg",
                    'value': {'systolic': systolic, 'diastolic': diastolic},
                    'threshold': '180/120 mmHg'
                })
            
            spo2 = reading.get('values', {}).get('spo2', 100)
            if spo2 < 90:
                alerts.append({
                    'alert_type': 'LOW_OXYGEN',
                    'severity': 'HIGH',
                    'message': f"Low oxygen saturation: {spo2}%",
                    'value': spo2,
                    'threshold': '< 90%'
                })
        
        return alerts
    
    def store_reading(self, reading: Dict):
        """Store reading to TimescaleDB"""
        try:
            insert_sql = """
            INSERT INTO medical_readings 
            (time, patient_id, device_id, device_type, measurement_type, values, unit, is_abnormal, metadata)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (time, patient_id, device_id) DO NOTHING
            """
            
            timestamp = datetime.fromisoformat(reading['timestamp'].replace('Z', '+00:00'))
            
            self.db_cursor.execute(insert_sql, (
                timestamp,
                reading['patient_id'],
                reading['device_id'],
                reading['device_type'],
                reading.get('measurement_type', reading['device_type']),
                json.dumps(reading['values']),
                reading.get('unit'),
                reading.get('is_abnormal', False),
                json.dumps(reading.get('metadata', {}))
            ))
            
        except Exception as e:
            logger.error(f"Error storing reading: {e}")
            raise
    
    def process_message(self, message):
        """Process a single message"""
        try:
            reading = message.value
            
            # Validate
            is_valid, errors = self.validate_reading(reading)
            if not is_valid:
                logger.warning(f"Invalid reading: {errors}")
                self.metrics['messages_invalid'] += 1
                return
            
            # Check for alerts
            alerts = self.check_critical_alerts(reading)
            if alerts:
                for alert in alerts:
                    logger.warning(
                        f"ALERT: {alert['message']} - "
                        f"Patient: {reading['patient_id']}, "
                        f"Device: {reading['device_id']}"
                    )
                    self.metrics['alerts_triggered'] += 1
            
            # Store to database
            self.store_reading(reading)
            
            self.metrics['messages_processed'] += 1
            
            # Log progress
            if self.metrics['messages_processed'] % 100 == 0:
                logger.info(
                    f"Processed: {self.metrics['messages_processed']}, "
                    f"Invalid: {self.metrics['messages_invalid']}, "
                    f"Alerts: {self.metrics['alerts_triggered']}"
                )
        
        except Exception as e:
            logger.error(f"Error processing message: {e}")
    
    def run(self):
        """Run the consumer"""
        if not self.consumer:
            self.connect_kafka()
        if not self.db_conn:
            self.connect_database()
        
        logger.info("Starting consumer...")
        
        try:
            while self.running:
                # Poll for messages
                message_batch = self.consumer.poll(timeout_ms=1000)
                
                if not message_batch:
                    continue
                
                # Process batch
                for topic_partition, messages in message_batch.items():
                    for message in messages:
                        self.process_message(message)
                
                # Commit after successful processing
                try:
                    self.db_conn.commit()
                    self.consumer.commit()
                except Exception as e:
                    logger.error(f"Error committing: {e}")
                    self.db_conn.rollback()
        
        except Exception as e:
            logger.error(f"Consumer error: {e}")
        finally:
            self.close()
    
    def close(self):
        """Close connections"""
        logger.info("Closing consumer...")
        
        if self.consumer:
            self.consumer.close()
        
        if self.db_cursor:
            self.db_cursor.close()
        
        if self.db_conn:
            self.db_conn.commit()
            self.db_conn.close()
        
        logger.info(
            f"Consumer closed. Final metrics: "
            f"processed={self.metrics['messages_processed']}, "
            f"invalid={self.metrics['messages_invalid']}, "
            f"alerts={self.metrics['alerts_triggered']}"
        )


def main():
    parser = argparse.ArgumentParser(description='Medical Data Real-time Consumer')
    parser.add_argument(
        '--bootstrap-servers',
        default='localhost:9092',
        help='Kafka bootstrap servers'
    )
    parser.add_argument(
        '--group-id',
        default='medical-realtime-processor',
        help='Consumer group ID'
    )
    parser.add_argument(
        '--db-host',
        default='localhost',
        help='Database host'
    )
    parser.add_argument(
        '--db-port',
        type=int,
        default=5433,
        help='Database port'
    )
    
    args = parser.parse_args()
    
    postgres_config = {
        'host': args.db_host,
        'port': args.db_port,
        'database': 'timeseries_medical',
        'user': 'postgres',
        'password': 'postgres'
    }
    
    consumer = MedicalDataConsumer(
        bootstrap_servers=args.bootstrap_servers,
        group_id=args.group_id,
        postgres_config=postgres_config
    )
    
    consumer.run()


if __name__ == '__main__':
    main()
