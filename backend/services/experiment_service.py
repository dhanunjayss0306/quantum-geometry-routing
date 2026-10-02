"""Experiment service: routes API requests into the quantum engine.

The service layer is the ONLY place that touches quantum/ and algorithms/.
API route files never import quantum code directly.
"""

from algorithms.experiment_matrix import CONDITIONS, run_case, run_matrix
from backend.config import ALLOWED_CONDITIONS
from backend.schemas.experiment import ExperimentRequest
from backend.services.topology_service import get_topology


def run_experiment(req: ExperimentRequest) -> dict:
    """Run a single experiment case and return its result dict."""
    if req.condition not in ALLOWED_CONDITIONS:
        raise ValueError(f"unknown condition '{req.condition}'; choose from {CONDITIONS}")
    topology = get_topology(req.topology)
    return run_case(topology, req.condition, shots=req.shots, seed=req.seed)


def run_all_experiments(shots: int = 2000, seed: int = 42) -> list:
    """Run the full 9-case matrix. Returns a list of result dicts."""
    topologies = [get_topology(name) for name in
                  ["star", "heavy-hex", "hyperbolic"]]
    return run_matrix(topologies, shots=shots, seed=seed)
