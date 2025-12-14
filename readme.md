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

## 🎯 **PARAMETRIZACIÓN COMPLETA DEL FORMULARIO**

### **📋 SECCIONES DEL FORMULARIO COMPLETO**

#### **1️⃣ DATOS DEL SINIESTRO (Campos Base)**
- `compania_seguros`: Compañía aseguradora
- `reclamo_num`: Número de reclamo
- `fecha_siniestro`: Fecha del accidente
- `fecha_reportado`: Fecha de reporte del siniestro
- `direccion_siniestro`: Ubicación del siniestro
- `ubicacion_geo_lat/lng`: Coordenadas GPS
- `danos_terceros`: Boolean - Si hay daños a terceros
- `ejecutivo_cargo`: Ejecutivo asignado
- `fecha_designacion`: Fecha de asignación del ejecutivo
- `tipo_siniestro`: Tipo de siniestro
- `cobertura`: Tipo de cobertura del seguro

#### **2️⃣ DECLARACIÓN DEL SINIESTRO (Parametrización)**
- `fecha_declaracion`: Fecha de la declaración
- `persona_declara_tipo`: Tipo de persona ("asegurado" | "conductor" | "otro")
- `persona_declara_cedula`: Cédula de identidad
- `persona_declara_nombre`: Nombre completo
- `persona_declara_relacion`: Relación con el siniestro

#### **3️⃣ MISIVA DE INVESTIGACIÓN (Parametrización)**
- `misiva_investigacion`: Texto de la solicitud específica de la aseguradora
- **Nota:** Campo de texto largo para instrucciones particulares
- **Nota:** NO se incluye en el PDF del informe final

#### **4️⃣ ASEGURADO (Entidad Relacionada)**
- `asegurado.cedula`: Cédula del asegurado
- `asegurado.nombre`: Nombre completo
- `asegurado.direccion`: Dirección
- `asegurado.telefono`: Teléfono
- `asegurado.email`: Correo electrónico

#### **5️⃣ BENEFICIARIO (Entidad Relacionada)**
- `beneficiario.cedula`: Cédula del beneficiario
- `beneficiario.nombre`: Nombre completo
- `beneficiario.relacion`: Relación con el asegurado

#### **6️⃣ CONDUCTOR (Entidad Relacionada)**
- `conductor.cedula`: Cédula del conductor
- `conductor.nombre`: Nombre completo
- `conductor.licencia`: Número de licencia
- `conductor.direccion`: Dirección
- `conductor.telefono`: Teléfono

#### **7️⃣ OBJETO ASEGURADO (Entidad Relacionada)**
- `objeto_asegurado.tipo`: Tipo de vehículo/objeto
- `objeto_asegurado.marca`: Marca
- `objeto_asegurado.modelo`: Modelo
- `objeto_asegurado.anio`: Año
- `objeto_asegurado.placa`: Placa/patente
- `objeto_asegurado.color`: Color
- `objeto_asegurado.chasis`: Número de chasis
- `objeto_asegurado.motor`: Número de motor

#### **8️⃣ ANTECEDENTES (Lista Dinámica)**
- `antecedentes[].descripcion`: Descripción de antecedentes

#### **9️⃣ RELATOS DEL ASEGURADO (Lista Dinámica)**
- `relatos_asegurado[].numero_relato`: Número secuencial
- `relatos_asegurado[].texto`: Texto del relato
- `relatos_asegurado[].imagen_url`: URL de imagen opcional

#### **🔟 INSPECCIONES (Lista Dinámica)**
- `inspecciones[].numero_inspeccion`: Número secuencial
- `inspecciones[].descripcion`: Descripción de hallazgos
- `inspecciones[].imagen_url`: URL de imagen opcional

#### **1️⃣1️⃣ TESTIGOS (Lista Dinámica)**
- `testigos[].numero_relato`: Número secuencial
- `testigos[].texto`: Declaración del testigo
- `testigos[].imagen_url`: URL de imagen opcional

#### **1️⃣2️⃣ VISITAS TALLER (Lista Dinámica)**
- `visitas_taller[].fecha_visita`: Fecha de la visita
- `visitas_taller[].descripcion`: Descripción de la visita
- `visitas_taller[].imagen_url`: URL de imagen opcional

#### **1️⃣3️⃣ DINÁMICAS DEL ACCIDENTE (Lista Dinámica)**
- `dinamicas_accidente[].descripcion`: Descripción de la dinámica
- `dinamicas_accidente[].imagen_url`: URL de imagen opcional

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
