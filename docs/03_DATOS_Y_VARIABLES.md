# 03 · Datos, diccionario de variables e ingeniería de características

[← README](../README.md) · [Metodología](02_METODOLOGIA_MLOPS.md)

## Fuente y calidad de datos

NB01 descarga datos de la **API Socrata** `https://www.datos.gov.co/d/58ct-h586` mediante paginación. Las columnas de origen usadas para las estaciones son:

| Estación en el proyecto | Columna de la API | `station_code` |
| --- | --- | ---: |
| `santa_cruz` | `est_santa_cruz_gir_n_pm2` | 0.0 |
| `san_francisco` | `est_san_francisco_pm2_5` | 1.0 |

Las lecturas se convierten a numérico; valores negativos se tratan como ausentes, no como concentraciones negativas. El notebook no reemplaza faltantes con cero. Inserta los puntos en una cuadrícula **horaria**, calcula rezagos y promedios y exige entradas finitas para entrenar/inferir.

`bronze_api` conserva datos originales serializados como JSON. `silver_features` reúne las características, identificación de estación, fecha/hora y etiqueta futura. `gold_predictions` y `gold_monitoring` son resultados de uso/interpretación.

## Contrato del modelo (13 entradas)

| Columna | Tipo lógico | Cálculo / explicación |
| --- | --- | --- |
| `station_code` | Numérico | 0 = Santa Cruz; 1 = San Francisco |
| `pm25` | Numérico | Lectura observada en la hora t |
| `lag_1` | Numérico | PM2.5 de t−1 h |
| `lag_2` | Numérico | PM2.5 de t−2 h |
| `lag_3` | Numérico | PM2.5 de t−3 h |
| `lag_6` | Numérico | PM2.5 de t−6 h |
| `lag_24` | Numérico | PM2.5 de t−24 h |
| `mean_6` | Numérico | Promedio de las **seis** lecturas t−5…t (incluye t) |
| `mean_24` | Numérico | Promedio de las **24** lecturas t−23…t (incluye t) |
| `hour_sin` | Numérico | `sin(2π · hora / 24)` |
| `hour_cos` | Numérico | `cos(2π · hora / 24)` |
| `dow_sin` | Numérico | `sin(2π · día_semana / 7)`, lunes = 0 |
| `dow_cos` | Numérico | `cos(2π · día_semana / 7)`, lunes = 0 |

**Objetivo**, que nunca pertenece al vector de entrada: `target_pm25 = PM2.5[t+1]`; `target_time = feature_time + 1 hora`.

Las cuatro variables trigonométricas codifican la naturaleza cíclica de hora y día de semana. La variable de anomalía `pm25 - mean_24` se calcula **para monitorear drift**, pero **no** se añade a las 13 entradas del modelo.

### Ejemplo conceptual

Para una predicción a las 15:00 basada en mediciones conocidas a las 14:00:

- `feature_time = 14:00`, `target_time = 15:00`.
- `pm25` es la concentración a las 14:00; `lag_1` corresponde a las 13:00 y `lag_24` al día anterior a las 14:00.
- `mean_6` usa exclusivamente las lecturas entre 09:00 y 14:00.
- `mean_24` usa las lecturas entre las 15:00 del día anterior y las 14:00 del día actual.
- `target_pm25` es el valor medido a las 15:00; se usa **después**, al calcular errores.

## Estructura de las tablas consumidas

### `gold_predictions`

| Columna | Uso |
| --- | --- |
| `batch` | Mes `AAAA-MM` al que se asignó la predicción |
| `station` | Estación (`santa_cruz`, `san_francisco`) |
| `feature_time` | Fecha/hora hasta la que se conocen las entradas |
| `target_time` | Fecha/hora objetivo, una hora posterior |
| `target_pm25` | Medición objetivo (puede estar ausente) |
| `prediction` | Valor generado por el champion histórico |
| `model_version` | Versión exacta de MLflow utilizada |
| `silver_version` | Versión Delta de las características, creada por NB04 (no necesariamente aparece en la exportación CSV simplificada) |

### `gold_monitoring`

| Columna | Uso |
| --- | --- |
| `batch` | Mes |
| `payload` | JSON con `mae`, `rmse`, `model_version`, `persistence_mae`, `coverage`, `drift_signal`, `retrain_next`, `reasons`, `station_metrics`, `drift`, etc. |
| `updated_at` | Momento en que se registró el reporte, no fecha del mes simulado |

## Exportaciones usadas por la web

- `predicciones_2020.csv`: **11.564 filas** y siete columnas; 19 filas sin `target_pm25`.
- `monitoreo_2020.csv`: ocho filas, una por mes; el campo `payload` contiene el JSON de métricas.
- `data/historical_features_2020.json.gz`: índice comprimido con las 13 entradas reconstruidas, predicción histórica, valor observado y versión. Sus **11.089 horarios válidos** provienen de reconstrucción conservadora que exige 25 mediciones horarias pasadas/completas. No es una copia completa de `silver_features`.
- La página también incorpora un resumen histórico precomputado en el HTML. Por tanto, modificar tablas Databricks **no actualiza automáticamente** la visualización; es necesario regenerar/exportar los artefactos de la web.

### Advertencia sobre tiempo y unidades

El notebook lee `tiempo` sin conversión explícita de zona horaria. El archivo CSV exportado codifica sellos como `2020-...Z` y la página los presenta en **UTC**. **No debe interpretarse ese `Z` como verificación independiente del huso de la fuente.** Antes de un uso operativo, hay que documentar y validar zona horaria, cambios de horario y semántica de fecha.

PM2.5 es una **concentración** (en la página se representa como µg/m³); no es tamaño de partícula ni un índice sanitario. Los promedios de 24 horas utilizados como variables no son equivalentes a la valoración regulatoria diaria sin validar periodo, zona y criterios aplicables.

[Volver al índice](../README.md)
