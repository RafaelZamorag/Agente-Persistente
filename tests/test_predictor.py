from datetime import UTC, datetime

import pytest
from pydantic import ValidationError

from app.domain.models import Fixture, Odds, Outcome, TeamProfile
from app.domain.prediction_engine import PredictionEngine


@pytest.fixture
def fixture():
    return Fixture(
        id="test-001",
        league="Test",
        starts_at=datetime.now(UTC),
        home=TeamProfile(name="Local", strength=80, recent_form=0.8),
        away=TeamProfile(name="Visitante", strength=60, recent_form=0.5),
        odds=Odds(home=2.0, draw=3.5, away=4.0),
    )


def test_probabilities_sum_to_one(fixture):
    result = PredictionEngine().predict(fixture, "test")
    assert sum(result.probabilities.values()) == pytest.approx(1.0)
    assert set(result.probabilities) == set(Outcome)


def test_stronger_home_team_has_highest_probability(fixture):
    result = PredictionEngine().predict(fixture, "test")
    assert result.probabilities[Outcome.HOME] > result.probabilities[Outcome.AWAY]
    assert result.explanation


def test_invalid_odds_are_rejected():
    with pytest.raises(ValidationError):
        Odds(home=1.0, draw=3.0, away=4.0)
