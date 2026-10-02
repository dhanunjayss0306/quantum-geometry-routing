"""Bell-state fidelity from the three correlators.

For the target state |Phi+> = (|00> + |11>)/sqrt(2):

    F = (1 + <XX> - <YY> + <ZZ>) / 4

Each expectation comes from one circuit's counts:
    <PP> = P(agree) - P(disagree)
         = (N_00 + N_11 - N_01 - N_10) / N_total

Perfect Bell state: <XX>=+1, <YY>=-1, <ZZ>=+1  ->  F = 1.
"""

from .correlators import build_correlator_circuits  # noqa: F401  (re-export)


def pauli_expectation(counts: dict) -> float:
    """<PP> from one correlator circuit's counts."""
    total = sum(counts.values())
    agree = sum(n for bits, n in counts.items() if bits[0] == bits[1])
    return (2 * agree - total) / total


def bell_state_fidelity(counts_xx: dict, counts_yy: dict, counts_zz: dict) -> float:
    """Fidelity of the prepared state with the ideal |Phi+> Bell state."""
    xx = pauli_expectation(counts_xx)
    yy = pauli_expectation(counts_yy)
    zz = pauli_expectation(counts_zz)
    return (1 + xx - yy + zz) / 4


def fidelity_report(counts_xx: dict, counts_yy: dict, counts_zz: dict) -> dict:
    """All three correlators plus the fidelity, in one dict."""
    xx = pauli_expectation(counts_xx)
    yy = pauli_expectation(counts_yy)
    zz = pauli_expectation(counts_zz)
    return {
        "xx": xx,
        "yy": yy,
        "zz": zz,
        "fidelity": (1 + xx - yy + zz) / 4,
    }
