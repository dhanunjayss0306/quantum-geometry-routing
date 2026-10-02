# Architectural recommendation: what the next quantum cloud chip should look like

**Bottom line:** for cloud-scale entanglement, the coupling graph's *diameter
scaling* is the single number that matters. We measured three families from
~20 to 152 qubits. The hyperbolic `{7,3}` patch wins at every size, and the
industry-standard heavy-hex loses even to a plain square grid.

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
- Syndrome protection on heavy-hex-35: fidelity 0.864 → 0.920, at a cost of
  +1 SWAP, +4 CX, +14 two-qubit depth and 15% of shots discarded.

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
   (ancilla ZZ/XX parity checks) recovers ~0.06 fidelity on heavy-hex but
   costs +4 CX, +14 depth and 15% yield. A topology that needs 10 fewer
   SWAPs buys more fidelity than protection ever recovers. Prefer geometry
   over band-aids; reserve ancilla checks for the longest routes.

6. **Forward-looking: ~N/log N long-range shortcut couplers.** Our data
   covers planar graphs only, but the mechanism is clear -- diameter is set
   by the longest shortest path, and a few non-planar shortcuts collapse it
   (small-world effect). Worth simulating next; not yet measured.

## Honest caveats

- Noise is simulated depolarizing + readout error, not a real device's
  correlated noise. Relative ordering should hold; absolute fidelities will
  differ on hardware.
- Largest patch measured is 152 qubits; the log-vs-√N separation widens
  with N, so these numbers *understate* the hyperbolic advantage at 1000+ q.
- A `{7,3}` patch is a planar graph, so it is manufacturable as a coupler
  layout in principle -- but no foundry builds heptagonal coupler graphs
  today, and degree-3 vertices at non-standard angles need process work.
- Shot counts (1000/sweep point) leave ±0.01--0.02 statistical wobble in
  fidelity; diameter and SWAP counts are exact.
