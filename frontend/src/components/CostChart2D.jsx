import React from "react";

/**
 * Where-the-money-goes chart: total estimated cost ($) for geometry A vs B
 * as fixed overhead per shot grows. Two plain lines that start apart and
 * meet — the whole cost story in one glance. Rebuilds live from the
 * calculator's inputs.
 *
 * Props: depthA, depthB, labelA, labelB, shots, price, tLayer, tFixed.
 */
const W = 640, H = 340, PAD_L = 70, PAD_R = 16, PAD_T = 18, PAD_B = 44;
const N = 41, OVH_MAX = 2000;

function fmt$(v) {
  if (v >= 1e6) return `$${(v / 1e6).toFixed(1)}M`;
  if (v >= 1e3) return `$${(v / 1e3).toFixed(1)}k`;
  return `$${v.toFixed(v < 10 ? 2 : 0)}`;
}

export default function CostChart2D({ depthA, depthB, labelA, labelB, shots, price, tLayer, tFixed }) {
  const cost = (ovh, d) => (shots * (d * tLayer + ovh) * price) / 1e6;
  const ptsA = [], ptsB = [];
  for (let i = 0; i < N; i++) {
    const ovh = (i / (N - 1)) * OVH_MAX;
    ptsA.push([ovh, cost(ovh, depthA)]);
    ptsB.push([ovh, cost(ovh, depthB)]);
  }
  const yMax = Math.max(ptsA[N - 1][1], ptsB[N - 1][1], 1e-9) * 1.05;
  const x = (ovh) => PAD_L + (ovh / OVH_MAX) * (W - PAD_L - PAD_R);
  const y = (c) => H - PAD_B - (c / yMax) * (H - PAD_T - PAD_B);
  const line = (pts) => pts.map(([o, c], i) => `${i ? "L" : "M"}${x(o).toFixed(1)},${y(c).toFixed(1)}`).join(" ");

  const yTicks = [0, yMax / 2, yMax];
  const xTicks = [0, 500, 1000, 1500, 2000];
  const hereX = x(Math.min(Math.max(tFixed, 0), OVH_MAX));

  return (
    <div>
      <svg viewBox={`0 0 ${W} ${H}`} style={{ width: "100%", height: "auto", display: "block" }} role="img"
        aria-label={`Cost comparison chart for ${labelA} versus ${labelB}`}>
        {/* gridlines */}
        {yTicks.map((t, i) => (
          <g key={i}>
            <line x1={PAD_L} x2={W - PAD_R} y1={y(t)} y2={y(t)} stroke="#ddd5c4" strokeWidth="1" />
            <text x={PAD_L - 8} y={y(t) + 5} textAnchor="end" fontSize="14" fill="#1e1b16" fontFamily="ui-monospace, monospace">
              {fmt$(t)}
            </text>
          </g>
        ))}
        {xTicks.map((t) => (
          <text key={t} x={x(t)} y={H - PAD_B + 22} textAnchor="middle" fontSize="14" fill="#1e1b16" fontFamily="ui-monospace, monospace">
            {t}
          </text>
        ))}
        <text x={(W + PAD_L - PAD_R) / 2} y={H - 6} textAnchor="middle" fontSize="15" fill="#1e1b16">
          fixed overhead per shot (µs)
        </text>
        {/* you-are-here marker */}
        <line x1={hereX} x2={hereX} y1={PAD_T} y2={H - PAD_B} stroke="#a85f1d" strokeWidth="1.5" strokeDasharray="5 4" />
        <text x={hereX} y={PAD_T - 4} textAnchor="middle" fontSize="13" fill="#a85f1d" fontFamily="ui-monospace, monospace">
          your setting
        </text>
        {/* the two cost lines: A solid, B dashed */}
        <path d={line(ptsB)} fill="none" stroke="#a85f1d" strokeWidth="3.5" strokeDasharray="8 5" />
        <path d={line(ptsA)} fill="none" stroke="#0e7c8c" strokeWidth="3.5" />
        <circle cx={hereX} cy={y(cost(tFixed, depthA))} r="6" fill="#0e7c8c" stroke="#fffdf8" strokeWidth="2" />
        <rect x={hereX - 5.5} y={y(cost(tFixed, depthB)) - 5.5} width="11" height="11" fill="#a85f1d" stroke="#fffdf8" strokeWidth="2" />
      </svg>
      <div style={{ display: "flex", gap: 20, marginTop: 8, flexWrap: "wrap", alignItems: "center" }}>
        <span className="mono small">
          <span style={{ display: "inline-block", width: 22, height: 4, background: "#0e7c8c", marginRight: 8, verticalAlign: "middle", borderRadius: 2 }} />
          {labelA} — {fmt$(cost(tFixed, depthA))}
        </span>
        <span className="mono small">
          <span style={{ display: "inline-block", width: 22, height: 0, borderTop: "4px dashed #a85f1d", marginRight: 8, verticalAlign: "middle" }} />
          {labelB} — {fmt$(cost(tFixed, depthB))}
        </span>
      </div>
      <p className="small" style={{ marginTop: 10 }}>
        At zero overhead the gap is biggest ({(cost(0, depthA) / Math.max(cost(0, depthB), 1e-9)).toFixed(2)}×).
        At your overhead setting it is {(cost(tFixed, depthA) / Math.max(cost(tFixed, depthB), 1e-9)).toFixed(2)}× —
        the lines meet because fixed overhead dominates.
      </p>
    </div>
  );
}
