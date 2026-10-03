import React from "react";

/** The experiment matrix as a technical table. Values from summary.csv. */
export default function ResultsTable({ results }) {
  if (!results.length)
    return <p className="muted">No saved results yet. Run the matrix first.</p>;
  const fidColor = (f) =>
    f >= 0.99 ? "#4e7a77" : f >= 0.9 ? "#a85f1d" : "#b3261e";
  return (
    <div style={{ overflowX: "auto" }}>
      <table className="data">
        <thead>
          <tr>
            <th>Topology</th>
            <th>Set</th>
            <th>Condition</th>
            <th className="num">SWAPs</th>
            <th className="num">CX</th>
            <th className="num">2q depth</th>
            <th className="num">+SWAP</th>
            <th className="num">+CX</th>
            <th className="num">Fidelity</th>
            <th className="num">Yield</th>
          </tr>
        </thead>
        <tbody>
          {results.map((r) => (
            <tr key={`${r.topology}-${r.condition}`}>
              <td className="mono">{r.topology}</td>
              <td>
                <span className={`tag ${r.required === false ? "supp" : "req"}`}>
                  {r.required === false ? "supp." : "req."}
                </span>
              </td>
              <td>{r.condition}</td>
              <td className="num">{r.swap_count}</td>
              <td className="num">{r.cx_count}</td>
              <td className="num">{r.depth_2q}</td>
              <td className="num">
                {r.condition === "protected" ? `+${r.added_swap_count}` : "--"}
              </td>
              <td className="num">
                {r.condition === "protected" ? `+${r.added_cx_count}` : "--"}
              </td>
              <td className="num" style={{ color: fidColor(r.fidelity), fontWeight: 600 }}>
                {r.fidelity.toFixed(4)}
              </td>
              <td className="num">{r.yield.toFixed(3)}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
