"""Unit tests for Kafka producer components"""

from unittest.mock import MagicMock, patch

from kafka_streams.producer_medical_devices import generate_hl7_message, generate_vital_signs, send_to_kafka


def test_generate_vital_signs() -> None:
    """Test vital signs generation"""
    data = generate_vital_signs("patient-123")

    assert "patient_id" in data
    assert data["patient_id"] == "patient-123"
    assert "timestamp" in data
    assert "vitals" in data
    assert "heart_rate" in data["vitals"]
    assert 40 <= data["vitals"]["heart_rate"] <= 200
    assert "blood_pressure_systolic" in data["vitals"]
    assert "blood_pressure_diastolic" in data["vitals"]
    assert "temperature" in data["vitals"]
    assert "respiratory_rate" in data["vitals"]
    assert "oxygen_saturation" in data["vitals"]
    assert "device_id" in data
    assert "location" in data


def test_vital_signs_ranges() -> None:
    """Test vital signs are within expected ranges"""
    for _ in range(10):  # Test multiple generations
        data = generate_vital_signs(f"patient-{_}")

        vitals = data["vitals"]
        assert 40 <= vitals["heart_rate"] <= 200
        assert 90 <= vitals["blood_pressure_systolic"] <= 180
        assert 60 <= vitals["blood_pressure_diastolic"] <= 120
        assert 36.0 <= vitals["temperature"] <= 40.0
        assert 12 <= vitals["respiratory_rate"] <= 30
        assert 85 <= vitals["oxygen_saturation"] <= 100


def test_generate_hl7_message() -> None:
    """Test HL7 message generation"""
    msg = generate_hl7_message("patient-123", [{"test_code": "GLU", "value": 95, "unit": "mg/dL"}])

    assert msg.startswith("MSH|")
    assert "ORU^R01" in msg
    assert "patient-123" in msg
    assert "GLU" in msg
    assert "95" in msg
    assert "mg/dL" in msg
    assert "PID|" in msg
    assert "OBR|" in msg
    assert "OBX|" in msg


def test_generate_hl7_multiple_observations() -> None:
    """Test HL7 message with multiple observations"""
    observations = [
        {"test_code": "GLU", "value": 95, "unit": "mg/dL"},
        {"test_code": "HGB", "value": 14.5, "unit": "g/dL"},
        {"test_code": "WBC", "value": 7.2, "unit": "K/uL"},
    ]

    msg = generate_hl7_message("patient-456", observations)

    # Check all observations are present
    for obs in observations:
        assert obs["test_code"] in msg
        assert str(obs["value"]) in msg
        assert obs["unit"] in msg

    # Check multiple OBX segments
    assert msg.count("OBX|") == 3


@patch("kafka_streams.producer_medical_devices.KafkaProducer")
def test_send_to_kafka(mock_producer: MagicMock) -> None:
    """Test Kafka send functionality"""
    mock_instance = MagicMock()
    mock_producer.return_value = mock_instance

    data = {"test": "data", "value": 123}
    send_to_kafka("test-topic", data)

    # Verify producer was created with correct config
    mock_producer.assert_called_once()

    # Verify send was called
    mock_instance.send.assert_called_once()

    # Verify flush and close were called
    mock_instance.flush.assert_called_once()
    mock_instance.close.assert_called_once()


@patch("kafka_streams.producer_medical_devices.KafkaProducer")
def test_send_to_kafka_with_custom_servers(mock_producer: MagicMock) -> None:
    """Test Kafka send with custom bootstrap servers"""
    mock_instance = MagicMock()
    mock_producer.return_value = mock_instance

    custom_servers = ["broker1:9092", "broker2:9092"]
    data = {"test": "data"}

    send_to_kafka("test-topic", data, bootstrap_servers=custom_servers)

    # Verify producer was created with custom servers
    call_kwargs = mock_producer.call_args[1]
    assert call_kwargs["bootstrap_servers"] == custom_servers
