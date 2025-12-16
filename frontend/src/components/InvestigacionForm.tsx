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
  evidencias_complementarias?: any[];
  otras_diligencias?: any[];
  visita_taller?: any[];
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

  // Definir pestañas siguiendo la secuencia exacta del proceso de investigación - sin íconos para evitar ancho
  const tabs = [
    { id: 0, title: "Antecedentes", field: "antecedentes" },
    { id: 1, title: "Entrevista Asegurado", field: "relatos_asegurado" },
    { id: 2, title: "Entrevista Conductor", field: "relatos_conductor" },
    { id: 3, title: "Inspección Lugar", field: "inspecciones" },
    { id: 4, title: "Testigos", field: "testigos" },
    {
      id: 5,
      title: "Evidencias Complementarias",
      field: "evidencias_complementarias",
    },
    { id: 6, title: "Otras Diligencias", field: "otras_diligencias" },
    { id: 7, title: "Visita Taller", field: "visita_taller" },
    { id: 8, title: "Observaciones", field: "observaciones" },
    { id: 9, title: "Recomendación Pago", field: "recomendacion_pago" },
    { id: 10, title: "Conclusiones", field: "conclusiones" },
    { id: 11, title: "Anexo", field: "anexo" },
  ];

  useEffect(() => {
    const fetchSiniestroData = async () => {
      try {
        const response = await axios.get(`/api/v1/siniestros/${siniestroId}`);
        const siniestro = response.data;
        setSiniestroInfo(siniestro);
        // Función auxiliar para parsear JSON arrays
        const parseJsonArray = (field: any): any[] => {
          if (!field) return [];
          try {
            return Array.isArray(field) ? field : JSON.parse(field);
          } catch {
            return [];
          }
        };

        setFormData({
          antecedentes: siniestro.antecedentes || [],
          relatos_asegurado: siniestro.relatos_asegurado || [],
          relatos_conductor: siniestro.relatos_conductor || [],
          inspecciones: siniestro.inspecciones || [],
          testigos: siniestro.testigos || [],
          evidencias_complementarias: parseJsonArray(siniestro.evidencias_complementarias),
          otras_diligencias: parseJsonArray(siniestro.otras_diligencias),
          visita_taller: parseJsonArray(siniestro.visita_taller),
          observaciones: parseJsonArray(siniestro.observaciones),
          recomendacion_pago_cobertura: parseJsonArray(siniestro.recomendacion_pago_cobertura),
          conclusiones: parseJsonArray(siniestro.conclusiones),
          anexo: parseJsonArray(siniestro.anexo),
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
                {tab.title}
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
                <div className="card-section">
                  <div className="form-group" style={{ marginTop: "20px" }}>
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
                      rows={8}
                      placeholder="Escriba aquí los antecedentes del caso..."
                      style={{
                        width: "100%",
                        padding: "15px",
                        border: "1px solid #dee2e6",
                        borderRadius: "5px",
                        fontSize: "16px",
                        lineHeight: "1.5",
                      }}
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
                      {saving ? "Guardando..." : "💾 Guardar"}
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

            {/* TAB 1: ENTREVISTA ASEGURADO */}
            {activeTab === 1 && (
              <div className="tab-section active">
                <div className="card-section">
                  <div className="card-header">
                    <div className="card-icon">👤</div>
                    <div>
                      <h3 className="card-title">Entrevista al Asegurado</h3>
                    </div>
                  </div>
                  <div className="form-group">
                    <button
                      type="button"
                      onClick={() => {
                        const currentRelatos = formData.relatos_asegurado || [];
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
                      {saving ? "Guardando..." : "💾 Guardar"}
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

            {/* TAB 2: ENTREVISTA CONDUCTOR */}
            {activeTab === 2 && (
              <div className="tab-section active">
                <div className="card-section">
                  <div className="card-header">
                    <div className="card-icon">👨‍🚗</div>
                    <div>
                      <h3 className="card-title">Entrevista al Conductor</h3>
                    </div>
                  </div>
                  <div className="form-group">
                    <button
                      type="button"
                      onClick={() => {
                        const currentRelatos = formData.relatos_conductor || [];
                        const nextNumero = currentRelatos.length + 1;
                        setFormData((prev) => ({
                          ...prev,
                          relatos_conductor: [
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
                  {(formData.relatos_conductor || []).map((relato, index) => (
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
                              relatos_conductor:
                                prev.relatos_conductor?.filter(
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
                              relatos_conductor:
                                prev.relatos_conductor?.map((r, i) =>
                                  i === index ? { ...r, texto: value } : r
                                ) || [],
                            }));
                          }}
                          rows={3}
                          placeholder="Escriba el relato del conductor..."
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
                                  relatos_conductor:
                                    prev.relatos_conductor?.map((r, i) =>
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
                          "relatos_conductor",
                          formData.relatos_conductor || []
                        )
                      }
                      disabled={saving}
                    >
                      {saving ? "Guardando..." : "💾 Guardar"}
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

            {/* TAB 3: INSPECCIÓN LUGAR */}
            {activeTab === 3 && (
              <div className="tab-section active">
                <div className="card-section">
                  <div className="card-header">
                    <div className="card-icon">🔍</div>
                    <div>
                      <h3 className="card-title">Inspección del Lugar</h3>
                    </div>
                  </div>
                  <div className="form-group">
                    <button
                      type="button"
                      onClick={() => {
                        const currentInspecciones = formData.inspecciones || [];
                        const nextNumero = currentInspecciones.length + 1;
                        setFormData((prev) => ({
                          ...prev,
                          inspecciones: [
                            ...currentInspecciones,
                            {
                              numero_inspeccion: nextNumero,
                              descripcion: "",
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
                      ➕ Agregar Inspección
                    </button>
                  </div>
                  {(formData.inspecciones || []).map((inspeccion, index) => (
                    <div key={index} className="dynamic-item">
                      <div className="dynamic-item-header">
                        <h4 className="dynamic-item-title">
                          Inspección {inspeccion.numero_inspeccion}
                        </h4>
                        <button
                          type="button"
                          className="btn-delete"
                          onClick={() => {
                            setFormData((prev) => ({
                              ...prev,
                              inspecciones:
                                prev.inspecciones?.filter(
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
                          value={inspeccion.descripcion}
                          onChange={(e) => {
                            const value = e.target.value;
                            setFormData((prev) => ({
                              ...prev,
                              inspecciones:
                                prev.inspecciones?.map((insp, i) =>
                                  i === index
                                    ? { ...insp, descripcion: value }
                                    : insp
                                ) || [],
                            }));
                          }}
                          rows={3}
                          placeholder="Describa la inspección realizada..."
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
                                  inspecciones:
                                    prev.inspecciones?.map((insp, i) =>
                                      i === index
                                        ? { ...insp, imagen_url: imageUrl }
                                        : insp
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
                        {inspeccion.imagen_url && (
                          <img
                            src={inspeccion.imagen_url}
                            alt={`Inspección ${inspeccion.numero_inspeccion}`}
                            style={{ maxWidth: "200px", marginTop: "5px" }}
                          />
                        )}
                      </div>
                    </div>
                  ))}
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
                          "inspecciones",
                          formData.inspecciones || []
                        )
                      }
                      disabled={saving}
                    >
                      {saving ? "Guardando..." : "💾 Guardar"}
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

            {/* TAB 4: TESTIGOS */}
            {activeTab === 4 && (
              <div className="tab-section active">
                <div className="card-section">
                  <div className="card-header">
                    <div className="card-icon">👥</div>
                    <div>
                      <h3 className="card-title">Testigos</h3>
                    </div>
                  </div>
                  <div className="form-group">
                    <button
                      type="button"
                      onClick={() => {
                        const currentTestigos = formData.testigos || [];
                        const nextNumero = currentTestigos.length + 1;
                        setFormData((prev) => ({
                          ...prev,
                          testigos: [
                            ...currentTestigos,
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
                      ➕ Agregar Testigo
                    </button>
                  </div>
                  {(formData.testigos || []).map((testigo, index) => (
                    <div key={index} className="dynamic-item">
                      <div className="dynamic-item-header">
                        <h4 className="dynamic-item-title">
                          Testigo {testigo.numero_relato}
                        </h4>
                        <button
                          type="button"
                          className="btn-delete"
                          onClick={() => {
                            setFormData((prev) => ({
                              ...prev,
                              testigos:
                                prev.testigos?.filter((_, i) => i !== index) ||
                                [],
                            }));
                          }}
                        >
                          ❌ Eliminar
                        </button>
                      </div>
                      <div className="form-group">
                        <textarea
                          value={testigo.texto}
                          onChange={(e) => {
                            const value = e.target.value;
                            setFormData((prev) => ({
                              ...prev,
                              testigos:
                                prev.testigos?.map((t, i) =>
                                  i === index ? { ...t, texto: value } : t
                                ) || [],
                            }));
                          }}
                          rows={3}
                          placeholder="Escriba el testimonio del testigo..."
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
                                  testigos:
                                    prev.testigos?.map((t, i) =>
                                      i === index
                                        ? { ...t, imagen_url: imageUrl }
                                        : t
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
                        {testigo.imagen_url && (
                          <img
                            src={testigo.imagen_url}
                            alt={`Testigo ${testigo.numero_relato}`}
                            style={{ maxWidth: "200px", marginTop: "5px" }}
                          />
                        )}
                      </div>
                    </div>
                  ))}
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
                        guardarSeccion("testigos", formData.testigos || [])
                      }
                      disabled={saving}
                    >
                      {saving ? "Guardando..." : "💾 Guardar"}
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

            {/* TAB 5: EVIDENCIAS COMPLEMENTARIAS */}
            {activeTab === 5 && (
              <div className="tab-section active">
                <div className="card-section">
                  <div className="card-header">
                    <div className="card-icon">📎</div>
                    <div>
                      <h3 className="card-title">Evidencias Complementarias</h3>
                    </div>
                  </div>
                  <div className="form-group">
                    <button
                      type="button"
                      onClick={() => {
                        const currentEvidencias = formData.evidencias_complementarias || [];
                        setFormData((prev) => ({
                          ...prev,
                          evidencias_complementarias: [
                            ...currentEvidencias,
                            {
                              descripcion: "",
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
                      ➕ Agregar Evidencia
                    </button>
                  </div>
                  {(formData.evidencias_complementarias || []).map((evidencia, index) => (
                    <div key={index} className="dynamic-item">
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
                              evidencias_complementarias:
                                prev.evidencias_complementarias?.filter(
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
                          value={evidencia.descripcion}
                          onChange={(e) => {
                            const value = e.target.value;
                            setFormData((prev) => ({
                              ...prev,
                              evidencias_complementarias:
                                prev.evidencias_complementarias?.map((r, i) =>
                                  i === index ? { ...r, descripcion: value } : r
                                ) || [],
                            }));
                          }}
                          rows={3}
                          placeholder="Describe la evidencia complementaria..."
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
                                  evidencias_complementarias:
                                    prev.evidencias_complementarias?.map((r, i) =>
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
                        {evidencia.imagen_url && (
                          <img
                            src={evidencia.imagen_url}
                            alt={`Evidencia ${index + 1}`}
                            style={{ maxWidth: "200px", marginTop: "5px" }}
                          />
                        )}
                      </div>
                    </div>
                  ))}
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
                          "evidencias_complementarias",
                          formData.evidencias_complementarias || []
                        )
                      }
                      disabled={saving}
                    >
                      {saving ? "Guardando..." : "💾 Guardar"}
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

            {/* TAB 6: OTRAS DILIGENCIAS */}
            {activeTab === 6 && (
              <div className="tab-section active">
                <div className="card-section">
                  <div className="card-header">
                    <div className="card-icon">📋</div>
                    <div>
                      <h3 className="card-title">Otras Diligencias</h3>
                    </div>
                  </div>
                  <div className="form-group">
                    <button
                      type="button"
                      onClick={() => {
                        const currentDiligencias = formData.otras_diligencias || [];
                        setFormData((prev) => ({
                          ...prev,
                          otras_diligencias: [
                            ...currentDiligencias,
                            {
                              descripcion: "",
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
                      ➕ Agregar Diligencia
                    </button>
                  </div>
                  {(formData.otras_diligencias || []).map((diligencia, index) => (
                    <div key={index} className="dynamic-item">
                      <div className="dynamic-item-header">
                        <h4 className="dynamic-item-title">
                          Diligencia {index + 1}
                        </h4>
                        <button
                          type="button"
                          className="btn-delete"
                          onClick={() => {
                            setFormData((prev) => ({
                              ...prev,
                              otras_diligencias:
                                prev.otras_diligencias?.filter(
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
                          value={diligencia.descripcion}
                          onChange={(e) => {
                            const value = e.target.value;
                            setFormData((prev) => ({
                              ...prev,
                              otras_diligencias:
                                prev.otras_diligencias?.map((r, i) =>
                                  i === index ? { ...r, descripcion: value } : r
                                ) || [],
                            }));
                          }}
                          rows={3}
                          placeholder="Describe la diligencia realizada..."
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
                                  otras_diligencias:
                                    prev.otras_diligencias?.map((r, i) =>
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
                        {diligencia.imagen_url && (
                          <img
                            src={diligencia.imagen_url}
                            alt={`Diligencia ${index + 1}`}
                            style={{ maxWidth: "200px", marginTop: "5px" }}
                          />
                        )}
                      </div>
                    </div>
                  ))}
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
                          "otras_diligencias",
                          formData.otras_diligencias || []
                        )
                      }
                      disabled={saving}
                    >
                      {saving ? "Guardando..." : "💾 Guardar"}
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

            {/* TAB 7: VISITA TALLER */}
            {activeTab === 7 && (
              <div className="tab-section active">
                <div className="card-section">
                  <div className="card-header">
                    <div className="card-icon">🏭</div>
                    <div>
                      <h3 className="card-title">Visita al Taller</h3>
                    </div>
                  </div>
                  <div className="form-group">
                    <button
                      type="button"
                      onClick={() => {
                        const currentVisitas = formData.visita_taller || [];
                        setFormData((prev) => ({
                          ...prev,
                          visita_taller: [
                            ...currentVisitas,
                            {
                              descripcion: "",
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
                      ➕ Agregar Visita
                    </button>
                  </div>
                  {(formData.visita_taller || []).map((visita, index) => (
                    <div key={index} className="dynamic-item">
                      <div className="dynamic-item-header">
                        <h4 className="dynamic-item-title">
                          Visita {index + 1}
                        </h4>
                        <button
                          type="button"
                          className="btn-delete"
                          onClick={() => {
                            setFormData((prev) => ({
                              ...prev,
                              visita_taller:
                                prev.visita_taller?.filter(
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
                          value={visita.descripcion}
                          onChange={(e) => {
                            const value = e.target.value;
                            setFormData((prev) => (({
                              ...prev,
                              visita_taller:
                                prev.visita_taller?.map((r, i) =>
                                  i === index ? { ...r, descripcion: value } : r
                                ) || [],
                            })));
                          }}
                          rows={3}
                          placeholder="Describe la visita al taller..."
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
                                  visita_taller:
                                    prev.visita_taller?.map((r, i) =>
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
                        {visita.imagen_url && (
                          <img
                            src={visita.imagen_url}
                            alt={`Visita ${index + 1}`}
                            style={{ maxWidth: "200px", marginTop: "5px" }}
                          />
                        )}
                      </div>
                    </div>
                  ))}
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
                          "visita_taller",
                          formData.visita_taller || []
                        )
                      }
                      disabled={saving}
                    >
                      {saving ? "Guardando..." : "💾 Guardar"}
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

            {/* TAB 8: OBSERVACIONES */}
            {activeTab === 8 && (
              <div className="tab-section active">
                <div className="card-section">
                  <div className="card-header">
                    <div className="card-icon">💭</div>
                    <div>
                      <h3 className="card-title">Observaciones</h3>
                    </div>
                  </div>
                  <div className="form-group">
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
                  </div>
                  {(formData.observaciones || []).map((observacion, index) => (
                    <div key={index} className="dynamic-item">
                      <div className="form-group">
                        <textarea
                          value={observacion}
                          onChange={(e) => {
                            const value = e.target.value;
                            const currentObservaciones =
                              formData.observaciones || [];
                            const newObservaciones = [...currentObservaciones];
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
                  ))}
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
                          "observaciones",
                          formData.observaciones || []
                        )
                      }
                      disabled={saving}
                    >
                      {saving ? "Guardando..." : "💾 Guardar"}
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

            {/* TAB 9: RECOMENDACIÓN PAGO */}
            {activeTab === 9 && (
              <div className="tab-section active">
                <div className="card-section">
                  <div className="card-header">
                    <div className="card-icon">💰</div>
                    <div>
                      <h3 className="card-title">
                        Recomendación sobre el Pago
                      </h3>
                    </div>
                  </div>
                  <div className="form-group">
                    <button
                      type="button"
                      onClick={() => {
                        const currentRecomendaciones =
                          formData.recomendacion_pago_cobertura || [];
                        setFormData((prev) => ({
                          ...prev,
                          recomendacion_pago_cobertura: [
                            ...currentRecomendaciones,
                            "",
                          ],
                        }));
                      }}
                      style={{
                        backgroundColor: "#28a745",
                        marginBottom: "10px",
                      }}
                    >
                      ➕ Agregar Recomendación
                    </button>
                  </div>
                  {(formData.recomendacion_pago_cobertura || []).map(
                    (recomendacion, index) => (
                      <div key={index} className="dynamic-item">
                        <div className="form-group">
                          <textarea
                            value={recomendacion}
                            onChange={(e) => {
                              const value = e.target.value;
                              const currentRecomendaciones =
                                formData.recomendacion_pago_cobertura || [];
                              const newRecomendaciones = [
                                ...currentRecomendaciones,
                              ];
                              newRecomendaciones[index] = value;
                              setFormData((prev) => ({
                                ...prev,
                                recomendacion_pago_cobertura:
                                  newRecomendaciones,
                              }));
                            }}
                            rows={3}
                            placeholder="Escribe la recomendación sobre el pago..."
                          />
                        </div>
                      </div>
                    )
                  )}
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
                          "recomendacion_pago_cobertura",
                          formData.recomendacion_pago_cobertura || []
                        )
                      }
                      disabled={saving}
                    >
                      {saving ? "Guardando..." : "💾 Guardar"}
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

            {/* TAB 10: CONCLUSIONES */}
            {activeTab === 10 && (
              <div className="tab-section active">
                <div className="card-section">
                  <div className="card-header">
                    <div className="card-icon">📊</div>
                    <div>
                      <h3 className="card-title">Conclusiones</h3>
                    </div>
                  </div>
                  <div className="form-group">
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
                  </div>
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
                          "conclusiones",
                          formData.conclusiones || []
                        )
                      }
                      disabled={saving}
                    >
                      {saving ? "Guardando..." : "💾 Guardar"}
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

            {/* TAB 11: ANEXO */}
            {activeTab === 11 && (
              <div className="tab-section active">
                <div className="card-section">
                  <div className="card-header">
                    <div className="card-icon">📄</div>
                    <div>
                      <h3 className="card-title">Anexo</h3>
                    </div>
                  </div>
                  <div className="form-group">
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
                              anexo: currentAnexo.filter((_, i) => i !== index),
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
                                await axios.post(
                                  "/api/v1/siniestros/upload-image",
                                  formDataUpload,
                                  {
                                    headers: {
                                      "Content-Type": "multipart/form-data",
                                    },
                                  }
                                );
                                // Documento subido exitosamente
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
                        guardarSeccion("anexo", formData.anexo || [])
                      }
                      disabled={saving}
                    >
                      {saving ? "Guardando..." : "💾 Guardar"}
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
