"""Caso de uso de consulta de fixtures."""
from app.application.ports.outbound.sports_data import SportsDataPort
from app.domain.models import Fixture


class ListFixtures:
    def __init__(self, sports_data: SportsDataPort) -> None:
        self._sports_data = sports_data

    def execute(self) -> list[Fixture]:
        return self._sports_data.list_fixtures()
