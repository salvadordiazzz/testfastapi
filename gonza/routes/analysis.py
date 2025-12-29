from fastapi import APIRouter, HTTPException
from db.database import db
from services.anomaly_detector import anomaly_detector
from typing import Optional

router = APIRouter()

@router.get("/analizar/{item_descripcion}")
async def analizar_item(item_descripcion: str):
    """
    Analiza un item específico y detecta anomalías de precio
    """
    try:
        print(f"🔍 Analizando: {item_descripcion}")
        
        # Buscar item más reciente con esa descripción
        item = db.fetchone("""
            SELECT * FROM items 
            WHERE descripcion ILIKE %s
            ORDER BY created_at DESC
            LIMIT 1
        """, (f"%{item_descripcion}%",))
        
        if not item:
            raise HTTPException(
                status_code=404,
                detail=f"No se encontró ningún item que coincida con '{item_descripcion}'"
            )
        
        # Detectar anomalía
        anomaly_data = anomaly_detector.detect_anomaly(
            item["descripcion"],
            float(item["precio_unitario"])
        )
        
        # Guardar alerta si es anómalo
        if anomaly_data["es_anomalo"]:
            alert_id = anomaly_detector.save_alert(item["id"], anomaly_data)
            anomaly_data["alert_id"] = alert_id
        
        return {
            "success": True,
            "item": {
                "id": item["id"],
                "descripcion": item["descripcion"],
                "precio": float(item["precio_unitario"]),
                "cantidad": item["cantidad"]
            },
            "analisis": anomaly_data
        }
    
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error en análisis: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/alertas")
async def obtener_alertas(
    limite: Optional[int] = 100,
    solo_criticas: Optional[bool] = False
):
    """
    Obtiene todas las alertas de anomalías
    """
    try:
        # Query base
        query = """
            SELECT 
                a.id,
                a.tipo_anomalia,
                a.descripcion,
                a.score_riesgo,
                a.created_at,
                i.id as item_id,
                i.descripcion as item_descripcion,
                i.precio_unitario,
                i.cantidad,
                l.id as licitacion_id,
                l.empresa,
                l.numero_licitacion,
                l.fecha
            FROM alertas a
            JOIN items i ON a.item_id = i.id
            JOIN licitaciones l ON i.licitacion_id = l.id
        """
        
        # Filtrar solo críticas si se solicita
        if solo_criticas:
            query += " WHERE a.score_riesgo >= 80"
        
        query += " ORDER BY a.score_riesgo DESC, a.created_at DESC"
        query += f" LIMIT {limite}"
        
        alertas = db.fetchall(query)
        
        # Agrupar por nivel de riesgo
        por_nivel = {
            "critico": [a for a in alertas if a["score_riesgo"] >= 80],
            "alto": [a for a in alertas if 60 <= a["score_riesgo"] < 80],
            "medio": [a for a in alertas if 40 <= a["score_riesgo"] < 60],
            "bajo": [a for a in alertas if a["score_riesgo"] < 40]
        }
        
        return {
            "success": True,
            "total": len(alertas),
            "por_nivel": {
                "critico": len(por_nivel["critico"]),
                "alto": len(por_nivel["alto"]),
                "medio": len(por_nivel["medio"]),
                "bajo": len(por_nivel["bajo"])
            },
            "alertas": alertas
        }
    
    except Exception as e:
        print(f"❌ Error obteniendo alertas: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/reporte/{licitacion_id}")
async def generar_reporte(licitacion_id: int):
    """
    Genera un reporte completo de una licitación con análisis de anomalías
    """
    try:
        # Obtener datos de la licitación
        licitacion = db.fetchone(
            "SELECT * FROM licitaciones WHERE id = %s",
            (licitacion_id,)
        )
        
        if not licitacion:
            raise HTTPException(status_code=404, detail="Licitación no encontrada")
        
        # Obtener items
        items = db.fetchall(
            "SELECT * FROM items WHERE licitacion_id = %s ORDER BY id",
            (licitacion_id,)
        )
        
        # Analizar cada item
        items_con_analisis = []
        total_alertas = 0
        score_promedio = 0
        
        for item in items:
            analisis = anomaly_detector.detect_anomaly(
                item["descripcion"],
                float(item["precio_unitario"])
            )
            
            items_con_analisis.append({
                **item,
                "analisis": analisis
            })
            
            if analisis["es_anomalo"]:
                total_alertas += 1
                score_promedio += analisis["score_riesgo"]
        
        # Calcular score promedio de riesgo
        if total_alertas > 0:
            score_promedio = score_promedio / total_alertas
        
        return {
            "success": True,
            "licitacion": licitacion,
            "resumen": {
                "total_items": len(items),
                "items_con_anomalias": total_alertas,
                "score_riesgo_promedio": round(score_promedio, 2),
                "monto_total": sum(float(i["precio_total"]) for i in items)
            },
            "items": items_con_analisis
        }
    
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error generando reporte: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/dashboard")
async def get_dashboard():
    """
    Dashboard con estadísticas generales del sistema
    """
    try:
        # Totales
        total_licitaciones = db.fetchone("SELECT COUNT(*) as total FROM licitaciones")
        total_items = db.fetchone("SELECT COUNT(*) as total FROM items")
        total_alertas = db.fetchone("SELECT COUNT(*) as total FROM alertas")
        
        # Monto total procesado
        monto_total = db.fetchone("""
            SELECT COALESCE(SUM(precio_total), 0) as total 
            FROM items
        """)
        
        # Alertas por tipo
        alertas_por_tipo = db.fetchall("""
            SELECT 
                tipo_anomalia,
                COUNT(*) as cantidad,
                AVG(score_riesgo) as score_promedio
            FROM alertas
            GROUP BY tipo_anomalia
            ORDER BY cantidad DESC
        """)
        
        # Empresas con más alertas
        empresas_alertas = db.fetchall("""
            SELECT 
                l.empresa,
                COUNT(DISTINCT l.id) as total_licitaciones,
                COUNT(a.id) as total_alertas,
                AVG(a.score_riesgo) as riesgo_promedio
            FROM licitaciones l
            JOIN items i ON l.id = i.licitacion_id
            JOIN alertas a ON i.id = a.item_id
            GROUP BY l.empresa
            ORDER BY total_alertas DESC
            LIMIT 10
        """)
        
        # Tendencia temporal (últimos 30 días)
        tendencia = db.fetchall("""
            SELECT 
                DATE(created_at) as fecha,
                COUNT(*) as alertas_generadas
            FROM alertas
            WHERE created_at >= CURRENT_DATE - INTERVAL '30 days'
            GROUP BY DATE(created_at)
            ORDER BY fecha DESC
        """)
        
        return {
            "success": True,
            "resumen": {
                "total_licitaciones": total_licitaciones["total"],
                "total_items": total_items["total"],
                "total_alertas": total_alertas["total"],
                "monto_total_procesado": float(monto_total["total"])
            },
            "alertas_por_tipo": alertas_por_tipo,
            "empresas_con_mas_alertas": empresas_alertas,
            "tendencia_30_dias": tendencia
        }
    
    except Exception as e:
        print(f"❌ Error en dashboard: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/estadisticas/{item_descripcion}")
async def obtener_estadisticas_item(item_descripcion: str):
    """
    Obtiene estadísticas históricas de un item específico
    """
    try:
        stats = anomaly_detector.get_item_statistics(item_descripcion)
        
        if not stats:
            raise HTTPException(
                status_code=404,
                detail=f"No hay datos históricos para '{item_descripcion}'"
            )
        
        # Obtener distribución de precios
        precios = db.fetchall("""
            SELECT 
                precio_unitario,
                created_at,
                descripcion
            FROM items
            WHERE descripcion ILIKE %s
            ORDER BY created_at DESC
            LIMIT 50
        """, (f"%{item_descripcion}%",))
        
        return {
            "success": True,
            "item_descripcion": item_descripcion,
            "estadisticas": stats,
            "historico_precios": precios
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
