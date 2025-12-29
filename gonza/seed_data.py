from db.database import db
from datetime import datetime, timedelta
import random

def seed():
    print("🌱 Generando datos de prueba en PostgreSQL...\n")
    
    empresas = [
        "TechCorp SA",
        "CompuSolutions SpA",
        "InnovateTech Ltda",
        "BaratoCorp SA",
        "PremiumTech SpA"
    ]
    
    productos = [
        "Laptop HP ProBook 450 G9",
        "Laptop Dell Latitude 5520",
        "Monitor Dell 24 pulgadas",
        "Teclado Logitech MX Keys",
        "Mouse Logitech MX Master 3"
    ]
    
    # Precios base normales
    precios_base = {
        "Laptop HP ProBook 450 G9": 18000,
        "Laptop Dell Latitude 5520": 19500,
        "Monitor Dell 24 pulgadas": 5000,
        "Teclado Logitech MX Keys": 2500,
        "Mouse Logitech MX Master 3": 1800
    }
    
    # Generar 20 licitaciones
    for i in range(1, 21):
        # Fecha aleatoria en los últimos 6 meses
        dias_atras = random.randint(1, 180)
        fecha = (datetime.now() - timedelta(days=dias_atras)).strftime("%Y-%m-%d")
        
        empresa = random.choice(empresas)
        
        # Insertar licitación
        licitacion_id = db.execute(
            """INSERT INTO licitaciones (empresa, numero_licitacion, fecha)
               VALUES (%s, %s, %s) RETURNING id""",
            (empresa, f"LIC-2024-{i:03d}", fecha)
        )
        
        print(f"📋 Licitación {i}/20: {empresa} - LIC-2024-{i:03d}")
        
        # Generar 2-4 items por licitación
        num_items = random.randint(2, 4)
        for j in range(num_items):
            producto = random.choice(productos)
            precio_base = precios_base[producto]
            cantidad = random.choice([10, 20, 30, 50, 100])
            
            # Determinar si será anómalo
            tipo_precio = random.choices(
                ["normal", "bajo", "muy_bajo", "alto"],
                weights=[0.6, 0.2, 0.1, 0.1]  # 60% normales, 30% bajos, 10% altos
            )[0]
            
            if tipo_precio == "normal":
                # Precio normal (±10%)
                precio = precio_base * random.uniform(0.9, 1.1)
            elif tipo_precio == "bajo":
                # Precio bajo (20-30% menos)
                precio = precio_base * random.uniform(0.7, 0.8)
            elif tipo_precio == "muy_bajo":
                # Precio muy bajo (40-50% menos) - SOSPECHOSO
                precio = precio_base * random.uniform(0.5, 0.6)
            else:  # alto
                # Precio alto (40-60% más)
                precio = precio_base * random.uniform(1.4, 1.6)
            
            precio_total = precio * cantidad
            
            db.execute(
                """INSERT INTO items (licitacion_id, descripcion, cantidad, 
                   precio_unitario, precio_total) VALUES (%s, %s, %s, %s, %s)""",
                (licitacion_id, producto, cantidad, round(precio, 2), round(precio_total, 2))
            )
            
            emoji = "✅" if tipo_precio == "normal" else "⚠️"
            print(f"   {emoji} {producto}: ${precio:,.0f} ({tipo_precio})")
    
    print(f"\n✅ Datos de prueba generados exitosamente")
    print(f"\n🧪 Prueba los endpoints:")
    print("   curl http://localhost:8001/api/licitaciones")
    print("   curl http://localhost:8001/api/analizar/laptop")
    print("   curl http://localhost:8001/api/alertas")
    print("   curl http://localhost:8001/api/dashboard")

if __name__ == "__main__":
    seed()
