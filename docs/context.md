# Contexto persistente del proyecto

## Identidad

- **Proyecto:** Agente Persistente — Sports Prediction Assistant
- **Repositorio:** `RafaelZamorag/Agente-Persistente`
- **Rama principal:** `main`
- **Propietario:** Rafael Enrique Zamora García
- **Idioma de documentación:** español latinoamericano

## Misión

Construir un agente académico que analice eventos deportivos y comunique probabilidades explicables en tiempo real, sin ejecutar apuestas y sin afirmar certeza.

## Principios

1. Evidencia antes que intuición.
2. Separar datos, modelo, explicación y decisión humana.
3. Registrar fuente, hora y versión del modelo.
4. No almacenar secretos ni credenciales.
5. Diseñar para auditoría y reproducibilidad.
6. Incluir uso responsable en cada interfaz.

## Convenciones

- Especificaciones en `specs/<id>/spec.md`.
- Plan en `specs/<id>/plan.md`.
- Tareas en `specs/<id>/tasks.md`.
- Código Python con tipado y docstrings.
- Cambios pequeños, testeables y documentados.
- Ningún commit debe contener `.env` ni tokens.

## Estado actual

El MVP usa `DemoSportsDataProvider`, un modelo base explicable y una API FastAPI. Antes de usar datos reales se debe completar T011, establecer términos del proveedor, validar calidad temporal y realizar backtesting.

## Próxima sesión recomendada

1. Elegir una liga y proveedor de datos permitido.
2. Definir esquema de snapshots históricos.
3. Implementar backtesting sin fuga de información.
4. Calibrar probabilidades y reportar Brier score, log loss y ROI simulado con advertencias.
