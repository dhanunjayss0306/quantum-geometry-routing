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
- **Run** — pick topology / condition / shots, run a live Bell-state routing
  experiment, get metrics plus a one-line plain-English explanation.
