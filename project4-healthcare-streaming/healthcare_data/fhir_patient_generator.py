#!/usr/bin/env python3
"""
FHIR R4 Patient Resource Generator
Generates synthetic FHIR R4 Patient resources for testing
"""

import json
import random
import uuid
from datetime import datetime, timedelta
from typing import List, Dict
import argparse

from faker import Faker

fake = Faker()


class FHIRPatientGenerator:
    """Generate synthetic FHIR R4 Patient resources"""
    
    def __init__(self, seed: int = None):
        if seed:
            Faker.seed(seed)
            random.seed(seed)
        self.fake = Faker()
    
    def generate_patient(self) -> Dict:
        """Generate a single FHIR R4 Patient resource"""
        mrn = f"MRN{random.randint(100000, 999999)}"
        gender = random.choice(['male', 'female', 'other'])
        
        # Generate birth date (18-90 years old)
        birth_date = self.fake.date_of_birth(minimum_age=18, maximum_age=90)
        
        patient = {
            "resourceType": "Patient",
            "id": str(uuid.uuid4()),
            "meta": {
                "versionId": "1",
                "lastUpdated": datetime.now().isoformat() + "Z",
                "profile": [
                    "http://hl7.org/fhir/us/core/StructureDefinition/us-core-patient"
                ]
            },
            "identifier": [
                {
                    "use": "official",
                    "type": {
                        "coding": [{
                            "system": "http://terminology.hl7.org/CodeSystem/v2-0203",
                            "code": "MR",
                            "display": "Medical Record Number"
                        }]
                    },
                    "system": "http://hospital.example.org",
                    "value": mrn
                },
                {
                    "use": "secondary",
                    "system": "http://hl7.org/fhir/sid/us-ssn",
                    "value": self.fake.ssn()
                }
            ],
            "active": True,
            "name": [{
                "use": "official",
                "family": self.fake.last_name(),
                "given": [self.fake.first_name()],
                "prefix": [random.choice(["Mr.", "Mrs.", "Ms.", "Dr."])]
            }],
            "telecom": [
                {
                    "system": "phone",
                    "value": self.fake.phone_number(),
                    "use": "home"
                },
                {
                    "system": "email",
                    "value": self.fake.email(),
                    "use": "home"
                }
            ],
            "gender": gender,
            "birthDate": birth_date.isoformat(),
            "address": [{
                "use": "home",
                "type": "both",
                "line": [self.fake.street_address()],
                "city": self.fake.city(),
                "state": self.fake.state_abbr(),
                "postalCode": self.fake.zipcode(),
                "country": "US"
            }],
            "maritalStatus": {
                "coding": [{
                    "system": "http://terminology.hl7.org/CodeSystem/v3-MaritalStatus",
                    "code": random.choice(["M", "S", "D", "W"]),
                    "display": random.choice(["Married", "Single", "Divorced", "Widowed"])
                }]
            },
            "communication": [{
                "language": {
                    "coding": [{
                        "system": "urn:ietf:bcp:47",
                        "code": "en-US",
                        "display": "English (United States)"
                    }]
                },
                "preferred": True
            }]
        }
        
        return patient
    
    def generate_patients(self, count: int) -> List[Dict]:
        """Generate multiple patients"""
        return [self.generate_patient() for _ in range(count)]
    
    def export_ndjson(self, patients: List[Dict], filename: str):
        """Export patients as NDJSON (newline-delimited JSON)"""
        with open(filename, 'w') as f:
            for patient in patients:
                f.write(json.dumps(patient) + '\n')
    
    def export_bundle(self, patients: List[Dict], filename: str):
        """Export patients as FHIR Bundle"""
        bundle = {
            "resourceType": "Bundle",
            "type": "collection",
            "entry": [
                {
                    "fullUrl": f"urn:uuid:{patient['id']}",
                    "resource": patient
                }
                for patient in patients
            ]
        }
        
        with open(filename, 'w') as f:
            json.dump(bundle, f, indent=2)


def main():
    parser = argparse.ArgumentParser(description='FHIR R4 Patient Generator')
    parser.add_argument(
        '--count',
        type=int,
        default=100,
        help='Number of patients to generate (default: 100)'
    )
    parser.add_argument(
        '--output',
        default='patients.ndjson',
        help='Output filename (default: patients.ndjson)'
    )
    parser.add_argument(
        '--format',
        choices=['ndjson', 'bundle'],
        default='ndjson',
        help='Output format (default: ndjson)'
    )
    parser.add_argument(
        '--seed',
        type=int,
        help='Random seed for reproducibility'
    )
    
    args = parser.parse_args()
    
    generator = FHIRPatientGenerator(seed=args.seed)
    patients = generator.generate_patients(args.count)
    
    if args.format == 'ndjson':
        generator.export_ndjson(patients, args.output)
    else:
        generator.export_bundle(patients, args.output)
    
    print(f"Generated {args.count} patients and saved to {args.output}")


if __name__ == '__main__':
    main()
