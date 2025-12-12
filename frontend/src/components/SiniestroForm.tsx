import axios from "axios";
import React, { useState } from "react";

// Configurar base URL para el backend - cambiar cuando se cree el servicio separado
const BACKEND_URL =
  process.env.REACT_APP_BACKEND_URL ||
  "https://siniestros-production.up.railway.app";
axios.defaults.baseURL = BACKEND_URL;

// Interfaces para futuras expansiones del formulario
// interface AseguradoData { ... }
// interface ConductorData { ... }
// interface VehiculoData { ... }

interface RelatoData {
  numero_relato: number;
  texto: string;
  imagen_url?: string;
}

interface InspeccionData {
  numero_inspeccion: number;
  descripcion: string;
  imagen_url?: string;
}

interface TestigoData {
  numero_relato: number;
  texto: string;
  imagen_url?: string;
}

interface AntecedenteData {
  descripcion: string;
}

interface FormData {
  // Datos básicos del siniestro (según backend schema)
  compania_seguros: string;
  reclamo_num: string;
  fecha_siniestro: string;
  direccion_siniestro: string;
  ubicacion_geo_lat?: number;
  ubicacion_geo_lng?: number;
  danos_terceros: boolean;
  ejecutivo_cargo?: string;
  fecha_designacion?: string;
  tipo_siniestro?: string;

  // Secciones dinámicas
  antecedentes?: AntecedenteData[];
  relatos_asegurado?: RelatoData[];
  inspecciones?: InspeccionData[];
  testigos?: TestigoData[];
}

const SiniestroForm: React.FC = () => {
  const [formData, setFormData] = useState<FormData>({
    // Datos básicos según backend schema
    compania_seguros: "Zurich Seguros Ecuador S.A.",
    reclamo_num: "25-01-VH-7079448",
    fecha_siniestro: "2023-10-15",
    direccion_siniestro: "Av. Amazonas y Naciones Unidas, Quito",
    ubicacion_geo_lat: -0.1807,
    ubicacion_geo_lng: -78.4678,
    danos_terceros: true,
    ejecutivo_cargo: "Juan Pérez",
    fecha_designacion: "2025-12-11",
    tipo_siniestro: "Vehicular",
  });

  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState("");

  const handleInputChange = (
    e: React.ChangeEvent<
      HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement
    >
  ) => {
    const { name, value, type } = e.target;
    const checked = (e.target as HTMLInputElement).checked;

    setFormData((prev) => ({
      ...prev,
      [name]: type === "checkbox" ? checked : value,
    }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setMessage("");

    console.log("🚀 Enviando datos del formulario:", formData);
    console.log("🌐 URL de destino:", axios.defaults.baseURL + "/api/v1/");

    try {
      const response = await axios.post("/api/v1/", formData);
      console.log("✅ Respuesta del servidor:", response);
      console.log("📋 Datos de respuesta:", response.data);
      setMessage("Siniestro creado exitosamente!");
      // Redirect to list after 2 seconds
      setTimeout(() => {
        window.location.href = "/siniestros";
      }, 2000);
    } catch (error: any) {
      console.error("❌ Error completo:", error);
      console.error("❌ Respuesta del servidor:", error.response);
      console.error("❌ Datos del error:", error.response?.data);
      console.error("❌ Status del error:", error.response?.status);

      // Mostrar errores detallados en el formulario
      let errorMessage = "Error al crear el siniestro";

      if (error.response) {
        const status = error.response.status;
        const data = error.response.data;

        switch (status) {
          case 400:
            errorMessage = `Datos inválidos: ${
              data.detail || "Verifica los campos requeridos"
            }`;
            break;
          case 405:
            errorMessage = `Error 405: Método no permitido. URL: ${axios.defaults.baseURL}/api/v1/`;
            break;
          case 404:
            errorMessage = `Error 404: Endpoint no encontrado. Verifica la URL de la API`;
            break;
          case 500:
            errorMessage = `Error del servidor: ${
              data.detail || data.message || "Error interno"
            }`;
            break;
          default:
            errorMessage = `Error ${status}: ${
              data.detail || data.message || "Error desconocido"
            }`;
        }
      } else if (error.request) {
        errorMessage =
          "No se pudo conectar al servidor. Verifica tu conexión a internet.";
      } else {
        errorMessage = `Error de configuración: ${error.message}`;
      }

      setMessage(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="form-container">
      <h2>Registro de Siniestro</h2>
      <form onSubmit={handleSubmit}>
        <div className="form-row">
          <div className="form-group">
            <label>Compañía de Seguros:</label>
            <input
              type="text"
              name="compania_seguros"
              value={formData.compania_seguros}
              onChange={handleInputChange}
              required
            />
          </div>
          <div className="form-group">
            <label>Número de Reclamo:</label>
            <input
              type="text"
              name="reclamo_num"
              value={formData.reclamo_num}
              onChange={handleInputChange}
              required
            />
          </div>
        </div>

        <div className="form-row">
          <div className="form-group">
            <label>Fecha del Siniestro:</label>
            <input
              type="date"
              name="fecha_siniestro"
              value={formData.fecha_siniestro}
              onChange={handleInputChange}
              required
            />
          </div>
          <div className="form-group">
            <label>Fecha de Designación:</label>
            <input
              type="date"
              name="fecha_designacion"
              value={formData.fecha_designacion}
              onChange={handleInputChange}
            />
          </div>
        </div>

        <div className="form-group">
          <label>Dirección del Siniestro:</label>
          <textarea
            name="direccion_siniestro"
            value={formData.direccion_siniestro}
            onChange={handleInputChange}
            rows={2}
            required
          />
        </div>

        <div className="form-row">
          <div className="form-group">
            <label>Latitud:</label>
            <input
              type="number"
              step="0.0001"
              name="ubicacion_geo_lat"
              value={formData.ubicacion_geo_lat || ""}
              onChange={handleInputChange}
            />
          </div>
          <div className="form-group">
            <label>Longitud:</label>
            <input
              type="number"
              step="0.0001"
              name="ubicacion_geo_lng"
              value={formData.ubicacion_geo_lng || ""}
              onChange={handleInputChange}
            />
          </div>
        </div>

        <div className="form-row">
          <div className="form-group">
            <label>Ejecutivo a Cargo:</label>
            <input
              type="text"
              name="ejecutivo_cargo"
              value={formData.ejecutivo_cargo}
              onChange={handleInputChange}
            />
          </div>
          <div className="form-group">
            <label className="checkbox-label">
              <input
                type="checkbox"
                name="danos_terceros"
                checked={formData.danos_terceros}
                onChange={handleInputChange}
              />
              Daños a Terceros
            </label>
          </div>
        </div>

        {/* ANTECEDENTES */}
        <div style={{ marginBottom: '30px', padding: '20px', backgroundColor: '#f8f9fa', borderRadius: '8px' }}>
          <h3 style={{ color: '#0f172a', marginBottom: '15px' }}>📋 Antecedentes</h3>
          <div className="form-group">
            <label>Descripción de los antecedentes:</label>
            <textarea
              name="antecedentes_descripcion"
              value={(formData.antecedentes && formData.antecedentes[0]?.descripcion) || ""}
              onChange={(e) => {
                const value = e.target.value;
                setFormData((prev) => ({
                  ...prev,
                  antecedentes: [{ descripcion: value }]
                }));
              }}
              rows={4}
              placeholder="Describa el aviso de siniestro, alcances de la investigación..."
            />
          </div>
        </div>

        {/* ENTREVISTA CON EL ASEGURADO */}
        <div style={{ marginBottom: '30px', padding: '20px', backgroundColor: '#f8f9fa', borderRadius: '8px' }}>
          <h3 style={{ color: '#0f172a', marginBottom: '15px' }}>🎤 Entrevista con el Asegurado</h3>
          <div style={{ marginBottom: '15px' }}>
            <button
              type="button"
              onClick={() => {
                const currentRelatos = formData.relatos_asegurado || [];
                const nextNumero = currentRelatos.length + 1;
                setFormData((prev) => ({
                  ...prev,
                  relatos_asegurado: [
                    ...currentRelatos,
                    { numero_relato: nextNumero, texto: "", imagen_url: "" }
                  ]
                }));
              }}
              style={{ backgroundColor: '#28a745', marginBottom: '10px' }}
            >
              ➕ Agregar Relato
            </button>
          </div>

          {formData.relatos_asegurado?.map((relato, index) => (
            <div key={index} style={{ marginBottom: '20px', padding: '15px', backgroundColor: '#ffffff', borderRadius: '5px', border: '1px solid #e2e8f0' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '10px' }}>
                <h4 style={{ color: '#0f172a', margin: 0 }}>Relato {relato.numero_relato}</h4>
                <button
                  type="button"
                  onClick={() => {
                    setFormData((prev) => ({
                      ...prev,
                      relatos_asegurado: prev.relatos_asegurado?.filter((_, i) => i !== index) || []
                    }));
                  }}
                  style={{ backgroundColor: '#dc3545', color: 'white', border: 'none', borderRadius: '3px', padding: '5px 10px', cursor: 'pointer' }}
                >
                  ❌ Eliminar
                </button>
              </div>

              <div className="form-group">
                <label>Texto del relato:</label>
                <textarea
                  value={relato.texto}
                  onChange={(e) => {
                    const value = e.target.value;
                    setFormData((prev) => ({
                      ...prev,
                      relatos_asegurado: prev.relatos_asegurado?.map((r, i) =>
                        i === index ? { ...r, texto: value } : r
                      ) || []
                    }));
                  }}
                  rows={3}
                  placeholder="Escriba el relato del asegurado..."
                />
              </div>

              <div className="form-group">
                <label>Imagen:</label>
                <input
                  type="file"
                  accept="image/*"
                  onChange={async (e) => {
                    const file = e.target.files?.[0];
                    if (file) {
                      try {
                        const formDataUpload = new FormData();
                        formDataUpload.append('file', file);

                        const response = await axios.post('/api/v1/upload-imagen', formDataUpload, {
                          headers: { 'Content-Type': 'multipart/form-data' }
                        });

                        const imageUrl = response.data.url;
                        setFormData((prev) => ({
                          ...prev,
                          relatos_asegurado: prev.relatos_asegurado?.map((r, i) =>
                            i === index ? { ...r, imagen_url: imageUrl } : r
                          ) || []
                        }));
                      } catch (error) {
                        console.error('Error subiendo imagen:', error);
                        alert('Error al subir la imagen. Intente nuevamente.');
                      }
                    }
                  }}
                />
                {relato.imagen_url && (
                  <div style={{ marginTop: '5px' }}>
                    <img
                      src={`http://localhost:8000${relato.imagen_url}`}
                      alt={`Relato ${relato.numero_relato}`}
                      style={{ maxWidth: '200px', maxHeight: '150px', border: '1px solid #ddd' }}
                    />
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>

        {/* INSPECCIÓN DEL LUGAR */}
        <div style={{ marginBottom: '30px', padding: '20px', backgroundColor: '#f8f9fa', borderRadius: '8px' }}>
          <h3 style={{ color: '#0f172a', marginBottom: '15px' }}>🔍 Inspección del Lugar</h3>
          <div style={{ marginBottom: '15px' }}>
            <button
              type="button"
              onClick={() => {
                const currentInspecciones = formData.inspecciones || [];
                const nextNumero = currentInspecciones.length + 1;
                setFormData((prev) => ({
                  ...prev,
                  inspecciones: [
                    ...currentInspecciones,
                    { numero_inspeccion: nextNumero, descripcion: "", imagen_url: "" }
                  ]
                }));
              }}
              style={{ backgroundColor: '#28a745', marginBottom: '10px' }}
            >
              ➕ Agregar Inspección
            </button>
          </div>

          {formData.inspecciones?.map((inspeccion, index) => (
            <div key={index} style={{ marginBottom: '20px', padding: '15px', backgroundColor: '#ffffff', borderRadius: '5px', border: '1px solid #e2e8f0' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '10px' }}>
                <h4 style={{ color: '#0f172a', margin: 0 }}>Inspección {inspeccion.numero_inspeccion}</h4>
                <button
                  type="button"
                  onClick={() => {
                    setFormData((prev) => ({
                      ...prev,
                      inspecciones: prev.inspecciones?.filter((_, i) => i !== index) || []
                    }));
                  }}
                  style={{ backgroundColor: '#dc3545', color: 'white', border: 'none', borderRadius: '3px', padding: '5px 10px', cursor: 'pointer' }}
                >
                  ❌ Eliminar
                </button>
              </div>

              <div className="form-group">
                <label>Descripción de la inspección:</label>
                <textarea
                  value={inspeccion.descripcion}
                  onChange={(e) => {
                    const value = e.target.value;
                    setFormData((prev) => ({
                      ...prev,
                      inspecciones: prev.inspecciones?.map((insp, i) =>
                        i === index ? { ...insp, descripcion: value } : insp
                      ) || []
                    }));
                  }}
                  rows={3}
                  placeholder="Describa los hallazgos de la inspección..."
                />
              </div>

              <div className="form-group">
                <label>Imagen:</label>
                <input
                  type="file"
                  accept="image/*"
                  onChange={async (e) => {
                    const file = e.target.files?.[0];
                    if (file) {
                      try {
                        const formDataUpload = new FormData();
                        formDataUpload.append('file', file);

                        const response = await axios.post('/api/v1/upload-imagen', formDataUpload, {
                          headers: { 'Content-Type': 'multipart/form-data' }
                        });

                        const imageUrl = response.data.url;
                        setFormData((prev) => ({
                          ...prev,
                          inspecciones: prev.inspecciones?.map((insp, i) =>
                            i === index ? { ...insp, imagen_url: imageUrl } : insp
                          ) || []
                        }));
                      } catch (error) {
                        console.error('Error subiendo imagen:', error);
                        alert('Error al subir la imagen. Intente nuevamente.');
                      }
                    }
                  }}
                />
                {inspeccion.imagen_url && (
                  <div style={{ marginTop: '5px' }}>
                    <img
                      src={`http://localhost:8000${inspeccion.imagen_url}`}
                      alt={`Inspección ${inspeccion.numero_inspeccion}`}
                      style={{ maxWidth: '200px', maxHeight: '150px', border: '1px solid #ddd' }}
                    />
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>

        {/* TESTIGOS */}
        <div style={{ marginBottom: '30px', padding: '20px', backgroundColor: '#f8f9fa', borderRadius: '8px' }}>
          <h3 style={{ color: '#0f172a', marginBottom: '15px' }}>👥 Testigos</h3>
          <div style={{ marginBottom: '15px' }}>
            <button
              type="button"
              onClick={() => {
                const currentTestigos = formData.testigos || [];
                const nextNumero = currentTestigos.length + 1;
                setFormData((prev) => ({
                  ...prev,
                  testigos: [
                    ...currentTestigos,
                    { numero_relato: nextNumero, texto: "", imagen_url: "" }
                  ]
                }));
              }}
              style={{ backgroundColor: '#28a745', marginBottom: '10px' }}
            >
              ➕ Agregar Testigo
            </button>
          </div>

          {formData.testigos?.map((testigo, index) => (
            <div key={index} style={{ marginBottom: '20px', padding: '15px', backgroundColor: '#ffffff', borderRadius: '5px', border: '1px solid #e2e8f0' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '10px' }}>
                <h4 style={{ color: '#0f172a', margin: 0 }}>Testigo {testigo.numero_relato}</h4>
                <button
                  type="button"
                  onClick={() => {
                    setFormData((prev) => ({
                      ...prev,
                      testigos: prev.testigos?.filter((_, i) => i !== index) || []
                    }));
                  }}
                  style={{ backgroundColor: '#dc3545', color: 'white', border: 'none', borderRadius: '3px', padding: '5px 10px', cursor: 'pointer' }}
                >
                  ❌ Eliminar
                </button>
              </div>

              <div className="form-group">
                <label>Declaración del testigo:</label>
                <textarea
                  value={testigo.texto}
                  onChange={(e) => {
                    const value = e.target.value;
                    setFormData((prev) => ({
                      ...prev,
                      testigos: prev.testigos?.map((test, i) =>
                        i === index ? { ...test, texto: value } : test
                      ) || []
                    }));
                  }}
                  rows={3}
                  placeholder="Escriba la declaración del testigo..."
                />
              </div>

              <div className="form-group">
                <label>Imagen:</label>
                <input
                  type="file"
                  accept="image/*"
                  onChange={async (e) => {
                    const file = e.target.files?.[0];
                    if (file) {
                      try {
                        const formDataUpload = new FormData();
                        formDataUpload.append('file', file);

                        const response = await axios.post('/api/v1/upload-imagen', formDataUpload, {
                          headers: { 'Content-Type': 'multipart/form-data' }
                        });

                        const imageUrl = response.data.url;
                        setFormData((prev) => ({
                          ...prev,
                          testigos: prev.testigos?.map((test, i) =>
                            i === index ? { ...test, imagen_url: imageUrl } : test
                          ) || []
                        }));
                      } catch (error) {
                        console.error('Error subiendo imagen:', error);
                        alert('Error al subir la imagen. Intente nuevamente.');
                      }
                    }
                  }}
                />
                {testigo.imagen_url && (
                  <div style={{ marginTop: '5px' }}>
                    <img
                      src={`http://localhost:8000${testigo.imagen_url}`}
                      alt={`Testigo ${testigo.numero_relato}`}
                      style={{ maxWidth: '200px', maxHeight: '150px', border: '1px solid #ddd' }}
                    />
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>

        <div style={{ display: "flex", gap: "10px", marginTop: "20px" }}>
          <button
            type="button"
            onClick={() => {
              setFormData((prev) => ({
                ...prev,
                // Datos básicos del siniestro
                compania_seguros: "Zurich Seguros Ecuador S.A.",
                reclamo_num: `TEST-${Date.now()}`,
                fecha_siniestro: "2023-10-15",
                direccion_siniestro: "Av. Amazonas y Naciones Unidas, Quito",
                ubicacion_geo_lat: -0.1807,
                ubicacion_geo_lng: -78.4678,
                danos_terceros: true,
                ejecutivo_cargo: "Juan Pérez",
                fecha_designacion: "2025-12-11",
                tipo_siniestro: "Vehicular",
              }));
            }}
            style={{ backgroundColor: "#6c757d" }}
          >
            Llenar con Datos de Prueba
          </button>

          <button type="submit" disabled={loading}>
            {loading ? "Guardando..." : "Crear Siniestro"}
          </button>
        </div>

        {message && (
          <div
            className={`message ${
              message.includes("Error") ? "error" : "success"
            }`}
          >
            {message}
          </div>
        )}
      </form>
    </div>
  );
};

export default SiniestroForm;
