# 🔥 **ESTRATEGIA DEFINITIVA: RESET COMPLETO DE BASE DE DATOS**

## ❗ **DECISIÓN ARQUITECTÓNICA DEFINITIVA**

- ❗ **La base de datos NO contiene datos valiosos**
- ❗ **Se puede borrar completamente cuantas veces sea necesario**
- ❗ **NO queremos migraciones incrementales**

---

## 🚫 **PROHIBIDO**

* NO usar Alembic / Django migrations / Prisma migrate / TypeORM migrations
* NO intentar "arreglar" migraciones existentes
* NO asumir continuidad del esquema anterior

---

## ✅ **ESTRATEGIA OBLIGATORIA**

1️⃣ El esquema de base de datos es **declarativo y fuente única de verdad**

2️⃣ En cada deploy:
   * Si el esquema cambió:
     * **BORRAR COMPLETAMENTE la base de datos**
     * **RECREAR TODAS LAS TABLAS DESDE CERO**

3️⃣ El arranque del backend debe:
   * Detectar inconsistencia de esquema
   * Ejecutar automáticamente:
   ```text
   DROP ALL TABLES
   CREATE ALL TABLES
   ```

4️⃣ No debe existir historial de migraciones

---

## 🧠 **OBJETIVO**

* Evitar conflictos de migraciones
* Evitar estados intermedios corruptos
* Garantizar que el backend SIEMPRE arranca

Este es un **entorno de desarrollo activo**, no producción.

---

## 📋 **PROCESO PASO A PASO PARA AGREGAR NUEVOS CAMPOS**

### **1️⃣ AGREGAR CAMPO AL MODELO (Backend)**
**Archivo:** `backend/app/models/siniestro.py`

```python
# Ejemplo: Agregar campo "fecha_reportado"
fecha_reportado = Column(DateTime, nullable=True)
```

### **2️⃣ AGREGAR CAMPO AL SCHEMA (Backend)**
**Archivo:** `backend/app/schemas/siniestro.py`

```python
# En SiniestroBase
fecha_reportado: Optional[datetime] = None

# En SiniestroUpdate (si es editable)
fecha_reportado: Optional[datetime] = None
```

### **3️⃣ ACTUALIZAR INTERFAZ TYPESCRIPT (Frontend)**
**Archivo:** `frontend/src/components/SiniestroForm.tsx` o `SiniestroEdit.tsx`

```typescript
interface FormData {
  // Agregar el nuevo campo
  fecha_reportado?: string;
  // ... otros campos
}
```

### **4️⃣ AGREGAR CAMPO AL FORMULARIO HTML (Frontend)**
**Ubicación:** Dentro del `<form>` en el componente

```jsx
<div className="form-row">
  <div className="form-group">
    <label>Fecha Reportado:</label>
    <input
      type="date"
      name="fecha_reportado"
      value={formData.fecha_reportado}
      onChange={handleInputChange}
    />
  </div>
</div>
```

### **5️⃣ ACTUALIZAR DATOS DE PRUEBA**
**Archivo:** `backend/create_test_data.py`

```python
siniestro = models.Siniestro(
    # Agregar el campo con valor de prueba
    fecha_reportado="2025-11-30T10:49:00",
    # ... otros campos
)
```

### **6️⃣ HACER COMMIT Y PUSH**
```bash
git add .
git commit -m "Add new field: fecha_reportado for siniestro reporting date"
git push origin main
```
**Railway redeploy automáticamente y ejecuta reset completo de BD**

## 🎯 **EJEMPLOS DE CAMPOS RECIENTEMENTE AGREGADOS**

### **✅ Fecha Reportado**
- **Propósito:** Fecha en que se reportó el siniestro
- **Tipo:** `DateTime` nullable
- **Uso:** Aparece en el informe de investigación

### **✅ Cobertura**
- **Propósito:** Tipo de cobertura del seguro
- **Tipo:** `String(100)` nullable
- **Uso:** Ej: "Todo riesgo", "Terceros", etc.

### **✅ Campos de Declaración del Siniestro**
- **fecha_declaracion:** Fecha de la declaración
- **persona_declara_tipo:** "asegurado" | "conductor" | "otro"
- **persona_declara_cedula:** Cédula de quien declara
- **persona_declara_nombre:** Nombre completo
- **persona_declara_relacion:** Relación con el siniestro

### **✅ Misiva de Investigación**
- **Propósito:** Solicitud específica de la aseguradora
- **Tipo:** `Text` nullable
- **Nota:** No se muestra en el PDF del informe

## 🔄 **FLUJO DE DESARROLLO DEPLOY-DRIVEN**

```
1. Backend Model → 2. Backend Schema → 3. Frontend Types →
4. Frontend Form → 5. Test Data → 6. Commit → 7. Push →
8. Railway Redeploy → 9. Reset BD Automático → 10. ✅ Listo
```

## ⚠️ **NOTAS IMPORTANTES**

- **Base de datos se recrea automáticamente** en cada deploy
- **NO hay migraciones Alembic** - evitamos problemas de compatibilidad
- **Campos nuevos son opcionales** por defecto para compatibilidad
- **Railway redeploy automáticamente** después de push
- **Reset completo es automático** y no requiere intervención manual

## 📝 **REGISTRO DE CAMBIOS RECIENTES**

| Fecha | Campo Agregado | Propósito | Estado |
|-------|---------------|-----------|---------|
| 2025-12-13 | `fecha_reportado` | Fecha de reporte del siniestro | ✅ Implementado |
| 2025-12-13 | `cobertura` | Tipo de cobertura del seguro | ✅ Implementado |
| 2025-12-13 | `fecha_declaracion` | Fecha de declaración | ✅ Implementado |
| 2025-12-13 | `persona_declara_*` | Información de quien declara | ✅ Implementado |
| 2025-12-13 | `misiva_investigacion` | Solicitud de aseguradora | ✅ Implementado |

---

**Esta estrategia garantiza desarrollo ágil sin problemas de migraciones.** 🚀
