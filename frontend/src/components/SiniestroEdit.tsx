import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import axios from 'axios';

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

const SiniestroEdit: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const [formData, setFormData] = useState<FormData>({
    compania_seguros: '',
    reclamo_num: '',
    fecha_siniestro: '',
    direccion_siniestro: '',
    ubicacion_geo_lat: null,
    ubicacion_geo_lng: null,
    danos_terceros: false,
    ejecutivo_cargo: '',
    fecha_designacion: '',
  });

  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState('');

  useEffect(() => {
    if (id) {
      fetchSiniestro();
    }
  }, [id]); // eslint-disable-line react-hooks/exhaustive-deps

  const fetchSiniestro = async () => {
    try {
      const response = await axios.get(`/api/v1/${id}`);
      const data = response.data;
      setFormData({
        compania_seguros: data.compania_seguros || '',
        reclamo_num: data.reclamo_num || '',
        fecha_siniestro: data.fecha_siniestro ? new Date(data.fecha_siniestro).toISOString().split('T')[0] : '',
        direccion_siniestro: data.direccion_siniestro || '',
        ubicacion_geo_lat: data.ubicacion_geo_lat,
        ubicacion_geo_lng: data.ubicacion_geo_lng,
        danos_terceros: data.danos_terceros || false,
        ejecutivo_cargo: data.ejecutivo_cargo || '',
        fecha_designacion: data.fecha_designacion ? new Date(data.fecha_designacion).toISOString().split('T')[0] : '',
      });
    } catch (error) {
      console.error('Error loading siniestro:', error);
      setMessage('Error al cargar los datos del siniestro');
    } finally {
      setLoading(false);
    }
  };

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
    setSaving(true);
    setMessage('');

    try {
      await axios.put(`/api/v1/${id}`, formData);
      setMessage('Siniestro actualizado exitosamente!');
      setTimeout(() => {
        window.location.href = `/siniestro/${id}`;
      }, 2000);
    } catch (error: any) {
      console.error('Error updating siniestro:', error);
      setMessage('Error al actualizar el siniestro');
    } finally {
      setSaving(false);
    }
  };

  if (loading) return <div>Cargando datos del siniestro...</div>;

  return (
    <div className="form-container">
      <h2>Editar Siniestro</h2>
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
          <button
            type="button"
            onClick={() => window.history.back()}
            style={{ backgroundColor: '#6c757d' }}
          >
            Cancelar
          </button>
          <button type="submit" disabled={saving}>
            {saving ? 'Guardando...' : 'Actualizar Siniestro'}
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

export default SiniestroEdit;
