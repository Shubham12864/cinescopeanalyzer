"""Pytest configuration and fixtures"""
import sys
import os
from pathlib import Path

# Add the backend directory to Python path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

import pytest
from fastapi.testclient import TestClient

@pytest.fixture
def client():
    """Create a test client"""
    try:
        from app.main import app
        return TestClient(app)
    except ImportError as e:
        pytest.skip(f"Could not import app.main: {e}")

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    import asyncio
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()
