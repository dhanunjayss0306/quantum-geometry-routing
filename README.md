# Quantum Geometry Routing

**Track 4 — Geometry-Aware Quantum Cloud Challenge** (IBM Qiskit Fall Fest 2026)

Which road-map should future quantum computers use? We create a Bell state
between distant qubits on three processor topologies — a 2016-style 5-qubit
star, a modern heavy-hex layout, and a proposed hyperbolic layout — and compare
routing cost (SWAPs, depth) and Bell-state fidelity across 9 experiments
(3 topologies × ideal / noisy / protected).

## What makes this different

**We benchmarked a future chip.** Most teams compare existing layouts; we added
a hyperbolic-inspired topology (22 qubits, graph diameter 6) alongside the
2016 star and today's heavy-hex (35 qubits, diameter 14) — and found
exponential expansion beats sprawl: the hyperbolic patch routes its worst-case
Bell pair in 5 SWAPs where heavy-hex needs 13.

**We priced the protection.** Syndrome post-selection restores fidelity to 1.0
everywhere, but we show it is not free: heavy-hex must discard ~9% of shots to
get there, the star only ~5%. The fidelity-vs-yield trade-off is quantified per
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
pip install -r requirements.txt
python3 scripts/tiebreaker.py   # Bell state routed on the 5-qubit star
```

## Docs

- `docs/architecture.md` — what every directory does
- `docs/quantum-basics.md` — qubits to fidelity, beginner level
- `docs/methodology.md` — the experimental procedure
- `docs/algorithms.md` — the math behind each algorithm
