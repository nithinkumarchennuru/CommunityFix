from app import create_app


def test_health_route():
    app = create_app({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
    })
    client = app.test_client()

    response = client.get("/api/health")

    assert response.status_code == 200
    assert response.get_json()["success"] is True
    assert response.get_json()["message"] == "CommunityFix backend is running"
