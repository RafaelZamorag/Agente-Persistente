"""Adaptador de salida demo para datos deportivos reproducibles."""
from datetime import UTC, datetime, timedelta

from app.domain.models import Fixture, Odds, TeamProfile


class DemoSportsDataAdapter:
    """Implementación demo del puerto SportsDataPort."""

    name = "demo-static-v1"

    def __init__(self) -> None:
        now = datetime.now(UTC).replace(second=0, microsecond=0)
        self._fixtures = [
            Fixture(
                id="demo-001",
                league="Liga Demo",
                starts_at=now + timedelta(hours=2),
                home=TeamProfile(name="Aurora FC", strength=78, recent_form=0.76),
                away=TeamProfile(name="Río Norte", strength=72, recent_form=0.61),
                odds=Odds(home=1.90, draw=3.60, away=4.20),
            ),
            Fixture(
                id="demo-002",
                league="Liga Demo",
                starts_at=now + timedelta(hours=5),
                home=TeamProfile(name="Cóndor Unido", strength=65, recent_form=0.55),
                away=TeamProfile(name="Estrella Sur", strength=67, recent_form=0.70),
                odds=Odds(home=2.55, draw=3.20, away=2.65),
            ),
        ]

    def list_fixtures(self) -> list[Fixture]:
        return list(self._fixtures)

    def get_fixture(self, fixture_id: str) -> Fixture | None:
        return next((fixture for fixture in self._fixtures if fixture.id == fixture_id), None)
