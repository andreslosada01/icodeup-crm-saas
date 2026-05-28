import React from "react";
import { createRoot } from "react-dom/client";

import "./styles.css";

function App() {
  return (
    <main className="app-shell">
      <section className="panel">
        <p className="eyebrow">IcodeUp CRM V2</p>
        <h1>Arquitectura SaaS corporativa</h1>
        <p>
          Base modular para evolucionar el frontend React de la plataforma actual.
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
