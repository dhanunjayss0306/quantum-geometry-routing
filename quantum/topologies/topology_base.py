"""Interface every topology must follow.

A topology is a graph: vertices = physical qubits,
edges = pairs allowed to do a two-qubit gate directly.
This is the "road map" the transpiler routes circuits on.

Every topology class provides:
    name            short id, e.g. "star"
    description     one-line human description
    num_qubits()    how many physical qubits
    edges()         undirected edges as (a, b) pairs
    coupling_map()  Qiskit CouplingMap (directed, both ways)
    graph()         networkx Graph for analysis / drawing
"""

import networkx as nx
from qiskit.transpiler import CouplingMap


class TopologyBase:
    name = "base"
    description = "base topology (override me)"

    def num_qubits(self) -> int:
        raise NotImplementedError

    def edges(self) -> list:
        """Undirected edges as (a, b) tuples."""
        raise NotImplementedError

    def coupling_map(self) -> CouplingMap:
        """Qiskit coupling map: every undirected edge added in both directions."""
        directed = []
        for a, b in self.edges():
            directed.append([a, b])
            directed.append([b, a])
        return CouplingMap(directed)

    def graph(self) -> nx.Graph:
        """networkx graph of the topology (for metrics and drawing)."""
        g = nx.Graph()
        g.add_nodes_from(range(self.num_qubits()))
        g.add_edges_from(self.edges())
        return g
