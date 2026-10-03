"""Test the experiment matrix on one fast case."""

from quantum.topologies.star import StarTopology
from quantum.topologies.heavy_hex import HeavyHexPatch
from algorithms.experiment_matrix import run_case


def test_run_case_keys():
    r = run_case(StarTopology(), "noisy", shots=200, seed=1)
    for key in ["topology", "condition", "swap_count", "cx_count", "depth",
                "fidelity", "yield", "xx", "yy", "zz"]:
        assert key in r, f"missing key: {key}"
    assert r["topology"] == "star"
    assert 0.0 <= r["fidelity"] <= 1.0
    assert r["swap_count"] >= 1


def test_fixed_seed_reproducible():
    """Same seed -> identical results (routing and noisy simulation)."""
    topo = HeavyHexPatch(1, 2)
    r1 = run_case(topo, "noisy", shots=500, seed=42)
    r2 = run_case(topo, "noisy", shots=500, seed=42)
    assert r1 == r2
    # protected too (syndrome sampling must also be seeded)
    p1 = run_case(topo, "protected", shots=500, seed=42)
    p2 = run_case(topo, "protected", shots=500, seed=42)
    assert p1 == p2
