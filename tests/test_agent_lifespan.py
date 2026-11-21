"""Regresión: el temporizador debe engancharse al ciclo de vida del servidor.

Este prueba existe porque la primera versión de la consola mostraba
`running: false` y `total_runs: 0`: el lifespan estaba definido pero nunca
se conectaba a la aplicación FastAPI, así que el agente jamás se autodisparaba.
"""
import time

import pytest
from fastapi.testclient import TestClient

from app.adapters.inbound.http import create_http_app
from app.bootstrap import build_container
from app.settings import Settings


@pytest.mark.adapter
def test_server_lifecycle_starts_scheduler_and_records_startup_run(tmp_path):
    settings = Settings(
        agent_enabled=True,
        agent_startup_run=True,
        agent_interval_seconds=3600,
        runs_file=tmp_path / "lifecycle.jsonl",
    )
    container = build_container(settings=settings, project_root=tmp_path)

    assert container.list_agent_runs.execute(limit=5) == []

    client = TestClient(create_http_app(container))
    with client:
        # El ciclo de arranque corre en el bucle del portal: se observa vía API
        # con un reintento corto para no depender de una condición de carrera.
        runs = []
        deadline = time.monotonic() + 3
        while time.monotonic() < deadline and not runs:
            runs = client.get("/api/v1/agent/runs?limit=5").json()["runs"]
            if not runs:
                time.sleep(0.05)

    assert len(runs) == 1
    assert runs[0]["trigger"] == "startup"
    assert runs[0]["fixtures_analyzed"] == 2


@pytest.mark.adapter
def test_disabled_agent_does_not_run_on_startup(tmp_path):
    settings = Settings(
        agent_enabled=False,
        agent_startup_run=True,
        runs_file=tmp_path / "disabled.jsonl",
    )
    container = build_container(settings=settings, project_root=tmp_path)

    with TestClient(create_http_app(container)):
        assert container.list_agent_runs.execute(limit=5) == []
