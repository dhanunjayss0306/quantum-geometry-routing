"""Tests for the 3D layouts and the extended topology API fields."""

import math

import networkx as nx

from quantum.topologies.star import StarTopology
from quantum.topologies.tshape import TShapeTopology
from quantum.topologies.heavy_hex import HeavyHexPatch
from quantum.topologies.hyperbolic import HyperbolicTiling
from quantum.topologies.layout3d import layout_3d
from backend.services import topology_service


def _all_topos():
    return [StarTopology(), TShapeTopology(), HeavyHexPatch(1, 2),
            HyperbolicTiling(17)]


def test_positions_length_finite_and_deterministic():
    for topo in _all_topos():
        L = layout_3d(topo)
        pos = L["positions"]
        assert len(pos) == topo.num_qubits(), topo.name
        assert all(len(p) == 3 for p in pos)
        assert all(all(math.isfinite(c) for c in p) for p in pos), topo.name
        # deterministic across two calls
        assert layout_3d(topo)["positions"] == pos, topo.name


def test_flat_chips_have_zero_z():
    for topo in [StarTopology(), TShapeTopology(), HeavyHexPatch(1, 2)]:
        L = layout_3d(topo)
        assert L["family"] == "flat"
        assert L["surface"]["type"] == "plane"
        assert all(p[2] == 0.0 for p in L["positions"]), topo.name


def test_hyperbolic_lies_on_hyperboloid():
    L = layout_3d(HyperbolicTiling(17))
    assert L["family"] == "hyperbolic"
    assert L["surface"]["type"] == "hyperboloid"
    # x^2 + y^2 - (z-1)^2 == -1 (hyperboloid with tip at the origin)
    for p in L["positions"]:
        assert abs(p[0] ** 2 + p[1] ** 2 - (p[2] - 1) ** 2 + 1) < 0.02


def test_api_detail_route_matches_bell_pair():
    for name in ["t-shape", "star", "heavy-hex-21", "hyperbolic-20"]:
        d = topology_service.topology_detail(name)
        assert len(d["positions3d"]) == d["num_qubits"]
        a, b = d["bell_pair"]
        route = d["route"]
        assert route[0] == a and route[-1] == b, name
        assert len(route) - 1 == d["diameter"], name
        edges = {tuple(sorted(e)) for e in d["edges"]}
        for u, v in zip(route, route[1:]):
            assert tuple(sorted((u, v))) in edges, (name, u, v)


def test_api_list_has_new_fields():
    for d in topology_service.list_topologies():
        for field in ("positions3d", "surface", "bell_pair", "route",
                      "diameter", "family"):
            assert field in d, (d["name"], field)
        assert d["family"] in ("flat", "hyperbolic")
