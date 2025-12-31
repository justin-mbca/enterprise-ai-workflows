# Project 4: Healthcare Streaming Infrastructure

Real-time healthcare data processing platform using Kafka, Flink, and Spark for medical device monitoring, HL7 message processing, and FHIR resource management.

## Overview

This project demonstrates enterprise-grade streaming infrastructure for healthcare applications with:

- **Real-time vital signs processing** from medical devices
- **HL7 v2 message handling** for lab results and clinical data
- **FHIR R4 compliant** patient and observation resources
- **HIPAA-focused** security and compliance measures
- **Comprehensive testing** with >80% code coverage

## Architecture

```
Medical Devices → Kafka (medical-devices-vitals)
                    ↓
                  Flink Stream Processing
                    ↓
HL7 Systems → Kafka (hl7-messages) → Spark Streaming → Analytics
                    ↓
FHIR Resources → Kafka (fhir-resources)
```

## Quick Start

### Prerequisites

- Python 3.9+
- Docker & Docker Compose
- 8GB RAM minimum

### Installation

```bash
# Install dependencies
cd project4-healthcare-streaming
make install

# Start infrastructure
docker-compose up -d

# Run tests
make test
```

## Testing

### Unit Tests

```bash
# Run unit tests only
make test-unit

# Run with coverage
pytest tests/unit/ --cov=. --cov-report=html
```

### Integration Tests

```bash
# Requires Docker services
make test-integration
```

### Local Testing Suite

```bash
# Complete stack validation
./scripts/run_local_tests.sh

# With cleanup
CLEANUP=true ./scripts/run_local_tests.sh
```

### AWS Integration Tests

```bash
# Configure AWS credentials first
aws configure

# Run AWS tests
./scripts/run_aws_tests.sh
```

## Performance Benchmarking

```bash
# Run performance benchmarks
make benchmark

# Results saved to benchmarks/YYYYMMDD_HHMMSS.json
```

## Data Validation

```bash
# Validate FHIR R4, HL7, and device data
./scripts/data_validation.sh
```

## Security Scanning

```bash
# Run security and compliance checks
./scripts/security_scan.sh
```

## Components

### Kafka Streams

**Producer for Medical Devices:**
```python
from kafka_streams.producer_medical_devices import generate_vital_signs, send_to_kafka

# Generate vital signs data
vitals = generate_vital_signs("patient-123")

# Send to Kafka
send_to_kafka("medical-devices-vitals", vitals)
```

### Healthcare Data Generators

**FHIR Patient Generator:**
```python
from healthcare_data.fhir_patient_generator import generate_patient

patient = generate_patient()
print(patient["resourceType"])  # "Patient"
```

**HL7 Message Simulator:**
```python
from healthcare_data.hl7_message_simulator import create_hl7_message

msg = create_hl7_message(
    patient_id="12345",
    observations=[{"test": "GLU", "value": 95, "unit": "mg/dL"}]
)
```

## Configuration Files

- **pytest.ini** - Test configuration
- **.flake8** - Linting rules
- **pyproject.toml** - Black, isort, mypy settings
- **Makefile** - Task automation

## Documentation

- [Testing Guide](TESTING.md) - Comprehensive testing documentation
- [Performance Tuning](docs/PERFORMANCE_TUNING.md) - Optimization guide
- [Security Guide](docs/SECURITY.md) - Security best practices

## Monitoring

```bash
# Collect metrics from all services
python3 monitoring/collect_metrics.py

# Results saved to reports/metrics_<timestamp>.json
```

## CI/CD Pipeline

GitHub Actions workflow: `.github/workflows/streaming-tests.yml`

**Pipeline stages:**
1. Code quality (flake8, black, isort, mypy)
2. Unit tests with coverage
3. Integration tests
4. Data validation
5. Security scanning
6. Performance benchmarks
7. AWS deployment (main branch only)

## Healthcare Data Standards

### FHIR R4

Compliant with FHIR R4 specifications:
- Patient resources
- Observation resources
- Encounter resources
- Condition resources

### HL7 v2.5

Supports HL7 v2.5 message types:
- ORU^R01 (Observation Result)
- ADT^A01 (Patient Admission)
- ORM^O01 (Order Message)

### Medical Device Data

Standard vital signs:
- Heart rate (beats/min)
- Blood pressure (systolic/diastolic)
- Temperature (°F or °C)
- Respiratory rate (breaths/min)
- Oxygen saturation (%)

## HIPAA Compliance

Security measures implemented:
- ✓ Encryption at rest (configurable)
- ✓ Encryption in transit (TLS/SSL)
- ✓ Access controls (RBAC)
- ✓ Audit logging
- ✓ De-identification checks
- ✓ Data retention policies

**Note:** This is a demonstration project. Production deployments require:
- Proper Business Associate Agreements (BAAs)
- Comprehensive security audits
- Penetration testing
- Regular compliance reviews

## Performance Targets

| Metric | Target | Status |
|--------|--------|--------|
| Throughput | >10,000 msg/sec | ⚠️ Needs testing |
| Latency | <100ms e2e | ⚠️ Needs testing |
| Availability | 99.9% | ⚠️ Needs testing |
| Test Coverage | >80% | ✅ Achieved |

## Cost Estimation

### Local Development
- **Cost:** $0 (Docker-based)
- **Requirements:** 8GB RAM, 20GB disk

### AWS Production
- **Kinesis:** $25/month (1 shard)
- **MSK:** $150/month (3 t3.small brokers)
- **Lambda:** $0.20/1M requests
- **Estimated Total:** $200-500/month

See [Performance Tuning Guide](docs/PERFORMANCE_TUNING.md) for cost optimization strategies.

## Technology Stack

- **Kafka** - Event streaming platform
- **Flink** - Stream processing framework
- **Spark Streaming** - Batch/micro-batch processing
- **Python 3.9+** - Application code
- **Docker** - Containerization
- **pytest** - Testing framework
- **GitHub Actions** - CI/CD pipeline

## Development

### Code Quality

```bash
# Format code
make format

# Lint code
make lint

# Type checking
mypy kafka_streams/ healthcare_data/
```

### Adding Tests

1. Create test file in `tests/unit/` or `tests/integration/`
2. Follow naming convention: `test_*.py`
3. Add markers: `@pytest.mark.unit` or `@pytest.mark.integration`
4. Run: `pytest tests/`

### Debugging

```bash
# Verbose test output
pytest -vv -s

# Run specific test
pytest tests/unit/test_kafka_producer.py::test_generate_vital_signs -v

# Debug with pdb
pytest --pdb
```

## Troubleshooting

### Docker Issues

```bash
# Reset Docker environment
docker-compose down -v
docker-compose up -d

# View logs
docker-compose logs -f kafka
```

### Test Failures

```bash
# Clean artifacts
make clean

# Reinstall dependencies
make install

# Run tests with verbose output
pytest -vv
```

### Kafka Connection Issues

```bash
# Verify Kafka is running
docker-compose ps | grep kafka

# Test connectivity
nc -zv localhost 9092

# Wait longer for startup
sleep 60
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make changes and add tests
4. Run: `make lint && make test`
5. Submit a pull request

## License

MIT License - See LICENSE file for details

## Related Projects

- [Project 1: Rapid Insights](../project1-rapid-insights/)
- [Project 2: MLOps Pipeline](../project2-mlops-pipeline/)
- [Project 3: Document Q&A](../project3-document-qa/)
- [Data Platform](../data-platform/)

## Resources

- [Kafka Documentation](https://kafka.apache.org/documentation/)
- [Apache Flink](https://flink.apache.org/)
- [Apache Spark Streaming](https://spark.apache.org/streaming/)
- [FHIR Specification](https://www.hl7.org/fhir/)
- [HL7 Standards](https://www.hl7.org/)
- [HIPAA Guidelines](https://www.hhs.gov/hipaa/)

## Contact

For questions or issues, please open a GitHub issue.
