import io
import logging
import os
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    PageTemplate,
    Frame,
    NextPageTemplate,
)
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.pdfgen import canvas
from sqlalchemy.orm import Session
from ..models import Siniestro


def header_footer(canvas, doc):
    """Función para dibujar header y footer en cada página"""
    # Obtener el ancho y alto de la página
    width, height = letter

    # ==================== HEADER ====================
    # Línea superior
    canvas.setStrokeColor(colors.black)
    canvas.setLineWidth(1)
    canvas.line(
        0.5 * inch, height - 0.5 * inch, width - 0.5 * inch, height - 0.5 * inch
    )

    # Título del header
    canvas.setFont("Helvetica-Bold", 10)
    canvas.drawString(
        0.75 * inch, height - 0.7 * inch, "INFORME DE INVESTIGACIÓN DE SINIESTRO"
    )

    # Número de página en el header (derecha)
    page_num = canvas.getPageNumber()
    canvas.setFont("Helvetica", 8)
    canvas.drawRightString(
        width - 0.75 * inch, height - 0.7 * inch, f"Página {page_num}"
    )

    # ==================== FOOTER ====================
    # Línea inferior
    canvas.setStrokeColor(colors.black)
    canvas.setLineWidth(1)
    canvas.line(0.5 * inch, 0.5 * inch, width - 0.5 * inch, 0.5 * inch)

    # Información del footer
    canvas.setFont("Helvetica", 8)
    footer_text = "Sistema de Gestión de Siniestros - Susana Espinosa"
    canvas.drawString(0.75 * inch, 0.3 * inch, footer_text)

    # Fecha en el footer (derecha)
    fecha_actual = datetime.now().strftime("%d/%m/%Y")
    canvas.drawRightString(width - 0.75 * inch, 0.3 * inch, f"Fecha: {fecha_actual}")


logger = logging.getLogger(__name__)

try:
    from endesive.pdf import cms
    from cryptography.hazmat.primitives.serialization import pkcs12

    CRYPTO_AVAILABLE = True
    logger.info("✅ Bibliotecas de criptografía disponibles")
except ImportError as e:
    CRYPTO_AVAILABLE = False
    logger.warning(f"⚠️ Bibliotecas de criptografía no disponibles: {e}")


def load_certificate_from_s3(
    cert_key: str = "certificates/maria_susana_espinosa_lozada.p12",
) -> tuple[bytes, str]:
    """Cargar certificado desde S3 y retornar datos + contraseña"""
    try:
        # Importar configuración de S3 con ruta relativa correcta
        from ..services.s3_service import get_s3_client, S3_BUCKET_NAME

        s3_client = get_s3_client()
        response = s3_client.get_object(Bucket=S3_BUCKET_NAME, Key=cert_key)
        cert_data = response["Body"].read()

        # Obtener contraseña desde variables de entorno
        password = os.getenv("CERT_PASSWORD", "")

        logger.info(f"✅ Certificado cargado desde S3: {len(cert_data)} bytes")
        return cert_data, password

    except Exception as e:
        logger.warning(f"❌ No se pudo cargar certificado desde S3: {e}")
        return None, None


def sign_pdf(
    pdf_data: bytes, certificate_data: bytes = None, password: str = None
) -> bytes:
    """Firmar PDF digitalmente usando certificado P12"""
    try:
        logger.info("🔐 Firmando PDF con certificado digital")

        # Usar datos del certificado proporcionados
        p12_data = certificate_data

        # Extraer clave privada y certificado
        from cryptography.hazmat.primitives.serialization import pkcs12

        private_key, certificate, additional_certificates = (
            pkcs12.load_key_and_certificates(
                p12_data, password.encode() if password else None
            )
        )

        # Preparar datos para firma
        date = datetime.now().strftime("D:%Y%m%d%H%M%S+00'00'")
        dct = {
            "aligned": 0,
            "sigflags": 3,
            "sigflagsft": 132,
            "sigpage": 0,
            "sigbutton": True,
            "sigfield": "Signature1",
            "auto_sigfield": True,
            "sigandcertify": True,
            "signaturebox": (470, 840, 570, 640),
            "signature": "Documento firmado electrónicamente",
            "contact": "sistema@siniestros.com",
            "location": "Quito, Ecuador",
            "signingdate": date,
            "reason": "Firma digital de informe de siniestro",
            "password": password or "",
        }

        # Crear firma
        signed_pdf = cms.sign(
            pdf_data, dct, private_key, certificate, additional_certificates or []
        )

        logger.info(f"✅ PDF firmado exitosamente: {len(signed_pdf)} bytes")
        return signed_pdf

    except Exception as e:
        logger.error(f"❌ Error firmando PDF: {e}")
        # Retornar PDF sin firma si hay error
        return pdf_data


def generate_simple_pdf(siniestro: Siniestro) -> bytes:
    """Generar PDF completo del informe de siniestro con saltos de página entre secciones"""
    logger.info(f"🔄 Generando PDF completo para siniestro ID: {siniestro.id}")

    try:
        # Crear buffer para el PDF
        buffer = io.BytesIO()

        # Crear documento con headers/footers
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            topMargin=1 * inch,
            bottomMargin=1 * inch,
            leftMargin=1 * inch,
            rightMargin=1 * inch,
        )

        # Agregar función de header/footer
        doc.onFirstPage = header_footer
        doc.onLaterPages = header_footer
        styles = getSampleStyleSheet()

        # Estilos personalizados
        title_style = ParagraphStyle(
            "Title",
            parent=styles["Heading1"],
            fontSize=20,
            alignment=TA_CENTER,
            spaceAfter=30,
            fontName="Helvetica-Bold",
        )

        subtitle_style = ParagraphStyle(
            "Subtitle",
            parent=styles["Heading2"],
            fontSize=16,
            alignment=TA_CENTER,
            spaceAfter=20,
            fontName="Helvetica-Bold",
        )

        section_style = ParagraphStyle(
            "Section",
            parent=styles["Heading3"],
            fontSize=14,
            spaceAfter=15,
            fontName="Helvetica-Bold",
        )

        normal_style = ParagraphStyle(
            "Normal", parent=styles["Normal"], fontSize=10, fontName="Helvetica"
        )

        story = []

        # ==================== CARÁTULA ====================
        logger.info("📄 Generando carátula...")

        # Título principal
        title = Paragraph("INFORME DE INVESTIGACIÓN<br/>DE SINIESTRO", title_style)
        story.append(title)

        # Información del siniestro en la carátula (solo campos solicitados)
        caratula_data = [
            ["Compañía de Seguros:", siniestro.compania_seguros or ""],
            ["Número de Reclamo:", siniestro.reclamo_num or ""],
            [
                "Asegurado:",
                (
                    siniestro.asegurado.nombre
                    if siniestro.asegurado and siniestro.asegurado.nombre
                    else ""
                ),
            ],
            ["Nombre de Investigador:", "Susana Espinosa"],
        ]

        # Solo mostrar filas que tengan información
        caratula_data_filtered = [row for row in caratula_data if row[1].strip()]

        if caratula_data_filtered:
            caratula_table = Table(
                caratula_data_filtered, colWidths=[2.2 * inch, 4.3 * inch]
            )
            caratula_table.setStyle(
                TableStyle(
                    [
                        ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
                        ("FONTSIZE", (0, 0), (-1, -1), 12),
                        ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                        ("BACKGROUND", (0, 0), (0, -1), colors.lightgrey),
                        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                        ("LEFTPADDING", (0, 0), (-1, -1), 6),
                        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                        ("TOPPADDING", (0, 0), (-1, -1), 4),
                        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                    ]
                )
            )
            story.append(caratula_table)
            story.append(Spacer(1, 40))

        # Fecha de generación
        fecha_gen = Paragraph(
            f"Fecha de Generación: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}",
            ParagraphStyle(
                "Fecha", parent=styles["Normal"], fontSize=10, alignment=TA_CENTER
            ),
        )
        story.append(fecha_gen)

        # Salto de página explícito antes del Índice
        from reportlab.platypus import PageBreak

        story.append(PageBreak())

        # ==================== ÍNDICE EN PÁGINA SEPARADA ====================
        logger.info("📋 Generando índice en página separada...")

        indice_title = Paragraph("ÍNDICE", subtitle_style)
        story.append(indice_title)
        story.append(Spacer(1, 20))

        # Crear índice dinámico basado en secciones que tienen contenido
        indice_items = []
        page_num = 3  # Página del registro del siniestro (ahora página 3)

        # Siempre incluir registro del siniestro
        indice_items.append(f"{page_num}. REGISTRO DEL SINIESTRO")

        # Verificar qué secciones de investigación tienen contenido
        has_investigacion = (
            siniestro.antecedentes
            or siniestro.relatos_asegurado
            or siniestro.relatos_conductor
            or siniestro.inspecciones
            or siniestro.testigos
            or (
                siniestro.evidencias_complementarias
                and siniestro.evidencias_complementarias.strip()
            )
            or (siniestro.otras_diligencias and siniestro.otras_diligencias.strip())
            or (
                siniestro.visita_taller
                and siniestro.visita_taller.descripcion
                and siniestro.visita_taller.descripcion.strip()
            )
            or (siniestro.observaciones and siniestro.observaciones.strip())
            or (
                siniestro.recomendacion_pago_cobertura
                and siniestro.recomendacion_pago_cobertura.strip()
            )
            or (siniestro.conclusiones and siniestro.conclusiones.strip())
            or (siniestro.anexo and siniestro.anexo.strip())
        )

        if has_investigacion:
            indice_items.append(f"{page_num + 1}. INVESTIGACIÓN")
            page_num += 1

        # Agregar anexos si hay
        if siniestro.anexo and siniestro.anexo.strip():
            indice_items.append(f"{page_num + 1}. ANEXOS")
            page_num += 1

        # Siempre agregar cierre
        indice_items.append(f"{page_num + 1}. CIERRE")

        for item in indice_items:
            story.append(Paragraph(item, normal_style))
            story.append(Spacer(1, 5))

        # Salto de página explícito antes del Registro del Siniestro
        story.append(PageBreak())

        # ==================== REGISTRO DEL SINIESTRO ====================
        logger.info("📝 Generando registro del siniestro...")

        registro_title = Paragraph("REGISTRO DEL SINIESTRO", section_style)
        story.append(registro_title)
        story.append(Spacer(1, 15))

        # Datos básicos del siniestro (solo filas con información)
        registro_data_raw = [
            ["Compañía de Seguros:", siniestro.compania_seguros or ""],
            ["RUC Compañía:", siniestro.ruc_compania or ""],
            ["Tipo de Reclamo:", siniestro.tipo_reclamo or ""],
            ["Póliza:", siniestro.poliza or ""],
            ["Número de Reclamo:", siniestro.reclamo_num or ""],
            [
                "Fecha del Siniestro:",
                (
                    siniestro.fecha_siniestro.strftime("%d/%m/%Y")
                    if siniestro.fecha_siniestro
                    else ""
                ),
            ],
            [
                "Fecha Reportado:",
                (
                    siniestro.fecha_reportado.strftime("%d/%m/%Y")
                    if siniestro.fecha_reportado
                    else ""
                ),
            ],
            ["Dirección del Siniestro:", siniestro.direccion_siniestro or ""],
            [
                "Ubicación Geo Lat:",
                str(siniestro.ubicacion_geo_lat) if siniestro.ubicacion_geo_lat else "",
            ],
            [
                "Ubicación Geo Lng:",
                str(siniestro.ubicacion_geo_lng) if siniestro.ubicacion_geo_lng else "",
            ],
            ["Daños a Terceros:", "Sí" if siniestro.danos_terceros else ""],
            ["Ejecutivo a Cargo:", siniestro.ejecutivo_cargo or ""],
            [
                "Fecha de Designación:",
                (
                    siniestro.fecha_designacion.strftime("%d/%m/%Y")
                    if siniestro.fecha_designacion
                    else ""
                ),
            ],
            ["Tipo de Siniestro:", siniestro.tipo_siniestro or ""],
            ["Cobertura:", siniestro.cobertura or ""],
        ]

        # Filtrar solo filas que tengan información
        registro_data = [row for row in registro_data_raw if row[1].strip()]

        if registro_data:
            registro_table = Table(registro_data, colWidths=[2.5 * inch, 4 * inch])
            registro_table.setStyle(
                TableStyle(
                    [
                        ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
                        ("FONTSIZE", (0, 0), (-1, -1), 10),
                        ("GRID", (0, 0), (-1, -1), 1, colors.black),
                        ("ALIGN", (0, 0), (0, -1), "LEFT"),
                        ("ALIGN", (1, 0), (1, -1), "LEFT"),
                        ("BACKGROUND", (0, 0), (0, -1), colors.lightgrey),
                        ("LEFTPADDING", (0, 0), (-1, -1), 6),
                        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                        ("TOPPADDING", (0, 0), (-1, -1), 4),
                        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                    ]
                )
            )
            story.append(registro_table)
            story.append(Spacer(1, 20))

        # Declaración del siniestro (solo título si tiene información)
        declaracion_data_raw = [
            [
                "Fecha de Declaración:",
                (
                    siniestro.fecha_declaracion.strftime("%d/%m/%Y")
                    if siniestro.fecha_declaracion
                    else ""
                ),
            ],
            ["Persona que Declara (Tipo):", siniestro.persona_declara_tipo or ""],
            ["Cédula/RUC:", siniestro.persona_declara_cedula or ""],
            ["Nombre/Razón Social:", siniestro.persona_declara_nombre or ""],
            ["Relación:", siniestro.persona_declara_relacion or ""],
        ]

        declaracion_data = [row for row in declaracion_data_raw if row[1].strip()]

        if declaracion_data:
            story.append(Paragraph("Declaración del Siniestro:", section_style))
            declaracion_table = Table(
                declaracion_data, colWidths=[2.5 * inch, 4 * inch]
            )
            declaracion_table.setStyle(
                TableStyle(
                    [
                        ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
                        ("FONTSIZE", (0, 0), (-1, -1), 10),
                        ("GRID", (0, 0), (-1, -1), 1, colors.black),
                        ("ALIGN", (0, 0), (0, -1), "LEFT"),
                        ("ALIGN", (1, 0), (1, -1), "LEFT"),
                        ("BACKGROUND", (0, 0), (0, -1), colors.lightgrey),
                        ("LEFTPADDING", (0, 0), (-1, -1), 6),
                        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                        ("TOPPADDING", (0, 0), (-1, -1), 4),
                        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                    ]
                )
            )
            story.append(declaracion_table)
            story.append(Spacer(1, 15))

        # Información de partes relacionadas (solo títulos si hay contenido)
        if siniestro.asegurado:
            asegurado_data_raw = [
                ["Tipo:", siniestro.asegurado.tipo or ""],
                [
                    "Cédula/RUC:",
                    siniestro.asegurado.cedula or siniestro.asegurado.ruc or "",
                ],
                [
                    "Nombre/Empresa:",
                    siniestro.asegurado.nombre or siniestro.asegurado.empresa or "",
                ],
                ["Representante Legal:", siniestro.asegurado.representante_legal or ""],
                [
                    "Celular:",
                    siniestro.asegurado.celular or siniestro.asegurado.telefono or "",
                ],
                ["Correo:", siniestro.asegurado.correo or ""],
                ["Dirección:", siniestro.asegurado.direccion or ""],
                ["Parentesco:", siniestro.asegurado.parentesco or ""],
            ]

            asegurado_data = [row for row in asegurado_data_raw if row[1].strip()]

            if asegurado_data:
                story.append(Paragraph("Información del Asegurado:", section_style))
                asegurado_table = Table(
                    asegurado_data, colWidths=[2.5 * inch, 4 * inch]
                )
                asegurado_table.setStyle(
                    TableStyle(
                        [
                            ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
                            ("FONTSIZE", (0, 0), (-1, -1), 10),
                            ("GRID", (0, 0), (-1, -1), 1, colors.black),
                            ("ALIGN", (0, 0), (0, -1), "LEFT"),
                            ("ALIGN", (1, 0), (1, -1), "LEFT"),
                            ("BACKGROUND", (0, 0), (0, -1), colors.lightgrey),
                            ("LEFTPADDING", (0, 0), (-1, -1), 6),
                            ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                            ("TOPPADDING", (0, 0), (-1, -1), 4),
                            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                        ]
                    )
                )
                story.append(asegurado_table)
                story.append(Spacer(1, 15))

        if siniestro.beneficiario:
            beneficiario_data_raw = [
                ["Razón Social:", siniestro.beneficiario.razon_social or ""],
                ["Cédula/RUC:", siniestro.beneficiario.cedula_ruc or ""],
                ["Domicilio:", siniestro.beneficiario.domicilio or ""],
            ]

            beneficiario_data = [row for row in beneficiario_data_raw if row[1].strip()]

            if beneficiario_data:
                story.append(Paragraph("Información del Beneficiario:", section_style))
                beneficiario_table = Table(
                    beneficiario_data, colWidths=[2.5 * inch, 4 * inch]
                )
                beneficiario_table.setStyle(
                    TableStyle(
                        [
                            ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
                            ("FONTSIZE", (0, 0), (-1, -1), 10),
                            ("GRID", (0, 0), (-1, -1), 1, colors.black),
                            ("ALIGN", (0, 0), (0, -1), "LEFT"),
                            ("ALIGN", (1, 0), (1, -1), "LEFT"),
                            ("BACKGROUND", (0, 0), (0, -1), colors.lightgrey),
                            ("LEFTPADDING", (0, 0), (-1, -1), 6),
                            ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                            ("TOPPADDING", (0, 0), (-1, -1), 4),
                            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                        ]
                    )
                )
                story.append(beneficiario_table)
                story.append(Spacer(1, 15))

        if siniestro.conductor:
            conductor_data_raw = [
                ["Nombre:", siniestro.conductor.nombre or ""],
                ["Cédula:", siniestro.conductor.cedula or ""],
                ["Celular:", siniestro.conductor.celular or ""],
                ["Dirección:", siniestro.conductor.direccion or ""],
                ["Parentesco:", siniestro.conductor.parentesco or ""],
            ]

            conductor_data = [row for row in conductor_data_raw if row[1].strip()]

            if conductor_data:
                story.append(Paragraph("Información del Conductor:", section_style))
                conductor_table = Table(
                    conductor_data, colWidths=[2.5 * inch, 4 * inch]
                )
                conductor_table.setStyle(
                    TableStyle(
                        [
                            ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
                            ("FONTSIZE", (0, 0), (-1, -1), 10),
                            ("GRID", (0, 0), (-1, -1), 1, colors.black),
                            ("ALIGN", (0, 0), (0, -1), "LEFT"),
                            ("ALIGN", (1, 0), (1, -1), "LEFT"),
                            ("BACKGROUND", (0, 0), (0, -1), colors.lightgrey),
                            ("LEFTPADDING", (0, 0), (-1, -1), 6),
                            ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                            ("TOPPADDING", (0, 0), (-1, -1), 4),
                            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                        ]
                    )
                )
                story.append(conductor_table)
                story.append(Spacer(1, 15))

        if siniestro.objeto_asegurado:
            objeto_data_raw = [
                ["Placa:", siniestro.objeto_asegurado.placa or ""],
                ["Marca:", siniestro.objeto_asegurado.marca or ""],
                ["Modelo:", siniestro.objeto_asegurado.modelo or ""],
                ["Tipo:", siniestro.objeto_asegurado.tipo or ""],
                ["Color:", siniestro.objeto_asegurado.color or ""],
                [
                    "Año:",
                    (
                        str(siniestro.objeto_asegurado.ano)
                        if siniestro.objeto_asegurado.ano
                        else ""
                    ),
                ],
                ["Serie Motor:", siniestro.objeto_asegurado.serie_motor or ""],
                ["Chasis:", siniestro.objeto_asegurado.chasis or ""],
            ]

            objeto_data = [row for row in objeto_data_raw if row[1].strip()]

            if objeto_data:
                story.append(
                    Paragraph("Información del Objeto Asegurado:", section_style)
                )
                objeto_table = Table(objeto_data, colWidths=[2.5 * inch, 4 * inch])
                objeto_table.setStyle(
                    TableStyle(
                        [
                            ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
                            ("FONTSIZE", (0, 0), (-1, -1), 10),
                            ("GRID", (0, 0), (-1, -1), 1, colors.black),
                            ("ALIGN", (0, 0), (0, -1), "LEFT"),
                            ("ALIGN", (1, 0), (1, -1), "LEFT"),
                            ("BACKGROUND", (0, 0), (0, -1), colors.lightgrey),
                            ("LEFTPADDING", (0, 0), (-1, -1), 6),
                            ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                            ("TOPPADDING", (0, 0), (-1, -1), 4),
                            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                        ]
                    )
                )
                story.append(objeto_table)
                story.append(Spacer(1, 15))

        story.append(Spacer(1, 120))  # Salto de página completo

        # ==================== INVESTIGACIÓN ====================
        logger.info("🔍 Generando sección de investigación...")

        # Función auxiliar para verificar si un campo JSON tiene contenido real
        def has_real_content(json_field):
            """Verifica si un campo JSON tiene contenido real (no vacío)"""
            logger.info(f"🔍 DEBUG: verificando campo: {repr(json_field)} (tipo: {type(json_field)})")
            if not json_field:
                logger.info("❌ Campo vacío o None")
                return False
            try:
                parsed = json.loads(json_field) if isinstance(json_field, str) else json_field
                logger.info(f"📋 Campo parseado: {repr(parsed)} (tipo: {type(parsed)})")
                if isinstance(parsed, list):
                    # Filtrar elementos que no sean strings vacías
                    has_content = any(item.strip() for item in parsed if isinstance(item, str))
                    logger.info(f"📋 Lista con contenido real: {has_content} (elementos: {[repr(item) for item in parsed]})")
                    return has_content
                result = bool(parsed)
                logger.info(f"📋 Resultado boolean: {result}")
                return result
            except Exception as e:
                logger.error(f"❌ Error parseando JSON: {e}")
                return bool(json_field and json_field.strip())

        has_any_investigation = (
            siniestro.antecedentes
            or siniestro.relatos_asegurado
            or siniestro.relatos_conductor
            or siniestro.inspecciones
            or siniestro.testigos
            or (
                siniestro.evidencias_complementarias
                and siniestro.evidencias_complementarias.strip()
            )
            or (siniestro.otras_diligencias and siniestro.otras_diligencias.strip())
            or (
                siniestro.visita_taller
                and siniestro.visita_taller.descripcion
                and siniestro.visita_taller.descripcion.strip()
            )
            or has_real_content(siniestro.observaciones)
            or has_real_content(siniestro.recomendacion_pago_cobertura)
            or has_real_content(siniestro.conclusiones)
            or has_real_content(siniestro.anexo)
        )

        if has_any_investigation:
            # Salto de página explícito antes de la Investigación
            story.append(PageBreak())

            investigacion_title = Paragraph("INVESTIGACIÓN", section_style)
            story.append(investigacion_title)
            story.append(Spacer(1, 15))

            section_num = 1

            # 2.1 Antecedentes
            if siniestro.antecedentes:
                story.append(Paragraph(f"{section_num}. Antecedentes", section_style))
                for antecedente in siniestro.antecedentes:
                    story.append(Paragraph(antecedente.descripcion, normal_style))
                    story.append(Spacer(1, 10))
                story.append(Spacer(1, 15))
                section_num += 1

            # 2.2 Entrevista al Asegurado
            if siniestro.relatos_asegurado:
                story.append(
                    Paragraph(f"{section_num}. Entrevista al Asegurado", section_style)
                )
                for i, relato in enumerate(siniestro.relatos_asegurado, 1):
                    story.append(
                        Paragraph(
                            f"Relato {i}:",
                            ParagraphStyle(
                                "Subsection",
                                parent=styles["Heading4"],
                                fontSize=12,
                                fontName="Helvetica-Bold",
                            ),
                        )
                    )
                    story.append(Paragraph(relato.texto, normal_style))
                    # Incluir referencia a imagen si existe
                    if relato.imagen_url and relato.imagen_url.strip():
                        story.append(Paragraph(f"[Imagen adjunta: {i}]", ParagraphStyle(
                            "ImageRef", parent=styles["Normal"], fontSize=8, textColor=colors.blue, fontName="Helvetica-Oblique"
                        )))
                    story.append(Spacer(1, 10))
                story.append(Spacer(1, 15))
                section_num += 1

            # 2.3 Entrevista al Conductor
            if siniestro.relatos_conductor:
                story.append(
                    Paragraph(f"{section_num}. Entrevista al Conductor", section_style)
                )
                for i, relato in enumerate(siniestro.relatos_conductor, 1):
                    story.append(
                        Paragraph(
                            f"Relato {i}:",
                            ParagraphStyle(
                                "Subsection",
                                parent=styles["Heading4"],
                                fontSize=12,
                                fontName="Helvetica-Bold",
                            ),
                        )
                    )
                    story.append(Paragraph(relato.texto, normal_style))
                    # Incluir referencia a imagen si existe
                    if relato.imagen_url and relato.imagen_url.strip():
                        story.append(Paragraph(f"[Imagen adjunta: {i}]", ParagraphStyle(
                            "ImageRef", parent=styles["Normal"], fontSize=8, textColor=colors.blue, fontName="Helvetica-Oblique"
                        )))
                    story.append(Spacer(1, 10))
                story.append(Spacer(1, 15))
                section_num += 1

            # 2.4 Inspección del Lugar
            if siniestro.inspecciones:
                story.append(
                    Paragraph(f"{section_num}. Inspección del Lugar", section_style)
                )
                for i, inspeccion in enumerate(siniestro.inspecciones, 1):
                    story.append(
                        Paragraph(
                            f"Inspección {i}:",
                            ParagraphStyle(
                                "Subsection",
                                parent=styles["Heading4"],
                                fontSize=12,
                                fontName="Helvetica-Bold",
                            ),
                        )
                    )
                    story.append(Paragraph(inspeccion.descripcion, normal_style))
                    # Incluir referencia a imagen si existe
                    if inspeccion.imagen_url and inspeccion.imagen_url.strip():
                        story.append(Paragraph(f"[Imagen adjunta: {i}]", ParagraphStyle(
                            "ImageRef", parent=styles["Normal"], fontSize=8, textColor=colors.blue, fontName="Helvetica-Oblique"
                        )))
                    story.append(Spacer(1, 10))
                story.append(Spacer(1, 15))
                section_num += 1

            # 2.5 Testigos
            if siniestro.testigos:
                story.append(Paragraph(f"{section_num}. Testigos", section_style))
                for i, testigo in enumerate(siniestro.testigos, 1):
                    story.append(
                        Paragraph(
                            f"Testigo {i}:",
                            ParagraphStyle(
                                "Subsection",
                                parent=styles["Heading4"],
                                fontSize=12,
                                fontName="Helvetica-Bold",
                            ),
                        )
                    )
                    story.append(Paragraph(testigo.texto, normal_style))
                    # Incluir referencia a imagen si existe
                    if testigo.imagen_url and testigo.imagen_url.strip():
                        story.append(Paragraph(f"[Imagen adjunta: {i}]", ParagraphStyle(
                            "ImageRef", parent=styles["Normal"], fontSize=8, textColor=colors.blue, fontName="Helvetica-Oblique"
                        )))
                    story.append(Spacer(1, 10))
                story.append(Spacer(1, 15))
                section_num += 1

            # 2.6 Evidencias Complementarias
            if (
                siniestro.evidencias_complementarias
                and siniestro.evidencias_complementarias.strip()
            ):
                story.append(
                    Paragraph(
                        f"{section_num}. Evidencias Complementarias", section_style
                    )
                )
                story.append(
                    Paragraph(siniestro.evidencias_complementarias, normal_style)
                )
                story.append(Spacer(1, 15))
                section_num += 1

            # 2.7 Otras Diligencias
            if siniestro.otras_diligencias and siniestro.otras_diligencias.strip():
                story.append(
                    Paragraph(f"{section_num}. Otras Diligencias", section_style)
                )
                story.append(Paragraph(siniestro.otras_diligencias, normal_style))
                story.append(Spacer(1, 15))
                section_num += 1

            # 2.8 Visita al Taller
            if (
                siniestro.visita_taller
                and siniestro.visita_taller.descripcion
                and siniestro.visita_taller.descripcion.strip()
            ):
                story.append(
                    Paragraph(f"{section_num}. Visita al Taller", section_style)
                )
                story.append(
                    Paragraph(siniestro.visita_taller.descripcion, normal_style)
                )
                story.append(Spacer(1, 15))
                section_num += 1

            # Función auxiliar para verificar si un campo JSON tiene contenido real
            def has_real_content(json_field):
                """Verifica si un campo JSON tiene contenido real (no vacío)"""
                if not json_field:
                    return False
                try:
                    parsed = json.loads(json_field) if isinstance(json_field, str) else json_field
                    if isinstance(parsed, list):
                        # Filtrar elementos que no sean strings vacías
                        return any(item.strip() for item in parsed if isinstance(item, str))
                    return bool(parsed)
                except:
                    return bool(json_field and json_field.strip())

            # 2.9 Observaciones
            if has_real_content(siniestro.observaciones):
                story.append(Paragraph(f"{section_num}. Observaciones", section_style))
                import json

                try:
                    observaciones_list = (
                        json.loads(siniestro.observaciones)
                        if isinstance(siniestro.observaciones, str)
                        else siniestro.observaciones
                    )
                    for i, obs in enumerate(observaciones_list, 1):
                        if isinstance(obs, str) and obs.strip():  # Solo mostrar items no vacíos
                            story.append(Paragraph(f"{i}. {obs}", normal_style))
                            story.append(Spacer(1, 5))
                except:
                    if siniestro.observaciones and siniestro.observaciones.strip():
                        story.append(Paragraph(siniestro.observaciones, normal_style))
                story.append(Spacer(1, 15))
                section_num += 1

            # 2.10 Recomendación sobre el Pago de la Cobertura
            if has_real_content(siniestro.recomendacion_pago_cobertura):
                story.append(
                    Paragraph(
                        f"{section_num}. Recomendación sobre el Pago de la Cobertura",
                        section_style,
                    )
                )
                import json

                try:
                    recomendaciones_list = (
                        json.loads(siniestro.recomendacion_pago_cobertura)
                        if isinstance(siniestro.recomendacion_pago_cobertura, str)
                        else siniestro.recomendacion_pago_cobertura
                    )
                    for i, rec in enumerate(recomendaciones_list, 1):
                        if isinstance(rec, str) and rec.strip():  # Solo mostrar items no vacíos
                            story.append(Paragraph(f"{i}. {rec}", normal_style))
                            story.append(Spacer(1, 5))
                except:
                    if siniestro.recomendacion_pago_cobertura and siniestro.recomendacion_pago_cobertura.strip():
                        story.append(
                            Paragraph(siniestro.recomendacion_pago_cobertura, normal_style)
                        )
                story.append(Spacer(1, 15))
                section_num += 1

            # 2.11 Conclusiones
            if has_real_content(siniestro.conclusiones):
                story.append(Paragraph(f"{section_num}. Conclusiones", section_style))
                import json

                try:
                    conclusiones_list = (
                        json.loads(siniestro.conclusiones)
                        if isinstance(siniestro.conclusiones, str)
                        else siniestro.conclusiones
                    )
                    for i, conc in enumerate(conclusiones_list, 1):
                        if isinstance(conc, str) and conc.strip():  # Solo mostrar items no vacíos
                            story.append(Paragraph(f"{i}. {conc}", normal_style))
                            story.append(Spacer(1, 5))
                except:
                    if siniestro.conclusiones and siniestro.conclusiones.strip():
                        story.append(Paragraph(siniestro.conclusiones, normal_style))
                story.append(Spacer(1, 15))
                section_num += 1

            # 2.12 Anexo (si está en la sección de investigación)
            if has_real_content(siniestro.anexo):
                story.append(Paragraph(f"{section_num}. Anexo", section_style))
                import json

                try:
                    anexo_list = (
                        json.loads(siniestro.anexo)
                        if isinstance(siniestro.anexo, str)
                        else siniestro.anexo
                    )
                    for i, anex in enumerate(anexo_list, 1):
                        if isinstance(anex, str) and anex.strip():  # Solo mostrar items no vacíos
                            story.append(Paragraph(f"{i}. {anex}", normal_style))
                            story.append(Spacer(1, 5))
                except:
                    if siniestro.anexo and siniestro.anexo.strip():
                        story.append(Paragraph(siniestro.anexo, normal_style))
                story.append(Spacer(1, 15))
                section_num += 1

            # Después de TODA la investigación, salto de página
            story.append(Spacer(1, 120))  # Salto de página completo

        # ==================== ANEXOS ====================
        if has_real_content(siniestro.anexo):
            logger.info("📎 Generando sección de anexos...")
            # Salto de página explícito antes de Anexos
            story.append(PageBreak())

            anexos_title = Paragraph("ANEXOS", section_style)
            story.append(anexos_title)
            story.append(Spacer(1, 15))

            import json

            try:
                anexo_list = (
                    json.loads(siniestro.anexo)
                    if isinstance(siniestro.anexo, str)
                    else siniestro.anexo
                )
                for i, anex in enumerate(anexo_list, 1):
                    if isinstance(anex, str) and anex.strip():  # Solo mostrar items no vacíos
                        story.append(
                            Paragraph(
                                f"Anexo {i}:",
                                ParagraphStyle(
                                    "Subsection",
                                    parent=styles["Heading4"],
                                    fontSize=12,
                                    fontName="Helvetica-Bold",
                                ),
                            ),
                        )
                        story.append(Paragraph(anex, normal_style))
                        story.append(Spacer(1, 20))
            except:
                if siniestro.anexo and siniestro.anexo.strip():
                    story.append(Paragraph(siniestro.anexo, normal_style))

            story.append(Spacer(1, 120))  # Salto de página

        # ==================== CIERRE ====================
        logger.info("📝 Generando sección de cierre...")

        # Texto de despedida (sin título "CIERRE")
        despedida = Paragraph(
            "Sin otro particular, me despido atentamente esperando que la presente investigación "
            "haya sido de su completa satisfacción y utilidad. Quedo a sus órdenes para cualquier "
            "consulta adicional que pueda surgir en relación con este caso.",
            normal_style,
        )
        story.append(despedida)
        story.append(Spacer(1, 40))

        # Firma alineada a la izquierda (sin línea de firma)
        firma_style = ParagraphStyle(
            "Firma", parent=styles["Normal"], fontSize=10, alignment=TA_LEFT
        )

        firma_text = Paragraph(
            "Saludos cordiales,<br/><br/>"
            "<b>SUSANA ESPINOSA - INVESTIGADORA DE SINIESTROS</b><br/>"
            "susi.espinosa@hotmail.com   |   PBX: 022.417.481   |   CEL: 099.9846.432",
            firma_style,
        )
        story.append(firma_text)
        story.append(Spacer(1, 30))

        # Fecha del informe (alineada a la izquierda)
        fecha_cierre = Paragraph(
            f"Quito, {datetime.now().strftime('%d de %B de %Y')}",
            ParagraphStyle(
                "FechaCierre", parent=styles["Normal"], fontSize=10, alignment=TA_LEFT
            ),
        )
        story.append(fecha_cierre)

        # Generar PDF
        doc.build(story)

        # Asegurar que el buffer esté completo antes de obtener datos
        buffer.flush()

        # Obtener datos del buffer
        buffer.seek(0)
        pdf_data = buffer.getvalue()

        logger.info(f"✅ PDF generado exitosamente: {len(pdf_data)} bytes")
        logger.info(f"PDF bytes before signing: {len(pdf_data)}")

        # Validar que el PDF sea válido (debe empezar con %PDF-)
        if not pdf_data.startswith(b"%PDF-"):
            logger.error("PDF generado es inválido - no empieza con %PDF-")
            raise Exception("PDF generado es corrupto - no cumple formato PDF estándar")

        # Intentar firmar PDF usando certificado desde S3
        cert_data, password = load_certificate_from_s3()
        if cert_data and password:
            logger.info("🔐 Firmando PDF con certificado digital desde S3...")
            try:
                signed_pdf = sign_pdf(pdf_data, cert_data, password)
                # Validar que el PDF firmado siga siendo válido
                if signed_pdf.startswith(b"%PDF-"):
                    pdf_data = signed_pdf
                    logger.info(f"PDF bytes after signing: {len(pdf_data)}")
                else:
                    logger.warning("PDF firmado es inválido - usando PDF sin firma")
            except Exception as e:
                logger.error(f"Error durante firma digital: {e}")
                logger.warning("Continuando con PDF sin firma digital")
        else:
            logger.warning(
                "Certificado digital no encontrado en S3. "
                "PDF generado sin firma digital."
            )
            logger.info("⚠️  Certificado no encontrado en S3, PDF sin firma")

        return pdf_data

    except Exception as e:
        logger.error(f"❌ Error generando PDF: {e}")
        # PDF de error mínimo
        error_buffer = io.BytesIO()
        try:
            doc = SimpleDocTemplate(error_buffer, pagesize=letter)
            story = [Paragraph("ERROR: No se pudo generar el PDF", styles["Normal"])]
            doc.build(story)
            error_buffer.seek(0)
            return error_buffer.read()
        finally:
            error_buffer.close()
    finally:
        # Cerrar buffer correctamente
        try:
            buffer.close()
        except:
            pass


def generate_unsigned_pdf(siniestro: Siniestro) -> bytes:
    """Generar PDF sin firma digital para pruebas"""
    logger.info(f"🔄 Generando PDF SIN FIRMA para siniestro ID: {siniestro.id}")

    try:
        # Crear buffer para el PDF
        buffer = io.BytesIO()

        # Crear documento
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            topMargin=1 * inch,
            bottomMargin=1 * inch,
            leftMargin=1 * inch,
            rightMargin=1 * inch,
        )
        styles = getSampleStyleSheet()

        # Estilos personalizados
        title_style = ParagraphStyle(
            "Title",
            parent=styles["Heading1"],
            fontSize=18,
            alignment=TA_CENTER,
            spaceAfter=30,
            fontName="Helvetica-Bold",
        )

        normal_style = ParagraphStyle(
            "Normal", parent=styles["Normal"], fontSize=10, fontName="Helvetica"
        )

        story = []

        # Título principal
        title = Paragraph(
            "INFORME DE INVESTIGACIÓN DE SINIESTRO (SIN FIRMA)", title_style
        )
        story.append(title)

        # Tabla con datos básicos
        data = [
            ["Compañía de Seguros:", siniestro.compania_seguros or "No especificada"],
            ["Número de Reclamo:", siniestro.reclamo_num or "No especificado"],
            [
                "Fecha del Siniestro:",
                (
                    siniestro.fecha_siniestro.strftime("%d/%m/%Y")
                    if siniestro.fecha_siniestro
                    else "No especificada"
                ),
            ],
            ["Dirección:", siniestro.direccion_siniestro or "No especificada"],
            ["Tipo de Siniestro:", siniestro.tipo_siniestro or "No especificado"],
        ]

        table = Table(data, colWidths=[2.5 * inch, 4 * inch])
        table.setStyle(
            TableStyle(
                [
                    ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
                    ("FONTSIZE", (0, 0), (-1, -1), 10),
                    ("GRID", (0, 0), (-1, -1), 1, colors.black),
                    ("ALIGN", (0, 0), (0, -1), "LEFT"),
                    ("ALIGN", (1, 0), (1, -1), "LEFT"),
                    ("BACKGROUND", (0, 0), (0, -1), colors.lightgrey),
                ]
            )
        )
        story.append(table)
        story.append(Spacer(1, 20))

        # Nota sobre falta de firma
        nota_style = ParagraphStyle(
            "Nota", parent=styles["Normal"], fontSize=8, textColor=colors.red
        )
        nota = Paragraph(
            "NOTA: Este PDF fue generado sin firma digital para pruebas.", nota_style
        )
        story.append(nota)
        story.append(Spacer(1, 10))

        # Fecha de generación
        fecha_gen = Paragraph(
            f"Fecha de Generación: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}",
            normal_style,
        )
        story.append(fecha_gen)
        story.append(Spacer(1, 10))

        # Generar PDF
        doc.build(story)

        # Asegurar que el buffer esté completo antes de obtener datos
        buffer.flush()

        # Obtener datos del buffer
        buffer.seek(0)
        pdf_data = buffer.getvalue()

        logger.info(f"✅ PDF sin firma generado exitosamente: {len(pdf_data)} bytes")

        # Validar que el PDF sea válido
        if not pdf_data.startswith(b"%PDF-"):
            logger.error("PDF generado es inválido - no empieza con %PDF-")
            raise Exception("PDF generado es corrupto - no cumple formato PDF estándar")

        return pdf_data

    except Exception as e:
        logger.error(f"❌ Error generando PDF sin firma: {e}")
        # PDF de error mínimo
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        story = [
            Paragraph("ERROR: No se pudo generar el PDF sin firma", styles["Normal"])
        ]
        doc.build(story)
        buffer.seek(0)
        return buffer.getvalue()


class SiniestroPDFGenerator:
    """Generador de PDF con firma digital"""

    def generate_pdf(self, siniestro: Siniestro, db: Session) -> bytes:
        """Generar PDF del siniestro con firma digital"""
        return generate_simple_pdf(siniestro)

    def generate_unsigned_pdf(self, siniestro: Siniestro, db: Session) -> bytes:
        """Generar PDF del siniestro sin firma digital (para pruebas)"""
        return generate_unsigned_pdf(siniestro)
