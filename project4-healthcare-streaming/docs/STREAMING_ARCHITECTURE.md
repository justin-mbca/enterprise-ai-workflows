# Streaming Architecture Documentation

## Overview

The Medical Streaming Infrastructure is designed to process real-time healthcare data from medical devices, validate the data, detect critical conditions, and store it for analytics. The architecture follows a lambda architecture pattern with both batch and stream processing capabilities.

## Architecture Diagram

```
┌─────────────────┐
│ Medical Devices │
│  (IoT Sensors)  │
└────────┬────────┘
         │
         ▼
┌─────────────────────────────────────────────────────┐
│           Data Ingestion Layer                       │
│  ┌──────────┐  ┌──────────┐  ┌──────────────┐     │
│  │  Kafka   │  │ Kinesis  │  │  AWS IoT     │     │
│  │ Topics   │  │ Streams  │  │  Core (MQTT) │     │
│  └──────────┘  └──────────┘  └──────────────┘     │
└─────────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────┐
│          Stream Processing Layer                     │
│  ┌──────────┐  ┌──────────┐  ┌──────────────┐     │
│  │  Apache  │  │  Apache  │  │    Spark     │     │
│  │  Flink   │  │  Kafka   │  │  Structured  │     │
│  │  CEP     │  │  Streams │  │  Streaming   │     │
│  └──────────┘  └──────────┘  └──────────────┘     │
└─────────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────┐
│              Data Storage Layer                      │
│  ┌──────────┐  ┌──────────┐  ┌──────────────┐     │
│  │TimescaleDB│ │PostgreSQL│  │  S3 / Delta  │     │
│  │(Timeseries│ │  (OLTP)  │  │   Lake       │     │
│  └──────────┘  └──────────┘  └──────────────┘     │
└─────────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────┐
│           Analytics & Monitoring                     │
│  ┌──────────┐  ┌──────────┐  ┌──────────────┐     │
│  │ Grafana  │  │Prometheus│  │  CloudWatch  │     │
│  └──────────┘  └──────────┘  └──────────────┘     │
└─────────────────────────────────────────────────────┘
```

## Component Responsibilities

### 1. Data Ingestion Layer

#### Apache Kafka
- **Purpose**: Primary event streaming platform for high-throughput medical device data
- **Configuration**: 3-broker cluster with replication factor of 3
- **Topics**:
  - `medical-devices-ecg`: ECG/EKG monitor data
  - `medical-devices-glucose`: Blood glucose readings
  - `medical-devices-vitals`: General vitals (BP, SpO2, temp)
  - `medical-alerts-critical`: High-priority alerts
  - `hl7-messages-raw`: Raw HL7 v2.x messages
- **Throughput**: 10,000+ messages/second per topic
- **Retention**: 7 days (configurable per topic)

#### AWS Kinesis Data Streams
- **Purpose**: Cloud-native alternative for AWS deployments
- **Configuration**: Auto-scaling shards based on throughput
- **Integration**: Direct integration with Lambda, Firehose, and Glue
- **Encryption**: KMS encryption at rest

#### AWS IoT Core
- **Purpose**: MQTT protocol support for medical device connectivity
- **Features**: Device registry, thing shadows, rules engine
- **Security**: X.509 certificates, IoT policies

### 2. Stream Processing Layer

#### Apache Flink
- **Purpose**: Real-time stream processing with exactly-once semantics
- **Use Cases**:
  - Complex Event Processing (CEP) for pattern detection
  - Windowed aggregations (tumbling, sliding, session)
  - Stateful stream processing
  - Anomaly detection
- **Configuration**:
  - Parallelism: 4
  - Checkpointing: Every 60 seconds
  - State Backend: RocksDB
- **Latency**: <100ms processing latency

#### Kafka Streams
- **Purpose**: Lightweight stream processing within Kafka ecosystem
- **Use Cases**:
  - 5-minute tumbling window aggregations
  - Per-patient vitals statistics (min, max, avg)
  - Stream joins for correlating multiple device types
- **Features**:
  - Exactly-once processing semantics
  - Fault-tolerant with state stores

#### Spark Structured Streaming
- **Purpose**: Unified batch and streaming analytics
- **Use Cases**:
  - HL7 v2.x message parsing and transformation
  - FHIR R4 resource processing
  - Delta Lake writes for data lakehouse
  - ML model inference on streaming data
- **Configuration**:
  - Micro-batch interval: 5-10 seconds
  - Checkpointing: S3-backed
  - Adaptive query execution enabled

### 3. Data Storage Layer

#### TimescaleDB
- **Purpose**: Time-series database for medical readings
- **Features**:
  - Automatic partitioning (hypertables)
  - Compression for older data
  - Continuous aggregates for pre-computed stats
- **Schema**: Optimized for time-series queries on patient vitals

#### PostgreSQL
- **Purpose**: Operational data store for transactional data
- **Use Cases**:
  - Device registry
  - Patient metadata
  - Alert history

#### S3 / Delta Lake
- **Purpose**: Long-term storage and analytics
- **Features**:
  - Parquet format with Snappy compression
  - Partitioned by date and patient_id
  - ACID transactions with Delta Lake
  - Lifecycle policies (transition to Glacier after 90 days)

### 4. Analytics & Monitoring

#### Grafana
- **Purpose**: Visualization and dashboards
- **Dashboards**:
  - Kafka cluster health
  - Flink job metrics
  - Spark streaming statistics
  - Medical device data metrics

#### Prometheus
- **Purpose**: Metrics collection and alerting
- **Metrics**:
  - Kafka consumer lag
  - Flink backpressure
  - Processing latency
  - Error rates

## Data Flow

### Real-Time Processing Flow

1. **Ingestion**: Medical device sends data via IoT protocol (MQTT/HTTP)
2. **Validation**: Initial schema validation at ingestion
3. **Topic Routing**: Data routed to appropriate Kafka topic based on device type
4. **Stream Processing**: 
   - Flink processes for CEP and anomaly detection
   - Kafka Streams for windowed aggregations
   - Spark for HL7/FHIR parsing
5. **Critical Alert Detection**: Abnormal vitals trigger alerts
6. **Storage**: 
   - TimescaleDB for real-time queries
   - S3 for long-term analytics
7. **Monitoring**: Metrics collected by Prometheus, visualized in Grafana

### Batch Processing Flow

1. **Data Lake**: Historical data stored in S3 (Parquet format)
2. **Spark Batch Jobs**: Daily/hourly aggregations and analytics
3. **Delta Lake**: ACID transactions and time travel
4. **Data Warehouse**: Aggregated data for BI tools

## Scalability

### Horizontal Scaling

- **Kafka**: Add more brokers and increase partition count
- **Flink**: Increase parallelism and task managers
- **Spark**: Add more worker nodes
- **Kinesis**: Increase shard count (automatic or manual)

### Vertical Scaling

- **Kafka**: Increase broker memory and CPU
- **Flink**: Increase task manager memory
- **Spark**: Increase executor memory and cores

## Fault Tolerance

### Kafka
- Replication factor of 3
- min.insync.replicas = 2
- Automatic leader election

### Flink
- Checkpointing every 60 seconds
- Savepoints for manual recovery
- Restart strategy: fixed-delay with 3 attempts

### Spark
- Checkpoint-based recovery
- Write-ahead logs
- Automatic driver restart

## Security

### Encryption
- **In Transit**: TLS 1.2+ for all communication
- **At Rest**: AES-256 encryption for S3, KMS for Kinesis

### Access Control
- **Kafka**: ACLs for topic-level access
- **AWS**: IAM roles and policies
- **Database**: Role-based access control

### Compliance
- **HIPAA**: PHI encryption, audit logging, access controls
- **Data Retention**: 7-year retention for compliance

## Performance Characteristics

| Metric | Target | Actual |
|--------|--------|--------|
| Kafka Throughput | 10K msg/s | 15K msg/s |
| Flink Latency | <100ms | 50-80ms |
| Spark Micro-batch | 5-10s | 8s avg |
| End-to-End Latency | <5s | 3-4s |
| Data Availability | 99.9% | 99.95% |

## Cost Optimization

### Development Environment
- Use smaller instance types
- Reduce retention periods
- Disable enhanced monitoring
- **Estimated Cost**: $500-800/month

### Production Environment
- Right-size instances based on metrics
- Use reserved instances for predictable workloads
- Implement auto-scaling
- Archive old data to Glacier
- **Estimated Cost**: $3,000-5,000/month

## Future Enhancements

1. **Machine Learning Integration**
   - Real-time ML inference on streaming data
   - Predictive analytics for patient deterioration
   - Anomaly detection using autoencoders

2. **Advanced CEP**
   - Sepsis detection algorithms
   - Multi-parameter trend analysis
   - Medication adherence monitoring

3. **Multi-Region Deployment**
   - Active-active replication
   - Geographic redundancy
   - Disaster recovery

4. **Enhanced Security**
   - Kafka encryption in transit
   - Fine-grained access control
   - Data masking for non-production environments
