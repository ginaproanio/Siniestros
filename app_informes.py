import streamlit as st
import datetime
import os
import staticmap
import io
from PIL import Image
from endesive import pdf
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Image as RLImage, Table, TableStyle
from reportlab.lib.enums import TA_JUSTIFY, TA_LEFT, TA_CENTER, TA_RIGHT
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.platypus.doctemplate import PageTemplate, BaseDocTemplate
from reportlab.platypus.frames import Frame

st.set_page_config(
    page_title="Sistema de Informes de Siniestros",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="collapsed"
)

class CustomDocTemplate(BaseDocTemplate):
    def __init__(self, filename, **kwargs):
        super().__init__(filename, **kwargs)
        self.total_pages = 0

    def afterPage(self):
        super().afterPage()
        self.total_pages = max(self.total_pages, self.page)

# Crear carpeta para guardar informes y archivos si no existe
if not os.path.exists('informes'):
    os.makedirs('informes')

st.title("Sistema de Generación de Informes de Siniestros")
st.write("Llena los campos obligatorios para generar el informe. Usa las áreas de texto para las secciones narrativas. Puedes subir evidencias al final.")

# Initialize session state for relatos
if 'num_relatos_aseg' not in st.session_state:
    st.session_state.num_relatos_aseg = 1
if 'num_relatos_inspec' not in st.session_state:
    st.session_state.num_relatos_inspec = 1
if 'num_relatos_testigos' not in st.session_state:
    st.session_state.num_relatos_testigos = 1



# Sección: ASEGURADO (fuera del formulario para actualización dinámica)
st.header("Asegurado")
tipo_asegurado = st.radio("Tipo de Asegurado", options=["Persona Natural", "Persona Jurídica"], index=1, key="tipo_asegurado")

asegurado_data = {}

if tipo_asegurado == "Persona Natural":
    cols3 = st.columns(5)
    with cols3[0]:
        cedula_aseg = st.text_input("Cédula", value="1701234567", key="cedula_aseg")
    with cols3[1]:
        nombre_aseg = st.text_input("Nombre", value="Juan Pérez", key="nombre_aseg")
    with cols3[2]:
        celular_aseg = st.text_input("Celular", value="0987654321", key="celular_aseg")
    with cols3[3]:
        direccion_aseg = st.text_input("Dirección", value="Calle Principal 123, Quito", key="direccion_aseg")
    with cols3[4]:
        parentesco_aseg = st.text_input("Parentesco", value="Propietario", key="parentesco_aseg")

    asegurado_data = {
        'Tipo': 'Persona Natural',
        'Cédula': cedula_aseg,
        'Nombre': nombre_aseg,
        'Celular': celular_aseg,
        'Dirección': direccion_aseg,
        'Parentesco': parentesco_aseg
    }
else:  # Persona Jurídica
    cols3 = st.columns(4)
    with cols3[0]:
        ruc_aseg = st.text_input("RUC", value="1791234567001", key="ruc_aseg")
    with cols3[1]:
        empresa_aseg = st.text_input("Empresa", value="Empresa XYZ S.A.", key="empresa_aseg")
    with cols3[2]:
        representante_legal_aseg = st.text_input("Representante Legal", value="Juan Pérez", key="representante_aseg")
    with cols3[3]:
        telefono_aseg = st.text_input("Teléfono", value="022417481", key="telefono_aseg")

    cols4 = st.columns(1)
    with cols4[0]:
        direccion_aseg_jur = st.text_input("Dirección", value="Calle Principal 123, Quito", key="direccion_aseg_jur")

    asegurado_data = {
        'Tipo': 'Persona Jurídica',
        'RUC': ruc_aseg,
        'Empresa': empresa_aseg,
        'Representante Legal': representante_legal_aseg,
        'Dirección': direccion_aseg_jur,
        'Teléfono': telefono_aseg
    }

# Formulario principal
with st.form(key='form_informe'):
    # Fecha actual para el informe
    fecha_informe = datetime.date.today().strftime("%d de %B de %Y")

    # Sección: DATOS DEL SINIESTRO
    st.header("Datos del Siniestro")
    cols = st.columns(4)
    with cols[0]:
        compania_seguros = st.text_input("Compañía de Seguros", value="Zurich Seguros Ecuador S.A.")
    with cols[1]:
        reclamo_num = st.text_input("Reclamo #", value="25-01-VH-7079448")
    with cols[2]:
        fecha_siniestro = st.date_input("Fecha del Siniestro", value=datetime.date(2023, 10, 15))
    with cols[3]:
        direccion_siniestro = st.text_input("Dirección del Siniestro", value="Av. Amazonas y Naciones Unidas, Quito")

    cols2 = st.columns(4)
    with cols2[0]:
        ubicacion_geo = st.text_input("Ubicación Georreferenciada", value="-0.1807,-78.4678")
    with cols2[1]:
        danos_terceros = st.selectbox("Daños a Terceros", options=["Sí", "No"], index=0)
    with cols2[2]:
        ejecutivo_cargo = st.text_input("Ejecutivo a Cargo", value="Juan Pérez")
    with cols2[3]:
        fecha_designacion = st.date_input("Fecha de Designación", value=datetime.date.today())



    # Sección: CONDUCTOR
    st.header("Conductor")
    cols4 = st.columns(3)
    with cols4[0]:
        nombre_conductor = st.text_input("Nombre", value="Carlos López", key="nombre_conductor")
    with cols4[1]:
        cedula_conductor = st.text_input("Cédula", value="1701234567", key="cedula_conductor")
    with cols4[2]:
        celular_conductor = st.text_input("Celular", value="0987654321", key="celular_conductor")

    cols5 = st.columns(2)
    with cols5[0]:
        direccion_conductor = st.text_input("Dirección", value="Av. República 456, Quito", key="direccion_conductor")
    with cols5[1]:
        parentesco = st.text_input("Parentesco", value="Propietario", key="parentesco_conductor")

    # Sección: OBJETO ASEGURADO
    st.header("Objeto Asegurado")
    cols6 = st.columns(4)
    with cols6[0]:
        placa_aseg = st.text_input("Placa", value="ABC-123")
    with cols6[1]:
        marca_aseg = st.text_input("Marca", value="Toyota")
    with cols6[2]:
        modelo_aseg = st.text_input("Modelo", value="Corolla")
    with cols6[3]:
        color_aseg = st.text_input("Color", value="Blanco")

    cols7 = st.columns(3)
    with cols7[0]:
        ano_aseg = st.number_input("Año", value=2020, min_value=1900, max_value=2100)
    with cols7[1]:
        motor_aseg = st.text_input("Serie del Motor", value="")
    with cols7[2]:
        chasis_aseg = st.text_input("Chasis", value="1HGCM82633A123456")

    # ANTECEDENTES
    st.header("ANTECEDENTES")
    antecedentes = st.text_area("Antecedentes", value="El asegurado reportó un accidente vehicular el 15 de octubre de 2023. El vehículo asegurado colisionó con otro vehículo en la intersección.", height=150)



    # ENTREVISTA CON EL ASEGURADO
    st.markdown('<span style="background-color: yellow;">ENTREVISTA CON EL ASEGURADO</span>', unsafe_allow_html=True)

    relatos_asegurado = []

    for i in range(st.session_state.num_relatos_aseg):
        st.subheader(f"Relato {i+1}")
        cols_relato = st.columns([3, 1])  # 3 for text, 1 for image
        with cols_relato[0]:
            relato_text = st.text_area(f"Texto del Relato {i+1}", value="" if i > 0 else "El asegurado declaró que el vehículo estaba estacionado cuando fue impactado por otro vehículo. No hubo testigos directos del incidente.", height=150, key=f"relato_aseg_text_{i}")
        with cols_relato[1]:
            st.write("Añadir Imagen (opcional)")
            image_file = st.file_uploader(f"Cargar Imagen {i+1}", type=['jpg', 'jpeg', 'png'], key=f"relato_aseg_img_{i}")



        relatos_asegurado.append({
            'text': relato_text,
            'image': image_file
        })

    # INSPECCIÓN DEL LUGAR DEL SINIESTRO
    st.header("INSPECCIÓN DEL LUGAR DEL SINIESTRO")

    inspeccion_relatos = []

    for i in range(st.session_state.num_relatos_inspec):
        st.subheader(f"Descripción {i+1}")
        cols_inspec = st.columns([3, 1])  # 3 for text, 1 for image
        with cols_inspec[0]:
            inspec_text = st.text_area(f"Texto de la Descripción {i+1}", value="" if i > 0 else "El lugar del accidente presenta daños en la infraestructura vial. Se observan marcas de frenado y restos de vidrio.", height=150, key=f"inspec_text_{i}")
        with cols_inspec[1]:
            st.write("Añadir Imagen (opcional)")
            inspec_image = st.file_uploader(f"Seleccionar imagen {i+1}", type=['jpg', 'jpeg', 'png'], key=f"inspec_img_{i}")



        inspeccion_relatos.append({
            'text': inspec_text,
            'image': inspec_image
        })

    # TESTIGOS
    st.header("TESTIGOS")

    testigos_relatos = []

    for i in range(st.session_state.num_relatos_testigos):
        st.subheader(f"Relato {i+1}")
        cols_testigo = st.columns([3, 1])  # 3 for text, 1 for image
        with cols_testigo[0]:
            testigo_text = st.text_area(f"Texto del Relato {i+1}", value="" if i > 0 else "El testigo declaró haber visto el accidente desde su ventana. Confirma la versión del asegurado.", height=150, key=f"testigo_text_{i}")
        with cols_testigo[1]:
            st.write("Añadir Imagen (opcional)")
            testigo_image = st.file_uploader(f"Seleccionar imagen {i+1}", type=['jpg', 'jpeg', 'png'], key=f"testigo_img_{i}")



        testigos_relatos.append({
            'text': testigo_text,
            'image': testigo_image
        })

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

    # Galería de Imágenes de Inspección
    st.header("Galería de Imágenes de Inspección")
    st.write("Sube las fotos tomadas durante la inspección del siniestro. Para cada imagen, proporciona una descripción detallada.")

    # Permitir subir hasta 10 imágenes
    num_images = st.number_input("Número de imágenes a subir", min_value=0, max_value=10, value=0)

    inspection_images = []
    image_descriptions = []

    if num_images > 0:
        cols = st.columns(2)  # 2 columnas para organizar los inputs

        for i in range(num_images):
            col_idx = i % 2
            with cols[col_idx]:
                st.subheader(f"Imagen {i+1}")
                image_file = st.file_uploader(f"Seleccionar imagen {i+1}", type=['jpg', 'jpeg', 'png'], key=f"img_{i}")
                description = st.text_area(f"Descripción de la imagen {i+1}",
                                         placeholder=f"Describe detalladamente la imagen {i+1}...",
                                         height=80, key=f"desc_{i}")

                if image_file is not None:
                    inspection_images.append(image_file)
                    image_descriptions.append(description if description.strip() else f"Imagen {i+1} del siniestro")

    # Upload de evidencias adicionales
    st.header("Evidencias Adicionales (documentos, PDFs, etc.)")
    uploaded_files = st.file_uploader("Sube archivos adicionales (documentos, PDFs, etc.)", accept_multiple_files=True)

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
        asegurado_lines = '\n'.join([f'{k}\t{v}' for k, v in asegurado_data.items()])
        relatos_aseg_text = '\n\n'.join([f'Relato {i+1}:\n{relato["text"]}' for i, relato in enumerate(relatos_asegurado, 1)])
        inspeccion_text = '\n\n'.join([f'Descripción {i+1}:\n{desc["text"]}' for i, desc in enumerate(inspeccion_relatos, 1)])
        testigos_text = '\n\n'.join([f'Relato {i+1}:\n{relato["text"]}' for i, relato in enumerate(testigos_relatos, 1)])

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
{asegurado_lines}

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

ANTECEDENTES
{antecedentes}

ENTREVISTA CON EL ASEGURADO
{relatos_aseg_text}

INSPECCIÓN DEL LUGAR DEL SINIESTRO
{inspeccion_text}

TESTIGOS
{testigos_text}
"""



        informe_texto += f"""

VISITA AL TALLER
{visita_taller}

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
        filename_pdf = f"informes/{reclamo_num}.pdf"

        # Estilos
        styles = getSampleStyleSheet()
        styles.add(ParagraphStyle(name='ReportTitle', fontSize=16, alignment=TA_CENTER, spaceAfter=20, fontName='Helvetica-Bold'))
        styles.add(ParagraphStyle(name='ReportDate', fontSize=12, alignment=TA_CENTER, spaceAfter=30))
        styles.add(ParagraphStyle(name='SectionHeader', fontSize=14, alignment=TA_LEFT, spaceAfter=10, fontName='Helvetica-Bold'))
        styles.add(ParagraphStyle(name='NormalLeft', fontSize=10, alignment=TA_LEFT, spaceAfter=10))
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
                ('FONTSIZE', (0, 0), (-1, 0), 9),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('FONTSIZE', (0, 1), (-1, -1), 8),
                ('ROUNDEDCORNERS', [3, 3, 3, 3]),  # Radio de 3px para todas las 4 esquinas
            ]))
            return table

        # Variable para almacenar el total de páginas
        total_pages = [0]

        # Función para header
        def header(canvas, doc):
            canvas.saveState()
            # Header - Right aligned
            canvas.setFont('Helvetica-Bold', 10)
            # First line: INFORME DE INVESTIGACIÓN
            canvas.drawRightString(7.5*inch, 10.8*inch, "INFORME DE INVESTIGACIÓN")
            # Second line: RECLAMO: [number]
            canvas.drawRightString(7.5*inch, 10.6*inch, f"RECLAMO: {reclamo_num}")
            canvas.restoreState()

        # Función para footer
        def footer(canvas, doc):
            canvas.saveState()
            # Footer - Page numbering centered
            canvas.setFont('Helvetica', 8)
            page_num = canvas.getPageNumber()
            if total_pages[0] > 0:
                page_text = f"Pág. {page_num}/{total_pages[0]}"
            else:
                page_text = f"Pág. {page_num}"
            canvas.drawCentredString(4.25*inch, 0.5*inch, page_text)
            canvas.restoreState()

        # Función para crear página de carátula
        def create_cover_page():
            cover_story = []

            # Espacio inicial
            cover_story.append(Spacer(1, 2*inch))

            # Título principal
            cover_story.append(Paragraph("INFORME DE INVESTIGACIÓN DE SINIESTRO", styles['ReportTitle']))
            cover_story.append(Spacer(1, 0.5*inch))

            # Reclamo
            cover_story.append(Paragraph(f"RECLAMO: {reclamo_num}", ParagraphStyle('CoverSubtitle', parent=styles['NormalLeft'], fontSize=14, alignment=TA_CENTER)))
            cover_story.append(Spacer(1, 0.3*inch))

            # Fecha de emisión
            cover_story.append(Paragraph(f"FECHA DE EMISIÓN: {fecha_informe}", ParagraphStyle('CoverDate', parent=styles['NormalLeft'], fontSize=12, alignment=TA_CENTER)))
            cover_story.append(Spacer(1, 1*inch))

            # Datos principales
            cover_story.append(Paragraph("DATOS PRINCIPALES:", ParagraphStyle('CoverHeader', parent=styles['SectionHeader'], fontSize=12, alignment=TA_LEFT)))

            bullet_style = ParagraphStyle('BulletStyle', parent=styles['NormalLeft'], leftIndent=20, bulletIndent=0)
            cover_story.append(Paragraph(f"• Asegurado: {asegurado_data.get('Empresa', asegurado_data.get('Tipo', 'Asegurado'))}", bullet_style))
            cover_story.append(Paragraph(f"• Placa: {placa_aseg}", bullet_style))
            cover_story.append(Paragraph(f"• Fecha Siniestro: {str(fecha_siniestro)}", bullet_style))
            cover_story.append(Paragraph(f"• Inspector: {nombre_investigador}", bullet_style))
            cover_story.append(Paragraph(f"• Compañía: {compania_seguros}", bullet_style))

            cover_story.append(Spacer(1, 1*inch))

            # Texto final
            cover_story.append(Paragraph("Este informe consta de varias páginas incluyendo anexos.", ParagraphStyle('CoverText', parent=styles['NormalLeft'], alignment=TA_CENTER)))
            cover_story.append(Spacer(1, 0.5*inch))

            return cover_story

        # Función para crear índice dinámico
        def create_index():
            index_story = []

            # Título del índice
            index_story.append(Paragraph("ÍNDICE", styles['SectionHeader']))
            index_story.append(Spacer(1, 0.5*inch))

            # Lista de secciones con páginas estimadas
            sections = [
                ("DATOS DEL SINIESTRO", 1),
                ("ASEGURADO", 1),
                ("CONDUCTOR", 2),
                ("OBJETO ASEGURADO", 2),
                ("LUGAR DEL SINIESTRO", 3),
            ]

            # Secciones narrativas
            page_counter = 4
            narrative_titles = []
            if antecedentes.strip(): narrative_titles.append("ANTECEDENTES")
            if any(relato['text'].strip() for relato in relatos_asegurado): narrative_titles.append("ENTREVISTA CON EL ASEGURADO")
            if visita_taller.strip(): narrative_titles.append("VISITA AL TALLER")
            if inspeccion_lugar.strip(): narrative_titles.append("INSPECCIÓN DEL LUGAR DEL SINIESTRO")
            if evidencias_complementarias.strip(): narrative_titles.append("EVIDENCIAS COMPLEMENTARIAS")
            if dinamica_accidente.strip(): narrative_titles.append("DINÁMICA DEL ACCIDENTE")
            if otras_diligencias.strip(): narrative_titles.append("OTRAS DILIGENCIAS")
            if observaciones.strip(): narrative_titles.append("OBSERVACIONES")
            if conclusiones.strip(): narrative_titles.append("CONCLUSIONES")
            if recomendacion.strip(): narrative_titles.append("RECOMENDACIÓN SOBRE EL PAGO DE LA COBERTURA")

            for title in narrative_titles:
                sections.append((title, page_counter))
                page_counter += 1

            # Generar entradas del índice
            for i, (section_title, page_num) in enumerate(sections, 1):
                dots = "." * (60 - len(section_title))
                index_story.append(Paragraph(f"{i}. {section_title} {dots} {page_num}", styles['NormalLeft']))

            return index_story

        # Crear el story completo
        story = []

        # Página de carátula
        story.extend(create_cover_page())
        story.append(PageBreak())

        # Índice
        story.extend(create_index())
        story.append(PageBreak())

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
            'Fecha de Designación': str(fecha_designacion),
            'Tipo de Siniestro': 'Vehicular'
        }
        story.append(create_data_table(siniestro_data))
        story.append(Spacer(1, 6))

        # Asegurado
        story.append(Paragraph("ASEGURADO", styles['SectionHeader']))
        story.append(create_data_table(asegurado_data))
        story.append(Spacer(1, 6))

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
        story.append(Spacer(1, 6))

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
        story.append(Spacer(1, 6))

        # Lugar del Siniestro
        story.append(Paragraph("LUGAR DEL SINIESTRO", styles['SectionHeader']))
        if lat is not None and lng is not None:
            maps_url = f"https://www.google.com/maps?q={lat},{lng}"
            # Solo la URL subrayada y en azul, no la palabra "Ubicación"
            story.append(Paragraph(f"Ubicación: ", styles['NormalLeft']))
            url_style = ParagraphStyle('URLStyle', parent=styles['NormalLeft'], underline=True, textColor=colors.blue)
            story.append(Paragraph(maps_url, url_style))
            story.append(Spacer(1, 6))

            # Crear mapa estático con staticmap
            m = staticmap.StaticMap(400, 300, url_template='https://tile.openstreetmap.org/{z}/{x}/{y}.png')
            marker = staticmap.CircleMarker((lng, lat), 'red', 10)
            m.add_marker(marker)
            img = m.render()
            img_bytes = io.BytesIO()
            img.save(img_bytes, format='PNG')
            img_bytes.seek(0)
            map_img = RLImage(img_bytes, width=4*inch, height=3*inch)
            story.append(map_img)
        else:
            story.append(Paragraph("Coordenadas no disponibles", styles['NormalLeft']))
        story.append(Spacer(1, 12))



        # Galería de Imágenes de Inspección
        if inspection_images:
            story.append(Paragraph("GALERÍA DE IMÁGENES DE INSPECCIÓN", styles['SectionHeader']))
            story.append(Spacer(1, 6))

            # Crear tabla de 2 columnas para las imágenes
            image_table_data = []
            current_row = []

            for i, (img_file, description) in enumerate(zip(inspection_images, image_descriptions)):
                # Procesar imagen
                img = Image.open(img_file)
                # Redimensionar manteniendo proporción
                max_width, max_height = 2.5*inch, 2*inch
                img_ratio = img.width / img.height
                if img_ratio > max_width / max_height:
                    new_width = max_width
                    new_height = max_width / img_ratio
                else:
                    new_height = max_height
                    new_width = max_height * img_ratio

                # Convertir a ReportLab Image
                img_bytes = io.BytesIO()
                img.save(img_bytes, format='PNG')
                img_bytes.seek(0)
                rl_img = RLImage(img_bytes, width=new_width, height=new_height)

                # Crear celda con imagen y descripción
                image_cell = []
                image_cell.append(rl_img)
                image_cell.append(Spacer(1, 6))
                image_cell.append(Paragraph(f"Imagen {i+1}: {description}", styles['NormalLeft']))

                current_row.append(image_cell)

                # Si tenemos 2 imágenes o es la última, agregar fila
                if len(current_row) == 2 or i == len(inspection_images) - 1:
                    # Si solo tenemos una imagen en la fila, agregar celda vacía
                    if len(current_row) == 1:
                        current_row.append("")

                    image_table_data.append(current_row)
                    current_row = []

            # Crear tabla de imágenes
            if image_table_data:
                image_table = Table(image_table_data, colWidths=[3*inch, 3*inch])
                image_table.setStyle(TableStyle([
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ]))
                story.append(image_table)
                story.append(Spacer(1, 12))

        # ANTECEDENTES
        if antecedentes.strip():
            story.append(Paragraph("ANTECEDENTES", styles['SectionHeader']))
            story.append(Paragraph(antecedentes.replace('\n', '<br/>'), styles['Justified']))
            story.append(Spacer(1, 12))

        # ENTREVISTA CON EL ASEGURADO
        if any(relato['text'].strip() for relato in relatos_asegurado):
            story.append(Paragraph("ENTREVISTA CON EL ASEGURADO", styles['SectionHeader']))
            story.append(Spacer(1, 6))

            for i, relato in enumerate(relatos_asegurado):
                if relato['text'].strip():
                    if len(relatos_asegurado) > 1:
                        story.append(Paragraph(f"Relato {i+1}", styles['NormalLeft']))
                        story.append(Spacer(1, 3))

                    if relato['image'] is not None:
                        # Procesar imagen
                        img = Image.open(relato['image'])
                        # Redimensionar manteniendo proporción
                        max_width, max_height = 2.5*inch, 3*inch
                        img_ratio = img.width / img.height
                        if img_ratio > max_width / max_height:
                            new_width = max_width
                            new_height = max_width / img_ratio
                        else:
                            new_height = max_height
                            new_width = max_height * img_ratio

                        # Convertir a ReportLab Image
                        img_bytes = io.BytesIO()
                        img.save(img_bytes, format='PNG')
                        img_bytes.seek(0)
                        rl_img = RLImage(img_bytes, width=new_width, height=new_height)

                        # Crear tabla de 2 columnas: imagen y texto
                        table_data = [[rl_img, Paragraph(relato['text'].replace('\n', '<br/>'), styles['Justified'])]]
                        table = Table(table_data, colWidths=[3*inch, 4*inch])
                        table.setStyle(TableStyle([
                            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                        ]))
                        story.append(table)
                    else:
                        # Texto a ancho completo
                        story.append(Paragraph(relato['text'].replace('\n', '<br/>'), styles['Justified']))

                    story.append(Spacer(1, 6))

        # INSPECCIÓN DEL LUGAR DEL SINIESTRO
        if any(desc['text'].strip() for desc in inspeccion_relatos):
            story.append(Paragraph("INSPECCIÓN DEL LUGAR DEL SINIESTRO", styles['SectionHeader']))
            story.append(Spacer(1, 6))

            for i, desc in enumerate(inspeccion_relatos):
                if desc['text'].strip():
                    if len(inspeccion_relatos) > 1:
                        story.append(Paragraph(f"Descripción {i+1}", styles['NormalLeft']))
                        story.append(Spacer(1, 3))

                    if desc['image'] is not None:
                        # Procesar imagen
                        img = Image.open(desc['image'])
                        # Redimensionar manteniendo proporción
                        max_width, max_height = 2.5*inch, 3*inch
                        img_ratio = img.width / img.height
                        if img_ratio > max_width / max_height:
                            new_width = max_width
                            new_height = max_width / img_ratio
                        else:
                            new_height = max_height
                            new_width = max_height * img_ratio

                        # Convertir a ReportLab Image
                        img_bytes = io.BytesIO()
                        img.save(img_bytes, format='PNG')
                        img_bytes.seek(0)
                        rl_img = RLImage(img_bytes, width=new_width, height=new_height)

                        # Crear tabla de 2 columnas: imagen y texto
                        table_data = [[rl_img, Paragraph(desc['text'].replace('\n', '<br/>'), styles['Justified'])]]
                        table = Table(table_data, colWidths=[3*inch, 4*inch])
                        table.setStyle(TableStyle([
                            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                        ]))
                        story.append(table)
                    else:
                        # Texto a ancho completo
                        story.append(Paragraph(desc['text'].replace('\n', '<br/>'), styles['Justified']))

                    story.append(Spacer(1, 6))

        # TESTIGOS
        if any(relato['text'].strip() for relato in testigos_relatos):
            story.append(Paragraph("TESTIGOS", styles['SectionHeader']))
            story.append(Spacer(1, 6))

            for i, relato in enumerate(testigos_relatos):
                if relato['text'].strip():
                    if len(testigos_relatos) > 1:
                        story.append(Paragraph(f"Relato {i+1}", styles['NormalLeft']))
                        story.append(Spacer(1, 3))

                    if relato['image'] is not None:
                        # Procesar imagen
                        img = Image.open(relato['image'])
                        # Redimensionar manteniendo proporción
                        max_width, max_height = 2.5*inch, 3*inch
                        img_ratio = img.width / img.height
                        if img_ratio > max_width / max_height:
                            new_width = max_width
                            new_height = max_width / img_ratio
                        else:
                            new_height = max_height
                            new_width = max_height * img_ratio

                        # Convertir a ReportLab Image
                        img_bytes = io.BytesIO()
                        img.save(img_bytes, format='PNG')
                        img_bytes.seek(0)
                        rl_img = RLImage(img_bytes, width=new_width, height=new_height)

                        # Crear tabla de 2 columnas: imagen y texto
                        table_data = [[rl_img, Paragraph(relato['text'].replace('\n', '<br/>'), styles['Justified'])]]
                        table = Table(table_data, colWidths=[3*inch, 4*inch])
                        table.setStyle(TableStyle([
                            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                        ]))
                        story.append(table)
                    else:
                        # Texto a ancho completo
                        story.append(Paragraph(relato['text'].replace('\n', '<br/>'), styles['Justified']))

                    story.append(Spacer(1, 6))



        # Resto de secciones
        remaining_sections = [
            ("VISITA AL TALLER", visita_taller),
            ("EVIDENCIAS COMPLEMENTARIAS", evidencias_complementarias),
            ("DINÁMICA DEL ACCIDENTE", dinamica_accidente),
            ("OTRAS DILIGENCIAS", otras_diligencias),
            ("OBSERVACIONES", observaciones),
            ("CONCLUSIONES", conclusiones),
            ("RECOMENDACIÓN SOBRE EL PAGO DE LA COBERTURA", recomendacion)
        ]

        for title, content in remaining_sections:
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

        # Función unificada para header y footer
        def header_footer(canvas, doc):
            canvas.saveState()

            # Header - más arriba en la página
            canvas.setFont('Helvetica-Bold', 10)
            # INFORME DE INVESTIGACIÓN - alineado a la derecha
            canvas.drawRightString(7.5*inch, 10.5*inch, "INFORME DE INVESTIGACIÓN")
            # RECLAMO: [número] - alineado a la derecha
            canvas.drawRightString(7.5*inch, 10.3*inch, f"RECLAMO: {reclamo_num}")

            # Footer - numeración de páginas alineada a la derecha
            canvas.setFont('Helvetica', 8)
            page_num = canvas.getPageNumber()
            page_text = f"Pág. {page_num}"
            canvas.drawRightString(7.5*inch, 0.75*inch, page_text)

            canvas.restoreState()

        # Crear template de página personalizado para header/footer
        def create_page_template():
            frame = Frame(inch, inch, 6.5*inch, 9*inch)  # left, bottom, width, height
            template = PageTemplate(id='custom', frames=[frame], onPage=header_footer)
            return template

        # Generar PDF con CustomDocTemplate para mejor control de headers/footers
        doc = CustomDocTemplate(filename_pdf, pagesize=letter, pageTemplates=[create_page_template()])

        doc.build(story)

        # Firmar digitalmente el PDF
        try:
            if os.path.exists('maria_susana_espinosa_lozada.p12'):
                with open(filename_pdf, 'rb') as f:
                    data = f.read()
                dct = {
                    "sigflags": 3,
                    "contact": email,
                    "location": "Quito, Ecuador",
                    "signingdate": datetime.datetime.now().strftime("D:%Y%m%d%H%M%S+00'00'"),
                    "reason": "Firma del Informe de Investigación de Siniestro",
                }
                with open('maria_susana_espinosa_lozada.p12', 'rb') as f:
                    p12 = f.read()
                # Nota: Reemplaza 'password' con la contraseña real del certificado
                data_signed = pdf.cms.sign(data, dct, p12, 'password', 'sha256', fname=filename_pdf)
                # Escribir el PDF firmado de vuelta
                with open(filename_pdf, 'wb') as f:
                    f.write(data_signed)
                st.success("PDF firmado digitalmente exitosamente.")
            else:
                st.warning("Archivo de certificado 'maria_susana_espinosa_lozada.p12' no encontrado. El PDF no se firmará digitalmente.")
        except Exception as e:
            st.warning(f"No se pudo firmar digitalmente el PDF: {e}")

        # Leer el PDF para descarga
        with open(filename_pdf, "rb") as pdf_file:
            pdf_data = pdf_file.read()

        st.success("Informe generado exitosamente!")

        # Botón de descarga del PDF
        st.download_button(
            label="Descargar Informe en PDF",
            data=pdf_data,
            file_name=f"{reclamo_num}.pdf",
            mime="application/pdf"
        )

        # Guardar archivos subidos
        if uploaded_files:
            for uploaded_file in uploaded_files:
                with open(os.path.join('informes', f"{reclamo_num}_{uploaded_file.name}"), "wb") as f:
                    f.write(uploaded_file.getbuffer())
            st.success("Archivos de evidencias subidos y guardados.")

# Botones para añadir más relatos (fuera del formulario)
st.header("Añadir Más Relatos")
col1, col2, col3 = st.columns(3)

with col1:
    if st.button("Añadir Otro Relato del Asegurado (Azul)", help="Añade un nuevo relato del asegurado"):
        st.session_state.num_relatos_aseg += 1
        st.rerun()

with col2:
    if st.button("Añadir Otra Descripción de Inspección (Verde)", help="Añade una nueva descripción de inspección"):
        st.session_state.num_relatos_inspec += 1
        st.rerun()

with col3:
    if st.button("Añadir Otro Relato de Testigo (Rojo)", help="Añade un nuevo relato de testigo"):
        st.session_state.num_relatos_testigos += 1
        st.rerun()
