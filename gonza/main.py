from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from dotenv import load_dotenv
import os

load_dotenv()

app = FastAPI(title="gonza - Análisis de Licitaciones")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Importar rutas
from routes import data, analysis

app.include_router(data.router, prefix="/api", tags=["data"])
app.include_router(analysis.router, prefix="/api", tags=["analysis"])

@app.get("/health")
async def health_check():
    return {
        "status": "OK", 
        "service": "gonza - Análisis",
        "database": "PostgreSQL"
    }

@app.on_event("shutdown")
async def shutdown_event():
    from db.database import db
    db.close()

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8001))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)
