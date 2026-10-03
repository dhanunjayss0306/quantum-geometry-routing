# Design implications from the benchmark

**Summary:** For the tested farthest-pair Bell-routing workload, lower graph
diameter was strongly associated with fewer SWAPs and higher noisy fidelity
under the simulated noise model.

## Observed

Sizes are near-matched; exact qubit counts shown (from
`results/tables/scaling.csv`).

| Family | ~21q | ~62q | ~127q | Diameter growth (empirical fit, 3 points — not a law) |
|---|---|---|---|---|
| heavy-hex (IBM Eagle-style) | 21q: d=10 | 63q: d=18 | 127q: d=26 | ~2.3·√N |
| square grid (flat reference) | 20q: d=7 | 64q: d=14 | 132q: d=21 | ~1.8·√N |
| hyperbolic `{7,3}` (proposed) | 20q: d=7 | 61q: d=11 | 127q: d=15 | slower than √N over the 20-152q range measured; five points from one growth pattern are not enough to establish an asymptotic law |

For the farthest-pair routing procedure used in this benchmark, the measured
SWAP count follows the graph distance closely (about diameter − 1), and
noisy fidelity decreased as SWAP count increased. At near-matched 127
qubits:

- heavy-hex-127: 25 SWAPs → fidelity **0.814**
- hyperbolic-127: 14 SWAPs → fidelity **0.863**
- grid-11x12 (132q): 20 SWAPs → fidelity **0.839**

Syndrome protection on heavy-hex-127 (9-case matrix): fidelity 0.820 →
0.934, at a cost of +5 SWAPs, +4 CX, +9 two-qubit depth, and 20.5% of shots
discarded (yield 0.795).

## Interpretation

1. **Max degree 3 is a feasible target.** Heavy-hex chips operate with
   maximum degree 3, so degree 3 is a feasible target; this benchmark did
   not test whether lower or higher degree changes the result. The grid's
   degree 4 buys little diameter improvement (it still scales as √N) while
   each extra coupler adds crosstalk and frequency-collision risk.

2. **Slower diameter growth than the grid in the tested range.** In the
   tested range, the `{7,3}` family showed slower diameter growth than the
   square grid and heavy-hex; whether growth is logarithmic is not
   established by five points from one growth pattern — the data are
   insufficient to establish an asymptotic scaling law. Heavy-hex's ~2.3·√N
   is worse than a plain grid's ~1.8·√N -- the subdivided honeycomb's
   degree-2 "wire" qubits stretch paths without adding connectivity. Our
   `{7,3}` patch is the only family measured here with lower diameter than
   the grid at near-matched sizes.

3. **No long degree-2 chains (hypothesis).** Every degree-2 qubit is a
   wire: it adds a hop without a routing choice. The heavy-hex graphs
   tested here contain degree-2 wire-like qubits that contribute to longer
   paths, but a controlled experiment is needed to isolate their
   independent effect from face size and other confounders. Hypothesis for
   follow-up: capping degree-2 runs at length 1--2 shortens diameters;
   not yet tested.

4. **Small faces (cycle length ≤ 8): correlation, not cause.** Short cycles
   correlate with shorter diameters in our data (`{7,3}` heptagons, length 7,
   vs heavy-hex dodecagons, length 12; at N≈60, `{7,3}` diameter 11 vs
   heavy-hex 18). But the heavy-hex vs hyperbolic difference is confounded
   with heavy-hex's degree-2 wire qubits, which independently stretch paths.
   This experiment did not isolate face size, so treat it as a hypothesis
   for a controlled follow-up, not a design rule.

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

## Future hypotheses

- **~N/log N long-range shortcut couplers (unmeasured hypothesis).** Our
  data covers planar graphs only. One possible mechanism is that
  diameter is set by the longest shortest path, and a few non-planar
  shortcuts collapse it (small-world effect). Worth simulating next; not
  yet measured.
- A `{7,3}` patch is a planar graph, which keeps it compatible in principle
  with planar fabrication processes -- but this repository does not
  demonstrate fabrication feasibility or device-level implementation, no
  foundry builds heptagonal coupler graphs today, and degree-3 vertices at
  non-standard angles would need process work.

## Caveats

- Noise is simulated depolarizing + readout error, not a real device's
  correlated noise. Whether the same ordering holds on hardware requires
  additional hardware measurements; absolute fidelities will also differ
  with device-specific noise.
- Largest patch measured is 152 qubits. Whether the observed gap persists
  at larger N requires additional measurements.
- Shot counts (1000/sweep point) leave ±0.01--0.02 statistical wobble in
  fidelity; diameter and SWAP counts are exact.
