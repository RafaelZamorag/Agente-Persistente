# Contexto persistente del proyecto

## Identidad

- **Proyecto:** Agente Persistente — Sports Prediction Assistant
- **Repositorio:** `RafaelZamorag/Agente-Persistente`
- **Rama principal:** `main`
- **Propietario:** Rafael Enrique Zamora García
- **Idioma de documentación:** español latinoamericano

## Misión

Construir un agente académico que analice eventos deportivos y comunique probabilidades explicables en tiempo real, sin ejecutar apuestas y sin afirmar certeza.

## Arquitectura vigente

El sistema usa arquitectura hexagonal. `app/domain` contiene reglas y entidades; `app/application` contiene puertos y casos de uso; `app/adapters/inbound` contiene HTTP; `app/adapters/outbound` contiene proveedores; `app/bootstrap.py` ensambla dependencias. `app/main.py` funciona como composition root HTTP.

## Principios

1. Evidencia antes que intuición.
2. Separar datos, modelo, explicación y decisión humana.
3. Registrar fuente, hora y versión del modelo.
4. No almacenar secretos ni credenciales.
5. Diseñar para auditoría y reproducibilidad.
6. Incluir uso responsable en cada interfaz.
7. Hacer que las dependencias apunten hacia el dominio.

## Estado actual

El MVP usa `DemoSportsDataAdapter`, un modelo base explicable y casos de uso independientes. Antes de usar datos reales se debe completar T011, establecer términos del proveedor, validar calidad temporal y realizar backtesting.

## Próxima sesión recomendada

1. Elegir una liga y proveedor de datos permitido.
2. Implementar un adaptador real detrás de `SportsDataPort`.
3. Definir esquema de snapshots históricos.
4. Implementar backtesting sin fuga de información.
5. Calibrar probabilidades y reportar Brier score, log loss y ROI simulado con advertencias.
