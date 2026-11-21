"""Puerto de entrada para ejecutar un ciclo de análisis."""
from typing import Protocol

from app.domain.agent import AgentRun, RunTrigger


class RunAnalysisCycleUseCase(Protocol):
    def execute(self, trigger: RunTrigger) -> AgentRun:
        """Analiza los fixtures disponibles y registra el resultado."""
