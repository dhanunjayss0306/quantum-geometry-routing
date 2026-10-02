"""Test the experiment matrix on one fast case."""

from quantum.topologies.star import StarTopology
from algorithms.experiment_matrix import run_case


def test_run_case_keys():
    r = run_case(StarTopology(), "noisy", shots=200, seed=1)
    for key in ["topology", "condition", "swap_count", "cx_count", "depth",
                "fidelity", "yield", "xx", "yy", "zz"]:
        assert key in r, f"missing key: {key}"
    assert r["topology"] == "star"
    assert 0.0 <= r["fidelity"] <= 1.0
    assert r["swap_count"] >= 1
