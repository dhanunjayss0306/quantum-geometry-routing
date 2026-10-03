"""Export a static snapshot of the API data for the frontend.

Writes frontend/public/data/topologies.json, results.json and scaling.json
using the same functions as the live API (so tier and case fields match).
The frontend falls back to these files when the backend is unreachable.

Run from the repo root:
    python3 scripts/export_static_data.py
"""

import json
import os
import sys

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)

from backend.api.topologies import list_results, list_scaling, list_topologies
from backend.api.hardware import get_hardware_run


def main():
    out_dir = os.path.join(REPO_ROOT, "frontend", "public", "data")
    os.makedirs(out_dir, exist_ok=True)
    payloads = {
        "topologies.json": list_topologies(),
        "results.json": list_results(),
        "scaling.json": list_scaling(),
        "hardware.json": get_hardware_run(),
    }
    for name, payload in payloads.items():
        path = os.path.join(out_dir, name)
        with open(path, "w") as f:
            json.dump(payload, f, indent=2)
        print(f"wrote {path} ({len(payload)} rows)")


if __name__ == "__main__":
    main()
