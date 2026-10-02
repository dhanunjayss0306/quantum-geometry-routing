"""Topology service: the single place that builds topology objects."""

from quantum.topologies.star import StarTopology
from quantum.topologies.tshape import TShapeTopology
from quantum.topologies.heavy_hex import HeavyHexPatch
from quantum.topologies.hyperbolic import HyperbolicTiling
from backend.config import ALLOWED_TOPOLOGIES

_BUILDERS = {
    "t-shape": TShapeTopology,
    "star": StarTopology,
    "heavy-hex-21": lambda: HeavyHexPatch(1, 2),
    "heavy-hex-35": lambda: HeavyHexPatch(2, 2),
    "hyperbolic-20": lambda: HyperbolicTiling(17),
    "hyperbolic-43": lambda: HyperbolicTiling(40),
}


def get_topology(name: str):
    """Build a topology by name. Raises ValueError for unknown names."""
    if name not in _BUILDERS:
        raise ValueError(f"unknown topology '{name}'; choose from {ALLOWED_TOPOLOGIES}")
    return _BUILDERS[name]()


def list_topologies() -> list:
    """Metadata for every topology (for the frontend viewer)."""
    infos = []
    for name in ALLOWED_TOPOLOGIES:
        t = get_topology(name)
        infos.append({
            "name": t.name,
            "description": t.description,
            "num_qubits": t.num_qubits(),
            "edges": [list(e) for e in t.edges()],
        })
    return infos
