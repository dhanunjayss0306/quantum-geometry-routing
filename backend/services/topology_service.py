"""Topology service: the single place that builds topology objects."""

from quantum.topologies.star import StarTopology
from quantum.topologies.heavy_hex import HeavyHexTopology
from quantum.topologies.hyperbolic import HyperbolicTopology
from backend.config import ALLOWED_TOPOLOGIES

_BUILDERS = {
    "star": StarTopology,
    "heavy-hex": HeavyHexTopology,
    "hyperbolic": HyperbolicTopology,
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
