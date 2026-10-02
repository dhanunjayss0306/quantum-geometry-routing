"""Heavy-hex topologies -- the connectivity of modern IBM QPUs.

What "heavy-hex" means: start from a honeycomb (hexagonal) lattice, then put
one extra qubit in the MIDDLE of every edge. The original corner qubits keep
degree 3, the new edge qubits have degree 2. That exact pattern is what IBM
uses on its current chips.

Two flavors live here:

1. HeavyHexPatch(rows, cols): a subdivided-honeycomb patch of any size.
   Used for the size-matched matrix variant (~21 qubits) and the scaling
   sweep. Its name always carries its qubit count, e.g. "heavy-hex-35".

2. Eagle127Topology: the REAL 127-qubit IBM Eagle coupling map, extracted
   once from qiskit-ibm-runtime's FakeSherbrooke backend and stored as a
   static edge list (eagle127_edges.json). No runtime dependency on
   qiskit-ibm-runtime -- the map is just data. 127 nodes, 144 edges,
   max degree 3, diameter 26.
"""

import json
import os

import networkx as nx

from .topology_base import TopologyBase


def _heavy_hex_edges(rows: int = 2, cols: int = 2) -> tuple:
    """Build heavy-hex edges by subdividing a honeycomb lattice.

    Returns (num_qubits, edge_list).
    """
    honey = nx.hexagonal_lattice_graph(rows, cols)
    index = {node: i for i, node in enumerate(honey.nodes())}
    edges = []
    nxt = len(index)
    for u, v in honey.edges():
        w = nxt
        nxt += 1
        # edge qubit w sits between corner qubits u and v
        edges.append((index[u], w))
        edges.append((w, index[v]))
    return nxt, edges


class HeavyHexPatch(TopologyBase):
    """Subdivided-honeycomb heavy-hex patch. Name carries the qubit count."""

    def __init__(self, rows: int = 2, cols: int = 2):
        self._rows, self._cols = rows, cols
        self._num_qubits, self._edges = _heavy_hex_edges(rows, cols)

    @property
    def name(self) -> str:
        return f"heavy-hex-{self._num_qubits}"

    @property
    def description(self) -> str:
        return (f"{self._num_qubits}-qubit heavy-hex patch "
                f"(subdivided {self._rows}x{self._cols} honeycomb).")

    def num_qubits(self) -> int:
        return self._num_qubits

    def edges(self) -> list:
        return self._edges


# Backwards-compatible alias for the original 35-qubit patch.
HeavyHexTopology = HeavyHexPatch


class Eagle127Topology(TopologyBase):
    """The real IBM Eagle 127-qubit heavy-hex coupling map (static data)."""

    name = "heavy-hex-127"
    description = ("127-qubit IBM Eagle heavy-hex coupling map, extracted from "
                   "qiskit-ibm-runtime's FakeSherbrooke backend.")

    def __init__(self):
        path = os.path.join(os.path.dirname(__file__), "eagle127_edges.json")
        with open(path) as f:
            self._edges = [tuple(e) for e in json.load(f)]

    def num_qubits(self) -> int:
        return 127

    def edges(self) -> list:
        return self._edges
