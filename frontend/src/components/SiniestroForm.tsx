import React, { useState } from 'react';
import axios from 'axios';

// Configurar base URL para el backend
axios.defaults.baseURL = 'https://siniestros-production.up.railway.app';

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
    reclamo_num: '',
    fecha_siniestro: '',
    direccion_siniestro: 'Av. Amazonas y Naciones Unidas, Quito',
    ubicacion_geo_lat: -0.1807,
    ubicacion_geo_lng: -78.4678,
    danos_terceros: false,
    ejecutivo_cargo: 'Juan Pérez',
    fecha_designacion: '',
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

    try {
      const response = await axios.post('/api/v1/', formData);
      setMessage('Siniestro creado exitosamente!');
      console.log('Siniestro creado:', response.data);
    } catch (error) {
      setMessage('Error al crear el siniestro');
      console.error('Error:', error);
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

        <button type="submit" disabled={loading}>
          {loading ? 'Guardando...' : 'Crear Siniestro'}
        </button>

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
