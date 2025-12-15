import React, { useState, useEffect } from 'react';
import { useLocation } from 'react-router-dom';
import axios from 'axios';

// Configurar base URL para el backend
const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || 'https://siniestros-production.up.railway.app';
console.log('🌐 Backend URL:', BACKEND_URL);
axios.defaults.baseURL = BACKEND_URL;

interface Siniestro {
  id: number;
  compania_seguros: string;
  reclamo_num: string;
  fecha_siniestro: string;
  tipo_siniestro: string;
}

const SiniestrosList: React.FC = () => {
  const location = useLocation();
  const isFromInvestigacion = location.pathname === '/investigacion';

  const [siniestros, setSiniestros] = useState<Siniestro[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    fetchSiniestros();
  }, []);

  const fetchSiniestros = async () => {
    try {
      setLoading(true);
      const response = await axios.get('/api/v1/siniestros/');
      setSiniestros(response.data);
    } catch (err: any) {
      setError('Error al cargar siniestros');
      console.error('Error fetching siniestros:', err);
    } finally {
      setLoading(false);
    }
  };

  if (loading) return <div>Cargando siniestros...</div>;
  if (error) return <div className="error">{error}</div>;

  return (
    <div className="siniestros-list">
      <h2>{isFromInvestigacion ? 'Selecciona un Siniestro para Investigar' : 'Siniestros Registrados'}</h2>
      {isFromInvestigacion && (
        <div style={{
          backgroundColor: '#e8f5e8',
          padding: '15px',
          borderRadius: '8px',
          marginBottom: '20px',
          border: '2px solid #28a745'
        }}>
          <p style={{ margin: 0, fontWeight: 'bold', color: '#0f172a' }}>
            🔍 Modo Investigación: Selecciona un siniestro para completar la investigación recabada
          </p>
          <p style={{ margin: '5px 0 0 0', fontSize: '14px', color: '#666' }}>
            Al hacer clic en "Editar", podrás acceder a todas las secciones de investigación después de Testigos.
          </p>
        </div>
      )}
      {siniestros.length === 0 ? (
        <p>No hay siniestros registrados aún.</p>
      ) : (
        <div className="table-container">
          <table>
            <thead>
              <tr>
                <th>ID</th>
                <th>Compañía</th>
                <th>Número de Reclamo</th>
                <th>Fecha del Siniestro</th>
                <th>Tipo</th>
                <th>Acciones</th>
              </tr>
            </thead>
            <tbody>
              {siniestros.map((siniestro) => (
                <tr key={siniestro.id}>
                  <td>{siniestro.id}</td>
                  <td>{siniestro.compania_seguros}</td>
                  <td>{siniestro.reclamo_num}</td>
                  <td>{new Date(siniestro.fecha_siniestro).toLocaleDateString()}</td>
                  <td>{siniestro.tipo_siniestro}</td>
                  <td>
                    <button
                      onClick={() => window.location.href = `/siniestro/${siniestro.id}/editar`}
                      style={{ backgroundColor: '#ffc107' }}
                    >
                      Editar
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
};

export default SiniestrosList;
