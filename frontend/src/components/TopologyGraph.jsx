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
  const hl = new Set(highlight);
  return (
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
          strokeWidth={hl.has(a) && hl.has(b) ? 2.5 : 1.2}
        />
      ))}
      {Object.entries(pos).map(([n, [x, y]]) => (
        <g key={n}>
          <circle
            cx={x}
            cy={y}
            r={hl.has(Number(n)) ? 9 : 6}
            fill={hl.has(Number(n)) ? "#a85f1d" : "#4e7a77"}
            stroke="#f7f4ee"
            strokeWidth={1.5}
          />
          <text x={x} y={y + 3.5} textAnchor="middle" fontSize={8} fill="#1e1b16"
                fontFamily="IBM Plex Mono, monospace">
            {n}
          </text>
        </g>
      ))}
    </svg>
  );
}
