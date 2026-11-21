# SPEC-001 — Agente de predicción deportiva responsable

## Estado

- **Estado:** aprobado para MVP académico
- **Versión:** 0.1.0
- **Responsable:** Rafael Zamora
- **Objetivo:** demostrar un agente que transforma datos de un partido en una predicción explicable, sin prometer resultados ni ejecutar apuestas.

## Problema

Las cuotas deportivas cambian en tiempo real y es difícil comparar una probabilidad estimada con la probabilidad implícita de una cuota. El sistema debe presentar una señal cuantitativa, sus factores y sus limitaciones, manteniendo una separación estricta entre análisis y ejecución de apuestas.

## Alcance del MVP

1. Consultar partidos próximos desde un proveedor desacoplado.
2. Calcular probabilidades 1X2 con un modelo base explicable.
3. Comparar la probabilidad estimada con la cuota decimal y calcular valor esperado.
4. Exponer resultados mediante API REST.
5. Mostrar un dashboard HTML para demostración.
6. Registrar modelo, hora de cálculo, fuente, datos faltantes y nivel de confianza.
7. Permitir modo demo reproducible sin credenciales externas.

## Fuera de alcance

- Apostar automáticamente o conectarse a una casa de apuestas.
- Prometer aciertos, rentabilidad o ingresos.
- Usar datos personales, sistemas de pago o datos de menores.
- Considerar la salida como asesoría financiera o garantía.
- Entrenar modelos complejos con un dataset no auditado.

## Criterios de aceptación

- `GET /health` responde estado del servicio y versión.
- `GET /api/v1/fixtures` devuelve partidos demo con fuente y timestamp.
- `GET /api/v1/predictions/{fixture_id}` devuelve probabilidades que suman 1, cuota implícita, valor esperado y explicación.
- El motor rechaza cuotas menores o iguales a 1.0.
- Cada predicción incluye advertencia de uso responsable.
- `pytest` pasa sin depender de internet.
- El README permite levantar el proyecto en menos de cinco minutos.

## Decisiones de diseño

- **Modelo:** baseline ponderado por fuerza relativa, forma reciente y ventaja de localía. Es intencionalmente explicable; no se presenta como modelo validado para apuestas reales.
- **Datos:** contrato `SportsDataProvider`; `DemoSportsDataProvider` para desarrollo y exposición.
- **Transparencia:** toda predicción lleva `model_version`, `generated_at`, `data_source`, `missing_data` y `explanation`.
- **Seguridad:** no se guardan tokens en Git; configuración por variables de entorno.
