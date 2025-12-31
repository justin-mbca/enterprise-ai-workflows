#!/bin/bash
#
# Security and Compliance Scan Script
# Checks TLS encryption, IAM roles, credentials, HIPAA compliance, and container vulnerabilities
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
WARNINGS=0

print_success() {
    echo -e "${GREEN}✓${NC} $1"
    ((PASSED++))
}

print_error() {
    echo -e "${RED}✗${NC} $1"
    ((FAILED++))
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
    ((WARNINGS++))
}

print_info() {
    echo -e "${YELLOW}ℹ${NC} $1"
}

# Check for hardcoded credentials
scan_hardcoded_credentials() {
    print_info "Scanning for hardcoded credentials..."
    
    # Patterns to search for
    PATTERNS=(
        "password\s*=\s*['\"][^'\"]+['\"]"
        "api[_-]?key\s*=\s*['\"][^'\"]+['\"]"
        "secret\s*=\s*['\"][^'\"]+['\"]"
        "aws_access_key_id\s*=\s*['\"][^'\"]+['\"]"
        "aws_secret_access_key\s*=\s*['\"][^'\"]+['\"]"
    )
    
    FOUND=0
    
    for pattern in "${PATTERNS[@]}"; do
        RESULTS=$(grep -r -i -E "$pattern" --include="*.py" --include="*.sh" --include="*.yml" --include="*.yaml" --exclude-dir=".git" . 2>/dev/null | grep -v "print_info\|print_error\|print_warning" || true)
        
        if [ -n "$RESULTS" ]; then
            echo "$RESULTS" | head -5
            FOUND=1
        fi
    done
    
    if [ $FOUND -eq 0 ]; then
        print_success "No obvious hardcoded credentials found"
    else
        print_warning "Potential hardcoded credentials detected (review output above)"
    fi
}

# Check TLS encryption configuration
check_tls_encryption() {
    print_info "Checking TLS encryption configuration..."
    
    # Check Kafka TLS config
    if [ -f "docker-compose.yml" ]; then
        if grep -q "KAFKA_SSL_ENABLED\|SSL_ENABLED\|KAFKA_SECURITY_PROTOCOL.*SSL" docker-compose.yml; then
            print_success "Kafka TLS/SSL configuration found"
        else
            print_warning "Kafka TLS not configured - recommend enabling for production"
        fi
        
        # Check for SSL certificates
        if [ -d "certs" ] || [ -d "ssl" ]; then
            print_success "SSL certificate directory found"
        else
            print_warning "No SSL certificate directory found"
        fi
    else
        print_info "No docker-compose.yml found"
    fi
}

# Validate IAM roles and policies (AWS)
check_iam_configuration() {
    print_info "Checking IAM configuration..."
    
    # Check if AWS CLI is available
    if command -v aws &> /dev/null; then
        # Check if credentials are configured
        if aws sts get-caller-identity &> /dev/null; then
            IDENTITY=$(aws sts get-caller-identity --query 'Arn' --output text)
            print_success "AWS credentials configured: $IDENTITY"
            
            # Check for least privilege
            print_info "Verify IAM policies follow least privilege principle"
        else
            print_info "AWS credentials not configured (OK for local development)"
        fi
    else
        print_info "AWS CLI not installed (OK for local development)"
    fi
}

# HIPAA compliance checklist
check_hipaa_compliance() {
    print_info "Running HIPAA compliance checklist..."
    
    echo ""
    echo "  HIPAA Technical Safeguards Checklist:"
    echo "  [ ] Encryption at rest - Use encrypted storage volumes"
    echo "  [ ] Encryption in transit - Enable TLS/SSL for all connections"
    echo "  [ ] Access controls - Implement role-based access control (RBAC)"
    echo "  [ ] Audit logging - Enable comprehensive audit logs"
    echo "  [ ] Unique user identification - Each user has unique ID"
    echo "  [ ] Emergency access - Procedures for emergency data access"
    echo "  [ ] Automatic logoff - Implement session timeouts"
    echo "  [ ] Encryption and decryption - Secure key management"
    echo ""
    
    print_info "Review and implement all HIPAA requirements before production deployment"
    
    # Check for common HIPAA violations
    VIOLATIONS=0
    
    # Check for unencrypted data stores
    if [ -f "docker-compose.yml" ]; then
        if ! grep -q "ENCRYPT\|SSL\|TLS" docker-compose.yml; then
            print_warning "Unencrypted services detected - review docker-compose.yml"
            ((VIOLATIONS++))
        fi
    fi
    
    if [ $VIOLATIONS -eq 0 ]; then
        print_success "No obvious HIPAA violations detected"
    else
        print_warning "$VIOLATIONS potential HIPAA compliance issues found"
    fi
}

# Network security validation
check_network_security() {
    print_info "Checking network security..."
    
    # Check for exposed ports
    if [ -f "docker-compose.yml" ]; then
        EXPOSED_PORTS=$(grep -E "^\s+- [0-9]+:[0-9]+" docker-compose.yml | wc -l)
        print_info "Found $EXPOSED_PORTS exposed ports in docker-compose.yml"
        
        # Check for database ports exposed to 0.0.0.0
        if grep -E "^\s+- \"?0\.0\.0\.0:[0-9]+\"?" docker-compose.yml > /dev/null; then
            print_warning "Services exposed to 0.0.0.0 - restrict in production"
        else
            print_success "No services exposed to 0.0.0.0"
        fi
    fi
    
    # Check for firewall rules (if applicable)
    print_info "Verify firewall rules restrict access to authorized IPs only"
}

# Container vulnerability scanning
scan_container_vulnerabilities() {
    print_info "Scanning container vulnerabilities..."
    
    # Check if Trivy is installed
    if command -v trivy &> /dev/null; then
        print_info "Running Trivy container scan..."
        
        # Scan Docker images if they exist
        IMAGES=$(docker images --format "{{.Repository}}:{{.Tag}}" | grep -v "<none>" | head -5)
        
        if [ -n "$IMAGES" ]; then
            for image in $IMAGES; do
                print_info "Scanning $image..."
                trivy image --severity HIGH,CRITICAL --quiet "$image" || true
            done
            print_success "Container vulnerability scan complete"
        else
            print_info "No Docker images to scan"
        fi
    else
        print_info "Trivy not installed - install with: curl -sfL https://raw.githubusercontent.com/aquasecurity/trivy/main/contrib/install.sh | sh"
    fi
}

# Check for security headers (if web services exist)
check_security_headers() {
    print_info "Checking security headers for web services..."
    
    # Common ports to check
    PORTS=("8080" "8081" "8082")
    
    for port in "${PORTS[@]}"; do
        if curl -s -I "http://localhost:$port" > /dev/null 2>&1; then
            HEADERS=$(curl -s -I "http://localhost:$port")
            
            # Check for security headers
            if echo "$HEADERS" | grep -qi "X-Content-Type-Options"; then
                print_success "Port $port: X-Content-Type-Options header present"
            else
                print_warning "Port $port: Missing X-Content-Type-Options header"
            fi
            
            if echo "$HEADERS" | grep -qi "X-Frame-Options"; then
                print_success "Port $port: X-Frame-Options header present"
            else
                print_warning "Port $port: Missing X-Frame-Options header"
            fi
        fi
    done
}

# Check dependency vulnerabilities
check_dependency_vulnerabilities() {
    print_info "Checking Python dependency vulnerabilities..."
    
    # Check if safety is installed
    if command -v safety &> /dev/null; then
        print_info "Running safety check..."
        safety check --json > /tmp/safety-report.json 2>&1 || true
        
        VULNS=$(cat /tmp/safety-report.json 2>/dev/null | grep -c "vulnerability" || echo "0")
        if [ "$VULNS" -eq "0" ]; then
            print_success "No known vulnerabilities in Python dependencies"
        else
            print_warning "Found $VULNS vulnerabilities in Python dependencies"
            cat /tmp/safety-report.json
        fi
    else
        print_info "safety not installed - install with: pip install safety"
    fi
}

# Check secrets in environment variables
check_environment_secrets() {
    print_info "Checking for secrets in environment variables..."
    
    # Check .env files
    if [ -f ".env" ]; then
        print_warning ".env file found - ensure it's in .gitignore"
        
        if [ -f ".gitignore" ] && grep -q ".env" .gitignore; then
            print_success ".env is in .gitignore"
        else
            print_error ".env is NOT in .gitignore!"
        fi
    else
        print_success "No .env file found"
    fi
    
    # Check for .env.example
    if [ -f ".env.example" ]; then
        print_success ".env.example found (good practice)"
    fi
}

# Generate security report
generate_security_report() {
    print_info "Generating security report..."
    
    REPORT_FILE="security_report_$(date +%Y%m%d_%H%M%S).txt"
    
    cat > "$REPORT_FILE" <<EOF
Healthcare Streaming Security Scan Report
Generated: $(date)
========================================

Summary:
  Passed: $PASSED
  Failed: $FAILED
  Warnings: $WARNINGS

Recommendations:
  1. Enable TLS/SSL for all data in transit
  2. Implement encryption at rest for all databases
  3. Use environment variables or secrets manager for credentials
  4. Implement role-based access control (RBAC)
  5. Enable comprehensive audit logging
  6. Regularly scan containers for vulnerabilities
  7. Keep dependencies up to date
  8. Implement network segmentation
  9. Use strong authentication mechanisms
  10. Regular security audits and penetration testing

HIPAA Compliance:
  - Review HIPAA Technical Safeguards checklist
  - Ensure Business Associate Agreements (BAAs) are in place
  - Implement breach notification procedures
  - Conduct regular risk assessments

Next Steps:
  - Address all FAILED items immediately
  - Review and address WARNINGS before production
  - Implement security monitoring and alerting
  - Conduct regular security training
EOF
    
    print_success "Security report saved to: $REPORT_FILE"
}

# Main execution
main() {
    echo "========================================"
    echo "Healthcare Streaming - Security Scan"
    echo "========================================"
    echo ""
    
    scan_hardcoded_credentials
    check_tls_encryption
    check_iam_configuration
    check_hipaa_compliance
    check_network_security
    scan_container_vulnerabilities
    check_security_headers
    check_dependency_vulnerabilities
    check_environment_secrets
    
    generate_security_report
    
    echo ""
    echo "========================================"
    echo "Security Scan Summary"
    echo "========================================"
    echo -e "${GREEN}Passed: $PASSED${NC}"
    echo -e "${YELLOW}Warnings: $WARNINGS${NC}"
    echo -e "${RED}Failed: $FAILED${NC}"
    echo ""
    
    if [ $FAILED -eq 0 ] && [ $WARNINGS -eq 0 ]; then
        print_success "Security scan completed with no issues!"
        exit 0
    elif [ $FAILED -eq 0 ]; then
        print_warning "Security scan completed with warnings - review before production"
        exit 0
    else
        print_error "Security scan found critical issues - address immediately!"
        exit 1
    fi
}

# Run main
main
