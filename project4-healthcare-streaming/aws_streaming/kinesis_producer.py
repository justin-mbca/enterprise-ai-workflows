#!/usr/bin/env python3
"""
AWS Kinesis Producer for Medical Device Data
"""

import json
import logging
import time
import random
from datetime import datetime, timezone
import argparse

import boto3
from botocore.exceptions import ClientError

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class KinesisProducer:
    """Kinesis Data Streams producer for medical devices"""
    
    def __init__(self, stream_name: str, region: str = 'us-east-1'):
        self.stream_name = stream_name
        self.kinesis_client = boto3.client('kinesis', region_name=region)
        self.metrics = {'records_sent': 0, 'records_failed': 0}
    
    def put_record(self, data: dict, partition_key: str):
        """Put a single record to Kinesis"""
        try:
            response = self.kinesis_client.put_record(
                StreamName=self.stream_name,
                Data=json.dumps(data),
                PartitionKey=partition_key
            )
            self.metrics['records_sent'] += 1
            return response
        except ClientError as e:
            logger.error(f"Error putting record: {e}")
            self.metrics['records_failed'] += 1
            raise
    
    def put_records_batch(self, records: list):
        """Put multiple records in batch"""
        try:
            response = self.kinesis_client.put_records(
                StreamName=self.stream_name,
                Records=records
            )
            
            failed_count = response.get('FailedRecordCount', 0)
            success_count = len(records) - failed_count
            
            self.metrics['records_sent'] += success_count
            self.metrics['records_failed'] += failed_count
            
            return response
        except ClientError as e:
            logger.error(f"Error putting batch: {e}")
            self.metrics['records_failed'] += len(records)
            raise
    
    def generate_medical_record(self, patient_id: str) -> dict:
        """Generate sample medical device record"""
        return {
            'patient_id': patient_id,
            'device_id': f"DEV{random.randint(1000, 9999)}",
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'vitals': {
                'heart_rate': random.randint(60, 100),
                'blood_pressure': {
                    'systolic': random.randint(90, 140),
                    'diastolic': random.randint(60, 90)
                },
                'spo2': random.randint(95, 100),
                'temperature': round(random.uniform(36.1, 37.5), 1)
            }
        }
    
    def run(self, duration: int = 300, rate: int = 10):
        """Run producer for specified duration"""
        logger.info(f"Starting Kinesis producer: stream={self.stream_name}, rate={rate}/s")
        
        start_time = time.time()
        patient_ids = [f"PAT{str(i).zfill(6)}" for i in range(1, 101)]
        
        try:
            while time.time() - start_time < duration:
                patient_id = random.choice(patient_ids)
                record = self.generate_medical_record(patient_id)
                
                self.put_record(record, patient_id)
                
                time.sleep(1.0 / rate)
                
                if self.metrics['records_sent'] % 100 == 0:
                    logger.info(
                        f"Sent: {self.metrics['records_sent']}, "
                        f"Failed: {self.metrics['records_failed']}"
                    )
        
        except KeyboardInterrupt:
            logger.info("Producer interrupted")
        finally:
            logger.info(f"Final metrics: {self.metrics}")


def main():
    parser = argparse.ArgumentParser(description='Kinesis Medical Device Producer')
    parser.add_argument('--stream-name', default='medical-devices-stream', help='Kinesis stream name')
    parser.add_argument('--region', default='us-east-1', help='AWS region')
    parser.add_argument('--duration', type=int, default=300, help='Duration in seconds')
    parser.add_argument('--rate', type=int, default=10, help='Records per second')
    
    args = parser.parse_args()
    
    producer = KinesisProducer(stream_name=args.stream_name, region=args.region)
    producer.run(duration=args.duration, rate=args.rate)


if __name__ == '__main__':
    main()
