"""
{{ PrefixName }}{{ SuffixName }} FastAPI Application

This module creates and configures the main FastAPI application for the REST API.
Similar to how the gRPC archetype has gRPC service implementations that delegate to core services,
this FastAPI app provides REST endpoints that delegate to the same business logic.
"""

import logging
from typing import Dict, Any

from fastapi import FastAPI, HTTPException, Depends, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import ValidationError

from .config.settings import get_settings
from .middleware.auth import get_auth_service

# Core service imports
from {{ org_name }}.{{ solution_name }}.{{ prefix_name }}.{{ suffix_name }}.core.{{ prefix_name }}_service_core import {{ PrefixName }}ServiceCore
from {{ org_name }}.{{ solution_name }}.{{ prefix_name }}.{{ suffix_name }}.api.models import (
    {{ PrefixName }}Dto,
    Create{{ PrefixName }}Response,
    Get{{ PrefixName }}Request,
    Get{{ PrefixName }}Response,
    Get{{ PrefixName }}sRequest,
    Get{{ PrefixName }}sResponse,
    Update{{ PrefixName }}Response,
    Delete{{ PrefixName }}Request,
    Delete{{ PrefixName }}Response,
)
from {{ org_name }}.{{ solution_name }}.{{ prefix_name }}.{{ suffix_name }}.api.exception.service_exception import ServiceException

# Persistence imports for dependency injection
from {{ org_name }}.{{ solution_name }}.{{ prefix_name }}.{{ suffix_name }}.persistence.database_config import DatabaseConfig
from {{ org_name }}.{{ solution_name }}.{{ prefix_name }}.{{ suffix_name }}.persistence.repositories.{{ prefix_name }}_repository import {{ PrefixName }}Repository

logger = logging.getLogger(__name__)

# Global instances for dependency injection
_database_config: DatabaseConfig = None


async def get_database_session():
    """Get database session for dependency injection."""
    global _database_config
    if _database_config is None:
        _database_config = DatabaseConfig()
        await _database_config.initialize()
    
    async with _database_config.get_session() as session:
        yield session


async def get_{{ prefix_name }}_repository(session = Depends(get_database_session)) -> {{ PrefixName }}Repository:
    """Get {{ PrefixName }} repository instance for dependency injection."""
    return {{ PrefixName }}Repository(session)


async def get_{{ prefix_name }}_service(repository: {{ PrefixName }}Repository = Depends(get_{{ prefix_name }}_repository)) -> {{ PrefixName }}ServiceCore:
    """Get {{ PrefixName }} service instance for dependency injection."""
    return {{ PrefixName }}ServiceCore(repository)


# DTO Conversion Functions
def fastapi_to_get_{{ prefix_name }}_request({{ prefix_name }}_id: str) -> Get{{ PrefixName }}Request:
    """Convert FastAPI path parameter to Get{{ PrefixName }}Request."""
    return Get{{ PrefixName }}Request(id={{ prefix_name }}_id)


def fastapi_to_delete_{{ prefix_name }}_request({{ prefix_name }}_id: str) -> Delete{{ PrefixName }}Request:
    """Convert FastAPI path parameter to Delete{{ PrefixName }}Request."""
    return Delete{{ PrefixName }}Request(id={{ prefix_name }}_id)


def fastapi_to_get_{{ prefix_name }}s_request(page: int, size: int, status: Optional[str] = None) -> Get{{ PrefixName }}sRequest:
    """Convert FastAPI query parameters to Get{{ PrefixName }}sRequest."""
    return Get{{ PrefixName }}sRequest(
        start_page=page,
        page_size=size,
        status=status
    )


def dict_to_{{ prefix_name }}_dto(data: dict) -> {{ PrefixName }}Dto:
    """Convert dictionary data to {{ PrefixName }}Dto."""
    return {{ PrefixName }}Dto(
        id=data.get("id"),
        name=data["name"],
        description=data.get("description"),
        status=data.get("status", "active")
    )


def create_error_response(status_code: int, message: str) -> Dict[str, Any]:
    """Create standardized error response."""
    return {
        "error": {
            "code": status_code,
            "message": message
        }
    }


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
    @app.get("/api/v1/{{ prefix_name }}s", response_model=Get{{ PrefixName }}sResponse)
    async def list_{{ prefix_name }}s(
        page: int = Query(0, ge=0),
        size: int = Query(50, ge=1, le=100),
        status: str = Query(None),
        service: {{ PrefixName }}ServiceCore = Depends(get_{{ prefix_name }}_service)
    ):
        """List {{ prefix_name }}s with pagination."""
        try:
            # Convert FastAPI parameters to core service request
            request = fastapi_to_get_{{ prefix_name }}s_request(page, size, status)
            
            # Delegate to core service
            result = await service.get_{{ prefix_name }}s(request)
            
            # Return the result directly (already the correct response model)
            return result
            
        except ServiceException as e:
            logger.error(f"Service error listing {{ prefix_name }}s: {e}")
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            logger.error(f"Unexpected error listing {{ prefix_name }}s: {e}")
            raise HTTPException(status_code=500, detail="Internal server error")
    
    @app.post("/api/v1/{{ prefix_name }}s", response_model=Create{{ PrefixName }}Response, status_code=201)
    async def create_{{ prefix_name }}(
        request: dict,
        service: {{ PrefixName }}ServiceCore = Depends(get_{{ prefix_name }}_service)
    ):
        """Create a new {{ prefix_name }}."""
        try:
            # Convert request data to DTO
            {{ prefix_name }}_dto = dict_to_{{ prefix_name }}_dto(request)
            
            # Delegate to core service
            result = await service.create_{{ prefix_name }}({{ prefix_name }}_dto)
            
            # Return the result directly (already the correct response model)
            return result
            
        except ServiceException as e:
            logger.error(f"Service error creating {{ prefix_name }}: {e}")
            if "already exists" in str(e).lower():
                raise HTTPException(status_code=409, detail=str(e))
            elif "validation" in str(e).lower() or "invalid" in str(e).lower():
                raise HTTPException(status_code=400, detail=str(e))
            else:
                raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            logger.error(f"Unexpected error creating {{ prefix_name }}: {e}")
            raise HTTPException(status_code=500, detail="Internal server error")
    
    @app.get("/api/v1/{{ prefix_name }}s/{{{ prefix_name }}_id}", response_model=Get{{ PrefixName }}Response)
    async def get_{{ prefix_name }}(
        {{ prefix_name }}_id: str,
        service: {{ PrefixName }}ServiceCore = Depends(get_{{ prefix_name }}_service)
    ):
        """Get a specific {{ prefix_name }} by ID."""
        try:
            # Convert path parameter to service request
            request = fastapi_to_get_{{ prefix_name }}_request({{ prefix_name }}_id)
            
            # Delegate to core service
            result = await service.get_{{ prefix_name }}(request)
            
            # Return the result directly (already the correct response model)
            return result
            
        except ServiceException as e:
            logger.error(f"Service error getting {{ prefix_name }} {{{ prefix_name }}_id}: {e}")
            if "not found" in str(e).lower():
                raise HTTPException(status_code=404, detail=str(e))
            elif "invalid" in str(e).lower():
                raise HTTPException(status_code=400, detail=str(e))
            else:
                raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            logger.error(f"Unexpected error getting {{ prefix_name }} {{{ prefix_name }}_id}: {e}")
            raise HTTPException(status_code=500, detail="Internal server error")
    
    @app.put("/api/v1/{{ prefix_name }}s/{{{ prefix_name }}_id}", response_model=Update{{ PrefixName }}Response)
    async def update_{{ prefix_name }}(
        {{ prefix_name }}_id: str,
        request: dict,
        service: {{ PrefixName }}ServiceCore = Depends(get_{{ prefix_name }}_service)
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
            
        except ServiceException as e:
            logger.error(f"Service error updating {{ prefix_name }} {{{ prefix_name }}_id}: {e}")
            if "not found" in str(e).lower():
                raise HTTPException(status_code=404, detail=str(e))
            elif "validation" in str(e).lower() or "invalid" in str(e).lower():
                raise HTTPException(status_code=400, detail=str(e))
            else:
                raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            logger.error(f"Unexpected error updating {{ prefix_name }} {{{ prefix_name }}_id}: {e}")
            raise HTTPException(status_code=500, detail="Internal server error")
    
    @app.delete("/api/v1/{{ prefix_name }}s/{{{ prefix_name }}_id}", response_model=Delete{{ PrefixName }}Response, status_code=200)
    async def delete_{{ prefix_name }}(
        {{ prefix_name }}_id: str,
        service: {{ PrefixName }}ServiceCore = Depends(get_{{ prefix_name }}_service)
    ):
        """Delete a {{ prefix_name }}."""
        try:
            # Convert path parameter to service request
            request = fastapi_to_delete_{{ prefix_name }}_request({{ prefix_name }}_id)
            
            # Delegate to core service
            result = await service.delete_{{ prefix_name }}(request)
            
            # Return the result directly (already the correct response model)
            return result
            
        except ServiceException as e:
            logger.error(f"Service error deleting {{ prefix_name }} {{{ prefix_name }}_id}: {e}")
            if "not found" in str(e).lower():
                raise HTTPException(status_code=404, detail=str(e))
            elif "invalid" in str(e).lower():
                raise HTTPException(status_code=400, detail=str(e))
            else:
                raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            logger.error(f"Unexpected error deleting {{ prefix_name }} {{{ prefix_name }}_id}: {e}")
            raise HTTPException(status_code=500, detail="Internal server error")


# Create the application instance
app = create_app() 