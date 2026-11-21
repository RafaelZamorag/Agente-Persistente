# Arquitectura hexagonal

```text
Dashboard HTML
      |
      v
Adaptador de entrada HTTP / FastAPI
      |
      v
Puertos inbound
      |
      v
Casos de uso: ListFixtures / PredictFixture
      |
      +--> Puerto outbound: SportsDataPort
      |          ^
      |          |
      |   DemoSportsDataAdapter
      |   (futuro: API real)
      |
      +--> Dominio: PredictionEngine + entidades
```

## Capas

### Dominio

`app/domain` contiene `Fixture`, `Odds`, `Prediction`, `Outcome` y `PredictionEngine`. No conoce HTTP, FastAPI ni proveedores concretos.

### Aplicación

`app/application/use_cases` contiene `ListFixtures` y `PredictFixture`. Cada caso de uso tiene una sola responsabilidad y recibe dependencias mediante puertos. `app/application/ports` define los contratos inbound y outbound.

### Adaptadores

`app/adapters/inbound/http.py` convierte solicitudes HTTP en llamadas a casos de uso y traduce resultados a respuestas JSON. `app/adapters/outbound/demo_sports_data.py` implementa el puerto de datos con fixtures reproducibles.

### Composición

`app/bootstrap.py` es el composition root: crea el proveedor, el motor y los casos de uso. `app/main.py` solo conecta el contenedor con el adaptador HTTP.

## Flujo de una predicción

1. HTTP recibe un `fixture_id`.
2. El adaptador inbound invoca `PredictFixture.execute`.
3. El caso de uso consulta `SportsDataPort`.
4. El caso de uso entrega el fixture a `PredictionEngine`.
5. El dominio calcula probabilidades, edge y explicación.
6. El adaptador devuelve la respuesta auditable.

## Regla de evolución

Para agregar un proveedor real, crear un nuevo adaptador que implemente `SportsDataPort` y modificar únicamente `build_container`. Los casos de uso y el dominio no deben importar SDKs externos.
