import streamlit as st
import datetime
import os
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

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
    reclamo_num = st.text_input("Reclamo #", placeholder="Ej: 25-01-VH-7079448")
    fecha_siniestro = st.date_input("Fecha del Siniestro")
    direccion_siniestro = st.text_input("Dirección del Siniestro")
    ubicacion_geo = st.text_input("Ubicación Georreferenciada")
    danos_terceros = st.text_input("Daños a Terceros")
    ejecutivo_cargo = st.text_input("Ejecutivo a Cargo")
    fecha_designacion = st.date_input("Fecha de Designación")

    # Sección: ASEGURADO
    st.header("Asegurado")
    razon_social = st.text_input("Razón Social")
    cedula_ruc_aseg = st.text_input("Cédula / RUC")
    domicilio_aseg = st.text_input("Domicilio")

    # Sección: CONDUCTOR
    st.header("Conductor")
    nombre_conductor = st.text_input("Nombre", key="nombre_conductor")
    cedula_conductor = st.text_input("Cédula", key="cedula_conductor")
    celular_conductor = st.text_input("Celular", key="celular_conductor")
    direccion_conductor = st.text_input("Dirección", key="direccion_conductor")
    parentesco = st.text_input("Parentesco", key="parentesco_conductor")

    # Sección: OBJETO ASEGURADO
    st.header("Objeto Asegurado")
    placa_aseg = st.text_input("Placa")
    marca_aseg = st.text_input("Marca")
    modelo_aseg = st.text_input("Modelo")
    color_aseg = st.text_input("Color")
    ano_aseg = st.number_input("Año", min_value=1900, max_value=2100)
    motor_aseg = st.text_input("Motor")
    chasis_aseg = st.text_input("Chasis")

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
    antecedentes = st.text_area("Antecedentes", height=150)
    entrevista_conductor = st.text_area("Entrevista con el Conductor", height=200)
    visita_taller = st.text_area("Visita al Taller", height=150)
    inspeccion_lugar = st.text_area("Inspección del Lugar del Siniestro", height=150)
    evidencias_complementarias = st.text_area("Evidencias Complementarias", height=150)
    dinamica_accidente = st.text_area("Dinámica del Accidente", height=150)
    otras_diligencias = st.text_area("Otras Diligencias", height=100)
    observaciones = st.text_area("Observaciones (usa numeración si es lista)", height=150)
    conclusiones = st.text_area("Conclusiones (usa numeración si es lista)", height=150)
    recomendacion = st.text_area("Recomendación sobre el Pago de la Cobertura", height=150)

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
        
        # Opcional: Generar PDF
        filename_pdf = f"informes/informe_{reclamo_num}_{datetime.date.today()}.pdf"
        c = canvas.Canvas(filename_pdf, pagesize=letter)
        y = 750  # Posición inicial
        for line in informe_texto.split('\n'):
            c.drawString(50, y, line)
            y -= 15
            if y < 50:
                c.showPage()
                y = 750
        c.save()

        st.success(f"Informe generado y guardado en: {filename_txt} y {filename_pdf}")

        # Guardar archivos subidos
        if uploaded_files:
            for uploaded_file in uploaded_files:
                with open(os.path.join('informes', f"{reclamo_num}_{uploaded_file.name}"), "wb") as f:
                    f.write(uploaded_file.getbuffer())
            st.success("Archivos de evidencias subidos y guardados.")

        # Mostrar vista previa
        st.text_area("Vista Previa del Informe", informe_texto, height=400)
