# Skills y tools del agente

El proyecto separa capacidades de alto nivel (skills) de herramientas técnicas (tools). Esta separación facilita explicar el comportamiento del agente y permite sustituir implementaciones sin cambiar el contrato principal.

## Skills

| Skill | Propósito | Estado |
|---|---|---|
| `fixture_discovery` | Encontrar partidos próximos y exponer fuente y hora. | MVP demo |
| `probability_estimation` | Convertir fuerza, forma y localía en probabilidades 1X2. | MVP |
| `odds_comparison` | Calcular probabilidad implícita, edge y valor esperado. | MVP |
| `explainable_reporting` | Presentar factores, versión y confianza en lenguaje claro. | MVP |
| `responsible_use` | Evitar garantías, ejecución automática y lenguaje de certeza. | MVP |
| `historical_backtesting` | Evaluar el modelo con datos pasados sin fuga temporal. | Roadmap |
| `live_monitoring` | Actualizar snapshots y detectar cambios de cuota. | Roadmap |

## Tools

| Tool | Contrato actual | Uso |
|---|---|---|
| `DemoSportsDataProvider` | `list_fixtures`, `get_fixture` | Datos reproducibles para desarrollo y exposición. |
| `PredictionEngine` | `predict(fixture, data_source)` | Motor determinista y explicable. |
| `GET /health` | Estado y versión | Observabilidad básica. |
| `GET /api/v1/fixtures` | Lista de fixtures | Alimenta el dashboard. |
| `GET /api/v1/predictions/{id}` | Predicción auditable | Devuelve probabilidades y explicación. |
| `/docs` | OpenAPI | Exploración y prueba manual de endpoints. |

## Recomendación de evolución

Antes de añadir un LLM, conviene mantener el cálculo numérico en Python y usar un modelo de lenguaje únicamente para resumir evidencia estructurada. Así se evita que un texto generado invente estadísticas o altere probabilidades. Cualquier skill futura debe declarar entradas, salidas, fuente, versión y manejo de errores.
