"""Scaling sweep: how does routing cost grow with chip size, per family?

For each topology family (heavy-hex, hyperbolic {7,3}, square grid) we build
several sizes (~20 to 127 qubits) and route a Bell state across each chip's
diameter, recording graph metrics and noisy fidelity.

Simulation method: 'stabilizer'. Our circuits are Clifford (H, CX, SWAP,
measure) and our noise is Pauli (depolarizing) -- the extended stabilizer
simulator handles this exactly and scales to 127+ qubits, where statevector
would need 2^127 amplitudes. Validated to match statevector fidelity on
small cases (see tests/test_scaling.py).
"""

import networkx as nx

from quantum.circuits.bell_state import create_bell_circuit
from quantum.routing.transpiler import route_circuit, strip_idle_qubits
from quantum.routing.swap_analysis import analyze_routing
from quantum.noise.noise_models import build_depolarizing_noise_model
from quantum.noise.noisy_simulation import simulate_counts
from quantum.fidelity.correlators import build_correlator_circuits
from quantum.fidelity.fidelity import fidelity_report
from algorithms.experiment_matrix import farthest_pair


def scaling_point(topology, shots: int = 1000, seed: int = 42,
                  method: str = "stabilizer") -> dict:
    """One size point: graph metrics + routed Bell metrics + noisy fidelity."""
    g = topology.graph()
    a, b, graph_dist = farthest_pair(topology)
    routed = route_circuit(create_bell_circuit(), topology.coupling_map(),
                           initial_layout=[a, b], seed=seed)
    routing = analyze_routing(strip_idle_qubits(routed))

    nm = build_depolarizing_noise_model()
    counts = {}
    for name, circ in build_correlator_circuits(routed).items():
        slim = strip_idle_qubits(circ)
        counts[name] = simulate_counts(slim, noise_model=nm, shots=shots,
                                       seed=seed, method=method)
    rep = fidelity_report(counts["XX"], counts["YY"], counts["ZZ"])

    return {
        "family": topology.name.rsplit("-", 1)[0],
        "topology": topology.name,
        "num_qubits": topology.num_qubits(),
        "diameter": nx.diameter(g),
        "avg_shortest_path": round(nx.average_shortest_path_length(g), 3),
        "max_degree": max(dict(g.degree()).values()),
        "graph_distance": graph_dist,
        "swap_count": routing["swap_count"],
        "cx_count": routing["cx_count"],
        "depth": routing["depth"],
        "depth_2q": routing["depth_2q"],
        "fidelity_noisy": round(rep["fidelity"], 4),
        "shots": shots,
        "seed": seed,
        "method": method,
    }


def run_scaling(families: dict, shots: int = 1000, seed: int = 42) -> list:
    """Run the sweep. families: {family_name: [topologies]}."""
    results = []
    for family, topologies in families.items():
        for topo in topologies:
            print(f"  scaling {topo.name:18s} ...", flush=True)
            results.append(scaling_point(topo, shots=shots, seed=seed))
    return results
