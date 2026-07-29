import React from "react";
import { createRoot } from "react-dom/client";

import "./styles.css";

function App() {
  return (
    <main className="app-shell">
      <section className="panel">
        <p className="eyebrow">IEP</p>
        <h1>Icodeup Enterprise Platform</h1>
        <p>
          Suite inteligente para operar empresas, datos, procesos y decisiones.
        </p>
      </section>
    </main>
  );
}

createRoot(document.getElementById("root") as HTMLElement).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
