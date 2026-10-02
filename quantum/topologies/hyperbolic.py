"""Hyperbolic-inspired topology -- a {7,3}-like tiling patch (the future bet).

In hyperbolic geometry, space expands EXPONENTIALLY: the number of points
within d steps grows like c^d instead of d^2 (as on a flat chip). That means
far-apart "houses" stay connected by short paths -- exactly what a quantum
cloud wants, because shorter trips need fewer SWAPs.

We mimic a {7,3} tiling patch (3 roads meeting at every junction,
heptagon-like faces):
  layer 0:            1 node (center)
  layer k -> k+1:     every node grows 2 children  (sizes 3, 6, 12, ...)
  "face" edges:       link neighboring branches in each layer, creating the
                      cycles (shortcuts) a pure tree lacks.

3 layers -> 1 + 3 + 6 + 12 = 22 qubits. Nobody has built this in hardware;
that is why we simulate it.
"""

from .topology_base import TopologyBase


def _hyperbolic_edges(layers: int = 3) -> tuple:
    """Build the layered hyperbolic patch. Returns (num_qubits, edge_list)."""
    edges = []
    levels = [[0], [1, 2, 3]]
    edges += [(0, 1), (0, 2), (0, 3)]
    nxt = 4
    for _ in range(1, layers):
        prev = levels[-1]
        cur = []
        for v in prev:
            c1, c2 = nxt, nxt + 1
            nxt += 2
            edges += [(v, c1), (v, c2)]
            cur += [c1, c2]
        # face edges: stitch neighboring branches into cycles (the "faces")
        m = len(prev)
        for i in range(m):
            a = cur[2 * i + 1]
            b = cur[2 * ((i + 1) % m)]
            edges.append((a, b))
        levels.append(cur)
    return nxt, edges


class HyperbolicTopology(TopologyBase):
    name = "hyperbolic"
    description = "22-qubit hyperbolic-inspired patch: exponential expansion, {7,3}-like."

    def __init__(self, layers: int = 3):
        self._num_qubits, self._edges = _hyperbolic_edges(layers)

    def num_qubits(self) -> int:
        return self._num_qubits

    def edges(self) -> list:
        return self._edges
