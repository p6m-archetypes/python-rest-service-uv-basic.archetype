"""REST HTTP client for {{ PrefixName }} {{ SuffixName }}."""

from typing import Optional, Dict, Any
import json

import httpx
import structlog

# Import DTOs from API models
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

logger = structlog.get_logger(__name__)


class {{ PrefixName }}ServiceClientError(Exception):
    """Base exception for {{ PrefixName }} service client errors."""
    
    def __init__(self, message: str, status_code: Optional[int] = None, response_body: Optional[str] = None):
        super().__init__(message)
        self.status_code = status_code
        self.response_body = response_body


class {{ PrefixName }}ServiceClient:
    """Client for connecting to the {{ PrefixName }} {{ SuffixName }} REST API."""

    def __init__(
        self,
        base_url: str = "http://localhost:8000",
        timeout: float = 30.0,
        headers: Optional[Dict[str, str]] = None,
        verify_ssl: bool = True,
        follow_redirects: bool = True
    ) -> None:
        """Initialize the {{ PrefixName }} Service client.
        
        Args:
            base_url: Base URL for the REST API (e.g., "http://localhost:8000")
            timeout: Default timeout for requests in seconds
            headers: Optional default headers to include with requests
            verify_ssl: Whether to verify SSL certificates
            follow_redirects: Whether to follow HTTP redirects
        """
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.default_headers = headers or {}
        
        # Set up default headers
        self.default_headers.setdefault('Content-Type', 'application/json')
        self.default_headers.setdefault('Accept', 'application/json')
        
        # Create httpx client with configuration
        self.client = httpx.AsyncClient(
            timeout=httpx.Timeout(timeout),
            headers=self.default_headers,
            verify=verify_ssl,
            follow_redirects=follow_redirects
        )
        
        logger.info(
            "{{ PrefixName }} Service client initialized",
            base_url=base_url,
            timeout=timeout,
            verify_ssl=verify_ssl
        )

    @classmethod
    def create(cls, base_url: str, timeout: float = 30.0) -> "{{ PrefixName }}ServiceClient":
        """Factory method to create a client instance.
        
        Args:
            base_url: Base URL for the REST API
            timeout: Request timeout in seconds
            
        Returns:
            Configured client instance
        """
        return cls(base_url=base_url, timeout=timeout)

    async def create_{{ prefix_name }}(self, {{ prefix_name }}: {{ PrefixName }}Dto) -> Create{{ PrefixName }}Response:
        """Create a new {{ prefix_name }}.
        
        Args:
            {{ prefix_name }}: {{ PrefixName }} data to create
            
        Returns:
            Response containing the created {{ prefix_name }}
            
        Raises:
            {{ PrefixName }}ServiceClientError: If the API call fails
        """
        logger.info("Creating {{ prefix_name }}", name={{ prefix_name }}.name)
        
        try:
            # Convert DTO to JSON payload
            payload = {{ prefix_name }}.model_dump(exclude_none=True)
            
            # Make REST API call
            response = await self.client.post(
                f"{self.base_url}/api/v1/{{ prefix_name }}s",
                json=payload
            )
            
            # Handle response
            if response.status_code == 201:
                response_data = response.json()
                result = Create{{ PrefixName }}Response(**response_data)
                logger.info("{{ PrefixName }} created successfully", {{ prefix_name }}_id=result.{{ prefix_name }}.id)
                return result
            else:
                await self._handle_error_response(response, "creating {{ prefix_name }}")
                
        except httpx.RequestError as e:
            logger.error("Network error creating {{ prefix_name }}", error=str(e))
            raise {{ PrefixName }}ServiceClientError(f"Network error: {str(e)}")
        except Exception as e:
            logger.error("Unexpected error creating {{ prefix_name }}", error=str(e), exc_info=True)
            raise {{ PrefixName }}ServiceClientError(f"Unexpected error: {str(e)}")

    async def get_{{ prefix_name }}s(self, request: Get{{ PrefixName }}sRequest) -> Get{{ PrefixName }}sResponse:
        """Get a paginated list of {{ prefix_name }}s.
        
        Args:
            request: Pagination request parameters
            
        Returns:
            Response containing {{ prefix_name }}s and pagination metadata
            
        Raises:
            {{ PrefixName }}ServiceClientError: If the API call fails
        """
        logger.info("Getting {{ prefix_name }}s", start_page=request.start_page, page_size=request.page_size)
        
        try:
            # Build query parameters
            params = {
                "page": request.start_page,
                "size": request.page_size
            }
            if request.status:
                params["status"] = request.status
            
            # Make REST API call
            response = await self.client.get(
                f"{self.base_url}/api/v1/{{ prefix_name }}s",
                params=params
            )
            
            # Handle response
            if response.status_code == 200:
                response_data = response.json()
                result = Get{{ PrefixName }}sResponse(**response_data)
                logger.info("{{ PrefixName }}s retrieved successfully", count=len(result.{{ prefix_name }}s))
                return result
            else:
                await self._handle_error_response(response, "getting {{ prefix_name }}s")
                
        except httpx.RequestError as e:
            logger.error("Network error getting {{ prefix_name }}s", error=str(e))
            raise {{ PrefixName }}ServiceClientError(f"Network error: {str(e)}")
        except Exception as e:
            logger.error("Unexpected error getting {{ prefix_name }}s", error=str(e), exc_info=True)
            raise {{ PrefixName }}ServiceClientError(f"Unexpected error: {str(e)}")

    async def get_{{ prefix_name }}(self, request: Get{{ PrefixName }}Request) -> Get{{ PrefixName }}Response:
        """Get a single {{ prefix_name }} by ID.
        
        Args:
            request: Request containing the {{ prefix_name }} ID
            
        Returns:
            Response containing the requested {{ prefix_name }}
            
        Raises:
            {{ PrefixName }}ServiceClientError: If the API call fails
        """
        logger.info("Getting {{ prefix_name }}", {{ prefix_name }}_id=request.id)
        
        try:
            # Make REST API call
            response = await self.client.get(
                f"{self.base_url}/api/v1/{{ prefix_name }}s/{request.id}"
            )
            
            # Handle response
            if response.status_code == 200:
                response_data = response.json()
                result = Get{{ PrefixName }}Response(**response_data)
                logger.info("{{ PrefixName }} retrieved successfully", {{ prefix_name }}_id=result.{{ prefix_name }}.id)
                return result
            else:
                await self._handle_error_response(response, f"getting {{ prefix_name }} {request.id}")
                
        except httpx.RequestError as e:
            logger.error("Network error getting {{ prefix_name }}", error=str(e), {{ prefix_name }}_id=request.id)
            raise {{ PrefixName }}ServiceClientError(f"Network error: {str(e)}")
        except Exception as e:
            logger.error("Unexpected error getting {{ prefix_name }}", error=str(e), {{ prefix_name }}_id=request.id, exc_info=True)
            raise {{ PrefixName }}ServiceClientError(f"Unexpected error: {str(e)}")

    async def update_{{ prefix_name }}(self, {{ prefix_name }}: {{ PrefixName }}Dto) -> Update{{ PrefixName }}Response:
        """Update an existing {{ prefix_name }}.
        
        Args:
            {{ prefix_name }}: Updated {{ prefix_name }} data
            
        Returns:
            Response containing the updated {{ prefix_name }}
            
        Raises:
            {{ PrefixName }}ServiceClientError: If the API call fails
        """
        if not {{ prefix_name }}.id:
            raise {{ PrefixName }}ServiceClientError("{{ PrefixName }} ID is required for update operations")
            
        logger.info("Updating {{ prefix_name }}", {{ prefix_name }}_id={{ prefix_name }}.id)
        
        try:
            # Convert DTO to JSON payload (exclude ID from body, it's in the URL)
            payload = {{ prefix_name }}.model_dump(exclude_none=True, exclude={'id'})
            
            # Make REST API call
            response = await self.client.put(
                f"{self.base_url}/api/v1/{{ prefix_name }}s/{{{ prefix_name }}.id}",
                json=payload
            )
            
            # Handle response
            if response.status_code == 200:
                response_data = response.json()
                result = Update{{ PrefixName }}Response(**response_data)
                logger.info("{{ PrefixName }} updated successfully", {{ prefix_name }}_id=result.{{ prefix_name }}.id)
                return result
            else:
                await self._handle_error_response(response, f"updating {{ prefix_name }} {{{ prefix_name }}.id}")
                
        except httpx.RequestError as e:
            logger.error("Network error updating {{ prefix_name }}", error=str(e), {{ prefix_name }}_id={{ prefix_name }}.id)
            raise {{ PrefixName }}ServiceClientError(f"Network error: {str(e)}")
        except Exception as e:
            logger.error("Unexpected error updating {{ prefix_name }}", error=str(e), {{ prefix_name }}_id={{ prefix_name }}.id, exc_info=True)
            raise {{ PrefixName }}ServiceClientError(f"Unexpected error: {str(e)}")

    async def delete_{{ prefix_name }}(self, request: Delete{{ PrefixName }}Request) -> Delete{{ PrefixName }}Response:
        """Delete a {{ prefix_name }} by ID.
        
        Args:
            request: Request containing the {{ prefix_name }} ID to delete
            
        Returns:
            Response with confirmation message
            
        Raises:
            {{ PrefixName }}ServiceClientError: If the API call fails
        """
        logger.info("Deleting {{ prefix_name }}", {{ prefix_name }}_id=request.id)
        
        try:
            # Make REST API call
            response = await self.client.delete(
                f"{self.base_url}/api/v1/{{ prefix_name }}s/{request.id}"
            )
            
            # Handle response
            if response.status_code == 200:
                response_data = response.json()
                result = Delete{{ PrefixName }}Response(**response_data)
                logger.info("{{ PrefixName }} deleted successfully", message=result.message)
                return result
            else:
                await self._handle_error_response(response, f"deleting {{ prefix_name }} {request.id}")
                
        except httpx.RequestError as e:
            logger.error("Network error deleting {{ prefix_name }}", error=str(e), {{ prefix_name }}_id=request.id)
            raise {{ PrefixName }}ServiceClientError(f"Network error: {str(e)}")
        except Exception as e:
            logger.error("Unexpected error deleting {{ prefix_name }}", error=str(e), {{ prefix_name }}_id=request.id, exc_info=True)
            raise {{ PrefixName }}ServiceClientError(f"Unexpected error: {str(e)}")

    async def close(self) -> None:
        """Close the HTTP client."""
        if self.client:
            await self.client.aclose()
            logger.info("HTTP client closed")

    async def __aenter__(self) -> "{{ PrefixName }}ServiceClient":
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Async context manager exit."""
        await self.close()

    # Synchronous context manager support for backward compatibility
    def __enter__(self) -> "{{ PrefixName }}ServiceClient":
        """Synchronous context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Synchronous context manager exit."""
        # Note: This is not ideal for async clients, but provided for compatibility
        # Users should prefer the async context manager
        import asyncio
        try:
            asyncio.get_running_loop()
            logger.warning("Using synchronous context manager in async context. Consider using async context manager.")
        except RuntimeError:
            # No event loop running, we can create one
            asyncio.run(self.close())

    async def _handle_error_response(self, response: httpx.Response, operation: str) -> None:
        """Handle error responses from the API.
        
        Args:
            response: The HTTP response object
            operation: Description of the operation that failed
            
        Raises:
            {{ PrefixName }}ServiceClientError: Always raises with appropriate error message
        """
        try:
            error_data = response.json()
            error_message = error_data.get('error', {}).get('message', f'HTTP {response.status_code}')
        except (json.JSONDecodeError, KeyError):
            error_message = f"HTTP {response.status_code}: {response.text}"
        
        logger.error(
            f"API error {operation}",
            status_code=response.status_code,
            error_message=error_message,
            response_body=response.text
        )
        
        raise {{ PrefixName }}ServiceClientError(
            f"API error {operation}: {error_message}",
            status_code=response.status_code,
            response_body=response.text
        )

    def set_auth_token(self, token: str) -> None:
        """Set authentication token for future requests.
        
        Args:
            token: JWT or API token to use for authentication
        """
        self.client.headers["Authorization"] = f"Bearer {token}"
        logger.info("Authentication token set")

    def remove_auth_token(self) -> None:
        """Remove authentication token from future requests."""
        self.client.headers.pop("Authorization", None)
        logger.info("Authentication token removed")

    def set_header(self, name: str, value: str) -> None:
        """Set a custom header for future requests.
        
        Args:
            name: Header name
            value: Header value
        """
        self.client.headers[name] = value
        logger.debug("Custom header set", header_name=name)

    def remove_header(self, name: str) -> None:
        """Remove a custom header from future requests.
        
        Args:
            name: Header name to remove
        """
        self.client.headers.pop(name, None)
        logger.debug("Custom header removed", header_name=name)