# 11 · Organización del repositorio y mantenimiento documental

[← README](../README.md) · [Despliegue](08_DESPLIEGUE_Y_OPERACION.md)

## Árbol de referencia

```text
mlops-aire/
├── README.md                     ← Presentación principal en GitHub
├── main.py                       ← FastAPI interactiva
├── requirements.txt              ← Paquetes para la API
├── .gitignore                     ← Exclusiones de archivos locales/credenciales
├── static/
│   └── index.html                ← AIRE STUDIO
├── data/
│   └── historical_features_2020.json.gz
├── docs/
│   ├── 01_ARQUITECTURA.md
│   ├── 02_METODOLOGIA_MLOPS.md
│   ├── 03_DATOS_Y_VARIABLES.md
│   ├── 04_DRIFT_REENTRENAMIENTO_Y_PROMOCION.md
│   ├── 05_RESULTADOS_2020.md
│   ├── 06_GUIA_DE_LA_WEB.md
│   ├── 07_API_Y_CONTRATOS.md
│   ├── 08_DESPLIEGUE_Y_OPERACION.md
│   ├── 09_GLOSARIO.md
│   ├── 10_VALIDACION_Y_LIMITACIONES.md
│   ├── 11_REPOSITORIO_Y_MANTENIMIENTO.md
│   └── assets/
│       └── aire-studio-vista-previa.png
└── .github/workflows/           ← Si ya existen workflows de pruebas / despliegue
```

Los cuatro notebooks viven originalmente en Databricks. Puedes **opcionalmente** exportarlos a `notebooks/` en el repositorio para dar trazabilidad al código, sin suponer que GitHub los ejecuta. La fuente de verdad de los Jobs y de las tablas del experimento sigue en el workspace de Databricks hasta que implementes sincronización automática.

## Cómo añadir esta documentación al repositorio existente

**Opción GitHub desde el navegador:**

1. Descomprime el paquete de documentación.
2. Abre tu repositorio en GitHub, rama `main` o una rama de documentación.
3. **Reemplaza solo el `README.md`** de la raíz con el archivo del paquete, si quieres que sea la portada principal.
4. Crea o sube la carpeta `docs/` completa, incluido `docs/assets/aire-studio-vista-previa.png`.
5. Comprueba que los enlaces del README a `docs/` funcionan y la imagen aparece correctamente.
6. Confirma los cambios mediante un commit, por ejemplo: `docs: documentar arquitectura y resultados MLOps aire 2020`.

**Opción terminal**, desde una copia local del repositorio ya clonada y con archivos copiados:

```bash
git status
git add README.md docs/
git commit -m "docs: arquitectura, metodologia y resultados MLOps 2020"
git push origin main
```

Si usas ramas de revisión, crea una pull request y fusiona después de comprobar la documentación. **No uses `git init` otra vez sobre una carpeta clonada**.

## Convención de mantenimiento

| Si cambia… | Actualiza también… |
| --- | --- |
| Features o firma del modelo | `03_DATOS_Y_VARIABLES.md`, contrato de API, ejemplo de solicitud y tests |
| Regla de PSI/reentrenamiento | `04_DRIFT_REENTRENAMIENTO_Y_PROMOCION.md` y resultados pertinentes |
| Champion o política de selección | `02_METODOLOGIA_MLOPS.md`, `04_DRIFT...` y notas de evaluación |
| Nuevos meses / exportación histórica | `05_RESULTADOS_2020.md`, resumen del README y archivo `data/*.json.gz` |
| Endpoint o autenticación | `07_API_Y_CONTRATOS.md` y `08_DESPLIEGUE_Y_OPERACION.md` |
| UI o rutas de FastAPI | `06_GUIA_DE_LA_WEB.md`, `07_API_Y_CONTRATOS.md` y capturas |
| Servicios Azure / GitHub Actions | `01_ARQUITECTURA.md`, `08_DESPLIEGUE_Y_OPERACION.md` |

## Reglas para un repositorio profesional

- El README debe explicar qué **está implementado** y qué solo está **previsto**.
- Las cifras de evaluación deben poder rastrearse a tablas o CSV, con esquema, período y fecha de extracción.
- No subir `.venv/`, `.env`, credenciales, tokens, logs de errores sensibles ni dumps de datos privados.
- No cambiar resultados históricos en documentos sin volver a generar y comprobar la exportación.
- Referenciar diagramas Mermaid para mantenerlos editables dentro del Markdown de GitHub.
- Mantener el mismo vocabulario entre notebooks, API y documentación: `champion`, `challenger`, `drift_signal`, `retrain_next`.
- Versionar cambios de documentación junto con cambios del sistema cuando afecten su comportamiento.

[Volver al índice](../README.md)
