#!/usr/bin/env python3
"""
Unit tests for Kafka Medical Device Producer
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import json
from datetime import datetime

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'kafka_streams'))

from producer_medical_devices import MedicalDeviceProducer


class TestMedicalDeviceProducer(unittest.TestCase):
    """Test cases for MedicalDeviceProducer"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.producer = MedicalDeviceProducer(
            bootstrap_servers='localhost:9092',
            device_count=5
        )
    
    def test_initialization(self):
        """Test producer initialization"""
        self.assertEqual(len(self.producer.devices), 5)
        self.assertEqual(len(self.producer.patient_ids), 5)
        self.assertEqual(self.producer.metrics['messages_sent'], 0)
    
    def test_device_initialization(self):
        """Test device metadata initialization"""
        device = self.producer.devices[0]
        
        self.assertIn('device_id', device)
        self.assertIn('device_type', device)
        self.assertIn('patient_id', device)
        self.assertIn('manufacturer', device)
        self.assertIn('model', device)
        self.assertIn('firmware_version', device)
    
    def test_ecg_reading_generation(self):
        """Test ECG reading generation"""
        device = {
            'device_id': 'DEV001',
            'device_type': 'ECG',
            'patient_id': 'PAT000001',
            'manufacturer': 'Philips',
            'model': 'Model-123',
            'firmware_version': '1.0.0'
        }
        
        reading = self.producer._generate_ecg_reading(device)
        
        self.assertEqual(reading['device_id'], 'DEV001')
        self.assertEqual(reading['device_type'], 'ECG')
        self.assertEqual(reading['measurement_type'], 'ECG')
        self.assertIn('values', reading)
        self.assertIn('heart_rate', reading['values'])
        self.assertIn('rhythm', reading['values'])
        self.assertTrue(40 <= reading['values']['heart_rate'] <= 200)
    
    def test_glucose_reading_generation(self):
        """Test glucose reading generation"""
        device = {
            'device_id': 'DEV002',
            'device_type': 'GLUCOSE_METER',
            'patient_id': 'PAT000002',
            'manufacturer': 'Abbott',
            'model': 'Model-456',
            'firmware_version': '2.0.0'
        }
        
        reading = self.producer._generate_glucose_reading(device)
        
        self.assertEqual(reading['device_type'], 'GLUCOSE_METER')
        self.assertEqual(reading['measurement_type'], 'GLUCOSE')
        self.assertIn('glucose_level', reading['values'])
        self.assertTrue(20 <= reading['values']['glucose_level'] <= 600)
        self.assertEqual(reading['unit'], 'mg/dL')
    
    def test_vitals_reading_generation(self):
        """Test vitals reading generation"""
        device = {
            'device_id': 'DEV003',
            'device_type': 'BP_MONITOR',
            'patient_id': 'PAT000003',
            'manufacturer': 'Omron',
            'model': 'Model-789',
            'firmware_version': '3.0.0'
        }
        
        reading = self.producer._generate_vitals_reading(device)
        
        self.assertEqual(reading['device_type'], 'BP_MONITOR')
        self.assertIn('blood_pressure', reading['values'])
        self.assertIn('spo2', reading['values'])
        self.assertIn('pulse_rate', reading['values'])
        
        bp = reading['values']['blood_pressure']
        self.assertIn('systolic', bp)
        self.assertIn('diastolic', bp)
        self.assertTrue(50 <= bp['systolic'] <= 220)
        self.assertTrue(40 <= bp['diastolic'] <= 130)
    
    def test_hl7_message_generation(self):
        """Test HL7 v2.x message generation"""
        device = {
            'device_id': 'DEV004',
            'device_type': 'ECG',
            'patient_id': 'PAT000004',
            'manufacturer': 'GE Healthcare',
            'model': 'Model-111',
            'firmware_version': '1.5.0'
        }
        
        measurement = {
            'measurement_type': 'ECG',
            'values': {'heart_rate': 75},
            'unit': 'bpm',
            'is_abnormal': False
        }
        
        hl7_message = self.producer._generate_hl7_oru_message(device, measurement)
        
        self.assertIn('MSH|', hl7_message)
        self.assertIn('PID|', hl7_message)
        self.assertIn('OBR|', hl7_message)
        self.assertIn('OBX|', hl7_message)
        self.assertIn('PAT000004', hl7_message)
    
    def test_topic_mapping(self):
        """Test device type to topic mapping"""
        self.assertEqual(
            self.producer._get_topic_for_device_type('ECG'),
            'medical-devices-ecg'
        )
        self.assertEqual(
            self.producer._get_topic_for_device_type('GLUCOSE_METER'),
            'medical-devices-glucose'
        )
        self.assertEqual(
            self.producer._get_topic_for_device_type('BP_MONITOR'),
            'medical-devices-vitals'
        )
    
    @patch('producer_medical_devices.KafkaProducer')
    def test_kafka_connection(self, mock_kafka_producer):
        """Test Kafka connection"""
        mock_producer_instance = MagicMock()
        mock_kafka_producer.return_value = mock_producer_instance
        
        self.producer.connect()
        
        mock_kafka_producer.assert_called_once()
        self.assertIsNotNone(self.producer.producer)


class TestReadingValidation(unittest.TestCase):
    """Test reading validation logic"""
    
    def test_valid_heart_rate_range(self):
        """Test heart rate is within valid range"""
        producer = MedicalDeviceProducer(device_count=1)
        device = producer.devices[0]
        device['device_type'] = 'ECG'
        
        for _ in range(100):
            reading = producer._generate_ecg_reading(device)
            hr = reading['values']['heart_rate']
            # Allow for abnormal readings
            self.assertTrue(20 <= hr <= 250, f"Heart rate {hr} out of valid range")
    
    def test_timestamp_format(self):
        """Test timestamp is in ISO 8601 format"""
        producer = MedicalDeviceProducer(device_count=1)
        device = producer.devices[0]
        
        reading = producer._generate_ecg_reading(device)
        timestamp = reading['timestamp']
        
        # Should be able to parse ISO 8601 timestamp
        try:
            datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
        except ValueError:
            self.fail(f"Timestamp {timestamp} is not valid ISO 8601 format")


if __name__ == '__main__':
    unittest.main()
