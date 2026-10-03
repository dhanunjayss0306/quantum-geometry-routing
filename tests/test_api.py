"""API-level tests: call the route functions directly.

FastAPI's TestClient needs httpx, which is not a pinned dependency, so
these tests exercise the route logic in-process instead of over HTTP.
"""

import pytest
from fastapi import HTTPException
from pydantic import ValidationError

from backend.api import experiments as exp_routes
from backend.api import topologies as topo_routes
from backend.schemas.experiment import ExperimentRequest


def test_results_order_and_cases():
    rows = topo_routes.list_results()
    expected = [
        ("t-shape", "ideal", 1), ("t-shape", "noisy", 2),
        ("t-shape", "protected", 3),
        ("heavy-hex-127", "ideal", 4), ("heavy-hex-127", "noisy", 5),
        ("heavy-hex-127", "protected", 6),
        ("hyperbolic-20", "ideal", 7), ("hyperbolic-20", "noisy", 8),
        ("hyperbolic-20", "protected", 9),
    ]
    got = [(r["topology"], r["condition"], r["case"]) for r in rows[:9]]
    assert got == expected, f"results order wrong: {got}"
    for r in rows[9:]:
        assert r["case"] is None, f"supplementary row has case: {r}"
        assert r["required"] is False


def test_exactly_nine_numbered_cases():
    rows = topo_routes.list_results()
    cases = sorted(r["case"] for r in rows if r["case"] is not None)
    assert cases == list(range(1, 10)), f"cases: {cases}"


def test_topologies_have_tiers():
    topos = topo_routes.list_topologies()
    by_name = {t["name"]: t["tier"] for t in topos}
    assert by_name["t-shape"] == "required"
    assert by_name["heavy-hex-127"] == "required"
    assert by_name["hyperbolic-20"] == "required"
    assert by_name["heavy-hex-21"] == "supplementary"
    assert by_name["hyperbolic-127"] == "supplementary"
    assert by_name["star"] == "exploratory"
    assert by_name["heavy-hex-35"] == "exploratory"
    assert by_name["hyperbolic-43"] == "exploratory"


def test_unknown_topology_returns_400():
    req = ExperimentRequest(topology="not-a-chip", condition="noisy",
                            shots=100, seed=42)
    with pytest.raises(HTTPException) as exc:
        exp_routes.run_single(req)
    assert exc.value.status_code == 400


def test_shots_below_minimum_rejected():
    # FastAPI turns this pydantic ValidationError into a 422 response.
    with pytest.raises(ValidationError):
        ExperimentRequest(topology="t-shape", condition="noisy",
                          shots=5, seed=42)
