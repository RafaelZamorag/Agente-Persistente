# Contexto persistente del proyecto

## Identidad

- **Proyecto:** Agente Persistente — Sports Prediction Assistant
- **Repositorio:** `RafaelZamorag/Agente-Persistente`
- **Rama principal:** `main`
- **Propietario:** Rafael Enrique Zamora García
- **Documentación:** español latinoamericano

## Misión

Agente académico que analiza eventos deportivos de forma periódica y comunica probabilidades explicables y auditables, sin ejecutar apuestas y sin afirmar certeza.

## Estado actual (v0.3.1)

Arquitectura hexagonal completa con runtime visible. El agente se autodispara al arrancar y cada `AGENT_INTERVAL_SECONDS`, registra cada ciclo en JSONL y se observa en la consola de `frontend/`. El modelo es un baseline logístico calibrado, explicable, con margen de casa, cuota justa y guardia de divergencia.

Métricas de la última verificación: 32 pruebas unitarias y de integración, `ruff` limpio, servidor real ejecutando ciclos automáticos, consola renderizada sin errores de navegador.

## Decisiones vigentes

| Área | Decisión | Motivo |
|---|---|---|
| Arquitectura | Hexagonal con puertos y composition root | Sustituir proveedor o entrada sin tocar el dominio |
| Datos | `DemoSportsDataAdapter` | Reproducibilidad y exposición sin API externa |
| Modelo | Baseline logístico v0.2 | Explicable en clase, sin dataset validado aún |
| Runtime | `asyncio` en `lifespan` de FastAPI | Persistente dentro del proceso, sin dependencias externas |
| Registro | JSONL en `data/agent_runs.jsonl` | Auditoría legible y cero dependencias; excluido de Git |
| Pruebas | Temporizador y disco desactivados en `conftest.py` | Determinismo y ausencia de esperas reales |

## Defectos corregidos (memoria de ingeniería)

1. **Sin autodisparo.** El `lifespan` estaba definido pero no se inyectaba en `FastAPI(...)`. Síntoma: `running: false`, `total_runs: 0`. Corrección: `lifespan_hooks` expuesto por el composition root. Prueba de regresión: `tests/test_agent_lifespan.py`.
2. **Señales irreales.** El baseline asignaba ~17 % al empate y las cuotas demo eran incoherentes, dando un EV de +59 %. Corrección: banda de empate 16 %–32 %, cuotas demo recalibradas, margen de casa, cuota justa y aviso si la divergencia es ≥15 pp.
3. **Barras invisibles.** Un `span` en línea ignoraba `width`, por lo que la barra no se pintaba. Corrección: `display: block` en `.bar-fill`.
4. **Duración en 0 ms.** Restar `datetime` perdía resolución. Corrección: `time.perf_counter` y campo `float`.

## Límites conocidos

Datos de demostración, sin backtesting, sin calibración empírica y sin validación de mercado. La consola usa sondeo, no SSE. Ninguna métrica de rendimiento del modelo ha sido publicada todavía.

## Próxima sesión recomendada

1. Elegir liga y proveedor con licencia explícita.
2. Implementar `outbound/api_sports_data.py` detrás de `SportsDataPort`.
3. Definir el esquema de snapshots históricos y capturarse antes del inicio del evento.
4. Implementar backtesting sin fuga temporal y reportar Brier score, log loss y ROI simulado con advertencias.
