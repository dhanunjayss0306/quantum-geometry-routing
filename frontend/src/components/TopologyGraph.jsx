import React from "react";

/**
 * Draw a coupling graph as concentric BFS rings from qubit 0.
 * Ring depth = graph distance, so the drawing literally shows how
 * "spread out" each topology is -- the project's core idea.
 */
function layoutRings(numQubits, edges) {
  const adj = Array.from({ length: numQubits }, () => []);
  edges.forEach(([a, b]) => {
    adj[a].push(b);
    adj[b].push(a);
  });
  const depth = new Array(numQubits).fill(-1);
  depth[0] = 0;
  const queue = [0];
  while (queue.length) {
    const u = queue.shift();
    adj[u].forEach((v) => {
      if (depth[v] === -1) {
        depth[v] = depth[u] + 1;
        queue.push(v);
      }
    });
  }
  const rings = {};
  depth.forEach((d, i) => {
    (rings[d] = rings[d] || []).push(i);
  });
  const W = 420;
  const H = 340;
  const cx = W / 2;
  const cy = H / 2;
  const maxD = Math.max(...Object.keys(rings).map(Number));
  const pos = {};
  Object.entries(rings).forEach(([d, nodes]) => {
    const r = (Number(d) / Math.max(maxD, 1)) * Math.min(W, H) * 0.44;
    nodes.forEach((n, k) => {
      if (r === 0) {
        pos[n] = [cx, cy];
      } else {
        const ang = (2 * Math.PI * k) / nodes.length - Math.PI / 2;
        pos[n] = [cx + r * Math.cos(ang), cy + r * Math.sin(ang)];
      }
    });
  });
  return { pos, depth, W, H };
}

export default function TopologyGraph({ topology, highlight = [] }) {
  const { pos, W, H } = React.useMemo(
    () => layoutRings(topology.num_qubits, topology.edges),
    [topology]
  );
  // Labels on by default for small graphs; off for >40 qubits (they overlap).
  const [showLabels, setShowLabels] = React.useState(topology.num_qubits <= 40);
  const hl = new Set(highlight);
  const endpoints = new Set(topology.bell_pair || []);
  const big = topology.num_qubits > 40;
  const nodeR = big ? 3.2 : 6;
  const hlR = big ? 5.5 : 9;
  const edgeW = big ? 0.7 : 1.2;
  const fontSize = big ? 6.5 : 8;
  const label = (n) => showLabels || endpoints.has(Number(n));
  return (
    <div>
      <label className="check small" style={{ marginBottom: 6 }}>
        <input
          type="checkbox"
          checked={showLabels}
          onChange={(e) => setShowLabels(e.target.checked)}
        />
        Show qubit labels
      </label>
      <svg width={W} height={H} className="topo-svg" role="img"
           aria-label={`Coupling graph of ${topology.num_qubits} qubits`}>
        {topology.edges.map(([a, b], i) => (
          <line
            key={i}
            x1={pos[a][0]}
            y1={pos[a][1]}
            x2={pos[b][0]}
            y2={pos[b][1]}
            stroke={hl.has(a) && hl.has(b) ? "#a85f1d" : "#b9ae97"}
            strokeWidth={hl.has(a) && hl.has(b) ? edgeW + 1.3 : edgeW}
          />
        ))}
        {Object.entries(pos).map(([n, [x, y]]) => (
          <g key={n}>
            <circle
              cx={x}
              cy={y}
              r={hl.has(Number(n)) ? hlR : nodeR}
              fill={hl.has(Number(n)) ? "#a85f1d" : "#4e7a77"}
              stroke="#f7f4ee"
              strokeWidth={1.5}
            />
            {label(n) && (
              <text x={x} y={y + fontSize * 0.35} textAnchor="middle"
                    fontSize={fontSize} fill="#1e1b16"
                    fontFamily="IBM Plex Mono, monospace">
                {n}
              </text>
            )}
          </g>
        ))}
      </svg>
      <p className="small muted" style={{ marginTop: 6 }}>
        Layout: qubits placed by graph distance from q0, so the drawing
        shows how spread out the chip is. It is not the physical chip shape.
      </p>
    </div>
  );
}
