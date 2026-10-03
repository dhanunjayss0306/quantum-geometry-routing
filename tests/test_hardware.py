"""Tests for the real-hardware run endpoint."""

import os

from backend.api import hardware as hw_routes
from backend.config import REPO_ROOT


def test_hardware_run_serves_recorded_job():
    data = hw_routes.get_hardware_run()
    assert data["backend"] == "ibm_fez"
    assert data["job_id"] == "db0e7hal7guc73cgblgg"
    assert data["job_status"] == "DONE"
    assert abs(data["fidelity_phi_plus"] - 0.921) < 1e-9
    assert data["shots_per_circuit"] == 2000
    assert data["screenshot"] == "/images/ibm_fez_job.png"
    assert os.path.exists(
        os.path.join(REPO_ROOT, "frontend", "public",
                     data["screenshot"].lstrip("/"))
    ), "dashboard screenshot image must exist in frontend/public"


def test_hardware_run_has_full_provenance():
    data = hw_routes.get_hardware_run()
    for key in ("submitted_utc", "completed_utc", "bell_pair",
                "transpiled_depth", "counts", "correlators",
                "t_shape_physical_qubits"):
        assert key in data, f"hardware record missing {key}"
    assert set(data["counts"]) == {"XX", "YY", "ZZ"}
