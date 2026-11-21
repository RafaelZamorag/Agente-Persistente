"""Casos de uso de predicción."""
from app.domain.models import Prediction
from app.providers.base import SportsDataProvider
from app.services.predictor import PredictionEngine


class PredictionService:
    def __init__(self, provider: SportsDataProvider, engine: PredictionEngine) -> None:
        self.provider = provider
        self.engine = engine

    def list_fixtures(self):
        return self.provider.list_fixtures()

    def predict(self, fixture_id: str) -> Prediction | None:
        fixture = self.provider.get_fixture(fixture_id)
        return None if fixture is None else self.engine.predict(fixture, self.provider.name)
