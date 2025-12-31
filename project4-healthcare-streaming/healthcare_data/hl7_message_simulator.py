"""HL7 message simulator and parser"""
from datetime import datetime
from typing import Dict, List, Any


def create_hl7_message(patient_id: str, observations: List[Dict[str, Any]]) -> str:
    """Create HL7 v2.5 message
    
    Args:
        patient_id: Patient identifier
        observations: List of observation dictionaries
        
    Returns:
        HL7 formatted message string
    """
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    message_id = str(int(datetime.now().timestamp()))
    
    segments = [
        f"MSH|^~\\&|LAB||EMR||{timestamp}||ORU^R01|{message_id}|P|2.5",
        f"PID|1||{patient_id}||Doe^John||19800101|M",
        "OBR|1||ORDER123|LAB^Laboratory^LN|||20231231120000"
    ]
    
    for idx, obs in enumerate(observations, start=1):
        test_code = obs.get("test", obs.get("test_code", "UNK"))
        value = obs.get("value", "")
        unit = obs.get("unit", "")
        obx = f"OBX|{idx}|NM|{test_code}^Test^LN||{value}|{unit}|||||F"
        segments.append(obx)
    
    return "\n".join(segments)


def parse_hl7_segments(message: str) -> Dict[str, Dict[str, Any]]:
    """Parse HL7 message into segments
    
    Args:
        message: HL7 message string
        
    Returns:
        Dictionary of parsed segments
    """
    segments = {}
    lines = message.strip().split("\n")
    
    for line in lines:
        if not line:
            continue
        
        fields = line.split("|")
        segment_type = fields[0]
        
        if segment_type == "MSH":
            segments["MSH"] = {
                "encoding": fields[1] if len(fields) > 1 else "",
                "sending_app": fields[2] if len(fields) > 2 else "",
                "message_type": fields[8] if len(fields) > 8 else "",
            }
        elif segment_type == "PID":
            segments["PID"] = {
                "patient_id": fields[3] if len(fields) > 3 else "",
                "patient_name": fields[5] if len(fields) > 5 else "",
            }
        elif segment_type == "OBR":
            segments["OBR"] = {
                "order_id": fields[2] if len(fields) > 2 else "",
                "test_code": fields[4] if len(fields) > 4 else "",
            }
        elif segment_type == "OBX":
            if "OBX" not in segments:
                segments["OBX"] = []
            segments["OBX"].append({
                "set_id": fields[1] if len(fields) > 1 else "",
                "value_type": fields[2] if len(fields) > 2 else "",
                "observation": fields[3] if len(fields) > 3 else "",
                "value": fields[5] if len(fields) > 5 else "",
            })
    
    return segments


if __name__ == "__main__":
    # Example usage
    msg = create_hl7_message(
        patient_id="12345",
        observations=[{"test": "GLU", "value": 95, "unit": "mg/dL"}]
    )
    print(msg)
    print("\n--- Parsed ---")
    parsed = parse_hl7_segments(msg)
    print(parsed)
