# PLAN-002 — Secuencia de implementación

## Fase A — Diagnóstico antes de tocar código

1. Confirmar que `GET /` respondía 200 y servía HTML real: el problema no era de enrutamiento.
2. Concluir que faltaba la capa de agente: ciclo de ejecución, registro y consola.
3. Levantar el servidor y observar el estado real: `running: false` reveló el bug de wiring.

## Fase B — Dominio y puertos

1. Entidades `AgentRun`, `RunSignal`, `AgentSchedulerState`, `RunStatus`, `RunTrigger`.
2. Puerto outbound `RunRepositoryPort` y `SchedulerStatePort`.
3. Puertos inbound `RunAnalysisCycleUseCase`, `ListAgentRunsUseCase`, `GetAgentStatusUseCase`.

## Fase C — Casos de uso

1. `RunAnalysisCycle` orquesta `SportsDataPort`, `PredictFixture` y el repositorio.
2. `ListAgentRuns` y `GetAgentStatus` exponen observabilidad.
3. Ningún caso de uso importa `asyncio`, FastAPI ni `pathlib`.

## Fase D — Adaptadores

1. `FilesystemRunRepository` en JSONL, tolerante a líneas corruptas.
2. `InMemoryRunRepository` para pruebas y demos sin disco.
3. `AgentTimerScheduler` como adaptador de entrada conducido por el reloj.
4. Adaptador HTTP ampliado con endpoints de agente y estáticos montados.

## Fase E — Correcciones de calidad del modelo

1. Recalibrar la masa de empate dentro de una banda realista.
2. Añadir margen de casa, cuotas justas y avisos de divergencia.
3. Recalibrar las cuotas demo para que sean coherentes con el modelo.
4. Separar en el texto “mayor probabilidad” de “señal de valor”.

## Fase F — Verificación

1. Pruebas de casos de uso con dobles, pruebas de adaptadores, prueba de regresión del `lifespan`.
2. Ejecución real del servidor con intervalo corto y observación de autodisparo.
3. Captura headless de la consola para validar maquetación y errores de navegador.

## Decisiones y reversibilidad

| Decisión | Alternativa descartada | Motivo |
|---|---|---|
| JSONL para el registro | SQLite | Legible en auditoría, cero dependencias, fácil de mostrar en clase; se migra detrás del mismo puerto. |
| `asyncio.create_task` en lifespan | APScheduler / cron externo | Suficiente para el MVP y mantiene el runtime como adaptador intercambiable. |
| Disparo manual delegando al runtime | Ejecutar el caso de uso desde HTTP | Mantiene contadores y cuenta regresiva coherentes. |
