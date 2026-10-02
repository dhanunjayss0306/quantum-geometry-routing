"""Syndrome post-selection: discard runs that fail the parity check.

The sealed-envelopes idea, implemented simply and honestly: for a perfect
|Phi+> Bell state we KNOW what each correlator's outcomes must look like:

  XX circuit -> the two bits must AGREE    (00 or 11)
  YY circuit -> the two bits must DISAGREE  (01 or 10, because <YY> = -1)
  ZZ circuit -> the two bits must AGREE    (00 or 11)

Any shot violating this suffered an error. We throw those shots away and
compute fidelity from the survivors. Fidelity goes up; the price is the
"survival yield" (fraction of shots kept). That trade-off is real physics,
and we plot it.
"""

from .fidelity import pauli_expectation, bell_state_fidelity


def post_select_counts(counts: dict, expected_agree: bool) -> tuple:
    """Keep only shots passing the parity check.

    Args:
        counts: raw measurement counts, e.g. {'00': 900, '01': 50, ...}.
        expected_agree: True if good shots have agreeing bits (XX, ZZ),
            False if good shots disagree (YY).

    Returns:
        (kept_counts, yield_fraction).
    """
    kept = {
        bits: n
        for bits, n in counts.items()
        if (bits[0] == bits[1]) == expected_agree
    }
    total = sum(counts.values())
    kept_total = sum(kept.values())
    return kept, (kept_total / total if total else 0.0)


def protected_fidelity(counts_xx: dict, counts_yy: dict, counts_zz: dict) -> dict:
    """Fidelity after post-selection, plus the survival yield.

    Returns:
        {'fidelity': ..., 'yield': mean fraction of shots kept,
         'xx': ..., 'yy': ..., 'zz': ...} (post-selected correlators).
    """
    kept_xx, y_xx = post_select_counts(counts_xx, expected_agree=True)
    kept_yy, y_yy = post_select_counts(counts_yy, expected_agree=False)
    kept_zz, y_zz = post_select_counts(counts_zz, expected_agree=True)
    return {
        "xx": pauli_expectation(kept_xx),
        "yy": pauli_expectation(kept_yy),
        "zz": pauli_expectation(kept_zz),
        "fidelity": bell_state_fidelity(kept_xx, kept_yy, kept_zz),
        "yield": (y_xx + y_yy + y_zz) / 3,
    }
