# 12 · Aplicación web pública: AIRE STUDIO

[← README](../README.md) · [Guía de uso](06_GUIA_DE_LA_WEB.md) · [Despliegue](08_DESPLIEGUE_Y_OPERACION.md)

## Enlace directo

### **[ABRIR AIRE STUDIO EN AZURE ↗](https://web-app-calidad-d4fvd7f3byc9dtfh.mexicocentral-01.azurewebsites.net/)**

**URL pública:** https://web-app-calidad-d4fvd7f3byc9dtfh.mexicocentral-01.azurewebsites.net/

Este enlace apunta a la Web App `Web-App-Calidad` en **Azure App Service (Linux, Mexico Central)**. La aplicación visualiza los resultados históricos de enero a agosto de 2020 y ofrece una consulta retrospectiva al modelo publicado en Databricks.

## Verificaciones rápidas

| Qué revisar | Enlace | Resultado esperado |
| --- | --- | --- |
| Página web | [Abrir AIRE STUDIO](https://web-app-calidad-d4fvd7f3byc9dtfh.mexicocentral-01.azurewebsites.net/) | Se carga el diseño, los gráficos, el calendario y la simulación histórica |
| Salud de FastAPI | [Abrir `/health`](https://web-app-calidad-d4fvd7f3byc9dtfh.mexicocentral-01.azurewebsites.net/health) | `{"status":"ok"}` y respuesta HTTP 200 |
| Documentación de FastAPI | [Abrir `/docs`](https://web-app-calidad-d4fvd7f3byc9dtfh.mexicocentral-01.azurewebsites.net/docs) | Se muestran las rutas HTTP disponibles |

**Estado de verificación:** el workflow de **despliegue** terminó en verde el 16/10/2026, pero aquí **no se da por comprobada** la respuesta actual de las URLs ni la consulta a Databricks: esas pruebas deben ejecutarse en el navegador y quedar registradas. La URL se tomó del *Default domain* observado en Azure, no se dedujo del nombre del recurso.

## Qué puede hacer un visitante

1. Explorar enero–agosto de 2020, los errores MAE/RMSE, señales de drift y cambios de champion.
2. Seleccionar **Santa Cruz** o **San Francisco**, y una fecha y hora con historial suficiente.
3. Comparar predicción histórica y PM2.5 realmente observado una hora después.
4. Solicitar una **nueva inferencia retrospectiva** mediante el Serving endpoint, si está autorizado y disponible.

La web no inicia Jobs de Databricks, no reentrena y no predice concentraciones actuales de 2026.

## Información para soporte

- **Nombre de la Web App:** `Web-App-Calidad`
- **Región:** `Mexico Central`
- **Grupo de recursos:** `Resource_calidad_aire`
- **Repositorio:** [MLOPS_Calidad_aire](https://github.com/Fred-0606/MLOPS_Calidad_aire)
- **Rama principal:** `main`
- **Workflow de despliegue:** `main_web-app-calidad.yml`
- **Backend:** FastAPI (Python), accesible desde `/health` y `/api/history/*`

Para comprobar el modelo servido, revisa en **Databricks → Serving** su nombre, versión y estado `READY`. No deduzcas la versión del endpoint a partir de la versión 8 que cerró la simulación.

> **Seguridad:** la URL es pública; si el botón de nueva inferencia está habilitado sin autenticación/rate limiting, terceros podrían generar consultas a Databricks. Revisa permisos, límites, presupuesto y monitoreo antes de difundir el enlace masivamente.

[Volver al README](../README.md)
