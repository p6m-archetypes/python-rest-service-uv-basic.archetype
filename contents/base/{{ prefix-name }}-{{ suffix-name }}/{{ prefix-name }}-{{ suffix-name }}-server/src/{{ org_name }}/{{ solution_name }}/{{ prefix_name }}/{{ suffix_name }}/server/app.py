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

logger = logging.getLogger(__name__)


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
    @app.get("/api/v1/{{ prefix_name }}s")
    async def list_{{ prefix_name }}s(
        page: int = Query(0, ge=0),
        size: int = Query(50, ge=1, le=100),
        status: str = Query(None)
    ):
        """List {{ prefix_name }}s with pagination."""
        # TODO: Delegate to {{ PrefixName }}Service in core layer
        # This should call {{ org_name }}.{{ solution_name }}.{{ prefix_name }}.{{ suffix_name }}.core.{{ prefix_name }}_service_core
        raise HTTPException(status_code=501, detail="List {{ prefix_name }}s - to be implemented")
    
    @app.post("/api/v1/{{ prefix_name }}s")
    async def create_{{ prefix_name }}(request: dict):
        """Create a new {{ prefix_name }}."""
        # TODO: Delegate to {{ PrefixName }}Service in core layer
        raise HTTPException(status_code=501, detail="Create {{ prefix_name }} - to be implemented")
    
    @app.get("/api/v1/{{ prefix_name }}s/{{{ prefix_name }}_id}")
    async def get_{{ prefix_name }}({{ prefix_name }}_id: str):
        """Get a specific {{ prefix_name }} by ID."""
        # TODO: Delegate to {{ PrefixName }}Service in core layer
        raise HTTPException(status_code=501, detail="Get {{ prefix_name }} - to be implemented")
    
    @app.put("/api/v1/{{ prefix_name }}s/{{{ prefix_name }}_id}")
    async def update_{{ prefix_name }}({{ prefix_name }}_id: str, request: dict):
        """Update an existing {{ prefix_name }}."""
        # TODO: Delegate to {{ PrefixName }}Service in core layer
        raise HTTPException(status_code=501, detail="Update {{ prefix_name }} - to be implemented")
    
    @app.delete("/api/v1/{{ prefix_name }}s/{{{ prefix_name }}_id}")
    async def delete_{{ prefix_name }}({{ prefix_name }}_id: str):
        """Delete a {{ prefix_name }}."""
        # TODO: Delegate to {{ PrefixName }}Service in core layer
        raise HTTPException(status_code=501, detail="Delete {{ prefix_name }} - to be implemented")


# Create the application instance
app = create_app() 