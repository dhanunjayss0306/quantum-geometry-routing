import React from "react";
import Topology3D from "./Topology3D";

function plainEnglish(t) {
  const hops = t.diameter;
  if (t.family === "hyperbolic")
    return `${hops} hops on ${t.num_qubits} qubits. The surface curves away, so each ring holds more qubits and distant pairs stay close.`;
  return `${hops} hops on ${t.num_qubits} qubits. The flat layout forces long chains between its most distant qubits.`;
}

function stat(results, topology, condition, field) {
  const r = results.find(
    (x) => x.topology === topology && x.condition === condition
  );
  return r ? r[field] : null;
}

function ChipStats({ topology, results }) {
  const noisyF = stat(results, topology.name, "noisy", "fidelity");
  const protYield = stat(results, topology.name, "protected", "yield");
  const swaps = stat(results, topology.name, "noisy", "swap_count");
  const rows = [
    ["Qubits", topology.num_qubits],
    ["Diameter", `${topology.diameter} hops`],
    ["SWAPs, worst-case route", swaps ?? topology.diameter - 1],
    ["Noisy fidelity", noisyF != null ? noisyF.toFixed(3) : "n/a"],
    ["Protected yield", protYield != null ? protYield.toFixed(3) : "n/a"],
  ];
  return (
    <div className="panel">
      <h3>
        <span className="mono">{topology.name}</span>{" "}
        <span className="muted">({topology.family})</span>
      </h3>
      <div className="metric-strip">
        {rows.map(([k, v]) => (
          <div key={k} className="metric-cell">
            <span className="k">{k}</span>
            <span className="v" style={{ fontSize: 16 }}>{v}</span>
          </div>
        ))}
      </div>
      <p className="explanation">{plainEnglish(topology)}</p>
      {topology.family === "hyperbolic" && (
        <p className="muted">
          Geometric visualization of proposed {"{7,3}"} coupling topology.
          Simulated proposal, not fabricated hardware.
        </p>
      )}
    </div>
  );
}

export default function Topology3DTab({ topologies, results }) {
  const [selected, setSelected] = React.useState(topologies[0]?.name);
  const [compare, setCompare] = React.useState(false);
  const [autoRotate, setAutoRotate] = React.useState(
    () => !(window.matchMedia?.("(prefers-reduced-motion: reduce)").matches ?? false)
  );
  const viewerRefs = React.useRef({});

  const shown = compare
    ? topologies
    : topologies.filter((t) => t.name === selected);

  return (
    <main>
      <div className="panel">
        <h2>Coupling-graph viewer</h2>
        <p className="sub">
          Geometry from <span className="mono">GET /api/topologies</span>.
          Drag to orbit, scroll or pinch to zoom.
        </p>
        <div className="form-row">
          <label>
            Chip
            <select
              value={selected}
              onChange={(e) => setSelected(e.target.value)}
              disabled={compare}
              aria-label="Select chip topology"
            >
              {topologies.map((t) => (
                <option key={t.name} value={t.name}>
                  {t.name} ({t.num_qubits} qubits)
                </option>
              ))}
            </select>
          </label>
          <label className="check">
            <input
              type="checkbox"
              checked={compare}
              onChange={(e) => setCompare(e.target.checked)}
            />
            Compare all (same scale)
          </label>
          <label className="check">
            <input
              type="checkbox"
              checked={autoRotate}
              onChange={(e) => setAutoRotate(e.target.checked)}
            />
            Auto-rotate
          </label>
        </div>
        <p className="muted">
          The amber tube marks the worst-case Bell-pair route, the path that
          needs the most SWAPs. Flat chips sit on a plane. The hyperbolic chip
          sits on a curved surface where the qubit count per ring grows
          exponentially.
        </p>
      </div>

      <div className={compare ? "grid-2" : ""}>
        {shown.map((t) => (
          <div key={t.name} className="panel">
            <div className="topo3d-head">
              <h3>
                <span className="mono">{t.name}</span>{" "}
                <span className="muted">({t.num_qubits} qubits)</span>
              </h3>
              <button
                className="btn"
                onClick={() =>
                  viewerRefs.current[t.name]?.exportPNG?.(`${t.name}-3d.png`)
                }
              >
                Export PNG
              </button>
            </div>
            <Topology3D
              ref={(el) => (viewerRefs.current[t.name] = el)}
              topology={t}
              normalize={compare}
              autoRotate={autoRotate}
            />
            <p className="muted small">
              Worst-case Bell pair:{" "}
              <span className="mono">q{t.bell_pair[0]} to q{t.bell_pair[1]}</span>{" "}
              ({t.diameter} hops, route{" "}
              <span className="mono">{t.route.join(" -> ")}</span>)
            </p>
          </div>
        ))}
      </div>

      {(compare ? topologies : topologies.filter((t) => t.name === selected)).map(
        (t) => (
          <ChipStats key={t.name} topology={t} results={results} />
        )
      )}
    </main>
  );
}
