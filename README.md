# Sistema de Actividades con Autenticación

Sistema completo de gestión de actividades con autenticación JWT, encriptación bcrypt y interfaz web moderna.

## 🚀 Características

- **Autenticación JWT**: Login y registro de usuarios
- **Encriptación bcrypt**: Protección de datos sensibles
- **Actividades por usuario**: Cada usuario ve solo sus actividades
- **Interfaz web moderna**: Bootstrap 5 + JavaScript vanilla
- **API REST completa**: FastAPI con documentación automática
- **Base de datos MongoDB**: Almacenamiento NoSQL

## 📋 Requisitos

- Python 3.8+
- MongoDB
- Dependencias en `requirements.txt`

## 🛠️ Instalación

1. **Clonar e instalar dependencias:**
```bash
pip install -r requirements.txt
```

2. **Configurar variables de entorno:**
```bash
cp config.env.example config.env
# Editar config.env con tus configuraciones
```

3. **Iniciar MongoDB:**
```bash
# En Windows con MongoDB instalado
mongod
```

4. **Iniciar el servidor:**
```bash
python start_server.py
```

## 🌐 Acceso

- **Aplicación web**: http://localhost:8000/app
- **API Docs**: http://localhost:8000/docs
- **API Redoc**: http://localhost:8000/redoc

## 🔐 Funcionalidades de Seguridad

### Autenticación JWT
- Tokens con expiración de 30 minutos
- Verificación automática de tokens
- Logout seguro

### Encriptación bcrypt
- Contraseñas hasheadas con salt
- Descripción de actividades encriptada
- Emails encriptados en notificaciones

### Autorización por usuario
- Cada usuario solo ve sus actividades
- Operaciones CRUD restringidas por usuario
- Validación de tokens en cada request

## 📱 Uso de la Aplicación Web

### Registro y Login
1. Accede a http://localhost:8000/app
2. Crea una cuenta nueva o inicia sesión
3. El token se guarda automáticamente

### Gestión de Actividades
- **Crear**: Botón flotante (+) en la esquina inferior derecha
- **Editar**: Botón de lápiz en cada tarjeta
- **Cambiar estado**: Botón de check/undo
- **Eliminar**: Botón de papelera (con confirmación)

### Filtros y Búsqueda
- **Búsqueda**: Por nombre o descripción
- **Estado**: Filtrar por "En revisión" o "Cerrado"
- **Categoría**: Filtrar por categorías existentes

## 🔧 API Endpoints

### Autenticación
- `POST /sesion/login` - Iniciar sesión
- `POST /sesion/logout` - Cerrar sesión
- `GET /sesion/verify-token` - Verificar token

### Usuarios
- `POST /usuarios/` - Crear usuario
- `GET /usuarios/` - Listar usuarios
- `GET /usuarios/{id}` - Obtener usuario
- `PUT /usuarios/{id}` - Actualizar usuario
- `DELETE /usuarios/{id}` - Eliminar usuario

### Actividades (requieren autenticación)
- `GET /actividades/` - Listar actividades del usuario
- `POST /actividades/` - Crear actividad
- `GET /actividades/{id}` - Obtener actividad
- `PUT /actividades/{id}` - Actualizar actividad
- `DELETE /actividades/{id}` - Eliminar actividad
- `PATCH /actividades/{id}/alternar_estado` - Cambiar estado
- `GET /actividades/{id}/verify_encryption` - Verificar encriptación

## 🗃️ Estructura de Datos

### Usuario
```json
{
  "nombre": "string",
  "email": "string",
  "password": "string (hasheado)",
  "activo": true,
  "fecha_creacion": "datetime",
  "fecha_actualizacion": "datetime"
}
```

### Actividad
```json
{
  "Nombre": "string",
  "Categoria": "string",
  "Descripcion": "string (encriptado)",
  "Prioridad": 1-3,
  "Fin": "datetime",
  "Estatus": "En revisión|Cerrado",
  "mailto": [{"to": "email", "cc": "email", "bcc": "email"}],
  "usuario_id": "string",
  "Fecha": "datetime"
}
```

## 🔒 Headers de Autenticación

Para usar la API directamente, incluye el header:
```
Authorization: Bearer <tu_token_jwt>
```

## 🐛 Solución de Problemas

### Error de conexión a MongoDB
- Verificar que MongoDB esté ejecutándose
- Comprobar la URL en `config.env`

### Token inválido
- El token expira en 30 minutos
- Hacer login nuevamente

### Error de CORS
- Verificar que el frontend esté en el mismo dominio
- Ajustar configuración CORS en `mongoapi.py`

## 🚀 Producción

Para producción, recuerda:
1. Cambiar `SECRET_KEY` en `config.env`
2. Configurar CORS específicamente
3. Usar HTTPS
4. Configurar MongoDB con autenticación
5. Usar un servidor WSGI como Gunicorn

## 📝 Notas de Desarrollo

- Los datos sensibles se encriptan automáticamente
- Las respuestas de la API muestran datos desencriptados para usabilidad
- El frontend maneja automáticamente la autenticación
- Los filtros funcionan en tiempo real