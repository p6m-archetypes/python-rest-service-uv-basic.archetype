"""Core business logic implementation for the Example Service."""

import uuid
from typing import Optional

import structlog

# Fixed imports - matching our actual module structure
from {{ org_name }}.{{ solution_name }}.{{ prefix_name }}.{{ suffix_name }}.api.{{ prefix_name }}_service import {{ PrefixName }}{{ SuffixName }}
from {{ org_name }}.{{ solution_name }}.{{ prefix_name }}.{{ suffix_name }}.api.models import (
    Create{{ PrefixName }}Response,
    Delete{{ PrefixName }}Request,
    Delete{{ PrefixName }}Response,
    {{ PrefixName }}Dto,
    Get{{ PrefixName }}Request,
    Get{{ PrefixName }}Response,
    Get{{ PrefixName }}sRequest,
    Get{{ PrefixName }}sResponse,
    Update{{ PrefixName }}Response,
)
from {{ org_name }}.{{ solution_name }}.{{ prefix_name }}.{{ suffix_name }}.api.exception.service_exception import ServiceException
from {{ org_name }}.{{ solution_name }}.{{ prefix_name }}.{{ suffix_name }}.persistence.repositories.{{ prefix_name }}_repository import {{ PrefixName }}Repository
from {{ org_name }}.{{ solution_name }}.{{ prefix_name }}.{{ suffix_name }}.persistence.entities.{{ prefix_name }}_entity import {{ PrefixName }}Entity

logger = structlog.get_logger(__name__)


class {{ PrefixName }}ServiceCore({{ PrefixName }}{{ SuffixName }}):
    """Core business logic implementation for {{ PrefixName }} {{ SuffixName }} operations."""

    def __init__(self, {{ prefix_name }}_repository: {{ PrefixName }}Repository) -> None:
        """Initialize the service with required dependencies.
        
        Args:
            {{ prefix_name }}_repository: Repository for {{ PrefixName }} entity persistence
        """
        self.{{ prefix_name }}_repository = {{ prefix_name }}_repository

    async def create_{{ prefix_name }}(self, {{ prefix_name }}: {{ PrefixName }}Dto) -> Create{{ PrefixName }}Response:
        """Create a new {{ prefix_name }} entity.
        
        Args:
            {{ prefix_name }}: The {{ prefix_name }} data to create
            
        Returns:
            Response containing the created {{ prefix_name }}
            
        Raises:
            ServiceException: If creation fails or constraint violations occur
        """
        logger.info("Creating {{ prefix_name }} entity", name={{ prefix_name }}.name)
        logger.debug("Create{{ PrefixName }} request details", 
                    has_id={{ prefix_name }}.id is not None,
                    name_length=len({{ prefix_name }}.name))

        start_time = logger.bind().info("Starting create operation")
        
        try:
            # Create new entity - let database generate ID if not provided
            entity_data = {
                "name": {{ prefix_name }}.name
            }
            
            saved_entity = await self.{{ prefix_name }}_repository.save(entity_data)
            duration_ms = logger.bind().info("Create operation completed")
            
            logger.info("Successfully created {{ prefix_name }} entity",
                       entity_id=saved_entity.id,
                       name=saved_entity.name,
                       duration_ms=duration_ms)

            # Convert entity to DTO
            {{ prefix_name }}_dto = self._entity_to_dto(saved_entity)
            
            return Create{{ PrefixName }}Response({{ prefix_name }}={{ prefix_name }}_dto)
            
        except Exception as e:
            duration_ms = logger.bind().error("Create operation failed")
            logger.error("Failed to create {{ prefix_name }} entity",
                        name={{ prefix_name }}.name,
                        duration_ms=duration_ms,
                        error=str(e),
                        exc_info=True)

            # Check for common database constraint violations
            error_message = str(e).lower()
            if "constraint" in error_message or "unique" in error_message:
                raise ServiceException.invalid_request(f"Database constraint violation: {str(e)}")
            
            raise ServiceException.internal_error("Failed to create {{ prefix_name }} entity", e)

    async def get_{{ prefix_name }}s(self, request: Get{{ PrefixName }}sRequest) -> Get{{ PrefixName }}sResponse:
        """Get a paginated list of {{ prefix_name }}s.
        
        Args:
            request: Pagination request parameters
            
        Returns:
            Response containing {{ prefix_name }}s and pagination metadata
        """
        # Normalize page size to reasonable bounds
        requested_page_size = request.page_size
        page_size = max(1, min(requested_page_size, 100))
        
        logger.info("Retrieving {{ prefix_name }}s",
                   start_page=request.start_page,
                   requested_page_size=requested_page_size,
                   adjusted_page_size=page_size)

        if page_size != requested_page_size:
            logger.debug("Page size adjusted",
                        requested=requested_page_size,
                        adjusted=page_size)

        start_time = logger.bind().info("Starting get {{ prefix_name }}s operation")
        
        try:
            # Get paginated results from repository
            page_result = await self.{{ prefix_name }}_repository.find_all_paginated(
                page=request.start_page,
                size=page_size
            )
            
            query_duration_ms = logger.bind().info("Database query completed")
            
            # Convert entities to DTOs
            {{ prefix_name }}s = [self._entity_to_dto(entity) for entity in page_result.items]
            
            total_duration_ms = logger.bind().info("Get {{ prefix_name }}s operation completed")
            
            logger.info("Retrieved {{ prefix_name }}s",
                       count=len({{ prefix_name }}s),
                       total_elements=page_result.total_elements,
                       total_pages=page_result.total_pages,
                       query_duration_ms=query_duration_ms,
                       total_duration_ms=total_duration_ms)

            return Get{{ PrefixName }}sResponse(
                {{ prefix_name }}s={{ prefix_name }}s,
                has_next=page_result.has_next,
                has_previous=page_result.has_previous,
                next_page=page_result.next_page,
                previous_page=page_result.previous_page,
                total_pages=page_result.total_pages,
                total_elements=page_result.total_elements
            )
            
        except Exception as e:
            duration_ms = logger.bind().error("Get {{ prefix_name }}s operation failed")
            logger.error("Failed to retrieve {{ prefix_name }}s",
                        start_page=request.start_page,
                        page_size=page_size,
                        duration_ms=duration_ms,
                        error=str(e),
                        exc_info=True)
            
            raise ServiceException.internal_error("Failed to retrieve {{ prefix_name }}s", e)

    async def get_{{ prefix_name }}(self, request: Get{{ PrefixName }}Request) -> Get{{ PrefixName }}Response:
        """Get a single {{ prefix_name }} by ID.
        
        Args:
            request: Request containing the {{ prefix_name }} ID
            
        Returns:
            Response containing the requested {{ prefix_name }}
            
        Raises:
            ServiceException: If {{ prefix_name }} not found or retrieval fails
        """
        entity_id = request.id
        logger.info("Retrieving {{ prefix_name }} entity", entity_id=entity_id)

        # Validate UUID format
        try:
            parsed_id = uuid.UUID(entity_id)
        except ValueError as e:
            logger.warning("Invalid UUID format in get{{ PrefixName }} request",
                          entity_id=entity_id,
                          error=str(e))
            raise ServiceException.invalid_request(f"Invalid UUID format: {entity_id}")

        start_time = logger.bind().info("Starting get {{ prefix_name }} operation")
        
        try:
            entity = await self.{{ prefix_name }}_repository.find_by_id(parsed_id)
            duration_ms = logger.bind().info("Get {{ prefix_name }} operation completed")
            
            if entity:
                logger.info("Successfully retrieved {{ prefix_name }} entity",
                           entity_id=entity.id,
                           name=entity.name,
                           duration_ms=duration_ms)
                
                {{ prefix_name }}_dto = self._entity_to_dto(entity)
                return Get{{ PrefixName }}Response({{ prefix_name }}={{ prefix_name }}_dto)
            
            logger.warning("{{ PrefixName }} entity not found",
                          entity_id=entity_id,
                          duration_ms=duration_ms)
            raise ServiceException.not_found("{{ PrefixName }}", entity_id)
            
        except ServiceException:
            # Re-raise service exceptions as-is
            raise
        except Exception as e:
            duration_ms = logger.bind().error("Get {{ prefix_name }} operation failed")
            logger.error("Failed to retrieve {{ prefix_name }} entity",
                        entity_id=entity_id,
                        duration_ms=duration_ms,
                        error=str(e),
                        exc_info=True)
            
            raise ServiceException.internal_error("Failed to retrieve {{ prefix_name }} entity", e)

    async def update_{{ prefix_name }}(self, {{ prefix_name }}: {{ PrefixName }}Dto) -> Update{{ PrefixName }}Response:
        """Update an existing {{ prefix_name }}.
        
        Args:
            {{ prefix_name }}: The updated {{ prefix_name }} data
            
        Returns:
            Response containing the updated {{ prefix_name }}
            
        Raises:
            ServiceException: If {{ prefix_name }} not found or update fails
        """
        if not {{ prefix_name }}.id:
            logger.warning("Update {{ prefix_name }} request missing required ID field")
            raise ServiceException.invalid_request("Update request must include entity ID")

        entity_id = {{ prefix_name }}.id
        new_name = {{ prefix_name }}.name
        logger.info("Updating {{ prefix_name }} entity", entity_id=entity_id, new_name=new_name)

        # Validate UUID format
        try:
            parsed_id = uuid.UUID(entity_id)
        except ValueError as e:
            logger.warning("Invalid UUID format in update{{ PrefixName }} request",
                          entity_id=entity_id,
                          error=str(e))
            raise ServiceException.invalid_request(f"Invalid UUID format: {entity_id}")

        start_time = logger.bind().info("Starting update {{ prefix_name }} operation")
        
        try:
            # First check if entity exists
            existing_entity = await self.{{ prefix_name }}_repository.find_by_id(parsed_id)
            
            if not existing_entity:
                duration_ms = logger.bind().warning("Update failed - entity not found")
                logger.warning("Failed to update {{ prefix_name }} entity - entity not found",
                              entity_id=entity_id,
                              duration_ms=duration_ms)
                raise ServiceException.not_found("{{ PrefixName }}", entity_id)

            old_name = existing_entity.name
            
            # Update the entity
            update_data = {"name": new_name}
            updated_entity = await self.{{ prefix_name }}_repository.update(parsed_id, update_data)
            
            duration_ms = logger.bind().info("Update {{ prefix_name }} operation completed")
            
            logger.info("Successfully updated {{ prefix_name }} entity",
                       entity_id=entity_id,
                       old_name=old_name,
                       new_name=new_name,
                       duration_ms=duration_ms)

            {{ prefix_name }}_dto = self._entity_to_dto(updated_entity)
            return Update{{ PrefixName }}Response({{ prefix_name }}={{ prefix_name }}_dto)
            
        except ServiceException:
            # Re-raise service exceptions as-is
            raise
        except Exception as e:
            duration_ms = logger.bind().error("Update {{ prefix_name }} operation failed")
            logger.error("Failed to update {{ prefix_name }} entity",
                        entity_id=entity_id,
                        new_name=new_name,
                        duration_ms=duration_ms,
                        error=str(e),
                        exc_info=True)
            
            raise ServiceException.internal_error("Failed to update {{ prefix_name }} entity", e)

    async def delete_{{ prefix_name }}(self, request: Delete{{ PrefixName }}Request) -> Delete{{ PrefixName }}Response:
        """Delete a {{ prefix_name }} by ID.
        
        Args:
            request: Request containing the {{ prefix_name }} ID to delete
            
        Returns:
            Response with confirmation message
            
        Raises:
            ServiceException: If {{ prefix_name }} not found or deletion fails
        """
        entity_id = request.id
        logger.info("Deleting {{ prefix_name }} entity", entity_id=entity_id)

        # Validate UUID format
        try:
            parsed_id = uuid.UUID(entity_id)
        except ValueError as e:
            logger.warning("Invalid UUID format in delete{{ PrefixName }} request",
                          entity_id=entity_id,
                          error=str(e))
            raise ServiceException.invalid_request(f"Invalid UUID format: {entity_id}")

        start_time = logger.bind().info("Starting delete {{ prefix_name }} operation")
        
        try:
            # Check if entity exists before deletion
            exists = await self.{{ prefix_name }}_repository.exists_by_id(parsed_id)
            
            if not exists:
                duration_ms = logger.bind().warning("Delete failed - entity not found")
                logger.warning("Attempted to delete non-existent {{ prefix_name }} entity",
                              entity_id=entity_id,
                              duration_ms=duration_ms)
                raise ServiceException.not_found("{{ PrefixName }}", entity_id)

            # Perform deletion
            await self.{{ prefix_name }}_repository.delete_by_id(parsed_id)
            
            duration_ms = logger.bind().info("Delete {{ prefix_name }} operation completed")
            logger.info("Successfully deleted {{ prefix_name }} entity",
                       entity_id=entity_id,
                       duration_ms=duration_ms)

            return Delete{{ PrefixName }}Response(message="Successfully deleted {{ prefix_name }}")
            
        except ServiceException:
            # Re-raise service exceptions as-is
            raise
        except Exception as e:
            duration_ms = logger.bind().error("Delete {{ prefix_name }} operation failed")
            logger.error("Failed to delete {{ prefix_name }} entity",
                        entity_id=entity_id,
                        duration_ms=duration_ms,
                        error=str(e),
                        exc_info=True)
            
            raise ServiceException.internal_error("Failed to delete {{ prefix_name }} entity", e)

    def _entity_to_dto(self, entity: {{ PrefixName }}Entity) -> {{ PrefixName }}Dto:
        """Convert an entity to a DTO.
        
        Args:
            entity: The entity to convert
            
        Returns:
            The converted DTO
        """
        return {{ PrefixName }}Dto(
            id=str(entity.id),
            name=entity.name
        )