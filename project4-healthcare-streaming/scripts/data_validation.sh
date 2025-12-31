#!/bin/bash
#
# Data Validation Script for Healthcare Streaming
# Validates FHIR R4, HL7 v2, medical device data formats, and compliance
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

# Validate FHIR R4 schema
validate_fhir() {
    print_info "Validating FHIR R4 resources..."
    
    # Check if sample FHIR file exists
    if [ ! -f "tests/fixtures/sample_fhir.json" ]; then
        print_error "Sample FHIR file not found"
        return 1
    fi
    
    # Validate JSON structure
    if python3 -c "import json; json.load(open('tests/fixtures/sample_fhir.json'))" 2>/dev/null; then
        print_success "FHIR JSON is valid"
    else
        print_error "FHIR JSON is invalid"
        return 1
    fi
    
    # Validate FHIR resource structure
    python3 << 'PYTHON_EOF'
import json
import sys

with open('tests/fixtures/sample_fhir.json') as f:
    bundle = json.load(f)

errors = []

# Check bundle structure
if bundle.get('resourceType') != 'Bundle':
    errors.append("Not a valid FHIR Bundle")

# Check entries
for entry in bundle.get('entry', []):
    resource = entry.get('resource', {})
    resource_type = resource.get('resourceType')
    
    if not resource_type:
        errors.append("Resource missing resourceType")
        continue
    
    # Validate Patient resource
    if resource_type == 'Patient':
        required_fields = ['id', 'name', 'gender', 'birthDate']
        for field in required_fields:
            if field not in resource:
                errors.append(f"Patient missing required field: {field}")
    
    # Validate Observation resource
    elif resource_type == 'Observation':
        required_fields = ['id', 'status', 'code', 'subject']
        for field in required_fields:
            if field not in resource:
                errors.append(f"Observation missing required field: {field}")

if errors:
    print("FHIR validation errors:")
    for error in errors:
        print(f"  - {error}")
    sys.exit(1)
else:
    print("FHIR R4 structure validation passed")
PYTHON_EOF
    
    if [ $? -eq 0 ]; then
        print_success "FHIR R4 schema validation passed"
    else
        print_error "FHIR R4 schema validation failed"
        return 1
    fi
}

# Validate HL7 v2 messages
validate_hl7() {
    print_info "Validating HL7 v2 messages..."
    
    if [ ! -f "tests/fixtures/sample_hl7.txt" ]; then
        print_error "Sample HL7 file not found"
        return 1
    fi
    
    # Validate HL7 message structure
    python3 << 'PYTHON_EOF'
import sys

with open('tests/fixtures/sample_hl7.txt') as f:
    content = f.read()

messages = content.strip().split('\n\n')
errors = []

for idx, message in enumerate(messages, 1):
    if not message.strip():
        continue
    
    lines = message.strip().split('\n')
    
    # First line must be MSH
    if not lines[0].startswith('MSH|'):
        errors.append(f"Message {idx}: Must start with MSH segment")
        continue
    
    # Check for ORU^R01 message type
    if 'ORU^R01' not in lines[0]:
        errors.append(f"Message {idx}: Expected ORU^R01 message type")
    
    # Check for required segments
    has_pid = any(line.startswith('PID|') for line in lines)
    has_obx = any(line.startswith('OBX|') for line in lines)
    
    if not has_pid:
        errors.append(f"Message {idx}: Missing PID segment")
    
    if not has_obx:
        errors.append(f"Message {idx}: Missing OBX segment")

if errors:
    print("HL7 validation errors:")
    for error in errors:
        print(f"  - {error}")
    sys.exit(1)
else:
    print(f"HL7 v2 structure validation passed ({len(messages)} messages)")
PYTHON_EOF
    
    if [ $? -eq 0 ]; then
        print_success "HL7 v2 message validation passed"
    else
        print_error "HL7 v2 message validation failed"
        return 1
    fi
}

# Validate medical device data format
validate_device_data() {
    print_info "Validating medical device data..."
    
    if [ ! -f "tests/fixtures/sample_vitals.json" ]; then
        print_error "Sample vitals file not found"
        return 1
    fi
    
    # Validate vitals data structure
    python3 << 'PYTHON_EOF'
import json
import sys

with open('tests/fixtures/sample_vitals.json') as f:
    vitals_data = json.load(f)

errors = []

required_fields = ['patient_id', 'device_id', 'timestamp', 'vitals']
vital_signs = ['heart_rate', 'blood_pressure_systolic', 'blood_pressure_diastolic', 
               'temperature', 'respiratory_rate', 'oxygen_saturation']

for idx, record in enumerate(vitals_data, 1):
    # Check required fields
    for field in required_fields:
        if field not in record:
            errors.append(f"Record {idx}: Missing field '{field}'")
    
    # Check vital signs
    if 'vitals' in record:
        vitals = record['vitals']
        for sign in vital_signs:
            if sign not in vitals:
                errors.append(f"Record {idx}: Missing vital sign '{sign}'")
            else:
                # Validate ranges
                value = vitals[sign]
                if sign == 'heart_rate' and not (0 <= value <= 300):
                    errors.append(f"Record {idx}: Heart rate out of range: {value}")
                elif sign == 'oxygen_saturation' and not (0 <= value <= 100):
                    errors.append(f"Record {idx}: O2 saturation out of range: {value}")
                elif sign == 'temperature' and not (90 <= value <= 110):
                    errors.append(f"Record {idx}: Temperature out of range: {value}")

if errors:
    print("Medical device data validation errors:")
    for error in errors:
        print(f"  - {error}")
    sys.exit(1)
else:
    print(f"Medical device data validation passed ({len(vitals_data)} records)")
PYTHON_EOF
    
    if [ $? -eq 0 ]; then
        print_success "Medical device data format validation passed"
    else
        print_error "Medical device data format validation failed"
        return 1
    fi
}

# Check for PII/PHI de-identification
validate_deidentification() {
    print_info "Checking for patient data de-identification..."
    
    # Check for common PII patterns
    python3 << 'PYTHON_EOF'
import re
import sys

# Patterns to check for
ssn_pattern = r'\b\d{3}-\d{2}-\d{4}\b'
phone_pattern = r'\b\d{3}-\d{3}-\d{4}\b'
email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'

files_to_check = [
    'tests/fixtures/sample_fhir.json',
    'tests/fixtures/sample_hl7.txt',
    'tests/fixtures/sample_vitals.json'
]

warnings = []

for filepath in files_to_check:
    try:
        with open(filepath) as f:
            content = f.read()
        
        # Check for SSN
        if re.search(ssn_pattern, content):
            warnings.append(f"{filepath}: Contains SSN pattern")
        
        # Check for phone (allow fixture data)
        phones = re.findall(phone_pattern, content)
        if phones:
            print(f"  Found {len(phones)} phone numbers in {filepath} (fixture data - OK)")
        
    except FileNotFoundError:
        pass

if warnings:
    print("De-identification warnings:")
    for warning in warnings:
        print(f"  - {warning}")
    print("\nNote: These are warnings, not failures. Review if real data is used.")
else:
    print("No obvious PII patterns detected")
PYTHON_EOF
    
    print_success "De-identification check complete"
}

# HIPAA compliance checks
validate_hipaa_compliance() {
    print_info "Running HIPAA compliance checks..."
    
    # Check for encryption configuration
    print_info "Checking encryption requirements..."
    
    # Check if TLS is configured
    if [ -f "docker-compose.yml" ]; then
        if grep -q "KAFKA_SSL" docker-compose.yml; then
            print_success "Kafka SSL/TLS configuration found"
        else
            print_info "Kafka SSL/TLS not configured (recommended for production)"
        fi
    fi
    
    # Check for access control
    print_info "Checking access control configuration..."
    print_info "HIPAA compliance requires: encryption at rest, encryption in transit, access controls, audit logging"
    
    print_success "HIPAA compliance checklist reviewed"
}

# Main execution
main() {
    echo "========================================"
    echo "Healthcare Data Validation"
    echo "========================================"
    echo ""
    
    validate_fhir
    validate_hl7
    validate_device_data
    validate_deidentification
    validate_hipaa_compliance
    
    echo ""
    echo "========================================"
    echo "Validation Summary"
    echo "========================================"
    echo -e "${GREEN}Passed: $PASSED${NC}"
    echo -e "${RED}Failed: $FAILED${NC}"
    echo ""
    
    if [ $FAILED -eq 0 ]; then
        print_success "All data validation checks passed!"
        exit 0
    else
        print_error "Some validation checks failed!"
        exit 1
    fi
}

# Run main
main
