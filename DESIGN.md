# 🎨 **Guía de Diseño - Siniestros**

## **Paleta de Colores Corporativa**

### **Colores Primarios**
```css
--color-negro-corporativo: #0f172a;  /* Azul oscuro corporativo */
--color-rojo-acento: #dc2626;         /* Rojo para acciones importantes */
--color-gris-texto: #475569;          /* Gris para texto principal */
--color-gris-borde: #e2e8f0;          /* Gris claro para bordes */
```

### **Colores Secundarios**
```css
--color-blanco-puro: #ffffff;         /* Blanco puro */
--color-negro-hover: #1e293b;        /* Hover para elementos oscuros */
--color-rojo-hover: #b91c1c;          /* Hover para botones rojos */
--color-gris-hover: #64748b;         /* Hover para elementos grises */
```

### **Colores de Secciones**
```css
/* Información Básica */
background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%);

/* Parametrización */
background: linear-gradient(135deg, #fff3cd 0%, #ffeaa7 100%);

/* Entidades Relacionadas */
background: linear-gradient(135deg, #f0f9ff 0%, #bae6fd 100%);

/* Investigación */
background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%);
```

## **Espaciado y Tipografía**

### **Sistema de Espaciado (Base 4px)**
```css
--spacing-xs: 0.25rem;   /* 4px */
--spacing-sm: 0.5rem;    /* 8px */
--spacing-md: 0.75rem;   /* 12px */
--spacing-lg: 1rem;      /* 16px */
--spacing-xl: 1.25rem;   /* 20px */
--spacing-2xl: 1.5rem;   /* 24px */
```

### **Tipografía**
- **Familia**: `-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif`
- **Pesos**: 400 (normal), 500 (medium), 600 (semibold), 700 (bold)
- **Tamaños**:
  - `font-size: 12px` - Texto pequeño (etiquetas)
  - `font-size: 14px` - Texto regular (descripciones)
  - `font-size: 16px` - Texto principal (inputs)
  - `font-size: 18px` - Títulos de sección
  - `font-size: 24px` - Título principal

## **Componentes de UI**

### **1. Radio Buttons Personalizados**
```css
.person-type-selector {
  display: flex;
  gap: 16px;
  margin-bottom: 20px;
}

.person-type-card {
  flex: 1;
  padding: 12px 16px;
  border: 2px solid #e2e8f0;
  border-radius: 4px;
  background: white;
  cursor: pointer;
  transition: all 0.3s ease;
  font-weight: 500;
  min-height: 48px;
}

.person-type-radio:checked + .person-type-card {
  border-color: #dc2626;
  background: rgba(220, 38, 38, 0.1);
  color: #0f172a;
  font-weight: 600;
}
```

### **2. Checkboxes Estilizados**
```css
.checkbox-group {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 12px;
}

.checkbox-input {
  width: 18px;
  height: 18px;
  accent-color: #dc2626;
}

.checkbox-label-text {
  font-weight: 500;
  color: #0f172a;
  cursor: pointer;
}
```

### **3. Tarjetas de Sección**
```css
.card-section {
  background: white;
  border-radius: 8px;
  padding: 20px;
  margin-bottom: 20px;
  border: 1px solid #e2e8f0;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.card-header {
  display: flex;
  align-items: center;
  margin-bottom: 16px;
  padding-bottom: 12px;
  border-bottom: 2px solid #f1f5f9;
}
```

## **Pautas de UX/UI**

### **Jerarquía Visual**
1. **Títulos principales**: `font-size: 24px, font-weight: 600`
2. **Títulos de sección**: `font-size: 18px, font-weight: 600`
3. **Etiquetas de campo**: `font-size: 14px, font-weight: 500`
4. **Texto descriptivo**: `font-size: 14px, color: #475569`

### **Estados Interactivos**
- **Hover**: `opacity: 0.8`, cambio de color sutil
- **Focus**: `border-color: #dc2626`, `box-shadow: rgba(220, 38, 38, 0.25)`
- **Active**: `transform: scale(0.98)` para botones
- **Disabled**: `opacity: 0.5`, `cursor: not-allowed`

### **Animaciones y Transiciones**
- **Duración**: `0.3s ease` para la mayoría de transiciones
- **Propiedades**: `color, background-color, border-color, transform`
- **Efectos**: Hover states, tab switching, form validation

## **Sistema de Íconos**

### **Categorías Principales**
- 📋 **Información**: Documentos, datos, formularios
- ⚙️ **Configuración**: Ajustes, parametrización, opciones
- 👥 **Personas**: Usuarios, entidades, relaciones
- 🔍 **Búsqueda**: Investigación, inspección, análisis
- ✅ **Acciones**: Agregar, guardar, confirmar
- ❌ **Eliminar**: Quitar, cancelar, borrar

### **Uso Consistente**
- **Tamaño**: 16px para texto, 20px para botones, 24px para headers
- **Color**: Heredado del contexto, con énfasis en estados activos
- **Posicionamiento**: Alineado con texto, espaciado consistente

## **Responsive Design**

### **Breakpoints**
```css
/* Móvil */
@media (max-width: 480px) {
  .form-container { padding: 16px; }
  .form-row { flex-direction: column; }
}

/* Tablet */
@media (max-width: 768px) {
  .tabs-header { flex-wrap: wrap; }
  .person-type-selector { flex-direction: column; }
}

/* Desktop */
@media (min-width: 769px) {
  .form-container { max-width: 800px; margin: 0 auto; }
}
```

### **Layout Adaptativo**
- **Móvil**: Campos apilados, navegación simplificada
- **Tablet**: 2 columnas en algunos layouts
- **Desktop**: Layout completo con todas las optimizaciones

## **Accesibilidad**

### **Consideraciones WCAG 2.1**
- **Contraste**: Mínimo 4.5:1 para texto normal
- **Enfoque**: Indicadores visuales claros para navegación por teclado
- **Etiquetas**: Todos los inputs tienen labels asociados
- **Semántica**: Uso correcto de elementos HTML5

### **Navegación por Teclado**
- **Tab order**: Lógico y predecible
- **Enter/Escape**: Confirmar/cancelar acciones
- **Arrow keys**: Navegación en grupos de radio buttons

## **Patrones de Interacción**

### **Formularios Progresivos**
1. **Paso 1**: Información básica (requerida)
2. **Paso 2**: Configuración específica (opcional)
3. **Paso 3**: Entidades relacionadas (condicional)
4. **Paso 4**: Investigación completa (dinámica)

### **Estados de Validación**
- **Éxito**: Verde (#059669), ícono de check
- **Error**: Rojo (#dc2626), mensaje descriptivo
- **Advertencia**: Amarillo (#d97706), sugerencias
- **Info**: Azul (#2563eb), información adicional

### **Feedback Visual**
- **Loading states**: Spinners o skeletons
- **Success animations**: Checkmarks con fade-in
- **Error handling**: Mensajes contextuales
- **Progress indicators**: Barras o steps visuales

## **Implementación Técnica**

### **CSS Architecture**
```css
/* Variables globales */
:root { /* Colores, espaciado, tipografía */ }

/* Componentes base */
.form-container, .card-section, .tab-button { /* Estilos base */ }

/* Estados interactivos */
:hover, :focus, :active, :disabled { /* Estados dinámicos */ }

/* Responsive */
@media (max-width: 768px) { /* Adaptaciones móviles */ }
```

### **Component Structure**
```jsx
// Layout consistente
<div className="form-container">
  <header>...</header>
  <nav>...</nav>
  <main>...</main>
  <footer>...</footer>
</div>
```

Esta guía asegura consistencia visual y experiencia de usuario coherente en toda la aplicación Siniestros.
