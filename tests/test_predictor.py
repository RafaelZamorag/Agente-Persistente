from datetime import UTC, datetime

import pytest
from pydantic import ValidationError

from app.domain.models import Fixture, Odds, Outcome, TeamProfile
from app.domain.prediction_engine import DRAW_MAX, DRAW_MIN, PredictionEngine


def make_fixture(home_strength=80, away_strength=60, home_form=0.8, away_form=0.5, odds=None):
    return Fixture(
        id="test-001",
        league="Test",
        starts_at=datetime.now(UTC),
        home=TeamProfile(name="Local", strength=home_strength, recent_form=home_form),
        away=TeamProfile(name="Visitante", strength=away_strength, recent_form=away_form),
        odds=odds or Odds(home=1.90, draw=3.70, away=3.95),
    )


def test_probabilities_sum_to_one():
    result = PredictionEngine().predict(make_fixture(), "test")
    assert sum(result.probabilities.values()) == pytest.approx(1.0)
    assert set(result.probabilities) == set(Outcome)


def test_stronger_home_team_has_highest_probability():
    result = PredictionEngine().predict(make_fixture(), "test")
    assert result.probabilities[Outcome.HOME] > result.probabilities[Outcome.AWAY]
    assert result.explanation


def test_away_favours_reflect_negative_effect():
    result = PredictionEngine().predict(
        make_fixture(home_strength=60, away_strength=82, home_form=0.4, away_form=0.85), "test"
    )
    assert result.probabilities[Outcome.AWAY] > result.probabilities[Outcome.HOME]


def test_draw_mass_stays_in_realistic_band():
    for gap in (0, 8, 25):
        result = PredictionEngine().predict(
            make_fixture(away_strength=80 - gap, away_form=0.8 - gap / 100), "test"
        )
        assert DRAW_MIN <= result.probabilities[Outcome.DRAW] <= DRAW_MAX


def test_draw_is_most_likely_when_match_is_balanced():
    balanced = PredictionEngine().predict(make_fixture(away_strength=80, away_form=0.8), "test")
    lopsided = PredictionEngine().predict(make_fixture(away_strength=40, away_form=0.2), "test")
    assert balanced.probabilities[Outcome.DRAW] > lopsided.probabilities[Outcome.DRAW]


def test_bookmaker_margin_and_fair_odds():
    result = PredictionEngine().predict(make_fixture(), "test")
    assert result.bookmaker_margin == pytest.approx(
        sum(result.implied_probabilities.values()) - 1
    )
    assert result.fair_odds[Outcome.HOME] == pytest.approx(
        1 / result.probabilities[Outcome.HOME]
    )


def test_divergent_market_adds_warning_and_lowers_confidence():
    weird_odds = Odds(home=1.05, draw=20.0, away=30.0)
    result = PredictionEngine().predict(make_fixture(odds=weird_odds), "test")
    assert result.confidence == "muy baja"
    assert result.warnings and "diverge" in result.warnings[0]


def test_recommendation_separates_favourite_from_value_signal():
    result = PredictionEngine().predict(make_fixture(), "test")
    assert "Mayor probabilidad: home" in result.recommendation
    assert "Señal de valor" in result.recommendation or "Sin señal" in result.recommendation


def test_engine_is_deterministic():
    engine = PredictionEngine()
    fixture = make_fixture()
    first = engine.predict(fixture, "test")
    second = engine.predict(fixture, "test")
    assert first.probabilities == second.probabilities
    assert first.expected_value == second.expected_value
    assert first.model_version == engine.model_version


def test_invalid_odds_are_rejected():
    with pytest.raises(ValidationError):
        Odds(home=1.0, draw=3.0, away=4.0)
