# Quantum Geometry Routing

**Track 4 — Geometry-Aware Quantum Cloud Challenge** (IBM Qiskit Fall Fest 2026)

Which road-map should future quantum computers use? We create a Bell state
between distant qubits on three processor topologies — a 2016-style 5-qubit
T, a modern heavy-hex layout, and a genuine hyperbolic `{7,3}` tiling patch —
and compare routing cost (SWAPs, two-qubit depth) and Bell-state fidelity
across 9 experiments (3 topologies × ideal / noisy / protected). A scaling
sweep (20 → 127 qubits) then measures how each geometry's diameter grows.

## What makes this different

**We benchmarked a future chip.** Most teams compare existing layouts; we
added a finite patch of the hyperbolic `{7,3}` tessellation (built by
Poincaré-disk reflections, not hand-drawn) alongside the 2016 T-shape and
today's heavy-hex — and found expansion beats sprawl: at matched ~20 qubits
the `{7,3}` patch routes its worst-case Bell pair in 6 SWAPs where heavy-hex
needs 9, and the gap widens with size (diameter 16 vs 26 at ~130 qubits).

**We priced the protection.** An ancilla measures the Bell pair's ZZ and XX
stabilizers without collapsing it; we keep only clean-syndrome shots. It
helps (heavy-hex fidelity 0.894 → 0.921) but it is honest work, not magic:
it costs +1 SWAP and +4 CX, discards ~12% of shots, and never reaches
perfection. The fidelity-vs-yield-vs-cost trade-off is quantified per
topology, not hand-waved.

## Repo map

| Want to change... | Go here |
|---|---|
| Bell-state circuit | `quantum/circuits/bell_state.py` |
| Star / heavy-hex / hyperbolic topologies | `quantum/topologies/` |
| Routing / transpilation | `quantum/routing/transpiler.py` |
| SWAP & depth metrics | `quantum/routing/swap_analysis.py` |
| Noise models | `quantum/noise/` |
| Fidelity (XX/YY/ZZ) | `quantum/fidelity/` |
| Experiment comparison logic | `algorithms/` |
| Run the 9-case matrix | `scripts/run_all_cases.py` |
| API | `backend/` |
| Dashboard | `frontend/` |
| Concepts (beginner) | `docs/quantum-basics.md` |

## Quickstart

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt          # pinned versions, incl. qiskit 2.5.2

python3 scripts/tiebreaker.py            # Bell state routed on the 5-qubit star
python3 scripts/run_all_cases.py         # the 9-case matrix (~10 s) -> results/
python3 scripts/scaling_sweep.py         # 13 chips, 20->127 qubits (~10 s)
python3 scripts/build_deck.py            # 8-slide deck from results/ -> results/reports/

# API + dashboard (two terminals):
uvicorn backend.main:app --port 8765    # http://localhost:8765/docs
cd frontend && npm install && npm run dev  # http://localhost:5173
```

## Results (9-case matrix, seed 42)

| Topology | Ideal F | Noisy F | Protected F | Yield | SWAPs | +SWAP/+CX (protection) |
|---|---|---|---|---|---|---|
| t-shape (5q, 2016) | 1.0000 | 0.9203 | 0.9340 | 0.913 | 2 | +1 / +4 |
| heavy-hex-21 (IBM-style) | 1.0000 | 0.8938 | 0.9208 | 0.881 | 9 | +1 / +4 |
| hyperbolic-20 (`{7,3}` future) | 1.0000 | 0.9075 | 0.9276 | 0.891 | 6 | +1 / +4 |

Protection = ancilla ZZ/XX stabilizer checks; it helps but never reaches 1.0.
Scaling: at 127 qubits the real Eagle map needs 25 SWAPs (F=0.814); the
`{7,3}` patch needs 15 at 152 qubits (F=0.868). See `docs/recommendation.md`.

## Docs

- `docs/architecture.md` — what every directory does
- `docs/quantum-basics.md` — qubits to fidelity, beginner level
- `docs/methodology.md` — the experimental procedure
- `docs/algorithms.md` — the math behind each algorithm
