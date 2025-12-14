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
    # Solo loguear body en desarrollo, no en producción por seguridad
    if os.getenv("LOG_BODY", "true").lower() == "true" and request.method in ["POST", "PUT", "PATCH"]:
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

@app.delete("/debug/clear-database")
async def clear_database():
    """⚠️ PELIGROSO: Endpoint para limpiar TODOS los datos de prueba de la base de datos"""
    logger.warning("🚨 INICIANDO LIMPIEZA COMPLETA DE BASE DE DATOS")

    try:
        from app.database import SessionLocal
        from app import models

        db = SessionLocal()

        # Contar registros antes de eliminar
        siniestros_count = db.query(models.Siniestro).count()
        asegurados_count = db.query(models.Asegurado).count()
        beneficiarios_count = db.query(models.Beneficiario).count()
        conductores_count = db.query(models.Conductor).count()
        objetos_count = db.query(models.ObjetoAsegurado).count()
        antecedentes_count = db.query(models.Antecedente).count()
        relatos_count = db.query(models.RelatoAsegurado).count()
        inspecciones_count = db.query(models.Inspeccion).count()
        testigos_count = db.query(models.Testigo).count()
        visitas_count = db.query(models.VisitaTaller).count()
        dinamicas_count = db.query(models.DinamicaAccidente).count()

        logger.info(f"📊 Registros encontrados antes de limpiar:")
        logger.info(f"  - Siniestros: {siniestros_count}")
        logger.info(f"  - Asegurados: {asegurados_count}")
        logger.info(f"  - Beneficiarios: {beneficiarios_count}")
        logger.info(f"  - Conductores: {conductores_count}")
        logger.info(f"  - Objetos asegurados: {objetos_count}")
        logger.info(f"  - Antecedentes: {antecedentes_count}")
        logger.info(f"  - Relatos: {relatos_count}")
        logger.info(f"  - Inspecciones: {inspecciones_count}")
        logger.info(f"  - Testigos: {testigos_count}")
        logger.info(f"  - Visitas taller: {visitas_count}")
        logger.info(f"  - Dinámicas accidente: {dinamicas_count}")

        # Eliminar en orden correcto (foreign keys)
        db.query(models.Testigo).delete()
        db.query(models.Inspeccion).delete()
        db.query(models.RelatoAsegurado).delete()
        db.query(models.Antecedente).delete()
        db.query(models.VisitaTaller).delete()
        db.query(models.DinamicaAccidente).delete()
        db.query(models.ObjetoAsegurado).delete()
        db.query(models.Conductor).delete()
        db.query(models.Beneficiario).delete()
        db.query(models.Asegurado).delete()
        db.query(models.Siniestro).delete()

        db.commit()

        logger.info("✅ Base de datos limpiada exitosamente")
        logger.warning("⚠️ TODOS LOS DATOS DE PRUEBA HAN SIDO ELIMINADOS")

        return {
            "message": "✅ Base de datos limpiada exitosamente",
            "registros_eliminados": {
                "siniestros": siniestros_count,
                "asegurados": asegurados_count,
                "beneficiarios": beneficiarios_count,
                "conductores": conductores_count,
                "objetos_asegurados": objetos_count,
                "antecedentes": antecedentes_count,
                "relatos_asegurados": relatos_count,
                "inspecciones": inspecciones_count,
                "testigos": testigos_count,
                "visitas_taller": visitas_count,
                "dinamicas_accidente": dinamicas_count
            },
            "warning": "⚠️ TODOS LOS DATOS HAN SIDO ELIMINADOS PERMANENTEMENTE"
        }

    except Exception as e:
        logger.error(f"❌ Error limpiando base de datos: {e}")
        db.rollback()
        return {
            "error": f"Error limpiando base de datos: {str(e)}",
            "status": "failed"
        }
    finally:
        db.close()

@app.post("/debug/apply-migrations")
async def apply_migrations():
    """Aplicar migraciones de base de datos pendientes"""
    import subprocess
    import sys
    import os

    logger.info("🔄 APLICANDO MIGRACIONES DE BASE DE DATOS")

    try:
        # Cambiar al directorio backend
        os.chdir("backend")

        # Ejecutar alembic upgrade head
        result = subprocess.run([
            sys.executable, "-m", "alembic", "upgrade", "head"
        ], capture_output=True, text=True, cwd=".")

        if result.returncode == 0:
            logger.info("✅ Migraciones aplicadas exitosamente")
            logger.info(f"Output: {result.stdout}")
            return {
                "message": "✅ Migraciones aplicadas exitosamente",
                "output": result.stdout,
                "error": result.stderr
            }
        else:
            logger.error(f"❌ Error aplicando migraciones: {result.stderr}")
            return {
                "error": f"Error aplicando migraciones: {result.stderr}",
                "output": result.stdout,
                "status": "failed"
            }

    except Exception as e:
        logger.error(f"❌ Error ejecutando migraciones: {e}")
        return {
            "error": f"Error ejecutando migraciones: {str(e)}",
            "status": "failed"
        }
