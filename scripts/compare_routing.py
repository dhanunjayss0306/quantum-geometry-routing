"""Compare the headline topologies head-to-head (routing only, ideal simulation).

For each topology:
  * report graph stats (qubits, diameter = longest shortest path),
  * route a Bell state between the two farthest-apart qubits,
  * count SWAPs / CX / depth,
  * ideal-simulate and check the Bell state survived.

This is the routing half of the 9-case matrix. Noise + fidelity come next.

Run from the repo root:
    python3 scripts/compare_routing.py
"""

import os
import sys

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)

from qiskit_aer import AerSimulator

from quantum.circuits.bell_state import create_bell_measurement_circuit
from quantum.topologies.tshape import TShapeTopology
from quantum.topologies.heavy_hex import HeavyHexPatch
from quantum.topologies.hyperbolic import HyperbolicTiling
from quantum.routing.transpiler import route_circuit, strip_idle_qubits
from quantum.routing.swap_analysis import analyze_routing
from algorithms.experiment_matrix import farthest_pair

SHOTS = 2000
SEED = 42


def main() -> None:
    sim = AerSimulator(seed_simulator=SEED)
    print(f"{'topology':<16}{'qubits':<8}{'diameter':<10}"
          f"{'Bell pair':<12}{'SWAPs':<7}{'CX':<5}{'depth':<7}{'fidelity~':<10}")
    print("-" * 75)
    for topology in [TShapeTopology(), HeavyHexPatch(1, 2),
                     HyperbolicTiling(17)]:
        a, b, dist = farthest_pair(topology)

        bell = create_bell_measurement_circuit()
        routed = route_circuit(bell, topology.coupling_map(),
                               initial_layout=[a, b], seed=SEED)
        slim = strip_idle_qubits(routed)
        m = analyze_routing(slim)

        counts = sim.run(slim, shots=SHOTS).result().get_counts()
        fid = (counts.get("00", 0) + counts.get("11", 0)) / SHOTS

        print(f"{topology.name:<16}{topology.num_qubits():<8}{dist:<10}"
              f"{f'{a}<->{b}':<12}{m['swap_count']:<7}{m['cx_count']:<5}"
              f"{m['depth']:<7}{fid:<10.4f}")
    print("-" * 75)
    print("diameter = longest shortest path (graph hops). Bell pair routed across it.")


if __name__ == "__main__":
    main()
