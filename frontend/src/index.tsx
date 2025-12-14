import React from 'react';
import ReactDOM from 'react-dom/client';
import './index.css';
import App from './App';
import axios from 'axios';

// Configurar axios con la URL base del backend
const API_BASE_URL = process.env.REACT_APP_BACKEND_URL;
if (!API_BASE_URL) {
  console.error('REACT_APP_BACKEND_URL no está configurado');
}
axios.defaults.baseURL = API_BASE_URL;

const root = ReactDOM.createRoot(
  document.getElementById('root') as HTMLElement
);
root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
