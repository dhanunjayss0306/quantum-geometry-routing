"""Verify the fidelity pipeline: ideal must give F=1.0, noise must degrade it.

Run from the repo root:
    python3 scripts/check_fidelity.py
"""

import os
import sys

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)

from quantum.circuits.bell_state import create_bell_circuit
from quantum.topologies.star import StarTopology
from quantum.routing.transpiler import route_circuit, strip_idle_qubits
from quantum.noise.noise_models import build_depolarizing_noise_model
from quantum.noise.noisy_simulation import simulate_counts
from quantum.fidelity.correlators import build_correlator_circuits
from quantum.fidelity.fidelity import fidelity_report

SHOTS = 4000
SEED = 42


def run_case(label, noise_model):
    topo = StarTopology()
    routed = route_circuit(create_bell_circuit(), topo.coupling_map(),
                           initial_layout=[1, 3], seed=SEED)
    report = {}
    for name, circ in build_correlator_circuits(routed).items():
        slim = strip_idle_qubits(circ)
        counts = simulate_counts(slim, noise_model=noise_model,
                                 shots=SHOTS, seed=SEED)
        report[name] = counts
    rep = fidelity_report(report["XX"], report["YY"], report["ZZ"])
    print(f"{label}: <XX>={rep['xx']:+.4f} <YY>={rep['yy']:+.4f} "
          f"<ZZ>={rep['zz']:+.4f} -> F={rep['fidelity']:.4f}")
    return rep


def main():
    print("Bell state, star topology, leaves 1<->3")
    ideal = run_case("ideal", None)
    noisy = run_case("noisy", build_depolarizing_noise_model())
    ok = abs(ideal["fidelity"] - 1.0) < 0.02 and noisy["fidelity"] < ideal["fidelity"]
    print("PASS - ideal ~1.0 and noise degrades fidelity" if ok
          else "FAIL - check the correlator math!")


if __name__ == "__main__":
    main()
