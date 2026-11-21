"""Composition root: único lugar donde se ensamblan implementaciones concretas."""
from collections.abc import Awaitable, Callable
from contextlib import asynccontextmanager
from dataclasses import dataclass
from pathlib import Path

from app.adapters.inbound.timer_scheduler import AgentTimerScheduler
from app.adapters.outbound.demo_sports_data import DemoSportsDataAdapter
from app.adapters.outbound.filesystem_run_repository import FilesystemRunRepository
from app.application.use_cases.get_agent_status import GetAgentStatus
from app.application.use_cases.list_agent_runs import ListAgentRuns
from app.application.use_cases.list_fixtures import ListFixtures
from app.application.use_cases.predict_fixture import PredictFixture
from app.application.use_cases.run_analysis_cycle import RunAnalysisCycle
from app.domain.prediction_engine import PredictionEngine
from app.settings import Settings, get_settings


@dataclass(frozen=True)
class ApplicationContainer:
    """Dependencias ready-to-use para el adaptador HTTP y el runtime."""

    list_fixtures: ListFixtures
    predict_fixture: PredictFixture
    run_cycle: RunAnalysisCycle
    list_agent_runs: ListAgentRuns
    get_agent_status: GetAgentStatus
    scheduler: AgentTimerScheduler
    model_version: str
    data_source: str
    runs_repository: str
    settings: Settings
    lifespan_hooks: Callable[..., Callable[[], Awaitable[None]]]


def build_container(settings: Settings | None = None, project_root: Path | None = None):
    """Construye el grafo de dependencias.

    `project_root` permite redirigir el registro de ejecuciones en pruebas.
    """
    settings = settings or get_settings()
    root = Path(project_root) if project_root else Path.cwd()
    runs_path = settings.runs_file
    if not runs_path.is_absolute():
        runs_path = root / runs_path

    sports_data = DemoSportsDataAdapter()
    engine = PredictionEngine()
    repository = FilesystemRunRepository(runs_path)

    predict_fixture = PredictFixture(sports_data, engine)
    run_cycle = RunAnalysisCycle(sports_data, predict_fixture, repository, engine.model_version)
    scheduler = AgentTimerScheduler(
        run_cycle=run_cycle,
        interval_seconds=settings.agent_interval_seconds,
        enabled=settings.agent_enabled,
        run_on_startup=settings.agent_startup_run,
    )

    return ApplicationContainer(
        list_fixtures=ListFixtures(sports_data),
        predict_fixture=predict_fixture,
        run_cycle=run_cycle,
        list_agent_runs=ListAgentRuns(repository),
        get_agent_status=GetAgentStatus(scheduler, repository),
        scheduler=scheduler,
        model_version=engine.model_version,
        data_source=sports_data.name,
        runs_repository=str(runs_path),
        settings=settings,
        lifespan_hooks=_build_lifespan(scheduler),
    )


def _build_lifespan(scheduler: AgentTimerScheduler):
    """Empaqueta el arranque/paro del temporizador para el adaptador HTTP."""

    @asynccontextmanager
    async def lifespan(_application):
        await scheduler.start()
        try:
            yield
        finally:
            await scheduler.stop()

    return lifespan
