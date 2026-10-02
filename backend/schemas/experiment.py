"""API schemas: what the frontend may send, and what it gets back."""

from pydantic import BaseModel, Field

from backend.config import (
    ALLOWED_CONDITIONS,
    ALLOWED_TOPOLOGIES,
    DEFAULT_SEED,
    DEFAULT_SHOTS,
    MAX_SHOTS,
    MIN_SHOTS,
)


class ExperimentRequest(BaseModel):
    """One experiment run. Only fixed choices allowed -- no arbitrary code."""

    topology: str = Field(..., description=f"one of {ALLOWED_TOPOLOGIES}")
    condition: str = Field("noisy", description=f"one of {ALLOWED_CONDITIONS}")
    shots: int = Field(DEFAULT_SHOTS, ge=MIN_SHOTS, le=MAX_SHOTS)
    seed: int = Field(DEFAULT_SEED)


class ExperimentResult(BaseModel):
    """Result of one experiment case (mirrors algorithms/experiment_matrix)."""

    topology: str
    condition: str
    num_qubits: int
    bell_pair: list
    graph_distance: int
    swap_count: int
    cx_count: int
    depth: int
    xx: float
    yy: float
    zz: float
    fidelity: float
    yield_: float = Field(..., alias="yield")
    shots: int
    seed: int

    class Config:
        populate_by_name = True


class TopologyInfo(BaseModel):
    name: str
    description: str
    num_qubits: int
    edges: list
