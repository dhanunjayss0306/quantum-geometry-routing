"""Correlator circuits: asking the Bell pair three careful questions.

Fidelity needs <XX>, <YY>, <ZZ> -- "do the two qubits agree when measured
in the X / Y / Z language?" Each needs its own circuit:

  ZZ: measure both qubits directly.
  XX: apply H to both first (H translates X-language into Z-language),
      then measure.
  YY: apply S-dagger then H to both (translates Y into Z), then measure.

Crucial subtlety: these rotations must hit the physical qubits that HOLD
the logical qubits AFTER routing (SWAPs move them!). We read that from
the transpiler's final layout -- never guess.
"""

from qiskit import QuantumCircuit


def logical_positions(routed: QuantumCircuit) -> tuple:
    """Physical qubits holding logical qubit 0 and 1 after routing.

    Returns:
        (phys0, phys1): physical index of logical 0, then logical 1.
    """
    final = routed.layout.final_index_layout()  # virtual -> physical
    return final[0], final[1]


def build_correlator_circuits(routed_bell: QuantumCircuit) -> dict:
    """Build the XX, YY, ZZ measurement circuits for a routed Bell state.

    Args:
        routed_bell: Bell circuit AFTER routing, WITHOUT measurements.

    Returns:
        {'XX': circuit, 'YY': circuit, 'ZZ': circuit}, each with 2 clbits
        where clbit 0 holds logical qubit 0's result.
    """
    p0, p1 = logical_positions(routed_bell)
    circuits = {}

    def _base():
        qc = QuantumCircuit(routed_bell.num_qubits, 2)
        qc.compose(routed_bell, inplace=True)
        return qc

    # ZZ: direct measurement.
    qc = _base()
    qc.measure([p0, p1], [0, 1])
    circuits["ZZ"] = qc

    # XX: H on both, then measure.
    qc = _base()
    qc.h([p0, p1])
    qc.measure([p0, p1], [0, 1])
    circuits["XX"] = qc

    # YY: S-dagger then H on both, then measure.
    qc = _base()
    qc.sdg([p0, p1])
    qc.h([p0, p1])
    qc.measure([p0, p1], [0, 1])
    circuits["YY"] = qc

    return circuits
