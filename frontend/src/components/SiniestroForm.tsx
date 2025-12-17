import axios from "axios";
import React, { useState } from "react";
import { useParams } from "react-router-dom";

// Configurar base URL para el backend
const BACKEND_URL =
  process.env.REACT_APP_BACKEND_URL ||
  "https://siniestros-production.up.railway.app";
console.log("🌐 Backend URL:", BACKEND_URL);
axios.defaults.baseURL = BACKEND_URL;

// Interfaces para futuras expansiones del formulario
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

  // Nuevos campos de declaración (fecha_reportado es la fecha de declaración)
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

  // Datos relacionados
  asegurado?: any;
  beneficiario?: any;
  conductor?: any;
  objeto_asegurado?: any;
}

const SiniestroForm: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const isEditMode = Boolean(id);
  const siniestroId = parseInt(id || '0');

  const [activeTab, setActiveTab] = useState(0);
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState("");

  const [formData, setFormData] = useState<FormData>({
    compania_seguros: "ZURICH SEGUROS ECUADOR S.A.",
    ruc_compania: "1791240014001",
    tipo_reclamo: "ROBO",
    poliza: "3351",
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

  const tabs = [
    { id: 0, title: "Información Básica", icon: "📋" },
    { id: 1, title: "Parametrización", icon: "⚙️" },
    { id: 2, title: "Entidades", icon: "👥" },
  ];

  const goToTab = (tabId: number) => {
    setActiveTab(tabId);
  };

  // Cargar datos si estamos editando
  React.useEffect(() => {
    if (isEditMode && siniestroId) {
      const fetchSiniestro = async () => {
        try {
          const response = await axios.get(`/api/v1/siniestros/${siniestroId}`);
          const data = response.data;

          setFormData({
            compania_seguros: data.compania_seguros || "ZURICH SEGUROS ECUADOR S.A.",
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
            persona_declara_tipo: data.persona_declara_tipo || "",
            persona_declara_cedula: data.persona_declara_cedula || "",
            persona_declara_nombre: data.persona_declara_nombre || "",
            persona_declara_relacion: data.persona_declara_relacion || "",
            misiva_investigacion: data.misiva_investigacion || "",
            antecedentes: data.antecedentes || [],
            relatos_asegurado: data.relatos_asegurado || [],
            inspecciones: data.inspecciones || [],
            testigos: data.testigos || [],
            asegurado: data.asegurado || null,
            beneficiario: data.beneficiario || null,
            conductor: data.conductor || null,
            objeto_asegurado: data.objeto_asegurado || null,
          });
        } catch (error) {
          console.error("Error loading siniestro:", error);
          setMessage("Error al cargar los datos del siniestro");
        }
      };

      fetchSiniestro();
    }
  }, [isEditMode, siniestroId]);

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

    console.log("🚀 Enviando datos del formulario:", formData);

    try {
      let response;
      if (isEditMode) {
        response = await axios.put(`/api/v1/siniestros/${siniestroId}`, formData);
        setMessage("✅ Siniestro actualizado exitosamente!");
      } else {
        response = await axios.post("/api/v1/siniestros/", formData);
        setMessage("✅ Siniestro creado exitosamente!");
      }
      console.log("✅ Respuesta del servidor:", response);
      setTimeout(() => {
        window.location.href = "/siniestros";
      }, 2000);
    } catch (error: any) {
      console.error("❌ Error completo:", error);
      let errorMessage = isEditMode ? "Error al actualizar el siniestro" : "Error al crear el siniestro";

      if (error.response) {
        const status = error.response.status;
        const data = error.response.data;

        switch (status) {
          case 400:
            errorMessage = `Datos inválidos: ${
              data.detail || "Verifica los campos requeridos"
            }`;
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
      setSaving(false);
    }
  };

  return (
    <div className="form-container">
      <div className="form-header">
        <h2>{isEditMode ? `Editar Siniestro #${siniestroId}` : 'Registro de Siniestro'}</h2>
      </div>

      {/* Tab Navigation */}
      <div className="tabs-container">
        <div className="tabs-header" style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
          <div style={{ display: "flex" }}>
            {tabs.map((tab) => {
              const isActive = activeTab === tab.id;
              const buttonClass = `tab-button${isActive ? " active" : ""}`;

              return (
                <button
                  key={tab.id}
                  type="button"
                  className={buttonClass}
                  onClick={() => goToTab(tab.id)}
                >
                  {tab.icon} {tab.title}
                </button>
              );
            })}
          </div>
          {isEditMode && (
            <button
              type="button"
              onClick={() => document.querySelector('form')?.dispatchEvent(new Event('submit', { cancelable: true, bubbles: true }))}
              className="btn-submit-main"
              disabled={saving}
              style={{
                backgroundColor: "#0f172a",
                color: "white",
                border: "none",
                padding: "10px 20px",
                borderRadius: "4px",
                fontSize: "14px",
                cursor: saving ? "not-allowed" : "pointer",
                opacity: saving ? 0.6 : 1
              }}
            >
              {saving ? "💾 Guardando..." : "💾 Actualizar Siniestro"}
            </button>
          )}
        </div>

        {/* Tab Content */}
        <div className="tab-content">
          <form onSubmit={handleSubmit}>
            {/* TAB 0: Información Básica del Siniestro */}
            {activeTab === 0 && (
              <div className="tab-section active">
                <div className="card-section info-section">
                  <div className="card-header">
                    <div className="card-icon">📋</div>
                    <div>
                      <h3 className="card-title">
                        Información Básica del Siniestro
                      </h3>
                      <p className="card-description">
                        Datos principales del incidente reportado y
                        configuración inicial
                      </p>
                    </div>
                  </div>

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

                  {/* Primera línea: Número de Reclamo, Tipo de Reclamo, Póliza, Fecha Designación */}
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
                    <div className="form-group">
                      <label>Fecha Designación:</label>
                      <input
                        type="date"
                        name="fecha_designacion"
                        value={
                          formData.fecha_designacion ||
                          new Date().toISOString().split("T")[0]
                        }
                        onChange={handleInputChange}
                      />
                    </div>
                  </div>

                  {/* Segunda línea: Fecha Reportado, Fecha del Siniestro, Latitud, Longitud */}
                  <div className="form-row">
                    <div className="form-group">
                      <label>Fecha Reportado:</label>
                      <input
                        type="date"
                        name="fecha_reportado"
                        value={formData.fecha_reportado || ""}
                        onChange={handleInputChange}
                      />
                    </div>
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

                  <div className="form-group">
                    <label>Dirección del Siniestro:</label>
                    <textarea
                      name="direccion_siniestro"
                      value={formData.direccion_siniestro}
                      onChange={handleInputChange}
                      rows={3}
                      required
                    />
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
                      <label>Tipo de Siniestro:</label>
                      <input
                        type="text"
                        name="tipo_siniestro"
                        value={formData.tipo_siniestro || ""}
                        onChange={handleInputChange}
                        placeholder="Ej: Vehicular, Incendio, Robo"
                      />
                    </div>
                  </div>

                  <div className="form-row">
                    <div className="form-group">
                      <label>Cobertura:</label>
                      <input
                        type="text"
                        name="cobertura"
                        value={formData.cobertura || ""}
                        onChange={handleInputChange}
                        placeholder="Ej: Todo riesgo, Terceros, etc."
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
                </div>
              </div>
            )}

            {/* TAB 1: Parametrización */}
            {activeTab === 1 && (
              <div className="tab-section active">
                <div className="card-section param-section">
                  <div className="card-header">
                    <div className="card-icon">⚙️</div>
                    <div>
                      <h3 className="card-title">
                        Parametrización del Formulario
                      </h3>
                      <p className="card-description">
                        Configuración específica de la investigación y
                        declaración formal
                      </p>
                    </div>
                  </div>

                  {/* Misiva de Investigación */}
                  <div
                    className="card-section"
                    style={{ marginBottom: "20px", backgroundColor: "#fff3cd" }}
                  >
                    <h4 style={{ color: "#0f172a", marginBottom: "10px" }}>
                      📋 Misiva de Investigación
                    </h4>
                    <div className="form-group">
                      <label>
                        Instrucciones específicas de la aseguradora:
                      </label>
                      <textarea
                        name="misiva_investigacion"
                        value={formData.misiva_investigacion || ""}
                        onChange={handleInputChange}
                        rows={6}
                        placeholder="Escriba aquí las instrucciones específicas que dio la aseguradora para esta investigación..."
                      />
                    </div>
                    <small style={{ color: "#6c757d", fontStyle: "italic" }}>
                      * Este campo contiene las instrucciones particulares de la
                      aseguradora para adaptar la investigación a sus
                      requerimientos específicos.
                    </small>
                  </div>

                  {/* Declaración del Siniestro */}
                  <div
                    className="card-section"
                    style={{ backgroundColor: "#e8f4fd" }}
                  >
                    <h4 style={{ color: "#0f172a", marginBottom: "10px" }}>
                      📝 Declaración del Siniestro
                    </h4>

                    <div className="form-row">
                      <div className="form-group">
                        <label>Tipo de Persona que Declara:</label>
                        <div className="inline-fields">
                          <div className="inline-field narrow">
                            <select
                              name="persona_declara_tipo"
                              value={formData.persona_declara_tipo || ""}
                              onChange={handleInputChange}
                              style={{ width: "100%" }}
                            >
                              <option value="">Seleccionar...</option>
                              <option value="asegurado">Asegurado</option>
                              <option value="conductor">Conductor</option>
                              <option value="broker">Bróker</option>
                              <option value="otro">Otro</option>
                            </select>
                          </div>
                        </div>
                      </div>
                      <div className="form-group">
                        <label>Fecha Reportado:</label>
                        <div className="read-only-field">
                          <input
                            type="date"
                            value={formData.fecha_reportado || ""}
                            readOnly
                            style={{
                              backgroundColor: "#f8f9fa",
                              cursor: "not-allowed",
                              border: "1px solid #dee2e6",
                            }}
                          />
                          <small style={{ color: "#6c757d", fontSize: "12px" }}>
                            * Se toma de la Información Básica
                          </small>
                        </div>
                      </div>
                    </div>

                    <div className="form-row">
                      <div className="form-group">
                        <label>Cédula o RUC de quien declara:</label>
                        <input
                          type="text"
                          name="persona_declara_cedula"
                          value={formData.persona_declara_cedula || ""}
                          onChange={handleInputChange}
                          placeholder="Ej: 1234567890"
                        />
                      </div>
                      <div className="form-group">
                        <label>Nombre completo:</label>
                        <input
                          type="text"
                          name="persona_declara_nombre"
                          value={formData.persona_declara_nombre || ""}
                          onChange={handleInputChange}
                          placeholder="Ej: Juan Pérez"
                        />
                      </div>
                    </div>

                    <div className="form-group">
                      <label>Relación con el asegurado:</label>
                      <input
                        type="text"
                        name="persona_declara_relacion"
                        value={formData.persona_declara_relacion || ""}
                        onChange={handleInputChange}
                        placeholder="Ej: Propietario del vehículo, Esposo/a, Hijo/a, etc."
                      />
                    </div>
                  </div>
                </div>
              </div>
            )}

            {/* TAB 2: Entidades Relacionadas */}
            {activeTab === 2 && (
              <div className="tab-section active">
                <div className="card-section entidades-section">
                  <div className="card-header">
                    <div className="card-icon">👥</div>
                    <div>
                      <h3 className="card-title">Entidades Relacionadas</h3>
                      <p className="card-description">
                        Información completa de las personas y objetos
                        involucrados en el siniestro
                      </p>
                    </div>
                  </div>

                  {/* Asegurado */}
                  <div
                    className="card-section"
                    style={{ marginBottom: "20px", backgroundColor: "#f0f9ff" }}
                  >
                    <h4 style={{ color: "#0f172a", marginBottom: "15px" }}>
                      👤 Datos del Asegurado
                    </h4>

                    <div
                      className="form-group"
                      style={{ marginBottom: "15px" }}
                    >
                      <label>Tipo de Persona:</label>
                      <div className="person-type-selector">
                        <div className="person-type-option">
                          <input
                            type="radio"
                            id="asegurado-natural"
                            name="asegurado-tipo"
                            value="natural"
                            checked={formData.asegurado?.tipo === "natural"}
                            onChange={(e) => {
                              const value = e.target.value;
                              setFormData((prev) => ({
                                ...prev,
                                asegurado: { ...prev.asegurado, tipo: value },
                              }));
                            }}
                            className="person-type-radio"
                          />
                          <label
                            htmlFor="asegurado-natural"
                            className="person-type-card"
                          >
                            Persona Natural
                          </label>
                        </div>
                        <div className="person-type-option">
                          <input
                            type="radio"
                            id="asegurado-juridica"
                            name="asegurado-tipo"
                            value="juridica"
                            checked={formData.asegurado?.tipo === "juridica"}
                            onChange={(e) => {
                              const value = e.target.value;
                              setFormData((prev) => ({
                                ...prev,
                                asegurado: { ...prev.asegurado, tipo: value },
                              }));
                            }}
                            className="person-type-radio"
                          />
                          <label
                            htmlFor="asegurado-juridica"
                            className="person-type-card"
                          >
                            Persona Jurídica
                          </label>
                        </div>
                      </div>
                    </div>

                    {formData.asegurado?.tipo === "natural" && (
                      <>
                        <div className="form-row">
                          <div className="form-group">
                            <label>Cédula:</label>
                            <input
                              type="text"
                              value={formData.asegurado?.cedula || ""}
                              onChange={(e) => {
                                const value = e.target.value;
                                setFormData((prev) => ({
                                  ...prev,
                                  asegurado: {
                                    ...prev.asegurado,
                                    cedula: value,
                                  },
                                }));
                              }}
                              placeholder="Ej: 1234567890"
                            />
                          </div>
                          <div className="form-group">
                            <label>Nombre Completo:</label>
                            <input
                              type="text"
                              value={formData.asegurado?.nombre || ""}
                              onChange={(e) => {
                                const value = e.target.value;
                                setFormData((prev) => ({
                                  ...prev,
                                  asegurado: {
                                    ...prev.asegurado,
                                    nombre: value,
                                  },
                                }));
                              }}
                              placeholder="Ej: Juan Pérez"
                            />
                          </div>
                        </div>

                        <div className="form-row">
                          <div className="form-group">
                            <label>Celular:</label>
                            <input
                              type="tel"
                              value={formData.asegurado?.celular || ""}
                              onChange={(e) => {
                                const value = e.target.value;
                                setFormData((prev) => ({
                                  ...prev,
                                  asegurado: {
                                    ...prev.asegurado,
                                    celular: value,
                                  },
                                }));
                              }}
                              placeholder="Ej: 0991234567"
                            />
                          </div>
                          <div className="form-group">
                            <label>Email:</label>
                            <input
                              type="email"
                              value={formData.asegurado?.correo || ""}
                              onChange={(e) => {
                                const value = e.target.value;
                                setFormData((prev) => ({
                                  ...prev,
                                  asegurado: {
                                    ...prev.asegurado,
                                    correo: value,
                                  },
                                }));
                              }}
                              placeholder="Ej: juan.perez@email.com"
                            />
                          </div>
                        </div>

                        <div className="form-group">
                          <label>Dirección:</label>
                          <input
                            type="text"
                            value={formData.asegurado?.direccion || ""}
                            onChange={(e) => {
                              const value = e.target.value;
                              setFormData((prev) => ({
                                ...prev,
                                asegurado: {
                                  ...prev.asegurado,
                                  direccion: value,
                                },
                              }));
                            }}
                            placeholder="Ej: Av. Amazonas N32-45"
                          />
                        </div>
                      </>
                    )}

                    {formData.asegurado?.tipo === "juridica" && (
                      <>
                        <div className="form-row">
                          <div className="form-group">
                            <label>RUC:</label>
                            <input
                              type="text"
                              value={formData.asegurado?.ruc || ""}
                              onChange={(e) => {
                                const value = e.target.value;
                                setFormData((prev) => ({
                                  ...prev,
                                  asegurado: { ...prev.asegurado, ruc: value },
                                }));
                              }}
                              placeholder="Ej: 1791234567001"
                            />
                          </div>
                          <div className="form-group">
                            <label>Razón Social:</label>
                            <input
                              type="text"
                              value={formData.asegurado?.razon_social || ""}
                              onChange={(e) => {
                                const value = e.target.value;
                                setFormData((prev) => ({
                                  ...prev,
                                  asegurado: {
                                    ...prev.asegurado,
                                    razon_social: value,
                                  },
                                }));
                              }}
                              placeholder="Ej: Empresa S.A."
                            />
                          </div>
                        </div>

                        <div className="form-row">
                          <div className="form-group">
                            <label>Representante Legal:</label>
                            <input
                              type="text"
                              value={
                                formData.asegurado?.representante_legal || ""
                              }
                              onChange={(e) => {
                                const value = e.target.value;
                                setFormData((prev) => ({
                                  ...prev,
                                  asegurado: {
                                    ...prev.asegurado,
                                    representante_legal: value,
                                  },
                                }));
                              }}
                              placeholder="Ej: Juan Pérez"
                            />
                          </div>
                          <div className="form-group">
                            <label>Cédula Representante:</label>
                            <input
                              type="text"
                              value={
                                formData.asegurado?.cedula_representante || ""
                              }
                              onChange={(e) => {
                                const value = e.target.value;
                                setFormData((prev) => ({
                                  ...prev,
                                  asegurado: {
                                    ...prev.asegurado,
                                    cedula_representante: value,
                                  },
                                }));
                              }}
                              placeholder="Ej: 1234567890"
                            />
                          </div>
                        </div>

                        <div className="form-row">
                          <div className="form-group">
                            <label>Teléfono Empresa:</label>
                            <input
                              type="tel"
                              value={formData.asegurado?.telefono_empresa || ""}
                              onChange={(e) => {
                                const value = e.target.value;
                                setFormData((prev) => ({
                                  ...prev,
                                  asegurado: {
                                    ...prev.asegurado,
                                    telefono_empresa: value,
                                  },
                                }));
                              }}
                              placeholder="Ej: (02) 123-4567"
                            />
                          </div>
                          <div className="form-group">
                            <label>Email Empresa:</label>
                            <input
                              type="email"
                              value={formData.asegurado?.correo_empresa || ""}
                              onChange={(e) => {
                                const value = e.target.value;
                                setFormData((prev) => ({
                                  ...prev,
                                  asegurado: {
                                    ...prev.asegurado,
                                    correo_empresa: value,
                                  },
                                }));
                              }}
                              placeholder="Ej: info@empresa.com"
                            />
                          </div>
                        </div>

                        <div className="form-group">
                          <label>Dirección Empresa:</label>
                          <input
                            type="text"
                            value={formData.asegurado?.direccion_empresa || ""}
                            onChange={(e) => {
                              const value = e.target.value;
                              setFormData((prev) => ({
                                ...prev,
                                asegurado: {
                                  ...prev.asegurado,
                                  direccion_empresa: value,
                                },
                              }));
                            }}
                            placeholder="Ej: Av. Amazonas N32-45, Quito"
                          />
                        </div>
                      </>
                    )}
                  </div>

                  {/* Objeto Asegurado */}
                  <div
                    className="card-section"
                    style={{ marginBottom: "20px", backgroundColor: "#fff8e1" }}
                  >
                    <h4 style={{ color: "#0f172a", marginBottom: "15px" }}>
                      🚗 Datos del Objeto Asegurado
                    </h4>

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
                          required
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
                              objeto_asegurado: {
                                ...prev.objeto_asegurado,
                                tipo: value,
                              },
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
                              objeto_asegurado: {
                                ...prev.objeto_asegurado,
                                ano: value,
                              },
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

export default SiniestroForm;
