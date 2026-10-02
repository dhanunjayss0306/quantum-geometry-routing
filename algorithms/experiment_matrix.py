"""The 9-case experiment matrix: the scientific core of the project.

    3 topologies (star, heavy-hex, hyperbolic)
  x 3 conditions (ideal, noisy, noisy+protected)
  = 9 experiments.

Each case: route a Bell state between the topology's two farthest-apart
qubits (worst-case trip), then report routing cost (SWAPs, CX, depth)
and Bell-state fidelity. The 'protected' condition adds syndrome
post-selection on top of noise.

Every case returns a plain dict -- JSON-serializable, no magic.
"""

import networkx as nx

from quantum.circuits.bell_state import create_bell_circuit
from quantum.routing.transpiler import route_circuit, strip_idle_qubits
from quantum.routing.swap_analysis import analyze_routing
from quantum.noise.noise_models import (
    build_depolarizing_noise_model,
    ONE_QUBIT_GATE_ERROR,
    TWO_QUBIT_GATE_ERROR,
    READOUT_ERROR,
)
from quantum.noise.noisy_simulation import simulate_counts
from quantum.fidelity.correlators import build_correlator_circuits
from quantum.fidelity.fidelity import fidelity_report
from quantum.fidelity.post_selection import (
    create_protected_bell_circuit,
    route_protected_circuit,
    build_protected_correlator_circuits,
    protected_fidelity,
)

CONDITIONS = ["ideal", "noisy", "protected"]


def farthest_pair(topology):
    """Two qubits with the longest shortest-path between them (worst-case trip)."""
    g = topology.graph()
    lengths = dict(nx.shortest_path_length(g))
    nodes = list(g.nodes())
    a, b = max(
        ((u, v) for i, u in enumerate(nodes) for v in nodes[i + 1:]),
        key=lambda p: lengths[p[0]][p[1]],
    )
    return a, b, lengths[a][b]


def run_case(topology, condition: str, shots: int = 2000, seed: int = 42) -> dict:
    """Run one of the 9 cases.

    Args:
        topology: a TopologyBase instance.
        condition: 'ideal', 'noisy', or 'protected'.
        shots: simulator shots per correlator circuit.
        seed: fixed seed for reproducibility.

    Returns:
        dict with topology, condition, routing metrics, fidelity, yield,
        and full provenance (noise params, seed, qubit pair).
    """
    assert condition in CONDITIONS, f"unknown condition: {condition}"
    a, b, graph_dist = farthest_pair(topology)

    routed = route_circuit(
        create_bell_circuit(), topology.coupling_map(),
        initial_layout=[a, b], seed=seed,
    )
    routing = analyze_routing(strip_idle_qubits(routed))

    noise_model = None if condition == "ideal" else build_depolarizing_noise_model()
    # Protection overhead, reported for the 'protected' condition only.
    added = {"swap_count": 0, "cx_count": 0, "depth": 0, "depth_2q": 0}

    if condition == "protected":
        # Route the full 3-qubit protected circuit (Bell + syndrome ancilla);
        # the transpiler places the ancilla and inserts the extra SWAPs.
        routed_prot = route_protected_circuit(
            create_protected_bell_circuit(), topology.coupling_map(),
            initial_layout=[a, b], seed=seed,
        )
        routing_prot = analyze_routing(strip_idle_qubits(routed_prot))
        for k in added:
            added[k] = routing_prot[k] - routing[k]
        routing = routing_prot  # protected case reports its true (higher) cost

        raw = {}
        for name, circ in build_protected_correlator_circuits(routed_prot).items():
            slim = strip_idle_qubits(circ)
            raw[name] = simulate_counts(slim, noise_model=noise_model,
                                        shots=shots, seed=seed)
        rep = protected_fidelity(raw["XX"], raw["YY"], raw["ZZ"])
        fidelity, yld = rep["fidelity"], rep["yield"]
        xx, yy, zz = rep["xx"], rep["yy"], rep["zz"]
    else:
        raw = {}
        for name, circ in build_correlator_circuits(routed).items():
            slim = strip_idle_qubits(circ)
            raw[name] = simulate_counts(slim, noise_model=noise_model,
                                        shots=shots, seed=seed)
        rep = fidelity_report(raw["XX"], raw["YY"], raw["ZZ"])
        fidelity, yld = rep["fidelity"], 1.0
        xx, yy, zz = rep["xx"], rep["yy"], rep["zz"]

    return {
        "topology": topology.name,
        "condition": condition,
        "num_qubits": topology.num_qubits(),
        "bell_pair": [a, b],
        "graph_distance": graph_dist,
        "swap_count": routing["swap_count"],
        "cx_count": routing["cx_count"],
        "depth": routing["depth"],
        "depth_2q": routing["depth_2q"],
        "added_swap_count": added["swap_count"],
        "added_cx_count": added["cx_count"],
        "added_depth": added["depth"],
        "added_depth_2q": added["depth_2q"],
        "xx": round(xx, 4),
        "yy": round(yy, 4),
        "zz": round(zz, 4),
        "fidelity": round(fidelity, 4),
        "yield": round(yld, 4),
        "shots": shots,
        "seed": seed,
        "noise": {"p1": ONE_QUBIT_GATE_ERROR, "p2": TWO_QUBIT_GATE_ERROR,
                  "readout": READOUT_ERROR} if noise_model else None,
    }


def run_matrix(topologies, shots: int = 2000, seed: int = 42) -> list:
    """Run all 9 cases. Returns a list of result dicts."""
    results = []
    for topology in topologies:
        for condition in CONDITIONS:
            print(f"  running {topology.name:12s} {condition:9s} ...", flush=True)
            results.append(run_case(topology, condition, shots=shots, seed=seed))
    return results
