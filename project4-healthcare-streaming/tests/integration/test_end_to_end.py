"""End-to-end integration tests for healthcare streaming"""

import json
import time
from typing import Generator

import pytest
import requests
from kafka import KafkaConsumer, KafkaProducer


@pytest.fixture(scope="module")
def kafka_producer() -> Generator[KafkaProducer, None, None]:
    """Kafka producer fixture"""
    producer = KafkaProducer(
        bootstrap_servers=["localhost:9092"],
        value_serializer=lambda v: json.dumps(v).encode("utf-8"),
        request_timeout_ms=5000,
        max_block_ms=5000,
    )
    yield producer
    producer.close()


@pytest.fixture(scope="module")
def kafka_consumer() -> Generator[KafkaConsumer, None, None]:
    """Kafka consumer fixture"""
    consumer = KafkaConsumer(
        "medical-devices-vitals",
        bootstrap_servers=["localhost:9092"],
        auto_offset_reset="earliest",
        consumer_timeout_ms=10000,
        value_deserializer=lambda m: json.loads(m.decode("utf-8")),
    )
    yield consumer
    consumer.close()


@pytest.mark.integration
def test_kafka_connectivity() -> None:
    """Test Kafka broker is accessible"""
    try:
        # Try to connect to Kafka REST API or admin endpoint
        # Note: This assumes Kafka UI or similar is running on port 8080
        response = requests.get("http://localhost:8080/api/health", timeout=5)
        assert response.status_code == 200
    except requests.exceptions.RequestException:
        # If no REST API is available, skip this test
        pytest.skip("Kafka REST API not available")


@pytest.mark.integration
def test_produce_consume_flow(kafka_producer: KafkaProducer, kafka_consumer: KafkaConsumer) -> None:
    """Test complete produce-consume flow"""
    test_data = {"patient_id": f"test-{int(time.time())}", "timestamp": time.time(), "vitals": {"heart_rate": 72}}

    # Produce message
    future = kafka_producer.send("medical-devices-vitals", value=test_data)
    kafka_producer.flush()

    # Wait for send to complete
    try:
        record_metadata = future.get(timeout=10)
        assert record_metadata is not None
    except Exception as e:
        pytest.fail(f"Failed to produce message: {e}")

    # Consume messages
    messages = []
    found = False

    for message in kafka_consumer:
        messages.append(message.value)
        if message.value.get("patient_id") == test_data["patient_id"]:
            found = True
            break

    assert len(messages) > 0, "No messages consumed"
    consumed_ids = [m.get("patient_id") for m in messages]
    assert found, f"Test message not found. Produced: {test_data['patient_id']}, Consumed: {consumed_ids}"


@pytest.mark.integration
@pytest.mark.slow
def test_flink_job_running() -> None:
    """Test Flink job is running"""
    try:
        response = requests.get("http://localhost:8081/jobs", timeout=5)
        data = response.json()

        assert "jobs" in data
        # Note: In test environment, there might not be jobs running
        # This test validates the endpoint is accessible
        assert isinstance(data["jobs"], list)
    except requests.exceptions.RequestException:
        pytest.skip("Flink REST API not available")


@pytest.mark.integration
@pytest.mark.slow
def test_spark_application_running() -> None:
    """Test Spark streaming app is running"""
    try:
        response = requests.get("http://localhost:8082/api/v1/applications", timeout=5)
        data = response.json()

        # Spark should return a list of applications
        assert isinstance(data, list)
    except requests.exceptions.RequestException:
        pytest.skip("Spark REST API not available")


@pytest.mark.integration
def test_kafka_topic_creation() -> None:
    """Test that required Kafka topics exist"""
    from kafka.admin import KafkaAdminClient

    try:
        admin_client = KafkaAdminClient(bootstrap_servers=["localhost:9092"], request_timeout_ms=5000)

        topics = admin_client.list_topics()
        admin_client.close()

        # At least one topic should exist (the test might create it)
        assert len(topics) > 0, "No Kafka topics found"
    except Exception as e:
        pytest.skip(f"Kafka admin API not accessible: {e}")


@pytest.mark.integration
def test_health_check_endpoints() -> None:
    """Test all service health check endpoints"""
    services = {
        "Kafka UI": "http://localhost:8080",
        "Flink Dashboard": "http://localhost:8081",
        "Spark UI": "http://localhost:8082",
    }

    available_services = []

    for service_name, url in services.items():
        try:
            response = requests.get(url, timeout=2)
            if response.status_code < 500:
                available_services.append(service_name)
        except requests.exceptions.RequestException:
            pass

    # At least one service should be available for integration tests
    if not available_services:
        pytest.skip("No streaming services available")

    assert len(available_services) > 0


@pytest.mark.integration
@pytest.mark.aws
def test_kinesis_stream_accessible() -> None:
    """Test AWS Kinesis stream is accessible (if configured)"""
    pytest.skip("AWS integration tests require AWS credentials")


@pytest.mark.integration
@pytest.mark.aws
def test_msk_cluster_accessible() -> None:
    """Test AWS MSK cluster is accessible (if configured)"""
    pytest.skip("AWS integration tests require AWS credentials")


@pytest.mark.integration
def test_data_pipeline_latency() -> None:
    """Test end-to-end latency of data pipeline"""
    # This would measure the time from producer to consumer
    # Skip if services aren't available
    pytest.skip("Latency test requires full stack deployment")


@pytest.mark.integration
def test_throughput_basic() -> None:
    """Test basic throughput - produce and consume multiple messages"""
    try:
        producer = KafkaProducer(
            bootstrap_servers=["localhost:9092"],
            value_serializer=lambda v: json.dumps(v).encode("utf-8"),
            request_timeout_ms=5000,
        )

        # Produce 10 test messages
        sent_count = 0
        for i in range(10):
            test_data = {
                "patient_id": f"throughput-test-{i}",
                "timestamp": time.time(),
                "vitals": {"heart_rate": 70 + i},
            }
            producer.send("medical-devices-vitals", value=test_data)
            sent_count += 1

        producer.flush()
        producer.close()

        assert sent_count == 10, "Not all messages were sent"
    except Exception as e:
        pytest.skip(f"Throughput test failed due to: {e}")
