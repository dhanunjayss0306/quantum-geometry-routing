"""5-qubit star topology -- inspired by IBM's 2016 5-qubit chip.

            1
            |
        2 - 0 - 3
            |
            4

Qubit 0 is the hub; leaves 1-4 connect ONLY to the hub.
Two leaves (e.g. 1 and 3) are distance 2 apart, so entangling them
forces the transpiler to route through the hub with SWAPs.
"""

from .topology_base import TopologyBase


class StarTopology(TopologyBase):
    name = "star"
    description = "5-qubit star: hub qubit 0 with 4 leaves (2016-era layout)."

    def num_qubits(self) -> int:
        return 5

    def edges(self) -> list:
        return [(0, 1), (0, 2), (0, 3), (0, 4)]
