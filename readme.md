# Sistema de Informes de Siniestros
Aplicación web en Streamlit para generar informes profesionales de investigaciones de siniestros en seguros. Utiliza ReportLab para crear PDFs con diseño corporativo, incluyendo mapas integrados y headers/footers automáticos.

**Repositorio**: https://github.com/ginaproanio/Siniestros  
**Rama**: main

## Instalación Local
1. Instala Python 3.8 o superior desde python.org.
2. Instala las dependencias:
   ```bash
   pip install -r requirements.txt
   ```
3. Ejecuta la aplicación:
   ```bash
   streamlit run app_informes.py
   ```
   Se abrirá en http://localhost:8501.

## Despliegue en Railway
1. Sube este proyecto a un repositorio Git (GitHub, GitLab, etc.).
2. Conecta el repositorio a Railway.app.
3. Railway detectará automáticamente el Procfile y requirements.txt para desplegar la app.
4. La app estará disponible en la URL proporcionada por Railway.

**Nota**: Los archivos subidos e informes se guardan localmente en la carpeta 'informes'. En Railway, estos son temporales; considera integrar almacenamiento en la nube (AWS S3, etc.) para persistencia.

## Funcionalidades
- **Formulario estructurado**: Recolección completa de datos del siniestro, asegurado, conductor, vehículo y terceros afectados.
- **Generación de PDFs profesionales**: Utiliza ReportLab para crear PDFs con:
  - Diseño corporativo con tablas estructuradas
  - Mapas integrados generados con Folium
  - Headers con nombre de compañía y fecha
  - Footers con numeración de páginas y confidencialidad
  - Tipografía formal (Helvetica)
- **Vista previa en texto**: Permite revisar el contenido antes de generar el PDF.
- **Upload de evidencias**: Subida de fotos y documentos complementarios.
- **Archivos de respaldo**: Genera informes en formato TXT además del PDF.

## Arquitectura Técnica
- **Frontend**: Streamlit para interfaz web
- **Generación de PDFs**: ReportLab con diseño profesional, tablas estructuradas, headers/footers automáticos
- **Mapas**: Folium para generación de mapas estáticos integrados en PDF
- **Almacenamiento**: Sistema de archivos local (carpeta `informes/`)

## Requisitos del Sistema
- Python 3.8+
- Dependencias listadas en `requirements.txt`:
  - streamlit
  - reportlab
  - folium
  - staticmap
  - pillow
  - requests
