# Operación y recomendaciones

## Instalación y ejecución

```bash
python -m venv .venv
source .venv/bin/activate          # Windows: .\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -e ".[dev]"
python -m uvicorn app.main:app --reload
```

Consola: `http://127.0.0.1:8000` · OpenAPI: `http://127.0.0.1:8000/docs` · Estado: `http://127.0.0.1:8000/health`.

El agente queda activo mientras el proceso esté vivo. Para una demostración con ciclos visibles, reducir el intervalo:

```bash
AGENT_INTERVAL_SECONDS=15 python -m uvicorn app.main:app
```

## Verificación rápida antes de exponer

```bash
pytest -q && ruff check .
curl -s localhost:8000/api/v1/agent/status | python3 -m json.tool
sleep 30
curl -s "localhost:8000/api/v1/agent/runs?limit=5" | python3 -m json.tool
```

Comprobaciones esperadas: `running: true`, `total_runs` creciendo sin intervención, una línea JSON por corrida en `data/agent_runs.jsonl` y barras de probabilidad visibles en la consola.

## Variables del runtime

| Variable | Por defecto | Nota |
|---|---|---|
| `AGENT_ENABLED` | `true` | `false` pausa el ciclo automático; el botón manual sigue funcionando |
| `AGENT_INTERVAL_SECONDS` | `600` | Mínimo aplicado por código: 5 s |
| `AGENT_STARTUP_RUN` | `true` | Útil para que la consola muestre datos al abrirla |
| `RUNS_FILE` | `data/agent_runs.jsonl` | Dato operativo; excluido de Git |

## Antes de conectar datos reales

- Verificar licencia, atribución y límites de petición del proveedor.
- Guardar la hora de captura de cada cuota y del inicio del evento.
- Nunca usar información posterior al inicio del partido como si fuera previa.
- Versionar transformaciones y modelo; el `model_version` viaja en cada respuesta.
- Publicar métricas de calibración, no solo señales.

## Guion sugerido para la exposición

1. Mostrar la consola y señalar que el contador de ciclos sube solo: el agente está corriendo.
2. Abrir `data/agent_runs.jsonl` y explicar que cada línea es evidencia auditable.
3. Comparar “mayor probabilidad” con “señal de valor” en un mismo partido.
4. Explicar el margen de la casa: por qué casi todas las cuotas reales dan EV negativo.
5. Mostrar el aviso de divergencia y argumentar que detectar datos malos vale más que fingir precisión.
6. Cerrar con la hoja de ruta: proveedor real, backtesting y calibración.

## Límites éticos

Sistema educativo y analítico. No debe incentivar apuestas compulsivas, perseguir pérdidas, automatizar decisiones financieras ni presentarse como fuente de ingresos. Cualquier integración futura con interfaces de apuestas se mantiene en modo solo lectura y con confirmación humana explícita.
