# Skills y tools del agente

Se mantiene la separación entre capacidades de razonamiento (skills) y mecanismos técnicos (tools). Después del incremento 002, el agente tiene además un ciclo de vida propio.

## Skills

| Skill | Propósito | Implementación actual | Estado |
|---|---|---|---|
| `fixture_discovery` | Obtener partidos próximos con su fuente y hora | `ListFixtures` + `SportsDataPort` | MVP demo |
| `probability_estimation` | Convertir fuerza, forma y localía en probabilidades 1X2 | `PredictionEngine` v0.2 | MVP |
| `odds_comparison` | Margen de casa, probabilidad implícita, cuota justa, edge y EV | `PredictionEngine` | MVP |
| `market_consistency_guard` | Detectar divergencias ≥15 pp y degradar la confianza | `PredictionEngine._confidence` | MVP |
| `explainable_reporting` | Explicación, versión de modelo, hora y advertencias | `Prediction` | MVP |
| `periodic_execution` | Ejecutarse solo cada N segundos | `AgentTimerScheduler` + `RunAnalysisCycle` | MVP |
| `execution_auditing` | Dejar evidencia por corrida | `RunRepositoryPort` (JSONL) | MVP |
| `responsible_use` | Sin apuestas, sin garantías, decisión humana | `responsible_use` en cada respuesta | MVP |
| `historical_backtesting` | Evaluar con datos pasados sin fuga temporal | T014 | Pendiente |

## Tools

| Tool | Contrato | Uso |
|---|---|---|
| `DemoSportsDataAdapter` | `list_fixtures`, `get_fixture`, `name` | Datos reproducibles sin credenciales |
| `FilesystemRunRepository` | `append`, `recent`, `total` | Persistencia auditable en JSONL |
| `InMemoryRunRepository` | igual que el anterior | Pruebas y demos sin disco |
| `PredictionEngine` | `predict(fixture, data_source)` | Reglas de dominio deterministas |
| `RunAnalysisCycle` | `execute(trigger)` | Un ciclo completo con registro |
| `GetAgentStatus` / `ListAgentRuns` | `execute()` / `execute(limit)` | Observabilidad |
| `GET /api/v1/agent/status` | estado + versión + fuente + ruta del registro | Cabecera de la consola |
| `GET /api/v1/agent/runs` | corridas de la más nueva a la más antigua | Línea de tiempo |
| `POST /api/v1/agent/runs` | disparo manual o con trigger explícito | Botón de demostración |
| `/`, `/assets/*` | consola HTML, CSS y JS | Vista principal |
| `/docs` | OpenAPI | Prueba interactiva de contratos |

## Recomendación de diseño para el futuro

Mantener el cálculo numérico en Python y reservar cualquier modelo de lenguaje para resumir evidencia ya estructurada. Si se añade un LLM, debe recibir únicamente la salida JSON del caso de uso (probabilidades, cuotas, margen, avisos) y devolver texto, nunca recalcular ni inventar números. Así la explicación sigue siendo auditable y el riesgo de invención se limita al lenguaje, no a los datos.
