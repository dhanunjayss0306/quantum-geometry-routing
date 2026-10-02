"""Topology + saved-result endpoints."""

import glob
import json
import os

from fastapi import APIRouter, HTTPException

from backend.config import RESULTS_DIR
from backend.schemas.experiment import TopologyInfo
from backend.services import topology_service

router = APIRouter(prefix="/api", tags=["topologies", "results"])


@router.get("/topologies", response_model=list[TopologyInfo])
def list_topologies():
    """All topologies with their coupling graphs (for the frontend viewer)."""
    return topology_service.list_topologies()


@router.get("/topologies/{name}", response_model=TopologyInfo)
def get_topology(name: str):
    try:
        return topology_service.topology_detail(name)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/results")
def list_results():
    """Previously saved experiment results (from scripts/run_all_cases.py)."""
    out = []
    for path in sorted(glob.glob(os.path.join(RESULTS_DIR, "*.json"))):
        with open(path) as f:
            out.append(json.load(f))
    return out
