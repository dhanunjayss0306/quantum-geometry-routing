import React from "react";
import { api, isStaticMode } from "./api/client";
import TopologyGraph from "./components/TopologyGraph";
import Topology3DTab from "./components/Topology3DTab";
import ResultsTable from "./components/ResultsTable";
import RunExperiment from "./components/RunExperiment";
import "./styles.css";

const BAR_COLORS = { ideal: "#4e7a77", noisy: "#a85f1d", protected: "#0e7c8c" };
const REQUIRED = ["t-shape", "heavy-hex-127", "hyperbolic-20"];

function findRow(results, topology, condition) {
  return results.find(
    (r) => r.topology === topology && r.condition === condition
  );
}

/** E1: two labelled groups, values from data, never hard-coded. */
function HeadlineGroups({ results, scaling }) {
  const req = results.filter((r) => REQUIRED.includes(r.topology));
  if (!req.length) return null;

  const swaps = REQUIRED.map((t) => {
    const r = findRow(req, t, "ideal");
    return [t, r ? r.swap_count : null];
  });
  const prot = REQUIRED.map((t) => {
    const noisy = findRow(req, t, "noisy");
    const p = findRow(req, t, "protected");
    const dF = noisy && p ? p.fidelity - noisy.fidelity : null;
    return [t, dF, p ? p.yield : null];
  });

  const hyp127 = (scaling || []).find((s) => s.topology === "hyperbolic-127");
  const hh127n = findRow(req, "heavy-hex-127", "noisy");
  const hh127i = findRow(req, "heavy-hex-127", "ideal");

  return (
    <div>
      <div className="metric-strip" role="region" aria-label="Worst-case route SWAPs">
        <div className="metric-cell" style={{ borderRight: "1px solid var(--rule-strong)" }}>
          <span className="k">Worst-case route (SWAPs)</span>
        </div>
        {swaps.map(([t, v]) => (
          <div key={t} className="metric-cell">
            <span className="k mono">{t}</span>
            <span className="v">{v}</span>
          </div>
        ))}
      </div>
      <div className="metric-strip" role="region" aria-label="Protection effect">
        <div className="metric-cell" style={{ borderRight: "1px solid var(--rule-strong)" }}>
          <span className="k">Protection effect</span>
        </div>
        {prot.map(([t, dF, eta]) => (
          <div key={t} className="metric-cell">
            <span className="k mono">{t}</span>
            <span className="v" style={{ fontSize: 16 }}>
              dF {dF != null ? (dF >= 0 ? "+" : "") + dF.toFixed(3) : "n/a"}
            </span>
            <span className="u">eta {eta != null ? eta.toFixed(3) : "n/a"}</span>
          </div>
        ))}
      </div>
      <p className="muted small" style={{ marginTop: -12, marginBottom: 20 }}>
        Rows have different qubit counts (5 / 127 / 20). Size-matched
        comparison at ~127 qubits:{" "}
        <span className="mono">hyperbolic-127</span> needs{" "}
        {hyp127 ? hyp127.swap_count : "?"} SWAPs (noisy F{" "}
        {hyp127 ? Number(hyp127.fidelity_noisy).toFixed(3) : "?"}) vs{" "}
        <span className="mono">heavy-hex-127</span>{" "}
        {hh127i ? hh127i.swap_count : "?"} SWAPs (F{" "}
        {hh127n ? hh127n.fidelity.toFixed(3) : "?"}){"."}
      </p>
    </div>
  );
}

function FidelityBars({ results }) {
  const groups = {};
  results.forEach((r) => {
    (groups[r.topology] = groups[r.topology] || []).push(r);
  });
  return (
    <div className="panel">
      <h2>Bell-state fidelity</h2>
      <p className="sub">Measured with Qiskit Aer, seed 42, 2000 shots per correlator. Bars start at 0.</p>
      <div className="bar-legend" style={{ display: "flex", gap: 16, marginBottom: 12 }}>
        {Object.entries(BAR_COLORS).map(([cond, color]) => (
          <span key={cond} className="mono small">
            <span
              style={{
                display: "inline-block", width: 12, height: 12,
                background: color, marginRight: 6, verticalAlign: -1,
              }}
            />
            {cond}
          </span>
        ))}
      </div>
      {Object.entries(groups).map(([topo, rows]) => (
        <div key={topo} className="bar-group">
          <div className="bar-label">
            {rows[0].required === false ? (
              <><span className="tag supp">supplementary</span>{topo}</>
            ) : (
              <><span className="tag req">required</span>{topo}</>
            )}
          </div>
          {rows.map((r) => {
            const noisy = rows.find((x) => x.condition === "noisy");
            const dF = r.condition === "protected" && noisy
              ? r.fidelity - noisy.fidelity : null;
            return (
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
                {dF != null && (
                  <span className="mono small muted" style={{ width: 150 }}>
                    dF {(dF >= 0 ? "+" : "") + dF.toFixed(3)} eta {r.yield.toFixed(3)}
                  </span>
                )}
              </div>
            );
          })}
        </div>
      ))}
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
  const [scaling, setScaling] = React.useState([]);
  const [loading, setLoading] = React.useState(true);
  const [staticMode, setStaticMode] = React.useState(false);
  const [error, setError] = React.useState(null);

  React.useEffect(() => {
    Promise.all([api.topologies(), api.results(), api.scaling()])
      .then(([t, r, s]) => {
        setTopologies(t);
        setResults(r);
        setScaling(s);
        setStaticMode(isStaticMode());
      })
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false));
  }, []);

  const statusChip = loading ? (
    <span className="status-chip">connecting...</span>
  ) : error ? (
    <span className="status-chip warn">backend unreachable</span>
  ) : staticMode ? (
    <span className="status-chip warn">static snapshot (stored results)</span>
  ) : (
    <span className="status-chip live">backend connected</span>
  );

  return (
    <div className="app">
      <header className="instrument-head">
        <h1>Quantum Geometry Routing</h1>
        <p className="track">Track 4: Geometry-Aware Quantum Cloud Challenge</p>
        <div className="status-line" role="status">
          {statusChip}
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

      {error && !loading && (
        <p className="error" role="alert">
          Backend not reachable: {error}. Start it with{" "}
          <code className="mono">uvicorn backend.main:app --port 8765</code>.
        </p>
      )}

      {tab === "dashboard" && (
        <main>
          <HeadlineGroups results={results} scaling={scaling} />
          <FidelityBars results={results} />
          <div className="panel">
            <h2>9-case experiment matrix</h2>
            <p className="sub">
              Required cases (Track 4 spec) and supplementary size-matched rows.
              All values from <span className="mono">results/tables/summary.csv</span>.
            </p>
            <ResultsTable results={results} />
          </div>
          <div className="panel">
            <h2>Observed</h2>
            <ul className="small" style={{ margin: 0, paddingLeft: 20 }}>
              <li>Longer routes accumulated more simulated error (fidelity fell as SWAPs rose).</li>
              <li>Protection raised fidelity but discarded shots (yield &lt; 1) and added gates.</li>
            </ul>
          </div>
        </main>
      )}
      {tab === "topologies" && (
        <main className="grid-2">
          {topologies.map((t) => (
            <div key={t.name} className="panel">
              <h3>
                <span className="mono">{t.name}</span>{" "}
                <span className="muted">({t.num_qubits} qubits, diameter {t.diameter})</span>{" "}
                <span className={`tag ${t.tier === "required" ? "req" : t.tier === "supplementary" ? "supp" : ""}`}>
                  {t.tier}
                </span>
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
          <RunExperiment topologies={topologies} staticMode={staticMode} />
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
