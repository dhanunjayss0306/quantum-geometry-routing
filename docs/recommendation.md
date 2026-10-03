# Architectural recommendation: coupling-graph features worth testing next

**Bottom line:** for the workload we tested -- routing a Bell state between
a chip's two farthest qubits -- the coupling graph's diameter scaling is the
strongest predictor of cost. We measured three families from ~20 to 152
qubits. The hyperbolic `{7,3}` patch had the smallest diameter at every
measured size, and the industry-standard heavy-hex had a larger diameter
than even a plain square grid at matched sizes.

## The evidence (from `results/tables/scaling.csv`)

| Family | N=21 | N≈60 | N≈127 | Diameter law (fit) |
|---|---|---|---|---|
| heavy-hex (IBM Eagle-style) | d=10 | d=18 | d=26 | ~2.3·√N |
| square grid (flat reference) | d=7 | d=14 | d=18* | ~1.8·√N |
| hyperbolic `{7,3}` (ours) | d=7 | d=11 | d=16* | sub-√N, near-log |

\* largest measured: grid-100, hyperbolic-152.

Routing a Bell state across the diameter (worst case) needs `diameter − 1`
SWAPs, and noisy fidelity falls with SWAP count:

- heavy-hex-127: 25 SWAPs → fidelity **0.814**
- hyperbolic-152: 15 SWAPs → fidelity **0.868**
- Syndrome protection on heavy-hex-21 (9-case matrix): fidelity 0.894 →
  0.921, at a cost of +1 SWAP, +4 CX, +7 two-qubit depth, and 12% of shots
  discarded (yield 0.881).

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

5. **Budget for error detection, or avoid needing it.** Syndrome protection
   (ancilla ZZ/XX parity checks) recovers ~0.03 fidelity on heavy-hex-21 but
   costs +4 CX, +7 two-qubit depth and 12% yield. A topology that needs 3
   fewer SWAPs buys more fidelity than protection recovers here. Prefer
   reducing the route length over adding checks; reserve ancilla checks for
   the longest routes.

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
