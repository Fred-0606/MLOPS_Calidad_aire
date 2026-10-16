# 02 · Metodología MLOps y protocolo temporal

[← README](../README.md) · [Arquitectura](01_ARQUITECTURA.md) · [Datos →](03_DATOS_Y_VARIABLES.md)

## Pregunta y tipo de aprendizaje

A partir de observaciones disponibles hasta la hora **t**, predecir la concentración numérica de **PM2.5 en t+1 hora**, por estación. Es un problema de **regresión supervisada**; no se predicen categorías ni se estima un índice AQI.

La simulación recorre 2020-01 → 2020-08. El mes a evaluar no puede intervenir en el entrenamiento o la selección del champion que predice ese mismo mes.

## Pipeline por mes

| Orden | Notebook | Operaciones y salida persistente |
| --- | --- | --- |
| 1 | `NB01_Aire_API_Datos_PSI_Anomalia` | Descarga Socrata con paginación; interpreta fechas y lecturas; filtra datos publicados hasta el fin del mes; crea bronce, plata, manifiesto y evento `prepare` |
| 2 | `NB02_Aire_Entrenamiento_PSI_Anomalia` | Consulta `retrain_next` anterior o `force_train`; si procede, entrena candidatos en cortes históricos, selecciona familia y registra `challenger`; evento `train`, que puede quedar `SKIPPED` |
| 3 | `NB03_Aire_CICD_PSI_Anomalia` | Evalúa challenger y champion sobre una **puerta temporal común** (gate), aplica criterios por estación y registra `champion_version`; evento `promotion`, que no equivale necesariamente a promoción efectiva |
| 4 | `NB04_Aire_Monitoreo_PSI_Anomalia` | Usa versión de champion fija para predecir el mes; escribe `gold_predictions`, MAE, RMSE, PSI/KS, reglas `retrain_next` y `gold_monitoring`; evento `monitor` |

**Nota de terminología:** NB03 se denomina `CICD` en el notebook, pero su función visible en el código es la **evaluación y promoción del modelo en MLflow**. El despliegue continuo de **la aplicación web** pertenece a GitHub Actions; son mecanismos distintos.

## División temporal exacta para mes M

Si `START` es el primer día del mes simulado:

```text
Pasado más antiguo     START −14 días      START −7 días           START        Mes M
        ├─ TRAIN ─────────┤─ SELECTION ───────┤─ GATE ─────────────────┤─ MONITOR ───>
        Targets conocidos antes de cada frontera temporal         Solo se predice
```

En el código:

- `train`: `target_time < START - 14 días`.
- `selection`: `feature_time >= START - 14 días` y `target_time < START - 7 días`.
- `gate`: `feature_time >= START - 7 días` y `target_time < START`.
- Mes M: se genera predicción con el modelo escogido antes de M; su resultado t+1 solo se usa para evaluar cuando ya es conocido.

La selección de hiperparámetros/familia se hace sobre `selection`. La decisión de reemplazo del champion se toma sobre `gate`, separada del bloque utilizado para escoger el candidato. Los cortes son cronológicos, **no** aleatorios.

## Familias de modelos evaluadas

1. **Persistence:** predice que la hora siguiente conserva el valor actual: `ŷ[t+1]=PM2.5[t]`. Es una referencia obligatoria; incluso puede ser champion si otra familia no demuestra ventaja.
2. **Ridge:** regresión lineal regularizada con `StandardScaler` ajustado únicamente con el conjunto de entrenamiento.
3. **RandomForestRegressor:** 80 árboles, `max_depth=12`, `min_samples_leaf=8`, semilla 42.
4. **HistGradientBoostingRegressor:** 120 iteraciones, `max_leaf_nodes=15`, learning rate 0,07; sin validación interna aleatoria.

Estos hiperparámetros son decisiones didácticas registradas, **no** resultado de una optimización exhaustiva. MLflow registra métricas, artefactos, firma, parámetros y entorno; las versiones se registran en Unity Catalog.

## Política mes a mes

1. **Enero:** entrenamiento inicial obligatorio; NB03 define el primer champion.
2. **Febrero y siguientes:** NB02 entrena si `force_train=true` o si NB04 del mes anterior dejó `retrain_next=true`; de lo contrario registra `SKIPPED`.
3. NB03 compara con el champion existente; puede **rechazar** un challenger y conservar la versión vigente.
4. NB04 evalúa sin reentrenar retroactivamente el mes actual, y publica la decisión aplicable al siguiente mes.
5. El siguiente mes solo comienza cuando existe el evento `monitor` del anterior. Si el mes ya está cerrado, el notebook reutiliza su registro y sale sin repetir trabajo.

Ejemplo real: marzo reportó PSI de anomalía elevado y peor MAE que la persistencia; esto solicitó entrenamiento para abril. La predicción de marzo permanece atribuida al champion v1; abril fue servido históricamente por el champion v5.

## Reproducibilidad y condiciones

- `batch_month` es una etiqueta de simulación; **no** la fecha en la que se ejecutó el notebook (la ejecución del experimento fue en octubre de 2026).
- `catalog`, `schema`, `batch_month`, `force_train`, `experiment_path` deben ser coherentes entre las cuatro tareas.
- Reiniciar una simulación **no** significa borrar `control`: debe usarse un esquema nuevo o una estrategia formal de restauración; de otro modo los eventos ya cerrados son reutilizados.
- Se fijan versiones Delta (`silver_version`) y versiones MLflow para que las decisiones de un mes puedan reconstruirse posteriormente.
- Existe descarga de una fuente histórica completa, pero NB01 libera las filas `feature_time < END`. Es una **simulación cronológica retrospectiva**, no un flujo de datos en vivo.

[Volver al índice](../README.md)
