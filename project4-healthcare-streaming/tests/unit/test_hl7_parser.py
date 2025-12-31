"""Unit tests for HL7 message parsing"""

from healthcare_data.hl7_message_simulator import create_hl7_message, parse_hl7_segments


def test_create_hl7_message() -> None:
    """Test HL7 message creation"""
    msg = create_hl7_message(patient_id="12345", observations=[{"test": "GLU", "value": 95, "unit": "mg/dL"}])

    assert "MSH|" in msg
    assert "PID|" in msg
    assert "OBR|" in msg
    assert "OBX|" in msg
    assert "12345" in msg
    assert "GLU" in msg
    assert "95" in msg


def test_create_hl7_message_structure() -> None:
    """Test HL7 message has correct structure"""
    msg = create_hl7_message(patient_id="67890", observations=[{"test": "HGB", "value": 14.5, "unit": "g/dL"}])

    lines = msg.split("\n")

    # Check segment order
    assert lines[0].startswith("MSH|")
    assert lines[1].startswith("PID|")
    assert lines[2].startswith("OBR|")
    assert lines[3].startswith("OBX|")

    # Check MSH has message type
    assert "ORU^R01" in lines[0]


def test_create_hl7_multiple_observations() -> None:
    """Test HL7 with multiple observations"""
    observations = [{"test": "GLU", "value": 95, "unit": "mg/dL"}, {"test": "HGB", "value": 14.5, "unit": "g/dL"}]

    msg = create_hl7_message("patient-999", observations)

    # Count OBX segments
    assert msg.count("OBX|") == 2

    # Verify both observations are present
    assert "GLU" in msg
    assert "HGB" in msg


def test_parse_hl7_segments() -> None:
    """Test HL7 segment parsing"""
    msg = "MSH|^~\\&|LAB||EMR||20231231||ORU^R01|001|P|2.5\nPID|1||12345||Doe^John"

    segments = parse_hl7_segments(msg)

    assert "MSH" in segments
    assert "PID" in segments
    assert segments["PID"]["patient_id"] == "12345"


def test_parse_hl7_msh_segment() -> None:
    """Test parsing MSH segment"""
    msg = "MSH|^~\\&|LAB|SENDAPP|EMR|RECAPP|20231231120000||ORU^R01|MSG001|P|2.5"

    segments = parse_hl7_segments(msg)

    assert "MSH" in segments
    assert segments["MSH"]["encoding"] == "^~\\&"
    assert segments["MSH"]["sending_app"] == "LAB"
    assert segments["MSH"]["message_type"] == "ORU^R01"


def test_parse_hl7_pid_segment() -> None:
    """Test parsing PID segment"""
    msg = "MSH|^~\\&|LAB||EMR||20231231||ORU^R01|001|P|2.5\nPID|1||PAT123||Smith^John^A||19800101|M"

    segments = parse_hl7_segments(msg)

    assert "PID" in segments
    assert segments["PID"]["patient_id"] == "PAT123"
    assert segments["PID"]["patient_name"] == "Smith^John^A"


def test_parse_hl7_obx_segments() -> None:
    """Test parsing multiple OBX segments"""
    msg = """MSH|^~\\&|LAB||EMR||20231231||ORU^R01|001|P|2.5
PID|1||12345
OBR|1||ORDER1|LAB
OBX|1|NM|GLU||95|mg/dL|||||F
OBX|2|NM|HGB||14.5|g/dL|||||F"""

    segments = parse_hl7_segments(msg)

    assert "OBX" in segments
    assert isinstance(segments["OBX"], list)
    assert len(segments["OBX"]) == 2

    # Check first observation
    assert segments["OBX"][0]["set_id"] == "1"
    assert segments["OBX"][0]["value_type"] == "NM"

    # Check second observation
    assert segments["OBX"][1]["set_id"] == "2"


def test_parse_empty_message() -> None:
    """Test parsing empty message"""
    segments = parse_hl7_segments("")
    assert segments == {}


def test_parse_malformed_message() -> None:
    """Test parsing malformed message gracefully"""
    msg = "INVALID||DATA"
    segments = parse_hl7_segments(msg)
    # Should not crash, just return empty or partial data
    assert isinstance(segments, dict)


def test_round_trip_create_and_parse() -> None:
    """Test creating and then parsing an HL7 message"""
    patient_id = "TEST-001"
    observations = [{"test": "GLU", "value": 95, "unit": "mg/dL"}]

    # Create message
    msg = create_hl7_message(patient_id, observations)

    # Parse it back
    segments = parse_hl7_segments(msg)

    # Verify parsed data
    assert "MSH" in segments
    assert "PID" in segments
    assert segments["PID"]["patient_id"] == patient_id
    assert "OBX" in segments
    assert len(segments["OBX"]) == 1
