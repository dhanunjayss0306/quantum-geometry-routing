import React from "react";

/** The 9-case matrix as a table. Fidelity cells are color-coded. */
export default function ResultsTable({ results }) {
  if (!results.length) return <p>No saved results yet. Run the matrix first.</p>;
  const fidColor = (f) =>
    f >= 0.99 ? "#2ca02c" : f >= 0.9 ? "#d69e00" : "#d62728";
  return (
    <table className="table">
      <thead>
        <tr>
          <th>Topology</th>
          <th>Condition</th>
          <th>SWAPs</th>
          <th>CX</th>
          <th>2q depth</th>
          <th>+SWAP</th>
          <th>+CX</th>
          <th>Fidelity</th>
          <th>Yield</th>
        </tr>
      </thead>
      <tbody>
        {results.map((r) => (
          <tr key={`${r.topology}-${r.condition}`}>
            <td>{r.topology}</td>
            <td>{r.condition}</td>
            <td>{r.swap_count}</td>
            <td>{r.cx_count}</td>
            <td>{r.depth_2q}</td>
            <td>{r.condition === "protected" ? `+${r.added_swap_count}` : "--"}</td>
            <td>{r.condition === "protected" ? `+${r.added_cx_count}` : "--"}</td>
            <td style={{ color: fidColor(r.fidelity), fontWeight: "bold" }}>
              {r.fidelity.toFixed(4)}
            </td>
            <td>{r.yield.toFixed(3)}</td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}
