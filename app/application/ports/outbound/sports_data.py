"""Puerto de salida para proveedores de datos deportivos."""
from typing import Protocol

from app.domain.models import Fixture


class SportsDataPort(Protocol):
    """Contrato que cualquier proveedor de datos debe implementar."""

    name: str

    def list_fixtures(self) -> list[Fixture]:
        """Devuelve fixtures próximos."""

    def get_fixture(self, fixture_id: str) -> Fixture | None:
        """Busca un fixture por identificador."""
