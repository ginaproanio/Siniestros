# Sistema de Informes de Siniestros
Aplicación web full-stack para generar informes profesionales de investigaciones de siniestros en seguros. Utiliza React para el frontend, FastAPI para el backend, y ReportLab para crear PDFs con diseño corporativo, incluyendo mapas integrados y headers/footers automáticos.

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
1. Sube este proyecto a un repositorio Git (GitHub, GitLab, etc.).
2. Conecta el repositorio a Railway.app.
3. Railway detectará automáticamente el Procfile y railway.toml para desplegar la app.
4. La app estará disponible en la URL proporcionada por Railway.

**Nota**: Los archivos subidos e informes se guardan en la base de datos PostgreSQL. En Railway, la BD es persistente.

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
- **Vista previa en texto**: Permite revisar el contenido antes de generar el PDF.
- **Upload de evidencias**: Subida de fotos y documentos complementarios.
- **Archivos de respaldo**: Genera informes en formato TXT además del PDF.
- **Firma digital**: Soporte para firma digital de PDFs usando certificado P12.

## Arquitectura Técnica
- **Frontend**: React.js con TypeScript para formularios dinámicos avanzados
- **Backend**: FastAPI con SQLAlchemy y PostgreSQL
- **Generación de PDFs**: ReportLab con diseño profesional, tablas estructuradas, headers/footers automáticos, y disposición inteligente de imágenes y texto
- **Mapas**: StaticMap para generación de mapas estáticos integrados en PDF
- **Firma Digital**: Endesive para firma digital de PDFs
- **Almacenamiento**: Base de datos PostgreSQL para datos, archivos en Railway volumes o AWS S3

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
