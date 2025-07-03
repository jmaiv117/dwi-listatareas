#!/usr/bin/env python3
import uvicorn
import os
from dotenv import load_dotenv

def main():
    # Cargar variables de entorno
    load_dotenv("config.env")
    
    # Configuración del servidor
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", 8800))
    reload = os.getenv("RELOAD", "true").lower() == "true"
    
    print(f"🚀 Iniciando API de Transacciones MongoDB...")
    print(f"📍 Host: {host}")
    print(f"🔌 Puerto: {port}")
    print(f"🔄 Reload: {reload}")
    print("-" * 50)
    
    # Ejecutar el servidor
    uvicorn.run(
        "mongoapi:app",
        host=host,
        port=port,
        reload=reload,
        log_level="info"
    )

if __name__ == "__main__":
    main() 