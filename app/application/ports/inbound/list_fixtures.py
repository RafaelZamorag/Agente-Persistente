"""Puerto de entrada del caso de uso de listado."""
from typing import Protocol

from app.domain.models import Fixture


class ListFixturesUseCase(Protocol):
    def execute(self) -> list[Fixture]:
        """Lista los fixtures disponibles."""
