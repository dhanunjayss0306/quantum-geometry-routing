"""Routing-cost metrics: how expensive was the detour?

After routing, we read off:
    swap_count  number of SWAP gates inserted (each SWAP = 3 CNOTs)
    cx_count    number of two-qubit CX gates
    depth       circuit depth = number of time-steps (gates that must
                run one after another). Deeper = longer exposure to noise.
    depth_2q    two-qubit-gate depth: time-steps containing only two-qubit
                gates -- the number the challenge asks us to report, since
                two-qubit gates dominate the noise.
"""

from qiskit import QuantumCircuit


def two_qubit_depth(circuit: QuantumCircuit) -> int:
    """Depth counting only two-qubit gates (cx, swap)."""
    qc2 = QuantumCircuit(circuit.num_qubits)
    for instr in circuit.data:
        if instr.operation.num_qubits == 2:
            qc2.append(
                instr.operation,
                [circuit.find_bit(q).index for q in instr.qubits],
            )
    return qc2.depth()


def analyze_routing(transpiled: QuantumCircuit) -> dict:
    """Measure the routing cost of a transpiled circuit.

    Args:
        transpiled: circuit returned by route_circuit().

    Returns:
        dict with swap_count, cx_count, depth, depth_2q, num_qubits
        and full op counts.
    """
    ops = transpiled.count_ops()
    return {
        "swap_count": ops.get("swap", 0),
        "cx_count": ops.get("cx", 0),
        "depth": transpiled.depth(),
        "depth_2q": two_qubit_depth(transpiled),
        "num_qubits": transpiled.num_qubits,
        "op_counts": dict(ops),
    }
