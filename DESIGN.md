# 🎨 Guía de Diseño - Sistema de Informes de Siniestros

## Identidad Visual Corporativa

### Colores Primarios

#### Negro Corporativo (Slate 900)
- **Uso**: Fondos oscuros, títulos principales, botones primarios
- **HEX**: `#0f172a`
- **RGB**: `15, 23, 42`
- **CMYK** (Aprox): `88, 76, 53, 66`

#### Rojo Acento (Red 600)
- **Uso**: Detalles, líneas decorativas, iconos destacados, botones de llamada a la acción
- **HEX**: `#dc2626`
- **RGB**: `220, 38, 38`
- **CMYK** (Aprox): `13, 96, 81, 3`

### Colores Secundarios (Textos y Bordes)

#### Gris Texto (Slate 600)
- **Uso**: Párrafos, descripciones, textos secundarios
- **HEX**: `#475569`
- **RGB**: `71, 85, 105`
- **CMYK** (Aprox): `64, 48, 36, 17`

#### Gris Borde (Slate 200)
- **Uso**: Líneas divisorias sutiles, bordes de tarjetas claras
- **HEX**: `#e2e8f0`
- **RGB**: `226, 232, 240`
- **CMYK** (Aprox): `9, 6, 6, 0`

#### Blanco Puro
- **Uso**: Fondos principales, textos sobre fondos oscuros
- **HEX**: `#ffffff`
- **RGB**: `255, 255, 255`
- **CMYK**: `0, 0, 0, 0`

## Paleta de Colores en Código

### CSS Variables Recomendadas

```css
:root {
  /* Colores Primarios */
  --color-negro-corporativo: #0f172a;
  --color-rojo-acento: #dc2626;

  /* Colores Secundarios */
  --color-gris-texto: #475569;
  --color-gris-borde: #e2e8f0;
  --color-blanco-puro: #ffffff;

  /* Variantes para interacción */
  --color-negro-hover: #1e293b;
  --color-rojo-hover: #b91c1c;
  --color-gris-hover: #64748b;
}
```

### Tailwind CSS (si se usa)

```javascript
// tailwind.config.js
module.exports = {
  theme: {
    extend: {
      colors: {
        'negro-corporativo': '#0f172a',
        'rojo-acento': '#dc2626',
        'gris-texto': '#475569',
        'gris-borde': '#e2e8f0',
      }
    }
  }
}
```

## Aplicación de Colores por Componente

### Navegación y Headers
- **Fondo**: Negro Corporativo (`#0f172a`)
- **Texto**: Blanco Puro (`#ffffff`)
- **Enlaces hover**: Rojo Acento (`#dc2626`)

### Botones
- **Primarios**: Negro Corporativo (`#0f172a`)
- **Secundarios**: Rojo Acento (`#dc2626`)
- **Hover**: Variantes más oscuras

### Formularios
- **Labels**: Gris Texto (`#475569`)
- **Bordes**: Gris Borde (`#e2e8f0`)
- **Focus**: Rojo Acento (`#dc2626`)

### Tarjetas y Contenedores
- **Bordes**: Gris Borde (`#e2e8f0`)
- **Headers**: Negro Corporativo (`#0f172a`)
- **Texto**: Gris Texto (`#475569`)

## Tipografía

### Familia Principal
- **Helvetica** (o **Arial** como fallback)
- **Pesos**: Regular (400), Bold (700)

### Jerarquía
- **Títulos principales (H1)**: 24px, Bold, Negro Corporativo
- **Subtítulos (H2/H3)**: 18px, Bold, Negro Corporativo
- **Texto normal**: 14px, Regular, Gris Texto
- **Texto pequeño**: 12px, Regular, Gris Texto

## Espaciado y Layout

### Sistema de Espaciado
- **Espaciado base**: 4px (0.25rem)
- **Escala**: 4, 8, 12, 16, 20, 24, 32, 40, 48, 64px

### Componentes
- **Padding interno**: 16px (1rem)
- **Márgenes entre secciones**: 24px (1.5rem)
- **Bordes redondeados**: 4px (0.25rem)

## Iconografía

### Estilo
- **Minimalista** y **funcional**
- **Stroke weight**: 2px
- **Color**: Gris Texto para estado normal, Rojo Acento para activo

### Conjunto Recomendado
- **Lucide React** o **Heroicons**
- Iconos consistentes en toda la aplicación

## Estados Interactivos

### Hover
- **Botones**: Oscurecer 10-15%
- **Enlaces**: Cambiar a Rojo Acento
- **Campos**: Resaltar borde con Rojo Acento

### Focus
- **Campos de formulario**: Borde Rojo Acento (2px)
- **Botones**: Outline Rojo Acento

### Loading/Disabled
- **Opacidad**: 60%
- **Cursor**: not-allowed
- **Color**: Gris Borde

## Responsive Design

### Breakpoints
- **Mobile**: < 640px
- **Tablet**: 640px - 1024px
- **Desktop**: > 1024px

### Layout Adaptativo
- **Mobile**: Columnas simples, navegación colapsable
- **Tablet/Desktop**: Layout de 2-3 columnas, navegación expandida

## Accesibilidad

### Contraste
- **Texto sobre fondo oscuro**: Mínimo 7:1
- **Texto sobre fondo claro**: Mínimo 4.5:1

### Navegación por Teclado
- **Focus visible** en todos los elementos interactivos
- **Tab order** lógico
- **Skip links** para navegación rápida

## Implementación Técnica

### CSS Framework Recomendado
- **Tailwind CSS** para desarrollo rápido
- **CSS Modules** para componentes específicos
- **CSS Variables** para temas

### Componentes Base
```typescript
// Ejemplo de componente Button
interface ButtonProps {
  variant: 'primary' | 'secondary';
  size: 'sm' | 'md' | 'lg';
  disabled?: boolean;
  children: React.ReactNode;
}
```

## Validación de Diseño

### Checklist Pre-deployment
- [ ] Colores aplicados consistentemente
- [ ] Contraste de texto suficiente
- [ ] Estados hover/focus implementados
- [ ] Diseño responsive probado
- [ ] Componentes accesibles

---

**Última actualización**: Diciembre 2025
**Versión**: 1.0
**Autor**: Equipo de Desarrollo
