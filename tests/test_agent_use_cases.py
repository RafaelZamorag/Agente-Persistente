from datetime import UTC, datetime

import pytest

from app.adapters.outbound.in_memory_run_repository import InMemoryRunRepository
from app.application.use_cases.get_agent_status import GetAgentStatus
from app.application.use_cases.list_agent_runs import ListAgentRuns
from app.application.use_cases.predict_fixture import PredictFixture
from app.application.use_cases.run_analysis_cycle import RunAnalysisCycle
from app.domain.agent import AgentSchedulerState, RunStatus, RunTrigger
from app.domain.models import Fixture, Odds, TeamProfile
from app.domain.prediction_engine import PredictionEngine


class FakeSportsData:
    name = "fake-agent-provider"

    def __init__(self, fixtures):
        self._fixtures = fixtures

    def list_fixtures(self):
        return list(self._fixtures)

    def get_fixture(self, fixture_id):
        return next((f for f in self._fixtures if f.id == fixture_id), None)


class FakeScheduler:
    def __init__(self, total=0):
        self._total = total

    def state(self):
        return AgentSchedulerState(
            enabled=True,
            interval_seconds=600,
            running=True,
            next_run_at=datetime.now(UTC),
            total_runs=self._total,
            last_run_id=None,
        )


class BrokenSportsData(FakeSportsData):
    def list_fixtures(self):
        raise RuntimeError("proveedor indisponible")


def make_fixture(fixture_id="fake-001"):
    return Fixture(
        id=fixture_id,
        league="Test",
        starts_at=datetime.now(UTC),
        home=TeamProfile(name="Local", strength=74, recent_form=0.68),
        away=TeamProfile(name="Visitante", strength=69, recent_form=0.6),
        odds=Odds(home=2.05, draw=3.3, away=3.6),
    )


def build_cycle(sports_data, repository):
    predict = PredictFixture(sports_data, PredictionEngine())
    return RunAnalysisCycle(sports_data, predict, repository, PredictionEngine.model_version)


@pytest.mark.use_case
def test_cycle_records_successful_run_with_signals():
    repository = InMemoryRunRepository()
    sports_data = FakeSportsData([make_fixture("a"), make_fixture("b")])

    run = build_cycle(sports_data, repository).execute(RunTrigger.SCHEDULE)

    assert run.status is RunStatus.SUCCESS
    assert run.fixtures_analyzed == 2
    assert len(run.signals) == 2
    assert run.data_source == "fake-agent-provider"
    assert repository.total() == 1
    assert repository.recent(1)[0].id == run.id


@pytest.mark.use_case
def test_cycle_records_failure_without_raising():
    repository = InMemoryRunRepository()
    run = build_cycle(BrokenSportsData([]), repository).execute(RunTrigger.MANUAL)

    assert run.status is RunStatus.FAILED
    assert "proveedor indisponible" in run.error
    assert repository.total() == 1


@pytest.mark.use_case
def test_list_agent_runs_is_newest_first():
    repository = InMemoryRunRepository()
    cycle = build_cycle(FakeSportsData([make_fixture()]), repository)
    cycle.execute(RunTrigger.SCHEDULE)
    cycle.execute(RunTrigger.MANUAL)

    runs = ListAgentRuns(repository).execute(limit=5)

    assert len(runs) == 2
    assert runs[0].trigger is RunTrigger.MANUAL


@pytest.mark.use_case
def test_status_uses_repository_total():
    repository = InMemoryRunRepository()
    build_cycle(FakeSportsData([make_fixture()]), repository).execute(RunTrigger.STARTUP)

    state = GetAgentStatus(FakeScheduler(), repository).execute()

    assert state.total_runs == 1
    assert state.enabled is True
