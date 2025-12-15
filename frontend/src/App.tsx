import React from 'react';
import { BrowserRouter as Router, Switch, Route, Link } from 'react-router-dom';
import './App.css';
import SiniestroForm from './components/SiniestroForm';
import SiniestrosList from './components/SiniestrosList';
import SiniestroDetail from './components/SiniestroDetail';
import SiniestroEdit from './components/SiniestroEdit';

function App() {
  return (
    <Router>
      <div className="App">
        <header className="App-header">
          <h1>Sistema de Informes de Siniestros</h1>
          <nav>
            <Link to="/">Nuevo Siniestro</Link> | <Link to="/siniestros">Ver Siniestros</Link>
          </nav>
          <p>Llena los campos obligatorios para generar el informe.</p>
        </header>
        <main>
          <Switch>
            <Route exact path="/" component={SiniestroForm} />
            <Route path="/siniestro/nuevo" component={SiniestroForm} />
            <Route path="/siniestro/:id/editar" component={SiniestroForm} />
            <Route path="/siniestros" component={SiniestrosList} />
            <Route path="/siniestro/:id" component={SiniestroDetail} />
          </Switch>
        </main>
      </div>
    </Router>
  );
}

export default App;
