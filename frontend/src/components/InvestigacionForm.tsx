import axios from "axios";
import React, { useEffect, useState } from "react";
import { useParams } from "react-router-dom";

const BACKEND_URL =
  process.env.REACT_APP_BACKEND_URL ||
  "https://siniestros-production.up.railway.app";
axios.defaults.baseURL = BACKEND_URL;

interface InvestigationData {
  antecedentes?: string;
  relatos_asegurado?: string[];
}

const InvestigacionForm: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const siniestroId = parseInt(id || "0");

  const [activeTab, setActiveTab] = useState(0);
  const [data, setData] = useState<InvestigationData>({
    antecedentes: "",
    relatos_asegurado: [""],
  });
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState("");
  const [siniestroInfo, setSiniestroInfo] = useState<any>(null);

  const tabs = [
    { id: 0, title: "Antecedentes", field: "antecedentes" },
    { id: 1, title: "Entrevista Asegurado", field: "relatos_asegurado" },
  ];

  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await axios.get(`/api/v1/siniestros/${siniestroId}`);
        const siniestro = response.data;
        setSiniestroInfo(siniestro);

        // Cargar antecedentes existentes
        const antecedentesExistentes = siniestro.antecedentes || [];
        const textoAntecedentes = antecedentesExistentes.length > 0
          ? antecedentesExistentes[0]?.descripcion || ""
          : "";

        // Cargar relatos del asegurado existentes
        const relatosExistentes = siniestro.relatos_asegurado || [];
        const textosRelatos = relatosExistentes.map((r: any) => r.texto || "");

        // Asegurar al menos un relato vacío si no hay ninguno
        const relatos = textosRelatos.length > 0 ? textosRelatos : [""];

        setData({
          antecedentes: textoAntecedentes,
          relatos_asegurado: relatos,
        });
      } catch (error) {
        console.error("Error loading data:", error);
        setMessage("Error al cargar datos del siniestro");
      } finally {
        setLoading(false);
      }
    };

    if (siniestroId) fetchData();
  }, [siniestroId]);

  const saveRelatosAsegurado = async () => {
    if (!data.relatos_asegurado || data.relatos_asegurado.length === 0) {
      setMessage("No hay relatos para guardar");
      return;
    }

    setSaving(true);
    setMessage("");

    try {
      // Filtrar relatos vacíos antes de enviar
      const relatosValidos = data.relatos_asegurado
        .map((texto) => ({ texto: texto.trim() }))
        .filter((relato) => relato.texto.length > 0);

      if (relatosValidos.length === 0) {
        setMessage("⚠️ No hay relatos con contenido para guardar");
        return;
      }

      console.log("📤 Enviando relatos:", relatosValidos);

      const response = await axios.put(
        `/api/v1/siniestros/${siniestroId}/seccion/relatos_asegurado`,
        relatosValidos
      );

      console.log("✅ Respuesta del servidor:", response.data);
      setMessage("✅ Relatos del asegurado guardados exitosamente");
    } catch (error: any) {
      console.error("❌ Error guardando relatos:", error);
      let errorMessage = "Error al guardar los relatos";

      if (error.response) {
        const status = error.response.status;
        const data = error.response.data;
        errorMessage = `Error ${status}: ${
          data.detail || data.message || "Error del servidor"
        }`;
      } else if (error.request) {
        errorMessage = "No se pudo conectar al servidor";
      }

      setMessage(errorMessage);
    } finally {
      setSaving(false);
    }
  };

  const addRelato = () => {
    setData((prev) => ({
      ...prev,
      relatos_asegurado: [...(prev.relatos_asegurado || []), ""],
    }));
  };

  const updateRelato = (index: number, value: string) => {
    setData((prev) => {
      const newRelatos = [...(prev.relatos_asegurado || [])];
      newRelatos[index] = value;
      return { ...prev, relatos_asegurado: newRelatos };
    });
  };

  const removeRelato = (index: number) => {
    setData((prev) => {
      const newRelatos = (prev.relatos_asegurado || []).filter(
        (_, i) => i !== index
      );
      // Asegurar al menos un relato
      return {
        ...prev,
        relatos_asegurado: newRelatos.length > 0 ? newRelatos : [""],
      };
    });
  };

  const saveCurrentTab = async () => {
    const currentTab = tabs[activeTab];
    setSaving(true);
    setMessage("");

    try {
      if (currentTab.field === "antecedentes") {
        // Guardar antecedentes
        const antecedentesData = [{ descripcion: data.antecedentes || "" }];
        await axios.put(
          `/api/v1/siniestros/${siniestroId}/seccion/antecedentes`,
          antecedentesData
        );
        setMessage("✅ Antecedentes guardados");
      } else if (currentTab.field === "relatos_asegurado") {
        // Guardar relatos del asegurado
        const relatosValidos = (data.relatos_asegurado || [])
          .map((texto) => ({ texto: texto.trim() }))
          .filter((relato) => relato.texto.length > 0);

        if (relatosValidos.length > 0) {
          await axios.put(
            `/api/v1/siniestros/${siniestroId}/seccion/relatos_asegurado`,
            relatosValidos
          );
          setMessage("✅ Relatos del asegurado guardados");
        } else {
          setMessage("⚠️ No hay relatos con contenido para guardar");
        }
      }
    } catch (error: any) {
      console.error(`❌ Error guardando ${currentTab.title}:`, error);
      let errorMessage = `Error guardando ${currentTab.title}`;

      if (error.response) {
        const status = error.response.status;
        const errorData = error.response.data;
        errorMessage = `Error ${status}: ${
          errorData.detail || errorData.message || "Error del servidor"
        }`;
      } else if (error.request) {
        errorMessage = "No se pudo conectar al servidor";
      }

      setMessage(errorMessage);
    } finally {
      setSaving(false);
    }
  };

  const handleTabChange = async (newTab: number) => {
    if (activeTab !== newTab) {
      // Guardar la pestaña actual antes de cambiar
      await saveCurrentTab();
      // Cambiar a la nueva pestaña
      setActiveTab(newTab);
    }
  };

  const updateAntecedentes = (value: string) => {
    setData((prev) => ({ ...prev, antecedentes: value }));
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

      {/* PESTAÑAS */}
      <div className="tabs-container">
        <div className="tabs-header">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              type="button"
              className={`tab-button${activeTab === tab.id ? " active" : ""}`}
              onClick={() => handleTabChange(tab.id)}
              disabled={saving}
            >
              {tab.title}
            </button>
          ))}
        </div>

        <div className="tab-content">
          {/* PESTAÑA 0: ANTECEDENTES */}
          {activeTab === 0 && (
            <div className="tab-section active">
              <div className="card-section investigacion-section">
                <div className="card-header">
                  <div className="card-icon">📋</div>
                  <div>
                    <h3 className="card-title">Antecedentes del Caso</h3>
                    <p className="card-description">
                      Información histórica y antecedentes relevantes del siniestro
                    </p>
                  </div>
                </div>
                <div className="form-group" style={{ marginTop: "20px" }}>
                  <textarea
                    value={data.antecedentes || ""}
                    onChange={(e) => updateAntecedentes(e.target.value)}
                    rows={8}
                    placeholder="Escriba aquí los antecedentes del caso..."
                    style={{
                      width: "100%",
                      padding: "12px 16px",
                      borderRadius: "4px",
                      border: "1px solid #ddd",
                      fontSize: "16px",
                      lineHeight: "1.5",
                    }}
                  />
                </div>
              </div>
            </div>
          )}

          {/* PESTAÑA 1: ENTREVISTA ASEGURADO */}
          {activeTab === 1 && (
            <div className="tab-section active">
              <div className="card-section investigacion-section">
                <div className="card-header">
                  <div className="card-icon">👤</div>
                  <div>
                    <h3 className="card-title">Entrevista al Asegurado</h3>
                    <p className="card-description">
                      Relatos y declaraciones obtenidas del asegurado
                    </p>
                  </div>
                  <button
                    type="button"
                    onClick={addRelato}
                    style={{
                      backgroundColor: "#28a745",
                      color: "white",
                      border: "none",
                      padding: "8px 16px",
                      borderRadius: "4px",
                    }}
                  >
                    ➕ Agregar Relato
                  </button>
                </div>

                {(data.relatos_asegurado || []).map((relato, index) => (
                  <div key={index} className="dynamic-item">
                    <div className="dynamic-item-header">
                      <h4 className="dynamic-item-title">Relato {index + 1}</h4>
                      <button
                        type="button"
                        className="btn-delete"
                        onClick={() => removeRelato(index)}
                      >
                        ❌ Eliminar
                      </button>
                    </div>
                    <div className="form-group">
                      <textarea
                        value={relato}
                        onChange={(e) => updateRelato(index, e.target.value)}
                        rows={4}
                        placeholder="Escriba el relato del asegurado..."
                        style={{
                          width: "100%",
                          padding: "12px 16px",
                          borderRadius: "4px",
                          border: "1px solid #ddd",
                          fontSize: "16px",
                          lineHeight: "1.5",
                        }}
                      />
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>

      {message && (
        <div
          className={`message ${
            message.includes("Error") ? "error" : "success"
          }`}
          style={{
            marginTop: "20px",
            padding: "10px",
            borderRadius: "4px",
            textAlign: "center",
            fontWeight: "bold",
          }}
        >
          {message}
        </div>
      )}
    </div>
  );
};

export default InvestigacionForm;
