"""Simulation runner: ideal world vs noisy world, same interface."""

from qiskit import QuantumCircuit
from qiskit_aer import AerSimulator


def simulate_counts(
    circuit: QuantumCircuit,
    noise_model=None,
    shots: int = 2000,
    seed: int = 42,
) -> dict:
    """Run a circuit on AerSimulator and return measurement counts.

    Args:
        circuit: must already contain measurements.
        noise_model: None = ideal world; otherwise the noisy world.
        shots: number of repetitions.
        seed: fixed seed for reproducibility.

    Returns:
        dict like {'00': 983, '11': 1017}.
    """
    sim = AerSimulator(seed_simulator=seed)
    kwargs = {"shots": shots}
    if noise_model is not None:
        kwargs["noise_model"] = noise_model
    return sim.run(circuit, **kwargs).result().get_counts()
