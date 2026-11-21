"""Adaptador de entrada: temporizador asíncrono que dispara el ciclo del agente."""
import asyncio
from datetime import UTC, datetime, timedelta

from app.application.use_cases.run_analysis_cycle import RunAnalysisCycle
from app.domain.agent import AgentRun, AgentSchedulerState, RunTrigger

MIN_INTERVAL_SECONDS = 5


class AgentTimerScheduler:
    """Ejecuta el análisis cada N segundos y permite disparos manuales.

    Es un adaptador de entrada: la iniciativa nace del reloj, no del dominio.
    Un disparo manual desplaza la cuenta regresiva en lugar de provocar una
    ejecución doble del ciclo programado.
    """

    def __init__(
        self,
        run_cycle: RunAnalysisCycle,
        interval_seconds: int,
        enabled: bool = True,
        run_on_startup: bool = True,
        tick_seconds: float = 1.0,
    ) -> None:
        self._run_cycle = run_cycle
        self._interval_seconds = max(int(interval_seconds), MIN_INTERVAL_SECONDS)
        self._enabled = enabled
        self._run_on_startup = run_on_startup
        self._tick_seconds = max(float(tick_seconds), 0.01)
        self._task: asyncio.Task | None = None
        self._running = False
        self._next_run_at: datetime | None = None
        self._last_run_id: str | None = None
        self._total_runs = 0
        self._deadline_shift = 0.0
        self._deadline = 0.0

    async def start(self) -> None:
        if not self._enabled or self._task is not None:
            return
        self._running = True
        self._task = asyncio.create_task(self._loop(), name="agent-timer-scheduler")

    async def stop(self) -> None:
        self._running = False
        if self._task is not None:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
            self._task = None

    def run_now(self, trigger: RunTrigger = RunTrigger.MANUAL) -> AgentRun:
        """Ejecuta un ciclo inmediato y pospone el siguiente disparo programado."""
        run = self._register(self._run_cycle.execute(trigger))
        self._deadline_shift = self._interval_seconds
        return run

    def state(self) -> AgentSchedulerState:
        return AgentSchedulerState(
            enabled=self._enabled,
            interval_seconds=self._interval_seconds,
            running=self._running,
            next_run_at=self._next_run_at,
            total_runs=self._total_runs,
            last_run_id=self._last_run_id,
        )

    async def _loop(self) -> None:
        if self._run_on_startup:
            self._register(self._run_cycle.execute(RunTrigger.STARTUP))
            self._deadline_shift = self._interval_seconds
        while self._running:
            self._arm_deadline()
            while self._running:
                remaining = self._deadline - asyncio.get_running_loop().time()
                if remaining <= 0:
                    break
                await asyncio.sleep(min(self._tick_seconds, remaining))
            if not self._running:
                return
            self._register(self._run_cycle.execute(RunTrigger.SCHEDULE))

    def _arm_deadline(self) -> None:
        loop_time = asyncio.get_running_loop().time()
        self._deadline = loop_time + self._interval_seconds + self._deadline_shift
        self._deadline_shift = 0.0
        self._next_run_at = datetime.now(UTC) + timedelta(
            seconds=max(int(self._deadline - loop_time), 0)
        )

    def _register(self, run: AgentRun) -> AgentRun:
        self._total_runs += 1
        self._last_run_id = run.id
        return run
