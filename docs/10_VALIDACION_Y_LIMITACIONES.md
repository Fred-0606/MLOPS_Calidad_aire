# 10 · Validación, trazabilidad y límites del proyecto

[← README](../README.md) · [Arquitectura](01_ARQUITECTURA.md) · [Resultados](05_RESULTADOS_2020.md)

## Matriz de verificación

| Afirmación | Evidencia disponible | Estado / alcance |
| --- | --- | --- |
| Se procesaron los ocho meses | Tabla `control` con 4 eventos por mes | **Verificado** en la consulta compartida |
| Se generaron predicciones por estación y mes | `gold_predictions` exportada | **Verificado:** 11.564 filas, 19 sin objetivo |
| NB04 registró errores, drift y motivos | `gold_monitoring`, ocho JSON | **Verificado** |
| El calendario contiene horas reconstruibles | `historical_features_2020.json.gz` | **Verificado:** 11.089 entradas válidas |
| FastAPI dispone de rutas históricas y proxy Serving | `main.py` versión interactiva | **Comprobado en código**; requiere instalar archivos completos |
| La UI muestra los históricos | `static/index.html` con resumen incorporado | **Funcionalidad implementada**, no actualiza datos en vivo |
| Nueva inferencia consulta Databricks | `/api/history/predict` | **Implementada en código; prueba real depende del endpoint, credencial y versión servida** |
| El endpoint está usando la v8 | No basta el historial de MLflow | **No verificado**: revisar Serving → endpoint → served entities |
| El botón de la web inicia Jobs de Databricks | No hay rutas para Jobs en el backend actual | **No implementado** |
| Mejora causal de versiones | Comparación mensual y gate temporal | **No demostrada** únicamente con el MAE de meses diferentes |

## Riesgos metodológicos por reconocer

### 1. Retrospectividad

Aunque el procesamiento se hace en orden y el modelo se evalúa con un mes todavía no entrenado, toda la fuente es histórica y accesible al ejecutar la práctica. Se trata de una **simulación retrospectiva** con controles de filtrado temporal. No equivale a operación continua con mediciones que vayan llegando en tiempo real.

### 2. Comparaciones entre meses diferentes

Cambios de MAE pueden explicarse por cambios de nivel, meteorología, representatividad y disponibilidad de datos, además de cambios de modelo. Para medir la diferencia entre versiones sobre las **mismas** observaciones, consultar los registros de `gate` y diseñar una evaluación común independiente.

### 3. Zona horaria de origen

NB01 interpreta `tiempo` sin convertir explícitamente el huso de la fuente. El CSV exportado y los selectores web exponen sufijos `Z`. El proyecto debe aclarar si los sellos representan UTC verdadero, hora local originalmente registrada o una convención impuesta en el proceso de exportación. De momento no debe utilizarse esa codificación para comparaciones regulatorias por hora local.

### 4. Datos faltantes y cobertura

No se imputan faltantes. El MAE mensual solo se calcula sobre entradas con valor objetivo conocido. El número de predicciones puede ser mayor que el número de errores comparables. La consulta interactiva es todavía más restrictiva porque reconstruye un historial completo para las 13 entradas. Es indispensable acompañar la precisión con cobertura.

### 5. Drift y significación estadística

PSI es una heurística; el umbral 0,20 no procede de una validación estadística universal. Las series horarias están autocorrelacionadas y la prueba KS puede sobreestimar evidencia si se interpreta su p-valor bajo independencia. El drift puede coexistir con buen error; su presencia no implica que un retraining mejorará el modelo.

### 6. Versión servida y seguridad

Mover alias `champion` no garantiza que un endpoint activo se actualice. `main.py` actual no devuelve el ID de versión servida y no incluye autenticación para consultas públicas. Antes de publicar a terceros, comprobar configuración de Serving, permisos, tasa de invocaciones y límites de gasto. La clave de Databricks no debe publicarse ni en documentos ni en el frontend.

## Pruebas recomendadas (checklist)

- [ ] Ocho meses `2020-01`...`2020-08` aparecen con cuatro eventos (`prepare`, `train`, `promotion`, `monitor`).
- [ ] `gold_monitoring` tiene ocho registros y `gold_predictions` contiene ambos nombres de estación.
- [ ] La suma de registros exportados es 11.564 y existen exactamente 19 etiquetas futuras nulas.
- [ ] La página abre y presenta el histórico aunque el endpoint esté apagado.
- [ ] `/health` responde 200 sin afirmar que el modelo esté disponible.
- [ ] Las rutas `/api/history/dates`, `/hours` y `/result` rechazan fechas sin vector válido.
- [ ] Una consulta válida por `/api/history/predict` devuelve `current_prediction` numérico.
- [ ] El endpoint Serving está READY; se ha documentado su **versión exacta** y el JSON que acepta.
- [ ] Se comprueba que no hay secretos en el repositorio, el HTML o los logs.
- [ ] Antes de permitir acceso público se implementan autenticación, rate limiting, presupuesto y auditoría.
- [ ] Se documenta explícitamente el huso horario confirmado de la fuente.

## Futuras ampliaciones separadas del alcance actual

- API para iniciar y consultar Jobs con estado persistente, autenticación y bloqueo de concurrencia.
- Fuente de datos en tiempo real; cómputo de lags y medias en una infraestructura de características actualizable.
- Observabilidad operativa del endpoint, con medición de latencia, errores e identificación de versión servida.
- Comparación A/B o *shadow* de dos modelos sobre un mismo período sin contaminar el flujo de decisiones.
- Pruebas automatizadas CI/CD, validación de esquemas, mantenimiento de documentación y alertas de presupuesto.

[Volver al índice](../README.md)
