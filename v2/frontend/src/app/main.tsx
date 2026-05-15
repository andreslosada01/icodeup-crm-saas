import React from "react";
import { createRoot } from "react-dom/client";

import "./styles.css";

function App() {
  return (
    <main className="app-shell">
      <section className="panel">
        <p className="eyebrow">IcodeUp CRM V2</p>
        <h1>Arquitectura modular iniciada</h1>
        <p>
          Esta version sera migrada por modulos desde la V1 funcional hacia una base SaaS corporativa.
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

