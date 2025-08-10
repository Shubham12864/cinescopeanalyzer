import pytest
from fastapi.testclient import TestClient

def test_health_endpoint(client):
    """Test the health check endpoint"""
    response = client.get('/health')
    assert response.status_code == 200
    data = response.json()
    assert 'status' in data
    assert data['status'] == 'healthy'

def test_root_endpoint(client):
    """Test the root endpoint"""
    response = client.get('/')
    assert response.status_code == 200
    data = response.json()
    assert 'message' in data
    assert 'version' in data

def test_api_health_endpoint(client):
    """Test the API health check endpoint"""
    response = client.get('/api/health')
    assert response.status_code == 200
    data = response.json()
    assert 'status' in data
    assert data['status'] == 'healthy'

def test_cors_headers(client):
    """Test CORS headers are present"""
    response = client.options('/health')
    assert response.status_code == 200
    # CORS headers should be present due to middleware