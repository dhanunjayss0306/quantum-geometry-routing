"""Syndrome-based protection: detect errors WITHOUT collapsing the Bell state.

For |Phi+>, XX and ZZ are *stabilizers* (both have eigenvalue +1). After the
Bell state is routed, one ancilla qubit measures the ZZ parity (catches bit
flips) and then the XX parity (catches phase flips), using mid-circuit
measurements into SEPARATE classical bits. Shots where either syndrome reads
1 are discarded; the XX/YY/ZZ correlators are then computed from the DATA
qubits' bits only.

Why selection and scoring use disjoint bits: an earlier version filtered
shots on the very same bits it then scored, forcing fidelity to 1.0 by
construction -- even pure noise "passed". Here selection uses ONLY ancilla
bits, which are never scored, so a random input can no longer fake a
perfect fidelity.

The ancilla must sit next to the data qubits (CNOTs need a road). We pick the
physical qubit minimizing the total SWAP distance to the Bell pair's final
positions, move the data states next to it (counting every added SWAP), and
report the protection overhead separately.
"""

import networkx as nx
from qiskit import QuantumCircuit

from .fidelity import pauli_expectation, bell_state_fidelity

# Classical bit layout in protected circuits: [d0, d1, syn_zz, syn_xx].
# In Qiskit count bitstrings the leftmost char is the HIGHEST clbit,
# so a 4-bit outcome reads as syn_xx syn_zz d1 d0.
N_DATA_BITS = 2


def _coupling_graph(coupling_map) -> nx.Graph:
    g = nx.Graph()
    g.add_edges_from(tuple(sorted(e)) for e in coupling_map.get_edges())
    return g


def create_protected_bell_circuit() -> QuantumCircuit:
    """Logical 3-qubit circuit: Bell pair + ancilla syndrome extraction.

    Qubits 0,1 hold the Bell state; qubit 2 is the ancilla. After the Bell
    state is prepared, the ancilla measures the ZZ parity (catches bit
    flips) and then the XX parity via phase kickback (catches phase flips),
    with mid-circuit measurements into clbits 2 (syn_zz) and 3 (syn_xx).
    Data qubits are NOT measured here -- the caller adds correlator
    measurements into clbits 0 and 1 afterwards.

    The whole 3-qubit circuit is routed by the transpiler, which places the
    ancilla and inserts whatever SWAPs the coupling map demands. That is
    the measured protection cost: we count it instead of hand-placing qubits.
    """
    qc = QuantumCircuit(3, 4)
    # Bell pair on qubits 0 and 1.
    qc.h(0)
    qc.cx(0, 1)
    # ZZ parity -> ancilla. Ancilla flips iff parity is odd,
    # i.e. a bit flip (X error) struck one of the data qubits.
    qc.cx(0, 2)
    qc.cx(1, 2)
    qc.measure(2, 2)  # syn_zz
    qc.reset(2)
    # XX parity via phase kickback: H, controlled-XX, H. Ancilla reads 1
    # iff a phase flip (Z error) struck. |Phi+> is a +1 eigenstate of both
    # stabilizers, so a clean run leaves the Bell state untouched.
    qc.h(2)
    qc.cx(2, 0)
    qc.cx(2, 1)
    qc.h(2)
    qc.measure(2, 3)  # syn_xx
    return qc


def _best_ancilla_spot(coupling_map, a: int, b: int) -> int:
    """Physical qubit minimizing SWAP distance to both Bell endpoints."""
    g = _coupling_graph(coupling_map)
    dist = dict(nx.shortest_path_length(g))
    return min((n for n in g.nodes if n not in (a, b)),
               key=lambda n: (dist[n][a] + dist[n][b], n))


def route_protected_circuit(logical_prot: QuantumCircuit, coupling_map,
                            initial_layout=None, seed: int = 42) -> QuantumCircuit:
    """Route the 3-qubit protected circuit onto the coupling map.

    Args:
        logical_prot: from create_protected_bell_circuit().
        coupling_map: the topology's coupling map.
        initial_layout: [phys_a, phys_b] pinning the Bell pair's endpoints
            (farthest pair); the ancilla starts at the physical qubit
            closest to both endpoints, then the transpiler routes everything.
        seed: fixed seed for reproducibility.
    """
    from quantum.routing.transpiler import route_circuit, BASIS_GATES_WITH_RESET
    a, b = initial_layout[0], initial_layout[1]
    az = _best_ancilla_spot(coupling_map, a, b)
    # initial_layout as a dict needs Bit keys, not ints -- and it must
    # cover all virtual qubits.
    layout = {logical_prot.qubits[0]: a,
              logical_prot.qubits[1]: b,
              logical_prot.qubits[2]: az}
    return route_circuit(
        logical_prot, coupling_map, initial_layout=layout,
        seed=seed, basis_gates=BASIS_GATES_WITH_RESET,
    )


def build_protected_correlator_circuits(routed_prot: QuantumCircuit) -> dict:
    """Add basis rotations + data measurements to a routed protected circuit.

    Args:
        routed_prot: create_protected_bell_circuit() AFTER routing.
            Virtual qubits 0,1 are the data; the ancilla's syndrome bits
            already sit in clbits 2 and 3.

    Returns:
        {'XX', 'YY', 'ZZ'} circuits; data measured into clbits 0 and 1.
    """
    from quantum.fidelity.correlators import logical_positions
    q0, q1 = logical_positions(routed_prot)
    circuits = {}

    qc = routed_prot.copy()
    qc.measure([q0, q1], [0, 1])
    circuits["ZZ"] = qc

    qc = routed_prot.copy()
    qc.h([q0, q1])
    qc.measure([q0, q1], [0, 1])
    circuits["XX"] = qc

    qc = routed_prot.copy()
    qc.sdg([q0, q1])
    qc.h([q0, q1])
    qc.measure([q0, q1], [0, 1])
    circuits["YY"] = qc
    return circuits


def syndrome_post_select(counts: dict) -> tuple:
    """Split counts into syndrome/data; keep only clean-syndrome shots.

    Args:
        counts: raw counts with 4-bit outcomes (syn_xx syn_zz d1 d0).

    Returns:
        (kept_data_counts, yield_fraction): kept_data_counts maps the
        2 data bits to shot counts; yield is kept/total.
    """
    kept = {}
    total = sum(counts.values())
    for bits, n in counts.items():
        syn_xx, syn_zz = bits[0], bits[1]
        if syn_xx == "0" and syn_zz == "0":
            data = bits[2] + bits[3]
            kept[data] = kept.get(data, 0) + n
    kept_total = sum(kept.values())
    return kept, (kept_total / total if total else 0.0)


def protected_fidelity(counts_xx: dict, counts_yy: dict,
                       counts_zz: dict) -> dict:
    """Fidelity from syndrome post-selection, plus the survival yield.

    Selection uses ONLY ancilla bits; correlators use ONLY data bits.
    """
    kept_xx, y_xx = syndrome_post_select(counts_xx)
    kept_yy, y_yy = syndrome_post_select(counts_yy)
    kept_zz, y_zz = syndrome_post_select(counts_zz)
    return {
        "xx": pauli_expectation(kept_xx),
        "yy": pauli_expectation(kept_yy),
        "zz": pauli_expectation(kept_zz),
        "fidelity": bell_state_fidelity(kept_xx, kept_yy, kept_zz),
        "yield": (y_xx + y_yy + y_zz) / 3,
    }
