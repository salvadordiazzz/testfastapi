from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from dotenv import load_dotenv
import os
from routes import upload

load_dotenv()

app = FastAPI(title="Salva - Procesamiento de Licitaciones")

# noinspection PyTypeChecker
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(upload.router, prefix="/api", tags=["upload"])

@app.get("/health")
async def health_check():
    return {"status": "OK", "service": "Salva - Procesamiento"}

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)
