# 08 · Despliegue en Azure, GitHub Actions y operación

[← README](../README.md) · [Arquitectura](01_ARQUITECTURA.md) · [Aplicación pública](12_APLICACION_WEB_PUBLICA.md) · [Bitácora](13_BITACORA_DESPLIEGUE_2026.md)

## Aplicación publicada

**[Abrir AIRE STUDIO ↗](https://web-app-calidad-d4fvd7f3byc9dtfh.mexicocentral-01.azurewebsites.net/)**  
**[Comprobar FastAPI `/health`](https://web-app-calidad-d4fvd7f3byc9dtfh.mexicocentral-01.azurewebsites.net/health)**

**Estado documentado al 16/10/2026:** GitHub Actions completó el despliegue a Azure y la Web App apareció en estado `Running`. La respuesta pública de `/health`, la carga del HTML y las invocaciones al endpoint son pruebas posteriores y deben ejecutarse para confirmar operación completa.

## Arquitectura de despliegue

1. **Databricks:** NB01–NB04 ejecutaron la simulación 2020; MLflow/Unity Catalog conserva las versiones y Databricks Model Serving recibe inferencias individuales.
2. **GitHub:** el código (`main.py`, `static/index.html`, `data/` y dependencias) se mantiene en `main` del repositorio [`Fred-0606/MLOPS_Calidad_aire`](https://github.com/Fred-0606/MLOPS_Calidad_aire).
3. **GitHub Actions:** un workflow de pruebas verifica la API; otro hace build y publicación de la Web App mediante OIDC.
4. **Azure App Service:** FastAPI sirve el HTML y los datos históricos empaquetados, y actúa como intermediario seguro hacia Model Serving.

**Los notebooks y el entrenamiento no se ejecutan en Azure.** El sitio web tampoco inicia Jobs; su botón de reproducción despliega resultados históricos ya calculados.

## Recursos reales de Azure

| Recurso / propiedad | Valor |
| --- | --- |
| Suscripción | Azure for Students (según portal) |
| Aplicación | `Web-App-Calidad` |
| Grupo de recursos de la aplicación | `Resource_calidad_aire` |
| App Service Plan | `ASP-RecursosStudents-b107` |
| Grupo del plan | `Recursos_students` |
| SKU observado | Free F1 |
| Ubicación | Mexico Central |
| Plataforma | Linux, publicación de código Python |
| Identidad OIDC | `oidc-msi-9e69` (User-assigned managed identity) |
| Rol verificado para la identidad | `Website Contributor` sobre `Web-App-Calidad` |
| Workflow de despliegue | `.github/workflows/main_web-app-calidad.yml` |
| Rama | `main` |
| Dominio público | [https://web-app-calidad-d4fvd7f3byc9dtfh.mexicocentral-01.azurewebsites.net/](https://web-app-calidad-d4fvd7f3byc9dtfh.mexicocentral-01.azurewebsites.net/) |

El plan F1 era compartido con otra aplicación denominada `mlops-students`; no mover, detener ni eliminarla por un fallo de la Web App nueva.

## Configuración de FastAPI

En **App Services → Web-App-Calidad → Settings → Configuration → Stack Settings**, configura el *Startup Command*:

```bash
gunicorn -w 2 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8000 main:app
```

En **Settings → Environment variables → App settings**, comprueba las variables:

| Nombre | Contenido esperado | Precaución |
| --- | --- | --- |
| `DATABRICKS_HOST` | Host HTTPS del workspace Databricks | No incluir `/serving-endpoints/...` |
| `DATABRICKS_ENDPOINT` | Nombre exacto del endpoint | Revisar qué versión sirve actualmente |
| `DATABRICKS_TOKEN` | Credencial válida de consulta | **Secreto, nunca en HTML o GitHub** |
| `SCM_DO_BUILD_DURING_DEPLOYMENT` | `true` | Permite instalación de dependencias mediante el build de App Service |

Para una aplicación accesible públicamente, adopta autenticación, límites de invocación y presupuestos: el endpoint de Databricks puede generar cargos. En producción se prefiere principal de servicio, OAuth y custodia de secretos.

## GitHub Actions: cómo comprobar la publicación

En GitHub, entra a **Actions** y distingue dos workflows:

- `Pruebas de la API`: valida Python y respuestas HTTP locales de prueba; **no publica en Azure**.
- `Build and deploy Python app to Azure Web App - Web-App-Calidad`: contiene los Jobs **build** y **deploy**. Ejecuta `azure/login@v2` mediante OIDC y `azure/webapps-deploy@v3` con destino `Web-App-Calidad`.

El archivo de despliegue se encuentra en `.github/workflows/main_web-app-calidad.yml`. Utiliza secretos de GitHub para `client-id`, `tenant-id` y `subscription-id`. No expongas sus valores en capturas ni commits; no confundas esos identificadores con `DATABRICKS_TOKEN`, que pertenece a **App settings** de Azure.

Cuando haya un commit sobre `main`, GitHub Actions podrá publicar nuevamente. El indicador verde significa que los pasos del workflow terminaron bien, **no es una prueba de inferencia real**.

## Verificación después de un despliegue

1. Comprueba que Azure → **Web-App-Calidad → Overview → Status** muestre `Running`.
2. Abre [el dominio público](https://web-app-calidad-d4fvd7f3byc9dtfh.mexicocentral-01.azurewebsites.net/). Debe cargar la interfaz AIRE STUDIO.
3. Abre [el endpoint `/health`](https://web-app-calidad-d4fvd7f3byc9dtfh.mexicocentral-01.azurewebsites.net/health). Debe devolver HTTP 200 y `{"status":"ok"}`.
4. Selecciona un mes, reproduce la secuencia y consulta una hora con histórico disponible.
5. Abre [`/api/history/dates?station=santa_cruz`](https://web-app-calidad-d4fvd7f3byc9dtfh.mexicocentral-01.azurewebsites.net/api/history/dates?station=santa_cruz) y confirma que devuelve fechas.
6. **Con autorización**, realiza una nueva inferencia y verifica `current_prediction` numérico. En Databricks confirma qué modelo y versión están realmente publicados y que Serving esté `READY`.
7. Anota fecha, commit, código HTTP y versión real del endpoint en el registro de validaciones (documento 10).

## Diagnóstico de las incidencias de octubre de 2026

| Mensaje | Qué ocurrió | Dónde revisar |
| --- | --- | --- |
| `assert 'API_URL' in response.text` | Test viejo para el HTML original | `tests/test_api.py`; la prueba ahora comprueba HTML y `Content-Type` |
| `No subscriptions found` | Falla de login OIDC | Secretos de GitHub, roles IAM, identidad y suscripción |
| `AADSTS700016` | El client ID no se encontraba en el tenant informado | Comprobar coincidencia entre ID de identidad, tenant y secretos del workflow |
| `Site Disabled (CODE: 403)` en OneDeploy | Azure tenía el sitio en `Quota exceeded` | Azure → Overview → Status; App Service plan → Quotas |
| `Quota exceeded` en F1 | App bloqueada, pese a contadores de consumo en cero durante la revisión | Revisar cuotas, estado y restablecimiento; no diagnosticar de inmediato como error de Python |
| `Running` pero falla `/health` | La Web App existe; FastAPI puede no arrancar | Startup Command, dependencias, Log stream y rutas de archivos |
| Histórico funciona, nueva inferencia falla | Error de Databricks o configuración | Variables `DATABRICKS_*`, contrato `dataframe_split`, permisos CAN QUERY y estado Serving |

El error por cuota se recuperó posteriormente y la publicación terminó en verde. No se identificó con certeza el origen del estado `Quota exceeded`; evitar atribuirlo sin evidencia a la otra aplicación compartida.

## Costos y mantenimiento

- App Service F1 está sujeto a cuotas y puede detener el sitio temporalmente; el uso de Databricks Model Serving se factura/limita por separado según su configuración.
- Vigila el estado de la Web App, errores 5xx, el presupuesto Azure y el consumo de Serving.
- Si cambias solo HTML/CSS/JS, actualiza `static/index.html` y comprueba la nueva compilación. Si cambia el backend, actualiza pruebas y contratos.
- El histórico es **estático**: nuevos resultados Databricks no aparecen hasta regenerar `data/historical_features_2020.json.gz` y los resúmenes incrustados en `static/index.html`.
- No elimines `Resource_calidad_aire` o `Recursos_students` sin revisar todos sus recursos; el segundo grupo contiene también recursos del proyecto anterior.

[Volver al README](../README.md)
