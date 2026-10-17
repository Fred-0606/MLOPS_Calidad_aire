# 13 · Bitácora del despliegue a Azure (octubre de 2026)

[← README](../README.md) · [Despliegue](08_DESPLIEGUE_Y_OPERACION.md) · [Web pública](12_APLICACION_WEB_PUBLICA.md)

## Estado observado al cierre de la configuración

- **Repositorio:** `Fred-0606/MLOPS_Calidad_aire`, rama `main`.
- **Flujo de pruebas:** `Pruebas de la API` terminó en verde, después de actualizar una prueba que todavía exigía la variable JavaScript `API_URL` de la página original.
- **Flujo de despliegue:** `Build and deploy Python app to Azure Web App - Web-App-Calidad`; el usuario informó que la nueva ejecución terminó **en verde el 16 de octubre de 2026**.
- **Web App:** `Web-App-Calidad`, Linux, `Mexico Central`, grupo de recursos `Resource_calidad_aire`.
- **Plan:** `ASP-RecursosStudents-b107`, F1 (gratuito), ubicado en `Recursos_students`, compartido con la aplicación preexistente `mlops-students`.
- **Dominio público:** [abrir AIRE STUDIO](../README.md#acceder-a-la-aplicación-web-pública) y [acceso directo](12_APLICACION_WEB_PUBLICA.md).
- **Estado funcional de la URL:** **pendiente de comprobar aquí** con `/health`, apertura del HTML, consulta de históricos e inferencia real. Un workflow verde verifica que la acción terminó, no que la API esté funcional.

## Incidencias y decisiones

| Fase | Mensaje o síntoma | Interpretación | Resolución / acción seguida |
| --- | --- | --- | --- |
| Prueba CI | `assert 'API_URL' in response.text` | Prueba de la antigua plantilla incompatible con la interfaz nueva | Se reemplazó por verificaciones de HTML y tipo de contenido; pruebas CI en verde |
| Login OIDC | `No subscriptions found` | No se completaba acceso efectivo a la suscripción | Revisar rol IAM, referencias a secretos y visibilidad de la suscripción |
| Login OIDC | `AADSTS700016 Application ... was not found in the directory` | Desajuste de client ID / tenant ID de la identidad federada | Se revisaron/corrigieron valores de GitHub para la identidad OIDC; el login pasó a la etapa posterior |
| Publicación | `Failed to deploy ... OneDeploy; Site Disabled (CODE: 403)` | Azure rechazaba la publicación porque la Web App estaba deshabilitada | Se detectó `Quota exceeded` en el estado de Azure |
| Plan F1 | Indicadores de consumo en cero pero estado `Quota exceeded` | Se observó bloqueo de cuota; la causa exacta del contador no quedó demostrada | Se aguardó recuperación de la disponibilidad; posteriormente Azure pasó a `Running` |
| Reejecución | Build y deploy en verde | GitHub Actions completó la publicación al recuperarse la Web App | Pendiente prueba HTTP y de inferencia desde la URL pública |

**Precisión:** las acciones que se siguieron no prueban que una asignación específica de `Reader` fuese la única causa de la solución OIDC, ni que otra aplicación fuese responsable del estado de cuota. Evitar atribuir causalidad sin un registro explícito de Azure.

## Autenticación y alcance de permisos

Se creó una identidad de usuario `oidc-msi-9e69` para el despliegue GitHub → Azure y se observó su rol `Website Contributor` sobre `Web-App-Calidad`. El workflow obtiene credenciales mediante secretos de GitHub y autenticación federada OIDC; no incrusta tokens de Databricks en el YAML. Se debe revisar periódicamente la credencial federada (emisor, repositorio, rama y audiencia) y mantener permisos mínimos.

## Pruebas que deben anexarse para cerrar operación

- [ ] `GET /health` devuelve HTTP 200 y `{"status":"ok"}` desde el dominio público.
- [ ] `GET /` sirve AIRE STUDIO sin errores de archivos o dependencias.
- [ ] Selección de mes y reproducción histórica muestran datos exportados.
- [ ] `GET /api/history/dates?station=santa_cruz` devuelve fechas.
- [ ] La consulta individual recupera un resultado histórico válido.
- [ ] `POST /api/history/predict` funciona con permisos y Serving `READY`; anotar el nombre y versión efectivamente servidos.
- [ ] Se verifican límites de acceso y presupuesto antes de promocionar el sitio como demostración pública abierta.

No publicar en GitHub capturas con tokens, valores de secretos, cabeceras de autenticación o material sensible de despliegue.

[Volver al README](../README.md)
