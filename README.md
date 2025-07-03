# dwi-listatareas

![Logo](https://i.ibb.co/3YM5DmL5/Fast-API-b.jpg)

## Descripción General

Este proyecto es un administrador de tareas con categorías y prioridades, desarrollado con un frontend en HTML/JS y un backend en FastAPI, utilizando MongoDB Atlas como base de datos.

![Logo](https://i.ibb.co/8nTwFhxx/Bloc-tareas.png)

---

## Ciclo de Ejecución

### 1. Infraestructura y Preparación

- **MongoDB Atlas:**
  - Se crea una cuenta y un clúster gratuito.
  - Se configuran usuarios y direcciones IP autorizadas.
  - Se obtiene y prueba el string de conexión.

- **Proyecto Local:**
  - Se crea la carpeta del proyecto y se inicializa un entorno virtual (`venv`).
  - Se instalan las dependencias necesarias (`Django`, `FastAPI`, etc.).
  - Se inicializan los servicios de Django y FastAPI.
  - Se configura el control de versiones con Git y GitHub.

### 2. Desarrollo y Versionado
- El código fuente se gestiona con Git y se almacena en GitHub.
- Se mantiene un archivo de seguimiento (`docs/Seguimiento.txt`) y diagramas de arquitectura en la carpeta `docs/`.

### 3. Ejecución del Sistema
- **Frontend:**
  - El usuario interactúa con una SPA (Single Page Application) en HTML/JS.
  - Todas las operaciones de tareas (crear, leer, actualizar, eliminar) se realizan mediante llamadas a la API REST de FastAPI.

- **Backend:**
  - FastAPI expone endpoints RESTful para CRUD sobre la colección `actividades` en MongoDB.
  - El backend se conecta a MongoDB Atlas usando el string de conexión configurado.

- **Pruebas:**
  - Se pueden realizar pruebas de los endpoints usando `curl` (ver ejemplos en `docs/testing.txt`).

### 4. Flujo General

![Logo](https://i.ibb.co/HpG2YyQJ/Diagrama-dw-listatareas-2.png)

- El usuario accede al frontend y gestiona tareas.
- El frontend realiza peticiones a la API de FastAPI.
- FastAPI procesa las peticiones y opera sobre la base de datos MongoDB.

### 5. Pruebas de Endpoints (ejemplos)
- **GET todas las actividades:**
  ```bash
  curl -X GET http://localhost:8000/actividades
  ```
- **POST nueva actividad:**
  ```bash
  curl -X POST http://localhost:8000/actividades -H "Content-Type: application/json" -d '{"Nombre": "Tarea de ejemplo","Categoria": "Trabajo","Descripcion": "Completar el informe mensual","Prioridad": "Alta","Fin": "2024-06-30T18:00:00"}'
  ```
- **PUT actualizar actividad:**
  ```bash
  curl -X PUT http://localhost:8000/actividades/<_id> -H "Content-Type: application/json" -d '{ "Nombre": "Tarea actualizada", ... }'
  ```
- **DELETE eliminar actividad:**
  ```bash
  curl -X DELETE http://localhost:8000/actividades/<_id>
  ```

---

## Autoría y Colaboradores
- Proyecto inicializado y gestionado por JoseStalker117.
- Colaboradores: Dany77103.
