# PLAN-001 — Implementación del MVP

## Fase 1 — Base del proyecto

- Configurar Python, dependencias y variables de entorno.
- Crear estructura `app/`, `tests/`, `docs/` y `specs/`.
- Añadir controles de calidad y exclusión de secretos.

## Fase 2 — Dominio y datos

- Definir entidades de partido, cuotas y predicción.
- Definir el contrato de proveedor.
- Implementar proveedor demo determinista.

## Fase 3 — Inteligencia del agente

- Implementar cálculo de probabilidades normalizadas.
- Implementar probabilidad implícita, margen y valor esperado.
- Generar explicación y nivel de confianza.
- Añadir protección contra datos incompletos y cuotas inválidas.

## Fase 4 — Interfaces

- Exponer endpoints FastAPI.
- Servir dashboard estático.
- Añadir endpoint de documentación OpenAPI automático.

## Fase 5 — Validación y entrega

- Ejecutar pruebas unitarias y de API.
- Verificar formato de respuesta y documentación.
- Revisar que no existan secretos.
- Crear commit y publicar en `main`.

## Riesgos y mitigaciones

| Riesgo | Mitigación |
|---|---|
| Datos desactualizados | Mostrar timestamp y fuente en cada respuesta. |
| Sobreajuste o falsa precisión | Baseline explicable, intervalos de confianza y advertencias. |
| Cambio brusco de cuotas | No cachear indefinidamente; registrar `generated_at`. |
| Uso irresponsable | No ejecutar apuestas, límites de exposición documentados y lenguaje no promesante. |
| Dependencia de un proveedor | Interfaz estable + adaptadores independientes. |
