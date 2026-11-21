"""Puertos para fuentes de datos deportivas."""
from abc import ABC, abstractmethod

from app.domain.models import Fixture


class SportsDataProvider(ABC):
    """Interfaz estable para sustituir el proveedor demo por uno real."""

    name: str

    @abstractmethod
    def list_fixtures(self) -> list[Fixture]:
        """Devuelve partidos próximos con cuotas y hora de captura."""

    @abstractmethod
    def get_fixture(self, fixture_id: str) -> Fixture | None:
        """Busca un partido por identificador."""
