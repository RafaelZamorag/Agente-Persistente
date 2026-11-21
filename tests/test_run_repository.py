import asyncio
import json

import pytest

from app.adapters.outbound.filesystem_run_repository import FilesystemRunRepository
from app.adapters.outbound.in_memory_run_repository import InMemoryRunRepository
from app.application.use_cases.predict_fixture import PredictFixture
from app.application.use_cases.run_analysis_cycle import RunAnalysisCycle
from app.domain.agent import RunStatus, RunTrigger
from app.domain.prediction_engine import PredictionEngine
from tests.test_agent_use_cases import FakeSportsData, make_fixture


@pytest.mark.adapter
def test_filesystem_repository_roundtrip(tmp_path):
    repository = FilesystemRunRepository(tmp_path / "runs.jsonl")
    cycle = RunAnalysisCycle(
        FakeSportsData([make_fixture()]),
        PredictFixture(FakeSportsData([make_fixture()]), PredictionEngine()),
        repository,
        "test-model",
    )

    run = cycle.execute(RunTrigger.SCHEDULE)
    stored = repository.recent(10)

    assert stored[0].id == run.id
    assert stored[0].status is RunStatus.SUCCESS
    raw = (tmp_path / "runs.jsonl").read_text(encoding="utf-8").strip()
    assert json.loads(raw)["trigger"] == "schedule"


@pytest.mark.adapter
def test_filesystem_repository_ignores_corrupted_lines(tmp_path):
    path = tmp_path / "runs.jsonl"
    path.write_text("{linea rota}\n", encoding="utf-8")
    repository = FilesystemRunRepository(path)

    assert repository.total() == 0

    cycle = RunAnalysisCycle(
        FakeSportsData([make_fixture()]),
        PredictFixture(FakeSportsData([make_fixture()]), PredictionEngine()),
        repository,
        "test-model",
    )
    cycle.execute(RunTrigger.MANUAL)

    assert repository.total() == 1


@pytest.mark.adapter
def test_scheduler_orders_runs_newest_first():
    repository = InMemoryRunRepository()
    sports_data = FakeSportsData([make_fixture()])
    cycle = RunAnalysisCycle(
        sports_data, PredictFixture(sports_data, PredictionEngine()), repository, "test-model"
    )

    cycle.execute(RunTrigger.SCHEDULE)
    cycle.execute(RunTrigger.MANUAL)

    assert [run.trigger for run in repository.recent(10)] == [
        RunTrigger.MANUAL,
        RunTrigger.SCHEDULE,
    ]


@pytest.mark.adapter
def test_disabled_scheduler_does_not_start_task():
    from app.adapters.inbound.timer_scheduler import AgentTimerScheduler

    repository = InMemoryRunRepository()
    sports_data = FakeSportsData([make_fixture()])
    cycle = RunAnalysisCycle(
        sports_data, PredictFixture(sports_data, PredictionEngine()), repository, "test-model"
    )
    scheduler = AgentTimerScheduler(cycle, interval_seconds=60, enabled=False)

    async def scenario():
        await scheduler.start()
        assert scheduler.state().running is False
        await scheduler.stop()

    asyncio.run(scenario())


@pytest.mark.adapter
def test_startup_run_and_manual_trigger_are_recorded():
    from app.adapters.inbound.timer_scheduler import AgentTimerScheduler

    repository = InMemoryRunRepository()
    sports_data = FakeSportsData([make_fixture()])
    cycle = RunAnalysisCycle(
        sports_data, PredictFixture(sports_data, PredictionEngine()), repository, "test-model"
    )
    scheduler = AgentTimerScheduler(
        cycle, interval_seconds=60, enabled=True, run_on_startup=True
    )

    async def scenario():
        await scheduler.start()
        await asyncio.sleep(0.05)
        manual = scheduler.run_now()
        state = scheduler.state()
        await scheduler.stop()
        return state, manual

    state, manual = asyncio.run(scenario())

    assert state.total_runs == 2
    assert state.last_run_id == manual.id
    assert repository.total() == 2
