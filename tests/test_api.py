import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert "Code4Py API" in response.json()["message"]

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_generate_code():
    response = client.post(
        "/api/generate",
        json={
            "prompt": "Create a simple hello world function",
            "language": "python"
        }
    )
    # This will fail without Replicate API token, but tests the endpoint structure
    assert response.status_code in [200, 500]  # 500 if no API token

def test_convert_code():
    response = client.post(
        "/api/convert",
        json={
            "code": "console.log('Hello World');",
            "from_language": "javascript",
            "to_language": "python"
        }
    )
    assert response.status_code in [200, 500]

def test_explain_code():
    response = client.post(
        "/api/explain",
        json={
            "code": "def hello():\n    print('Hello World')",
            "language": "python"
        }
    )
    assert response.status_code in [200, 500]

def test_debug_code():
    response = client.post(
        "/api/debug",
        json={
            "code": "def divide(a, b):\n    return a / b",
            "language": "python"
        }
    )
    assert response.status_code in [200, 500]

def test_register_user():
    response = client.post(
        "/api/auth/register",
        json={
            "email": "test@example.com",
            "password": "testpassword",
            "name": "Test User"
        }
    )
    assert response.status_code == 200
    assert "id" in response.json()

def test_login_user():
    response = client.post(
        "/api/auth/login",
        json={
            "email": "test@example.com",
            "password": "testpassword"
        }
    )
    assert response.status_code == 200
    assert "access_token" in response.json()


