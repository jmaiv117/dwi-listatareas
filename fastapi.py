from fastapi import FastAPI, HTTPException, Depends
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel
from typing import List, Optional
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

app = FastAPI(title="API MongoDB Transacciones", version="1.0.0")

# Configuración de MongoDB
MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
DATABASE_NAME = os.getenv("DATABASE_NAME", "transacciones_db")

# Cliente de MongoDB
client = None
database = None

# Modelos Pydantic
class TransaccionBase(BaseModel):
    descripcion: str
    monto: float
    tipo: str  # "ingreso" o "gasto"
    categoria: Optional[str] = None

class TransaccionCreate(TransaccionBase):
    pass

class Transaccion(TransaccionBase):
    id: str
    fecha: str
    
    class Config:
        from_attributes = True

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

# Rutas de la API
@app.get("/")
async def root():
    return {"message": "API de Transacciones MongoDB"}

@app.get("/transacciones", response_model=List[Transaccion])
async def obtener_transacciones():
    """Obtener todas las transacciones"""
    try:
        transacciones = []
        cursor = database.transacciones.find()
        async for documento in cursor:
            documento["id"] = str(documento["_id"])
            transacciones.append(Transaccion(**documento))
        return transacciones
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener transacciones: {str(e)}")

@app.post("/transacciones", response_model=Transaccion)
async def crear_transaccion(transaccion: TransaccionCreate):
    """Crear una nueva transaccion"""
    try:
        from datetime import datetime
        documento = transaccion.dict()
        documento["fecha"] = datetime.now().isoformat()
        
        resultado = await database.transacciones.insert_one(documento)
        documento["id"] = str(resultado.inserted_id)
        
        return Transaccion(**documento)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al crear transaccion: {str(e)}")

@app.get("/transacciones/{transaccion_id}", response_model=Transaccion)
async def obtener_transaccion(transaccion_id: str):
    """Obtener una transaccion específica por ID"""
    try:
        from bson import ObjectId
        documento = await database.transacciones.find_one({"_id": ObjectId(transaccion_id)})
        if not documento:
            raise HTTPException(status_code=404, detail="Transaccion no encontrada")
        
        documento["id"] = str(documento["_id"])
        return Transaccion(**documento)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener transaccion: {str(e)}")

@app.put("/transacciones/{transaccion_id}", response_model=Transaccion)
async def actualizar_transaccion(transaccion_id: str, transaccion: TransaccionCreate):
    """Actualizar una transaccion existente"""
    try:
        from bson import ObjectId
        documento = transaccion.dict()
        
        resultado = await database.transacciones.update_one(
            {"_id": ObjectId(transaccion_id)},
            {"$set": documento}
        )
        
        if resultado.matched_count == 0:
            raise HTTPException(status_code=404, detail="Transaccion no encontrada")
        
        # Obtener el documento actualizado
        documento_actualizado = await database.transacciones.find_one({"_id": ObjectId(transaccion_id)})
        documento_actualizado["id"] = str(documento_actualizado["_id"])
        
        return Transaccion(**documento_actualizado)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al actualizar transaccion: {str(e)}")

@app.delete("/transacciones/{transaccion_id}")
async def eliminar_transaccion(transaccion_id: str):
    """Eliminar una transaccion"""
    try:
        from bson import ObjectId
        resultado = await database.transacciones.delete_one({"_id": ObjectId(transaccion_id)})
        
        if resultado.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Transaccion no encontrada")
        
        return {"message": "Transaccion eliminada exitosamente"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al eliminar transaccion: {str(e)}")

@app.get("/transacciones/tipo/{tipo}")
async def obtener_transacciones_por_tipo(tipo: str):
    """Obtener transacciones por tipo (ingreso/gasto)"""
    try:
        transacciones = []
        cursor = database.transacciones.find({"tipo": tipo})
        async for documento in cursor:
            documento["id"] = str(documento["_id"])
            transacciones.append(Transaccion(**documento))
        return transacciones
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener transacciones: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
