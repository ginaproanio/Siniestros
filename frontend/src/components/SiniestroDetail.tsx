import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import axios from 'axios';

interface SiniestroData {
  id: number;
  compania_seguros: string;
  reclamo_num: string;
  fecha_siniestro: string;
  tipo_siniestro: string;
  // Add other fields as needed
}

const SiniestroDetail: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const [siniestro, setSiniestro] = useState<SiniestroData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  const fetchSiniestroDetail = async () => {
    if (!id) return;

    try {
      setLoading(true);
      const response = await axios.get(`/api/v1/${id}`);
      setSiniestro(response.data);
    } catch (err: any) {
      setError('Error al cargar detalles del siniestro');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchSiniestroDetail();
  }, [id]); // eslint-disable-line react-hooks/exhaustive-deps

  if (loading) return <div>Cargando detalles...</div>;
  if (error) return <div className="error">{error}</div>;
  if (!siniestro) return <div>Siniestro no encontrado</div>;

  return (
    <div className="siniestro-detail">
      <h2>Detalles del Siniestro</h2>
      <div className="detail-grid">
        <div><strong>ID:</strong> {siniestro.id}</div>
        <div><strong>Compañía:</strong> {siniestro.compania_seguros}</div>
        <div><strong>Número de Reclamo:</strong> {siniestro.reclamo_num}</div>
        <div><strong>Fecha del Siniestro:</strong> {new Date(siniestro.fecha_siniestro).toLocaleDateString()}</div>
        <div><strong>Tipo:</strong> {siniestro.tipo_siniestro}</div>
      </div>
      <button onClick={() => window.history.back()}>← Volver</button>
    </div>
  );
};

export default SiniestroDetail;
