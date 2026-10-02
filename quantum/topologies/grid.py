"""2D square-grid topology -- the classical reference family.

A flat grid is what "no clever geometry" looks like: diameter grows like
sqrt(N). It anchors the scaling sweep -- hyperbolic should beat it
(log-like vs sqrt), heavy-hex should track it.
"""

import networkx as nx

from .topology_base import TopologyBase


class GridTopology(TopologyBase):
    def __init__(self, rows: int, cols: int):
        self._rows, self._cols = rows, cols
        g = nx.grid_2d_graph(rows, cols)
        self._index = {node: i for i, node in enumerate(sorted(g.nodes()))}
        self._edges = [(self._index[u], self._index[v])
                       for u, v in g.edges()]
        self._num_qubits = rows * cols

    @property
    def name(self) -> str:
        return f"grid-{self._rows}x{self._cols}"

    @property
    def description(self) -> str:
        return (f"{self._num_qubits}-qubit 2D square grid "
                f"({self._rows}x{self._cols}) -- flat reference.")

    def num_qubits(self) -> int:
        return self._num_qubits

    def edges(self) -> list:
        return self._edges
