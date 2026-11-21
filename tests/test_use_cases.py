from datetime import UTC, datetime

from app.application.use_cases.list_fixtures import ListFixtures
from app.application.use_cases.predict_fixture import PredictFixture
from app.domain.models import Fixture, Odds, TeamProfile
from app.domain.prediction_engine import PredictionEngine


class FakeSportsData:
    name = "fake-test-provider"

    def __init__(self, fixture: Fixture):
        self.fixture = fixture

    def list_fixtures(self):
        return [self.fixture]

    def get_fixture(self, fixture_id: str):
        return self.fixture if fixture_id == self.fixture.id else None


def make_fixture():
    return Fixture(
        id="fake-001",
        league="Test",
        starts_at=datetime.now(UTC),
        home=TeamProfile(name="Local", strength=70, recent_form=0.7),
        away=TeamProfile(name="Visitante", strength=68, recent_form=0.6),
        odds=Odds(home=2.1, draw=3.2, away=3.4),
    )


def test_list_fixtures_depends_on_port_only():
    fixture = make_fixture()
    assert ListFixtures(FakeSportsData(fixture)).execute() == [fixture]


def test_predict_fixture_orchestrates_domain_service():
    fixture = make_fixture()
    result = PredictFixture(FakeSportsData(fixture), PredictionEngine()).execute(fixture.id)
    assert result is not None
    assert result.fixture_id == fixture.id
    assert result.data_source == "fake-test-provider"


def test_predict_fixture_returns_none_for_unknown_id():
    fixture = make_fixture()
    result = PredictFixture(FakeSportsData(fixture), PredictionEngine()).execute("missing")
    assert result is None
