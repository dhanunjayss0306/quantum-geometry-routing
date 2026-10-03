# Real-hardware validation: t-shape on ibm_fez

On 2026-10-03 the t-shape 5-qubit Bell-routing case was run on a real QPU
to check whether the Aer noise model used in the benchmark resembles
actual hardware. This is a **validation spot-check**, not a second
benchmark: one topology, one condition (noisy, no protection), one seed.

## Run record

| field | value |
|---|---|
| backend | ibm_fez (156-qubit IBM Heron r2) |
| job ID | db0e7hal7guc73cgblgg |
| submitted (UTC) | 2026-10-03 11:15:15 |
| completed (UTC) | 2026-10-03 11:16:17 |
| status | DONE |
| shots per circuit | 2000 (XX, YY, ZZ) |
| topology | t-shape 5q, Bell pair on farthest qubits (0, 4), graph distance 3 |
| physical qubits | virtual 0..4 → physical [16, 3, 2, 4, 5], a T-shaped subset of the Heron lattice |
| transpiled depth | 13 (two-qubit depth 4, 7 CZ gates) per correlator circuit |
| plan | IBM Quantum Open (free tier) |

Raw counts and metadata: `results/qpu/tshape_real_backend.json`.

## Result

Measured correlators: XX = 0.921, YY = −0.866, ZZ = 0.897, giving
Bell-state fidelity **F = 0.921 ± 0.004** (1 sigma, from correlator
shot noise).

Standard error: each correlator's shot-noise standard error is
se(c) = sqrt((1 − c²) / 2000), giving se(XX) = 0.0087, se(YY) = 0.0112,
se(ZZ) = 0.0099. Since F = (1 + XX − YY + ZZ) / 4, the errors combine
in quadrature: se(F) = 0.25 × sqrt(se(XX)² + se(YY)² + se(ZZ)²) = 0.0043.

The matching Aer simulation (t-shape, noisy, seed 42, 2000 shots) gives
F = 0.9203. Hardware F = 0.921 ± 0.004 vs simulated 0.9203: consistent
within shot noise for this one case. This is a spot-check; it does not
show the noise model fits other chips, topologies, or conditions.

## Limitations

- Single run, single backend, single qubit placement; not a statistical sample.
- Only the t-shape case was run on hardware. The heavy-hex-127 and
  hyperbolic-20/127 comparisons remain simulation-only.
- The hardware circuit differs from the simulated one: 7 CZ gates at
  two-qubit depth 4 on hand-picked T-shaped physical qubits [16, 3, 2, 4, 5],
  vs the simulator's abstract t-shape routing. Agreement here does not imply
  the same noise model accuracy for other routings.
- No error mitigation was applied on hardware.
- Hardware results drift with calibration; a rerun on another day or another
  Heron chip will differ.
- The API tokens used for this run were revoked afterwards.
