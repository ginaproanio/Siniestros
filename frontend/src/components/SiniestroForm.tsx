import axios from "axios";
import React, { useState } from "react";

// Configurar base URL para el backend
const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || 'https://siniestros-production.up.railway.app';
console.log('🌐 Backend URL:', BACKEND_URL);
axios.defaults.baseURL = BACKEND_URL;

// Interfaces para futuras expansiones del formulario
// interface AseguradoData { ... }
// interface ConductorData { ... }
// interface VehiculoData { ... }

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
  const [formData, setFormData] = useState<FormData>({
    // Datos básicos según backend schema
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

  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState("");

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
    console.log("🌐 URL de destino:", axios.defaults.baseURL + "/api/v1/siniestros/");

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
      <form onSubmit={handleSubmit}>
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
            <label>Fecha de Designación:</label>
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
            <label>Fecha Reportado:</label>
            <input
              type="date"
              name="fecha_reportado"
              value={formData.fecha_reportado || ""}
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
        </div>

        {/* PARAMETRIZACIÓN DEL FORMULARIO */}
        <div className="section-container">
          <h3 className="section-header">⚙️ PARAMETRIZACIÓN DEL FORMULARIO</h3>

          {/* PRIMERO: MISIVA DE INVESTIGACIÓN */}
          <div style={{ marginBottom: "20px", padding: "15px", backgroundColor: "#fff3cd", borderRadius: "5px" }}>
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

          {/* SEGUNDO: DECLARACIÓN DEL SINIESTRO (Fecha Reportado) */}
          <div style={{ marginBottom: "20px", padding: "15px", backgroundColor: "#e8f4fd", borderRadius: "5px" }}>
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

        {/* ENTIDADES RELACIONADAS */}
        <div className="section-container">
          <h3 className="section-header">👥 ENTIDADES RELACIONADAS</h3>

          {/* ASEGURADO */}
          <div style={{ marginBottom: "20px", padding: "15px", backgroundColor: "#f0f9ff", borderRadius: "5px" }}>
            <h4 style={{ color: "#0f172a", marginBottom: "10px" }}>👤 Datos del Asegurado</h4>

            <div className="form-group" style={{ marginBottom: "15px" }}>
              <label>Tipo de Persona:</label>
              <select
                value={formData.asegurado?.tipo || ""}
                onChange={(e) => {
                  const value = e.target.value;
                  setFormData((prev) => ({
                    ...prev,
                    asegurado: { ...prev.asegurado, tipo: value }
                  }));
                }}
              >
                <option value="">Seleccionar...</option>
                <option value="natural">Persona Natural</option>
                <option value="juridica">Persona Jurídica</option>
              </select>
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
                          asegurado: { ...prev.asegurado, cedula: value }
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
                          asegurado: { ...prev.asegurado, nombre: value }
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
                          asegurado: { ...prev.asegurado, celular: value }
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
                          asegurado: { ...prev.asegurado, correo: value }
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
                        asegurado: { ...prev.asegurado, direccion: value }
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
                          asegurado: { ...prev.asegurado, ruc: value }
                        }));
                      }}
                      placeholder="Ej: 1234567890001"
                    />
                  </div>
                  <div className="form-group">
                    <label>Razón Social:</label>
                    <input
                      type="text"
                      value={formData.asegurado?.empresa || ""}
                      onChange={(e) => {
                        const value = e.target.value;
                        setFormData((prev) => ({
                          ...prev,
                          asegurado: { ...prev.asegurado, empresa: value }
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
                      value={formData.asegurado?.representante_legal || ""}
                      onChange={(e) => {
                        const value = e.target.value;
                        setFormData((prev) => ({
                          ...prev,
                          asegurado: { ...prev.asegurado, representante_legal: value }
                        }));
                      }}
                      placeholder="Ej: Juan Pérez"
                    />
                  </div>
                  <div className="form-group">
                    <label>Celular:</label>
                    <input
                      type="tel"
                      value={formData.asegurado?.celular || ""}
                      onChange={(e) => {
                        const value = e.target.value;
                        setFormData((prev) => ({
                          ...prev,
                          asegurado: { ...prev.asegurado, celular: value }
                        }));
                      }}
                      placeholder="Ej: 0991234567"
                    />
                  </div>
                </div>

                <div className="form-row">
                  <div className="form-group">
                    <label>Teléfono:</label>
                    <input
                      type="tel"
                      value={formData.asegurado?.telefono || ""}
                      onChange={(e) => {
                        const value = e.target.value;
                        setFormData((prev) => ({
                          ...prev,
                          asegurado: { ...prev.asegurado, telefono: value }
                        }));
                      }}
                      placeholder="Ej: 022345678"
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
                          asegurado: { ...prev.asegurado, correo: value }
                        }));
                      }}
                      placeholder="Ej: info@empresa.com"
                    />
                  </div>
                </div>
              </>
            )}
          </div>

          {/* BENEFICIARIO */}
          <div style={{ marginBottom: "20px", padding: "15px", backgroundColor: "#f0fdf4", borderRadius: "5px" }}>
            <h4 style={{ color: "#0f172a", marginBottom: "10px" }}>🎯 Datos del Beneficiario</h4>

            <div className="form-group" style={{ marginBottom: "15px" }}>
              <label>
                <input
                  type="checkbox"
                  checked={formData.beneficiario?.es_asegurado || false}
                  onChange={(e) => {
                    const checked = e.target.checked;
                    setFormData((prev) => ({
                      ...prev,
                      beneficiario: checked ? {
                        ...prev.beneficiario,
                        es_asegurado: true,
                        cedula: prev.asegurado?.cedula || "",
                        nombre: prev.asegurado?.nombre || "",
                        relacion: "Asegurado"
                      } : {
                        ...prev.beneficiario,
                        es_asegurado: false
                      }
                    }));
                  }}
                />
                Es el asegurado
              </label>
            </div>

            {!formData.beneficiario?.es_asegurado && (
              <>
                <div className="form-group" style={{ marginBottom: "15px" }}>
                  <label>Tipo de Persona:</label>
                  <select
                    value={formData.beneficiario?.tipo || ""}
                    onChange={(e) => {
                      const value = e.target.value;
                      setFormData((prev) => ({
                        ...prev,
                        beneficiario: { ...prev.beneficiario, tipo: value }
                      }));
                    }}
                  >
                    <option value="">Seleccionar...</option>
                    <option value="natural">Persona Natural</option>
                    <option value="juridica">Persona Jurídica</option>
                  </select>
                </div>

                {formData.beneficiario?.tipo === "natural" && (
                  <>
                    <div className="form-row">
                      <div className="form-group">
                        <label>Cédula:</label>
                        <input
                          type="text"
                          value={formData.beneficiario?.cedula || ""}
                          onChange={(e) => {
                            const value = e.target.value;
                            setFormData((prev) => ({
                              ...prev,
                              beneficiario: { ...prev.beneficiario, cedula: value }
                            }));
                          }}
                          placeholder="Ej: 0987654321"
                        />
                      </div>
                      <div className="form-group">
                        <label>Nombre Completo:</label>
                        <input
                          type="text"
                          value={formData.beneficiario?.nombre || ""}
                          onChange={(e) => {
                            const value = e.target.value;
                            setFormData((prev) => ({
                              ...prev,
                              beneficiario: { ...prev.beneficiario, nombre: value }
                            }));
                          }}
                          placeholder="Ej: María González"
                        />
                      </div>
                    </div>
                  </>
                )}

                {formData.beneficiario?.tipo === "juridica" && (
                  <>
                    <div className="form-row">
                      <div className="form-group">
                        <label>RUC:</label>
                        <input
                          type="text"
                          value={formData.beneficiario?.cedula_ruc || ""}
                          onChange={(e) => {
                            const value = e.target.value;
                            setFormData((prev) => ({
                              ...prev,
                              beneficiario: { ...prev.beneficiario, cedula_ruc: value }
                            }));
                          }}
                          placeholder="Ej: 1234567890001"
                        />
                      </div>
                      <div className="form-group">
                        <label>Razón Social:</label>
                        <input
                          type="text"
                          value={formData.beneficiario?.razon_social || ""}
                          onChange={(e) => {
                            const value = e.target.value;
                            setFormData((prev) => ({
                              ...prev,
                              beneficiario: { ...prev.beneficiario, razon_social: value }
                            }));
                          }}
                          placeholder="Ej: Empresa Beneficiaria S.A."
                        />
                      </div>
                    </div>
                  </>
                )}

                <div className="form-group">
                  <label>Relación con el Asegurado:</label>
                  <input
                    type="text"
                    value={formData.beneficiario?.relacion || ""}
                    onChange={(e) => {
                      const value = e.target.value;
                      setFormData((prev) => ({
                        ...prev,
                        beneficiario: { ...prev.beneficiario, relacion: value }
                      }));
                    }}
                    placeholder="Ej: Esposa, Hijo, Padre"
                  />
                </div>
              </>
            )}
          </div>

          {/* CONDUCTOR */}
          <div style={{ marginBottom: "20px", padding: "15px", backgroundColor: "#fef3c7", borderRadius: "5px" }}>
            <h4 style={{ color: "#0f172a", marginBottom: "10px" }}>🚗 Datos del Conductor</h4>

            <div className="form-group" style={{ marginBottom: "15px" }}>
              <label>
                <input
                  type="checkbox"
                  checked={formData.conductor?.es_asegurado || false}
                  onChange={(e) => {
                    const checked = e.target.checked;
                    setFormData((prev) => ({
                      ...prev,
                      conductor: checked ? {
                        ...prev.conductor,
                        es_asegurado: true,
                        cedula: prev.asegurado?.cedula || "",
                        nombre: prev.asegurado?.nombre || "",
                        licencia: "",
                        telefono: prev.asegurado?.celular || "",
                        direccion: prev.asegurado?.direccion || ""
                      } : {
                        ...prev.conductor,
                        es_asegurado: false
                      }
                    }));
                  }}
                />
                Es el asegurado
              </label>
            </div>

            {!formData.conductor?.es_asegurado && (
              <>
                <div className="form-row">
                  <div className="form-group">
                    <label>Cédula:</label>
                    <input
                      type="text"
                      value={formData.conductor?.cedula || ""}
                      onChange={(e) => {
                        const value = e.target.value;
                        setFormData((prev) => ({
                          ...prev,
                          conductor: { ...prev.conductor, cedula: value }
                        }));
                      }}
                      placeholder="Ej: 1122334455"
                    />
                  </div>
                  <div className="form-group">
                    <label>Nombre Completo:</label>
                    <input
                      type="text"
                      value={formData.conductor?.nombre || ""}
                      onChange={(e) => {
                        const value = e.target.value;
                        setFormData((prev) => ({
                          ...prev,
                          conductor: { ...prev.conductor, nombre: value }
                        }));
                      }}
                      placeholder="Ej: Carlos Rodríguez"
                    />
                  </div>
                </div>

                <div className="form-row">
                  <div className="form-group">
                    <label>Número de Licencia:</label>
                    <input
                      type="text"
                      value={formData.conductor?.licencia || ""}
                      onChange={(e) => {
                        const value = e.target.value;
                        setFormData((prev) => ({
                          ...prev,
                          conductor: { ...prev.conductor, licencia: value }
                        }));
                      }}
                      placeholder="Ej: 123456789"
                    />
                  </div>
                  <div className="form-group">
                    <label>Teléfono:</label>
                    <input
                      type="tel"
                      value={formData.conductor?.telefono || ""}
                      onChange={(e) => {
                        const value = e.target.value;
                        setFormData((prev) => ({
                          ...prev,
                          conductor: { ...prev.conductor, telefono: value }
                        }));
                      }}
                      placeholder="Ej: 0987654321"
                    />
                  </div>
                </div>

                <div className="form-group">
                  <label>Dirección:</label>
                  <input
                    type="text"
                    value={formData.conductor?.direccion || ""}
                    onChange={(e) => {
                      const value = e.target.value;
                      setFormData((prev) => ({
                        ...prev,
                        conductor: { ...prev.conductor, direccion: value }
                      }));
                    }}
                    placeholder="Ej: Calle Principal 123"
                  />
                </div>
              </>
            )}
          </div>

          {/* OBJETO ASEGURADO */}
          <div style={{ padding: "15px", backgroundColor: "#fdf2f8", borderRadius: "5px" }}>
            <h4 style={{ color: "#0f172a", marginBottom: "10px" }}>🚙 Datos del Objeto Asegurado</h4>

            <div className="form-row">
              <div className="form-group">
                <label>Tipo:</label>
                <input
                  type="text"
                  name="objeto_tipo"
                  value={formData.objeto_asegurado?.tipo || ""}
                  onChange={(e) => {
                    const value = e.target.value;
                    setFormData((prev) => ({
                      ...prev,
                      objeto_asegurado: { ...prev.objeto_asegurado, tipo: value }
                    }));
                  }}
                  placeholder="Ej: Automóvil, Motocicleta, Camión"
                />
              </div>
              <div className="form-group">
                <label>Marca:</label>
                <input
                  type="text"
                  name="objeto_marca"
                  value={formData.objeto_asegurado?.marca || ""}
                  onChange={(e) => {
                    const value = e.target.value;
                    setFormData((prev) => ({
                      ...prev,
                      objeto_asegurado: { ...prev.objeto_asegurado, marca: value }
                    }));
                  }}
                  placeholder="Ej: Toyota, Chevrolet, Honda"
                />
              </div>
            </div>

            <div className="form-row">
              <div className="form-group">
                <label>Modelo:</label>
                <input
                  type="text"
                  name="objeto_modelo"
                  value={formData.objeto_asegurado?.modelo || ""}
                  onChange={(e) => {
                    const value = e.target.value;
                    setFormData((prev) => ({
                      ...prev,
                      objeto_asegurado: { ...prev.objeto_asegurado, modelo: value }
                    }));
                  }}
                  placeholder="Ej: Corolla, Cruze, Civic"
                />
              </div>
              <div className="form-group">
                <label>Año:</label>
                <input
                  type="number"
                  name="objeto_anio"
                  value={formData.objeto_asegurado?.anio || ""}
                  onChange={(e) => {
                    const value = e.target.value;
                    setFormData((prev) => ({
                      ...prev,
                      objeto_asegurado: { ...prev.objeto_asegurado, anio: value }
                    }));
                  }}
                  placeholder="Ej: 2020"
                  min="1900"
                  max="2030"
                />
              </div>
            </div>

            <div className="form-row">
              <div className="form-group">
                <label>Placa/Patente:</label>
                <input
                  type="text"
                  name="objeto_placa"
                  value={formData.objeto_asegurado?.placa || ""}
                  onChange={(e) => {
                    const value = e.target.value;
                    setFormData((prev) => ({
                      ...prev,
                      objeto_asegurado: { ...prev.objeto_asegurado, placa: value }
                    }));
                  }}
                  placeholder="Ej: ABC-1234"
                />
              </div>
              <div className="form-group">
                <label>Color:</label>
                <input
                  type="text"
                  name="objeto_color"
                  value={formData.objeto_asegurado?.color || ""}
                  onChange={(e) => {
                    const value = e.target.value;
                    setFormData((prev) => ({
                      ...prev,
                      objeto_asegurado: { ...prev.objeto_asegurado, color: value }
                    }));
                  }}
                  placeholder="Ej: Blanco, Negro, Rojo"
                />
              </div>
            </div>

            <div className="form-row">
              <div className="form-group">
                <label>Número de Chasis:</label>
                <input
                  type="text"
                  name="objeto_chasis"
                  value={formData.objeto_asegurado?.chasis || ""}
                  onChange={(e) => {
                    const value = e.target.value;
                    setFormData((prev) => ({
                      ...prev,
                      objeto_asegurado: { ...prev.objeto_asegurado, chasis: value }
                    }));
                  }}
                  placeholder="Ej: 1HGCM82633A123456"
                />
              </div>
              <div className="form-group">
                <label>Número de Motor:</label>
                <input
                  type="text"
                  name="objeto_motor"
                  value={formData.objeto_asegurado?.motor || ""}
                  onChange={(e) => {
                    const value = e.target.value;
                    setFormData((prev) => ({
                      ...prev,
                      objeto_asegurado: { ...prev.objeto_asegurado, motor: value }
                    }));
                  }}
                  placeholder="Ej: 1NZ-FXE-1234567"
                />
              </div>
            </div>
          </div>
        </div>

        {/* ANTECEDENTES */}
        <div className="section-container">
          <h3 className="section-header">📋 Antecedentes</h3>
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
        <div className="section-container">
          <h3 className="section-header">🎤 Entrevista con el Asegurado</h3>
          <button
            type="button"
            className="btn-add"
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
          >
            ➕ Agregar Relato
          </button>

          {formData.relatos_asegurado?.map((relato, index) => (
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
                        prev.relatos_asegurado?.filter((_, i) => i !== index) ||
                        [],
                    }));
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
                          "/api/v1/upload-imagen",
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
                  <div>
                    <img
                      src={`${BACKEND_URL}${relato.imagen_url}`}
                      alt={`Relato ${relato.numero_relato}`}
                      className="image-preview"
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
                          "/api/v1/upload-imagen",
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
                          "/api/v1/upload-imagen",
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

        <div style={{ display: "flex", gap: "10px", marginTop: "20px" }}>
          <button
            type="button"
            onClick={() => {
              setFormData((prev) => ({
                ...prev,
                // Datos básicos del siniestro
                compania_seguros: "Zurich Seguros Ecuador S.A.",
                reclamo_num: `TEST-${Date.now()}`,
                fecha_siniestro: "2023-10-15",
                direccion_siniestro: "Av. Amazonas y Naciones Unidas, Quito",
                ubicacion_geo_lat: -0.1807,
                ubicacion_geo_lng: -78.4678,
                danos_terceros: true,
                ejecutivo_cargo: "Juan Pérez",
                fecha_designacion: "2025-12-11",
                tipo_siniestro: "Vehicular",
              }));
            }}
            style={{ backgroundColor: "#6c757d" }}
          >
            Llenar con Datos de Prueba
          </button>

          <button type="submit" disabled={loading}>
            {loading ? "Guardando..." : "Crear Siniestro"}
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

export default SiniestroForm;
