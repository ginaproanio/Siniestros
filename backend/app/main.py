from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from app.routers import siniestros
import logging
import os

# Configurar logging detallado
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Las tablas se crean automáticamente con Alembic migrations

app = FastAPI(
    title="Sistema de Informes de Siniestros API",
    description="API para gestión de informes de siniestros vehiculares",
    version="1.0.0"
)

# CORS middleware
allowed_origins = os.getenv("ALLOWED_ORIGINS", "*").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Middleware para logging detallado de requests
@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.info(f"📨 {request.method} {request.url}")
    if request.method in ["POST", "PUT", "PATCH"]:
        try:
            body = await request.body()
            logger.info(f"📦 Body: {body.decode()}")
        except Exception as e:
            logger.warning(f"⚠️ No se pudo leer el body: {e}")
    response = await call_next(request)
    logger.info(f"📤 Response status: {response.status_code}")
    return response

# Include routers
app.include_router(siniestros.router, prefix="/api/v1", tags=["siniestros"])

@app.get("/")
async def root():
    return {"message": "API de Sistema de Informes de Siniestros"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.get("/debug/db")
async def debug_database():
    """Endpoint para debug de conexión a base de datos"""
    try:
        from app.database import SessionLocal

        db = SessionLocal()
        db.execute("SELECT 1")
        db.close()
        return {"database": "connected", "status": "healthy"}
    except Exception as e:
        logger.error(f"Database connection error: {e}")
        return {"database": "error", "error": str(e)}
