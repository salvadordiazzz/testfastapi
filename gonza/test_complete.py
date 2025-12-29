import requests
import json

BASE_URL = "http://localhost:8001/api"

def print_json(data):
    print(json.dumps(data, indent=2, ensure_ascii=False))

def test_complete_flow():
    print("🧪 Testing flujo completo con PostgreSQL\n")
    
    # 1. Health check
    print("1️⃣ Health Check")
    response = requests.get("http://localhost:8001/health")
    print_json(response.json())
    print()
    
    # 2. Ver licitaciones
    print("2️⃣ Licitaciones guardadas")
    response = requests.get(f"{BASE_URL}/licitaciones")
    data = response.json()
    print(f"Total: {data['total']} licitaciones")
    print()
    
    # 3. Analizar items sospechosos
    print("3️⃣ Analizando 'Laptop HP'")
    response = requests.get(f"{BASE_URL}/analizar/Laptop HP")
    data = response.json()
    
    if data['analisis']['es_anomalo']:
        print(f"⚠️  ANOMALÍA DETECTADA!")
        print(f"   Tipo: {data['analisis']['tipo']}")
        print(f"   Score: {data['analisis']['score_riesgo']}/100")
        print(f"   {data['analisis']['mensaje']}")
    else:
        print("✅ Precio normal")
    print()
    
    # 4. Ver alertas
    print("4️⃣ Alertas generadas")
    response = requests.get(f"{BASE_URL}/alertas")
    data = response.json()
    print(f"Total alertas: {data['total']}")
    print(f"   Críticas: {data['por_nivel']['critico']}")
    print(f"   Altas: {data['por_nivel']['alto']}")
    print(f"   Medias: {data['por_nivel']['medio']}")
    print()
    
    # 5. Dashboard
    print("5️⃣ Dashboard")
    response = requests.get(f"{BASE_URL}/dashboard")
    data = response.json()
    print(f"Licitaciones: {data['resumen']['total_licitaciones']}")
    print(f"Items: {data['resumen']['total_items']}")
    print(f"Alertas: {data['resumen']['total_alertas']}")
    print(f"Monto total: ${data['resumen']['monto_total_procesado']:,.0f}")
    print()
    
    print("✅ Tests completados")

if __name__ == "__main__":
    test_complete_flow()
