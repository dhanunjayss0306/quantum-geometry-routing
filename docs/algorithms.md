# Algorithms

## 1. Bell-state generation
Input: none. Output: 2-qubit circuit H(0); CX(0->1).
Math: H|0> = (|0>+|1>)/sqrt(2); CX entangles -> (|00>+|11>)/sqrt(2).

## 2. Topology construction
Input: size parameters. Output: edge list (undirected).
- Star: hub 0 connected to leaves 1..4.
- Heavy-hex: honeycomb via `networkx.hexagonal_lattice_graph`, then
  subdivide every edge with a new node (this is exactly IBM's heavy-hex).
- Hyperbolic: layered expansion -- each node grows 2 children per layer
  (sizes 1,3,6,12), plus face edges stitching neighboring branches into
  cycles. Exponential growth mimics hyperbolic {7,3} tilings.

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

## 8. Syndrome post-selection
Input: raw counts + expected parity per correlator. Output: kept counts, yield.
Discard shots where XX/ZZ disagree or YY agree (these are certain errors).
Fidelity is recomputed on survivors; yield = kept/total.

## 9. Topology comparison
Input: the 9 result dicts. Output: tables + charts.
Compare routing cost (SWAPs, depth) and fidelity per condition; the
protection trade-off plot shows fidelity gained vs yield lost.
