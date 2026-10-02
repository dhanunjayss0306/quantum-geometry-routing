"""Routing-cost metrics: how expensive was the detour?

After routing, we read off:
    swap_count  number of SWAP gates inserted (each SWAP = 3 CNOTs)
    cx_count    number of two-qubit CX gates
    depth       circuit depth = number of time-steps (gates that must
                run one after another). Deeper = longer exposure to noise.
"""

from qiskit import QuantumCircuit


def analyze_routing(transpiled: QuantumCircuit) -> dict:
    """Measure the routing cost of a transpiled circuit.

    Args:
        transpiled: circuit returned by route_circuit().

    Returns:
        dict with swap_count, cx_count, depth, num_qubits and full op counts.
    """
    ops = transpiled.count_ops()
    return {
        "swap_count": ops.get("swap", 0),
        "cx_count": ops.get("cx", 0),
        "depth": transpiled.depth(),
        "num_qubits": transpiled.num_qubits,
        "op_counts": dict(ops),
    }
