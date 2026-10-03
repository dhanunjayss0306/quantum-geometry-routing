import React from "react";
import { api } from "./api/client";
import TopologyGraph from "./components/TopologyGraph";
import Topology3DTab from "./components/Topology3DTab";
import ResultsTable from "./components/ResultsTable";
import RunExperiment from "./components/RunExperiment";
import "./styles.css";

function FidelityBars({ results }) {
  const groups = {};
  results.forEach((r) => {
    (groups[r.topology] = groups[r.topology] || []).push(r);
  });
  const colors = { ideal: "#2ca02c", noisy: "#d62728", protected: "#1f77b4" };
  return (
    <div className="card">
      <h3>Bell-state fidelity</h3>
      {Object.entries(groups).map(([topo, rows]) => (
        <div key={topo} className="bar-group">
          <div className="bar-label">{topo}</div>
          {rows.map((r) => (
            <div key={r.condition} className="bar-row">
              <span className="bar-cond">{r.condition}</span>
              <div className="bar-track">
                <div
                  className="bar-fill"
                  style={{
                    width: `${r.fidelity * 100}%`,
                    background: colors[r.condition],
                  }}
                />
              </div>
              <span className="bar-val">{r.fidelity.toFixed(3)}</span>
            </div>
          ))}
        </div>
      ))}
    </div>
  );
}

export default function App() {
  const [tab, setTab] = React.useState("dashboard");
  const [topologies, setTopologies] = React.useState([]);
  const [results, setResults] = React.useState([]);
  const [error, setError] = React.useState(null);

  React.useEffect(() => {
    Promise.all([api.topologies(), api.results()])
      .then(([t, r]) => {
        setTopologies(t);
        setResults(r);
      })
      .catch((e) => setError(e.message));
  }, []);

  return (
    <div className="app">
      <header>
        <h1>Quantum Geometry Routing</h1>
        <p>Bell-state routing across chip topologies, simulated with Qiskit Aer. Compare routing cost and fidelity by coupling-graph geometry.</p>
        <nav>
          {["dashboard", "topologies", "3d", "run"].map((t) => (
            <button
              key={t}
              className={tab === t ? "active" : ""}
              onClick={() => setTab(t)}
            >
              {t === "3d" ? "3D" : t[0].toUpperCase() + t.slice(1)}
            </button>
          ))}
        </nav>
      </header>
      {error && <p className="error">Backend not reachable: {error}. Start it with <code>uvicorn backend.main:app --port 8765</code>.</p>}
      {tab === "dashboard" && (
        <main>
          <FidelityBars results={results} />
          <div className="card">
            <h3>9-case experiment matrix</h3>
            <ResultsTable results={results} />
          </div>
        </main>
      )}
      {tab === "topologies" && (
        <main className="grid">
          {topologies.map((t) => (
            <div key={t.name} className="card">
              <h3>{t.name} <small>({t.num_qubits} qubits)</small></h3>
              <p className="muted">{t.description}</p>
              <TopologyGraph topology={t} />
            </div>
          ))}
        </main>
      )}
      {tab === "3d" && topologies.length > 0 && (
        <Topology3DTab topologies={topologies} results={results} />
      )}
      {tab === "run" && (
        <main>
          <RunExperiment />
        </main>
      )}
    </div>
  );
}
