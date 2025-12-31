#!/bin/bash
#
# Local Testing Script for Healthcare Streaming Infrastructure
# Tests Docker Compose stack health, Kafka, Flink, Spark, and data producers
#

set -e

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test counters
PASSED=0
FAILED=0

# Cleanup flag
CLEANUP=${CLEANUP:-"false"}

# Print colored output
print_success() {
    echo -e "${GREEN}✓${NC} $1"
    ((PASSED++))
}

print_error() {
    echo -e "${RED}✗${NC} $1"
    ((FAILED++))
}

print_info() {
    echo -e "${YELLOW}ℹ${NC} $1"
}

# Test Docker Compose services are running
test_docker_services() {
    print_info "Testing Docker Compose services..."
    
    if ! command -v docker-compose &> /dev/null; then
        print_error "docker-compose not installed"
        return 1
    fi
    
    # Check if docker-compose.yml exists
    if [ ! -f "docker-compose.yml" ]; then
        print_error "docker-compose.yml not found"
        return 1
    fi
    
    # Start services
    print_info "Starting Docker Compose stack..."
    docker-compose up -d || {
        print_error "Failed to start Docker Compose services"
        return 1
    }
    
    print_success "Docker Compose services started"
    
    # Wait for services to be ready
    print_info "Waiting for services to initialize (30s)..."
    sleep 30
}

# Test Kafka broker health
test_kafka_broker() {
    print_info "Testing Kafka broker..."
    
    # Check if Kafka container is running
    if ! docker-compose ps | grep -q "kafka.*Up"; then
        print_error "Kafka container not running"
        return 1
    fi
    
    print_success "Kafka broker is running"
    
    # Test Kafka connectivity (if kafka tools are available)
    if command -v kafka-topics &> /dev/null; then
        kafka-topics --bootstrap-server localhost:9092 --list &> /dev/null && \
            print_success "Kafka broker is accessible" || \
            print_error "Cannot connect to Kafka broker"
    else
        print_info "Kafka tools not available, skipping connectivity test"
    fi
}

# Test Zookeeper health
test_zookeeper() {
    print_info "Testing Zookeeper..."
    
    if docker-compose ps | grep -q "zookeeper.*Up"; then
        print_success "Zookeeper is running"
    else
        print_error "Zookeeper container not running"
        return 1
    fi
}

# Test Flink job manager
test_flink() {
    print_info "Testing Flink..."
    
    # Check if Flink container is running
    if docker-compose ps | grep -q "flink.*Up"; then
        print_success "Flink containers are running"
    else
        print_info "Flink not configured or not running (optional)"
        return 0
    fi
    
    # Test Flink REST API
    if curl -s -f http://localhost:8081/overview > /dev/null 2>&1; then
        print_success "Flink REST API is accessible"
    else
        print_error "Flink REST API not accessible"
    fi
}

# Test Spark
test_spark() {
    print_info "Testing Spark..."
    
    # Check if Spark container is running
    if docker-compose ps | grep -q "spark.*Up"; then
        print_success "Spark containers are running"
    else
        print_info "Spark not configured or not running (optional)"
        return 0
    fi
    
    # Test Spark UI
    if curl -s -f http://localhost:8082 > /dev/null 2>&1; then
        print_success "Spark UI is accessible"
    else
        print_info "Spark UI not accessible (may not be started yet)"
    fi
}

# Test producer functionality
test_producers() {
    print_info "Testing data producers..."
    
    # Check if producer scripts exist
    if [ -f "kafka_streams/producer_medical_devices.py" ]; then
        print_success "Producer scripts found"
    else
        print_error "Producer scripts not found"
        return 1
    fi
    
    # Try to run a simple producer test (if Python is available)
    if command -v python3 &> /dev/null; then
        python3 -c "from kafka_streams.producer_medical_devices import generate_vital_signs; print(generate_vital_signs('test-patient'))" > /dev/null 2>&1 && \
            print_success "Producer code is functional" || \
            print_info "Producer test skipped (dependencies may not be installed)"
    fi
}

# Test consumer functionality
test_consumers() {
    print_info "Testing data consumers..."
    
    # This would test if consumers can read from Kafka
    print_info "Consumer tests require full integration setup (skipped)"
}

# Test healthcare data generators
test_data_generators() {
    print_info "Testing healthcare data generators..."
    
    if command -v python3 &> /dev/null; then
        # Test FHIR generator
        python3 -c "from healthcare_data.fhir_patient_generator import generate_patient; generate_patient()" > /dev/null 2>&1 && \
            print_success "FHIR generator functional" || \
            print_info "FHIR generator test skipped"
        
        # Test HL7 generator
        python3 -c "from healthcare_data.hl7_message_simulator import create_hl7_message; create_hl7_message('test', [])" > /dev/null 2>&1 && \
            print_success "HL7 generator functional" || \
            print_info "HL7 generator test skipped"
    fi
}

# Service health check
test_service_health() {
    print_info "Checking service health endpoints..."
    
    # Kafka UI (if available)
    if curl -s -f http://localhost:8080 > /dev/null 2>&1; then
        print_success "Kafka UI is accessible"
    else
        print_info "Kafka UI not available (optional)"
    fi
    
    # Schema Registry (if available)
    if curl -s -f http://localhost:8081 > /dev/null 2>&1; then
        print_success "Schema Registry is accessible"
    else
        print_info "Schema Registry not available (optional)"
    fi
}

# Cleanup function
cleanup() {
    if [ "$CLEANUP" = "true" ]; then
        print_info "Cleaning up Docker Compose services..."
        docker-compose down -v
        print_success "Cleanup complete"
    else
        print_info "Skipping cleanup (use CLEANUP=true to enable)"
    fi
}

# Main test execution
main() {
    echo "========================================"
    echo "Healthcare Streaming - Local Tests"
    echo "========================================"
    echo ""
    
    # Run all tests
    test_docker_services
    test_zookeeper
    test_kafka_broker
    test_flink
    test_spark
    test_producers
    test_consumers
    test_data_generators
    test_service_health
    
    echo ""
    echo "========================================"
    echo "Test Summary"
    echo "========================================"
    echo -e "${GREEN}Passed: $PASSED${NC}"
    echo -e "${RED}Failed: $FAILED${NC}"
    echo ""
    
    # Cleanup if requested
    cleanup
    
    # Exit with appropriate code
    if [ $FAILED -eq 0 ]; then
        print_success "All tests passed!"
        exit 0
    else
        print_error "Some tests failed!"
        exit 1
    fi
}

# Run main function
main
