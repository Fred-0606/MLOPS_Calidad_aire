# Plantilla general Databricks → GitHub → Azure App Service

API FastAPI que reenvía un JSON compatible al endpoint de Model Serving de Databricks.
No contiene datos de entrenamiento ni presupone nombres de variables.

## Prueba local en Windows (PowerShell)

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
$env:DATABRICKS_HOST='TU_HOST_DATABRICKS'
$env:DATABRICKS_ENDPOINT='TU_ENDPOINT'
$env:DATABRICKS_TOKEN='TU_TOKEN'
python -m uvicorn main:app --reload
```

Abrir http://127.0.0.1:8000/health y http://127.0.0.1:8000/.

## Azure App Service

Crear Web App Linux con Python 3.11 (Publish: Code). En Environment variables / App settings:
- `DATABRICKS_HOST`: URL base HTTPS (sin barra final).
- `DATABRICKS_ENDPOINT`: nombre del endpoint de Databricks.
- `DATABRICKS_TOKEN`: credencial de Databricks **solo en el servidor**.
- `SCM_DO_BUILD_DURING_DEPLOYMENT`: `true` (cuando corresponda a la vía de publicación).

Startup Command para Python <=3.13:
`gunicorn -w 2 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8000 main:app`

Conectar el repositorio desde Deployment Center > GitHub > GitHub Actions;
preferir autenticación de identidad administrada. Ver instructivo HTML.

## Adaptación a otros modelos

Cambiar el contenido de `static/index.html` para que sus campos correspondan
exactamente al esquema que espera el Serving Endpoint. El backend acepta un
objeto JSON y lo retransmite sin traducir ni reordenar columnas.

## Seguridad

Una API pública puede permitir llamadas no autorizadas a Databricks y generar costos.
Esta plantilla es para laboratorio. Antes de exponerla a terceros, agregar
identidad/autenticación, permisos mínimos, límites de petición, control de costo,
monitorización y protección de datos. Preferir OAuth M2M con principal de servicio
para producción y Key Vault / identidades administradas, donde aplique.
