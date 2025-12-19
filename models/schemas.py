from pydantic import BaseModel
from typing import Optional, List
from datetime import date


class ItemExtracted(BaseModel):
    descripcion: str
    cantidad: Optional[int] = 1
    precio_unitario: float
    precio_total: Optional[float] = None

class ExtractedData(BaseModel):
    empresa: str
    licitacion: Optional[str] = None
    fecha: Optional[str] = None
    items: List[ItemExtracted]

class UploadResponse(BaseModel):
    success: bool
    message: str
    file_id: Optional[str] = None
    file_name: Optional[str] = None

class ProcessResponse(BaseModel):
    success: bool
    message: str
    data: Optional[ExtractedData] = None
    error: Optional[str] = None
