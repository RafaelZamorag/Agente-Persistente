"""Adaptador de salida: persistencia local en JSONL, sin dependencias externas."""
import json
from pathlib import Path

from app.domain.agent import AgentRun


class FilesystemRunRepository:
    """Guarda cada ejecución como una línea JSON para auditoría y exposición."""

    def __init__(self, path: Path) -> None:
        self._path = Path(path)
        self._path.parent.mkdir(parents=True, exist_ok=True)
        if not self._path.exists():
            self._path.touch()

    @property
    def path(self) -> Path:
        return self._path

    def append(self, run: AgentRun) -> None:
        payload = run.model_dump(mode="json")
        with self._path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(payload, ensure_ascii=False) + "\n")

    def recent(self, limit: int = 20) -> list[AgentRun]:
        runs = self._read_all()
        return list(reversed(runs))[: max(limit, 0)]

    def total(self) -> int:
        return len(self._read_all())

    def _read_all(self) -> list[AgentRun]:
        if not self._path.exists():
            return []
        runs: list[AgentRun] = []
        with self._path.open(encoding="utf-8") as handle:
            for line in handle:
                line = line.strip()
                if not line:
                    continue
                try:
                    runs.append(AgentRun.model_validate(json.loads(line)))
                except (ValueError, json.JSONDecodeError):
                    # Una línea corrupta no debe romper el registro histórico.
                    continue
        return runs
