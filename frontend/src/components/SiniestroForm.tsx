import axios from "axios";
import React, { useState } from "react";

// Configurar base URL para el backend
const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || 'https://siniestros-production.up.railway.app';
console.log('🌐 Backend URL:', BACKEND_URL);
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
  const [activeTab, setActiveTab] = useState(0);
  const [completedTabs, setCompletedTabs] = useState<number[]>([]);

  const [formData, setFormData] = useState<FormData>({
    compania_seguros: "Zurich Seguros Ecuador S.A.",
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

  const [loading, setLoading] = useState(false); // eslint-disable-line @typescript-eslint/no-unused-vars
  const [message, setMessage] = useState("");

  const tabs = [
    { id: 0, title: "Información Básica", icon: "📋" },
    { id: 1, title: "Parametrización", icon: "⚙️" },
    { id: 2, title: "Entidades", icon: "👥" },
    { id: 3, title: "Investigación", icon: "🔍" },
  ];

  const nextTab = () => {
    if (activeTab < tabs.length - 1) {
      setCompletedTabs(prev => [...prev, activeTab]);
      setActiveTab(activeTab + 1);
    }
  };

  const prevTab = () => { // eslint-disable-line @typescript-eslint/no-unused-vars
    if (activeTab > 0) {
      setActiveTab(activeTab - 1);
    }
  };

  const goToTab = (tabId: number) => {
    setActiveTab(tabId);
  };

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
    setLoading(true);
    setMessage("");

    console.log("🚀 Enviando datos del formulario:", formData);
    console.log(
      "🌐 URL de destino:",
      axios.defaults.baseURL + "/api/v1/siniestros/"
    );

    try {
      const response = await axios.post("/api/v1/siniestros/", formData);
      console.log("✅ Respuesta del servidor:", response);
      console.log("📋 Datos de respuesta:", response.data);
      setMessage("Siniestro creado exitosamente!");
      // Redirect to list after 2 seconds
      setTimeout(() => {
        window.location.href = "/siniestros";
      }, 2000);
    } catch (error: any) {
      console.error("❌ Error completo:", error);
      console.error("❌ Respuesta del servidor:", error.response);
      console.error("❌ Datos del error:", error.response?.data);
      console.error("❌ Status del error:", error.response?.status);

      // Mostrar errores detallados en el formulario
      let errorMessage = "Error al crear el siniestro";

      if (error.response) {
        const status = error.response.status;
        const data = error.response.data;

        switch (status) {
          case 400:
            errorMessage = `Datos inválidos: ${
              data.detail || "Verifica los campos requeridos"
            }`;
            break;
          case 405:
            errorMessage = `Error 405: Método no permitido. URL: ${axios.defaults.baseURL}/api/v1/siniestros/`;
            break;
          case 404:
            errorMessage = `Error 404: Endpoint no encontrado. Verifica la URL de la API`;
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
      setLoading(false);
    }
  };

  return (
    <div className="form-container">
      <h2>Registro de Siniestro</h2>

      {/* Progress Indicator */}
      <div className="progress-container">
        <div className="progress-steps">
          {tabs.map((tab, index) => (
            <div
              key={tab.id}
              className={`progress-step ${
                index === activeTab ? 'active' : ''
              } ${completedTabs.includes(index) ? 'completed' : ''}`}
            >
              <div className="step-circle">{index + 1}</div>
              <div className="step-label">{tab.title}</div>
            </div>
          ))}
        </div>
      </div>

      {/* Tab Navigation */}
      <div className="tabs-container">
        <div className="tabs-header">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              type="button"
              className={`tab-button ${
                activeTab === tab.id ? 'active' : ''
              } ${completedTabs.includes(tab.id) ? 'completed' : ''}`}
              onClick={() => goToTab(tab.id)}
            >
              {tab.icon} {tab.title}
            </button>
          ))}
        </div>

        {/* Tab Content */}
        <div className="tab-content">
          <form onSubmit={handleSubmit}>

            {/* TAB 1: Información Básica del Siniestro */}
            <div className={`tab-section ${activeTab === 0 ? 'active' : ''}`}>
              <div className="card-section">
                <div className="card-header">
                  <div className="card-icon" style={{ backgroundColor: '#e3f2fd' }}>📋</div>
                  <div>
                    <h3 className="card-title">Información Básica del Siniestro</h3>
                    <p className="card-description">Datos principales del incidente reportado</p>
                  </div>
                </div>

                <div className="form-row">
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
                      value={formData.fecha_reportado || ""}
                      onChange={handleInputChange}
                    />
                  </div>
                  <div className="form-group">
                    <label>Fecha Designación:</label>
                    <input
                      type="date"
                      name="fecha_designacion"
                      value={formData.fecha_designacion || new Date().toISOString().split('T')[0]}
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
                      <input
                        type="checkbox"
                        name="danos_terceros"
                        checked={formData.danos_terceros}
                        onChange={handleInputChange}
                      />
                      Daños a Terceros
                    </label>
                  </div>
                </div>

                <div className="form-row">
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
                </div>
              </div>

              {/* Tab Navigation */}
              <div className="tab-navigation">
                <button type="button" className="btn-prev" disabled>
                  Anterior
                </button>
                <button type="button" className="btn-next" onClick={nextTab}>
                  Siguiente
                </button>
              </div>
            </div>

            {/* TAB 2: Parametrización */}
            <div className={`tab-section ${activeTab === 1 ? 'active' : ''}`}>
              <div className="card-section">
                <div className="card-header">
                  <div className="card-icon" style={{ backgroundColor: '#fff3cd' }}>⚙️</div>
                  <div>
                    <h3 className="card-title">Parametrización del Formulario</h3>
                    <p className="card-description">Configuración específica de la investigación</p>
                  </div>
                </div>

                <div className="card-section" style={{ marginBottom: '20px', backgroundColor: '#fff3cd' }}>
                  <h4 style={{ color: "#0f172a", marginBottom: "10px" }}>📋 Misiva de Investigación</h4>
                  <div className="form-group">
                    <label>Instrucciones específicas de la aseguradora:</label>
                    <textarea
                      name="misiva_investigacion"
                      value={formData.misiva_investigacion || ""}
                      onChange={handleInputChange}
                      rows={6}
                      placeholder="Escriba aquí las instrucciones específicas que dio la aseguradora para esta investigación..."
                    />
                  </div>
                  <small style={{ color: "#6c757d", fontStyle: "italic" }}>
                    * Este campo contiene las instrucciones particulares de la aseguradora para adaptar la investigación a sus requerimientos específicos.
                  </small>
                </div>

                <div className="card-section" style={{ backgroundColor: '#e8f4fd' }}>
                  <h4 style={{ color: "#0f172a", marginBottom: "10px" }}>📝 Declaración del Siniestro</h4>

                  <div className="form-row">
                    <div className="form-group">
                      <label>Tipo de Persona que Declara:</label>
                      <select
                        name="persona_declara_tipo"
                        value={formData.persona_declara_tipo || ""}
                        onChange={handleInputChange}
                      >
                        <option value="">Seleccionar...</option>
                        <option value="asegurado">Asegurado</option>
                        <option value="conductor">Conductor</option>
                        <option value="broker">Bróker</option>
                        <option value="otro">Otro</option>
                      </select>
                    </div>
                    <div className="form-group">
                      <label>Fecha Reportado:</label>
                      <input
                        type="date"
                        name="fecha_reportado"
                        value={formData.fecha_reportado || ""}
                        onChange={handleInputChange}
                      />
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

              {/* Tab Navigation */}
              <div className="tab-navigation">
                <button type="button" className="btn-prev" onClick={prevTab}>
                  Anterior
                </button>
                <button type="button" className="btn-next" onClick={nextTab}>
                  Siguiente
                </button>
              </div>
            </div>

            {/* TAB 3: Entidades Relacionadas */}
            <div className={`tab-section ${activeTab === 2 ? 'active' : ''}`}>
              <div className="card-section">
                <div className="card-header">
                  <div className="card-icon" style={{ backgroundColor: '#f0f9ff' }}>👥</div>
                  <div>
                    <h3 className="card-title">Entidades Relacionadas</h3>
                    <p className="card-description">Datos de las personas y objetos involucrados</p>
                  </div>
                </div>

                {/* Placeholder content - to be expanded */}
                <div className="form-group">
                  <p style={{ textAlign: 'center', color: '#6c757d', padding: '40px' }}>
                    📝 Esta sección incluirá los datos del Asegurado, Beneficiario, Conductor y Objeto Asegurado.
                  </p>
                </div>
              </div>

              {/* Tab Navigation */}
              <div className="tab-navigation">
                <button type="button" className="btn-prev" onClick={prevTab}>
                  Anterior
                </button>
                <button type="button" className="btn-next" onClick={nextTab}>
                  Siguiente
                </button>
              </div>
            </div>

            {/* TAB 4: Investigación */}
            <div className={`tab-section ${activeTab === 3 ? 'active' : ''}`}>
              <div className="card-section">
                <div className="card-header">
                  <div className="card-icon" style={{ backgroundColor: '#fef3c7' }}>🔍</div>
                  <div>
                    <h3 className="card-title">Investigación y Evidencia</h3>
                    <p className="card-description">Recopilación de información y evidencia del siniestro</p>
                  </div>
                </div>

                {/* Placeholder content - to be expanded */}
                <div className="form-group">
                  <p style={{ textAlign: 'center', color: '#6c757d', padding: '40px' }}>
                    📋 Esta sección incluirá Antecedentes, Entrevistas, Inspecciones y Testigos.
                  </p>
                </div>
              </div>

              {/* Tab Navigation */}
              <div className="tab-navigation">
                <button type="button" className="btn-prev" onClick={prevTab}>
                  Anterior
                </button>
                <button type="button" className="btn-submit-tab" onClick={handleSubmit}>
                  {loading ? "Guardando..." : "Crear Siniestro"}
                </button>
              </div>
            </div>

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
