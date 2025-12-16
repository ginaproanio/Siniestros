import axios from "axios";
import React, { useEffect, useState } from "react";
import { useParams } from "react-router-dom";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || "https://siniestros-production.up.railway.app";
axios.defaults.baseURL = BACKEND_URL;

interface InvestigationData {
  antecedentes?: string;
  relatos_asegurado?: string[];
  relatos_conductor?: string[];
  inspecciones?: string[];
  testigos?: string[];
  evidencias_complementarias?: string[];
  otras_diligencias?: string[];
  visita_taller?: string[];
  observaciones?: string[];
  recomendacion_pago_cobertura?: string[];
  conclusiones?: string[];
  anexo?: string[];
}

const InvestigacionForm: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const siniestroId = parseInt(id || "0");

  const [activeTab, setActiveTab] = useState(0);
  const [data, setData] = useState<InvestigationData>({});
  const [loading, setLoading] = useState(true);
  const [message, setMessage] = useState("");
  const [siniestroInfo, setSiniestroInfo] = useState<any>(null);

  const tabs = [
    { id: 0, title: "Antecedentes", field: "antecedentes" },
    { id: 1, title: "Entrevista Asegurado", field: "relatos_asegurado" },
    { id: 2, title: "Entrevista Conductor", field: "relatos_conductor" },
    { id: 3, title: "Inspección Lugar", field: "inspecciones" },
    { id: 4, title: "Testigos", field: "testigos" },
    { id: 5, title: "Evidencias Complementarias", field: "evidencias_complementarias" },
    { id: 6, title: "Otras Diligencias", field: "otras_diligencias" },
    { id: 7, title: "Visita Taller", field: "visita_taller" },
    { id: 8, title: "Observaciones", field: "observaciones" },
    { id: 9, title: "Recomendación Pago", field: "recomendacion_pago_cobertura" },
    { id: 10, title: "Conclusiones", field: "conclusiones" },
    { id: 11, title: "Anexo", field: "anexo" },
  ];

  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await axios.get(`/api/v1/siniestros/${siniestroId}`);
        const siniestro = response.data;
        setSiniestroInfo(siniestro);

        const parseArray = (field: any): string[] => {
          if (!field) return [];
          try {
            return Array.isArray(field) ? field : JSON.parse(field);
          } catch {
            return [];
          }
        };

        setData({
          antecedentes: siniestro.antecedentes?.[0]?.descripcion || "",
          relatos_asegurado: parseArray(siniestro.relatos_asegurado?.map((r: any) => r.texto)),
          relatos_conductor: parseArray(siniestro.relatos_conductor?.map((r: any) => r.texto)),
          inspecciones: parseArray(siniestro.inspecciones?.map((i: any) => i.descripcion)),
          testigos: parseArray(siniestro.testigos?.map((t: any) => t.texto)),
          evidencias_complementarias: parseArray(siniestro.evidencias_complementarias),
          otras_diligencias: parseArray(siniestro.otras_diligencias),
          visita_taller: parseArray(siniestro.visita_taller),
          observaciones: parseArray(siniestro.observaciones),
          recomendacion_pago_cobertura: parseArray(siniestro.recomendacion_pago_cobertura),
          conclusiones: parseArray(siniestro.conclusiones),
          anexo: parseArray(siniestro.anexo),
        });
      } catch (error) {
        console.error("Error loading data:", error);
        setMessage("Error al cargar datos");
      } finally {
        setLoading(false);
      }
    };

    if (siniestroId) fetchData();
  }, [siniestroId]);

  const handleTabChange = async (newTab: number) => {
    if (activeTab !== newTab) {
      await saveCurrentTab();
      setActiveTab(newTab);
    }
  };

  const saveCurrentTab = async () => {
    const currentTab = tabs[activeTab];
    const fieldData = data[currentTab.field as keyof InvestigationData];

    if (fieldData) {
      try {
        await axios.put(`/api/v1/siniestros/${siniestroId}/seccion/${currentTab.field}`, fieldData);
        console.log(`✅ ${currentTab.title} guardado`);
      } catch (error) {
        console.error(`❌ Error guardando ${currentTab.title}:`, error);
      }
    }
  };

  const updateField = (field: keyof InvestigationData, value: any) => {
    setData(prev => ({ ...prev, [field]: value }));
  };

  const addItem = (field: keyof InvestigationData) => {
    const currentArray = (data[field] as string[]) || [];
    updateField(field, [...currentArray, ""]);
  };

  const updateItem = (field: keyof InvestigationData, index: number, value: string) => {
    const currentArray = (data[field] as string[]) || [];
    const newArray = [...currentArray];
    newArray[index] = value;
    updateField(field, newArray);
  };

  const removeItem = (field: keyof InvestigationData, index: number) => {
    const currentArray = (data[field] as string[]) || [];
    updateField(field, currentArray.filter((_, i) => i !== index));
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
          <div style={{ marginTop: "10px", padding: "10px", backgroundColor: "#f8f9fa", borderRadius: "5px" }}>
            <strong>Reclamo:</strong> {siniestroInfo.reclamo_num} |
            <strong> Compañía:</strong> {siniestroInfo.compania_seguros} |
            <strong> Fecha:</strong> {new Date(siniestroInfo.fecha_siniestro).toLocaleDateString()}
          </div>
        )}
      </div>

      <div className="tabs-container">
        <div className="tabs-header">
          {tabs.map((tab) => {
            const isActive = activeTab === tab.id;
            return (
              <button
                key={tab.id}
                type="button"
                className={`tab-button${isActive ? " active" : ""}`}
                onClick={() => goToTab(tab.id)}
              >
                {tab.title}
              </button>
            );
          })}
        </div>

        <div className="tab-content">
          <form onSubmit={(e) => e.preventDefault()}>
            {/* TAB 0: ANTECEDENTES */}
            {activeTab === 0 && (
              <div className="tab-section active">
                <div className="card-section">
                  <div className="form-group" style={{ marginTop: "20px" }}>
                    <textarea
                      value={data.antecedentes || ""}
                      onChange={(e) => updateField("antecedentes", e.target.value)}
                      rows={8}
                      placeholder="Escriba aquí los antecedentes del caso..."
                    />
                  </div>
                  <div className="tab-navigation">
                    <button type="button" className="btn-submit-tab" onClick={() => saveCurrentTab()}>
                      💾 Guardar
                    </button>
                    <button type="button" className="btn-next" onClick={nextTab}>Siguiente →</button>
                  </div>
                </div>
              </div>
            )}

            {/* TAB 1: ENTREVISTA ASEGURADO */}
            {activeTab === 1 && (
              <div className="tab-section active">
                <div className="card-section">
                  <div className="card-header">
                    <h3 className="card-title">Entrevista al Asegurado</h3>
                    <button type="button" onClick={() => addItem("relatos_asegurado")}
                      style={{ backgroundColor: "#28a745", color: "white", border: "none", padding: "8px 16px", borderRadius: "4px" }}>
                      ➕ Agregar Relato
                    </button>
                  </div>
                  {(data.relatos_asegurado || []).map((relato, index) => (
                    <div key={index} className="dynamic-item">
                      <div className="dynamic-item-header">
                        <h4 className="dynamic-item-title">Relato {index + 1}</h4>
                        <button type="button" className="btn-delete" onClick={() => removeItem("relatos_asegurado", index)}>
                          ❌ Eliminar
                        </button>
                      </div>
                      <div className="form-group">
                        <textarea
                          value={relato}
                          onChange={(e) => updateItem("relatos_asegurado", index, e.target.value)}
                          rows={3}
                          placeholder="Escriba el relato del asegurado..."
                        />
                      </div>
                    </div>
                  ))}
                  <div className="tab-navigation">
                    <button type="button" className="btn-prev" onClick={prevTab}>← Anterior</button>
                    <button type="button" className="btn-submit-tab" onClick={() => saveCurrentTab()}>
                      💾 Guardar
                    </button>
                    <button type="button" className="btn-next" onClick={nextTab}>Siguiente →</button>
                  </div>
                </div>
              </div>
            )}

            {/* TAB 2: ENTREVISTA CONDUCTOR */}
            {activeTab === 2 && (
              <div className="tab-section active">
                <div className="card-section">
                  <div className="card-header">
                    <h3 className="card-title">Entrevista al Conductor</h3>
                    <button type="button" onClick={() => addItem("relatos_conductor")}
                      style={{ backgroundColor: "#28a745", color: "white", border: "none", padding: "8px 16px", borderRadius: "4px" }}>
                      ➕ Agregar Relato
                    </button>
                  </div>
                  {(data.relatos_conductor || []).map((relato, index) => (
                    <div key={index} className="dynamic-item">
                      <div className="dynamic-item-header">
                        <h4 className="dynamic-item-title">Relato {index + 1}</h4>
                        <button type="button" className="btn-delete" onClick={() => removeItem("relatos_conductor", index)}>
                          ❌ Eliminar
                        </button>
                      </div>
                      <div className="form-group">
                        <textarea
                          value={relato}
                          onChange={(e) => updateItem("relatos_conductor", index, e.target.value)}
                          rows={3}
                          placeholder="Escriba el relato del conductor..."
                        />
                      </div>
                    </div>
                  ))}
                  <div className="tab-navigation">
                    <button type="button" className="btn-prev" onClick={prevTab}>← Anterior</button>
                    <button type="button" className="btn-submit-tab" onClick={() => saveCurrentTab()}>
                      💾 Guardar
                    </button>
                    <button type="button" className="btn-next" onClick={nextTab}>Siguiente →</button>
                  </div>
                </div>
              </div>
            )}

            {/* TAB 3: INSPECCIÓN LUGAR */}
            {activeTab === 3 && (
              <div className="tab-section active">
                <div className="card-section">
                  <div className="card-header">
                    <h3 className="card-title">Inspección del Lugar</h3>
                    <button type="button" onClick={() => addItem("inspecciones")}
                      style={{ backgroundColor: "#28a745", color: "white", border: "none", padding: "8px 16px", borderRadius: "4px" }}>
                      ➕ Agregar Inspección
                    </button>
                  </div>
                  {(data.inspecciones || []).map((inspeccion, index) => (
                    <div key={index} className="dynamic-item">
                      <div className="dynamic-item-header">
                        <h4 className="dynamic-item-title">Inspección {index + 1}</h4>
                        <button type="button" className="btn-delete" onClick={() => removeItem("inspecciones", index)}>
                          ❌ Eliminar
                        </button>
                      </div>
                      <div className="form-group">
                        <textarea
                          value={inspeccion}
                          onChange={(e) => updateItem("inspecciones", index, e.target.value)}
                          rows={3}
                          placeholder="Describa la inspección realizada..."
                        />
                      </div>
                    </div>
                  ))}
                  <div className="tab-navigation">
                    <button type="button" className="btn-prev" onClick={prevTab}>← Anterior</button>
                    <button type="button" className="btn-submit-tab" onClick={() => saveCurrentTab()}>
                      💾 Guardar
                    </button>
                    <button type="button" className="btn-next" onClick={nextTab}>Siguiente →</button>
                  </div>
                </div>
              </div>
            )}

            {/* TAB 4: TESTIGOS */}
            {activeTab === 4 && (
              <div className="tab-section active">
                <div className="card-section">
                  <div className="card-header">
                    <h3 className="card-title">Testigos</h3>
                    <button type="button" onClick={() => addItem("testigos")}
                      style={{ backgroundColor: "#28a745", color: "white", border: "none", padding: "8px 16px", borderRadius: "4px" }}>
                      ➕ Agregar Testigo
                    </button>
                  </div>
                  {(data.testigos || []).map((testigo, index) => (
                    <div key={index} className="dynamic-item">
                      <div className="dynamic-item-header">
                        <h4 className="dynamic-item-title">Testigo {index + 1}</h4>
                        <button type="button" className="btn-delete" onClick={() => removeItem("testigos", index)}>
                          ❌ Eliminar
                        </button>
                      </div>
                      <div className="form-group">
                        <textarea
                          value={testigo}
                          onChange={(e) => updateItem("testigos", index, e.target.value)}
                          rows={3}
                          placeholder="Escriba el testimonio del testigo..."
                        />
                      </div>
                    </div>
                  ))}
                  <div className="tab-navigation">
                    <button type="button" className="btn-prev" onClick={prevTab}>← Anterior</button>
                    <button type="button" className="btn-submit-tab" onClick={() => saveCurrentTab()}>
                      💾 Guardar
                    </button>
                    <button type="button" className="btn-next" onClick={nextTab}>Siguiente →</button>
                  </div>
                </div>
              </div>
            )}

            {/* TAB 5: EVIDENCIAS COMPLEMENTARIAS */}
            {activeTab === 5 && (
              <div className="tab-section active">
                <div className="card-section">
                  <div className="card-header">
                    <h3 className="card-title">Evidencias Complementarias</h3>
                    <button type="button" onClick={() => addItem("evidencias_complementarias")}
                      style={{ backgroundColor: "#28a745", color: "white", border: "none", padding: "8px 16px", borderRadius: "4px" }}>
                      ➕ Agregar Evidencia
                    </button>
                  </div>
                  {(data.evidencias_complementarias || []).map((evidencia, index) => (
                    <div key={index} className="dynamic-item">
                      <div className="dynamic-item-header">
                        <h4 className="dynamic-item-title">Evidencia {index + 1}</h4>
                        <button type="button" className="btn-delete" onClick={() => removeItem("evidencias_complementarias", index)}>
                          ❌ Eliminar
                        </button>
                      </div>
                      <div className="form-group">
                        <textarea
                          value={evidencia}
                          onChange={(e) => updateItem("evidencias_complementarias", index, e.target.value)}
                          rows={3}
                          placeholder="Describe la evidencia complementaria..."
                        />
                      </div>
                    </div>
                  ))}
                  <div className="tab-navigation">
                    <button type="button" className="btn-prev" onClick={prevTab}>← Anterior</button>
                    <button type="button" className="btn-submit-tab" onClick={() => saveCurrentTab()}>
                      💾 Guardar
                    </button>
                    <button type="button" className="btn-next" onClick={nextTab}>Siguiente →</button>
                  </div>
                </div>
              </div>
            )}

            {/* TAB 6: OTRAS DILIGENCIAS */}
            {activeTab === 6 && (
              <div className="tab-section active">
                <div className="card-section">
                  <div className="card-header">
                    <h3 className="card-title">Otras Diligencias</h3>
                    <button type="button" onClick={() => addItem("otras_diligencias")}
                      style={{ backgroundColor: "#28a745", color: "white", border: "none", padding: "8px 16px", borderRadius: "4px" }}>
                      ➕ Agregar Diligencia
                    </button>
                  </div>
                  {(data.otras_diligencias || []).map((diligencia, index) => (
                    <div key={index} className="dynamic-item">
                      <div className="dynamic-item-header">
                        <h4 className="dynamic-item-title">Diligencia {index + 1}</h4>
                        <button type="button" className="btn-delete" onClick={() => removeItem("otras_diligencias", index)}>
                          ❌ Eliminar
                        </button>
                      </div>
                      <div className="form-group">
                        <textarea
                          value={diligencia}
                          onChange={(e) => updateItem("otras_diligencias", index, e.target.value)}
                          rows={3}
                          placeholder="Describe la diligencia realizada..."
                        />
                      </div>
                    </div>
                  ))}
                  <div className="tab-navigation">
                    <button type="button" className="btn-prev" onClick={prevTab}>← Anterior</button>
                    <button type="button" className="btn-submit-tab" onClick={() => saveCurrentTab()} disabled={saving}>
                      {saving ? "Guardando..." : "💾 Guardar"}
                    </button>
                    <button type="button" className="btn-next" onClick={nextTab}>Siguiente →</button>
                  </div>
                </div>
              </div>
            )}

            {/* TAB 7: VISITA TALLER */}
            {activeTab === 7 && (
              <div className="tab-section active">
                <div className="card-section">
                  <div className="card-header">
                    <h3 className="card-title">Visita al Taller</h3>
                    <button type="button" onClick={() => addItem("visita_taller")}
                      style={{ backgroundColor: "#28a745", color: "white", border: "none", padding: "8px 16px", borderRadius: "4px" }}>
                      ➕ Agregar Visita
                    </button>
                  </div>
                  {(data.visita_taller || []).map((visita, index) => (
                    <div key={index} className="dynamic-item">
                      <div className="dynamic-item-header">
                        <h4 className="dynamic-item-title">Visita {index + 1}</h4>
                        <button type="button" className="btn-delete" onClick={() => removeItem("visita_taller", index)}>
                          ❌ Eliminar
                        </button>
                      </div>
                      <div className="form-group">
                        <textarea
                          value={visita}
                          onChange={(e) => updateItem("visita_taller", index, e.target.value)}
                          rows={3}
                          placeholder="Describe la visita al taller..."
                        />
                      </div>
                    </div>
                  ))}
                  <div className="tab-navigation">
                    <button type="button" className="btn-prev" onClick={prevTab}>← Anterior</button>
                    <button type="button" className="btn-submit-tab" onClick={() => saveCurrentTab()} disabled={saving}>
                      {saving ? "Guardando..." : "💾 Guardar"}
                    </button>
                    <button type="button" className="btn-next" onClick={nextTab}>Siguiente →</button>
                  </div>
                </div>
              </div>
            )}

            {/* TAB 8: OBSERVACIONES */}
            {activeTab === 8 && (
              <div className="tab-section active">
                <div className="card-section">
                  <div className="card-header">
                    <h3 className="card-title">Observaciones</h3>
                    <button type="button" onClick={() => addItem("observaciones")}
                      style={{ backgroundColor: "#28a745", color: "white", border: "none", padding: "8px 16px", borderRadius: "4px" }}>
                      ➕ Agregar Observación
                    </button>
                  </div>
                  {(data.observaciones || []).map((observacion, index) => (
                    <div key={index} className="dynamic-item">
                      <div className="form-group">
                        <textarea
                          value={observacion}
                          onChange={(e) => updateItem("observaciones", index, e.target.value)}
                          rows={3}
                          placeholder="Escribe la observación..."
                        />
                      </div>
                    </div>
                  ))}
                  <div className="tab-navigation">
                    <button type="button" className="btn-prev" onClick={prevTab}>← Anterior</button>
                    <button type="button" className="btn-submit-tab" onClick={() => saveCurrentTab()} disabled={saving}>
                      {saving ? "Guardando..." : "💾 Guardar"}
                    </button>
                    <button type="button" className="btn-next" onClick={nextTab}>Siguiente →</button>
                  </div>
                </div>
              </div>
            )}

            {/* TAB 9: RECOMENDACIÓN PAGO */}
            {activeTab === 9 && (
              <div className="tab-section active">
                <div className="card-section">
                  <div className="card-header">
                    <h3 className="card-title">Recomendación sobre el Pago</h3>
                    <button type="button" onClick={() => addItem("recomendacion_pago_cobertura")}
                      style={{ backgroundColor: "#28a745", color: "white", border: "none", padding: "8px 16px", borderRadius: "4px" }}>
                      ➕ Agregar Recomendación
                    </button>
                  </div>
                  {(data.recomendacion_pago_cobertura || []).map((recomendacion, index) => (
                    <div key={index} className="dynamic-item">
                      <div className="form-group">
                        <textarea
                          value={recomendacion}
                          onChange={(e) => updateItem("recomendacion_pago_cobertura", index, e.target.value)}
                          rows={3}
                          placeholder="Escribe la recomendación sobre el pago..."
                        />
                      </div>
                    </div>
                  ))}
                  <div className="tab-navigation">
                    <button type="button" className="btn-prev" onClick={prevTab}>← Anterior</button>
                    <button type="button" className="btn-submit-tab" onClick={() => saveCurrentTab()} disabled={saving}>
                      {saving ? "Guardando..." : "💾 Guardar"}
                    </button>
                    <button type="button" className="btn-next" onClick={nextTab}>Siguiente →</button>
                  </div>
                </div>
              </div>
            )}

            {/* TAB 10: CONCLUSIONES */}
            {activeTab === 10 && (
              <div className="tab-section active">
                <div className="card-section">
                  <div className="card-header">
                    <h3 className="card-title">Conclusiones</h3>
                    <button type="button" onClick={() => addItem("conclusiones")}
                      style={{ backgroundColor: "#28a745", color: "white", border: "none", padding: "8px 16px", borderRadius: "4px" }}>
                      ➕ Agregar Conclusión
                    </button>
                  </div>
                  {(data.conclusiones || []).map((conclusion, index) => (
                    <div key={index} className="dynamic-item">
                      <div className="form-group">
                        <textarea
                          value={conclusion}
                          onChange={(e) => updateItem("conclusiones", index, e.target.value)}
                          rows={3}
                          placeholder="Escribe la conclusión..."
                        />
                      </div>
                    </div>
                  ))}
                  <div className="tab-navigation">
                    <button type="button" className="btn-prev" onClick={prevTab}>← Anterior</button>
                    <button type="button" className="btn-submit-tab" onClick={() => saveCurrentTab()} disabled={saving}>
                      {saving ? "Guardando..." : "💾 Guardar"}
                    </button>
                    <button type="button" className="btn-next" onClick={nextTab}>Siguiente →</button>
                  </div>
                </div>
              </div>
            )}

            {/* TAB 11: ANEXO */}
            {activeTab === 11 && (
              <div className="tab-section active">
                <div className="card-section">
                  <div className="card-header">
                    <h3 className="card-title">Anexo</h3>
                    <button type="button" onClick={() => addItem("anexo")}
                      style={{ backgroundColor: "#28a745", color: "white", border: "none", padding: "8px 16px", borderRadius: "4px" }}>
                      ➕ Agregar Anexo
                    </button>
                  </div>
                  {(data.anexo || []).map((anexoItem, index) => (
                    <div key={index} className="dynamic-item">
                      <div className="dynamic-item-header">
                        <h4 className="dynamic-item-title">Anexo {index + 1}</h4>
                        <button type="button" className="btn-delete" onClick={() => removeItem("anexo", index)}>
                          ❌ Eliminar
                        </button>
                      </div>
                      <div className="form-group">
                        <textarea
                          value={anexoItem}
                          onChange={(e) => updateItem("anexo", index, e.target.value)}
                          rows={3}
                          placeholder="Escribe el anexo..."
                        />
                      </div>
                    </div>
                  ))}
                  <div className="tab-navigation">
                    <button type="button" className="btn-prev" onClick={prevTab}>← Anterior</button>
                    <button type="button" className="btn-submit-tab" onClick={() => saveCurrentTab()} disabled={saving}>
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
        <div className={`message ${message.includes("Error") ? "error" : "success"}`}>
          {message}
        </div>
      )}
    </div>
  );
};

export default InvestigacionForm;
