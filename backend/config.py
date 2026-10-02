"""Central backend configuration. All tunable values live here."""

import os

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RESULTS_DIR = os.path.join(REPO_ROOT, "experiments", "results")

ALLOWED_TOPOLOGIES = ["star", "heavy-hex", "hyperbolic"]
ALLOWED_CONDITIONS = ["ideal", "noisy", "protected"]

DEFAULT_SHOTS = 2000
MIN_SHOTS = 100
MAX_SHOTS = 20000
DEFAULT_SEED = 42
