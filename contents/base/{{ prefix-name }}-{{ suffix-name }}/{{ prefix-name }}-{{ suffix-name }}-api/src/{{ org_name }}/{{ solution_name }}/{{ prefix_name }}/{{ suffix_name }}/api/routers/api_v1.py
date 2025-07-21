"""
API v1 Router

This module provides the main API v1 endpoints for {{ PrefixName }}{{ SuffixName }} service.
"""

import logging
from typing import Dict, List, Any, Optional
from uuid import UUID

from fastapi import APIRouter, HTTPException, status, Depends, Query
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

# Import persistence layer
from ....persistence import (
    get_db_session,
    {{ PrefixName }}Repository,
    {{ PrefixName }}Entity,
    PageRequest,
)

# Import API models
from ..models import (
    {{ PrefixName }}Dto,
    Get{{ PrefixName }}Request,
    Get{{ PrefixName }}Response,
    Get{{ PrefixName }}sRequest, 
    Get{{ PrefixName }}sResponse,
    Create{{ PrefixName }}Request,
    Create{{ PrefixName }}Response,
    Update{{ PrefixName }}Request,
    Update{{ PrefixName }}Response,
    Delete{{ PrefixName }}Request,
    Delete{{ PrefixName }}Response,
)

logger = logging.getLogger(__name__)
router = APIRouter()


async def get_{{ prefix_name }}_repository(db: AsyncSession = Depends(get_db_session)) -> {{ PrefixName }}Repository:
    """Get {{ PrefixName }} repository instance."""
    return {{ PrefixName }}Repository(db)


def entity_to_dto(entity: {{ PrefixName }}Entity) -> {{ PrefixName }}Dto:
    """Convert {{ PrefixName }}Entity to {{ PrefixName }}Dto."""
    return {{ PrefixName }}Dto(
        id=str(entity.id),
        name=entity.name,
        description=entity.description,
        status=entity.status,
        created_at=entity.created_at,
        updated_at=entity.updated_at,
        version=entity.version
    )


@router.get("/", response_model=Dict[str, Any])
async def api_info() -> Dict[str, Any]:
    """
    Get API information and available endpoints.
    
    Returns:
        API information and available endpoints
    """
    return {
        "name": "{{ PrefixName }}{{ SuffixName }} API v1",
        "version": "1.0.0",
        "description": "RESTful API for {{ PrefixName }}{{ SuffixName }} management",
        "endpoints": {
            "{{ prefix_name | lower }}s": "/api/v1/{{ prefix_name | lower }}s",
            "health": "/health",
            "metrics": "/health/metrics",
            "docs": "/api/v1/docs"
        }
    }


@router.get("/{{ prefix_name | lower }}s", response_model=Get{{ PrefixName }}sResponse)
async def list_{{ prefix_name | lower }}s(
    start_page: int = Query(0, ge=0, description="Starting page number (0-based)"),
    page_size: int = Query(10, ge=1, le=100, description="Number of items per page"),
    status: Optional[str] = Query(None, description="Filter by status"),
    search: Optional[str] = Query(None, description="Search term for name"),
    repository: {{ PrefixName }}Repository = Depends(get_{{ prefix_name }}_repository)
) -> Get{{ PrefixName }}sResponse:
    """
    List all {{ prefix_name | lower }}s with pagination.
    
    Args:
        start_page: Starting page number (0-based)
        page_size: Number of items per page
        status: Filter by status
        search: Search term for name
        repository: {{ PrefixName }} repository instance
        
    Returns:
        Paginated list of {{ prefix_name | lower }}s
    """
    try:
        filters = {}
        if status:
            filters["status"] = status
        if search:
            filters["name__ilike"] = f"%{search}%"
        
        # Get paginated results
        page_request = PageRequest(page=start_page, size=page_size)
        page_result = await repository.get_all(
            offset=page_request.offset,
            limit=page_request.size,
            filters=filters
        )
        
        # Convert entities to DTOs
        {{ prefix_name }}_dtos = [entity_to_dto(entity) for entity in page_result.items]
        
        return Get{{ PrefixName }}sResponse(
            {{ prefix_name }}s={{ prefix_name }}_dtos,
            has_next=page_result.has_next,
            has_previous=page_result.has_previous,
            next_page=page_result.next_page,
            previous_page=page_result.previous_page,
            total_pages=page_result.total_pages,
            total_elements=page_result.total_elements
        )
        
    except Exception as exc:
        logger.error(f"Error listing {{ prefix_name | lower }}s: {str(exc)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve {{ prefix_name | lower }}s"
        )


@router.post("/{{ prefix_name | lower }}s", response_model=Create{{ PrefixName }}Response, status_code=status.HTTP_201_CREATED)
async def create_{{ prefix_name | lower }}(
    {{ prefix_name | lower }}_data: Create{{ PrefixName }}Request,
    repository: {{ PrefixName }}Repository = Depends(get_{{ prefix_name }}_repository)
) -> Create{{ PrefixName }}Response:
    """
    Create a new {{ prefix_name | lower }}.
    
    Args:
        {{ prefix_name | lower }}_data: {{ PrefixName }} creation data
        repository: {{ PrefixName }} repository instance
        
    Returns:
        Created {{ prefix_name | lower }}
    """
    try:
        # Create new entity
        entity_data = {
            "name": {{ prefix_name | lower }}_data.name,
            "description": {{ prefix_name | lower }}_data.description,
            "status": {{ prefix_name | lower }}_data.status
        }
        
        entity = await repository.create(entity_data)
        {{ prefix_name }}_dto = entity_to_dto(entity)
        
        return Create{{ PrefixName }}Response({{ prefix_name }}={{ prefix_name }}_dto)
        
    except ValueError as exc:
        logger.warning(f"Validation error creating {{ prefix_name | lower }}: {str(exc)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc)
        )
    except Exception as exc:
        logger.error(f"Error creating {{ prefix_name | lower }}: {str(exc)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create {{ prefix_name | lower }}"
        )


@router.get("/{{ prefix_name | lower }}s/{{{ prefix_name | lower }}_id}", response_model=Get{{ PrefixName }}Response)
async def get_{{ prefix_name | lower }}(
    {{ prefix_name | lower }}_id: str,
    repository: {{ PrefixName }}Repository = Depends(get_{{ prefix_name }}_repository)
) -> Get{{ PrefixName }}Response:
    """
    Get a {{ prefix_name | lower }} by ID.
    
    Args:
        {{ prefix_name | lower }}_id: {{ PrefixName }} ID (UUID)
        repository: {{ PrefixName }} repository instance
        
    Returns:
        {{ PrefixName }} details
    """
    try:
        # Parse UUID
        try:
            entity_id = UUID({{ prefix_name | lower }}_id)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid UUID format"
            )
        
        entity = await repository.get_by_id(entity_id)
        if not entity:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"{{ PrefixName }} with ID {{{ prefix_name | lower }}_id}} not found"
            )
        
        {{ prefix_name }}_dto = entity_to_dto(entity)
        return Get{{ PrefixName }}Response({{ prefix_name }}={{ prefix_name }}_dto)
        
    except HTTPException:
        raise
    except Exception as exc:
        logger.error(f"Error retrieving {{ prefix_name | lower }} {{{ prefix_name | lower }}_id}}: {str(exc)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve {{ prefix_name | lower }}"
        )


@router.put("/{{ prefix_name | lower }}s/{{{ prefix_name | lower }}_id}", response_model=Update{{ PrefixName }}Response)
async def update_{{ prefix_name | lower }}(
    {{ prefix_name | lower }}_id: str,
    {{ prefix_name | lower }}_data: Update{{ PrefixName }}Request,
    repository: {{ PrefixName }}Repository = Depends(get_{{ prefix_name }}_repository)
) -> Update{{ PrefixName }}Response:
    """
    Update a {{ prefix_name | lower }} by ID.
    
    Args:
        {{ prefix_name | lower }}_id: {{ PrefixName }} ID (UUID)
        {{ prefix_name | lower }}_data: {{ PrefixName }} update data
        repository: {{ PrefixName }} repository instance
        
    Returns:
        Updated {{ prefix_name | lower }}
    """
    try:
        # Parse UUID
        try:
            entity_id = UUID({{ prefix_name | lower }}_id)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid UUID format"
            )
        
        # Prepare update data (only include non-None fields)
        update_data = {}
        if {{ prefix_name | lower }}_data.name is not None:
            update_data["name"] = {{ prefix_name | lower }}_data.name
        if {{ prefix_name | lower }}_data.description is not None:
            update_data["description"] = {{ prefix_name | lower }}_data.description
        if {{ prefix_name | lower }}_data.status is not None:
            update_data["status"] = {{ prefix_name | lower }}_data.status
        
        entity = await repository.update(entity_id, update_data)
        if not entity:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"{{ PrefixName }} with ID {{{ prefix_name | lower }}_id}} not found"
            )
        
        {{ prefix_name }}_dto = entity_to_dto(entity)
        return Update{{ PrefixName }}Response({{ prefix_name }}={{ prefix_name }}_dto)
        
    except HTTPException:
        raise
    except ValueError as exc:
        logger.warning(f"Validation error updating {{ prefix_name | lower }} {{{ prefix_name | lower }}_id}}: {str(exc)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc)
        )
    except Exception as exc:
        logger.error(f"Error updating {{ prefix_name | lower }} {{{ prefix_name | lower }}_id}}: {str(exc)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update {{ prefix_name | lower }}"
        )


@router.delete("/{{ prefix_name | lower }}s/{{{ prefix_name | lower }}_id}", response_model=Delete{{ PrefixName }}Response)
async def delete_{{ prefix_name | lower }}(
    {{ prefix_name | lower }}_id: str,
    repository: {{ PrefixName }}Repository = Depends(get_{{ prefix_name }}_repository)
) -> Delete{{ PrefixName }}Response:
    """
    Delete a {{ prefix_name | lower }} by ID.
    
    Args:
        {{ prefix_name | lower }}_id: {{ PrefixName }} ID (UUID)
        repository: {{ PrefixName }} repository instance
        
    Returns:
        Deletion confirmation message
    """
    try:
        # Parse UUID
        try:
            entity_id = UUID({{ prefix_name | lower }}_id)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid UUID format"
            )
        
        success = await repository.delete(entity_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"{{ PrefixName }} with ID {{{ prefix_name | lower }}_id}} not found"
            )
        
        return Delete{{ PrefixName }}Response(
            message=f"{{ PrefixName }} with ID {{{ prefix_name | lower }}_id}} successfully deleted"
        )
        
    except HTTPException:
        raise
    except Exception as exc:
        logger.error(f"Error deleting {{ prefix_name | lower }} {{{ prefix_name | lower }}_id}}: {str(exc)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete {{ prefix_name | lower }}"
        ) 