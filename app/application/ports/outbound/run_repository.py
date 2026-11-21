"""Puerto de salida para persistir registros del agente."""
from typing import Protocol

from app.domain.agent import AgentRun


class RunRepositoryPort(Protocol):
    """Contrato de almacenamiento auditable de ejecuciones."""

    def append(self, run: AgentRun) -> None:
        """Guarda una ejecución."""

    def recent(self, limit: int = 20) -> list[AgentRun]:
        """Devuelve las ejecuciones más recientes, de la más nueva a la más antigua."""

    def total(self) -> int:
        """Total de ejecuciones registradas."""
