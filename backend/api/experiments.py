"""Experiment endpoints: run the quantum engine over HTTP."""

from fastapi import APIRouter, HTTPException

from backend.schemas.experiment import ExperimentRequest, ExperimentResult
from backend.services import experiment_service

router = APIRouter(prefix="/api/experiments", tags=["experiments"])


@router.post("/run", response_model=ExperimentResult)
def run_single(req: ExperimentRequest):
    """Run one experiment case, e.g. hyperbolic + noisy."""
    try:
        return experiment_service.run_experiment(req)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/run-all", response_model=list[ExperimentResult])
def run_all(shots: int = 2000, seed: int = 42):
    """Run the full 9-case matrix. Takes ~10 seconds."""
    if not (100 <= shots <= 20000):
        raise HTTPException(status_code=400, detail="shots must be 100..20000")
    return experiment_service.run_all_experiments(shots=shots, seed=seed)
