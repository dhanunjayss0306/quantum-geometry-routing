"""Tests for the scaling sweep: stabilizer == statevector on Clifford noise."""

from quantum.circuits.bell_state import create_bell_circuit
from quantum.topologies.heavy_hex import HeavyHexPatch
from quantum.topologies.hyperbolic import HyperbolicTiling
from quantum.topologies.grid import GridTopology
from quantum.routing.transpiler import route_circuit, strip_idle_qubits
from quantum.noise.noise_models import build_depolarizing_noise_model
from quantum.noise.noisy_simulation import simulate_counts
from quantum.fidelity.correlators import build_correlator_circuits
from quantum.fidelity.fidelity import bell_state_fidelity
from algorithms.scaling import scaling_point


def _fidelity(method, topology, shots=1500):
    routed = route_circuit(create_bell_circuit(), topology.coupling_map(),
                           initial_layout=[0, 5], seed=42)
    nm = build_depolarizing_noise_model()
    counts = {}
    for name, circ in build_correlator_circuits(routed).items():
        counts[name] = simulate_counts(strip_idle_qubits(circ),
                                       noise_model=nm, shots=shots,
                                       seed=42, method=method)
    return bell_state_fidelity(counts["XX"], counts["YY"], counts["ZZ"])


def test_stabilizer_matches_statevector():
    """Justifies using stabilizer for the 127-qubit sweep points."""
    topo = HeavyHexPatch(1, 2)
    f_sv = _fidelity("statevector", topo)
    f_st = _fidelity("stabilizer", topo)
    assert abs(f_sv - f_st) < 0.02


def test_scaling_point_small():
    pt = scaling_point(HeavyHexPatch(1, 2), shots=200, seed=42)
    assert pt["num_qubits"] == 21
    assert pt["diameter"] == 10
    assert pt["swap_count"] == 9
    assert 0.7 < pt["fidelity_noisy"] < 1.0
    assert pt["method"] == "stabilizer"


def test_grid_topology():
    t = GridTopology(4, 5)
    assert t.num_qubits() == 20
    assert t.name == "grid-4x5"
    import networkx as nx
    assert nx.diameter(t.graph()) == 7  # (4-1) + (5-1)
