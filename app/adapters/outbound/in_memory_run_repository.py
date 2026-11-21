"""Adaptador de salida en memoria, útil para pruebas y demostraciones."""
from app.domain.agent import AgentRun


class InMemoryRunRepository:
    def __init__(self) -> None:
        self._runs: list[AgentRun] = []

    def append(self, run: AgentRun) -> None:
        self._runs.append(run)

    def recent(self, limit: int = 20) -> list[AgentRun]:
        return list(reversed(self._runs))[: max(limit, 0)]

    def total(self) -> int:
        return len(self._runs)
