import io
import logging
import os
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from sqlalchemy.orm import Session
from ..models import Siniestro

logger = logging.getLogger(__name__)

try:
    from endesive.pdf import cms
    from cryptography.hazmat.primitives.serialization import pkcs12
    CRYPTO_AVAILABLE = True
    logger.info("✅ Bibliotecas de criptografía disponibles")
except ImportError as e:
    CRYPTO_AVAILABLE = False
    logger.warning(f"⚠️ Bibliotecas de criptografía no disponibles: {e}")


def load_certificate_from_s3(cert_key: str = "certificates/maria_susana_espinosa_lozada.p12") -> tuple[bytes, str]:
    """Cargar certificado desde S3 y retornar datos + contraseña"""
    try:
        # Importar configuración de S3 con ruta relativa correcta
        from ..services.s3_service import get_s3_client, S3_BUCKET_NAME

        s3_client = get_s3_client()
        response = s3_client.get_object(Bucket=S3_BUCKET_NAME, Key=cert_key)
        cert_data = response['Body'].read()

        # Obtener contraseña desde variables de entorno
        password = os.getenv("CERT_PASSWORD", "")

        logger.info(f"✅ Certificado cargado desde S3: {len(cert_data)} bytes")
        return cert_data, password

    except Exception as e:
        logger.warning(f"❌ No se pudo cargar certificado desde S3: {e}")
        return None, None


def sign_pdf(pdf_data: bytes, certificate_data: bytes = None, password: str = None) -> bytes:
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
    """Generar PDF simple y básico del siniestro"""
    logger.info(f"🔄 Generando PDF para siniestro ID: {siniestro.id}")

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
        title = Paragraph("INFORME DE INVESTIGACIÓN DE SINIESTRO", title_style)
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

        logger.info(f"✅ PDF generado exitosamente: {len(pdf_data)} bytes")
        logger.info(f"PDF bytes before signing: {len(pdf_data)}")

        # Validar que el PDF sea válido (debe empezar con %PDF-)
        if not pdf_data.startswith(b'%PDF-'):
            logger.error("PDF generado es inválido - no empieza con %PDF-")
            raise Exception("PDF generado es corrupto - no cumple formato PDF estándar")

        # Intentar firmar PDF usando certificado desde S3
        cert_data, password = load_certificate_from_s3()
        if cert_data and password:
            logger.info("🔐 Firmando PDF con certificado digital desde S3...")
            try:
                signed_pdf = sign_pdf(pdf_data, cert_data, password)
                # Validar que el PDF firmado siga siendo válido
                if signed_pdf.startswith(b'%PDF-'):
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
        title = Paragraph("INFORME DE INVESTIGACIÓN DE SINIESTRO (SIN FIRMA)", title_style)
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
        nota = Paragraph("NOTA: Este PDF fue generado sin firma digital para pruebas.", nota_style)
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
        if not pdf_data.startswith(b'%PDF-'):
            logger.error("PDF generado es inválido - no empieza con %PDF-")
            raise Exception("PDF generado es corrupto - no cumple formato PDF estándar")

        return pdf_data

    except Exception as e:
        logger.error(f"❌ Error generando PDF sin firma: {e}")
        # PDF de error mínimo
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        story = [Paragraph("ERROR: No se pudo generar el PDF sin firma", styles["Normal"])]
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
