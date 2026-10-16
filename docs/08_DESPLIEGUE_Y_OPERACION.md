# 08 · Despliegue, CI/CD y operación

[← README](../README.md) · [API](07_API_Y_CONTRATOS.md)

## Dos despliegues diferentes

- **Software**: se versiona en GitHub y se publica en **Azure App Service** mediante GitHub Actions; incluye FastAPI, HTML, artefacto histórico y documentación.
- **Modelo**: vive en MLflow/Unity Catalog; su publicación o actualización en **Databricks Model Serving** es una operación independiente. Que GitHub Actions aparezca en verde no demuestra que el endpoint sirva el último champion ni que la inferencia funcione.

## Preparación antes de subir el repositorio

Estructura mínima:

```text
repo/
├── README.md
├── main.py
├── requirements.txt
├── .gitignore
├── static/index.html
├── data/historical_features_2020.json.gz
└── docs/
    ├── 01_ARQUITECTURA.md
    ├── ... otros documentos ...
    └── assets/aire-studio-vista-previa.png
```

Puedes conservar archivos JSON de ejemplo **si están libres de datos sensibles**. No es necesario subir los CSV fuente completos si el sitio consume el JSON gzip ya generado. Si se publican notebooks, hacerlo en una carpeta `notebooks/` y mantenerlos sincronizados con Databricks; subirlos no ejecuta Jobs automáticamente.

## Ejecución local (Windows)

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m uvicorn main:app --reload
```

Prueba el HTML, `/health`, el calendario y un registro histórico antes de utilizar un token. Para consultar Databricks configura las tres variables de entorno de manera **local y temporal**; usa un método seguro para introducir el token. En producción utiliza identidad de servicio/OAuth cuando sea viable, con permisos mínimos.

## Infraestructura Azure de la guía

| Recurso Azure | Necesario | Uso |
| --- | --- | --- |
| Resource Group | Sí | Agrupar recursos de la práctica |
| App Service Plan | Sí | Capacidad y costo |
| Web App Linux + Python | Sí | Ejecutar `main.py` y servir `static/index.html` |
| App settings / Environment variables | Sí | Guardar conexión a Databricks y configuración de build |
| Application Insights | Recomendado | Observabilidad de la API |
| Key Vault | Recomendado en producción | Custodia de secretos |
| Storage Static Website | No, en esta arquitectura | Web y API comparten la Web App |
| Azure Container Apps / `Microsoft.App` | No | Se usa App Service con proveedor `Microsoft.Web` |

El comando de arranque documentado por la guía del proyecto (con versión Python compatible) es:

```text
gunicorn -w 2 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8000 main:app
```

Comprueba que las dependencias incluyan `gunicorn` y `uvicorn`. Configura estas App settings en Azure:

```text
DATABRICKS_HOST = URL base HTTPS
DATABRICKS_ENDPOINT = nombre del Serving endpoint
DATABRICKS_TOKEN = credencial segura de consulta
SCM_DO_BUILD_DURING_DEPLOYMENT = true
```

El token se configura **en Azure**, no en `README.md` ni en secrets del frontend. En una instalación productiva, se recomienda un principal de servicio, OAuth y Key Vault cuando la configuración del entorno lo permita.

## GitHub Actions

En Azure App Service → **Deployment Center**:

1. Selecciona **GitHub** y la rama que publicará (por ejemplo, `main`).
2. Utiliza el workflow generado por Azure mediante autenticación federada OIDC/identidad administrada cuando se permita.
3. Confirma que `.github/workflows/` tenga un flujo de **despliegue**, diferente de cualquier workflow de **pruebas**.
4. Ejecuta la publicación y revisa su registro en GitHub Actions.
5. Desde Azure Web App → **Overview**, copia el valor real de **Default domain**. No inventes el host a partir del nombre de la aplicación.
6. Verifica `/health`, `/`, `/api/history/dates`, `/api/history/result` y, finalmente, `/api/history/predict` con el endpoint operativo.

## Diagnóstico rápido

| Síntoma | Revisar primero |
| --- | --- |
| Error 404 en `/` | Carpeta `static` y `index.html` en la raíz correcta de ejecución |
| `503` en calendario | Carpeta `data`, nombre exacto del archivo `.json.gz` y permisos |
| `/health` funciona pero falla inferencia | App settings, token, permisos `CAN QUERY`, Serving endpoint READY y contrato JSON |
| GitHub Actions está verde pero no responde | Arranque Gunicorn y logs de Azure; workflow correcto ≠ app funcionando |
| App Service Plan genera costo | SKU/plan, horas en servicio y consumo de Databricks por separado |
| `Microsoft.App` en estado Registering | No es necesario para esta ruta con **App Service**, que usa `Microsoft.Web` |
| La UI no refleja nuevos resultados Databricks | Los archivos históricos son estáticos; volver a exportar y desplegar |

## Operación responsable

- Deshabilita accesos anónimos para inferencia antes de exposición pública; aplica rate limiting y alertas de presupuesto.
- Registra versión de API, versión de modelo, tiempos de respuesta, errores y fecha de generación de los artefactos.
- No hagas `Delete resource group` sin revisar los recursos del grupo; el Serving endpoint puede seguir cobrando aunque se elimine Azure App Service.
- Una visualización histórica de 2020 **no es** un predictor operativo de 2026. Conectar datos en vivo y hacer monitoreo continuo exige integrar una fuente actual, controlar tiempo de evento, servicio y reentrenamiento en producción.

[Volver al índice](../README.md)
