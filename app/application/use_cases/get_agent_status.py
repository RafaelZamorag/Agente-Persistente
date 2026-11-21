"""Caso de uso: estado operativo del agente."""
from app.application.ports.outbound.run_repository import RunRepositoryPort
from app.application.ports.outbound.scheduler_state import SchedulerStatePort
from app.domain.agent import AgentSchedulerState


class GetAgentStatus:
    def __init__(self, scheduler: SchedulerStatePort, repository: RunRepositoryPort) -> None:
        self._scheduler = scheduler
        self._repository = repository

    def execute(self) -> AgentSchedulerState:
        state = self._scheduler.state()
        return state.model_copy(update={"total_runs": self._repository.total()})
