# Runtime y consola del agente

## Qué es “persistente” aquí

El agente corre dentro del proceso del servidor. Al arrancar, el `lifespan` de FastAPI inicia `AgentTimerScheduler`, que ejecuta un ciclo cada `AGENT_INTERVAL_SECONDS`. Cada ciclo produce un `AgentRun` con evidencia de auditoría. El proceso debe permanecer vivo: si se detiene Uvicorn, se detiene el temporizador, pero el registro en JSONL sobrevive.

## Ciclo de vida

```text
uvicorn arranca
   -> build_container() ensambla dependencias
   -> FastAPI lifespan: scheduler.start()
   -> ciclo STARTUP (si AGENT_STARTUP_RUN=true)
   -> bucle: espera interval_seconds -> ciclo SCHEDULE -> repite
   -> POST /api/v1/agent/runs -> ciclo MANUAL y se pospone el SCHEDULE siguiente
   -> shutdown: scheduler.stop() cancela la tarea
```

## Configuración

| Variable | Por defecto | Efecto |
|---|---|---|
| `AGENT_ENABLED` | `true` | `false` desactiva el ciclo automático; la API y el botón manual siguen operativos. |
| `AGENT_INTERVAL_SECONDS` | `600` | Segundos entre ciclos. El código aplica un mínimo de 5 s. |
| `AGENT_STARTUP_RUN` | `true` | Ejecuta un ciclo apenas inicia el servidor. |
| `RUNS_FILE` | `data/agent_runs.jsonl` | Ruta del registro auditable. |

## Formato del registro

Una ejecución por línea, en JSON con tipos canónicos:

```json
{"id":"f73586ba1474","trigger":"schedule","status":"success","started_at":"2026-11-21T16:13:41.018659Z","finished_at":"...","duration_ms":0.412,"model_version":"baseline-v0.2","data_source":"demo-static-v1","fixtures_analyzed":2,"signals":[{"fixture_id":"demo-001","home":"Aurora FC","away":"Río Norte","likely_outcome":"home","likely_probability":0.49,"best_outcome":"away","confidence":"alta","recommendation":"Mayor probabilidad: home (49.0%) · Señal de valor: away (EV +5.3%)","best_expected_value":0.0534}],"error":null}
```

El archivo está fuera de Git (`data/` en `.gitignore`): es dato operativo, no fuente.

## Cómo se lee la consola

- **Píldora de estado:** `AGENTE ACTIVO` significa que el temporizador está corriendo; `DESACTIVADO` indica `AGENT_ENABLED=false`.
- **Próximo ciclo:** cuenta regresiva al siguiente disparo programado; un disparo manual la reinicia.
- **Ciclos registrados:** total de `AgentRun` persistidos.
- **Tarjetas de partido:** barra = probabilidad del modelo; EV = valor esperado contra la cuota; “cuota justa” y “margen de la casa” permiten ver cuánto cobra el mercado.
- **Aviso amarillo:** el modelo y el mercado difieren 15 pp o más; normalmente indica datos sospechosos, no una oportunidad.
- **Registro del agente:** línea por ejecución con hora, disparador, duración, modelo y fuente; “Ver señales” despliega el detalle.

## Lecturas de ingeniería aprendidas

1. Definir un `lifespan` no lo ejecuta: debe inyectarse en el constructor de FastAPI y existe una prueba de regresión que lo garantiza.
2. Un EV de +59 % era una señal de datos inconsistentes, no de oportunidad: por eso ahora hay un guardia de divergencia.
3. La duración de un ciclo no debe medirse restando `datetime` (resolución limitada): se usa `time.perf_counter`.
