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

## 🎯 **PARAMETRIZACIÓN COMPLETA: FORMULARIO "REGISTRO DE SINIESTRO"**

### **🔧 QUÉ ES LA PARAMETRIZACIÓN**

**TODO el formulario "Registro de Siniestro" ES LA PARAMETRIZACIÓN.** No hay separación entre "parametrización" y "registro" - el formulario mismo permite configurar y adaptar cada investigación según los requerimientos específicos de la aseguradora.

### **📋 CAMPOS DE PARAMETRIZACIÓN (FORMULARIO COMPLETO)**

#### **1️⃣ DATOS BÁSICOS DEL SINIESTRO**
- `compania_seguros`: Compañía aseguradora
- `reclamo_num`: Número de reclamo
- `fecha_siniestro`: Fecha del accidente
- `fecha_reportado`: Fecha de reporte del siniestro ⭐ **(Campo parametrizable)**
- `direccion_siniestro`: Ubicación del siniestro
- `ubicacion_geo_lat/lng`: Coordenadas GPS
- `danos_terceros`: Boolean - Si hay daños a terceros
- `ejecutivo_cargo`: Ejecutivo asignado
- `fecha_designacion`: Fecha de asignación del ejecutivo
- `tipo_siniestro`: Tipo de siniestro ⭐ **(Campo parametrizable)**
- `cobertura`: Tipo de cobertura del seguro ⭐ **(Campo parametrizable)**

#### **2️⃣ MISIVA DE INVESTIGACIÓN (Campo Parametrizable)**
Campo que contiene las **instrucciones específicas** de la aseguradora para esta investigación particular:
- `misiva_investigacion`: Texto de la solicitud específica de la aseguradora ⭐ **(Campo parametrizable)**
- **Nota:** Campo de texto largo para instrucciones particulares
- **Nota:** NO se incluye en el PDF del informe final

#### **3️⃣ DECLARACIÓN DEL SINIESTRO (Campos Parametrizables)**
Campos que varían según quién realiza la declaración y el contexto del siniestro:
- `fecha_reportado`: Fecha de reporte del siniestro (equivale a fecha de declaración) ⭐ **(Campo parametrizable)**
- `persona_declara_tipo`: Tipo de persona ("asegurado" | "conductor" | "otro") ⭐ **(Campo parametrizable)**
- `persona_declara_cedula`: Cédula de identidad ⭐ **(Campo parametrizable)**
- `persona_declara_nombre`: Nombre completo ⭐ **(Campo parametrizable)**
- `persona_declara_relacion`: Relación con el **asegurado** ⭐ **(Campo parametrizable)**

#### **4️⃣ ENTIDADES RELACIONADAS (Campos Dinámicos)**
- **ASEGURADO**: Datos del asegurado (cedula, nombre, direccion, telefono, email)
- **BENEFICIARIO**: Datos del beneficiario (cedula, nombre, relacion)
- **CONDUCTOR**: Datos del conductor (cedula, nombre, licencia, direccion, telefono)
- **OBJETO ASEGURADO**: Datos del vehículo (tipo, marca, modelo, anio, placa, color, chasis, motor)

#### **5️⃣ INVESTIGACIÓN (Datos Recopilados - Campos Dinámicos)**
- **ANTECEDENTES**: Descripción del aviso de siniestro y alcances
- **RELATOS DEL ASEGURADO**: Entrevistas con el asegurado
- **INSPECCIONES**: Hallazgos del lugar del siniestro
- **TESTIGOS**: Declaraciones de testigos
- **VISITAS TALLER**: Inspecciones técnicas
- **DINÁMICAS DEL ACCIDENTE**: Análisis del accidente

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
