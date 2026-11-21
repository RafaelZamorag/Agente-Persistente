"""Adaptador de entrada HTTP para FastAPI."""
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse

from app.application.ports.inbound.list_fixtures import ListFixturesUseCase
from app.application.ports.inbound.predict_fixture import PredictFixtureUseCase

BASE_DIR = Path(__file__).resolve().parents[3]


def create_http_app(
    list_fixtures: ListFixturesUseCase,
    predict_fixture: PredictFixtureUseCase,
    model_version: str,
    data_source: str,
) -> FastAPI:
    """Construye el adaptador HTTP con casos de uso inyectados."""
    app = FastAPI(
        title="Agente Persistente — Predicción deportiva",
        version="0.2.0",
        description=(
            "MVP académico con arquitectura hexagonal. No ejecuta apuestas y "
            "no garantiza resultados."
        ),
    )

    @app.get("/", include_in_schema=False)
    def dashboard():
        return FileResponse(BASE_DIR / "frontend" / "index.html")

    @app.get("/health")
    def health():
        return {
            "status": "ok",
            "service": "agente-persistente",
            "model_version": model_version,
            "data_source": data_source,
        }

    @app.get("/api/v1/fixtures")
    def fixtures():
        return {"source": data_source, "fixtures": list_fixtures.execute()}

    @app.get("/api/v1/predictions/{fixture_id}")
    def prediction(fixture_id: str):
        result = predict_fixture.execute(fixture_id)
        if result is None:
            raise HTTPException(status_code=404, detail="Fixture no encontrado")
        return result

    return app
