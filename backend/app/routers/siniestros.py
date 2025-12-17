from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Request
from sqlalchemy.orm import Session
from typing import List
import logging

from app import models, schemas
from app.database import get_db
from app.services.siniestro_service import SiniestroService
from app.services.pdf_service import PDFService
from app.routers.error_handlers import handle_api_error, get_validation_service

router = APIRouter()


@router.post("/", response_model=schemas.SiniestroResponse)
async def create_siniestro(
    siniestro: schemas.SiniestroCreate, db: Session = Depends(get_db)
):
    """Crear un nuevo siniestro"""
    siniestro_service = SiniestroService(db)
    validation_service = get_validation_service()

    try:
        # Validate input data
        validated_data = validation_service.validate_siniestro_data(
            siniestro.model_dump()
        )

        # Create siniestro using service
        db_siniestro = siniestro_service.create_siniestro(
            schemas.SiniestroCreate(**validated_data)
        )

        return db_siniestro

    except Exception as e:
        handle_api_error(
            e,
            "create_siniestro",
            {"reclamo_num": siniestro.reclamo_num},
            validation_service
        )


@router.get("/", response_model=List[schemas.SiniestroResponse])
async def get_siniestros(
    skip: int = 0, limit: int = 100, db: Session = Depends(get_db)
):
    """Obtener todos los siniestros con paginación"""
    siniestro_service = SiniestroService(db)
    siniestros = siniestro_service.get_siniestros(skip=skip, limit=limit)
    return siniestros


@router.get("/{siniestro_id}", response_model=schemas.SiniestroFullResponse)
async def get_siniestro(siniestro_id: int, db: Session = Depends(get_db)):
    """Obtener un siniestro completo por ID con todas sus relaciones"""
    siniestro_service = SiniestroService(db)
    siniestro = siniestro_service.get_siniestro(siniestro_id)
    if not siniestro:
        raise HTTPException(status_code=404, detail="Siniestro no encontrado")
    return siniestro


# NUEVOS ENDPOINTS PARA GUARDADO POR SECCIONES
@router.put("/{siniestro_id}/seccion/{seccion}")
async def guardar_seccion(
    siniestro_id: int,
    seccion: str,  # 'asegurado', 'conductor', 'objeto_asegurado', 'antecedentes', etc.
    datos: (
        List[schemas.RelatoInput] | List[schemas.AntecedenteInput] | dict
    ),  # Datos específicos de la sección
    db: Session = Depends(get_db),
):
    """
    Guardar datos de una sección específica del siniestro.

    Service layer now accepts Pydantic models directly, eliminating
    manual conversion and maintaining type safety throughout.
    """
    siniestro_service = SiniestroService(db)
    validation_service = get_validation_service()

    try:
        # Validate section data (service handles Pydantic conversion internally)
        validated_data = validation_service.validate_section_data(seccion, datos)

        # Update section using service (accepts Pydantic models directly)
        result = siniestro_service.update_section(siniestro_id, seccion, datos)

        return result

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=validation_service.create_safe_error_message(e)
        )


@router.put("/{siniestro_id}", response_model=schemas.SiniestroResponse)
async def update_siniestro(
    siniestro_id: int,
    siniestro_update: schemas.SiniestroUpdate,
    request: Request,
    db: Session = Depends(get_db),
):
    """Actualizar un siniestro"""
    logger = logging.getLogger(__name__)

    # DIAGNÓSTICO JSON ERROR
    try:
        raw_body = await request.body()
        logger.error(f"🔥 RAW BODY RECIBIDO: {raw_body}")
        logger.error(f"🔥 BODY como string: {raw_body.decode('utf-8', errors='ignore')}")
    except Exception as e:
        logger.error(f"🔥 ERROR leyendo body: {e}")

    siniestro_service = SiniestroService(db)
    validation_service = get_validation_service()

    try:
        # Validate input data
        validated_data = validation_service.validate_siniestro_data(
            siniestro_update.model_dump(exclude_unset=True)
        )

        # Update siniestro using service
        updated_siniestro = siniestro_service.update_siniestro(
            siniestro_id, schemas.SiniestroUpdate(**validated_data)
        )

        return updated_siniestro

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=validation_service.create_safe_error_message(e)
        )


@router.post("/{siniestro_id}/testigo", response_model=schemas.TestigoResponse)
async def create_testigo(
    siniestro_id: int, testigo: schemas.TestigoCreate, db: Session = Depends(get_db)
):
    """Crear testigo"""
    siniestro_service = SiniestroService(db)
    validation_service = get_validation_service()

    try:
        # Validate input data
        validated_data = validation_service.validate_section_data(
            "testigos", [testigo.model_dump()]
        )

        # Create testigo using service
        db_testigo = siniestro_service.create_testigo(
            siniestro_id, schemas.TestigoCreate(**validated_data[0])
        )

        return db_testigo

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=validation_service.create_safe_error_message(e)
        )


@router.get("/{siniestro_id}/generar-pdf")
async def generar_pdf(siniestro_id: int, db: Session = Depends(get_db)):
    """Generar PDF del informe de siniestro"""
    pdf_service = PDFService(db)

    try:
        return pdf_service.generate_siniestro_pdf(siniestro_id, sign_document=True)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error generando PDF")


@router.get("/{siniestro_id}/generar-pdf-sin-firma")
async def generar_pdf_sin_firma(siniestro_id: int, db: Session = Depends(get_db)):
    """Generar PDF del informe de siniestro SIN FIRMA DIGITAL (para pruebas)"""
    pdf_service = PDFService(db)

    try:
        return pdf_service.generate_unsigned_pdf(siniestro_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error generando PDF sin firma")


@router.post("/upload-image")
async def upload_image(file: UploadFile = File(...)):
    """Subir imagen a AWS S3 y devolver URL optimizada para PostgreSQL"""
    from app.services.s3_service import upload_file_to_s3

    result = await upload_file_to_s3(file)
    # Devolver URL optimizada (esta va a imagen_url en BD según arquitectura)
    return {"url_optimizada": result["url_optimizada"]}


@router.get("/diagnostico-pdf")
async def diagnostico_pdf(db: Session = Depends(get_db)):
    """Endpoint de diagnóstico para analizar problemas de generación de PDFs"""
    pdf_service = PDFService(db)

    try:
        return pdf_service.generate_diagnostic_pdf()
    except Exception as e:
        # Log the actual error for debugging
        import logging
        logger = logging.getLogger(__name__)
        logger.error(
            f"Error guardando sección {seccion} para siniestro {siniestro_id}: {str(e)}"
        )
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")

        raise HTTPException(
            status_code=500, detail=validation_service.create_safe_error_message(e)
        )


@router.get("/test-pdf")
async def test_pdf():
    """Generar PDF de prueba mínimo sin BD"""
    pdf_service = PDFService(None)  # No database needed for test PDF

    try:
        return pdf_service.generate_test_pdf()
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error generando PDF de prueba")


@router.get("/{siniestro_id}/debug-json")
async def debug_json_fields(siniestro_id: int, db: Session = Depends(get_db)):
    """Debug endpoint para verificar campos JSON"""
    siniestro = (
        db.query(models.Siniestro)
        .filter(models.Siniestro.id == siniestro_id)
        .first()
    )

    if not siniestro:
        raise HTTPException(status_code=404, detail="Siniestro no encontrado")

    import json

    json_fields_to_check = [
        "evidencias_complementarias",
        "otras_diligencias",
        "observaciones",
        "recomendacion_pago_cobertura",
        "conclusiones",
        "anexo"
    ]

    result = {
        "siniestro_id": siniestro_id,
        "reclamo_num": siniestro.reclamo_num,
        "json_fields": {}
    }

    for field in json_fields_to_check:
        value = getattr(siniestro, field, None)
        result["json_fields"][field] = {
            "raw_value": value,
            "is_json": False,
            "parsed_value": None
        }

        if value:
            try:
                parsed = json.loads(value)
                result["json_fields"][field]["is_json"] = True
                result["json_fields"][field]["parsed_value"] = parsed
            except json.JSONDecodeError:
                result["json_fields"][field]["is_json"] = False

    return result


@router.get("/diagnostico/tablas-investigacion")
async def diagnostico_tablas_investigacion(db: Session = Depends(get_db)):
    """Verificar solo tablas de investigación"""
    from sqlalchemy import text

    tablas_investigacion = [
        "antecedentes",
        "relatos_asegurado",
        "relatos_conductor",
        "inspecciones",
        "testigos"
    ]

    resultado = {}

    for tabla in tablas_investigacion:
        try:
            # Verificar si la tabla existe
            count = db.execute(text(f"SELECT COUNT(*) FROM {tabla}")).scalar()
            resultado[tabla] = {
                "existe": True,
                "total_registros": count,
                "con_siniestro_id": db.execute(
                    text(f"SELECT COUNT(*) FROM {tabla} WHERE siniestro_id IS NOT NULL")
                ).scalar()
            }
        except Exception as e:
            resultado[tabla] = {
                "existe": False,
                "error": str(e)
            }

    # Verificar un siniestro específico
    try:
        siniestro_1 = db.execute(
            text("SELECT id, reclamo_num FROM siniestros WHERE id = 1")
        ).fetchone()

        if siniestro_1:
            resultado["siniestro_1"] = {
                "id": siniestro_1[0],
                "reclamo_num": siniestro_1[1],
                "antecedentes_count": db.execute(
                    text("SELECT COUNT(*) FROM antecedentes WHERE siniestro_id = 1")
                ).scalar(),
                "relatos_asegurado_count": db.execute(
                    text("SELECT COUNT(*) FROM relatos_asegurado WHERE siniestro_id = 1")
                ).scalar()
            }
    except Exception as e:
        resultado["siniestro_1_error"] = str(e)

    return resultado


@router.post("/{siniestro_id}/upload-pdf-firmado")
async def upload_pdf_firmado(
    siniestro_id: int, file: UploadFile = File(...), db: Session = Depends(get_db)
):
    """Subir PDF firmado digitalmente para un siniestro"""
    import logging

    logger = logging.getLogger(__name__)

    try:
        logger.info(f"📤 Subiendo PDF firmado para siniestro ID: {siniestro_id}")

        # Verificar que el siniestro existe
        siniestro = (
            db.query(models.Siniestro)
            .filter(models.Siniestro.id == siniestro_id)
            .first()
        )
        if not siniestro:
            raise HTTPException(status_code=404, detail="Siniestro no encontrado")

        # Validar que es un PDF
        if not file.filename.lower().endswith(".pdf"):
            raise HTTPException(status_code=400, detail="Solo se permiten archivos PDF")

        # Leer contenido del archivo
        content = await file.read()
        file_size = len(content)

        # Validar tamaño (máximo 50MB)
        if file_size > 50 * 1024 * 1024:
            raise HTTPException(
                status_code=400, detail="El archivo excede el tamaño máximo de 50MB"
            )

        # Subir a S3
        from app.services.s3_service import upload_file_to_s3

        presigned_url = await upload_file_to_s3(file, content=content)

        # Actualizar el siniestro con la URL del PDF firmado
        siniestro.pdf_firmado_url = presigned_url
        db.commit()

        logger.info(f"✅ PDF firmado subido exitosamente para siniestro {siniestro_id}")
        return {
            "message": "PDF firmado subido exitosamente",
            "url_presigned": presigned_url,
            "siniestro_id": siniestro_id,
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error subiendo PDF firmado: {e}")
        import traceback

        logger.error(f"❌ Traceback: {traceback.format_exc()}")
        raise HTTPException(
            status_code=500, detail=f"Error interno del servidor: {str(e)}"
        )
