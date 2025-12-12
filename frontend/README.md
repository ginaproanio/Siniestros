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
- ✅ Formulario responsive para crear siniestros
- ✅ Validación de campos
- ✅ Conexión con API backend
- ✅ Estados de carga y mensajes de error
- ✅ Diseño moderno y accesible
