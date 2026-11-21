# Agente Persistente — Sports Prediction Assistant

MVP académico de un agente que genera probabilidades deportivas explicables a partir de un proveedor de datos desacoplado. El proyecto está diseñado para una exposición: se puede ejecutar sin credenciales, inspeccionar mediante OpenAPI y extender con datos reales cuando existan un contrato de proveedor, histórico validado y backtesting reproducible.

> **Advertencia:** este software es educativo. No ejecuta apuestas, no garantiza resultados y no debe usarse para perseguir pérdidas ni como asesoría financiera.

## Inicio rápido

Requiere Python 3.11 o superior.

```bash
python -m venv .venv
source .venv/bin/activate       # Windows: .venv\\Scripts\\activate
pip install -e '.[dev]'
uvicorn app.main:app --reload
```

Visita `http://127.0.0.1:8000` para el dashboard y `http://127.0.0.1:8000/docs` para OpenAPI.

Para validar el proyecto:

```bash
pytest -q
ruff check .
```

## Qué hace

El proveedor demo entrega dos fixtures deterministas. El baseline pondera fuerza, forma reciente y localía; normaliza el resultado como probabilidades 1X2 y calcula probabilidad implícita, edge y valor esperado frente a cuotas decimales. Cada respuesta incluye versión, fuente, hora, explicación, nivel de confianza y advertencia de uso responsable.

## Estructura

```text
app/                  Código del dominio, proveedores, servicios y API.
frontend/             Dashboard HTML sin dependencias externas.
specs/001-mvp/        Spec, plan y tareas del primer incremento.
docs/                 Contexto persistente, arquitectura y operación.
tests/                Pruebas unitarias y de API.
.github/workflows/     CI de lint y pruebas.
```

## Método de trabajo

Cada incremento nuevo debe crear o actualizar `specs/<id>/spec.md`, `plan.md` y `tasks.md`. `docs/context.md` conserva decisiones y el siguiente paso recomendado entre sesiones. El código debe mantener separado el proveedor de datos, el motor, la explicación y la interfaz.

## Próximos incrementos

La siguiente prioridad es T011: implementar un adaptador de datos reales en modo solo lectura, con licencia revisada, timestamps y manejo de errores. Después se debe construir un dataset histórico sin fuga temporal, hacer backtesting, medir Brier score y log loss, calibrar probabilidades y documentar los resultados antes de afirmar que el sistema es útil fuera del aula.

## API

- `GET /health` — estado del servicio.
- `GET /api/v1/fixtures` — fixtures disponibles y fuente.
- `GET /api/v1/predictions/{fixture_id}` — predicción explicable de un fixture.
- `GET /docs` — documentación OpenAPI interactiva.
