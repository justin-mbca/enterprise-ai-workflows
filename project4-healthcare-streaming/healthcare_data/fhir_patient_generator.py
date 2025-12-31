"""FHIR R4 patient data generator"""

import random
import uuid
from datetime import datetime, timedelta
from typing import Any, Dict


def generate_patient() -> Dict[str, Any]:
    """Generate FHIR R4 compliant patient resource

    Returns:
        Dictionary representing a FHIR Patient resource
    """
    patient_id = str(uuid.uuid4())

    # Random names
    first_names = ["John", "Jane", "Michael", "Sarah", "David", "Emily", "Robert", "Lisa"]
    last_names = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis"]

    first_name = random.choice(first_names)
    last_name = random.choice(last_names)

    # Random birth date (20-80 years ago)
    days_ago = random.randint(20 * 365, 80 * 365)
    birth_date = (datetime.now() - timedelta(days=days_ago)).strftime("%Y-%m-%d")

    gender = random.choice(["male", "female", "other"])

    patient = {
        "resourceType": "Patient",
        "id": patient_id,
        "meta": {"versionId": "1", "lastUpdated": datetime.now().isoformat() + "Z"},
        "identifier": [
            {
                "use": "official",
                "system": "http://hospital.org/patients",
                "value": f"MRN-{random.randint(100000, 999999)}",
            }
        ],
        "active": True,
        "name": [{"use": "official", "family": last_name, "given": [first_name]}],
        "gender": gender,
        "birthDate": birth_date,
        "address": [
            {
                "use": "home",
                "line": [f"{random.randint(100, 9999)} Main Street"],
                "city": random.choice(["Springfield", "Riverside", "Fairview", "Clinton"]),
                "state": random.choice(["CA", "NY", "TX", "FL"]),
                "postalCode": f"{random.randint(10000, 99999)}",
            }
        ],
        "telecom": [
            {
                "system": "phone",
                "value": f"{random.randint(200, 999)}-{random.randint(200, 999)}-{random.randint(1000, 9999)}",
                "use": "mobile",
            }
        ],
    }

    return patient


def generate_observation(patient_id: str, code: str, value: float, unit: str) -> Dict[str, Any]:
    """Generate FHIR R4 observation resource

    Args:
        patient_id: Patient identifier
        code: LOINC code for observation
        value: Numeric value
        unit: Unit of measurement

    Returns:
        Dictionary representing a FHIR Observation resource
    """
    observation = {
        "resourceType": "Observation",
        "id": str(uuid.uuid4()),
        "status": "final",
        "category": [
            {
                "coding": [
                    {
                        "system": "http://terminology.hl7.org/CodeSystem/observation-category",
                        "code": "vital-signs",
                        "display": "Vital Signs",
                    }
                ]
            }
        ],
        "code": {"coding": [{"system": "http://loinc.org", "code": code, "display": "Vital Sign"}]},
        "subject": {"reference": f"Patient/{patient_id}"},
        "effectiveDateTime": datetime.now().isoformat() + "Z",
        "valueQuantity": {"value": value, "unit": unit, "system": "http://unitsofmeasure.org", "code": unit},
    }

    return observation


if __name__ == "__main__":
    import json

    # Generate sample patient
    patient = generate_patient()
    print(json.dumps(patient, indent=2))

    # Generate sample observation
    obs = generate_observation(patient["id"], "8867-4", 72, "beats/min")
    print("\n" + json.dumps(obs, indent=2))
