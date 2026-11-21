"""Puerto de entrada para el estado operativo del agente."""
from typing import Protocol

from app.domain.agent import AgentSchedulerState


class GetAgentStatusUseCase(Protocol):
    def execute(self) -> AgentSchedulerState:
        """Devuelve el estado observable del runtime."""
