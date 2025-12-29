from fastapi import APIRouter, HTTPException
from typing import List
from models.schemas import LicitacionCreate, GuardarResponse
from db.database import db
from datetime import datetime

router = APIRouter()

@router.post("/guardar", response_model=GuardarResponse)
async def guardar_licitacion(data: LicitacionCreate):
    """
    Guarda una licitación con sus items en PostgreSQL
    """
    try:
        print(f"💾 Guardando datos de: {data.empresa}")
        
        # 1. Insertar licitación (con RETURNING para obtener el ID)
        fecha = data.fecha or datetime.now().strftime("%Y-%m-%d")
        
        licitacion_id = db.execute(
            """INSERT INTO licitaciones (empresa, numero_licitacion, fecha)
               VALUES (%s, %s, %s) RETURNING id""",
            (data.empresa, data.licitacion or "SIN-NUMERO", fecha)
        )
        
        # 2. Insertar items
        items_count = 0
        for item in data.items:
            precio_total = item.precio_total or (item.precio_unitario * (item.cantidad or 1))
            
            db.execute(
                """INSERT INTO items (licitacion_id, descripcion, cantidad, 
                   precio_unitario, precio_total) VALUES (%s, %s, %s, %s, %s)""",
                (licitacion_id, item.descripcion, item.cantidad or 1,
                 item.precio_unitario, precio_total)
            )
            items_count += 1
        
        print(f"✅ Guardados {items_count} items para licitación ID {licitacion_id}")
        
        return {
            "success": True,
            "message": "Datos guardados correctamente en PostgreSQL",
            "licitacion_id": licitacion_id,
            "items_guardados": items_count
        }
    
    except Exception as e:
        print(f"❌ Error guardando datos: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/licitaciones")
async def listar_licitaciones():
    """
    Lista todas las licitaciones
    """
    try:
        licitaciones = db.fetchall("""
            SELECT 
                l.id,
                l.empresa,
                l.numero_licitacion,
                l.fecha,
                COUNT(i.id) as total_items,
                SUM(i.precio_total) as monto_total
            FROM licitaciones l
            LEFT JOIN items i ON l.id = i.licitacion_id
            GROUP BY l.id, l.empresa, l.numero_licitacion, l.fecha
            ORDER BY l.created_at DESC
        """)
        
        return {
            "success": True,
            "total": len(licitaciones),
            "licitaciones": licitaciones
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/licitaciones/{licitacion_id}/items")
async def obtener_items(licitacion_id: int):
    """
    Obtiene los items de una licitación específica
    """
    try:
        items = db.fetchall(
            "SELECT * FROM items WHERE licitacion_id = %s ORDER BY id",
            (licitacion_id,)
        )
        
        return {
            "success": True,
            "total": len(items),
            "items": items
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/licitaciones/{licitacion_id}")
async def eliminar_licitacion(licitacion_id: int):
    """
    Elimina una licitación y todos sus items (CASCADE)
    """
    try:
        rows_affected = db.execute(
            "DELETE FROM licitaciones WHERE id = %s",
            (licitacion_id,)
        )
        
        if rows_affected == 0:
            raise HTTPException(status_code=404, detail="Licitación no encontrada")
        
        return {
            "success": True,
            "message": f"Licitación {licitacion_id} eliminada correctamente"
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
