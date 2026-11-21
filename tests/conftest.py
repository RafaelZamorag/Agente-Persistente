"""Configuración de pruebas: el agente se evalúa de forma determinista y aislada."""
import os
import tempfile
from pathlib import Path

# Debe aplicarse antes de importar la aplicación, que lee variables de entorno.
os.environ.update(
    {
        "AGENT_ENABLED": "false",
        "AGENT_STARTUP_RUN": "false",
        "AGENT_INTERVAL_SECONDS": "60",
        "RUNS_FILE": str(Path(tempfile.mkdtemp(prefix="agente-runs-")) / "agent_runs.jsonl"),
    }
)


def pytest_configure(config):
    """Registra marcas para agrupar pruebas por capa arquitectónica."""
    config.addinivalue_line("markers", "use_case: pruebas de casos de uso")
    config.addinivalue_line("markers", "adapter: pruebas de adaptadores")
