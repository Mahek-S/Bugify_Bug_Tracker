from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_root_route():
    """Test the root endpoint returns welcome message."""
    response = client.get("/")
    
    assert response.status_code == 200
    data = response.json()

    assert data["message"] == "Welcome to Bugify API"
    assert data["version"] == "1.0.0"
    assert data["docs"] == "/docs"


def test_health_route():
    """Test health check endpoint."""
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}
