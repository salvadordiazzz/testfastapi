from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class ItemCreate(BaseModel):
    descripcion: str
    cantidad: Optional[int] = 1
    precio_unitario: float
    precio_total: Optional[float] = None

class LicitacionCreate(BaseModel):
    empresa: str
    licitacion: Optional[str] = None
    fecha: Optional[str] = None
    items: List[ItemCreate]

class GuardarResponse(BaseModel):
    success: bool
    message: str
    licitacion_id: Optional[int] = None
    items_guardados: Optional[int] = None

class Estadisticas(BaseModel):
    promedio: float
    minimo: float
    maximo: float
    desviacion_estandar: float
    muestras: int

class AnalisisAnomalia(BaseModel):
    es_anomalo: bool
    tipo: str
    mensaje: str
    score_riesgo: int
    estadisticas: Optional[dict] = None
