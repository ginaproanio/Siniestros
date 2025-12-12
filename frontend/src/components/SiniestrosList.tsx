import React, { useState, useEffect } from 'react';
import axios from 'axios';

interface Siniestro {
  id: number;
  compania_seguros: string;
  reclamo_num: string;
  fecha_siniestro: string;
  tipo_siniestro: string;
}

const SiniestrosList: React.FC = () => {
  const [siniestros, setSiniestros] = useState<Siniestro[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    fetchSiniestros();
  }, []);

  const fetchSiniestros = async () => {
    try {
      setLoading(true);
      const response = await axios.get('/api/v1/');
      setSiniestros(response.data);
    } catch (err: any) {
      setError('Error al cargar siniestros');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  if (loading) return <div>Cargando siniestros...</div>;
  if (error) return <div className="error">{error}</div>;

  return (
    <div className="siniestros-list">
      <h2>Siniestros Registrados</h2>
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
                    <button onClick={() => window.location.href = `/siniestro/${siniestro.id}`}>
                      Ver Detalles
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
