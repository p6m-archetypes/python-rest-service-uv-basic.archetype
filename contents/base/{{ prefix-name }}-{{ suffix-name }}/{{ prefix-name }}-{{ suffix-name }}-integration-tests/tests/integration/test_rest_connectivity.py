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
                # Should return 200 (implemented) or error status
                assert response.status_code in [200, 400, 500, 501]
            except httpx.ConnectError:
                pytest.fail(f"Cannot connect to API endpoint at {host}:{port}")

    @pytest.mark.asyncio
    async def test_crud_endpoints_structure(self):
        """Test that CRUD endpoints are accessible and return proper response structure."""
        host = os.getenv("API_SERVER_HOST", "localhost")
        port = int(os.getenv("API_SERVER_PORT", "8000"))
        base_url = f"http://{host}:{port}/api/v1/{{ prefix_name }}s"
        
        async with httpx.AsyncClient() as client:
            try:
                # Test LIST endpoint structure
                list_response = await client.get(base_url)
                if list_response.status_code == 200:
                    data = list_response.json()
                    # Should have pagination structure if implemented
                    assert isinstance(data, dict)
                
                # Test CREATE endpoint (expect validation error with empty data)
                create_response = await client.post(base_url, json={})
                # Should return 400 (validation error) or 500/501 if not implemented
                assert create_response.status_code in [400, 422, 500, 501]
                
                # Test GET by ID endpoint (with dummy ID)
                get_response = await client.get(f"{base_url}/test-id")
                # Should return 400 (invalid ID), 404 (not found), or 500/501 if not implemented
                assert get_response.status_code in [400, 404, 500, 501]
                
                # Test UPDATE endpoint (with dummy ID)
                update_response = await client.put(f"{base_url}/test-id", json={})
                # Should return 400/404/422 or 500/501 if not implemented
                assert update_response.status_code in [400, 404, 422, 500, 501]
                
                # Test DELETE endpoint (with dummy ID)
                delete_response = await client.delete(f"{base_url}/test-id")
                # Should return 400/404 or 500/501 if not implemented
                assert delete_response.status_code in [400, 404, 500, 501]
                
            except httpx.ConnectError:
                pytest.fail(f"Cannot connect to CRUD endpoints at {host}:{port}")

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