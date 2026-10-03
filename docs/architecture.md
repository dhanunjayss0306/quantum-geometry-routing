# Architecture

Three layers. Quantum logic never touches the API or the frontend.

```
FRONTEND (React/Vite)          BACKEND (FastAPI)          QUANTUM CORE (Qiskit)
Dashboard, charts,                Experiment API,            Bell circuit,
topology viewer,                  validation,               topologies,
experiment controls  --JSON-->    run controller    -->      routing, noise,
                                                              fidelity
                                        |
                                   algorithms/  (metrics, comparison, 9-case matrix)
                                        |
                                   results/ (JSON, CSV, PNG figures)
```

## Directory responsibilities

- `quantum/`: the science. Circuits, topologies (graphs), routing via
  `transpile()`, noise models, fidelity from correlators. No API code here.
- `algorithms/`: pure-Python analysis: routing metrics, graph metrics,
  fidelity math, topology comparison, the 3x3 experiment matrix.
- `backend/`: FastAPI. Routes call services, services call `quantum/` +
  `algorithms/`. Routes never contain quantum logic.
- `frontend/`: dashboard that calls the backend API and draws charts. The
  **3D** tab (`components/Topology3D.jsx`, three.js) renders each chip's
  coupling graph in rotatable 3D from the API's `positions3d` field; layouts
  themselves live in `quantum/topologies/layout3d.py`, never in the frontend.
- `scripts/`: one-command runners (`tiebreaker.py`, `run_all_cases.py`,
  `render_3d_figure.py` for a static matplotlib 3D PNG).
- `experiments/`: configs in, results out.
- `tests/`: pytest, mirrors the module structure.
- `docs/`: beginner explanations + methodology.

If fidelity looks wrong, look in `quantum/fidelity/`.
If the hyperbolic graph looks wrong, look in `quantum/topologies/hyperbolic.py`.
If the dashboard shows nothing, look in `frontend/` then `backend/api/`.
