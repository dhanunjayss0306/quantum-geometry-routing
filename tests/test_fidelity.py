"""Tests for fidelity: ideal Bell state must score F = 1."""

import itertools

from quantum.circuits.bell_state import create_bell_circuit
from quantum.topologies.star import StarTopology
from quantum.topologies.heavy_hex import HeavyHexTopology
from quantum.routing.transpiler import route_circuit, strip_idle_qubits
from quantum.noise.noisy_simulation import simulate_counts
from quantum.fidelity.correlators import build_correlator_circuits
from quantum.fidelity.fidelity import fidelity_report, bell_state_fidelity
from quantum.fidelity.post_selection import (
    create_protected_bell_circuit,
    route_protected_circuit,
    build_protected_correlator_circuits,
    syndrome_post_select,
    protected_fidelity,
)
from algorithms.experiment_matrix import run_case


def _reports(shots=400):
    topo = StarTopology()
    routed = route_circuit(create_bell_circuit(), topo.coupling_map(),
                           initial_layout=[1, 3])
    counts = {}
    for name, circ in build_correlator_circuits(routed).items():
        counts[name] = simulate_counts(strip_idle_qubits(circ), shots=shots)
    return counts


def test_ideal_fidelity_is_one():
    c = _reports()
    rep = fidelity_report(c["XX"], c["YY"], c["ZZ"])
    assert abs(rep["fidelity"] - 1.0) < 0.03
    assert abs(rep["xx"] - 1.0) < 0.05
    assert abs(rep["yy"] + 1.0) < 0.05
    assert abs(rep["zz"] - 1.0) < 0.05


def _protected_reports(topology, condition, shots):
    from quantum.noise.noise_models import build_depolarizing_noise_model
    a, b, _ = __import__("algorithms.experiment_matrix",
                         fromlist=["farthest_pair"]).farthest_pair(topology)
    routed_prot = route_protected_circuit(
        create_protected_bell_circuit(), topology.coupling_map(),
        initial_layout=[a, b])
    nm = None if condition == "ideal" else build_depolarizing_noise_model()
    counts = {}
    for name, circ in build_protected_correlator_circuits(routed_prot).items():
        counts[name] = simulate_counts(strip_idle_qubits(circ),
                                       noise_model=nm, shots=shots)
    return counts


def test_protected_ideal_fidelity_one_and_yield_one():
    """Ideal world: syndrome never fires, nothing is discarded."""
    c = _protected_reports(StarTopology(), "ideal", shots=400)
    rep = protected_fidelity(c["XX"], c["YY"], c["ZZ"])
    assert abs(rep["fidelity"] - 1.0) < 0.03
    assert abs(rep["yield"] - 1.0) < 0.03


def test_protected_beats_noisy_but_below_one():
    """Protection helps under noise, but cannot reach perfection."""
    noisy = run_case(HeavyHexTopology(), "noisy", shots=1000, seed=42)
    prot = run_case(HeavyHexTopology(), "protected", shots=1000, seed=42)
    assert prot["fidelity"] > noisy["fidelity"] + 0.01
    assert prot["fidelity"] < 1.0
    assert prot["yield"] < 1.0
    assert prot["added_cx_count"] > 0 and prot["added_depth"] > 0


def test_uniform_counts_do_not_fake_perfection():
    """The old tautological filter turned even random counts into F=1.
    Selection now uses only ancilla bits, so uniform data gives F ~ 0.25."""
    uniform = {"".join(b): 64 for b in itertools.product("01", repeat=4)}
    kept, _ = syndrome_post_select(uniform)
    f = bell_state_fidelity(kept, kept, kept)
    assert abs(f - 0.25) < 0.02
    assert f != 1.0
