"""Puerto de entrada para listar registros del agente."""
from typing import Protocol

from app.domain.agent import AgentRun


class ListAgentRunsUseCase(Protocol):
    def execute(self, limit: int = 20) -> list[AgentRun]:
        """Lista ejecuciones recientes."""
