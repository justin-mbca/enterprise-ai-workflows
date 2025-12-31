# 🌊 Project 4: Real-Time Healthcare Data Streaming

Production-grade streaming data platform for medical device integration and real-time healthcare analytics.

## 🏗️ Architecture Overview

This project demonstrates a complete streaming data infrastructure capable of processing high-volume medical device data in real-time with HIPAA-compliant configurations.

```
Medical Devices (IoT) → Kafka/Kinesis → Stream Processing (Flink/Spark) → Data Lake/Warehouse
                                ↓
                          Real-time Analytics & Alerts
```

### Components

1. **Apache Kafka**: Distributed event streaming (1M+ messages/sec capability)
2. **Apache Flink**: Real-time stream processing with Complex Event Processing (CEP)
3. **Spark Streaming**: Structured streaming for HL7/FHIR data processing
4. **AWS Streaming**: Kinesis, MSK, IoT Core, Glue Streaming, Lambda
5. **Healthcare Data**: HL7 v2.x, FHIR R4, OMOP CDM data generation

## 🚀 Quick Start

### Prerequisites

- Docker Desktop 20.10+
- Docker Compose 2.0+
- Python 3.9+
- AWS CLI (for cloud deployment)
- Terraform 1.5+ (for infrastructure provisioning)
- 8GB+ RAM available
- 20GB+ free disk space

### Local Development Stack

Start the complete streaming platform locally:

```bash
cd project4-healthcare-streaming

# Start Kafka cluster, Flink, Spark, and databases
docker-compose up -d

# Verify all services are running
docker-compose ps

# View logs
docker-compose logs -f kafka-broker-1
```

### Generate Healthcare Data

```bash
# Install dependencies
pip install -r healthcare_data/requirements.txt

# Generate synthetic FHIR patients
python healthcare_data/fhir_patient_generator.py --count 1000

# Simulate medical device data
python healthcare_data/medical_device_iot_simulator.py --devices 10 --duration 300

# Generate HL7 messages
python healthcare_data/hl7_message_simulator.py --rate 100
```

### Run Kafka Streaming Pipeline

```bash
# Install Kafka dependencies
pip install -r kafka_streams/requirements.txt

# Create topics
python kafka_streams/setup_topics.py

# Start producer (simulates medical devices)
python kafka_streams/producer_medical_devices.py --rate 1000

# Start consumer (processes and validates data)
python kafka_streams/consumer_realtime_processing.py

# Run stream aggregations
python kafka_streams/streams_aggregation.py
```

### Run Flink Processing

```bash
# Build Flink Docker image
docker build -t medical-flink:latest -f flink_processing/Dockerfile.flink .

# Submit Flink job
docker exec -it flink-jobmanager flink run -py medical_data_processor.py
```

### Run Spark Streaming

```bash
# Install Spark dependencies
pip install -r spark_streaming/requirements.txt

# Submit Spark Structured Streaming job
./spark_streaming/spark_submit_config.sh
```

## 📊 Healthcare Use Cases

### Real-Time Patient Monitoring
- Continuous vitals monitoring (ECG, BP, glucose, SpO2)
- Automated alerting for abnormal readings
- Trend detection and predictive analytics

### Medical Device Integration
- HL7 v2.x ORU^R01 (Observation Results) processing
- FHIR R4 Observation resources
- Device data validation and normalization

### Clinical Event Processing
- Sepsis detection using SIRS criteria
- Cardiac event identification
- Medication adherence monitoring

### Remote Patient Monitoring (RPM)
- Home medical device data collection
- Real-time physician alerts
- Longitudinal patient data analysis

## 🔧 Technology Stack

### Streaming Platforms
- **Apache Kafka 3.6**: Event streaming backbone
- **Apache Flink 1.17**: Real-time stream processing
- **Apache Spark 3.5**: Structured streaming and batch processing

### AWS Services
- **Amazon MSK**: Managed Kafka service
- **Kinesis Data Streams**: Real-time data ingestion
- **Kinesis Data Firehose**: Serverless data delivery
- **AWS Glue Streaming**: Continuous ETL
- **AWS Lambda**: Event-driven processing
- **AWS IoT Core**: Medical device connectivity (MQTT)
- **DynamoDB**: Device registry and metadata
- **S3**: Data lake storage

### Data Storage
- **PostgreSQL**: Operational data store
- **TimescaleDB**: Time-series data
- **Delta Lake**: Analytical data lake
- **Redis**: Caching and state management

### Monitoring
- **Prometheus**: Metrics collection
- **Grafana**: Visualization and dashboards
- **CloudWatch**: AWS monitoring

## 📁 Project Structure

```
project4-healthcare-streaming/
├── README.md                          # This file
├── docker-compose.yml                 # Local development stack
│
├── kafka_streams/                     # Kafka streaming components
│   ├── docker-compose.kafka.yaml     # Kafka cluster configuration
│   ├── kafka_topics_config.json      # Topic configurations
│   ├── producer_medical_devices.py   # Medical device data producer
│   ├── consumer_realtime_processing.py # Real-time consumer
│   ├── streams_aggregation.py        # Windowed aggregations
│   └── requirements.txt
│
├── flink_processing/                  # Apache Flink jobs
│   ├── Dockerfile.flink              # Flink with PyFlink
│   ├── medical_data_processor.py     # Main streaming job
│   ├── flink_job_definition.yaml     # Job configuration
│   ├── window_aggregations.py        # Advanced windowing
│   ├── cep_patterns.py               # Complex Event Processing
│   └── requirements.txt
│
├── spark_streaming/                   # Spark Structured Streaming
│   ├── structured_streaming_hl7.py   # HL7 message processing
│   ├── spark_submit_config.sh        # Job submission script
│   ├── checkpoint_management.py      # Checkpoint utilities
│   ├── fhir_streaming_etl.py         # FHIR R4 ETL
│   ├── streaming_ml_inference.py     # Real-time ML inference
│   └── requirements.txt
│
├── aws_streaming/                     # AWS streaming components
│   ├── kinesis_producer.py           # Kinesis producer
│   ├── kinesis_consumer.py           # Kinesis consumer
│   ├── glue_streaming_etl.py         # Glue Streaming ETL
│   ├── lambda_iot_medical_devices.py # IoT Core Lambda
│   ├── firehose_delivery_config.json # Firehose configuration
│   └── requirements.txt
│
├── healthcare_data/                   # Data generation and simulation
│   ├── fhir_patient_generator.py     # FHIR R4 patient generator
│   ├── hl7_message_simulator.py      # HL7 v2.x simulator
│   ├── medical_device_iot_simulator.py # IoT device simulator
│   ├── synthetic_data_generator.py   # Comprehensive data generator
│   ├── omop_schema_examples/         # OMOP CDM sample data
│   └── requirements.txt
│
├── terraform_aws/                     # AWS infrastructure as code
│   ├── main.tf                       # Main configuration
│   ├── variables.tf                  # Input variables
│   ├── kinesis.tf                    # Kinesis resources
│   ├── lambda_streaming.tf           # Lambda functions
│   ├── glue_streaming.tf             # Glue jobs
│   ├── msk_kafka.tf                  # Amazon MSK
│   ├── iot_core.tf                   # IoT Core
│   ├── dynamodb.tf                   # DynamoDB tables
│   ├── s3_data_lake.tf               # S3 data lake
│   └── outputs.tf                    # Outputs
│
├── monitoring/                        # Observability
│   ├── prometheus_config.yml         # Prometheus configuration
│   ├── alerting_rules.yml            # Alert definitions
│   └── grafana_dashboards/           # Grafana dashboards
│
├── docs/                              # Documentation
│   ├── STREAMING_ARCHITECTURE.md     # Architecture deep-dive
│   ├── KAFKA_GUIDE.md                # Kafka guide
│   ├── FLINK_GUIDE.md                # Flink guide
│   └── SPARK_STREAMING_GUIDE.md      # Spark Streaming guide
│
└── tests/                             # Testing
    ├── test_kafka_producer.py        # Kafka producer tests
    ├── test_hl7_parser.py            # HL7 parser tests
    └── integration/                   # Integration tests
        └── test_end_to_end.py
```

## 🔒 Security & Compliance

### HIPAA Compliance
- **Encryption in Transit**: TLS 1.2+ for all data transmission
- **Encryption at Rest**: AES-256 encryption for stored data
- **Access Control**: IAM roles and policies, principle of least privilege
- **Audit Logging**: Comprehensive logging of all data access
- **Data Anonymization**: PHI de-identification in non-production environments

### Security Measures
- No hardcoded credentials (AWS Secrets Manager, environment variables)
- VPC isolation for AWS resources
- Security groups with minimal required ports
- Regular security scanning (CodeQL, dependency scanning)
- Monitoring and alerting for suspicious activity

## ⚡ Performance Characteristics

### Throughput
- **Kafka**: 10,000+ messages/second per topic
- **Flink**: <100ms processing latency
- **Spark**: 5-10 second micro-batch intervals
- **Kinesis**: 1,000 records/second per shard

### Scalability
- Horizontal scaling via partitions/shards
- Auto-scaling for AWS Lambda and Kinesis
- Kubernetes deployment ready for Flink/Spark

### Fault Tolerance
- Kafka replication factor: 3
- Flink checkpointing: Every 60 seconds
- Spark checkpointing: S3-backed
- Automatic recovery from failures

## 💰 Cost Estimates (AWS)

**Development Environment** (8 hours/day, 20 days/month):
- Amazon MSK (kafka.m5.large, 3 brokers): ~$450/month
- Kinesis Data Streams (5 shards): ~$75/month
- Lambda (1M invocations): ~$5/month
- S3 Storage (100GB): ~$2.30/month
- DynamoDB (on-demand): ~$10/month
- **Total: ~$542/month**

**Production Environment** (24/7):
- Amazon MSK (kafka.m5.xlarge, 6 brokers): ~$2,600/month
- Kinesis Data Streams (20 shards): ~$300/month
- Glue Streaming (2 DPUs): ~$880/month
- Lambda: ~$50/month
- S3 Storage (1TB): ~$23/month
- DynamoDB (provisioned): ~$200/month
- **Total: ~$4,053/month**

*Note: Costs vary by region, usage patterns, and data volume*

## 🧪 Testing

### Unit Tests
```bash
pip install pytest pytest-mock
pytest tests/test_kafka_producer.py -v
pytest tests/test_hl7_parser.py -v
```

### Integration Tests
```bash
# Requires Docker Compose stack running
pytest tests/integration/test_end_to_end.py -v
```

## 📈 Monitoring & Observability

### Access Monitoring Dashboards

**Grafana** (Default credentials: admin/admin):
```bash
open http://localhost:3000
```

**Kafka UI**:
```bash
open http://localhost:8080
```

**Prometheus**:
```bash
open http://localhost:9090
```

### Key Metrics
- Kafka consumer lag
- Flink job backpressure
- Spark streaming batch duration
- Message processing latency
- Error rates and DLQ messages

## 🚢 Deployment

### AWS Deployment

```bash
cd terraform_aws

# Initialize Terraform
terraform init

# Review infrastructure plan
terraform plan -var-file=dev.tfvars

# Deploy infrastructure
terraform apply -var-file=dev.tfvars

# Get outputs (Kinesis stream names, MSK endpoints, etc.)
terraform output
```

### Kubernetes Deployment (Optional)

```bash
# Deploy Flink on Kubernetes
kubectl apply -f k8s/flink-deployment.yaml

# Deploy Spark on Kubernetes
kubectl apply -f k8s/spark-deployment.yaml
```

## 🔧 Configuration

### Environment Variables

Create `.env` file:
```bash
# Kafka Configuration
KAFKA_BOOTSTRAP_SERVERS=localhost:9092
KAFKA_SECURITY_PROTOCOL=PLAINTEXT

# AWS Configuration
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=your-key-id
AWS_SECRET_ACCESS_KEY=your-secret-key

# Database Configuration
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=medical_data
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres

# Application Configuration
LOG_LEVEL=INFO
MESSAGE_RATE=1000
ALERT_THRESHOLD_HIGH_BP=140
```

## 📚 Healthcare Data Standards

### HL7 v2.x
- ADT^A01: Patient Admission
- ADT^A08: Patient Update
- ORU^R01: Observation Results (Lab/Vitals)
- ORM^O01: Order Messages

### FHIR R4
- Patient: Demographics and identifiers
- Observation: Vitals, labs, and device readings
- Device: Medical device metadata
- Encounter: Healthcare encounters

### OMOP CDM
- Common Data Model for observational health data
- Standardized vocabulary (SNOMED, LOINC, RxNorm)

## 🐛 Troubleshooting

### Kafka Issues

**Consumer lag too high:**
```bash
# Check consumer group lag
kafka-consumer-groups.sh --bootstrap-server localhost:9092 --group medical-consumers --describe

# Increase consumer parallelism (add more partition consumers)
```

**Out of memory errors:**
```bash
# Increase Kafka heap size in docker-compose.yml
KAFKA_HEAP_OPTS: "-Xmx2G -Xms2G"
```

### Flink Issues

**Job failing with checkpointing errors:**
```bash
# Check state backend size
# Increase checkpoint timeout in flink_job_definition.yaml
```

**High backpressure:**
```bash
# Access Flink Web UI
open http://localhost:8081

# Scale up parallelism or optimize operators
```

### Spark Issues

**Checkpoint directory errors:**
```bash
# Clean checkpoint directory
hdfs dfs -rm -r /checkpoints/medical-streaming

# Or locally
rm -rf /tmp/spark-checkpoints/medical-streaming
```

## 🤝 Contributing

This is a demonstration project for portfolio purposes. For questions or suggestions:
- Open an issue on GitHub
- Contact: [Your contact information]

## 📄 License

This project is for educational and portfolio demonstration purposes.

## 🎯 Learning Outcomes

By exploring this project, you'll understand:
- Building production streaming data platforms
- Processing real-time healthcare data at scale
- Implementing HIPAA-compliant data pipelines
- Using Apache Kafka, Flink, and Spark together
- Deploying streaming infrastructure on AWS
- Healthcare data standards (HL7, FHIR, OMOP)
- Complex Event Processing (CEP) patterns
- Real-time ML inference on streaming data
- Infrastructure as Code with Terraform
- Monitoring and observability best practices

## 📞 Support

For issues with:
- **Kafka**: Check logs with `docker-compose logs kafka-broker-1`
- **Flink**: Access Web UI at http://localhost:8081
- **Spark**: Check Spark UI at http://localhost:4040
- **AWS**: Review CloudWatch logs and metrics

## 🔗 References

- [Apache Kafka Documentation](https://kafka.apache.org/documentation/)
- [Apache Flink Documentation](https://flink.apache.org/docs/)
- [Spark Structured Streaming](https://spark.apache.org/docs/latest/structured-streaming-programming-guide.html)
- [HL7 v2.x Standards](https://www.hl7.org/implement/standards/product_brief.cfm?product_id=185)
- [FHIR R4 Specification](https://www.hl7.org/fhir/)
- [OMOP Common Data Model](https://ohdsi.github.io/CommonDataModel/)
- [AWS Streaming Services](https://aws.amazon.com/streaming-data/)
