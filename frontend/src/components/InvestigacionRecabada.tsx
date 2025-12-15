import axios from "axios";
import React, { useState, useEffect, useCallback } from "react";

// Configurar base URL para el backend
const BACKEND_URL =
  process.env.REACT_APP_BACKEND_URL ||
  "https://siniestros-production.up.railway.app";
console.log("🌐 Backend URL:", BACKEND_URL);
axios.defaults.baseURL = BACKEND_URL;

interface FormData {
  // Campos de investigación recabada según requerimientos
  evidencias_complementarias_descripcion?: string;
  evidencias_complementarias_imagen_url?: string;
  otras_diligencias_descripcion?: string;
  otras_diligencias_imagen_url?: string;
  visita_taller_descripcion?: string;
  visita_taller_imagen_url?: string;
  observaciones?: string[]; // Array of strings for numbered list
  recomendacion_pago_cobertura?: string[]; // Array of strings for numbered list
  conclusiones?: string[]; // Array of strings for numbered list
  anexo?: string[]; // Array of strings for numbered list
}

interface Props {
  siniestroId: number;
}

const InvestigacionRecabada: React.FC<Props> = ({ siniestroId }) => {
  const [formData, setFormData] = useState<FormData>({});
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState("");
  const [siniestroData, setSiniestroData] = useState<any>(null);

  const loadSiniestroData = useCallback(async () => {
    try {
      const response = await axios.get(`/api/v1/siniestros/${siniestroId}`);
      setSiniestroData(response.data);

      // Parse JSON strings back to arrays
      const parseJsonArray = (jsonString: string | null): string[] => {
        if (!jsonString) return [];
        try {
          const parsed = JSON.parse(jsonString);
          return Array.isArray(parsed) ? parsed : [];
        } catch {
          return [];
        }
      };

      // Cargar datos existentes de investigación recabada
      setFormData({
        evidencias_complementarias_descripcion:
          response.data.evidencias_complementarias || "",
        evidencias_complementarias_imagen_url:
          response.data.evidencias_complementarias_imagen_url || "",
        otras_diligencias_descripcion: response.data.otras_diligencias || "",
        otras_diligencias_imagen_url:
          response.data.otras_diligencias_imagen_url || "",
        visita_taller_descripcion: response.data.visita_taller_descripcion || "",
        visita_taller_imagen_url: response.data.visita_taller_imagen_url || "",
        observaciones: parseJsonArray(response.data.observaciones),
        recomendacion_pago_cobertura: parseJsonArray(
          response.data.recomendacion_pago_cobertura
        ),
        conclusiones: parseJsonArray(response.data.conclusiones),
        anexo: parseJsonArray(response.data.anexo),
      });
    } catch (error) {
      console.error("Error cargando datos del siniestro:", error);
      setMessage("Error al cargar los datos del siniestro");
    }
  }, [siniestroId]);

  useEffect(() => {
    loadSiniestroData();
  }, [loadSiniestroData]);

  const handleArrayInputChange = (arrayName: keyof FormData, index: number, value: string) => {
    setFormData((prev) => {
      const array = prev[arrayName] as string[] || [];
      const newArray = [...array];
      newArray[index] = value;
      return {
        ...prev,
        [arrayName]: newArray,
      };
    });
  };

  const addArrayItem = (arrayName: keyof FormData) => {
    setFormData((prev) => {
      const array = prev[arrayName] as string[] || [];
      return {
        ...prev,
        [arrayName]: [...array, ""],
      };
    });
  };

  const removeArrayItem = (arrayName: keyof FormData, index: number) => {
    setFormData((prev) => {
      const array = prev[arrayName] as string[] || [];
      return {
        ...prev,
        [arrayName]: array.filter((_, i) => i !== index),
      };
    });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setMessage("");

    try {
      // Prepare data for submission - serialize arrays to JSON strings
      const submitData = {
        evidencias_complementarias: formData.evidencias_complementarias_descripcion || "",
        evidencias_complementarias_imagen_url: formData.evidencias_complementarias_imagen_url || "",
        otras_diligencias: formData.otras_diligencias_descripcion || "",
        otras_diligencias_imagen_url: formData.otras_diligencias_imagen_url || "",
        visita_taller_descripcion: formData.visita_taller_descripcion || "",
        visita_taller_imagen_url: formData.visita_taller_imagen_url || "",
        observaciones: JSON.stringify(formData.observaciones || []),
        recomendacion_pago_cobertura: JSON.stringify(formData.recomendacion_pago_cobertura || []),
        conclusiones: JSON.stringify(formData.conclusiones || []),
        anexo: JSON.stringify(formData.anexo || []),
      };

      // Actualizar el siniestro con los datos de investigación recabada
      const response = await axios.put(
        `/api/v1/siniestros/${siniestroId}`,
        submitData
      );
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
            errorMessage = `Datos inválidos: ${
              data.detail || "Verifica los campos"
            }`;
            break;
          case 404:
            errorMessage = "Siniestro no encontrado";
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
        <p>
          <strong>Compañía:</strong> {siniestroData.compania_seguros}
        </p>
        <p>
          <strong>Número de Reclamo:</strong> {siniestroData.reclamo_num}
        </p>
        <p>
          <strong>Fecha del Siniestro:</strong>{" "}
          {new Date(siniestroData.fecha_siniestro).toLocaleDateString()}
        </p>
      </div>

      <form onSubmit={handleSubmit}>
        {/* EVIDENCIAS COMPLEMENTARIAS */}
        <div className="section-container">
          <h3 className="section-header">📎 Evidencias Complementarias</h3>
          <div className="form-group">
            <label>Descripción:</label>
            <textarea
              value={formData.evidencias_complementarias_descripcion || ""}
              onChange={(e) =>
                setFormData((prev) => ({
                  ...prev,
                  evidencias_complementarias_descripcion: e.target.value,
                }))
              }
              rows={4}
              placeholder="Describe las evidencias complementarias..."
            />
          </div>

          {/* Mostrar campo de imagen solo si contiene "Parte Policial" */}
          {formData.evidencias_complementarias_descripcion?.toLowerCase().includes("parte policial") && (
            <div className="form-group">
              <label>Imagen (Parte Policial):</label>
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
                        evidencias_complementarias_imagen_url: imageUrl,
                      }));
                    } catch (error) {
                      console.error("Error subiendo imagen:", error);
                      alert("Error al subir la imagen. Intente nuevamente.");
                    }
                  }
                }}
              />
              {formData.evidencias_complementarias_imagen_url && (
                <div>
                  <img
                    src={`${BACKEND_URL}${formData.evidencias_complementarias_imagen_url}`}
                    alt="Parte Policial"
                    className="image-preview"
                  />
                </div>
              )}
            </div>
          )}
        </div>

        {/* OTRAS DILIGENCIAS */}
        <div className="section-container">
          <h3 className="section-header">📋 Otras Diligencias</h3>
          <div className="form-group">
            <label>Descripción:</label>
            <textarea
              value={formData.otras_diligencias_descripcion || ""}
              onChange={(e) =>
                setFormData((prev) => ({
                  ...prev,
                  otras_diligencias_descripcion: e.target.value,
                }))
              }
              rows={4}
              placeholder="Describe otras diligencias realizadas..."
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
                      otras_diligencias_imagen_url: imageUrl,
                    }));
                  } catch (error) {
                    console.error("Error subiendo imagen:", error);
                    alert("Error al subir la imagen. Intente nuevamente.");
                  }
                }
              }}
            />
            {formData.otras_diligencias_imagen_url && (
              <div>
                <img
                  src={`${BACKEND_URL}${formData.otras_diligencias_imagen_url}`}
                  alt="Otras Diligencias"
                  className="image-preview"
                />
              </div>
            )}
          </div>
        </div>

        {/* VISITA AL TALLER */}
        <div className="section-container">
          <h3 className="section-header">🔧 Visita al Taller</h3>
          <div className="form-group">
            <label>Descripción:</label>
            <textarea
              value={formData.visita_taller_descripcion || ""}
              onChange={(e) =>
                setFormData((prev) => ({
                  ...prev,
                  visita_taller_descripcion: e.target.value,
                }))
              }
              rows={4}
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
                      visita_taller_imagen_url: imageUrl,
                    }));
                  } catch (error) {
                    console.error("Error subiendo imagen:", error);
                    alert("Error al subir la imagen. Intente nuevamente.");
                  }
                }
              }}
            />
            {formData.visita_taller_imagen_url && (
              <div>
                <img
                  src={`${BACKEND_URL}${formData.visita_taller_imagen_url}`}
                  alt="Visita al Taller"
                  className="image-preview"
                />
              </div>
            )}
          </div>
        </div>

        {/* OBSERVACIONES */}
        <div className="section-container">
          <h3 className="section-header">👁️ Observaciones</h3>
          <button
            type="button"
            className="btn-add"
            onClick={() => addArrayItem("observaciones")}
          >
            ➕ Agregar Observación
          </button>

          {(formData.observaciones || []).map((observacion, index) => (
            <div key={index} className="dynamic-item">
              <div className="dynamic-item-header">
                <h4 className="dynamic-item-title">Observación {index + 1}</h4>
                <button
                  type="button"
                  className="btn-delete"
                  onClick={() => removeArrayItem("observaciones", index)}
                >
                  ❌ Eliminar
                </button>
              </div>

              <div className="form-group">
                <textarea
                  value={observacion}
                  onChange={(e) =>
                    handleArrayInputChange("observaciones", index, e.target.value)
                  }
                  rows={3}
                  placeholder="Escribe la observación..."
                />
              </div>
            </div>
          ))}
        </div>

        {/* RECOMENDACIÓN SOBRE EL PAGO DE LA COBERTURA */}
        <div className="section-container">
          <h3 className="section-header">💰 Recomendación (Sobre el Pago de la Cobertura)</h3>
          <button
            type="button"
            className="btn-add"
            onClick={() => addArrayItem("recomendacion_pago_cobertura")}
          >
            ➕ Agregar Recomendación
          </button>

          {(formData.recomendacion_pago_cobertura || []).map((recomendacion, index) => (
            <div key={index} className="dynamic-item">
              <div className="dynamic-item-header">
                <h4 className="dynamic-item-title">Recomendación {index + 1}</h4>
                <button
                  type="button"
                  className="btn-delete"
                  onClick={() => removeArrayItem("recomendacion_pago_cobertura", index)}
                >
                  ❌ Eliminar
                </button>
              </div>

              <div className="form-group">
                <textarea
                  value={recomendacion}
                  onChange={(e) =>
                    handleArrayInputChange("recomendacion_pago_cobertura", index, e.target.value)
                  }
                  rows={3}
                  placeholder="Escribe la recomendación sobre el pago de la cobertura..."
                />
              </div>
            </div>
          ))}
        </div>

        {/* CONCLUSIONES */}
        <div className="section-container">
          <h3 className="section-header">📊 Conclusiones</h3>
          <button
            type="button"
            className="btn-add"
            onClick={() => addArrayItem("conclusiones")}
          >
            ➕ Agregar Conclusión
          </button>

          {(formData.conclusiones || []).map((conclusion, index) => (
            <div key={index} className="dynamic-item">
              <div className="dynamic-item-header">
                <h4 className="dynamic-item-title">Conclusión {index + 1}</h4>
                <button
                  type="button"
                  className="btn-delete"
                  onClick={() => removeArrayItem("conclusiones", index)}
                >
                  ❌ Eliminar
                </button>
              </div>

              <div className="form-group">
                <textarea
                  value={conclusion}
                  onChange={(e) =>
                    handleArrayInputChange("conclusiones", index, e.target.value)
                  }
                  rows={3}
                  placeholder="Escribe la conclusión..."
                />
              </div>
            </div>
          ))}
        </div>

        {/* ANEXO */}
        <div className="section-container">
          <h3 className="section-header">📎 Anexo</h3>
          <button
            type="button"
            className="btn-add"
            onClick={() => addArrayItem("anexo")}
          >
            ➕ Agregar Anexo
          </button>

          {(formData.anexo || []).map((anexoItem, index) => (
            <div key={index} className="dynamic-item">
              <div className="dynamic-item-header">
                <h4 className="dynamic-item-title">Anexo {index + 1}</h4>
                <button
                  type="button"
                  className="btn-delete"
                  onClick={() => removeArrayItem("anexo", index)}
                >
                  ❌ Eliminar
                </button>
              </div>

              <div className="form-group">
                <textarea
                  value={anexoItem}
                  onChange={(e) =>
                    handleArrayInputChange("anexo", index, e.target.value)
                  }
                  rows={3}
                  placeholder="Escribe el anexo..."
                />
              </div>
            </div>
          ))}
        </div>

        <div style={{ display: "flex", gap: "10px", marginTop: "20px" }}>
          <button type="submit" disabled={loading}>
            {loading ? "Guardando..." : "Guardar Investigación Recabada"}
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

export default InvestigacionRecabada;
