import React from "react";
import { api } from "../api/client";

/** One-line plain-English explanation of a result. */
function explain(r) {
  const bits = [];
  if (r.swap_count === 0) {
    bits.push("no SWAPs were needed -- the qubits were directly connected");
  } else {
    bits.push(
      `${r.swap_count} SWAP${r.swap_count > 1 ? "s were" : " was"} needed because ` +
        `qubits ${r.bell_pair[0]} and ${r.bell_pair[1]} are ${r.graph_distance} hops apart`
    );
  }
  bits.push(`fidelity ${r.fidelity.toFixed(3)}`);
  if (r.condition === "protected") {
    bits.push(
      `after discarding ${((1 - r.yield) * 100).toFixed(1)}% of shots with a bad syndrome`
    );
    if (r.added_swap_count || r.added_cx_count) {
      bits.push(
        `protection itself cost +${r.added_swap_count} SWAPs and +${r.added_cx_count} CX gates`
      );
    }
  } else if (r.condition === "noisy") {
    bits.push("under depolarizing + readout noise");
  } else {
    bits.push("with no noise");
  }
  return bits.join(", ") + ".";
}

const TIER_LABELS = {
  required: "Required benchmark",
  supplementary: "Supplementary",
  exploratory: "Exploratory",
};
const TIER_ORDER = ["required", "supplementary", "exploratory"];

function shortLabel(t) {
  const q = `${t.num_qubits}q`;
  if (t.name === "heavy-hex-127") return `heavy-hex 127q (Eagle-style map)`;
  if (t.family === "hyperbolic") return `hyperbolic {7,3} ${q} (proposed)`;
  if (t.name.startsWith("heavy-hex")) return `heavy-hex ${q} (IBM-style)`;
  return `${t.name} ${q}`;
}

export default function RunExperiment({ topologies = [], staticMode = false }) {
  const [topology, setTopology] = React.useState("hyperbolic-20");
  const [condition, setCondition] = React.useState("noisy");
  const [shots, setShots] = React.useState(2000);
  const [seed, setSeed] = React.useState(42);
  const [result, setResult] = React.useState(null);
  const [loading, setLoading] = React.useState(false);
  const [error, setError] = React.useState(null);

  const groups = {};
  topologies.forEach((t) => {
    const tier = t.tier || "exploratory";
    (groups[tier] = groups[tier] || []).push(t);
  });

  const run = async () => {
    setLoading(true);
    setError(null);
    try {
      const r = await api.runExperiment(
        topology, condition, Number(shots), Number(seed)
      );
      setResult(r);
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="panel">
      <h2>Run one benchmark case</h2>
      <p className="sub">
        Run a local Aer simulation on the selected topology. Same noise
        model and seed convention as the stored matrix. Never a quantum
        processor.
      </p>
      {staticMode && (
        <p className="error" role="note">
          Running simulations needs the local backend:{" "}
          <code className="mono">uvicorn backend.main:app --port 8765</code>
        </p>
      )}
      <div className="form-row">
        <label>
          Topology
          <select value={topology} onChange={(e) => setTopology(e.target.value)}>
            {TIER_ORDER.filter((g) => groups[g]).map((g) => (
              <optgroup key={g} label={TIER_LABELS[g]}>
                {groups[g].map((t) => (
                  <option key={t.name} value={t.name}>
                    {shortLabel(t)}
                  </option>
                ))}
              </optgroup>
            ))}
          </select>
        </label>
        <label>
          Condition
          <select value={condition} onChange={(e) => setCondition(e.target.value)}>
            <option value="ideal">ideal</option>
            <option value="noisy">noisy</option>
            <option value="protected">noisy + protected</option>
          </select>
        </label>
        <label>
          Shots
          <input
            type="number"
            min={100}
            max={20000}
            value={shots}
            onChange={(e) => setShots(e.target.value)}
          />
        </label>
        <label>
          Seed
          <input
            type="number"
            value={seed}
            onChange={(e) => setSeed(e.target.value)}
          />
        </label>
        <button
          className="btn primary"
          onClick={run}
          disabled={loading || staticMode}
        >
          {loading ? "Running..." : "Run case"}
        </button>
      </div>
      {error && <p className="error" role="alert">Error: {error}</p>}
      {result && (
        <div className="result" style={{ marginTop: 16 }}>
          <p className="mono small muted">
            {result.topology} / {result.condition} / {result.shots} shots /
            seed {result.seed}
          </p>
          <div className="metric-strip">
            <div className="metric-cell"><span className="k">SWAPs</span><span className="v">{result.swap_count}</span></div>
            <div className="metric-cell"><span className="k">CX gates</span><span className="v">{result.cx_count}</span></div>
            <div className="metric-cell"><span className="k">2q depth</span><span className="v">{result.depth_2q}</span></div>
            <div className="metric-cell"><span className="k">Fidelity</span><span className="v">{result.fidelity.toFixed(4)}</span></div>
            <div className="metric-cell"><span className="k">Yield</span><span className="v">{result.yield.toFixed(3)}</span></div>
            {result.condition === "protected" && (
              <div className="metric-cell"><span className="k">Protection cost</span><span className="v" style={{ fontSize: 15 }}>+{result.added_swap_count} SWAP, +{result.added_cx_count} CX</span></div>
            )}
          </div>
          <p className="explanation">{explain(result)}</p>
        </div>
      )}
    </div>
  );
}
