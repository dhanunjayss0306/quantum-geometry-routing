/** Thin client for the FastAPI backend (proxied by Vite in dev). */

async function get(path) {
  const res = await fetch(path);
  if (!res.ok) throw new Error(`${path} -> ${res.status}`);
  return res.json();
}

async function post(path, body) {
  const res = await fetch(path, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || `${path} -> ${res.status}`);
  }
  return res.json();
}

export const api = {
  health: () => get("/health"),
  topologies: () => get("/api/topologies"),
  results: () => get("/api/results"),
  runExperiment: (topology, condition, shots = 2000, seed = 42) =>
    post("/api/experiments/run", { topology, condition, shots, seed }),
  runAll: (shots = 2000, seed = 42) =>
    post(`/api/experiments/run-all?shots=${shots}&seed=${seed}`),
};
