"""Heavy-hex topology -- the connectivity of modern IBM QPUs (e.g. 127-qubit Eagle).

What "heavy-hex" means: start from a honeycomb (hexagonal) lattice, then put
one extra qubit in the MIDDLE of every edge. The original corner qubits keep
degree 3, the new edge qubits have degree 2. That exact pattern is what IBM
uses on its current chips.

We build a 35-qubit patch -- a "snippet" of the full 127-qubit chip, big
enough that routing across it needs real SWAP detours, small enough to
simulate after stripping idle qubits (see quantum/routing/transpiler.py).
"""

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


class HeavyHexTopology(TopologyBase):
    name = "heavy-hex"
    description = "35-qubit heavy-hex patch: subdivided honeycomb, like IBM's Eagle chips."

    def __init__(self, rows: int = 2, cols: int = 2):
        self._num_qubits, self._edges = _heavy_hex_edges(rows, cols)

    def num_qubits(self) -> int:
        return self._num_qubits

    def edges(self) -> list:
        return self._edges
