"""Medical device data producer for Kafka"""
import json
import random
import time
from datetime import datetime
from typing import Dict, List, Any, Optional
from kafka import KafkaProducer


def generate_vital_signs(patient_id: str) -> Dict[str, Any]:
    """Generate realistic vital signs data for a patient
    
    Args:
        patient_id: Unique patient identifier
        
    Returns:
        Dictionary containing patient vitals data
    """
    return {
        "patient_id": patient_id,
        "timestamp": datetime.now().isoformat(),
        "vitals": {
            "heart_rate": random.randint(40, 200),
            "blood_pressure_systolic": random.randint(90, 180),
            "blood_pressure_diastolic": random.randint(60, 120),
            "temperature": round(random.uniform(36.0, 40.0), 1),
            "respiratory_rate": random.randint(12, 30),
            "oxygen_saturation": random.randint(85, 100)
        },
        "device_id": f"monitor-{random.randint(1000, 9999)}",
        "location": random.choice(["ICU", "ER", "Ward-A", "Ward-B"])
    }


def generate_hl7_message(patient_id: str, observations: List[Dict[str, Any]]) -> str:
    """Generate HL7 v2.5 ORU^R01 message for lab results
    
    Args:
        patient_id: Patient identifier
        observations: List of observation dicts with test_code, value, unit
        
    Returns:
        HL7 formatted message string
    """
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    message_id = f"{int(time.time())}"
    
    segments = [
        f"MSH|^~\\&|LAB||EMR||{timestamp}||ORU^R01|{message_id}|P|2.5",
        f"PID|1||{patient_id}||Doe^John||19800101|M|||123 Main St^^City^ST^12345",
        "OBR|1||12345|LAB^Laboratory Panel^LN|||20231231120000|||||||"
    ]
    
    for idx, obs in enumerate(observations, start=1):
        obx = f"OBX|{idx}|NM|{obs['test_code']}^{obs.get('test_name', 'Test')}^LN||{obs['value']}|{obs['unit']}|||||F"
        segments.append(obx)
    
    return "\n".join(segments)


def send_to_kafka(topic: str, data: Dict[str, Any], bootstrap_servers: Optional[List[str]] = None) -> None:
    """Send data to Kafka topic
    
    Args:
        topic: Kafka topic name
        data: Data dictionary to send
        bootstrap_servers: List of Kafka broker addresses
    """
    if bootstrap_servers is None:
        bootstrap_servers = ['localhost:9092']
    
    producer = KafkaProducer(
        bootstrap_servers=bootstrap_servers,
        value_serializer=lambda v: json.dumps(v).encode('utf-8')
    )
    
    producer.send(topic, value=data)
    producer.flush()
    producer.close()


if __name__ == "__main__":
    # Example usage
    patient_data = generate_vital_signs("patient-123")
    print(json.dumps(patient_data, indent=2))
    
    hl7_msg = generate_hl7_message("patient-123", [
        {"test_code": "GLU", "value": 95, "unit": "mg/dL"},
        {"test_code": "HGB", "value": 14.5, "unit": "g/dL"}
    ])
    print("\n" + hl7_msg)
