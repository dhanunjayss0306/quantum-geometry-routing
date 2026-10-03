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

const TOPOLOGIES = [
  ["t-shape", "t-shape (2016)"],
  ["star", "star (2016 variant)"],
  ["heavy-hex-21", "heavy-hex 21q (IBM-style)"],
  ["heavy-hex-35", "heavy-hex 35q (IBM-style)"],
  ["heavy-hex-127", "heavy-hex 127q (real Eagle map)"],
  ["hyperbolic-20", "hyperbolic {7,3} 20q (proposed)"],
  ["hyperbolic-43", "hyperbolic {7,3} 43q (proposed)"],
];

export default function RunExperiment() {
  const [topology, setTopology] = React.useState("hyperbolic-20");
  const [condition, setCondition] = React.useState("noisy");
  const [shots, setShots] = React.useState(1000);
  const [result, setResult] = React.useState(null);
  const [loading, setLoading] = React.useState(false);
  const [error, setError] = React.useState(null);

  const run = async () => {
    setLoading(true);
    setError(null);
    try {
      const r = await api.runExperiment(topology, condition, Number(shots));
      setResult(r);
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="panel">
      <h2>Run an experiment</h2>
      <p className="sub">
        Live Bell-state routing on the selected topology, simulated with
        Qiskit Aer. Same noise model and seed convention as the stored matrix.
      </p>
      <div className="form-row">
        <label>
          Topology
          <select value={topology} onChange={(e) => setTopology(e.target.value)}>
            {TOPOLOGIES.map(([v, label]) => (
              <option key={v} value={v}>{label}</option>
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
        <button className="btn primary" onClick={run} disabled={loading}>
          {loading ? "Running..." : "Run experiment"}
        </button>
      </div>
      {error && <p className="error" role="alert">Error: {error}</p>}
      {result && (
        <div className="result" style={{ marginTop: 16 }}>
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
