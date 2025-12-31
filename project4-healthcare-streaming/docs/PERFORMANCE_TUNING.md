# Performance Tuning Guide

Comprehensive guide for optimizing healthcare streaming infrastructure performance, including Kafka, Flink, Spark tuning, and cost optimization.

## Table of Contents

- [Overview](#overview)
- [Kafka Performance Tuning](#kafka-performance-tuning)
- [Flink Optimization](#flink-optimization)
- [Spark Streaming Tuning](#spark-streaming-tuning)
- [Network Optimization](#network-optimization)
- [Storage Optimization](#storage-optimization)
- [Cost Optimization](#cost-optimization)
- [Monitoring & Profiling](#monitoring--profiling)

## Overview

### Performance Goals

- **Throughput:** >10,000 messages/second
- **Latency:** <100ms end-to-end
- **Availability:** 99.9% uptime
- **Cost:** Minimize cloud spend

### Key Metrics

| Metric | Target | Warning | Critical |
|--------|--------|---------|----------|
| Producer Latency | <50ms | >100ms | >500ms |
| Consumer Lag | <1000 | >10000 | >100000 |
| CPU Usage | <70% | >80% | >90% |
| Memory Usage | <80% | >90% | >95% |

## Kafka Performance Tuning

### Producer Configuration

**High Throughput Settings:**

```properties
# Batching
batch.size=32768                  # 32KB batches
linger.ms=10                      # Wait 10ms to batch
compression.type=snappy           # Fast compression

# Buffer settings
buffer.memory=67108864            # 64MB buffer
max.in.flight.requests.per.connection=5

# Reliability
acks=1                            # Leader acknowledgment (balance)
retries=3
```

**Low Latency Settings:**

```properties
# Immediate send
linger.ms=0
batch.size=16384                  # Smaller batches
compression.type=none             # No compression delay

# Network
buffer.memory=33554432            # 32MB (smaller)
acks=1
```

**Reliable Settings (HIPAA compliance):**

```properties
# Durability
acks=all                          # All replicas must ack
retries=Integer.MAX_VALUE
enable.idempotence=true

# Ordering
max.in.flight.requests.per.connection=1

# Compression
compression.type=snappy
```

### Consumer Configuration

```properties
# Fetch settings
fetch.min.bytes=1048576           # 1MB minimum fetch
fetch.max.wait.ms=500             # Wait up to 500ms
max.partition.fetch.bytes=1048576 # 1MB per partition

# Processing
max.poll.records=500              # Process 500 records at once
max.poll.interval.ms=300000       # 5 minutes

# Commit strategy
enable.auto.commit=false          # Manual commit for reliability
auto.offset.reset=earliest
```

### Broker Configuration

```properties
# Replication
min.insync.replicas=2             # Minimum replicas for write
default.replication.factor=3      # Data redundancy
unclean.leader.election.enable=false

# Log settings
log.segment.bytes=1073741824      # 1GB segments
log.retention.hours=168           # 7 days retention
log.retention.check.interval.ms=300000

# Performance
num.network.threads=8
num.io.threads=8
socket.send.buffer.bytes=102400
socket.receive.buffer.bytes=102400
```

### Topic Configuration

```bash
# Create high-throughput topic
kafka-topics --create \
  --bootstrap-server localhost:9092 \
  --topic medical-devices-vitals \
  --partitions 10 \
  --replication-factor 3 \
  --config compression.type=snappy \
  --config min.insync.replicas=2 \
  --config retention.ms=604800000
```

**Partitioning Strategy:**

- **Partitions = (Target Throughput / Partition Throughput)**
- Example: 100MB/s target ÷ 10MB/s per partition = 10 partitions
- Consider: 1 partition per consumer for parallel processing

## Flink Optimization

### Parallelism Configuration

```yaml
# flink-conf.yaml
taskmanager.numberOfTaskSlots: 4
parallelism.default: 4
```

```java
// Job-level parallelism
env.setParallelism(8);

// Operator-level parallelism
stream
  .map(new MyMapper())
  .setParallelism(16)  // Scale this operator
  .keyBy(x -> x.getKey())
  .window(TumblingProcessingTimeWindows.of(Time.seconds(60)))
  .reduce(new MyReducer())
  .setParallelism(8);
```

### Memory Configuration

```yaml
# Task Manager memory
taskmanager.memory.process.size: 4096m
taskmanager.memory.managed.fraction: 0.4
taskmanager.memory.network.fraction: 0.2

# JVM settings
taskmanager.memory.jvm-metaspace.size: 256m
taskmanager.memory.jvm-overhead.fraction: 0.1
```

### Checkpointing

```java
// Enable checkpointing
env.enableCheckpointing(60000); // Every 60 seconds

// Checkpoint configuration
CheckpointConfig config = env.getCheckpointConfig();
config.setCheckpointingMode(CheckpointingMode.EXACTLY_ONCE);
config.setMinPauseBetweenCheckpoints(30000);
config.setCheckpointTimeout(600000);
config.setMaxConcurrentCheckpoints(1);
config.enableExternalizedCheckpoints(
    CheckpointConfig.ExternalizedCheckpointCleanup.RETAIN_ON_CANCELLATION
);
```

### State Backend

```java
// RocksDB for large state
env.setStateBackend(new EmbeddedRocksDBStateBackend());
env.getCheckpointConfig()
   .setCheckpointStorage("s3://my-bucket/checkpoints");
```

### Watermark Strategy

```java
// Bounded out-of-orderness
WatermarkStrategy
  .<Event>forBoundedOutOfOrderness(Duration.ofSeconds(5))
  .withTimestampAssigner((event, timestamp) -> event.getTimestamp());
```

## Spark Streaming Tuning

### Executor Configuration

```bash
spark-submit \
  --master spark://master:7077 \
  --deploy-mode cluster \
  --executor-memory 4G \
  --executor-cores 4 \
  --num-executors 10 \
  --driver-memory 2G \
  --conf spark.streaming.backpressure.enabled=true \
  --conf spark.streaming.kafka.maxRatePerPartition=1000 \
  my-streaming-app.jar
```

### Batch Interval

```scala
// Micro-batch interval
val streamingContext = new StreamingContext(sc, Seconds(5))

// Balance: smaller = lower latency, larger = higher throughput
// Healthcare: 5-10 seconds is typical
```

### Kafka Integration

```scala
val kafkaParams = Map[String, Object](
  "bootstrap.servers" -> "localhost:9092",
  "key.deserializer" -> classOf[StringDeserializer],
  "value.deserializer" -> classOf[StringDeserializer],
  "group.id" -> "healthcare-consumer-group",
  "auto.offset.reset" -> "latest",
  "enable.auto.commit" -> (false: java.lang.Boolean),
  // Performance tuning
  "fetch.min.bytes" -> "1048576",
  "max.partition.fetch.bytes" -> "10485760"
)
```

### Structured Streaming

```scala
val df = spark
  .readStream
  .format("kafka")
  .option("kafka.bootstrap.servers", "localhost:9092")
  .option("subscribe", "medical-devices-vitals")
  .option("maxOffsetsPerTrigger", 10000)  // Throughput limit
  .option("startingOffsets", "latest")
  .load()

// Trigger configuration
df.writeStream
  .trigger(Trigger.ProcessingTime("10 seconds"))  // Micro-batch
  .format("console")
  .start()
```

## Network Optimization

### TCP Tuning (Linux)

```bash
# /etc/sysctl.conf
net.core.rmem_max=134217728       # 128MB receive buffer
net.core.wmem_max=134217728       # 128MB send buffer
net.ipv4.tcp_rmem=4096 87380 134217728
net.ipv4.tcp_wmem=4096 65536 134217728
net.core.netdev_max_backlog=5000
net.ipv4.tcp_window_scaling=1

# Apply settings
sudo sysctl -p
```

### Network Topology

**Single Data Center:**
```
Producer → Load Balancer → Kafka Cluster (3+ brokers)
                          ↓
                       Flink/Spark Cluster
                          ↓
                     Storage/Sink
```

**Multi-Region:**
- Use MirrorMaker 2 for cross-region replication
- Place consumers close to brokers
- Consider network latency in SLAs

## Storage Optimization

### Kafka Storage

**Disk Configuration:**
```bash
# Use multiple disks
log.dirs=/disk1/kafka-logs,/disk2/kafka-logs,/disk3/kafka-logs

# File system
# - XFS or EXT4 (not EXT3)
# - noatime mount option
# - RAID 10 for performance + redundancy
```

**Compression:**
- **Snappy:** Good balance (recommended)
- **LZ4:** Fastest decompression
- **Gzip:** Highest compression ratio
- **ZSTD:** Best compression/speed tradeoff (Kafka 2.1+)

### State Storage (Flink)

**RocksDB Tuning:**
```yaml
# RocksDB options
state.backend.rocksdb.block.cache-size: 512mb
state.backend.rocksdb.writebuffer.size: 64mb
state.backend.rocksdb.writebuffer.count: 4
```

**Cleanup:**
```java
// TTL for state
StateTtlConfig ttlConfig = StateTtlConfig
    .newBuilder(Time.hours(24))
    .setUpdateType(StateTtlConfig.UpdateType.OnCreateAndWrite)
    .setStateVisibility(StateTtlConfig.StateVisibility.NeverReturnExpired)
    .build();

ValueStateDescriptor<MyState> descriptor = 
    new ValueStateDescriptor<>("my-state", MyState.class);
descriptor.enableTimeToLive(ttlConfig);
```

## Cost Optimization

### AWS Cost Optimization

**EC2 Instances:**
- Use Reserved Instances for base load (1-year commitment: 40% savings)
- Spot Instances for non-critical workloads (70% savings)
- Right-size instances based on metrics

**MSK (Managed Kafka):**
```
kafka.t3.small:  $0.038/hour = $27/month per broker
kafka.m5.large:  $0.210/hour = $151/month per broker

Recommendation: Start with t3.small, scale to m5.large if needed
```

**Kinesis:**
```
Shard Hour: $0.015
PUT Payload Unit: $0.014 per million

Cost = (Shards × Hours × $0.015) + (Records × $0.014/1M)
```

**Data Transfer:**
- Keep data in same region (free)
- Use VPC endpoints (no NAT gateway costs)
- Enable compression to reduce transfer volume

### Resource Right-Sizing

**Monitoring-Based Sizing:**
```bash
# Monitor CPU/memory for 1 week
# If avg < 50%: downsize
# If max > 80%: upsize

# Example: Flink Task Manager
Current: 8GB RAM, 4 cores
Actual usage: 4GB RAM, 2 cores
Recommendation: 4GB RAM, 2 cores (50% cost savings)
```

### Retention Policies

```properties
# Kafka topic retention
log.retention.hours=168           # 7 days (standard)
log.retention.bytes=1073741824    # 1GB per partition

# For high-volume topics
log.retention.hours=24            # 1 day only
```

## Monitoring & Profiling

### Key Metrics to Monitor

**Kafka:**
- Producer: `request-latency-avg`, `record-send-rate`
- Consumer: `records-lag-max`, `fetch-rate`
- Broker: `bytes-in-per-sec`, `bytes-out-per-sec`

**Flink:**
- `numRecordsInPerSecond`
- `numRecordsOutPerSecond`
- `lastCheckpointDuration`
- `numberOfFailedCheckpoints`

**Spark:**
- `streaming.totalReceivedRecords`
- `streaming.totalProcessedRecords`
- `streaming.lastCompletedBatch_processingDelay`

### Profiling Tools

```bash
# JVM profiling
-XX:+UnlockDiagnosticVMOptions
-XX:+DebugNonSafepoints
-XX:+FlightRecorder

# Async profiler (low overhead)
./profiler.sh -d 60 -f flamegraph.html <pid>
```

### Performance Testing

```bash
# Kafka throughput test
kafka-producer-perf-test \
  --topic medical-devices-vitals \
  --num-records 1000000 \
  --record-size 1024 \
  --throughput -1 \
  --producer-props bootstrap.servers=localhost:9092

# Results interpretation
# Target: >50,000 records/sec for healthcare streaming
```

## Best Practices Summary

1. **Start Small, Scale Up:** Begin with minimal resources, scale based on metrics
2. **Monitor Everything:** Implement comprehensive monitoring before optimization
3. **Test Under Load:** Use realistic data volumes and patterns
4. **Optimize Bottlenecks:** Profile to find actual bottlenecks, don't guess
5. **Document Changes:** Track configuration changes and their impact
6. **Regular Review:** Review performance metrics weekly, optimize monthly

## Healthcare-Specific Considerations

### HIPAA Compliance Impact

- Encryption adds ~5-10% latency overhead
- Audit logging increases storage by ~20%
- Access controls add minimal performance impact

### Medical Device Data Patterns

- **High frequency:** 1-10 samples/second per device
- **Burst patterns:** Alerts generate traffic spikes
- **Small messages:** Typically 100-500 bytes
- **Time-sensitive:** Real-time alerts critical

### Recommended Configuration

```properties
# Healthcare streaming optimized for:
# - 1000 devices
# - 5 samples/second per device
# - 99.9% availability
# - <100ms latency

# Kafka
partitions=10
replication.factor=3
compression.type=snappy
acks=all

# Flink
parallelism=8
checkpoint.interval=60s

# Spark
batch.interval=5s
max.rate.per.partition=500
```

---

**Related Documentation:**
- [Testing Guide](TESTING.md)
- [Architecture Overview](../README.md)
- [Security Guide](docs/SECURITY.md)
