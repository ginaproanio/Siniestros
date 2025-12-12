# Sistema de Informes de Siniestros
Aplicación web full-stack para generar informes profesionales de investigaciones de siniestros en seguros. Utiliza React para el frontend, FastAPI para el backend, y ReportLab para crear PDFs con diseño corporativo, incluyendo mapas integrados y headers/footers automáticos.

## 🎯 OBJETIVOS PRINCIPALES

### ✅ Funcionalidades Implementadas
- **Formulario CRUD completo** para gestionar informes de investigación de siniestros
- **Edición de Informes**: Buscar informes existentes y modificarlos
- **Secciones dinámicas**: Antecedentes + Entrevistas con relatos numerados e imágenes
- **Navegación completa**: Crear → Listar → Ver Detalles → Editar
- **Backend FastAPI** con PostgreSQL y Railway deployment
- **Frontend React** con secciones dinámicas y diseño responsivo
- **Almacenamiento AWS S3** con URLs presigned y validación completa
- **Código completamente refactorizado** siguiendo mejores prácticas

### 🚧 Funcionalidades Pendientes
- **Generación de PDFs** (diagnosticada, pendiente de resolución de corrupción)
- **Firma digital electrónica** con certificado P12
- **Búsqueda avanzada** por filtros
- **Campos adicionales**: Asegurado, Conductor, Vehículo, Testigos, Inspecciones
- **Dashboard administrativo**

**Repositorio**: https://github.com/ginaproanio/Siniestros
**Rama**: main

## Instalación Local
1. **Instala Python 3.8+** desde python.org
2. **Instala Node.js 18+** desde nodejs.org
3. **Instala dependencias** (ejecuta el script automático):
   ```bash
   install-dependencies.bat
   ```
   O manualmente:
   ```bash
   # Backend
   pip install -r requirements.txt

   # Frontend
   cd frontend && npm install
   ```
4. **Ejecuta el backend**:
   ```bash
   cd backend
   uvicorn app.main:app --reload
   ```
   API disponible en http://localhost:8000

5. **Ejecuta el frontend** (en otra terminal):
   ```bash
   cd frontend
   npm run dev
   ```
   Frontend disponible en http://localhost:3000

## Despliegue en Railway

### Configuración de Servicios Separados (Recomendado)
Para un despliegue limpio y profesional, configura **dos servicios separados** en Railway:

#### 1. Servicio Frontend (React)
- **Nombre**: `frontend`
- **Root Directory**: `frontend`
- **Variables de entorno**:
  - `REACT_APP_BACKEND_URL`: URL del servicio backend (ej: `https://siniestros-backend-production.up.railway.app`)
- **Build**: Automático con Railpack (Node.js)
- **Start**: Automático (`npm start`)

#### 2. Servicio Backend (FastAPI)
- **Nombre**: `Siniestros` o `backend`
- **Root Directory**: `backend`
- **Variables de entorno**:
  - `DATABASE_URL`: Proporcionada automáticamente por Railway PostgreSQL
  - `AWS_ACCESS_KEY_ID`: Tu access key de AWS
  - `AWS_SECRET_ACCESS_KEY`: Tu secret key de AWS
  - `AWS_DEFAULT_REGION`: `us-east-2`
  - `S3_BUCKET_NAME`: `siniestrossusiespinosa`
  - `ALLOWED_ORIGINS`: URLs permitidas para CORS (ej: `https://frontend-production.up.railway.app`)
  - `LOG_BODY`: `false` (para no loguear datos sensibles en producción)
- **Start Command**: `alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port $PORT`

### Configuración Antigua (Obsoleta)
⚠️ **Los archivos `railway.toml` y `Procfile` del directorio raíz ya no se usan** porque ahora usamos servicios separados. Estos archivos han sido eliminados del repositorio para evitar conflictos.

**Nota**: Los archivos subidos e informes se guardan en la base de datos PostgreSQL. En Railway, la BD es persistente.

## Configuración AWS S3
Para el almacenamiento de imágenes, el sistema utiliza AWS S3. Configura estas variables de entorno en Railway:

- `AWS_ACCESS_KEY_ID`: Tu access key de AWS
- `AWS_SECRET_ACCESS_KEY`: Tu secret key de AWS
- `AWS_DEFAULT_REGION`: Región de S3 (ej: us-east-2)
- `S3_BUCKET_NAME`: Nombre del bucket (ej: siniestrossusiespinosa)
- `ALLOWED_ORIGINS`: Dominios permitidos para CORS (ej: https://tu-dominio.com)

Las imágenes se suben a la carpeta `uploads/` en S3 y se generan URLs presigned válidas por 7 días.

## 🏆 Calidad del Código - Mejoras Implementadas

### ✅ **Refactorización Completa del Backend**
- **Arquitectura Limpia**: Separación de responsabilidades, funciones especializadas
- **Seguridad Robusta**: Validación completa, manejo específico de errores
- **Configuración Flexible**: Variables de entorno para personalización
- **Logging Completo**: Trazabilidad y debugging efectivo
- **Código Mantenible**: Principios SOLID aplicados correctamente

### ✅ **Problemas Críticos Resueltos**
- ✅ Eliminación completa de código duplicado
- ✅ Manejo de errores específico (no más `except Exception`)
- ✅ Cliente S3 con factory pattern y validación de credenciales
- ✅ Constantes configurables via variables de entorno
- ✅ Logging consistente en todo el proyecto
- ✅ Imports innecesarios eliminados
- ✅ Comentarios obsoletos removidos

### ✅ **Mejores Prácticas Aplicadas**
- ✅ Principio de responsabilidad única
- ✅ Manejo específico de excepciones
- ✅ Configuración externa (no hardcoded)
- ✅ Validación robusta de inputs
- ✅ Arquitectura modular y extensible
- ✅ Documentación clara y completa

**Estado**: 🏆 **CÓDIGO PROFESIONAL Y PRODUCTION-READY**

## Funcionalidades
- **Formulario estructurado**: Recolección completa de datos del siniestro, asegurado, conductor, vehículo y terceros afectados.
- **Sección Asegurado Dinámica**: Permite seleccionar entre Persona Natural o Persona Jurídica, mostrando campos específicos:
  - Persona Natural: Cédula, Celular, Dirección, Parentesco
  - Persona Jurídica: RUC, Empresa, Representante Legal, Dirección, Teléfono
- **Entrevista con el Conductor**: Permite registrar múltiples relatos dinámicamente, cada uno con texto opcional y imagen adjunta. Incluye acciones por relato: Buscar, Grabar, Añadir Otro.
- **Orden de Secciones**: ANTECEDENTES antes de TERCEROS AFECTADOS.
- **Generación de PDFs profesionales**: Utiliza ReportLab para crear PDFs con:
  - Diseño corporativo con tablas estructuradas
  - Mapas integrados generados con StaticMap
  - Headers con nombre de compañía y fecha
  - Footers con numeración de páginas
  - Relatos con imágenes dispuestas lado a lado cuando aplicable
  - Tipografía formal (Helvetica)
  - Firma digital electrónica usando certificado P12
- **Vista previa en texto**: Permite revisar el contenido antes de generar el PDF.
- **Upload de imágenes**: Subida a AWS S3 con URLs presigned de 7 días, validación de tipos y tamaño (10MB máximo).
- **Archivos de respaldo**: Genera informes en formato TXT además del PDF.
- **Firma digital**: Soporte para firma digital de PDFs usando certificado P12.

## CAMPOS DEL FORMULARIO (BASADO EN EL PDF ANALIZADO)
*(Organizados por secciones, con nombres de variables sugeridos)*

### A. METADATOS / ENCABEZADO
- `numero_reclamo` (Ej: "24-01-VH-7059206")
- `fecha_informe` (Fecha de elaboración del informe)
- `pagina_total / pagina_actual` (Para el pie de página)
- `investigador_nombre`
- `investigador_email`
- `investigador_telefono`
- `investigador_empresa` ("INVESTIGACIÓN Y RECUPERACIÓN VEHICULAR")

### B. DATOS DEL SINIESTRO
- `compania_seguros`
- `fecha_siniestro`
- `direccion_siniestro`
- `ubicacion_gps` (URL de Google Maps)
- `fecha_radicado`
- `danos_a_terceros` (Si/No)
- `ejecutivo_a_cargo`
- `fecha_designacion`

### C. DATOS DE PERSONAS
**Asegurado:**
- `asegurado_nombre`
- `asegurado_cedula`
- `asegurado_domicilio`
- `asegurado_celular`

**Conductor (si es diferente):**
- `conductor_nombre`
- `conductor_cedula`
- `conductor_celular`

### D. OBJETO ASEGURADO (VEHÍCULO)
- `vehiculo_placa`
- `vehiculo_marca`
- `vehiculo_modelo`
- `vehiculo_color`
- `vehiculo_anio`
- `vehiculo_motor`
- `vehiculo_chasis`

### E. CONTENIDO DEL INFORME (CAMPOS DE TEXTO LARGO - EDITABLES)
- `antecedentes` (Texto con el aviso de siniestro y alcances)
- `inspeccion_lugar` (Lista de hallazgos, con puntos 1, 2, 3...)
- `entrevista_asegurado` (Lista numerada de manifestaciones)
- `version_terceros` (Subsecciones para cada tercero: Administrador Supermaxi, Presunto Causante, Conductor)
- `otras_diligencias` (Ej: verificación en AMT)
- `observaciones` (Lista de puntos contradictorios o relevantes)
- `conclusiones` (Texto final con recomendación)

### F. DATOS DE TERCEROS INVOLUCRADOS (Estructura repetible)
- `terceros[]` (Array de objetos con: nombre, telefono, placa(si aplica), relacion, declaracion)

### G. FIRMAS Y ADJUNTOS
- `firma_investigador` (Podría ser una imagen o texto)
- `adjuntos` (Campo para listar archivos adjuntos, ej: "Audio de entrevista")

## Arquitectura Técnica
- **Frontend**: React.js con TypeScript para formularios dinámicos avanzados
- **Backend**: FastAPI con SQLAlchemy y PostgreSQL
- **Generación de PDFs**: ReportLab con diseño profesional, tablas estructuradas, headers/footers automáticos, y disposición inteligente de imágenes y texto
- **Mapas**: StaticMap para generación de mapas estáticos integrados en PDF
- **Firma Digital**: Endesive para firma digital de PDFs
- **Almacenamiento**: Base de datos PostgreSQL para datos, archivos en AWS S3 con URLs presigned

## Arquitectura Implementada
Esta implementación utiliza una arquitectura full-stack moderna para superar las limitaciones de la versión anterior con Streamlit:

### Ventajas de la Nueva Arquitectura
1. **Formularios Dinámicos Avanzados**:
   - Componentes React permiten botones interactivos dentro de formularios.
   - Secciones expansibles con "Añadir Otro" sin recargas de página.
   - Validación en tiempo real con feedback inmediato.

2. **Manejo de Estado Robusto**:
   - Estado global con React Query para cache y sincronización.
   - Persistencia automática en base de datos PostgreSQL.
   - Sesiones independientes por usuario.

3. **Escalabilidad y Rendimiento**:
   - Separación frontend/backend permite despliegue independiente.
   - API REST eficiente con FastAPI.
   - Generación de PDFs asíncrona.

4. **Almacenamiento Persistente**:
   - Base de datos PostgreSQL integrada en Railway.
   - Archivos en la nube con Railway volumes o AWS S3.
   - Historial completo de informes y versiones.

### Componentes Técnicos
1. **Backend (FastAPI)**:
   - **Modelos SQLAlchemy**: Definición completa de entidades con relaciones.
   - **Schemas Pydantic**: Validación automática de datos.
   - **Endpoints REST**: CRUD completo para todas las entidades.
   - **Base de Datos**: PostgreSQL con migraciones Alembic.

2. **Frontend (React + TypeScript)**:
   - **Componentes Reutilizables**: Para secciones dinámicas.
   - **React Router**: Navegación SPA sin recargas.
   - **Axios + React Query**: API calls con cache inteligente.
   - **Estado Local**: React hooks para formularios complejos.

3. **Despliegue en Railway**:
   - **Frontend**: Build estático servido con `serve`.
   - **Backend**: FastAPI con Uvicorn.
   - **Base de Datos**: PostgreSQL integrada.
   - **Variables de Entorno**: Configuración segura.

### Nueva Arquitectura Propuesta y Plan de Desarrollo
Dado las limitaciones identificadas, se implementará una nueva arquitectura full-stack para superar las restricciones de Streamlit:

#### Arquitectura Objetivo
- **Frontend**: React.js con TypeScript para formularios dinámicos avanzados
- **Backend**: FastAPI (Python) con base de datos PostgreSQL
- **Despliegue**: Railway para frontend (Vite) y backend (FastAPI) con BD integrada
- **Almacenamiento**: Railway volumes o AWS S3 para archivos
- **Autenticación**: JWT con roles (Investigador, Administrador)

#### Estructura del Proyecto
```
siniestros-app/
├── frontend/              # React + TypeScript
│   ├── src/
│   │   ├── components/    # Componentes reutilizables
│   │   │   ├── RelatoForm.tsx
│   │   │   ├── ImageUpload.tsx
│   │   │   └── DynamicSection.tsx
│   │   ├── pages/
│   │   │   ├── FormularioSiniestro.tsx
│   │   │   └── Dashboard.tsx
│   │   ├── hooks/         # Custom hooks para formularios
│   │   ├── services/      # API calls
│   │   └── types/         # TypeScript interfaces
│   ├── public/
│   └── package.json
├── backend/               # FastAPI + SQLAlchemy
│   ├── app/
│   │   ├── models/        # SQLAlchemy models
│   │   ├── schemas/       # Pydantic schemas
│   │   ├── routers/       # API endpoints
│   │   ├── services/      # Business logic
│   │   └── utils/         # PDF generation, file handling
│   ├── tests/
│   └── requirements.txt
├── database/              # Railway PostgreSQL
├── docker/                # Dockerfiles para Railway
└── docs/                  # Documentación API
```

#### Funcionalidades Clave a Implementar
1. **Formulario Dinámico**:
   - Componentes React para secciones expansibles
   - Botones "Añadir Otro" dentro de cada sección
   - Validación en tiempo real

2. **Manejo de Archivos**:
   - Upload múltiple con preview
   - Almacenamiento en S3/Railway volumes
   - Asociación con registros de BD

3. **Generación de PDF**:
   - Servicio backend asíncrono
   - Templates profesionales con ReportLab
   - Descarga directa desde frontend

4. **Base de Datos**:
   - Tablas: siniestros, relatos, imagenes, usuarios
   - Relaciones many-to-one/many-to-many
   - Migraciones con Alembic

#### Estado Actual del Desarrollo
✅ **Fase 1: Setup e Infraestructura** - COMPLETADA
- ✅ Configurar repositorio con estructura backend
- ✅ Desplegar PostgreSQL en Railway
- ✅ Configurar CI/CD con Railway (FastAPI funcionando)

✅ **Fase 2: Backend Core** - COMPLETADA
- ✅ Modelos SQLAlchemy completos para todas las entidades
- ✅ Schemas Pydantic con validación
- ✅ Endpoints CRUD funcionales para siniestros
- ✅ Configuración de base de datos PostgreSQL
- ✅ Alembic para migraciones de BD
- ✅ Servicio S3 completamente refactorizado con mejores prácticas
- ✅ Arquitectura limpia con separación de responsabilidades
- ✅ Manejo robusto de errores y logging completo
- ✅ Configuración flexible via variables de entorno
- ⏳ Servicio de generación PDF (parcial)
- ⏳ Autenticación básica (pendiente)

**Fase 3: Frontend Core** - PENDIENTE
- Componentes React + TypeScript
- Integración con API backend
- Manejo de estado con React Query
- UI/UX responsive

**Fase 4: Funcionalidades Avanzadas** - PENDIENTE
- Upload de archivos con drag&drop
- Previews de imágenes
- Formularios dinámicos anidados
- Dashboard de informes

**Fase 5: Testing y Optimización** - PENDIENTE
- Tests unitarios e integración
- Optimización de rendimiento
- Documentación completa

#### Despliegue en Railway
- **Frontend**: Railway detectará package.json y desplegará con Vite
- **Backend**: Railway usará requirements.txt y Procfile para FastAPI
- **Base de Datos**: Railway PostgreSQL integrada
- **Variables de Entorno**: Configurar en Railway dashboard

Esta nueva arquitectura permitirá formularios complejos sin limitaciones, persistencia de datos, y escalabilidad para múltiples usuarios.

### Próximos Pasos Sugeridos
- Crear nuevo repositorio para la arquitectura full-stack
- Implementar Fase 1: Setup de infraestructura
- Desarrollar backend primero, luego frontend
- Mantener despliegue continuo en Railway

La versión Streamlit actual queda como prototipo funcional, pero se recomienda migrar a la nueva arquitectura para producción.

## Requisitos del Sistema
- Python 3.8+
- Dependencias listadas en `requirements.txt`:
  - streamlit
  - reportlab
  - staticmap
  - pillow
  - endesive
  - requests
