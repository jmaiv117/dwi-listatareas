from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional
from datetime import datetime
from bson import ObjectId
import bcrypt
from motor.motor_asyncio import AsyncIOMotorClient

router = APIRouter(prefix="/usuarios", tags=["usuarios"])

# Modelos para usuario
class UsuarioBase(BaseModel):
    nombre: str
    email: EmailStr
    activo: bool = True

class UsuarioCreate(UsuarioBase):
    password: str

class UsuarioUpdate(BaseModel):
    nombre: Optional[str] = None
    email: Optional[EmailStr] = None
    activo: Optional[bool] = None
    password: Optional[str] = None

class Usuario(UsuarioBase):
    id: str = Field(..., alias="_id")
    fecha_creacion: datetime
    fecha_actualizacion: datetime

    class Config:
        from_attributes = True
        populate_by_name = True
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            ObjectId: str
        }

def hash_password(password: str) -> str:
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')

async def get_database():
    from mongoapi import database
    if database is None:
        raise HTTPException(
            status_code=500, 
            detail="Error de conexión a la base de datos. Verifica que MongoDB esté conectado."
        )
    return database

@router.get("/", response_model=List[Usuario])
async def obtener_usuarios(db = Depends(get_database)):
    try:
        usuarios = []
        cursor = db.usuarios.find({}, {"password": 0})  # Excluir password del query
        async for documento in cursor:
            documento["_id"] = str(documento["_id"])
            usuarios.append(Usuario(**documento))
        return usuarios
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener usuarios: {str(e)}")

@router.get("/{usuario_id}", response_model=Usuario)
async def obtener_usuario(usuario_id: str, db = Depends(get_database)):
    try:
        documento = await db.usuarios.find_one({"_id": ObjectId(usuario_id)}, {"password": 0})  # Excluir password
        if not documento:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")
        documento["_id"] = str(documento["_id"])
        return Usuario(**documento)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener usuario: {str(e)}")

@router.post("/", response_model=Usuario)
async def crear_usuario(usuario: UsuarioCreate, db = Depends(get_database)):
    try:
        # Verificar si el email ya existe
        existing_user = await db.usuarios.find_one({"email": usuario.email})
        if existing_user:
            raise HTTPException(status_code=400, detail="El email ya está registrado")
        
        # Crear documento del usuario
        documento = usuario.dict()
        documento["password"] = hash_password(usuario.password)
        documento["fecha_creacion"] = datetime.now()
        documento["fecha_actualizacion"] = datetime.now()
        
        resultado = await db.usuarios.insert_one(documento)
        documento["_id"] = str(resultado.inserted_id)
        
        # Remover password del response
        del documento["password"]
        return Usuario(**documento)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al crear usuario: {str(e)}")

@router.put("/{usuario_id}", response_model=Usuario)
async def actualizar_usuario(usuario_id: str, usuario: UsuarioUpdate, db = Depends(get_database)):
    try:
        documento = usuario.dict(exclude_unset=True)
        
        if "password" in documento:
            documento["password"] = hash_password(documento["password"])
        
        documento["fecha_actualizacion"] = datetime.now()
        
        resultado = await db.usuarios.update_one(
            {"_id": ObjectId(usuario_id)},
            {"$set": documento}
        )
        
        if resultado.matched_count == 0:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")
        
        documento_actualizado = await db.usuarios.find_one({"_id": ObjectId(usuario_id)})
        documento_actualizado["_id"] = str(documento_actualizado["_id"])
        
        # Remover password del response
        if "password" in documento_actualizado:
            del documento_actualizado["password"]
            
        return Usuario(**documento_actualizado)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al actualizar usuario: {str(e)}")

@router.delete("/{usuario_id}")
async def eliminar_usuario(usuario_id: str, db = Depends(get_database)):
    try:
        resultado = await db.usuarios.delete_one({"_id": ObjectId(usuario_id)})
        if resultado.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")
        return {"message": "Usuario eliminado exitosamente"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al eliminar usuario: {str(e)}")

@router.patch("/{usuario_id}/toggle-status")
async def alternar_estado_usuario(usuario_id: str, db = Depends(get_database)):
    try:
        documento = await db.usuarios.find_one({"_id": ObjectId(usuario_id)})
        if not documento:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")
        
        nuevo_estado = not documento.get("activo", True)
        
        await db.usuarios.update_one(
            {"_id": ObjectId(usuario_id)},
            {"$set": {"activo": nuevo_estado, "fecha_actualizacion": datetime.now()}}
        )
        
        documento_actualizado = await db.usuarios.find_one({"_id": ObjectId(usuario_id)})
        documento_actualizado["_id"] = str(documento_actualizado["_id"])
        
        # Remover password del response
        if "password" in documento_actualizado:
            del documento_actualizado["password"]
            
        return Usuario(**documento_actualizado)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al alternar estado: {str(e)}")