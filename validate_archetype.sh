#!/bin/bash
set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
TEST_SERVICE_NAME="test-validation-service"
TEST_ORG="test.example"
TEST_SOLUTION="test-python-rest-service"
TEST_PREFIX="test"
TEST_SUFFIX="service"
MAX_STARTUP_TIME=120 # 2 minutes in seconds
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TEMP_DIR="$(mktemp -d)"
VALIDATION_LOG="$TEMP_DIR/validation.log"

# Cleanup function - DISABLED FOR DEBUGGING
cleanup() {
    echo -e "${BLUE}NOT cleaning up for debugging...${NC}"
    echo -e "${YELLOW}Generated service directory: $TEMP_DIR/$TEST_SERVICE_NAME/$TEST_PREFIX-$TEST_SUFFIX${NC}"
    if [ -d "$TEMP_DIR/$TEST_SERVICE_NAME/$TEST_PREFIX-$TEST_SUFFIX" ]; then
        cd "$TEMP_DIR/$TEST_SERVICE_NAME/$TEST_PREFIX-$TEST_SUFFIX"
        if [ -f "docker-compose.yml" ]; then
            echo -e "${YELLOW}To manually clean up later, run:${NC}"
            echo -e "${YELLOW}cd $TEMP_DIR/$TEST_SERVICE_NAME/$TEST_PREFIX-$TEST_SUFFIX && docker-compose down --volumes --remove-orphans${NC}"
        fi
    fi
    # rm -rf "$TEMP_DIR"  # DISABLED
}

# Trap cleanup on exit
trap cleanup EXIT

# Logging function
log() {
    echo -e "$1" | tee -a "$VALIDATION_LOG"
}

# Success/Failure tracking
TESTS_PASSED=0
TESTS_FAILED=0

test_result() {
    if [ $1 -eq 0 ]; then
        log "${GREEN}✅ $2${NC}"
        TESTS_PASSED=$((TESTS_PASSED + 1))
    else
        log "${RED}❌ $2${NC}"
        TESTS_FAILED=$((TESTS_FAILED + 1))
        return 1
    fi
}

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check prerequisites
check_prerequisites() {
    log "${BLUE}Checking prerequisites...${NC}"
    
    local missing_deps=()
    
    if ! command_exists archetect; then
        missing_deps+=("archetect")
    fi
    
    if ! command_exists docker; then
        missing_deps+=("docker")
    fi
    
    if ! command_exists docker-compose; then
        missing_deps+=("docker-compose")
    fi
    
    if ! command_exists uv; then
        missing_deps+=("uv")
    fi
    
    if ! command_exists curl; then
        missing_deps+=("curl")
    fi
    
    if [ ${#missing_deps[@]} -ne 0 ]; then
        log "${RED}Missing required dependencies: ${missing_deps[*]}${NC}"
        log "${YELLOW}Please install the missing dependencies and try again.${NC}"
        exit 1
    fi
    
    test_result 0 "All prerequisites available"
}

# Generate test service from archetype
generate_test_service() {
    log "\n${BLUE}Generating test service from archetype...${NC}"
    
    cd "$TEMP_DIR"
    
    # Copy the test answers file from the archetype
    if [ -f "$SCRIPT_DIR/test_answers_complete.yaml" ]; then
        cp "$SCRIPT_DIR/test_answers_complete.yaml" ./test_answers.yaml
        test_result 0 "Test answers file copied successfully"
    else
        log "${RED}Test answers file not found at $SCRIPT_DIR/test_answers_complete.yaml${NC}"
        # Create minimal answers file as fallback
        cat > test_answers.yaml << EOF
# Fallback answer file for archetype validation testing
project: "$TEST_SERVICE_NAME"
description: "Test Python REST service with UV for validation testing"
version: "1.0.0"
author_full: "Validation Test Suite"
prefix-name: "$TEST_PREFIX"
suffix-name: "$TEST_SUFFIX"
org-name: "$TEST_ORG"
solution-name: "$TEST_SOLUTION"
prefix_name: "$TEST_PREFIX"
suffix_name: "$TEST_SUFFIX"
org_name: "$TEST_ORG"
solution_name: "$TEST_SOLUTION"
EOF
        test_result 1 "Using fallback test answers file"
    fi
    
    # Generate the service using render command
    if archetect render "$SCRIPT_DIR" --answer-file test_answers.yaml "$TEST_SERVICE_NAME" >> "$VALIDATION_LOG" 2>&1; then
        test_result 0 "Archetype generation successful"
    else
        test_result 1 "Archetype generation failed"
        return 1
    fi
    
    # Verify the generated structure
    if [ -d "$TEST_SERVICE_NAME" ]; then
        test_result 0 "Generated service directory exists"
    else
        test_result 1 "Generated service directory missing"
        return 1
    fi
    
    # Remove any stale lock files that came with the archetype
    log "${YELLOW}Removing any stale lock files...${NC}"
    cd "$TEST_SERVICE_NAME/$TEST_PREFIX-$TEST_SUFFIX"
    find . -name "uv.lock" -delete 2>/dev/null || true
    cd ../..
}

# Run template validation
validate_template_substitution() {
    log "\n${BLUE}Validating template variable substitution...${NC}"
    
    cd "$TEMP_DIR/$TEST_SERVICE_NAME/$TEST_PREFIX-$TEST_SUFFIX"
    
    # Track validation issues
    local template_issues=0
    local error_details=""
    
    # Check for unreplaced template variables
    local unreplaced=$(grep -r "{{ prefix\|{{ suffix\|{{ org" . --exclude-dir=.git --exclude="*.pyc" 2>/dev/null | wc -l)
    if [ "$unreplaced" -gt 0 ]; then
        log "${RED}Found $unreplaced unreplaced template variables:${NC}"
        grep -r "{{ prefix\|{{ suffix\|{{ org" . --exclude-dir=.git --exclude="*.pyc" 2>/dev/null | head -5
        if [ "$unreplaced" -gt 5 ]; then
            log "${YELLOW}... and $((unreplaced - 5)) more${NC}"
        fi
        template_issues=1
        error_details="${error_details}- Unreplaced template variables ($unreplaced found)\n"
    fi
    
    # Check for gRPC references that should have been replaced 
    local grpc_refs=$(grep -r "grpc" . --exclude-dir=.git --exclude="*.pyc" --exclude-dir=.venv 2>/dev/null | grep -v "# REST replaces gRPC" | wc -l)
    if [ "$grpc_refs" -gt 0 ]; then
        log "${RED}Found $grpc_refs unexpected gRPC references:${NC}"
        grep -r "grpc" . --exclude-dir=.git --exclude="*.pyc" --exclude-dir=.venv 2>/dev/null | grep -v "# REST replaces gRPC" | head -3
        if [ "$grpc_refs" -gt 3 ]; then
            log "${YELLOW}... and $((grpc_refs - 3)) more${NC}"
        fi
        template_issues=1
        error_details="${error_details}- gRPC references still present ($grpc_refs found)\n"
    fi
    
    # Check for proto references that should have been replaced
    local proto_refs=$(grep -r "\bproto\b" . --exclude-dir=.git --exclude="*.pyc" --exclude-dir=.venv 2>/dev/null | grep -v "# proto files not needed" | grep -v "protocol:" | wc -l)
    if [ "$proto_refs" -gt 0 ]; then
        log "${RED}Found $proto_refs unexpected proto references:${NC}"
        grep -r "\bproto\b" . --exclude-dir=.git --exclude="*.pyc" --exclude-dir=.venv 2>/dev/null | grep -v "# proto files not needed" | grep -v "protocol:" | head -3
        if [ "$proto_refs" -gt 3 ]; then
            log "${YELLOW}... and $((proto_refs - 3)) more${NC}"
        fi
        template_issues=1
        error_details="${error_details}- Proto references still present ($proto_refs found)\n"
    fi
    
    # Check for proper REST endpoint patterns
    local rest_endpoints=$(grep -r "/api/v1/" . --exclude-dir=.git --exclude="*.pyc" 2>/dev/null | wc -l)
    if [ "$rest_endpoints" -eq 0 ]; then
        log "${RED}Missing expected REST API endpoint patterns${NC}"
        template_issues=1
        error_details="${error_details}- No REST API endpoints found\n"
    fi
    
    # Report results with proper logic (0 = success, 1 = failure)
    if [ $template_issues -eq 0 ]; then
        test_result 0 "Template validation passed - archetype generated correctly"
    else
        log "${RED}Template validation issues found:${NC}"
        log -e "${error_details}"
        test_result 1 "Template validation failed - archetype needs fixes before use"
        return 1
    fi
}

# Test UV sync on all packages
test_uv_sync() {
    log "\n${BLUE}Testing UV sync on all packages...${NC}"
    
    cd "$TEMP_DIR/$TEST_SERVICE_NAME/$TEST_PREFIX-$TEST_SUFFIX"
    
    local sync_failed=0
    
    # First sync from root to build and install all local packages
    log "${YELLOW}Syncing root project to build local packages...${NC}"
    if uv sync >> "$VALIDATION_LOG" 2>&1; then
        log "${GREEN}  ✅ Root project sync successful${NC}"
    else
        log "${RED}  ❌ Root project sync failed${NC}"
        sync_failed=1
    fi
    
    # Then sync individual packages (which should now work since local deps are available)
    while IFS= read -r -d '' pyproject_file; do
        package_dir=$(dirname "$pyproject_file")
        package_name=$(basename "$package_dir")
        
        # Skip the root project as we already synced it
        if [ "$package_name" = "$TEST_PREFIX-$TEST_SUFFIX" ]; then
            continue
        fi
        
        log "${YELLOW}Syncing package: $package_name${NC}"
        
        if (cd "$package_dir" && uv sync >> "$VALIDATION_LOG" 2>&1); then
            log "${GREEN}  ✅ $package_name sync successful${NC}"
        else
            log "${RED}  ❌ $package_name sync failed${NC}"
            sync_failed=1
        fi
    done < <(find . -name "pyproject.toml" -print0)
    
    if [ $sync_failed -eq 0 ]; then
        test_result 0 "UV sync on all packages"
    else
        log "${YELLOW}Some packages failed to sync due to dependency resolution, but will continue validation...${NC}"
        test_result 1 "UV sync on all packages (some failures expected due to package interdependencies)"
    fi
}

# Validate generated lock files are clean
validate_lock_files() {
    log "\n${BLUE}Validating generated UV lock files...${NC}"
    
    cd "$TEMP_DIR/$TEST_SERVICE_NAME/$TEST_PREFIX-$TEST_SUFFIX"
    
    # Count gRPC and protobuf references in lock files
    local lock_grpc_refs=0
    local lock_proto_refs=0
    
    if find . -name "uv.lock" | head -1 > /dev/null 2>&1; then
        lock_grpc_refs=$(find . -name "uv.lock" -exec grep -l "grpc" {} \; 2>/dev/null | wc -l)
        lock_proto_refs=$(find . -name "uv.lock" -exec grep -l "protobuf\|proto.*=" {} \; 2>/dev/null | wc -l)
        
        local lock_issues=0
        
        if [ "$lock_grpc_refs" -gt 0 ]; then
            log "${RED}Found gRPC dependencies in $lock_grpc_refs lock files${NC}"
            find . -name "uv.lock" -exec grep -l "grpc" {} \; 2>/dev/null | head -3
            lock_issues=1
        fi
        
        if [ "$lock_proto_refs" -gt 0 ]; then
            log "${RED}Found protobuf dependencies in $lock_proto_refs lock files${NC}"
            find . -name "uv.lock" -exec grep -l "protobuf\|proto.*=" {} \; 2>/dev/null | head -3
            lock_issues=1
        fi
        
        if [ $lock_issues -eq 0 ]; then
            test_result 0 "Generated lock files are clean (no gRPC/protobuf dependencies)"
        else
            test_result 1 "Generated lock files contain stale gRPC/protobuf dependencies"
            return 1
        fi
    else
        log "${YELLOW}No lock files found to validate${NC}"
        test_result 0 "No lock files to validate"
    fi
}

# Test Docker build and startup
test_docker_stack() {
    log "\n${BLUE}Testing Docker stack build and startup...${NC}"
    
    cd "$TEMP_DIR/$TEST_SERVICE_NAME/$TEST_PREFIX-$TEST_SUFFIX"
    
    # Build the Docker stack - SHOW OUTPUT TO TERMINAL
    echo -e "${YELLOW}Running: docker-compose build${NC}"
    echo -e "${YELLOW}Working directory: $(pwd)${NC}"
    if docker-compose build 2>&1 | tee -a "$VALIDATION_LOG"; then
        test_result 0 "Docker build successful"
    else
        test_result 1 "Docker build failed"
        echo -e "${RED}Docker build failed. Generated service is at: $TEMP_DIR/$TEST_SERVICE_NAME${NC}"
        return 1
    fi
    
    # Start the stack
    log "${YELLOW}Starting Docker stack...${NC}"
    echo -e "${YELLOW}Running: docker-compose up -d${NC}"
    if docker-compose up -d 2>&1 | tee -a "$VALIDATION_LOG"; then
        test_result 0 "Docker stack started"
    else
        test_result 1 "Docker stack failed to start"
        return 1
    fi
    
    # Wait for services to be ready and measure startup time
    local start_time=$(date +%s)
    local max_wait=60
    local waited=0
    
    log "${YELLOW}Waiting for services to be ready...${NC}"
    
    while [ $waited -lt $max_wait ]; do
        if docker-compose ps | grep -q "Up"; then
            local end_time=$(date +%s)
            local startup_time=$((end_time - start_time))
            log "${GREEN}Services ready in ${startup_time} seconds${NC}"
            
            if [ $startup_time -le $MAX_STARTUP_TIME ]; then
                test_result 0 "Service startup time within 2 minutes ($startup_time seconds)"
            else
                test_result 1 "Service startup time exceeded 2 minutes ($startup_time seconds)"
            fi
            break
        fi
        sleep 2
        waited=$((waited + 2))
    done
    
    if [ $waited -ge $max_wait ]; then
        test_result 1 "Services failed to start within timeout"
        return 1
    fi
}

# Test REST service connectivity
test_service_connectivity() {
    log "\n${BLUE}Testing REST service connectivity...${NC}"
    
    cd "$TEMP_DIR/$TEST_SERVICE_NAME/$TEST_PREFIX-$TEST_SUFFIX"
    
    # Test REST API root endpoint
    if curl -s --connect-timeout 5 http://localhost:8080/ | grep -q "REST API" 2>/dev/null; then
        test_result 0 "REST API root endpoint accessible"
    else
        test_result 1 "REST API root endpoint not accessible"
    fi
    
    # Test REST API health endpoint
    if curl -s --connect-timeout 5 http://localhost:8080/health | grep -q "healthy" 2>/dev/null; then
        test_result 0 "REST API health endpoint accessible"
    else
        test_result 1 "REST API health endpoint not accessible"
    fi
    
    # Test OpenAPI docs endpoint
    if curl -s --connect-timeout 5 http://localhost:8080/docs >/dev/null 2>&1; then
        test_result 0 "OpenAPI docs endpoint accessible"
    else
        test_result 1 "OpenAPI docs endpoint not accessible"
    fi
    
    # Test management health endpoint
    if curl -s --connect-timeout 5 http://localhost:8080/health >/dev/null 2>&1; then
        test_result 0 "Management health endpoint accessible"
    else
        test_result 1 "Management health endpoint not accessible"
    fi
    
    # Test metrics endpoint
    if curl -s --connect-timeout 5 http://localhost:8080/metrics | grep -q "python_" 2>/dev/null; then
        test_result 0 "Metrics endpoint accessible and contains metrics"
    else
        test_result 1 "Metrics endpoint not accessible or missing metrics"
    fi
}

# Test REST API CRUD operations
test_rest_api_crud() {
    log "\n${BLUE}Testing REST API CRUD operations...${NC}"
    
    # Test GET /api/v1/tests (list endpoint)
    if curl -s --connect-timeout 5 "http://localhost:8000/api/v1/tests" | grep -q "\[\]" 2>/dev/null; then
        test_result 0 "REST API list endpoint returns empty array"
    else
        test_result 1 "REST API list endpoint not working properly"
    fi
    
    # Test POST /api/v1/tests (create endpoint)
    local create_response=$(curl -s --connect-timeout 5 \
        -X POST "http://localhost:8000/api/v1/tests" \
        -H "Content-Type: application/json" \
        -d '{"name": "test-item", "description": "Test item for validation"}' 2>/dev/null)
    
    if echo "$create_response" | grep -q "test-item" 2>/dev/null; then
        test_result 0 "REST API create endpoint working"
        # Extract ID for further tests
        local test_id=$(echo "$create_response" | grep -o '"id":"[^"]*"' | cut -d'"' -f4)
        
        if [ -n "$test_id" ]; then
            # Test GET /api/v1/tests/{id} (get by ID endpoint)
            if curl -s --connect-timeout 5 "http://localhost:8000/api/v1/tests/$test_id" | grep -q "test-item" 2>/dev/null; then
                test_result 0 "REST API get by ID endpoint working"
            else
                test_result 1 "REST API get by ID endpoint not working"
            fi
            
            # Test PUT /api/v1/tests/{id} (update endpoint)
            if curl -s --connect-timeout 5 \
                -X PUT "http://localhost:8000/api/v1/tests/$test_id" \
                -H "Content-Type: application/json" \
                -d '{"name": "updated-test-item", "description": "Updated test item"}' | grep -q "updated-test-item" 2>/dev/null; then
                test_result 0 "REST API update endpoint working"
            else
                test_result 1 "REST API update endpoint not working"
            fi
            
            # Test DELETE /api/v1/tests/{id} (delete endpoint)
            if curl -s --connect-timeout 5 -X DELETE "http://localhost:8000/api/v1/tests/$test_id" | grep -q "deleted" 2>/dev/null; then
                test_result 0 "REST API delete endpoint working"
            else
                test_result 1 "REST API delete endpoint not working"
            fi
        fi
    else
        test_result 1 "REST API create endpoint not working properly"
    fi
}

# Test monitoring infrastructure
test_monitoring() {
    log "\n${BLUE}Testing monitoring infrastructure...${NC}"
    
    cd "$TEMP_DIR/$TEST_SERVICE_NAME/$TEST_PREFIX-$TEST_SUFFIX"
    
    # Test Prometheus
    if curl -s --connect-timeout 10 http://localhost:9090/-/healthy >/dev/null 2>&1; then
        test_result 0 "Prometheus accessible"
    else
        test_result 1 "Prometheus not accessible"
    fi
    
    # Test Grafana
    if curl -s --connect-timeout 10 http://localhost:3000/api/health | grep -q "ok" 2>/dev/null; then
        test_result 0 "Grafana accessible"
    else
        test_result 1 "Grafana not accessible"
    fi
}

# Run integration tests
run_integration_tests() {
    log "\n${BLUE}Running integration tests...${NC}"
    
    cd "$TEMP_DIR/$TEST_SERVICE_NAME/$TEST_PREFIX-$TEST_SUFFIX"
    
    if [ -f "scripts/run-integration-tests.sh" ]; then
        # Make the script executable
        chmod +x scripts/run-integration-tests.sh
        
        if ./scripts/run-integration-tests.sh >> "$VALIDATION_LOG" 2>&1; then
            test_result 0 "Integration tests passed"
        else
            test_result 1 "Integration tests failed"
            return 1
        fi
    else
        log "${YELLOW}Integration test script not found, creating basic test...${NC}"
        
        # Create a basic integration test
        mkdir -p scripts
        cat > scripts/run-integration-tests.sh << 'EOF'
#!/bin/bash
# Basic integration test for REST service
echo "Running basic REST service integration test..."

# Test service is responding
if curl -s --connect-timeout 5 http://localhost:8000/health > /dev/null; then
    echo "✅ Service health check passed"
else
    echo "❌ Service health check failed"
    exit 1
fi

# Test API endpoint
if curl -s --connect-timeout 5 http://localhost:8000/api/v1/tests > /dev/null; then
    echo "✅ API endpoint accessible"
else
    echo "❌ API endpoint not accessible"
    exit 1
fi

echo "✅ Basic integration tests passed"
EOF
        chmod +x scripts/run-integration-tests.sh
        
        if ./scripts/run-integration-tests.sh >> "$VALIDATION_LOG" 2>&1; then
            test_result 0 "Basic integration tests passed"
        else
            test_result 1 "Basic integration tests failed"
            return 1
        fi
    fi
}

# Main validation workflow
main() {
    log "${BLUE}========================================${NC}"
    log "${BLUE}Python REST Service Archetype Validation${NC}"
    log "${BLUE}========================================${NC}"
    log "Validation log: $VALIDATION_LOG"
    log "Temp directory: $TEMP_DIR"
    log "${YELLOW}Generated service will be at: $TEMP_DIR/$TEST_SERVICE_NAME/$TEST_PREFIX-$TEST_SUFFIX${NC}"
    
    local overall_start_time=$(date +%s)
    
    # Run all validation steps
    check_prerequisites || exit 1
    generate_test_service || exit 1
    validate_template_substitution || exit 1
    
    # Check if we should stop after generation for debugging
    if [ "$1" = "--generate-only" ]; then
        log "\n${YELLOW}Stopping after generation as requested. Service generated at: $TEMP_DIR/$TEST_SERVICE_NAME/$TEST_PREFIX-$TEST_SUFFIX${NC}"
        return 0
    fi
    
    log "\n${BLUE}Starting end-to-end timing measurement...${NC}"
    local e2e_start_time=$(date +%s)
    
    test_uv_sync  # Don't exit on UV sync failures - some packages may have dependency issues
    validate_lock_files || exit 1
    test_docker_stack || exit 1
    test_service_connectivity || exit 1
    test_rest_api_crud || exit 1
    test_monitoring || exit 1
    run_integration_tests || exit 1
    
    local e2e_end_time=$(date +%s)
    local e2e_total_time=$((e2e_end_time - e2e_start_time))
    
    log "\n${BLUE}End-to-end time (sync + build + start + test): ${e2e_total_time} seconds${NC}"
    
    if [ $e2e_total_time -le $MAX_STARTUP_TIME ]; then
        test_result 0 "End-to-end workflow within 2 minutes ($e2e_total_time seconds)"
    else
        test_result 1 "End-to-end workflow exceeded 2 minutes ($e2e_total_time seconds)"
    fi
    
    local overall_end_time=$(date +%s)
    local total_time=$((overall_end_time - overall_start_time))
    
    # Final summary
    log "\n${BLUE}========================================${NC}"
    log "${BLUE}Validation Summary${NC}"
    log "${BLUE}========================================${NC}"
    log "Total tests: $((TESTS_PASSED + TESTS_FAILED))"
    log "${GREEN}Passed: $TESTS_PASSED${NC}"
    log "${RED}Failed: $TESTS_FAILED${NC}"
    log "Total validation time: $total_time seconds"
    log "End-to-end workflow time: $e2e_total_time seconds"
    
    if [ $TESTS_FAILED -eq 0 ]; then
        log "\n${GREEN}🎉 All validation tests passed! REST archetype is ready for release.${NC}"
        log "${YELLOW}Generated service directory preserved at: $TEMP_DIR/$TEST_SERVICE_NAME/$TEST_PREFIX-$TEST_SUFFIX${NC}"
        return 0
    else
        log "\n${RED}❌ Validation failed. Please check the issues above.${NC}"
        log "${YELLOW}Validation log available at: $VALIDATION_LOG${NC}"
        log "${YELLOW}Generated service directory preserved at: $TEMP_DIR/$TEST_SERVICE_NAME/$TEST_PREFIX-$TEST_SUFFIX${NC}"
        return 1
    fi
}

# Run main function
main "$@" 