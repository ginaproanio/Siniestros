import React, { useState } from 'react';
import axios from 'axios';

// Configurar base URL para el backend - cambiar cuando se cree el servicio separado
const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || 'https://siniestros-production.up.railway.app';
axios.defaults.baseURL = BACKEND_URL;

interface FormData {
  compania_seguros: string;
  reclamo_num: string;
  fecha_siniestro: string;
  direccion_siniestro: string;
  ubicacion_geo_lat: number | null;
  ubicacion_geo_lng: number | null;
  danos_terceros: boolean;
  ejecutivo_cargo: string;
  fecha_designacion: string;
}

const SiniestroForm: React.FC = () => {
  const [formData, setFormData] = useState<FormData>({
    compania_seguros: 'Zurich Seguros Ecuador S.A.',
    reclamo_num: '25-01-VH-7079448',
    fecha_siniestro: '2023-10-15',
    direccion_siniestro: 'Av. Amazonas y Naciones Unidas, Quito',
    ubicacion_geo_lat: -0.1807,
    ubicacion_geo_lng: -78.4678,
    danos_terceros: true,
    ejecutivo_cargo: 'Juan Pérez',
    fecha_designacion: '2025-12-11',
  });

  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState('');

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
    const { name, value, type } = e.target;
    const checked = (e.target as HTMLInputElement).checked;

    setFormData(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value
    }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setMessage('');

    console.log('🚀 Enviando datos del formulario:', formData);
    console.log('🌐 URL de destino:', axios.defaults.baseURL + '/api/v1/');

    try {
      const response = await axios.post('/api/v1/', formData);
      console.log('✅ Respuesta del servidor:', response);
      console.log('📋 Datos de respuesta:', response.data);
      setMessage('Siniestro creado exitosamente!');
      // Redirect to list after 2 seconds
      setTimeout(() => {
        window.location.href = '/siniestros';
      }, 2000);
    } catch (error: any) {
      console.error('❌ Error completo:', error);
      console.error('❌ Respuesta del servidor:', error.response);
      console.error('❌ Datos del error:', error.response?.data);
      console.error('❌ Status del error:', error.response?.status);

      // Mostrar errores detallados en el formulario
      let errorMessage = 'Error al crear el siniestro';

      if (error.response) {
        const status = error.response.status;
        const data = error.response.data;

        switch (status) {
          case 400:
            errorMessage = `Datos inválidos: ${data.detail || 'Verifica los campos requeridos'}`;
            break;
          case 405:
            errorMessage = `Error 405: Método no permitido. URL: ${axios.defaults.baseURL}/api/v1/`;
            break;
          case 404:
            errorMessage = `Error 404: Endpoint no encontrado. Verifica la URL de la API`;
            break;
          case 500:
            errorMessage = `Error del servidor: ${data.detail || data.message || 'Error interno'}`;
            break;
          default:
            errorMessage = `Error ${status}: ${data.detail || data.message || 'Error desconocido'}`;
        }
      } else if (error.request) {
        errorMessage = 'No se pudo conectar al servidor. Verifica tu conexión a internet.';
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
      <h2>Datos del Siniestro</h2>
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
              value={formData.fecha_designacion}
              onChange={handleInputChange}
              required
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
              value={formData.ubicacion_geo_lat || ''}
              onChange={handleInputChange}
            />
          </div>
          <div className="form-group">
            <label>Longitud:</label>
            <input
              type="number"
              step="0.0001"
              name="ubicacion_geo_lng"
              value={formData.ubicacion_geo_lng || ''}
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

        <div style={{ display: 'flex', gap: '10px', marginTop: '20px' }}>
          <button type="button" onClick={() => {
            setFormData({
              compania_seguros: 'Zurich Seguros Ecuador S.A.',
              reclamo_num: `TEST-${Date.now()}`,
              fecha_siniestro: '2023-10-15',
              direccion_siniestro: 'Av. Amazonas y Naciones Unidas, Quito',
              ubicacion_geo_lat: -0.1807,
              ubicacion_geo_lng: -78.4678,
              danos_terceros: true,
              ejecutivo_cargo: 'Juan Pérez',
              fecha_designacion: '2025-12-11',
            });
          }} style={{ backgroundColor: '#6c757d' }}>
            Llenar con Datos de Prueba
          </button>

          <button type="submit" disabled={loading}>
            {loading ? 'Guardando...' : 'Crear Siniestro'}
          </button>
        </div>

        {message && (
          <div className={`message ${message.includes('Error') ? 'error' : 'success'}`}>
            {message}
          </div>
        )}
      </form>
    </div>
  );
};

export default SiniestroForm;
