# Methodology

## Research question
Which coupling-graph geometry minimizes the cost of entangling distant
qubits on a quantum cloud processor?

## Provenance
The 127-qubit IBM Eagle-style coupling map is a static edge list extracted
once from the Qiskit FakeSherbrooke fake backend and stored as
`quantum/topologies/eagle127_edges.json`. No real Eagle QPU was used; the
map is a static stand-in for Eagle-style connectivity.

The benchmark results are primarily Qiskit Aer simulations (see Procedure).
Separately, one t-shape validation case was run on real IBM hardware
(`ibm_fez`, 156-qubit Heron r2; full record in `docs/real_hardware.md`).
That hardware run is a spot-check of the simulated noise model for one
small case — it is not used to claim validation of the 127-qubit or
hyperbolic benchmark results.

Simulated noise is an idealized depolarizing (p1=0.001, p2=0.01) +
readout (0.02) model, not a real device's correlated noise. The hardware
spot-check does not show the model universally reproduces IBM hardware.

## Procedure (per case)
1. **Generate** the Bell state |Phi+> on 2 logical qubits (H + CNOT).
2. **Choose** the topology's two farthest-apart physical qubits
   (worst-case trip; found via all-pairs shortest paths).
3. **Route** with Qiskit `transpile()` onto the coupling map
   (`initial_layout` pins the endpoints; seed fixed for reproducibility).
4. **Measure routing cost**: SWAP count, CX count, circuit depth.
5. **Simulate** the XX, YY, ZZ correlator circuits on AerSimulator:
   - ideal: no noise model
   - noisy: depolarizing (p1=0.001, p2=0.01) + readout (0.02) errors
   - protected: noisy + ancilla syndrome checks (one ancilla measures the
     ZZ then XX stabilizers via mid-circuit measurement; keep only shots
     with a clean syndrome; correlators computed from data bits only)
6. **Compute** fidelity F = (1 + <XX> - <YY> + <ZZ>)/4 and survival yield.
7. **Record** everything (config, seed, versions implied by
   requirements.txt) as JSON; aggregate to CSV; plot.

## Why this design
- Farthest-pair routing measures the *worst* detour each geometry forces.
- Fixed seeds + saved configs make every number reproducible.
- Idle-qubit stripping keeps simulation exact (2^8 instead of 2^35
  amplitudes) without changing any measurement result.
- Post-selection is error *detection*, not correction: we report both the
  fidelity gained and the shots discarded (the trade-off plot).

## Limitations
- The benchmark numbers come from Qiskit Aer simulation
  (AerSimulator, statevector/stabilizer methods), except the single
  t-shape hardware spot-check on `ibm_fez` (`docs/real_hardware.md`).
  Simulated noise is a depolarizing + readout model, not a real device's
  correlated noise. Whether the same ordering holds on hardware requires
  additional measurements; absolute fidelities will also differ.
- Post-selection discards data instead of correcting it; it does not scale
  to large computations, but it fairly compares geometries' error burden.
- Timing: the syndrome ancilla is measured once, after routing completes.
  It detects the net error accumulated along the whole route, not errors
  at each hop. Future work: mid-route syndrome checks that catch errors
  closer to where they occur.
- The hyperbolic patch is a finite `{7,3}` tessellation patch
  (built by Poincare-disk reflections), a proposed/simulated coupling
  topology -- not a fabricated chip.
