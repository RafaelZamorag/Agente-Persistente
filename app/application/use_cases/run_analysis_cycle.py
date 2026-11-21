"""Caso de uso: ejecutar un ciclo completo del agente y dejar evidencia."""
import time
from datetime import UTC, datetime

from app.application.ports.outbound.run_repository import RunRepositoryPort
from app.application.ports.outbound.sports_data import SportsDataPort
from app.application.use_cases.predict_fixture import PredictFixture
from app.domain.agent import AgentRun, RunSignal, RunStatus, RunTrigger


class RunAnalysisCycle:
    """Orquesta proveedor, predicción y registro sin conocer HTTP ni el temporizador."""

    def __init__(
        self,
        sports_data: SportsDataPort,
        predict_fixture: PredictFixture,
        repository: RunRepositoryPort,
        model_version: str,
    ) -> None:
        self._sports_data = sports_data
        self._predict_fixture = predict_fixture
        self._repository = repository
        self._model_version = model_version

    def execute(self, trigger: RunTrigger) -> AgentRun:
        started_at = datetime.now(UTC)
        # perf_counter evita registrar 0 ms cuando el ciclo tarda menos de un
        # milisegundo: la diferencia de datetimes tiene resolución limitada.
        elapsed = time.perf_counter
        started_perf = elapsed()
        try:
            fixtures = self._sports_data.list_fixtures()
            signals = self._build_signals(fixtures)
            run = self._make_run(
                trigger, started_at, (elapsed() - started_perf) * 1000, len(fixtures), signals, None
            )
        except Exception as exc:  # noqa: BLE001 - el runtime debe registrar la falla
            run = self._make_run(
                trigger,
                started_at,
                (elapsed() - started_perf) * 1000,
                0,
                [],
                f"{type(exc).__name__}: {exc}",
            )
        self._repository.append(run)
        return run

    def _build_signals(self, fixtures) -> list[RunSignal]:
        signals: list[RunSignal] = []
        for fixture in fixtures:
            prediction = self._predict_fixture.execute(fixture.id)
            if prediction is None:
                continue
            best = max(prediction.expected_value, key=prediction.expected_value.get)
            likely = max(prediction.probabilities, key=prediction.probabilities.get)
            signals.append(
                RunSignal(
                    fixture_id=fixture.id,
                    home=fixture.home.name,
                    away=fixture.away.name,
                    likely_outcome=likely.value,
                    likely_probability=prediction.probabilities[likely],
                    best_outcome=best.value,
                    confidence=prediction.confidence,
                    recommendation=prediction.recommendation,
                    best_expected_value=prediction.expected_value[best],
                )
            )
        return signals

    def _make_run(
        self,
        trigger: RunTrigger,
        started_at: datetime,
        duration_ms: float,
        fixtures_analyzed: int,
        signals: list[RunSignal],
        error: str | None,
    ) -> AgentRun:
        finished_at = datetime.now(UTC)
        return AgentRun(
            trigger=trigger,
            status=RunStatus.FAILED if error else RunStatus.SUCCESS,
            started_at=started_at,
            finished_at=finished_at,
            duration_ms=round(duration_ms, 3),
            model_version=self._model_version,
            data_source=self._sports_data.name,
            fixtures_analyzed=fixtures_analyzed,
            signals=signals,
            error=error,
        )
