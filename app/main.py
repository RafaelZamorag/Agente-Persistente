"""Punto de entrada HTTP del agente."""
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse

from app.providers.demo import DemoSportsDataProvider
from app.services.prediction_service import PredictionService
from app.services.predictor import PredictionEngine

BASE_DIR = Path(__file__).resolve().parent.parent
provider = DemoSportsDataProvider()
service = PredictionService(provider, PredictionEngine())
app = FastAPI(
    title="Agente Persistente — Predicción deportiva",
    version="0.1.0",
    description=(
        "MVP académico para probabilidades explicables. No ejecuta apuestas y "
        "no garantiza resultados."
    ),
)


@app.get("/", include_in_schema=False)
def dashboard():
    return FileResponse(BASE_DIR / "frontend" / "index.html")


@app.get("/health")
def health():
    return {"status": "ok", "service": "agente-persistente", "model_version": "baseline-v0.1"}


@app.get("/api/v1/fixtures")
def list_fixtures():
    return {"source": provider.name, "fixtures": service.list_fixtures()}


@app.get("/api/v1/predictions/{fixture_id}")
def predict(fixture_id: str):
    prediction = service.predict(fixture_id)
    if prediction is None:
        raise HTTPException(status_code=404, detail="Fixture no encontrado")
    return prediction
