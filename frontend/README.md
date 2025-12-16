# Frontend - Sistema de Informes de Siniestros

Interfaz de usuario React para el sistema de informes de siniestros vehiculares.

## Tecnologías
- **React 18** con TypeScript
- **Axios** para comunicación con API
- **CSS moderno** para estilos responsive

## Desarrollo Local

### Prerrequisitos
- Node.js 18+ y npm
- Backend corriendo en `http://localhost:8000`

### Instalación
```bash
cd frontend
npm install
```

### Ejecución
```bash
npm start
```
Abre http://localhost:3000

### Construcción para producción
```bash
npm run build
```

## Configuración
- **API Base URL**: Configurada para producción en Railway
- **Proxy para desarrollo**: Apunta a `http://localhost:8000`

## Estructura
```
src/
├── components/     # Componentes React
│   └── SiniestroForm.tsx
├── App.tsx         # Componente principal
├── App.css         # Estilos globales
├── index.tsx       # Punto de entrada
└── index.css       # Estilos base
```

## Funcionalidades
- ✅ **Formulario responsive para crear siniestros** con interfaz por pestañas
- ✅ **Sistema CRUD completo** para todas las secciones de investigación:
  - Entrevista al Asegurado (múltiples relatos con imágenes)
  - Entrevista al Conductor (múltiples relatos con imágenes)
  - Inspección del Lugar (múltiples inspecciones con imágenes)
  - Testigos (múltiples declaraciones con imágenes)
  - Evidencias Complementarias (múltiples evidencias con imágenes)
  - Otras Diligencias (múltiples diligencias con imágenes)
  - Visita al Taller (múltiples visitas con imágenes)
  - Observaciones (múltiples observaciones)
  - Recomendación de Pago (múltiples recomendaciones)
  - Conclusiones (múltiples conclusiones)
  - Anexo (múltiples documentos adjuntos)
- ✅ Validación de campos
- ✅ Conexión con API backend
- ✅ Estados de carga y mensajes de error
- ✅ Subida de imágenes integrada
- ✅ Diseño moderno y accesible
