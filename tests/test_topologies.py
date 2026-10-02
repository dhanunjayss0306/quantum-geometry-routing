"""Tests for the three topologies."""

import networkx as nx

from quantum.topologies.star import StarTopology
from quantum.topologies.heavy_hex import HeavyHexTopology
from quantum.topologies.hyperbolic import HyperbolicTopology


def _check(topology, expected_qubits):
    assert topology.num_qubits() == expected_qubits
    g = topology.graph()
    assert g.number_of_nodes() == expected_qubits
    assert nx.is_connected(g), f"{topology.name} must be one connected chip"
    cm = topology.coupling_map()
    assert len(cm.get_edges()) == 2 * len(topology.edges())  # both directions


def test_star():
    _check(StarTopology(), 5)


def test_heavy_hex():
    _check(HeavyHexTopology(), 35)


def test_hyperbolic():
    _check(HyperbolicTopology(), 22)
    # hyperbolic must expand fast: diameter stays small for its size
    assert nx.diameter(HyperbolicTopology().graph()) <= 7
