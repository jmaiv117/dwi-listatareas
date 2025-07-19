#!/usr/bin/env python3
"""
Script para probar la conexión a MongoDB
"""

import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
import os

# Cargar variables de entorno
load_dotenv("config.env")

async def test_mongodb():
    print("🔍 Probando conexión a MongoDB...")
    
    # Obtener configuración
    MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
    DATABASE_NAME = os.getenv("DATABASE_NAME", "actividades")
    
    print(f"📍 URL: {MONGODB_URL}")
    print(f"📍 Database: {DATABASE_NAME}")
    
    try:
        # Crear cliente
        print("🔌 Conectando...")
        client = AsyncIOMotorClient(MONGODB_URL)
        
        # Probar conexión
        await client.admin.command('ping')
        print("✅ Conexión exitosa!")
        
        # Obtener database
        database = client[DATABASE_NAME]
        print(f"✅ Database '{DATABASE_NAME}' obtenida")
        
        # Probar operación básica
        collections = await database.list_collection_names()
        print(f"📋 Colecciones disponibles: {collections}")
        
        # Probar inserción de prueba
        test_collection = database.test
        result = await test_collection.insert_one({"test": "connection", "timestamp": "now"})
        print(f"✅ Test de inserción exitoso: {result.inserted_id}")
        
        # Limpiar test
        await test_collection.delete_one({"_id": result.inserted_id})
        print("🧹 Test limpiado")
        
        # Cerrar conexión
        client.close()
        print("✅ Conexión cerrada correctamente")
        
    except Exception as e:
        print(f"❌ Error de conexión: {e}")
        print(f"❌ Tipo de error: {type(e).__name__}")
        
        # Sugerencias de solución
        print("\n💡 Posibles soluciones:")
        print("1. Verificar que la URL de MongoDB Atlas sea correcta")
        print("2. Verificar que la contraseña no tenga caracteres especiales sin escapar")
        print("3. Verificar que la IP esté en la whitelist de MongoDB Atlas")
        print("4. Verificar conectividad a internet")

if __name__ == "__main__":
    asyncio.run(test_mongodb())