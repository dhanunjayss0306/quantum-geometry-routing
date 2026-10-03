# Architectural recommendation: coupling-graph features worth testing next

**Bottom line:** for the workload we tested -- routing a Bell state between
a chip's two farthest qubits -- the coupling graph's diameter scaling is the
strongest predictor of cost. We measured three families from ~20 to 152
qubits. The hyperbolic `{7,3}` patch had the smallest diameter at every
measured size, and the industry-standard heavy-hex had a larger diameter
than even a plain square grid at near-matched sizes.

## The evidence (from `results/tables/scaling.csv`)

Sizes are near-matched; exact qubit counts shown.

| Family | ~21q | ~62q | ~127q | Diameter law (fit) |
|---|---|---|---|---|
| heavy-hex (IBM Eagle-style) | 21q: d=10 | 63q: d=18 | 127q: d=26 | ~2.3·√N |
| square grid (flat reference) | 20q: d=7 | 64q: d=14 | 132q: d=21 | ~1.8·√N |
| hyperbolic `{7,3}` (proposed) | 20q: d=7 | 61q: d=11 | 127q: d=15 | sub-√N, near-log |

Routing a Bell state across the diameter (worst case) needs `diameter − 1`
SWAPs, and noisy fidelity falls with SWAP count. At near-matched 127
qubits:

- heavy-hex-127: 25 SWAPs → fidelity **0.814**
- hyperbolic-127: 14 SWAPs → fidelity **0.863**
- grid-11x12 (132q): 20 SWAPs → fidelity **0.839**

Syndrome protection on heavy-hex-127 (9-case matrix): fidelity 0.820 →
0.934, at a cost of +5 SWAPs, +4 CX, +9 two-qubit depth, and 20.5% of shots
discarded (yield 0.795).

## Recommended coupling-graph features

1. **Max degree 3.** Heavy-hex proves degree 3 suffices for a working chip;
   the grid's degree 4 buys little (it still scales as √N) while each extra
   coupler adds crosstalk and frequency-collision risk. Target exactly 3.

2. **Diameter scaling strictly better than √N; target logarithmic.**
   Heavy-hex's ~2.3·√N is *worse* than a plain grid's ~1.8·√N -- the
   subdivided honeycomb's degree-2 "wire" qubits stretch paths without
   adding connectivity. Any future layout should beat the grid, not just
   match it. Our `{7,3}` patch is the only family measured here that does.

3. **No long degree-2 chains.** Every degree-2 qubit is a wire: it adds a hop
   without a routing choice. Heavy-hex is full of them (the "heavy" edge
   qubits); they are the main reason its diameter constant (2.3) exceeds the
   grid's (1.8). Cap degree-2 runs at length 1--2.

4. **Small faces (cycle length ≤ 8).** Short cycles are local shortcuts:
   `{7,3}` heptagons (length 7) vs heavy-hex dodecagons (length 12).
   Measured: at N≈60, `{7,3}` diameter 11 vs heavy-hex 18.

5. **Budget for error detection; its value grows with route length.**
   Syndrome protection (ancilla ZZ/XX parity checks) recovers 0.014 fidelity
   on t-shape and 0.020 on hyperbolic-20 -- modest, because short routes
   accumulate little error. On Eagle-127 (25-SWAP route) it recovers 0.113
   (0.820 → 0.934), the largest gain measured, because there is far more
   error to detect. The price also grows with chip size: +1 SWAP / +4 CX /
   +4-5 two-qubit depth on the small chips vs +5 SWAPs / +4 CX / +9
   two-qubit depth on Eagle-127, discarding 9-21% of shots. The overhead
   varies because the ancilla is placed at the qubit minimizing total
   distance to the Bell endpoints (`_best_ancilla_spot`); on bigger chips
   that qubit is farther from the endpoints, so reaching it costs more
   SWAPs. Shorter routes still help more per unit cost -- but on long
   routes, detection is worth budgeting for.

6. **Forward-looking: ~N/log N long-range shortcut couplers.** Our data
   covers planar graphs only, but the mechanism is clear -- diameter is set
   by the longest shortest path, and a few non-planar shortcuts collapse it
   (small-world effect). Worth simulating next; not yet measured.

## Caveats

- Noise is simulated depolarizing + readout error, not a real device's
  correlated noise. Relative ordering should hold; absolute fidelities will
  differ on hardware.
- Largest patch measured is 152 qubits; the measured trends suggest the
  gap would widen at larger N, but that is extrapolation, not measurement.
- A `{7,3}` patch is a planar graph, so it is manufacturable as a coupler
  layout in principle -- but no foundry builds heptagonal coupler graphs
  today, and degree-3 vertices at non-standard angles need process work.
- Shot counts (1000/sweep point) leave ±0.01--0.02 statistical wobble in
  fidelity; diameter and SWAP counts are exact.
