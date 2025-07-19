from fastapi import APIRouter, HTTPException, Depends, Header
from pydantic import BaseModel, Field
from typing import List, Dict, Union, Optional
from dotenv import load_dotenv
from datetime import datetime
from bson import ObjectId
import bcrypt
import base64
import jwt
import os
from cryptography.fernet import Fernet, InvalidToken

load_dotenv("config.env")
router = APIRouter(prefix="/actividades", tags=["actividades"])

# --- Utilidades de Encriptación ---
class CryptoUtils:
    @staticmethod
    def get_fernet():
        key = os.getenv("FERNET_KEY", "clave_generada")
        if not key:
            raise Exception("FERNET_KEY no configurada en variables de entorno")
        return Fernet(key.encode() if isinstance(key, str) else key)

    @staticmethod
    def encrypt_data(data: str) -> str:
        """Encripta datos sensibles usando Fernet"""
        if not data:
            return data
        f = CryptoUtils.get_fernet()
        return f.encrypt(data.encode('utf-8')).decode('utf-8')

    @staticmethod
    def decrypt_data(data: str) -> str:
        """Desencripta datos sensibles usando Fernet"""
        if not data:
            return data
        f = CryptoUtils.get_fernet()
        try:
            return f.decrypt(data.encode('utf-8')).decode('utf-8')
        except (InvalidToken, Exception):
            return data  # Si no se puede desencriptar, retorna el valor original

    @staticmethod
    def encrypt_field_if_sensitive(field_name: str, value: str) -> str:
        """Encripta campos sensibles específicos"""
        sensitive_fields = ['Descripcion', 'mailto']
        if field_name in sensitive_fields and value:
            return CryptoUtils.encrypt_data(value)
        return value
    
    @staticmethod
    def encrypt_mailto_list(mailto_list: List[Dict[str, str]]) -> List[Dict[str, str]]:
        """Encripta emails en la lista mailto"""
        if not mailto_list:
            return mailto_list
        
        encrypted_list = []
        for item in mailto_list:
            encrypted_item = {}
            for key, value in item.items():
                if key in ('to', 'cc', 'bcc') and value:
                    encrypted_item[key] = CryptoUtils.encrypt_data(value)
                else:
                    encrypted_item[key] = value
            encrypted_list.append(encrypted_item)
        return encrypted_list

    @staticmethod
    def decrypt_mailto_list(mailto_list: List[Dict[str, str]]) -> List[Dict[str, str]]:
        """Desencripta emails en la lista mailto"""
        if not mailto_list:
            return mailto_list
        
        decrypted_list = []
        for item in mailto_list:
            decrypted_item = {}
            for key, value in item.items():
                if key in ('to', 'cc', 'bcc') and value:
                    decrypted_item[key] = CryptoUtils.decrypt_data(value)
                else:
                    decrypted_item[key] = value
            decrypted_list.append(decrypted_item)
        return decrypted_list

# --- Modelo Base ---
class ActividadBase(BaseModel):
    Nombre: str
    Categoria: str
    Descripcion: str
    Prioridad: Optional[int] = None
    Fin: Union[datetime, Dict[str, str]] # Puede venir como string o {"$date": ...}
    Estatus: str
    mailto: Optional[List[Dict[str, str]]] = []

    @staticmethod
    def normalize_fecha(fecha):
        if isinstance(fecha, dict) and "$date" in fecha:
            return datetime.fromisoformat(fecha["$date"].replace('Z', '+00:00'))
        if isinstance(fecha, str):
            return datetime.fromisoformat(fecha)
        return fecha

    @staticmethod
    def normalize_mailto(mailto):
        if mailto is None:
            return []
        if isinstance(mailto, list):
            # Solo aceptar claves to, cc, bcc
            return [
                {k: v for k, v in d.items() if k in ("to", "cc", "bcc")}
                for d in mailto if isinstance(d, dict)
            ]
        return []

    @classmethod
    def normalize(cls, data):
        data = dict(data)
        data["Fin"] = cls.normalize_fecha(data.get("Fin"))
        if "Fecha" in data:
            data["Fecha"] = cls.normalize_fecha(data["Fecha"])
        data["mailto"] = cls.normalize_mailto(data.get("mailto"))
        # Eliminar normalización de Estatus, solo guardar el string tal cual
        return data
    
    @classmethod
    def encrypt_sensitive_data(cls, data):
        """Encripta datos sensibles antes de guardar en la base de datos"""
        data = dict(data)
        # Encriptar campos sensibles si existen
        for field in ["Descripcion", "Categoria", "Nombre"]:
            if field in data and data[field]:
                data[field] = CryptoUtils.encrypt_data(data[field])
        # Encriptar emails en mailto
        if "mailto" in data and data["mailto"]:
            data["mailto"] = CryptoUtils.encrypt_mailto_list(data["mailto"])
        return data

    @classmethod
    def decrypt_sensitive_data(cls, data):
        """Desencripta datos sensibles para mostrar al usuario"""
        data = dict(data)
        for field in ["Descripcion", "Categoria", "Nombre"]:
            if field in data and data[field]:
                data[field] = CryptoUtils.decrypt_data(data[field])
        if "mailto" in data and data["mailto"]:
            data["mailto"] = CryptoUtils.decrypt_mailto_list(data["mailto"])
        return data

# --- Modelo de Creación ---
class ActividadCreate(ActividadBase):
    pass

# --- Modelo de Respuesta (y de la DB) ---
class Actividad(ActividadBase):
    id: str = Field(..., alias="_id")
    Fecha: Union[datetime, Dict[str, str]]
    usuario_id: Optional[str] = None

    class Config:
        from_attributes = True
        populate_by_name = True
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            ObjectId: str
        }

async def get_database():
    from mongoapi import database
    if database is None:
        raise HTTPException(
            status_code=500, 
            detail="Error de conexión a la base de datos. Verifica que MongoDB esté conectado."
        )
    return database

# Configuración JWT
SECRET_KEY = os.getenv("SECRET_KEY", "tu_clave_secreta_muy_segura")
ALGORITHM = "HS256"

async def get_current_user(authorization: str = Header(None), db = Depends(get_database)):
    """Obtiene el usuario actual desde el token JWT"""
    if not authorization:
        raise HTTPException(status_code=401, detail="Token de autorización requerido")
    
    try:
        # Extraer token del header "Bearer <token>"
        token = authorization.replace("Bearer ", "")
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=401, detail="Token inválido")
        
        # Buscar usuario en la base de datos
        user = await db.usuarios.find_one({"email": email})
        if not user:
            raise HTTPException(status_code=401, detail="Usuario no encontrado")
        
        return {"user_id": str(user["_id"]), "email": user["email"]}
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Token inválido")

# Obtener todas las actividades del usuario autenticado
@router.get("/", response_model=List[Actividad])
async def obtener_actividades(current_user = Depends(get_current_user), db = Depends(get_database)):
    try:
        actividades = []
        cursor = db.actividades.find({"usuario_id": current_user["user_id"]})
        async for documento in cursor:
            documento["_id"] = str(documento["_id"])
            # Normalizar campos
            doc_norm = ActividadBase.normalize(documento)
            # Desencriptar campos sensibles
            doc_norm = ActividadBase.decrypt_sensitive_data(doc_norm)
            actividades.append(Actividad(**{**doc_norm, "_id": documento["_id"], "Fecha": doc_norm.get("Fecha", datetime.now()), "usuario_id": documento.get("usuario_id")}))
        return actividades
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener las actividades: {str(e)}")

# Obtener una actividad específica del usuario autenticado
@router.get("/{actividad_id}", response_model=Actividad)
async def obtener_actividad(actividad_id: str, current_user = Depends(get_current_user), db = Depends(get_database)):
    try:
        documento = await db.actividades.find_one({"_id": ObjectId(actividad_id), "usuario_id": current_user["user_id"]})
        if not documento:
            raise HTTPException(status_code=404, detail="Actividad no encontrada")
        documento["_id"] = str(documento["_id"])
        doc_norm = ActividadBase.normalize(documento)
        doc_norm = ActividadBase.decrypt_sensitive_data(doc_norm)
        return Actividad(**{**doc_norm, "_id": documento["_id"], "Fecha": doc_norm.get("Fecha", datetime.now()), "usuario_id": documento.get("usuario_id")})
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener la actividad: {str(e)}")

# Crear una nueva actividad
@router.post("/", response_model=Actividad)
async def crear_actividad(actividad: ActividadCreate, current_user = Depends(get_current_user), db = Depends(get_database)):
    try:
        documento = actividad.dict()
        documento["Fecha"] = datetime.now()
        documento["usuario_id"] = current_user["user_id"]  # Asociar con el usuario autenticado
        documento = ActividadBase.normalize(documento)
        # Encriptar datos sensibles antes de guardar
        documento = ActividadBase.encrypt_sensitive_data(documento)
        resultado = await db.actividades.insert_one(documento)
        
        # Para la respuesta, usar los datos originales (sin encriptar)
        documento_respuesta = actividad.dict()
        documento_respuesta["Fecha"] = datetime.now()
        documento_respuesta["usuario_id"] = current_user["user_id"]
        documento_respuesta = ActividadBase.normalize(documento_respuesta)
        documento_respuesta["_id"] = str(resultado.inserted_id)
        
        return Actividad(**{**documento_respuesta, "Fecha": documento_respuesta.get("Fecha", datetime.now())})
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al crear la actividad: {str(e)}")

# Actualizar una actividad existente
@router.put("/{actividad_id}", response_model=Actividad)
async def actualizar_actividad(actividad_id: str, actividad: ActividadCreate, current_user = Depends(get_current_user), db = Depends(get_database)):
    try:
        documento = actividad.dict()
        documento = ActividadBase.normalize(documento)
        # Encriptar datos sensibles antes de actualizar
        documento_encriptado = ActividadBase.encrypt_sensitive_data(documento)
        
        resultado = await db.actividades.update_one(
            {"_id": ObjectId(actividad_id), "usuario_id": current_user["user_id"]},
            {"$set": documento_encriptado}
        )
        if resultado.matched_count == 0:
            raise HTTPException(status_code=404, detail="Actividad no encontrada")
        
        # Para la respuesta, usar los datos originales (sin encriptar)
        documento_respuesta = documento.copy()
        documento_respuesta["_id"] = actividad_id
        documento_respuesta["usuario_id"] = current_user["user_id"]
        
        return Actividad(**{**documento_respuesta, "_id": actividad_id, "Fecha": documento_respuesta.get("Fecha", datetime.now())})
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al actualizar la actividad: {str(e)}")

# Eliminar una actividad
@router.delete("/{actividad_id}")
async def eliminar_actividad(actividad_id: str, current_user = Depends(get_current_user), db = Depends(get_database)):
    try:
        resultado = await db.actividades.delete_one({"_id": ObjectId(actividad_id), "usuario_id": current_user["user_id"]})
        if resultado.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Actividad no encontrada")
        return {"message": "Actividad eliminada exitosamente"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al eliminar la actividad: {str(e)}")

# Alternar el estado entre 'Cerrado' y 'En revisión'
@router.patch("/{actividad_id}/alternar_estado", response_model=Actividad)
async def alternar_estado_actividad(actividad_id: str, current_user = Depends(get_current_user), db = Depends(get_database)):
    try:
        documento = await db.actividades.find_one({"_id": ObjectId(actividad_id), "usuario_id": current_user["user_id"]})
        if not documento:
            raise HTTPException(status_code=404, detail="Actividad no encontrada")
        estatus_actual = documento.get("Estatus", "En revisión")
        if estatus_actual == "Cerrado":
            nuevo_estatus = "En revisión"
        else:
            nuevo_estatus = "Cerrado"
        await db.actividades.update_one(
            {"_id": ObjectId(actividad_id), "usuario_id": current_user["user_id"]},
            {"$set": {"Estatus": nuevo_estatus}}
        )
        documento["Estatus"] = nuevo_estatus
        documento["_id"] = str(documento["_id"])
        doc_norm = ActividadBase.normalize(documento)
        return Actividad(**{**doc_norm, "_id": documento["_id"], "Fecha": doc_norm.get("Fecha", documento.get("Fecha")), "usuario_id": documento.get("usuario_id")})
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al alternar el estado: {str(e)}")

# Endpoint para verificar integridad de datos encriptados
@router.get("/{actividad_id}/verify_encryption")
async def verificar_encriptacion(actividad_id: str, current_user = Depends(get_current_user), db = Depends(get_database)):
    try:
        documento = await db.actividades.find_one({"_id": ObjectId(actividad_id), "usuario_id": current_user["user_id"]})
        if not documento:
            raise HTTPException(status_code=404, detail="Actividad no encontrada")
        
        encryption_status = {
            "actividad_id": actividad_id,
            "descripcion_encriptada": bool(documento.get("Descripcion", "").startswith("$2b$") if documento.get("Descripcion") else False),
            "mailto_encriptado": False,
            "total_emails_encriptados": 0
        }
        
        # Verificar encriptación de emails
        if documento.get("mailto"):
            emails_encriptados = 0
            for item in documento["mailto"]:
                for key in ['to', 'cc', 'bcc']:
                    if key in item and item[key]:
                        try:
                            # Verificar si está en base64 y es un hash bcrypt
                            decoded = base64.b64decode(item[key])
                            if decoded.startswith(b'$2b$'):
                                emails_encriptados += 1
                        except:
                            pass
            
            encryption_status["total_emails_encriptados"] = emails_encriptados
            encryption_status["mailto_encriptado"] = emails_encriptados > 0
        
        return encryption_status
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al verificar encriptación: {str(e)}")

@router.post("/reordenar_prioridad")
async def reordenar_prioridad(current_user = Depends(get_current_user), db = Depends(get_database)):
    try:
        # Seleccionar actividades del usuario excluyendo estatus 'Finalizado' y 'Cerrado'
        filtro = {
            "usuario_id": current_user["user_id"],
            "Estatus": {"$nin": ["Finalizado", "Cerrado"]}
        }
        actividades = []
        cursor = db.actividades.find(filtro)
        async for doc in cursor:
            doc["_id"] = str(doc["_id"])
            actividades.append(doc)
        # Separar actividades con prioridad numérica y nula
        actividades_con_prioridad = [a for a in actividades if a.get("Prioridad") is not None]
        actividades_sin_prioridad = [a for a in actividades if a.get("Prioridad") is None]
        # Ordenar por prioridad ascendente
        actividades_con_prioridad.sort(key=lambda x: x.get("Prioridad", 99999))
        # Reasignar prioridades consecutivas a partir de 1, manteniendo duplicados
        nueva_prioridad = 1
        prioridad_anterior = None
        for doc in actividades_con_prioridad:
            prioridad_actual = doc.get("Prioridad")
            # Si la prioridad actual es diferente a la anterior, incrementar el contador
            if prioridad_actual != prioridad_anterior:
                nueva_prioridad += 1
            # Asignar la nueva prioridad (mantener la misma si es duplicado)
            await db.actividades.update_one(
                {"_id": ObjectId(doc["_id"]), "usuario_id": current_user["user_id"]},
                {"$set": {"Prioridad": nueva_prioridad - 1}}
            )
            doc["Prioridad"] = nueva_prioridad - 1
            prioridad_anterior = prioridad_actual
        # Las de prioridad nula permanecen igual
        # Unir ambas listas para la respuesta
        actividades_final = actividades_con_prioridad + actividades_sin_prioridad
        # Devolver la lista reorganizada (opcional: desencriptar campos)
        actividades_final = [ActividadBase.decrypt_sensitive_data(ActividadBase.normalize(doc)) for doc in actividades_final]
        return {"message": "Prioridades reorganizadas exitosamente (nulos conservados)", "actividades": actividades_final}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al reorganizar prioridades: {str(e)}")