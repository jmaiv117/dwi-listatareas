from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
from contextlib import asynccontextmanager
import os
from dotenv import load_dotenv

# Importar routers
from rutas.sesion import router as sesion_router
from rutas.usuario import router as usuario_router
from rutas.actividades import router as actividades_router

# Cargar variables de entorno
load_dotenv("config.env")

# Configuración de MongoDB
MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
DATABASE_NAME = os.getenv("DATABASE_NAME", "listas")

# Cliente de MongoDB
client = None
database = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    global client, database
    try:
        print(f"🔌 Intentando conectar a MongoDB...")
        print(f"📍 URL: {MONGODB_URL}")
        print(f"📍 Database: {DATABASE_NAME}")
        
        client = AsyncIOMotorClient(MONGODB_URL)
        
        # Probar la conexión
        await client.admin.command('ping')
        print("✅ Ping a MongoDB exitoso")
        
        database = client[DATABASE_NAME]
        print(f"✅ Conectado a MongoDB - Database: {DATABASE_NAME}")
        
        # Listar colecciones para verificar acceso
        collections = await database.list_collection_names()
        print(f"📋 Colecciones disponibles: {collections}")
        
    except Exception as e:
        print(f"❌ Error conectando a MongoDB: {e}")
        print(f"❌ Tipo de error: {type(e).__name__}")
        database = None
        client = None
    
    yield
    
    # Shutdown
    if client:
        client.close()
        print("🔌 Desconectado de MongoDB")

app = FastAPI(title="API MongoDB", version="1.0.0", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # O usa ["*"] para permitir todos los orígenes (solo para desarrollo)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# FastAPI solo maneja la API - Los archivos estáticos los sirve Django

# Incluir routers
app.include_router(sesion_router)
app.include_router(usuario_router)
app.include_router(actividades_router)

@app.get("/")
async def root():
    return {"message": "Estás conectado a FastAPI"}

# Endpoint de información - El frontend está en Django (puerto 8000)
@app.get("/info")
async def get_info():
    return {
        "message": "API FastAPI funcionando correctamente",
        "frontend_url": "http://localhost:8000",
        "api_docs": "http://localhost:8800/docs"
    }

@app.get("/health")
async def health_check():
    """Endpoint para verificar el estado de la API y MongoDB"""
    try:
        # Verificar conexión a MongoDB
        if database is None:
            return {
                "status": "error",
                "api": "ok",
                "database": "disconnected",
                "message": "MongoDB no está conectado"
            }
        
        # Probar operación en MongoDB
        await database.command("ping")
        collections = await database.list_collection_names()
        
        return {
            "status": "ok",
            "api": "ok",
            "database": "connected",
            "database_name": DATABASE_NAME,
            "collections": collections,
            "message": "Todos los servicios funcionando correctamente"
        }
    except Exception as e:
        return {
            "status": "error",
            "api": "ok",
            "database": "error",
            "error": str(e),
            "message": "Error en la conexión a MongoDB"
        }



if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8800)
