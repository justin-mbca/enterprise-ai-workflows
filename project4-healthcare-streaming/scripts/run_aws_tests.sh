#!/bin/bash
#
# AWS Integration Testing Script for Healthcare Streaming
# Tests Kinesis, MSK, Lambda, IoT Core, and Glue Streaming
#

set -e

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Test counters
PASSED=0
FAILED=0

# AWS Configuration
AWS_REGION=${AWS_REGION:-"us-east-1"}
KINESIS_STREAM_NAME=${KINESIS_STREAM_NAME:-"healthcare-vitals-stream"}
MSK_CLUSTER_NAME=${MSK_CLUSTER_NAME:-"healthcare-streaming-cluster"}

# Cleanup flag
CLEANUP_RESOURCES=${CLEANUP_RESOURCES:-"false"}

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

# Check AWS credentials
test_aws_credentials() {
    print_info "Checking AWS credentials..."
    
    if ! command -v aws &> /dev/null; then
        print_error "AWS CLI not installed"
        return 1
    fi
    
    if aws sts get-caller-identity > /dev/null 2>&1; then
        ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
        print_success "AWS credentials valid (Account: $ACCOUNT_ID)"
    else
        print_error "AWS credentials not configured"
        return 1
    fi
}

# Test/Create Kinesis stream
test_kinesis_stream() {
    print_info "Testing Kinesis stream..."
    
    # Check if stream exists
    if aws kinesis describe-stream --stream-name "$KINESIS_STREAM_NAME" --region "$AWS_REGION" > /dev/null 2>&1; then
        print_success "Kinesis stream '$KINESIS_STREAM_NAME' exists"
    else
        print_info "Creating Kinesis stream..."
        if aws kinesis create-stream \
            --stream-name "$KINESIS_STREAM_NAME" \
            --shard-count 1 \
            --region "$AWS_REGION" > /dev/null 2>&1; then
            
            print_success "Kinesis stream created"
            
            # Wait for stream to be active
            print_info "Waiting for stream to be active..."
            aws kinesis wait stream-exists --stream-name "$KINESIS_STREAM_NAME" --region "$AWS_REGION"
            print_success "Stream is active"
        else
            print_error "Failed to create Kinesis stream"
            return 1
        fi
    fi
    
    # Test putting a record
    print_info "Testing Kinesis put-record..."
    TEST_DATA='{"patient_id":"test-001","heart_rate":72}'
    
    if aws kinesis put-record \
        --stream-name "$KINESIS_STREAM_NAME" \
        --partition-key "test-001" \
        --data "$TEST_DATA" \
        --region "$AWS_REGION" > /dev/null 2>&1; then
        print_success "Successfully sent test record to Kinesis"
    else
        print_error "Failed to send record to Kinesis"
        return 1
    fi
}

# Test Lambda functions
test_lambda_functions() {
    print_info "Testing Lambda functions..."
    
    # List Lambda functions
    LAMBDA_FUNCTIONS=$(aws lambda list-functions --region "$AWS_REGION" --query 'Functions[?contains(FunctionName, `healthcare`) || contains(FunctionName, `streaming`)].FunctionName' --output text)
    
    if [ -n "$LAMBDA_FUNCTIONS" ]; then
        print_success "Found Lambda functions: $LAMBDA_FUNCTIONS"
        
        # Test invoke (if any functions exist)
        for func in $LAMBDA_FUNCTIONS; do
            print_info "Testing Lambda function: $func"
            if aws lambda invoke \
                --function-name "$func" \
                --payload '{"test": true}' \
                --region "$AWS_REGION" \
                /tmp/lambda-output.json > /dev/null 2>&1; then
                print_success "Lambda function '$func' invoked successfully"
            else
                print_error "Lambda function '$func' invocation failed"
            fi
        done
    else
        print_info "No healthcare Lambda functions found (skipping)"
    fi
}

# Test MSK cluster
test_msk_cluster() {
    print_info "Testing MSK cluster..."
    
    # List MSK clusters
    CLUSTERS=$(aws kafka list-clusters --region "$AWS_REGION" --query 'ClusterInfoList[?ClusterName==`'"$MSK_CLUSTER_NAME"'`].ClusterArn' --output text 2>/dev/null)
    
    if [ -n "$CLUSTERS" ]; then
        print_success "MSK cluster '$MSK_CLUSTER_NAME' found"
        
        # Get cluster details
        CLUSTER_ARN=$(echo "$CLUSTERS" | head -1)
        STATE=$(aws kafka describe-cluster --cluster-arn "$CLUSTER_ARN" --region "$AWS_REGION" --query 'ClusterInfo.State' --output text)
        print_info "Cluster state: $STATE"
        
        if [ "$STATE" = "ACTIVE" ]; then
            print_success "MSK cluster is active"
        else
            print_error "MSK cluster is not active (state: $STATE)"
        fi
    else
        print_info "MSK cluster not found (skipping)"
    fi
}

# Test IoT Core
test_iot_core() {
    print_info "Testing IoT Core..."
    
    # List IoT things
    THINGS=$(aws iot list-things --region "$AWS_REGION" --query 'things[?contains(thingName, `device`) || contains(thingName, `monitor`)].thingName' --output text 2>/dev/null)
    
    if [ -n "$THINGS" ]; then
        print_success "IoT devices found: $(echo $THINGS | wc -w)"
        
        # Test IoT endpoint
        IOT_ENDPOINT=$(aws iot describe-endpoint --endpoint-type iot:Data-ATS --region "$AWS_REGION" --query 'endpointAddress' --output text 2>/dev/null)
        if [ -n "$IOT_ENDPOINT" ]; then
            print_success "IoT endpoint: $IOT_ENDPOINT"
        fi
    else
        print_info "No IoT devices found (skipping)"
    fi
}

# Test Glue Streaming jobs
test_glue_streaming() {
    print_info "Testing Glue Streaming jobs..."
    
    # List Glue jobs
    GLUE_JOBS=$(aws glue list-jobs --region "$AWS_REGION" --query 'JobNames[?contains(@, `streaming`) || contains(@, `healthcare`)]' --output text 2>/dev/null)
    
    if [ -n "$GLUE_JOBS" ]; then
        print_success "Found Glue streaming jobs: $GLUE_JOBS"
    else
        print_info "No Glue streaming jobs found (skipping)"
    fi
}

# Cost estimation
estimate_costs() {
    print_info "Estimating AWS costs..."
    
    echo ""
    echo "Estimated Monthly Costs (approximate):"
    echo "  - Kinesis Stream (1 shard): \$25"
    echo "  - MSK Cluster (kafka.t3.small x3): \$150"
    echo "  - Lambda (1M requests): \$0.20"
    echo "  - IoT Core (1M messages): \$1.00"
    echo "  - Glue Streaming: \$0.44/DPU-hour"
    echo ""
    print_info "Actual costs depend on usage and configuration"
}

# Cleanup AWS resources
cleanup_aws_resources() {
    if [ "$CLEANUP_RESOURCES" = "true" ]; then
        print_info "Cleaning up AWS resources..."
        
        # Delete Kinesis stream if we created it
        if aws kinesis describe-stream --stream-name "$KINESIS_STREAM_NAME" --region "$AWS_REGION" > /dev/null 2>&1; then
            print_info "Deleting Kinesis stream..."
            aws kinesis delete-stream --stream-name "$KINESIS_STREAM_NAME" --region "$AWS_REGION"
            print_success "Kinesis stream deleted"
        fi
        
        print_info "Note: MSK clusters and other resources require manual cleanup"
    else
        print_info "Skipping resource cleanup (use CLEANUP_RESOURCES=true to enable)"
    fi
}

# Main execution
main() {
    echo "========================================"
    echo "Healthcare Streaming - AWS Tests"
    echo "========================================"
    echo "Region: $AWS_REGION"
    echo ""
    
    # Run tests
    test_aws_credentials
    test_kinesis_stream
    test_lambda_functions
    test_msk_cluster
    test_iot_core
    test_glue_streaming
    
    echo ""
    estimate_costs
    
    echo ""
    echo "========================================"
    echo "Test Summary"
    echo "========================================"
    echo -e "${GREEN}Passed: $PASSED${NC}"
    echo -e "${RED}Failed: $FAILED${NC}"
    echo ""
    
    # Cleanup
    cleanup_aws_resources
    
    # Exit with appropriate code
    if [ $FAILED -eq 0 ]; then
        print_success "All AWS tests passed!"
        exit 0
    else
        print_error "Some AWS tests failed!"
        exit 1
    fi
}

# Run main
main
