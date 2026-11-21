"""Configuración central del agente mediante variables de entorno."""
from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Parámetros operativos; el MVP no requiere credenciales."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "Agente Persistente"
    agent_enabled: bool = True
    agent_interval_seconds: int = 600
    agent_startup_run: bool = True
    agent_max_signal_list: int = 20
    runs_file: Path = Path("data/agent_runs.jsonl")


@lru_cache
def get_settings() -> Settings:
    return Settings()
