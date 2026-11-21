# SPEC-002 — Runtime persistente y consola del agente

## Estado

- **Versión:** 0.3.1
- **Depende de:** SPEC-001 (MVP y arquitectura hexagonal)
- **Objetivo:** que el agente sea visible y observable: ejecutarse solo, registrar cada ejecución y mostrarlo en una consola web.

## Problema detectado

SPEC-001 entregó una “vitrina” estática: mostraba dos predicciones, pero no había agente en ejecución. Durante la verificación de este incremento se encontraron además dos defectos de fondo.

| Defecto | Síntoma | Causa raíz | Corrección |
|---|---|---|---|
| Agente sin runtime | `/api/v1/agent/status` devolvía `running: false` y `total_runs: 0` | El `lifespan` estaba definido en `main.py` pero nunca se inyectaba al constructor de FastAPI | `build_container` expone `lifespan_hooks` y el adaptador HTTP lo pasa a `FastAPI(lifespan=...)` |
| Señales absurdas | Valor esperado de +59 % en un fixture demo | El baseline asignaba solo ~17 % al empate y las cuotas demo eran incoherentes con el modelo | Modelo logístico con masa de empate calibrada (16 %–32 %), margen de casa, cuotas justas y guardia de divergencia |

## Requisitos funcionales

1. `FR-1` El agente ejecuta un ciclo de análisis cada `AGENT_INTERVAL_SECONDS` segundos.
2. `FR-2` Cada ciclo registra instante de inicio, disparador, duración, versión del modelo, fuente, fixtures analizados y señales.
3. `FR-3` El registro persiste entre reinicios en JSONL (`RUNS_FILE`).
4. `FR-4` Puede dispararse un ciclo manual desde la consola sin desincronizar el ciclo programado.
5. `FR-5` La consola muestra estado del runtime, cuenta regresiva, señales explicables y línea de tiempo de ejecuciones.
6. `FR-6` Un fallo del proveedor no derriba el servicio: se registra como `status: failed` con el error.
7. `FR-7` Si el modelo diverge 15 pp o más del mercado, se muestra un aviso y la confianza baja a “muy baja”.

## Requisitos no funcionales

- **Observabilidad:** `/api/v1/agent/status` responde sin tocar el disco de forma costura; el registro es auditable en texto plano.
- **Aislamiento:** el dominio y los casos de uso no conocen FastAPI, `asyncio` ni el sistema de archivos.
- **Determinismo:** las pruebas desactivan el temporizador y redirigen el registro a un directorio temporal.
- **Seguridad:** sin credenciales; el directorio `data/` está excluido de Git.

## Contratos de API

| Método | Ruta | Propósito |
|---|---|---|
| GET | `/api/v1/agent/status` | Estado del planificador, versión de modelo, fuente y ruta del registro. |
| GET | `/api/v1/agent/runs?limit=` | Ejecuciones recientes de la más nueva a la más antigua. |
| POST | `/api/v1/agent/runs` | Dispara un ciclo (`startup`, `schedule` o `manual`). |
| GET | `/` | Consola del agente. |
| GET | `/assets/{archivo}` | CSS y JS de la consola. |

## Criterios de aceptación

- Después de arrancar el servidor, `total_runs` aumenta sin intervención humana.
- `data/agent_runs.jsonl` contiene una línea JSON por ejecución.
- La consola se renderiza con las barras de probabilidad visibles y sin errores de consola del navegador.
- Un disparo manual pospone el siguiente ciclo en lugar de ejecutarlo dos veces.
- Ninguna prueba depende de esperar el intervalo real de producción.
- `pytest` y `ruff` pasan; una prueba de regresión fija el wiring del `lifespan`.

## Fuera de alcance

Ejecución de apuestas, autenticación, despliegue gestionado, modelos entrenados y datos reales en vivo.
