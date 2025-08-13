# Python REST Service Basic Archetype

![Latest Release](https://img.shields.io/github/v/release/p6m-archetypes/python-rest-service-uv-basic.archetype?style=flat-square&label=Latest%20Release&color=blue)

A production-ready [Archetect](https://archetect.github.io/) archetype for generating modular, enterprise-grade Python REST services with modern tooling and best practices.

## 🎯 What This Generates

This archetype creates a complete, production-ready REST service with:

- **🏗️ Modular Architecture**: Separate packages for API, core logic, persistence, server, and client
- **⚡ Modern Python Tooling**: UV for dependency management, modern pyproject.toml configuration
- **🐳 Docker-Ready**: Complete containerization with Docker Compose orchestration
- **📊 Monitoring Stack**: Integrated Prometheus metrics and Grafana dashboards
- **🧪 Comprehensive Testing**: Unit, integration, and REST connectivity tests
- **🔄 CI/CD Pipeline**: GitHub Actions workflows for testing, building, and deployment
- **📋 Health Checks**: Built-in health endpoints and service monitoring
- **🔧 Development Tools**: Scripts for setup, testing, and database management

## 📦 Generated Service Structure

```
my-awesome-service/
├── my-awesome-service-api/          # API contracts and models
├── my-awesome-service-core/         # Business logic
├── my-awesome-service-persistence/  # Database layer with migrations
├── my-awesome-service-server/       # FastAPI server implementation
├── my-awesome-service-client/       # HTTP client library
├── my-awesome-service-integration-tests/  # End-to-end tests
├── monitoring/                      # Grafana & Prometheus config
├── scripts/                         # Development utilities
├── docker-compose.yml              # Complete stack orchestration
└── Dockerfile                      # Multi-stage production build
```

## 🚀 Quick Start

### Prerequisites

- [Archetect](https://archetect.github.io/) CLI tool
- Git access to this repository

### Generate a New Service

```bash
# Generate a new service
archetect render https://github.com/p6m-archetypes/python-rest-service-basic.archetype.git#v1

# Answer the prompts:
# org-name: myorg
# solution-name: myproject
# prefix-name: awesome
# suffix-name: service

# Result: my-new-service/ directory with awesome-service REST API
```

### Development Workflow

```bash
cd my-new-service

# 1. Sync all packages
find . -name "pyproject.toml" -exec sh -c 'cd "$(dirname "$1")" && echo "Syncing $(pwd)" && uv sync' _ {} \;

# 2. Start the complete stack
docker-compose up -d

# 3. Run integration tests
./scripts/run-tests.sh

# 4. Access your service
# - REST API: http://localhost:8080
# - Health: http://localhost:8080/health
# - OpenAPI Docs: http://localhost:8080/docs
# - Metrics: http://localhost:8080/metrics
# - Grafana: http://localhost:3000 (admin/admin)
# - Prometheus: http://localhost:9090
```

## ✨ Key Features

### 🏛️ Enterprise Architecture

- **Hexagonal Architecture**: Clean separation of concerns
- **Modular Design**: Independent, reusable packages
- **Dependency Injection**: Proper service layer organization
- **Error Handling**: Structured exception management

### 🔧 Modern Python Ecosystem

- **UV Package Manager**: Fast, reliable dependency management
- **Python 3.11+**: Modern language features and performance
- **FastAPI**: High-performance, modern async web framework
- **Pydantic**: Type-safe data validation and serialization
- **SQLAlchemy 2.0**: Modern ORM with async support
- **Structured Logging**: JSON-structured logs with contextual information

### 📊 Production Monitoring

- **Prometheus Metrics**: Business and technical metrics
- **Grafana Dashboards**: Pre-configured service monitoring
- **Health Checks**: Comprehensive service health reporting
- **OpenTelemetry**: Distributed tracing and observability

### 🧪 Testing Excellence

- **pytest Framework**: Modern testing with async support
- **TestContainers**: Isolated integration testing
- **HTTP Testing**: Comprehensive REST API connectivity validation
- **Coverage Reporting**: Code coverage with HTML reports
- **CI Integration**: Automated testing in GitHub Actions

### 🚢 Production Ready

- **Multi-stage Dockerfile**: Optimized container builds
- **Docker Compose**: Complete development environment
- **Database Migrations**: Alembic-powered schema management
- **Security**: JWT authentication and rate limiting middleware
- **Performance**: Connection pooling and async operations
- **OpenAPI Documentation**: Auto-generated API documentation

## 📋 Validation & Quality

This archetype includes a comprehensive validation suite that ensures generated services meet production standards:

- **✅ 0 manual fixes required** - Services work immediately after generation
- **✅ <2 minutes from generation to running service** - Fast development cycle
- **✅ 100% integration test pass rate** - Reliable, tested code
- **✅ Template validation** - No hardcoded values remain

Run the validation suite:

```bash
./validate_archetype.sh
```

## 🛠️ Recent Improvements

This archetype has been extensively updated and tested:

### Fixed Issues ✅

1. **Package Configuration Modernization** - Updated all pyproject.toml files to modern standards
2. **FastAPI Version Consistency** - Pinned FastAPI and dependencies to stable versions
3. **Python Package Structure** - Fixed namespace organization and import paths
4. **Docker Configuration** - Updated container setup for reliable operation
5. **Monitoring Infrastructure** - Added complete Prometheus/Grafana stack
6. **Integration Testing** - Fixed pytest hooks and REST connectivity tests
7. **CI/CD Pipelines** - Updated GitHub Actions with proper template variables
8. **Database Configuration** - Replaced hardcoded database references
9. **Build System** - Cleaned up package references and dependencies
10. **Template Validation** - Created comprehensive validation tools
11. **Test Structure Alignment** - Aligned test patterns with gRPC archetype for consistency
12. **Port Configuration** - Standardized on port 8080 for REST services

### Verification ✅

- **Comprehensive test suite** validates all success criteria
- **Reference implementation** comparison ensures correctness
- **Integration testing** covers all service components
- **Monitoring validation** confirms observability stack works
- **CI/CD testing** verifies automation pipelines

## 📚 Documentation

Generated services include comprehensive documentation:

- **README.md** - Complete setup and usage instructions
- **OpenAPI Documentation** - Interactive API documentation at `/docs`
- **Development Guide** - Local development workflow
- **Deployment Guide** - Production deployment instructions
- **Monitoring Guide** - Observability and alerting setup

## 🔧 API Features

### REST Endpoints

- **CRUD Operations**: Complete Create, Read, Update, Delete functionality
- **Pagination**: Built-in pagination support for list endpoints
- **Filtering**: Query parameter filtering capabilities
- **Validation**: Automatic request/response validation with Pydantic
- **Error Handling**: Consistent error responses with proper HTTP status codes

### Documentation

- **OpenAPI 3.0**: Auto-generated OpenAPI/Swagger specifications
- **Interactive Docs**: Swagger UI at `/docs` and ReDoc at `/redoc`
- **Schema Validation**: Runtime request/response validation
- **Type Safety**: Full type hints throughout the codebase

## 🤝 Contributing

This archetype is actively maintained and improved. For issues or enhancements:

1. Check existing issues in the repository
2. Create detailed bug reports or feature requests
3. Follow the contribution guidelines
4. Test changes with the validation suite

## 📄 License

This archetype is released under the MIT License. Generated services inherit this license but can be changed as needed for your organization.

---

**Ready to build production-grade REST services?** Generate your first service with the command above and have a fully functional microservice running in under 2 minutes! 🚀
