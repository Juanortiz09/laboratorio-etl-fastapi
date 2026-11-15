from typing import Any, Dict, Optional
from pydantic import BaseModel, Field


class ExtraerRequest(BaseModel):
    cantidad: int = Field(..., gt=0, description="Número de registros a extraer de DummyJSON")


class ExtraerResponse(BaseModel):
    mensaje: str
    total_solicitados: int
    nuevos_insertados: int
    ya_existentes: int


class TransformarResponse(BaseModel):
    mensaje: str
    documentos_procesados: int
    registros_cargados_sql: int


class ResetResponse(BaseModel):
    mensaje: str
    documentos_eliminados_mongo: int
    registros_eliminados_sql: int


class PerfilDualResponse(BaseModel):
    id: int
    estado_sincronizacion: str
    mensaje: str
    datos_staging_mongo: Optional[Dict[str, Any]] = None
    datos_analitica_sql: Optional[Dict[str, Any]] = None