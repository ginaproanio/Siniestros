"""
PDF Generation Utilities - Separated Responsibilities Implementation

This module has been refactored to follow Single Responsibility Principle:
- ImageProcessor: Handles image processing and optimization
- PDFSigner: Manages digital signature operations
- PDFContentBuilder: Constructs PDF content sections
- PDFGenerator: Orchestrates the complete PDF generation process
"""

import io
import os
import logging
from datetime import datetime
from typing import List, Optional, Dict, Any
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    Image,
    PageBreak,
)
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from sqlalchemy.orm import Session
from fastapi.responses import Response
from ..models import Siniestro

# Configure minimal logging
logger = logging.getLogger(__name__)

try:
    from PIL import Image as PILImage
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

try:
    from endesive.pdf import cms
    from cryptography.hazmat.primitives.serialization import pkcs12
    CRYPTO_AVAILABLE = True
except ImportError:
    CRYPTO_AVAILABLE = False


class ImageProcessor:
    """Handles image processing and optimization for PDF generation."""

    @staticmethod
    def optimize_image_for_pdf(base64_str: str, max_width: int = 800, max_height: int = 600, quality: int = 85) -> str:
        """Optimize images for PDF inclusion."""
        try:
            import base64
            if "base64," in base64_str:
                base64_str = base64_str.split("base64,")[1]

            image_data = base64.b64decode(base64_str)
            img = PILImage.open(io.BytesIO(image_data))
            img.thumbnail((max_width, max_height), PILImage.Resampling.LANCZOS)

            if img.mode in ('RGBA', 'LA', 'P'):
                background = PILImage.new('RGB', img.size, (255, 255, 255))
                if img.mode == 'P':
                    img = img.convert('RGBA')
                background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                img = background

            output_buffer = io.BytesIO()
            img.save(output_buffer, format='JPEG', quality=quality, optimize=True)
            return base64.b64encode(output_buffer.getvalue()).decode('utf-8')
        except Exception:
            return base64_str

    @staticmethod
    def get_image_from_base64(base64_data: str, content_type: str = None, optimize: bool = True) -> Optional[bytes]:
        """Convert base64 string to image bytes."""
        if not base64_data or not base64_data.strip():
            return None

        try:
            import base64
            if optimize:
                base64_data = ImageProcessor.optimize_image_for_pdf(base64_data)

            image_data = base64.b64decode(base64_data)

            if len(image_data) == 0 or len(image_data) > 10 * 1024 * 1024:
                return None

            if content_type and not content_type.startswith("image/"):
                return None

            return image_data
        except Exception:
            return None

    @staticmethod
    def create_pdf_image(image_data: bytes, max_width: float = 4 * inch, max_height: float = 3 * inch) -> Optional[Image]:
        """Create ReportLab Image object from image bytes."""
        try:
            if not image_data:
                return None

            image_buffer = io.BytesIO(image_data)

            if PIL_AVAILABLE:
                try:
                    pil_image = PILImage.open(image_buffer)
                    if pil_image.mode not in ("RGB", "L"):
                        pil_image = pil_image.convert("RGB")

                    pil_image.thumbnail((max_width * 72, max_height * 72), PILImage.LANCZOS)

                    output_buffer = io.BytesIO()
                    pil_image.save(output_buffer, format="JPEG", quality=85)
                    output_buffer.seek(0)

                    pdf_image = Image(output_buffer)
                    pdf_image.hAlign = "LEFT"
                    return pdf_image
                except Exception:
                    pass

            image_buffer.seek(0)
            pdf_image = Image(image_buffer)
            pdf_image.hAlign = "LEFT"
            return pdf_image
        except Exception:
            return None


class PDFSigner:
    """Handles digital signature operations for PDFs."""

    @staticmethod
    def load_certificate_from_s3(cert_key: str = "certificates/maria_susana_espinosa_lozada.p12") -> tuple:
        """Load certificate and password from S3."""
        try:
            from ..services.s3_service import get_s3_client, S3_BUCKET_NAME
            s3_client = get_s3_client()
            response = s3_client.get_object(Bucket=S3_BUCKET_NAME, Key=cert_key)
            cert_data = response["Body"].read()
            password = os.getenv("CERT_PASSWORD", "")
            return cert_data, password
        except Exception:
            return None, None

    @staticmethod
    def sign_pdf(pdf_data: bytes, certificate_data: bytes = None, password: str = None) -> bytes:
        """Sign PDF digitally using certificate."""
        try:
            p12_data = certificate_data
            private_key, certificate, additional_certificates = pkcs12.load_key_and_certificates(
                p12_data, password.encode() if password else None
            )

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

            signed_pdf = cms.sign(pdf_data, dct, private_key, certificate, additional_certificates or [])
            return signed_pdf
        except Exception:
            return pdf_data


class PDFContentBuilder:
    """Builds PDF content sections from siniestro data."""

    def __init__(self, image_processor: ImageProcessor):
        self.image_processor = image_processor
        self.styles = self._get_styles()

    def _get_styles(self):
        """Get PDF styles configuration."""
        styles = getSampleStyleSheet()
        styles.title_style = ParagraphStyle(
            "Title", parent=styles["Heading1"], fontSize=20, alignment=TA_CENTER,
            spaceAfter=30, fontName="Helvetica-Bold"
        )
        styles.subtitle_style = ParagraphStyle(
            "Subtitle", parent=styles["Heading2"], fontSize=16, alignment=TA_CENTER,
            spaceAfter=20, fontName="Helvetica-Bold"
        )
        styles.section_style = ParagraphStyle(
            "Section", parent=styles["Heading3"], fontSize=14,
            spaceAfter=15, fontName="Helvetica-Bold"
        )
        styles.normal_style = ParagraphStyle(
            "Normal", parent=styles["Normal"], fontSize=10, fontName="Helvetica"
        )
        return styles

    def build_title_section(self, sign_document: bool) -> list:
        """Build the title section of the PDF."""
        title_text = "INFORME DE INVESTIGACIÓN<br/>DE SINIESTRO"
        if not sign_document:
            title_text += " (SIN FIRMA)"

        return [
            Paragraph(title_text, self.styles.title_style),
            Spacer(1, 40)
        ]

    def build_caratula_section(self, siniestro: Siniestro) -> list:
        """Build the caratula (header) section."""
        caratula_data = [
            ["Compañía de Seguros:", siniestro.compania_seguros or ""],
            ["Número de Reclamo:", siniestro.reclamo_num or ""],
            ["Asegurado:", siniestro.asegurado.nombre if siniestro.asegurado and siniestro.asegurado.nombre else ""],
            ["Nombre de Investigador:", "Susana Espinosa"],
        ]

        caratula_data_filtered = [row for row in caratula_data if row[1].strip()]

        if caratula_data_filtered:
            caratula_table = crear_tabla_estandar(
                caratula_data_filtered,
                font_size=12,
                add_grid=False,
                valign="MIDDLE"
            )
            return [caratula_table, Spacer(1, 40)]

        return []

    def build_registration_section(self, siniestro: Siniestro) -> list:
        """Build the registration section."""
        content = []

        # Title
        content.extend([
            Paragraph("REGISTRO DEL SINIESTRO", self.styles.section_style),
            Spacer(1, 15)
        ])

        # Basic registration data
        registro_data_raw = [
            ["Compañía de Seguros:", siniestro.compania_seguros or ""],
            ["RUC Compañía:", siniestro.ruc_compania or ""],
            ["Tipo de Reclamo:", siniestro.tipo_reclamo or ""],
            ["Póliza:", siniestro.poliza or ""],
            ["Número de Reclamo:", siniestro.reclamo_num or ""],
            ["Fecha del Siniestro:", siniestro.fecha_siniestro.strftime("%d/%m/%Y") if siniestro.fecha_siniestro else ""],
            ["Fecha Reportado:", siniestro.fecha_reportado.strftime("%d/%m/%Y") if siniestro.fecha_reportado else ""],
            ["Dirección del Siniestro:", siniestro.direccion_siniestro or ""],
            ["Ubicación Geo Lat:", str(siniestro.ubicacion_geo_lat) if siniestro.ubicacion_geo_lat else ""],
            ["Ubicación Geo Lng:", str(siniestro.ubicacion_geo_lng) if siniestro.ubicacion_geo_lng else ""],
            ["Daños a Terceros:", "Sí" if siniestro.danos_terceros else ""],
            ["Ejecutivo a Cargo:", siniestro.ejecutivo_cargo or ""],
            ["Fecha de Designación:", siniestro.fecha_designacion.strftime("%d/%m/%Y") if siniestro.fecha_designacion else ""],
            ["Tipo de Siniestro:", siniestro.tipo_siniestro or ""],
            ["Cobertura:", siniestro.cobertura or ""],
        ]

        registro_data = [row for row in registro_data_raw if row[1].strip()]

        if registro_data:
            registro_table = crear_tabla_estandar(registro_data)
            content.extend([registro_table, Spacer(1, 20)])

        # Declaration section
        if any([
            siniestro.fecha_declaracion, siniestro.persona_declara_tipo,
            siniestro.persona_declara_cedula, siniestro.persona_declara_nombre,
            siniestro.persona_declara_relacion
        ]):
            content.extend([
                Paragraph("Declaración del Siniestro:", self.styles.section_style),
                Spacer(1, 15)
            ])

            declaracion_data = [
                ["Fecha de Declaración:", siniestro.fecha_declaracion.strftime("%d/%m/%Y") if siniestro.fecha_declaracion else ""],
                ["Persona que Declara (Tipo):", siniestro.persona_declara_tipo or ""],
                ["Cédula/RUC:", siniestro.persona_declara_cedula or ""],
                ["Nombre/Razón Social:", siniestro.persona_declara_nombre or ""],
                ["Relación:", siniestro.persona_declara_relacion or ""],
            ]
            declaracion_data = [row for row in declaracion_data if row[1].strip()]

            if declaracion_data:
                declaracion_table = crear_tabla_estandar(declaracion_data)
                content.extend([declaracion_table, Spacer(1, 15)])

        # Entity sections
        entities = [
            ("asegurado", [
                ["Tipo:", siniestro.asegurado.tipo if siniestro.asegurado else ""],
                ["Cédula/RUC:", siniestro.asegurado.cedula or siniestro.asegurado.ruc if siniestro.asegurado else ""],
                ["Nombre/Empresa:", siniestro.asegurado.nombre or siniestro.asegurado.empresa if siniestro.asegurado else ""],
                ["Representante Legal:", siniestro.asegurado.representante_legal if siniestro.asegurado else ""],
                ["Celular:", siniestro.asegurado.celular or siniestro.asegurado.telefono if siniestro.asegurado else ""],
                ["Correo:", siniestro.asegurado.correo if siniestro.asegurado else ""],
                ["Dirección:", siniestro.asegurado.direccion if siniestro.asegurado else ""],
                ["Parentesco:", siniestro.asegurado.parentesco if siniestro.asegurado else ""],
            ]),
            ("beneficiario", [
                ["Razón Social:", siniestro.beneficiario.razon_social if siniestro.beneficiario else ""],
                ["Cédula/RUC:", siniestro.beneficiario.cedula_ruc if siniestro.beneficiario else ""],
                ["Domicilio:", siniestro.beneficiario.domicilio if siniestro.beneficiario else ""],
            ]),
            ("conductor", [
                ["Nombre:", siniestro.conductor.nombre if siniestro.conductor else ""],
                ["Cédula:", siniestro.conductor.cedula if siniestro.conductor else ""],
                ["Celular:", siniestro.conductor.celular if siniestro.conductor else ""],
                ["Dirección:", siniestro.conductor.direccion if siniestro.conductor else ""],
                ["Parentesco:", siniestro.conductor.parentesco if siniestro.conductor else ""],
            ]),
            ("objeto_asegurado", [
                ["Placa:", siniestro.objeto_asegurado.placa if siniestro.objeto_asegurado else ""],
                ["Marca:", siniestro.objeto_asegurado.marca if siniestro.objeto_asegurado else ""],
                ["Modelo:", siniestro.objeto_asegurado.modelo if siniestro.objeto_asegurado else ""],
                ["Tipo:", siniestro.objeto_asegurado.tipo if siniestro.objeto_asegurado else ""],
                ["Color:", siniestro.objeto_asegurado.color if siniestro.objeto_asegurado else ""],
                ["Año:", str(siniestro.objeto_asegurado.ano) if siniestro.objeto_asegurado and siniestro.objeto_asegurado.ano else ""],
                ["Serie Motor:", siniestro.objeto_asegurado.serie_motor if siniestro.objeto_asegurado else ""],
                ["Chasis:", siniestro.objeto_asegurado.chasis if siniestro.objeto_asegurado else ""],
            ]),
        ]

        for entity_name, entity_data in entities:
            entity_data_filtered = [row for row in entity_data if row[1].strip()]
            if entity_data_filtered:
                title_map = {
                    "asegurado": "Información del Asegurado:",
                    "beneficiario": "Información del Beneficiario:",
                    "conductor": "Información del Conductor:",
                    "objeto_asegurado": "Información del Objeto Asegurado:",
                }
                content.extend([
                    Paragraph(title_map[entity_name], self.styles.section_style),
                    crear_tabla_estandar(entity_data_filtered),
                    Spacer(1, 15)
                ])

        return content


class PDFGenerator:
    """Orchestrates the complete PDF generation process using separated responsibilities."""

    def __init__(self):
        self.image_processor = ImageProcessor()
        self.pdf_signer = PDFSigner()
        self.content_builder = PDFContentBuilder(self.image_processor)

    def generate_pdf(self, siniestro: Siniestro, sign_document: bool = True) -> bytes:
        """
        Generate complete PDF using separated responsibility classes.

        Args:
            siniestro: Siniestro model instance with all related data
            sign_document: Whether to sign the PDF digitally

        Returns:
            PDF data as bytes
        """
        try:
            # Build PDF content structure
            story = []

            # Add title section
            story.extend(self.content_builder.build_title_section(sign_document))

            # Add caratula section
            story.extend(self.content_builder.build_caratula_section(siniestro))

            # Add generation date
            from reportlab.platypus import Paragraph, Spacer
            fecha_gen = Paragraph(
                f"Fecha de Generación: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}",
                self.content_builder.styles.normal_style
            )
            story.extend([Spacer(1, 20), fecha_gen])

            # Add unsigned note if needed
            if not sign_document:
                nota_style = ParagraphStyle(
                    "Nota", parent=getSampleStyleSheet()["Normal"],
                    fontSize=8, textColor=colors.red, alignment=TA_CENTER
                )
                nota = Paragraph("NOTA: Este PDF fue generado sin firma digital para pruebas.", nota_style)
                story.extend([Spacer(1, 10), nota])

            # Build and add registration section
            story.extend(self.content_builder.build_registration_section(siniestro))

            # Create PDF document
            buffer = io.BytesIO()
            doc = SimpleDocTemplate(
                buffer,
                pagesize=letter,
                topMargin=1.2 * inch,
                bottomMargin=1.2 * inch,
                leftMargin=1 * inch,
                rightMargin=1 * inch,
            )

            doc.onFirstPage = header_footer
            doc.onLaterPages = header_footer

            # Build PDF
            doc.build(story)
            buffer.flush()
            buffer.seek(0)
            pdf_data = buffer.getvalue()

            # Validate PDF
            if not pdf_data.startswith(b"%PDF-"):
                raise Exception("PDF generado es corrupto")

            # Sign PDF if requested and certificates available
            if sign_document and CRYPTO_AVAILABLE:
                cert_data, password = self.pdf_signer.load_certificate_from_s3()
                if cert_data and password:
                    try:
                        signed_pdf = self.pdf_signer.sign_pdf(pdf_data, cert_data, password)
                        if signed_pdf.startswith(b"%PDF-"):
                            pdf_data = signed_pdf
                    except Exception:
                        pass  # Continue with unsigned PDF

            return pdf_data

        except Exception as e:
            # Minimal error PDF
            error_buffer = io.BytesIO()
            doc = SimpleDocTemplate(error_buffer, pagesize=letter)
            styles = getSampleStyleSheet()
            story = [Paragraph("ERROR: No se pudo generar el PDF", styles["Normal"])]
            doc.build(story)
            error_buffer.seek(0)
            return error_buffer.getvalue()


def optimize_image_for_pdf(base64_str: str, max_width: int = 800, max_height: int = 600, quality: int = 85) -> str:
    """Optimize images for PDF"""
    try:
        import base64
        if "base64," in base64_str:
            base64_str = base64_str.split("base64,")[1]

        image_data = base64.b64decode(base64_str)
        img = PILImage.open(io.BytesIO(image_data))
        img.thumbnail((max_width, max_height), PILImage.Resampling.LANCZOS)

        if img.mode in ('RGBA', 'LA', 'P'):
            background = PILImage.new('RGB', img.size, (255, 255, 255))
            if img.mode == 'P':
                img = img.convert('RGBA')
            background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
            img = background

        output_buffer = io.BytesIO()
        img.save(output_buffer, format='JPEG', quality=quality, optimize=True)
        return base64.b64encode(output_buffer.getvalue()).decode('utf-8')
    except Exception:
        return base64_str


def get_image_from_base64(base64_data: str, content_type: str = None, optimize: bool = True) -> bytes:
    """Convert base64 to image bytes"""
    if not base64_data or not base64_data.strip():
        return None

    try:
        import base64
        if optimize:
            base64_data = optimize_image_for_pdf(base64_data)

        image_data = base64.b64decode(base64_data)

        if len(image_data) == 0 or len(image_data) > 10 * 1024 * 1024:
            return None

        if content_type and not content_type.startswith("image/"):
            return None

        return image_data
    except Exception:
        return None


def create_pdf_image(image_data: bytes, max_width: float = 4 * inch, max_height: float = 3 * inch) -> Image:
    """Create ReportLab Image object"""
    try:
        if not image_data:
            return None

        image_buffer = io.BytesIO(image_data)

        if PIL_AVAILABLE:
            try:
                pil_image = PILImage.open(image_buffer)
                if pil_image.mode not in ("RGB", "L"):
                    pil_image = pil_image.convert("RGB")

                pil_image.thumbnail((max_width * 72, max_height * 72), PILImage.LANCZOS)

                output_buffer = io.BytesIO()
                pil_image.save(output_buffer, format="JPEG", quality=85)
                output_buffer.seek(0)

                pdf_image = Image(output_buffer)
                pdf_image.hAlign = "LEFT"
                return pdf_image
            except Exception:
                pass

        image_buffer.seek(0)
        pdf_image = Image(image_buffer)
        pdf_image.hAlign = "LEFT"
        return pdf_image
    except Exception:
        return None


def crear_tabla_estandar(datos, titulo=None, font_size=10, add_grid=True, background_color=colors.lightgrey, valign="MIDDLE"):
    """Crear tabla PDF con estilo estándar customizable"""
    from reportlab.platypus import Table, TableStyle

    table = Table(datos, colWidths=[2.5 * inch, 4 * inch])

    styles = [
        ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
        ("FONTSIZE", (0, 0), (-1, -1), font_size),
        ("ALIGN", (0, 0), (-1, -1), "LEFT"),
        ("ALIGN", (1, 0), (1, -1), "LEFT"),
        ("VALIGN", (0, 0), (-1, -1), valign),
        ("BACKGROUND", (0, 0), (0, -1), background_color),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]

    if add_grid:
        styles.insert(2, ("GRID", (0, 0), (-1, -1), 1, colors.black))

    table.setStyle(TableStyle(styles))
    return table


def header_footer(canvas, doc):
    """Draw header and footer"""
    canvas.saveState()
    width, height = letter

    canvas.setStrokeColor(colors.black)
    canvas.setLineWidth(1)
    canvas.line(0.5 * inch, height - 0.5 * inch, width - 0.5 * inch, height - 0.5 * inch)

    canvas.setFont("Helvetica-Bold", 10)
    canvas.drawString(0.75 * inch, height - 0.75 * inch, "INFORME DE INVESTIGACIÓN DE SINIESTRO")

    page_num = canvas.getPageNumber()
    canvas.setFont("Helvetica", 8)
    canvas.drawRightString(width - 0.75 * inch, height - 0.75 * inch, f"Página {page_num}")

    canvas.line(0.5 * inch, 0.5 * inch, width - 0.5 * inch, 0.5 * inch)

    canvas.setFont("Helvetica", 8)
    footer_text = "Sistema de Gestión de Siniestros - Susana Espinosa"
    canvas.drawString(0.75 * inch, 0.25 * inch, footer_text)

    fecha_actual = datetime.now().strftime("%d/%m/%Y")
    canvas.drawRightString(width - 0.75 * inch, 0.25 * inch, f"Fecha: {fecha_actual}")

    canvas.restoreState()


def load_certificate_from_s3(cert_key: str = "certificates/maria_susana_espinosa_lozada.p12"):
    """Load certificate from S3"""
    try:
        from ..services.s3_service import get_s3_client, S3_BUCKET_NAME
        s3_client = get_s3_client()
        response = s3_client.get_object(Bucket=S3_BUCKET_NAME, Key=cert_key)
        cert_data = response["Body"].read()
        password = os.getenv("CERT_PASSWORD", "")
        return cert_data, password
    except Exception:
        return None, None


def sign_pdf(pdf_data: bytes, certificate_data: bytes = None, password: str = None) -> bytes:
    """Sign PDF digitally"""
    try:
        p12_data = certificate_data
        private_key, certificate, additional_certificates = pkcs12.load_key_and_certificates(
            p12_data, password.encode() if password else None
        )

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

        signed_pdf = cms.sign(pdf_data, dct, private_key, certificate, additional_certificates or [])
        return signed_pdf
    except Exception:
        return pdf_data


def generate_pdf(siniestro: Siniestro, sign_document: bool = True) -> bytes:
    """
    Unified PDF generation function

    Args:
        siniestro: Siniestro model instance
        sign_document: Whether to sign the PDF digitally

    Returns:
        PDF data as bytes
    """
    try:
        logger.info(f"🔄 Iniciando generación PDF para siniestro {siniestro.id}")

        # DIAGNÓSTICO DE DATOS QUE LLEGAN
        logger.info("=== DIAGNÓSTICO PDF - INICIO ===")
        logger.info(f"Siniestro ID: {siniestro.id}")
        logger.info(f"Asegurado: {siniestro.asegurado}")
        logger.info(f"Nombre asegurado: {getattr(siniestro.asegurado, 'nombre', 'NO EXISTE')}")
        logger.info(f"Empresa: {getattr(siniestro.asegurado, 'empresa', 'NO EXISTE')}")
        logger.info(f"Objeto asegurado: {siniestro.objeto_asegurado}")
        logger.info(f"Descripción objeto: {getattr(siniestro.objeto_asegurado, 'descripcion', 'NO EXISTE')}")
        logger.info(f"Antecedentes count: {len(siniestro.antecedentes) if siniestro.antecedentes else 0}")
        logger.info("=== DIAGNÓSTICO PDF - FIN ===")
        buffer = io.BytesIO()

        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            topMargin=1.2 * inch,
            bottomMargin=1.2 * inch,
            leftMargin=1 * inch,
            rightMargin=1 * inch,
        )

        doc.onFirstPage = header_footer
        doc.onLaterPages = header_footer
        styles = getSampleStyleSheet()

        title_style = ParagraphStyle(
            "Title", parent=styles["Heading1"], fontSize=20, alignment=TA_CENTER,
            spaceAfter=30, fontName="Helvetica-Bold"
        )

        subtitle_style = ParagraphStyle(
            "Subtitle", parent=styles["Heading2"], fontSize=16, alignment=TA_CENTER,
            spaceAfter=20, fontName="Helvetica-Bold"
        )

        section_style = ParagraphStyle(
            "Section", parent=styles["Heading3"], fontSize=14,
            spaceAfter=15, fontName="Helvetica-Bold"
        )

        normal_style = ParagraphStyle(
            "Normal", parent=styles["Normal"], fontSize=10, fontName="Helvetica"
        )

        story = []

        # Title with optional signature note
        title_text = "INFORME DE INVESTIGACIÓN<br/>DE SINIESTRO"
        if not sign_document:
            title_text += " (SIN FIRMA)"

        title = Paragraph(title_text, title_style)
        story.append(title)

        # Basic data table
        caratula_data = [
            ["Compañía de Seguros:", siniestro.compania_seguros or ""],
            ["Número de Reclamo:", siniestro.reclamo_num or ""],
            ["Asegurado:", siniestro.asegurado.nombre if siniestro.asegurado and siniestro.asegurado.nombre else ""],
            ["Nombre de Investigador:", "Susana Espinosa"],
        ]

        caratula_data_filtered = [row for row in caratula_data if row[1].strip()]

        if caratula_data_filtered:
            # Use the unified table function with caratula-specific styling
            caratula_table = crear_tabla_estandar(
                caratula_data_filtered,
                font_size=12,
                add_grid=False,
                valign="MIDDLE"
            )
            story.append(caratula_table)
            story.append(Spacer(1, 40))

        # Generation date
        fecha_gen = Paragraph(
            f"Fecha de Generación: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}",
            ParagraphStyle("Fecha", parent=styles["Normal"], fontSize=10, alignment=TA_CENTER)
        )
        story.append(fecha_gen)

        # Note for unsigned documents
        if not sign_document:
            nota_style = ParagraphStyle(
                "Nota", parent=styles["Normal"], fontSize=8, textColor=colors.red, alignment=TA_CENTER
            )
            nota = Paragraph("NOTA: Este PDF fue generado sin firma digital para pruebas.", nota_style)
            story.append(Spacer(1, 10))
            story.append(nota)

        # Index page
        from reportlab.platypus import PageBreak
        story.append(PageBreak())

        indice_title = Paragraph("ÍNDICE", subtitle_style)
        story.append(indice_title)
        story.append(Spacer(1, 20))

        indice_items = ["3. REGISTRO DEL SINIESTRO"]

        has_investigacion = (
            siniestro.antecedentes or siniestro.relatos_asegurado or siniestro.relatos_conductor or
            siniestro.inspecciones or siniestro.testigos or
            (siniestro.evidencias_complementarias and siniestro.evidencias_complementarias.strip()) or
            (siniestro.otras_diligencias and siniestro.otras_diligencias.strip()) or
            (siniestro.visita_taller and siniestro.visita_taller.descripcion and siniestro.visita_taller.descripcion.strip()) or
            (siniestro.observaciones and siniestro.observaciones.strip()) or
            (siniestro.recomendacion_pago_cobertura and siniestro.recomendacion_pago_cobertura.strip()) or
            (siniestro.conclusiones and siniestro.conclusiones.strip()) or
            (siniestro.anexo and siniestro.anexo.strip())
        )

        if has_investigacion:
            indice_items.append("4. INVESTIGACIÓN")
        if siniestro.anexo and siniestro.anexo.strip():
            indice_items.append("5. ANEXOS")
        indice_items.append("6. CIERRE")

        for item in indice_items:
            story.append(Paragraph(item, normal_style))
            story.append(Spacer(1, 5))

        story.append(PageBreak())

        # Registration section
        registro_title = Paragraph("REGISTRO DEL SINIESTRO", section_style)
        story.append(registro_title)
        story.append(Spacer(1, 15))

        registro_data_raw = [
            ["Compañía de Seguros:", siniestro.compania_seguros or ""],
            ["RUC Compañía:", siniestro.ruc_compania or ""],
            ["Tipo de Reclamo:", siniestro.tipo_reclamo or ""],
            ["Póliza:", siniestro.poliza or ""],
            ["Número de Reclamo:", siniestro.reclamo_num or ""],
            ["Fecha del Siniestro:", siniestro.fecha_siniestro.strftime("%d/%m/%Y") if siniestro.fecha_siniestro else ""],
            ["Fecha Reportado:", siniestro.fecha_reportado.strftime("%d/%m/%Y") if siniestro.fecha_reportado else ""],
            ["Dirección del Siniestro:", siniestro.direccion_siniestro or ""],
            ["Ubicación Geo Lat:", str(siniestro.ubicacion_geo_lat) if siniestro.ubicacion_geo_lat else ""],
            ["Ubicación Geo Lng:", str(siniestro.ubicacion_geo_lng) if siniestro.ubicacion_geo_lng else ""],
            ["Daños a Terceros:", "Sí" if siniestro.danos_terceros else ""],
            ["Ejecutivo a Cargo:", siniestro.ejecutivo_cargo or ""],
            ["Fecha de Designación:", siniestro.fecha_designacion.strftime("%d/%m/%Y") if siniestro.fecha_designacion else ""],
            ["Tipo de Siniestro:", siniestro.tipo_siniestro or ""],
            ["Cobertura:", siniestro.cobertura or ""],
        ]

        registro_data = [row for row in registro_data_raw if row[1].strip()]

        if registro_data:
            registro_table = crear_tabla_estandar(registro_data)
            story.append(registro_table)
            story.append(Spacer(1, 20))

        # Declaration section
        if any([
            siniestro.fecha_declaracion, siniestro.persona_declara_tipo,
            siniestro.persona_declara_cedula, siniestro.persona_declara_nombre,
            siniestro.persona_declara_relacion
        ]):
            story.append(Paragraph("Declaración del Siniestro:", section_style))
            declaracion_data = [
                ["Fecha de Declaración:", siniestro.fecha_declaracion.strftime("%d/%m/%Y") if siniestro.fecha_declaracion else ""],
                ["Persona que Declara (Tipo):", siniestro.persona_declara_tipo or ""],
                ["Cédula/RUC:", siniestro.persona_declara_cedula or ""],
                ["Nombre/Razón Social:", siniestro.persona_declara_nombre or ""],
                ["Relación:", siniestro.persona_declara_relacion or ""],
            ]
            declaracion_data = [row for row in declaracion_data if row[1].strip()]

            if declaracion_data:
                declaracion_table = crear_tabla_estandar(declaracion_data)
                story.append(declaracion_table)
                story.append(Spacer(1, 15))

        # Entity sections (Asegurado, Beneficiario, Conductor, Objeto)
        entities = [
            ("asegurado", [
                ["Tipo:", siniestro.asegurado.tipo if siniestro.asegurado else ""],
                ["Cédula/RUC:", siniestro.asegurado.cedula or siniestro.asegurado.ruc if siniestro.asegurado else ""],
                ["Nombre/Empresa:", siniestro.asegurado.nombre or siniestro.asegurado.empresa if siniestro.asegurado else ""],
                ["Representante Legal:", siniestro.asegurado.representante_legal if siniestro.asegurado else ""],
                ["Celular:", siniestro.asegurado.celular or siniestro.asegurado.telefono if siniestro.asegurado else ""],
                ["Correo:", siniestro.asegurado.correo if siniestro.asegurado else ""],
                ["Dirección:", siniestro.asegurado.direccion if siniestro.asegurado else ""],
                ["Parentesco:", siniestro.asegurado.parentesco if siniestro.asegurado else ""],
            ]),
            ("beneficiario", [
                ["Razón Social:", siniestro.beneficiario.razon_social if siniestro.beneficiario else ""],
                ["Cédula/RUC:", siniestro.beneficiario.cedula_ruc if siniestro.beneficiario else ""],
                ["Domicilio:", siniestro.beneficiario.domicilio if siniestro.beneficiario else ""],
            ]),
            ("conductor", [
                ["Nombre:", siniestro.conductor.nombre if siniestro.conductor else ""],
                ["Cédula:", siniestro.conductor.cedula if siniestro.conductor else ""],
                ["Celular:", siniestro.conductor.celular if siniestro.conductor else ""],
                ["Dirección:", siniestro.conductor.direccion if siniestro.conductor else ""],
                ["Parentesco:", siniestro.conductor.parentesco if siniestro.conductor else ""],
            ]),
            ("objeto_asegurado", [
                ["Placa:", siniestro.objeto_asegurado.placa if siniestro.objeto_asegurado else ""],
                ["Marca:", siniestro.objeto_asegurado.marca if siniestro.objeto_asegurado else ""],
                ["Modelo:", siniestro.objeto_asegurado.modelo if siniestro.objeto_asegurado else ""],
                ["Tipo:", siniestro.objeto_asegurado.tipo if siniestro.objeto_asegurado else ""],
                ["Color:", siniestro.objeto_asegurado.color if siniestro.objeto_asegurado else ""],
                ["Año:", str(siniestro.objeto_asegurado.ano) if siniestro.objeto_asegurado and siniestro.objeto_asegurado.ano else ""],
                ["Serie Motor:", siniestro.objeto_asegurado.serie_motor if siniestro.objeto_asegurado else ""],
                ["Chasis:", siniestro.objeto_asegurado.chasis if siniestro.objeto_asegurado else ""],
            ]),
        ]

        for entity_name, entity_data in entities:
            entity_data_filtered = [row for row in entity_data if row[1].strip()]
            if entity_data_filtered:
                title_map = {
                    "asegurado": "Información del Asegurado:",
                    "beneficiario": "Información del Beneficiario:",
                    "conductor": "Información del Conductor:",
                    "objeto_asegurado": "Información del Objeto Asegurado:",
                }
                story.append(Paragraph(title_map[entity_name], section_style))
                entity_table = crear_tabla_estandar(entity_data_filtered)
                story.append(entity_table)
                story.append(Spacer(1, 15))

        # Investigation section
        if has_investigacion:
            story.append(PageBreak())
            investigacion_title = Paragraph("INVESTIGACIÓN", section_style)
            story.append(investigacion_title)
            story.append(Spacer(1, 15))

            section_num = 1

            # Antecedentes
            if siniestro.antecedentes:
                story.append(Paragraph(f"{section_num}. Antecedentes", section_style))
                for antecedente in siniestro.antecedentes:
                    story.append(Paragraph(antecedente.descripcion, normal_style))
                    story.append(Spacer(1, 10))
                story.append(Spacer(1, 15))
                section_num += 1

            # Relatos del asegurado
            if siniestro.relatos_asegurado:
                story.append(Paragraph(f"{section_num}. Entrevista al Asegurado", section_style))
                for i, relato in enumerate(siniestro.relatos_asegurado, 1):
                    story.append(Paragraph(f"Relato {i}:", ParagraphStyle("Subsection", parent=styles["Heading4"], fontSize=12, fontName="Helvetica-Bold")))
                    story.append(Paragraph(relato.texto, normal_style))
                    # Try to include image
                    try:
                        if relato.imagen_base64 and relato.imagen_base64.strip():
                            image_data = get_image_from_base64(relato.imagen_base64, relato.imagen_content_type)
                            if image_data:
                                pdf_image = create_pdf_image(image_data)
                                if pdf_image:
                                    story.append(Spacer(1, 5))
                                    story.append(pdf_image)
                                    story.append(Spacer(1, 5))
                    except Exception:
                        pass  # Silently skip image errors
                    story.append(Spacer(1, 10))
                story.append(Spacer(1, 15))
                section_num += 1

            # Relatos del conductor
            if siniestro.relatos_conductor:
                story.append(Paragraph(f"{section_num}. Entrevista al Conductor", section_style))
                for i, relato in enumerate(siniestro.relatos_conductor, 1):
                    story.append(Paragraph(f"Relato {i}:", ParagraphStyle("Subsection", parent=styles["Heading4"], fontSize=12, fontName="Helvetica-Bold")))
                    story.append(Paragraph(relato.texto, normal_style))
                    # Try to include image
                    try:
                        if relato.imagen_base64 and relato.imagen_base64.strip():
                            image_data = get_image_from_base64(relato.imagen_base64, relato.imagen_content_type)
                            if image_data:
                                pdf_image = create_pdf_image(image_data)
                                if pdf_image:
                                    story.append(Spacer(1, 5))
                                    story.append(pdf_image)
                                    story.append(Spacer(1, 5))
                    except Exception:
                        pass  # Silently skip image errors
                    story.append(Spacer(1, 10))
                story.append(Spacer(1, 15))
                section_num += 1

            # Inspecciones
            if siniestro.inspecciones:
                story.append(Paragraph(f"{section_num}. Inspección del Lugar", section_style))
                for i, inspeccion in enumerate(siniestro.inspecciones, 1):
                    story.append(Paragraph(f"Inspección {i}:", ParagraphStyle("Subsection", parent=styles["Heading4"], fontSize=12, fontName="Helvetica-Bold")))
                    story.append(Paragraph(inspeccion.descripcion, normal_style))
                    # Try to include image
                    try:
                        if inspeccion.imagen_base64 and inspeccion.imagen_base64.strip():
                            image_data = get_image_from_base64(inspeccion.imagen_base64, inspeccion.imagen_content_type)
                            if image_data:
                                pdf_image = create_pdf_image(image_data)
                                if pdf_image:
                                    story.append(Spacer(1, 5))
                                    story.append(pdf_image)
                                    story.append(Spacer(1, 5))
                    except Exception:
                        pass  # Silently skip image errors
                    story.append(Spacer(1, 10))
                story.append(Spacer(1, 15))
                section_num += 1

            # Testigos
            if siniestro.testigos:
                story.append(Paragraph(f"{section_num}. Testigos", section_style))
                for i, testigo in enumerate(siniestro.testigos, 1):
                    story.append(Paragraph(f"Testigo {i}:", ParagraphStyle("Subsection", parent=styles["Heading4"], fontSize=12, fontName="Helvetica-Bold")))
                    story.append(Paragraph(testigo.texto, normal_style))
                    # Try to include image
                    try:
                        if testigo.imagen_base64 and testigo.imagen_base64.strip():
                            image_data = get_image_from_base64(testigo.imagen_base64, testigo.imagen_content_type)
                            if image_data:
                                pdf_image = create_pdf_image(image_data)
                                if pdf_image:
                                    story.append(Spacer(1, 5))
                                    story.append(pdf_image)
                                    story.append(Spacer(1, 5))
                    except Exception:
                        pass  # Silently skip image errors
                    story.append(Spacer(1, 10))
                story.append(Spacer(1, 15))
                section_num += 1

            # Helper function for JSON content checking
            def has_json_content(json_field):
                if not json_field:
                    return False
                try:
                    import json
                    parsed = json.loads(json_field) if isinstance(json_field, str) else json_field
                    if isinstance(parsed, list):
                        return any(item.strip() for item in parsed if isinstance(item, str))
                    return bool(parsed)
                except:
                    return bool(json_field and json_field.strip())

            # Other investigation fields
            investigation_fields = [
                ("evidencias_complementarias", "Evidencias Complementarias"),
                ("otras_diligencias", "Otras Diligencias"),
                ("visita_taller", lambda: siniestro.visita_taller.descripcion if siniestro.visita_taller else "", "Visita al Taller"),
                ("observaciones", "Observaciones"),
                ("recomendacion_pago_cobertura", "Recomendación sobre el Pago de la Cobertura"),
                ("conclusiones", "Conclusiones"),
                ("anexo", "Anexo"),
            ]

            for field_name, display_name in investigation_fields:
                if field_name == "visita_taller":
                    content = display_name[0]() if callable(display_name[0]) else getattr(siniestro, field_name, "")
                    display_name = display_name[1]
                else:
                    content = getattr(siniestro, field_name, "")

                if content and content.strip():
                    story.append(Paragraph(f"{section_num}. {display_name}", section_style))

                    # Handle JSON arrays for some fields
                    if field_name in ["observaciones", "recomendacion_pago_cobertura", "conclusiones", "anexo"]:
                        try:
                            import json
                            items = json.loads(content) if isinstance(content, str) else content
                            if isinstance(items, list):
                                for i, item in enumerate(items, 1):
                                    if isinstance(item, str) and item.strip():
                                        story.append(Paragraph(f"{i}. {item}", normal_style))
                                        story.append(Spacer(1, 5))
                            else:
                                story.append(Paragraph(content, normal_style))
                        except:
                            story.append(Paragraph(content, normal_style))
                    else:
                        story.append(Paragraph(content, normal_style))

                    story.append(Spacer(1, 15))
                    section_num += 1

            story.append(PageBreak())

        # Annexes section
        if siniestro.anexo and siniestro.anexo.strip():
            story.append(PageBreak())
            anexos_title = Paragraph("ANEXOS", section_style)
            story.append(anexos_title)
            story.append(Spacer(1, 15))

            try:
                import json
                anexo_list = json.loads(siniestro.anexo) if isinstance(siniestro.anexo, str) else siniestro.anexo
                if isinstance(anexo_list, list):
                    for i, anex in enumerate(anexo_list, 1):
                        if isinstance(anex, str) and anex.strip():
                            story.append(Paragraph(f"Anexo {i}:", ParagraphStyle("Subsection", parent=styles["Heading4"], fontSize=12, fontName="Helvetica-Bold")))
                            story.append(Paragraph(anex, normal_style))
                            story.append(Spacer(1, 20))
                else:
                    story.append(Paragraph(siniestro.anexo, normal_style))
            except:
                story.append(Paragraph(siniestro.anexo, normal_style))

            story.append(PageBreak())

        # Closing section
        despedida = Paragraph(
            "Sin otro particular, me despido atentamente esperando que la presente investigación "
            "haya sido de su completa satisfacción y utilidad. Quedo a sus órdenes para cualquier "
            "consulta adicional que pueda surgir en relación con este caso.",
            normal_style,
        )
        story.append(despedida)
        story.append(Spacer(1, 40))

        firma_style = ParagraphStyle("Firma", parent=styles["Normal"], fontSize=10, alignment=TA_LEFT)
        firma_text = Paragraph(
            "<b>SUSANA ESPINOSA - INVESTIGADORA DE SINIESTROS</b><br/>"
            "susi.espinosa@hotmail.com   |   PBX: 022.417.481   |   CEL: 099.9846.432",
            firma_style,
        )
        story.append(firma_text)
        story.append(Spacer(1, 30))

        fecha_cierre = Paragraph(
            f"Quito, {datetime.now().strftime('%d de %B de %Y')}",
            ParagraphStyle("FechaCierre", parent=styles["Normal"], fontSize=10, alignment=TA_LEFT),
        )
        story.append(fecha_cierre)

        # Generate PDF
        doc.build(story)

        buffer.flush()
        buffer.seek(0)
        pdf_data = buffer.getvalue()

        # Validate PDF
        if not pdf_data.startswith(b"%PDF-"):
            raise Exception("PDF generado es corrupto")

        # Sign PDF if requested and certificates available
        if sign_document and CRYPTO_AVAILABLE:
            cert_data, password = load_certificate_from_s3()
            if cert_data and password:
                try:
                    signed_pdf = sign_pdf(pdf_data, cert_data, password)
                    if signed_pdf.startswith(b"%PDF-"):
                        pdf_data = signed_pdf
                except Exception:
                    pass  # Continue with unsigned PDF

        return pdf_data

    except Exception as e:
        # Log detailed error information
        logger.error(f"❌ ERROR generando PDF para siniestro {siniestro.id}: {str(e)}")
        import traceback
        error_details = traceback.format_exc()
        logger.error(f"🔍 Traceback completo:\n{error_details}")

        # Minimal error PDF
        error_buffer = io.BytesIO()
        doc = SimpleDocTemplate(error_buffer, pagesize=letter)
        story = [Paragraph("ERROR: No se pudo generar el PDF", styles["Normal"])]
        doc.build(story)
        error_buffer.seek(0)
        return error_buffer.getvalue()


def generate_diagnostic_pdf(db: Session) -> bytes:
    """Generate diagnostic PDF for system testing"""
    try:
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)

        styles = getSampleStyleSheet()
        story = []

        # Diagnostic content
        story.append(Paragraph("REPORTE DE DIAGNÓSTICO - SISTEMA PDF", styles["Heading1"]))
        story.append(Spacer(1, 20))

        # System checks
        checks = [
            ["ReportLab", "✅ Instalado" if True else "❌ Faltante"],
            ["PIL/Pillow", "✅ Instalado" if PIL_AVAILABLE else "❌ Faltante"],
            ["Cryptography", "✅ Instalado" if CRYPTO_AVAILABLE else "❌ Faltante"],
            ["Fecha de Prueba", datetime.now().strftime("%d/%m/%Y %H:%M:%S")],
        ]

        # Add siniestro count if DB is available
        if db:
            try:
                from ..models import Siniestro
                siniestro_count = db.query(Siniestro).count()
                checks.append([f"Siniestros en BD", str(siniestro_count)])
            except:
                checks.append(["Base de Datos", "❌ Error de conexión"])

        # Create table
        table = crear_tabla_estandar(checks)
        story.append(table)

        doc.build(story)
        buffer.seek(0)
        pdf_data = buffer.getvalue()

        # Validate PDF
        if not pdf_data.startswith(b"%PDF-"):
            raise Exception("PDF generado es corrupto")

        return pdf_data

    except Exception as e:
        # Fallback minimal PDF
        error_buffer = io.BytesIO()
        doc = SimpleDocTemplate(error_buffer, pagesize=letter)
        story = [Paragraph("ERROR: No se pudo generar PDF de diagnóstico", styles["Normal"])]
        doc.build(story)
        error_buffer.seek(0)
        return error_buffer.getvalue()


def generate_test_pdf() -> bytes:
    """Generate minimal test PDF"""
    try:
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)

        styles = getSampleStyleSheet()
        story = [
            Paragraph("PDF DE PRUEBA - SISTEMA FUNCIONANDO", styles["Heading1"]),
            Paragraph("Si puedes leer esto, el generador de PDF está funcionando correctamente.", styles["Normal"]),
            Paragraph(f"Fecha de generación: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}", styles["Normal"]),
        ]

        doc.build(story)
        buffer.seek(0)
        pdf_data = buffer.getvalue()

        # Validate PDF
        if not pdf_data.startswith(b"%PDF-"):
            raise Exception("PDF generado es corrupto")

        return pdf_data

    except Exception as e:
        # Fallback minimal PDF
        error_buffer = io.BytesIO()
        doc = SimpleDocTemplate(error_buffer, pagesize=letter)
        story = [Paragraph("ERROR: No se pudo generar PDF de prueba", styles["Normal"])]
        doc.build(story)
        error_buffer.seek(0)
        return error_buffer.getvalue()


# Legacy compatibility functions
def generate_simple_pdf(siniestro: Siniestro) -> bytes:
    """Legacy function - use generate_pdf(siniestro, sign_document=True)"""
    return generate_pdf(siniestro, sign_document=True)


def generate_unsigned_pdf(siniestro: Siniestro) -> bytes:
    """Legacy function - use generate_pdf(siniestro, sign_document=False)"""
    return generate_pdf(siniestro, sign_document=False)


class SiniestroPDFGenerator:
    """Clean PDF generator class with single responsibility"""

    def generate_pdf(self, siniestro: Siniestro, db: Session) -> bytes:
        """Generate signed PDF"""
        return generate_pdf(siniestro, sign_document=True)

    def generate_unsigned_pdf(self, siniestro: Siniestro, db: Session) -> bytes:
        """Generate unsigned PDF"""
        return generate_pdf(siniestro, sign_document=False)
