import streamlit as st
import datetime
import os
import staticmap
import io
from PIL import Image
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Image as RLImage, Table, TableStyle
from reportlab.lib.enums import TA_JUSTIFY, TA_LEFT, TA_CENTER, TA_RIGHT
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.platypus.doctemplate import PageTemplate, BaseDocTemplate
from reportlab.platypus.frames import Frame

# Crear carpeta para guardar informes y archivos si no existe
if not os.path.exists('informes'):
    os.makedirs('informes')

st.title("Sistema de Generación de Informes de Siniestros")
st.write("Llena los campos obligatorios para generar el informe. Usa las áreas de texto para las secciones narrativas. Puedes subir evidencias al final.")

# Formulario principal
with st.form(key='form_informe'):
    # Fecha actual para el informe
    fecha_informe = datetime.date.today().strftime("%d de %B de %Y")

    # Sección: DATOS DEL SINIESTRO
    st.header("Datos del Siniestro")
    compania_seguros = st.text_input("Compañía de Seguros", value="Zurich Seguros Ecuador S.A.")
    reclamo_num = st.text_input("Reclamo #", value="25-01-VH-7079448")
    fecha_siniestro = st.date_input("Fecha del Siniestro", value=datetime.date(2023, 10, 15))
    direccion_siniestro = st.text_input("Dirección del Siniestro", value="Av. Amazonas y Naciones Unidas, Quito")
    ubicacion_geo = st.text_input("Ubicación Georreferenciada", value="-0.1807,-78.4678")
    danos_terceros = st.text_input("Daños a Terceros", value="Vehículo dañado")
    ejecutivo_cargo = st.text_input("Ejecutivo a Cargo", value="Juan Pérez")
    fecha_designacion = st.date_input("Fecha de Designación", value=datetime.date.today())

    # Sección: ASEGURADO
    st.header("Asegurado")
    razon_social = st.text_input("Razón Social", value="Empresa XYZ S.A.")
    cedula_ruc_aseg = st.text_input("Cédula / RUC", value="1791234567001")
    domicilio_aseg = st.text_input("Domicilio", value="Calle Principal 123, Quito")

    # Sección: CONDUCTOR
    st.header("Conductor")
    nombre_conductor = st.text_input("Nombre", value="Carlos López", key="nombre_conductor")
    cedula_conductor = st.text_input("Cédula", value="1701234567", key="cedula_conductor")
    celular_conductor = st.text_input("Celular", value="0987654321", key="celular_conductor")
    direccion_conductor = st.text_input("Dirección", value="Av. República 456, Quito", key="direccion_conductor")
    parentesco = st.text_input("Parentesco", value="Propietario", key="parentesco_conductor")

    # Sección: OBJETO ASEGURADO
    st.header("Objeto Asegurado")
    placa_aseg = st.text_input("Placa", value="ABC-123")
    marca_aseg = st.text_input("Marca", value="Toyota")
    modelo_aseg = st.text_input("Modelo", value="Corolla")
    color_aseg = st.text_input("Color", value="Blanco")
    ano_aseg = st.number_input("Año", value=2020, min_value=1900, max_value=2100)
    motor_aseg = st.text_input("Motor", value="1.8L")
    chasis_aseg = st.text_input("Chasis", value="1HGCM82633A123456")

    # Sección: TERCEROS AFECTADOS
    st.header("Terceros Afectados")
    afectado = st.text_input("Afectado", key="afectado")
    ruc_afectado = st.text_input("RUC", key="ruc_afectado")
    direccion_afectado = st.text_input("Dirección", key="direccion_afectado")
    telefono_afectado = st.text_input("Teléfono", key="telefono_afectado")
    correo_afectado = st.text_input("Correo", key="correo_afectado")
    bien_afectado = st.text_input("Bien Afectado", key="bien_afectado")
    placa_afectado = st.text_input("Placa", key="placa_afectado")
    marca_afectado = st.text_input("Marca", key="marca_afectado")
    tipo_afectado = st.text_input("Tipo", key="tipo_afectado")
    color_afectado = st.text_input("Color", key="color_afectado")

    # Secciones narrativas
    st.header("Secciones Narrativas")
    antecedentes = st.text_area("Antecedentes", value="El asegurado reportó un accidente vehicular el 15 de octubre de 2023. El vehículo asegurado colisionó con otro vehículo en la intersección.", height=150)
    entrevista_conductor = st.text_area("Entrevista con el Conductor", value="El conductor declaró que circulaba a velocidad normal cuando el otro vehículo invadió su carril. No hubo consumo de alcohol. El conductor tiene licencia válida.", height=200)
    visita_taller = st.text_area("Visita al Taller", value="En el taller se constató daños en el parachoques delantero y lateral izquierdo. El costo estimado de reparación es de $2,500.", height=150)
    inspeccion_lugar = st.text_area("Inspección del Lugar del Siniestro", value="El lugar del accidente es una intersección con semáforo. Las condiciones climáticas eran buenas. Hay testigos que confirman la versión del conductor.", height=150)
    evidencias_complementarias = st.text_area("Evidencias Complementarias", value="Fotos del lugar del accidente, informe policial, y declaración de testigos.", height=150)
    dinamica_accidente = st.text_area("Dinámica del Accidente", value="El vehículo asegurado circulaba de norte a sur. El tercero invadío el cruce en rojo, causando la colisión lateral.", height=150)
    otras_diligencias = st.text_area("Otras Diligencias", value="Contacto con la policía para obtener el parte de accidente.", height=100)
    observaciones = st.text_area("Observaciones (usa numeración si es lista)", value="1. El vehículo estaba asegurado al momento del siniestro.\n2. No hay reporte de lesiones.", height=150)
    conclusiones = st.text_area("Conclusiones (usa numeración si es lista)", value="1. El accidente fue causado por negligencia del tercero.\n2. Los daños son cubiertos por la póliza.", height=150)
    recomendacion = st.text_area("Recomendación sobre el Pago de la Cobertura", value="Se recomienda aprobar el pago de la indemnización por los daños al vehículo asegurado.", height=150)

    # Firma
    st.header("Firma")
    nombre_investigador = st.text_input("Nombre del Investigador", value="María Susana Espinosa Lozada")
    cargo = st.text_input("Cargo", value="Investigación y Recuperación")
    pbx = st.text_input("PBX", value="022.417.481")
    cel = st.text_input("Cel", value="099.9846.432")
    email = st.text_input("Correo", value="susi.espinosa@hotmail.com")

    # Upload de evidencias
    st.header("Subir Evidencias (fotos, documentos, etc.)")
    uploaded_files = st.file_uploader("Sube archivos (imágenes, PDFs, etc.)", accept_multiple_files=True)

    submit_button = st.form_submit_button(label='Generar y Guardar Informe')

if submit_button:
    if not reclamo_num:
        st.error("El número de reclamo es obligatorio.")
    else:
        # Parse geolocation
        try:
            lat_str, lng_str = ubicacion_geo.split(',')
            lat = float(lat_str.strip())
            lng = float(lng_str.strip())
        except:
            lat = lng = None

        # No necesitamos generar mapa para el texto, solo para PDF
        # Generar el contenido del informe
        informe_texto = f"""
INFORME DE INVESTIGACIÓN DE SINIESTRO
{fecha_informe}

DATOS DEL SINIESTRO
CAMPO\tDETALLE
Compañía de Seguros\t{compania_seguros}
Reclamo #\t{reclamo_num}
Fecha del Siniestro\t{fecha_siniestro}
Dirección del Siniestro\t{direccion_siniestro}
Ubicación Georreferenciada\t{ubicacion_geo}
Daños a Terceros\t{danos_terceros}
Ejecutivo a Cargo\t{ejecutivo_cargo}
Fecha de Designación\t{fecha_designacion}

ASEGURADO
CAMPO\tDETALLE
Razón Social\t{razon_social}
Cédula / RUC\t{cedula_ruc_aseg}
Domicilio\t{domicilio_aseg}

CONDUCTOR
CAMPO\tDETALLE
Nombre\t{nombre_conductor}
Cédula\t{cedula_conductor}
Celular\t{celular_conductor}
Dirección\t{direccion_conductor}
Parentesco\t{parentesco}

OBJETO ASEGURADO
CAMPO\tDETALLE
Placa\t{placa_aseg}
Marca\t{marca_aseg}
Modelo\t{modelo_aseg}
Color\t{color_aseg}
Año\t{ano_aseg}
Motor\t{motor_aseg}
Chasis\t{chasis_aseg}

TERCEROS AFECTADOS
CAMPO\tDETALLE
Afectado\t{afectado}
RUC\t{ruc_afectado}
Dirección\t{direccion_afectado}
Teléfono\t{telefono_afectado}
Correo\t{correo_afectado}
Bien Afectado\t{bien_afectado}
Placa\t{placa_afectado}
Marca\t{marca_afectado}
Tipo\t{tipo_afectado}
Color\t{color_afectado}

ANTECEDENTES
{antecedentes}

ENTREVISTA CON EL CONDUCTOR
{entrevista_conductor}

VISITA AL TALLER
{visita_taller}

INSPECCIÓN DEL LUGAR DEL SINIESTRO
{inspeccion_lugar}

EVIDENCIAS COMPLEMENTARIAS
{evidencias_complementarias}

DINÁMICA DEL ACCIDENTE
{dinamica_accidente}

OTRAS DILIGENCIAS
{otras_diligencias}

OBSERVACIONES
{observaciones}

CONCLUSIONES
{conclusiones}

RECOMENDACIÓN SOBRE EL PAGO DE LA COBERTURA
{recomendacion}

Atentamente,
{nombre_investigador}
{cargo}
PBX: {pbx} | Cel: {cel}
{email}
"""

        # Guardar el informe como TXT
        filename_txt = f"informes/informe_{reclamo_num}_{datetime.date.today()}.txt"
        with open(filename_txt, 'w', encoding='utf-8') as f:
            f.write(informe_texto)
        
        # Generar PDF profesional con ReportLab
        filename_pdf = f"informes/informe_{reclamo_num}_{datetime.date.today()}.pdf"

        # Estilos
        styles = getSampleStyleSheet()
        styles.add(ParagraphStyle(name='Title', fontSize=16, alignment=TA_CENTER, spaceAfter=20, fontName='Helvetica-Bold'))
        styles.add(ParagraphStyle(name='Date', fontSize=12, alignment=TA_CENTER, spaceAfter=30))
        styles.add(ParagraphStyle(name='SectionHeader', fontSize=14, alignment=TA_LEFT, spaceAfter=10, fontName='Helvetica-Bold'))
        styles.add(ParagraphStyle(name='Normal', fontSize=10, alignment=TA_LEFT, spaceAfter=10))
        styles.add(ParagraphStyle(name='Justified', fontSize=10, alignment=TA_JUSTIFY, spaceAfter=10))
        styles.add(ParagraphStyle(name='Signature', fontSize=10, alignment=TA_LEFT, spaceAfter=5))

        # Función para crear tabla de datos
        def create_data_table(data_dict):
            table_data = [['Campo', 'Detalle']]
            for key, value in data_dict.items():
                if value:  # Solo incluir campos con valor
                    table_data.append([key, str(value)])

            table = Table(table_data, colWidths=[2.5*inch, 4*inch])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('FONTSIZE', (0, 1), (-1, -1), 9),
            ]))
            return table

        # Función para header y footer
        def header_footer(canvas, doc):
            canvas.saveState()

            # Header
            canvas.setFont('Helvetica-Bold', 10)
            canvas.drawString(inch, 10.5*inch, compania_seguros)
            canvas.drawRightString(7.5*inch, 10.5*inch, fecha_informe)
            canvas.line(inch, 10.3*inch, 7.5*inch, 10.3*inch)

            # Footer
            canvas.setFont('Helvetica', 8)
            page_num = canvas.getPageNumber()
            canvas.drawString(inch, 0.5*inch, f"Página {page_num}")
            canvas.drawRightString(7.5*inch, 0.5*inch, "Documento Confidencial")
            canvas.line(inch, 0.7*inch, 7.5*inch, 0.7*inch)

            canvas.restoreState()

        # Documento
        doc = SimpleDocTemplate(filename_pdf, pagesize=letter, leftMargin=inch, rightMargin=inch,
                               topMargin=1.5*inch, bottomMargin=inch, onFirstPage=header_footer,
                               onLaterPages=header_footer)
        story = []

        # Título
        story.append(Paragraph("INFORME DE INVESTIGACIÓN DE SINIESTRO", styles['Title']))
        story.append(Paragraph(fecha_informe, styles['Date']))

        # Mapa si existe
        if lat is not None and lng is not None:
            # Crear mapa estático con staticmap
            m = staticmap.StaticMap(400, 300, url_template='https://tile.openstreetmap.org/{z}/{x}/{y}.png')
            marker = staticmap.CircleMarker((lng, lat), 'red', 10)  # Nota: staticmap usa (lng, lat)
            m.add_marker(marker)
            img = m.render()
            img_bytes = io.BytesIO()
            img.save(img_bytes, format='PNG')
            img_bytes.seek(0)
            map_img = RLImage(img_bytes, width=4*inch, height=3*inch)
            story.append(map_img)
            story.append(Spacer(1, 12))

        # Datos del Siniestro
        story.append(Paragraph("DATOS DEL SINIESTRO", styles['SectionHeader']))
        siniestro_data = {
            'Compañía de Seguros': compania_seguros,
            'Reclamo #': reclamo_num,
            'Fecha del Siniestro': str(fecha_siniestro),
            'Dirección del Siniestro': direccion_siniestro,
            'Ubicación Georreferenciada': ubicacion_geo,
            'Daños a Terceros': danos_terceros,
            'Ejecutivo a Cargo': ejecutivo_cargo,
            'Fecha de Designación': str(fecha_designacion)
        }
        story.append(create_data_table(siniestro_data))
        story.append(Spacer(1, 12))

        # Asegurado
        story.append(Paragraph("ASEGURADO", styles['SectionHeader']))
        asegurado_data = {
            'Razón Social': razon_social,
            'Cédula / RUC': cedula_ruc_aseg,
            'Domicilio': domicilio_aseg
        }
        story.append(create_data_table(asegurado_data))
        story.append(Spacer(1, 12))

        # Conductor
        story.append(Paragraph("CONDUCTOR", styles['SectionHeader']))
        conductor_data = {
            'Nombre': nombre_conductor,
            'Cédula': cedula_conductor,
            'Celular': celular_conductor,
            'Dirección': direccion_conductor,
            'Parentesco': parentesco
        }
        story.append(create_data_table(conductor_data))
        story.append(Spacer(1, 12))

        # Objeto Asegurado
        story.append(Paragraph("OBJETO ASEGURADO", styles['SectionHeader']))
        objeto_data = {
            'Placa': placa_aseg,
            'Marca': marca_aseg,
            'Modelo': modelo_aseg,
            'Color': color_aseg,
            'Año': ano_aseg,
            'Motor': motor_aseg,
            'Chasis': chasis_aseg
        }
        story.append(create_data_table(objeto_data))
        story.append(Spacer(1, 12))

        # Terceros Afectados (solo si hay datos)
        if afectado or placa_afectado:
            story.append(Paragraph("TERCEROS AFECTADOS", styles['SectionHeader']))
            afectados_data = {
                'Afectado': afectado,
                'RUC': ruc_afectado,
                'Dirección': direccion_afectado,
                'Teléfono': telefono_afectado,
                'Correo': correo_afectado,
                'Bien Afectado': bien_afectado,
                'Placa': placa_afectado,
                'Marca': marca_afectado,
                'Tipo': tipo_afectado,
                'Color': color_afectado
            }
            story.append(create_data_table(afectados_data))
            story.append(Spacer(1, 12))

        # Secciones narrativas
        narrative_sections = [
            ("ANTECEDENTES", antecedentes),
            ("ENTREVISTA CON EL CONDUCTOR", entrevista_conductor),
            ("VISITA AL TALLER", visita_taller),
            ("INSPECCIÓN DEL LUGAR DEL SINIESTRO", inspeccion_lugar),
            ("EVIDENCIAS COMPLEMENTARIAS", evidencias_complementarias),
            ("DINÁMICA DEL ACCIDENTE", dinamica_accidente),
            ("OTRAS DILIGENCIAS", otras_diligencias),
            ("OBSERVACIONES", observaciones),
            ("CONCLUSIONES", conclusiones),
            ("RECOMENDACIÓN SOBRE EL PAGO DE LA COBERTURA", recomendacion)
        ]

        for title, content in narrative_sections:
            if content.strip():
                story.append(Paragraph(title, styles['SectionHeader']))
                story.append(Paragraph(content.replace('\n', '<br/>'), styles['Justified']))
                story.append(Spacer(1, 12))

        # Firma
        story.append(Spacer(1, 30))
        story.append(Paragraph("Atentamente,", styles['Signature']))
        story.append(Paragraph(nombre_investigador, styles['Signature']))
        story.append(Paragraph(cargo, styles['Signature']))
        story.append(Paragraph(f"PBX: {pbx} | Cel: {cel}", styles['Signature']))
        story.append(Paragraph(email, styles['Signature']))

        doc.build(story)

        # Leer el PDF para descarga
        with open(filename_pdf, "rb") as pdf_file:
            pdf_data = pdf_file.read()

        st.success("Informe generado exitosamente!")

        # Botón de descarga del PDF
        st.download_button(
            label="Descargar Informe en PDF",
            data=pdf_data,
            file_name=f"informe_{reclamo_num}_{datetime.date.today()}.pdf",
            mime="application/pdf"
        )

        # Guardar archivos subidos
        if uploaded_files:
            for uploaded_file in uploaded_files:
                with open(os.path.join('informes', f"{reclamo_num}_{uploaded_file.name}"), "wb") as f:
                    f.write(uploaded_file.getbuffer())
            st.success("Archivos de evidencias subidos y guardados.")

        # Mostrar vista previa (opcional)
        with st.expander("Vista Previa del Informe (Texto)"):
            st.text_area("", informe_texto, height=300)
