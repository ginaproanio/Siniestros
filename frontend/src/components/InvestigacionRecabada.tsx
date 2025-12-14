import axios from "axios";
import React, { useState, useEffect } from "react";

// Configurar base URL para el backend
const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || 'https://siniestros-production.up.railway.app';
console.log('🌐 Backend URL:', BACKEND_URL);
axios.defaults.baseURL = BACKEND_URL;

interface VisitaTaller {
  id?: number;
  fecha_visita: string;
  descripcion: string;
  imagen_url?: string;
}

interface DinamicaAccidente {
  id?: number;
  descripcion: string;
  imagen_url?: string;
}

interface EvidenciaComplementaria {
  id?: number;
  descripcion: string;
  imagen_url?: string;
}

interface FormData {
  // Campos adicionales de investigación recabada
  visitas_taller?: VisitaTaller[];
  dinamicas_accidente?: DinamicaAccidente[];
  evidencias_complementarias?: EvidenciaComplementaria[];
  observaciones?: string;
  recomendaciones?: string;
  conclusiones?: string;
}

interface Props {
  siniestroId: number;
}

const InvestigacionRecabada: React.FC<Props> = ({ siniestroId }) => {
  const [formData, setFormData] = useState<FormData>({});
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState("");
  const [siniestroData, setSiniestroData] = useState<any>(null);

  useEffect(() => {
    loadSiniestroData();
  }, [siniestroId]);

  const loadSiniestroData = async () => {
    try {
      const response = await axios.get(`/api/v1/siniestros/${siniestroId}`);
      setSiniestroData(response.data);

      // Cargar datos existentes de investigación recabada
      setFormData({
        visitas_taller: response.data.visitas_taller || [],
        dinamicas_accidente: response.data.dinamicas_accidente || [],
        evidencias_complementarias: response.data.evidencias_complementarias || [],
        observaciones: response.data.observaciones || "",
        recomendaciones: response.data.recomendaciones || "",
        conclusiones: response.data.conclusiones || "",
      });
    } catch (error) {
      console.error("Error cargando datos del siniestro:", error);
      setMessage("Error al cargar los datos del siniestro");
    }
  };

  const handleInputChange = (
    e: React.ChangeEvent<HTMLTextAreaElement>
  ) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setMessage("");

    try {
      // Actualizar el siniestro con los datos de investigación recabada
      const response = await axios.put(`/api/v1/siniestros/${siniestroId}`, formData);
      console.log("✅ Investigación recabada guardada:", response.data);
      setMessage("Investigación recabada guardada exitosamente!");
    } catch (error: any) {
      console.error("❌ Error guardando investigación:", error);
      let errorMessage = "Error al guardar la investigación recabada";

      if (error.response) {
        const status = error.response.status;
        const data = error.response.data;

        switch (status) {
          case 400:
            errorMessage = `Datos inválidos: ${data.detail || "Verifica los campos"}`;
            break;
          case 404:
            errorMessage = "Siniestro no encontrado";
            break;
          case 500:
            errorMessage = `Error del servidor: ${data.detail || data.message || "Error interno"}`;
            break;
          default:
            errorMessage = `Error ${status}: ${data.detail || data.message || "Error desconocido"}`;
        }
      }

      setMessage(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  if (!siniestroData) {
    return <div className="loading">Cargando datos del siniestro...</div>;
  }

  return (
    <div className="form-container">
      <h2>Investigación Recabada</h2>
      <div className="siniestro-info">
        <h3>Información del Siniestro</h3>
        <p><strong>Compañía:</strong> {siniestroData.compania_seguros}</p>
        <p><strong>Número de Reclamo:</strong> {siniestroData.reclamo_num}</p>
        <p><strong>Fecha del Siniestro:</strong> {new Date(siniestroData.fecha_siniestro).toLocaleDateString()}</p>
      </div>

      <form onSubmit={handleSubmit}>
        {/* VISITAS A TALLER */}
        <div className="section-container">
          <h3 className="section-header">🔧 Visitas a Taller</h3>
          <button
            type="button"
            className="btn-add"
            onClick={() => {
              const currentVisitas = formData.visitas_taller || [];
              const nextId = Math.max(...currentVisitas.map(v => v.id || 0), 0) + 1;
              setFormData((prev) => ({
                ...prev,
                visitas_taller: [
                  ...currentVisitas,
                  { id: nextId, fecha_visita: "", descripcion: "", imagen_url: "" },
                ],
              }));
            }}
          >
            ➕ Agregar Visita a Taller
          </button>

          {formData.visitas_taller?.map((visita, index) => (
            <div key={visita.id || index} className="dynamic-item">
              <div className="dynamic-item-header">
                <h4 className="dynamic-item-title">
                  Visita a Taller {index + 1}
                </h4>
                <button
                  type="button"
                  className="btn-delete"
                  onClick={() => {
                    setFormData((prev) => ({
                      ...prev,
                      visitas_taller: prev.visitas_taller?.filter((_, i) => i !== index) || [],
                    }));
                  }}
                >
                  ❌ Eliminar
                </button>
              </div>

              <div className="form-row">
                <div className="form-group">
                  <label>Fecha de Visita:</label>
                  <input
                    type="date"
                    value={visita.fecha_visita}
                    onChange={(e) => {
                      const value = e.target.value;
                      setFormData((prev) => ({
                        ...prev,
                        visitas_taller: prev.visitas_taller?.map((v, i) =>
                          i === index ? { ...v, fecha_visita: value } : v
                        ) || [],
                      }));
                    }}
                  />
                </div>
              </div>

              <div className="form-group">
                <label>Descripción de la visita:</label>
                <textarea
                  value={visita.descripcion}
                  onChange={(e) => {
                    const value = e.target.value;
                    setFormData((prev) => ({
                      ...prev,
                      visitas_taller: prev.visitas_taller?.map((v, i) =>
                        i === index ? { ...v, descripcion: value } : v
                      ) || [],
                    }));
                  }}
                  rows={3}
                  placeholder="Describe los hallazgos de la visita al taller..."
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
                        formDataUpload.append("file", file);

                        const response = await axios.post(
                          "/api/v1/upload-imagen",
                          formDataUpload,
                          {
                            headers: { "Content-Type": "multipart/form-data" },
                          }
                        );

                        const imageUrl = response.data.url;
                        setFormData((prev) => ({
                          ...prev,
                          visitas_taller: prev.visitas_taller?.map((v, i) =>
                            i === index ? { ...v, imagen_url: imageUrl } : v
                          ) || [],
                        }));
                      } catch (error) {
                        console.error("Error subiendo imagen:", error);
                        alert("Error al subir la imagen. Intente nuevamente.");
                      }
                    }
                  }}
                />
                {visita.imagen_url && (
                  <div>
                    <img
                      src={`${BACKEND_URL}${visita.imagen_url}`}
                      alt={`Visita a Taller ${index + 1}`}
                      className="image-preview"
                    />
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>

        {/* DINÁMICAS DEL ACCIDENTE */}
        <div className="section-container">
          <h3 className="section-header">🚨 Dinámicas del Accidente</h3>
          <button
            type="button"
            className="btn-add"
            onClick={() => {
              const currentDinamicas = formData.dinamicas_accidente || [];
              const nextId = Math.max(...currentDinamicas.map(d => d.id || 0), 0) + 1;
              setFormData((prev) => ({
                ...prev,
                dinamicas_accidente: [
                  ...currentDinamicas,
                  { id: nextId, descripcion: "", imagen_url: "" },
                ],
              }));
            }}
          >
            ➕ Agregar Dinámica del Accidente
          </button>

          {formData.dinamicas_accidente?.map((dinamica, index) => (
            <div key={dinamica.id || index} className="dynamic-item">
              <div className="dynamic-item-header">
                <h4 className="dynamic-item-title">
                  Dinámica {index + 1}
                </h4>
                <button
                  type="button"
                  className="btn-delete"
                  onClick={() => {
                    setFormData((prev) => ({
                      ...prev,
                      dinamicas_accidente: prev.dinamicas_accidente?.filter((_, i) => i !== index) || [],
                    }));
                  }}
                >
                  ❌ Eliminar
                </button>
              </div>

              <div className="form-group">
                <label>Descripción de la dinámica:</label>
                <textarea
                  value={dinamica.descripcion}
                  onChange={(e) => {
                    const value = e.target.value;
                    setFormData((prev) => ({
                      ...prev,
                      dinamicas_accidente: prev.dinamicas_accidente?.map((d, i) =>
                        i === index ? { ...d, descripcion: value } : d
                      ) || [],
                    }));
                  }}
                  rows={4}
                  placeholder="Describe la dinámica del accidente, causas, factores contribuyentes..."
                />
              </div>

              <div className="form-group">
                <label>Imagen/Evidencia:</label>
                <input
                  type="file"
                  accept="image/*"
                  onChange={async (e) => {
                    const file = e.target.files?.[0];
                    if (file) {
                      try {
                        const formDataUpload = new FormData();
                        formDataUpload.append("file", file);

                        const response = await axios.post(
                          "/api/v1/upload-imagen",
                          formDataUpload,
                          {
                            headers: { "Content-Type": "multipart/form-data" },
                          }
                        );

                        const imageUrl = response.data.url;
                        setFormData((prev) => ({
                          ...prev,
                          dinamicas_accidente: prev.dinamicas_accidente?.map((d, i) =>
                            i === index ? { ...d, imagen_url: imageUrl } : d
                          ) || [],
                        }));
                      } catch (error) {
                        console.error("Error subiendo imagen:", error);
                        alert("Error al subir la imagen. Intente nuevamente.");
                      }
                    }
                  }}
                />
                {dinamica.imagen_url && (
                  <div>
                    <img
                      src={`${BACKEND_URL}${dinamica.imagen_url}`}
                      alt={`Dinámica ${index + 1}`}
                      className="image-preview"
                    />
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>

        {/* EVIDENCIAS COMPLEMENTARIAS */}
        <div className="section-container">
          <h3 className="section-header">📎 Evidencias Complementarias</h3>
          <button
            type="button"
            className="btn-add"
            onClick={() => {
              const currentEvidencias = formData.evidencias_complementarias || [];
              const nextId = Math.max(...currentEvidencias.map(e => e.id || 0), 0) + 1;
              setFormData((prev) => ({
                ...prev,
                evidencias_complementarias: [
                  ...currentEvidencias,
                  { id: nextId, descripcion: "", imagen_url: "" },
                ],
              }));
            }}
          >
            ➕ Agregar Evidencia Complementaria
          </button>

          {formData.evidencias_complementarias?.map((evidencia, index) => (
            <div key={evidencia.id || index} className="dynamic-item">
              <div className="dynamic-item-header">
                <h4 className="dynamic-item-title">
                  Evidencia {index + 1}
                </h4>
                <button
                  type="button"
                  className="btn-delete"
                  onClick={() => {
                    setFormData((prev) => ({
                      ...prev,
                      evidencias_complementarias: prev.evidencias_complementarias?.filter((_, i) => i !== index) || [],
                    }));
                  }}
                >
                  ❌ Eliminar
                </button>
              </div>

              <div className="form-group">
                <label>Descripción de la evidencia:</label>
                <textarea
                  value={evidencia.descripcion}
                  onChange={(e) => {
                    const value = e.target.value;
                    setFormData((prev) => ({
                      ...prev,
                      evidencias_complementarias: prev.evidencias_complementarias?.map((e, i) =>
                        i === index ? { ...e, descripcion: value } : e
                      ) || [],
                    }));
                  }}
                  rows={3}
                  placeholder="Describe la evidencia complementaria (videos, documentos, etc.)..."
                />
              </div>

              <div className="form-group">
                <label>Archivo/Imagen:</label>
                <input
                  type="file"
                  accept="image/*,video/*,application/*"
                  onChange={async (e) => {
                    const file = e.target.files?.[0];
                    if (file) {
                      try {
                        const formDataUpload = new FormData();
                        formDataUpload.append("file", file);

                        const response = await axios.post(
                          "/api/v1/upload-imagen",
                          formDataUpload,
                          {
                            headers: { "Content-Type": "multipart/form-data" },
                          }
                        );

                        const imageUrl = response.data.url;
                        setFormData((prev) => ({
                          ...prev,
                          evidencias_complementarias: prev.evidencias_complementarias?.map((e, i) =>
                            i === index ? { ...e, imagen_url: imageUrl } : e
                          ) || [],
                        }));
                      } catch (error) {
                        console.error("Error subiendo archivo:", error);
                        alert("Error al subir el archivo. Intente nuevamente.");
                      }
                    }
                  }}
                />
                {evidencia.imagen_url && (
                  <div>
                    <img
                      src={`${BACKEND_URL}${evidencia.imagen_url}`}
                      alt={`Evidencia ${index + 1}`}
                      className="image-preview"
                    />
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>

        {/* CONCLUSIONES FINALES */}
        <div className="section-container">
          <h3 className="section-header">📊 Conclusiones de la Investigación</h3>

          <div className="form-group">
            <label>Observaciones:</label>
            <textarea
              name="observaciones"
              value={formData.observaciones || ""}
              onChange={handleInputChange}
              rows={4}
              placeholder="Observaciones generales de la investigación..."
            />
          </div>

          <div className="form-group">
            <label>Recomendaciones:</label>
            <textarea
              name="recomendaciones"
              value={formData.recomendaciones || ""}
              onChange={handleInputChange}
              rows={4}
              placeholder="Recomendaciones basadas en los hallazgos..."
            />
          </div>

          <div className="form-group">
            <label>Conclusiones:</label>
            <textarea
              name="conclusiones"
              value={formData.conclusiones || ""}
              onChange={handleInputChange}
              rows={6}
              placeholder="Conclusiones finales de la investigación..."
            />
          </div>
        </div>

        <div style={{ display: "flex", gap: "10px", marginTop: "20px" }}>
          <button type="submit" disabled={loading}>
            {loading ? "Guardando..." : "Guardar Investigación Recabada"}
          </button>
        </div>

        {message && (
          <div
            className={`message ${message.includes("Error") ? "error" : "success"}`}
          >
            {message}
          </div>
        )}
      </form>
    </div>
  );
};

export default InvestigacionRecabada;
