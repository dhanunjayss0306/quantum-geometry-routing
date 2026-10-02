"""Tests for the Bell-state circuit."""

from quantum.circuits.bell_state import create_bell_circuit, create_bell_measurement_circuit


def test_bell_circuit_structure():
    qc = create_bell_circuit()
    assert qc.num_qubits == 2
    ops = qc.count_ops()
    assert ops["h"] == 1 and ops["cx"] == 1


def test_bell_measurement_circuit():
    qc = create_bell_measurement_circuit()
    assert qc.num_qubits == 2 and qc.num_clbits == 2
    assert qc.count_ops()["measure"] == 2
