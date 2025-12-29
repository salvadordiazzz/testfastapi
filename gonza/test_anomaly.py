from services.anomaly_detector import anomaly_detector

def test():
    print("Testing detector de anomalías con PostgreSQL...\n")
    
    tests = [
        ("Laptop HP", 18000, "Precio normal"),
        ("Laptop HP", 12000, "Precio bajo (~33% menos)"),
        ("Laptop HP", 8000, "Precio MUY bajo (~55% menos)"),
        ("Laptop HP", 25000, "Precio alto (~39% más)"),
        ("Laptop HP", 30000, "Precio MUY alto (~67% más)"),
    ]
    
    for i, (item, precio, descripcion) in enumerate(tests, 1):
        print(f"{i}️⃣ {descripcion}:")
        print(f"   Item: {item}, Precio: ${precio:,}")
        
        result = anomaly_detector.detect_anomaly(item, precio)
        
        print(f"   ✓ Es anómalo: {result['es_anomalo']}")
        print(f"   ✓ Tipo: {result['tipo']}")
        print(f"   ✓ Score de riesgo: {result['score_riesgo']}/100")
        
        if result['es_anomalo']:
            print(f"   ✓ {result['mensaje']}")
        
        if result.get('estadisticas'):
            stats = result['estadisticas']
            print(f"   ✓ Promedio histórico: ${stats['precio_promedio']:,.2f}")
            print(f"   ✓ Muestras: {stats['muestras']}")
        
        print()

if __name__ == "__main__":
    test()
