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
