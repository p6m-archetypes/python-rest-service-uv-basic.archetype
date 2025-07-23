"""
{{ PrefixName }}{{ SuffixName }} FastAPI Application

This module creates and configures the main FastAPI application for the REST API.
Similar to how the gRPC archetype has gRPC service implementations that delegate to core services,
this FastAPI app provides REST endpoints that delegate to the same business logic.
"""

import logging
from typing import Dict, Any, Optional

import structlog
from fastapi import FastAPI, HTTPException, Depends, Query, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
from pydantic import ValidationError

from .config.settings import get_settings
from .middleware.auth import get_auth_service

# Note: These imports will work once we set up proper dependencies
# from {{ org_name }}.{{ solution_name }}.{{ prefix_name }}.{{ suffix_name }}.core.example_service_core import ExampleServiceCore
# from {{ org_name }}.{{ solution_name }}.{{ prefix_name }}.{{ suffix_name }}.api.models import (
#     ExampleDto,
#     CreateExampleResponse,
#     GetExampleRequest,
#     GetExampleResponse,
#     GetExamplesRequest,
#     GetExamplesResponse,
#     UpdateExampleResponse,
#     DeleteExampleRequest,
#     DeleteExampleResponse,
# )
# from {{ org_name }}.{{ solution_name }}.{{ prefix_name }}.{{ suffix_name }}.api.exception.service_exception import ServiceException
# from {{ org_name }}.{{ solution_name }}.{{ prefix_name }}.{{ suffix_name }}.persistence.database_config import DatabaseConfig
# from {{ org_name }}.{{ solution_name }}.{{ prefix_name }}.{{ suffix_name }}.persistence.repositories.example_repository import ExampleRepository

logger = structlog.get_logger(__name__)

# Global instances for dependency injection  
_database_config = None


async def get_database_session():
    """Get database session for dependency injection."""
    global _database_config
    if _database_config is None:
        # Placeholder for now (following gRPC archetype pattern)
        async def dummy_close(*args, **kwargs):
            pass
        
        _database_config = type('DatabaseConfig', (), {
            'health_check': lambda: True,
            'close': dummy_close,
            'get_session': lambda: dummy_close
        })()
    
    # Return a mock session for now
    mock_session = type('Session', (), {})()
    yield mock_session


async def get_{{ prefix_name }}_repository(session = Depends(get_database_session)):
    """Get repository instance for dependency injection."""
    # Placeholder for now
    example_repository = type('ExampleRepository', (), {})()
    return example_repository


async def get_{{ prefix_name }}_service(repository = Depends(get_{{ prefix_name }}_repository)):
    """Get service instance for dependency injection."""
    # Placeholder for now  
    example_service_core = type('ExampleServiceCore', (), {})()
    return example_service_core


# DTO Conversion Functions - Placeholders for now
def fastapi_to_get_{{ prefix_name }}_request({{ prefix_name }}_id: str):
    """Convert FastAPI path parameter to request object."""
    # Placeholder for now
    return type('GetRequest', (), {'id': {{ prefix_name }}_id})()


def fastapi_to_delete_{{ prefix_name }}_request({{ prefix_name }}_id: str):
    """Convert FastAPI path parameter to request object."""
    # Placeholder for now
    return type('DeleteRequest', (), {'id': {{ prefix_name }}_id})()


def fastapi_to_get_{{ prefix_name }}s_request(page: int, size: int, status: Optional[str] = None):
    """Convert FastAPI query parameters to request object."""
    # Placeholder for now
    return type('GetAllRequest', (), {
        'start_page': page,
        'page_size': size,
        'status': status
    })()


def dict_to_{{ prefix_name }}_dto(data: dict):
    """Convert dictionary data to DTO object."""
    # Placeholder for now
    return type('Dto', (), {
        'id': data.get("id"),
        'name': data["name"],
        'description': data.get("description"),
        'status': data.get("status", "active")
    })()


def create_error_response(status_code: int, message: str):
    """Create standardized error response."""
    return {
        "error": {
            "code": status_code,
            "message": message
        }
    }


def map_service_exception_to_http_error(exc):
    """Map exception to appropriate HTTP status code and message.
    
    Args:
        exc: The exception to map
        
    Returns:
        Tuple of (status_code, error_message)
    """
    # Placeholder for now - would map service exceptions once implemented
    message = str(exc)
    
    # Default error mapping
    if "not found" in message.lower():
        return 404, message
    elif "already exists" in message.lower():
        return 409, message
    elif "invalid" in message.lower() or "validation" in message.lower():
        return 400, message
    else:
        # Default to 500 for unexpected errors
        logger.error(f"Unmapped exception: {type(exc).__name__}", exc_info=True)
        return 500, "Internal server error"


def handle_service_exception(exc, operation: str, resource_id: str = None):
    """Handle exception and convert to HTTPException with proper logging.
    
    Args:
        exc: The exception to handle
        operation: Description of the operation (e.g., "creating user", "listing products")
        resource_id: Optional resource ID for context
        
    Returns:
        HTTPException with appropriate status code and message
    """
    status_code, message = map_service_exception_to_http_error(exc)
    
    # Log with appropriate level based on error type
    if status_code >= 500:
        logger.error(f"Service error {operation}", 
                    resource_id=resource_id,
                    exception_type=type(exc).__name__,
                    exc_info=True)
    elif status_code >= 400:
        logger.warning(f"Client error {operation}", 
                      resource_id=resource_id,
                      exception_type=type(exc).__name__,
                      message=message)
    
    return HTTPException(status_code=status_code, detail=message)


def handle_unexpected_exception(exc, operation: str, resource_id: str = None):
    """Handle unexpected exceptions with proper logging.
    
    Args:
        exc: The unexpected exception
        operation: Description of the operation
        resource_id: Optional resource ID for context
        
    Returns:
        HTTPException with 500 status code
    """
    logger.error(f"Unexpected error {operation}", 
                resource_id=resource_id,
                error_type=type(exc).__name__,
                error_message=str(exc),
                exc_info=True)
    
    return HTTPException(status_code=500, detail="Internal server error")


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    settings = get_settings()
    
    app = FastAPI(
        title=settings.api_title,
        description=settings.api_description,
        version=settings.api_version,
        docs_url="/docs" if settings.debug else None,
        redoc_url="/redoc" if settings.debug else None
    )
    
    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=settings.cors_allow_credentials,
        allow_methods=settings.cors_allow_methods,
        allow_headers=settings.cors_allow_headers,
    )
    
    # Add exception handlers
    _add_exception_handlers(app)
    
    # Add routes (thin wrappers that delegate to business services)
    _add_routes(app)
    
    logger.info(
        "FastAPI application created",
        title=settings.api_title,
        version=settings.api_version,
        debug=settings.debug
    )
    
    return app


def _add_exception_handlers(app: FastAPI) -> None:
    """Add global exception handlers."""
    
    @app.exception_handler(ValidationError)
    async def validation_exception_handler(request, exc):
        return JSONResponse(
            status_code=422,
            content={"error": "Validation error", "details": str(exc)}
        )
    
    @app.exception_handler(HTTPException)
    async def http_exception_handler(request, exc):
        return JSONResponse(
            status_code=exc.status_code,
            content={"error": exc.detail}
        )


def _add_routes(app: FastAPI) -> None:
    """Add API routes that delegate to business services."""
    
    # Root endpoint
    @app.get("/")
    async def root() -> Dict[str, str]:
        """Root endpoint with API information."""
        settings = get_settings()
        return {
            "service": settings.api_title,
            "version": settings.api_version,
            "status": "running"
        }
    
    # Health endpoint (basic - detailed health is in management server)
    @app.get("/health")
    async def health() -> Dict[str, str]:
        """Basic health check endpoint."""
        return {"status": "healthy"}
    
    @app.get("/health/live")
    async def liveness_check() -> Dict[str, str]:
        """Kubernetes liveness probe endpoint."""
        return {"status": "UP"}

    @app.get("/health/ready")
    async def readiness_check() -> Dict[str, str]:
        """Kubernetes readiness probe endpoint."""
        return {"status": "UP"}

    @app.get("/metrics")
    async def metrics() -> Response:
        """Prometheus metrics endpoint."""
        try:
            # Generate Prometheus metrics
            metrics_data = generate_latest()
            
            return Response(
                content=metrics_data,
                media_type=CONTENT_TYPE_LATEST
            )
        except Exception as e:
            logger.error("Failed to generate metrics", error=str(e), exc_info=True)
            raise HTTPException(status_code=500, detail="Failed to generate metrics")
    
    # Authentication endpoints
    @app.post("/auth/login")
    async def login(request: dict):
        """User login endpoint."""
        # TODO: Delegate to auth service in core layer
        # This should call {{ org_name }}.{{ solution_name }}.{{ prefix_name }}.{{ suffix_name }}.core business logic
        auth_service = get_auth_service()
        # Implementation will delegate to core business service
        raise HTTPException(status_code=501, detail="Login endpoint - to be implemented")
    
    @app.post("/auth/token")
    async def token(request: dict):
        """Token generation endpoint (alias for login)."""
        return await login(request)
    
    @app.post("/auth/refresh")
    async def refresh_token(request: dict):
        """Token refresh endpoint."""
        # TODO: Delegate to auth service in core layer
        raise HTTPException(status_code=501, detail="Token refresh - to be implemented")
    
    # {{ PrefixName }} business endpoints
    @app.get(
        "/api/v1/{{ prefix_name }}s", 
        summary="List {{ prefix_name }}s",
        description="Retrieve a paginated list of {{ prefix_name }}s with optional filtering",
        responses={
            200: {"description": "Successfully retrieved {{ prefix_name }}s"},
            400: {"description": "Invalid query parameters"},
            500: {"description": "Internal server error"}
        }
    )
    async def list_{{ prefix_name }}s(
        page: int = Query(0, ge=0, description="Page number (0-based)"),
        size: int = Query(50, ge=1, le=100, description="Number of items per page"),
        status: str = Query(None, description="Filter by {{ prefix_name }} status"),
        service = Depends(get_{{ prefix_name }}_service)
    ):
        """List {{ prefix_name }}s with pagination and optional filtering."""
        try:
            # Convert FastAPI parameters to core service request
            request = fastapi_to_get_{{ prefix_name }}s_request(page, size, status)
            
            # Delegate to core service
            result = await service.get_{{ prefix_name }}s(request)
            
            # Return the result directly (already the correct response model)
            return result
            
        except Exception as e:
            # TODO: Add proper ServiceException handling when dependencies are set up
            logger.error(f"Service error listing {{ prefix_name }}s: {e}")
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            logger.error(f"Unexpected error listing {{ prefix_name }}s: {e}")
            raise HTTPException(status_code=500, detail="Internal server error")
    
    @app.post(
        "/api/v1/{{ prefix_name }}s", 
        status_code=201,
        summary="Create {{ prefix_name }}",
        description="Create a new {{ prefix_name }} with the provided data",
        responses={
            201: {"description": "{{ PrefixName }} created successfully"},
            400: {"description": "Invalid input data or validation error"},
            409: {"description": "{{ PrefixName }} already exists"},
            500: {"description": "Internal server error"}
        }
    )
    async def create_{{ prefix_name }}(
        request: dict,
        service = Depends(get_{{ prefix_name }}_service)
    ):
        """Create a new {{ prefix_name }} with the provided data."""
        try:
            # Convert request data to DTO
            {{ prefix_name }}_dto = dict_to_{{ prefix_name }}_dto(request)
            
            # Delegate to core service
            result = await service.create_{{ prefix_name }}({{ prefix_name }}_dto)
            
            # Return the result directly (already the correct response model)
            return result
            
        except Exception as e:
            # TODO: Add proper ServiceException handling when dependencies are set up
            raise handle_service_exception(e, "creating {{ prefix_name }}")
    
    @app.get("/api/v1/{{ prefix_name }}s/{{ '{' }}{{ prefix_name }}_id{{ '}' }}")
    async def get_{{ prefix_name }}(
        {{ prefix_name }}_id: str,
        service = Depends(get_{{ prefix_name }}_service)
    ):
        """Get a specific {{ prefix_name }} by ID."""
        try:
            # Convert path parameter to service request
            request = fastapi_to_get_{{ prefix_name }}_request({{ prefix_name }}_id)
            
            # Delegate to core service
            result = await service.get_{{ prefix_name }}(request)
            
            # Return the result directly (already the correct response model)
            return result
            
        except Exception as e:
            # TODO: Add proper ServiceException handling when dependencies are set up
            raise handle_service_exception(e, f"getting {{ prefix_name }}", {{ prefix_name }}_id)
    
    @app.put("/api/v1/{{ prefix_name }}s/{{ '{' }}{{ prefix_name }}_id{{ '}' }}")
    async def update_{{ prefix_name }}(
        {{ prefix_name }}_id: str,
        request: dict,
        service = Depends(get_{{ prefix_name }}_service)
    ):
        """Update an existing {{ prefix_name }}."""
        try:
            # Convert request data to DTO and set the ID
            {{ prefix_name }}_dto = dict_to_{{ prefix_name }}_dto(request)
            {{ prefix_name }}_dto.id = {{ prefix_name }}_id
            
            # Delegate to core service
            result = await service.update_{{ prefix_name }}({{ prefix_name }}_dto)
            
            # Return the result directly (already the correct response model)
            return result
            
        except Exception as e:
            # TODO: Add proper ServiceException handling when dependencies are set up
            logger.error(f"Service error updating {{ prefix_name }} {{ '{' }}{{ prefix_name }}_id{{ '}' }}: {e}")
            if "not found" in str(e).lower():
                raise HTTPException(status_code=404, detail=str(e))
            else:
                raise HTTPException(status_code=400, detail=str(e))
    
    @app.delete("/api/v1/{{ prefix_name }}s/{{ '{' }}{{ prefix_name }}_id{{ '}' }}", status_code=200)
    async def delete_{{ prefix_name }}(
        {{ prefix_name }}_id: str,
        service = Depends(get_{{ prefix_name }}_service)
    ):
        """Delete a {{ prefix_name }} by ID."""
        try:
            # Convert FastAPI parameter to core service request
            request = fastapi_to_delete_{{ prefix_name }}_request({{ prefix_name }}_id)
            
            # Delegate to core service
            result = await service.delete_{{ prefix_name }}(request)
            
            # Return the result directly (already the correct response model)
            return result
            
        except Exception as e:
            # TODO: Add proper ServiceException handling when dependencies are set up
            logger.error(f"Service error deleting {{ prefix_name }} {{ '{' }}{{ prefix_name }}_id{{ '}' }}: {e}")
            if "not found" in str(e).lower():
                raise HTTPException(status_code=404, detail=str(e))
            else:
                raise HTTPException(status_code=400, detail=str(e))


# Create the application instance
app = create_app() 