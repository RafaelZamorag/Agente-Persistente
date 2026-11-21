"""Caso de uso: consultar ejecuciones recientes del agente."""
from app.application.ports.outbound.run_repository import RunRepositoryPort
from app.domain.agent import AgentRun


class ListAgentRuns:
    def __init__(self, repository: RunRepositoryPort) -> None:
        self._repository = repository

    def execute(self, limit: int = 20) -> list[AgentRun]:
        return self._repository.recent(limit=limit)
