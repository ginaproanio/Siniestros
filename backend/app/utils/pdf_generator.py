import io
import os
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT
from staticmap import StaticMap, CircleMarker
import requests
from PIL import Image as PILImage
from sqlalchemy.orm import Session
from app import models

class SiniestroPDFGenerator:
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self.setup_styles()

    def setup_styles(self):
        """Configurar estilos personalizados para el PDF"""
        self.title_style = ParagraphStyle(
            'CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=16,
            spaceAfter=30,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        )

        self.section_style = ParagraphStyle(
            'SectionHeader',
            parent=self.styles['Heading2'],
            fontSize=14,
            spaceAfter=15,
            fontName='Helvetica-Bold'
        )

        self.normal_style = ParagraphStyle(
            'CustomNormal',
            parent=self.styles['Normal'],
            fontSize=10,
            fontName='Helvetica'
        )

        self.table_header_style = ParagraphStyle(
            'TableHeader',
            parent=self.styles['Normal'],
            fontSize=10,
            fontName='Helvetica-Bold',
            alignment=TA_CENTER
        )

    def generate_map(self, lat: float, lng: float) -> bytes:
        """Generar mapa estático con la ubicación del siniestro"""
        try:
            # Crear mapa con StaticMap
            m = StaticMap(400, 300, 10)

            # Agregar marcador en la ubicación
            marker = CircleMarker((lng, lat), 'red', 10)
            m.add_marker(marker)

            # Generar imagen del mapa
            image = m.render()
            img_byte_arr = io.BytesIO()
            image.save(img_byte_arr, format='PNG')
            img_byte_arr.seek(0)
            return img_byte_arr.getvalue()
        except Exception as e:
            print(f"Error generando mapa: {e}")
            return None

    def download_image(self, url: str) -> bytes:
        """Descargar imagen desde URL"""
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                return response.content
            return None
        except Exception as e:
            print(f"Error descargando imagen {url}: {e}")
            return None

    def create_header_footer(self, canvas, doc):
        """Crear header y footer para cada página"""
        canvas.saveState()

        # Header
        canvas.setFont('Helvetica-Bold', 12)
        canvas.drawString(inch, 10.5 * inch, "INFORME DE INVESTIGACIÓN DE SINIESTRO")

        canvas.setFont('Helvetica', 10)
        canvas.drawString(inch, 10.3 * inch, f"Fecha: {datetime.now().strftime('%d/%m/%Y')}")

        # Footer con numeración de páginas
        page_num = canvas.getPageNumber()
        canvas.setFont('Helvetica', 8)
        canvas.drawString(3 * inch, 0.5 * inch, f"Página {page_num}")

        canvas.restoreState()

    def generate_pdf(self, siniestro: models.Siniestro, db: Session) -> bytes:
        """Generar PDF completo del siniestro"""
        try:
            buffer = io.BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=letter, topMargin=1.5*inch, bottomMargin=1*inch)
            doc.onFirstPage = self.create_header_footer
            doc.onLaterPages = self.create_header_footer

            story = []

            # Título principal
            story.append(Paragraph("INFORME DE INVESTIGACIÓN DE SINIESTRO", self.title_style))
            story.append(Spacer(1, 20))
        except Exception as e:
            print(f"Error inicializando PDF: {e}")
            # Return a minimal PDF if initialization fails
            buffer = io.BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=letter)
            story = [Paragraph("Error generando PDF", self.normal_style)]
            doc.build(story)
            buffer.seek(0)
            return buffer.getvalue()

        # Información básica del siniestro
        story.append(Paragraph("DATOS DEL SINIESTRO", self.section_style))

        basic_data = [
            ["Compañía de Seguros:", siniestro.compania_seguros],
            ["Número de Reclamo:", siniestro.reclamo_num],
            ["Fecha del Siniestro:", siniestro.fecha_siniestro.strftime('%d/%m/%Y %H:%M') if siniestro.fecha_siniestro else ""],
            ["Dirección:", siniestro.direccion_siniestro],
            ["Tipo de Siniestro:", siniestro.tipo_siniestro],
            ["Daños a Terceros:", "Sí" if siniestro.danos_terceros else "No"],
            ["Ejecutivo a Cargo:", siniestro.ejecutivo_cargo or ""],
            ["Fecha de Designación:", siniestro.fecha_designacion.strftime('%d/%m/%Y') if siniestro.fecha_designacion else ""]
        ]

        table = Table(basic_data, colWidths=[2*inch, 4*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
            ('TEXTCOLOR', (0, 0), (0, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        story.append(table)
        story.append(Spacer(1, 20))

        # Mapa de ubicación
        if siniestro.ubicacion_geo_lat and siniestro.ubicacion_geo_lng:
            story.append(Paragraph("UBICACIÓN DEL SINIESTRO", self.section_style))
            map_data = self.generate_map(siniestro.ubicacion_geo_lat, siniestro.ubicacion_geo_lng)
            if map_data:
                map_img = Image(io.BytesIO(map_data), width=4*inch, height=3*inch)
                story.append(map_img)
                story.append(Spacer(1, 10))

        # Datos del asegurado
        if siniestro.asegurado:
            story.append(Paragraph("DATOS DEL ASEGURADO", self.section_style))
            asegurado = siniestro.asegurado
            asegurado_data = [
                ["Tipo:", asegurado.tipo],
            ]

            if asegurado.tipo == "Natural":
                asegurado_data.extend([
                    ["Cédula:", asegurado.cedula or ""],
                    ["Nombre:", asegurado.nombre or ""],
                    ["Celular:", asegurado.celular or ""],
                    ["Dirección:", asegurado.direccion or ""],
                    ["Parentesco:", asegurado.parentesco or ""]
                ])
            else:  # Jurídica
                asegurado_data.extend([
                    ["RUC:", asegurado.ruc or ""],
                    ["Empresa:", asegurado.empresa or ""],
                    ["Representante Legal:", asegurado.representante_legal or ""],
                    ["Teléfono:", asegurado.telefono or ""]
                ])

            table = Table(asegurado_data, colWidths=[2*inch, 4*inch])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
            ]))
            story.append(table)
            story.append(Spacer(1, 20))

        # Datos del conductor
        if siniestro.conductor:
            story.append(Paragraph("DATOS DEL CONDUCTOR", self.section_style))
            conductor = siniestro.conductor
            conductor_data = [
                ["Nombre:", conductor.nombre],
                ["Cédula:", conductor.cedula],
                ["Celular:", conductor.celular or ""],
                ["Dirección:", conductor.direccion or ""],
                ["Parentesco:", conductor.parentesco or ""]
            ]

            table = Table(conductor_data, colWidths=[2*inch, 4*inch])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
            ]))
            story.append(table)
            story.append(Spacer(1, 20))

        # Objeto asegurado (vehículo)
        if siniestro.objeto_asegurado:
            story.append(Paragraph("DATOS DEL VEHÍCULO ASEGURADO", self.section_style))
            vehiculo = siniestro.objeto_asegurado
            vehiculo_data = [
                ["Placa:", vehiculo.placa],
                ["Marca:", vehiculo.marca or ""],
                ["Modelo:", vehiculo.modelo or ""],
                ["Color:", vehiculo.color or ""],
                ["Año:", str(vehiculo.ano) if vehiculo.ano else ""],
                ["Serie Motor:", vehiculo.serie_motor or ""],
                ["Chasis:", vehiculo.chasis or ""]
            ]

            table = Table(vehiculo_data, colWidths=[2*inch, 4*inch])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
            ]))
            story.append(table)
            story.append(Spacer(1, 20))

        # Antecedentes
        if siniestro.antecedentes:
            story.append(Paragraph("ANTECEDENTES", self.section_style))
            for i, antecedente in enumerate(siniestro.antecedentes, 1):
                story.append(Paragraph(f"{i}. {antecedente.descripcion}", self.normal_style))
                story.append(Spacer(1, 10))

        # Relatos del asegurado
        if siniestro.relatos_asegurado:
            story.append(Paragraph("RELATOS DEL ASEGURADO", self.section_style))
            for relato in siniestro.relatos_asegurado:
                story.append(Paragraph(f"Relato {relato.numero_relato}:", self.section_style))
                story.append(Paragraph(relato.texto, self.normal_style))

                # Si hay imagen, intentar incluirla
                if relato.imagen_url:
                    img_data = self.download_image(relato.imagen_url)
                    if img_data:
                        try:
                            img = Image(io.BytesIO(img_data), width=3*inch, height=2*inch)
                            story.append(img)
                        except:
                            pass
                story.append(Spacer(1, 15))

        # Inspecciones del lugar
        if siniestro.inspecciones:
            story.append(Paragraph("INSPECCIÓN DEL LUGAR", self.section_style))
            for inspeccion in siniestro.inspecciones:
                story.append(Paragraph(f"Inspección {inspeccion.numero_inspeccion}:", self.section_style))
                story.append(Paragraph(inspeccion.descripcion, self.normal_style))

                if inspeccion.imagen_url:
                    img_data = self.download_image(inspeccion.imagen_url)
                    if img_data:
                        try:
                            img = Image(io.BytesIO(img_data), width=3*inch, height=2*inch)
                            story.append(img)
                        except:
                            pass
                story.append(Spacer(1, 15))

        # Testigos
        if siniestro.testigos:
            story.append(Paragraph("TESTIGOS", self.section_style))
            for testigo in siniestro.testigos:
                story.append(Paragraph(f"Testigo {testigo.numero_relato}:", self.section_style))
                story.append(Paragraph(testigo.texto, self.normal_style))

                if testigo.imagen_url:
                    img_data = self.download_image(testigo.imagen_url)
                    if img_data:
                        try:
                            img = Image(io.BytesIO(img_data), width=3*inch, height=2*inch)
                            story.append(img)
                        except:
                            pass
                story.append(Spacer(1, 15))

        # Visita al taller
        if siniestro.visita_taller:
            story.append(Paragraph("VISITA AL TALLER", self.section_style))
            story.append(Paragraph(siniestro.visita_taller.descripcion, self.normal_style))
            story.append(Spacer(1, 20))

        # Dinámica del accidente
        if siniestro.dinamica_accidente:
            story.append(Paragraph("DINÁMICA DEL ACCIDENTE", self.section_style))
            story.append(Paragraph(siniestro.dinamica_accidente.descripcion, self.normal_style))
            story.append(Spacer(1, 20))

        # Generar PDF
        doc.build(story)
        buffer.seek(0)
        return buffer.getvalue()

def generate_siniestro_pdf(siniestro_id: int, db: Session) -> bytes:
    """Función principal para generar PDF de siniestro"""
    siniestro = db.query(models.Siniestro).filter(models.Siniestro.id == siniestro_id).first()
    if not siniestro:
        raise ValueError("Siniestro no encontrado")

    generator = SiniestroPDFGenerator()
    return generator.generate_pdf(siniestro, db)
