# Algorithms

## 1. Bell-state generation
Input: none. Output: 2-qubit circuit H(0); CX(0->1).
Math: H|0> = (|0>+|1>)/sqrt(2); CX entangles -> (|00>+|11>)/sqrt(2).

## 2. Topology construction
Input: size parameters. Output: edge list (undirected).
- T-shape: 5-qubit reference (edges (0,1),(1,2),(1,3),(3,4)).
- Heavy-hex: honeycomb via `networkx.hexagonal_lattice_graph`, then
  subdivide every edge with a new node (this is exactly IBM's heavy-hex).
  `Eagle127Topology` instead loads the real 127-qubit Eagle coupling map
  from a static edge list (extracted once from FakeSherbrooke).
- Hyperbolic: a finite patch of the `{7,3}` tessellation, built by
  reflecting the fundamental heptagon across its geodesic edges in the
  Poincare disk. Every interior vertex has degree 3, every face is a
  7-cycle. A proposed/simulated coupling topology, not hardware.

## 3. Quantum routing (transpilation)
Input: logical circuit + coupling map. Output: physical circuit.
Qiskit's `transpile()` solves layout (virtual->physical mapping) and
routing (SWAP insertion along shortest paths). We keep `swap` in the basis
gates so the cost stays countable.

## 4. SWAP / depth analysis
Input: transpiled circuit. Output: {swap_count, cx_count, depth}.
`count_ops()['swap']` counts detours; `depth()` counts sequential
time-steps (= noise exposure time).

## 5. Idle-qubit stripping
Input: N-qubit routed circuit. Output: equivalent circuit on used qubits only.
Collect qubits touched by any non-barrier op; rebuild the circuit remapped
to 0..k-1. Exact: untouched qubits are always |0> and unmeasured.

## 6. Noise simulation
Input: circuit + depolarizing model (p1, p2, readout). Output: counts.
Each gate applies a random Pauli error with probability p; measurements
flip with probability `readout`. Monte-Carlo over `shots` repetitions.

## 7. Fidelity from correlators
Input: counts from XX, YY, ZZ circuits. Output: F in [0,1].
<PP> = (N_agree - N_disagree)/N. Then F = (1 + <XX> - <YY> + <ZZ>)/4.
The YY sign is negative because |Phi+> anti-correlates in the Y basis.

## 8. Syndrome post-selection (ancilla-based)
Input: counts from protected XX/YY/ZZ circuits (4-bit outcomes:
syn_xx syn_zz d1 d0). Output: fidelity from data bits, yield.
After routing, one ancilla measures the Bell stabilizers ZZ then XX via
mid-circuit measurement (phase kickback for XX); the transpiler places the
ancilla and routes the extra CNOTs. Keep shots with syndrome 00; compute
<XX>,<YY>,<ZZ> from the DATA bits only. Selection and scoring use disjoint
bits, so random inputs cannot fake F=1. Yield = kept/total; the added
SWAP/CX/depth vs the unprotected circuit is reported as protection overhead.

## 9. Topology comparison
Input: the 9 result dicts. Output: tables + charts.
Compare routing cost (SWAPs, depth) and fidelity per condition; the
protection trade-off plot shows fidelity gained vs yield lost.
