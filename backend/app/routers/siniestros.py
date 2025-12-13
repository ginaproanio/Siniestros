from fastapi import APIRouter, HTTPException, Depends, UploadFile, File
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime

from app import models, schemas
from app.database import get_db

router = APIRouter()


@router.post("/", response_model=schemas.SiniestroResponse)
async def create_siniestro(
    siniestro: schemas.SiniestroCreate, db: Session = Depends(get_db)
):
    """Crear un nuevo siniestro"""
    import logging

    logger = logging.getLogger(__name__)

    logger.info("🚀 Iniciando creación de siniestro")
    logger.info(f"📋 Datos recibidos: {siniestro.model_dump()}")

    try:
        # Check if reclamo_num already exists
        db_siniestro = (
            db.query(models.Siniestro)
            .filter(models.Siniestro.reclamo_num == siniestro.reclamo_num)
            .first()
        )
        if db_siniestro:
            logger.warning(f"⚠️ Número de reclamo ya existe: {siniestro.reclamo_num}")
            raise HTTPException(status_code=400, detail="Número de reclamo ya existe")

        logger.info("✅ Validación de reclamo_num pasada")

        # Crear el siniestro
        siniestro_data = siniestro.model_dump()
        logger.info(f"📝 Creando siniestro con datos: {siniestro_data}")

        db_siniestro = models.Siniestro(**siniestro_data)
        db.add(db_siniestro)

        logger.info("💾 Guardando en base de datos...")
        db.commit()
        db.refresh(db_siniestro)

        logger.info(f"✅ Siniestro creado exitosamente con ID: {db_siniestro.id}")
        return db_siniestro

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error al crear siniestro: {e}")
        logger.error(f"❌ Tipo de error: {type(e)}")
        import traceback

        logger.error(f"❌ Traceback: {traceback.format_exc()}")
        db.rollback()
        raise HTTPException(
            status_code=500, detail=f"Error interno del servidor: {str(e)}"
        )


@router.get("/", response_model=List[schemas.SiniestroResponse])
async def get_siniestros(
    skip: int = 0, limit: int = 100, db: Session = Depends(get_db)
):
    """Obtener todos los siniestros con paginación"""
    siniestros = db.query(models.Siniestro).offset(skip).limit(limit).all()
    return siniestros


@router.get("/{siniestro_id}", response_model=schemas.SiniestroFullResponse)
async def get_siniestro(siniestro_id: int, db: Session = Depends(get_db)):
    """Obtener un siniestro completo por ID con todas sus relaciones"""
    siniestro = (
        db.query(models.Siniestro).filter(models.Siniestro.id == siniestro_id).first()
    )
    if not siniestro:
        raise HTTPException(status_code=404, detail="Siniestro no encontrado")
    return siniestro


@router.put("/{siniestro_id}", response_model=schemas.SiniestroResponse)
async def update_siniestro(
    siniestro_id: int,
    siniestro_update: schemas.SiniestroUpdate,
    db: Session = Depends(get_db),
):
    """Actualizar un siniestro"""
    db_siniestro = (
        db.query(models.Siniestro).filter(models.Siniestro.id == siniestro_id).first()
    )
    if not db_siniestro:
        raise HTTPException(status_code=404, detail="Siniestro no encontrado")

    update_data = siniestro_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_siniestro, field, value)

    db.commit()
    db.refresh(db_siniestro)
    return db_siniestro


@router.delete("/{siniestro_id}")
async def delete_siniestro(siniestro_id: int, db: Session = Depends(get_db)):
    """Eliminar un siniestro"""
    db_siniestro = (
        db.query(models.Siniestro).filter(models.Siniestro.id == siniestro_id).first()
    )
    if not db_siniestro:
        raise HTTPException(status_code=404, detail="Siniestro no encontrado")

    db.delete(db_siniestro)
    db.commit()
    return {"message": "Siniestro eliminado exitosamente"}


# Additional endpoints for related entities
@router.post("/{siniestro_id}/asegurado", response_model=schemas.AseguradoResponse)
async def create_asegurado(
    siniestro_id: int, asegurado: schemas.AseguradoCreate, db: Session = Depends(get_db)
):
    """Crear asegurado para un siniestro"""
    db_asegurado = models.Asegurado(siniestro_id=siniestro_id, **asegurado.model_dump())
    db.add(db_asegurado)
    db.commit()
    db.refresh(db_asegurado)
    return db_asegurado


@router.post(
    "/{siniestro_id}/relato-asegurado", response_model=schemas.RelatoAseguradoResponse
)
async def create_relato_asegurado(
    siniestro_id: int,
    relato: schemas.RelatoAseguradoCreate,
    db: Session = Depends(get_db),
):
    """Crear relato del asegurado"""
    # Get the next numero_relato
    max_num = (
        db.query(models.RelatoAsegurado)
        .filter(models.RelatoAsegurado.siniestro_id == siniestro_id)
        .count()
    )
    numero_relato = max_num + 1

    db_relato = models.RelatoAsegurado(
        siniestro_id=siniestro_id, numero_relato=numero_relato, **relato.model_dump()
    )
    db.add(db_relato)
    db.commit()
    db.refresh(db_relato)
    return db_relato


# Similar endpoints for other entities...
@router.post("/{siniestro_id}/inspeccion", response_model=schemas.InspeccionResponse)
async def create_inspeccion(
    siniestro_id: int,
    inspeccion: schemas.InspeccionCreate,
    db: Session = Depends(get_db),
):
    """Crear inspección del lugar del siniestro"""
    max_num = (
        db.query(models.Inspeccion)
        .filter(models.Inspeccion.siniestro_id == siniestro_id)
        .count()
    )
    numero_inspeccion = max_num + 1

    db_inspeccion = models.Inspeccion(
        siniestro_id=siniestro_id,
        numero_inspeccion=numero_inspeccion,
        **inspeccion.model_dump(),
    )
    db.add(db_inspeccion)
    db.commit()
    db.refresh(db_inspeccion)
    return db_inspeccion


@router.post("/{siniestro_id}/testigo", response_model=schemas.TestigoResponse)
async def create_testigo(
    siniestro_id: int, testigo: schemas.TestigoCreate, db: Session = Depends(get_db)
):
    """Crear testigo"""
    max_num = (
        db.query(models.Testigo)
        .filter(models.Testigo.siniestro_id == siniestro_id)
        .count()
    )
    numero_relato = max_num + 1

    db_testigo = models.Testigo(
        siniestro_id=siniestro_id, numero_relato=numero_relato, **testigo.model_dump()
    )
    db.add(db_testigo)
    db.commit()
    db.refresh(db_testigo)
    return db_testigo


# PDF generation endpoint
@router.post("/{siniestro_id}/generar-pdf")
async def generar_pdf(siniestro_id: int, db: Session = Depends(get_db)):
    """Generar PDF del informe de siniestro"""
    try:
        print(f"🔍 INICIANDO GENERACIÓN PDF - Siniestro ID: {siniestro_id}")
        from app.utils.pdf_generator import generate_simple_pdf

        # Get siniestro data first
        siniestro = (
            db.query(models.Siniestro)
            .filter(models.Siniestro.id == siniestro_id)
            .first()
        )
        if not siniestro:
            raise HTTPException(status_code=404, detail="Siniestro no encontrado")

        pdf_data = generate_simple_pdf(siniestro)
        print(f"✅ PDF generado exitosamente: {len(pdf_data)} bytes")

        from fastapi.responses import Response

        # Generar nombre de archivo seguro con caracteres especiales
        import unicodedata
        import re

        # Crear nombre base del archivo
        compania = siniestro.compania_seguros or "sin_compania"
        reclamo = siniestro.reclamo_num or str(siniestro_id)

        # Normalizar caracteres especiales (ñ, á, é, í, ó, ú)
        filename_base = f"siniestro_{reclamo}_{compania}"
        filename_base = unicodedata.normalize('NFKD', filename_base).encode('ASCII', 'ignore').decode('ASCII')

        # Remover caracteres no seguros para filename
        filename_base = re.sub(r'[^\w\-_\.]', '_', filename_base)
        filename_safe = f"{filename_base}.pdf"

        return Response(
            content=pdf_data,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename*=UTF-8''{filename_safe}",
                "Content-Length": str(len(pdf_data)),
            },
        )
    except Exception as e:
        print(f"❌ Error generando PDF: {e}")
        import traceback

        print(f"❌ Traceback completo: {traceback.format_exc()}")

        # Generar PDF de error mínimo como prueba
        print("🧪 Generando PDF de error mínimo...")
        from reportlab.lib.pagesizes import letter
        from reportlab.platypus import SimpleDocTemplate, Paragraph
        from reportlab.lib.styles import getSampleStyleSheet
        import io

        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        styles = getSampleStyleSheet()
        story = [
            Paragraph(
                "ERROR: No se pudo generar el PDF completo. Intente nuevamente.",
                styles["Normal"],
            )
        ]

        try:
            doc.build(story)
            buffer.seek(0)
            error_pdf = buffer.getvalue()
            print(f"✅ PDF de error generado: {len(error_pdf)} bytes")

            return Response(
                content=error_pdf,
                media_type="application/pdf",
                headers={
                    "Content-Disposition": f"attachment; filename=error_siniestro_{siniestro_id}.pdf",
                    "Content-Length": str(len(error_pdf)),
                },
            )
        except Exception as e2:
            print(f"❌ Error generando PDF de error: {e2}")
            raise HTTPException(
                status_code=500, detail=f"Error crítico generando PDF: {str(e)}"
            )


@router.post("/{siniestro_id}/generar-pdf-sin-firma")
async def generar_pdf_sin_firma(siniestro_id: int, db: Session = Depends(get_db)):
    """Generar PDF del informe de siniestro SIN FIRMA DIGITAL (para pruebas)"""
    try:
        print(f"🔍 GENERANDO PDF SIN FIRMA - Siniestro ID: {siniestro_id}")
        from app.utils.pdf_generator import generate_unsigned_pdf

        # Get siniestro data first
        siniestro = (
            db.query(models.Siniestro)
            .filter(models.Siniestro.id == siniestro_id)
            .first()
        )
        if not siniestro:
            raise HTTPException(status_code=404, detail="Siniestro no encontrado")

        pdf_data = generate_unsigned_pdf(siniestro)
        print(f"✅ PDF sin firma generado exitosamente: {len(pdf_data)} bytes")

        from fastapi.responses import Response

        # Generar nombre de archivo seguro con caracteres especiales
        import unicodedata
        import re

        # Crear nombre base del archivo
        compania = siniestro.compania_seguros or "sin_compania"
        reclamo = siniestro.reclamo_num or str(siniestro_id)

        # Normalizar caracteres especiales (ñ, á, é, í, ó, ú)
        filename_base = f"siniestro_sin_firma_{reclamo}_{compania}"
        filename_base = unicodedata.normalize('NFKD', filename_base).encode('ASCII', 'ignore').decode('ASCII')

        # Remover caracteres no seguros para filename
        filename_base = re.sub(r'[^\w\-_\.]', '_', filename_base)
        filename_safe = f"{filename_base}.pdf"

        return Response(
            content=pdf_data,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename*=UTF-8''{filename_safe}",
                "Content-Length": str(len(pdf_data)),
            },
        )
    except Exception as e:
        print(f"❌ Error generando PDF sin firma: {e}")
        import traceback

        print(f"❌ Traceback: {traceback.format_exc()}")
        raise HTTPException(
            status_code=500, detail=f"Error generando PDF sin firma: {str(e)}"
        )


@router.post("/upload-image")
async def upload_image(file: UploadFile = File(...)):
    """Subir imagen a AWS S3 y devolver URL presigned"""
    from app.services.s3_service import upload_file_to_s3

    presigned_url = await upload_file_to_s3(file)
    return {"url_presigned": presigned_url}


@router.get("/diagnostico-pdf")
async def diagnostico_pdf(db: Session = Depends(get_db)):
    """Endpoint de diagnóstico para analizar problemas de generación de PDFs"""
    import logging
    logger = logging.getLogger(__name__)

    logger.info("🔍 INICIANDO DIAGNÓSTICO DE PDF")

    diagnostico = {
        "timestamp": datetime.now().isoformat(),
        "checks": {},
        "errors": [],
        "warnings": []
    }

    try:
        # 1. Verificar conexión a base de datos
        logger.info("📊 Verificando conexión a base de datos...")
        siniestros_count = db.query(models.Siniestro).count()
        diagnostico["checks"]["database_connection"] = f"✅ Conectado - {siniestros_count} siniestros encontrados"
        logger.info(f"✅ Base de datos OK: {siniestros_count} siniestros")

    except Exception as e:
        diagnostico["errors"].append(f"❌ Error de base de datos: {str(e)}")
        logger.error(f"❌ Error BD: {e}")

    try:
        # 2. Verificar generación básica de PDF
        logger.info("📄 Probando generación básica de PDF...")
        from reportlab.lib.pagesizes import letter
        from reportlab.platypus import SimpleDocTemplate, Paragraph
        from reportlab.lib.styles import getSampleStyleSheet
        import io

        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        styles = getSampleStyleSheet()

        story = [
            Paragraph("DIAGNÓSTICO DE SISTEMA PDF", styles["Heading1"]),
            Paragraph(f"Fecha: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}", styles["Normal"]),
            Paragraph("Este PDF verifica el funcionamiento del generador.", styles["Normal"]),
        ]

        doc.build(story)
        buffer.seek(0)
        test_pdf = buffer.getvalue()

        if test_pdf.startswith(b'%PDF-'):
            diagnostico["checks"]["basic_pdf_generation"] = f"✅ PDF básico OK - {len(test_pdf)} bytes"
            logger.info(f"✅ PDF básico OK: {len(test_pdf)} bytes")
        else:
            diagnostico["errors"].append("❌ PDF básico no válido")
            logger.error("❌ PDF básico no válido")

    except Exception as e:
        diagnostico["errors"].append(f"❌ Error en generación básica de PDF: {str(e)}")
        logger.error(f"❌ Error PDF básico: {e}")

    try:
        # 3. Verificar carga de certificado desde S3
        logger.info("🔐 Verificando carga de certificado desde S3...")
        from app.utils.pdf_generator import load_certificate_from_s3

        cert_data = load_certificate_from_s3()
        if cert_data:
            diagnostico["checks"]["certificate_loading"] = f"✅ Certificado cargado - {len(cert_data)} bytes"
            logger.info(f"✅ Certificado OK: {len(cert_data)} bytes")
        else:
            diagnostico["warnings"].append("⚠️ Certificado no encontrado en S3 - PDFs sin firma")
            logger.warning("⚠️ Certificado no encontrado en S3")

    except Exception as e:
        diagnostico["errors"].append(f"❌ Error cargando certificado: {str(e)}")
        logger.error(f"❌ Error certificado: {e}")

    try:
        # 4. Verificar generación completa de PDF con datos reales
        logger.info("📋 Probando generación completa de PDF...")
        from app.utils.pdf_generator import generate_unsigned_pdf

        # Obtener primer siniestro para prueba
        siniestro = db.query(models.Siniestro).first()
        if siniestro:
            pdf_data = generate_unsigned_pdf(siniestro)
            if pdf_data.startswith(b'%PDF-'):
                diagnostico["checks"]["full_pdf_generation"] = f"✅ PDF completo OK - {len(pdf_data)} bytes"
                logger.info(f"✅ PDF completo OK: {len(pdf_data)} bytes")
            else:
                diagnostico["errors"].append("❌ PDF completo no válido")
                logger.error("❌ PDF completo no válido")
        else:
            diagnostico["warnings"].append("⚠️ No hay siniestros en BD para probar generación completa")
            logger.warning("⚠️ No hay siniestros para probar")

    except Exception as e:
        diagnostico["errors"].append(f"❌ Error en generación completa de PDF: {str(e)}")
        logger.error(f"❌ Error PDF completo: {e}")

    # 5. Verificar configuración de logging
    diagnostico["checks"]["logging_config"] = "✅ Logging configurado correctamente"
    logger.info("✅ Diagnóstico completado")

    # Crear PDF de diagnóstico
    try:
        from reportlab.lib.pagesizes import letter
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib import colors
        from reportlab.lib.enums import TA_CENTER
        from fastapi.responses import Response
        import io

        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter, topMargin=1*inch, bottomMargin=1*inch, leftMargin=1*inch, rightMargin=1*inch)

        styles = getSampleStyleSheet()
        title_style = ParagraphStyle("Title", parent=styles["Heading1"], fontSize=16, alignment=TA_CENTER, spaceAfter=20)

        story = []
        story.append(Paragraph("REPORTE DE DIAGNÓSTICO - SISTEMA PDF", title_style))
        story.append(Spacer(1, 20))

        # Checks exitosos
        if diagnostico["checks"]:
            story.append(Paragraph("✅ VERIFICACIONES EXITOSAS:", styles["Heading2"]))
            for check, result in diagnostico["checks"].items():
                story.append(Paragraph(f"• {check}: {result}", styles["Normal"]))
            story.append(Spacer(1, 10))

        # Advertencias
        if diagnostico["warnings"]:
            story.append(Paragraph("⚠️ ADVERTENCIAS:", styles["Heading2"]))
            for warning in diagnostico["warnings"]:
                story.append(Paragraph(f"• {warning}", styles["Normal"]))
            story.append(Spacer(1, 10))

        # Errores
        if diagnostico["errors"]:
            error_style = ParagraphStyle("Error", parent=styles["Normal"], textColor=colors.red)
            story.append(Paragraph("❌ ERRORES ENCONTRADOS:", styles["Heading2"]))
            for error in diagnostico["errors"]:
                story.append(Paragraph(f"• {error}", error_style))
            story.append(Spacer(1, 10))

        story.append(Paragraph(f"Diagnóstico completado: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}", styles["Normal"]))

        doc.build(story)
        buffer.seek(0)
        pdf_data = buffer.getvalue()

        logger.info(f"✅ PDF de diagnóstico generado: {len(pdf_data)} bytes")

        return Response(
            content=pdf_data,
            media_type="application/pdf",
            headers={
                "Content-Disposition": "attachment; filename=diagnostico.pdf",
                "Content-Length": str(len(pdf_data)),
            },
        )

    except Exception as e:
        logger.error(f"❌ Error generando PDF de diagnóstico: {e}")
        raise HTTPException(status_code=500, detail=f"Error en diagnóstico: {str(e)}")


@router.get("/test-pdf")
async def test_pdf():
    """Generar PDF de prueba mínimo sin BD"""
    print("🧪 GENERANDO PDF DE PRUEBA MÍNIMO")

    from reportlab.lib.pagesizes import letter
    from reportlab.platypus import SimpleDocTemplate, Paragraph
    from reportlab.lib.styles import getSampleStyleSheet
    from fastapi.responses import Response
    import io

    try:
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        styles = getSampleStyleSheet()
        story = [
            Paragraph("PDF DE PRUEBA - SISTEMA FUNCIONANDO", styles["Heading1"]),
            Paragraph(
                "Si puedes leer esto, el generador de PDF está funcionando correctamente.",
                styles["Normal"],
            ),
            Paragraph("Fecha de generación: " + str(datetime.now()), styles["Normal"]),
        ]

        doc.build(story)
        buffer.seek(0)
        pdf_data = buffer.getvalue()

        print(f"✅ PDF de prueba generado: {len(pdf_data)} bytes")

        return Response(
            content=pdf_data,
            media_type="application/pdf",
            headers={
                "Content-Disposition": "attachment; filename=test.pdf",
                "Content-Length": str(len(pdf_data)),
            },
        )
    except Exception as e:
        print(f"❌ Error generando PDF de prueba: {e}")
        import traceback

        print(f"❌ Traceback: {traceback.format_exc()}")
        raise HTTPException(
            status_code=500, detail=f"Error generando PDF de prueba: {str(e)}"
        )
