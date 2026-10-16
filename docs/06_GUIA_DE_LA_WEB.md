# 06 · Guía de lectura y uso de AIRE STUDIO

[← README](../README.md) · [Resultados](05_RESULTADOS_2020.md) · [API →](07_API_Y_CONTRATOS.md)

## ¿Qué se ve en la aplicación?

La página AIRE STUDIO 2026 tiene dos usos complementarios:

1. **Exploración de la simulación cerrada** de enero–agosto de 2020: reproduce en la interfaz resultados de predicciones, métricas, alertas y decisiones calculadas anteriormente en Databricks. Los botones de reproducción/mes **no vuelven a ejecutar los notebooks**.
2. **Consulta individual histórica:** el usuario elige estación, fecha y hora válidas; ve lo que predijo el champion original y el resultado que se observó una hora después. Si pulsa consultar modelo actual, FastAPI envía **las mismas características históricas** al endpoint de Databricks configurado y recupera una nueva predicción.

## Interpretación de las tres cifras de una consulta

| Indicador | Qué responde | Procedencia |
| --- | --- | --- |
| **Predicción histórica almacenada** | «¿Cuánto predijo en ese momento el champion utilizado para ese mes?» | Exportación de `gold_predictions` y archivo comprimido de la web |
| **PM2.5 observado una hora después** | «¿Qué valor de PM2.5 se registró efectivamente en la hora objetivo?» | `target_pm25` histórico |
| **Nueva inferencia del Serving endpoint** | «¿Qué predice ahora el modelo **actualmente desplegado** en Databricks usando aquel vector de 13 entradas?» | `POST /api/history/predict`, que llama a Model Serving |

**Ejemplo ilustrativo de lectura:** si a las 14:00 de un día el champion histórico predijo **34,6 µg/m³** para las 15:00, el sensor midió **34,0 µg/m³** y el endpoint devolvió **33,5 µg/m³**, los errores absolutos respectivos son **0,6** y **0,5 µg/m³**. **Las cifras de este ejemplo son ilustrativas, no una comprobación de inferencia al endpoint.**

La nueva inferencia **no** es un pronóstico de 2026. Es una consulta **retrospectiva** de datos de 2020 al modelo desplegado hoy. Si ese modelo se entrenó más tarde, el resultado no constituye una evaluación fuera de muestra equivalente a la predicción histórica original.

## Uso del calendario

1. Selecciona `Santa Cruz` o `San Francisco`.
2. Escoge mes, día y hora entre los registros disponibles para esa estación.
3. Consulta la predicción histórica almacenada y el valor observado, cuando exista.
4. Solicita la nueva inferencia **solo si deseas comparar** y el Serving endpoint está `READY`.
5. Observa la versión histórica indicada por la aplicación. Para la versión del endpoint actual, revisa Databricks Serving; el backend no devuelve automáticamente su identificador de versión.

El calendario **no filtra días hábiles**: los sensores pueden registrar sábados, domingos y festivos. Filtra horas con las 13 variables reconstruibles sin rellenar faltantes. El archivo histórico contiene **11.089** combinaciones estación–hora válidas, menos que las **11.564** predicciones de la simulación.

## Cómo leer el panel mensual

- **MAE:** promedio de `|predicción − observación|`; menor es mejor, comparando condiciones equivalentes.
- **RMSE:** error cuadrático medio con raíz; penaliza fallos grandes.
- **Drift:** indica que una regla de cambio de distribución se activó; **no implica automáticamente error alto**.
- **PSI de anomalía:** indicador de cambio respecto al histórico por estación; el umbral del proyecto es **0,20**.
- **Reentrenamiento solicitado:** NB04 pide que el siguiente mes considere entrenamiento; no significa que en ese mismo mes se haya cambiado de champion.
- **Champion vN:** versión exacta utilizada al generar las predicciones del mes. La versión puede persistir durante varios meses.

### Ejemplo del proceso completo (marzo → abril)

1. **Marzo:** se monitorea el champion v1; hay drift de anomalía y MAE mayor que persistencia.
2. **Cierre de marzo:** `retrain_next=true` por tres razones.
3. **Comienzo de abril:** NB02 entrena, NB03 aplica su gate temporal y selecciona la versión correspondiente.
4. **Abril:** NB04 predice con v5 y registra las métricas del mes.

Marzo no se vuelve a predecir retroactivamente con v5 dentro de la simulación; una eventual **nueva inferencia** solicitada desde la web es una operación distinta.

## Casos de error y su significado

| Mensaje/situación | Interpretación o comprobación |
| --- | --- |
| El calendario no ofrece una hora | Faltan variables históricas completas para esa estación/hora |
| La parte histórica funciona, pero «Consultar modelo» falla | Problema de endpoint, configuración, permisos o forma de respuesta; no del archivo histórico necesariamente |
| `503` en `/api/history/*` | Falta o no puede leerse `data/historical_features_2020.json.gz` |
| `503` en nueva inferencia | Faltan `DATABRICKS_*` o URL inválida |
| `502` en nueva inferencia | Error devuelto por Databricks o respuesta que no coincide con el contrato esperado |
| `504` | Consulta a Databricks agotó su tiempo de espera |
| Histórica ≠ nueva inferencia | Pueden usar distintas versiones; no constituye por sí solo un defecto |

## Consideraciones al presentar el proyecto

- Usa el término **concentración estimada de PM2.5 una hora adelante**, no «calidad del aire futura real» ni «índice AQI».
- Explica que la visualización histórica es un **replay** de datos ya calculados; no una ingesta o entrenamiento en tiempo real.
- No interpretes el umbral PSI como criterio sanitario: es una regla del monitoreo del modelo.
- Ten presente que el HTML presenta sellos como UTC aunque la ingesta no documenta una conversión explícita desde la zona original. Valida ese detalle antes de comparar con registros locales.

[Volver al índice](../README.md)
