#!/usr/bin/env python3
"""
Medical Device Data Producer for Kafka
Simulates various medical devices streaming real-time health data
"""

import json
import logging
import random
import time
import uuid
from datetime import datetime, timezone
from typing import Dict, List, Optional
import argparse

from kafka import KafkaProducer
from kafka.errors import KafkaError

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class MedicalDeviceProducer:
    """Kafka producer for medical device data simulation"""
    
    def __init__(
        self,
        bootstrap_servers: str = 'localhost:9092',
        device_count: int = 10
    ):
        """
        Initialize the medical device producer
        
        Args:
            bootstrap_servers: Kafka bootstrap servers
            device_count: Number of simulated devices
        """
        self.bootstrap_servers = bootstrap_servers
        self.device_count = device_count
        self.producer = None
        self.metrics = {
            'messages_sent': 0,
            'messages_failed': 0,
            'bytes_sent': 0
        }
        
        # Simulated patient IDs
        self.patient_ids = [f"PAT{str(i).zfill(6)}" for i in range(1, device_count + 1)]
        
        # Device metadata
        self.devices = self._initialize_devices()
        
    def _initialize_devices(self) -> List[Dict]:
        """Initialize device metadata"""
        device_types = ['ECG', 'GLUCOSE_METER', 'BP_MONITOR', 'PULSE_OX', 'CGM']
        devices = []
        
        for i in range(self.device_count):
            device_type = random.choice(device_types)
            devices.append({
                'device_id': f"DEV{device_type[:3]}{str(i).zfill(5)}",
                'device_type': device_type,
                'patient_id': self.patient_ids[i],
                'manufacturer': self._get_manufacturer(device_type),
                'model': f"Model-{random.randint(100, 999)}",
                'firmware_version': f"{random.randint(1, 5)}.{random.randint(0, 9)}.{random.randint(0, 99)}"
            })
        
        return devices
    
    def _get_manufacturer(self, device_type: str) -> str:
        """Get manufacturer based on device type"""
        manufacturers = {
            'ECG': ['Philips', 'GE Healthcare', 'Medtronic'],
            'GLUCOSE_METER': ['Abbott', 'Roche', 'LifeScan'],
            'BP_MONITOR': ['Omron', 'Welch Allyn', 'A&D Medical'],
            'PULSE_OX': ['Masimo', 'Nellcor', 'Nonin'],
            'CGM': ['Dexcom', 'Abbott', 'Medtronic']
        }
        return random.choice(manufacturers.get(device_type, ['Generic']))
    
    def connect(self):
        """Establish connection to Kafka"""
        try:
            self.producer = KafkaProducer(
                bootstrap_servers=self.bootstrap_servers,
                value_serializer=lambda v: json.dumps(v).encode('utf-8'),
                key_serializer=lambda k: k.encode('utf-8') if k else None,
                acks='all',  # Wait for all replicas
                retries=3,
                max_in_flight_requests_per_connection=5,
                compression_type='snappy',
                linger_ms=10,
                batch_size=16384
            )
            logger.info(f"Connected to Kafka at {self.bootstrap_servers}")
        except Exception as e:
            logger.error(f"Failed to connect to Kafka: {e}")
            raise
    
    def _generate_ecg_reading(self, device: Dict) -> Dict:
        """Generate ECG monitor reading"""
        # Simulate ECG waveform (simplified)
        heart_rate = random.randint(60, 100)
        
        # Add occasional abnormalities
        is_abnormal = random.random() < 0.05
        if is_abnormal:
            heart_rate = random.choice([random.randint(40, 55), random.randint(120, 180)])
        
        return {
            'device_id': device['device_id'],
            'device_type': device['device_type'],
            'patient_id': device['patient_id'],
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'measurement_type': 'ECG',
            'values': {
                'heart_rate': heart_rate,
                'rhythm': 'SINUS' if not is_abnormal else random.choice(['AFIB', 'VTACH', 'BRADYCARDIA']),
                'st_segment': round(random.uniform(-0.5, 0.5), 2),
                'pr_interval': round(random.uniform(120, 200), 0),
                'qrs_duration': round(random.uniform(80, 120), 0),
                'qt_interval': round(random.uniform(350, 450), 0)
            },
            'unit': 'bpm',
            'is_abnormal': is_abnormal,
            'metadata': {
                'manufacturer': device['manufacturer'],
                'model': device['model'],
                'firmware_version': device['firmware_version']
            }
        }
    
    def _generate_glucose_reading(self, device: Dict) -> Dict:
        """Generate blood glucose reading"""
        # Normal range: 70-140 mg/dL
        glucose_level = random.randint(70, 140)
        
        # Add occasional abnormalities
        is_abnormal = random.random() < 0.1
        if is_abnormal:
            glucose_level = random.choice([random.randint(40, 65), random.randint(200, 400)])
        
        return {
            'device_id': device['device_id'],
            'device_type': device['device_type'],
            'patient_id': device['patient_id'],
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'measurement_type': 'GLUCOSE',
            'values': {
                'glucose_level': glucose_level,
                'measurement_context': random.choice(['FASTING', 'POST_MEAL', 'RANDOM', 'BEDTIME']),
                'trend': random.choice(['STABLE', 'RISING', 'FALLING']),
                'rate_of_change': round(random.uniform(-3, 3), 2)
            },
            'unit': 'mg/dL',
            'is_abnormal': is_abnormal,
            'metadata': {
                'manufacturer': device['manufacturer'],
                'model': device['model'],
                'calibration_date': '2025-01-01'
            }
        }
    
    def _generate_vitals_reading(self, device: Dict) -> Dict:
        """Generate general vitals reading (BP, SpO2, temp)"""
        # Blood pressure
        systolic = random.randint(90, 140)
        diastolic = random.randint(60, 90)
        
        # Add occasional hypertension
        is_abnormal = random.random() < 0.08
        if is_abnormal:
            systolic = random.randint(160, 200)
            diastolic = random.randint(100, 120)
        
        # SpO2
        spo2 = random.randint(95, 100)
        if is_abnormal and random.random() < 0.3:
            spo2 = random.randint(85, 93)
        
        return {
            'device_id': device['device_id'],
            'device_type': device['device_type'],
            'patient_id': device['patient_id'],
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'measurement_type': 'VITALS',
            'values': {
                'blood_pressure': {
                    'systolic': systolic,
                    'diastolic': diastolic,
                    'mean_arterial_pressure': round((systolic + 2 * diastolic) / 3, 1)
                },
                'spo2': spo2,
                'pulse_rate': random.randint(60, 100),
                'temperature': round(random.uniform(36.1, 37.5), 1),
                'respiratory_rate': random.randint(12, 20)
            },
            'unit': 'mixed',
            'is_abnormal': is_abnormal,
            'metadata': {
                'manufacturer': device['manufacturer'],
                'model': device['model']
            }
        }
    
    def _generate_hl7_oru_message(self, device: Dict, measurement: Dict) -> str:
        """Generate HL7 v2.x ORU^R01 message (Observation Result)"""
        # MSH - Message Header
        msg_control_id = str(uuid.uuid4())[:20]
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        
        msh = f"MSH|^~\\&|{device['manufacturer']}|MEDICAL_FACILITY|HL7_SYSTEM|HOSPITAL|{timestamp}||ORU^R01|{msg_control_id}|P|2.5"
        
        # PID - Patient Identification
        pid = f"PID|1||{device['patient_id']}^^^HOSPITAL^MR||DOE^JOHN^A||19800101|M|||123 MAIN ST^^CITY^STATE^12345^USA|||||||{device['patient_id']}"
        
        # OBR - Observation Request
        obr = f"OBR|1||{msg_control_id}|{measurement['measurement_type']}^{measurement['measurement_type']}|||{timestamp}"
        
        # OBX - Observation Result
        obx_segments = []
        for idx, (key, value) in enumerate(measurement['values'].items(), 1):
            if isinstance(value, dict):
                for sub_key, sub_value in value.items():
                    obx_segments.append(
                        f"OBX|{idx}|NM|{sub_key.upper()}^{sub_key.replace('_', ' ').title()}||{sub_value}|{measurement.get('unit', '')}||||{'A' if measurement.get('is_abnormal') else 'N'}|||F"
                    )
            else:
                obx_segments.append(
                    f"OBX|{idx}|NM|{key.upper()}^{key.replace('_', ' ').title()}||{value}|{measurement.get('unit', '')}||||{'A' if measurement.get('is_abnormal') else 'N'}|||F"
                )
        
        return '\r'.join([msh, pid, obr] + obx_segments)
    
    def _get_topic_for_device_type(self, device_type: str) -> str:
        """Map device type to Kafka topic"""
        topic_mapping = {
            'ECG': 'medical-devices-ecg',
            'GLUCOSE_METER': 'medical-devices-glucose',
            'CGM': 'medical-devices-glucose',
            'BP_MONITOR': 'medical-devices-vitals',
            'PULSE_OX': 'medical-devices-vitals'
        }
        return topic_mapping.get(device_type, 'medical-devices-vitals')
    
    def generate_and_send_reading(self, device: Dict):
        """Generate and send a reading for a specific device"""
        try:
            # Generate measurement based on device type
            if device['device_type'] == 'ECG':
                measurement = self._generate_ecg_reading(device)
            elif device['device_type'] in ['GLUCOSE_METER', 'CGM']:
                measurement = self._generate_glucose_reading(device)
            else:
                measurement = self._generate_vitals_reading(device)
            
            # Determine topic
            topic = self._get_topic_for_device_type(device['device_type'])
            
            # Send to JSON topic
            future = self.producer.send(
                topic,
                key=device['patient_id'],
                value=measurement
            )
            
            # Wait for send to complete
            record_metadata = future.get(timeout=10)
            
            # Also send as HL7 message
            hl7_message = self._generate_hl7_oru_message(device, measurement)
            hl7_future = self.producer.send(
                'hl7-messages-raw',
                key=device['patient_id'],
                value={'message': hl7_message, 'patient_id': device['patient_id']}
            )
            hl7_future.get(timeout=10)
            
            # Update metrics
            self.metrics['messages_sent'] += 2
            self.metrics['bytes_sent'] += len(json.dumps(measurement).encode())
            
            # Check for critical alerts
            if measurement.get('is_abnormal'):
                alert = {
                    'alert_id': str(uuid.uuid4()),
                    'timestamp': datetime.now(timezone.utc).isoformat(),
                    'patient_id': device['patient_id'],
                    'device_id': device['device_id'],
                    'alert_type': 'ABNORMAL_READING',
                    'severity': 'HIGH' if random.random() < 0.3 else 'MEDIUM',
                    'measurement': measurement,
                    'requires_immediate_attention': random.random() < 0.2
                }
                
                self.producer.send(
                    'medical-alerts-critical',
                    key=device['patient_id'],
                    value=alert
                )
                logger.warning(f"Critical alert sent for patient {device['patient_id']}")
            
            logger.debug(
                f"Sent message to {topic}: partition={record_metadata.partition}, "
                f"offset={record_metadata.offset}"
            )
            
        except KafkaError as e:
            logger.error(f"Kafka error sending message: {e}")
            self.metrics['messages_failed'] += 1
        except Exception as e:
            logger.error(f"Error generating/sending reading: {e}")
            self.metrics['messages_failed'] += 1
    
    def run(self, duration: int = 300, rate: int = 10):
        """
        Run the producer for a specified duration
        
        Args:
            duration: Duration in seconds (default: 300)
            rate: Messages per second (default: 10)
        """
        if not self.producer:
            self.connect()
        
        logger.info(f"Starting producer: {self.device_count} devices, {rate} msg/sec, {duration}s duration")
        
        start_time = time.time()
        message_interval = 1.0 / rate
        
        try:
            while time.time() - start_time < duration:
                iteration_start = time.time()
                
                # Send reading from a random device
                device = random.choice(self.devices)
                self.generate_and_send_reading(device)
                
                # Maintain rate
                elapsed = time.time() - iteration_start
                sleep_time = max(0, message_interval - elapsed)
                time.sleep(sleep_time)
                
                # Log metrics every 100 messages
                if self.metrics['messages_sent'] % 100 == 0:
                    logger.info(
                        f"Metrics: sent={self.metrics['messages_sent']}, "
                        f"failed={self.metrics['messages_failed']}, "
                        f"bytes={self.metrics['bytes_sent']}"
                    )
        
        except KeyboardInterrupt:
            logger.info("Producer interrupted by user")
        finally:
            self.close()
    
    def close(self):
        """Close producer and flush remaining messages"""
        if self.producer:
            logger.info("Flushing remaining messages...")
            self.producer.flush()
            self.producer.close()
            logger.info(
                f"Producer closed. Final metrics: "
                f"sent={self.metrics['messages_sent']}, "
                f"failed={self.metrics['messages_failed']}, "
                f"bytes={self.metrics['bytes_sent']}"
            )


def main():
    parser = argparse.ArgumentParser(description='Medical Device Data Producer')
    parser.add_argument(
        '--bootstrap-servers',
        default='localhost:9092',
        help='Kafka bootstrap servers (default: localhost:9092)'
    )
    parser.add_argument(
        '--devices',
        type=int,
        default=10,
        help='Number of simulated devices (default: 10)'
    )
    parser.add_argument(
        '--duration',
        type=int,
        default=300,
        help='Duration in seconds (default: 300)'
    )
    parser.add_argument(
        '--rate',
        type=int,
        default=10,
        help='Messages per second (default: 10)'
    )
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Enable verbose logging'
    )
    
    args = parser.parse_args()
    
    if args.verbose:
        logger.setLevel(logging.DEBUG)
    
    producer = MedicalDeviceProducer(
        bootstrap_servers=args.bootstrap_servers,
        device_count=args.devices
    )
    
    producer.run(duration=args.duration, rate=args.rate)


if __name__ == '__main__':
    main()
