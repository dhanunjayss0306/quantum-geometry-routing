"""Tests for fidelity: ideal Bell state must score F = 1."""

from quantum.circuits.bell_state import create_bell_circuit
from quantum.topologies.star import StarTopology
from quantum.routing.transpiler import route_circuit, strip_idle_qubits
from quantum.noise.noisy_simulation import simulate_counts
from quantum.fidelity.correlators import build_correlator_circuits
from quantum.fidelity.fidelity import fidelity_report
from quantum.fidelity.post_selection import protected_fidelity


def _reports(shots=400):
    topo = StarTopology()
    routed = route_circuit(create_bell_circuit(), topo.coupling_map(),
                           initial_layout=[1, 3])
    counts = {}
    for name, circ in build_correlator_circuits(routed).items():
        counts[name] = simulate_counts(strip_idle_qubits(circ), shots=shots)
    return counts


def test_ideal_fidelity_is_one():
    c = _reports()
    rep = fidelity_report(c["XX"], c["YY"], c["ZZ"])
    assert abs(rep["fidelity"] - 1.0) < 0.03
    assert abs(rep["xx"] - 1.0) < 0.05
    assert abs(rep["yy"] + 1.0) < 0.05
    assert abs(rep["zz"] - 1.0) < 0.05


def test_protected_fidelity_ideal_yield_one():
    c = _reports()
    rep = protected_fidelity(c["XX"], c["YY"], c["ZZ"])
    assert abs(rep["fidelity"] - 1.0) < 0.03
    assert abs(rep["yield"] - 1.0) < 0.03  # nothing to discard in ideal world
