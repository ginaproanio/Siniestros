# 🚀 Configuración de Railway - Sistema de Siniestros

## 📋 **ESTADO ACTUAL: SERVICIOS SEPARADOS FUNCIONANDO**

### ✅ **Configuración Implementada**
- **Frontend**: Servicio React independiente
- **Backend**: Servicio FastAPI independiente
- **Base de Datos**: PostgreSQL integrada en Railway
- **Almacenamiento**: AWS S3 configurado

## 🏗️ **ESTRUCTURA DE SERVICIOS**

### **1. Servicio Frontend (React)**
- **URL**: `https://siniestros-production.up.railway.app/`
- **Root Directory**: `frontend/`
- **Framework**: React + TypeScript + Vite
- **Variables de Entorno**:
  ```bash
  REACT_APP_BACKEND_URL=https://siniestros-production.up.railway.app/
  ```

### **2. Servicio Backend (FastAPI)**
- **URL**: Railway asigna automáticamente (ej: `https://siniestros-production.up.railway.app/`)
- **Root Directory**: `backend/`
- **Framework**: FastAPI + SQLAlchemy + PostgreSQL
- **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- **Reset BD Automático**: Se ejecuta en cada startup (DROP ALL + CREATE ALL)

#### **Variables de Entorno del Backend**:
```bash
# Base de datos (Railway asigna automáticamente)
DATABASE_URL=postgresql://[usuario]:[password]@postgres.railway.internal:5432/railway

# AWS S3 (requeridas para upload de imágenes)
AWS_ACCESS_KEY_ID=tu_access_key
AWS_SECRET_ACCESS_KEY=tu_secret_key
AWS_DEFAULT_REGION=us-east-2
S3_BUCKET_NAME=siniestrossusiespinosa

# CORS (permitir requests del frontend)
ALLOWED_ORIGINS=https://siniestros-production.up.railway.app/

# Logging (deshabilitar en producción por seguridad)
LOG_BODY=false
```

## 🔧 **CONFIGURACIÓN PASO A PASO**

### **Paso 1: Verificar Servicios Existentes**
1. Ve a tu proyecto Railway "Siniestros"
2. Deberías tener **2 servicios**:
   - `frontend` (React)
   - `backend` (FastAPI)

### **Paso 2: Configurar Variables de Entorno**
Para cada servicio, configura las variables requeridas en la sección "Variables" del dashboard.

### **Paso 3: Verificar Despliegue**
- **Frontend**: Debe cargar la aplicación React
- **Backend**: Debe responder en `/health`
- **Base de Datos**: Railway crea automáticamente la instancia PostgreSQL

## 📊 **ENDPOINTS DISPONIBLES**

### **API REST Endpoints**
```bash
# Health check
GET /health

# Debug y diagnóstico
GET /debug/db
GET /debug/analyze-db
POST /debug/create-test-data
POST /debug/reset-database

# CRUD Siniestros
GET /api/v1/siniestros/           # Listar siniestros
POST /api/v1/siniestros/          # Crear siniestro
GET /api/v1/siniestros/{id}       # Obtener siniestro
PUT /api/v1/siniestros/{id}       # Actualizar siniestro
DELETE /api/v1/siniestros/{id}    # Eliminar siniestro

# PDFs
GET /api/v1/{id}/generar-pdf                    # PDF con firma
GET /api/v1/{id}/generar-pdf-sin-firma          # PDF sin firma
GET /api/v1/diagnostico-pdf                     # Diagnóstico PDF
GET /api/v1/test-pdf                            # PDF de prueba

# Documentación API
GET /docs                                       # Swagger UI
GET /redoc                                      # ReDoc
```

## 🎯 **FORMULARIOS COMPLETAMENTE PARAMETRIZADOS**

### **Campos Requeridos en "Registro de Siniestro"**
El formulario incluye **TODOS** los campos necesarios para el Informe de Investigación:

#### **DATOS DEL SINIESTRO**
- Compañía de Seguros
- Número de Reclamo
- Fecha del Siniestro
- **Fecha Reportado** ← Campo agregado
- Dirección del Siniestro
- Ubicación Georreferenciada
- Daños a Terceros
- Ejecutivo a Cargo
- Fecha de Designación
- **Cobertura** ← Campo agregado

#### **ASEGURADO, BENEFICIARIO, CONDUCTOR, OBJETO ASEGURADO**
- **Todos los campos** de cada entidad relacionada

#### **DECLARACIÓN DEL SINIESTRO** ← Sección nueva
- Fecha de Declaración del Siniestro
- Persona que Declara (Asegurado/Conductor/Otro)
- Cédula/Nombre/Relación de quien declara

#### **MISIVA DE INVESTIGACIÓN** ← Campo nuevo
- Solicitud específica de la aseguradora (no se muestra en PDF)

## 🚀 **DEPLOYMENT AUTOMÁTICO**

### **Triggers de Redeploy**
- **Push a `main`**: Railway redeploy automáticamente
- **Reset BD automático**: Se ejecuta en cada startup (DROP ALL + CREATE ALL)
- **Sin migraciones**: No hay sistema de migraciones incrementales
- **Variables de entorno**: Se aplican sin redeploy manual

### **Logs y Debugging**
- **Railway Dashboard**: Logs en tiempo real
- **Endpoint de diagnóstico**: `/debug/analyze-db`
- **Health Check**: `/health`

## ✅ **VERIFICACIÓN POST-DEPLOY**

### **Checklist Funcional**
- [ ] Frontend carga correctamente
- [ ] Formulario de creación funciona
- [ ] Formulario de edición funciona
- [ ] PDFs se generan correctamente
- [ ] Imágenes se suben a S3
- [ ] Base de datos tiene datos correctos

### **URLs de Verificación**
- **Aplicación**: `https://siniestros-production.up.railway.app/`
- **API Docs**: `https://[backend-url]/docs`
- **Health Check**: `https://[backend-url]/health`
- **Diagnóstico BD**: `https://[backend-url]/debug/analyze-db`

## 🔐 **SEGURIDAD**

### **Variables Sensibles**
- ✅ AWS credentials configuradas como variables de entorno
- ✅ DATABASE_URL asignada automáticamente por Railway
- ✅ LOG_BODY=false en producción
- ✅ CORS configurado correctamente

### **Certificados SSL**
- ✅ Railway proporciona HTTPS automáticamente
- ✅ Certificados válidos y renovados automáticamente

## 📞 **SOPORTE**

Si encuentras problemas:
1. Revisa los logs en Railway Dashboard
2. Usa el endpoint `/debug/analyze-db` para diagnosticar BD
3. Verifica las variables de entorno
4. Contacta al equipo de desarrollo

---

**Última actualización**: Diciembre 2025
**Estado**: ✅ **PRODUCTION READY**
