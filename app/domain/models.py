"""Entidades y contratos de dominio del agente."""
from datetime import UTC, datetime
from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field


class Outcome(StrEnum):
    HOME = "home"
    DRAW = "draw"
    AWAY = "away"


class TeamProfile(BaseModel):
    name: str
    strength: float = Field(ge=0, le=100)
    recent_form: float = Field(ge=0, le=1, description="Rendimiento reciente normalizado")


class Odds(BaseModel):
    home: float = Field(gt=1)
    draw: float = Field(gt=1)
    away: float = Field(gt=1)


class Fixture(BaseModel):
    model_config = ConfigDict(frozen=True)

    id: str
    league: str
    starts_at: datetime
    home: TeamProfile
    away: TeamProfile
    odds: Odds
    status: str = "scheduled"


class Prediction(BaseModel):
    fixture_id: str
    model_version: str
    generated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    data_source: str
    probabilities: dict[Outcome, float]
    implied_probabilities: dict[Outcome, float]
    edge: dict[Outcome, float]
    expected_value: dict[Outcome, float]
    recommendation: str
    confidence: str
    explanation: list[str]
    missing_data: list[str] = Field(default_factory=list)
    responsible_use: str = (
        "Salida educativa y probabilística; no garantiza resultados ni sustituye "
        "una decisión humana."
    )
