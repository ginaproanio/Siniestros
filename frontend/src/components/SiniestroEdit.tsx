import axios from "axios";
import React, { useEffect, useState } from "react";
import { useParams } from "react-router-dom";

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
  // Datos básicos del siniestro
  compania_seguros: string;
  ruc_compania?: string;
  tipo_reclamo?: string;
  poliza?: string;
  reclamo_num: string;
  fecha_siniestro: string;
  fecha_reportado?: string;
  direccion_siniestro: string;
  ubicacion_geo_lat?: number;
  ubicacion_geo_lng?: number;
  danos_terceros: boolean;
  ejecutivo_cargo?: string;
  fecha_designacion?: string;
  tipo_siniestro?: string;
  cobertura?: string;

  // Nuevos campos de declaración
  fecha_declaracion?: string;
  persona_declara_tipo?: string;
  persona_declara_cedula?: string;
  persona_declara_nombre?: string;
  persona_declara_relacion?: string;
  misiva_investigacion?: string;

  // Secciones dinámicas
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
  observaciones?: string[]; // Array of strings for numbered list
  recomendacion_pago_cobertura?: string[]; // Array of strings for numbered list
  conclusiones?: string[]; // Array of strings for numbered list
  anexo?: string[]; // Array of strings for numbered list

  // Datos relacionados
  asegurado?: any;
  beneficiario?: any;
  conductor?: any;
  objeto_asegurado?: any;
}

// Configurar base URL para el backend
const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
if (!BACKEND_URL) {
  console.error("REACT_APP_BACKEND_URL no está configurado");
}
axios.defaults.baseURL = BACKEND_URL;

const SiniestroEdit: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const [formData, setFormData] = useState<FormData>({
    // Datos básicos según backend schema
    compania_seguros: "Zurich Seguros Ecuador S.A.",
    reclamo_num: "",
    fecha_siniestro: "",
    direccion_siniestro: "",
    danos_terceros: false,
    tipo_siniestro: "Vehicular",
  });

  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState("");

  // Función para parsear arrays JSON
  const parseJsonArray = (jsonString: string | null): string[] => {
    if (!jsonString) return [];
    try {
      const parsed = JSON.parse(jsonString);
      return Array.isArray(parsed) ? parsed : [];
    } catch {
      return [];
    }
  };

  useEffect(() => {
    const fetchSiniestro = async () => {
      try {
        const response = await axios.get(`/api/v1/${id}`);
        const data = response.data;

        console.log("Datos cargados del siniestro:", data);

        setFormData({
          // Datos básicos
          compania_seguros:
            data.compania_seguros || "ZURICH SEGUROS ECUADOR S.A.",
          ruc_compania: data.ruc_compania || "",
          tipo_reclamo: data.tipo_reclamo || "",
          poliza: data.poliza || "",
          reclamo_num: data.reclamo_num || "",
          fecha_siniestro: data.fecha_siniestro
            ? new Date(data.fecha_siniestro).toISOString().split("T")[0]
            : "",
          fecha_reportado: data.fecha_reportado
            ? new Date(data.fecha_reportado).toISOString().split("T")[0]
            : "",
          direccion_siniestro: data.direccion_siniestro || "",
          ubicacion_geo_lat: data.ubicacion_geo_lat || undefined,
          ubicacion_geo_lng: data.ubicacion_geo_lng || undefined,
          danos_terceros: data.danos_terceros || false,
          ejecutivo_cargo: data.ejecutivo_cargo || "",
          fecha_designacion: data.fecha_designacion
            ? new Date(data.fecha_designacion).toISOString().split("T")[0]
            : "",
          tipo_siniestro: data.tipo_siniestro || "Vehicular",
          cobertura: data.cobertura || "",

          // Nuevos campos de declaración
          fecha_declaracion: data.fecha_declaracion
            ? new Date(data.fecha_declaracion).toISOString().split("T")[0]
            : "",
          persona_declara_tipo: data.persona_declara_tipo || "",
          persona_declara_cedula: data.persona_declara_cedula || "",
          persona_declara_nombre: data.persona_declara_nombre || "",
          persona_declara_relacion: data.persona_declara_relacion || "",
          misiva_investigacion: data.misiva_investigacion || "",

          // Secciones dinámicas
          antecedentes: data.antecedentes || [],
          relatos_asegurado: data.relatos_asegurado || [],
          inspecciones: data.inspecciones || [],
          testigos: data.testigos || [],

          // Campos de investigación recabada
          evidencias_complementarias_descripcion: data.evidencias_complementarias || "",
          evidencias_complementarias_imagen_url: data.evidencias_complementarias_imagen_url || "",
          otras_diligencias_descripcion: data.otras_diligencias || "",
          otras_diligencias_imagen_url: data.otras_diligencias_imagen_url || "",
          visita_taller_descripcion: data.visita_taller_descripcion || "",
          visita_taller_imagen_url: data.visita_taller_imagen_url || "",
          observaciones: parseJsonArray(data.observaciones),
          recomendacion_pago_cobertura: parseJsonArray(data.recomendacion_pago_cobertura),
          conclusiones: parseJsonArray(data.conclusiones),
          anexo: parseJsonArray(data.anexo),

          // Datos relacionados
          asegurado: data.asegurado || null,
          beneficiario: data.beneficiario || null,
          conductor: data.conductor || null,
          objeto_asegurado: data.objeto_asegurado || null,
        });
      } catch (error) {
        console.error("Error loading siniestro:", error);
        setMessage("Error al cargar los datos del siniestro");
      } finally {
        setLoading(false);
      }
    };

    if (id) {
      fetchSiniestro();
    }
  }, [id]);

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
    setSaving(true);
    setMessage("");

    console.log("🚀 Enviando datos actualizados:", formData);

    try {
      // Preparar datos para envío - serializar arrays a JSON strings
      const submitData = {
        ...formData,
        observaciones: JSON.stringify(formData.observaciones || []),
        recomendacion_pago_cobertura: JSON.stringify(formData.recomendacion_pago_cobertura || []),
        conclusiones: JSON.stringify(formData.conclusiones || []),
        anexo: JSON.stringify(formData.anexo || []),
      };

      await axios.put(`/api/v1/${id}`, submitData);
      setMessage("Siniestro actualizado exitosamente!");
      setTimeout(() => {
        window.location.href = `/siniestro/${id}`;
      }, 2000);
    } catch (error: any) {
      console.error("Error updating siniestro:", error);
      setMessage("Error al actualizar el siniestro");
    } finally {
      setSaving(false);
    }
  };

  if (loading) return <div>Cargando datos del siniestro...</div>;

  return (
    <div className="form-container">
      <h2>Editar Siniestro</h2>

      {/* INDICADOR DE PROGRESO */}
      <div style={{
        marginBottom: "30px",
        padding: "20px",
        backgroundColor: "#f8f9fa",
        borderRadius: "8px",
        border: "2px solid #007bff"
      }}>
        <h3 style={{ marginBottom: "15px", color: "#007bff" }}>📊 Progreso del Informe</h3>
        <div style={{
          display: "flex",
          flexWrap: "wrap",
          gap: "10px",
          fontSize: "14px"
        }}>
          <span style={{ padding: "5px 10px", backgroundColor: "#28a745", color: "white", borderRadius: "15px" }}>✅ 1. Datos Básicos</span>
          <span style={{ padding: "5px 10px", backgroundColor: "#28a745", color: "white", borderRadius: "15px" }}>✅ 2. Objeto Asegurado</span>
          <span style={{ padding: "5px 10px", backgroundColor: "#28a745", color: "white", borderRadius: "15px" }}>✅ 3. Antecedentes</span>
          <span style={{ padding: "5px 10px", backgroundColor: "#28a745", color: "white", borderRadius: "15px" }}>✅ 4. Entrevista Asegurado</span>
          <span style={{ padding: "5px 10px", backgroundColor: "#28a745", color: "white", borderRadius: "15px" }}>✅ 5. Inspección Lugar</span>
          <span style={{ padding: "5px 10px", backgroundColor: "#28a745", color: "white", borderRadius: "15px" }}>✅ 6. Testigos</span>
          <span style={{ padding: "5px 10px", backgroundColor: "#17a2b8", color: "white", borderRadius: "15px", fontWeight: "bold" }}>🔍 7. Investigación Recabada</span>
          <span style={{ padding: "5px 10px", backgroundColor: "#6c757d", color: "white", borderRadius: "15px" }}>⏳ 8. Generar PDF</span>
        </div>
        <p style={{ marginTop: "10px", fontSize: "12px", color: "#6c757d" }}>
          Estás en la sección 7: Investigación Recabada. Completa todas las secciones antes de generar el PDF.
        </p>
      </div>

      <form onSubmit={handleSubmit}>
        <div className="form-row">
          <div className="form-group">
            <label>RUC Compañía:</label>
            <input
              type="text"
              name="ruc_compania"
              value={formData.ruc_compania || ""}
              onChange={handleInputChange}
              placeholder="Ej: 1791240014001"
            />
          </div>
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
        </div>

        <div className="form-row">
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
          <div className="form-group">
            <label>Tipo de Reclamo:</label>
            <select
              name="tipo_reclamo"
              value={formData.tipo_reclamo || ""}
              onChange={handleInputChange}
            >
              <option value="">Seleccionar...</option>
              <option value="ROBO">Robo</option>
              <option value="ACCIDENTE">Accidente</option>
              <option value="INCENDIO">Incendio</option>
              <option value="OTRO">Otro</option>
            </select>
          </div>
          <div className="form-group">
            <label>Póliza:</label>
            <input
              type="text"
              name="poliza"
              value={formData.poliza || ""}
              onChange={handleInputChange}
              placeholder="Ej: 3351"
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
            <label>Fecha Reportado:</label>
            <input
              type="date"
              name="fecha_reportado"
              value={formData.fecha_reportado}
              onChange={handleInputChange}
            />
          </div>
        </div>

        <div className="form-row">
          <div className="form-group">
            <label>Fecha de Designación:</label>
            <input
              type="date"
              name="fecha_designacion"
              value={formData.fecha_designacion}
              onChange={handleInputChange}
            />
          </div>
          <div className="form-group">
            <label>Cobertura:</label>
            <input
              type="text"
              name="cobertura"
              value={formData.cobertura}
              onChange={handleInputChange}
              placeholder="Todo riesgo, etc."
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
              Daños a Terceros
              <input
                type="checkbox"
                name="danos_terceros"
                checked={formData.danos_terceros}
                onChange={handleInputChange}
              />
            </label>
          </div>
        </div>

        {/* OBJETO ASEGURADO */}
        <div
          style={{
            marginBottom: "30px",
            padding: "20px",
            backgroundColor: "#fff8e1",
            borderRadius: "8px",
          }}
        >
          <h3 style={{ color: "#0f172a", marginBottom: "15px" }}>
            🚗 Datos del Objeto Asegurado
          </h3>

          <div className="form-row">
            <div className="form-group">
              <label>Placa:</label>
              <input
                type="text"
                value={formData.objeto_asegurado?.placa || ""}
                onChange={(e) => {
                  const value = e.target.value;
                  setFormData((prev) => ({
                    ...prev,
                    objeto_asegurado: {
                      ...prev.objeto_asegurado,
                      placa: value,
                    },
                  }));
                }}
                placeholder="Ej: PFB4337"
              />
            </div>
            <div className="form-group">
              <label>Marca:</label>
              <input
                type="text"
                value={formData.objeto_asegurado?.marca || ""}
                onChange={(e) => {
                  const value = e.target.value;
                  setFormData((prev) => ({
                    ...prev,
                    objeto_asegurado: {
                      ...prev.objeto_asegurado,
                      marca: value,
                    },
                  }));
                }}
                placeholder="Ej: TOYOTA"
              />
            </div>
            <div className="form-group">
              <label>Modelo:</label>
              <input
                type="text"
                value={formData.objeto_asegurado?.modelo || ""}
                onChange={(e) => {
                  const value = e.target.value;
                  setFormData((prev) => ({
                    ...prev,
                    objeto_asegurado: {
                      ...prev.objeto_asegurado,
                      modelo: value,
                    },
                  }));
                }}
                placeholder="Ej: Corolla Cross High AC 1.8 5P 4x2"
              />
            </div>
          </div>

          <div className="form-row">
            <div className="form-group">
              <label>Tipo:</label>
              <input
                type="text"
                value={formData.objeto_asegurado?.tipo || ""}
                onChange={(e) => {
                  const value = e.target.value;
                  setFormData((prev) => ({
                    ...prev,
                    objeto_asegurado: { ...prev.objeto_asegurado, tipo: value },
                  }));
                }}
                placeholder="Ej: Jeep"
              />
            </div>
            <div className="form-group">
              <label>Color:</label>
              <input
                type="text"
                value={formData.objeto_asegurado?.color || ""}
                onChange={(e) => {
                  const value = e.target.value;
                  setFormData((prev) => ({
                    ...prev,
                    objeto_asegurado: {
                      ...prev.objeto_asegurado,
                      color: value,
                    },
                  }));
                }}
                placeholder="Ej: Blanco"
              />
            </div>
            <div className="form-group">
              <label>Año:</label>
              <input
                type="number"
                value={formData.objeto_asegurado?.ano || ""}
                onChange={(e) => {
                  const value = parseInt(e.target.value) || undefined;
                  setFormData((prev) => ({
                    ...prev,
                    objeto_asegurado: { ...prev.objeto_asegurado, ano: value },
                  }));
                }}
                placeholder="Ej: 2023"
              />
            </div>
          </div>

          <div className="form-row">
            <div className="form-group">
              <label>Serie Motor:</label>
              <input
                type="text"
                value={formData.objeto_asegurado?.serie_motor || ""}
                onChange={(e) => {
                  const value = e.target.value;
                  setFormData((prev) => ({
                    ...prev,
                    objeto_asegurado: {
                      ...prev.objeto_asegurado,
                      serie_motor: value,
                    },
                  }));
                }}
                placeholder="Ej: 2ZR2X01895"
              />
            </div>
            <div className="form-group">
              <label>Chasis:</label>
              <input
                type="text"
                value={formData.objeto_asegurado?.chasis || ""}
                onChange={(e) => {
                  const value = e.target.value;
                  setFormData((prev) => ({
                    ...prev,
                    objeto_asegurado: {
                      ...prev.objeto_asegurado,
                      chasis: value,
                    },
                  }));
                }}
                placeholder="Ej: 9BRKZAAGXR0669964"
              />
            </div>
          </div>
        </div>

        {/* ANTECEDENTES */}
        <div
          style={{
            marginBottom: "30px",
            padding: "20px",
            backgroundColor: "#f8f9fa",
            borderRadius: "8px",
          }}
        >
          <h3 style={{ color: "#0f172a", marginBottom: "15px" }}>
            📋 Antecedentes
          </h3>
          <div className="form-group">
            <label>Descripción de los antecedentes:</label>
            <textarea
              name="antecedentes_descripcion"
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
              rows={4}
              placeholder="Describa el aviso de siniestro, alcances de la investigación..."
            />
          </div>
        </div>

        {/* ENTREVISTA CON EL ASEGURADO */}
        <div
          style={{
            marginBottom: "30px",
            padding: "20px",
            backgroundColor: "#f8f9fa",
            borderRadius: "8px",
          }}
        >
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
                    { numero_relato: nextNumero, texto: "", imagen_url: "" },
                  ],
                }));
              }}
              style={{ backgroundColor: "#28a745", marginBottom: "10px" }}
            >
              ➕ Agregar Relato
            </button>
          </div>

          {formData.relatos_asegurado?.map((relato, index) => (
            <div
              key={index}
              style={{
                marginBottom: "20px",
                padding: "15px",
                backgroundColor: "#ffffff",
                borderRadius: "5px",
                border: "1px solid #e2e8f0",
              }}
            >
              <div
                style={{
                  display: "flex",
                  justifyContent: "space-between",
                  alignItems: "center",
                  marginBottom: "10px",
                }}
              >
                <h4 style={{ color: "#0f172a", margin: 0 }}>
                  Relato {relato.numero_relato}
                </h4>
                <button
                  type="button"
                  onClick={() => {
                    setFormData((prev) => ({
                      ...prev,
                      relatos_asegurado:
                        prev.relatos_asegurado?.filter((_, i) => i !== index) ||
                        [],
                    }));
                  }}
                  style={{
                    backgroundColor: "#dc3545",
                    color: "white",
                    border: "none",
                    borderRadius: "3px",
                    padding: "5px 10px",
                    cursor: "pointer",
                  }}
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
                            headers: { "Content-Type": "multipart/form-data" },
                          }
                        );

                        const imageUrl = response.data.url;
                        setFormData((prev) => ({
                          ...prev,
                          relatos_asegurado:
                            prev.relatos_asegurado?.map((r, i) =>
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
                      style={{
                        maxWidth: "200px",
                        maxHeight: "150px",
                        border: "1px solid #ddd",
                      }}
                    />
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>

        {/* INSPECCIÓN DEL LUGAR */}
        <div
          style={{
            marginBottom: "30px",
            padding: "20px",
            backgroundColor: "#f8f9fa",
            borderRadius: "8px",
          }}
        >
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

          {formData.inspecciones?.map((inspeccion, index) => (
            <div
              key={index}
              style={{
                marginBottom: "20px",
                padding: "15px",
                backgroundColor: "#ffffff",
                borderRadius: "5px",
                border: "1px solid #e2e8f0",
              }}
            >
              <div
                style={{
                  display: "flex",
                  justifyContent: "space-between",
                  alignItems: "center",
                  marginBottom: "10px",
                }}
              >
                <h4 style={{ color: "#0f172a", margin: 0 }}>
                  Inspección {inspeccion.numero_inspeccion}
                </h4>
                <button
                  type="button"
                  onClick={() => {
                    setFormData((prev) => ({
                      ...prev,
                      inspecciones:
                        prev.inspecciones?.filter((_, i) => i !== index) || [],
                    }));
                  }}
                  style={{
                    backgroundColor: "#dc3545",
                    color: "white",
                    border: "none",
                    borderRadius: "3px",
                    padding: "5px 10px",
                    cursor: "pointer",
                  }}
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
                      inspecciones:
                        prev.inspecciones?.map((insp, i) =>
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

                        const response = await axios.post(
                          "/api/v1/siniestros/upload-image",
                          formDataUpload,
                          {
                            headers: { "Content-Type": "multipart/form-data" },
                          }
                        );

                        const imageUrl = response.data.url;
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
                      style={{
                        maxWidth: "200px",
                        maxHeight: "150px",
                        border: "1px solid #ddd",
                      }}
                    />
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>

        {/* TESTIGOS */}
        <div
          style={{
            marginBottom: "30px",
            padding: "20px",
            backgroundColor: "#f8f9fa",
            borderRadius: "8px",
          }}
        >
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
                    { numero_relato: nextNumero, texto: "", imagen_url: "" },
                  ],
                }));
              }}
              style={{ backgroundColor: "#28a745", marginBottom: "10px" }}
            >
              ➕ Agregar Testigo
            </button>
          </div>

          {formData.testigos?.map((testigo, index) => (
            <div
              key={index}
              style={{
                marginBottom: "20px",
                padding: "15px",
                backgroundColor: "#ffffff",
                borderRadius: "5px",
                border: "1px solid #e2e8f0",
              }}
            >
              <div
                style={{
                  display: "flex",
                  justifyContent: "space-between",
                  alignItems: "center",
                  marginBottom: "10px",
                }}
              >
                <h4 style={{ color: "#0f172a", margin: 0 }}>
                  Testigo {testigo.numero_relato}
                </h4>
                <button
                  type="button"
                  onClick={() => {
                    setFormData((prev) => ({
                      ...prev,
                      testigos:
                        prev.testigos?.filter((_, i) => i !== index) || [],
                    }));
                  }}
                  style={{
                    backgroundColor: "#dc3545",
                    color: "white",
                    border: "none",
                    borderRadius: "3px",
                    padding: "5px 10px",
                    cursor: "pointer",
                  }}
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
                      testigos:
                        prev.testigos?.map((test, i) =>
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

                        const response = await axios.post(
                          "/api/v1/siniestros/upload-image",
                          formDataUpload,
                          {
                            headers: { "Content-Type": "multipart/form-data" },
                          }
                        );

                        const imageUrl = response.data.url;
                        setFormData((prev) => ({
                          ...prev,
                          testigos:
                            prev.testigos?.map((test, i) =>
                              i === index
                                ? { ...test, imagen_url: imageUrl }
                                : test
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
                      style={{
                        maxWidth: "200px",
                        maxHeight: "150px",
                        border: "1px solid #ddd",
                      }}
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

                      const response = await axios.post(
                        "/api/v1/siniestros/upload-image",
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
                      "/api/v1/siniestros/upload-image",
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
                      "/api/v1/siniestros/upload-image",
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

        <div style={{ display: "flex", gap: "10px", marginTop: "20px" }}>
          <button
            type="button"
            onClick={() => window.history.back()}
            style={{ backgroundColor: "#6c757d" }}
          >
            Cancelar
          </button>
          <button type="submit" disabled={saving}>
            {saving ? "Guardando..." : "Actualizar Siniestro"}
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

export default SiniestroEdit;
