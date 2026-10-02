"""Noise models: the telephone game that scrambles qubits.

Every gate is slightly wrong and every measurement slightly misread.
We model this with *depolarizing* noise: with probability p, a gate
accidentally applies a random Pauli error (X, Y or Z) -- like static on
the line. Two-qubit gates (cx, swap) are ~10x noisier than single-qubit
gates, which matches real hardware.

ALL noise parameters live here. Nothing else in the repo hard-codes them.
"""

from qiskit_aer.noise import NoiseModel, ReadoutError, depolarizing_error

# Single configuration point for the whole project.
ONE_QUBIT_GATE_ERROR = 0.001   # p for h, x, sx, id, rz
TWO_QUBIT_GATE_ERROR = 0.01    # p for cx, swap  (the expensive gates)
READOUT_ERROR = 0.02           # probability a measurement bit flips


def build_depolarizing_noise_model(
    p1: float = ONE_QUBIT_GATE_ERROR,
    p2: float = TWO_QUBIT_GATE_ERROR,
    readout: float = READOUT_ERROR,
) -> NoiseModel:
    """Build a simple, explainable depolarizing noise model.

    Args:
        p1: error probability per single-qubit gate.
        p2: error probability per two-qubit gate.
        readout: probability a measurement result flips.

    Returns:
        qiskit_aer NoiseModel usable with AerSimulator.
    """
    model = NoiseModel()
    model.add_all_qubit_quantum_error(
        depolarizing_error(p1, 1), ["h", "x", "sx", "id", "rz"]
    )
    # SWAPs are decomposed by Aer into noisy gates anyway, but our routed
    # circuits keep 'swap' as an explicit gate, so cover it too.
    model.add_all_qubit_quantum_error(depolarizing_error(p2, 2), ["cx", "swap"])
    if readout > 0:
        model.add_all_qubit_readout_error(
            ReadoutError([[1 - readout, readout], [readout, 1 - readout]])
        )
    return model
