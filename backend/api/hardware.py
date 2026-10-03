"""Real-hardware run endpoint.

Serves the recorded IBM QPU validation run (results/qpu/tshape_real_backend.json)
so the dashboard can display it. Read-only; the file is committed to the repo.
"""

import json
import os

from fastapi import APIRouter, HTTPException

from backend.config import REPO_ROOT

router = APIRouter(prefix="/api", tags=["hardware"])

HARDWARE_FILE = os.path.join(REPO_ROOT, "results", "qpu", "tshape_real_backend.json")


@router.get("/hardware")
def get_hardware_run():
    """The recorded real-QPU t-shape validation run, or 404 if absent."""
    if not os.path.exists(HARDWARE_FILE):
        raise HTTPException(status_code=404, detail="no hardware run recorded")
    with open(HARDWARE_FILE) as f:
        data = json.load(f)
    data["screenshot"] = "/images/ibm_fez_job.png"
    return data
