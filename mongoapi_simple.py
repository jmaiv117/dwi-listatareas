#!/usr/bin/env python3
"""
Versión simplificada de FastAPI sin MongoDB para testing
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import os

# Crear app
app = FastAPI(title="API Actividades (Modo Test)", version="1.0.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "FastAPI funcionando en modo test", "status": "OK"}

@app.get("/info")
async def get_info():
    return {
        "message": "API FastAPI funcionando correctamente",
        "frontend_url": "http://localhost:8000",
        "api_docs": "http://localhost:8080/docs",
        "mode": "test_without_mongodb"
    }

# Endpoints de prueba para autenticación
@app.post("/usuarios/")
async def crear_usuario_test():
    return {"message": "Endpoint de usuarios funcionando (modo test)", "user_id": "test123"}

@app.post("/sesion/login")
async def login_test():
    return {
        "access_token": "test_token_123",
        "token_type": "bearer",
        "user_id": "test123",
        "email": "test@example.com"
    }

@app.get("/sesion/verify-token")
async def verify_token_test():
    return {"valid": True, "email": "test@example.com"}

if __name__ == "__main__":
    print("🧪 Iniciando FastAPI en modo test (sin MongoDB)...")
    print("📍 URL: http://localhost:8080")
    print("📚 Docs: http://localhost:8080/docs")
    print("=" * 50)
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8080,
        log_level="info"
    )