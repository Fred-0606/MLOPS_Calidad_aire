"""API genérica para consultar un Databricks Model Serving endpoint.

Este proyecto NO contiene un modelo entrenado: envía el JSON del cliente
al endpoint de Databricks y devuelve su respuesta sin transformarla.
"""
import os
import logging
from pathlib import Path
from typing import Any
from urllib.parse import quote

import httpx
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import RootModel

app = FastAPI(title="Mi integración MLOps", version="1.0.0")
log = logging.getLogger(__name__)
BASE_DIR = Path(__file__).resolve().parent


class Payload(RootModel[dict[str, Any]]):
    """Cuerpo compatible con el contrato particular del endpoint de Databricks."""


@app.get("/health")
def health() -> dict[str, str]:
    """Comprueba que el servidor HTTP está respondiendo (no prueba el modelo)."""
    return {"status": "ok"}


@app.get("/", include_in_schema=False)
def home() -> FileResponse:
    return FileResponse(BASE_DIR / "static" / "index.html")


@app.post("/predict")
async def predict(payload: Payload) -> Any:
    host = os.getenv("DATABRICKS_HOST", "").rstrip("/")
    endpoint = os.getenv("DATABRICKS_ENDPOINT", "")
    token = os.getenv("DATABRICKS_TOKEN", "")
    if not (host and endpoint and token):
        raise HTTPException(status_code=503, detail="Falta la configuración de Databricks en el servidor")
    if not host.startswith("https://"):
        raise HTTPException(status_code=503, detail="DATABRICKS_HOST debe comenzar por https://")
    # quote protege el segmento de ruta si el nombre del endpoint tiene caracteres especiales.
    url = f"{host}/serving-endpoints/{quote(endpoint, safe='')}/invocations"
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                url,
                headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
                json=payload.root,
            )
            response.raise_for_status()
            return response.json()
    except httpx.TimeoutException:
        raise HTTPException(status_code=504, detail="Tiempo de espera agotado al consultar Databricks")
    except httpx.HTTPStatusError as exc:
        log.warning("Error de Databricks. Estado HTTP %s", exc.response.status_code)
        raise HTTPException(status_code=502, detail=f"Databricks respondió HTTP {exc.response.status_code}")
    except (httpx.RequestError, ValueError):
        log.exception("Falló la consulta a Databricks")
        raise HTTPException(status_code=502, detail="No se pudo completar la consulta a Databricks")
