from db.database import db
from typing import Optional, Dict
import math

class AnomalyDetector:
    
    def get_item_statistics(self, item_descripcion: str) -> Optional[Dict]:
        """
        Calcula estadísticas de un item basado en histórico
        Usa ILIKE para búsqueda case-insensitive en PostgreSQL
        """
        try:
            # Buscar items similares (PostgreSQL ILIKE)
            items = db.fetchall("""
                SELECT precio_unitario 
                FROM items 
                WHERE descripcion ILIKE %s
                ORDER BY created_at DESC
                LIMIT 100
            """, (f"%{item_descripcion}%",))
            
            if not items:
                return None
            
            precios = [float(item["precio_unitario"]) for item in items]
            
            # Calcular estadísticas
            n = len(precios)
            promedio = sum(precios) / n
            minimo = min(precios)
            maximo = max(precios)
            
            # Desviación estándar
            varianza = sum((p - promedio) ** 2 for p in precios) / n
            desviacion = math.sqrt(varianza)
            
            return {
                "promedio": promedio,
                "minimo": minimo,
                "maximo": maximo,
                "desviacion_estandar": desviacion,
                "muestras": n
            }
        
        except Exception as e:
            print(f"Error calculando estadísticas: {str(e)}")
            return None
    
    def detect_anomaly(self, item_descripcion: str, precio_actual: float) -> Dict:
        """
        Detecta si un precio es anómalo comparándolo con el histórico
        """
        try:
            stats = self.get_item_statistics(item_descripcion)
            
            if not stats:
                return {
                    "es_anomalo": False,
                    "tipo": "sin_datos",
                    "mensaje": "No hay datos históricos suficientes para comparar",
                    "score_riesgo": 0
                }
            
            promedio = stats["promedio"]
            desviacion = stats["desviacion_estandar"]
            
            # Z-score (desviaciones estándar del promedio)
            z_score = (precio_actual - promedio) / desviacion if desviacion > 0 else 0
            
            # Porcentaje de diferencia
            dif_porcentaje = ((precio_actual - promedio) / promedio) * 100
            
            # Determinar tipo de anomalía
            tipo = "normal"
            mensaje = "Precio dentro del rango normal"
            es_anomalo = False
            score_riesgo = 0
            
            # Precio muy bajo (>30% bajo el promedio)
            if precio_actual < promedio * 0.7:
                tipo = "precio_muy_bajo"
                mensaje = f"ALERTA CRÍTICA: Precio {abs(dif_porcentaje):.1f}% más bajo que el promedio. Posible subvaluación o fraude."
                es_anomalo = True
                score_riesgo = min(100, int(abs(dif_porcentaje)))
            
            # Precio bajo moderado (15-30% bajo)
            elif precio_actual < promedio * 0.85:
                tipo = "precio_bajo"
                mensaje = f"Precio {abs(dif_porcentaje):.1f}% más bajo que el promedio. Revisar justificación."
                es_anomalo = True
                score_riesgo = min(75, int(abs(dif_porcentaje)))
            
            # Precio muy alto (>50% sobre promedio)
            elif precio_actual > promedio * 1.5:
                tipo = "precio_muy_alto"
                mensaje = f"ALERTA: Precio {dif_porcentaje:.1f}% más alto que el promedio. Posible sobrevaloración."
                es_anomalo = True
                score_riesgo = min(100, int(dif_porcentaje))
            
            # Precio alto moderado (30-50% sobre promedio)
            elif precio_actual > promedio * 1.3:
                tipo = "precio_alto"
                mensaje = f"⚠️ Precio {dif_porcentaje:.1f}% más alto que el promedio. Verificar."
                es_anomalo = True
                score_riesgo = min(75, int(dif_porcentaje))
            
            return {
                "es_anomalo": es_anomalo,
                "tipo": tipo,
                "mensaje": mensaje,
                "score_riesgo": score_riesgo,
                "estadisticas": {
                    "precio_actual": round(precio_actual, 2),
                    "precio_promedio": round(promedio, 2),
                    "precio_minimo": round(stats["minimo"], 2),
                    "precio_maximo": round(stats["maximo"], 2),
                    "diferencia_porcentaje": round(dif_porcentaje, 2),
                    "z_score": round(z_score, 2),
                    "desviacion_estandar": round(desviacion, 2),
                    "muestras": stats["muestras"]
                }
            }
        
        except Exception as e:
            print(f"Error detectando anomalía: {str(e)}")
            raise
    
    def save_alert(self, item_id: int, anomaly_data: Dict) -> Optional[int]:
        """
        Guarda una alerta en PostgreSQL
        """
        try:
            if not anomaly_data["es_anomalo"]:
                return None
            
            alert_id = db.execute("""
                INSERT INTO alertas (item_id, tipo_anomalia, descripcion, score_riesgo)
                VALUES (%s, %s, %s, %s) RETURNING id
            """, (
                item_id,
                anomaly_data["tipo"],
                anomaly_data["mensaje"],
                anomaly_data["score_riesgo"]
            ))
            
            print(f"Alerta guardada con ID {alert_id} - Score: {anomaly_data['score_riesgo']}")
            return alert_id
        
        except Exception as e:
            print(f"Error guardando alerta: {str(e)}")
            raise

# Singleton
anomaly_detector = AnomalyDetector()
