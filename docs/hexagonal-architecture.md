# Arquitectura hexagonal

La aplicación se organiza alrededor de casos de uso. El centro no conoce FastAPI, archivos, bases de datos ni proveedores concretos. Las dependencias apuntan hacia el núcleo mediante puertos.

```text
                 Adaptador de entrada
                 FastAPI (HTTP)  |  Temporizador (reloj)
                         |
                         v
              Puertos de entrada (inbound)
                         |
                         v
              Casos de uso de aplicación
              /                       \\
             v                         v
  Puerto de salida               Dominio
  SportsDataPort / RunRepositoryPort
  / SchedulerStatePort     PredictionEngine + entidades
             ^
             |
  DemoSportsDataAdapter / API real futura
  FilesystemRunRepository (JSONL)
```

## Reglas

1. `app/domain` contiene reglas de negocio y modelos del problema.
2. `app/application/use_cases` orquesta una acción completa del usuario.
3. `app/application/ports` define contratos, no implementaciones.
4. `app/adapters/inbound` transforma HTTP en llamadas a casos de uso.
5. `app/adapters/outbound` transforma una fuente externa en entidades del dominio.
6. `app/bootstrap.py` es el único lugar que ensambla implementaciones concretas y define el `lifespan` que arranca y detiene el temporizador.
7. `app/main.py` no contiene lógica de negocio; solo crea el contenedor y la aplicación HTTP.
8. Un adaptador de entrada puede ser conducido por una petición (HTTP) o por el reloj (`AgentTimerScheduler`); ambos invocan los mismos puertos inbound.

## Cómo agregar un proveedor real

Se debe crear otro adaptador que implemente `SportsDataPort`, por ejemplo `ApiSportsDataAdapter`. El caso de uso no se modifica. Solo cambia la composición en `build_container`, y se conservan las pruebas usando `FakeSportsData`.

## Beneficio para la exposición

El diseño permite probar la lógica sin red, cambiar FastAPI por otra entrada y sustituir la fuente demo por una API real. Esto reduce acoplamiento, mejora la trazabilidad y hace explícita la inversión de dependencias.
