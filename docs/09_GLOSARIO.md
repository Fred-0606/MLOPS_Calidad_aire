# 09 · Glosario técnico del proyecto

[← README](../README.md)

| Término | Definición aplicada al proyecto |
| --- | --- |
| **API** | Interfaz programática para intercambiar datos; Socrata es fuente y FastAPI es backend público de la demo. |
| **Azure App Service** | Servicio PaaS donde se ejecuta FastAPI y se sirve el sitio; proveedor Azure `Microsoft.Web`. |
| **Azure Container Apps** | Servicio de contenedores del proveedor `Microsoft.App`, no utilizado en esta ruta. |
| **Batch / `batch_month`** | Mes histórico considerado «actual» dentro de la simulación secuencial. |
| **Baseline / persistencia** | Modelo ingenuo que usa PM2.5 de t como predicción de t+1. |
| **Bronze** | Datos ingestados en una forma cercana a la original, con trazabilidad. |
| **Champion** | Versión vigente seleccionada por NB03 para la inferencia de un mes; alias movible en MLflow. |
| **Challenger** | Versión candidata que debe pasar la puerta de promoción. |
| **CI/CD** | Integración y entrega/despliegue continuos de código; aquí GitHub Actions publica la web. NB03 aplica política de *promoción del modelo*, no despliega la aplicación. |
| **Cobertura** | Fracción de filas del mes que reúne suficientes entradas para producir predicción (`len(inputs)/len(month)`). |
| **Data drift** | Cambio de distribución de las variables respecto a una referencia histórica. |
| **Data leakage** | Uso inapropiado de información futura o ajena al momento de predicción en preparación, entrenamiento o evaluación. |
| **Delta Lake** | Formato de almacenamiento de tablas con transacciones e historial de versiones. |
| **Endpoint / Serving endpoint** | Servicio HTTP de Databricks que ejecuta un modelo publicado y devuelve predicciones. |
| **Feature engineering** | Transformación de datos en variables útiles, como rezagos, medias y componentes cíclicas. |
| **`feature_time`** | Hora t hasta la cual se conocen las entradas del modelo. |
| **`target_time`** | Hora t+1 para la que se produce el pronóstico. |
| **Gate / puerta de promoción** | Bloque cronológico de la última semana antes de un mes, reservado para comparar challenger y champion. |
| **GitHub Actions** | Automatización definida en YAML para probar/desplegar una revisión del repositorio. |
| **Gold** | Resultados de predicción y monitoreo preparados para ser consultados. |
| **Horizon** | Separación entre instante de entrada y pronóstico; aquí 1 hora. |
| **Inferencia** | Aplicación de un modelo ya entrenado a un vector de entradas, sin volver a entrenarlo. |
| **KS** | Estadístico Kolmogorov–Smirnov de dos muestras; compara distribuciones acumuladas. |
| **`ks_pvalue`** | Valor p de la prueba KS; **no** es la probabilidad de que exista drift. |
| **MAE** | Error absoluto medio: `mean(|y - ŷ|)`; unidad igual a la concentración. |
| **MLflow** | Tracking de experimentos y registro de versiones de modelos. |
| **MLOps** | Prácticas de operación del ciclo del modelo, desde datos y entrenamiento hasta evaluación, versión, despliegue y monitoreo. |
| **Model Serving** | Infraestructura que recibe entradas y ejecuta inferencias de un modelo específico. |
| **Observado** | Concentración registrada por el sensor en la hora objetivo, no una predicción. |
| **PM2.5** | Concentración de partículas finas con diámetro aerodinámico ≤2,5 μm; no equivale directamente a AQI. |
| **PSI** | Population Stability Index: compara distribuciones discretizadas de referencia y periodo actual. |
| **PSI de anomalía** | PSI sobre `pm25 - mean_24` por estación; en este proyecto se usa para activar una de las reglas de reentrenamiento. |
| **Random Forest** | Conjunto de árboles de decisión que permite modelar relaciones no lineales. |
| **Regresión** | Predicción de una magnitud numérica continua (PM2.5). |
| **Reentrenamiento solicitado** | `retrain_next=true`: señal para que NB02 del siguiente mes evalúe entrenar, no reemplazo inmediato. |
| **Replay histórico** | Navegación visual por resultados previamente calculados; no es una ejecución nueva de Jobs. |
| **RMSE** | Raíz del error cuadrático medio; penaliza más errores grandes. |
| **Ridge** | Regresión lineal con penalización sobre coeficientes; en la implementación se estandarizan entradas. |
| **Socrata** | Plataforma de publicación y API de datasets usada por datos.gov.co. |
| **Silver** | Datos validados y transformados en características/objetivo. |
| **Snapshot Delta** | Versión específica de una tabla que permite repetir una evaluación sobre las mismas filas. |
| **Unity Catalog** | Catálogo y sistema de gobierno de tablas y modelos de Databricks. |
| **UTC / sufijo `Z`** | Representación de tiempo con referencia UTC. En este proyecto se requiere verificar si el huso de la fuente original coincide con la convención del exportado. |
| **`force_train`** | Parámetro manual que fuerza la solicitud de entrenamiento sin permitir saltar meses ni promover automáticamente. |

### Fórmulas de referencia

\[
MAE = \frac{1}{n}\sum_{i=1}^{n}\lvert y_i-\hat y_i\rvert
\qquad
RMSE=\sqrt{\frac{1}{n}\sum_{i=1}^{n}(y_i-\hat y_i)^2}
\]

\[
\mathrm{anomalía}_t = PM2.5_t - \mathrm{media}_{24,t}
\]

Las métricas y umbrales descritos son herramientas de validación del modelo, **no** umbrales oficiales de salud pública.

[Volver al índice](../README.md)
