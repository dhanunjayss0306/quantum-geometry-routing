"""Topology service: the single place that builds topology objects."""

import networkx as nx

from quantum.topologies.star import StarTopology
from quantum.topologies.tshape import TShapeTopology
from quantum.topologies.heavy_hex import HeavyHexPatch
from quantum.topologies.hyperbolic import HyperbolicTiling
from quantum.topologies.layout3d import layout_3d
from algorithms.experiment_matrix import farthest_pair
from backend.config import ALLOWED_TOPOLOGIES

_BUILDERS = {
    "t-shape": TShapeTopology,
    "star": StarTopology,
    "heavy-hex-21": lambda: HeavyHexPatch(1, 2),
    "heavy-hex-35": lambda: HeavyHexPatch(2, 2),
    "hyperbolic-20": lambda: HyperbolicTiling(17),
    "hyperbolic-43": lambda: HyperbolicTiling(40),
}

# Topologies never change at runtime; cache the (expensive) 3D details.
_DETAIL_CACHE = {}


def get_topology(name: str):
    """Build a topology by name. Raises ValueError for unknown names."""
    if name not in _BUILDERS:
        raise ValueError(f"unknown topology '{name}'; choose from {ALLOWED_TOPOLOGIES}")
    return _BUILDERS[name]()


def topology_detail(name: str) -> dict:
    """Full viewer metadata: 3D layout, worst-case Bell pair and its route."""
    if name not in _DETAIL_CACHE:
        topo = get_topology(name)
        layout = layout_3d(topo)
        a, b, dist = farthest_pair(topo)
        route = nx.shortest_path(topo.graph(), a, b)
        _DETAIL_CACHE[name] = {
            "name": topo.name,
            "description": topo.description,
            "num_qubits": topo.num_qubits(),
            "edges": [list(e) for e in topo.edges()],
            "positions3d": layout["positions"],
            "surface": layout["surface"],
            "bell_pair": [a, b],
            "route": route,
            "diameter": nx.diameter(topo.graph()),
            "family": layout["family"],
        }
    return _DETAIL_CACHE[name]


def list_topologies() -> list:
    """Metadata for every topology (for the frontend viewer)."""
    return [topology_detail(name) for name in ALLOWED_TOPOLOGIES]
