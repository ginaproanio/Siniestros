import axios from "axios";
import React, { useEffect, useState } from "react";
import { useParams } from "react-router-dom";

const BACKEND_URL =
  process.env.REACT_APP_BACKEND_URL ||
  "https://siniestros-production.up.railway.app";
axios.defaults.baseURL = BACKEND_URL;

interface RelatoData {
  texto: string;
  imagen_url?: string;
}

interface InvestigationData {
  antecedentes?: string;
  relatos_asegurado?: RelatoData[];
}

const InvestigacionForm: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const siniestroId = parseInt(id || "0");

  const [activeTab, setActiveTab] = useState(0);
  const [data, setData] = useState<InvestigationData>({
    antecedentes: "",
    relatos_asegurado: [{ texto: "", imagen_url: "" }],
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
        const relatosObjetos = relatosExistentes.map((r: any) => ({
          texto: r.texto || "",
          imagen_url: r.imagen_url || ""
        }));

        // Asegurar al menos un relato vacío si no hay ninguno
        const relatos = relatosObjetos.length > 0 ? relatosObjetos : [{ texto: "", imagen_url: "" }];

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



  const addRelato = () => {
    setData((prev) => ({
      ...prev,
      relatos_asegurado: [...(prev.relatos_asegurado || []), { texto: "", imagen_url: "" }],
    }));
  };

  const updateRelato = (index: number, value: string) => {
    setData((prev) => {
      const newRelatos = [...(prev.relatos_asegurado || [])];
      newRelatos[index] = { ...newRelatos[index], texto: value };
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
        relatos_asegurado: newRelatos.length > 0 ? newRelatos : [{ texto: "", imagen_url: "" }],
      };
    });
  };

  const saveCurrentTab = async () => {
    const currentTab = tabs[activeTab];
    setSaving(true);
    setMessage("");

    try {
      if (currentTab.field === "antecedentes") {
        // Guardar antecedentes solo si tienen contenido
        const antecedentesTexto = data.antecedentes?.trim() || "";
        if (antecedentesTexto.length > 0) {
          const antecedentesData = [{ descripcion: antecedentesTexto }];
          await axios.put(
            `/api/v1/siniestros/${siniestroId}/seccion/antecedentes`,
            antecedentesData
          );
          setMessage("✅ Antecedentes guardados");
        } else {
          setMessage("⚠️ Antecedentes vacíos - no se guardaron");
        }
      } else if (currentTab.field === "relatos_asegurado") {
        // Guardar relatos del asegurado
        const relatosValidos = (data.relatos_asegurado || [])
          .map((relato) => ({ texto: relato.texto.trim(), imagen_url: relato.imagen_url || "" }))
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
    // Cambiar de pestaña libremente SIN guardar automáticamente
    setActiveTab(newTab);
    setMessage(""); // Limpiar mensajes al cambiar de pestaña
  };

  const updateAntecedentes = (value: string) => {
    setData((prev) => ({ ...prev, antecedentes: value }));
  };

  const uploadImageForRelato = async (index: number, file: File) => {
    try {
      // Crear URL local para preview inmediato
      const localUrl = URL.createObjectURL(file);

      // Actualizar el relato con la URL local inmediatamente para feedback visual
      setData((prev) => {
        const newRelatos = [...(prev.relatos_asegurado || [])];
        newRelatos[index] = { ...newRelatos[index], imagen_url: localUrl };
        return { ...prev, relatos_asegurado: newRelatos };
      });

      // Intentar subir a S3 en segundo plano
      try {
        const formData = new FormData();
        formData.append('file', file);

        const response = await axios.post('/api/v1/siniestros/upload-image', formData, {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
        });

        const s3Url = response.data.url_presigned;

        // Actualizar con la URL de S3
        setData((prev) => {
          const newRelatos = [...(prev.relatos_asegurado || [])];
          newRelatos[index] = { ...newRelatos[index], imagen_url: s3Url };
          return { ...prev, relatos_asegurado: newRelatos };
        });

        setMessage("✅ Imagen subida correctamente a S3");
      } catch (s3Error) {
        console.warn("⚠️ S3 upload failed, keeping local URL:", s3Error);
        setMessage("⚠️ Imagen cargada localmente (S3 no disponible)");
      }
    } catch (error) {
      console.error("Error procesando imagen:", error);
      setMessage("❌ Error al procesar la imagen");
    }
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

                {/* BOTÓN GUARDAR ANTECEDENTES */}
                <div className="tab-navigation" style={{ justifyContent: "center", marginTop: "20px" }}>
                  <button
                    type="button"
                    className="btn-submit-tab"
                    onClick={() => saveCurrentTab()}
                    disabled={saving}
                    style={{
                      backgroundColor: "#007bff",
                      color: "white",
                      border: "none",
                      padding: "12px 24px",
                      borderRadius: "4px",
                      fontSize: "16px",
                      cursor: saving ? "not-allowed" : "pointer",
                    }}
                  >
                    {saving ? "💾 Guardando..." : "💾 Guardar Antecedentes"}
                  </button>
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
                        value={relato.texto}
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

                    {/* IMAGEN PARA ESTE RELATO */}
                    <div className="form-group" style={{ marginTop: "12px" }}>
                      <label style={{ display: "block", marginBottom: "8px", fontWeight: "500" }}>
                        📷 Imagen del Relato (opcional)
                      </label>
                      <div style={{ display: "flex", gap: "12px", alignItems: "center" }}>
                        <input
                          type="file"
                          accept="image/*"
                          onChange={(e) => {
                            const file = e.target.files?.[0];
                            if (file) {
                              uploadImageForRelato(index, file);
                            }
                          }}
                          style={{
                            flex: 1,
                            padding: "8px",
                            border: "1px solid #ddd",
                            borderRadius: "4px",
                          }}
                        />
                        {relato.imagen_url && (
                          <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
                            <span style={{ fontSize: "12px", color: "#28a745" }}>
                              ✅ Imagen subida
                            </span>
                            <img
                              src={relato.imagen_url}
                              alt={`Relato ${index + 1}`}
                              style={{
                                width: "40px",
                                height: "40px",
                                objectFit: "cover",
                                borderRadius: "4px",
                                border: "1px solid #ddd",
                              }}
                            />
                          </div>
                        )}
                      </div>
                    </div>
                  </div>
                ))}

                {/* BOTÓN GUARDAR RELATOS ASEGURADO */}
                <div className="tab-navigation" style={{ justifyContent: "center", marginTop: "20px" }}>
                  <button
                    type="button"
                    className="btn-submit-tab"
                    onClick={() => saveCurrentTab()}
                    disabled={saving}
                    style={{
                      backgroundColor: "#007bff",
                      color: "white",
                      border: "none",
                      padding: "12px 24px",
                      borderRadius: "4px",
                      fontSize: "16px",
                      cursor: saving ? "not-allowed" : "pointer",
                    }}
                  >
                    {saving ? "💾 Guardando..." : "💾 Guardar Relatos"}
                  </button>
                </div>
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
