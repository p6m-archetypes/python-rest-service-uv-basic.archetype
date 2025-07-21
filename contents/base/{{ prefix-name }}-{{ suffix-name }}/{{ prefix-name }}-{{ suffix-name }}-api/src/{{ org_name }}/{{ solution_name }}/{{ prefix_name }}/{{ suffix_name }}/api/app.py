"""
FastAPI Application Factory

This module provides the main FastAPI application factory with all middleware,
routing, and configuration setup.
"""

import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.openapi.utils import get_openapi

from .config import Settings
from .routers import health, api_v1
from .middleware import (
    logging_middleware,
    metrics_middleware,
    error_handling_middleware
)


logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """
    Application lifespan manager for startup and shutdown events.
    
    Args:
        app: FastAPI application instance
        
    Yields:
        None during application runtime
    """
    # Startup
    logger.info("Starting {{ PrefixName }}{{ SuffixName }} API...")
    
    # Initialize database connections, Redis, etc.
    # await initialize_database()
    # await initialize_redis()
    
    logger.info("{{ PrefixName }}{{ SuffixName }} API started successfully")
    
    yield
    
    # Shutdown
    logger.info("Shutting down {{ PrefixName }}{{ SuffixName }} API...")
    
    # Cleanup database connections, Redis, etc.
    # await cleanup_database()
    # await cleanup_redis()
    
    logger.info("{{ PrefixName }}{{ SuffixName }} API shutdown complete")


def create_app(settings: Settings = None) -> FastAPI:
    """
    Create and configure FastAPI application.
    
    Args:
        settings: Application settings (uses global settings if not provided)
        
    Returns:
        Configured FastAPI application instance
    """
    if settings is None:
        from .config import settings as default_settings
        settings = default_settings
    
    # Create FastAPI application
    app = FastAPI(
        title=settings.api_title,
        description=settings.api_description,
        version=settings.api_version,
        debug=settings.debug,
        lifespan=lifespan,
        openapi_url="/api/v1/openapi.json" if not settings.is_development else "/openapi.json",
        docs_url="/api/v1/docs" if not settings.is_development else "/docs",
        redoc_url="/api/v1/redoc" if not settings.is_development else "/redoc",
    )
    
    # Configure CORS
    if settings.cors_origins:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=settings.cors_origins,
            allow_credentials=settings.cors_allow_credentials,
            allow_methods=settings.cors_allow_methods,
            allow_headers=settings.cors_allow_headers,
        )
    
    # Add custom middleware
    app.middleware("http")(error_handling_middleware)
    app.middleware("http")(logging_middleware)
    
    if settings.metrics_enabled:
        app.middleware("http")(metrics_middleware)
    
    # Include routers
    app.include_router(health.router, prefix="/health", tags=["Health"])
    app.include_router(api_v1.router, prefix="/api/v1", tags=["API v1"])
    
    # Custom OpenAPI schema
    def custom_openapi():
        if app.openapi_schema:
            return app.openapi_schema
        
        openapi_schema = get_openapi(
            title=settings.api_title,
            version=settings.api_version,
            description=settings.api_description,
            routes=app.routes,
        )
        
        # Add custom OpenAPI extensions
        openapi_schema["info"]["x-logo"] = {
            "url": "https://fastapi.tiangolo.com/img/logo-margin/logo-teal.png"
        }
        
        # Add security schemes for JWT
        openapi_schema["components"]["securitySchemes"] = {
            "Bearer": {
                "type": "http",
                "scheme": "bearer",
                "bearerFormat": "JWT",
                "description": "Enter JWT token"
            }
        }
        
        app.openapi_schema = openapi_schema
        return app.openapi_schema
    
    app.openapi = custom_openapi
    
    # Root endpoint
    @app.get("/", response_class=JSONResponse, include_in_schema=False)
    async def root():
        """Root endpoint providing API information."""
        return {
            "service": settings.api_title,
            "version": settings.api_version,
            "description": settings.api_description,
            "health": "/health",
            "docs": "/api/v1/docs" if not settings.is_development else "/docs",
            "openapi": "/api/v1/openapi.json" if not settings.is_development else "/openapi.json"
        }
    
    return app 