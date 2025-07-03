from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel, Field
from typing import List
from datetime import datetime
import os
from dotenv import load_dotenv
from bson import ObjectId
import pytz

# Cargar variables de entorno
load_dotenv("config.env")

app = FastAPI(title="API MongoDB", version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # O usa ["*"] para permitir todos los orígenes (solo para desarrollo)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuración de MongoDB
MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
DATABASE_NAME = os.getenv("DATABASE_NAME", "actividades")

# Cliente de MongoDB
global client, database
client = None
database = None


# --- Modelo Base ---
class ActividadBase(BaseModel):
    Nombre: str
    Categoria: str
    Descripcion: str
    Prioridad: str
    # Fecha: datetime
    Fin: datetime # El usuario define la fecha de finalización
    Estatus: bool = False

# --- Modelo de Creación ---
class ActividadCreate(ActividadBase):
    pass

# --- Modelo de Respuesta (y de la DB) ---
class Actividad(ActividadBase):
    id: str = Field(..., alias="_id")
    Fecha: datetime

    class Config:
        from_attributes = True
        populate_by_name = True
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            ObjectId: str
        }

# Eventos de la aplicación
@app.on_event("startup")
async def startup_db_client():
    global client, database
    client = AsyncIOMotorClient(MONGODB_URL)
    database = client[DATABASE_NAME]
    print("Conectado a MongoDB")

@app.on_event("shutdown")
async def shutdown_db_client():
    if client:
        client.close()
        print("Desconectado de MongoDB")

@app.get("/")
async def root():
    return {"message": "Estás conectado a FastAPI"}

# Obtener todas las actividades
@app.get("/actividades", response_model=List[Actividad])
async def obtener_actividades():
    try:
        actividades = []
        cursor = database.actividades.find()
        async for documento in cursor:
            # Convertir _id y fechas
            documento["_id"] = str(documento["_id"])
            if isinstance(documento["Fecha"], str):
                documento["Fecha"] = datetime.fromisoformat(documento["Fecha"])
            if isinstance(documento["Fin"], str):
                documento["Fin"] = datetime.fromisoformat(documento["Fin"])
            if "Estatus" not in documento:
                documento["Estatus"] = False
            actividades.append(Actividad(**documento))
        return actividades
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener las actividades: {str(e)}")

# Obtener una actividad específica
@app.get("/actividades/{actividad_id}", response_model=Actividad)
async def obtener_actividad(actividad_id: str):
    try:
        documento = await database.actividades.find_one({"_id": ObjectId(actividad_id)})
        if not documento:
            raise HTTPException(status_code=404, detail="Actividad no encontrada")
        documento["_id"] = str(documento["_id"])
        if isinstance(documento["Fecha"], str):
            documento["Fecha"] = datetime.fromisoformat(documento["Fecha"])
        if isinstance(documento["Fin"], str):
            documento["Fin"] = datetime.fromisoformat(documento["Fin"])
        if "Estatus" not in documento:
            documento["Estatus"] = False
        return Actividad(**documento)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener la actividad: {str(e)}")

# Crear una nueva actividad
@app.post("/actividades", response_model=Actividad)
async def crear_actividad(actividad: ActividadCreate):
    try:
        documento = actividad.dict()
        tz = pytz.timezone("America/Monterrey")
        documento["Fecha"] = datetime.now(tz)
        documento["Estatus"] = False  # Siempre por defecto en False
        resultado = await database.actividades.insert_one(documento)
        documento["_id"] = str(resultado.inserted_id)
        return Actividad(**documento)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al crear la actividad: {str(e)}")

# Actualizar una actividad existente
@app.put("/actividades/{actividad_id}", response_model=Actividad)
async def actualizar_actividad(actividad_id: str, actividad: ActividadCreate):
    try:
        documento = actividad.dict()
        resultado = await database.actividades.update_one(
            {"_id": ObjectId(actividad_id)},
            {"$set": documento}
        )
        if resultado.matched_count == 0:
            raise HTTPException(status_code=404, detail="Actividad no encontrada")
        documento_actualizado = await database.actividades.find_one({"_id": ObjectId(actividad_id)})
        documento_actualizado["_id"] = str(documento_actualizado["_id"])
        if isinstance(documento_actualizado["Fecha"], str):
            documento_actualizado["Fecha"] = datetime.fromisoformat(documento_actualizado["Fecha"])
        if isinstance(documento_actualizado["Fin"], str):
            documento_actualizado["Fin"] = datetime.fromisoformat(documento_actualizado["Fin"])
        if "Estatus" not in documento_actualizado:
            documento_actualizado["Estatus"] = False
        return Actividad(**documento_actualizado)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al actualizar la actividad: {str(e)}")

# Eliminar una actividad
@app.delete("/actividades/{actividad_id}")
async def eliminar_actividad(actividad_id: str):
    try:
        resultado = await database.actividades.delete_one({"_id": ObjectId(actividad_id)})
        if resultado.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Actividad no encontrada")
        return {"message": "Actividad eliminada exitosamente"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al eliminar la actividad: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
