from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from app.routers import siniestros
import logging
import os
from datetime import datetime

# Configurar logging detallado
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Sistema de Informes de Siniestros API",
    description="API para gestión de informes de siniestros vehiculares",
    version="1.0.0"
)

# Database initialization - COMPLETE RESET on every startup
@app.on_event("startup")
async def startup_event():
    """🔥 COMPLETE DATABASE RESET: Drop all tables and recreate from scratch"""
    import logging
    logger = logging.getLogger(__name__)

    logger.info("🔥 INICIANDO RESET COMPLETO DE BASE DE DATOS...")

    try:
        from app.database import engine, Base
        from app import models
        import sqlalchemy as sa

        # 1. DROP ALL EXISTING TABLES
        logger.info("🗑️ Eliminando todas las tablas existentes...")
        with engine.connect() as conn:
            # Get all table names
            result = conn.execute(sa.text("""
                SELECT tablename FROM pg_tables
                WHERE schemaname = 'public'
            """))
            tables = [row[0] for row in result]

            if tables:
                # Drop tables with CASCADE to handle foreign keys
                for table in tables:
                    try:
                        conn.execute(sa.text(f"DROP TABLE IF EXISTS {table} CASCADE"))
                        logger.info(f"  ✅ Dropped table: {table}")
                    except Exception as e:
                        logger.warning(f"  ⚠️ Could not drop {table}: {e}")

                conn.commit()
                logger.info(f"✅ Dropped {len(tables)} tables")
            else:
                logger.info("ℹ️ No tables to drop")

        # 2. CREATE ALL TABLES FROM SCRATCH
        logger.info("🏗️ Creando todas las tablas desde cero...")
        Base.metadata.create_all(bind=engine)
        logger.info("✅ Todas las tablas creadas exitosamente")

        # 3. Verify database is ready
        from sqlalchemy.orm import sessionmaker
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        db = SessionLocal()

        try:
            # Test basic query
            siniestros_count = db.query(models.Siniestro).count()
            logger.info(f"📊 Base de datos lista: {siniestros_count} siniestros registrados")
            logger.info("✅ Sistema operativo y listo para uso")

        finally:
            db.close()

    except Exception as e:
        logger.error(f"❌ Error en reset completo de BD: {e}")
        import traceback
        logger.error(f"❌ Traceback: {traceback.format_exc()}")
        # Don't crash the app - log and continue
        logger.warning("⚠️ Continuando sin inicialización de BD")

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

@app.get("/debug/analyze-db")
async def analyze_database():
    """Analizar completamente la base de datos: tablas, registros, estructura"""
    try:
        from app.database import SessionLocal, engine
        from app import models
        import sqlalchemy as sa

        analysis = {
            "timestamp": str(datetime.now()),
            "database_info": {},
            "tables_analysis": {},
            "summary": {}
        }

        # Información general de la base de datos
        db = SessionLocal()
        try:
            # Verificar conexión
            db.execute(sa.text("SELECT 1"))
            analysis["database_info"]["connection"] = "✅ Connected"

            # Obtener lista de tablas
            result = db.execute(sa.text("""
                SELECT tablename FROM pg_tables
                WHERE schemaname = 'public'
                ORDER BY tablename
            """))
            tables = [row[0] for row in result]
            analysis["database_info"]["tables"] = tables
            analysis["database_info"]["total_tables"] = len(tables)

            # Análisis de cada tabla
            total_records = 0
            tables_with_data = 0

            for table_name in tables:
                table_analysis = {
                    "exists": True,
                    "record_count": 0,
                    "has_data": False,
                    "sample_records": []
                }

                try:
                    # Contar registros
                    if hasattr(models, table_name.capitalize()):
                        model_class = getattr(models, table_name.capitalize())
                        count = db.query(model_class).count()
                        table_analysis["record_count"] = count
                        total_records += count

                        if count > 0:
                            tables_with_data += 1
                            table_analysis["has_data"] = True

                            # Obtener muestra de registros (máximo 3)
                            sample = db.query(model_class).limit(3).all()
                            table_analysis["sample_records"] = [
                                {"id": getattr(record, 'id', 'N/A'), "data": str(record)[:200] + "..." if len(str(record)) > 200 else str(record)}
                                for record in sample
                            ]

                except Exception as e:
                    table_analysis["error"] = str(e)

                analysis["tables_analysis"][table_name] = table_analysis

            # Resumen
            analysis["summary"] = {
                "total_tables": len(tables),
                "tables_with_data": tables_with_data,
                "tables_empty": len(tables) - tables_with_data,
                "total_records": total_records,
                "database_status": "✅ Active with data" if tables_with_data > 0 else "📭 Empty database"
            }

        finally:
            db.close()

        return analysis

    except Exception as e:
        logger.error(f"❌ Database analysis error: {e}")
        import traceback
        return {
            "error": f"Analysis failed: {str(e)}",
            "traceback": traceback.format_exc(),
            "timestamp": str(datetime.now())
        }

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

@app.post("/debug/reset-database")
async def reset_database():
    """🔥 RESET COMPLETO: Limpiar TODOS los datos y reconstruir esquema"""
    logger.warning("🔥 INICIANDO RESET COMPLETO DE BASE DE DATOS")

    try:
        from app.database import SessionLocal, engine, Base
        from app import models
        import sqlalchemy as sa

        db = SessionLocal()

        # 1. Limpiar todos los datos existentes
        logger.info("🗑️ Paso 1: Eliminando datos existentes...")
        try:
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
            logger.info("✅ Datos eliminados")
        except Exception as e:
            logger.warning(f"⚠️ Algunos datos ya estaban limpios: {e}")
            db.rollback()

        # 2. Recrear todas las tablas desde cero
        logger.info("🏗️ Paso 2: Recreando esquema de base de datos...")
        Base.metadata.drop_all(bind=engine)  # Eliminar tablas existentes
        Base.metadata.create_all(bind=engine)  # Crear tablas nuevas
        logger.info("✅ Esquema recreado")

        db.close()

        return {
            "message": "🔥 RESET COMPLETO EJECUTADO EXITOSAMENTE",
            "actions_taken": [
                "✅ Eliminados todos los datos existentes",
                "✅ Eliminadas todas las tablas",
                "✅ Recreación completa del esquema",
                "✅ Base de datos lista para uso"
            ],
            "status": "ready"
        }

    except Exception as e:
        logger.error(f"❌ Error en reset completo: {e}")
        return {
            "error": f"Reset falló: {str(e)}",
            "status": "failed"
        }

@app.post("/debug/create-test-data")
async def create_test_data_endpoint():
    """Crear datos de prueba manualmente - ejecuta el script create_test_data.py"""
    import subprocess
    import sys
    import os

    logger.info("🧪 EJECUTANDO CREACIÓN MANUAL DE DATOS DE PRUEBA")

    try:
        current_dir = os.getcwd()
        logger.info(f"Directorio actual: {current_dir}")

        # Ejecutar el script create_test_data.py
        result = subprocess.run([
            sys.executable, "create_test_data.py"
        ], capture_output=True, text=True, cwd=current_dir)

        if result.returncode == 0:
            logger.info("✅ Datos de prueba creados exitosamente")
            logger.info(f"Output: {result.stdout}")

            # Verificar que se creó el siniestro
            from app.database import SessionLocal
            from app import models

            db = SessionLocal()
            count = db.query(models.Siniestro).count()
            db.close()

            return {
                "message": "✅ Datos de prueba creados exitosamente",
                "output": result.stdout.strip(),
                "error": result.stderr.strip(),
                "siniestros_creados": count,
                "status": "success"
            }
        else:
            logger.error(f"❌ Error creando datos de prueba: {result.stderr}")
            return {
                "error": f"Error creando datos: {result.stderr.strip()}",
                "output": result.stdout.strip(),
                "status": "failed"
            }

    except Exception as e:
        logger.error(f"❌ Error ejecutando script: {e}")
        import traceback
        error_details = traceback.format_exc()
        logger.error(f"Traceback: {error_details}")
        return {
            "error": f"Error ejecutando script: {str(e)}",
            "traceback": error_details,
            "status": "failed"
        }

@app.post("/debug/apply-migrations")
async def apply_migrations():
    """Aplicar migraciones de base de datos pendientes"""
    import subprocess
    import sys
    import os

    logger.info("🔄 APLICANDO MIGRACIONES DE BASE DE DATOS")

    try:
        # El directorio actual ya ES backend/ (donde está este archivo)
        # alembic.ini está en el mismo directorio, script_location = alembic
        # Las migraciones están en ./alembic/versions/

        current_dir = os.getcwd()
        logger.info(f"Directorio actual: {current_dir}")

        # Verificar que alembic.ini existe
        if not os.path.exists("alembic.ini"):
            return {
                "error": "alembic.ini no encontrado en el directorio actual",
                "current_dir": current_dir,
                "status": "failed"
            }

        # Verificar que el directorio alembic existe
        if not os.path.exists("alembic"):
            return {
                "error": "Directorio alembic/ no encontrado",
                "current_dir": current_dir,
                "status": "failed"
            }

        # Ejecutar alembic upgrade head desde el directorio actual
        result = subprocess.run([
            sys.executable, "-m", "alembic", "upgrade", "head"
        ], capture_output=True, text=True, cwd=current_dir)

        if result.returncode == 0:
            logger.info("✅ Migraciones aplicadas exitosamente")
            logger.info(f"Output: {result.stdout}")
            return {
                "message": "✅ Migraciones aplicadas exitosamente",
                "output": result.stdout.strip(),
                "error": result.stderr.strip(),
                "current_dir": current_dir
            }
        else:
            logger.error(f"❌ Error aplicando migraciones: {result.stderr}")
            return {
                "error": f"Error aplicando migraciones: {result.stderr.strip()}",
                "output": result.stdout.strip(),
                "status": "failed",
                "current_dir": current_dir
            }

    except Exception as e:
        logger.error(f"❌ Error ejecutando migraciones: {e}")
        import traceback
        error_details = traceback.format_exc()
        logger.error(f"Traceback: {error_details}")
        return {
            "error": f"Error ejecutando migraciones: {str(e)}",
            "traceback": error_details,
            "status": "failed"
        }
