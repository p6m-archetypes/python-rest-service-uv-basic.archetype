"""REST API connectivity and health check tests for CI/CD integration."""

import asyncio
import os

import httpx
import pytest


class TestRestConnectivity:
    """Test REST API server connectivity and health checks."""

    @pytest.mark.asyncio
    async def test_rest_server_accessible(self):
        """Test that REST API server is accessible."""
        host = os.getenv("API_SERVER_HOST", "localhost")
        port = int(os.getenv("API_SERVER_PORT", "8000"))
        
        timeout = httpx.Timeout(connect=5.0, read=10.0)
        
        async with httpx.AsyncClient(timeout=timeout) as client:
            try:
                response = await client.get(f"http://{host}:{port}/")
                assert response.status_code == 200
                data = response.json()
                assert "service" in data
                assert "version" in data
            except httpx.ConnectError:
                pytest.fail(f"Cannot connect to REST API server at {host}:{port}")
            except httpx.TimeoutException:
                pytest.fail(f"Timeout connecting to REST API server at {host}:{port}")

    @pytest.mark.asyncio
    async def test_health_endpoints(self):
        """Test health check endpoints."""
        host = os.getenv("MANAGEMENT_SERVER_HOST", "localhost") 
        port = int(os.getenv("MANAGEMENT_SERVER_PORT", "8080"))
        
        health_endpoints = ["/health", "/health/live", "/health/ready"]
        
        async with httpx.AsyncClient() as client:
            for endpoint in health_endpoints:
                try:
                    response = await client.get(f"http://{host}:{port}{endpoint}")
                    assert response.status_code == 200
                    data = response.json()
                    assert "status" in data
                except httpx.ConnectError:
                    pytest.fail(f"Cannot connect to health endpoint {endpoint} at {host}:{port}")

    @pytest.mark.asyncio
    async def test_api_endpoints(self):
        """Test main API endpoints."""
        host = os.getenv("API_SERVER_HOST", "localhost")
        port = int(os.getenv("API_SERVER_PORT", "8000"))
        
        async with httpx.AsyncClient() as client:
            # Test list endpoint
            try:
                response = await client.get(f"http://{host}:{port}/api/v1/{{ prefix_name }}s")
                # Should return 501 (not implemented) or 200 (if implemented)
                assert response.status_code in [200, 501]
            except httpx.ConnectError:
                pytest.fail(f"Cannot connect to API endpoint at {host}:{port}")

    @pytest.mark.asyncio 
    async def test_openapi_docs(self):
        """Test that OpenAPI documentation is available."""
        host = os.getenv("API_SERVER_HOST", "localhost")
        port = int(os.getenv("API_SERVER_PORT", "8000"))
        
        async with httpx.AsyncClient() as client:
            try:
                # Test OpenAPI JSON endpoint
                response = await client.get(f"http://{host}:{port}/openapi.json")
                assert response.status_code == 200
                data = response.json()
                assert "openapi" in data
                assert "info" in data
                
                # Test docs endpoint (if not disabled)
                docs_response = await client.get(f"http://{host}:{port}/docs")
                # Should be 200 (available) or 404 (disabled in production)
                assert docs_response.status_code in [200, 404]
                
            except httpx.ConnectError:
                pytest.fail(f"Cannot connect to OpenAPI endpoints at {host}:{port}")

    @pytest.mark.asyncio
    async def test_cors_headers(self):
        """Test CORS headers are present."""
        host = os.getenv("API_SERVER_HOST", "localhost")
        port = int(os.getenv("API_SERVER_PORT", "8000"))
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.options(f"http://{host}:{port}/")
                # CORS headers should be present
                assert "access-control-allow-origin" in response.headers
            except httpx.ConnectError:
                pytest.fail(f"Cannot test CORS at {host}:{port}")


if __name__ == "__main__":
    # Allow running tests directly for debugging
    asyncio.run(pytest.main([__file__, "-v"])) 