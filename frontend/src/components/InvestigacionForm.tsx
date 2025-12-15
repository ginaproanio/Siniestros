import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import axios from 'axios';

// Configurar base URL para el backend
const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || 'https://siniestros-production.up.railway.app';
console.log('🌐 Backend URL:', BACKEND_URL);
axios.defaults.baseURL = BACKEND_URL;

interface AntecedenteData {
  descripcion: string;
}

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

interface FormData {
  // Secciones de investigación
  antecedentes?: AntecedenteData[];
  relatos_asegurado?: RelatoData[];
  inspecciones?: InspeccionData[];
  testigos?: TestigoData[];

  // Campos de investigación recabada
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
  const siniestroId = parseInt(id || '0');

  const [formData, setFormData] = useState<FormData>({});
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState('');
  const [siniestroInfo, setSiniestroInfo] = useState<any>(null);

  useEffect(() => {
    if (siniestroId) {
      fetchSiniestroData();
    }
  }, [siniestroId]);

  const fetchSiniestroData = async () => {
    try {
      const response = await axios.get(`/api/v1/siniestros/${siniestroId}`);
      const siniestro = response.data;
      setSiniestroInfo(siniestro);

      // Cargar datos de investigación existentes
      setFormData({
        antecedentes: siniestro.antecedentes || [],
        relatos_asegurado: siniestro.relatos_asegurado || [],
        inspecciones: siniestro.inspecciones || [],
        testigos: siniestro.testigos || [],
        evidencias_complementarias_descripcion: siniestro.evidencias_complementarias_descripcion,
        evidencias_complementarias_imagen_url: siniestro.evidencias_complementarias_imagen_url,
        otras_diligencias_descripcion: siniestro.otras_diligencias_descripcion,
        otras_diligencias_imagen_url: siniestro.otras_diligencias_imagen_url,
        visita_taller_descripcion: siniestro.visita_taller_descripcion,
        visita_taller_imagen_url: siniestro.visita_taller_imagen_url,
        observaciones: siniestro.observaciones || [],
        recomendacion_pago_cobertura: siniestro.recomendacion_pago_cobertura || [],
        conclusiones: siniestro.conclusiones || [],
        anexo: siniestro.anexo || []
      });
    } catch (error) {
      console.error('Error fetching siniestro data:', error);
      setMessage('Error al cargar los datos del siniestro');
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setMessage('');

    try {
      await axios.put(`/api/v1/siniestros/${siniestroId}`, formData);
      setMessage('✅ Investigación guardada exitosamente');
    } catch (error: any) {
      console.error('Error saving investigation:', error);
      setMessage('❌ Error al guardar la investigación');
    } finally {
      setLoading(false);
    }
  };

  const handleInputChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>
  ) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }));
  };

  return (
    <div className="form-container">
      <div className="form-header">
        <h2>Registrar Investigación - Siniestro #{siniestroId}</h2>
        {siniestroInfo && (
          <div style={{ marginTop: '10px', padding: '10px', backgroundColor: '#f8f9fa', borderRadius: '5px' }}>
            <strong>Reclamo:</strong> {siniestroInfo.reclamo_num} |
            <strong> Compañía:</strong> {siniestroInfo.compania_seguros} |
            <strong> Fecha:</strong> {new Date(siniestroInfo.fecha_siniestro).toLocaleDateString()}
          </div>
        )}
      </div>

      <form onSubmit={handleSubmit}>
        {/* ANTECEDENTES */}
        <div className="card-section" style={{ marginBottom: "20px", backgroundColor: "#f8f9fa" }}>
          <h4 style={{ color: "#0f172a", marginBottom: "15px" }}>
            📋 Antecedentes
          </h4>
          <div className="form-group">
            <label>Descripción de los antecedentes:</label>
            <textarea
              name="antecedentes_descripcion"
              value={(formData.antecedentes && formData.antecedentes[0]?.descripcion) || ""}
              onChange={(e) => {
                const value = e.target.value;
                setFormData((prev) => ({
                  ...prev,
                  antecedentes: [{ descripcion: value }],
                }));
              }}
              rows={4}
              placeholder="Describa el aviso de siniestro, alcances de la investigación..."
            />
          </div>
        </div>

        {/* ENTREVISTA CON EL ASEGURADO */}
        <div style={{ marginBottom: "30px", padding: "20px", backgroundColor: "#f8f9fa", borderRadius: "8px" }}>
          <h3 style={{ color: "#0f172a", marginBottom: "15px" }}>
            🎤 Entrevista con el Asegurado
          </h3>
          <div style={{ marginBottom: "15px" }}>
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
              style={{ backgroundColor: "#28a745", marginBottom: "10px" }}
            >
              ➕ Agregar Relato
            </button>
          </div>

          {(formData.relatos_asegurado || []).map((relato, index) => (
            <div key={index} style={{ marginBottom: "20px", padding: "15px", backgroundColor: "#ffffff", borderRadius: "5px", border: "1px solid #e2e8f0" }}>
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "10px" }}>
                <h4 style={{ color: "#0f172a", margin: 0 }}>
                  Relato {relato.numero_relato}
                </h4>
                <button
                  type="button"
                  onClick={() => {
                    setFormData((prev) => ({
                      ...prev,
                      relatos_asegurado: prev.relatos_asegurado?.filter((_, i) => i !== index) || [],
                    }));
                  }}
                  style={{ backgroundColor: "#dc3545", color: "white", border: "none", borderRadius: "3px", padding: "5px 10px", cursor: "pointer" }}
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

                        const response = await axios.post("/api/v1/upload-image", formDataUpload, {
                          headers: { "Content-Type": "multipart/form-data" },
                        });

                        const imageUrl = response.data.url;
                        setFormData((prev) => ({
                          ...prev,
                          relatos_asegurado: prev.relatos_asegurado?.map((r, i) =>
                            i === index ? { ...r, imagen_url: imageUrl } : r
                          ) || [],
                        }));
                      } catch (error) {
                        console.error("Error subiendo imagen:", error);
                        alert("Error al subir la imagen. Intente nuevamente.");
                      }
                    }
                  }}
                />
                {relato.imagen_url && (
                  <div style={{ marginTop: "5px" }}>
                    <img
                      src={`${BACKEND_URL}${relato.imagen_url}`}
                      alt={`Relato ${relato.numero_relato}`}
                      style={{ maxWidth: "200px", maxHeight: "150px", border: "1px solid #ddd" }}
                    />
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>

        {/* INSPECCIÓN DEL LUGAR */}
        <div style={{ marginBottom: "30px", padding: "20px", backgroundColor: "#f8f9fa", borderRadius: "8px" }}>
          <h3 style={{ color: "#0f172a", marginBottom: "15px" }}>
            🔍 Inspección del Lugar
          </h3>
          <div style={{ marginBottom: "15px" }}>
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
              style={{ backgroundColor: "#28a745", marginBottom: "10px" }}
            >
              ➕ Agregar Inspección
            </button>
          </div>

          {(formData.inspecciones || []).map((inspeccion, index) => (
            <div key={index} style={{ marginBottom: "20px", padding: "15px", backgroundColor: "#ffffff", borderRadius: "5px", border: "1px solid #e2e8f0" }}>
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "10px" }}>
                <h4 style={{ color: "#0f172a", margin: 0 }}>
                  Inspección {inspeccion.numero_inspeccion}
                </h4>
                <button
                  type="button"
                  onClick={() => {
                    setFormData((prev) => ({
                      ...prev,
                      inspecciones: prev.inspecciones?.filter((_, i) => i !== index) || [],
                    }));
                  }}
                  style={{ backgroundColor: "#dc3545", color: "white", border: "none", borderRadius: "3px", padding: "5px 10px", cursor: "pointer" }}
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
                      ) || [],
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
                        formDataUpload.append("file", file);

                        const response = await axios.post("/api/v1/upload-image", formDataUpload, {
                          headers: { "Content-Type": "multipart/form-data" },
                        });

                        const imageUrl = response.data.url;
                        setFormData((prev) => ({
                          ...prev,
                          inspecciones: prev.inspecciones?.map((insp, i) =>
                            i === index ? { ...insp, imagen_url: imageUrl } : insp
                          ) || [],
                        }));
                      } catch (error) {
                        console.error("Error subiendo imagen:", error);
                        alert("Error al subir la imagen. Intente nuevamente.");
                      }
                    }
                  }}
                />
                {inspeccion.imagen_url && (
                  <div style={{ marginTop: "5px" }}>
                    <img
                      src={`${BACKEND_URL}${inspeccion.imagen_url}`}
                      alt={`Inspección ${inspeccion.numero_inspeccion}`}
                      style={{ maxWidth: "200px", maxHeight: "150px", border: "1px solid #ddd" }}
                    />
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>

        {/* TESTIGOS */}
        <div style={{ marginBottom: "30px", padding: "20px", backgroundColor: "#f8f9fa", borderRadius: "8px" }}>
          <h3 style={{ color: "#0f172a", marginBottom: "15px" }}>
            👥 Testigos
          </h3>
          <div style={{ marginBottom: "15px" }}>
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
              style={{ backgroundColor: "#28a745", marginBottom: "10px" }}
            >
              ➕ Agregar Testigo
            </button>
          </div>

          {(formData.testigos || []).map((testigo, index) => (
            <div key={index} style={{ marginBottom: "20px", padding: "15px", backgroundColor: "#ffffff", borderRadius: "5px", border: "1px solid #e2e8f0" }}>
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "10px" }}>
                <h4 style={{ color: "#0f172a", margin: 0 }}>
                  Testigo {testigo.numero_relato}
                </h4>
                <button
                  type="button"
                  onClick={() => {
                    setFormData((prev) => ({
                      ...prev,
                      testigos: prev.testigos?.filter((_, i) => i !== index) || [],
                    }));
                  }}
                  style={{ backgroundColor: "#dc3545", color: "white", border: "none", borderRadius: "3px", padding: "5px 10px", cursor: "pointer" }}
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
                      ) || [],
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
                        formDataUpload.append("file", file);

                        const response = await axios.post("/api/v1/upload-image", formDataUpload, {
                          headers: { "Content-Type": "multipart/form-data" },
                        });

                        const imageUrl = response.data.url;
                        setFormData((prev) => ({
                          ...prev,
                          testigos: prev.testigos?.map((test, i) =>
                            i === index ? { ...test, imagen_url: imageUrl } : test
                          ) || [],
                        }));
                      } catch (error) {
                        console.error("Error subiendo imagen:", error);
                        alert("Error al subir la imagen. Intente nuevamente.");
                      }
                    }
                  }}
                />
                {testigo.imagen_url && (
                  <div style={{ marginTop: "5px" }}>
                    <img
                      src={`${BACKEND_URL}${testigo.imagen_url}`}
                      alt={`Testigo ${testigo.numero_relato}`}
                      style={{ maxWidth: "200px", maxHeight: "150px", border: "1px solid #ddd" }}
                    />
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>

        {/* SECCIONES DE INVESTIGACIÓN RECABADA */}
        <div style={{ marginTop: "50px", padding: "30px", backgroundColor: "#e8f5e8", borderRadius: "15px", border: "4px solid #28a745", boxShadow: "0 6px 12px rgba(0,0,0,0.15)" }}>
          <h2 style={{ color: "#0f172a", marginBottom: "20px", fontSize: "28px", fontWeight: "bold", textAlign: "center" }}>
            🔍 SECCIONES DE INVESTIGACIÓN RECABADA
          </h2>
          <p style={{ color: "#666", fontSize: "18px", marginBottom: "30px", fontStyle: "italic", textAlign: "center" }}>
            Complete todas las secciones siguientes para completar la investigación del siniestro
          </p>
        </div>

        {/* EVIDENCIAS COMPLEMENTARIAS */}
        <div className="section-container">
          <h3 className="section-header">📎 Evidencias Complementarias</h3>
          <div className="form-group">
            <label>Descripción:</label>
            <textarea
              name="evidencias_complementarias_descripcion"
              value={formData.evidencias_complementarias_descripcion || ""}
              onChange={handleInputChange}
              rows={4}
              placeholder="Describe las evidencias complementarias..."
            />
          </div>

          {/* Mostrar campo de imagen solo si contiene "Parte Policial" */}
          {(formData.evidencias_complementarias_descripcion || "").toLowerCase().includes("parte policial") && (
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

                      const response = await axios.post("/api/v1/upload-image", formDataUpload, {
                        headers: { "Content-Type": "multipart/form-data" },
                      });

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
              name="otras_diligencias_descripcion"
              value={formData.otras_diligencias_descripcion || ""}
              onChange={handleInputChange}
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

                    const response = await axios.post("/api/v1/upload-image", formDataUpload, {
                      headers: { "Content-Type": "multipart/form-data" },
                    });

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
              name="visita_taller_descripcion"
              value={formData.visita_taller_descripcion || ""}
              onChange={handleInputChange}
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

                    const response = await axios.post("/api/v1/upload-image", formDataUpload, {
                      headers: { "Content-Type": "multipart/form-data" },
                    });

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
            onClick={() => {
              const currentObservaciones = formData.observaciones || [];
              setFormData((prev) => ({
                ...prev,
                observaciones: [...currentObservaciones, ""],
              }));
            }}
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
                  onClick={() => {
                    const currentObservaciones = formData.observaciones || [];
                    setFormData((prev) => ({
                      ...prev,
                      observaciones: currentObservaciones.filter((_, i) => i !== index),
                    }));
                  }}
                >
                  ❌ Eliminar
                </button>
              </div>

              <div className="form-group">
                <textarea
                  value={observacion}
                  onChange={(e) => {
                    const value = e.target.value;
                    const currentObservaciones = formData.observaciones || [];
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
        </div>

        {/* RECOMENDACIÓN SOBRE EL PAGO DE LA COBERTURA */}
        <div className="section-container">
          <h3 className="section-header">💰 Recomendación (Sobre el Pago de la Cobertura)</h3>
          <button
            type="button"
            className="btn-add"
            onClick={() => {
              const currentRecomendaciones = formData.recomendacion_pago_cobertura || [];
              setFormData((prev) => ({
                ...prev,
                recomendacion_pago_cobertura: [...currentRecomendaciones, ""],
              }));
            }}
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
                  onClick={() => {
                    const currentRecomendaciones = formData.recomendacion_pago_cobertura || [];
                    setFormData((prev) => ({
                      ...prev,
                      recomendacion_pago_cobertura: currentRecomendaciones.filter((_, i) => i !== index),
                    }));
                  }}
                >
                  ❌ Eliminar
                </button>
              </div>

              <div className="form-group">
                <textarea
                  value={recomendacion}
                  onChange={(e) => {
                    const value = e.target.value;
                    const currentRecomendaciones = formData.recomendacion_pago_cobertura || [];
                    const newRecomendaciones = [...currentRecomendaciones];
                    newRecomendaciones[index] = value;
                    setFormData((prev) => ({
                      ...prev,
                      recomendacion_pago_cobertura: newRecomendaciones,
                    }));
                  }}
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
            onClick={() => {
              const currentConclusiones = formData.conclusiones || [];
              setFormData((prev) => ({
                ...prev,
                conclusiones: [...currentConclusiones, ""],
              }));
            }}
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
                  onClick={() => {
                    const currentConclusiones = formData.conclusiones || [];
                    setFormData((prev) => ({
                      ...prev,
                      conclusiones: currentConclusiones.filter((_, i) => i !== index),
                    }));
                  }}
                >
                  ❌ Eliminar
                </button>
              </div>

              <div className="form-group">
                <textarea
                  value={conclusion}
                  onChange={(e) => {
                    const value = e.target.value;
                    const currentConclusiones = formData.conclusiones || [];
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

        {/* ANEXO */}
        <div className="section-container">
          <h3 className="section-header">📎 Anexo</h3>
          <button
            type="button"
            className="btn-add"
            onClick={() => {
              const currentAnexo = formData.anexo || [];
              setFormData((prev) => ({
                ...prev,
                anexo: [...currentAnexo, ""],
              }));
            }}
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
            </div>
          ))}
        </div>

        {/* Submit Button */}
        <div style={{ justifyContent: "center", padding: "20px" }}>
          <button type="submit" className="btn-submit-tab" disabled={loading}>
            {loading ? "Guardando..." : "💾 Guardar Investigación"}
          </button>
        </div>
      </form>

      {message && (
        <div className={`message ${message.includes("Error") ? "error" : "success"}`}>
          {message}
        </div>
      )}
    </div>
  );
};

export default InvestigacionForm;
