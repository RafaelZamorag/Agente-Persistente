"""Puerto de entrada del caso de uso de predicción."""
from typing import Protocol

from app.domain.models import Prediction


class PredictFixtureUseCase(Protocol):
    def execute(self, fixture_id: str) -> Prediction | None:
        """Calcula una predicción o devuelve None si no existe el fixture."""
