"""Tiebreaker test: route a Bell state across the 5-qubit star.

Question: can we build a Bell state between two distant qubits
(leaves 1 and 3 of the 5-qubit star) and route it through the hub?

Expected: the transpiler inserts SWAPs (the detour), the ideal
simulation still gives a near-perfect Bell state (~50% '00', ~50% '11'),
so our quick fidelity estimate P(00)+P(11) is ~1.0.

Run from the repo root:
    python3 scripts/tiebreaker.py
"""

import os
import sys

# Make repo-root imports work no matter where you run from.
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)

from qiskit_aer import AerSimulator

from quantum.circuits.bell_state import create_bell_measurement_circuit
from quantum.topologies.star import StarTopology
from quantum.routing.transpiler import route_circuit
from quantum.routing.swap_analysis import analyze_routing

SHOTS = 2000
SEED = 42


def main() -> None:
    print("=" * 60)
    print("TIEBREAKER: Bell state between leaves 1 and 3 of the star")
    print("=" * 60)

    # 1. Logical Bell circuit (2 qubits).
    bell = create_bell_measurement_circuit()
    print("\nLogical circuit:")
    print(bell.draw(output="text"))

    # 2. Route it: logical 0 -> physical 1, logical 1 -> physical 3.
    #    Leaves 1 and 3 are NOT directly connected (path 1-0-3),
    #    so the transpiler must insert SWAPs.
    topo = StarTopology()
    routed = route_circuit(
        bell, topo.coupling_map(), initial_layout=[1, 3], seed=SEED
    )
    print("\nRouted circuit on the star:")
    print(routed.draw(output="text", fold=-1))

    # 3. Measure the routing cost.
    metrics = analyze_routing(routed)
    print("\nRouting cost:")
    print(f"  SWAPs inserted : {metrics['swap_count']}")
    print(f"  CX gates       : {metrics['cx_count']}")
    print(f"  Circuit depth  : {metrics['depth']}")

    # 4. Ideal simulation: does the Bell state survive the trip?
    sim = AerSimulator(seed_simulator=SEED)
    counts = sim.run(routed, shots=SHOTS).result().get_counts()
    print(f"\nIdeal simulation counts ({SHOTS} shots):")
    for bitstring, n in sorted(counts.items()):
        print(f"  {bitstring}: {n}")

    bell_fraction = (counts.get("00", 0) + counts.get("11", 0)) / SHOTS
    print(f"\nQuick fidelity estimate P(00)+P(11) = {bell_fraction:.4f}")

    # 5. Verdict.
    ok = metrics["swap_count"] > 0 and bell_fraction > 0.95
    print("\n" + ("PASS" if ok else "FAIL"),
          "- SWAPs were needed AND the ideal Bell state survived."
          if ok else "- something is wrong, investigate!")
    print("=" * 60)


if __name__ == "__main__":
    main()
