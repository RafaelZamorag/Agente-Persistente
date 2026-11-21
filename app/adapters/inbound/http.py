"""Adaptador de entrada HTTP para FastAPI."""
from collections.abc import Awaitable, Callable
from pathlib import Path

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from app.bootstrap import ApplicationContainer
from app.domain.agent import RunTrigger


class TriggerRunRequest(BaseModel):
    trigger: RunTrigger = Field(default=RunTrigger.MANUAL)


def resolve_frontend_dir() -> Path:
    """Localiza `frontend/` tanto en checkout Git como en instalación empaquetada."""
    here = Path(__file__).resolve()
    candidates = [here.parents[3] / "frontend", here.parents[2] / "frontend"]
    for candidate in candidates:
        if (candidate / "index.html").is_file():
            return candidate
    return candidates[0]


FRONTEND_DIR = resolve_frontend_dir()


LifespanFactory = Callable[..., Callable[[], Awaitable[None]]]


def create_http_app(container: ApplicationContainer) -> FastAPI:
    """Expone los casos de uso como API REST y sirve la consola del agente."""
    app = FastAPI(
        title="Agente Persistente — Predicción deportiva",
        version="0.3.1",
        description=(
            "Agente académico con arquitectura hexagonal. Analiza fixtures de forma "
            "periódica y deja un registro auditable. No ejecuta apuestas."
        ),
        lifespan=container.lifespan_hooks,
    )

    @app.get("/", include_in_schema=False)
    def console():
        index = FRONTEND_DIR / "index.html"
        if not index.is_file():
            raise HTTPException(
                status_code=500,
                detail=(
                    f"No se encontró la consola del agente en {index}. "
                    "Ejecuta uvicorn desde la raíz del repositorio."
                ),
            )
        return FileResponse(index)

    @app.get("/health")
    def health():
        return {
            "status": "ok",
            "service": "agente-persistente",
            "model_version": container.model_version,
            "data_source": container.data_source,
        }

    @app.get("/api/v1/fixtures")
    def fixtures():
        return {"source": container.data_source, "fixtures": container.list_fixtures.execute()}

    @app.get("/api/v1/predictions/{fixture_id}")
    def prediction(fixture_id: str):
        result = container.predict_fixture.execute(fixture_id)
        if result is None:
            raise HTTPException(status_code=404, detail="Fixture no encontrado")
        return result

    @app.get("/api/v1/agent/status")
    def agent_status():
        # El adaptador añade metadatos de versión: el dominio no conoce HTTP.
        state = container.get_agent_status.execute().model_dump(mode="json")
        return state | {
            "model_version": container.model_version,
            "data_source": container.data_source,
            "runs_repository": container.runs_repository,
        }

    @app.get("/api/v1/agent/runs")
    def agent_runs(limit: int = Query(default=20, ge=1, le=200)):
        return {
            "repository": container.runs_repository,
            "count": limit,
            "runs": container.list_agent_runs.execute(limit=limit),
        }

    @app.post("/api/v1/agent/runs", status_code=201)
    def trigger_agent_run(payload: TriggerRunRequest):
        # Se delega al runtime para que el ciclo manual y el programado compartan
        # contadores y la cuenta regresiva observable.
        return container.scheduler.run_now(payload.trigger)

    app.mount("/assets", StaticFiles(directory=FRONTEND_DIR), name="assets")
    return app
