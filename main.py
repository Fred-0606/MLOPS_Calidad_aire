"""MLOps Aire · API FastAPI y simulador histórico enero-agosto 2020.

GET / predicciones y monitoreo ya almacenados en HTML, sin nuevos Jobs.
/api/history/* : calendario y consultas reconstruidas SOLO a partir del histórico hasta t.
/predict : proxy JSON original hacia Databricks Model Serving.

El target de t+1 nunca entra a las 13 variables usadas en /api/history/predict.
"""
import gzip
import json
import logging
import os
from functools import lru_cache
from pathlib import Path
from typing import Any, Literal
from urllib.parse import quote

import httpx
from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import FileResponse
from pydantic import BaseModel, RootModel

app = FastAPI(title="MLOps Aire | PM2.5", version="2.0.0")
log = logging.getLogger(__name__)
BASE_DIR = Path(__file__).resolve().parent
FEATURE_ARCHIVE = BASE_DIR / "data" / "historical_features_2020.json.gz"

class Payload(RootModel[dict[str, Any]]):
    """Contrato genérico preexistente de Databricks."""

class HistoricSelection(BaseModel):
    station: Literal["santa_cruz", "san_francisco"]
    feature_time: str

@lru_cache(maxsize=1)
def historic_data() -> dict[str, Any]:
    if not FEATURE_ARCHIVE.is_file():
        raise HTTPException(status_code=503,detail="Falta data/historical_features_2020.json.gz. Copia la carpeta data completa.")
    try:
        with gzip.open(FEATURE_ARCHIVE, 'rt', encoding='utf-8') as f:
            out = json.load(f)
    except (OSError, ValueError):
        log.exception("No se pudo leer el historial")
        raise HTTPException(status_code=503, detail="No se pudo leer el archivo de histórico.")
    return out

def get_record(station: str, feature_time: str) -> list[Any]:
    records=historic_data()['records'].get(station)
    if records is None:
        raise HTTPException(status_code=422,detail="Estación no válida")
    item=records.get(feature_time)
    if item is None:
        raise HTTPException(status_code=404,detail="Esa estación y hora no tienen todas las variables históricas válidas.")
    return item

def public_record(station: str, feature_time: str, item: list[Any]) -> dict[str, Any]:
    # El índice guarda [vector13, predicción_histórica, observado_t+1, version_histórica].
    return {
        "station":station,"feature_time":feature_time,
        "target_time":_target_time(feature_time),
        "historical_prediction":item[1],
        "observed_pm25":item[2],
        "historical_model_version":str(item[3]),
    }

def _target_time(feature_time: str) -> str:
    from datetime import datetime, timedelta, timezone
    dt=datetime.strptime(feature_time, '%Y-%m-%dT%H:%M:%SZ').replace(tzinfo=timezone.utc)
    return (dt+timedelta(hours=1)).strftime('%Y-%m-%dT%H:%M:%SZ')

async def ask_databricks(payload: dict[str, Any]) -> Any:
    host=os.getenv('DATABRICKS_HOST','').rstrip('/')
    endpoint=os.getenv('DATABRICKS_ENDPOINT','')
    token=os.getenv('DATABRICKS_TOKEN','')
    if not (host and endpoint and token):
        raise HTTPException(status_code=503,detail="Falta configurar DATABRICKS_HOST, DATABRICKS_ENDPOINT o DATABRICKS_TOKEN en el servidor.")
    if not host.startswith('https://'):
        raise HTTPException(status_code=503,detail="DATABRICKS_HOST debe comenzar por https://")
    url=f"{host}/serving-endpoints/{quote(endpoint, safe='')}/invocations"
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response=await client.post(url,headers={"Authorization":f"Bearer {token}","Content-Type":"application/json"},json=payload)
            response.raise_for_status()
            return response.json()
    except httpx.TimeoutException:
        raise HTTPException(status_code=504,detail="Tiempo de espera agotado al consultar Databricks")
    except httpx.HTTPStatusError as exc:
        log.warning("Databricks respondió HTTP %s",exc.response.status_code)
        raise HTTPException(status_code=502,detail=f"Databricks respondió HTTP {exc.response.status_code}")
    except (httpx.RequestError,ValueError):
        log.exception("Falló la consulta a Databricks")
        raise HTTPException(status_code=502,detail="No se pudo completar la consulta a Databricks")

@app.get('/health')
def health() -> dict[str,str]:
    return {"status":"ok"}

@app.get('/',include_in_schema=False)
def home() -> FileResponse:
    return FileResponse(BASE_DIR/'static'/'index.html')

@app.post('/predict')
async def predict(payload: Payload) -> Any:
    """Se mantiene el contrato original para cualquier consulta JSON compatible."""
    return await ask_databricks(payload.root)

@app.get('/api/history/dates')
def history_dates(station:Literal['san_francisco','santa_cruz']) -> dict[str,Any]:
    records=historic_data()['records'][station]
    dates=sorted({k[:10] for k in records})
    return {"station":station,"dates":dates,"timezone":"UTC"}

@app.get('/api/history/hours')
def history_hours(station:Literal['san_francisco','santa_cruz'], date:str=Query(min_length=10,max_length=10)) -> dict[str,Any]:
    import re
    if not re.fullmatch(r'2020-0[1-8]-[0-3][0-9]', date):
        raise HTTPException(status_code=422,detail="La fecha debe corresponder a enero-agosto de 2020 (AAAA-MM-DD).")
    records=historic_data()['records'][station]
    hours=[k for k in records if k.startswith(date+'T')]
    return {"station":station,"date":date,"hours":hours,"timezone":"UTC"}

@app.get('/api/history/result')
def history_result(station:Literal['san_francisco','santa_cruz'], feature_time:str) -> dict[str,Any]:
    return public_record(station,feature_time,get_record(station,feature_time))

@app.post('/api/history/predict')
async def history_predict(selection:HistoricSelection) -> dict[str,Any]:
    item=get_record(selection.station, selection.feature_time)
    feature_names=historic_data()['feature_names']
    payload={"dataframe_split":{"columns":feature_names,"data":[item[0]]}}
    response=await ask_databricks(payload)
    # No se inventa el resultado si el endpoint entrega un formato inesperado.
    predictions=response.get('predictions') if isinstance(response,dict) else None
    if not (isinstance(predictions,list) and len(predictions)==1 and isinstance(predictions[0],(int,float)) and not isinstance(predictions[0],bool)):
        raise HTTPException(status_code=502,detail="El endpoint no devolvió una predicción numérica en predictions[0]. Verifica su contrato JSON.")
    import math
    if not math.isfinite(predictions[0]):
        raise HTTPException(status_code=502,detail="El endpoint devolvió un valor numérico no finito.")
    return {**public_record(selection.station,selection.feature_time,item),"current_prediction":float(predictions[0]),"source":"databricks_model_serving_current_endpoint"}
