# Arquitectura hexagonal

```text
        Consola web (frontend)            Cliente REST / curl
                |                                   |
   +------------+-----------------------------------+-------------+
   |  ADAPTADORES DE ENTRADA                                     |
   |  inbound/http.py  FastAPI      inbound/timer_scheduler.py    |
   |  (lifespan -> start/stop)      ciclo por reloj (SCHEDULE)    |
   +------------+-----------------------------------+-------------+
                v                                   v
        PUERTOS INBOUND (Protocol)          run_now(trigger)
        ListFixtures / PredictFixture
        RunAnalysisCycle / ListAgentRuns
        GetAgentStatus
                |                                   |
                v                                   v
        CASOS DE USO (application/use_cases)
        ListFixtures  PredictFixture  RunAnalysisCycle
        ListAgentRuns GetAgentStatus
                |                        |
                v                        v
   DOMINIO: PredictionEngine      PUERTOS OUTBOUND
   entidades Fixture/Prediction    SportsDataPort   RunRepositoryPort
   AgentRun/RunSignal              SchedulerStatePort
                                       |                 |
                                       v                 v
                        ADAPTADORES OUTBOUND (demo/API futura)
                        DemoSportsDataAdapter  FilesystemRunRepository
                        InMemoryRunRepository
```

`bootstrap.py` (composition root) es el único módulo que conoce las implementaciones concretas y construye el `lifespan` que engancha el temporizador al ciclo de vida del servidor. `main.py` solo llama `build_container()` y `create_http_app(container)`.

## Capas

### Dominio (`app/domain`)

Entidades del problema: `Fixture`, `Odds`, `TeamProfile`, `Outcome`, `Prediction`, `AgentRun`, `RunSignal`, `AgentSchedulerState`. Reglas: `PredictionEngine`, que también calcula probabilidad implícita, margen de casa y cuota justa. No hay importaciones de FastAPI, `asyncio`, `pathlib` ni SDKs.

### Aplicación (`app/application`)

`ports/inbound` define lo que el exterior puede pedir. `ports/outbound` define lo que el agente necesita del exterior. `use_cases` orquesta: `RunAnalysisCycle` obtiene fixtures, pide predicciones y deja evidencia de la corrida, incluyendo el fallo. Cada caso de uso tiene una sola responsabilidad.

### Adaptadores (`app/adapters`)

`inbound/http.py` traduce REST a casos de uso y sirve la consola. `inbound/timer_scheduler.py` convierte el reloj en llamadas al caso de uso. `outbound/*` implementan `SportsDataPort` y `RunRepositoryPort`.

## Flujo de un ciclo automático

1. El temporizador cumple el intervalo y llama `RunAnalysisCycle.execute(SCHEDULE)`.
2. El caso de uso pide fixtures a `SportsDataPort`.
3. Para cada fixture invoca `PredictFixture`, que usa `PredictionEngine`.
4. Se construye `AgentRun` con inicio, fin, duración, modelo, fuente y señales.
5. Se guarda en `RunRepositoryPort` (JSONL hoy).
6. La consola lee `/api/v1/agent/runs` y `/api/v1/agent/status`.

## Reglas de evolución

- Nuevo proveedor: crear un adaptador que implemente `SportsDataPort`; cambiar solo `build_container`.
- Nuevo almacenamiento: implementar `RunRepositoryPort`; casos de uso intactos.
- Nueva entrada (CLI, bot de Telegram): invocar los mismos puertos inbound.
- Nunca importar un SDK externo en `app/domain`.
