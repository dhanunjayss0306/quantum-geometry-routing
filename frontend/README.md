# Frontend — Track 4 dashboard

React + Vite dashboard for the quantum experiment API.

## Run

Terminal 1 (backend, from repo root):

```bash
source .venv/bin/activate
uvicorn backend.main:app --port 8765
```

Terminal 2 (frontend, from `frontend/`):

```bash
npm install
npm run dev        # opens http://localhost:5173
```

The Vite dev server proxies `/api` and `/health` to the backend.

## Pages

- **Dashboard** — fidelity bars + the 9-case experiment matrix table.
- **Topologies** — coupling graphs drawn as BFS rings from qubit 0, so the
  drawing itself shows how "spread out" each topology is.
- **3D** — rotatable 3D chip viewer (three.js). Spheres for qubits, lines for
  couplers, a gold tube along the worst-case Bell-pair route, a pulse
  travelling the route, and the supporting surface: a grid plane for flat
  chips, a wireframe hyperboloid for the hyperbolic chip. Includes a topology
  selector, a "Compare all" mode at matched scale, auto-rotate toggle, per-chip
  stats (qubits, diameter, SWAPs, noisy fidelity, protected yield) with a
  one-sentence explanation, and an Export PNG button. Data comes from
  `GET /api/topologies`, which returns `positions3d`, `surface`
  (`plane`|`hyperboloid`), `bell_pair`, `route`, `diameter`, `family`
  (`flat`|`hyperbolic`) per topology. Honors `prefers-reduced-motion`.
- **Run** — pick topology / condition / shots, run a live Bell-state routing
  experiment, get metrics plus a one-line plain-English explanation.
