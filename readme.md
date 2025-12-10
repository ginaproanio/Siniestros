# Sistema de Informes de Siniestros
App en Streamlit para generar informes automáticos de investigaciones de siniestros en seguros.

## Instalación Local
1. Instala Python 3.8 o superior desde python.org.
2. Instala las dependencias:
   ```
   pip install -r requirements.txt
   ```
3. Ejecuta la app:
   ```
   streamlit run app_informes.py
   ```
   Se abrirá en http://localhost:8501.

## Despliegue en Railway
1. Sube este proyecto a un repositorio Git (GitHub, GitLab, etc.).
2. Conecta el repositorio a Railway.app.
3. Railway detectará automáticamente el Procfile y requirements.txt para desplegar la app.
4. La app estará disponible en la URL proporcionada por Railway (ej: siniestros-production.up.railway.app).

Nota: Los archivos subidos y informes se guardan localmente en la carpeta 'informes'. En Railway, estos son temporales; considera integrar almacenamiento en la nube (AWS S3, etc.) para persistencia.

## Funcionalidades
- Formulario estructurado para recolectar datos del siniestro.
- Generación automática de informes en TXT y PDF.
- Upload de evidencias (fotos, documentos).
- Vista previa del informe antes de guardar.
