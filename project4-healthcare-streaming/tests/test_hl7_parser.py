#!/usr/bin/env python3
"""
Unit tests for HL7 v2.x message parsing
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'spark_streaming'))

from structured_streaming_hl7 import parse_hl7_message


class TestHL7Parser(unittest.TestCase):
    """Test cases for HL7 message parsing"""
    
    def test_parse_oru_message(self):
        """Test parsing of ORU^R01 message"""
        hl7_message = """MSH|^~\\&|GE Healthcare|MEDICAL_FACILITY|HL7_SYSTEM|HOSPITAL|20250101120000||ORU^R01|MSG123456|P|2.5\rPID|1||PAT000001^^^HOSPITAL^MR||DOE^JOHN^A||19800101|M|||123 MAIN ST^^CITY^STATE^12345^USA|||||||PAT000001\rOBR|1||MSG123456|ECG^ECG|||20250101120000\rOBX|1|NM|HEART_RATE^Heart Rate||75|bpm||||N|||F"""
        
        result = parse_hl7_message(hl7_message)
        
        self.assertIn('message_type', result)
        self.assertEqual(result['message_type'], 'ORU^R01')
        self.assertIn('patient_id', result)
        self.assertEqual(result['patient_id'], 'PAT000001^^^HOSPITAL^MR')
        self.assertIn('observation_value', result)
    
    def test_parse_empty_message(self):
        """Test parsing of empty message"""
        result = parse_hl7_message("")
        self.assertEqual(result, {})
    
    def test_parse_malformed_message(self):
        """Test parsing of malformed message"""
        result = parse_hl7_message("INVALID|DATA")
        self.assertIsInstance(result, dict)
    
    def test_msh_segment_extraction(self):
        """Test MSH segment extraction"""
        hl7_message = "MSH|^~\\&|System|Facility|HL7|Hospital|20250101||ADT^A01|MSG001|P|2.5"
        
        result = parse_hl7_message(hl7_message)
        
        self.assertIn('message_type', result)
        self.assertEqual(result['message_type'], 'ADT^A01')
    
    def test_pid_segment_extraction(self):
        """Test PID segment extraction"""
        hl7_message = "MSH|^~\\&|System|Facility|HL7|Hospital|20250101||ADT^A01|MSG001|P|2.5\rPID|1||MRN123456^^^HOSP^MR||SMITH^JANE^M||19900515|F"
        
        result = parse_hl7_message(hl7_message)
        
        self.assertIn('patient_id', result)
        self.assertEqual(result['patient_id'], 'MRN123456^^^HOSP^MR')
        self.assertIn('patient_name', result)
        self.assertEqual(result['patient_name'], 'SMITH^JANE^M')
    
    def test_obr_segment_extraction(self):
        """Test OBR segment extraction"""
        hl7_message = "MSH|^~\\&|System|Facility|HL7|Hospital|20250101||ORU^R01|MSG001|P|2.5\rOBR|1||OBS123456|LAB^Lab Test"
        
        result = parse_hl7_message(hl7_message)
        
        self.assertIn('observation_id', result)
        self.assertEqual(result['observation_id'], 'OBS123456')
    
    def test_obx_segment_extraction(self):
        """Test OBX segment extraction"""
        hl7_message = "MSH|^~\\&|System|Facility|HL7|Hospital|20250101||ORU^R01|MSG001|P|2.5\rOBX|1|NM|GLU^Glucose||95|mg/dL||||N"
        
        result = parse_hl7_message(hl7_message)
        
        self.assertIn('observation_value', result)
        self.assertEqual(result['observation_value'], '95')
    
    def test_multiple_segments(self):
        """Test parsing message with multiple segments"""
        hl7_message = """MSH|^~\\&|Abbott|CLINIC|HL7_SYS|HOSP|20250101150000||ORU^R01|MSG789|P|2.5\rPID|1||PAT999999^^^HOSP^MR||WILLIAMS^BOB^T||19750320|M\rOBR|1||OBS999|GLU^Glucose Test|||20250101150000\rOBX|1|NM|GLU^Glucose||125|mg/dL||||A|||F"""
        
        result = parse_hl7_message(hl7_message)
        
        # Verify all key fields are extracted
        self.assertIn('message_type', result)
        self.assertIn('patient_id', result)
        self.assertIn('patient_name', result)
        self.assertIn('observation_id', result)
        self.assertIn('observation_value', result)
        
        self.assertEqual(result['message_type'], 'ORU^R01')
        self.assertEqual(result['patient_id'], 'PAT999999^^^HOSP^MR')
        self.assertEqual(result['observation_value'], '125')


class TestHL7MessageStructure(unittest.TestCase):
    """Test HL7 message structure validation"""
    
    def test_segment_delimiter(self):
        """Test that segments are properly delimited"""
        hl7_message = "MSH|field1|field2\rPID|field1|field2"
        result = parse_hl7_message(hl7_message)
        # Should successfully parse without errors
        self.assertIsInstance(result, dict)
    
    def test_field_delimiter(self):
        """Test that fields are properly delimited"""
        hl7_message = "MSH|field1|field2|field3|field4|field5|field6|field7|field8|field9"
        result = parse_hl7_message(hl7_message)
        self.assertIn('message_type', result)


if __name__ == '__main__':
    unittest.main()
