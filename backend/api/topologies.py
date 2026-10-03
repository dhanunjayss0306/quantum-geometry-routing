"""Topology + saved-result endpoints."""

import csv
import glob
import json
import os

from fastapi import APIRouter, HTTPException

from backend.config import (MATRIX_TOPOLOGIES, REPO_ROOT, REQUIRED_TOPOLOGIES,
                            RESULTS_DIR, SUPPLEMENTARY_TOPOLOGIES)
from backend.schemas.experiment import TopologyInfo
from backend.services import topology_service

router = APIRouter(prefix="/api", tags=["topologies", "results"])

CONDITION_ORDER = ["ideal", "noisy", "protected"]
TOPOLOGY_ORDER = (REQUIRED_TOPOLOGIES + SUPPLEMENTARY_TOPOLOGIES)

# Case numbers for the required 9-case matrix: t-shape 1-3, heavy-hex-127
# 4-6, hyperbolic-20 7-9 (ideal/noisy/protected each). Supplementary rows
# get null.
CASE_NUMBERS = {
    topo: {cond: i * 3 + j + 1 for j, cond in enumerate(CONDITION_ORDER)}
    for i, topo in enumerate(REQUIRED_TOPOLOGIES)
}


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
    """Previously saved experiment results, in matrix order with case numbers.

    Order: t-shape, heavy-hex-127, hyperbolic-20, then supplementary
    (heavy-hex-21, hyperbolic-127), each ideal/noisy/protected. Required
    rows carry case 1-9; supplementary rows carry case null. The JSON
    files on disk are not modified.
    """
    rows = []
    for path in sorted(glob.glob(os.path.join(RESULTS_DIR, "*.json"))):
        with open(path) as f:
            r = json.load(f)
        r["case"] = CASE_NUMBERS.get(r["topology"], {}).get(r["condition"])
        rows.append(r)
    rows.sort(key=lambda r: (
        TOPOLOGY_ORDER.index(r["topology"])
        if r["topology"] in TOPOLOGY_ORDER else 99,
        CONDITION_ORDER.index(r["condition"])
        if r["condition"] in CONDITION_ORDER else 99,
    ))
    return rows


@router.get("/scaling")
def list_scaling():
    """Scaling sweep rows (from results/tables/scaling.csv)."""
    path = os.path.join(REPO_ROOT, "results", "tables", "scaling.csv")
    with open(path, newline="") as f:
        return list(csv.DictReader(f))
