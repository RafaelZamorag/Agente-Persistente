# Operación y recomendaciones

## Ejecución local

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e '.[dev]'
uvicorn app.main:app --reload
```

Abrir `http://127.0.0.1:8000` y la documentación en `http://127.0.0.1:8000/docs`.

## Variables

Copiar `.env.example` como `.env`. El MVP no necesita credenciales.

## Antes de datos reales

- Verificar licencia, límites y atribución del proveedor.
- Guardar hora de captura de cuotas y eventos.
- Evitar mezclar información posterior al inicio del partido.
- Versionar transformaciones y modelos.
- Hacer backtesting temporal, nunca una partición aleatoria ingenua.
- Reportar calibración, Brier score y log loss, además de cualquier ROI simulado.

## Recomendaciones para la exposición

1. Explicar que una probabilidad no es una garantía.
2. Mostrar la diferencia entre cuota decimal y probabilidad implícita.
3. Enseñar cómo cambia el resultado al variar la fuerza o la cuota.
4. Presentar el modo demo como una decisión de reproducibilidad.
5. Mostrar las tareas pendientes: datos reales, backtesting y calibración.

## Límites éticos

Este sistema es educativo y analítico. No debe incentivar apuestas compulsivas, perseguir pérdidas ni automatizar decisiones financieras. Si se conecta a una interfaz real, debe mantenerse en modo solo lectura y exigir confirmación humana explícita.
