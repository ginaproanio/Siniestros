import axios from "axios";
import React, { useEffect, useState } from "react";
import { useParams } from "react-router-dom";

// Configurar base URL para el backend
const BACKEND_URL =
  process.env.REACT_APP_BACKEND_URL ||
  "https://siniestros-production.up.railway.app";
console.log("🌐 Backend URL:", BACKEND_URL);
axios.defaults.baseURL = BACKEND_URL;

interface FormData {
  antecedentes?: any[];
  relatos_asegurado?: any[];
  relatos_conductor?: any[];
  inspecciones?: any[];
  testigos?: any[];
  evidencias_complementarias_descripcion?: string;
  evidencias_complementarias_imagen_url?: string;
  otras_diligencias_descripcion?: string;
  otras_diligencias_imagen_url?: string;
  visita_taller_descripcion?: string;
  visita_taller_imagen_url?: string;
  observaciones?: string[];
  recomendacion_pago_cobertura?: string[];
  conclusiones?: string[];
  anexo?: string[];
}

const InvestigacionForm: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const siniestroId = parseInt(id || "0");

  // Sistema de pestañas
  const [activeTab, setActiveTab] = useState(0);
  const [completedTabs, setCompletedTabs] = useState<number[]>([]);

  const [formData, setFormData] = useState<FormData>({});
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState("");
  const [siniestroInfo, setSiniestroInfo] = useState<any>(null);

  // Definir pestañas
  const tabs = [
    { id: 0, title: "Antecedentes", icon: "📋", required: true },
    { id: 1, title: "Entrevistas", icon: "🎤", required: false },
    { id: 2, title: "Inspección", icon: "🔍", required: false },
    { id: 3, title: "Testigos", icon: "👥", required: false },
    { id: 4, title: "Evidencias", icon: "📎", required: false },
    { id: 5, title: "Conclusiones", icon: "📊", required: true },
  ];

  useEffect(() => {
    const fetchSiniestroData = async () => {
      try {
        const response = await axios.get(`/api/v1/siniestros/${siniestroId}`);
        const siniestro = response.data;
        setSiniestroInfo(siniestro);
        setFormData({
          antecedentes: siniestro.antecedentes || [],
          relatos_asegurado: siniestro.relatos_asegurado || [],
          relatos_conductor: siniestro.relatos_conductor || [],
          inspecciones: siniestro.inspecciones || [],
          testigos: siniestro.testigos || [],
          evidencias_complementarias_descripcion:
            siniestro.evidencias_complementarias_descripcion,
          evidencias_complementarias_imagen_url:
            siniestro.evidencias_complementarias_imagen_url,
          otras_diligencias_descripcion:
            siniestro.otras_diligencias_descripcion,
          otras_diligencias_imagen_url: siniestro.otras_diligencias_imagen_url,
          visita_taller_descripcion: siniestro.visita_taller_descripcion,
          visita_taller_imagen_url: siniestro.visita_taller_imagen_url,
          observaciones: siniestro.observaciones || [],
          recomendacion_pago_cobertura:
            siniestro.recomendacion_pago_cobertura || [],
          conclusiones: siniestro.conclusiones || [],
          anexo: siniestro.anexo || [],
        });
      } catch (error) {
        console.error("Error fetching siniestro data:", error);
        setMessage("Error al cargar los datos del siniestro");
      } finally {
        setLoading(false);
      }
    };

    if (siniestroId) {
      fetchSiniestroData();
    }
  }, [siniestroId]);

  // Función para guardar sección específica
  const guardarSeccion = async (seccion: string, datos: any) => {
    try {
      setSaving(true);
      setMessage("");

      await axios.put(
        `/api/v1/siniestros/${siniestroId}/seccion/${seccion}`,
        datos
      );
      setMessage(`✅ Sección "${seccion}" guardada exitosamente`);

      if (!completedTabs.includes(activeTab)) {
        setCompletedTabs((prev) => [...prev, activeTab]);
      }

      return true;
    } catch (error: any) {
      console.error(`Error guardando sección ${seccion}:`, error);
      setMessage(`❌ Error al guardar sección "${seccion}"`);
      return false;
    } finally {
      setSaving(false);
    }
  };

  const nextTab = () => {
    if (activeTab < tabs.length - 1) {
      setActiveTab(activeTab + 1);
    }
  };

  const prevTab = () => {
    if (activeTab > 0) {
      setActiveTab(activeTab - 1);
    }
  };

  const goToTab = (tabIndex: number) => {
    setActiveTab(tabIndex);
  };

  if (loading) return <div>Cargando investigación...</div>;

  return (
    <div className="form-container">
      <div className="form-header">
        <h2>Registro de Investigación - Siniestro #{siniestroId}</h2>
        {siniestroInfo && (
          <div
            style={{
              marginTop: "10px",
              padding: "10px",
              backgroundColor: "#f8f9fa",
              borderRadius: "5px",
            }}
          >
            <strong>Reclamo:</strong> {siniestroInfo.reclamo_num} |
            <strong> Compañía:</strong> {siniestroInfo.compania_seguros} |
            <strong> Fecha:</strong>{" "}
            {new Date(siniestroInfo.fecha_siniestro).toLocaleDateString()}
          </div>
        )}
      </div>

      {/* Tab Navigation */}
      <div className="tabs-container">
        <div className="tabs-header">
          {tabs.map((tab) => {
            const isActive = activeTab === tab.id;
            const isCompleted = completedTabs.includes(tab.id);
            const buttonClass = `tab-button${isActive ? " active" : ""}${
              isCompleted ? " completed" : ""
            }`;

            return (
              <button
                key={tab.id}
                type="button"
                className={buttonClass}
                onClick={() => goToTab(tab.id)}
              >
                {tab.icon} {tab.title}
                {isCompleted && <span className="tab-check">✓</span>}
              </button>
            );
          })}
        </div>

        {/* Tab Content */}
        <div className="tab-content">
          <form onSubmit={(e) => e.preventDefault()}>
            {/* TAB 0: ANTECEDENTES */}
            {activeTab === 0 && (
              <div className="tab-section active">
                <div className="card-section antecedentes-section">
                  <div className="card-header">
                    <div className="card-icon">📋</div>
                    <div>
                      <h3 className="card-title">Antecedentes</h3>
                      <p className="card-description">
                        Información básica del aviso de siniestro y alcance de
                        la investigación
                      </p>
                    </div>
                  </div>

                  <div className="form-group">
                    <label>Descripción de los antecedentes:</label>
                    <textarea
                      value={
                        (formData.antecedentes &&
                          formData.antecedentes[0]?.descripcion) ||
                        ""
                      }
                      onChange={(e) => {
                        const value = e.target.value;
                        setFormData((prev) => ({
                          ...prev,
                          antecedentes: [{ descripcion: value }],
                        }));
                      }}
                      rows={6}
                      placeholder="Describa el aviso de siniestro, alcances de la investigación..."
                    />
                  </div>

                  <div className="tab-navigation">
                    <button
                      type="button"
                      className="btn-submit-tab"
                      onClick={() =>
                        guardarSeccion(
                          "antecedentes",
                          formData.antecedentes || []
                        )
                      }
                      disabled={saving}
                    >
                      {saving ? "Guardando..." : "💾 Guardar Antecedentes"}
                    </button>
                    <button
                      type="button"
                      className="btn-next"
                      onClick={nextTab}
                    >
                      Siguiente →
                    </button>
                  </div>
                </div>
              </div>
            )}

            {/* TAB 1: ENTREVISTAS */}
            {activeTab === 1 && (
              <div className="tab-section active">
                <div className="card-section entrevistas-section">
                  <div className="card-header">
                    <div className="card-icon">🎤</div>
                    <div>
                      <h3 className="card-title">Entrevistas</h3>
                      <p className="card-description">
                        Recopilación de testimonios del asegurado y conductor
                        involucrado
                      </p>
                    </div>
                  </div>

                  <div className="subsection">
                    <h4>Entrevista al Asegurado</h4>
                    <div style={{ marginBottom: "15px" }}>
                      <button
                        type="button"
                        onClick={() => {
                          const currentRelatos =
                            formData.relatos_asegurado || [];
                          const nextNumero = currentRelatos.length + 1;
                          setFormData((prev) => ({
                            ...prev,
                            relatos_asegurado: [
                              ...currentRelatos,
                              {
                                numero_relato: nextNumero,
                                texto: "",
                                imagen_url: "",
                              },
                            ],
                          }));
                        }}
                        style={{
                          backgroundColor: "#28a745",
                          marginBottom: "10px",
                        }}
                      >
                        ➕ Agregar Relato
                      </button>
                    </div>

                    {(formData.relatos_asegurado || []).map((relato, index) => (
                      <div key={index} className="dynamic-item">
                        <div className="dynamic-item-header">
                          <h4 className="dynamic-item-title">
                            Relato {relato.numero_relato}
                          </h4>
                          <button
                            type="button"
                            className="btn-delete"
                            onClick={() => {
                              setFormData((prev) => ({
                                ...prev,
                                relatos_asegurado:
                                  prev.relatos_asegurado?.filter(
                                    (_, i) => i !== index
                                  ) || [],
                              }));
                            }}
                          >
                            ❌ Eliminar
                          </button>
                        </div>
                        <div className="form-group">
                          <textarea
                            value={relato.texto}
                            onChange={(e) => {
                              const value = e.target.value;
                              setFormData((prev) => ({
                                ...prev,
                                relatos_asegurado:
                                  prev.relatos_asegurado?.map((r, i) =>
                                    i === index ? { ...r, texto: value } : r
                                  ) || [],
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
                                  formDataUpload.append("file", file);
                                  const response = await axios.post(
                                    "/api/v1/siniestros/upload-image",
                                    formDataUpload,
                                    {
                                      headers: {
                                        "Content-Type": "multipart/form-data",
                                      },
                                    }
                                  );
                                  const imageUrl = response.data.url_presigned;
                                  setFormData((prev) => ({
                                    ...prev,
                                    relatos_asegurado:
                                      prev.relatos_asegurado?.map((r, i) =>
                                        i === index
                                          ? { ...r, imagen_url: imageUrl }
                                          : r
                                      ) || [],
                                  }));
                                } catch (error) {
                                  alert(
                                    "Error al subir la imagen. Intente nuevamente."
                                  );
                                }
                              }
                            }}
                          />
                          {relato.imagen_url && (
                            <img
                              src={relato.imagen_url}
                              alt={`Relato ${relato.numero_relato}`}
                              style={{ maxWidth: "200px", marginTop: "5px" }}
                            />
                          )}
                        </div>
                      </div>
                    ))}
                  </div>

                  <div className="tab-navigation">
                    <button
                      type="button"
                      className="btn-prev"
                      onClick={prevTab}
                    >
                      ← Anterior
                    </button>
                    <button
                      type="button"
                      className="btn-submit-tab"
                      onClick={() =>
                        guardarSeccion(
                          "relatos_asegurado",
                          formData.relatos_asegurado || []
                        )
                      }
                      disabled={saving}
                    >
                      {saving ? "Guardando..." : "💾 Guardar Entrevistas"}
                    </button>
                    <button
                      type="button"
                      className="btn-next"
                      onClick={nextTab}
                    >
                      Siguiente →
                    </button>
                  </div>
                </div>
              </div>
            )}

            {/* TAB 4: EVIDENCIAS */}
            {activeTab === 4 && (
              <div className="tab-section active">
                <div className="card-section evidencias-section">
                  <div className="card-header">
                    <div className="card-icon">�</div>
                    <div>
                      <h3 className="card-title">Evidencias y Diligencias</h3>
                      <p className="card-description">
                        Documentación adicional y evidencias complementarias
                      </p>
                    </div>
                  </div>

                  {/* Evidencias Complementarias */}
                  <div className="subsection">
                    <h4>Evidencias Complementarias</h4>
                    <div className="form-group">
                      <label>Descripción:</label>
                      <textarea
                        value={
                          formData.evidencias_complementarias_descripcion || ""
                        }
                        onChange={(e) =>
                          setFormData((prev) => ({
                            ...prev,
                            evidencias_complementarias_descripcion:
                              e.target.value,
                          }))
                        }
                        rows={4}
                        placeholder="Describe las evidencias complementarias..."
                      />
                    </div>

                    <div className="form-group">
                      <label>Imagen de Evidencias Complementarias:</label>
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
                                "/api/v1/siniestros/upload-image",
                                formDataUpload,
                                {
                                  headers: {
                                    "Content-Type": "multipart/form-data",
                                  },
                                }
                              );
                              const imageUrl = response.data.url_presigned;
                              setFormData((prev) => ({
                                ...prev,
                                evidencias_complementarias_imagen_url: imageUrl,
                              }));
                            } catch (error) {
                              alert(
                                "Error al subir la imagen. Intente nuevamente."
                              );
                            }
                          }
                        }}
                      />
                      {formData.evidencias_complementarias_imagen_url && (
                        <img
                          src={formData.evidencias_complementarias_imagen_url}
                          alt="Evidencias Complementarias"
                          style={{ maxWidth: "200px", marginTop: "5px" }}
                        />
                      )}
                    </div>
                  </div>

                  {/* Anexos con carga de documentos */}
                  <div className="subsection">
                    <h4>Anexos</h4>
                    <div style={{ marginBottom: "15px" }}>
                      <button
                        type="button"
                        onClick={() => {
                          const currentAnexo = formData.anexo || [];
                          setFormData((prev) => ({
                            ...prev,
                            anexo: [...currentAnexo, ""],
                          }));
                        }}
                        style={{
                          backgroundColor: "#28a745",
                          marginBottom: "10px",
                        }}
                      >
                        ➕ Agregar Anexo
                      </button>
                    </div>

                    {(formData.anexo || []).map((anexoItem, index) => (
                      <div key={index} className="dynamic-item">
                        <div className="dynamic-item-header">
                          <h4 className="dynamic-item-title">
                            Anexo {index + 1}
                          </h4>
                          <button
                            type="button"
                            className="btn-delete"
                            onClick={() => {
                              const currentAnexo = formData.anexo || [];
                              setFormData((prev) => ({
                                ...prev,
                                anexo: currentAnexo.filter(
                                  (_, i) => i !== index
                                ),
                              }));
                            }}
                          >
                            ❌ Eliminar
                          </button>
                        </div>
                        <div className="form-group">
                          <textarea
                            value={anexoItem}
                            onChange={(e) => {
                              const value = e.target.value;
                              const currentAnexo = formData.anexo || [];
                              const newAnexo = [...currentAnexo];
                              newAnexo[index] = value;
                              setFormData((prev) => ({
                                ...prev,
                                anexo: newAnexo,
                              }));
                            }}
                            rows={3}
                            placeholder="Escribe el anexo..."
                          />
                        </div>
                        <div className="form-group">
                          <label>Documento adjunto:</label>
                          <input
                            type="file"
                            accept=".pdf,.doc,.docx,.xls,.xlsx,.txt,.jpg,.jpeg,.png"
                            onChange={async (e) => {
                              const file = e.target.files?.[0];
                              if (file) {
                                try {
                                  const formDataUpload = new FormData();
                                  formDataUpload.append("file", file);
                                  const response = await axios.post(
                                    "/api/v1/siniestros/upload-image",
                                    formDataUpload,
                                    {
                                      headers: {
                                        "Content-Type": "multipart/form-data",
                                      },
                                    }
                                  );
                                  const docUrl = response.data.url_presigned;
                                  const currentAnexo = formData.anexo || [];
                                  const newAnexo = [...currentAnexo];
                                  newAnexo[
                                    index
                                  ] = `${anexoItem}\n[Documento adjunto: ${file.name}]`;
                                  setFormData((prev) => ({
                                    ...prev,
                                    anexo: newAnexo,
                                  }));
                                } catch (error) {
                                  alert(
                                    "Error al subir el documento. Intente nuevamente."
                                  );
                                }
                              }
                            }}
                          />
                        </div>
                      </div>
                    ))}
                  </div>

                  <div className="tab-navigation">
                    <button
                      type="button"
                      className="btn-prev"
                      onClick={prevTab}
                    >
                      ← Anterior
                    </button>
                    <button
                      type="button"
                      className="btn-submit-tab"
                      onClick={() => {
                        guardarSeccion("evidencias_complementarias", {
                          evidencias_complementarias_descripcion:
                            formData.evidencias_complementarias_descripcion,
                          evidencias_complementarias_imagen_url:
                            formData.evidencias_complementarias_imagen_url,
                          anexo: formData.anexo,
                        });
                      }}
                      disabled={saving}
                    >
                      {saving ? "Guardando..." : "💾 Guardar Evidencias"}
                    </button>
                    <button
                      type="button"
                      className="btn-next"
                      onClick={nextTab}
                    >
                      Siguiente →
                    </button>
                  </div>
                </div>
              </div>
            )}

            {/* TAB 5: CONCLUSIONES */}
            {activeTab === 5 && (
              <div className="tab-section active">
                <div className="card-section conclusiones-section">
                  <div className="card-header">
                    <div className="card-icon">📊</div>
                    <div>
                      <h3 className="card-title">Conclusiones</h3>
                      <p className="card-description">
                        Resumen final de la investigación y recomendaciones
                      </p>
                    </div>
                  </div>

                  {/* Observaciones */}
                  <div className="subsection">
                    <h4>Observaciones</h4>
                    <button
                      type="button"
                      onClick={() => {
                        const currentObservaciones =
                          formData.observaciones || [];
                        setFormData((prev) => ({
                          ...prev,
                          observaciones: [...currentObservaciones, ""],
                        }));
                      }}
                      style={{
                        backgroundColor: "#28a745",
                        marginBottom: "10px",
                      }}
                    >
                      ➕ Agregar Observación
                    </button>

                    {(formData.observaciones || []).map(
                      (observacion, index) => (
                        <div key={index} className="dynamic-item">
                          <div className="form-group">
                            <textarea
                              value={observacion}
                              onChange={(e) => {
                                const value = e.target.value;
                                const currentObservaciones =
                                  formData.observaciones || [];
                                const newObservaciones = [
                                  ...currentObservaciones,
                                ];
                                newObservaciones[index] = value;
                                setFormData((prev) => ({
                                  ...prev,
                                  observaciones: newObservaciones,
                                }));
                              }}
                              rows={3}
                              placeholder="Escribe la observación..."
                            />
                          </div>
                        </div>
                      )
                    )}
                  </div>

                  {/* Conclusiones */}
                  <div className="subsection">
                    <h4>Conclusiones</h4>
                    <button
                      type="button"
                      onClick={() => {
                        const currentConclusiones = formData.conclusiones || [];
                        setFormData((prev) => ({
                          ...prev,
                          conclusiones: [...currentConclusiones, ""],
                        }));
                      }}
                      style={{
                        backgroundColor: "#28a745",
                        marginBottom: "10px",
                      }}
                    >
                      ➕ Agregar Conclusión
                    </button>

                    {(formData.conclusiones || []).map((conclusion, index) => (
                      <div key={index} className="dynamic-item">
                        <div className="form-group">
                          <textarea
                            value={conclusion}
                            onChange={(e) => {
                              const value = e.target.value;
                              const currentConclusiones =
                                formData.conclusiones || [];
                              const newConclusiones = [...currentConclusiones];
                              newConclusiones[index] = value;
                              setFormData((prev) => ({
                                ...prev,
                                conclusiones: newConclusiones,
                              }));
                            }}
                            rows={3}
                            placeholder="Escribe la conclusión..."
                          />
                        </div>
                      </div>
                    ))}
                  </div>

                  <div className="tab-navigation">
                    <button
                      type="button"
                      className="btn-prev"
                      onClick={prevTab}
                    >
                      ← Anterior
                    </button>
                    <button
                      type="button"
                      className="btn-submit-tab"
                      onClick={() =>
                        guardarSeccion("conclusiones", {
                          observaciones: formData.observaciones,
                          conclusiones: formData.conclusiones,
                        })
                      }
                      disabled={saving}
                    >
                      {saving ? "Guardando..." : "💾 Guardar Conclusiones"}
                    </button>
                  </div>
                </div>
              </div>
            )}
          </form>
        </div>
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
    </div>
  );
};

export default InvestigacionForm;
