# 07 · API FastAPI y contratos de entrada/salida

[← README](../README.md) · [Manual web](06_GUIA_DE_LA_WEB.md)

## URL de producción

**Aplicación:** [AIRE STUDIO](https://web-app-calidad-d4fvd7f3byc9dtfh.mexicocentral-01.azurewebsites.net/)  
**Prueba de servidor:** [`/health`](https://web-app-calidad-d4fvd7f3byc9dtfh.mexicocentral-01.azurewebsites.net/health)  
**Swagger / OpenAPI:** [`/docs`](https://web-app-calidad-d4fvd7f3byc9dtfh.mexicocentral-01.azurewebsites.net/docs)

Estos son los enlaces del dominio registrado en Azure. El cierre del workflow de GitHub Actions fue confirmado; la respuesta HTTP real y la inferencia deben verificarse independientemente.

## Componentes presentes en `main.py`

`main.py` sirve el HTML, consulta el historial comprimido y delega las inferencias en Databricks. **No entrena, no monitorea nuevas distribuciones y no inicia Jobs**. La configuración de Databricks se obtiene de variables de entorno del proceso de Azure.

| Método y ruta | Entrada principal | Devuelve / función |
| --- | --- | --- |
| `GET /` | Ninguna | `static/index.html` |
| `GET /health` | Ninguna | `{"status":"ok"}`. Prueba de vida, **no** de Databricks |
| `GET /api/history/dates` | `station=santa_cruz` o `san_francisco` | Fechas disponibles y `timezone` |
| `GET /api/history/hours` | `station`, `date=AAAA-MM-DD` | Horas válidas de esa fecha para la estación |
| `GET /api/history/result` | `station`, `feature_time` | Histórico, observado t+1 y versión histórica |
| `POST /api/history/predict` | JSON: `station`, `feature_time` | Histórico + una nueva inferencia de Databricks |
| `POST /predict` | JSON en formato aceptado por Databricks | Reenvía el cuerpo sin transformar al Serving endpoint |

### Ejemplos de prueba local

```http
GET http://127.0.0.1:8000/api/history/dates?station=santa_cruz
GET http://127.0.0.1:8000/api/history/hours?station=santa_cruz&date=2020-03-15
GET http://127.0.0.1:8000/api/history/result?station=santa_cruz&feature_time=2020-03-15T12:00:00Z
```

La última ruta debe consultarse con una hora que figure entre las de `/hours`; de lo contrario puede responder `404`.

```http
POST /api/history/predict
Content-Type: application/json

{
  "station": "santa_cruz",
  "feature_time": "2020-03-15T12:00:00Z"
}
```

La API toma automáticamente el vector histórico de 13 entradas y construye:

```json
{
  "dataframe_split": {
    "columns": [
      "station_code", "pm25", "lag_1", "lag_2", "lag_3",
      "lag_6", "lag_24", "mean_6", "mean_24",
      "hour_sin", "hour_cos", "dow_sin", "dow_cos"
    ],
    "data": [[0.0, 9.9, 12.4, 13.3, 11.6, 9.8, 38.8, 11.6333333333, 12.5458333333, 0.2588190451, 0.9659258263, 0.4338837391, -0.9009688679]]
  }
}
```

Este vector es un **ejemplo extraído de la estructura histórica reconstruida**; no representa automáticamente el registro de las 12:00 del 15 de marzo. Para esa hora, FastAPI recuperará su vector real.

### Respuesta de la nueva inferencia

La implementación **exige** una respuesta JSON de Databricks del tipo:

```json
{"predictions": [12.34]}
```

El número 12.34 es **ficticio**. Si Databricks entrega un esquema diferente, se produce error 502 y debe verificarse la firma/contrato del Serving endpoint. La respuesta pública de `/api/history/predict` incluye `historical_prediction`, `observed_pm25`, `historical_model_version`, `current_prediction` y `source`, más estación y horas.

## Configuración de Databricks

| Variable | Qué almacena | Regla |
| --- | --- | --- |
| `DATABRICKS_HOST` | Dirección HTTPS base del workspace | Ejemplo: `https://adb-...azuredatabricks.net`; sin barra final |
| `DATABRICKS_ENDPOINT` | Nombre exacto de Model Serving | Copiar desde Databricks Serving |
| `DATABRICKS_TOKEN` | Token autorizado para consultar el endpoint | **Solo servidor**, nunca GitHub ni HTML |

La llamada interna utiliza `POST {DATABRICKS_HOST}/serving-endpoints/{DATABRICKS_ENDPOINT}/invocations` con encabezado Bearer. El proceso debe tener permisos de **consulta** sobre el endpoint.

**Versiones:** el backend no consulta la versión del modelo servida por el endpoint. La versión del champion histórico **sí** viene del registro guardado. Si se desea mostrar ambas versiones juntas, se necesita incorporar una operación explícita y autorizada de consulta de la configuración del endpoint, sin deducirla de la versión numéricamente mayor del registro MLflow.

## Seguridad y protección

- El endpoint `/api/history/predict` expuesto sin autenticación permite invocaciones con consumo de cómputo. No publicar a usuarios desconocidos sin autenticación/autorización, límites y presupuestos.
- El HTML nunca debe incluir credenciales. No exponer tokens en respuestas de error o registros.
- `GET /health` no confirma conectividad a Databricks ni una inferencia exitosa.
- Los JSON de ejemplo (`Request_ejemplo.json`, `Answer_ejemplo.json`) son pruebas de contrato; sus nombres de archivo no se envían como parte del JSON.

[Volver al índice](../README.md)
