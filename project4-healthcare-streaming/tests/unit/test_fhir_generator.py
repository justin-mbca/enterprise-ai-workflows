"""Unit tests for FHIR patient generation"""
import pytest
import json
from healthcare_data.fhir_patient_generator import generate_patient, generate_observation


def test_generate_patient() -> None:
    """Test FHIR patient generation"""
    patient = generate_patient()
    
    assert patient["resourceType"] == "Patient"
    assert "id" in patient
    assert "name" in patient
    assert "gender" in patient
    assert "birthDate" in patient
    assert patient["gender"] in ["male", "female", "other"]


def test_patient_has_required_fields() -> None:
    """Test patient has all required FHIR fields"""
    patient = generate_patient()
    
    # Required fields per FHIR R4
    assert "resourceType" in patient
    assert patient["resourceType"] == "Patient"
    assert "id" in patient
    assert "meta" in patient
    assert "identifier" in patient
    assert "active" in patient
    assert "name" in patient
    assert "gender" in patient
    assert "birthDate" in patient


def test_patient_identifier_structure() -> None:
    """Test patient identifier structure"""
    patient = generate_patient()
    
    assert len(patient["identifier"]) > 0
    identifier = patient["identifier"][0]
    
    assert "use" in identifier
    assert "system" in identifier
    assert "value" in identifier
    assert identifier["use"] == "official"


def test_patient_name_structure() -> None:
    """Test patient name structure"""
    patient = generate_patient()
    
    assert len(patient["name"]) > 0
    name = patient["name"][0]
    
    assert "use" in name
    assert "family" in name
    assert "given" in name
    assert name["use"] == "official"
    assert isinstance(name["given"], list)
    assert len(name["given"]) > 0


def test_patient_address_structure() -> None:
    """Test patient address structure"""
    patient = generate_patient()
    
    assert "address" in patient
    assert len(patient["address"]) > 0
    
    address = patient["address"][0]
    assert "use" in address
    assert "line" in address
    assert "city" in address
    assert "state" in address
    assert "postalCode" in address


def test_patient_telecom_structure() -> None:
    """Test patient telecom structure"""
    patient = generate_patient()
    
    assert "telecom" in patient
    assert len(patient["telecom"]) > 0
    
    telecom = patient["telecom"][0]
    assert "system" in telecom
    assert "value" in telecom
    assert "use" in telecom
    assert telecom["system"] == "phone"


def test_patient_json_valid() -> None:
    """Test generated patient is valid JSON"""
    patient = generate_patient()
    json_str = json.dumps(patient)
    parsed = json.loads(json_str)
    
    assert parsed == patient


def test_patient_uniqueness() -> None:
    """Test that generated patients are unique"""
    patient1 = generate_patient()
    patient2 = generate_patient()
    
    # IDs should be different
    assert patient1["id"] != patient2["id"]
    
    # MRNs should be different (highly likely)
    mrn1 = patient1["identifier"][0]["value"]
    mrn2 = patient2["identifier"][0]["value"]
    assert mrn1 != mrn2


def test_patient_gender_distribution() -> None:
    """Test gender values are valid"""
    valid_genders = {"male", "female", "other"}
    
    for _ in range(10):
        patient = generate_patient()
        assert patient["gender"] in valid_genders


def test_generate_observation() -> None:
    """Test FHIR observation generation"""
    patient_id = "patient-123"
    observation = generate_observation(patient_id, "8867-4", 72.0, "beats/min")
    
    assert observation["resourceType"] == "Observation"
    assert observation["status"] == "final"
    assert "code" in observation
    assert "subject" in observation
    assert observation["subject"]["reference"] == f"Patient/{patient_id}"
    assert "valueQuantity" in observation


def test_observation_structure() -> None:
    """Test observation has correct FHIR structure"""
    observation = generate_observation("pat-001", "8867-4", 72.0, "beats/min")
    
    # Check required fields
    assert "resourceType" in observation
    assert "id" in observation
    assert "status" in observation
    assert "category" in observation
    assert "code" in observation
    assert "subject" in observation
    assert "effectiveDateTime" in observation
    assert "valueQuantity" in observation


def test_observation_category() -> None:
    """Test observation category structure"""
    observation = generate_observation("pat-001", "8867-4", 72.0, "beats/min")
    
    assert len(observation["category"]) > 0
    category = observation["category"][0]
    
    assert "coding" in category
    assert len(category["coding"]) > 0
    
    coding = category["coding"][0]
    assert coding["code"] == "vital-signs"


def test_observation_code_structure() -> None:
    """Test observation code structure"""
    code = "8867-4"
    observation = generate_observation("pat-001", code, 72.0, "beats/min")
    
    assert "coding" in observation["code"]
    coding = observation["code"]["coding"][0]
    
    assert "system" in coding
    assert "code" in coding
    assert coding["code"] == code
    assert coding["system"] == "http://loinc.org"


def test_observation_value_quantity() -> None:
    """Test observation value quantity structure"""
    value = 98.6
    unit = "degF"
    observation = generate_observation("pat-001", "8310-5", value, unit)
    
    value_qty = observation["valueQuantity"]
    
    assert "value" in value_qty
    assert "unit" in value_qty
    assert "system" in value_qty
    assert "code" in value_qty
    
    assert value_qty["value"] == value
    assert value_qty["unit"] == unit


def test_observation_json_valid() -> None:
    """Test observation is valid JSON"""
    observation = generate_observation("pat-001", "8867-4", 72.0, "beats/min")
    
    json_str = json.dumps(observation)
    parsed = json.loads(json_str)
    
    assert parsed == observation
