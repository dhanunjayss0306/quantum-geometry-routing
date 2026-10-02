import React from "react";
import Topology3D from "./Topology3D";

function plainEnglish(t) {
  const hops = t.diameter;
  if (t.family === "hyperbolic")
    return `${hops} hops on ${t.num_qubits} qubits because the surface curves away, so each ring holds exponentially more qubits and distant pairs stay close.`;
  return `${hops} hops on ${t.num_qubits} qubits because the flat layout forces long chains between its most distant qubits.`;
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
    ["SWAPs (worst-case route)", swaps ?? topology.diameter - 1],
    ["Noisy fidelity", noisyF != null ? noisyF.toFixed(3) : "—"],
    ["Protected yield", protYield != null ? protYield.toFixed(3) : "—"],
  ];
  return (
    <div className="card">
      <h3>
        {topology.name} <small>({topology.family})</small>
      </h3>
      <div className="metrics">
        {rows.map(([k, v]) => (
          <div key={k}>
            <span>{k}</span>
            <b>{v}</b>
          </div>
        ))}
      </div>
      <p className="explanation">{plainEnglish(topology)}</p>
      {topology.family === "hyperbolic" && (
        <p className="muted">
          The hyperbolic chip is a simulated proposal, not fabricated hardware.
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
      <div className="card">
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
          Drag to orbit, scroll or pinch to zoom. The gold tube is the worst-case
          Bell-pair route — the path that needs the most SWAPs. Flat chips sit on
          a plane; the hyperbolic chip sits on a curved surface where the number
          of qubits per ring grows exponentially.
        </p>
      </div>

      <div className={compare ? "grid" : ""}>
        {shown.map((t) => (
          <div key={t.name} className="card">
            <div className="topo3d-head">
              <h3>
                {t.name} <small>({t.num_qubits} qubits)</small>
              </h3>
              <button
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
            <p className="muted">
              Worst-case Bell pair: q{t.bell_pair[0]} → q{t.bell_pair[1]} (
              {t.diameter} hops, route {t.route.join(" → ")})
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
