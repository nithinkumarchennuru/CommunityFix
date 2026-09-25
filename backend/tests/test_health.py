import pytest
from app import create_app


@pytest.fixture
def client():
    app = create_app("testing")
    with app.test_client() as test_client:
        yield test_client


def test_root_endpoint(client):
    """Test root endpoint returns API information."""
    response = client.get("/")
    assert response.status_code == 200
    json_data = response.get_json()
    assert json_data["project"] == "CommunityFix"
    assert "health_endpoint" in json_data["documentation"]


def test_ping_endpoint(client):
    """Test ping endpoint returns pong and ok status."""
    response = client.get("/api/ping")
    assert response.status_code == 200
    json_data = response.get_json()
    assert json_data["status"] == "ok"
    assert json_data["message"] == "pong"


def test_health_endpoint_structure(client):
    """Test health endpoint returns structured service and DB status."""
    response = client.get("/api/health")
    assert response.status_code == 200
    json_data = response.get_json()
    assert "status" in json_data
    assert "service" in json_data
    assert "database" in json_data
    assert "connected" in json_data["database"]
