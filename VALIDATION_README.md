# REST Service Archetype Validation

This document describes how to validate the Python REST Service Archetype to ensure it generates working, production-ready services.

## Prerequisites

The validation script requires the following tools:

- **archetect** - For generating projects from the archetype
- **docker** - For containerization and orchestration
- **docker-compose** - For running the full application stack  
- **uv** - For Python dependency management
- **curl** - For testing REST API endpoints

## Running Validation

### Full End-to-End Validation

Run the complete validation suite:

```bash
./validate_archetype.sh
```

This performs:
1. ✅ **Prerequisites Check** - Verifies required tools are installed
2. ✅ **Archetype Generation** - Creates a test service from the archetype
3. ✅ **Template Validation** - Ensures all template variables are properly replaced
4. ✅ **Dependency Sync** - Tests `uv sync` on all packages
5. ✅ **Docker Build** - Builds the complete Docker stack
6. ✅ **Service Startup** - Starts services and measures startup time
7. ✅ **REST API Testing** - Tests all CRUD endpoints
8. ✅ **Connectivity Tests** - Verifies service ports and health endpoints
9. ✅ **Monitoring Tests** - Checks Prometheus and Grafana accessibility
10. ✅ **Integration Tests** - Runs end-to-end workflow tests

### Generation-Only Mode

To generate a test service without running the full validation (useful for debugging):

```bash
./validate_archetype.sh --generate-only
```

## What Gets Tested

### REST API Endpoints

The validation tests these REST endpoints:

- **`GET /`** - Root endpoint with service information
- **`GET /health`** - Health check endpoint
- **`GET /docs`** - OpenAPI documentation
- **`GET /api/v1/tests`** - List resources (empty array initially)
- **`POST /api/v1/tests`** - Create a new resource
- **`GET /api/v1/tests/{id}`** - Get resource by ID
- **`PUT /api/v1/tests/{id}`** - Update resource by ID
- **`DELETE /api/v1/tests/{id}`** - Delete resource by ID

### Service Infrastructure

- **FastAPI Server** - Main REST API on port 8000
- **Management Server** - Health/metrics on port 8080
- **PostgreSQL Database** - Data persistence
- **Redis Cache** - Session and caching
- **Prometheus** - Metrics collection on port 9090
- **Grafana** - Monitoring dashboard on port 3000

### Performance Requirements

- **Startup Time**: Complete stack must start within 2 minutes
- **Response Time**: API endpoints must respond within 5 seconds
- **Health Checks**: All health endpoints must return successful responses

## Test Configuration

The validation uses `test_answers_complete.yaml` which provides:

- Test service name: `test-validation-service`
- Organization: `test.example`
- Solution: `test-python-rest-service`
- Prefix: `test`
- Suffix: `service`
- REST API port: `8000`
- Management port: `8080`

## Validation Output

### Success Example

```
========================================
Python REST Service Archetype Validation
========================================

✅ All prerequisites available
✅ Archetype generation successful
✅ Generated service directory exists
✅ Template validation passed - no template issues found
✅ UV sync on all packages
✅ Docker build successful
✅ Docker stack started
✅ Service startup time within 2 minutes (45 seconds)
✅ REST API root endpoint accessible
✅ REST API health endpoint accessible
✅ OpenAPI docs endpoint accessible
✅ REST API list endpoint returns empty array
✅ REST API create endpoint working
✅ REST API get by ID endpoint working
✅ REST API update endpoint working
✅ REST API delete endpoint working
✅ Management health endpoint accessible
✅ Metrics endpoint accessible and contains metrics
✅ Prometheus accessible
✅ Grafana accessible
✅ Integration tests passed
✅ End-to-end workflow within 2 minutes (78 seconds)

========================================
Validation Summary
========================================
Total tests: 18
Passed: 18
Failed: 0
Total validation time: 95 seconds
End-to-end workflow time: 78 seconds

🎉 All validation tests passed! REST archetype is ready for release.
```

### Generated Service Location

After validation (whether successful or failed), the generated test service is preserved at:

```
/tmp/tmp.XXXXXXXXX/test-validation-service/test-service/
```

The script displays this location for manual inspection and debugging.

## Cleanup

The validation script intentionally preserves the generated service for debugging. To clean up manually:

```bash
# Navigate to the generated service directory
cd /path/to/generated/test-service

# Stop and remove Docker containers
docker-compose down --volumes --remove-orphans

# Remove the temporary directory
rm -rf /tmp/tmp.XXXXXXXXX
```

## Troubleshooting

### Common Issues

1. **Docker Build Fails**
   - Check Docker daemon is running
   - Verify sufficient disk space
   - Review build logs in validation.log

2. **Service Won't Start**
   - Check port conflicts (8000, 8080, 5432, 6379, 9090, 3000)
   - Verify Docker resources allocation
   - Check service logs: `docker-compose logs`

3. **Template Variables Not Replaced**
   - Review archetype.rhai script
   - Check template syntax in source files
   - Verify test_answers.yaml completeness

4. **API Endpoints Fail**
   - Check if database is properly initialized
   - Verify authentication configuration
   - Review server logs for errors

### Debug Mode

For detailed debugging, check the validation log:

```bash
cat /tmp/tmp.XXXXXXXXX/validation.log
```

The log contains full output from all commands including Docker build, service startup, and test execution.

## Continuous Integration

This validation script is designed to run in CI/CD pipelines to ensure archetype quality. It returns appropriate exit codes:

- **Exit 0**: All tests passed
- **Exit 1**: One or more tests failed

The validation completes in under 2 minutes making it suitable for automated testing workflows. 