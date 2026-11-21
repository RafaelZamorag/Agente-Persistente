"""Caso de uso de predicción de un fixture."""
from app.application.ports.outbound.sports_data import SportsDataPort
from app.domain.models import Prediction
from app.domain.prediction_engine import PredictionEngine


class PredictFixture:
    def __init__(self, sports_data: SportsDataPort, engine: PredictionEngine) -> None:
        self._sports_data = sports_data
        self._engine = engine

    def execute(self, fixture_id: str) -> Prediction | None:
        fixture = self._sports_data.get_fixture(fixture_id)
        if fixture is None:
            return None
        return self._engine.predict(fixture, self._sports_data.name)
