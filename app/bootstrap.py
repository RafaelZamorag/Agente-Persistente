"""Composition root: único punto donde se ensamblan dependencias concretas."""
from dataclasses import dataclass

from app.adapters.outbound.demo_sports_data import DemoSportsDataAdapter
from app.application.use_cases.list_fixtures import ListFixtures
from app.application.use_cases.predict_fixture import PredictFixture
from app.domain.prediction_engine import PredictionEngine


@dataclass(frozen=True)
class ApplicationContainer:
    list_fixtures: ListFixtures
    predict_fixture: PredictFixture
    model_version: str
    data_source: str


def build_container() -> ApplicationContainer:
    sports_data = DemoSportsDataAdapter()
    engine = PredictionEngine()
    return ApplicationContainer(
        list_fixtures=ListFixtures(sports_data),
        predict_fixture=PredictFixture(sports_data, engine),
        model_version=engine.model_version,
        data_source=sports_data.name,
    )
