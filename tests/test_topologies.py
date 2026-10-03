"""Tests for the topologies, including tessellation invariants."""

import networkx as nx
from collections import Counter

from quantum.topologies.star import StarTopology
from quantum.topologies.tshape import TShapeTopology
from quantum.topologies.heavy_hex import HeavyHexPatch, Eagle127Topology
from quantum.topologies.hyperbolic import HyperbolicTiling


def _check(topology, expected_qubits):
    assert topology.num_qubits() == expected_qubits
    g = topology.graph()
    assert g.number_of_nodes() == expected_qubits
    assert nx.is_connected(g), f"{topology.name} must be one connected chip"
    cm = topology.coupling_map()
    assert len(cm.get_edges()) == 2 * len(topology.edges())  # both directions


def test_star():
    _check(StarTopology(), 5)


def test_tshape():
    t = TShapeTopology()
    _check(t, 5)
    assert nx.diameter(t.graph()) == 3
    assert set(map(tuple, map(sorted, t.edges()))) == {
        (0, 1), (1, 2), (1, 3), (3, 4)}


def test_heavy_hex_patch_21():
    t = HeavyHexPatch(1, 2)
    _check(t, 21)
    assert t.name == "heavy-hex-21"
    assert max(dict(t.graph().degree()).values()) <= 3


def test_heavy_hex_patch_35():
    _check(HeavyHexPatch(2, 2), 35)


def test_eagle_127():
    """The real IBM Eagle map: 127 qubits, heavy-hex structure."""
    t = Eagle127Topology()
    _check(t, 127)
    g = t.graph()
    assert g.number_of_edges() == 144
    assert max(dict(g.degree()).values()) == 3
    assert nx.diameter(g) == 26
    # node ids must be contiguous 0..126 (frontend indexes positions by id)
    assert set(g.nodes()) == set(range(127))


def _check_73(t):
    g = t.graph()
    assert nx.is_connected(g)
    assert all(len(f) == 7 for f in t.faces()), "every face is a 7-cycle"
    assert max(dict(g.degree()).values()) <= 3
    ef = Counter()
    for f in t.faces():
        for a, b in zip(f, f[1:] + f[:1]):
            ef[tuple(sorted((a, b)))] += 1
    assert max(ef.values()) <= 2, "each edge in at most 2 faces"
    vf = Counter(v for f in t.faces() for v in f)
    assert max(vf.values()) <= 3, "each vertex in at most 3 faces"
    # genuine interior: vertices with the tiling's degree (3)
    assert sum(1 for d in dict(g.degree()).values() if d == 3) > 0


def test_hyperbolic_73_small():
    t = HyperbolicTiling(22)
    _check_73(t)
    assert 18 <= t.num_qubits() <= 30


def test_hyperbolic_73_large():
    t = HyperbolicTiling(60)
    _check_73(t)
    assert t.num_qubits() >= 55
