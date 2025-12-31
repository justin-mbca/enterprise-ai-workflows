#!/bin/bash
#
# Performance Benchmarking Script for Healthcare Streaming
# Measures throughput, latency, and resource utilization
#

set -e

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Configuration
KAFKA_BROKER=${KAFKA_BROKER:-"localhost:9092"}
KAFKA_TOPIC=${KAFKA_TOPIC:-"medical-devices-vitals"}
NUM_MESSAGES=${NUM_MESSAGES:-10000}
NUM_THREADS=${NUM_THREADS:-1}
RECORD_SIZE=${RECORD_SIZE:-100}

# Output directory
BENCHMARK_DIR="benchmarks"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
OUTPUT_FILE="$BENCHMARK_DIR/${TIMESTAMP}.json"

print_info() {
    echo -e "${YELLOW}ℹ${NC} $1"
}

print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

# Create benchmark directory
mkdir -p "$BENCHMARK_DIR"

# Initialize results JSON
init_results() {
    cat > "$OUTPUT_FILE" <<EOF
{
  "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "configuration": {
    "kafka_broker": "$KAFKA_BROKER",
    "kafka_topic": "$KAFKA_TOPIC",
    "num_messages": $NUM_MESSAGES,
    "num_threads": $NUM_THREADS,
    "record_size": $RECORD_SIZE
  },
  "results": {}
}
EOF
}

# Test Kafka producer throughput
benchmark_kafka_producer() {
    print_info "Benchmarking Kafka producer throughput..."
    
    if command -v kafka-producer-perf-test &> /dev/null; then
        PERF_OUTPUT=$(kafka-producer-perf-test \
            --topic "$KAFKA_TOPIC" \
            --num-records "$NUM_MESSAGES" \
            --record-size "$RECORD_SIZE" \
            --throughput -1 \
            --producer-props bootstrap.servers="$KAFKA_BROKER" 2>&1 | tail -1)
        
        # Parse output: "10000 records sent, 12345.67 records/sec (1.23 MB/sec), 456.78 ms avg latency"
        RECORDS_PER_SEC=$(echo "$PERF_OUTPUT" | grep -oP '\d+\.\d+ records/sec' | grep -oP '\d+\.\d+')
        MB_PER_SEC=$(echo "$PERF_OUTPUT" | grep -oP '\d+\.\d+ MB/sec' | grep -oP '\d+\.\d+')
        AVG_LATENCY=$(echo "$PERF_OUTPUT" | grep -oP '\d+\.\d+ ms avg latency' | grep -oP '\d+\.\d+')
        
        print_success "Producer throughput: $RECORDS_PER_SEC records/sec ($MB_PER_SEC MB/sec)"
        print_info "Average latency: $AVG_LATENCY ms"
        
        # Add to results
        python3 -c "
import json
with open('$OUTPUT_FILE', 'r') as f:
    data = json.load(f)
data['results']['kafka_producer'] = {
    'records_per_second': $RECORDS_PER_SEC,
    'mb_per_second': $MB_PER_SEC,
    'avg_latency_ms': $AVG_LATENCY
}
with open('$OUTPUT_FILE', 'w') as f:
    json.dump(data, f, indent=2)
"
    else
        print_info "kafka-producer-perf-test not available, using Python benchmark..."
        
        # Python-based simple benchmark
        python3 << 'PYTHON_EOF'
import json
import time
from kafka import KafkaProducer

producer = KafkaProducer(
    bootstrap_servers=['localhost:9092'],
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

start_time = time.time()
num_messages = 1000  # Reduced for Python test

for i in range(num_messages):
    data = {
        "patient_id": f"bench-{i}",
        "timestamp": time.time(),
        "vitals": {"heart_rate": 72}
    }
    producer.send('medical-devices-vitals', value=data)

producer.flush()
end_time = time.time()

duration = end_time - start_time
throughput = num_messages / duration

print(f"Python benchmark: {throughput:.2f} messages/sec")
producer.close()
PYTHON_EOF
        
        print_success "Python producer benchmark complete"
    fi
}

# Test consumer lag
benchmark_consumer_lag() {
    print_info "Checking consumer lag..."
    
    if command -v kafka-consumer-groups &> /dev/null; then
        # Check if there are any consumer groups
        GROUPS=$(kafka-consumer-groups --bootstrap-server "$KAFKA_BROKER" --list 2>/dev/null)
        
        if [ -n "$GROUPS" ]; then
            print_success "Found consumer groups: $(echo $GROUPS | wc -w)"
            
            # Get lag for each group
            for group in $GROUPS; do
                kafka-consumer-groups --bootstrap-server "$KAFKA_BROKER" --describe --group "$group" 2>/dev/null || true
            done
        else
            print_info "No consumer groups found"
        fi
    else
        print_info "kafka-consumer-groups not available"
    fi
}

# Test end-to-end latency
benchmark_e2e_latency() {
    print_info "Measuring end-to-end latency..."
    
    # Simple latency test using Python
    python3 << 'PYTHON_EOF'
import json
import time
from kafka import KafkaProducer, KafkaConsumer

# Create producer and consumer
producer = KafkaProducer(
    bootstrap_servers=['localhost:9092'],
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

consumer = KafkaConsumer(
    'medical-devices-vitals',
    bootstrap_servers=['localhost:9092'],
    auto_offset_reset='latest',
    consumer_timeout_ms=5000,
    value_deserializer=lambda m: json.loads(m.decode('utf-8'))
)

# Send test message with timestamp
test_id = f"latency-test-{int(time.time())}"
send_time = time.time()

data = {
    "patient_id": test_id,
    "timestamp": send_time,
    "vitals": {"heart_rate": 72}
}

producer.send('medical-devices-vitals', value=data)
producer.flush()

# Try to receive the message
received = False
for message in consumer:
    if message.value.get("patient_id") == test_id:
        receive_time = time.time()
        latency = (receive_time - send_time) * 1000  # Convert to ms
        print(f"End-to-end latency: {latency:.2f} ms")
        received = True
        break

if not received:
    print("Could not measure latency (message not received)")

producer.close()
consumer.close()
PYTHON_EOF
    
    print_success "Latency benchmark complete"
}

# Test Flink processing rate
benchmark_flink() {
    print_info "Checking Flink processing rate..."
    
    if curl -s http://localhost:8081/jobs > /dev/null 2>&1; then
        JOBS=$(curl -s http://localhost:8081/jobs | python3 -c "import sys, json; print('\n'.join([j['id'] for j in json.load(sys.stdin).get('jobs', [])]))")
        
        if [ -n "$JOBS" ]; then
            for job_id in $JOBS; do
                METRICS=$(curl -s "http://localhost:8081/jobs/$job_id/metrics?get=numRecordsInPerSecond,numRecordsOutPerSecond" 2>/dev/null)
                print_info "Flink job $job_id metrics: $METRICS"
            done
            print_success "Flink metrics collected"
        else
            print_info "No Flink jobs running"
        fi
    else
        print_info "Flink not available"
    fi
}

# Test Spark streaming
benchmark_spark() {
    print_info "Checking Spark streaming metrics..."
    
    if curl -s http://localhost:8082/api/v1/applications > /dev/null 2>&1; then
        APPS=$(curl -s http://localhost:8082/api/v1/applications 2>/dev/null)
        
        if echo "$APPS" | grep -q "id"; then
            print_success "Spark applications found"
            print_info "Spark metrics: $APPS"
        else
            print_info "No Spark applications running"
        fi
    else
        print_info "Spark not available"
    fi
}

# Measure resource utilization
benchmark_resources() {
    print_info "Measuring resource utilization..."
    
    # CPU usage
    if command -v mpstat &> /dev/null; then
        CPU_USAGE=$(mpstat 1 1 | awk '/Average/ {print 100-$NF}')
        print_info "CPU Usage: $CPU_USAGE%"
    fi
    
    # Memory usage
    if command -v free &> /dev/null; then
        MEM_USAGE=$(free | awk '/Mem:/ {printf "%.1f", $3/$2 * 100}')
        print_info "Memory Usage: $MEM_USAGE%"
    fi
    
    # Docker container stats
    if command -v docker &> /dev/null; then
        print_info "Docker container stats:"
        docker stats --no-stream --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}" 2>/dev/null | head -10 || true
    fi
}

# Finalize results
finalize_results() {
    print_info "Finalizing benchmark results..."
    
    # Add completion timestamp
    python3 -c "
import json
with open('$OUTPUT_FILE', 'r') as f:
    data = json.load(f)
data['completed_at'] = '$(date -u +%Y-%m-%dT%H:%M:%SZ)'
with open('$OUTPUT_FILE', 'w') as f:
    json.dump(data, f, indent=2)
"
    
    print_success "Results saved to: $OUTPUT_FILE"
}

# Main execution
main() {
    echo "========================================"
    echo "Healthcare Streaming - Performance Benchmark"
    echo "========================================"
    echo "Timestamp: $TIMESTAMP"
    echo ""
    
    init_results
    
    benchmark_kafka_producer
    benchmark_consumer_lag
    benchmark_e2e_latency
    benchmark_flink
    benchmark_spark
    benchmark_resources
    
    finalize_results
    
    echo ""
    echo "========================================"
    echo "Benchmark Complete!"
    echo "========================================"
    echo "Results: $OUTPUT_FILE"
    echo ""
    
    print_success "All benchmarks completed successfully"
}

# Run main
main
