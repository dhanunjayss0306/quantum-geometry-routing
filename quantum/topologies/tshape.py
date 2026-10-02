"""T-shaped 5-qubit topology -- the 2016 reference.

The earliest IBM 5-qubit chips (and the "T" layout in many textbooks) look
like this: a short backbone 0-1-2 with qubit 3 hanging off the middle and
qubit 4 hanging off 3. Diameter 3 -- the longest trip on this chip is three
hops, one more than the star's two. That single extra hop is exactly the
kind of geometric tax this project measures.
"""

from .topology_base import TopologyBase


class TShapeTopology(TopologyBase):
    name = "t-shape"
    description = "5-qubit T: 2016-era reference (edges 0-1, 1-2, 1-3, 3-4; diameter 3)."

    def num_qubits(self) -> int:
        return 5

    def edges(self) -> list:
        return [(0, 1), (1, 2), (1, 3), (3, 4)]
