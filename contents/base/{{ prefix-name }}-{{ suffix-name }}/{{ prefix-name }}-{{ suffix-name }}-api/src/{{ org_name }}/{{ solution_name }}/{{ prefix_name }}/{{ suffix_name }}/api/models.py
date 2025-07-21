"""Data transfer objects for the {{ PrefixName }} Service API."""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class {{ PrefixName }}Dto(BaseModel):
    """Data transfer object for {{ PrefixName }} entities."""
    
    id: Optional[str] = Field(None, description="Unique identifier for the {{ prefix_name }}")
    name: str = Field(..., description="Name of the {{ prefix_name }}", min_length=1, max_length=255)
    description: Optional[str] = Field(None, description="Description of the {{ prefix_name }}")
    status: str = Field("ACTIVE", description="Status of the {{ prefix_name }}")
    created_at: Optional[datetime] = Field(None, description="Creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Last update timestamp")
    version: int = Field(1, description="Version for optimistic locking")

    class Config:
        """Pydantic configuration."""
        json_encoders = {
            # Add any custom encoders here if needed
        }


class Get{{ PrefixName }}Request(BaseModel):
    """Request model for getting a single {{ prefix_name }}."""
    
    id: str = Field(..., description="The ID of the {{ prefix_name }} to retrieve")


class Get{{ PrefixName }}Response(BaseModel):
    """Response model for getting a single {{ prefix_name }}."""
    
    {{ prefix_name }}: {{ PrefixName }}Dto = Field(..., description="The requested {{ prefix_name }}")


class Get{{ PrefixName }}sRequest(BaseModel):
    """Request model for getting multiple {{ prefix_name }}s with pagination."""
    
    start_page: int = Field(0, description="Starting page number (0-based)", ge=0)
    page_size: int = Field(10, description="Number of items per page", ge=1, le=100)
    status: Optional[str] = Field(None, description="Filter by status")
    search: Optional[str] = Field(None, description="Search term for name")


class Get{{ PrefixName }}sResponse(BaseModel):
    """Response model for getting multiple {{ prefix_name }}s with pagination metadata."""
    
    {{ prefix_name }}s: List[{{ PrefixName }}Dto] = Field(default_factory=list, description="List of {{ prefix_name }}s")
    has_next: bool = Field(False, description="Whether there is a next page")
    has_previous: bool = Field(False, description="Whether there is a previous page")
    next_page: int = Field(0, description="Next page number")
    previous_page: int = Field(0, description="Previous page number")
    total_pages: int = Field(0, description="Total number of pages")
    total_elements: int = Field(0, description="Total number of elements")


class Create{{ PrefixName }}Request(BaseModel):
    """Request model for creating a {{ prefix_name }}."""
    
    name: str = Field(..., description="Name of the {{ prefix_name }}", min_length=1, max_length=255)
    description: Optional[str] = Field(None, description="Description of the {{ prefix_name }}")
    status: str = Field("ACTIVE", description="Status of the {{ prefix_name }}")


class Create{{ PrefixName }}Response(BaseModel):
    """Response model for creating a {{ prefix_name }}."""
    
    {{ prefix_name }}: {{ PrefixName }}Dto = Field(..., description="The created {{ prefix_name }}")


class Update{{ PrefixName }}Request(BaseModel):
    """Request model for updating a {{ prefix_name }}."""
    
    name: Optional[str] = Field(None, description="Name of the {{ prefix_name }}", min_length=1, max_length=255)
    description: Optional[str] = Field(None, description="Description of the {{ prefix_name }}")
    status: Optional[str] = Field(None, description="Status of the {{ prefix_name }}")


class Update{{ PrefixName }}Response(BaseModel):
    """Response model for updating a {{ prefix_name }}."""
    
    {{ prefix_name }}: {{ PrefixName }}Dto = Field(..., description="The updated {{ prefix_name }}")


class Delete{{ PrefixName }}Request(BaseModel):
    """Request model for deleting a {{ prefix_name }}."""
    
    id: str = Field(..., description="The ID of the {{ prefix_name }} to delete")


class Delete{{ PrefixName }}Response(BaseModel):
    """Response model for deleting a {{ prefix_name }}."""
    
    message: str = Field(..., description="Confirmation message")


class HealthCheckResponse(BaseModel):
    """Response model for health check."""
    
    status: str = Field(..., description="Overall health status")
    timestamp: datetime = Field(..., description="Timestamp of the health check")
    checks: dict = Field(default_factory=dict, description="Individual health check results") 