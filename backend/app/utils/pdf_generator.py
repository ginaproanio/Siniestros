import io
import os
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from sqlalchemy.orm import Session
from app import models
from endesive.pdf import cms
import hashlib


def sign_pdf(pdf_data: bytes, certificate_path: str, password: str = None) -> bytes:
    """Firmar PDF digitalmente usando certificado P12"""
    try:
        print(f"🔐 Firmando PDF con certificado: {certificate_path}")

        # Leer certificado
        with open(certificate_path, 'rb') as f:
            p12_data = f.read()

        # Extraer clave privada y certificado
        from cryptography.hazmat.primitives import serialization
        from cryptography.hazmat.primitives.serialization import pkcs12

        private_key, certificate, additional_certificates = pkcs12.load_key_and_certificates(
            p12_data, password.encode() if password else None
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
        signed_pdf = cms.sign(pdf_data, dct, private_key, certificate, additional_certificates or [])

        print(f"✅ PDF firmado exitosamente: {len(signed_pdf)} bytes")
        return signed_pdf

    except Exception as e:
        print(f"❌ Error firmando PDF: {e}")
        # Retornar PDF sin firma si hay error
        return pdf_data


def generate_simple_pdf(siniestro: models.Siniestro) -> bytes:
    """Generar PDF simple y básico del siniestro"""
    print(f"🔄 Generando PDF para siniestro ID: {siniestro.id}")

    try:
        # Crear buffer para el PDF
        buffer = io.BytesIO()

        # Crear documento
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            topMargin=1*inch,
            bottomMargin=1*inch,
            leftMargin=1*inch,
            rightMargin=1*inch
        )
        styles = getSampleStyleSheet()

        # Estilos personalizados
        title_style = ParagraphStyle(
            'Title',
            parent=styles['Heading1'],
            fontSize=18,
            alignment=TA_CENTER,
            spaceAfter=30,
            fontName='Helvetica-Bold'
        )

        normal_style = ParagraphStyle(
            'Normal',
            parent=styles['Normal'],
            fontSize=10,
            fontName='Helvetica'
        )

        story = []

        # Título principal
        title = Paragraph("INFORME DE INVESTIGACIÓN DE SINIESTRO", title_style)
        story.append(title)

        # Tabla con datos básicos
        data = [
            ["Compañía de Seguros:", siniestro.compania_seguros or "No especificada"],
            ["Número de Reclamo:", siniestro.reclamo_num or "No especificado"],
            ["Fecha del Siniestro:", siniestro.fecha_siniestro.strftime('%d/%m/%Y') if siniestro.fecha_siniestro else "No especificada"],
            ["Dirección:", siniestro.direccion_siniestro or "No especificada"],
            ["Tipo de Siniestro:", siniestro.tipo_siniestro or "No especificado"],
        ]

        table = Table(data, colWidths=[2.5*inch, 4*inch])
        table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'LEFT'),
            ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
        ]))
        story.append(table)
        story.append(Spacer(1, 20))

        # Fecha de generación
        fecha_gen = Paragraph(f"Fecha de Generación: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}", normal_style)
        story.append(fecha_gen)
        story.append(Spacer(1, 10))

        # Generar PDF
        doc.build(story)

        # Obtener datos del buffer
        buffer.seek(0)
        pdf_data = buffer.getvalue()

        print(f"✅ PDF generado exitosamente: {len(pdf_data)} bytes")

        # Firmar PDF si existe certificado
        cert_path = os.path.join(os.path.dirname(__file__), '..', '..', 'maria_susana_espinosa_lozada.p12')
        if os.path.exists(cert_path):
            print("🔐 Firmando PDF con certificado digital...")
            pdf_data = sign_pdf(pdf_data, cert_path)
        else:
            print("⚠️  Certificado no encontrado, PDF sin firma")

        return pdf_data

    except Exception as e:
        print(f"❌ Error generando PDF: {e}")
        # PDF de error mínimo
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        story = [Paragraph("ERROR: No se pudo generar el PDF", styles['Normal'])]
        doc.build(story)
        buffer.seek(0)
        return buffer.getvalue()


class SiniestroPDFGenerator:
    """Generador de PDF con firma digital"""

    def generate_pdf(self, siniestro: models.Siniestro, db: Session) -> bytes:
        """Generar PDF del siniestro con firma digital"""
        return generate_simple_pdf(siniestro)
