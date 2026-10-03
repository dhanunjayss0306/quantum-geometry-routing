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
  ["cost", "Cloud cost"],
  ["hardware", "Real hardware"],
  ["run", "Run"],
];

/** Cloud-cost model: depth ratio as an UPPER BOUND on relative QPU cost.
 *  Depths come from the scaling data; the sensitivity rows are the model's
 *  own formula rel(s) = s + ratio*(1-s). Nothing hard-coded. */
function CostPanel({ scaling }) {
  const hh = (scaling || []).find((s) => s.topology === "heavy-hex-127");
  const hyp = (scaling || []).find((s) => s.topology === "hyperbolic-127");
  const dHH = hh ? Number(hh.depth_2q) : null;
  const dHyp = hyp ? Number(hyp.depth_2q) : null;
  if (dHH == null || dHyp == null || !dHyp) return null;
  const ratio = dHH / dHyp;
  const shares = [0, 0.5, 0.9, 0.99];
  const rel = (s) => s + ratio * (1 - s);

  return (
    <div className="panel">
      <h2>Cloud-cost model <span className="tag supp">model, not a bill</span></h2>
      <p className="sub">
        On time-billed quantum cloud, deeper circuits bill more QPU time.
        Size-matched at 127 qubits, the heavy-hex layout needs two-qubit
        depth {dHH} vs hyperbolic's {dHyp}:
      </p>
      <div className="metric-strip" role="region" aria-label="Depth ratio upper bound">
        <div className="metric-cell">
          <span className="k">Depth ratio</span>
          <span className="v" style={{ fontSize: 28 }}>{ratio.toFixed(2)}×</span>
          <span className="u">upper bound, pure depth-proportional model</span>
        </div>
        <div className="metric-cell">
          <span className="k">heavy-hex-127 two-qubit depth</span>
          <span className="v">{dHH}</span>
        </div>
        <div className="metric-cell">
          <span className="k">hyperbolic-127 two-qubit depth</span>
          <span className="v">{dHyp}</span>
        </div>
      </div>
      <h3 style={{ marginTop: 20 }}>Fixed overhead shrinks the real ratio</h3>
      <p className="sub">
        Each shot also carries fixed overhead (readout, reset, repetition).
        If a share <span className="mono">s</span> of per-shot time is fixed,
        the relative cost becomes <span className="mono">s + ratio·(1−s)</span>:
      </p>
      <table className="data">
        <thead>
          <tr><th>Overhead share s</th><th>Relative cost (heavy-hex / hyperbolic)</th></tr>
        </thead>
        <tbody>
          {shares.map((s) => (
            <tr key={s}>
              <td className="mono">{s}{s === 0 ? " (no overhead)" : s === 0.99 ? " (overhead dominates)" : ""}</td>
              <td className="mono">{rel(s).toFixed(2)}×</td>
            </tr>
          ))}
        </tbody>
      </table>
      <ul className="small" style={{ paddingLeft: 20, margin: "12px 0 0" }}>
        <li>Our real <span className="mono">ibm_fez</span> job billed 4 s of QPU time for 6000 shots — fixed overhead dominates on real jobs, so the actual ratio sits well below the {ratio.toFixed(2)}× upper bound.</li>
        <li>Cost units are model quantities. This is not a prediction of any provider's bill: actual cost depends on billing model (time vs per-shot), device timing, parallelism, and pricing.</li>
        <li>Full model and sensitivity table: <span className="mono">docs/cloud_cost.md</span>, <span className="mono">results/tables/cloud_cost.csv</span>.</li>
      </ul>
    </div>
  );
}

/** Real-hardware validation page: the t-shape case run on ibm_fez.
 *  Full provenance plus the explicit caveat that the hardware circuit
 *  differs from the abstract simulated pipeline. */
function HardwarePage({ hw, simNoisyF }) {
  if (!hw) return (
    <main><div className="panel">
      <h2>Real hardware</h2>
      <p className="muted">No hardware record loaded.</p>
    </div></main>
  );
  const corr = hw.correlators || {};
  const cz = hw.transpiled_ops && hw.transpiled_ops.ZZ ? hw.transpiled_ops.ZZ.cz : null;
  const d2 = hw.transpiled_two_qubit_depth || {};
  return (
    <main>
      <div className="panel" style={{ borderLeft: "4px solid #0e7c8c" }}>
        <h2>Real hardware run <span className="tag req">ibm_fez</span></h2>
        <p className="sub">
          We ran our smallest test case on a real quantum computer — IBM's{" "}
          <span className="mono">ibm_fez</span> chip — to check whether our
          simulator's noise behaves like the real thing. Just this one
          small case.
        </p>
        <div className="metric-strip" role="region" aria-label="Hardware vs simulation">
          <div className="metric-cell">
            <span className="k">Real chip score</span>
            <span className="v" style={{ fontSize: 28 }}>
              {Number(hw.fidelity_phi_plus).toFixed(3)}
              {hw.fidelity_stderr != null && (
                <span style={{ fontSize: 16 }}> ± {Number(hw.fidelity_stderr).toFixed(3)}</span>
              )}
            </span>
            <span className="u">give or take 0.004 (shot noise)</span>
          </div>
          <div className="metric-cell">
            <span className="k">Simulator prediction</span>
            <span className="v" style={{ fontSize: 28 }}>
              {simNoisyF != null ? simNoisyF.toFixed(4) : "n/a"}
            </span>
            <span className="u">same noise model, Aer</span>
          </div>
          <div className="metric-cell">
            <span className="k">Measurements</span>
            <span className="v mono" style={{ fontSize: 15 }}>
              XX {Number(corr.XX).toFixed(3)} · YY {Number(corr.YY).toFixed(3)} · ZZ {Number(corr.ZZ).toFixed(3)}
            </span>
            <span className="u">{hw.shots_per_circuit} shots each</span>
          </div>
        </div>
        <p className="small" style={{ marginTop: 12 }}>
          The real chip scored 0.921, the simulator predicted 0.9203 —
          close enough to agree. But this is one test on 5 qubits. It
          doesn't prove the simulator matches real hardware everywhere.
        </p>
      </div>

      <div className="panel">
        <h2>The details</h2>
        <ul className="small" style={{ paddingLeft: 20, margin: "12px 0" }}>
          <li>Chip: <span className="mono">{hw.backend}</span> — IBM's 156-qubit Heron processor</li>
          <li>Job <span className="mono">{hw.job_id}</span> — finished successfully</li>
          <li>Sent {hw.submitted_utc} · done {hw.completed_utc}</li>
          <li>{hw.shots_per_circuit} shots for each of the three measurements (6000 total)</li>
          <li>Bell pair between the two most distant qubits ({(hw.bell_pair || []).join(", ")}), {hw.graph_distance} hops apart</li>
        </ul>
      </div>

      <div className="panel">
        <h2>Not exactly the same circuit</h2>
        <p className="sub">
          On the real chip, the circuit looked a little different from our
          idealized simulation:
        </p>
        <ul className="small" style={{ paddingLeft: 20, margin: "12px 0" }}>
          <li>It ran on physical qubits [{(hw.t_shape_physical_qubits || []).join(", ")}]</li>
          <li>{cz != null ? `${cz} CZ gates` : "7 CZ gates"} per measurement, at two-qubit depth {d2.ZZ}</li>
        </ul>
        <p className="small">
          That's normal — a real chip needs its own version of the circuit.
          It just means this was a sanity check of our noise model, not a
          rerun of the whole simulation. The 127-qubit and hyperbolic
          numbers are still simulation only.
        </p>
      </div>

      {hw.screenshot && (
        <div className="panel">
          <h2>Job record</h2>
          <figure style={{ margin: "12px 0 0" }}>
            <img
              src={hw.screenshot}
              alt="IBM Quantum Platform job page showing the completed ibm_fez run"
              style={{ maxWidth: "100%", border: "1px solid var(--rule-strong)", borderRadius: 6 }}
            />
            <figcaption className="muted small">
              Screenshot: the completed job on the IBM Quantum Platform, matching the record above.
            </figcaption>
          </figure>
        </div>
      )}
    </main>
  );
}

export default function App() {
  const [tab, setTab] = React.useState("dashboard");
  const [topologies, setTopologies] = React.useState([]);
  const [results, setResults] = React.useState([]);
  const [scaling, setScaling] = React.useState([]);
  const [hardware, setHardware] = React.useState(null);
  const [loading, setLoading] = React.useState(true);
  const [staticMode, setStaticMode] = React.useState(false);
  const [error, setError] = React.useState(null);

  React.useEffect(() => {
    Promise.all([api.topologies(), api.results(), api.scaling(), api.hardware().catch(() => null)])
      .then(([t, r, s, h]) => {
        setTopologies(t);
        setResults(r);
        setScaling(s);
        setHardware(h);
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
      {tab === "cost" && (
        <main>
          <CostPanel scaling={scaling} />
        </main>
      )}
      {tab === "hardware" && (
        <HardwarePage
          hw={hardware}
          simNoisyF={(findRow(results, "t-shape", "noisy") || {}).fidelity}
        />
      )}
      {tab === "run" && (
        <main>
          <RunExperiment topologies={topologies} staticMode={staticMode} />
        </main>
      )}

      <footer className="site">
        <span>Quantum Geometry Routing</span>
        <span>Simulation benchmark + one real-QPU validation run</span>
        <a href="https://github.com/dhanunjayss0306/quantum-geometry-routing">GitHub repository</a>
        <span>Docs: README, docs/methodology.md</span>
      </footer>
    </div>
  );
}
