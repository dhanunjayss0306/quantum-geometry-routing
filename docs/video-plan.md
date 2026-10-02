# Demo video plan (2-4 minutes)

Screen-record with voiceover. Keep the terminal + dashboard visible; nobody
reads a talking head in a code demo.

## Shot list

| Time | Screen | Say (gist) |
|---|---|---|
| 0:00-0:25 | Slide 1-2 of deck | "Future quantum clouds have 100s of qubits, but each talks to few neighbors. Entangling distant qubits costs SWAP detours. We ask: which chip road-map pays the smallest tax?" |
| 0:25-1:10 | Terminal: `python scripts/run_all_cases.py` | "Our engine routes a Bell state between each chip's two farthest qubits, under 3 conditions. Watch: 9 cases in ~8 seconds." Point at SWAP counts as they print. |
| 1:10-2:00 | `results/figures/fidelity.png` + `routing_cost.png` | "Ideal world: all perfect. Noisy world: heavy-hex drops to 0.86 -- 13 SWAPs of exposure. Protection restores 1.0, but heavy-hex discards 9% of shots. The trade is the finding." |
| 2:00-2:50 | Dashboard: Topologies tab, then Run tab | Show the BFS-ring graphs ("the drawing shows how spread out each chip is"), then run a live hyperbolic+noisy experiment and read the one-line explanation. |
| 2:50-3:10 | Slide 7-8 | "Star wins at lab scale but can't scale. Hyperbolic packs 22 qubits at diameter 6. For cloud-scale entanglement, expansion beats sprawl." + repo link. |

## Tips
- Run `run_all_cases.py` once before recording (warm caches, no pip surprises).
- Zoom terminal to 150%+; judges watch on phones.
- The one-line explanation on the Run tab is your Q&A cheat sheet -- read it verbatim if asked "what does this number mean".
