# Methodology

## Research question
Which coupling-graph geometry minimizes the cost of entangling distant
qubits on a quantum cloud processor?

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
- Every number in this repo comes from Qiskit Aer simulation
  (AerSimulator, statevector/stabilizer methods). Nothing was run on a QPU.
  Noise is a simulated depolarizing + readout model, not a real device's
  correlated noise; relative ordering across topologies should hold, but
  absolute fidelities will differ on hardware.
- Post-selection discards data instead of correcting it; it does not scale
  to large computations, but it fairly compares geometries' error burden.
- The hyperbolic patch is a finite `{7,3}` tessellation patch
  (built by Poincare-disk reflections), a proposed/simulated coupling
  topology -- not a fabricated chip.
