from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_fixtures_and_prediction():
    fixtures = client.get("/api/v1/fixtures")
    assert fixtures.status_code == 200
    fixture_id = fixtures.json()["fixtures"][0]["id"]
    prediction = client.get(f"/api/v1/predictions/{fixture_id}")
    assert prediction.status_code == 200
    assert prediction.json()["data_source"] == "demo-static-v1"


def test_unknown_fixture_returns_404():
    assert client.get("/api/v1/predictions/missing").status_code == 404
