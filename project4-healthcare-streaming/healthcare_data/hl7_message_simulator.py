#!/usr/bin/env python3
"""
HL7 v2.x Message Simulator
Generates realistic HL7 v2.x messages for various message types
"""

import random
import time
import argparse
from datetime import datetime, timedelta
from typing import List
import uuid

from faker import Faker

fake = Faker()


class HL7MessageSimulator:
    """Generate HL7 v2.x messages"""
    
    def __init__(self, num_patients: int = 100):
        self.num_patients = num_patients
        self.patients = self._generate_patients()
        self.message_count = 0
    
    def _generate_patients(self) -> List[dict]:
        """Generate patient database"""
        patients = []
        for i in range(self.num_patients):
            patients.append({
                'mrn': f"MRN{str(i+1).zfill(8)}",
                'first_name': fake.first_name(),
                'last_name': fake.last_name(),
                'dob': fake.date_of_birth(minimum_age=18, maximum_age=90).strftime('%Y%m%d'),
                'gender': random.choice(['M', 'F', 'O']),
                'ssn': fake.ssn().replace('-', '')
            })
        return patients
    
    def _format_timestamp(self, dt: datetime = None) -> str:
        """Format datetime as HL7 timestamp"""
        if dt is None:
            dt = datetime.now()
        return dt.strftime('%Y%m%d%H%M%S')
    
    def _get_message_control_id(self) -> str:
        """Generate unique message control ID"""
        self.message_count += 1
        return f"MSG{str(self.message_count).zfill(10)}"
    
    def generate_adt_a01(self, patient: dict = None) -> str:
        """Generate ADT^A01 (Patient Admission) message"""
        if patient is None:
            patient = random.choice(self.patients)
        
        msg_control_id = self._get_message_control_id()
        timestamp = self._format_timestamp()
        
        # MSH - Message Header
        msh = f"MSH|^~\\&|ADT_SYSTEM|HOSPITAL|HL7_APP|FACILITY|{timestamp}||ADT^A01|{msg_control_id}|P|2.5"
        
        # EVN - Event Type
        evn = f"EVN|A01|{timestamp}"
        
        # PID - Patient Identification
        pid = f"PID|1||{patient['mrn']}^^^HOSPITAL^MR||{patient['last_name']}^{patient['first_name']}||{patient['dob']}|{patient['gender']}|||123 MAIN ST^^CITY^STATE^12345^USA||(555)555-5555||ENG|M||{patient['mrn']}|||{patient['ssn']}||||||||N"
        
        # PV1 - Patient Visit
        pv1 = f"PV1|1|I|ICU^101^01^HOSPITAL||||12345^DOE^JOHN^M^DR|||MED||||ADM|||||12345678|||||||||||||||||||||||||{timestamp}"
        
        return '\r'.join([msh, evn, pid, pv1])
    
    def generate_adt_a08(self, patient: dict = None) -> str:
        """Generate ADT^A08 (Patient Update) message"""
        if patient is None:
            patient = random.choice(self.patients)
        
        msg_control_id = self._get_message_control_id()
        timestamp = self._format_timestamp()
        
        msh = f"MSH|^~\\&|ADT_SYSTEM|HOSPITAL|HL7_APP|FACILITY|{timestamp}||ADT^A08|{msg_control_id}|P|2.5"
        evn = f"EVN|A08|{timestamp}"
        pid = f"PID|1||{patient['mrn']}^^^HOSPITAL^MR||{patient['last_name']}^{patient['first_name']}||{patient['dob']}|{patient['gender']}"
        pv1 = f"PV1|1|I|MED^202^01^HOSPITAL"
        
        return '\r'.join([msh, evn, pid, pv1])
    
    def generate_oru_r01(self, patient: dict = None) -> str:
        """Generate ORU^R01 (Observation Results) message"""
        if patient is None:
            patient = random.choice(self.patients)
        
        msg_control_id = self._get_message_control_id()
        timestamp = self._format_timestamp()
        
        msh = f"MSH|^~\\&|LAB_SYSTEM|HOSPITAL|HL7_APP|FACILITY|{timestamp}||ORU^R01|{msg_control_id}|P|2.5"
        pid = f"PID|1||{patient['mrn']}^^^HOSPITAL^MR||{patient['last_name']}^{patient['first_name']}||{patient['dob']}|{patient['gender']}"
        obr = f"OBR|1||{msg_control_id}|CBC^Complete Blood Count|||{timestamp}|||||||{timestamp}||12345^DOE^JANE^M^DR||||||||LAB|F"
        
        # Generate multiple OBX segments (observations)
        obx_segments = []
        observations = [
            ('WBC', 'White Blood Count', random.uniform(4.0, 11.0), '10*3/uL', 'N'),
            ('RBC', 'Red Blood Count', random.uniform(4.2, 5.9), '10*6/uL', 'N'),
            ('HGB', 'Hemoglobin', random.uniform(12.0, 17.0), 'g/dL', 'N'),
            ('PLT', 'Platelets', random.uniform(150, 400), '10*3/uL', 'N')
        ]
        
        for idx, (code, name, value, unit, status) in enumerate(observations, 1):
            obx = f"OBX|{idx}|NM|{code}^{name}||{value:.2f}|{unit}|4.0-11.0|{status}|||F"
            obx_segments.append(obx)
        
        return '\r'.join([msh, pid, obr] + obx_segments)
    
    def generate_orm_o01(self, patient: dict = None) -> str:
        """Generate ORM^O01 (Order Message) message"""
        if patient is None:
            patient = random.choice(self.patients)
        
        msg_control_id = self._get_message_control_id()
        timestamp = self._format_timestamp()
        
        msh = f"MSH|^~\\&|ORDER_SYSTEM|HOSPITAL|HL7_APP|FACILITY|{timestamp}||ORM^O01|{msg_control_id}|P|2.5"
        pid = f"PID|1||{patient['mrn']}^^^HOSPITAL^MR||{patient['last_name']}^{patient['first_name']}||{patient['dob']}|{patient['gender']}"
        orc = f"ORC|NW|ORD{self.message_count}||||||{timestamp}"
        obr = f"OBR|1|ORD{self.message_count}||XRAY^Chest X-Ray|||{timestamp}|||||||||12345^SMITH^JANE^M^DR"
        
        return '\r'.join([msh, pid, orc, obr])
    
    def simulate_stream(self, rate: int = 10, duration: int = 300):
        """Simulate streaming HL7 messages"""
        message_types = [
            self.generate_adt_a01,
            self.generate_adt_a08,
            self.generate_oru_r01,
            self.generate_orm_o01
        ]
        
        start_time = time.time()
        interval = 1.0 / rate
        
        print(f"Starting HL7 message simulation: {rate} messages/sec for {duration} seconds")
        
        try:
            while time.time() - start_time < duration:
                message_func = random.choice(message_types)
                message = message_func()
                
                # Print message (in real scenario, would send to Kafka/Kinesis)
                print(f"\n{'='*80}")
                print(f"Message {self.message_count} - {message_func.__name__}")
                print(f"{'='*80}")
                print(message.replace('\r', '\n'))
                
                time.sleep(interval)
        
        except KeyboardInterrupt:
            print("\nSimulation stopped by user")
        
        print(f"\nTotal messages generated: {self.message_count}")


def main():
    parser = argparse.ArgumentParser(description='HL7 v2.x Message Simulator')
    parser.add_argument('--patients', type=int, default=100, help='Number of patients (default: 100)')
    parser.add_argument('--rate', type=int, default=10, help='Messages per second (default: 10)')
    parser.add_argument('--duration', type=int, default=300, help='Duration in seconds (default: 300)')
    parser.add_argument('--message-type', choices=['ADT_A01', 'ADT_A08', 'ORU_R01', 'ORM_O01', 'ALL'], 
                       default='ALL', help='Message type to generate')
    
    args = parser.parse_args()
    
    simulator = HL7MessageSimulator(num_patients=args.patients)
    
    if args.message_type == 'ALL':
        simulator.simulate_stream(rate=args.rate, duration=args.duration)
    else:
        # Generate single message type
        if args.message_type == 'ADT_A01':
            print(simulator.generate_adt_a01())
        elif args.message_type == 'ADT_A08':
            print(simulator.generate_adt_a08())
        elif args.message_type == 'ORU_R01':
            print(simulator.generate_oru_r01())
        elif args.message_type == 'ORM_O01':
            print(simulator.generate_orm_o01())


if __name__ == '__main__':
    main()
