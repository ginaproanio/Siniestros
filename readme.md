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
- **Sección Asegurado Dinámica**: Permite seleccionar entre Persona Natural o Persona Jurídica, mostrando campos específicos:
  - Persona Natural: Cédula, Celular, Dirección, Parentesco
  - Persona Jurídica: RUC, Empresa, Representante Legal, Dirección, Teléfono
- **Entrevista con el Conductor**: Permite registrar múltiples relatos dinámicamente, cada uno con texto opcional y imagen adjunta. Incluye acciones por relato: Buscar, Grabar, Añadir Otro.
- **Orden de Secciones**: ANTECEDENTES antes de TERCEROS AFECTADOS.
- **Generación de PDFs profesionales**: Utiliza ReportLab para crear PDFs con:
  - Diseño corporativo con tablas estructuradas
  - Mapas integrados generados con StaticMap
  - Headers con nombre de compañía y fecha
  - Footers con numeración de páginas
  - Relatos con imágenes dispuestas lado a lado cuando aplicable
  - Tipografía formal (Helvetica)
- **Vista previa en texto**: Permite revisar el contenido antes de generar el PDF.
- **Upload de evidencias**: Subida de fotos y documentos complementarios.
- **Archivos de respaldo**: Genera informes en formato TXT además del PDF.
- **Firma digital**: Soporte para firma digital de PDFs usando certificado P12.

## Arquitectura Técnica
- **Frontend**: Streamlit para interfaz web con formularios dinámicos y manejo de estado de sesión
- **Generación de PDFs**: ReportLab con diseño profesional, tablas estructuradas, headers/footers automáticos, y disposición inteligente de imágenes y texto
- **Mapas**: StaticMap para generación de mapas estáticos integrados en PDF
- **Firma Digital**: Endesive para firma digital de PDFs
- **Almacenamiento**: Sistema de archivos local (carpeta `informes/`)

## Limitaciones y Recomendaciones Arquitectónicas
Esta implementación inicial utiliza Streamlit como framework principal, pero presenta limitaciones significativas para formularios complejos y dinámicos:

### Limitaciones Identificadas
1. **Restricciones de st.form()**:
   - No permite botones interactivos (st.button) dentro del formulario. Solo st.form_submit_button() para envío completo.
   - Los botones para añadir elementos dinámicos (relatos, descripciones) deben estar FUERA del formulario, causando UX pobre en formularios largos.
   - Errores "DuplicateWidgetID" si se duplican estructuras de widgets.

2. **Manejo de Estado de Sesión**:
   - Estado limitado para elementos dinámicos; requiere recargas de página (st.rerun()).
   - No persiste datos entre sesiones sin base de datos.

3. **Escalabilidad y Rendimiento**:
   - Formularios largos causan scrolling excesivo y UX deficiente.
   - Generación de PDFs complejos puede ser lenta en entornos serverless como Railway.

4. **Almacenamiento**:
   - Archivos temporales en Railway; se pierden al redeploy.
   - No hay persistencia de datos ni historial de informes.

### Recomendaciones para Mejora Arquitectónica
Para un sistema de informes de siniestros más robusto y escalable, se recomienda migrar a una arquitectura full-stack:

1. **Backend con Base de Datos**:
   - **API REST/GraphQL**: FastAPI o Django REST Framework para lógica de negocio.
   - **Base de Datos**: PostgreSQL o MongoDB para persistencia de informes, usuarios y archivos.
   - **Autenticación**: JWT o OAuth para usuarios múltiples.

2. **Frontend Mejorado**:
   - **React/Vue.js**: Para formularios dinámicos avanzados sin limitaciones de widgets.
   - **Componentes Reutilizables**: Para secciones de relatos con botones internos.
   - **Estado Global**: Redux o Context API para manejo complejo de estado.

3. **Almacenamiento en la Nube**:
   - **AWS S3 / Google Cloud Storage**: Para archivos permanentes.
   - **CDN**: Para distribución de PDFs generados.

4. **Microservicios**:
   - **Servicio de PDFs**: Separado para generación asíncrona.
   - **Servicio de Mapas**: Para mapas dinámicos.
   - **Servicio de Firma Digital**: Integración con servicios de certificación.

5. **Despliegue**:
   - **Docker/Kubernetes**: Para escalabilidad.
   - **CI/CD**: Pipelines automatizados con GitHub Actions.

### Próximos Pasos Sugeridos
- Evaluar migración a React + FastAPI para superar limitaciones de Streamlit.
- Implementar base de datos para persistencia y consultas.
- Desarrollar API para integración con sistemas de seguros existentes.
- Considerar autenticación multi-usuario para equipos de investigación.

Esta versión actual es funcional para prototipado rápido, pero no escalable para producción con múltiples usuarios e informes complejos.

## Requisitos del Sistema
- Python 3.8+
- Dependencias listadas en `requirements.txt`:
  - streamlit
  - reportlab
  - staticmap
  - pillow
  - endesive
  - requests
