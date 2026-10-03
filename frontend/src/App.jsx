import React from "react";
import { api } from "./api/client";
import TopologyGraph from "./components/TopologyGraph";
import Topology3DTab from "./components/Topology3DTab";
import ResultsTable from "./components/ResultsTable";
import RunExperiment from "./components/RunExperiment";
import "./styles.css";

const BAR_COLORS = { ideal: "#4e7a77", noisy: "#a85f1d", protected: "#0e7c8c" };

function FidelityBars({ results }) {
  const groups = {};
  results.forEach((r) => {
    (groups[r.topology] = groups[r.topology] || []).push(r);
  });
  return (
    <div className="panel">
      <h2>Bell-state fidelity</h2>
      <p className="sub">Measured with Qiskit Aer, seed 42, 2000 shots per correlator.</p>
      {Object.entries(groups).map(([topo, rows]) => (
        <div key={topo} className="bar-group">
          <div className="bar-label">
            {rows[0].required === false ? (
              <><span className="tag supp">supplementary</span>{topo}</>
            ) : (
              <><span className="tag req">required</span>{topo}</>
            )}
          </div>
          {rows.map((r) => (
            <div key={r.condition} className="bar-row">
              <span className="bar-cond">{r.condition}</span>
              <div className="bar-track">
                <div
                  className="bar-fill"
                  style={{
                    width: `${r.fidelity * 100}%`,
                    background: BAR_COLORS[r.condition],
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

function HeadlineMetrics({ results }) {
  const req = results.filter((r) => r.required !== false);
  const cell = (topo, cond, field, digits, unit) => {
    const r = req.find((x) => x.topology === topo && x.condition === cond);
    if (!r) return <div className="metric-cell"><span className="k">n/a</span></div>;
    return (
      <div className="metric-cell">
        <span className="k">{topo} {cond}</span>
        <span className="v">{Number(r[field]).toFixed(digits)}</span>
        {unit && <span className="u">{unit}</span>}
      </div>
    );
  };
  const swaps = (topo) => {
    const r = req.find((x) => x.topology === topo && x.condition === "ideal");
    return r ? r.swap_count : null;
  };
  if (!req.length) return null;
  return (
    <div className="metric-strip" role="region" aria-label="Headline benchmark metrics">
      <div className="metric-cell">
        <span className="k">Eagle-127 SWAPs</span>
        <span className="v">{swaps("heavy-hex-127")}</span>
      </div>
      <div className="metric-cell">
        <span className="k">Hyperbolic-20 SWAPs</span>
        <span className="v">{swaps("hyperbolic-20")}</span>
      </div>
      {cell("heavy-hex-127", "noisy", "fidelity", 4)}
      {cell("heavy-hex-127", "protected", "fidelity", 4)}
      {cell("hyperbolic-20", "noisy", "fidelity", 4)}
      {cell("hyperbolic-20", "protected", "fidelity", 4)}
    </div>
  );
}

const TABS = [
  ["dashboard", "Dashboard"],
  ["topologies", "Topologies"],
  ["3d", "3D View"],
  ["run", "Run"],
];

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
      <header className="instrument-head">
        <h1>Quantum Geometry Routing</h1>
        <p className="track">Track 4: Geometry-Aware Quantum Cloud Challenge</p>
        <div className="status-line" role="status">
          <span className={`status-chip ${error ? "warn" : "live"}`}>
            {error ? "backend unreachable" : "backend connected"}
          </span>
          <span className="status-chip">Aer simulation</span>
          <span className="status-chip">seed 42</span>
          <span className="status-chip">reproducible benchmark</span>
        </div>
      </header>

      <div className="research-q">
        <span className="q-label">Research question</span>
        Which coupling-graph geometry keeps a worst-case Bell-state route short?
      </div>

      <nav className="tabs" aria-label="Views">
        {TABS.map(([key, label]) => (
          <button
            key={key}
            className={tab === key ? "active" : ""}
            onClick={() => setTab(key)}
            aria-current={tab === key ? "page" : undefined}
          >
            {label}
          </button>
        ))}
      </nav>

      {error && (
        <p className="error" role="alert">
          Backend not reachable: {error}. Start it with{" "}
          <code className="mono">uvicorn backend.main:app --port 8765</code>.
        </p>
      )}

      {tab === "dashboard" && (
        <main>
          <HeadlineMetrics results={results} />
          <FidelityBars results={results} />
          <div className="panel">
            <h2>9-case experiment matrix</h2>
            <p className="sub">
              Required cases (Track 4 spec) and supplementary size-matched rows.
              All values from <span className="mono">results/tables/summary.csv</span>.
            </p>
            <ResultsTable results={results} />
          </div>
        </main>
      )}
      {tab === "topologies" && (
        <main className="grid-2">
          {topologies.map((t) => (
            <div key={t.name} className="panel">
              <h3>
                <span className="mono">{t.name}</span>{" "}
                <span className="muted">({t.num_qubits} qubits, diameter {t.diameter})</span>
              </h3>
              <p className="muted">{t.description}</p>
              <TopologyGraph topology={t} />
              <p className="small muted">
                Worst-case route: <span className="mono">q{t.bell_pair[0]} to q{t.bell_pair[1]}</span> ({t.diameter} hops).
                {t.family === "hyperbolic" && " Geometric visualization of proposed {7,3} coupling topology."}
              </p>
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

      <footer className="site">
        <span>Quantum Geometry Routing</span>
        <span>Simulation-based research prototype</span>
        <a href="https://github.com/dhanunjayss0306/quantum-geometry-routing">GitHub repository</a>
        <span>Docs: README, docs/methodology.md</span>
      </footer>
    </div>
  );
}
