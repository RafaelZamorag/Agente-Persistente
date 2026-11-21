"""Entidades de dominio del runtime del agente."""
from datetime import UTC, datetime
from enum import StrEnum
from uuid import uuid4

from pydantic import BaseModel, Field


class RunStatus(StrEnum):
    SUCCESS = "success"
    FAILED = "failed"


class RunTrigger(StrEnum):
    SCHEDULE = "schedule"
    MANUAL = "manual"
    STARTUP = "startup"


def _new_id() -> str:
    return uuid4().hex[:12]


class RunSignal(BaseModel):
    """Resumen auditable de una predicción producida en un ciclo."""

    fixture_id: str
    home: str
    away: str
    likely_outcome: str
    likely_probability: float
    best_outcome: str
    confidence: str
    recommendation: str
    best_expected_value: float


class AgentRun(BaseModel):
    """Registro de una ejecución del agente."""

    id: str = Field(default_factory=_new_id)
    trigger: RunTrigger
    status: RunStatus
    started_at: datetime
    finished_at: datetime
    duration_ms: float = Field(ge=0, description="Milisegundos con resolución de perf_counter")
    model_version: str
    data_source: str
    fixtures_analyzed: int
    signals: list[RunSignal] = Field(default_factory=list)
    error: str | None = None

    @property
    def is_success(self) -> bool:
        return self.status is RunStatus.SUCCESS


class AgentSchedulerState(BaseModel):
    """Estado observable del planificador persistente."""

    enabled: bool
    interval_seconds: int
    running: bool
    next_run_at: datetime | None
    total_runs: int
    last_run_id: str | None
    generated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
