# Testing Guide for Healthcare Streaming Infrastructure

Complete guide for testing the healthcare streaming platform including local tests, AWS integration tests, performance benchmarking, and CI/CD pipelines.

## Table of Contents

- [Quick Start](#quick-start)
- [Prerequisites](#prerequisites)
- [Local Testing](#local-testing)
- [AWS Testing](#aws-testing)
- [Performance Benchmarking](#performance-benchmarking)
- [CI/CD Pipeline](#cicd-pipeline)
- [Test Coverage](#test-coverage)
- [Troubleshooting](#troubleshooting)

## Quick Start

Run all tests locally:

```bash
# Run unit tests
make test-unit

# Run integration tests (requires Docker)
make test-integration

# Run complete local test suite
make test-local

# Run performance benchmarks
make benchmark
```

## Prerequisites

### Required Software

- **Python 3.9+**
- **Docker & Docker Compose**
- **Git**

### Optional Tools

- **AWS CLI** (for AWS integration tests)
- **Kafka CLI tools** (for advanced testing)
- **Trivy** (for container security scanning)

### Installation

```bash
# Install Python dependencies
make install

# Install dev dependencies
make install-dev

# Verify installation
python3 --version
docker --version
docker-compose --version
```

## Local Testing

### Unit Tests

Unit tests validate individual components without external dependencies.

```bash
# Run all unit tests
pytest tests/unit/ -v

# Run specific test file
pytest tests/unit/test_kafka_producer.py -v

# Run with coverage
pytest tests/unit/ --cov=. --cov-report=html

# Using make
make test-unit
```

**Unit test categories:**
- `test_kafka_producer.py` - Kafka producer functionality
- `test_hl7_parser.py` - HL7 v2 message parsing
- `test_fhir_generator.py` - FHIR R4 patient generation

### Integration Tests

Integration tests require running services (Docker Compose).

```bash
# Start services
docker-compose up -d

# Wait for services to be ready
sleep 30

# Run integration tests
pytest tests/integration/ -v -m integration

# Stop services
docker-compose down -v

# Using make (handles Docker lifecycle)
make test-integration
```

**Integration test categories:**
- End-to-end produce/consume flow
- Flink job execution
- Spark streaming validation
- Service health checks

### Local Test Script

Comprehensive test script that validates the entire stack:

```bash
# Run all local tests
./scripts/run_local_tests.sh

# With automatic cleanup
CLEANUP=true ./scripts/run_local_tests.sh
```

**Test coverage:**
- ✓ Docker Compose services health
- ✓ Zookeeper connectivity
- ✓ Kafka broker functionality
- ✓ Flink job manager
- ✓ Spark streaming
- ✓ Data producers/consumers
- ✓ Healthcare data generators

## AWS Testing

### Prerequisites

```bash
# Configure AWS credentials
aws configure

# Set AWS region (optional)
export AWS_REGION=us-east-1
```

### Running AWS Tests

```bash
# Run AWS integration tests
./scripts/run_aws_tests.sh

# With resource cleanup
CLEANUP_RESOURCES=true ./scripts/run_aws_tests.sh

# Using make
make test-aws
```

**AWS components tested:**
- ✓ AWS credentials validation
- ✓ Kinesis stream creation/access
- ✓ Lambda function invocation
- ✓ MSK cluster connectivity
- ✓ IoT Core device connectivity
- ✓ Glue Streaming jobs

### Cost Estimation

The AWS test script provides cost estimates:

```
Estimated Monthly Costs:
  - Kinesis Stream (1 shard): $25
  - MSK Cluster (kafka.t3.small x3): $150
  - Lambda (1M requests): $0.20
  - IoT Core (1M messages): $1.00
  - Glue Streaming: $0.44/DPU-hour
```

## Performance Benchmarking

### Running Benchmarks

```bash
# Run full benchmark suite
./scripts/performance_benchmark.sh

# Using make
make benchmark
```

### Metrics Collected

**Kafka Metrics:**
- Producer throughput (messages/sec, MB/sec)
- Consumer lag
- Average latency

**Flink Metrics:**
- Job status
- Processing rate
- Records in/out per second

**Spark Metrics:**
- Application status
- Batch duration
- Processing time

**System Metrics:**
- CPU utilization
- Memory usage
- Disk I/O

### Benchmark Results

Results are saved to `benchmarks/YYYYMMDD_HHMMSS.json`:

```json
{
  "timestamp": "2023-12-31T12:00:00Z",
  "configuration": {
    "kafka_broker": "localhost:9092",
    "num_messages": 10000
  },
  "results": {
    "kafka_producer": {
      "records_per_second": 5000.0,
      "mb_per_second": 0.5,
      "avg_latency_ms": 2.5
    }
  }
}
```

## CI/CD Pipeline

### GitHub Actions Workflow

The project includes a comprehensive CI/CD workflow: `.github/workflows/streaming-tests.yml`

**Pipeline stages:**

1. **Linting** - Code quality checks (flake8, black, isort)
2. **Unit Tests** - Run all unit tests with coverage
3. **Integration Tests** - Docker-based integration tests
4. **Security Scanning** - Container vulnerability scanning
5. **Performance Tests** - Basic throughput validation
6. **AWS Deployment** - Deploy to AWS (main branch only)

### Triggering the Pipeline

```bash
# Push to trigger CI
git push origin main

# Manual trigger via GitHub UI
# Go to Actions tab → Select workflow → Run workflow
```

### Pipeline Artifacts

On failure, the pipeline uploads:
- Test logs
- Coverage reports
- Container logs
- Benchmark results

## Test Coverage

### Coverage Reports

```bash
# Generate HTML coverage report
pytest --cov=. --cov-report=html

# View report
open htmlcov/index.html

# Terminal coverage
pytest --cov=. --cov-report=term-missing
```

### Coverage Targets

- **Unit Tests:** >80% coverage
- **Integration Tests:** Core workflows validated
- **Critical paths:** 100% coverage

## Data Validation

### Running Data Validation

```bash
# Validate healthcare data formats
./scripts/data_validation.sh

# Using make
make data-validation
```

**Validation checks:**
- ✓ FHIR R4 schema compliance
- ✓ HL7 v2 message structure
- ✓ Medical device data format
- ✓ Patient data de-identification
- ✓ HIPAA compliance checklist

## Security Scanning

### Running Security Scans

```bash
# Run security scan
./scripts/security_scan.sh

# Using make
make security-scan
```

**Security checks:**
- ✓ Hardcoded credentials scan
- ✓ TLS/SSL configuration
- ✓ IAM roles validation
- ✓ HIPAA compliance review
- ✓ Network security
- ✓ Container vulnerabilities
- ✓ Dependency vulnerabilities

## Troubleshooting

### Common Issues

#### Docker Services Not Starting

```bash
# Check Docker is running
docker ps

# View logs
docker-compose logs

# Restart services
docker-compose down -v
docker-compose up -d
```

#### Kafka Connection Refused

```bash
# Check Kafka is running
docker-compose ps | grep kafka

# Verify port is accessible
nc -zv localhost 9092

# Wait longer for startup
sleep 60
```

#### Test Failures Due to Timing

```bash
# Increase wait time in tests
export KAFKA_STARTUP_WAIT=60

# Or edit pytest.ini to add longer timeouts
```

#### AWS Credentials Not Found

```bash
# Configure AWS credentials
aws configure

# Or set environment variables
export AWS_ACCESS_KEY_ID=your_key
export AWS_SECRET_ACCESS_KEY=your_secret
export AWS_DEFAULT_REGION=us-east-1
```

#### Missing Python Dependencies

```bash
# Reinstall dependencies
make clean
make install

# Or manually
pip install -r requirements.txt
pip install pytest pytest-cov kafka-python requests
```

### Debug Mode

Enable verbose output:

```bash
# Pytest verbose mode
pytest -vv -s

# Bash script debug mode
bash -x scripts/run_local_tests.sh
```

### Getting Help

- **Issues:** Open an issue on GitHub
- **Documentation:** See `docs/` directory
- **Examples:** Check `tests/fixtures/` for sample data

## Advanced Topics

### Custom Test Configuration

Edit `pytest.ini` to customize test behavior:

```ini
[pytest]
testpaths = tests
markers =
    unit: Unit tests
    integration: Integration tests
    slow: Slow running tests
    aws: AWS integration tests
```

### Parallel Test Execution

```bash
# Install pytest-xdist
pip install pytest-xdist

# Run tests in parallel
pytest -n auto
```

### Test Data Generation

```bash
# Generate sample FHIR patients
python3 healthcare_data/fhir_patient_generator.py

# Generate HL7 messages
python3 healthcare_data/hl7_message_simulator.py

# Generate vital signs
python3 kafka_streams/producer_medical_devices.py
```

## Continuous Improvement

### Adding New Tests

1. Create test file in `tests/unit/` or `tests/integration/`
2. Follow naming convention: `test_*.py`
3. Add appropriate markers: `@pytest.mark.unit` or `@pytest.mark.integration`
4. Run tests: `pytest tests/`
5. Update coverage targets

### Performance Baselines

Establish baseline metrics:

```bash
# Run benchmark multiple times
for i in {1..5}; do
    ./scripts/performance_benchmark.sh
done

# Compare results
python3 scripts/analyze_benchmarks.py benchmarks/
```

---

**For more information:**
- [Performance Tuning Guide](docs/PERFORMANCE_TUNING.md)
- [Architecture Documentation](../README.md)
- [Contributing Guidelines](../CONTRIBUTING.md)
