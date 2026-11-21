# Arquitectura

```text
Dashboard HTML
      |
      v
 FastAPI REST  ---> Health / OpenAPI
      |
      v
 PredictionService
      |
      +--> SportsDataProvider <--- DemoSportsDataProvider
      |
      +--> ExplainableBaselineModel
      |
      +--> Metrics: implied probability, edge, expected value
```

## Capas

### Dominio

Contiene `Fixture`, `TeamStrength`, `Odds` y `Prediction`. No conoce HTTP ni proveedores concretos.

### Proveedores

`SportsDataProvider` es un puerto. El proveedor demo permite una ejecución estable para clase. Un adaptador real debe devolver la misma forma de datos y reportar la hora de actualización.

### Servicios

`PredictionEngine` calcula probabilidades a partir de fuerza relativa, forma y localía. La salida incluye factores, datos faltantes, confianza y versión del modelo.

### API

FastAPI serializa modelos, valida parámetros y publica OpenAPI en `/docs`. No existe endpoint de colocación de apuestas.

### Interfaz

El dashboard consume la API, muestra las tres probabilidades, una señal de valor orientativa y las advertencias. La decisión sigue siendo humana.

## Flujo de una predicción

1. Solicitar un fixture.
2. Cargar equipos, forma y cuotas.
3. Convertir fuerza diferencial en puntuaciones.
4. Normalizar a probabilidades 1X2.
5. Calcular probabilidad implícita y edge.
6. Generar explicación y confianza.
7. Entregar respuesta auditable.
