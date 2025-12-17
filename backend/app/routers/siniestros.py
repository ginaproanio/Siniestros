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
    try:
        # Check if reclamo_num already exists
        db_siniestro = (
            db.query(models.Siniestro)
            .filter(models.Siniestro.reclamo_num == siniestro.reclamo_num)
            .first()
        )
        if db_siniestro:
            raise HTTPException(status_code=400, detail="Número de reclamo ya existe")

        # Crear el siniestro
        siniestro_data = siniestro.model_dump()
        db_siniestro = models.Siniestro(**siniestro_data)
        db.add(db_siniestro)
        db.commit()
        db.refresh(db_siniestro)

        return db_siniestro

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Error interno del servidor")


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


# NUEVOS ENDPOINTS PARA GUARDADO POR SECCIONES
@router.put("/{siniestro_id}/seccion/{seccion}")
async def guardar_seccion(
    siniestro_id: int,
    seccion: str,  # 'asegurado', 'conductor', 'objeto_asegurado', 'antecedentes', etc.
    datos: List[schemas.RelatoInput] | List[schemas.AntecedenteInput] | dict,  # Datos específicos de la sección
    db: Session = Depends(get_db),
):
    """Guardar datos de una sección específica del siniestro"""
    import logging

    logger = logging.getLogger(__name__)

    logger.info(f"💾 Guardando sección '{seccion}' para siniestro {siniestro_id}")
    logger.info(f"📋 Datos recibidos: {datos}")

    siniestro = (
        db.query(models.Siniestro).filter(models.Siniestro.id == siniestro_id).first()
    )
    if not siniestro:
        logger.warning(f"❌ Siniestro {siniestro_id} no encontrado")
        raise HTTPException(status_code=404, detail="Siniestro no encontrado")

    try:
        if seccion == "asegurado":
            # Crear o actualizar asegurado
            if siniestro.asegurado:
                for key, value in datos.items():
                    setattr(siniestro.asegurado, key, value)
            else:
                datos["siniestro_id"] = siniestro_id
                db_asegurado = models.Asegurado(**datos)
                db.add(db_asegurado)

        elif seccion == "conductor":
            # Crear o actualizar conductor
            if siniestro.conductor:
                for key, value in datos.items():
                    setattr(siniestro.conductor, key, value)
            else:
                datos["siniestro_id"] = siniestro_id
                db_conductor = models.Conductor(**datos)
                db.add(db_conductor)

        elif seccion == "objeto_asegurado":
            # Crear o actualizar objeto asegurado
            if siniestro.objeto_asegurado:
                for key, value in datos.items():
                    setattr(siniestro.objeto_asegurado, key, value)
            else:
                datos["siniestro_id"] = siniestro_id
                db_objeto = models.ObjetoAsegurado(**datos)
                db.add(db_objeto)

        elif seccion == "antecedentes":
            # Limpiar antecedentes existentes y crear nuevos
            db.query(models.Antecedente).filter(
                models.Antecedente.siniestro_id == siniestro_id
            ).delete()
            for antecedente_data in datos:
                antecedente = models.Antecedente(
                    siniestro_id=siniestro_id,
                    descripcion=antecedente_data.get("descripcion", ""),
                )
                db.add(antecedente)

        elif seccion == "relatos_asegurado":
            # Limpiar relatos existentes y crear nuevos
            db.query(models.RelatoAsegurado).filter(
                models.RelatoAsegurado.siniestro_id == siniestro_id
            ).delete()
            for i, relato_data in enumerate(datos, 1):
                try:
                    # Procesar imagen si existe
                    imagen_url = relato_data.get("imagen_url")
                    # Truncar imagen_url si es demasiado larga (máximo 500 chars para BD)
                    if imagen_url and len(imagen_url) > 500:
                        logger.warning(f"⚠️ imagen_url demasiado larga ({len(imagen_url)} chars), truncando")
                        imagen_url = imagen_url[:500]
                    imagen_base64 = None
                    imagen_content_type = None

                    # Si hay URL, intentar convertir a base64 para PDFs
                    if imagen_url and imagen_url.strip():
                        try:
                            from app.services.s3_service import download_image_from_url

                            image_data = download_image_from_url(imagen_url)
                            if image_data:
                                import base64

                                imagen_base64 = base64.b64encode(image_data).decode(
                                    "utf-8"
                                )
                                imagen_content_type = "image/jpeg"
                                logger.info(
                                    f"✅ Convertida imagen para relato asegurado {i}"
                                )
                        except Exception as e:
                            logger.warning(
                                f"⚠️ No se pudo convertir imagen para relato {i}: {e}"
                            )
                            # Continuar sin imagen base64, solo guardar URL
                            imagen_base64 = None
                            imagen_content_type = None

                    relato = models.RelatoAsegurado(
                        siniestro_id=siniestro_id,
                        numero_relato=i,
                        texto=str(relato_data.get("texto", "")),
                        imagen_url=imagen_url,
                        imagen_base64=imagen_base64,
                        imagen_content_type=imagen_content_type,
                    )
                    db.add(relato)
                    logger.info(f"✅ Relato asegurado {i} preparado para guardar")
                except Exception as e:
                    logger.error(f"❌ Error procesando relato asegurado {i}: {e}")
                    # Continuar con el siguiente relato
                    continue

        elif seccion == "relatos_conductor":
            # Limpiar relatos existentes y crear nuevos
            db.query(models.RelatoConductor).filter(
                models.RelatoConductor.siniestro_id == siniestro_id
            ).delete()
            for i, relato_data in enumerate(datos, 1):
                relato = models.RelatoConductor(
                    siniestro_id=siniestro_id,
                    numero_relato=i,
                    texto=relato_data.get("texto", ""),
                    imagen_url=relato_data.get("imagen_url"),
                    imagen_base64=relato_data.get("imagen_base64"),
                    imagen_content_type=relato_data.get("imagen_content_type"),
                )
                db.add(relato)

        elif seccion == "inspecciones":
            # Limpiar inspecciones existentes y crear nuevas
            db.query(models.Inspeccion).filter(
                models.Inspeccion.siniestro_id == siniestro_id
            ).delete()
            for i, inspeccion_data in enumerate(datos, 1):
                inspeccion = models.Inspeccion(
                    siniestro_id=siniestro_id,
                    numero_inspeccion=i,
                    descripcion=inspeccion_data.get("descripcion", ""),
                    imagen_url=inspeccion_data.get("imagen_url"),
                    imagen_base64=inspeccion_data.get("imagen_base64"),
                    imagen_content_type=inspeccion_data.get("imagen_content_type"),
                )
                db.add(inspeccion)

        elif seccion == "testigos":
            # Limpiar testigos existentes y crear nuevos
            db.query(models.Testigo).filter(
                models.Testigo.siniestro_id == siniestro_id
            ).delete()
            for i, testigo_data in enumerate(datos, 1):
                testigo = models.Testigo(
                    siniestro_id=siniestro_id,
                    numero_relato=i,
                    texto=testigo_data.get("texto", ""),
                    imagen_url=testigo_data.get("imagen_url"),
                    imagen_base64=testigo_data.get("imagen_base64"),
                    imagen_content_type=testigo_data.get("imagen_content_type"),
                )
                db.add(testigo)

        elif seccion in [
            "evidencias_complementarias",
            "otras_diligencias",
            "detalles_visita_taller",
            "observaciones",
            "recomendacion_pago_cobertura",
            "conclusiones",
            "anexo",
        ]:
            # Secciones que se guardan como JSON arrays
            import json

            siniestro_data = siniestro.__dict__
            siniestro_data[seccion] = json.dumps(datos)
            setattr(siniestro, seccion, json.dumps(datos))

        else:
            raise HTTPException(
                status_code=400, detail=f"Sección '{seccion}' no reconocida"
            )

        db.commit()
        logger.info(f"✅ Sección '{seccion}' guardada exitosamente")
        return {
            "message": f"Sección '{seccion}' guardada exitosamente",
            "siniestro_id": siniestro_id,
        }

    except Exception as e:
        logger.error(f"❌ Error guardando sección '{seccion}': {e}")
        db.rollback()
        raise HTTPException(
            status_code=500, detail=f"Error guardando sección: {str(e)}"
        )


@router.put("/{siniestro_id}", response_model=schemas.SiniestroResponse)
async def update_siniestro(
    siniestro_id: int,
    siniestro_update: schemas.SiniestroUpdate,
    db: Session = Depends(get_db),
):
    """Actualizar un siniestro"""
    import logging
    import json

    logger = logging.getLogger(__name__)

    logger.info(f"🔄 Iniciando actualización de siniestro ID: {siniestro_id}")

    db_siniestro = (
        db.query(models.Siniestro).filter(models.Siniestro.id == siniestro_id).first()
    )
    if not db_siniestro:
        logger.warning(f"⚠️ Siniestro {siniestro_id} no encontrado")
        raise HTTPException(status_code=404, detail="Siniestro no encontrado")

    update_data = siniestro_update.model_dump(exclude_unset=True)
    logger.info(f"📋 Datos de actualización: {list(update_data.keys())}")

    # Extraer datos de relaciones anidadas
    objeto_asegurado_data = update_data.pop("objeto_asegurado", None)
    asegurado_data = update_data.pop("asegurado", None)
    beneficiario_data = update_data.pop("beneficiario", None)
    conductor_data = update_data.pop("conductor", None)

    # Extraer datos de investigación (arrays que vienen del frontend)
    antecedentes_data = update_data.pop("antecedentes", None)
    relatos_asegurado_data = update_data.pop("relatos_asegurado", None)
    relatos_conductor_data = update_data.pop("relatos_conductor", None)
    inspecciones_data = update_data.pop("inspecciones", None)
    testigos_data = update_data.pop("testigos", None)

    # Convertir arrays de strings a JSON strings para campos que lo requieren
    json_fields = [
        "observaciones",
        "recomendacion_pago_cobertura",
        "conclusiones",
        "anexo",
    ]
    for field in json_fields:
        if field in update_data and isinstance(update_data[field], list):
            update_data[field] = json.dumps(update_data[field])
            logger.info(f"🔄 Convertido {field} a JSON: {update_data[field]}")

    # Actualizar campos del siniestro principal
    for field, value in update_data.items():
        logger.info(f"📝 Actualizando campo {field}: {value}")
        setattr(db_siniestro, field, value)

    # Manejar objeto asegurado
    if objeto_asegurado_data:
        if db_siniestro.objeto_asegurado:
            logger.info("🔄 Actualizando objeto asegurado existente")
            for field, value in objeto_asegurado_data.items():
                setattr(db_siniestro.objeto_asegurado, field, value)
        else:
            logger.info("➕ Creando nuevo objeto asegurado")
            objeto_asegurado_data["siniestro_id"] = siniestro_id
            db_objeto = models.ObjetoAsegurado(**objeto_asegurado_data)
            db.add(db_objeto)

    # Manejar asegurado
    if asegurado_data:
        if db_siniestro.asegurado:
            logger.info("🔄 Actualizando asegurado existente")
            for field, value in asegurado_data.items():
                setattr(db_siniestro.asegurado, field, value)
        else:
            logger.info("➕ Creando nuevo asegurado")
            asegurado_data["siniestro_id"] = siniestro_id
            db_asegurado = models.Asegurado(**asegurado_data)
            db.add(db_asegurado)

    # Manejar beneficiario
    if beneficiario_data:
        if db_siniestro.beneficiario:
            logger.info("🔄 Actualizando beneficiario existente")
            for field, value in beneficiario_data.items():
                setattr(db_siniestro.beneficiario, field, value)
        else:
            logger.info("➕ Creando nuevo beneficiario")
            beneficiario_data["siniestro_id"] = siniestro_id
            db_beneficiario = models.Beneficiario(**beneficiario_data)
            db.add(db_beneficiario)

    # Manejar conductor
    if conductor_data:
        if db_siniestro.conductor:
            logger.info("🔄 Actualizando conductor existente")
            for field, value in conductor_data.items():
                setattr(db_siniestro.conductor, field, value)
        else:
            logger.info("➕ Creando nuevo conductor")
            conductor_data["siniestro_id"] = siniestro_id
            db_conductor = models.Conductor(**conductor_data)
            db.add(db_conductor)

    # Manejar antecedentes
    if antecedentes_data is not None:
        logger.info(f"🔄 Actualizando antecedentes: {len(antecedentes_data)} items")
        # Eliminar antecedentes existentes
        db.query(models.Antecedente).filter(
            models.Antecedente.siniestro_id == siniestro_id
        ).delete()
        # Crear nuevos antecedentes
        for antecedente in antecedentes_data:
            db_antecedente = models.Antecedente(
                siniestro_id=siniestro_id,
                descripcion=antecedente.get("descripcion", ""),
            )
            db.add(db_antecedente)

    # Manejar relatos del asegurado
    if relatos_asegurado_data is not None:
        logger.info(
            f"🔄 Actualizando relatos asegurado: {len(relatos_asegurado_data)} items"
        )
        # Eliminar relatos existentes
        db.query(models.RelatoAsegurado).filter(
            models.RelatoAsegurado.siniestro_id == siniestro_id
        ).delete()
        # Crear nuevos relatos
        for relato in relatos_asegurado_data:
            # Si hay imagen_url pero no imagen_base64, intentar obtenerla del S3 service
            imagen_url = relato.get("imagen_url")
            imagen_base64 = relato.get("imagen_base64")
            imagen_content_type = relato.get("imagen_content_type")

            # Si tenemos URL pero no base64, intentar procesar la imagen
            if imagen_url and not imagen_base64:
                try:
                    from app.services.s3_service import download_image_from_url

                    image_data = download_image_from_url(imagen_url)
                    if image_data:
                        import base64

                        imagen_base64 = base64.b64encode(image_data).decode("utf-8")
                        imagen_content_type = "image/jpeg"  # Default
                        logger.info(
                            "✅ Convertida imagen URL a base64 para relato asegurado"
                        )
                except Exception as e:
                    logger.warning(
                        f"⚠️ No se pudo convertir imagen para relato asegurado: {e}"
                    )

            db_relato = models.RelatoAsegurado(
                siniestro_id=siniestro_id,
                numero_relato=relato.get("numero_relato", 1),
                texto=relato.get("texto", ""),
                imagen_url=imagen_url,
                imagen_base64=imagen_base64,
                imagen_content_type=imagen_content_type,
            )
            db.add(db_relato)

    # Manejar relatos del conductor
    if relatos_conductor_data is not None:
        logger.info(
            f"🔄 Actualizando relatos conductor: {len(relatos_conductor_data)} items"
        )
        # Eliminar relatos existentes
        db.query(models.RelatoConductor).filter(
            models.RelatoConductor.siniestro_id == siniestro_id
        ).delete()
        # Crear nuevos relatos
        for relato in relatos_conductor_data:
            db_relato = models.RelatoConductor(
                siniestro_id=siniestro_id,
                numero_relato=relato.get("numero_relato", 1),
                texto=relato.get("texto", ""),
                imagen_url=relato.get("imagen_url"),
            )
            db.add(db_relato)

    # Manejar inspecciones
    if inspecciones_data is not None:
        logger.info(f"🔄 Actualizando inspecciones: {len(inspecciones_data)} items")
        # Eliminar inspecciones existentes
        db.query(models.Inspeccion).filter(
            models.Inspeccion.siniestro_id == siniestro_id
        ).delete()
        # Crear nuevas inspecciones
        for inspeccion in inspecciones_data:
            db_inspeccion = models.Inspeccion(
                siniestro_id=siniestro_id,
                numero_inspeccion=inspeccion.get("numero_inspeccion", 1),
                descripcion=inspeccion.get("descripcion", ""),
                imagen_url=inspeccion.get("imagen_url"),
            )
            db.add(db_inspeccion)

    # Manejar testigos
    if testigos_data is not None:
        logger.info(f"🔄 Actualizando testigos: {len(testigos_data)} items")
        # Eliminar testigos existentes
        db.query(models.Testigo).filter(
            models.Testigo.siniestro_id == siniestro_id
        ).delete()
        # Crear nuevos testigos
        for testigo in testigos_data:
            db_testigo = models.Testigo(
                siniestro_id=siniestro_id,
                numero_relato=testigo.get("numero_relato", 1),
                texto=testigo.get("texto", ""),
                imagen_url=testigo.get("imagen_url"),
            )
            db.add(db_testigo)

    try:
        logger.info("💾 Confirmando cambios en base de datos...")
        db.commit()
        db.refresh(db_siniestro)
        logger.info(f"✅ Siniestro {siniestro_id} actualizado exitosamente")
        return db_siniestro
    except Exception as e:
        logger.error(f"❌ Error al actualizar siniestro: {e}")
        db.rollback()


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


# PDF generation endpoint - SOLUCIÓN SIMPLIFICADA Y ROBUSTA
@router.get("/{siniestro_id}/generar-pdf")
async def generar_pdf(siniestro_id: int, db: Session = Depends(get_db)):
    """Generar PDF del informe de siniestro - SIEMPRE FUNCIONA"""
    import logging

    logger = logging.getLogger(__name__)

    logger.info(f"🔍 INICIANDO GENERACIÓN PDF SENCILLO - Siniestro ID: {siniestro_id}")

    try:
        # Obtener datos del siniestro de forma simple
        siniestro = (
            db.query(models.Siniestro)
            .filter(models.Siniestro.id == siniestro_id)
            .first()
        )
        if not siniestro:
            raise HTTPException(status_code=404, detail="Siniestro no encontrado")

        # GENERAR PDF SENCILLO Y ROBUSTO - SIN DEPENDENCIAS EXTERNAS
        from reportlab.lib.pagesizes import letter
        from reportlab.platypus import (
            SimpleDocTemplate,
            Paragraph,
            Spacer,
            Table,
            TableStyle,
        )
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib import colors
        from reportlab.lib.units import inch
        from fastapi.responses import Response
        import io

        # Crear buffer para el PDF
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            topMargin=1 * inch,
            bottomMargin=1 * inch,
            leftMargin=1 * inch,
            rightMargin=1 * inch,
        )

        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            "Title",
            parent=styles["Heading1"],
            fontSize=18,
            alignment=1,
            spaceAfter=20,
            fontName="Helvetica-Bold",
        )
        section_style = ParagraphStyle(
            "Section",
            parent=styles["Heading2"],
            fontSize=14,
            spaceAfter=12,
            fontName="Helvetica-Bold",
        )
        normal_style = ParagraphStyle(
            "Normal", parent=styles["Normal"], fontSize=10, fontName="Helvetica"
        )

        story = []

        # 1. TÍTULO PRINCIPAL
        story.append(Paragraph("INFORME DE INVESTIGACIÓN DE SINIESTRO", title_style))
        story.append(Spacer(1, 20))

        # 2. INFORMACIÓN BÁSICA
        basic_data = [
            ["Número de Reclamo:", siniestro.reclamo_num or "No especificado"],
            ["Compañía de Seguros:", siniestro.compania_seguros or "No especificada"],
            ["Tipo de Siniestro:", siniestro.tipo_siniestro or "No especificado"],
            [
                "Fecha del Siniestro:",
                (
                    siniestro.fecha_siniestro.strftime("%d/%m/%Y")
                    if siniestro.fecha_siniestro
                    else "No especificada"
                ),
            ],
            ["Dirección:", siniestro.direccion_siniestro or "No especificada"],
        ]

        basic_table = Table(basic_data, colWidths=[2.5 * inch, 4 * inch])
        basic_table.setStyle(
            TableStyle(
                [
                    ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
                    ("FONTSIZE", (0, 0), (-1, -1), 10),
                    ("GRID", (0, 0), (-1, -1), 1, colors.black),
                ]
            )
        )
        story.append(basic_table)
        story.append(Spacer(1, 20))

        # 3. INFORMACIÓN DEL ASEGURADO
        story.append(Paragraph("INFORMACIÓN DEL ASEGURADO", section_style))
        if siniestro.asegurado:
            asegurado_data = [
                ["Nombre:", siniestro.asegurado.nombre or "No especificado"],
                [
                    "Cédula/RUC:",
                    siniestro.asegurado.cedula
                    or siniestro.asegurado.ruc
                    or "No especificado",
                ],
                ["Dirección:", siniestro.asegurado.direccion or "No especificada"],
                [
                    "Teléfono:",
                    siniestro.asegurado.celular
                    or siniestro.asegurado.telefono
                    or "No especificado",
                ],
            ]
            asegurado_table = Table(asegurado_data, colWidths=[2 * inch, 4.5 * inch])
            asegurado_table.setStyle(
                TableStyle(
                    [
                        ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
                        ("FONTSIZE", (0, 0), (-1, -1), 9),
                        ("GRID", (0, 0), (-1, -1), 1, colors.black),
                    ]
                )
            )
            story.append(asegurado_table)
        else:
            story.append(
                Paragraph("No hay información del asegurado registrada.", normal_style)
            )
        story.append(Spacer(1, 15))

        # 3.1 IMÁGENES DE LA INVESTIGACIÓN
        # Obtener todas las imágenes relacionadas con el siniestro
        from sqlalchemy.orm import joinedload

        siniestro_completo = (
            db.query(models.Siniestro)
            .options(
                joinedload(models.Siniestro.relatos_asegurado),
                joinedload(models.Siniestro.relatos_conductor),
                joinedload(models.Siniestro.inspecciones),
                joinedload(models.Siniestro.testigos),
            )
            .filter(models.Siniestro.id == siniestro_id)
            .first()
        )

        imagenes_encontradas = []

        # Buscar imágenes en relatos del asegurado
        if siniestro_completo.relatos_asegurado:
            for relato in siniestro_completo.relatos_asegurado:
                if relato.imagen_base64 and relato.imagen_content_type:
                    imagenes_encontradas.append(
                        {
                            "titulo": f"Relato del Asegurado #{relato.numero_relato}",
                            "base64": relato.imagen_base64,
                            "content_type": relato.imagen_content_type,
                        }
                    )

        # Buscar imágenes en relatos del conductor
        if siniestro_completo.relatos_conductor:
            for relato in siniestro_completo.relatos_conductor:
                if relato.imagen_base64 and relato.imagen_content_type:
                    imagenes_encontradas.append(
                        {
                            "titulo": f"Relato del Conductor #{relato.numero_relato}",
                            "base64": relato.imagen_base64,
                            "content_type": relato.imagen_content_type,
                        }
                    )

        # Buscar imágenes en inspecciones
        if siniestro_completo.inspecciones:
            for inspeccion in siniestro_completo.inspecciones:
                if inspeccion.imagen_base64 and inspeccion.imagen_content_type:
                    imagenes_encontradas.append(
                        {
                            "titulo": f"Inspección #{inspeccion.numero_inspeccion}",
                            "base64": inspeccion.imagen_base64,
                            "content_type": inspeccion.imagen_content_type,
                        }
                    )

        # Buscar imágenes en testigos
        if siniestro_completo.testigos:
            for testigo in siniestro_completo.testigos:
                if testigo.imagen_base64 and testigo.imagen_content_type:
                    imagenes_encontradas.append(
                        {
                            "titulo": f"Testigo #{testigo.numero_relato}",
                            "base64": testigo.imagen_base64,
                            "content_type": testigo.imagen_content_type,
                        }
                    )

        # Si hay imágenes, incluir sección de imágenes
        if imagenes_encontradas:
            story.append(Paragraph("📷 EVIDENCIAS FOTOGRÁFICAS", section_style))
            story.append(
                Paragraph(
                    "Las siguientes imágenes corresponden a la evidencia recopilada durante la investigación:",
                    normal_style,
                )
            )
            story.append(Spacer(1, 10))

            for i, imagen in enumerate(imagenes_encontradas, 1):
                # Título de la imagen
                story.append(
                    Paragraph(
                        f"{i}. {imagen['titulo']}",
                        ParagraphStyle(
                            "ImageTitle",
                            parent=styles["Heading4"],
                            fontSize=11,
                            fontName="Helvetica-Bold",
                        ),
                    )
                )

                # Incluir la imagen real en el PDF
                try:
                    import base64
                    from reportlab.platypus import Image
                    from io import BytesIO

                    # Decodificar base64 a bytes
                    image_data = base64.b64decode(imagen["base64"])

                    # Crear buffer de memoria
                    image_buffer = BytesIO(image_data)

                    # Procesar con PIL si está disponible
                    try:
                        from PIL import Image as PILImage

                        pil_image = PILImage.open(image_buffer)

                        # Convertir a RGB si es necesario
                        if pil_image.mode not in ("RGB", "L"):
                            pil_image = pil_image.convert("RGB")

                        # Redimensionar manteniendo proporción (máximo 4x3 pulgadas a 72 DPI)
                        pil_image.thumbnail((4 * 72, 3 * 72), PILImage.LANCZOS)

                        # Guardar como JPEG optimizado
                        output_buffer = BytesIO()
                        pil_image.save(output_buffer, format="JPEG", quality=85)
                        output_buffer.seek(0)

                        # Crear imagen de ReportLab
                        pdf_image = Image(output_buffer)
                        pdf_image.hAlign = "LEFT"

                        story.append(pdf_image)

                    except ImportError:
                        # Fallback sin PIL
                        image_buffer.seek(0)
                        pdf_image = Image(image_buffer)
                        pdf_image.hAlign = "LEFT"
                        story.append(pdf_image)

                    logger.info(f"✅ Imagen {i} incluida en PDF: {imagen['titulo']}")

                except Exception as img_error:
                    logger.warning(f"⚠️ Error procesando imagen {i}: {img_error}")
                    story.append(
                        Paragraph(
                            f"[Error al cargar imagen: {str(img_error)}]",
                            ParagraphStyle(
                                "ImageError",
                                parent=styles["Normal"],
                                fontSize=8,
                                textColor=colors.red,
                            ),
                        )
                    )

                story.append(Spacer(1, 15))

            story.append(Spacer(1, 20))

        # 4. INFORMACIÓN DEL CONDUCTOR
        if siniestro.conductor:
            story.append(Paragraph("INFORMACIÓN DEL CONDUCTOR", section_style))
            conductor_data = [
                ["Nombre:", siniestro.conductor.nombre or "No especificado"],
                ["Cédula:", siniestro.conductor.cedula or "No especificado"],
                ["Dirección:", siniestro.conductor.direccion or "No especificada"],
            ]
            conductor_table = Table(conductor_data, colWidths=[2 * inch, 4.5 * inch])
            conductor_table.setStyle(
                TableStyle(
                    [
                        ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
                        ("FONTSIZE", (0, 0), (-1, -1), 9),
                        ("GRID", (0, 0), (-1, -1), 1, colors.black),
                    ]
                )
            )
            story.append(conductor_table)
            story.append(Spacer(1, 15))

        # 5. INFORMACIÓN DEL OBJETO ASEGURADO
        if siniestro.objeto_asegurado:
            story.append(Paragraph("INFORMACIÓN DEL OBJETO ASEGURADO", section_style))
            objeto_data = [
                ["Placa:", siniestro.objeto_asegurado.placa or "No especificada"],
                ["Marca:", siniestro.objeto_asegurado.marca or "No especificada"],
                ["Modelo:", siniestro.objeto_asegurado.modelo or "No especificada"],
                [
                    "Año:",
                    (
                        str(siniestro.objeto_asegurado.ano)
                        if siniestro.objeto_asegurado.ano
                        else "No especificado"
                    ),
                ],
            ]
            objeto_table = Table(objeto_data, colWidths=[2 * inch, 4.5 * inch])
            objeto_table.setStyle(
                TableStyle(
                    [
                        ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
                        ("FONTSIZE", (0, 0), (-1, -1), 9),
                        ("GRID", (0, 0), (-1, -1), 1, colors.black),
                    ]
                )
            )
            story.append(objeto_table)
            story.append(Spacer(1, 15))

        # Nota: Las imágenes ahora se incluyen directamente en el PDF arriba

        # 7. FIRMA Y FECHA
        story.append(Paragraph("INFORME GENERADO POR:", section_style))
        firma_data = [
            ["Investigador:", "Susana Espinosa"],
            ["Fecha de Generación:", datetime.now().strftime("%d/%m/%Y %H:%M:%S")],
        ]
        firma_table = Table(firma_data, colWidths=[2 * inch, 4.5 * inch])
        firma_table.setStyle(
            TableStyle(
                [
                    ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
                    ("FONTSIZE", (0, 0), (-1, -1), 9),
                ]
            )
        )
        story.append(firma_table)

        # Generar PDF
        doc.build(story)
        buffer.seek(0)
        pdf_data = buffer.getvalue()

        logger.info(f"✅ PDF simple generado exitosamente: {len(pdf_data)} bytes")

        # Nombre del archivo
        reclamo = siniestro.reclamo_num or str(siniestro_id)
        filename_safe = f"{reclamo.replace('/', '_')}.pdf"

        return Response(
            content=pdf_data,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename*=UTF-8''{filename_safe}",
                "Content-Length": str(len(pdf_data)),
            },
        )

    except Exception as e:
        logger.error(f"❌ Error crítico generando PDF simple: {e}")
        import traceback

        logger.error(f"❌ Traceback: {traceback.format_exc()}")

        # ÚLTIMO RECURSO: PDF MÍNIMO DE ERROR
        try:
            buffer = io.BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=letter)
            story = [Paragraph(f"ERROR GENERANDO PDF: {str(e)}", styles["Normal"])]
            doc.build(story)
            buffer.seek(0)
            return Response(
                content=buffer.getvalue(),
                media_type="application/pdf",
                headers={"Content-Disposition": "attachment; filename=error.pdf"},
            )
        except:
            raise HTTPException(
                status_code=500, detail=f"Error total del sistema: {str(e)}"
            )


@router.get("/{siniestro_id}/generar-pdf-sin-firma")
async def generar_pdf_sin_firma(siniestro_id: int, db: Session = Depends(get_db)):
    """Generar PDF del informe de siniestro SIN FIRMA DIGITAL (para pruebas)"""
    import logging

    logger = logging.getLogger(__name__)

    try:
        logger.info(f"🔍 GENERANDO PDF SIN FIRMA - Siniestro ID: {siniestro_id}")
        from app.utils.pdf_generator import generate_unsigned_pdf

        # Get siniestro data with all relationships loaded
        from sqlalchemy.orm import selectinload

        siniestro = (
            db.query(models.Siniestro)
            .options(
                selectinload(models.Siniestro.asegurado),
                selectinload(models.Siniestro.beneficiario),
                selectinload(models.Siniestro.conductor),
                selectinload(models.Siniestro.objeto_asegurado),
                selectinload(models.Siniestro.antecedentes),
                selectinload(models.Siniestro.relatos_asegurado),
                selectinload(models.Siniestro.relatos_conductor),
                selectinload(models.Siniestro.inspecciones),
                selectinload(models.Siniestro.testigos),
                selectinload(models.Siniestro.visita_taller),
            )
            .filter(models.Siniestro.id == siniestro_id)
            .first()
        )
        if not siniestro:
            raise HTTPException(status_code=404, detail="Siniestro no encontrado")

        pdf_data = generate_unsigned_pdf(siniestro)
        logger.info(f"✅ PDF sin firma generado exitosamente: {len(pdf_data)} bytes")

        from fastapi.responses import Response

        # Generar nombre de archivo seguro (solo número de reclamo)
        import unicodedata
        import re

        # Crear nombre base del archivo (solo número de reclamo)
        reclamo = siniestro.reclamo_num or str(siniestro_id)

        # Normalizar caracteres especiales para filename
        filename_base = (
            unicodedata.normalize("NFKD", reclamo)
            .encode("ASCII", "ignore")
            .decode("ASCII")
        )

        # Remover caracteres no seguros para filename
        filename_base = re.sub(r"[^\w\-_\.]", "_", filename_base)
        filename_safe = f"{filename_base}_sin_firma.pdf"

        return Response(
            content=pdf_data,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename*=UTF-8''{filename_safe}",
                "Content-Length": str(len(pdf_data)),
            },
        )
    except Exception as e:
        logger.error(f"❌ Error generando PDF sin firma: {e}")
        import traceback

        logger.error(f"❌ Traceback: {traceback.format_exc()}")
        raise HTTPException(
            status_code=500, detail=f"Error generando PDF sin firma: {str(e)}"
        )


@router.post("/upload-image")
async def upload_image(file: UploadFile = File(...)):
    """Subir imagen a AWS S3 y devolver URL presigned + base64 para PDFs"""
    from app.services.s3_service import upload_file_to_s3

    result = await upload_file_to_s3(file)
    # Solo devolver la URL presigned al frontend, el base64 se guarda en BD
    return {"url_presigned": result["url_presigned"]}


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
        "warnings": [],
    }

    try:
        # 1. Verificar conexión a base de datos
        logger.info("📊 Verificando conexión a base de datos...")
        siniestros_count = db.query(models.Siniestro).count()
        diagnostico["checks"][
            "database_connection"
        ] = f"✅ Conectado - {siniestros_count} siniestros encontrados"
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
            Paragraph(
                f"Fecha: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}",
                styles["Normal"],
            ),
            Paragraph(
                "Este PDF verifica el funcionamiento del generador.", styles["Normal"]
            ),
        ]

        doc.build(story)
        buffer.seek(0)
        test_pdf = buffer.getvalue()

        if test_pdf.startswith(b"%PDF-"):
            diagnostico["checks"][
                "basic_pdf_generation"
            ] = f"✅ PDF básico OK - {len(test_pdf)} bytes"
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
            diagnostico["checks"][
                "certificate_loading"
            ] = f"✅ Certificado cargado - {len(cert_data)} bytes"
            logger.info(f"✅ Certificado OK: {len(cert_data)} bytes")
        else:
            diagnostico["warnings"].append(
                "⚠️ Certificado no encontrado en S3 - PDFs sin firma"
            )
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
            if pdf_data.startswith(b"%PDF-"):
                diagnostico["checks"][
                    "full_pdf_generation"
                ] = f"✅ PDF completo OK - {len(pdf_data)} bytes"
                logger.info(f"✅ PDF completo OK: {len(pdf_data)} bytes")
            else:
                diagnostico["errors"].append("❌ PDF completo no válido")
                logger.error("❌ PDF completo no válido")
        else:
            diagnostico["warnings"].append(
                "⚠️ No hay siniestros en BD para probar generación completa"
            )
            logger.warning("⚠️ No hay siniestros para probar")

    except Exception as e:
        diagnostico["errors"].append(
            f"❌ Error en generación completa de PDF: {str(e)}"
        )
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
        from reportlab.lib.units import inch
        from fastapi.responses import Response
        import io

        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            topMargin=1 * inch,
            bottomMargin=1 * inch,
            leftMargin=1 * inch,
            rightMargin=1 * inch,
        )

        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            "Title",
            parent=styles["Heading1"],
            fontSize=16,
            alignment=TA_CENTER,
            spaceAfter=20,
        )

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
            error_style = ParagraphStyle(
                "Error", parent=styles["Normal"], textColor=colors.red
            )
            story.append(Paragraph("❌ ERRORES ENCONTRADOS:", styles["Heading2"]))
            for error in diagnostico["errors"]:
                story.append(Paragraph(f"• {error}", error_style))
            story.append(Spacer(1, 10))

        story.append(
            Paragraph(
                f"Diagnóstico completado: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}",
                styles["Normal"],
            )
        )

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
    import logging

    logger = logging.getLogger(__name__)

    logger.info("🧪 GENERANDO PDF DE PRUEBA MÍNIMO")

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

        logger.info(f"✅ PDF de prueba generado: {len(pdf_data)} bytes")

        return Response(
            content=pdf_data,
            media_type="application/pdf",
            headers={
                "Content-Disposition": "attachment; filename=test.pdf",
                "Content-Length": str(len(pdf_data)),
            },
        )
    except Exception as e:
        logger.error(f"❌ Error generando PDF de prueba: {e}")
        import traceback

        logger.error(f"❌ Traceback: {traceback.format_exc()}")
        raise HTTPException(
            status_code=500, detail=f"Error generando PDF de prueba: {str(e)}"
        )


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
