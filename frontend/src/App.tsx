import React from 'react';
import './App.css';
import SiniestroForm from './components/SiniestroForm';

function App() {
  return (
    <div className="App">
      <header className="App-header">
        <h1>Sistema de Informes de Siniestros</h1>
        <p>Llena los campos obligatorios para generar el informe.</p>
      </header>
      <main>
        <SiniestroForm />
      </main>
    </div>
  );
}

export default App;
