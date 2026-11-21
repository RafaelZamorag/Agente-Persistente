# TASKS-002 — Backlog del incremento (prefijo C)

Se usa prefijo `C` (console/runtime) para no colisionar con los identificadores `T` del MVP.

- [x] C-01 Diagnosticar que la ruta raíz servía HTML y que lo ausente era la capa de agente.
- [x] C-02 Definir entidades de ejecución del agente en el dominio.
- [x] C-03 Definir puertos inbound y outbound del runtime.
- [x] C-04 Implementar `RunAnalysisCycle` con registro de éxito y de fallo.
- [x] C-05 Implementar `ListAgentRuns` y `GetAgentStatus`.
- [x] C-06 Implementar `FilesystemRunRepository` en JSONL.
- [x] C-07 Implementar `InMemoryRunRepository` para pruebas.
- [x] C-08 Implementar `AgentTimerScheduler` como adaptador de entrada.
- [x] C-09 Corregir el wiring del `lifespan` que impedía el autodisparo.
- [x] C-10 Añadir endpoints de status, listado y disparo manual.
- [x] C-11 Construir la consola del agente con estado, señales y línea de tiempo.
- [x] C-12 Recalibrar el baseline: banda de empate, margen de casa y cuota justa.
- [x] C-13 Añadir guardia de divergencia mercado-modelo con aviso visible.
- [x] C-14 Separar favorito probabilístico de señal de valor en la salida.
- [x] C-15 Corregir renderizado de barras y precisión de duración.
- [x] C-16 Prueba de regresión del ciclo de vida del servidor.
- [x] C-17 Verificación end-to-end con servidor real y captura headless.
- [ ] C-18 Migrar el registro JSONL a SQLite detrás del mismo `RunRepositoryPort`.
- [ ] C-19 Añadir métricas de calibración por corrida (Brier, log loss) al registro.
- [ ] C-20 Sustituir el sondeo de la consola por SSE o WebSocket.
