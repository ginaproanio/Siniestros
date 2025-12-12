# Configuración de Railway - Servicios Separados

## Problema Actual
Railway está sirviendo el frontend React en lugar del backend FastAPI, causando error 405 en las llamadas API.

## Solución: Servicios Separados

### Paso 1: Crear Servicio Backend
1. **Ve a Railway** → Tu proyecto "Siniestros"
2. **Haz clic en "Add Service"**
3. **Selecciona "GitHub"**
4. **Elige el repositorio** "ginaproanio/Siniestros"
5. **En "Root Directory"** escribe: `backend`
6. **Deja la rama en "main"**
7. **Railway detectará automáticamente** `backend/Procfile` y `backend/requirements.txt`
8. **Railway creará** `https://backend-siniestros-[hash].up.railway.app/`

### Paso 2: Configurar Variable de Entorno
1. **En el servicio backend** (el nuevo)
2. **Ve a "Variables"**
3. **Agrega:**
   - Key: `DATABASE_URL`
   - Value: `postgresql://postgres:IvyEBvPGcjQHeMwRlXrzexzBxEYRGtVW@postgres.railway.internal:5432/railway`

### Paso 3: Actualizar Frontend
1. **En el servicio frontend** (el original)
2. **Ve a "Variables"**
3. **Agrega:**
   - Key: `REACT_APP_BACKEND_URL`
   - Value: `https://backend-siniestros-[hash].up.railway.app/` (URL del backend)

## Resultado Final
- **Frontend**: `https://siniestros-production.up.railway.app/`
- **Backend**: `https://backend-siniestros-[hash].up.railway.app/`
- **API Docs**: `https://backend-siniestros-[hash].up.railway.app/docs`

## Verificación
1. Frontend carga correctamente
2. Formulario puede enviar datos al backend
3. Datos se guardan en PostgreSQL

## URLs de Referencia
- Documentación API: `/docs`
- Health check: `/health`
- Debug DB: `/debug/db`
- Crear siniestro: `POST /api/v1/`
