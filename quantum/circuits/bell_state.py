"""Bell-state circuit: the quantum heart of the project.

A Bell state is the simplest entangled state of two qubits::

    |Phi+> = (|00> + |11>) / sqrt(2)

Measure both qubits and the results always match (00 or 11),
yet each qubit alone is completely random.

Recipe -- just 2 gates::

    q0: --H--●--
             |
    q1: -----X--

Everything else in this project (topologies, routing, noise, fidelity)
is scaffolding around this tiny circuit.
"""

from qiskit import QuantumCircuit


def create_bell_circuit() -> QuantumCircuit:
    """Create the 2-qubit Bell state |Phi+> (no measurement).

    Returns:
        QuantumCircuit: H on qubit 0, then CNOT with qubit 0 as control.
    """
    qc = QuantumCircuit(2, name="bell_phi_plus")
    qc.h(0)      # H: flat coin -> spinning coin (superposition)
    qc.cx(0, 1)  # CNOT: "if qubit 0 is 1, flip qubit 1" -> links them
    return qc


def create_bell_measurement_circuit() -> QuantumCircuit:
    """Bell state plus measurement of both qubits into 2 classical bits.

    Returns:
        QuantumCircuit: the Bell circuit followed by measurement.
    """
    qc = QuantumCircuit(2, 2, name="bell_measured")
    qc.h(0)
    qc.cx(0, 1)
    qc.barrier()
    qc.measure([0, 1], [0, 1])
    return qc
