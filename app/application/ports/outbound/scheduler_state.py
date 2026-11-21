"""Puerto de salida para exponer el estado del runtime del agente."""
from typing import Protocol

from app.domain.agent import AgentSchedulerState


class SchedulerStatePort(Protocol):
    def state(self) -> AgentSchedulerState:
        """Snapshot del planificador para observabilidad."""
