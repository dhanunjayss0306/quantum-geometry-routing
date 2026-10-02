"""Tests for routing and SWAP analysis."""

from quantum.circuits.bell_state import create_bell_measurement_circuit
from quantum.topologies.star import StarTopology
from quantum.routing.transpiler import route_circuit, strip_idle_qubits
from quantum.routing.swap_analysis import analyze_routing


def test_distant_leaves_need_swaps():
    topo = StarTopology()
    routed = route_circuit(create_bell_measurement_circuit(),
                           topo.coupling_map(), initial_layout=[1, 3])
    m = analyze_routing(routed)
    assert m["swap_count"] > 0, "leaves 1 and 3 are not adjacent: SWAPs required"
    assert m["depth"] > 0


def test_adjacent_qubits_need_no_swaps():
    topo = StarTopology()
    routed = route_circuit(create_bell_measurement_circuit(),
                           topo.coupling_map(), initial_layout=[0, 1])
    m = analyze_routing(routed)
    assert m["swap_count"] == 0


def test_strip_idle_qubits():
    topo = StarTopology()
    routed = route_circuit(create_bell_measurement_circuit(),
                           topo.coupling_map(), initial_layout=[1, 3])
    slim = strip_idle_qubits(routed)
    assert slim.num_qubits < routed.num_qubits
    assert slim.num_clbits == routed.num_clbits
