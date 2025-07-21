from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, timedelta
import jwt
import bcrypt
from motor.motor_asyncio import AsyncIOMotorClient
import os

router = APIRouter(prefix="/sesion", tags=["sesion"])

# Modelos para sesión
class LoginRequest(BaseModel):
    email: str
    password: str

class LoginResponse(BaseModel):
    access_token: str
    token_type: str
    user_id: str
    email: str

class TokenData(BaseModel):
    email: Optional[str] = None

# Configuración JWT
SECRET_KEY = os.getenv("SECRET_KEY", "tu_clave_secreta_muy_segura")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 10

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

async def get_database():
    from mongoapi import database
    if database is None:
        raise HTTPException(
            status_code=500, 
            detail="Error de conexión a la base de datos. Verifica que MongoDB esté conectado."
        )
    return database

@router.post("/login", response_model=LoginResponse)
async def login(login_data: LoginRequest, db = Depends(get_database)):
    try:
        # Buscar usuario por email
        user = await db.usuarios.find_one({"email": login_data.email})
        if not user:
            raise HTTPException(status_code=401, detail="Credenciales incorrectas")
        
        # Verificar contraseña
        if not verify_password(login_data.password, user["password"]):
            raise HTTPException(status_code=401, detail="Credenciales incorrectas")
        
        # Crear token de acceso
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user["email"]}, expires_delta=access_token_expires
        )
        
        return LoginResponse(
            access_token=access_token,
            token_type="bearer",
            user_id=str(user["_id"]),
            email=user["email"]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error en el login: {str(e)}")

@router.post("/logout")
async def logout():
    return {"message": "Sesión cerrada exitosamente"}

@router.get("/verify-token")
async def verify_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=401, detail="Token inválido")
        return {"valid": True, "email": email}
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Token inválido")