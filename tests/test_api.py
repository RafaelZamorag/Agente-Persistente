from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "ok"
    assert payload["data_source"] == "demo-static-v1"


def test_console_is_served():
    response = client.get("/")
    assert response.status_code == 200
    assert "Consola del agente" in response.text


def test_console_assets_are_served():
    assert client.get("/assets/app.js").status_code == 200
    assert client.get("/assets/styles.css").status_code == 200


def test_fixtures_and_prediction():
    fixtures = client.get("/api/v1/fixtures")
    assert fixtures.status_code == 200
    fixture_id = fixtures.json()["fixtures"][0]["id"]
    prediction = client.get(f"/api/v1/predictions/{fixture_id}")
    assert prediction.status_code == 200
    assert prediction.json()["data_source"] == "demo-static-v1"


def test_unknown_fixture_returns_404():
    assert client.get("/api/v1/predictions/missing").status_code == 404


def test_agent_status_reports_runtime_state():
    response = client.get("/api/v1/agent/status")
    assert response.status_code == 200
    payload = response.json()
    assert payload["enabled"] is False
    assert payload["interval_seconds"] == 60
    assert payload["model_version"] == "baseline-v0.2"


def test_manual_agent_run_is_persisted_and_listed():
    created = client.post("/api/v1/agent/runs", json={"trigger": "manual"})
    assert created.status_code == 201
    run_id = created.json()["id"]
    assert created.json()["fixtures_analyzed"] == 2

    listed = client.get("/api/v1/agent/runs?limit=5")
    assert listed.status_code == 200
    assert run_id in [run["id"] for run in listed.json()["runs"]]

    status = client.get("/api/v1/agent/status").json()
    assert status["total_runs"] >= 1


def test_invalid_trigger_is_rejected():
    assert client.post("/api/v1/agent/runs", json={"trigger": "apostar"}).status_code == 422
