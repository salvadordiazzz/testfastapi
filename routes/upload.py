from fastapi import APIRouter, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
import os
import shutil
from datetime import datetime
from pathlib import Path

router = APIRouter()
UPLOAD_DIR = Path("./uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

ALLOWED_TYPES = ["application/pdf", "image/png", "image/jpeg", "image/jpg"]
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB


@router.post("/upload")
async def upload_document(documento: UploadFile = File(...)):
    """
    Endpoint para subir documentos de licitación
    """
    try:
        # Validar tipo de archivo
        if documento.content_type not in ALLOWED_TYPES:
            raise HTTPException(
                status_code=400,
                detail=f"Tipo de archivo no permitido. Permitidos: PDF, PNG, JPG"
            )

        # Validar tamaño
        contents = await documento.read()
        if len(contents) > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=400,
                detail="Archivo demasiado grande. Máximo 10MB"
            )

        # Generar nombre único
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_extension = Path(documento.filename).suffix
        unique_filename = f"{timestamp}_{documento.filename}"
        file_path = UPLOAD_DIR / unique_filename

        # Guardar archivo
        with open(file_path, "wb") as buffer:
            buffer.write(contents)

        print(f"📄 Archivo recibido: {documento.filename}")

        return {
            "success": True,
            "message": "Archivo recibido correctamente",
            "file": {
                "id": unique_filename,
                "original_name": documento.filename,
                "path": str(file_path),
                "size": len(contents)
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error en upload: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/files")
async def list_files():
    """
    Listar archivos subidos
    """
    try:
        files = []
        for file_path in UPLOAD_DIR.glob("*"):
            if file_path.is_file():
                files.append({
                    "name": file_path.name,
                    "size": file_path.stat().st_size,
                    "modified": datetime.fromtimestamp(file_path.stat().st_mtime).isoformat()
                })

        return {
            "success": True,
            "total": len(files),
            "files": files
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
