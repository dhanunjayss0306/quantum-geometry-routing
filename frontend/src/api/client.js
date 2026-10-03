/** Thin client for the FastAPI backend (proxied by Vite in dev).
 *
 *  Static fallback: if the backend is unreachable, GETs fall back to the
 *  committed snapshot in frontend/public/data/ (written by
 *  scripts/export_static_data.py) and `isStaticMode()` returns true.
 *  POSTs (running simulations) need the backend and fail with a plain
 *  message in static mode.
 */

let staticMode = false;
export const isStaticMode = () => staticMode;

function readableError(path, status, body) {
  const detail = body && body.detail;
  if (Array.isArray(detail)) {
    // FastAPI 422: [{loc: ["body", "shots"], msg: "..."}, ...]
    return detail
      .map((d) => {
        const loc = Array.isArray(d.loc)
          ? d.loc.filter((x) => x !== "body").join(".")
          : "";
        return `${loc ? loc + ": " : ""}${d.msg || "invalid value"}`;
      })
      .join("; ");
  }
  if (typeof detail === "string") return detail;
  return `${path} -> ${status}`;
}

async function staticSnapshot(name) {
  const res = await fetch(`/data/${name}.json`);
  if (!res.ok)
    throw new Error("backend unreachable and no static snapshot available");
  staticMode = true;
  return res.json();
}

async function get(path) {
  const name = path.split("/").pop();
  try {
    const res = await fetch(path);
    if (res.ok) return res.json();
    // API answered with an error (backend down, proxy 500, ...):
    // fall back to the static snapshot before giving up.
    try {
      return await staticSnapshot(name);
    } catch {
      const err = await res.json().catch(() => ({}));
      throw new Error(readableError(path, res.status, err));
    }
  } catch (e) {
    // Network failure (no route to the dev server at all).
    if (e instanceof TypeError) return staticSnapshot(name);
    throw e;
  }
}

async function post(path, body) {
  if (staticMode)
    throw new Error(
      "Running simulations needs the local backend: uvicorn backend.main:app --port 8765"
    );
  const res = await fetch(path, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(readableError(path, res.status, err));
  }
  return res.json();
}

export const api = {
  health: () => get("/health"),
  topologies: () => get("/api/topologies"),
  results: () => get("/api/results"),
  scaling: () => get("/api/scaling"),
  runExperiment: (topology, condition, shots = 2000, seed = 42) =>
    post("/api/experiments/run", { topology, condition, shots, seed }),
  runAll: (shots = 2000, seed = 42) =>
    post(`/api/experiments/run-all?shots=${shots}&seed=${seed}`),
};
