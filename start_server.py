#!/usr/bin/env python3
"""
Script para iniciar el servidor de desarrollo
"""

import uvicorn
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv("config.env")

if __name__ == "__main__":
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", 8800))
    
    print("🚀 Iniciando servidor de actividades...")
    print(f"📍 URL: http://{host}:{port}")
    print(f"🌐 Aplicación web: http://{host}:{port}/app")
    print(f"📚 Documentación API: http://{host}:{port}/docs")
    print("⚠️  IMPORTANTE: El frontend Django debe ejecutarse en puerto 8000")
    print("=" * 50)
    
    uvicorn.run(
        "mongoapi:app",
        host=host,
        port=port,
        reload=True,
        log_level="info"
    )