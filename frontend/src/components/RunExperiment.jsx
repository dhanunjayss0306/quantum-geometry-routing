import React from "react";
import { api } from "../api/client";

/** One-line plain-English explanation of a result. Judges love this. */
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
      `after discarding ${((1 - r.yield) * 100).toFixed(1)}% of shots that failed the parity check`
    );
  } else if (r.condition === "noisy") {
    bits.push("under depolarizing + readout noise");
  } else {
    bits.push("in the ideal noiseless world");
  }
  return bits.join(", ") + ".";
}

export default function RunExperiment() {
  const [topology, setTopology] = React.useState("hyperbolic");
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
    <div className="card">
      <h3>Run an experiment</h3>
      <div className="form-row">
        <label>
          Topology
          <select value={topology} onChange={(e) => setTopology(e.target.value)}>
            <option value="star">star (2016)</option>
            <option value="heavy-hex">heavy-hex (today)</option>
            <option value="hyperbolic">hyperbolic (future)</option>
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
        <button onClick={run} disabled={loading}>
          {loading ? "Running..." : "Run Bell-state routing"}
        </button>
      </div>
      {error && <p className="error">Error: {error}</p>}
      {result && (
        <div className="result">
          <div className="metrics">
            <div><span>SWAPs</span><b>{result.swap_count}</b></div>
            <div><span>CX gates</span><b>{result.cx_count}</b></div>
            <div><span>Depth</span><b>{result.depth}</b></div>
            <div><span>Fidelity</span><b>{result.fidelity.toFixed(4)}</b></div>
            <div><span>Yield</span><b>{result.yield.toFixed(3)}</b></div>
          </div>
          <p className="explanation">{explain(result)}</p>
        </div>
      )}
    </div>
  );
}
