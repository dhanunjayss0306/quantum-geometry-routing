"""Routing: map a logical circuit onto a physical coupling map.

The logical circuit says "do CNOT between qubit A and qubit B".
The hardware says "A and B have no road between them".
Qiskit's transpile() solves this: it picks physical qubits for each
logical qubit (layout) and inserts SWAP gates wherever a two-qubit
gate must travel (routing).

More SWAPs = longer detour = more noise = lower fidelity.
"""

from qiskit import QuantumCircuit, transpile
from qiskit.transpiler import CouplingMap

# Gates the routed circuit is allowed to use. Keeping "swap" visible
# (instead of decomposing it) lets us COUNT the routing cost directly.
BASIS_GATES = ["id", "rz", "sx", "x", "h", "cx", "swap", "measure"]


def route_circuit(
    circuit: QuantumCircuit,
    coupling_map: CouplingMap,
    initial_layout=None,
    optimization_level: int = 1,
    seed: int = 42,
) -> QuantumCircuit:
    """Transpile a logical circuit onto a physical coupling map.

    Args:
        circuit: logical circuit (e.g. the Bell circuit).
        coupling_map: hardware connectivity (the "road map").
        initial_layout: optional list mapping logical -> physical qubits,
            e.g. [1, 3] puts logical 0 on physical 1, logical 1 on physical 3.
        optimization_level: 0-3, how hard the transpiler optimizes.
        seed: fixed seed so results are reproducible.

    Returns:
        The routed physical circuit (may contain SWAP gates).
    """
    return transpile(
        circuit,
        coupling_map=coupling_map,
        basis_gates=BASIS_GATES,
        initial_layout=initial_layout,
        optimization_level=optimization_level,
        seed_transpiler=seed,
    )


def strip_idle_qubits(circuit: QuantumCircuit) -> QuantumCircuit:
    """Remove physical qubits that no gate touches.

    Why: routing a 2-qubit circuit onto a 35-qubit chip yields a 35-qubit
    circuit, but only the qubits along the SWAP path do anything. Simulating
    all 35 would need 2^35 amplitudes (impossible); the ~8 used ones are
    trivial. Idle qubits never affect measurement results, so dropping them
    is exact, not an approximation. Barriers are cosmetic and are dropped.
    """
    used_index = set()
    for instr in circuit.data:
        if instr.operation.name in ("barrier",):
            continue
        for q in instr.qubits:
            used_index.add(circuit.find_bit(q).index)
    used_index = sorted(used_index)
    remap = {old: new for new, old in enumerate(used_index)}

    slim = QuantumCircuit(len(used_index), circuit.num_clbits)
    for instr in circuit.data:
        if instr.operation.name in ("barrier",):
            continue
        slim.append(
            instr.operation,
            [remap[circuit.find_bit(q).index] for q in instr.qubits],
            [circuit.find_bit(c).index for c in instr.clbits],
        )
    slim.global_phase = circuit.global_phase
    return slim
